#!/usr/bin/env python3
"""WAVE 7 -- G-11 / G-12: THE CHAIN FLATTENING'S RELOCATION FALSIFIER.

The landing moved the nine chainable arm bodies out of `v30u_eu_step.svh` into
one `v30u_eu_arm_<state>.svh` each, so that chain POSITION 0 (the 33-arm case)
and the flattened POSITIONS >= 1 can share ONE copy of every body.  Two things
have to stay true of that and neither is self-evident from reading the files:

  G-11  each of the nine bodies exists in `hdl/` EXACTLY ONCE.  WAVE 6's
        prototype generator left the originals in the step file, so the
        prototype tree carried two copies of each; a landing may not.
  G-12  each body is BYTE-IDENTICAL to its pre-edit text -- RELOCATED, never
        rewritten -- and inlining the includes back reconstructs the pre-edit
        `case (st_n)` exactly, EXCEPT where a later wave has DECLARED a
        deviation below.

⚠ WAVE 26, 2026-09-20 -- WHY `DEVIATION` EXISTS AND WHY IT IS A PIN AND NOT A
HOLE.  As first written, G-12 froze the EU's whole `case (st_n)` at the
pre-flattening tree, so the FIRST later wave to change any arm -- WAVE 26's
one-mux `ea_pair_rhs` fix -- turned a standing gate permanently RED with no
way forward.  That was NOT foreseen and is reported as an unregistered miss in
`docs/notes/ea_qualifier_results_2026-09-20.md`.

The repair keeps the falsifier live rather than widening it:

  * G-11 is UNCHANGED IN MEANING and now derives the nine bodies from the
    CURRENT arm files, so "exactly one copy in hdl/" keeps being checked
    however the bodies evolve.  It never needed the frozen reference.
  * G-12 still diffs the reconstruction against the frozen reference.  What
    changed is that a deviation is allowed only if it is DECLARED here and
    matches `DEVIATION['digest']` -- the sha256 of the unified diff itself.
    **One further edited character anywhere in the EU's `case (st_n)` moves
    that digest and the gate FAILS**, so the pin is as strict as the old
    equality for everything except the exact, recorded text a wave landed.
  * A declaration that is NOT in force is also a FAIL ("stale declaration"),
    so the entry cannot be left behind to excuse a future tree.

`--ref REV` names the revision the bodies are compared against; the default is
the commit that landed the flattening.  `--positive-control` perturbs a body
in memory and requires the digest to move.  Exit 0 PASS / 1 a clause MISSED /
2 could-not-run.
"""
import argparse, difflib, hashlib, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
NINE = ['S_TAKE_OPC', 'S_DECODE', 'S_DECODE2', 'S_EA_CALC', 'S_BIND',
        'S_ENTER', 'S_TAIL', 'S_TAIL_POP', 'S_INSTR_END']
STEP = 'hdl/rtl/ucore/v30u_eu_step.svh'
# the tree as it stood BEFORE the flattening: the parent of the landing commit
DEFAULT_REF = 'aba01feb07'          # WAVE 7's pre-registration, pre-hdl-edit

# THE DECLARED DEVIATION.  `digest` is sha256 of the unified diff between the
# reference's `case (st_n)` onward and the reconstruction from the CURRENT
# bodies.  Set `digest` to None when the tree is expected to match the
# reference exactly.
DEVIATION = {
    'digest': 'abb6954fe1a73655dddc57931f2b23bfb6694941c9df3eba94f391b26eaae503',
    'wave': 'WAVE 26, 2026-09-20',
    'arms': ['S_EA_CALC', 'S_BIND'],
    'step_file_too': True,
    'reason': ("the retained EA lane takes the address adder's SECOND ADDEND "
               "on every EA calculation (one mux in S_EA_CALC); the S_BIND and "
               "S_ROW hunks are COMMENT-ONLY and carry the sentences silicon "
               "refuted.  docs/notes/ea_qualifier_results_2026-09-20.md"),
    'code_hunks': 1,
}


def fname(s):
    return 'v30u_eu_arm_' + s[2:].lower() + '.svh'


def arm_bodies(lines):
    """{state: body between `S_X: begin` and its closing `end`}"""
    starts = []
    for i, l in enumerate(lines):
        m = re.match(r'^(S_[A-Z0-9_]+|default):', l)
        if m:
            starts.append((i, m.group(1)))
    starts.append((len(lines), None))
    out = {}
    for k in range(len(starts) - 1):
        i, n = starts[k]
        if n not in NINE:
            continue
        j = starts[k + 1][0]
        close = [x for x in range(i + 1, j) if lines[x] == 'end']
        if not close:
            sys.exit('could not find %s\'s closing `end`' % n)
        out[n] = lines[i + 1:max(close)]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default=DEFAULT_REF,
                    help='revision holding the PRE-flattening step file')
    ap.add_argument('--positive-control', action='store_true',
                    help='perturb a body in memory; the digest must move')
    a = ap.parse_args()
    p = subprocess.run(['git', 'show', '%s:%s' % (a.ref, STEP)],
                       capture_output=True, text=True)
    if p.returncode:
        print('cannot read %s:%s -- %s' % (a.ref, STEP, p.stderr.strip()),
              file=sys.stderr)
        return 2
    pre = p.stdout.split('\n')
    bodies = arm_bodies(pre)
    if len(bodies) != 9:
        print('the reference has %d of the nine arms, not 9' % len(bodies),
              file=sys.stderr)
        return 2

    fails = []
    cur = {}
    for n in NINE:
        f = os.path.join('hdl/rtl/ucore', fname(n))
        if not os.path.exists(f):
            fails.append('G-12 %s: %s is missing' % (n, f))
            continue
        txt = open(f).read().split('\n')
        hdr = max(i for i, l in enumerate(txt) if l.startswith('//===='))
        got = txt[hdr + 1:]
        while got and got[-1] == '':
            got.pop()
        cur[n] = got
        if got != bodies[n]:
            if n in DEVIATION['arms']:
                print('  G-12 %-13s DEVIATES BY DECLARATION (%s), %3d lines'
                      % (n, DEVIATION['wave'], len(got)))
            else:
                fails.append('G-12 %s: the carved body DIFFERS from %s and is '
                             'NOT a declared deviation' % (n, a.ref))
                print('\n'.join(list(difflib.unified_diff(
                    bodies[n], got, 'ref', 'carved', lineterm=''))[:30]))
        else:
            print('  G-12 %-13s relocated byte-identical, %3d lines'
                  % (n, len(got)))

    tree = {}
    for root, _, fs in os.walk('hdl'):
        for f in fs:
            if f.endswith(('.sv', '.svh')):
                q = os.path.join(root, f)
                tree[q] = open(q, errors='replace').read()
    print()
    for n in NINE:
        hits = [q for q, t in tree.items() if '\n'.join(cur[n]) in t]
        if len(hits) != 1:
            fails.append('G-11 %s: %d copies in hdl/ -- %s'
                         % (n, len(hits), hits))
        else:
            print('  G-11 %-13s exactly one copy: %s' % (n, hits[0]))

    now = open(STEP).read().split('\n')
    rec = []
    for l in now:
        m = re.match(r'^\s*`include "(v30u_eu_arm_\w+\.svh)"$', l)
        if m:
            st = [x for x in NINE if fname(x) == m.group(1)]
            if not st:
                fails.append('unknown arm include: ' + m.group(1))
                continue
            rec.extend(cur[st[0]])
        else:
            rec.append(l)

    def tail(x):
        return x[x.index('case (st_n)'):]

    def deviation_digest(reconstruction):
        d = '\n'.join(difflib.unified_diff(
            tail(pre), tail(reconstruction), a.ref, 'reconstructed',
            lineterm=''))
        return (hashlib.sha256(d.encode()).hexdigest() if d else None), d

    dig, dtext = deviation_digest(rec)
    print()
    if DEVIATION['digest'] is None:
        if dig is None:
            print('  G-12 reconstruction from `case (st_n)` onward: IDENTICAL '
                  'to %s, and NO deviation is declared' % a.ref)
        else:
            fails.append('G-12: the reconstruction does NOT match %s and no '
                         'deviation is declared' % a.ref)
            print('\n'.join(dtext.split('\n')[:40]))
    elif dig is None:
        fails.append('G-12: a deviation is DECLARED (%s) but the tree matches '
                     '%s exactly -- STALE DECLARATION, remove it'
                     % (DEVIATION['wave'], a.ref))
    elif dig == DEVIATION['digest']:
        print('  G-12 DECLARED DEVIATION IN FORCE, digest %s…' % dig[:16])
        print('       %s -- arms %s%s, %d code hunk(s)'
              % (DEVIATION['wave'], ', '.join(DEVIATION['arms']),
                 ' + the step file itself' if DEVIATION['step_file_too']
                 else '', DEVIATION['code_hunks']))
        print('       %s' % DEVIATION['reason'])
        print('       EVERYTHING ELSE from `case (st_n)` onward is byte-'
              'identical to %s.' % a.ref)
    else:
        fails.append('G-12: the reconstruction deviates from %s by something '
                     'OTHER than the declared deviation (digest %s…, declared '
                     '%s…)' % (a.ref, dig[:16], DEVIATION['digest'][:16]))
        print('\n'.join(dtext.split('\n')[:60]))

    if a.positive_control:
        bad = dict(cur)
        bad['S_ENTER'] = bad['S_ENTER'] + ['    // synthetic perturbation']
        rec2 = []
        for l in now:
            m = re.match(r'^\s*`include "(v30u_eu_arm_\w+\.svh)"$', l)
            if m:
                st = [x for x in NINE if fname(x) == m.group(1)][0]
                rec2.extend(bad[st])
            else:
                rec2.append(l)
        d2, _ = deviation_digest(rec2)
        ok = (d2 is not None and d2 != dig)
        print('\n  POSITIVE CONTROL: one synthetic line in S_ENTER moves the '
              'digest %s…  ->  %s…   %s'
              % ((dig or 'none')[:12], (d2 or 'none')[:12],
                 'CAUGHT' if ok else 'NOT CAUGHT'))
        if not ok:
            fails.append('POSITIVE CONTROL FAILED: the digest does not move')

    if fails:
        print('\nchainflat_relocation_check: **FAIL**')
        for f in fails:
            print('  - ' + f)
        return 1
    if DEVIATION['digest'] is None:
        print('\nchainflat_relocation_check: PASS -- 9 arms, one copy each, '
              'byte-identical to %s, reconstruction exact' % a.ref)
    else:
        print('\nchainflat_relocation_check: PASS -- 9 arms, one copy each, '
              '%d byte-identical to %s, %d DECLARED DEVIATION(S) pinned by '
              'digest' % (9 - len(DEVIATION['arms']), a.ref,
                          len(DEVIATION['arms'])))
    return 0


if __name__ == '__main__':
    sys.exit(main())
