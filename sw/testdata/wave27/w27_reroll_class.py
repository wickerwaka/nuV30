#!/usr/bin/env python3
"""WAVE 27 (2): reroll-vs-different-draw, with a POSITIVE CONTROL.

METHOD.  `emit_suite.py` draws case i of form F from seed attempt k=0,1,2,...
in order, skipping any attempt it REROLLS; each reroll is one line of
`emit_log.txt` ("<form> case-seed <k> reroll: <reason>").  So

    out_idx -> seed_attempt  =  the ordered attempts MINUS the rerolled set.

CONTROL: v0.3 ships the true map per form (`XX.seeds.json`).  Reconstruct it
from v0.3's OWN emit_log and compare.  If the reconstruction reproduces the
committed map form for form, the same reconstruction applied to v0.2 (which
ships no map) is sound; if it does not, this instrument is refused.
"""
import json, re, sys, os, gzip
from pathlib import Path
from collections import defaultdict

V02 = Path("tests/v30/v0.2"); V03 = Path("tests/v30/v0.3")
LINE = re.compile(r"^(\S+) case-seed (\d+) reroll: (.*)$")

def rerolls(p):
    d = defaultdict(set); reasons = defaultdict(lambda: defaultdict(int))
    for ln in open(p, encoding="utf-8"):
        m = LINE.match(ln.rstrip("\n"))
        if m:
            d[m.group(1)].add(int(m.group(2)))
            reasons[m.group(1)][m.group(3)] += 1
    return d, reasons

def rebuild(bad, n):
    """out_idx -> seed attempt, for n outputs."""
    out, k = [], 0
    while len(out) < n:
        if k not in bad:
            out.append(k)
        k += 1
    return out

r3, why3 = rerolls(V03 / "emit_log.txt")
r2, why2 = rerolls(V02 / "emit_log.txt")

# ---------- POSITIVE CONTROL: reconstruct v0.3's committed maps ----------
ok = bad = nomap = 0; badforms = []
for p in sorted(V03.glob("*.seeds.json")):
    form = p.name[:-11]
    m = json.load(open(p))
    true = [s for _i, s in m["map"]]
    got = rebuild(r3.get(form, set()), len(true))
    if got == true:
        ok += 1
    else:
        bad += 1; badforms.append(form)
print(f"CONTROL: v0.3 maps reconstructed from its own emit_log: "
      f"{ok} forms EXACT, {bad} forms DIFFER {badforms[:8]}")
if bad:
    print("  -> the reconstruction is REFUSED; do not read the v0.2 column below")

# non-vacuity of the control: a form with rerolls must have a non-identity map
nontriv = sum(1 for p in V03.glob("*.seeds.json")
              if [s for _i, s in json.load(open(p))["map"]] != list(range(10000)))
print(f"CONTROL non-vacuity: {nontriv} of {len(list(V03.glob('*.seeds.json')))} "
      f"v0.3 forms have a NON-IDENTITY map (so equality is not trivial)")

# ---------- the classification ----------
scan = json.load(open(os.path.expanduser("~/.cache/ucsimt-tmp/w27/scan.json")))
cls = defaultdict(int); per_form = defaultdict(lambda: defaultdict(int))
reason_hist = defaultdict(int)
detail = {}
for r in scan:
    form = r["form"]
    if not r["absent"]:
        continue
    n2 = r["n02"]
    map2 = rebuild(r2.get(form, set()), n2)
    b3 = r3.get(form, set())
    m3p = V03 / f"{form}.seeds.json"
    used3 = set(s for _i, s in json.load(open(m3p))["map"]) if m3p.exists() else set()
    rows = []
    for i in r["absent"]:
        k = map2[i]
        if k in b3:
            c = "REJECTED_BY_v0.3"
            # which reason -- we only have per-form reason counts; record form
        elif k in used3:
            c = "SAME_SEED_DIFFERENT_RECORD"
        else:
            c = "SEED_BEYOND_v0.3_USE"
        cls[c] += 1; per_form[form][c] += 1
        rows.append((i, k, c))
    detail[form] = rows
print()
print("THE 1,237 ABSENT CASES, CLASSIFIED BY THEIR v0.2 SEED ATTEMPT:")
for c, n in sorted(cls.items(), key=lambda x: -x[1]):
    print(f"  {c:<28} {n}")
print()
for form in sorted(per_form):
    print(f"  {form:<10} " + "  ".join(f"{c}={n}" for c, n in sorted(per_form[form].items())))
print()
print("v0.3 REROLL REASONS on those forms:")
for form in sorted(per_form):
    print(f"  {form:<10} " + "; ".join(f"{k} x{v}" for k, v in sorted(why3[form].items(), key=lambda x: -x[1])))
json.dump({k: v for k, v in detail.items()},
          open(os.path.expanduser("~/.cache/ucsimt-tmp/w27/absent_cls.json"), "w"))
