#!/usr/bin/env python3
"""L-9 -- NON-VACUITY FOR L2.  `row_q` IS LOAD-BEARING, AND THE ADDRESS
MIRRORING IS THE CORRECTNESS ARGUMENT, SO BOTH ARE FALSIFIED BY CONSTRUCTION.

Each case makes ONE temporary, reverted perturbation of
`hdl/rtl/ucore/v30u_eu.sv`, REBUILDS the receipted ucore binary, runs a NAMED
gate leg, and requires it to FAIL.  A gate that cannot be made to fail is not
a gate.

  A  one bit of `row_q` inverted            -> `check_core --opcodes 8F.0` FAILS
  B  the `srst` arm dropped from
     `rom_addr_next`'s `upc_loc` selection   -> a named leg FAILS
  C  POSITIVE CONTROL: no perturbation       -> the same legs PASS

⚠ EACH CASE IS ITS OWN RUN.  Verilator treats a procedural `$error` as an
assertion and `$stop`s on the first one, so a single run carrying two probes
reports only the first (WAVE 2 §9).  Nothing here uses `$error`, but the same
discipline applies to a perturbation: two at once cannot be attributed.

⚠ IT REFUSES if `hdl/` carries uncommitted TRACKED changes, because it reverts
with `git checkout --` and would take them with it.  Run it on a COMMITTED L2
tree.
"""
import os, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
EU = 'hdl/rtl/ucore/v30u_eu.sv'

CASES = [
    ("A  row_q perturbed by one bit",
     "        row_q <= row_next;",
     "        row_q <= row_next ^ 29'h1;   // L-9 CASE A PROBE",
     [("check_core 8F.0", "python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0")],
     True),
    ("B  the srst arm dropped from rom_addr_next",
     "assign rom_addr_next = {dec_bank_next,\n"
     "        (srst && !ss_we) ? upc_loc_r[1:0] : upc_loc_n[1:0]};",
     "assign rom_addr_next = {dec_bank_next, upc_loc_n[1:0]};  // L-9 CASE B PROBE",
     [("check_core 8F.0", "python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0"),
      ("check_boot 220", "python3 sw/check_boot.py --core ucore"),
      ("check_core all", "python3 sw/check_core.py --core ucore --opcodes all --cases 0")],
     True),
    ("B2 the srst arm dropped, scored on the SAVE-STATE sweep",
     "assign rom_addr_next = {dec_bank_next,\n"
     "        (srst && !ss_we) ? upc_loc_r[1:0] : upc_loc_n[1:0]};",
     "assign rom_addr_next = {dec_bank_next, upc_loc_n[1:0]};  // L-9 CASE B2 PROBE",
     [("cc 8F.0 --ss-sweep", "python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0 --ss-sweep")],
     True),
    ("D  CONTROL FOR B -- the SAME arm dropped from L1's dec_addr_next",
     "assign dec_addr_next = (srst && !ss_we)\n"
     "        ? {upc_page_r, upc_opc_r, upc_loc_r[3:2]}\n"
     "        : {upc_page_n, upc_opc_n, upc_loc_n[3:2]};",
     "assign dec_addr_next = {upc_page_n, upc_opc_n, upc_loc_n[3:2]};  // L-9 CASE D PROBE",
     [("check_core 8F.0", "python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0"),
      ("check_boot 220", "python3 sw/check_boot.py --core ucore"),
      ("check_core all", "python3 sw/check_core.py --core ucore --opcodes all --cases 0"),
      ("cc 8F.0 --ss-sweep", "python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0 --ss-sweep")],
     True),
    ("C  POSITIVE CONTROL -- no perturbation", None, None,
     [("check_core 8F.0", "python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0"),
      ("check_boot 220", "python3 sw/check_boot.py --core ucore")],
     False),
]


def sh(c, **kw):
    return subprocess.run(c, shell=True, capture_output=True, text=True,
                          env={**os.environ,
                               'TMPDIR': os.path.expanduser('~/.cache/ucsimt-tmp')},
                          **kw)


def main():
    # `--only A,B2` runs a SUBSET, matched on the case label's leading token.
    # It exists because a case added after a first run should not require
    # re-paying for the cases that already have a recorded result -- and the
    # runs are kept as SEPARATE artifacts so which run produced which line is
    # never in doubt.
    only = None
    if len(sys.argv) > 2 and sys.argv[1] == '--only':
        only = set(sys.argv[2].split(','))
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    rc = 0
    for name, old, new, legs, want_fail in CASES:
        if only is not None and name.split()[0] not in only:
            continue
        print(f"\n=== {name} ===", flush=True)
        try:
            if old is not None:
                s = open(EU).read()
                if s.count(old) != 1:
                    print(f"  REFUSING: anchor not unique ({s.count(old)} hits)")
                    rc = 2
                    continue
                open(EU, 'w').write(s.replace(old, new, 1))
            b = sh("python3 sw/check_core.py --build --core ucore")
            if b.returncode != 0:
                print("  BUILD FAILED -- that is itself a falsification for a "
                      "perturbation that does not elaborate; recorded as such")
                print(b.stdout[-1500:], b.stderr[-1500:])
                if not want_fail:
                    rc = 1
                continue
            fell = False
            for leg, cmd in legs:
                r = sh(cmd)
                tail = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:] or ['']
                verdict = "FAILED" if r.returncode != 0 else "PASSED"
                fell = fell or (r.returncode != 0)
                ok = (verdict == "FAILED") if want_fail else (verdict == "PASSED")
                print(f"  {leg:16s} {verdict}  ({tail[0][:110]})   "
                      f"{'as required' if ok else '*** NOT AS REQUIRED ***'}",
                      flush=True)
                if not ok and not want_fail:
                    rc = 1
                # ⚠ a leg that SURVIVES one perturbation is information, not a
                # failure of the case: the case needs ONE named leg to fall, and
                # WHICH legs did not fall is itself reported above.
                if want_fail and fell:
                    break          # one falsifier is the bar; do not re-pay for more
            if want_fail:
                print(f"  CASE VERDICT: {'NON-VACUOUS' if fell else '*** VACUOUS ***'}")
                if not fell:
                    rc = 1
        finally:
            if old is not None:
                sh(f"git checkout -- {EU}")
    print("\nrestoring the receipted binary to the unperturbed tree", flush=True)
    sh("python3 sw/check_core.py --build --core ucore")
    left = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    print("hdl/ restored: %s" % ("CLEAN" if not left else "*** DIRTY ***\n" + left))
    return rc


if __name__ == "__main__":
    sys.exit(main())
