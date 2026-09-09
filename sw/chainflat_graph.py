#!/usr/bin/env python3
"""WAVE 6 (THE CHAIN FLATTENING STUDY) -- THE STATIC CHAIN GRAPH.

**MEASUREMENT ONLY.  IT EDITS NOTHING AND LANDS NOTHING.**

Deliverable A(i).  For each of the 33 state arms of
`hdl/rtl/ucore/v30u_eu_step.svh` (and the files it `include`s), enumerate the
PATHS through the arm and answer, per path:

    * does it fall through WITHOUT `stop` -- i.e. does the next chain position
      execute inside the SAME clock edge?
    * under what SOURCE-LEVEL CONDITION?
    * and to WHICH state?

The union of the fall-through TARGETS is, by construction, the set of states
that can stand at chain position >= 1.  `v30u_eu.sv` states that set twice --
in `st_zero_ok()` and in the step file's prose header -- and this tool derives
it a THIRD time, from the control flow, without being told either.

=== WHAT THIS IS NOT ===
⚠ It is a PARSER, NOT AN ELABORATOR.  It performs exactly three symbolic
reductions and NO others, each of which is declared and printed:

  R1  `st_n`'s value is tracked along a path, so a guard whose text is
      `st_n != S_X` / `st_n == S_X` (or `st != S_X`) is DECIDED rather than
      branched on.  This is what makes `S_MODRM`'s trailing
      `if (st_n != S_BIND) stop = 1'b1;` readable.
  R2  a condition TEXT already assumed on the path is not branched on again,
      so `S_PRERD`'s `st_n = ld_grpd_n ? ... ; if (ld_grpd_n) stop` yields 2
      feasible paths and not 4.
  R4  `chain == 4'd0` is decided TRUE -- see CHAIN0_RE below.
  R5  `stop` / `!stop` as a guard is decided from the path's tracked `stop`.
  R3  a statement whose subtree assigns neither `st_n` nor `stop` is collapsed
      to a no-op.  This is EXACT for the question asked and is what keeps
      `S_ROW`'s 282-line datapath include from exploding the enumeration.

Everything else is enumerated, including conditions the tool cannot read.  A
path whose feasibility it cannot decide is REPORTED, never dropped.

=== THE POSITIVE CONTROLS (`--control`) ===
PC-A1  the parser recovers 33 arms + `default`; 24 carry `if (chain == 4'd0)`
       and 9 do not; the 9 unguarded names are EXACTLY the 9 states
       `st_zero_ok()` returns true for, parsed separately out of `v30u_eu.sv`.
       (WAVE 5's `chain_srcmap` PC-0, re-run here so this tool carries its own.)
PC-A2  the set of FALL-THROUGH TARGETS the path enumeration produces equals
       that same 9.  Derived from control flow, compared against a function
       body: two independent derivations of one set.
PC-A3  NON-VACUITY.  With one named `stop = 1'b1;` deleted from a scratch copy
       of the step file, PC-A2 must FAIL and the target set must GROW.  A
       control that cannot fail proves nothing (`--nonvacuity`).

EXIT  0 controls pass / 1 a control FAILED / 2 could not run.
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
UC_DEFAULT = os.path.join(ROOT, 'hdl/rtl/ucore')
STEP = 'v30u_eu_step.svh'
EU = 'v30u_eu.sv'

ARM_RE = re.compile(r'^(S_[A-Z0-9_]+|default):')
GUARD_RE = re.compile(r"^S_[A-Z0-9_]+:\s*if\s*\(\s*chain\s*==\s*4'd0\s*\)")
INC_RE = re.compile(r'^\s*`include\s+"([^"]+)"')
STATE_RE = re.compile(r'^S_[A-Z0-9_]+$')


# --------------------------------------------------------------------------
# text
# --------------------------------------------------------------------------
def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return '\n'.join(l.split('//')[0] for l in text.split('\n'))


def expand(uc, fn, seen=None):
    """`include`-spliced, comment-stripped text.  Preprocessor lines are
    DROPPED (they are `ifndef SYNTHESIS` guards around trace-only writes; the
    tool prints how many it dropped so the drop is never silent)."""
    seen = (seen or set()) | {fn}
    out, dropped = [], 0
    for line in strip_comments(open(os.path.join(uc, fn)).read()).split('\n'):
        m = INC_RE.match(line)
        if m and os.path.exists(os.path.join(uc, m.group(1))):
            if m.group(1) in seen:
                continue
            sub, d = expand(uc, m.group(1), seen)
            out.append(sub)
            dropped += d
        elif line.strip().startswith('`'):
            dropped += 1
        else:
            out.append(line)
    return '\n'.join(out), dropped


# --------------------------------------------------------------------------
# tokeniser + recursive-descent parser over the SV subset this file uses
# --------------------------------------------------------------------------
TOK_RE = re.compile(r"""
      (?P<ws>\s+)
    | (?P<num>[0-9]+'[sSbBoOdDhH]?[0-9a-fA-FxXzZ_]+|[0-9][0-9_]*)
    | (?P<id>[A-Za-z_][A-Za-z0-9_$]*)
    | (?P<op><<=|>>=|<=|>=|==|!=|&&|\|\||<<|>>|\*\*|.)
""", re.X)


def tokenize(text):
    toks = []
    i = 0
    while i < len(text):
        m = TOK_RE.match(text, i)
        if not m:
            i += 1
            continue
        i = m.end()
        if m.lastgroup == 'ws':
            continue
        toks.append(m.group(0))
    return toks


class Node:
    __slots__ = ('kind', 'cond', 'kids', 'lhs', 'rhs', 'labels')

    def __init__(self, kind, cond=None, kids=None, lhs=None, rhs=None,
                 labels=None):
        self.kind = kind
        self.cond = cond
        self.kids = kids or []
        self.lhs = lhs
        self.rhs = rhs
        self.labels = labels


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self, k=0):
        j = self.i + k
        return self.t[j] if j < len(self.t) else None

    def take(self):
        v = self.peek()
        self.i += 1
        return v

    def expect(self, s):
        v = self.take()
        if v != s:
            raise SyntaxError(f'expected {s!r} got {v!r} at token {self.i}')
        return v

    def balanced(self, open_s='(', close_s=')'):
        """Consume a balanced group STARTING at the opener; return inner text."""
        self.expect(open_s)
        depth, out = 1, []
        while True:
            v = self.take()
            if v is None:
                raise SyntaxError('unbalanced')
            if v == open_s:
                depth += 1
            elif v == close_s:
                depth -= 1
                if depth == 0:
                    break
            out.append(v)
        return ' '.join(out)

    def statement(self):
        v = self.peek()
        if v is None:
            return Node('nop')
        if v == ';':
            self.take()
            return Node('nop')
        if v == 'begin':
            self.take()
            if self.peek() == ':':           # `begin : label`
                self.take()
                self.take()
            kids = []
            while self.peek() not in ('end', None):
                kids.append(self.statement())
            self.expect('end')
            return Node('seq', kids=kids)
        if v == 'if':
            self.take()
            cond = self.balanced()
            then = self.statement()
            els = None
            if self.peek() == 'else':
                self.take()
                els = self.statement()
            return Node('if', cond=cond, kids=[then, els])
        if v == 'case':
            self.take()
            self.balanced()                   # the selector: irrelevant here
            kids, labels = [], []
            while self.peek() not in ('endcase', None):
                lab = []
                while self.peek() not in (':', None):
                    lab.append(self.take())
                self.expect(':')
                labels.append(' '.join(lab))
                kids.append(self.statement())
            self.expect('endcase')
            return Node('case', kids=kids, labels=labels)
        # otherwise: an assignment or a call, terminated by `;`
        start = self.i
        depth = 0
        while self.peek() is not None:
            v = self.take()
            if v in '([{':
                depth += 1
            elif v in ')]}':
                depth -= 1
            elif v == ';' and depth == 0:
                break
        span = self.t[start:self.i - 1]
        # `lhs [ = | <= ] rhs`, the `=` at depth 0 and not part of ==/!=/<=/>=
        d, eq = 0, -1
        for k, tk in enumerate(span):
            if tk in '([{':
                d += 1
            elif tk in ')]}':
                d -= 1
            elif d == 0 and tk in ('=', '<='):
                eq = k
                break
        if eq < 0:
            return Node('call', rhs=' '.join(span))
        return Node('assign', lhs=' '.join(span[:eq]), rhs=' '.join(span[eq + 1:]))


# --------------------------------------------------------------------------
# R3: prune subtrees that touch neither `st_n` nor `stop`
# --------------------------------------------------------------------------
def touches(n):
    if n.kind == 'assign':
        base = n.lhs.split('[')[0].strip()
        return base in ('st_n', 'stop', 'st')
    if n.kind in ('seq', 'if', 'case'):
        return any(touches(k) for k in n.kids if k is not None)
    return False


def prune(n):
    if n is None:
        return None
    if not touches(n):
        return Node('nop')
    if n.kind in ('seq', 'if', 'case'):
        n.kids = [prune(k) if k is not None else None for k in n.kids]
    return n


# --------------------------------------------------------------------------
# path enumeration with R1 (st_n tracking) and R2 (repeated-condition reuse)
# --------------------------------------------------------------------------
CMP_RE = re.compile(r'^\s*(st_n|st)\s*(==|!=)\s*(S_[A-Z0-9_]+)\s*$')
# R4: `chain == 4'd0` is DECIDED TRUE.  The arm body is what the position that
# EXECUTES it does; the folded copy at a position >= 1 assigns nothing and is
# not a behaviour but an absence -- `st_zero_ok()` refuses to enter it and the
# `CHAIN OVERFLOW` $fatal fires if one ever did.  Reading the guard as a branch
# instead makes every arm its own fall-through target, which is an artefact of
# the reading and not of the design.
CHAIN0_RE = re.compile(r"^\s*chain\s*==\s*4'd0\s*$")
# R5: `stop` is a TRACKED variable, so a guard whose text is `stop` or `!stop`
# is DECIDED from the path's own `stop`, not branched on.  `S_ROW`'s
# `if (!stop) begin \`include "v30u_eu_row.svh" end` is the only site and it is
# the difference between reading the row include and inventing a path that
# skips it.
STOP_RE = re.compile(r'^\s*(!\s*)?stop\s*$')
TERNARY_STATE_RE = re.compile(
    r'^(?P<c>.+?)\?\s*(?P<a>S_[A-Z0-9_]+)\s*:\s*(?P<b>S_[A-Z0-9_]+)\s*$')


class Path:
    __slots__ = ('conds', 'st', 'stop', 'assume', 'undecided')

    def __init__(self, st):
        self.conds = []
        self.st = st            # symbolic st_n value: a state name or None
        self.stop = False
        self.assume = {}        # condition text -> bool
        self.undecided = 0

    def clone(self):
        p = Path(self.st)
        p.conds = list(self.conds)
        p.stop = self.stop
        p.assume = dict(self.assume)
        p.undecided = self.undecided
        return p


def norm(c):
    return ' '.join(c.split())


def decide(path, cond):
    """-> True / False / None, applying R1 then R2.  None = must branch."""
    c = norm(cond)
    if CHAIN0_RE.match(c):
        return True
    m = STOP_RE.match(c)
    if m:
        return (not path.stop) if m.group(1) else path.stop
    m = CMP_RE.match(c)
    if m and path.st is not None:
        eq = (path.st == m.group(3))
        return eq if m.group(2) == '==' else not eq
    if c in path.assume:
        return path.assume[c]
    neg = c[1:].strip() if c.startswith('!') else None
    if neg and neg in path.assume:
        return not path.assume[neg]
    return None


def walk(node, paths):
    """Advance every path in `paths` through `node`; return the new list."""
    if node is None or node.kind == 'nop' or node.kind == 'call':
        return paths
    if node.kind == 'seq':
        for k in node.kids:
            paths = walk(k, paths)
        return paths
    if node.kind == 'assign':
        base = node.lhs.split('[')[0].strip()
        out = []
        for p in paths:
            if base == 'stop':
                rhs = norm(node.rhs)
                p.stop = p.stop or not rhs.endswith("'b0")
                out.append(p)
            elif base in ('st_n', 'st'):
                rhs = norm(node.rhs)
                if STATE_RE.match(rhs):
                    p.st = rhs
                    out.append(p)
                else:
                    m = TERNARY_STATE_RE.match(rhs)
                    if m:
                        c = norm(m.group('c'))
                        d = decide(p, c)
                        for val, st in ((True, m.group('a')),
                                        (False, m.group('b'))):
                            if d is not None and d != val:
                                continue
                            q = p.clone()
                            if d is None:
                                q.conds.append(c if val else '!(%s)' % c)
                                q.assume[c] = val
                            q.st = st
                            out.append(q)
                    else:                       # an st_n we cannot read
                        p.st = None
                        p.undecided += 1
                        out.append(p)
            else:
                out.append(p)
        return out
    if node.kind == 'if':
        then, els = node.kids[0], node.kids[1]
        out = []
        for p in paths:
            d = decide(p, node.cond)
            c = norm(node.cond)
            if d is not False:
                q = p.clone()
                if d is None:
                    q.conds.append(c)
                    q.assume[c] = True
                out.extend(walk(then, [q]))
            if d is not True:
                q = p.clone()
                if d is None:
                    q.conds.append('!(%s)' % c)
                    q.assume[c] = False
                out.extend(walk(els, [q]) if els is not None else [q])
        return out
    if node.kind == 'case':
        has_default = any(l.strip() == 'default' for l in node.labels)
        out = []
        for p in paths:
            for lab, kid in zip(node.labels, node.kids):
                q = p.clone()
                q.conds.append('case:' + norm(lab))
                out.extend(walk(kid, [q]))
            if not has_default:                 # the implicit no-op arm
                q = p.clone()
                q.conds.append('case:<none>')
                out.append(q)
        return out
    return paths


# --------------------------------------------------------------------------
# the arms
# --------------------------------------------------------------------------
def parse_arms(uc):
    """{arm: (guarded, body_text)} in source order."""
    raw, dropped = expand(uc, STEP)
    lines = raw.split('\n')
    arms, order, cur, buf, guarded = {}, [], None, [], {}
    for line in lines:
        m = ARM_RE.match(line)
        if m:
            if cur:
                arms[cur] = '\n'.join(buf)
            cur = m.group(1)
            order.append(cur)
            guarded[cur] = bool(GUARD_RE.match(line))
            buf = [line[m.end():]]
        elif cur is not None:
            buf.append(line)
    if cur:
        arms[cur] = '\n'.join(buf)
    # the first "arm" text before `case (st_n)` is not an arm; drop stragglers
    for k in list(arms):
        if k == 'endcase':
            del arms[k]
    return arms, guarded, order, dropped


def st_zero_ok_states(uc):
    t = strip_comments(open(os.path.join(uc, EU)).read())
    m = re.search(r'function\s+automatic\s+logic\s+st_zero_ok.*?endfunction',
                  t, re.S)
    return set(re.findall(r'\bS_[A-Z0-9_]+\b', m.group(0))) if m else set()


def analyse(uc):
    arms, guarded, order, dropped = parse_arms(uc)
    res = {}
    for name in order:
        body = arms[name]
        # strip the trailing `endcase` of the LAST arm
        body = re.sub(r'\bendcase\s*$', '', body.rstrip())
        toks = tokenize(body)
        p = Parser(toks)
        stmts = []
        while p.peek() is not None:
            stmts.append(p.statement())
        tree = prune(Node('seq', kids=stmts))
        # the arm's ENTRY state is `name` itself (`default` has none)
        entry = name if STATE_RE.match(name) else None
        paths = walk(tree, [Path(entry)])
        rows = []
        for pa in paths:
            rows.append({'cond': ' && '.join(pa.conds) or '<always>',
                         'stop': pa.stop,
                         'to': pa.st,
                         'undecided': pa.undecided})
        res[name] = {'guarded': guarded[name], 'paths': rows,
                     'raw_paths': len(rows)}
    return res, dropped, order


def fallthrough_edges(res):
    """[(from, to, cond)] for every path that does NOT set `stop`."""
    e = []
    for name, r in res.items():
        for pa in r['paths']:
            if not pa['stop']:
                e.append((name, pa['to'], pa['cond'], pa['undecided']))
    return e


# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# THE GRAPH: sequences, depths, per-position occupancy
# --------------------------------------------------------------------------
def graph(uc):
    """-> dict with the fall-through adjacency, every MAXIMAL chained
    sequence, the depth histogram and the per-position occupancy set.

    A "sequence" is the list of states occupying chain positions 0..d-1 of ONE
    clock edge.  Position 0 may be ANY arm; positions >= 1 may only be an arm
    that some fall-through edge targets.  The enumeration is exhaustive because
    the fall-through sub-graph is a DAG (asserted below), so no path repeats a
    state and none is infinite."""
    res, dropped, order = analyse(uc)
    adj = {}
    for name, r in res.items():
        for pa in r['paths']:
            if not pa['stop'] and pa['to']:
                adj.setdefault(name, []).append((pa['to'], pa['cond']))
    # DAG check over the SUB-GRAPH the positions >= 1 can walk
    z = st_zero_ok_states(uc)
    cyc = []

    def dfs_cycle(n, seen):
        for t, _ in adj.get(n, []):
            if t in seen:
                cyc.append(seen + [t])
            else:
                dfs_cycle(t, seen + [t])
    for n in sorted(z):
        dfs_cycle(n, [n])

    seqs = []

    def walkseq(pref, conds):
        outs = adj.get(pref[-1], [])
        if not outs:
            seqs.append((tuple(pref), tuple(conds)))
            return
        # a state may ALSO stop here (the arm's other paths); a maximal
        # sequence therefore ends at every state that has at least one
        # stopping path as well as at a state with no outgoing edge.
        if any(pa['stop'] for pa in res[pref[-1]]['paths']):
            seqs.append((tuple(pref), tuple(conds)))
        for t, c in outs:
            walkseq(pref + [t], conds + [f'{pref[-1]}->{t}: {c}'])

    for a in order:
        walkseq([a], [])
    depths = {}
    occ = {}
    for sq, _ in seqs:
        depths[len(sq)] = depths.get(len(sq), 0) + 1
        for i, st in enumerate(sq):
            occ.setdefault(i, set()).add(st)
    return {'adj': adj, 'seqs': seqs, 'depths': depths, 'occ': occ,
            'cycles': cyc, 'st_zero_ok': z, 'res': res, 'order': order}


def graph_report(uc, as_json=False):
    g = graph(uc)
    if as_json:
        print(json.dumps({
            'adj': {k: [[t, c] for t, c in v] for k, v in g['adj'].items()},
            'sequences': [{'states': list(s), 'depth': len(s),
                           'conditions': list(c)} for s, c in g['seqs']],
            'depth_histogram': g['depths'],
            'occupancy': {str(k): sorted(v) for k, v in g['occ'].items()},
            'cycles': g['cycles']}, indent=1))
        return g
    print('=== FALL-THROUGH ADJACENCY (the chain graph) ===')
    for k in g['order']:
        for t, c in g['adj'].get(k, []):
            print(f'  {k:<12} -> {t:<12}  when {c}')
    print()
    print('CYCLES IN THE FALL-THROUGH GRAPH: %s'
          % ('NONE (it is a DAG)' if not g['cycles'] else g['cycles']))
    print()
    print('=== MAXIMAL CHAINED SEQUENCES (position 0 may be any arm) ===')
    longest = max(len(s) for s, _ in g['seqs'])
    for s, _ in sorted(g['seqs'], key=lambda x: (-len(x[0]), x[0])):
        if len(s) >= 2:
            print('  d=%d  %s' % (len(s), ' -> '.join(s)))
    print()
    print('DEPTH HISTOGRAM (sequences by length): %s'
          % ' '.join(f'{k}:{v}' for k, v in sorted(g['depths'].items())))
    print('STATIC MAXIMUM OCCUPANCY: %d positions (0..%d)'
          % (longest, longest - 1))
    print()
    print('=== PER-POSITION OCCUPANCY, STATICALLY ===')
    for i in sorted(g['occ']):
        print('  pos %d : %2d  %s' % (i, len(g['occ'][i]),
                                      ' '.join(sorted(g['occ'][i]))))
    return g


def report(uc, as_json=False):
    res, dropped, order = analyse(uc)
    edges = fallthrough_edges(res)
    targets = {t for _, t, _, _ in edges if t}
    out = {'arms': len(res), 'preproc_lines_dropped': dropped,
           'edges': [{'from': f, 'to': t, 'cond': c, 'undecided': u}
                     for f, t, c, u in edges],
           'targets': sorted(targets),
           'st_zero_ok': sorted(st_zero_ok_states(uc))}
    if as_json:
        print(json.dumps(out, indent=1))
        return out
    print(f'ARMS {len(res)}  (preprocessor lines dropped: {dropped})')
    print()
    for name in order:
        r = res[name]
        g = 'chain==0' if r['guarded'] else 'CHAINABLE-BODY'
        ft = [p for p in r['paths'] if not p['stop']]
        print(f'{name:<12} [{g:<14}] paths {len(r["paths"]):>3}   '
              f'fall-through {len(ft)}')
        for p in ft:
            u = '  (UNDECIDED st_n)' if p['undecided'] else ''
            print(f'      -> {str(p["to"]):<12} when  {p["cond"]}{u}')
    print()
    print('FALL-THROUGH TARGETS (%d): %s' %
          (len(targets), ' '.join(sorted(targets))))
    z = st_zero_ok_states(uc)
    print('st_zero_ok()          (%d): %s' % (len(z), ' '.join(sorted(z))))
    return out


def controls(uc, verbose=True):
    """PC-A1 and PC-A2.  -> (ok, detail dict)"""
    res, dropped, order = analyse(uc)
    arms = [a for a in res if STATE_RE.match(a)]
    n_arms = len(arms)
    n_guard = sum(1 for a in arms if res[a]['guarded'])
    n_open = n_arms - n_guard
    unguarded = {a for a in arms if not res[a]['guarded']}
    z = st_zero_ok_states(uc)
    edges = fallthrough_edges(res)
    targets = {t for _, t, _, _ in edges if t}
    a1 = (n_arms == 33 and 'default' in res and n_guard == 24 and n_open == 9
          and unguarded == z)
    a2 = (targets == z)
    d = {'n_arms': n_arms, 'n_guarded': n_guard, 'n_unguarded': n_open,
         'unguarded': sorted(unguarded), 'st_zero_ok': sorted(z),
         'targets': sorted(targets), 'PC-A1': a1, 'PC-A2': a2}
    if verbose:
        print('PC-A1  33 arms + default / 24 guarded / 9 open / open == '
              'st_zero_ok : %s' % ('PASS' if a1 else 'FAIL'))
        print('       arms %d  default %s  guarded %d  open %d' %
              (n_arms, 'default' in res, n_guard, n_open))
        print('       open      : %s' % ' '.join(sorted(unguarded)))
        print('       st_zero_ok: %s' % ' '.join(sorted(z)))
        print('PC-A2  fall-through targets == st_zero_ok                    '
              ': %s' % ('PASS' if a2 else 'FAIL'))
        print('       targets   : %s' % ' '.join(sorted(targets)))
    return a1 and a2, d


def nonvacuity(uc):
    """PC-A3.  Delete ONE named `stop = 1'b1;` in a scratch copy and require
    the target set to GROW and PC-A2 to FAIL."""
    tmp = tempfile.mkdtemp(prefix='chainflat-nv-',
                           dir=os.path.expanduser('~/.cache/ucsimt-tmp'))
    try:
        d = os.path.join(tmp, 'ucore')
        shutil.copytree(uc, d)
        f = os.path.join(d, STEP)
        txt = open(f).read()
        # S_PFX_CHG's own `stop`: an arm whose ONLY exit is `S_OPC_POP; stop`.
        old = ("    pop_is_first_n = 1'b1;                        "
               "// prefix_retire()\n    st_n = S_OPC_POP;\n    stop = 1'b1;\n")
        new = ("    pop_is_first_n = 1'b1;                        "
               "// prefix_retire()\n    st_n = S_OPC_POP;\n")
        if old not in txt:
            print('PC-A3  CANNOT RUN: the S_PFX_CHG anchor text moved',
                  file=sys.stderr)
            return False, {}
        open(f, 'w').write(txt.replace(old, new, 1))
        ok, det = controls(d, verbose=False)
        grew = 'S_OPC_POP' in det['targets']
        fired = (not det['PC-A2']) and grew
        print('PC-A3  NON-VACUITY (one `stop` deleted from S_PFX_CHG)        '
              ': %s' % ('PASS' if fired else 'FAIL'))
        print('       PC-A2 now %s ; targets now: %s' %
              ('PASS (WRONG)' if det['PC-A2'] else 'FAIL (right)',
               ' '.join(det['targets'])))
        return fired, det
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ucore', default=UC_DEFAULT)
    ap.add_argument('--control', action='store_true')
    ap.add_argument('--nonvacuity', action='store_true')
    ap.add_argument('--graph', action='store_true')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    os.makedirs(os.path.expanduser('~/.cache/ucsimt-tmp'), exist_ok=True)
    if a.control or a.nonvacuity:
        ok = True
        if a.control:
            ok &= controls(a.ucore)[0]
        if a.nonvacuity:
            ok &= nonvacuity(a.ucore)[0]
        return 0 if ok else 1
    if a.graph:
        graph_report(a.ucore, as_json=a.json)
    else:
        report(a.ucore, as_json=a.json)
    return 0


if __name__ == '__main__':
    sys.exit(main())
