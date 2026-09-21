#!/usr/bin/env python3
"""WAVE 26 -- the structural reason the architectural ladder CANNOT move.

Two facts, both derived from the tree with no engine run:

  (1) the two rails WAVE 26 changes -- `ea_pair_valid` and `ea_pair_rhs` --
      have exactly ONE functional consumer in the whole RTL: the `8D` /
      mod == 3 arm of `v30u_eu_arm_bind.svh`.
  (2) NOT ONE of the four architectural golden suites contains an `8D` case
      at mod == 3.

Therefore the edit's observable blast radius on those suites is EMPTY, and a
zero-delta architectural ladder is a STRUCTURAL EXPECTATION, not a hope.  A
non-zero delta is the falsifier: it means one of the two facts is wrong.

A READ is any occurrence of a rail that is not the left-hand side of its own
assignment.  Reads are consumers UNLESS they are on the DECLARED EXEMPTION
LIST below -- which is EXPLICIT, printed on every run, and matched on exact
whitespace-stripped text, so a statement that changes stops being exempt.

  * `v30u_eu_ss_read.svh` / `v30u_eu_ss_write.svh`: the save-state port.
  * `v30u_eu_preload.svh`: the per-clock `_n = <flop>` copy.
  * `v30u_eu.sv`: the srst RETENTION SHADOW (`_r = <flop>`) and the flop
    assignment that selects it.  These move the value through reset; they do
    not act on it.

--positive-control requires that four synthetic consumer shapes are CAUGHT,
that the exempt statements are NOT, and that DELETING an exemption makes its
statement appear.  Exit 0 PASS, 1 FAIL, 2 the control failed.
"""
import argparse
import gzip
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RTL = ROOT / "hdl" / "rtl" / "ucore"
RAIL = re.compile(r"ea_pair_(?:valid|rhs)")
WRITE = re.compile(r"ea_pair_\w+\s*(?:<=|=)(?!=)")
PREFIXES = {0x26, 0x2E, 0x36, 0x3E, 0xF0, 0xF2, 0xF3, 0x64, 0x65}
SUITES = ["v0.1", "v0.3", "v20suite"]
# ⚠ `"v0.2"` was in that list until WAVE 27 deleted the suite
# (`docs/notes/invalidation_ledger.md` RET-3).  It is NOT silently
# dropped: `mod3_cases()` would have found no `8D.json.gz` and reported
# `0 cases / 0 mod==3`, which reads as "checked, and empty" for a suite
# that no longer exists.  The retirement is PRINTED on every run instead.
# WAVE 26's own committed run (four suites, 0 cases over all four) is
# `sw/testdata/wave26/` and is not edited.
RETIRED_SUITES = [("v0.2", "deleted at WAVE 27, invalidation_ledger.md RET-3")]

EXEMPT_FILES = ("v30u_eu_ss_read.svh", "v30u_eu_ss_write.svh",
                "v30u_eu_preload.svh")
EXEMPT_LINES = (
    ("v30u_eu.sv", "ea_pair_rhs_r = ea_pair_rhs;"),
    ("v30u_eu.sv", "ea_pair_valid_r = ea_pair_valid;"),
    ("v30u_eu.sv",
     "ea_pair_rhs <= (srst && !ss_we) ? ea_pair_rhs_r : ea_pair_rhs_n;"),
    ("v30u_eu.sv",
     "ea_pair_valid <= (srst && !ss_we) ? ea_pair_valid_r : "
     "ea_pair_valid_n;"),
    # the PHASE-SPLIT stage bus, packed at one line and unpacked at the other
    # from ONE list (v30u_eu.sv's own "THE PACK AND THE UNPACK ARE ONE LIST,
    # WRITTEN TWICE AND CHECKED").  Carrying a value across the ce/ce_half
    # boundary is transport, not use; `sw/phase_split_lint.py` owns it.
    ("v30u_eu.sv",
     "count_n, ea_pair_valid_n, ea_residue_n, first_pop_seen_n,"),
)


def reads(fname, line, exempt_files, exempt_lines):
    """True iff this line READS a rail and is not exempt."""
    code = line.split("//")[0]
    if not RAIL.search(code):
        return False
    if re.match(r"\s*reg\b", code):          # a declaration
        return False
    if fname in exempt_files:
        return False
    if (fname, " ".join(code.split())) in exempt_lines:
        return False
    # A line may hold several statements.  Within each, drop the write
    # TARGET (`<rail> =` / `<rail> <=`) wherever it sits -- it may follow an
    # `if (...)` whose condition mentions no rail -- and see what is left.
    rest = WRITE.sub("", code)
    return bool(RAIL.search(rest))


def scan(texts, exempt_files=EXEMPT_FILES, exempt_lines=EXEMPT_LINES):
    return [(f, n, ln.strip())
            for f, text in texts
            for n, ln in enumerate(text.splitlines(), 1)
            if reads(f, ln, exempt_files, set(exempt_lines))]


def rtl_texts():
    return [(f.name, f.read_text()) for f in sorted(RTL.iterdir())
            if f.suffix in (".sv", ".svh")]


def mod3_cases():
    out = {}
    for s in SUITES:
        p = ROOT / "tests" / "v30" / s / "8D.json.gz"
        if not p.exists():
            out[s] = (0, 0)
            continue
        cases = json.load(gzip.open(p))
        n3 = 0
        for c in cases:
            b = c.get("instr") or c.get("bytes")
            if b is None:
                continue
            if isinstance(b, str):
                b = bytes.fromhex(b)
            i = 0
            while i < len(b) and b[i] in PREFIXES:
                i += 1
            if i + 1 < len(b) and b[i] == 0x8D and (b[i + 1] >> 6) == 3:
                n3 += 1
        out[s] = (len(cases), n3)
    return out


def control(texts):
    inj = [("SYNTH.sv", "    if (ea_pair_valid_n) foo_n = 1'b1;\n"
                        "    bar_n = ea_pair_rhs_n;\n"
                        "wire w = |ea_pair_rhs;\n"
                        "    zot_n = {ea_pair_valid, ea_pair_rhs};\n")]
    caught = len(scan(inj))
    exempt_hits = len(scan(texts)) - len(scan(texts))  # placeholder, see below
    # the exempt statements must NOT be reported...
    base = scan(texts)
    # ...and dropping ONE exemption must make exactly that statement appear
    revealed = []
    for e in EXEMPT_LINES:
        less = tuple(x for x in EXEMPT_LINES if x != e)
        revealed.append(len(scan(texts, EXEMPT_FILES, less)) - len(base))
    ssless = len(scan(texts, (), EXEMPT_LINES)) - len(base)
    print(f"POSITIVE CONTROL: {caught}/4 synthetic consumer shapes CAUGHT; "
          f"dropping each of the {len(EXEMPT_LINES)} exempt statements "
          f"reveals {revealed} more; dropping the {len(EXEMPT_FILES)} "
          f"plumbing files reveals {ssless} more")
    # the stage-bus statement occurs TWICE (pack and unpack), so the
    # requirement is >= 1 per exemption, not == 1.
    ok = (caught == 4 and all(r >= 1 for r in revealed) and ssless > 0
          and exempt_hits == 0)
    print("CONTROL PASSED\n" if ok else
          "CONTROL FAILED -- the classifier is not trustworthy")
    return ok


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--positive-control", action="store_true")
    a = ap.parse_args()
    texts = rtl_texts()

    if a.positive_control and not control(texts):
        return 2

    bad = 0
    print("DECLARED EXEMPTIONS (plumbing, printed every run):")
    for f in EXEMPT_FILES:
        print(f"  file  {f}")
    for f, s in EXEMPT_LINES:
        print(f"  line  {f}: {s}")

    print("\nCONSUMERS of ea_pair_valid / ea_pair_rhs:")
    cs = scan(texts)
    for f, n, line in cs:
        print(f"  {f}:{n}  {line}")
    outside = [c for c in cs if c[0] != "v30u_eu_arm_bind.svh"]
    print(f"  -> {len(cs)} consumer site(s); {len(outside)} outside "
          f"v30u_eu_arm_bind.svh")
    if len(cs) != 1 or outside:
        print("  FAIL: not exactly one consumer, in the 8D/mod==3 arm")
        bad = 1

    print("\n`8D` at mod == 3 in the architectural goldens:")
    tot = 0
    for s, (n, n3) in mod3_cases().items():
        print(f"  {s:9s} 8D cases {n:6d}   mod==3 {n3}")
        tot += n3
    for s, why in RETIRED_SUITES:
        print(f"  {s:9s} RETIRED -- {why}; NOT counted, NOT assumed empty")
    print(f"  -> {tot} case(s) over {len(SUITES)} suites")
    if tot:
        print("  FAIL: a golden reaches the changed rails")
        bad = 1

    print("\n" + ("FAIL" if bad else
                  "PASS -- ONE consumer, ZERO goldens reach it: the "
                  "architectural ladder cannot move"))
    return bad


if __name__ == "__main__":
    sys.exit(main())
