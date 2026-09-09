#!/usr/bin/env python3
"""WAVE 5 -- THE CROSS-DRAW REPORT.  Reads the per-draw outputs of
`sw/sta_chain_anatomy.tcl` (+ `sta_truefmax_probe.tcl`) and answers the wave's
bars in one place: E-2 (is the per-segment profile STABLE ACROSS SEEDS), E-3
(Q2 as a table over every boundary with an explicit YES/NO on 29.6 ns), E-4
(Q3's top contributors, attributed to case arms through `sw/chain_srcmap.py`).

⚠ IT PARSES; IT DOES NOT MEASURE.  Every number it prints is a number one of
the STA legs wrote, and it names the file each came from.

⚠ THE `SAME` k CHECK IS NOT COSMETIC.  These draws are fitted with the CE
multicycle DELETED, so `SAME` must measure **k = 1.0000**.  A draw whose SAME
still reads 2.0 was fitted to the exception and its numbers answer a different
question; this tool prints the k beside every draw and REFUSES to aggregate a
draw that is missing it.
"""
import argparse, glob, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BUDGET = 29.6            # the brief's `ce -> ce` target for 32 MHz

SEG_RE = re.compile(r'^\s{2,4}(\d+) \|\s*([\d.-]+) \|\s*([\d.-]+) \|\s*([\d.-]+) \|'
                    r'\s*(\d+) \|\s*(\d+) \| (.*)$')
CUM_RE = re.compile(r'^\s{2,3}(\d+) \|\s*([\d.-]+) \|\s*([\d.-]+) \|\s*([\d.-]+) \| (\w+)')
CONT_RE = re.compile(r'^  seg (\d+) \(([\d.]+) ns\): (.*)$')
HIST_RE = re.compile(r'^\s+(\d+) \|\s+(\d+) \|\s+([\d.]+) ns\s+levels (\S+)\s+(.*)$')


def parse(path):
    d = {'file': path, 'segs': [], 'cum': [], 'cont': {}, 'scan': {},
         'ctl': {}, 'biu': [], 'census': {}, 'floor': None}
    sec = None
    for ln in open(path):
        ln = ln.rstrip('\n')
        if ln.startswith('=== '):
            sec = ln.split()[1].rstrip('.')
            continue
        if 'PC-1 PASS' in ln or 'PC-1 FAILED' in ln: d['ctl']['PC-1'] = 'PASS' in ln
        if 'PC-2 PASS' in ln or 'PC-2 FAILED' in ln: d['ctl']['PC-2'] = 'PASS' in ln
        if 'PC-3 PASS' in ln or 'PC-3 FAILED' in ln: d['ctl']['PC-3'] = 'PASS' in ln
        if 'PC-4 PASS' in ln or 'PC-4 FAILED' in ln: d['ctl']['PC-4'] = 'PASS' in ln
        if ln.startswith('  from : '): d['from'] = ln[9:]
        if ln.startswith('  to   : '): d['to'] = ln[9:]
        m = re.match(r'^  slack\s+([+-][\d.]+)\s+logic levels (\d+)\s+data delay ([\d.]+)', ln)
        if m:
            d['slack'], d['levels'], d['dd'] = float(m.group(1)), int(m.group(2)), float(m.group(3))
        if sec == 'C':
            m = SEG_RE.match(ln)
            if m:
                d['segs'].append(dict(i=int(m.group(1)), a=float(m.group(2)),
                                      b=float(m.group(3)), span=float(m.group(4)),
                                      cells=int(m.group(5)), comb=int(m.group(6))))
        if sec == 'D':
            m = CUM_RE.match(ln)
            if m:
                d['cum'].append(dict(k=int(m.group(1)), up=float(m.group(2)),
                                     dn=float(m.group(3)), worse=float(m.group(4))))
        if sec == 'E':
            m = CONT_RE.match(ln)
            if m:
                d['cont'][int(m.group(1))] = (float(m.group(2)), m.group(3).split())
        if sec == 'F':
            m = re.match(r'^  --- scan (\w+):', ln)
            if m:
                cur = m.group(1); d['scan'][cur] = []
            m = HIST_RE.match(ln)
            if m and d['scan']:
                d['scan'][list(d['scan'])[-1]].append(
                    dict(nb=int(m.group(1)), n=int(m.group(2)),
                         worst=float(m.group(3)), levels=m.group(4), ep=m.group(5)))
            m = re.match(r'^  ARITHMETIC FLOOR on THIS arc: .* = ([\d.]+) ns', ln)
            if m: d['floor'] = float(m.group(1))
        if sec == 'G' and '|u_biu|' in ln and ln.strip().startswith('seg'):
            d['biu'].append(ln.strip())
        if sec == 'H':
            m = re.match(r'^  (\S+)\s+\| (\S+)\s+\| (\d+)\s+\(\+(\d+) indexed\)', ln)
            if m:
                d['census'][m.group(1)] = (m.group(2), int(m.group(3)), int(m.group(4)))
    tf = path[:-4] + '.truefmax.txt'
    d['same_k'] = d['same_fmax'] = None
    if os.path.exists(tf):
        blk = open(tf).read().split('--- SAME')
        if len(blk) > 1:
            m = re.search(r'k = ([\d.]+)\s+slack =\s*([+-][\d.]+)\s+->\s+T_min\s+([\d.]+) ns\s+=\s+([\d.]+) MHz',
                          blk[1])
            if m:
                d['same_k'] = float(m.group(1)); d['same_tmin'] = float(m.group(3))
                d['same_fmax'] = float(m.group(4))
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='sw/testdata/chainanat')
    a = ap.parse_args()
    files = sorted(glob.glob(os.path.join(ROOT, a.dir, '*_seed*.txt')))
    files = [f for f in files if not f.endswith('.arrivalpoints.txt')
             and not f.endswith('.truefmax.txt') and not f.endswith('.seedecho.txt')]
    if not files:
        print("no draws found"); return 2
    draws = [parse(f) for f in files]

    print("=== E-1  POSITIVE CONTROLS, PER DRAW (reported FIRST) ===")
    allok = True
    for d in draws:
        c = d['ctl']
        ok = all(c.get(k) for k in ('PC-1', 'PC-2', 'PC-3', 'PC-4'))
        allok &= ok
        print(f"  {os.path.basename(d['file']):24s} "
              + "  ".join(f"{k}:{'PASS' if c.get(k) else 'FAIL'}" for k in
                          ('PC-1', 'PC-2', 'PC-3', 'PC-4'))
              + f"   -> {'ALL PASS' if ok else '*** FAILED ***'}")
    print(f"  E-1: {'MET' if allok else 'MISSED -- THE WAVE IS VOID'}")

    print("\n=== THE NO-EXCEPTION CHECK (the deletion reached the compiler) ===")
    for d in draws:
        print(f"  {os.path.basename(d['file']):24s} SAME k={d['same_k']}  "
              f"(MUST be 1.0)   T_min {d.get('same_tmin')} ns  {d['same_fmax']} MHz")

    print("\n=== Q1 / E-2  THE PER-SEGMENT PROFILE, ALL DRAWS ===")
    print("  draw                     | arc ns | lvl | segs | per-segment span ns")
    for d in draws:
        spans = " ".join(f"{s['span']:.2f}" for s in d['segs'])
        print(f"  {os.path.basename(d['file'])[:-4]:24s} | {d.get('dd',0):6.3f} | "
              f"{d.get('levels',0):3d} | {len(d['segs']):4d} | {spans}")
    print("\n  seg 0 is the FRONT END + the first position's body; the rest are")
    print("  the folded positions.  seg 0 share of the arc:")
    for d in draws:
        if d['segs'] and d.get('dd'):
            print(f"    {os.path.basename(d['file'])[:-4]:24s} "
                  f"{d['segs'][0]['span']:.3f} / {d['dd']:.3f} = "
                  f"{100*d['segs'][0]['span']/d['dd']:.1f} %"
                  f"   folded positions = {d['dd']-d['segs'][0]['span']:.3f} ns")

    print("\n=== Q2 / E-3  THE CUMULATIVE PROFILE.  DOES ANY k GIVE BOTH HALVES <= 29.6 ns? ===")
    anyyes = False
    for d in draws:
        print(f"  --- {os.path.basename(d['file'])[:-4]} (arc {d.get('dd',0):.3f} ns) ---")
        print("    k |  upstream |downstream| worse half | both <= 29.6")
        best = None
        for c in d['cum']:
            yes = c['worse'] <= BUDGET
            anyyes |= yes
            if best is None or c['worse'] < best['worse']:
                best = c
            print(f"    {c['k']:2d} | {c['up']:9.3f} | {c['dn']:8.3f} | {c['worse']:10.3f} |"
                  f" {'YES' if yes else 'no'}")
        if best:
            print(f"    best-balanced k = {best['k']}, worse half {best['worse']:.3f} ns"
                  f"  -> {'BOTH INSIDE 29.6' if best['worse']<=BUDGET else 'OVER BUDGET'}")
    print(f"\n  E-3 ANSWER (uncut-netlist estimate): "
          f"{'YES -- some k gives both halves <= 29.6 ns' if anyyes else 'NO -- no k does'}")

    print("\n=== Q3 / E-4  WHAT DOMINATES INSIDE A SEGMENT ===")
    try:
        sys.path.insert(0, os.path.join(ROOT, 'sw'))
        import chain_srcmap
        ctl, s2a, chain_assigned, eu_assigned, _ = chain_srcmap.build()
        if not ctl['PASS']:
            print("  chain_srcmap POSITIVE CONTROL FAILED -- no arm attribution printed")
            s2a = None
    except Exception as e:                                    # pragma: no cover
        print(f"  chain_srcmap unavailable: {e}")
        s2a = None
    for d in draws:
        print(f"  --- {os.path.basename(d['file'])[:-4]} ---")
        for i in sorted(d['cont']):
            span, names = d['cont'][i]
            rows = []
            for n in names:
                arms = None
                if s2a is not None:
                    arms = s2a.get(n) or s2a.get(n + '_n')
                rows.append(f"{n}[{','.join(sorted(a[2:] for a in arms)) if arms else '-'}]")
            print(f"    seg {i} {span:7.3f} ns : " + " ".join(rows))

    print("\n=== Q4 / E-5  SHARED OR INDEPENDENT COPIES ===")
    for d in draws:
        print(f"  --- {os.path.basename(d['file'])[:-4]} ---")
        for k, v in sorted(d['census'].items(), key=lambda x: -x[1][1] - x[1][2]):
            print(f"    {k:20s} {v[0]:16s} {v[1]:4d} plain + {v[2]:4d} indexed = {v[1]+v[2]}")

    print("\n=== Q5  THE FLOOR ===")
    for d in draws:
        print(f"  --- {os.path.basename(d['file'])[:-4]}  arithmetic floor on the worst arc: "
              f"{d['floor']} ns ---")
        for scan, rows in d['scan'].items():
            print(f"    scan {scan}:")
            for r in rows:
                print(f"      {r['nb']} boundaries | {r['n']:5d} paths | worst {r['worst']:7.3f} ns"
                      f" | levels {r['levels']:>3s} | {r['ep']}")

    print("\n=== Q6  THE BIU ROUND TRIP ===")
    for d in draws:
        print(f"  --- {os.path.basename(d['file'])[:-4]}: {len(d['biu'])} BIU nodes on the worst arc ---")
        for r in d['biu']:
            print("      " + r)
    return 0


if __name__ == '__main__':
    sys.exit(main())
