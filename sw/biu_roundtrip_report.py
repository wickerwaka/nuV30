#!/usr/bin/env python3
"""WAVE 10 -- THE REPORTER for `sw/sta_biu_roundtrip.tcl` + `sta_truefmax_probe.tcl`.

MEASUREMENT ONLY.  It reports the CONTROLS FIRST (K-1) and refuses to print a
census row for a draw whose controls did not pass.

usage:  python3 sw/biu_roundtrip_report.py [--dir sw/testdata/wave10] [cells...]
"""
import argparse
import glob
import os
import re
import statistics
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

CELL_ORDER = ['uncut_control', 'uncut_retention', 'cut_control', 'cut_retention',
              'qripe_reg_control', 'qripe_tie_control']


def parse_census(p):
    t = open(p).read()
    d = {'file': p, 'ctl_ok': 'CONTROLS: ALL PASS' in t,
         'ax_ok': 'AX CONTROLS: ALL PASS' in t}
    for k, rx in (('pc_w1', r'PC-W1 PASS'), ('pc_w23', r'PC-W2/W3 PASS'),
                  ('pc_w5', r'PC-W5 PASS')):
        d[k] = bool(re.search(rx, t))
    m = re.search(r'get_pins\s+(\d+) -> paths (\d+)', t)
    d['pins_paths'] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r'get_nodes\s+(\d+) -> paths (\d+)', t)
    d['nodes_paths'] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r'ONE NAMED PIN : (-?\d+)', t)
    d['pcw2'] = int(m.group(1)) if m else None
    m = re.search(r'BULK -through of (\d+) pins yields : (-?\d+)', t)
    d['bulk'] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r'slack\s+([-+][\d.]+)\s+levels\s+(\S+)\s+data delay\s+([\d.]+)', t)
    if m:
        d['worst_slack'] = float(m.group(1))
        d['worst_levels'] = m.group(2)
        d['worst_delay'] = float(m.group(3))
    m = re.search(r'BIU nodes \(all points\) (\d+)\s+\(data section\) (\d+)\s+'
                  r'q_ripe_lead_n points (\d+)', t)
    if m:
        d['worst_biu'] = int(m.group(1))
        d['worst_biu_data'] = int(m.group(2))
        d['worst_ripe'] = int(m.group(3))
    m = re.search(r'span WAVE 9 convention ([\d.]+) ns\s+span WAVE 8 convention ([\d.]+)', t)
    if m:
        d['worst_s9'] = float(m.group(1))
        d['worst_s8'] = float(m.group(2))
    d['pop'] = {}
    for blk in re.split(r'--- POPULATION ', t)[1:]:
        tag = blk.split('---')[0].strip()
        g = {}
        for key, rx in (
                ('n', r'paths scanned\s+: (\d+)'),
                ('pairs', r'DISTINCT \(from,to\) endpoint pairs\s+: (\d+)'),
                ('carry', r'carrying the round trip \(all points\)\s+: (\d+)'),
                ('carry_data', r'carrying it in the DATA SECTION\s+: (\d+)'),
                ('carry_p8', r"under WAVE 8's normalising predicate\s+: (\d+)"),
                ('ripe', r'carrying `q_ripe_lead_n` BY NAME\s+: (\d+)'),
                ('kw', r'matching the KNOWN-WRONG type prefix\s+: (\d+)'),
                ('abs', r'matching an instance that does not exist\s+: (\d+)'),
                ('s9', r'mean span, WAVE 9 convention \(ns\)\s+: ([\d.]+)'),
                ('s9max', r'max  span, WAVE 9 convention \(ns\)\s+: ([\d.]+)'),
                ('s8', r'mean span, WAVE 8 convention \(ns\)\s+: ([\d.]+)')):
            m = re.search(rx, blk)
            if m:
                g[key] = float(m.group(1)) if '.' in m.group(1) else int(m.group(1))
        g.setdefault('s9', None)
        g.setdefault('s8', None)
        d['pop'][tag] = g
    return d


def parse_truefmax(p):
    t = open(p).read()
    out = {}
    for blk in re.split(r'\n--- ', t)[1:]:
        label = blk.split('\n')[0].split('(')[0].strip().split()[0]
        m = re.search(r'k = ([\d.]+)\s+slack = ([-+][\d.]+)\s+->\s+T_min\s+([\d.]+) ns\s+=\s+([\d.]+) MHz', blk)
        if m and label not in out:
            out[label] = {'k': float(m.group(1)), 'slack': float(m.group(2)),
                          'tmin': float(m.group(3)), 'mhz': float(m.group(4))}
    m = re.search(r'TRUE CEILING over the five classes: T_min ([\d.]+) ns = ([\d.]+) MHz', t)
    if m:
        out['CEILING'] = {'tmin': float(m.group(1)), 'mhz': float(m.group(2))}
    return out


def collect(d):
    draws = {}
    for p in sorted(glob.glob(os.path.join(d, '*_seed*.txt'))):
        if p.endswith('.truefmax.txt') or p.endswith('.arrivalpoints.txt') \
           or p.endswith('.rows.txt') or p.endswith('.seedecho.txt'):
            continue
        stem = p[:-4]
        name = os.path.basename(stem)
        m = re.match(r'(.+)_seed(\d+)$', name)
        if not m:
            continue
        cell, seed = m.group(1), int(m.group(2))
        rec = {'cell': cell, 'seed': seed, 'stem': stem, 'census': parse_census(p)}
        tf = stem + '.truefmax.txt'
        rec['truefmax'] = parse_truefmax(tf) if os.path.exists(tf) else {}
        draws.setdefault(cell, []).append(rec)
    for v in draws.values():
        v.sort(key=lambda r: r['seed'])
    return draws


P = print


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default=os.path.join(ROOT, 'sw/testdata/wave10'))
    a = ap.parse_args()
    draws = collect(a.dir)
    if not draws:
        P('no draws in ' + a.dir)
        return 1
    order = [c for c in CELL_ORDER if c in draws] + \
            [c for c in sorted(draws) if c not in CELL_ORDER]

    P('=' * 100)
    P('WAVE 10 -- THE UNIFIED BIU ROUND-TRIP CENSUS.  CONTROLS FIRST (K-1).')
    P('=' * 100)
    P('')
    P('  cell / seed            | PC-W1 | PC-W2/3 | PC-W5 | AX | pins->paths | nodes->paths | 1-pin BIU | bulk BIU')
    all_ok = True
    for c in order:
        for r in draws[c]:
            k = r['census']
            ok = k['ctl_ok'] and k['ax_ok']
            all_ok &= ok
            pp = k['pins_paths'] or ('-', '-')
            np_ = k['nodes_paths'] or ('-', '-')
            bk = k['bulk'] or ('-', '-')
            P(f"  {c:18s} s{r['seed']} | {'PASS' if k['pc_w1'] else 'FAIL':5s} "
              f"| {'PASS' if k['pc_w23'] else 'FAIL':7s} | {'PASS' if k['pc_w5'] else 'FAIL':5s} "
              f"| {'OK' if k['ax_ok'] else '**':2s} | {pp[0]:5d}->{pp[1]:<5d} "
              f"| {np_[0]:5d}->{np_[1]:<5d} | {str(k['pcw2']):9s} | {bk[1]}")
    P('')
    P('  CONTROLS: ' + ('ALL PASS' if all_ok else '*** A DRAW FAILED -- ITS ROWS MAY NOT BE QUOTED ***'))

    P('')
    P('=' * 100)
    P('THE CENSUS.  BOTH POPULATIONS, ONE PREDICATE, PER DRAW.')
    P('=' * 100)
    P('')
    P('  cell / seed            | SAME k | T_min  |   MHz | worst arc ns | BIU on worst |'
      ' POP-A carry   | POP-B carry   | span9 A | span8 A')
    for c in order:
        for r in draws[c]:
            k = r['census']
            tf = r['truefmax']
            sm = tf.get('SAME', {})
            ce = tf.get('CEILING', {})
            A = k['pop'].get('A_topN', {})
            B = k['pop'].get('B_nworst1', {})
            def frac(g):
                if not g:
                    return '   --        '
                return f"{g.get('carry', 0):4d} / {g.get('n', 0):<4d} {100.0*g.get('carry',0)/max(1,g.get('n',1)):5.1f}%"
            P(f"  {c:18s} s{r['seed']} | {sm.get('k', 0):6.4f} | {ce.get('tmin', 0):6.3f} "
              f"| {ce.get('mhz', 0):5.2f} | {k.get('worst_delay', 0):12.3f} "
              f"| {k.get('worst_biu', -1):3d} ({k.get('worst_ripe', -1)} ripe) "
              f"| {frac(A)} | {frac(B)} "
              f"| {(f'{A.get(chr(115)+chr(57)):7.3f}' if A.get('s9') is not None else '     --'):7s} "
              f"| {(f'{A.get(chr(115)+chr(56)):7.3f}' if A.get('s8') is not None else '     --'):7s}")

    P('')
    P('=' * 100)
    P('P-1 .. P-5, SCORED AS REGISTERED.  k(cell) = draws whose POP-A carries it on >= 90 % of paths.')
    P('=' * 100)
    P('')
    for c in order:
        n = len(draws[c])
        kk = 0
        for r in draws[c]:
            A = r['census']['pop'].get('A_topN', {})
            if A.get('n') and A['carry'] / A['n'] >= 0.90:
                kk += 1
        shape = 'ALL' if kk == n else ('NONE' if kk == 0 else '*** SPLIT -- A DRAW EFFECT (P-4) ***')
        P(f'  k({c:18s}) = {kk} of {n}    {shape}')
    P('')
    P('  P-5  the two populations, within each draw:')
    dis = 0
    for c in order:
        for r in draws[c]:
            A = r['census']['pop'].get('A_topN', {})
            B = r['census']['pop'].get('B_nworst1', {})
            if not A or not B:
                continue
            fa = A['carry'] / max(1, A['n'])
            fb = B['carry'] / max(1, B['n'])
            same = (fa >= 0.9) == (fb >= 0.9)
            if not same:
                dis += 1
                P(f'    {c} s{r["seed"]}: POP-A {fa*100:.1f}%  POP-B {fb*100:.1f}%   <-- DISAGREE')
    P(f'    draws on which the two populations disagree about presence: {dis}')

    P('')
    P('=' * 100)
    P('THE ARC, PER CELL (means over the cell\'s draws)')
    P('=' * 100)
    P('')
    P('  cell                   | n | worst arc ns  mean (min..max)      | T_min ns mean | MHz mean | MHz worst-of-n')
    for c in order:
        ds = [r['census'].get('worst_delay') for r in draws[c] if r['census'].get('worst_delay')]
        ts = [r['truefmax'].get('CEILING', {}).get('tmin') for r in draws[c]]
        ts = [x for x in ts if x]
        ms = [r['truefmax'].get('CEILING', {}).get('mhz') for r in draws[c]]
        ms = [x for x in ms if x]
        if not ds:
            continue
        P(f'  {c:22s} | {len(ds)} | {statistics.mean(ds):8.3f} ({min(ds):.3f}..{max(ds):.3f}) '
          f'| {statistics.mean(ts) if ts else 0:13.3f} | {statistics.mean(ms) if ms else 0:8.2f} '
          f'| {min(ms) if ms else 0:14.2f}')
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main())
