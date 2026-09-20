"""Is `neither` the emitter ERA, not the case?  Two offline legs."""
import sys, gzip, json
sys.path.insert(0,'/home/wickerwaka/src/nec_test/sw')
import emit_suite as es, suitemeta
from pathlib import Path
OUT = Path('/home/wickerwaka/src/nec_test/tests/v30/v0.3')
ARCH = Path('/home/wickerwaka/src/nec_test/sw/testdata/wave24/void-archive')
meta = suitemeta.load(OUT, delegate_to=es.DEFAULT_OUT)

print("LEG 1 -- _flat_mirror_check on BANKED cases (no board):")
tot = {}
for op, n in [("88", 6), ("01", 6), ("8B", 6)]:
    cases = json.load(gzip.open(OUT / f"{op}.json.gz"))
    fm = meta.flags_mask(op)
    for c in cases[:n]:
        d = es._flat_mirror_check(c, fm)
        tot[d] = tot.get(d, 0) + 1
print("   ", tot)

print("\nLEG 2 -- the ERA SIGNATURE in the artifacts themselves.")
def sig(cases):
    cc = n90 = 0
    for c in cases:
        b = list(c['initial']['queue']) + [v for _, v in c['initial']['ram']]
        if 0xCC in b: cc += 1
        if 0x90 in b: n90 += 1
    return cc, n90, len(cases)
for op in ("88", "01", "8B", "0F1B", "83.5"):
    cases = json.load(gzip.open(OUT / f"{op}.json.gz"))
    cc, n90, n = sig(cases)
    print(f"    banked {op:6s}: cases with a 0xCC byte {cc:5d} / {n}   with a 0x90 byte {n90:5d} / {n}")
for f, i in (("0F1B", 3917), ("83.5", 8683)):
    new = [t for t in json.load(gzip.open(OUT / f"{f}.json.gz")) if t['idx'] == i]
    old = [t for t in json.load(gzip.open(ARCH / f"{f}.json.gz.orig")) if t['idx'] == i]
    print(f"    {f}/{i}  OLD(banked 2026-07) {sig(old)}   NEW(captured today) {sig(new)}")
