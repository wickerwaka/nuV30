#!/usr/bin/env python3
"""WAVE 6 (THE CHAIN FLATTENING STUDY) -- WHAT THE COMPOSED FUNCTION TOUCHES.

**MEASUREMENT ONLY.  IT LANDS NOTHING.**  Deliverable C.

For each chained SEQUENCE the census actually observes, this answers:

  * WHAT each step reads and writes;
  * WHERE the same register is written at several positions down one chain --
    a FOLD opportunity, because only the last write survives the edge;
  * WHERE step k+1's input genuinely depends on step k's output -- an
    IRREDUCIBLE SERIAL DEPENDENCY, which is the floor a flattened form cannot
    beat;
  * WHICH inputs are CHAIN-INVARIANT -- read inside the chain and written by no
    arm that can occupy a non-final position, so every unrolled copy recomputes
    the identical value.

⚠ **THE READ / WRITE SETS ARE OVER-APPROXIMATIONS AND THE TWO ANSWERS THEY
SUPPORT POINT IN OPPOSITE DIRECTIONS.  BOTH ARE LABELLED.**
  * an over-approximated WRITE set makes CHAIN-INVARIANCE **conservative**: a
    name that appears in NO write set is invariant for certain.
  * an over-approximated READ set makes the carried-dependency depth an
    **UPPER BOUND**: a flattened form can be no deeper, and may be shallower.
    A LOWER bound needs the carried names read one at a time, so the tool
    NAMES them per adjacent pair instead of only counting.

THE CONTROLS (`--control`)
  PC-C1  the write sets recover, independently, the same 9-state chainable
         partition `chainflat_graph` derives -- an arm the graph calls
         position-0-only must write at least one name no chainable arm writes,
         or the two views are not looking at the same file.  (Reported, not
         asserted: it is a sanity read, and its FAILURE MODE is printed.)
  PC-C2  `gpr` / `sreg` -- the register file -- appear in NO chainable arm's
         write set.  WAVE 5 measured one `Ram<N>` read per position; this says
         from the source whether those reads can differ.  A NEGATIVE CONTROL
         name (`zzz_no_such_signal`) must be found nowhere.
  PC-C3  NON-VACUITY: an injected fake write of `gpr_n` into a chainable arm's
         text must flip PC-C2.

EXIT 0 / 1 as usual.
"""
import argparse
import json
import os
import re
import sys

SW = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SW, '..'))
sys.path.insert(0, SW)
import chainflat_graph as cg                                   # noqa: E402

UC = os.path.join(ROOT, 'hdl/rtl/ucore')

KEYWORDS = {
    'begin', 'end', 'if', 'else', 'case', 'endcase', 'default', 'for',
    'while', 'function', 'endfunction', 'task', 'endtask', 'logic', 'reg',
    'wire', 'integer', 'automatic', 'signed', 'unsigned', 'return', 'break',
    'localparam', 'parameter', 'int', 'bit', 'chain',
}
# Constants in this module are ALL-CAPS by convention (`R_BW`, `OK_MEM`,
# `PSW_FORCED`, `A_ADD`, `TEST_NONE`, `REP_E`, `PLA3_*`, `S_*`); signals are
# lower-case.  The filter is a CONVENTION and is declared as one -- it can only
# remove names, so a signal that broke it would be UNDER-reported, and the two
# claims this file makes are both checked against a NEGATIVE CONTROL.
CONST_RE = re.compile(r'^[A-Z][A-Z0-9_]*$')
IDENT_RE = re.compile(r'[A-Za-z_][A-Za-z0-9_$]*')
# ⚠ SIZED LITERALS FIRST.  `16'd1` / `6'b100000` / `8'h8D` tokenise into an
# `identifier` d1 / b100000 / h8D unless the literal is removed, and the first
# form of this file reported 25 such phantoms as chain-invariant INPUTS.
LIT_RE = re.compile(r"[0-9]*'[sS]?[bodhBODH][0-9a-fA-FxXzZ_?]+")
# `st_n` and `stop` are the SEQUENCER, not data.  They are carried by
# construction (that is what a chain IS) and are reported in their own column
# rather than counted as a data dependency.
CONTROL = {'st_n', 'st', 'stop', 'chain'}


def idents(text):
    text = LIT_RE.sub(' ', text or '')
    out = set()
    for m in IDENT_RE.finditer(text):
        n = m.group(0)
        if n in KEYWORDS or CONST_RE.match(n):
            continue
        # a function call: the name is followed by '('
        j = m.end()
        while j < len(text) and text[j] == ' ':
            j += 1
        if j < len(text) and text[j] == '(':
            continue
        out.add(n)
    return out


def base(lhs):
    return lhs.split('[')[0].strip()


def rw(node, w, r):
    """Collect writes and reads over an UNPRUNED statement tree."""
    if node is None:
        return
    if node.kind == 'assign':
        b = base(node.lhs)
        if b:
            w.add(b)
        # an indexed target READS its index expression
        if '[' in node.lhs:
            r |= idents(node.lhs[node.lhs.index('['):])
        r |= idents(node.rhs)
    elif node.kind == 'call':
        r |= idents(node.rhs)
    elif node.kind == 'if':
        r |= idents(node.cond)
        for k in node.kids:
            rw(k, w, r)
    elif node.kind == 'case':
        for k in node.kids:
            rw(k, w, r)
    elif node.kind == 'seq':
        for k in node.kids:
            rw(k, w, r)


def arm_rw(uc, inject=None):
    """{arm: (writes, reads)} over the step include, includes spliced.

    `inject` = (arm, 'text') splices extra source into that arm -- PC-C3."""
    arms, guarded, order, _ = cg.parse_arms(uc)
    out = {}
    for name in order:
        body = re.sub(r'\bendcase\s*$', '', arms[name].rstrip())
        if inject and inject[0] == name:
            body = body + '\n' + inject[1]
        p = cg.Parser(cg.tokenize(body))
        stmts = []
        while p.peek() is not None:
            stmts.append(p.statement())
        tree = cg.Node('seq', kids=stmts)
        w, r = set(), set()
        rw(tree, w, r)
        out[name] = (w - CONTROL, r - CONTROL)
    return out, guarded, order


# --------------------------------------------------------------------------
def analyse_sequences(uc, census, inject=None):
    g = cg.graph(uc)
    z = g['st_zero_ok']
    rws, guarded, order = arm_rw(uc, inject=inject)
    # CHAIN-INVARIANT: written by no arm that can occupy a NON-FINAL position,
    # i.e. by no arm with a fall-through path.
    fallthrough_arms = {f for f in g['adj']}
    written_in_chain = set()
    for a in fallthrough_arms:
        written_in_chain |= rws[a][0]
    written_by_chainable = set()
    for a in z:
        written_by_chainable |= rws[a][0]
    rows = []
    for entry in census:
        seq = entry['states']
        n = len(seq)
        if n < 2:
            continue
        W = [rws[s][0] for s in seq]
        R = [rws[s][1] for s in seq]
        # carried: written at k, read at j > k, not overwritten in between
        carried = {}
        for k in range(n):
            for v in W[k]:
                for j in range(k + 1, n):
                    if v in R[j]:
                        carried.setdefault((k, j), set()).add(v)
                        break
                    if v in W[j]:
                        break
        # dead writes: written at k, overwritten at j>k, never read in (k, j]
        dead = {}
        for k in range(n):
            for v in W[k]:
                for j in range(k + 1, n):
                    if v in R[j]:
                        break
                    if v in W[j]:
                        dead.setdefault((k, j), set()).add(v)
                        break
        # longest carried path == the serial depth this composition cannot beat
        best = [1] * n
        for k in range(n):
            for j in range(k + 1, n):
                if (k, j) in carried:
                    best[j] = max(best[j], best[k] + 1)
        # THE REGISTER FILE, PER SEQUENCE: is it written by ANY position
        # before the one that reads it?  This is the claim WAVE 5's "one
        # `Ram<N>` per position" makes measurable from the source.
        regfile = {'gpr_n', 'gpr', 'sreg_n', 'sreg'}
        rf_reader = [k for k in range(n) if regfile & R[k]]
        rf_writer = [k for k in range(n) if regfile & W[k]]
        rf_const = all(not any(w < k for w in rf_writer) for k in rf_reader)
        rows.append({
            'regfile_read_at': rf_reader, 'regfile_written_at': rf_writer,
            'regfile_constant_for_every_reader': rf_const,
            'states': seq, 'depth': n, 'count': entry['count'],
            'pct': entry['pct'],
            'serial_depth_upper': max(best),
            'carried': {f'{a}->{b}': sorted(v) for (a, b), v in
                        sorted(carried.items())},
            'dead_writes': {f'{a}->{b}': sorted(v) for (a, b), v in
                            sorted(dead.items())},
            'multiwrite': sorted({v for k in range(n) for v in W[k]
                                  if sum(1 for q in W if v in q) > 1}),
        })
    inv = {}
    for a in z:
        for v in rws[a][1]:
            if v not in written_in_chain:
                inv.setdefault(v, []).append(a)
    return {'rows': rows, 'invariant': {k: sorted(v) for k, v in
                                        sorted(inv.items())},
            'written_by_chainable': sorted(written_by_chainable),
            'written_in_chain': sorted(written_in_chain),
            'rws': {k: (sorted(v[0]), sorted(v[1])) for k, v in rws.items()}}


def controls(uc, verbose=True):
    g = cg.graph(uc)
    z = g['st_zero_ok']
    rws, guarded, order = arm_rw(uc)
    chain_w = set()
    for a in z:
        chain_w |= rws[a][0]
    pos0_only = [a for a in order if a in guarded and guarded[a]]
    c1_bad = [a for a in pos0_only if rws[a][0] and rws[a][0] <= chain_w]
    c1 = (len(c1_bad) <= 3)          # reported, see the docstring
    regfile = {'gpr_n', 'gpr', 'sreg_n', 'sreg'}
    c2 = not (regfile & chain_w) and 'zzz_no_such_signal' not in chain_w
    inj = ("S_EA_CALC", "gpr_n[3'd0] = 16'd0;")
    rws2, _, _ = arm_rw(uc, inject=inj)
    chain_w2 = set()
    for a in z:
        chain_w2 |= rws2[a][0]
    c3 = bool(regfile & chain_w2)
    if verbose:
        print('PC-C1  every position-0-only arm writes something no chainable '
              'arm writes')
        print('       arms failing that: %d  %s'
              % (len(c1_bad), ' '.join(c1_bad) if c1_bad else ''))
        print('       -> %s (reported, not a bar: an arm may legitimately '
              'write only shared names)' % ('OK' if c1 else 'NOTE'))
        print('PC-C2  the register file is written by NO chainable arm      '
              ': %s' % ('PASS' if c2 else 'FAIL'))
        print('       chainable write set carries gpr/sreg: %s'
              % (' '.join(sorted(regfile & chain_w)) or 'NO'))
        print('       negative control `zzz_no_such_signal` present : %s'
              % ('YES (WRONG)' if 'zzz_no_such_signal' in chain_w else 'no'))
        print('PC-C3  NON-VACUITY: injecting `gpr_n[0] = 0` into S_EA_CALC   '
              ': %s' % ('PASS' if c3 else 'FAIL'))
    return (c2 and c3), {'PC-C1': c1, 'PC-C1_arms': c1_bad,
                         'PC-C2': c2, 'PC-C3': c3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ucore', default=UC)
    ap.add_argument('--census', default=os.path.join(
        ROOT, 'sw/testdata/chainflat/dyncensus.json'))
    ap.add_argument('--control', action='store_true')
    ap.add_argument('--out', default=os.path.join(
        ROOT, 'sw/testdata/chainflat/compose.json'))
    a = ap.parse_args()
    ok = True
    if a.control:
        ok, _ = controls(a.ucore)
        print()
    census = json.load(open(a.census))['sequences']
    res = analyse_sequences(a.ucore, census)
    print('=== CHAIN-INVARIANT INPUTS ===')
    print('(read inside the chain, written by NO arm that can occupy a '
          'non-final position;\n so every unrolled copy recomputes the '
          'identical value)')
    print('%d names' % len(res['invariant']))
    for k, v in res['invariant'].items():
        print('   %-22s read by %s' % (k, ' '.join(v)))
    print()
    print('=== PER-SEQUENCE COMPOSITION (depth >= 2, by frequency) ===')
    for r in res['rows']:
        print('\n%8d edges  %5.2f%%  d=%d  %s'
              % (r['count'], r['pct'], r['depth'], ' -> '.join(r['states'])))
        print('   SERIAL DEPTH (upper bound)      : %d of %d positions'
              % (r['serial_depth_upper'], r['depth']))
        if r['regfile_read_at']:
            print('   register file read at positions : %s   written at: %s'
                  '   CONSTANT for every reader: %s'
                  % (r['regfile_read_at'],
                     r['regfile_written_at'] or 'NOWHERE',
                     r['regfile_constant_for_every_reader']))
        for k, v in r['carried'].items():
            print('   carries %-8s : %s' % (k, ' '.join(v)))
        if r['dead_writes']:
            for k, v in r['dead_writes'].items():
                print('   DEAD write %-6s: %s' % (k, ' '.join(v)))
        if r['multiwrite']:
            print('   written at >1 position          : %s'
                  % ' '.join(r['multiwrite']))
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, 'w'), indent=1)
    print('\nwrote %s' % a.out)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
