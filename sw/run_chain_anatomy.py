#!/usr/bin/env python3
"""WAVE 5 (THE CHAIN ANATOMY) -- THE DRIVER.  MEASUREMENT ONLY, NO GATE.

It measures the **NO-EXCEPTION** configuration, because USER RULING 2026-09-08
(*"I don't want custom sdc rules, period."*) makes that the GOAL STATE.  The CE
multicycle is deleted from `hdl/nec_test.sdc` FOR THE MEASUREMENT FIT ONLY and
restored with `git checkout --` in a `finally`, whatever happens -- the patch
text and the anchor are IMPORTED FROM `sw/l2_noexc_g6.py` (WAVE 3) rather than
re-typed, so there is one anchor in the tree and not two.

MAP ONCE PER CONFIGURATION, FIT ONCE PER SEED (`quartus_gate.py`'s own rule:
re-mapping per seed would measure A&S non-determinism on top of placement
variance).  Then `sw/sta_chain_anatomy.tcl` on each fitted netlist.

⚠ `hdl/nec_test_ucore.qsf` IS REWRITTEN BY `quartus_map` -- the declared §70.7
exemption -- and WAVE 4 lost a whole sweep to not putting it back (§7 item 6).
It is restored after EVERY Quartus group here, not just at the end.

⚠ THE DELETION IS CHECKED, NOT ASSERTED.  Each STA leg re-reads the SDC, so
`sta_truefmax_probe.tcl` is run beside the anatomy and its `SAME` class must
measure **k = 1.0**.  A leg whose `SAME` still reads k = 2.0 was fitted to the
exception and its numbers belong to a different question.

Single-writer guard by EXACT binary name.  Refuses on tracked `hdl/` changes.
"""
import argparse, os, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'sw'))
from l2_noexc_g6 import PRESENT, DELETED, SDC          # noqa: E402  one anchor

QB = os.path.expanduser('~/intelFPGA_lite/17.1/quartus/bin')
PROJECT, REVISION = 'nec_test', 'nec_test_ucore'
QSF = 'hdl/nec_test_ucore.qsf'


def sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)


def run(argv, log):
    t0 = time.time()
    print("  $ " + " ".join(argv), flush=True)
    r = subprocess.run(argv, cwd=os.path.join(ROOT, 'hdl'),
                       capture_output=True, text=True)
    open(log, 'a').write(r.stdout + r.stderr)
    print(f"    exit {r.returncode}  {time.time()-t0:.0f}s", flush=True)
    return r


def guard():
    for b in ("quartus_map", "quartus_fit", "quartus_sta", "quartus_asm", "quartus_sh"):
        if sh(f"pgrep -x {b}").returncode == 0:
            print(f"REFUSING: {b} is running -- two writers on one hdl/db")
            return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--control-seeds', default='1,2,3')
    ap.add_argument('--retention-seeds', default='1')
    ap.add_argument('--outdir', default='sw/testdata/chainanat')
    ap.add_argument('--npaths', default='200')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()

    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print("REFUSING: hdl/ carries uncommitted tracked changes:\n" + dirty)
        return 2
    if not guard():
        return 2
    os.makedirs(a.outdir, exist_ok=True)
    log = os.path.join(ROOT, a.outdir, 'run.log')
    open(log, 'w').write("=== run_chain_anatomy ===\n")

    s = open(SDC).read()
    if s.count(PRESENT) != 1:
        print("REFUSING: the CE multicycle block is not present verbatim "
              f"({s.count(PRESENT)} occurrences).  Re-derive the anchor.")
        return 2
    open(SDC, 'w').write(s.replace(PRESENT, DELETED, 1))
    try:
        chk = sh("grep -c '^ *set_multicycle_path' " + SDC).stdout.strip()
        print(f"patched: uncommented set_multicycle_path lines = {chk} (must be 0)")
        if chk != '0':
            print("REFUSING to build: the patch did not remove every exception")
            return 2
        if a.dry_run:
            print(sh(f"git diff -- {SDC}").stdout)
            return 0
        for cfg, seeds in (('control', a.control_seeds),
                           ('retention', a.retention_seeds)):
            seeds = [x for x in seeds.split(',') if x.strip()]
            if not seeds:
                continue
            print(f"\n=== MAP: {cfg} ===", flush=True)
            argv = [f"{QB}/quartus_map"]
            if cfg == 'retention':
                argv.append("--verilog_macro=X1_AD_RETENTION=1")
            argv += [PROJECT, "-c", REVISION]
            if run(argv, log).returncode != 0:
                print("MAP FAILED"); return 1
            sh(f"git checkout -- {QSF}")
            for sd in seeds:
                stem = os.path.join(ROOT, a.outdir, f"{cfg}_seed{sd}")
                print(f"\n=== FIT: {cfg} seed {sd} ===", flush=True)
                if run([f"{QB}/quartus_fit", f"--seed={sd}", "--recompile=off",
                        PROJECT, "-c", REVISION], log).returncode != 0:
                    print("FIT FAILED"); return 1
                sh(f"git checkout -- {QSF}")
                # seed echo, read back from Quartus's own report (E8's reading)
                se = sh("grep -m1 'Fitter Initial Placement Seed' "
                        f"hdl/{REVISION}.fit.rpt").stdout.strip()
                open(stem + ".seedecho.txt", 'w').write(se + "\n")
                print("    " + (se or "*** NO SEED ROW ***"))
                run([f"{QB}/quartus_sta", "-t", f"{ROOT}/sw/sta_truefmax_probe.tcl",
                     PROJECT, REVISION, stem + ".truefmax"], log)
                run([f"{QB}/quartus_sta", "-t", f"{ROOT}/sw/sta_chain_anatomy.tcl",
                     PROJECT, REVISION, stem, a.npaths], log)
                sh(f"git checkout -- {QSF}")
    finally:
        sh(f"git checkout -- {SDC} {QSF}")
        left = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
        print("\nhdl/ restored: %s" % ("CLEAN" if not left else "*** DIRTY ***\n" + left))
    return 0


if __name__ == '__main__':
    sys.exit(main())
