#!/usr/bin/env python3
"""C-9 NON-VACUITY, DEMONSTRATED AND RECORDED  (the CUT SET, WAVE 4).

An assertion nobody has seen fire is a comment, and a lint nobody has seen fail
is worse -- it is a comment that looks like a gate.  Each case below CONSTRUCTS
its condition by a temporary, reverted patch, runs the thing that must complain,
and requires the named message.  Every patched file is restored with
`git checkout --` and the tree is verified clean at the end.

  A  THE SHADOW IS LOAD-BEARING -- flip ONE BIT of the 778 on its way out of
     `s1q` and a named gate leg must break.  A shadow nothing depends on would
     pass every identity bar for the wrong reason.
  B  THE LINT FIRES ON A RE-INTRODUCED BYPASS -- put ONE pre-cut wire name back
     into `v30u_eu_step.svh`, exactly the defect WAVE 2 shipped without seeing,
     and `sw/cutset_lint.py` must FAIL naming it.  This is C-3(a)'s second half.
  B2 ...AND ON A BYPASS THAT NO `s1w_` PREFIX BETRAYS -- name a module-level
     wire that was never part of the cut set (`sigma`, the ALU result rail).
     X2 cannot see that one; X4 must.
  C  S-1's `$fatal` FIRES AND ITS MESSAGE NAMES THE EU'S DEPENDENCE -- withhold
     `CE_HALF` entirely and the core must say that the EU consumes a STALE
     stage 1, not merely that `t1_half2` missed its turnaround.

Exit 0 = every case fired as required.
"""
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
ENV = dict(os.environ, TMPDIR=os.path.expanduser("~/.cache/ucsimt-tmp"))


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, env=ENV)


def patch(path, old, new):
    s = open(path).read()
    assert s.count(old) == 1, "anchor not unique in %s: %r (%d)" % (path, old, s.count(old))
    open(path, 'w').write(s.replace(old, new, 1))


CASES = []


def case(name, patches, want, cmd, build=True):
    CASES.append((name, patches, want, cmd, build))


# --- A ---------------------------------------------------------------------
case("A   the shadow is LOAD-BEARING (one bit of 778 perturbed)",
     [("hdl/rtl/ucore/v30u_eu.sv", "        } = s1q;",
       "        } = s1q ^ 778'd1;   // C-9(A) PERTURBATION PROBE")],
     [r"first-div:"],                       # check_core prints this ONLY on a fail
     "python3 sw/check_core.py --core ucore --opcodes 90 --cases 5")

# --- B ---------------------------------------------------------------------
# `row_bus` is in the cut set, so the pre-cut wire is `s1w_row_bus`.  Naming it
# in the loop body is EXACTLY WAVE 2's defect: the chain reads the live value and
# the shadow is bypassed.  X2 sees the `s1w_`; X4 sees the module wire.
case("B   the LINT fires on a re-introduced bypass (`s1w_row_bus` in the chain)",
     [("hdl/rtl/ucore/v30u_eu_step.svh", "if (row_bus", "if (s1w_row_bus")],
     [r"VIOLATION X2", r"VIOLATION X4", r"cutset_lint: FAIL"],
     "python3 sw/cutset_lint.py", build=False)

# --- B2 --------------------------------------------------------------------
# ...and a bypass with NO `s1w_` in it at all.  `sigma` is a module-level wire
# `v30u_eu.sv` computes and the next-state block has never read; adding a read
# of it is a NEW bypass that no prefix betrays.  X2 is blind to it BY
# CONSTRUCTION; X4 is the clause that catches it, and this is what shows X4 is
# not a restatement of X2.
case("B2  ...and on a bypass no `s1w_` prefix betrays (`sigma`, never in the set)",
     [("hdl/rtl/ucore/v30u_eu_step.svh", "if (row_bus", "if ((|sigma) && row_bus")],
     [r"VIOLATION X4", r"cutset_lint: FAIL"],
     "python3 sw/cutset_lint.py", build=False)

# --- C ---------------------------------------------------------------------
case("C   S-1 $fatal, and its message names the EU's dependence",
     [("hdl/tb/tb_v30_core.sv",
       "    ce_half <= !ss_park && (ce_cnt == (ce_div / 2) - 1);",
       "    ce_half <= 1'b0;   // C-9(C) NON-VACUITY PROBE: withhold CE_HALF")],
     [r"REQUIREMENT VIOLATED \(S-1\)", r"STAGE-1 capture edge"],
     "python3 sw/check_core.py --core ucore --opcodes 90 --cases 1")


def main():
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    ok = True
    for name, patches, wants, cmd, build in CASES:
        miss = [pp for pp, o, n in patches if o not in open(pp).read()]
        if miss:
            print("[skip] %s\n       anchor absent in %s "
                  "(the mechanism it probes is not in this tree)" % (name, miss))
            ok = False
            continue
        print("\n=== %s" % name)
        for pp, o, n in patches:
            patch(pp, o, n)
        try:
            out = ""
            if build:
                b = sh("python3 sw/check_core.py --build --core ucore")
                out += b.stdout + b.stderr
            r = sh(cmd)
            out += r.stdout + r.stderr
            for w in wants:
                hit = re.search(w, out) is not None
                print("    %s  /%s/" % ("FIRED   " if hit else "DID NOT FIRE", w))
                ok &= hit
            if not all(re.search(w, out) for w in wants):
                print("    ---- last 12 lines of the run ----")
                for l in out.strip().split('\n')[-12:]:
                    print("      " + l)
        finally:
            sh("git checkout -- " + " ".join(pp for pp, o, n in patches))
    sh("python3 sw/check_core.py --build --core ucore")
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    print("\nhdl/ restored: %s" % ("CLEAN" if not dirty else "*** DIRTY *** " + dirty))
    ok &= not dirty
    print("=== cutset_nonvacuity: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
