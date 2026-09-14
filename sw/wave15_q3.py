#!/usr/bin/env python3
"""WAVE 15 -- Q-3's CLASSIFIER.  **PURE POST-PROCESSING OF `sta_biu_roundtrip.tcl`'s
OWN COMMITTED `*.rows.txt`.  IT RUNS NO STA AND EDITS NO INSTRUMENT.**

WAVE 10's `sw/sta_biu_roundtrip.tcl` is used UNEDITED (the WAVE 14 precedent:
*changing an instrument in the wave that measures with it is how a result gets
chosen*).  This file only READS the rows it writes and asks two questions of
them, one of which the tcl already prints and one of which it does not:

  **Q-3a  BY NAME** -- the tcl's own `<ripe>` column, i.e. how many paths of the
        population carry a node whose name contains `q_ripe_lead_n`.
        ⚠ The tcl's matcher is `string first "q_ripe_lead_n"`, a SUBSTRING test,
        so it matches WAVE 15's `q_ripe_lead_n0` / `q_ripe_lead_n1` as well.
        **That is deliberate and it is what makes Q-3a honest**: the mechanism
        cannot pass by renaming the node.

  **Q-3b  STRUCTURALLY** -- THIS mechanism's round trip: the path LAUNCHES in
        `u_eu`, ENDS in `u_eu`, carries a BIU node in its DATA SECTION, **and**
        carries `q_ripe_lead_n*`.  A path that launches at a BIU REGISTER and
        ends in the EU is NOT a round trip; it is the registered boundary
        working, and that is exactly the shape C1 converts the arc into.
        **Q-3a alone cannot tell those two apart.**

  **Q-3c  THE RESIDUAL, REPORTED AND NOT GATED** -- EU -> BIU -> EU through ANY
        BIU node.  ⚠ IT IS NOT ZERO EVEN ON WAVE 14's PROBE ARMS: `w14-tie`'s
        CONTROL netlist carries **115 of 200** such paths with `q_ripe_lead_n`
        on none of them.  **That was learned from the control before this wave
        had any data of its own**, and it is why Q-3b is scoped to this
        mechanism instead of to the word "round trip".

**THE POSITIVE CONTROL IS MANDATORY AND IS PRINTED FIRST**: the same classifier
must read 200 of 200 on the BASE arm's rows in the same invocation.  A
classifier that cannot say YES cannot be trusted when it says NO -- nine
instruments in this campaign have produced confident, wrong, vacuous results.

usage:
    python3 sw/wave15_q3.py --base BASE.rows.txt --arm ARM.rows.txt [--pop A_topN]
    python3 sw/wave15_q3.py --selftest      # against WAVE 14's committed rows
"""
import argparse
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# `# R <pop> <idx> <slack> <data_delay> <biu_all> <biu_data> <ripe>
#    <typeprefix> <span9> <span8> <from> <to>`
COLS = ['tag', 'pop', 'idx', 'slack', 'data_delay', 'biu_all', 'biu_data',
        'ripe', 'typeprefix', 'span9', 'span8', 'frm', 'to']


def rows(path, pop):
    out = []
    with open(path) as f:
        for line in f:
            if not line.startswith('R '):
                continue
            p = line.split()
            if len(p) != 13:
                raise SystemExit(f'REFUSING: unparsable row in {path}: {line!r}')
            r = dict(zip(COLS, p))
            if r['pop'] != pop:
                continue
            for k in ('biu_all', 'biu_data', 'ripe', 'typeprefix'):
                r[k] = int(r[k])
            out.append(r)
    return out


def score(rs):
    n = len(rs)
    a = sum(1 for r in rs if r['ripe'] > 0)
    rt = [r for r in rs if r['biu_data'] > 0
          and ':u_eu|' in r['frm'] and ':u_eu|' in r['to']]
    b = sum(1 for r in rt if r['ripe'] > 0)
    c = len(rt)
    # the two ways a path can carry a BIU node WITHOUT being a round trip
    biu_launch = sum(1 for r in rs if r['biu_data'] > 0 and ':u_eu|' not in r['frm'])
    biu_land = sum(1 for r in rs if r['biu_data'] > 0 and ':u_eu|' not in r['to'])
    return dict(n=n, q3a=a, q3b=b, q3c=c,
                biu_data=sum(1 for r in rs if r['biu_data'] > 0),
                biu_launch=biu_launch, biu_land=biu_land)


def show(tag, s):
    print(f'  {tag:<22} paths {s["n"]:>4}   '
          f'Q-3a `q_ripe_lead_n*` BY NAME {s["q3a"]:>4}   '
          f'Q-3b EU->BIU->EU via ripe {s["q3b"]:>4}   '
          f'Q-3c EU->BIU->EU any {s["q3c"]:>4}   '
          f'(BIU in data section {s["biu_data"]}, '
          f'non-EU launch {s["biu_launch"]}, non-EU landing {s["biu_land"]})')


def selftest():
    """WAVE 14's committed base and probe rows.  The base MUST read 200/200 on
    both questions and the two probe arms MUST read 0 on both -- which is the
    demonstration that this classifier can say YES and can say NO."""
    ok = True
    for arm, want_a, want_b in (('w14-base', 200, 200), ('w14-tie', 0, 0),
                                ('w14-hold', 0, 0)):   # Q-3c is NOT asserted
        for cfg in ('control', 'retention'):
            p = os.path.join(ROOT, 'sw/testdata/wave14', arm,
                             f'roundtrip_{cfg}.rows.txt')
            if not os.path.exists(p):
                print(f'  SELFTEST: missing {p}')
                ok = False
                continue
            s = score(rows(p, 'A_topN'))
            good = (s['q3a'] == want_a and s['q3b'] == want_b and s['n'] == 200)
            ok = ok and good
            show(f'{arm}/{cfg}', s)
            print(f'      expect Q-3a {want_a} Q-3b {want_b} over 200  ->  '
                  f'{"OK" if good else "*** SELFTEST FAILED ***"}')
    print(f'\n=== wave15_q3 SELFTEST: {"PASS" if ok else "*** FAILED ***"} ===')
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base')
    ap.add_argument('--arm')
    ap.add_argument('--pop', default='A_topN')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not (a.base and a.arm):
        ap.error('--base and --arm are both required (the base is the control)')
    b = score(rows(a.base, a.pop))
    m = score(rows(a.arm, a.pop))
    print(f'=== Q-3, population {a.pop} ===')
    print('  THE POSITIVE CONTROL FIRST:')
    show('BASE (control)', b)
    show('ARM', m)
    ctl = (b['q3a'] == b['n'] and b['q3b'] == b['n'] and b['n'] > 0)
    print(f'\n  control: the base must read {b["n"]}/{b["n"]} on BOTH questions  ->  '
          f'{"PASS" if ctl else "*** FAILED -- NOTHING BELOW MAY BE QUOTED ***"}')
    if not ctl:
        return 4
    print(f'  Q-3a  arm {m["q3a"]} of {m["n"]}   (bar: 0)  -> '
          f'{"MET" if m["q3a"] == 0 else "MISSED"}')
    print(f'  Q-3b  arm {m["q3b"]} of {m["n"]}   (bar: 0)  -> '
          f'{"MET" if m["q3b"] == 0 else "MISSED"}')
    print(f'  Q-3c  arm {m["q3c"]} of {m["n"]}   (REPORTED, NOT GATED -- '
          f'base {b["q3c"]}; WAVE 14`s tie/control read 115)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
