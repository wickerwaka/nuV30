#!/usr/bin/env python3
"""WAVE 6 (THE CHAIN FLATTENING STUDY) -- THE DYNAMIC SEQUENCE CENSUS.

**MEASUREMENT ONLY.  IT LANDS NOTHING.**  Deliverable A(ii) and B.

`v30u_eu.sv`'s `CHAIN_PROBE` block records, per CE edge, the ORDERED tuple of
states occupying chain positions 0..N-1, de-duplicated and counted.  This
driver builds the probe binaries **into a scratch objdir**, runs them over two
populations with nothing in common, merges the counts, and compares the result
against the STATIC graph `sw/chainflat_graph.py` derives from the source.

⚠ **THE PROBE BINARIES ARE NOT THE STANDING BINARIES AND MUST NEVER BE.**
`-DCHAIN_PROBE` is not in `check_core.recipe()` / `chain_lfsr_gate.recipe()`, so
building one into `hdl/tb/obj_dir_ucore/` would promote a receipt naming a
recipe the bytes do not come from.  Everything here builds under
`~/.cache/ucsimt-tmp/chainflat/` and the artifact layer is never asked to
promote it.

POPULATIONS
  golden  `tests/v30/v0.1` through `sw/check_core.py`, 347 forms -- KNOWN bytes
  lfsr    `hdl/tb/tb_chain_lfsr.sv`, 4 seeds -- ARBITRARY bytes, an environment
          with nothing in common with the golden suite

THE CONTROLS
  PC-B1  the probe's own `(position, state)` census reproduces
         `ucore_provenance.md` sec.51.2: exactly the 9 `st_zero_ok` states at
         position >= 1, and NOTHING else.
  PC-B2  every observed sequence is a walk of the STATIC adjacency, edge for
         edge -- this is bar **F-1**.
  PC-B3  NON-VACUITY: the same comparison against a DELIBERATELY WRONG static
         graph (one edge removed) must FAIL.  A comparison that cannot fail is
         not evidence.

EXIT  0 all controls pass / 1 a control FAILED / 2 could not run.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SW = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SW, '..'))
sys.path.insert(0, SW)
import chainflat_graph as cg                                   # noqa: E402

SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/chainflat')
UC = os.path.join(ROOT, 'hdl/rtl/ucore')
TB = os.path.join(ROOT, 'hdl/tb')

RTL = ['v30u_ss_pkg.sv', 'v30_core.sv', 'v30u_biu.sv', 'v30u_ucrom.sv',
       'v30u_eu.sv']

WARN = ['-Wall', '-Wno-UNUSEDSIGNAL', '-Wno-VARHIDDEN', '-Wno-TIMESCALEMOD',
        '-Wno-WIDTHEXPAND', '-Wno-BLKSEQ', '-Wno-DECLFILENAME',
        '-Wno-UNUSEDPARAM']

LFSR_SEEDS = ['1', '2', '3', '4']
LFSR_CLOCKS = 400000


def state_names():
    """{code: S_NAME} out of `v30u_eu.sv`'s localparam block."""
    txt = cg.strip_comments(open(os.path.join(UC, 'v30u_eu.sv')).read())
    m = re.search(r'localparam\s+bit\s*\[5:0\]\s*(.*?);', txt, re.S)
    out = {}
    for nm, val in re.findall(r'(S_[A-Z0-9_]+)\s*=\s*6\'d(\d+)', m.group(1)):
        out[int(val)] = nm
    return out


def build(kind, force=False):
    """kind in {'core','lfsr'} -> path to the probe binary."""
    os.makedirs(SCRATCH, exist_ok=True)
    obj = os.path.join(SCRATCH, 'obj_' + kind)
    binn = {'core': 'Vtb_v30_core', 'lfsr': 'Vtb_chain_lfsr'}[kind]
    out = os.path.join(obj, binn)
    probe = os.path.join(SCRATCH, f'probe_{kind}.txt')
    if os.path.exists(out) and not force:
        return out
    top = {'core': 'tb_v30_core', 'lfsr': 'tb_chain_lfsr'}[kind]
    if kind == 'core':
        # THE SOURCE LIST AND ITS ORDER COME FROM `check_core.core_paths`, not
        # from a second copy here: a package-first ordering that drifts is
        # exactly how a probe stops being the thing it claims to probe.
        import check_core as cc
        srcs = [str(p) for p in cc.core_paths('ucore')]
        # `-Wno-UNOPTFLAT`: the probe's own census arrays are read and written
        # inside the combinational chain block, which Verilator reports as a
        # circular comb path.  It is a SIM-ONLY census under `CHAIN_PROBE` and
        # the pre-existing `cp_seen` array has the same shape; the STANDING
        # build does not define `CHAIN_PROBE` and does not carry the waiver.
        extra = ['-DV30_BACKDOOR', '-DV30_PFX_ASSERT', '--assert',
                 '-DV30_UCORE', '-Wno-UNOPTFLAT']
    else:
        srcs = [os.path.join(TB, top + '.sv')] + [os.path.join(UC, f)
                                                  for f in RTL]
        extra = ['-Wno-MULTIDRIVEN', '-Wno-UNOPTFLAT', '-Wno-CASEINCOMPLETE']
    cmd = (['verilator', '--binary', '--timing', '-DV30_MUXED_AD',
            f'-DCHAIN_PROBE="{probe}"'] + extra + WARN +
           ['--top-module', top, '-I' + UC, '-Mdir', obj] + srcs)
    print('[build] ' + ' '.join(cmd[:6]) + ' ... ' + top, flush=True)
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0 or not os.path.exists(out):
        sys.stderr.write(p.stdout[-4000:] + p.stderr[-4000:])
        print('chainflat_probe: BUILD FAILED for ' + top, file=sys.stderr)
        sys.exit(2)
    return out


SEQ_RE = re.compile(r'^SEQCOUNT\s+(\d+)((?:\s+\d+)*)\s*$')
POS_RE = re.compile(r'^POS\s+(\d+)\s+ST\s+(\d+)\s*$')
TOT_RE = re.compile(r'^SEQ_EDGES\s+(\d+)\s+SEQ_DISTINCT\s+(\d+)\s*$')


def read_probe(path):
    seqs, pos, edges, overflow = {}, {}, 0, 0
    if not os.path.exists(path):
        return {'seqs': seqs, 'pos': pos, 'edges': 0, 'overflow': 0}
    for line in open(path):
        m = SEQ_RE.match(line)
        if m:
            key = tuple(int(x) for x in m.group(2).split())
            seqs[key] = seqs.get(key, 0) + int(m.group(1))
            continue
        m = POS_RE.match(line)
        if m:
            pos.setdefault(int(m.group(1)), set()).add(int(m.group(2)))
            continue
        m = TOT_RE.match(line)
        if m:
            edges += int(m.group(1))
            continue
        if line.startswith('SEQ_TABLE_OVERFLOW'):
            overflow += 1
    return {'seqs': seqs, 'pos': pos, 'edges': edges, 'overflow': overflow}


def merge(a, b):
    s = dict(a['seqs'])
    for k, v in b['seqs'].items():
        s[k] = s.get(k, 0) + v
    p = {k: set(v) for k, v in a['pos'].items()}
    for k, v in b['pos'].items():
        p.setdefault(k, set()).update(v)
    return {'seqs': s, 'pos': p, 'edges': a['edges'] + b['edges'],
            'overflow': a['overflow'] + b['overflow']}


# --------------------------------------------------------------------------
def run_lfsr(binp, seeds, clocks):
    probe = os.path.join(SCRATCH, 'probe_lfsr.txt')
    acc = {'seqs': {}, 'pos': {}, 'edges': 0, 'overflow': 0}
    for s in seeds:
        if os.path.exists(probe):
            os.remove(probe)
        p = subprocess.run([binp, '+chaindepth', f'+seed={s}',
                            f'+clocks={clocks}'], cwd=ROOT,
                           capture_output=True, text=True, timeout=7200)
        ok = 'RESULT OK' in (p.stdout + p.stderr)
        depth = max([int(m.group(1)) for m in
                     re.finditer(r'CHAIN_DEPTH_MAX\s+(\d+)', p.stdout)] or [0])
        print(f'[lfsr] seed {s}: RESULT OK={ok} depth={depth}', flush=True)
        if not ok:
            sys.stderr.write((p.stdout + p.stderr)[-3000:])
            print('chainflat_probe: LFSR seed %s did not finish' % s,
                  file=sys.stderr)
            sys.exit(2)
        acc = merge(acc, read_probe(probe))
    return acc


def run_golden(binp, argv):
    """Drive `check_core` with the PROBE binary by pointing its `core_objdir`
    at the scratch tree.  `build()` is stubbed out so the artifact layer is
    never asked to promote the probe build."""
    probe = os.path.join(SCRATCH, 'probe_core.txt')
    if os.path.exists(probe):
        os.remove(probe)
    obj = os.path.dirname(binp)
    code = (
        'import sys, pathlib\n'
        f'sys.path.insert(0, {SW!r})\n'
        'import check_core as cc\n'
        f'cc.core_objdir = lambda core: pathlib.Path({obj!r})\n'
        'cc.build = lambda *a, **k: None\n'
        f'sys.argv = ["check_core"] + {argv!r}\n'
        'sys.exit(cc.main())\n')
    p = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                       capture_output=True, text=True, timeout=14400)
    tail = (p.stdout + p.stderr)[-1500:]
    print('[golden] rc=%d\n%s' % (p.returncode, tail), flush=True)
    return read_probe(probe), p.returncode, p.stdout


# --------------------------------------------------------------------------
# THE COMPARISON -- bar F-1
# --------------------------------------------------------------------------
def compare(dyn, adj, names, drop_edge=None):
    """Every observed sequence must be a walk of the static adjacency.
    -> (ok, findings)"""
    bad = []
    a = {k: {t for t, _ in v} for k, v in adj.items()}
    if drop_edge:
        f, t = drop_edge
        a.get(f, set()).discard(t)
    for seq, n in sorted(dyn['seqs'].items(), key=lambda x: -x[1]):
        for i in range(len(seq) - 1):
            f = names.get(seq[i], f'?{seq[i]}')
            t = names.get(seq[i + 1], f'?{seq[i + 1]}')
            if t not in a.get(f, set()):
                bad.append((tuple(names.get(s, f'?{s}') for s in seq), n,
                            f'{f} -> {t}'))
                break
    return (not bad), bad


def controls(dyn, uc, names, verbose=True):
    g = cg.graph(uc)
    adj = g['adj']
    z = g['st_zero_ok']
    # PC-B1: the (position, state) census
    seen_ge1 = set()
    for p, sts in dyn['pos'].items():
        if p >= 1:
            seen_ge1 |= {names.get(s, f'?{s}') for s in sts}
    b1 = seen_ge1 <= z and seen_ge1 == z
    # PC-B2 / F-1
    b2, bad = compare(dyn, adj, names)
    # PC-B3 non-vacuity: remove ONE edge that the census actually walks
    walked = set()
    for seq in dyn['seqs']:
        for i in range(len(seq) - 1):
            walked.add((names.get(seq[i]), names.get(seq[i + 1])))
    victim = sorted(walked)[0] if walked else None
    b3ok, b3bad = (compare(dyn, adj, names, drop_edge=victim)
                   if victim else (True, []))
    b3 = (not b3ok)
    # the static side: which states does the static graph put at position >= 1
    static_ge1 = set()
    for i, s in g['occ'].items():
        if i >= 1:
            static_ge1 |= s
    # depths
    dyn_depth = max((len(k) for k in dyn['seqs']), default=0)
    static_depth = max(len(s) for s, _ in g['seqs'])
    b4 = (dyn_depth <= static_depth)
    if verbose:
        print()
        print('=== THE DYNAMIC CENSUS ===')
        print('CE edges censused        : %d' % dyn['edges'])
        print('distinct sequences       : %d' % len(dyn['seqs']))
        print('table overflows          : %d  (MUST be 0)' % dyn['overflow'])
        print('max observed depth       : %d' % dyn_depth)
        print('max STATIC depth         : %d' % static_depth)
        print()
        print('PC-B1  states at position >= 1 == st_zero_ok        : %s'
              % ('PASS' if b1 else 'FAIL'))
        print('       observed: %s' % ' '.join(sorted(seen_ge1)))
        print('       static  : %s' % ' '.join(sorted(static_ge1)))
        print('       st_zero_ok: %s' % ' '.join(sorted(z)))
        print('PC-B2  every observed sequence walks the static graph  '
              ': %s     <-- F-1' % ('PASS' if b2 else 'FAIL'))
        for s, n, e in bad[:10]:
            print('       OFF-GRAPH  %s  x%d  at %s' % (' -> '.join(s), n, e))
        print('PC-B3  NON-VACUITY: dropping the static edge %s'
              % (' -> '.join(victim) if victim else '<none>'))
        print('       makes PC-B2 FAIL                                : %s'
              % ('PASS' if b3 else 'FAIL'))
        print('PC-B4  observed depth <= static depth                  : %s'
              % ('PASS' if b4 else 'FAIL'))
    return all([b1, b2, b3, b4]), {
        'PC-B1': b1, 'PC-B2': b2, 'PC-B3': b3, 'PC-B4': b4,
        'observed_pos_ge1': sorted(seen_ge1), 'static_pos_ge1':
        sorted(static_ge1), 'st_zero_ok': sorted(z),
        'off_graph': [[list(s), n, e] for s, n, e in bad],
        'dyn_depth': dyn_depth, 'static_depth': static_depth}


def census_report(dyn, names):
    tot = sum(dyn['seqs'].values())
    rows = []
    for seq, n in sorted(dyn['seqs'].items(), key=lambda x: (-x[1], x[0])):
        rows.append({'states': [names.get(s, f'?{s}') for s in seq],
                     'codes': list(seq), 'depth': len(seq), 'count': n,
                     'pct': 100.0 * n / tot if tot else 0.0})
    return rows, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', action='store_true')
    ap.add_argument('--rebuild', action='store_true')
    ap.add_argument('--lfsr', action='store_true')
    ap.add_argument('--golden', action='store_true')
    ap.add_argument('--clocks', type=int, default=LFSR_CLOCKS)
    ap.add_argument('--seeds', default=','.join(LFSR_SEEDS))
    ap.add_argument('--golden-args', default='--core ucore --opcodes all '
                                             '--cases 0')
    ap.add_argument('--out', default=os.path.join(
        ROOT, 'sw/testdata/chainflat/dyncensus.json'))
    a = ap.parse_args()
    os.makedirs(SCRATCH, exist_ok=True)
    names = state_names()

    if a.build or a.rebuild:
        build('lfsr', force=a.rebuild)
        build('core', force=a.rebuild)
        if not (a.lfsr or a.golden):
            return 0

    acc = {'seqs': {}, 'pos': {}, 'edges': 0, 'overflow': 0}
    legs = {}
    if a.lfsr:
        b = build('lfsr')
        r = run_lfsr(b, a.seeds.split(','), a.clocks)
        legs['lfsr'] = {'edges': r['edges'], 'distinct': len(r['seqs'])}
        acc = merge(acc, r)
    gold_rc = None
    if a.golden:
        b = build('core')
        r, gold_rc, gout = run_golden(b, a.golden_args.split())
        legs['golden'] = {'edges': r['edges'], 'distinct': len(r['seqs']),
                          'rc': gold_rc,
                          'tail': gout[-800:]}
        acc = merge(acc, r)

    ok, det = controls(acc, UC, names)
    rows, tot = census_report(acc, names)
    print()
    print('=== THE SEQUENCE CENSUS (deliverable B) ===')
    print('%8s %6s  %s' % ('count', 'pct', 'sequence'))
    for r in rows:
        print('%8d %5.2f%%  d=%d  %s' % (r['count'], r['pct'], r['depth'],
                                         ' -> '.join(r['states'])))
    byd = {}
    for r in rows:
        byd.setdefault(r['depth'], [0, 0])
        byd[r['depth']][0] += 1
        byd[r['depth']][1] += r['count']
    print()
    print('DEPTH   distinct   edges      pct')
    for d in sorted(byd):
        print('%5d %10d %8d  %6.2f%%' % (d, byd[d][0], byd[d][1],
                                         100.0 * byd[d][1] / tot))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({'legs': legs, 'controls': det, 'total_edges': tot,
               'sequences': rows}, open(a.out, 'w'), indent=1)
    print('\nwrote %s' % a.out)
    if gold_rc not in (None, 0):
        print('chainflat_probe: the golden leg did not exit 0 (rc=%s)'
              % gold_rc, file=sys.stderr)
        return 1
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
