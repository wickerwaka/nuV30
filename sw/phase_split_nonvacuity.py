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

def case(name, patches, want, cmd):
    """`patches` is a list of (path, old, new)."""
    CASES.append((name, patches, want, cmd))

RUN = "python3 sw/check_core.py --core ucore --opcodes 90 --cases 1"
RUN_SS = ("python3 sw/check_core.py --core ucore --opcodes 90 --cases 1 "
          "--ss-sweep 40 --ss-cases 0 --ss-mode 2")

# A1 / A2 -- let CE_HALF run during the SS park, which is what the TB's
# `!ss_park` term exists to prevent.
#
# ⚠ THEY NEED TWO PROBES AND NOT ONE, AND THE REASON IS ITSELF WORTH RECORDING:
# **VERILATOR TREATS A PROCEDURAL `$error` AS AN ASSERTION AND `$stop`s ON THE
# FIRST ONE.**  A single probe that raises CE_HALF across the whole park fires
# A1 and the run ends there, so A2 would read "DID NOT FIRE" for a reason that
# has nothing to do with A2.  Each clause therefore gets a probe that
# constructs ITS OWN condition and NOT the other's.
#   A1: CE_HALF high on the clocks SS_WE is high  -> `SS_WE && CE_HALF`.
#   A2: CE_HALF high ONE CLOCK LATER, i.e. exactly where the core's staging
#       flop still carries `ss_we_q` and SS_WE has already fallen.
PARK_PROBE = ("hdl/tb/tb_v30_core.sv",
              "    ce_half <= !ss_park && (ce_cnt == (ce_div / 2) - 1);",
              "    ce_half <= (!ss_park && (ce_cnt == (ce_div / 2) - 1)) || ss_park;   // P-8(a) PROBE")

case("A1     SS_WE && CE_HALF", [PARK_PROBE],
     [r"SS_WE asserted while CE_HALF high"], RUN_SS)

# ...and A2 needs the SAME probe with A1's clause SILENCED, because A1 is
# reached FIRST on it.  Silencing the clause under test's NEIGHBOUR is the only
# honest way to show the neighbour is reachable at all; A2's own clause is
# untouched and is what must fire.
case("A2     CE_HALF && ss_we_q  (with A1 silenced so it can be reached)",
     [PARK_PROBE,
      ("hdl/rtl/ucore/v30_core.sv",
       '    if (SS_WE && CE_HALF) $error("SS_WE asserted while CE_HALF high',
       '    if (1\'b0)            $error("SS_WE asserted while CE_HALF high')],
     [r"CE_HALF resumed with SS command staging undrained"], RUN_SS)

# B -- withhold CE_HALF entirely: S-1 must fire, and its message must name the
# EU's stage-1 dependence, not only t1_half2/ad_oe_data.
case("B      S-1 $fatal, naming the EU",
     [("hdl/tb/tb_v30_core.sv",
       "    ce_half <= !ss_park && (ce_cnt == (ce_div / 2) - 1);",
       "    ce_half <= 1'b0;   // P-8(b) NON-VACUITY PROBE: withhold CE_HALF")],
     # ⚠ THE SECOND CLAUSE IS GONE WITH THE LANDING.  P-8(b) registered that
     # S-1's message must name the EU's dependence and not only
     # `t1_half2`/`ad_oe_data`; it was DEMONSTRATED on the landed tree
     # (`c720fbde54`, the message contained "STAGE-1 capture edge") and REVERTED
     # with it under P-9, because on a tree with no phase split the EU has no
     # such dependence and saying it would be saying something false.  What
     # remains checkable here is that S-1 still `$fatal`s at all.
     [r"REQUIREMENT VIOLATED \(S-1\)"],
     RUN)

# C -- the shadow is LOAD-BEARING.  Flip ONE BIT of it on its way out and a
# named gate leg must break.  A shadow nothing depends on would pass every
# identity bar for the wrong reason.  (Skipped automatically before the peel.)
case("C      the shadow is LOAD-BEARING (one bit perturbed)",
     [("hdl/rtl/ucore/v30u_eu.sv",
       "        } = s1q;",
       "        } = s1q ^ 495'd1;   // P-8(c) PERTURBATION PROBE")],
     [r"first-div:"],   # check_core prints this ONLY on a failing case
     "python3 sw/check_core.py --core ucore --opcodes 90 --cases 5")

def main():
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    ok = True
    for name, patches, wants, cmd in CASES:
        miss = [pp for pp, o, n in patches if o not in open(pp).read()]
        if miss:
            print(f"[skip] {name}\n       anchor absent in {miss} "
                  f"(the mechanism it probes is not in this tree yet)")
            continue
        print(f"\n=== {name}")
        for pp, o, n in patches:
            patch(pp, o, n)
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
            restore(*[pp for pp, o, n in patches])
    sh("python3 sw/check_core.py --build --core ucore")
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    print("\nhdl/ restored: %s" % ("CLEAN" if not dirty else "*** DIRTY *** " + dirty))
    ok &= not dirty
    print("=== phase_split_nonvacuity: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
