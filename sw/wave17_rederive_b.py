#!/usr/bin/env python3
"""WAVE 17 -- re-derive the ONE hunk of edit (b) `5cf3254104` whose TRAILING
CONTEXT is broken by ARM-A (`f174e1a24a`), which inserted the `q_ripe_lead_n`
select between `assign q_pop = q_demand;` and `assign q_first = ...`.

The hunk's CHANGE is untouched (`retire_ok_n && !bnd_fire` ->
`s1w_retire_ok_n && !s1w_bnd_fire`).  Only the trailing context is TRIMMED, by
dropping context lines from the END of the hunk and decrementing both line
counts.  Nothing else in the patch is altered -- proved by diffing the rewritten
patch against the original.
"""
import re, sys

src, dst = sys.argv[1], sys.argv[2]
lines = open(src).read().split('\n')
out = []
i = 0
n_rewritten = 0
TRIP = 'assign q_first = (st == S_OPC_POP) ? pop_is_first'
while i < len(lines):
    ln = lines[i]
    m = re.match(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@(.*)$', ln)
    if not m:
        out.append(ln); i += 1; continue
    # collect the hunk body
    a0, an, b0, bn, tail = int(m[1]), int(m[2]), int(m[3]), int(m[4]), m[5]
    body = []
    j = i + 1
    ca = cb = 0
    while j < len(lines) and (ca < an or cb < bn):
        bl = lines[j]
        if bl.startswith('-'):   ca += 1
        elif bl.startswith('+'): cb += 1
        elif bl.startswith(' ') or bl == '': ca += 1; cb += 1
        elif bl.startswith('\\'): pass
        else: break
        body.append(bl); j += 1
    if any(TRIP in b for b in body) and any('s1w_retire_ok_n' in b for b in body):
        # trim trailing pure-context lines up to and including the TRIP line
        while body and (body[-1].startswith(' ') or body[-1] == ''):
            popped = body.pop(); an -= 1; bn -= 1
            if TRIP in popped:
                break
        n_rewritten += 1
        out.append('@@ -%d,%d +%d,%d @@%s' % (a0, an, b0, bn, tail))
    else:
        out.append(ln)
    out.extend(body)
    i = j

assert n_rewritten == 1, 'expected exactly 1 rewritten hunk, got %d' % n_rewritten
open(dst, 'w').write('\n'.join(out))
print('rewrote %d hunk(s)' % n_rewritten)
