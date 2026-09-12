#!/usr/bin/env python3
"""WAVE 10 -- THE DRIVER FOR THE UNIFIED BIU ROUND-TRIP CENSUS.
MEASUREMENT ONLY, NO GATE, NO RECEIPT, NO Fmax.

It runs `sw/sta_biu_roundtrip.tcl` -- ONE instrument, BOTH population questions
-- across the configurations and seeds it is given, in whatever repository root
it is pointed at.  **THAT IS THE POINT: WAVE 8 measured the UNCUT tree and
WAVE 9 the CUT tree with two different instruments, so neither difference can
be attributed.  Here the instrument is held fixed and the tree varies.**

`--root` names the repository to build in.  A CUT-tree measurement is taken in
a SCRATCH GIT WORKTREE (WAVE 10 bar K-6: `hdl/` in the main tree carries no
tracked modification at the start or at the end, and nothing is landed).

THE NO-EXCEPTION CONFIGURATION IS THE GOAL STATE (USER RULING 2026-09-08:
*"I don't want custom sdc rules, period."*).  The CE multicycle is deleted from
`hdl/nec_test.sdc` FOR THE MEASUREMENT FITS ONLY and restored with
`git checkout --` in a `finally`, whatever happens.  The anchor text is
IMPORTED from `sw/l2_noexc_g6.py` and never re-typed.
⚠ A tree in which the exception is ALREADY absent (WAVE 9's `bacf7f9fd9`
deleted it) is detected and left alone -- and SAID SO, because silently
patching nothing and silently patching something must not look alike.

⚠ THE DELETION IS CHECKED, NOT ASSERTED: `sta_truefmax_probe.tcl` runs beside
the census on every draw and its core `SAME` class must measure k = 1.0.

MAP ONCE PER CONFIGURATION, FIT ONCE PER SEED.
⚠ `hdl/nec_test_ucore.qsf` is rewritten by `quartus_map` (the declared sec.70.7
exemption) and is restored after EVERY Quartus stage.
Single-writer guard by EXACT binary name before every stage.
"""
import argparse
import os
import subprocess
import sys
import time

QB = os.path.expanduser('~/intelFPGA_lite/17.1/quartus/bin')
PROJECT, REVISION = 'nec_test', 'nec_test_ucore'
QSF = 'hdl/nec_test_ucore.qsf'
SDC = 'hdl/nec_test.sdc'
HERE = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from l2_noexc_g6 import PRESENT, DELETED          # noqa: E402  one anchor, not two


def sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)


def guard():
    for b in ('quartus_map', 'quartus_fit', 'quartus_sta', 'quartus_asm', 'quartus_sh'):
        if sh(f'pgrep -x {b}').returncode == 0:
            print(f'REFUSING: {b} is running -- two writers on one db')
            return False
    return True


def run(argv, root, log):
    t0 = time.time()
    print('  $ ' + ' '.join(argv), flush=True)
    r = subprocess.run(argv, cwd=os.path.join(root, 'hdl'),
                       capture_output=True, text=True)
    open(log, 'a').write(r.stdout + r.stderr)
    print(f'    exit {r.returncode}  {time.time()-t0:.0f}s', flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.abspath(os.path.join(HERE, '..')),
                    help='repository root to build in (a scratch worktree for the CUT tree)')
    ap.add_argument('--label', required=True, help='e.g. uncut / cut -- names the artifacts')
    ap.add_argument('--control-seeds', default='1,2,3')
    ap.add_argument('--retention-seeds', default='1,2,3')
    ap.add_argument('--outdir', default='sw/testdata/wave10')
    ap.add_argument('--na', default='200')
    ap.add_argument('--nb', default='400')
    ap.add_argument('--skip-map', action='store_true')
    ap.add_argument('--clean-db', action='store_true',
                    help='remove hdl/db + hdl/incremental_db before each MAP.  '
                         '⚠ WAVE 10 CONTROL PC-C0: the QSF carries SMART_RECOMPILE ON, '
                         'and a re-run of a BYTE-IDENTICAL tree at the SAME SEED against '
                         'a db left by another tree drew 35.867 ns where WAVE 8 drew '
                         '34.220.  Every cell of this wave is compiled from the same '
                         'db state, and this flag is what makes that true.')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--allow-arm-dirty', action='store_true',
                    help='permit tracked changes under hdl/rtl/ucore/ in a SCRATCH '
                         'WORKTREE -- this is how a CEILING PROBE ARM is compiled.  '
                         '⚠ It is REFUSED unless --root is a worktree under '
                         '~/.cache/ucsimt-tmp/, so it can never loosen the main '
                         'tree\'s K-6 guarantee, and the permitted diff is PRINTED.')
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    tcl = os.path.join(HERE, 'sta_biu_roundtrip.tcl')
    tfx = os.path.join(HERE, 'sta_truefmax_probe.tcl')
    for f in (tcl, tfx):
        if not os.path.exists(f):
            print('REFUSING: missing instrument ' + f)
            return 2

    outdir = os.path.abspath(a.outdir)
    os.makedirs(outdir, exist_ok=True)
    log = os.path.join(outdir, f'{a.label}.run.log')
    open(log, 'w').write(f'=== run_biu_roundtrip {a.label} root={root} ===\n')

    scratch = os.path.expanduser('~/.cache/ucsimt-tmp/')
    # ⚠ `hdl/build_id.v` is GENERATED by the MiSTer PRE_FLOW script, which runs
    # only under `quartus_sh --flow compile` and NOT under a bare `quartus_map`.
    # It is `.gitignore`d, so a fresh worktree does not have it and A&S dies with
    # `Error (10054) ... can't open "build_id.v"`.  It is COPIED FROM THE MAIN
    # TREE rather than regenerated, so that the arm and the reference differ by
    # the ARM EDIT AND NOTHING ELSE -- a regenerated file could carry a different
    # BUILD_DATE and that would be a second difference between two builds whose
    # whole value is that they have exactly one.  The content is PRINTED.
    MAIN = os.path.abspath(os.path.join(HERE, '..'))
    bid = os.path.join(root, 'hdl', 'build_id.v')
    if not os.path.exists(bid):
        src = os.path.join(MAIN, 'hdl', 'build_id.v')
        if not os.path.exists(src):
            print('REFUSING: no hdl/build_id.v in the main tree to copy from.')
            return 2
        import shutil as _sh
        _sh.copyfile(src, bid)
        print(f'  build_id.v COPIED from the main tree (generated, gitignored): '
              f'{open(bid).read().strip()!r}')

    dirty = sh("git status --porcelain hdl/ | grep -v '^??'", root).stdout.strip()
    if dirty:
        if not (a.allow_arm_dirty and root.startswith(scratch)):
            print(f'REFUSING: {root}/hdl carries tracked changes:\n' + dirty)
            if a.allow_arm_dirty:
                print('  (--allow-arm-dirty is REFUSED outside ~/.cache/ucsimt-tmp/)')
            return 2
        print('⚠⚠ CEILING-PROBE ARM: tracked changes under a SCRATCH WORKTREE are')
        print('   permitted for this run and are PRINTED IN FULL.  THE ARM IS')
        print('   BEHAVIOUR-BREAKING BY CONSTRUCTION AND IS NEVER LANDED.')
        print(dirty)
        print(sh('git diff -- hdl/', root).stdout)
    if not guard():
        return 2

    sdcp = os.path.join(root, SDC)
    s = open(sdcp).read()
    npresent = s.count(PRESENT)
    active = len([l for l in open(sdcp) if l.lstrip().startswith('set_multicycle_path')])
    print(f'  {root}/{SDC}: exception block present x{npresent}, '
          f'active set_multicycle_path lines {active}')
    patched = False
    if npresent == 1:
        open(sdcp, 'w').write(s.replace(PRESENT, DELETED, 1))
        patched = True
        print('  PATCHED for the measurement (restored in a finally)')
    elif npresent == 0 and active == 0:
        print('  THE EXCEPTION IS ALREADY ABSENT IN THIS TREE -- nothing patched, '
              'and this line is the record that nothing was.')
    else:
        print(f'REFUSING: cannot establish the no-exception configuration '
              f'(block x{npresent}, active lines {active}).  Re-derive the anchor.')
        return 2

    try:
        active = len([l for l in open(sdcp) if l.lstrip().startswith('set_multicycle_path')])
        print(f'  active set_multicycle_path lines now: {active} (MUST be 0)')
        if active:
            print('REFUSING to build: an exception survives.')
            return 2
        if a.dry_run:
            print(sh(f'git diff -- {SDC}', root).stdout)
            return 0
        for cfg, seeds in (('control', a.control_seeds),
                           ('retention', a.retention_seeds)):
            seeds = [x for x in seeds.split(',') if x.strip()]
            if not seeds:
                continue
            if a.skip_map:
                print(f'\n=== MAP: {a.label} {cfg} SKIPPED ===', flush=True)
            else:
                if a.clean_db:
                    for d in ('db', 'incremental_db', 'output_files_ucore'):
                        pth = os.path.join(root, 'hdl', d)
                        if os.path.isdir(pth):
                            sh(f'rm -rf {pth}')
                    print(f'  CLEAN DB: hdl/db, hdl/incremental_db, '
                          f'hdl/output_files_ucore removed (PC-C0)')
                print(f'\n=== MAP: {a.label} {cfg} ===', flush=True)
                argv = [f'{QB}/quartus_map']
                if cfg == 'retention':
                    argv.append('--verilog_macro=X1_AD_RETENTION=1')
                argv += [PROJECT, '-c', REVISION]
                if run(argv, root, log).returncode:
                    print('MAP FAILED')
                    return 1
                sh(f'git checkout -- {QSF}', root)
            for sd in seeds:
                if not guard():
                    return 2
                stem = os.path.join(outdir, f'{a.label}_{cfg}_seed{sd}')
                print(f'\n=== FIT: {a.label} {cfg} seed {sd} ===', flush=True)
                if run([f'{QB}/quartus_fit', f'--seed={sd}', '--recompile=off',
                        PROJECT, '-c', REVISION], root, log).returncode:
                    print('FIT FAILED')
                    return 1
                sh(f'git checkout -- {QSF}', root)
                se = sh("grep -m1 'Fitter Initial Placement Seed' "
                        f'hdl/output_files_ucore/{REVISION}.fit.rpt', root).stdout.strip()
                open(stem + '.seedecho.txt', 'w').write(se + '\n')
                print('    ' + (se or '*** NO SEED ROW ***'))
                run([f'{QB}/quartus_sta', '-t', tfx, PROJECT, REVISION, stem], root, log)
                run([f'{QB}/quartus_sta', '-t', tcl, PROJECT, REVISION, stem,
                     a.na, a.nb], root, log)
                sh(f'git checkout -- {QSF}', root)
    finally:
        if patched:
            sh(f'git checkout -- {SDC}', root)
        sh(f'git checkout -- {QSF}', root)
        left = sh("git status --porcelain hdl/ | grep -v '^??'", root).stdout.strip()
        print('\n%s/hdl restored: %s' % (root, 'CLEAN' if not left else '*** DIRTY ***\n' + left))
    return 0


if __name__ == '__main__':
    sys.exit(main())
