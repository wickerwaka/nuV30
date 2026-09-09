#!/usr/bin/env python3
"""WAVE 5 (THE CHAIN ANATOMY) -- THE SOURCE-DERIVED ARM MAP.

MEASUREMENT ONLY.  It reads `hdl/rtl/ucore/v30u_eu_step.svh` (and the files it
includes) and answers, for a signal name, WHICH CASE ARMS OF THE CHAIN STEP
WRITE IT.  Q3 needs that map: a netlist node named `opc_base~48` is only
attributable to an RTL arm if something says which arms write `opc_base`.

It also answers the IN-CHAIN / PRE-CHAIN question a netlist name cannot: a
signal assigned ONLY inside the step include is produced by the unrolled chain
and exists once per position; a signal assigned only in `v30u_eu.sv`'s own
combinational blocks is FRONT END and exists once.

⚠ IT IS A TEXT PARSER, NOT AN ELABORATOR, and it says so.  Its answer is a SET
of arms, never a single one, and a name written by several arms is reported as
AMBIGUOUS rather than assigned to the first.

=== THE POSITIVE CONTROL, AND IT IS THE WHOLE REASON TO TRUST THIS FILE ===
The parser must independently recover a partition the SOURCE states in prose and
`v30u_eu.sv` states in code, WITHOUT being told either:

  (1) exactly 33 state arms plus `default`;
  (2) exactly 24 of them carry `if (chain == 4'd0)` and 9 do not;
  (3) the 9 unguarded arm names are EXACTLY the 9 states `st_zero_ok()` in
      `hdl/rtl/ucore/v30u_eu.sv` returns true for -- parsed from THAT file,
      separately.

If (1)(2)(3) hold the parser has understood the file's structure.  If any fails
the map is REFUSED (exit 3) and nothing downstream may quote it.  `--control`
runs only that.
"""
import argparse, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
UC = os.path.join(ROOT, 'hdl/rtl/ucore')
STEP = 'v30u_eu_step.svh'
EU = 'v30u_eu.sv'

ARM_RE = re.compile(r'^(S_[A-Z0-9_]+):')
GUARD_RE = re.compile(r"^S_[A-Z0-9_]+:\s*if\s*\(\s*chain\s*==\s*4'd0\s*\)")
INC_RE = re.compile(r'^\s*`include\s+"([^"]+)"')
# an assignment target: `name` or `name[...]` at the head of a statement
ASSIGN_RE = re.compile(r'(?:^|[;\)]\s*|\bbegin\b\s*|\belse\b\s*|\bdo\b\s*)'
                       r'([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]=]*\])?\s*(?:<?=)(?!=)')


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return '\n'.join(l.split('//')[0] for l in text.split('\n'))


def read(fn):
    return open(os.path.join(UC, fn)).read()


def expand(fn, seen=None):
    """Return the file's text with `include`s spliced in (comments stripped)."""
    seen = seen or set()
    if fn in seen:
        return ''
    seen = seen | {fn}
    out = []
    for line in strip_comments(read(fn)).split('\n'):
        m = INC_RE.match(line)
        if m and os.path.exists(os.path.join(UC, m.group(1))):
            out.append(expand(m.group(1), seen))
        else:
            out.append(line)
    return '\n'.join(out)


def targets(text):
    """Every identifier that appears as an assignment TARGET in `text`."""
    return {m.group(1) for m in ASSIGN_RE.finditer(text)}


def parse_arms():
    """{arm_name: {'guarded': bool, 'text': str}} over the step include.

    Arms start at COLUMN 0 in this file (checked), so the split is exact and
    needs no begin/end depth tracking."""
    raw = strip_comments(read(STEP)).split('\n')
    arms, cur, buf, guarded = {}, None, [], {}
    for line in raw:
        m = ARM_RE.match(line) or (re.match(r'^(default):', line) and
                                   re.match(r'^(default):', line))
        if m:
            if cur:
                arms[cur] = '\n'.join(buf)
            cur = m.group(1)
            guarded[cur] = bool(GUARD_RE.match(line))
            buf = [line]
        elif cur:
            buf.append(line)
    if cur:
        arms[cur] = '\n'.join(buf)
    # splice includes per arm
    for a in list(arms):
        out = []
        for line in arms[a].split('\n'):
            m = INC_RE.match(line)
            if m and os.path.exists(os.path.join(UC, m.group(1))):
                out.append(expand(m.group(1)))
            else:
                out.append(line)
        arms[a] = '\n'.join(out)
    return arms, guarded


def st_zero_ok_states():
    """The 9 names `st_zero_ok()` returns true for, parsed from v30u_eu.sv."""
    t = strip_comments(open(os.path.join(UC, EU)).read())
    m = re.search(r'function\s+automatic\s+logic\s+st_zero_ok.*?endfunction', t, re.S)
    if not m:
        return set()
    return set(re.findall(r'\bS_[A-Z0-9_]+\b', m.group(0)))


def build():
    arms, guarded = parse_arms()
    states = {a for a in arms if a != 'default'}
    zok = st_zero_ok_states()
    unguarded = {a for a in states if not guarded[a]}
    ctl = {
        'n_arms': len(states),
        'n_guarded': sum(1 for a in states if guarded[a]),
        'n_unguarded': len(unguarded),
        'zok': sorted(zok),
        'unguarded': sorted(unguarded),
        'match': unguarded == zok,
    }
    ok = (ctl['n_arms'] == 33 and ctl['n_guarded'] == 24 and
          ctl['n_unguarded'] == 9 and ctl['match'])
    ctl['PASS'] = ok
    sig2arms = {}
    for a in states:
        for t in targets(arms[a]):
            sig2arms.setdefault(t, set()).add(a)
    # PRE-CHAIN: assigned in v30u_eu.sv outside the step include's cone
    eu_txt = strip_comments(open(os.path.join(UC, EU)).read())
    eu_assigned = targets(eu_txt)
    chain_assigned = set(sig2arms)
    return ctl, sig2arms, chain_assigned, eu_assigned, unguarded


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--control', action='store_true', help='run only the positive control')
    ap.add_argument('--dump', metavar='FILE', default=None)
    ap.add_argument('--query', nargs='*', default=None)
    a = ap.parse_args()
    ctl, s2a, chain_assigned, eu_assigned, unguarded = build()
    print("=== chain_srcmap POSITIVE CONTROL (gates every use of this map) ===")
    print(f"  state arms parsed              : {ctl['n_arms']}   (must be 33)")
    print(f"  arms carrying `chain == 4'd0`  : {ctl['n_guarded']}   (must be 24)")
    print(f"  arms WITHOUT the guard         : {ctl['n_unguarded']}   (must be 9)")
    print(f"  st_zero_ok() states, parsed from {EU} : {len(ctl['zok'])}")
    print(f"  unguarded set == st_zero_ok set: {ctl['match']}")
    print(f"    unguarded : {' '.join(ctl['unguarded'])}")
    print(f"    st_zero_ok: {' '.join(ctl['zok'])}")
    print(f"  CONTROL: {'PASS' if ctl['PASS'] else 'FAIL'}")
    if not ctl['PASS']:
        print("REFUSING: the parser did not recover the file's own structure.")
        return 3
    if a.control:
        return 0
    chain_only = sorted(chain_assigned - eu_assigned)
    both = sorted(chain_assigned & eu_assigned)
    print(f"\n  signals assigned inside the chain step : {len(chain_assigned)}")
    print(f"    ...of which NEVER assigned elsewhere in {EU} : {len(chain_only)}")
    print(f"    ...also assigned in {EU} outside it          : {len(both)}")
    if a.query:
        print()
        for q in a.query:
            arms = sorted(s2a.get(q, []))
            kind = ('IN-CHAIN-ONLY' if q in chain_assigned and q not in eu_assigned
                    else 'CHAIN+MODULE' if q in chain_assigned
                    else 'PRE/POST-CHAIN' if q in eu_assigned else 'NOT-ASSIGNED')
            n = len(arms)
            lab = 'UNIQUE' if n == 1 else ('AMBIGUOUS(%d)' % n if n else '-')
            print(f"  {q:22s} {kind:15s} {lab:14s} {' '.join(arms)}")
    if a.dump:
        import json
        json.dump({'control': ctl,
                   'sig2arms': {k: sorted(v) for k, v in s2a.items()},
                   'chain_assigned': sorted(chain_assigned),
                   'eu_assigned': sorted(eu_assigned)},
                  open(a.dump, 'w'), indent=1)
        print(f"\n  map written to {a.dump}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
