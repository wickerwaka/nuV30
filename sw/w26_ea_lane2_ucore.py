#!/usr/bin/env python3
"""WAVE 26 -- the ucore leg of `sw/w26_ea_lane2.py`.

Whole-program replay from RESET through `sw/tb_bootrun.py`'s `+bootimg` mode,
no backdoor injection, via WAVE 23's `lea_mod3_gate.Runner` -- the same
instrument that took WAVE 23's and WAVE 24's ucore columns.

With `--capture <dir>` it diffs against a socket capture; without one it
prints the ucore's own column, which is what the wave REGISTERS as its point
prediction BEFORE the board is touched.
"""
import argparse
import gzip
import json
import sys
import tempfile
from pathlib import Path

SW = Path(__file__).resolve().parent
sys.path.insert(0, str(SW))
from lea_mod3_gate import Runner                             # noqa: E402
from w26_ea_lane2 import PROBES, LEA, REGS                   # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--capture", default=None,
                    help="a directory holding 8D.json.gz from the socket rig")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    silicon = {}
    if a.capture:
        for t in json.load(gzip.open(Path(a.capture) / "8D.json.gz")):
            silicon[t["b2_tag"]] = t["final"]["regs"].get("si", REGS["si"])

    rows = []
    with tempfile.TemporaryDirectory(dir=str(Path.home() / ".cache" /
                                             "ucsimt-tmp")) as td:
        r = Runner(td)
        for tag, pre, prose, ea, pred in PROBES:
            d = r.dump(pre + LEA)
            rows.append((tag, prose, " ".join(f"{b:02x}" for b in pre), ea,
                         pred, silicon.get(tag), d["IX"]))

    print("%-4s %-14s %-22s %6s %6s %8s %7s  %s" % (
        "tag", "predecessor", "prose", "EA", "pred", "SILICON", "ucore",
        "verdict"))
    agree = differ = nosil = 0
    out = []
    for tag, prose, pb, ea, pred, si, uc in rows:
        if si is None:
            v = "NO-SILICON"
            nosil += 1
        elif si == uc:
            v = "MATCH"
            agree += 1
        else:
            v = "DIVERGE"
            differ += 1
        pv = "" if pred is None else ("  pred=%s" % ("HIT" if pred == uc
                                                     else "MISS"))
        print("%-4s %-14s %-22s %6s %6s %8s %7s  %s%s" % (
            tag, pb, prose,
            "-" if ea is None else "%04x" % ea,
            "-" if pred is None else "%04x" % pred,
            "-" if si is None else "%04x" % si, "%04x" % uc, v, pv))
        out.append({"tag": tag, "pre_bytes": pb, "prose": prose, "ea": ea,
                    "predicted_si": pred, "silicon_si": si, "ucore_si": uc,
                    "verdict": v})
    if a.json:
        Path(a.json).write_text(json.dumps(
            {"probe": "8D F7 = LEA SI,DI at mod==3", "regs": REGS,
             "rows": out, "match": agree, "diverge": differ,
             "no_silicon": nosil}, indent=1))
    print(f"\nMATCH {agree}   DIVERGE {differ}   NO-SILICON {nosil}"
          f"   (of {len(rows)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
