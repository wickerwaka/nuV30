#!/usr/bin/env python3
"""WAVE 13 / N-5 -- compare two `fz2_replay --out` reports FIELD BY FIELD.

The brief is explicit: *compare the named fields directly, NOT a digest you
computed yourself.*  `sw/phase_split_replay_sha.py` is the repo's registered
instrument and is run beside this one, but a sha256 of a re-serialised payload
is a number this wave computed; a per-field comparison is the artifact.

SCORED CONTENT is `rows` and `tables` -- the same two keys the registered
instrument hashes.  IDENTITY (`tb_sys_receipt`, `tb_sys_tree`, `git`,
`era_report`, `era_ok`) and RUN metadata (`ts`) are printed and NOT scored: a
Verilator receipt moves across rebuilds of a byte-identical tree, so its
movement proves nothing in either direction.

  usage: wave13_replay_fieldcmp.py A.json B.json [--selftest]

`--selftest` is the POSITIVE CONTROL: it perturbs ONE field of ONE row of a
copy of A and requires this comparator to report the difference, naming the row
and the field.  A comparator that has not been shown able to say DIFFERS may
not be quoted when it says IDENTICAL.
"""
import json, sys, copy

SCORED = ("rows", "tables")
IDENTITY = ("tb_sys_receipt", "tb_sys_tree", "git", "era_report", "era_ok")


def keyof(r):
    for k in ("seed", "bank_seed", "name", "id"):
        if k in r:
            return f"{k}={r[k]}"
    return "?"


def cmp_rows(a, b, diffs):
    if len(a) != len(b):
        diffs.append(f"rows: LENGTH {len(a)} vs {len(b)}")
        return
    for i, (x, y) in enumerate(zip(a, b)):
        if x == y:
            continue
        ks = set(x) | set(y)
        for k in sorted(ks):
            if x.get(k, "<absent>") != y.get(k, "<absent>"):
                diffs.append(f"rows[{i}] ({keyof(x)}) field {k!r}: "
                             f"{x.get(k, '<absent>')!r} vs {y.get(k, '<absent>')!r}")


def compare(A, B, label_a, label_b):
    diffs = []
    for key in SCORED:
        if key not in A or key not in B:
            diffs.append(f"{key}: MISSING ({key in A}/{key in B})")
            continue
        if key == "rows":
            cmp_rows(A[key], B[key], diffs)
        elif A[key] != B[key]:
            diffs.append(f"{key}: DIFFERS")
            ka, kb = A[key], B[key]
            if isinstance(ka, dict) and isinstance(kb, dict):
                for k in sorted(set(ka) | set(kb)):
                    if ka.get(k) != kb.get(k):
                        diffs.append(f"  tables[{k!r}]: {ka.get(k)!r} vs {kb.get(k)!r}")
    print(f"A {label_a}")
    print(f"B {label_b}")
    print(f"  rows      A {len(A.get('rows', []))}   B {len(B.get('rows', []))}")
    print(f"  tables    A {len(A.get('tables', {}))} keys   B {len(B.get('tables', {}))} keys")
    for k in IDENTITY:
        va, vb = str(A.get(k))[:24], str(B.get(k))[:24]
        print(f"  [identity, NOT scored] {k:16s} A {va:26s} B {vb}")
    if diffs:
        print(f"\n*** SCORED CONTENT DIFFERS -- {len(diffs)} difference(s) ***")
        for d in diffs[:40]:
            print("   " + d)
        if len(diffs) > 40:
            print(f"   … and {len(diffs) - 40} more")
        return 1
    print("\nSCORED CONTENT IDENTICAL -- every row and every table entry, "
          "compared field by field")
    return 0


def main():
    a, b = sys.argv[1], sys.argv[2]
    A, B = json.loads(open(a).read()), json.loads(open(b).read())
    rc = compare(A, B, a, b)
    if "--selftest" in sys.argv:
        print("\n" + "=" * 70)
        print("POSITIVE CONTROL -- perturb ONE field of ONE row of a copy of A")
        C = copy.deepcopy(A)
        if not C.get("rows"):
            print("*** no rows to perturb -- CONTROL CANNOT RUN ***")
            return 2
        row = C["rows"][0]
        fld = sorted(row)[0]
        old = row[fld]
        row[fld] = "WAVE13-CONTROL-PERTURBATION"
        rc2 = compare(A, C, a, a + " [perturbed rows[0]." + fld + "]")
        if rc2 == 0:
            print("*** CONTROL FAILED: the comparator could not say DIFFERS. "
                  "Its IDENTICAL verdict above is NOT quotable. ***")
            return 2
        print(f"CONTROL PASSED -- the comparator named rows[0].{fld} "
              f"(was {old!r}).  It is able to say DIFFERS.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
