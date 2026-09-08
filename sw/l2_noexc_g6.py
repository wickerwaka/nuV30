#!/usr/bin/env python3
"""L-6 / L-6b -- THE GOAL-STATE MEASUREMENT: G6 WITH THE CE MULTICYCLE DELETED.

THE STANDING REQUIREMENT (USER RULING 2026-09-08, verbatim): *"I don't want
custom sdc rules, period."*  So the NO-EXCEPTION configuration is the GOAL
STATE, and a build WITH the multicycle is a CONTROL.  This tool measures the
goal state without LANDING an SDC change: it patches `hdl/nec_test.sdc` for the
duration of the sweeps and restores it with `git checkout --` in a `finally`,
whatever happens.

It is a PROBE, NOT A GATE.  Its receipts will read `-dirty` and that is
correct: the tree really is dirty while they are taken, and saying so is the
point.

⚠ THE DELETION IS CHECKED, NOT ASSERTED (bar L-11).  `sw/quartus_gate.py`'s
`nominal` table is NOT edited by this wave, so with the exception gone the
core-domain `SAME` class measures k = 1.0 against a nominal of 2.0 and lands in
`off_class`.  **A no-exception draw whose `off_class` is EMPTY, or whose `SAME`
still reads k = 2.0, means the deletion did not reach the compiler and its Fmax
may not be quoted.**  The summary this tool prints puts that column beside the
Fmax so the check cannot be forgotten.

⚠ IT DOES NOT STOP MEASURING WHEN THE FIRST MEASUREMENT IS BAD.  `--seeds N`
exits non-zero on a RED distribution, and WAVE 2's driver carried `set -e`, so
its CONTROL sweep's RED aborted the run before the RETENTION leg
(`phase_split_landing_results_2026-09-08.md` §10 item 6).  A driver that stops
measuring the moment there is something to measure reports less the more there
is to report.  Both legs always run here.

Single-writer guard by EXACT binary name first; refuses if `hdl/` carries
uncommitted TRACKED changes, because the revert would otherwise take them.
"""
import argparse, glob, json, os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
SDC = 'hdl/nec_test.sdc'

# The block as it stands, byte for byte.  Asserted UNIQUE before the patch, so
# a future SDC edit makes this tool refuse rather than silently do nothing.
PRESENT = """if {[get_collection_size $v30u_ce] > 0} {
    # ce -> ce : 2.0 periods.  C-a + S-1 (see the derivation at the top of this
    # file); it was 4/3 under the deleted C-b.
    set_multicycle_path -setup 2 -from $v30u_ce -to $v30u_ce
    set_multicycle_path -hold  1 -from $v30u_ce -to $v30u_ce
    post_message -type info \\
        "nec_test.sdc: CE multicycle 2/1 applied to [get_collection_size $v30u_ce] ce-gated v30u core registers"
}"""

DELETED = """if {[get_collection_size $v30u_ce] > 0} {
    # ⚠⚠⚠ L2 GOAL-STATE PROBE (sw/l2_noexc_g6.py) -- THE CE MULTICYCLE IS
    # DELETED FOR THIS BUILD ONLY, AND THIS FILE IS RESTORED WITH
    # `git checkout --` WHEN THE SWEEP ENDS.  IT IS NOT A LANDING.
    # The two lines it replaces are, verbatim:
    #     set_multicycle_path -setup 2 -from $v30u_ce -to $v30u_ce
    #     set_multicycle_path -hold  1 -from $v30u_ce -to $v30u_ce
    post_message -type info \\
        "nec_test.sdc: L2 GOAL-STATE PROBE -- NO ce->ce exception; [get_collection_size $v30u_ce] ce-gated v30u core registers are checked SINGLE-CYCLE"
}"""


def sh(c):
    return subprocess.run(c, shell=True, capture_output=True, text=True)


def summarise(path):
    """Print the per-draw table L-6 asks for: verdict, Fmax, worst setup, k,
    off_class.  Reads the distribution record, never a log."""
    try:
        d = json.load(open(path))
    except Exception as e:                                    # pragma: no cover
        print(f"  (no distribution record at {path}: {e})")
        return
    print(f"  record id {d['id'][:16]}…   verdict {d['verdict']}   "
          f"label {d['label']}")
    print(f"  configuration: {d['configuration']}")
    wo = d.get('worst_of_n', {})
    print(f"  {wo.get('quotable_as')}")
    for p in d.get('per_seed', []):
        cd = p.get('core_domain') or {}
        # ⚠ `off_class` IS A LIST OF CLASS-NAME STRINGS, not of dicts.  The
        # first version of this printer indexed it as dicts and died with
        # `TypeError: string indices must be integers` AFTER the sweep and
        # AFTER the `finally` had restored the SDC -- so the measurement
        # survived and only the summary was lost.  Recorded rather than quietly
        # fixed: it is the same class as every other accepted-and-ignored
        # finding in this repo, a tool doing what it was told where what it was
        # told was wrong.
        off = cd.get('off_class') or []
        km, kn = cd.get('k_measured') or {}, cd.get('k_nominal')
        offs = ", ".join(f"{c} k={km.get(c)} (nominal {kn})" for c in off) \
            or "EMPTY  <<< THE DELETION DID NOT REACH THE COMPILER"
        print(f"    seed {p['seed']}: Fmax {p.get('fmax_mhz')}  "
              f"worst_setup {p.get('worst_setup_ns')}  "
              f"verdict {p.get('verdict')}  off_class: {offs}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', default='5')
    ap.add_argument('--label', required=True,
                    help='label PREFIX; each leg appends -control-nN / -retention-nN')
    ap.add_argument('--configs', default='control,retention')
    ap.add_argument('--dry-run', action='store_true',
                    help='patch the SDC, print the diff, restore, and exit 0')
    ap.add_argument('--probe', metavar='OUTPREFIX', default=None,
                    help='BUILD NOTHING.  Patch the SDC, run the two STA '
                         'probes against the fitted `hdl/db` ALREADY ON DISK, '
                         'and restore.  ⚠ THE PATCH IS WHAT MAKES THE PROBE '
                         'HONEST: `read_sdc` reads the file as it stands, so '
                         'probing a no-exception FIT with the exception '
                         'restored would report every ce->ce slack under a '
                         '2.0-period budget the netlist was not fitted to.')
    a = ap.parse_args()

    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    for b in ("quartus_map", "quartus_fit", "quartus_sta", "quartus_asm"):
        if sh(f"pgrep -x {b}").returncode == 0:
            print(f"REFUSING: {b} is running -- two writers on one hdl/db")
            return 2

    s = open(SDC).read()
    if s.count(PRESENT) != 1:
        print("REFUSING: the CE multicycle block is not present verbatim "
              f"(found {s.count(PRESENT)} occurrences).  hdl/nec_test.sdc has "
              "moved; re-derive this tool's anchor before trusting it.")
        return 2
    open(SDC, 'w').write(s.replace(PRESENT, DELETED, 1))
    rc = 0
    try:
        chk = sh("grep -c '^ *set_multicycle_path' " + SDC).stdout.strip()
        print(f"patched: uncommented set_multicycle_path lines now = {chk} "
              "(must be 0)")
        if chk != '0':
            print("REFUSING to build: the patch did not remove every exception")
            return 2
        if a.dry_run:
            print(sh(f"git diff -- {SDC}").stdout)
            return 0
        if a.probe:
            q = os.path.expanduser('~/intelFPGA_lite/17.1/quartus/bin')
            out = os.path.abspath(a.probe)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            for script, extra in (('sw/sta_phase_split_scan.tcl', ' 50'),
                                  ('sw/sta_l2_rowq_probe.tcl', '')):
                cmd = (f"cd {ROOT}/hdl && {q}/quartus_sta -t {ROOT}/{script} "
                       f"nec_test nec_test_ucore {out}{extra}")
                print(f"\n=== {script} ===", flush=True)
                r = sh(cmd)
                print(r.stdout[-20000:])
                print(f"[{script}] exit {r.returncode}")
            return 0
        n = a.seeds
        for cfg in [c.strip() for c in a.configs.split(',') if c.strip()]:
            label = f"{a.label}-{cfg}-n{n}"
            flag = ' --retention' if cfg == 'retention' else ''
            log = f"sw/testdata/l2/g6_{cfg}_noexc_n{n}.log"
            print(f"\n=== {label} ===", flush=True)
            r = sh(f"python3 sw/quartus_gate.py --seeds {n}{flag} "
                   f"--label {label} --log {log}")
            print(r.stdout[-6000:])
            if r.stderr.strip():
                print("STDERR:", r.stderr[-2000:])
            print(f"[{label}] quartus_gate exit {r.returncode} "
                  "(non-zero is EXPECTED on a RED distribution and is not an "
                  "error of this driver)")
            rc = rc or 0          # the driver's own rc does not follow the gate's
            summarise(f"sw/testdata/g6dist/{label}/distribution.json")
    finally:
        sh(f"git checkout -- {SDC}")
        left = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
        print("\n%s restored: %s" % (SDC, "CLEAN" if not left
                                     else "*** DIRTY ***\n" + left))
    return rc


if __name__ == "__main__":
    sys.exit(main())
