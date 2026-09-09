#!/usr/bin/env python3
"""WAVE 6 -- THE REPORTER.  It reads the artifacts and scores the registered
bars.  MEASUREMENT ONLY; it computes nothing the artifacts do not contain.

It ARCHIVES the Quartus reports it quotes into `sw/testdata/chainflat/` first,
because a number with no artifact id is not quotable.
"""
import argparse
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    '..'))
SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/chainflat')
OUT = os.path.join(ROOT, 'sw/testdata/chainflat')

ALM = re.compile(r'Estimate of Logic utilization \(ALMs needed\)\s*;\s*(\d+)')
CALUT = re.compile(r'Combinational ALUT usage for logic\s*;\s*(\d+)')
DREG = re.compile(r'Dedicated logic registers\s*;\s*(\d+)')
FALM = re.compile(r'Logic utilization \(in ALMs\)\s*;\s*([\d,]+)')
FREG = re.compile(r'Total registers\s*;\s*([\d,]+)')
SEED = re.compile(r'Fitter Initial Placement Seed\s*;\s*(\d+)')
HEXOK = re.compile(r'ucrom\.hex\(1\)')


def grab(path, rx):
    if not os.path.exists(path):
        return None
    m = rx.search(open(path, errors='replace').read())
    return m.group(1) if m else None


# ⚠ `^` WITHOUT `re.M` ANCHORS AT THE START OF THE WHOLE STRING.  The first
# form of this file had all six of these without it and every field parsed to
# None -- an instrument returning nothing where it should return a number.
SEG = re.compile(r'^\s*seg (\d+)\s+([\d.]+) -> \s*([\d.]+)\s+=\s+([\d.]+)\s+'
                 r'cells\s+(\d+)\s+luts\s+(\d+)(.*)$', re.M)
SLK = re.compile(r'^\s*slack\s+(-?[\d.]+)', re.M)
DDY = re.compile(r'^\s*data delay\s+([\d.]+)', re.M)
LVL = re.compile(r'^\s*levels\s+(\d+) cells / (\d+) combout', re.M)
BND = re.compile(r'^\s*boundaries\s+(\d+)\s*$', re.M)
CEN = re.compile(r'^\s+([a-z_A-Z0-9]+)\s+(\d+)\s*$', re.M)
CTL = re.compile(r'RESULT controls=(\w+)')
BUCK = re.compile(r'boundaries\s+(-?\d+) : worst data delay\s+([\d.]+)\s+count (\d+)')


def read_sta(path):
    if not os.path.exists(path):
        return None
    t = open(path, errors='replace').read()
    segs = []
    for line in t.split('\n'):
        m = SEG.match(line)
        if m:
            segs.append({'i': int(m.group(1)), 'a': float(m.group(2)),
                         'b': float(m.group(3)), 'ns': float(m.group(4)),
                         'cells': int(m.group(5)), 'luts': int(m.group(6)),
                         'names': m.group(7).strip()})
    census = {}
    incens = False
    for line in t.split('\n'):
        if 'D. COPY CENSUS' in line:
            incens = True
            continue
        if incens:
            m = CEN.match(line)
            if m:
                census[m.group(1)] = int(m.group(2))
    buckets = {int(m.group(1)): (float(m.group(2)), int(m.group(3)))
               for m in BUCK.finditer(t)}
    def one(rx, cast=float, g=1):
        m = rx.search(t)
        return cast(m.group(g)) if m else None
    return {
        'controls': (CTL.search(t).group(1) if CTL.search(t) else None),
        'slack': one(SLK), 'data_delay': one(DDY),
        'levels_cells': one(LVL, int, 1), 'levels_lut': one(LVL, int, 2),
        'boundaries': one(BND, int),
        'segments': segs, 'census': census, 'buckets': buckets,
        'pc1': 'PC-1 PASS' in t, 'pc2': 'PC-2 PASS' in t,
        'pc3': 'PC-3 PASS' in t}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seeds', default='1,2,3')
    ap.add_argument('--kinds', default='ref,flat')
    ap.add_argument('--pc-seeds', default='',
                    help="AMENDMENT A-1: score P-1'(c) and P-1\" on THESE "
                         "seeds only -- the ones that did not select the "
                         "replacement bar.")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for kind in a.kinds.split(','):
        proj = os.path.join(SCRATCH, 'proj_' + kind)
        mp = os.path.join(proj, 'output', 'cf.map.rpt')
        fp = os.path.join(proj, 'output', 'cf.fit.rpt')
        for src, dst in ((mp, f'{kind}.map.rpt'), (fp, f'{kind}.fit.rpt')):
            if os.path.exists(src):
                shutil.copyfile(src, os.path.join(OUT, dst))
        r = {'as_alms': grab(mp, ALM), 'as_comb_aluts': grab(mp, CALUT),
             'as_registers': grab(mp, DREG),
             'fit_alms': grab(fp, FALM), 'fit_registers': grab(fp, FREG),
             'fit_seed': grab(fp, SEED),
             'hex_loaded_positively': bool(HEXOK.search(
                 open(mp, errors='replace').read())) if os.path.exists(mp)
             else None,
             'seeds': {}}
        for sd in a.seeds.split(','):
            st = read_sta(os.path.join(OUT, f'{kind}_seed{sd}.txt'))
            if st:
                r['seeds'][sd] = st
        res[kind] = r
    json.dump(res, open(os.path.join(OUT, 'report.json'), 'w'), indent=1)

    def p(*x):
        print(*x)
    p('=== AREA (Analysis & Synthesis, one map per project) ===')
    p('%-6s %12s %16s %12s' % ('', 'ALMs(est)', 'comb ALUTs', 'registers'))
    for k, v in res.items():
        p('%-6s %12s %16s %12s' % (k, v['as_alms'], v['as_comb_aluts'],
                                   v['as_registers']))
    if res.get('ref', {}).get('as_comb_aluts') and \
       res.get('flat', {}).get('as_comb_aluts'):
        a0 = int(res['ref']['as_comb_aluts'])
        a1 = int(res['flat']['as_comb_aluts'])
        p('  comb ALUT change: %+d  (%+.1f %%)   [P-4a asks <= -25 %%]'
          % (a1 - a0, 100.0 * (a1 - a0) / a0))
        b0 = int(res['ref']['as_alms'])
        b1 = int(res['flat']['as_alms'])
        p('  ALM(est) change : %+d  (%+.1f %%)' % (b1 - b0,
                                                   100.0 * (b1 - b0) / b0))
    p()
    p('=== THE WORST reg -> reg ARC, PER FIT SEED ===')
    p('%-6s %5s %9s %9s %8s %6s %s'
      % ('', 'seed', 'slack', 'data ns', 'cells', 'bnds', 'segments (ns)'))
    means = {}
    for k, v in res.items():
        for sd, st in sorted(v['seeds'].items()):
            segs = st['segments']
            p('%-6s %5s %9.3f %9.3f %8d %6d  %s'
              % (k, sd, st['slack'], st['data_delay'], st['levels_cells'],
                 st['boundaries'],
                 ' '.join('%.3f' % s['ns'] for s in segs)))
            means.setdefault(k, []).append(st['data_delay'])
    if 'ref' in means and 'flat' in means:
        m0 = sum(means['ref']) / len(means['ref'])
        m1 = sum(means['flat']) / len(means['flat'])
        p('  mean worst-arc data delay   REF %.3f   FLAT %.3f   '
          '%+.3f ns (%+.1f %%)   [P-4b band +/-15 %%]'
          % (m0, m1, m1 - m0, 100.0 * (m1 - m0) / m0))
    p()
    p('=== P-1  THE POSITIVE CONTROL (REF) ===')
    ref = res.get('ref', {})
    ok_a = ok_b = ok_c = None
    fold = []
    for sd, st in sorted(ref.get('seeds', {}).items()):
        segs = st['segments']
        nb = st['boundaries']
        a_ok = nb >= 2
        seg0 = segs[0]['ns'] if segs else 0.0
        b_ok = all(seg0 >= s['ns'] for s in segs[1:])
        c = st['census']
        c_ok = (c.get('st_n', 0) >= 20
                and c.get('rst_ctr_n', 99) <= 1
                and c.get('ld_dlo_n', 99) <= 1
                and c.get('ld_ripe_prev_n', 99) <= 1
                and c.get('zzz_no_such_signal', 99) == 0)
        folded = [s['ns'] for s in segs[1:]]
        fold += folded
        p('  seed %s  boundaries %d (>=2: %s)   seg0 %.3f largest: %s   '
          'census st_n %s rst_ctr_n %s ld_dlo_n %s ld_ripe_prev_n %s '
          'zzz %s -> %s'
          % (sd, nb, a_ok, seg0, b_ok, c.get('st_n'), c.get('rst_ctr_n'),
             c.get('ld_dlo_n'), c.get('ld_ripe_prev_n'),
             c.get('zzz_no_such_signal'), c_ok))
        p('           controls %s (PC-1 %s PC-2 %s PC-3 %s)'
          % (st['controls'], st['pc1'], st['pc2'], st['pc3']))
        ok_a = a_ok if ok_a is None else (ok_a and a_ok)
        ok_b = b_ok if ok_b is None else (ok_b and b_ok)
        ok_c = c_ok if ok_c is None else (ok_c and c_ok)
    if fold:
        p('  P-1d per-folded-position delay: n=%d  min %.3f  max %.3f  '
          'mean %.3f   [band 2.0-9.0, WAVE 5 in-situ mean 5.359]'
          % (len(fold), min(fold), max(fold), sum(fold) / len(fold)))
    p('  P-1 (a) %s  (b) %s  (c) %s' % (ok_a, ok_b, ok_c))
    if a.pc_seeds:
        p()
        p("=== AMENDMENT A-1 -- P-1'(c) AND P-1\" ON SEEDS %s ==="
          % a.pc_seeds)
        CHAINABLE = ['st_n', 'stop', 'st_zero_ok', 'ld_b_n', 'pv', 'opc_base',
                     'm_kind', 'seg_override_n']
        POS0 = ['rst_ctr_n', 'ld_dlo_n', 'ld_ripe_prev_n', 'nmi_latch_n',
                'rloop_n_n']
        FRONT = ['sigma', 's1_val', 'it_val']
        ok1 = ok2 = True
        for sd in a.pc_seeds.split(','):
            rs = res.get('ref', {}).get('seeds', {}).get(sd)
            fs = res.get('flat', {}).get('seeds', {}).get(sd)
            if not rs:
                p('  seed %s: NO REF STA -- CANNOT SCORE' % sd)
                ok1 = ok2 = False
                continue
            c = rs['census']
            lo = min(c.get(n, 0) for n in
                     ('st_n', 'ld_b_n', 'pv', 'opc_base'))
            hi = max(c.get(n, 0) for n in POS0)
            zz = c.get('zzz_no_such_signal', 99)
            r1 = (lo >= 10 * hi) and zz == 0
            ok1 = ok1 and r1
            p("  P-1'(c) seed %s: min(chainable)=%d  >= 10 x "
              'max(pos0-only)=%d  (= %d)   zzz=%d   -> %s'
              % (sd, lo, hi, 10 * hi, zz, 'PASS' if r1 else 'FAIL'))
            if not fs:
                p('  seed %s: NO FLAT STA -- CANNOT SCORE P-1"' % sd)
                ok2 = False
                continue
            fc = fs['census']
            fell = {n: (c.get(n, 0), fc.get(n, 0)) for n in CHAINABLE}
            kept = {n: (c.get(n, 0), fc.get(n, 0)) for n in FRONT}
            r2a = all(v[1] < v[0] for v in fell.values())
            r2b = all(v[1] >= v[0] for v in kept.values())
            ok2 = ok2 and r2a and r2b
            p('  P-1"    seed %s: chainable all FELL: %s   %s'
              % (sd, r2a, ' '.join('%s %d->%d' % (n, v[0], v[1])
                                   for n, v in fell.items())))
            p('               front-end none fell: %s   %s'
              % (r2b, ' '.join('%s %d->%d' % (n, v[0], v[1])
                               for n, v in kept.items())))
        p("  P-1'(c) %s     P-1\" %s"
          % ('MET' if ok1 else 'MISSED', 'MET' if ok2 else 'MISSED'))
    p()
    p('wrote %s' % os.path.join(OUT, 'report.json'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
