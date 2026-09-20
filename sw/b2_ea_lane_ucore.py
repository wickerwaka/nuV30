#!/usr/bin/env python3
"""WAVE 24 B-2, the ucore leg: replay B-2's THIRTEEN CONSTRUCTED probes through
the ucore, from RESET, no backdoor injection, and diff against the socket
column `sw/b2_ea_lane.py` captured on the same day with the same bytes and the
same register setup.

Whole-program replay via `sw/tb_bootrun.py`'s `+bootimg` mode, exactly as
WAVE 23's `sw/lea_mod3_gate.py` does it -- reusing that gate's own Runner so
the two waves' ucore columns are taken by one instrument.
"""
import gzip
import json
import sys
import tempfile
from pathlib import Path

SW = Path(__file__).resolve().parent
sys.path.insert(0, str(SW))
from lea_mod3_gate import Runner                             # noqa: E402
from b2_ea_lane import PROBES, LEA, REGS                     # noqa: E402

CAP = SW / "testdata" / "wave24" / "b2" / "8D.json.gz"


def main():
    silicon = {}
    for t in json.load(gzip.open(CAP)):
        silicon[t["b2_tag"]] = t["final"]["regs"].get("si", REGS["si"])

    rows = []
    with tempfile.TemporaryDirectory(dir=str(Path.home() / ".cache" /
                                             "ucsimt-tmp")) as td:
        r = Runner(td)
        for tag, pre, prose, ea, pred in PROBES:
            d = r.dump(pre + LEA)
            rows.append((tag, prose, " ".join(f"{b:02x}" for b in pre), ea,
                         pred, silicon.get(tag), d["IX"]))

    hdr = ("tag", "predecessor bytes", "prose", "EA", "pred",
           "SILICON", "ucore", "verdict")
    print("%-4s %-14s %-18s %6s %6s %8s %7s  %s" % hdr)
    agree = differ = 0
    out = []
    for tag, prose, pb, ea, pred, si, uc in rows:
        v = "MATCH" if si == uc else "DIVERGE"
        agree, differ = (agree + 1, differ) if si == uc else (agree, differ + 1)
        print("%-4s %-14s %-18s %6s %6s %8s %7s  %s" % (
            tag, pb, prose,
            "-" if ea is None else "%04x" % ea,
            "-" if pred is None else "%04x" % pred,
            "%04x" % si, "%04x" % uc, v))
        out.append({"tag": tag, "pre_bytes": pb, "prose": prose, "ea": ea,
                    "predicted_si": pred, "silicon_si": si, "ucore_si": uc,
                    "verdict": v})
    (CAP.parent / "b2_columns.json").write_text(json.dumps(
        {"probe": "8D F7 = LEA SI,DI at mod==3", "regs": REGS,
         "rows": out, "match": agree, "diverge": differ}, indent=1))
    print(f"\nMATCH {agree} / {len(rows)}   DIVERGE {differ} / {len(rows)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
