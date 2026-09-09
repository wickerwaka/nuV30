#!/usr/bin/env python3
"""WAVE 8 (THE FRONT END) -- THE REPORTER.  MEASUREMENT ONLY, NO GATE.

Reads the `.txt` / `.arrivalpoints.txt` / `.population.txt` written by
`sw/sta_frontend_anatomy.tcl` and censuses them against the SOURCE-DERIVED
stage map in `sw/frontend_srcmap.py`.

It reports, in this order:
  §1  the source-map controls (H-1: reported FIRST) and each draw's STA
      controls, quoted from the draw's own file;
  §2  the worst `ce -> ce` arc per draw, segmented;
  §3  THE POPULATION census by STAGE -- strict and carry-forward -- with the
      draw-property / tree-property split stated (H-3);
  §4  the BIU round trip over the population;
  §5  the array-read (`gpr` / `sreg`) cost over the population;
  §6  the ranked candidate table's raw inputs, with a spread per stage.
"""
import argparse, collections, os, re, statistics, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'sw'))
import frontend_srcmap as FS   # noqa: E402


def read_population(path):
    """-> [ {slack, delay, levels, nbnd, frm, to, pts:[(cum,inc,ty,name)]} ]"""
    out = []
    cur = None
    for line in open(path):
        if line.startswith('#'):
            continue
        f = line.split(None, 6)
        if not f:
            continue
        if f[0] == 'P':
            cur = {'idx': int(f[1]), 'slack': float(f[2]), 'delay': float(f[3]),
                   'levels': f[4], 'nbnd': int(f[5]),
                   'frm': f[6].split()[0] if len(f) > 6 else '',
                   'to': f[6].split()[1] if len(f) > 6 and len(f[6].split()) > 1 else '',
                   'pts': []}
            out.append(cur)
        elif f[0] == 'N' and cur is not None:
            cur['pts'].append((float(f[2]), float(f[3]), f[4], f[5].strip()))
    return out


def draw_controls(txt):
    """Pull each control's verdict line out of a draw's own .txt."""
    got = {}
    for m in re.finditer(r'(PC-\d) (PASS|FAILED)', txt):
        got.setdefault(m.group(1), m.group(2))
    for m in re.finditer(r'\*\*\* (PC-\d) FAILED \*\*\*', txt):
        got[m.group(1)] = 'FAILED'
    ok = 'CONTROLS: ALL PASS' in txt
    return got, ok


def census(paths, sig2sec, chain, carry):
    """-> (ns by stage, points by stage, per-path presence)"""
    ns = collections.Counter()
    npts = collections.Counter()
    present = collections.Counter()
    per_path = collections.defaultdict(list)
    for p in paths:
        st = [FS.classify(n[3], sig2sec, chain) for n in p['pts']]
        if carry:
            st = FS.carry_forward(st)
        seen = set()
        acc = collections.Counter()
        for (cum, inc, ty, name), k in zip(p['pts'], st):
            ns[k] += inc
            npts[k] += 1
            acc[k] += inc
            seen.add(k)
        for k in seen:
            present[k] += 1
        for k, v in acc.items():
            per_path[k].append(v)
    return ns, npts, present, per_path


def biu_span(p):
    """(nnodes, span ns, enter ns, leave ns) of the BIU round trip on a path."""
    hits = [(cum, inc, name) for cum, inc, ty, name in p['pts']
            if '|u_biu|' in FS.norm(name)]
    if not hits:
        return 0, 0.0, None, None
    a = hits[0][0] - hits[0][1]
    b = hits[-1][0]
    return len(hits), b - a, a, b


def array_span(p):
    hits = [(cum, inc, name) for cum, inc, ty, name in p['pts']
            if FS.RAM_RE.match(FS.basename2(name)) and '|u_eu|' in FS.norm(name)]
    if not hits:
        return 0, 0.0
    return len(hits), sum(h[1] for h in hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dir', default='sw/testdata/frontend/anat')
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    D = os.path.join(ROOT, a.dir)
    buf = []

    def P(s=''):
        print(s)
        buf.append(s)

    P("=" * 76)
    P("WAVE 8 -- THE FRONT-END ANATOMY.  MEASUREMENT ONLY; NOT A GATE.")
    P("=" * 76)
    P("")
    P("### §1  THE POSITIVE CONTROLS, REPORTED FIRST (H-1)")
    P("")
    ok_src = FS.controls()
    if not ok_src:
        P("REFUSING: source-map controls failed.")
        return 3
    sig2sec, chain = FS.build_stagemap(None)
    markers, deriv = FS.derive_markers(None)
    P("")
    P(f"  MARKER SET (source-derived): {' '.join(markers)}")

    draws = sorted(f[:-4] for f in os.listdir(D) if f.endswith('.txt') and
                   not f.endswith('.arrivalpoints.txt') and
                   not f.endswith('.population.txt') and
                   not f.endswith('.truefmax.txt') and
                   not f.endswith('.seedecho.txt') and f != 'report.txt')
    P("")
    P("  per-draw STA controls (quoted from each draw's own file):")
    P("    draw               | PC-1 | PC-2 | PC-3 | PC-4 | PC-5 | verdict")
    all_ok = True
    for d in draws:
        txt = open(os.path.join(D, d + '.txt')).read()
        got, ok = draw_controls(txt)
        all_ok &= ok
        P(f"    {d:18s} | " + " | ".join(
            f"{got.get(f'PC-{i}', '--')[:4]:4s}" for i in range(1, 6)) +
          f" | {'ALL PASS' if ok else '*** FAILED ***'}")
    P("")
    P(f"  === STA CONTROLS: {'ALL PASS on every draw' if all_ok else '*** A DRAW FAILED ***'} ===")
    if not all_ok:
        P("  NOTHING BELOW MAY BE QUOTED.")
        return 4

    # ---- §2 the worst arc, per draw
    P("")
    P("### §2  THE WORST `ce -> ce` ARC, PER DRAW")
    P("")
    P("  draw               |   arc ns | levels | bnds | k/Tmin(SAME) | seed | endpoints")
    arcs = {}
    for d in draws:
        txt = open(os.path.join(D, d + '.txt')).read()
        m = re.search(r'slack\s+([-+][\d.]+)\s+logic levels (\d+)\s+data delay ([\d.]+)', txt)
        b = re.search(r'boundaries found: (\d+)', txt)
        frm = re.search(r'^  from : (.*)$', txt, re.M)
        to = re.search(r'^  to   : (.*)$', txt, re.M)
        tf = os.path.join(D, d + '.truefmax.txt')
        k = '--'
        if os.path.exists(tf):
            # the `SAME` class's own k AND T_min, read out of the block that
            # names it -- not the first `k =` in the file, which is DEFAULT's.
            t = open(tf).read()
            km = re.search(r'--- SAME.*?k = ([\d.]+).*?T_min\s+([\d.]+)', t, re.S)
            if km:
                k = km.group(1) + '/' + km.group(2)
        se = ''
        sf = os.path.join(D, d + '.seedecho.txt')
        if os.path.exists(sf):
            sm = re.search(r':\s*(\d+)', open(sf).read())
            se = sm.group(1) if sm else ''
        arc = float(m.group(3)) if m else 0.0
        arcs[d] = arc
        e = ''
        if frm and to:
            e = f"{FS.basename2(frm.group(1))} -> {FS.basename2(to.group(1))}"
        P(f"  {d:18s} | {arc:8.3f} | {m.group(2) if m else '--':6s} | "
          f"{b.group(1) if b else '--':4s} | {k:12s} | {se:4s} | {e}")
    if arcs:
        v = list(arcs.values())
        P(f"  mean {statistics.mean(v):.3f}   min {min(v):.3f}   max {max(v):.3f}   "
          f"spread {max(v)-min(v):.3f}")

    # ---- §3 the population census
    for carry in (False, True):
        lab = 'CARRY-FORWARD (a READING, see frontend_srcmap.py)' if carry else 'STRICT'
        P("")
        P(f"### §3{'b' if carry else 'a'}  THE POPULATION CENSUS BY STAGE -- {lab}")
        P("")
        tot_rows = []
        for d in draws:
            pf = os.path.join(D, d + '.population.txt')
            if not os.path.exists(pf):
                continue
            paths = read_population(pf)
            ns, npts, present, per_path = census(paths, sig2sec, chain, carry)
            arcsum = sum(p['delay'] for p in paths)
            P(f"  --- {d}: {len(paths)} endpoint-diverse paths, "
              f"total arc {arcsum:.1f} ns, mean {arcsum/max(1,len(paths)):.3f} ns")
            P(f"      stage                                      |  mean ns/path | "
              f"% of arc | on n paths | mean ns when present")
            for k, v in ns.most_common():
                mp = statistics.mean(per_path[k]) if per_path[k] else 0.0
                P(f"      {k[:42]:42s} | {v/max(1,len(paths)):13.3f} | "
                  f"{v/max(1e-9,arcsum)*100:7.1f} % | {present[k]:10d} | {mp:9.3f}")
                tot_rows.append((d, k, v / max(1, len(paths)), v / max(1e-9, arcsum) * 100,
                                 present[k] / max(1, len(paths)), mp))
            P("")
        # cross-draw stability
        P(f"  --- CROSS-DRAW (H-3: what is a TREE property and what is a DRAW property)")
        agg = collections.defaultdict(list)
        for d, k, mns, pct, rate, mp in tot_rows:
            agg[k].append((mns, pct, rate))
        P(f"      stage                                      | mean ns/path (min..max) | "
          f"% of arc (min..max) | presence")
        for k in sorted(agg, key=lambda x: -statistics.mean([r[0] for r in agg[x]])):
            r = agg[k]
            m1 = [x[0] for x in r]
            m2 = [x[1] for x in r]
            m3 = [x[2] for x in r]
            P(f"      {k[:42]:42s} | {statistics.mean(m1):7.3f} "
              f"({min(m1):6.3f}..{max(m1):6.3f}) | {statistics.mean(m2):6.1f} % "
              f"({min(m2):5.1f}..{max(m2):5.1f}) | {statistics.mean(m3)*100:5.1f} %")

    # ---- §4 the BIU round trip
    P("")
    P("### §4  THE BIU ROUND TRIP (`q_cnt -> q_ripe_lead_n`) OVER THE POPULATION")
    P("")
    P("  draw               | on worst arc | paths carrying it | mean span when present | "
      "max span | mean over ALL paths")
    for d in draws:
        pf = os.path.join(D, d + '.population.txt')
        if not os.path.exists(pf):
            continue
        paths = read_population(pf)
        spans = [biu_span(p)[1] for p in paths]
        pres = [s for s in spans if s > 0]
        txt = open(os.path.join(D, d + '.txt')).read()
        wm = re.search(r'BIU nodes on the worst ce->ce arc: (\d+)', txt)
        ws = re.search(r'SPAN: ([\d.]+) ns', txt)
        P(f"  {d:18s} | {(ws.group(1)+' ns') if ws else 'ABSENT':12s} | "
          f"{len(pres):4d} / {len(paths):4d}       | "
          f"{statistics.mean(pres) if pres else 0.0:22.3f} | "
          f"{max(spans) if spans else 0.0:8.3f} | "
          f"{statistics.mean(spans) if spans else 0.0:8.3f}")

    # ---- §5 the array read
    P("")
    P("### §5  THE ARRAY READ (`gpr` / `sreg` / `tmps` mux) OVER THE POPULATION")
    P("")
    P("  draw               | paths carrying it | mean ns when present | max | mean over ALL")
    for d in draws:
        pf = os.path.join(D, d + '.population.txt')
        if not os.path.exists(pf):
            continue
        paths = read_population(pf)
        vals = [array_span(p)[1] for p in paths]
        pres = [v for v in vals if v > 0]
        P(f"  {d:18s} | {len(pres):4d} / {len(paths):4d}       | "
          f"{statistics.mean(pres) if pres else 0.0:20.3f} | "
          f"{max(vals) if vals else 0.0:6.3f} | {statistics.mean(vals) if vals else 0.0:6.3f}")

    # ---- §6 the top of the binding population
    P("")
    P("### §6  THE BINDING POPULATION -- the 20 worst endpoint-diverse paths")
    P("")
    for d in draws:
        pf = os.path.join(D, d + '.population.txt')
        if not os.path.exists(pf):
            continue
        paths = sorted(read_population(pf), key=lambda p: p['slack'])[:20]
        P(f"  --- {d}")
        for p in paths[:20]:
            st = FS.carry_forward([FS.classify(n[3], sig2sec, chain) for n in p['pts']])
            acc = collections.Counter()
            for (cum, inc, ty, name), k in zip(p['pts'], st):
                acc[k] += inc
            top = ' '.join(f"{k[:18]}={v:.1f}" for k, v in acc.most_common(4))
            P(f"      {p['delay']:7.3f} ns  bnd {p['nbnd']}  "
              f"{FS.basename2(p['frm'])[:22]:22s} -> {FS.basename2(p['to'])[:18]:18s} | {top}")
        P("")

    if a.out:
        open(os.path.join(ROOT, a.out), 'w').write('\n'.join(buf) + '\n')
        print(f"\n  written to {a.out}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
