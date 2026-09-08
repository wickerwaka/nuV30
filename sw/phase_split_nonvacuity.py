#!/usr/bin/env python3
"""P-8 NON-VACUITY, DEMONSTRATED AND RECORDED  (ce/ce_half phase split, WAVE 2).

An assertion nobody has seen fire is a comment.  Each case below CONSTRUCTS the
condition by a temporary, reverted patch to ONE file, rebuilds, runs a single
golden case, and requires the named message.  Every patched file is restored
with `git checkout --` before the next case, and the tree is verified clean at
the end.

  A1  `SS_WE && CE_HALF`            -- RULING 1, new clause
  A2  `CE_HALF && ss_we_q`          -- RULING 1, new clause
  B   S-1 `$fatal`, and its message names the EU's dependence
  C   the shadow is LOAD-BEARING (P-8c): perturb one bit of `s1q` and a named
      gate leg must break

Exit 0 = every case fired as required.
"""
import subprocess, sys, os, re, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
ENV = dict(os.environ, TMPDIR=os.path.expanduser("~/.cache/ucsimt-tmp"))

def sh(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                          env=ENV, **kw)

def patch(path, old, new):
    s = open(path).read()
    assert s.count(old) == 1, f"anchor not unique in {path}: {old!r}"
    open(path, 'w').write(s.replace(old, new, 1))

def restore(*paths):
    sh("git checkout -- " + " ".join(paths))

CASES = []

def case(name, path, old, new, want, cmd):
    CASES.append((name, path, old, new, want, cmd))

RUN = "python3 sw/check_core.py --core ucore --opcodes 90 --cases 1"
RUN_SS = ("python3 sw/check_core.py --core ucore --opcodes 90 --cases 1 "
          "--ss-sweep 40 --ss-cases 0")

# A1 / A2 -- let CE_HALF run during the SS park, which is what the TB's
# `!ss_park` term exists to prevent.  Both new clauses see it.
case("A1+A2  SS_WE && CE_HALF  and  CE_HALF && ss_we_q",
     "hdl/tb/tb_v30_core.sv",
     "    ce_half <= !ss_park && (ce_cnt == (ce_div / 2) - 1);",
     "    ce_half <= (ce_cnt == (ce_div / 2) - 1);   // P-8(a) NON-VACUITY PROBE",
     [r"SS_WE asserted while CE_HALF high", r"CE_HALF resumed with SS command staging undrained"],
     RUN_SS)

# B -- withhold CE_HALF entirely: S-1 must fire, and its message must name the
# EU's stage-1 dependence, not only t1_half2/ad_oe_data.
case("B      S-1 $fatal, naming the EU",
     "hdl/tb/tb_v30_core.sv",
     "    ce_half <= !ss_park && (ce_cnt == (ce_div / 2) - 1);",
     "    ce_half <= 1'b0;   // P-8(b) NON-VACUITY PROBE: withhold CE_HALF",
     [r"REQUIREMENT VIOLATED \(S-1\)", r"STAGE-1 capture edge"],
     RUN)

# C -- the shadow is LOAD-BEARING.  Flip one bit of it on its way out and a
# named gate leg must break.  (Skipped automatically before the peel lands.)
case("C      the shadow is LOAD-BEARING",
     "hdl/rtl/ucore/v30u_eu.sv",
     "        } = s1q;",
     "        } = s1q ^ {{(S1W-1){1'b0}}, 1'b1};   // P-8(c) PERTURBATION PROBE",
     [r"MISMATCH|FAIL|mismatch|PHASE-SPLIT PREMISE VIOLATED"],
     "python3 sw/check_core.py --core ucore --opcodes 90 --cases 5")

def main():
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    ok = True
    for name, path, old, new, wants, cmd in CASES:
        src = open(path).read()
        if old not in src:
            print(f"[skip] {name}\n       anchor absent in {path} "
                  f"(the mechanism it probes is not in this tree yet)")
            continue
        print(f"\n=== {name}")
        patch(path, old, new)
        try:
            b = sh("python3 sw/check_core.py --build --core ucore")
            r = sh(cmd)
            out = b.stdout + b.stderr + r.stdout + r.stderr
            for w in wants:
                hit = re.search(w, out) is not None
                print(f"    {'FIRED   ' if hit else 'DID NOT FIRE'}  /{w}/")
                ok &= hit
            if not any(re.search(w, out) for w in wants):
                print("    ---- last 12 lines of the run ----")
                for l in out.strip().split('\n')[-12:]:
                    print("      " + l)
        finally:
            restore(path)
    sh("python3 sw/check_core.py --build --core ucore")
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    print("\nhdl/ restored: %s" % ("CLEAN" if not dirty else "*** DIRTY *** " + dirty))
    ok &= not dirty
    print("=== phase_split_nonvacuity: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
