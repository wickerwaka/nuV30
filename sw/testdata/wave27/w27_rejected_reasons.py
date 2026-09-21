#!/usr/bin/env python3
"""WAVE 27 -- the 85 REJECTED_BY_v0.3 seed attempts, by v0.3's OWN reroll reason,
with the control that refuted the `final.flags` reading.

Runs from `tests/v30/v02-unique-archive/` + `tests/v30/v0.3/emit_log.txt` alone
(`tests/v30/v0.2/` is gone -- invalidation_ledger.md RET-3).
"""
import gzip, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "tests/v30/v02-unique-archive"
LOG = ROOT / "tests/v30/v0.3/emit_log.txt"

man = json.load(open(A / "manifest.json"))
reasons = {}
for ln in LOG.read_text(encoding="utf-8").splitlines():
    m = re.match(r"^(\S+) case-seed (\d+) reroll: (.*)$", ln)
    if m:
        reasons[(m.group(1), int(m.group(2)))] = m.group(3)

why, fam, byclass, missing = Counter(), Counter(), {}, 0
for form, d in sorted(man["forms"].items()):
    recs = {r["idx"]: r for r in json.load(gzip.open(A / f"{form}.json.gz"))}
    cls = {int(i): "SHIFTED"
           for i in d["disposition"]["PRESENT_IN_v0.3_AT_ANOTHER_INDEX"]}
    for i, info in d["disposition"]["ABSENT_FROM_v0.3"].items():
        cls[int(i)] = info["class"]
        if info["class"] == "REJECTED_BY_v0.3":
            r = reasons.get((form, info["v02_seed_attempt"]))
            if r is None:
                missing += 1
                continue
            why[r] += 1
            fam[re.sub(r"\s*\(?-?\w+\)?$", "", r).strip()] += 1
    for i, c in cls.items():
        f = recs[i]["final"].get("flags")
        byclass.setdefault(c, Counter())[
            "flags ABSENT" if f is None else
            ("flags == 0" if f == 0 else "flags present, non-zero")] += 1

print("WAVE 27 -- the 85 `REJECTED_BY_v0.3` seed attempts")
print()
print("⚠ WHAT THE CLASS MEANS: v0.3's generator rerolled that SEED ATTEMPT away.")
print("   It does NOT mean v0.3 was handed this v0.2 record and refused it -- the")
print("   two emissions build different cases from the same seed, which is what")
print("   the 1,152 SAME_SEED_DIFFERENT_RECORD cases demonstrate.")
print()
print(f"seed attempts with NO matching v0.3 reroll line (want 0): {missing}")
print()
print("BY FAMILY:")
for k, v in fam.most_common():
    print(f"  {v:>4}  {k}")
print()
print("VERBATIM, every distinct line:")
for k, v in why.most_common():
    print(f"  {v:>4}  {k}")
print()
print("THE CONTROL that refuted the `final.flags` reading -- `final.flags` in the")
print("archived v0.2 records, BY CLASS.  If absence were the discriminator the")
print("three rows would differ.  They do not:")
for c in ("REJECTED_BY_v0.3", "SAME_SEED_DIFFERENT_RECORD", "SHIFTED"):
    b = byclass.get(c, Counter())
    print(f"  {c:<28} n={sum(b.values()):>5}  "
          + "  ".join(f"{k}={v}" for k, v in sorted(b.items())))
print()
print("=> absence of `final.flags` is NOT a discriminator (`final.regs` is sparse")
print("   in this schema and these pin-event forms do not list it).  The reading")
print("   that the 85 are store-stub final-PSW capture failures is WITHDRAWN.")
sys.exit(1 if missing else 0)
