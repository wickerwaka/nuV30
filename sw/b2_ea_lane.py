#!/usr/bin/env python3
"""WAVE 24 B-2 -- directed SOCKET capture of the ModR/M retained-EA-lane law.

WAVE 23 (docs/notes/lea_mod3_results_2026-09-20.md section 4) found a real,
silicon-anchored divergence and could not close it: the two silicon rows it
reasoned from are `tests/v30/mod3_illegal/metadata.json::stale_ea_probe`, whose
`pre` field is ENGLISH PROSE, and the committed `sw/char_mod3.py`'s own probe
list does not contain them (the freeze's `rig` field says "char_mod3.py + inline
freeze").  The bytes are not recoverable from any artifact.

THIS RIG CONSTRUCTS THEM AND STATES THEM.  Every probe is
`<predecessor bytes> 8D F7`  --  `LEA SI, DI` at mod == 3 -- with the body at
PS=0x0000 PC=0x8100 so the live composer accepts it and the column is directly
comparable with WAVE 23's measured ucore column.

Truth source is the SOCKET (emit_suite.EMIT_USE_CORE is False and asserted).
"""
import argparse
import gzip
import json
import sys
import time
from pathlib import Path

SW = Path(__file__).resolve().parent
sys.path.insert(0, str(SW))
import emit_suite as es                                  # noqa: E402
from emit_suite import emit_case, OPCODES                # noqa: E402
from v30run import RunError                              # noqa: E402
from testimage import ComposeError                       # noqa: E402

# WAVE 23's register setup (char_mod3.SETUPS[0]) with the body moved to the
# live composer's code region.  AW = 0x1111 is the scratch term under test.
REGS = {"ax": 0x1111, "cx": 0x2222, "dx": 0x3333, "bx": 0x4444, "sp": 0x3F00,
        "bp": 0x6666, "si": 0x7777, "di": 0x8888, "cs": 0x0000, "ip": 0x8100,
        "ds": 0x1000, "es": 0x2000, "ss": 0x3000, "flags": 0xF002}

LEA = bytes([0x8D, 0xF7])          # LEA SI, DI  -- reg=110(SI) rm=111(DI), mod=3

#   tag  predecessor bytes                     prose                     EA   predicted SI
PROBES = [
    ("C1", bytes([0xA3, 0x34, 0x12]),          "MOV [1234h],AW",       0x1234, 0x1234),
    ("C2", bytes([0xA3, 0xEF, 0xBE]),          "MOV [BEEFh],AW",       0xBEEF, 0xBEEF),
    ("C3", bytes([0x90]),                      "NOP (no EA)",            None, None),
    ("R1", bytes([0x88, 0x26, 0x10, 0x30]),    "MOV [3010h],AH",       0x3010, 0x4121),
    ("R2", bytes([0x8B, 0x0E, 0x55, 0x44]),    "MOV CW,[4455h]",       0x4455, None),
    ("M0", bytes([0x89, 0x00]),                "MOV [BW+IX],AW",       0xBBBB, 0xCCCC),
    ("M1", bytes([0x89, 0x01]),                "MOV [BW+IY],AW",       0xCCCC, 0xDDDD),
    ("M2", bytes([0x89, 0x02]),                "MOV [BP+IX],AW",       0xDDDD, 0xEEEE),
    ("M3", bytes([0x89, 0x03]),                "MOV [BP+IY],AW",       0xEEEE, 0xFFFF),
    ("M4", bytes([0x89, 0x04]),                "MOV [IX],AW",          0x7777, 0x8888),
    ("M5", bytes([0x89, 0x05]),                "MOV [IY],AW",          0x8888, 0x9999),
    ("M6", bytes([0x89, 0x06, 0x34, 0x12]),    "MOV [1234h],AW",       0x1234, 0x2345),
    ("M7", bytes([0x89, 0x07]),                "MOV [BW],AW",          0x4444, 0x5555),
]

# WAVE 23's MEASURED ucore column, for the rows it published (section 4).
UCORE_W23 = {"C1": 0x1234, "C2": 0xBEEF, "R1": 0x9211, "R2": 0x1190,
             "M0": 0x8888, "M1": 0x9999, "M2": 0x8888, "M3": 0x9999,
             "M4": 0x9211, "M5": 0x9211, "M6": 0x9211, "M7": 0x9211}


def _case(pre, tag, prose):
    instr = pre + LEA
    return {"regs": dict(REGS), "instr": instr, "ram": [], "ivt": None,
            "name": f"{prose} ; LEA SI,DI(mod3)  [{tag}]",
            "next_ip": (REGS["ip"] + len(instr)) & 0xFFFF, "next_cs": None}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="root@mister-nec")
    ap.add_argument("--out", default=str(SW / "testdata" / "wave24" / "b2"))
    ap.add_argument("--dry-run", action="store_true",
                    help="compose only, no board: prints each probe's image "
                         "placement and refuses to touch the socket")
    a = ap.parse_args()

    if es.EMIT_USE_CORE is not False:
        sys.exit(f"REFUSED: truth source is not the socket "
                 f"(EMIT_USE_CORE={es.EMIT_USE_CORE!r})")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    spec = OPCODES["8D"]

    if a.dry_run:
        import testimage
        for tag, pre, prose, ea, pred in PROBES:
            c = _case(pre, tag, prose)
            nec = {es.INTEL2NEC[k]: v for k, v in c["regs"].items()}
            try:
                img, meta = testimage.compose(regs=nec, instr=c["instr"],
                                              ram=[], ivt=None)
                print(f"  {tag}: {' '.join(f'{b:02x}' for b in c['instr'])}"
                      f"  anchor={meta['anchor_linear']:05x}  COMPOSES")
            except ComposeError as e:
                print(f"  {tag}: COMPOSE ERROR: {e}")
        return 0

    goldens, fails = [], []
    t0 = time.time()
    for i, (tag, pre, prose, ea, pred) in enumerate(PROBES):
        c = _case(pre, tag, prose)
        try:
            t = emit_case(spec, c, a.host, tag="b2")
            t["idx"] = i
            t["b2_tag"] = tag
            t["b2_pre_bytes"] = " ".join(f"{b:02x}" for b in pre)
            t["b2_prose"] = prose
            t["b2_ea"] = ea
            t["b2_predicted_si"] = pred
            goldens.append(t)
            si = t["final"]["regs"].get("si", REGS["si"])
            print(f"  {tag} [{t['b2_pre_bytes']} 8d f7]  SI={si:04x}  "
                  f"pred={'-' if pred is None else f'{pred:04x}'}  "
                  f"ucore(W23)={UCORE_W23.get(tag, '-')!r}  "
                  f"[{time.time()-t0:.0f}s]", flush=True)
        except (RunError, ComposeError) as e:
            fails.append((tag, str(e)[:160]))
            print(f"  {tag}: FAIL {type(e).__name__}: {str(e)[:160]}",
                  flush=True)

    # DIVIDER PROVENANCE -- what the board ACTUALLY reports, not what we asked
    # for.  An UNPINNED readback is a rig-integrity FINDING and a hard stop.
    import v30run as _v30
    _r = _v30._runners.get(a.host)
    divrb = _r.div_readback if _r is not None else "(no runner: nothing captured)"
    print(f"\n# DIVIDER READBACK: {divrb}", flush=True)
    if "UNPINNED" in divrb:
        print("STOP S-1: UNPINNED divider readback -- rig-integrity FINDING",
              flush=True)

    with gzip.open(out / "8D.json.gz", "wt") as f:
        json.dump(goldens, f)
    (out / "b2_manifest.json").write_text(json.dumps({
        "rig": "sw/b2_ea_lane.py",
        "truth_source": es._truth_stamp(),
        "divider_commanded": es.emit_div_stamp(),
        "divider_readback": divrb,
        "regs": REGS,
        "probe": "8D F7 = LEA SI,DI at mod==3",
        "probes": [{"tag": t, "pre_bytes": " ".join(f"{b:02x}" for b in p),
                    "prose": s, "ea": e, "predicted_si": q}
                   for t, p, s, e, q in PROBES],
        "n_goldens": len(goldens), "fails": fails,
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=1))
    print(f"\ncaptured {len(goldens)}/{len(PROBES)} -> {out}")
    for f_ in fails:
        print("  FAIL:", f_)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
