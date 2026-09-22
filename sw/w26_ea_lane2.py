#!/usr/bin/env python3
"""WAVE 26 -- the directed SOCKET rig that CLOSES WAVE 24's declared reference
gap: `mod = 01` and `mod = 10`, where a base/index sum AND a displacement are
both present and WAVE 24 probed neither.

It is `sw/b2_ea_lane.py` extended, and it keeps that rig's THIRTEEN probes
VERBATIM as reproduction controls -- so this capture carries its own positive
control and a row that fails to reproduce is a rig finding, not a result.

Every probe is `<predecessor bytes> 8D F7` -- `LEA SI, DI` at `mod == 3`, the
undocumented form whose row-1 `SIGMA -> R` transfer observes the address
adder's two retained rails.  Body at `PS=0x0000 PC=0x8100`, register setup
`char_mod3.SETUPS[0]` with `AW = 0x1111` as the scratch term.

TRUTH SOURCE IS THE SOCKET (`emit_suite.EMIT_USE_CORE` is False and asserted).
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
from b2_ea_lane import PROBES as B2_PROBES, LEA, REGS    # noqa: E402

# --------------------------------------------------------------------------
# THE NEW ROWS.  `mod = 01` / `mod = 10`: a displacement is present, and on
# two of them an index register is present as well.
#
# The rule landed in WAVE 26 says the adder's B rail takes the SECOND ADDEND,
# and that a form carrying a displacement gives the displacement -- so on
# `P1` and `P4` the index is NOT what is retained even though the form has
# one.  `P1` is the sharpest row in the set: its displacement is ZERO, so
# "the form has a displacement" and "the displacement is non-zero" predict
# DIFFERENT values (0x1111 against 0x8888) and silicon chooses between them.
#
#   predicted SI = <retained B rail> + <tmpa>, and tmpa after `MOV [ea],AW`
#   is AW = 0x1111 on every row here.
# --------------------------------------------------------------------------
#   tag  predecessor bytes                        prose                          EA   predicted SI   the alternative it refutes
NEW = [
    ("P0", bytes([0x89, 0x40, 0x10]),       "MOV [BW+IX+10h],AW",  0xBBCB, 0x1121, ("B=index -> 0x8888",)),
    ("P1", bytes([0x89, 0x40, 0x00]),       "MOV [BW+IX+0],AW",    0xBBBB, 0x1111, ("B=index when disp==0 -> 0x8888",)),
    ("P2", bytes([0x89, 0x46, 0x10]),       "MOV [BP+10h],AW",     0x6676, 0x1121, ("B=0 on a one-register form -> 0x1111",)),
    ("P3", bytes([0x89, 0x84, 0x34, 0x12]), "MOV [IX+1234h],AW",   0x89AB, 0x2345, ("B=0 on a one-register form -> 0x1111",)),
    ("P4", bytes([0x89, 0x81, 0x34, 0x12]), "MOV [BW+IY+1234h],AW", 0xDF00, 0x2345, ("B=index -> 0x9999",)),
    ("P5", bytes([0x89, 0x45, 0x20]),       "MOV [IY+20h],AW",     0x88A8, 0x1131, ("B=0 -> 0x1111",)),
    ("P6", bytes([0x89, 0x87, 0x34, 0x12]), "MOV [BW+1234h],AW",   0x5678, 0x2345, ("B=0 -> 0x1111",)),
    ("P7", bytes([0x89, 0x44, 0xF0]),       "MOV [IX-10h],AW",     0x7767, 0x1101, ("B=0 -> 0x1111; B=unsigned disp8 -> 0x1201",)),
]

PROBES = [(t, p, s, e, q) for (t, p, s, e, q) in B2_PROBES] + \
         [(t, p, s, e, q) for (t, p, s, e, q, _alt) in NEW]

# WAVE 24's MEASURED SILICON column for the thirteen controls -- the values
# this capture must REPRODUCE.  Read out of the artifact, never hard-coded:
CTRL_CAP = SW / "testdata" / "wave24" / "b2" / "8D.json.gz"


def control_column():
    out = {}
    for t in json.load(gzip.open(CTRL_CAP)):
        out[t["b2_tag"]] = t["final"]["regs"].get("si", REGS["si"])
    return out


def case(pre, tag, prose):
    """`emit_case`'s cycle window is ONE instruction wide, so `next_ip` must
    name the PREDECESSOR's end (b2_ea_lane._case, measured 13/13).  The cycle
    rows of these goldens therefore cover the PREDECESSOR; what this rig reads
    is `final.regs.si`, from the terminator's dump after BOTH retire."""
    return {"regs": dict(REGS), "instr": pre + LEA, "ram": [], "ivt": None,
            "name": f"{prose} ; LEA SI,DI(mod3)  [{tag}]",
            "next_ip": (REGS["ip"] + len(pre)) & 0xFFFF, "next_cs": None}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="root@mister-nec")
    ap.add_argument("--out", default=str(SW / "testdata" / "wave26" / "b2b"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--new-only", action="store_true",
                    help="capture only the eight gap-closing rows")
    a = ap.parse_args()

    if es.EMIT_USE_CORE is not False:
        sys.exit(f"REFUSED: truth source is not the socket "
                 f"(EMIT_USE_CORE={es.EMIT_USE_CORE!r})")
    probes = [p for p in PROBES if p[0].startswith("P")] if a.new_only \
        else PROBES
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    spec = OPCODES["8D"]

    if a.dry_run:
        import testimage
        for tag, pre, prose, ea, pred in probes:
            c = case(pre, tag, prose)
            nec = {es.INTEL2NEC[k]: v for k, v in c["regs"].items()}
            try:
                img, meta = testimage.compose(regs=nec, instr=c["instr"],
                                              ram=[], ivt=None)
                print(f"  {tag}: {' '.join(f'{b:02x}' for b in c['instr'])}"
                      f"  anchor={meta['anchor_linear']:05x}  COMPOSES")
            except ComposeError as e:
                print(f"  {tag}: COMPOSE ERROR: {e}")
        return 0

    ctrl = control_column()
    goldens, fails = [], []
    t0 = time.time()
    for i, (tag, pre, prose, ea, pred) in enumerate(probes):
        c = case(pre, tag, prose)
        try:
            t = emit_case(spec, c, a.host, tag="w26")
            t["idx"] = i
            t["b2_tag"] = tag
            t["b2_pre_bytes"] = " ".join(f"{b:02x}" for b in pre)
            t["b2_prose"] = prose
            t["b2_ea"] = ea
            t["b2_predicted_si"] = pred
            goldens.append(t)
            si = t["final"]["regs"].get("si", REGS["si"])
            c24 = ctrl.get(tag)
            print(f"  {tag} [{t['b2_pre_bytes']} 8d f7]  SI={si:04x}  "
                  f"pred={'-' if pred is None else f'{pred:04x}'}  "
                  f"W24={'-' if c24 is None else f'{c24:04x}'}"
                  f"{'' if c24 is None else (' REPRO' if c24 == si else ' ** CONTROL MOVED **')}"
                  f"  [{time.time()-t0:.0f}s]", flush=True)
        except (RunError, ComposeError) as e:
            fails.append((tag, str(e)[:160]))
            print(f"  {tag}: FAIL {type(e).__name__}: {str(e)[:160]}",
                  flush=True)

    import v30run as _v30
    _r = _v30._runners.get(a.host)
    divrb = _r.div_readback if _r is not None else "(no runner: nothing captured)"
    print(f"\n# DIVIDER READBACK: {divrb}", flush=True)
    if "UNPINNED" in divrb:
        print("STOP S-5: UNPINNED divider readback -- rig-integrity FINDING",
              flush=True)

    with gzip.open(out / "8D.json.gz", "wt") as f:
        json.dump(goldens, f)
    (out / "manifest.json").write_text(json.dumps({
        "rig": "sw/w26_ea_lane2.py",
        "truth_source": es.truth_stamp(),
        "divider_commanded": es.emit_div_stamp(),
        "divider_readback": divrb,
        "regs": REGS,
        "probe": "8D F7 = LEA SI,DI at mod==3",
        "controls_from": str(CTRL_CAP.relative_to(SW.parent)),
        "probes": [{"tag": t, "pre_bytes": " ".join(f"{b:02x}" for b in p),
                    "prose": s, "ea": e, "predicted_si": q}
                   for t, p, s, e, q in probes],
        "n_goldens": len(goldens), "fails": fails,
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=1))
    print(f"\ncaptured {len(goldens)}/{len(probes)} -> {out}")
    for f_ in fails:
        print("  FAIL:", f_)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
