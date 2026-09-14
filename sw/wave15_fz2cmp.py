#!/usr/bin/env python3
"""WAVE 15 -- COMPARE TWO `fz2_replay` RESULTS **FIELD BY FIELD**.

⚠ **NEVER A DIGEST COMPUTED HERE.**  The bar is "the SCORED CONTENT is
identical", and a sha256 this file computed over a dict it also chose the key
order of proves nothing a reader can check.  So every scored field of every row
is compared by NAME and the first disagreement is printed with both values.

The build-identity fields (`tb_sys_receipt`, `tb_sys_tree`, `git`, `ts`) are
EXCLUDED BY NAME and printed, because they are REQUIRED to differ between two
different trees -- a run in which they matched would mean the two legs ran the
same binary, which is the vacuity this wave already caught once
(`fz2_replay` scored 0 seeds in a scratch worktree because
`sw/testdata/campaigns/*/captures/` is GITIGNORED).

usage:  python3 sw/wave15_fz2cmp.py BASE.json ARM.json
"""
import json
import sys

IDENTITY = ('tb_sys_receipt', 'tb_sys_tree', 'git', 'ts', 'era_report',
            'era_ok', 'tool', 'leg', 'ledger')


def main():
    b, a = (json.load(open(p)) for p in sys.argv[1:3])
    print('=== BUILD IDENTITY (REQUIRED to differ; printed, never compared) ===')
    for k in ('tb_sys_receipt', 'tb_sys_tree', 'git'):
        print(f'  {k:<16} base {str(b.get(k))[:24]}   arm {str(a.get(k))[:24]}   '
              f'{"same" if b.get(k) == a.get(k) else "DIFFER (expected)"}')
    br, ar = b.get('rows', []), a.get('rows', [])
    print(f'\n=== SCORED CONTENT ===\n  rows: base {len(br)}   arm {len(ar)}')
    if not br:
        print('  *** VACUOUS: 0 rows scored.  NOTHING MAY BE CONCLUDED. ***')
        return 4
    if len(br) != len(ar):
        print('  *** ROW COUNT DIFFERS ***')
        return 1
    keys = sorted({k for r in br for k in r})
    print(f'  fields compared, by name: {keys}')
    bad = 0
    for i, (x, y) in enumerate(zip(br, ar)):
        for k in keys:
            if x.get(k) != y.get(k):
                bad += 1
                if bad <= 10:
                    print(f'  *** row {i} seed {x.get("seed")} field {k}: '
                          f'base {x.get(k)!r}  arm {y.get(k)!r}')
    other = [k for k in b if k not in IDENTITY and k != 'rows']
    for k in other:
        if b[k] != a[k]:
            bad += 1
            print(f'  *** top-level {k} differs')
    print(f'\n=== {len(br)} rows x {len(keys)} fields: '
          f'{"IDENTICAL" if not bad else str(bad) + " DISAGREEMENT(S)"} ===')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
