#!/usr/bin/env python3
"""WAVE 28 / FLASH #24 -- ladder zero-delta check against WAVE 27.

Compares, leg by leg: the exit code, and the leg's SCORED LINES (the lines a
reader would quote -- TOTAL / PASS / FAIL / counts), with Verilator build
chatter, absolute paths, receipts and timings stripped, because those move
between runs for reasons that are not the ladder.

  SAME     the leg exists on both sides and its scored lines are identical
  MOVED    it exists on both sides and they are not
  GONE     WAVE 27 had it, WAVE 28 does not     (expected: NONE -- this wave edits no hdl/)
  NEW      WAVE 28 has it, WAVE 27 did not      (expected: NONE)
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A = ROOT / "sw/testdata/wave27/ladder"
B = ROOT / "sw/testdata/wave28/ladder"

SCORED = re.compile(
    r"(TOTAL|PASS|FAIL|MATCH|OK\b|REFUSED|: PASS|: FAIL|/\d|\d+ */ *\d+"
    r"|checks|flops|members|violation|entries|rows|REPLAY|LOCKSTEP)", re.I)
NOISE = re.compile(
    r"(verilator|%Warning|%Error|obj_dir|/home/|receipt|\breal\b|\buser\b|\bsys\b"
    r"|artifact:|staging|Timescale|elapsed|seconds|\.staging\.)", re.I)


def scored(p):
    if not p.exists():
        return None
    out = []
    for ln in p.read_text(errors="replace").splitlines():
        s = ln.rstrip()
        if not s or NOISE.search(s) or not SCORED.search(s):
            continue
        out.append(s)
    return out


def rcs(d):
    r = {}
    f = d / "rc.txt"
    if not f.exists():
        return r
    for ln in f.read_text().splitlines():
        m = re.match(r"^(\S+) RC=(\d+)", ln)
        if m:
            r[m.group(1)] = int(m.group(2))
    return r


ra, rb = rcs(A), rcs(B)
names = sorted(set(ra) | set(rb))
same = moved = 0
rows = []
for n in names:
    if n not in rb:
        rows.append(("GONE", n, f"WAVE 27 RC={ra[n]}"))
        continue
    if n not in ra:
        rows.append(("NEW", n, f"WAVE 28 RC={rb[n]}"))
        continue
    sa, sb = scored(A / f"{n}.log"), scored(B / f"{n}.log")
    if ra[n] == rb[n] and sa == sb:
        same += 1
        rows.append(("SAME", n, f"RC={rb[n]}, {len(sb)} scored line(s)"))
    else:
        moved += 1
        d = [(x, y) for x, y in zip(sa or [], sb or []) if x != y][:3]
        rows.append(("MOVED", n, f"RC {ra[n]}->{rb[n]}; "
                                 f"{abs(len(sa or []) - len(sb or []))} line-count delta; "
                                 f"first diffs {d}"))
for k, n, d in rows:
    print(f"  {k:<6} {n:<14} {d}")
print()
print(f"SAME {same} · MOVED {moved} · "
      f"GONE {sum(1 for k, _, _ in rows if k == 'GONE')} · "
      f"NEW {sum(1 for k, _, _ in rows if k == 'NEW')}")
sys.exit(1 if moved else 0)
