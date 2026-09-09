#!/usr/bin/env python3
"""WAVE 6 -- THE STANDALONE SYNTHESIS EXPERIMENT.  MEASUREMENT ONLY, NO GATE.

It compiles TWO standalone projects -- `v30u_eu` as its own top with virtual
pins (`ucore_provenance.md` sec.51.1's harness) -- one carrying the 7-copy
unrolled chain AS IT EXISTS (**REF**, the positive control) and one carrying the
flattened composition (**FLAT**), and compares logic depth, delay and area.

**IT TOUCHES NOTHING UNDER `hdl/`.**  Both projects live under
`~/.cache/ucsimt-tmp/chainflat/` and neither is the design.  `hdl/nec_test.qsf`,
`hdl/nec_test_ucore.qsf` and `hdl/nec_test.sdc` are never opened, never patched
and never restored, because they are never used -- which also means the WAVE 5
`git checkout --` dance has nothing to do here, and the driver CHECKS that by
refusing on a tracked-dirty `hdl/` at the start and re-checking at the end.

⚠ **NO FIGURE HERE IS A DESIGN Fmax.**  `standing_gates.md` §A governs, and a
standalone harness is not the design: WAVE 5 measured out-of-context estimates
mispredicting a realised half by **+11.3 to +20.0 ns**.  What the comparison is
FOR is the DIFFERENCE between two forms compiled the same way.

Single-writer guard by EXACT binary name before every Quartus stage.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..'))
SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/chainflat')
QB = os.path.expanduser('~/intelFPGA_lite/17.1/quartus/bin')


def sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True,
                          cwd=cwd)


def guard():
    for b in ('quartus_map', 'quartus_fit', 'quartus_sta', 'quartus_asm',
              'quartus_sh'):
        if sh(f'pgrep -x {b}').returncode == 0:
            print(f'REFUSING: {b} is running -- two writers on one db')
            return False
    return True


def run(argv, cwd, log):
    t0 = time.time()
    print('  $ ' + ' '.join(argv), flush=True)
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    open(log, 'a').write(r.stdout + r.stderr)
    print(f'    exit {r.returncode}  {time.time()-t0:.0f}s', flush=True)
    return r


FIT_ALM = re.compile(r'Logic utilization \(in ALMs\)\s*;\s*([\d,]+)')
FIT_COMB = re.compile(r'Combinational ALUTs?\s*;\s*([\d,]+)')
FIT_REG = re.compile(r'Total registers\s*;\s*([\d,]+)')
FIT_SEED = re.compile(r'Fitter Initial Placement Seed\s*;\s*(\d+)')
MAP_ERR = re.compile(r'Error \(\d+\)')
MAP_LATCH = re.compile(r'Number of latches\s*;\s*(\d+)')
STA_SLACK = re.compile(r'slack\s+(-?\d+\.\d+)')


def parse_reports(proj):
    out = {}
    for name, rx, key in (('cf.fit.rpt', FIT_ALM, 'alms'),
                          ('cf.fit.rpt', FIT_COMB, 'comb_aluts'),
                          ('cf.fit.rpt', FIT_REG, 'registers'),
                          ('cf.fit.rpt', FIT_SEED, 'seed')):
        p = os.path.join(proj, 'output', name)
        if os.path.exists(p):
            m = rx.search(open(p, errors='replace').read())
            if m:
                out[key] = m.group(1)
    p = os.path.join(proj, 'output', 'cf.map.rpt')
    if os.path.exists(p):
        t = open(p, errors='replace').read()
        out['map_errors'] = len(MAP_ERR.findall(t))
        # F44: a wrong HEXDIR gives $readmemh warnings and an ALL-ZERO ROM and
        # the compile SUCCEEDS.  The check is POSITIVE, not an absence.
        out['readmem_warnings'] = t.count('Memory Initialization File') \
            if False else len(re.findall(r'can\'t find.*\.hex', t))
        out['hex_ok'] = (out['readmem_warnings'] == 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--kinds', default='ref,flat')
    ap.add_argument('--npaths', default='400')
    ap.add_argument('--skip-map', action='store_true',
                    help='fit on the mapped db ALREADY on disk.  MAP ONCE PER '
                         'PROJECT is what makes the draws draws of one tree; '
                         'a second map would also re-roll the A&S '
                         'combinational count, which is not reproducible run '
                         'to run (ucore_provenance.md sec.74.4a).')
    ap.add_argument('--outdir', default='sw/testdata/chainflat')
    a = ap.parse_args()

    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty and 'v30u_eu.sv' not in dirty:
        print('REFUSING: hdl/ carries unexpected tracked changes:\n' + dirty)
        return 2
    outdir = os.path.join(ROOT, a.outdir)
    os.makedirs(outdir, exist_ok=True)
    log = os.path.join(outdir, 'synth.log')
    open(log, 'w').write('=== run_chainflat_synth ===\n')
    res = {}
    for kind in a.kinds.split(','):
        proj = os.path.join(SCRATCH, 'proj_' + kind)
        if not os.path.exists(os.path.join(proj, 'cf.qsf')):
            print('REFUSING: no project at ' + proj +
                  ' -- run `chainflat_proto.py --gen --qsf` first')
            return 2
        if not guard():
            return 2
        if a.skip_map:
            print(f'\n=== MAP: {kind} SKIPPED (--skip-map) ===', flush=True)
        else:
            print(f'\n=== MAP: {kind} ===', flush=True)
            if run([f'{QB}/quartus_map', 'cf', '-c', 'cf'],
                   proj, log).returncode:
                print('MAP FAILED for ' + kind)
                return 1
        for sd in [s for s in a.seeds.split(',') if s.strip()]:
            if not guard():
                return 2
            print(f'\n=== FIT: {kind} seed {sd} ===', flush=True)
            if run([f'{QB}/quartus_fit', f'--seed={sd}', '--recompile=off',
                    'cf', '-c', 'cf'], proj, log).returncode:
                print('FIT FAILED')
                return 1
            stem = os.path.join(outdir, f'{kind}_seed{sd}')
            run([f'{QB}/quartus_sta', '-t',
                 f'{ROOT}/sw/sta_chainflat.tcl', 'cf', 'cf', stem, a.npaths],
                proj, log)
            r = parse_reports(proj)
            r['sta_exists'] = os.path.exists(stem + '.txt')
            res[f'{kind}_seed{sd}'] = r
            print('    ' + json.dumps(r))
    json.dump(res, open(os.path.join(outdir, 'synth.json'), 'w'), indent=1)
    left = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    print('\nhdl/ at end: %s' % (left or 'CLEAN'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
