#!/usr/bin/env python3
"""Measure the WIDTH of the phase-split shadow register at WAVE 1's named cut.

WAVE 1 (`docs/notes/phase_split_anatomy_2026-09-08.md` §6 item 2) declares the
width of the phase register UNMEASURED and names it wave 2's first job.  This
is that measurement, and it is deliberately an UPPER BOUND: a name mentioned
at or after the cut is counted as read even if it is only ever an assignment
target there.  Over-reports, never under-reports.

THE CUT is the ENTRY to `v30u_eu.sv`'s unrolled
`for (chain = 0; chain < CHAIN_MAX; ...)` loop.

  STAGE 1 = the next-state block's pre-loop body (the `else` arm of
            `if (ss_we)`, blocks (a)-(f)).
  STAGE 2 = the loop, block (g) and the tail.

The CROSSING SET is every declared variable ASSIGNED in stage 1 and MENTIONED
in stage 2.  The preload -- which assigns every `_n` from its own flop -- is
EXCLUDED by construction: a `_n` that stage 1 never touches is readable by
stage 2 straight off the flop and crosses nothing.

`ifndef SYNTHESIS` trace-only names are dropped and listed.
"""
import re, sys, os

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'hdl', 'rtl', 'ucore')

def load(f):
    return open(os.path.join(D, f)).read().split('\n')

def expand(lines, depth=0):
    out = []
    for l in lines:
        m = re.search(r'`include "([^"]+)"', l)
        if m and depth < 6:
            out += expand(load(m.group(1)), depth + 1)
        else:
            out.append(l)
    return out

def main():
    eu = load('v30u_eu.sv')
    LOOP = SSW = END = None
    for i, l in enumerate(eu):
        if 'for (chain = 0; chain < CHAIN_MAX' in l and LOOP is None:
            LOOP = i
        if l.strip().startswith('if (ss_we) begin') and SSW is None:
            SSW = i
        if l.startswith('assign dec_addr_next') and END is None:
            END = i
    assert None not in (LOOP, SSW, END), (LOOP, SSW, END)

    nocomment = lambda ls: [re.sub(r'//.*', '', l) for l in ls]
    stage1 = nocomment(expand(eu[SSW + 3:LOOP]))
    stage2 = nocomment(expand(eu[LOOP:END]))

    # declared widths, module-wide
    w = {}
    for l in eu:
        m = re.match(r'^\s*(?:reg|logic)\s*(?:signed\s*)?(\[([^\]]+)\])?\s+(.*?);', l)
        if not m:
            continue
        rng = m.group(2)
        base = 1
        if rng:
            mm = re.match(r'\s*(\d+)\s*:\s*(\d+)\s*$', rng)
            base = abs(int(mm.group(1)) - int(mm.group(2))) + 1 if mm else 'EXPR:' + rng.strip()
        for n in m.group(3).split(','):
            n = n.strip()
            am = re.match(r'(\w+)\s*\[\s*(\d+)\s*:\s*(\d+)\s*\]$', n)
            if am:
                mult = abs(int(am.group(2)) - int(am.group(3))) + 1
                nm = am.group(1)
            else:
                m2 = re.match(r'(\w+)', n)
                if not m2:
                    continue
                mult, nm = 1, m2.group(1)
            w[nm] = base if isinstance(base, str) else base * mult

    written = set()
    for l in stage1:
        for m in re.finditer(r'(?<![\w.])(\w+)\s*(?:\[[^;=]*?\])?\s*=(?![=<])', l):
            written.add(m.group(1))
    mentioned = set()
    for l in stage2:
        for m in re.finditer(r'(?<![\w.`])([A-Za-z_]\w*)', l):
            mentioned.add(m.group(1))

    SIM = {'chain_used', 'chain_first', 'chain_report', 'chain_hi', 'cp_seen',
           'eutrace', 'brktrace'}
    simonly = lambda n: n.startswith('trc_') or n in SIM

    cand = sorted(n for n in (written & mentioned) if n in w)
    syn = [n for n in cand if not simonly(n)]
    dropped = [n for n in cand if simonly(n)]
    unparsed = [n for n in syn if not isinstance(w[n], int)]
    total = sum(w[n] for n in syn if isinstance(w[n], int))

    print("THE CUT: v30u_eu.sv chain-loop entry (line %d); stage 1 = %d..%d, "
          "stage 2 = %d..%d (source lines, pre-expansion)"
          % (LOOP + 1, SSW + 4, LOOP, LOOP + 1, END))
    print()
    for n in syn:
        print("  %-24s %4s" % (n, w[n]))
    print()
    print("CROSSING SET (UPPER BOUND): %d bits over %d names" % (total, len(syn)))
    if unparsed:
        print("  ⚠ UNPARSED WIDTHS (excluded from the sum): %s" % unparsed)
    print("sim-only names dropped: %s" % (dropped or 'none'))
    alln = [n for n in w if n.endswith('_n') and isinstance(w[n], int)]
    print("FOR SCALE, the whole `_n` set: %d bits over %d names"
          % (sum(w[n] for n in alln), len(alln)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
