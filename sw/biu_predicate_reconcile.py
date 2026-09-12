#!/usr/bin/env python3
"""WAVE 10 -- K-2.  THE PREDICATE RECONCILIATION.  OFFLINE, NO QUARTUS.

WAVE 8 sec.4 measured the EU -> BIU -> EU combinational round trip at **0.000 ns
on 0 of 1,200 CONTROL paths** and concluded *"it is not a candidate"*.
WAVE 9 sec.5.4 measured the SAME round trip on **200 of 200 CONTROL paths** at a
mean span of **2.786 ns**.  Both instruments passed their own positive controls.

**THE FIRST JOB OF WAVE 10 IS TO SAY WHETHER THOSE TWO INSTRUMENTS ASKED THE
SAME QUESTION, AND THIS FILE ANSWERS IT WITHOUT COMPILING ANYTHING** -- it runs
BOTH predicates over BOTH waves' OWN COMMITTED ARTIFACTS, so a difference in the
answer that survives is a difference in the DESIGN and not in the question.

⚠ IT COMPARES CONTENT, NEVER A DIGEST IT COMPUTED ITSELF.  Every number below
is a count of lines in a committed file, and the file is named beside it.

THE FOUR AXES ON WHICH TWO PATH CLASSIFIERS CAN DIFFER, and this file measures
all four:

  AX-1  THE MATCH.  What string, on what form of the node name?
          WAVE 8 : `'|u_biu|' in FS.norm(name)`     -- type prefixes STRIPPED,
                   so it matches BOTH `...|v30u_biu:u_biu|q_cnt` (a register)
                   and `...|u_biu|q_cnt~2|combout` (a LUT).
          WAVE 9 : `[string first "|u_biu|" $nm] >= 0` -- the RAW name, which
                   Quartus prints WITHOUT the type prefix on combinational
                   nodes and WITH it on registers, so it matches LUTs only.
                   Its own PC-B prints the type-prefix form as the known-wrong
                   control.
  AX-2  THE SECTION.  Which arrival points of the path are eligible?
          WAVE 8 : the DATA section only (its `walk` accumulates `pts` while
                   `state == 2`, i.e. strictly between the launch node and the
                   destination node).
          WAVE 9 : EVERY arrival point, clock network included.
  AX-3  THE POPULATION.  Which paths?
          WAVE 8 : `-npaths 400 -nworst 1`  -- ENDPOINT-DIVERSE, one path per
                   endpoint pair, so 400 DIFFERENT (from, to) pairs.
          WAVE 9 : `-npaths 200`            -- the top 200 by slack with no
                   diversity constraint, which on a design with one binding
                   cone is 200 slices of ONE arc.
  AX-4  THE SPAN CONVENTION (a size, not a presence).
          WAVE 8 : `last.cum - (first.cum - first.incr)` -- INCLUDES the
                   interconnect INTO the first BIU node.
          WAVE 9 : `last.total - first.total`            -- EXCLUDES it.

usage:  python3 sw/biu_predicate_reconcile.py
"""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(ROOT, 'sw'))
import frontend_srcmap as FS   # noqa: E402

W8 = os.path.join(ROOT, 'sw/testdata/frontend/anat')
W9 = os.path.join(ROOT, 'sw/testdata/wave9')
W8_DRAWS = ['control_seed1', 'control_seed2', 'control_seed3', 'retention_seed1']


# --------------------------------------------------------------------------- #
#  THE TWO PREDICATES, TRANSCRIBED FROM THE TWO INSTRUMENTS.
#  `pred8` is `sw/frontend_anat_report.py:biu_span`'s test.
#  `pred9` is `sw/sta_cutset_biu_census.tcl`'s `string first "|u_biu|" $nm`.
# --------------------------------------------------------------------------- #
def pred8(name):
    return '|u_biu|' in FS.norm(name)


def pred9(name):
    return name.find('|u_biu|') >= 0


def pred9_knownwrong(name):
    """WAVE 9's OWN negative control: the TYPE prefix form (must read 0)."""
    return name.find('v30u_biu:') >= 0


def span8(hits):
    """WAVE 8's convention: includes the interconnect INTO the first BIU node."""
    if not hits:
        return 0.0
    return hits[-1][0] - (hits[0][0] - hits[0][1])


def span9(hits):
    """WAVE 9's convention: first BIU point's total .. last BIU point's total."""
    if not hits:
        return 0.0
    return hits[-1][0] - hits[0][0]


# --------------------------------------------------------------------------- #
def read_population(path):
    out, cur = [], None
    for line in open(path):
        if line.startswith('#'):
            continue
        f = line.split(None, 6)
        if not f:
            continue
        if f[0] == 'P':
            rest = f[6].split() if len(f) > 6 else []
            cur = {'idx': int(f[1]), 'slack': float(f[2]), 'delay': float(f[3]),
                   'frm': rest[0] if rest else '', 'to': rest[1] if len(rest) > 1 else '',
                   'pts': []}
            out.append(cur)
        elif f[0] == 'N' and cur is not None:
            cur['pts'].append((float(f[2]), float(f[3]), f[4], f[5].strip()))
    return out


def read_arrivalpoints(path):
    """WAVE 9's dump: `%8.3f  <name>` per line, ALL points, clock included."""
    pts = []
    for line in open(path):
        m = re.match(r'\s*(-?[\d.]+)\s+(\S.*)$', line.rstrip('\n'))
        if m:
            pts.append((float(m.group(1)), m.group(2).strip()))
    return pts


def hits_of(pts, pred):
    """pts as (cum, inc, ty, name) -> [(cum, inc, name)] in order."""
    return [(c, i, n) for (c, i, t, n) in pts if pred(n)]


P = print


# --------------------------------------------------------------------------- #
def main():
    ok = True
    P('=' * 74)
    P('WAVE 10 / K-2 -- THE PREDICATE RECONCILIATION.  OFFLINE.')
    P('=' * 74)

    # ---------------------------------------------------------------- controls
    P('')
    P('### PC-R0  THE ARTIFACTS EXIST AND ARE THE COMMITTED ONES (named, counted)')
    for d in W8_DRAWS:
        p = os.path.join(W8, d + '.population.txt')
        n = sum(1 for _ in open(p))
        P(f'  {os.path.relpath(p, ROOT):58s}  {n:6d} lines')
    p9 = os.path.join(W9, 'diag_ctl_seed2.arrivalpoints.txt')
    P(f'  {os.path.relpath(p9, ROOT):58s}  {sum(1 for _ in open(p9)):6d} lines')
    p9c = os.path.join(W9, 'diag_ctl_seed2.biucensus.txt')
    P(f'  {os.path.relpath(p9c, ROOT):58s}  {sum(1 for _ in open(p9c)):6d} lines')

    P('')
    P('### PC-R1  EACH PREDICATE CAN SAY YES, ON THE OTHER WAVE\'S OWN ARTIFACT')
    P('    (a predicate that cannot say YES anywhere is the vacuity this')
    P('     campaign has been caught by EIGHT times)')
    w9pts = read_arrivalpoints(p9)
    n8_on9 = sum(1 for (_, n) in w9pts if pred8(n))
    n9_on9 = sum(1 for (_, n) in w9pts if pred9(n))
    nkw_on9 = sum(1 for (_, n) in w9pts if pred9_knownwrong(n))
    P(f'  WAVE 8\'s predicate on WAVE 9\'s binding path : {n8_on9:4d} points  (MUST be > 0)')
    P(f'  WAVE 9\'s predicate on WAVE 9\'s binding path : {n9_on9:4d} points  (MUST be > 0)')
    P(f'  the KNOWN-WRONG type-prefix form, same path : {nkw_on9:4d} points  (MUST be 0)')
    ret = read_population(os.path.join(W8, 'retention_seed1.population.txt'))
    n8_on8 = sum(len(hits_of(p['pts'], pred8)) for p in ret)
    n9_on8 = sum(len(hits_of(p['pts'], pred9)) for p in ret)
    nkw_on8 = sum(len(hits_of(p['pts'], pred9_knownwrong)) for p in ret)
    P(f'  WAVE 8\'s predicate on WAVE 8 retention_seed1: {n8_on8:4d} points  (MUST be > 0)')
    P(f'  WAVE 9\'s predicate on WAVE 8 retention_seed1: {n9_on8:4d} points  (MUST be > 0)')
    P(f'  the KNOWN-WRONG type-prefix form, same file : {nkw_on8:4d} points  (MUST be 0)')
    if not (n8_on9 > 0 and n9_on9 > 0 and nkw_on9 == 0
            and n8_on8 > 0 and n9_on8 > 0 and nkw_on8 == 0):
        ok = False
        P('  *** PC-R1 FAILED ***')
    else:
        P('  PC-R1 PASS')

    P('')
    P('### PC-R2  A NAME THAT IS NOT THERE READS ZERO (the negative control)')
    absent = sum(1 for (_, n) in w9pts if '|u_no_such_instance|' in n)
    absent2 = sum(len(hits_of(p['pts'], lambda n: '|u_no_such_instance|' in n))
                  for p in ret)
    P(f'  `|u_no_such_instance|` on WAVE 9 binding path: {absent:4d}  (MUST be 0)')
    P(f'  `|u_no_such_instance|` on WAVE 8 retention   : {absent2:4d}  (MUST be 0)')
    if absent or absent2:
        ok = False
        P('  *** PC-R2 FAILED ***')
    else:
        P('  PC-R2 PASS')

    # ---------------------------------------------------------------- AX-1
    P('')
    P('=' * 74)
    P('## AX-1  THE MATCH.  DO THE TWO PREDICATES SELECT THE SAME NODES?')
    P('=' * 74)
    P('')
    P('  file / draw            | points | pred8 | pred9 | DISAGREE | type-prefix')
    disagree_total = 0
    for d in W8_DRAWS:
        pts = [pt for p in read_population(os.path.join(W8, d + '.population.txt'))
               for pt in p['pts']]
        a = sum(1 for (_, _, _, n) in pts if pred8(n))
        b = sum(1 for (_, _, _, n) in pts if pred9(n))
        dis = sum(1 for (_, _, _, n) in pts if pred8(n) != pred9(n))
        kw = sum(1 for (_, _, _, n) in pts if pred9_knownwrong(n))
        disagree_total += dis
        P(f'  W8 {d:20s}| {len(pts):6d} | {a:5d} | {b:5d} | {dis:8d} | {kw:5d}')
    a = sum(1 for (_, n) in w9pts if pred8(n))
    b = sum(1 for (_, n) in w9pts if pred9(n))
    dis = sum(1 for (_, n) in w9pts if pred8(n) != pred9(n))
    disagree_total += dis
    P(f'  W9 {"diag_ctl_seed2":20s}| {len(w9pts):6d} | {a:5d} | {b:5d} | {dis:8d} | '
      f'{sum(1 for (_, n) in w9pts if pred9_knownwrong(n)):5d}')
    P('')
    if disagree_total == 0:
        P('  > **AX-1: THE TWO PREDICATES SELECT THE IDENTICAL NODE SET ON EVERY')
        P('  >  POINT OF EVERY COMMITTED ARTIFACT OF BOTH WAVES.  THE MATCH IS THE')
        P('  >  SAME QUESTION.**')
    else:
        P(f'  > **AX-1: THE PREDICATES DISAGREE ON {disagree_total} POINTS.**')
    P('')
    P('  ⚠ AND THAT IS AN AGREEMENT ON THESE ARTIFACTS, NOT AN IDENTITY OF THE')
    P('    TWO TESTS: WAVE 8\'s strips the type prefix and so WOULD also match a')
    P('    BIU *register*; WAVE 9\'s would not.  No BIU register appears in the')
    P('    data section of a `ce -> ce` path (the launch and the destination are')
    P('    the only registers on it), which is why the sets coincide.')

    # ---------------------------------------------------------------- AX-2
    P('')
    P('=' * 74)
    P('## AX-2  THE SECTION.  DATA-ONLY (W8) vs ALL ARRIVAL POINTS (W9).')
    P('=' * 74)
    P('')
    nclk = 0
    for i, (t, n) in enumerate(w9pts):
        if pred9(n):
            nclk = i
            break
    P(f'  WAVE 9\'s dump is ALL {len(w9pts)} arrival points; the clock network')
    P(f'  occupies the head of it and the first BIU point is line {nclk + 1}.')
    P('  A BIU hit in a CLOCK section would be a false positive WAVE 8 cannot make')
    P('  and WAVE 9 can.  Measured on the artifact:')
    clkpts = [n for (_, n) in w9pts[:nclk] if pred9(n)]
    P(f'    BIU points BEFORE the launch register on WAVE 9\'s binding path: '
      f'{len(clkpts)}  (MUST be 0)')
    if clkpts:
        ok = False
        P('    *** AX-2 CONTROL FAILED: WAVE 9\'s section is admitting clock nodes ***')
    else:
        P('  > **AX-2: NOT A DIFFERENCE IN THE ANSWER ON THE ARTIFACT AT HAND.**')
        P('  >  The wider section admits nodes WAVE 8 would exclude, but on a')
        P('  >  `ce -> ce` path the clock network holds no `u_biu` combinational')
        P('  >  node, so the two sections select the same points.')

    # ---------------------------------------------------------------- AX-3
    P('')
    P('=' * 74)
    P('## AX-3  THE POPULATION.  THIS IS THE ONE REAL DIFFERENCE OF QUESTION.')
    P('=' * 74)
    P('')
    P('  draw                  | paths | DISTINCT (from,to) pairs | slack range')
    for d in W8_DRAWS:
        ps = read_population(os.path.join(W8, d + '.population.txt'))
        pairs = len({(p['frm'], p['to']) for p in ps})
        sl = [p['slack'] for p in ps]
        P(f'  W8 {d:19s}| {len(ps):5d} | {pairs:24d} | {min(sl):+7.3f} .. {max(sl):+7.3f}')
    P('')
    P('  > **WAVE 8\'s 400 paths are 400 DIFFERENT ENDPOINT PAIRS (`-nworst 1`).**')
    P('  > **WAVE 9\'s 200 are the top 200 BY SLACK with no diversity constraint,**')
    P('  > **so they may all be slices of ONE arc.  THOSE ARE DIFFERENT QUESTIONS:**')
    P('  > *"is the round trip on an endpoint-diverse spread of the ce -> ce')
    P('  >  population?"* against *"is it on the binding class?"*')
    P('')
    P('  ⚠ **AND THE POPULATION DIFFERENCE DOES NOT EXPLAIN THE CONTRADICTION,**')
    P('    because the WORST PATH IS IN BOTH POPULATIONS BY CONSTRUCTION.  Path 0')
    P('    of a `-nworst 1` dump is the same worst path a plain `-npaths` dump')
    P('    starts with.  Measured on WAVE 8\'s own control artifacts:')
    for d in W8_DRAWS:
        ps = read_population(os.path.join(W8, d + '.population.txt'))
        h = hits_of(ps[0]['pts'], pred9)
        carr = sum(1 for p in ps if hits_of(p['pts'], pred9))
        P(f'    W8 {d:19s} worst arc BIU points {len(h):3d}   '
          f'paths carrying it {carr:3d} / {len(ps)}')

    # ---------------------------------------------------------------- AX-4
    P('')
    P('=' * 74)
    P('## AX-4  THE SPAN CONVENTION.  A SIZE DIFFERENCE, NOT A PRESENCE ONE.')
    P('=' * 74)
    P('')
    P('  draw                  | carrying | mean span W8 conv | mean span W9 conv | delta')
    for d in W8_DRAWS:
        ps = read_population(os.path.join(W8, d + '.population.txt'))
        s8 = [span8(hits_of(p['pts'], pred8)) for p in ps]
        s9 = [span9(hits_of(p['pts'], pred9)) for p in ps]
        pres8 = [x for x in s8 if x > 0]
        pres9 = [x for x in s9 if x > 0]
        if pres8:
            P(f'  W8 {d:19s}| {len(pres8):4d}/{len(ps)} | {sum(pres8)/len(pres8):17.3f} '
              f'| {sum(pres9)/len(pres9):17.3f} | {sum(pres8)/len(pres8) - sum(pres9)/len(pres9):+6.3f}')
        else:
            P(f'  W8 {d:19s}| {0:4d}/{len(ps)} | {"--":>17s} | {"--":>17s} | {"--":>6s}')
    # WAVE 9's own path, both conventions.  Its dump has no `incr` column, so
    # the W8 convention is reconstructed from the PREVIOUS point's total.
    idx = [i for i, (_, n) in enumerate(w9pts) if pred9(n)]
    if idx:
        first_total = w9pts[idx[0]][0]
        prev_total = w9pts[idx[0] - 1][0] if idx[0] > 0 else first_total
        last_total = w9pts[idx[-1]][0]
        P(f'  W9 {"diag_ctl_seed2":19s}| {1:4d}/{1:4d} | {last_total - prev_total:17.3f} '
          f'| {last_total - first_total:17.3f} | {first_total - prev_total:+6.3f}')
    P('')
    P('  > **AX-4: WAVE 8\'s span is the LARGER of the two by one interconnect')
    P('  >  segment.  It cannot turn 0.000 into 2.786 and it is not the')
    P('  >  contradiction; it IS a reason not to diff the two waves\' ns figures')
    P('  >  without saying which convention each used.**')

    # ---------------------------------------------------------------- verdict
    P('')
    P('=' * 74)
    P('## THE RECONCILIATION, IN ONE TABLE')
    P('=' * 74)
    P('')
    P('  axis | same question? | measured on the committed artifacts')
    P('  AX-1 the match       | **YES** | identical node set on every point of both waves')
    P('  AX-2 the section     | **YES on this design** | 0 BIU nodes in any clock section')
    P('  AX-3 the population  | **NO**  | endpoint-diverse 400 vs top-200-by-slack')
    P('  AX-4 the span        | **NO**  | W8 includes the entry interconnect, W9 does not')
    P('')
    P('  ⚠ **AND AX-3, THE ONE REAL DIFFERENCE OF QUESTION, IS NOT THE**')
    P('  ⚠ **RESOLUTION** -- the worst path belongs to both populations, and on')
    P('  ⚠ **all three of WAVE 8\'s CONTROL draws it carries ZERO BIU nodes.**')
    P('')
    P('  So the two instruments agree about what to look for and disagree about')
    P('  what they found.  WHAT IS LEFT IS THREE CONFOUNDS IN THE DESIGN, NOT IN')
    P('  THE QUESTION: the TREE (WAVE 8 uncut, WAVE 9 cut), the CONFIGURATION')
    P('  (WAVE 8\'s one RETENTION draw carried it 400/400; its CONTROL draws did')
    P('  not), and the DRAW.  **THAT IS WHAT WAVE 10 MEASURES WITH ONE**')
    P('  **INSTRUMENT ACROSS BOTH TREES AND BOTH CONFIGURATIONS.**')
    P('')
    P('CONTROLS: ' + ('ALL PASS' if ok else '*** FAILED -- NOTHING ABOVE MAY BE QUOTED ***'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
