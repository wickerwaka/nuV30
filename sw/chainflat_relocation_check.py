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
        `case (st_n)` exactly.

`--ref REV` names the revision the bodies are compared against; the default is
the commit that landed the flattening, so this keeps working as a standing
check long after the landing.  Exit 0 PASS / 1 a clause MISSED / 2 could-not-
run.
"""
import argparse, difflib, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)
NINE = ['S_TAKE_OPC', 'S_DECODE', 'S_DECODE2', 'S_EA_CALC', 'S_BIND',
        'S_ENTER', 'S_TAIL', 'S_TAIL_POP', 'S_INSTR_END']
STEP = 'hdl/rtl/ucore/v30u_eu_step.svh'
# the tree as it stood BEFORE the flattening: the parent of the landing commit
DEFAULT_REF = 'aba01feb07'          # WAVE 7's pre-registration, pre-hdl-edit


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
        if got != bodies[n]:
            fails.append('G-12 %s: the carved body DIFFERS from %s' % (n, a.ref))
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
        hits = [q for q, t in tree.items() if '\n'.join(bodies[n]) in t]
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
            rec.extend(bodies[st[0]])
        else:
            rec.append(l)

    def tail(x):
        return x[x.index('case (st_n)'):]
    if tail(rec) != tail(pre):
        fails.append('G-12: the reconstruction does NOT match %s' % a.ref)
        print('\n'.join(list(difflib.unified_diff(
            tail(pre), tail(rec), 'ref', 'reconstructed', lineterm=''))[:40]))
    else:
        print('\n  G-12 reconstruction from `case (st_n)` onward: IDENTICAL '
              'to %s' % a.ref)

    if fails:
        print('\nchainflat_relocation_check: **FAIL**')
        for f in fails:
            print('  - ' + f)
        return 1
    print('\nchainflat_relocation_check: PASS -- 9 arms, one copy each, '
          'byte-identical to %s, reconstruction exact' % a.ref)
    return 0


if __name__ == '__main__':
    sys.exit(main())
