#!/usr/bin/env python3
"""WAVE 19 -- V-1's LADDER COMPARATOR.  BEFORE vs ARM-B, **LEG BY LEG, BY THE
SCORED LINE**, never by raw log text.

⚠ COMPARING RAW LOG TEXT REPORTS EVERY LEG AS DIFFERING (timestamps, paths,
receipts, `time` output) -- trap #10 of the campaign's vacuous-instrument
register.  So each leg declares the REGEXes whose matching lines ARE its scored
content, and only those lines are compared.

⚠ AND THE COMPARATOR CARRIES ITS OWN POSITIVE CONTROL: `--selftest` perturbs one
character of one scored line and REQUIRES the comparison to fail.  A comparator
that cannot say DIFFERENT cannot be trusted when it says IDENTICAL.

usage:  python3 sw/wave19_ladder_cmp.py BEFORE_DIR AFTER_DIR [--selftest]
"""
import os
import re
import sys

# leg -> the regexes whose matching lines are that leg's SCORED CONTENT.
SCORED = {
    'r7_lint':           [r'^=== r7_lint:'],
    'core_portlist_lint':[r'^core_portlist_lint:'],
    'ss_lint':           [r'^ss_lint: ', r'^ss_flopcensus:', r'architectural flops ->'],
    'phase_split_lint':  [r'^=== phase_split_lint:'],
    'cutset_lint':       [r'^=== cutset_lint:'],
    'chainflat_reloc':   [r'^chainflat_relocation_check:'],
    'cc_all':            [r'^TOTAL:'],
    'cc_FA':             [r'^TOTAL:', r'^FA:'],
    'cc_FB':             [r'^TOTAL:', r'^FB:'],
    'cc_INTFB':          [r'^TOTAL:', r'^INT\.FB:'],
    'cc_8f0':            [r'^TOTAL:'],
    'hlt_w0':            [r'^TOTAL:', r'^\s*FAIL'],
    'hlt_w1':            [r'^TOTAL:', r'^\s*FAIL'],
    'hlt_w2':            [r'^TOTAL:', r'^\s*FAIL'],
    'hlt_w3':            [r'^TOTAL:', r'^\s*FAIL'],
    'v01_w1':            [r'^TOTAL:'],
    'v01_w3':            [r'^TOTAL:'],
    'v01_w1_EB':         [r'^TOTAL:'],
    'evt_w0':            [r'^TOTAL:'],
    'evt_w1':            [r'^TOTAL:'],
    'evt_w2':            [r'^TOTAL:'],
    'evt_w3':            [r'^TOTAL:'],
    'evt_biased':        [r'^TOTAL:'],
    'cc_all_div2':       [r'^TOTAL:'],
    'cc_all_div3':       [r'^TOTAL:'],
    'cc_all_div8':       [r'^TOTAL:'],
    'cc_div1_refused':   [r'REFUSED'],
    'ulockstep':         [r'LOCKSTEP$', r'^\s*TOTAL '],
    'ghost_launch':      [r'POPULATIONS'],
    'check_boot':        [r'^BOOT REPLAY'],
    'check_boot400':     [r'^BOOT REPLAY'],
    'check_ab_sim':      [r'^AB SIM'],
    's16':               [r'^S16 TOTAL', r'signature census'],
    'demux_off':         [r'^=== demux_off_gate:'],
    'test_artifact':     [r'^=== test_artifact:'],
    'test_quartus_gate': [r'checks pass', r'^=== test_quartus_gate:'],
    'ucrom_mif':         [r'^ucrom_mif_check: PASS'],
    'chain_lfsr':        [r'sig=', r'^chain_lfsr_gate:', r'gap', r'live'],
}


def scored(path, pats):
    out = []
    if not os.path.exists(path):
        # WAVE 19 -- THE ONE CLAUSE THIS COMPARATOR ADDS, AND IT IS WAVE 17
        # §3.1a's FINDING.  `wave16_ladder_cmp.py` returns a sentinel LINE here,
        # two absent logs then compare EQUAL, and a comparison over ZERO REAL
        # DATA reports `37 IDENTICAL, 0 DIFFERING, 0 VACUOUS`.  It happened, and
        # only `--selftest` running in the same invocation caught it.  Returning
        # the EMPTY list routes an absent log into the VACUOUS branch, which
        # prints and exits non-zero.  ⚠ `sw/wave16_ladder_cmp.py` IS NOT EDITED
        # -- this is a NEW instrument, not a repair of the shared one, and no
        # figure of WAVE 19 is quoted from the old one.
        return []
    for ln in open(path, errors='replace'):
        ln = ln.rstrip('\n')
        if any(re.search(p, ln) for p in pats):
            out.append(ln)
    return out


def main():
    b, a = sys.argv[1], sys.argv[2]
    selftest = '--selftest' in sys.argv
    bad = empty = 0
    differing = []
    for leg, pats in SCORED.items():
        lb = scored(os.path.join(b, leg + '.log'), pats)
        la = scored(os.path.join(a, leg + '.log'), pats)
        if selftest and leg == 'cc_all' and la:
            la = [la[0].replace('169000', '168999')] + la[1:]
        if not lb:
            empty += 1
            print(f'  {leg:<20} *** NO SCORED LINE MATCHED -- VACUOUS LEG ***')
            continue
        if lb == la:
            print(f'  {leg:<20} IDENTICAL ({len(lb)} scored line(s))  {lb[0][:76]}')
        else:
            bad += 1
            differing.append(leg)
            print(f'  {leg:<20} *** DIFFERS ***')
            for i in range(max(len(lb), len(la))):
                x = lb[i] if i < len(lb) else '<absent>'
                y = la[i] if i < len(la) else '<absent>'
                if x != y:
                    print(f'      base: {x}\n      arm : {y}')
    print(f'\n=== {len(SCORED)} legs: {len(SCORED) - bad - empty} IDENTICAL, '
          f'{bad} DIFFERING, {empty} VACUOUS ===')
    if selftest:
        # ⚠ THE CONTROL IS MEMBERSHIP, NOT A COUNT.  A REAL difference may also
        # be present (WAVE 16's `ss_lint` combinational-reg line is one), and a
        # `bad == 1` test would then read the control as failing when it in fact
        # worked.  The question the control asks is only: does the comparator
        # NOTICE the character this file just changed?
        ok = 'cc_all' in differing and empty == 0
        print(f'SELFTEST: perturbing one scored line of cc_all was '
              f'{"DETECTED -- the comparator can say DIFFERENT" if ok else "*** NOT DETECTED ***"}'
              f'   (all differing legs: {differing})')
        return 0 if ok else 3
    return 0 if (bad == 0 and empty == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
