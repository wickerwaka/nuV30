#!/usr/bin/env python3
"""P-8(d): THE MULTICYCLE'S DELETION IS WHAT CHANGES THE TIMING.

A control build with `nec_test.sdc`'s CE multicycle RESTORED must report the
core-domain `SAME` class at k = 2 again.  Without this, "every receipt reports
k = 1" is consistent with an SDC the compiler never read.

It patches ONE file, builds ONE draw, reads the receipt, and REVERTS with
`git checkout --` whether or not the build succeeded.  It is NOT a gate and it
writes no ratchet: it is P-8(d)'s evidence and nothing else.

⚠ It runs a full Quartus compile.  Single-writer guard by EXACT binary name
first, and it REFUSES if `hdl/` carries uncommitted tracked changes -- the
revert would otherwise take them with it.
"""
import subprocess, sys, os, json, glob, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
SDC = 'hdl/nec_test.sdc'

ANCHOR = """if {[get_collection_size $v30u_ce] > 0} {
    post_message -type info \\"""
RESTORED = """if {[get_collection_size $v30u_ce] > 0} {
    # P-8(d) CONTROL PROBE -- the DELETED exception, restored for one build.
    set_multicycle_path -setup 2 -from $v30u_ce -to $v30u_ce
    set_multicycle_path -hold  1 -from $v30u_ce -to $v30u_ce
    post_message -type info \\"""

def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True)

def main():
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    for b in ("quartus_map", "quartus_fit", "quartus_sta", "quartus_asm"):
        if sh(f"pgrep -x {b}").returncode == 0:
            print(f"REFUSING: {b} is running -- two writers on one hdl/db")
            return 2
    s = open(SDC).read()
    assert s.count(ANCHOR) == 1, "anchor not unique"
    open(SDC, 'w').write(s.replace(ANCHOR, RESTORED, 1))
    try:
        r = sh("python3 sw/quartus_gate.py --label phasesplit-w2-P8D-mcp-restored "
               "--log sw/testdata/phasesplit/wave2/p8d_mcp_restored.log")
        print(r.stdout[-4000:])
        print(r.stderr[-2000:])
    finally:
        sh(f"git checkout -- {SDC}")
        print("\n%s restored: %s" % (SDC, "CLEAN"
              if not sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
              else "*** DIRTY ***"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
