#!/usr/bin/env python3
"""WAVE 27 Z-1/Z-2 scan: v0.2 (1,000/form) vs v0.3's first 1,000 (prefix).

COMPARISON KEY: the record's own `hash` field = SHA1 of
json.dumps([name,bytes,initial,final,cycles],separators=(",",":")) -- i.e. the
WHOLE record except `idx`, which is a position label and not content.

Positive control (printed): for every position where the two hashes are EQUAL,
the two records are asserted byte-identical modulo `idx`.  If the key were not
a content key that assertion would fire.
"""
import gzip, json, hashlib, sys, os
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

V02 = Path("tests/v30/v0.2"); V03 = Path("tests/v30/v0.3")

def canon(r):
    return json.dumps([r["name"], r["bytes"], r["initial"], r["final"], r["cycles"]],
                      separators=(",", ":"))

def one(form):
    p2, p3 = V02 / f"{form}.json.gz", V03 / f"{form}.json.gz"
    out = {"form": form, "v03_present": p3.exists()}
    a = json.load(gzip.open(p2))
    out["n02"] = len(a)
    out["sha256_v02_file"] = hashlib.sha256(p2.read_bytes()).hexdigest()
    if not p3.exists():
        out["diff_idx"] = list(range(len(a))); out["absent"] = list(range(len(a)))
        out["n03"] = 0; out["key_control_bad"] = 0; out["shifted"] = []
        out["unique_records"] = [a[i] for i in range(len(a))]
        return out
    b = json.load(gzip.open(p3))
    out["n03"] = len(b)
    bh = {}
    for j, r in enumerate(b):
        bh.setdefault(r["hash"], []).append(j)
    diff, absent, shifted, badkey = [], [], [], 0
    uniq = []
    for i in range(len(a)):
        if i < len(b) and a[i]["hash"] == b[i]["hash"]:
            if canon(a[i]) != canon(b[i]):
                badkey += 1
            continue
        diff.append(i)
        uniq.append(a[i])
        j = bh.get(a[i]["hash"])
        if j is None:
            absent.append(i)
        else:
            shifted.append((i, j[0]))
    out["diff_idx"] = diff; out["absent"] = absent; out["shifted"] = shifted
    out["key_control_bad"] = badkey
    out["unique_records"] = uniq
    return out

if __name__ == "__main__":
    forms = sorted(p.name[:-8] for p in V02.glob("*.json.gz"))
    print(f"forms in v0.2: {len(forms)}", file=sys.stderr)
    res = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for i, r in enumerate(ex.map(one, forms)):
            res.append(r)
            if (i + 1) % 50 == 0:
                print(f"  ...{i+1}", file=sys.stderr)
    json.dump(res, open(os.path.expanduser("~/.cache/ucsimt-tmp/w27/scan.json"), "w"))
    tot = sum(r["n02"] for r in res)
    nd = sum(len(r["diff_idx"]) for r in res)
    na = sum(len(r["absent"]) for r in res)
    ns = sum(len(r["shifted"]) for r in res)
    bk = sum(r["key_control_bad"] for r in res)
    miss = [r["form"] for r in res if not r["v03_present"]]
    print(f"TOTAL v0.2 cases      : {tot}")
    print(f"forms missing in v0.3 : {len(miss)} {miss[:10]}")
    print(f"POSITIONAL DIFFERING  : {nd}  ({100.0*nd/tot:.4f} %)")
    print(f"  of which ABSENT from v0.3's 10,000 entirely : {na}")
    print(f"  of which PRESENT in v0.3 at another index   : {ns}")
    print(f"KEY POSITIVE CONTROL  : {bk} equal-hash pairs that are NOT byte-identical (want 0)")
    print(f"REPRODUCED positionally: {tot-nd}")
    print()
    print("per-form, forms with any difference:")
    for r in sorted(res, key=lambda r: -len(r["diff_idx"])):
        if r["diff_idx"]:
            print(f"  {r['form']:<10} diff {len(r['diff_idx']):>5}  absent {len(r['absent']):>5}  shifted {len(r['shifted']):>5}  n03 {r['n03']}")
