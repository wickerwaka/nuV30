#!/usr/bin/env python3
"""WAVE 28 / FLASH #24 -- THE FABRIC LEG of the retained-EA-lane law.

WAVE 26 measured the `ea_pair_valid` / second-addend law three ways and
**every one of them was VERILATOR or a SOCKET capture of the real part**:

  * `sw/b2_ea_lane_ucore.py`   13 / 13   -- Verilator, `tb_bootrun +bootimg`
  * `sw/w26_ea_lane2_ucore.py` 21 / 21   -- Verilator, the same Runner
  * `sw/w26_ea_lane2.py`       21 rows   -- the SOCKETED CHIP (`use_core=False`)

**THE SYNTHESISED CORE HAS NEVER RUN THE FIX.**  This file closes that, and it
is the only instrument in the family that puts the FPGA core on the probe.

HOW IT DRIVES THE TWO LEGS -- STATED, BECAUSE THE BRIEF REQUIRES IT
-------------------------------------------------------------------
`emit_case`'s record source is `emit_suite._capture`, which passes
`use_core=emit_suite.EMIT_USE_CORE` straight into `v30run.run_image`.  The
final register column it returns is parsed out of the STORE-STUB DUMP in the
captured bus rows, so it is bus-observable and engine-agnostic: the identical
image, composed once, yields a comparable column from either A/B position.

So for each probe this file captures the SAME COMPOSED IMAGE twice,
back-to-back in one session:

    leg `socket`  EMIT_USE_CORE = False   the socketed uPD70116 -- SILICON
    leg `core`    EMIT_USE_CORE = True    the in-FPGA v30_core  -- THE DUT

and scores them **PAIRWISE, probe by probe**.  `use_core` is passed
EXPLICITLY on every capture because the board's CFG is sticky.

⚠ THE PROVENANCE STAMP.  This file used to stamp each leg with its own typed
constant, because `emit_suite._truth_stamp()` returned the socket string from
`ENGINE == "chip"` alone and **never consulted `EMIT_USE_CORE`** -- so on the
core leg it would have written a provenance line that is false (WAVE 28
doc-discrepancy D-1).  **WAVE 29 FIXED THE DERIVATION INSTEAD**:
`emit_suite.truth_stamp(use_core=...)` derives the line from the engine, the
position, and `v30run.board_witness()`, and it REFUSES a position the board was
never actually commanded into.  So each leg is still stamped with the value it
actually passed -- but now by the ONE writer, and now checked.

THE POSITIVE CONTROL IS BUILT IN, AND IT IS NOT THE SAME AS THE RESULT
-----------------------------------------------------------------------
The `socket` leg must REPRODUCE WAVE 26's banked socket column
(`sw/testdata/wave26/b2b/8D.json.gz`) on all 21 rows.  Silicon cannot be moved
by a bitstream; a socket row that moves is a RIG FINDING, not a result, and is
printed as `** CONTROL MOVED **`.

THE NON-VACUITY CONTROL IS THE PRE-FLASH RUN
---------------------------------------------
Run against the RESIDENT (pre-flash) bitstream the `core` leg must DIVERGE --
7 of 21 matching, on exactly the rows and exactly the values WAVE 26 measured
for the pre-landing core (`sw/testdata/wave26/b2b/ucore_columns_before.json`).
A rig that reports 21 / 21 on BOTH bitstreams is measuring the socket twice.
`--expect before|after` scores that explicitly.
"""
import argparse
import gzip
import hashlib
import json
import sys
import time
from pathlib import Path

SW = Path(__file__).resolve().parent
sys.path.insert(0, str(SW))
import emit_suite as es                                    # noqa: E402
from emit_suite import emit_case, OPCODES                  # noqa: E402
from v30run import RunError                                # noqa: E402
from testimage import ComposeError                         # noqa: E402
from w26_ea_lane2 import PROBES, case                      # noqa: E402
from b2_ea_lane import REGS                                # noqa: E402

W26 = SW / "testdata" / "wave26" / "b2b"
BANKED_SOCKET = W26 / "8D.json.gz"                 # WAVE 26's socket column
UCORE_BEFORE = W26 / "ucore_columns_before.json"   # pre-landing Verilator core
UCORE_AFTER = W26 / "ucore_columns.json"           # landed Verilator core


def _col(path):
    return {t["b2_tag"]: t["final"]["regs"].get("si", REGS["si"])
            for t in json.load(gzip.open(path))}


def _ucore_col(path):
    d = json.load(open(path))
    return {r["tag"]: r["ucore_si"] for r in d["rows"]}


def capture_leg(host, use_core, probes, tag):
    """Capture every probe with EMIT_USE_CORE pinned to `use_core`.

    The pin is set on the module `emit_suite` itself because `_capture` reads
    it at call time; it is restored by the caller's `finally`."""
    es.EMIT_USE_CORE = use_core
    spec = OPCODES["8D"]
    out, fails = [], []
    for i, (t, pre, prose, ea, pred) in enumerate(probes):
        c = case(pre, t, prose)
        try:
            rec = emit_case(spec, c, host, tag=tag)
            rec["idx"] = i
            rec["b2_tag"] = t
            rec["b2_pre_bytes"] = " ".join(f"{b:02x}" for b in pre)
            rec["b2_prose"] = prose
            rec["b2_ea"] = ea
            rec["b2_predicted_si"] = pred
            # WAVE 29: the PER-ROW leg label is the SAME derivation as the
            # manifest's, so a row and the manifest it sits under cannot
            # disagree about where the row came from.  It is evaluated AFTER
            # `emit_case` has captured, so the board witness already carries
            # this leg's position and the claim is cross-checked per row.
            rec["w28_leg"] = es.truth_stamp(use_core=use_core)
            rec["w28_use_core"] = use_core
            out.append(rec)
        except (RunError, ComposeError) as e:
            fails.append((t, f"{type(e).__name__}: {str(e)[:200]}"))
            print(f"  {tag} {t}: FAIL {type(e).__name__}: {str(e)[:200]}",
                  flush=True)
    return out, fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="root@mister-nec")
    ap.add_argument("--out", required=True,
                    help="directory for this run's two columns + manifest")
    ap.add_argument("--expect", choices=["before", "after"], required=True,
                    help="`after` = the fixed core is flashed: core must be "
                         "21/21.  `before` = the NON-VACUITY control: core "
                         "must reproduce the pre-landing column, 7/21")
    ap.add_argument("--label", default="")
    a = ap.parse_args()

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    banked = _col(BANKED_SOCKET)
    predicted_core = _ucore_col(UCORE_BEFORE if a.expect == "before"
                                else UCORE_AFTER)

    t0 = time.time()
    saved = es.EMIT_USE_CORE
    try:
        print("== leg SOCKET (use_core=False) -- the real chip ==", flush=True)
        sock, sfail = capture_leg(a.host, False, PROBES, "w28s")
        print("== leg CORE (use_core=True) -- the FPGA v30_core ==", flush=True)
        core, cfail = capture_leg(a.host, True, PROBES, "w28c")
    finally:
        es.EMIT_USE_CORE = saved

    import v30run as _v30
    r = _v30._runners.get(a.host)
    divrb = r.div_readback if r is not None else "(no runner)"

    scol = {t["b2_tag"]: t["final"]["regs"].get("si", REGS["si"]) for t in sock}
    ccol = {t["b2_tag"]: t["final"]["regs"].get("si", REGS["si"]) for t in core}

    print(f"\n{'tag':<4} {'predecessor':<14} {'prose':<22} {'SOCKET':>7} "
          f"{'CORE':>6} {'verdict':<8} {'W26sock':>8} {'pred':>6}")
    pair_ok = pair_bad = 0
    ctrl_ok = ctrl_moved = 0
    pred_hit = pred_miss = 0
    rows = []
    for t, pre, prose, ea, _p in PROBES:
        s = scol.get(t)
        c = ccol.get(t)
        b = banked.get(t)
        pc = predicted_core.get(t)
        v = "ABSENT" if (s is None or c is None) else \
            ("MATCH" if s == c else "DIVERGE")
        if v == "MATCH":
            pair_ok += 1
        elif v == "DIVERGE":
            pair_bad += 1
        cm = "-" if (b is None or s is None) else \
            ("REPRO" if b == s else "** CONTROL MOVED **")
        if cm == "REPRO":
            ctrl_ok += 1
        elif cm.startswith("**"):
            ctrl_moved += 1
        ph = "-" if (pc is None or c is None) else ("HIT" if pc == c else "MISS")
        if ph == "HIT":
            pred_hit += 1
        elif ph == "MISS":
            pred_miss += 1
        print(f"{t:<4} {' '.join(f'{x:02x}' for x in pre):<14} {prose:<22} "
              f"{'----' if s is None else f'{s:04x}':>7} "
              f"{'----' if c is None else f'{c:04x}':>6} {v:<8} "
              f"{cm:>8} {ph:>6}")
        rows.append({"tag": t, "pre_bytes": " ".join(f"{x:02x}" for x in pre),
                     "prose": prose, "ea": ea, "socket_si": s, "core_si": c,
                     "verdict": v, "w26_socket_si": b, "control": cm,
                     "predicted_core_si": pc, "prediction": ph})

    for p, f in (("socket", sfail), ("core", cfail)):
        for tg, msg in f:
            print(f"  FAIL {p} {tg}: {msg}")

    def _h(p):
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()

    sp, cp = out / "8D_socket.json.gz", out / "8D_core.json.gz"
    with gzip.open(sp, "wt") as f:
        json.dump(sock, f)
    with gzip.open(cp, "wt") as f:
        json.dump(core, f)

    man = {
        "rig": "sw/w28_ea_lane_fabric.py",
        "wave": "WAVE 28 / FLASH #24",
        "label": a.label,
        "expect": a.expect,
        "probe": "8D F7 = LEA SI,DI at mod==3",
        "regs": REGS,
        "legs": {
            # WAVE 29: BOTH legs are now DERIVED by the ONE function, each
            # naming its own position; es.truth_stamp() REFUSES a position the
            # board was never commanded into (see the module docstring).
            "socket": {"use_core": False,
                       "truth_source": es.truth_stamp(use_core=False),
                       "file": sp.name, "sha256": _h(sp), "n": len(sock),
                       "fails": sfail},
            "core": {"use_core": True,
                     "truth_source": es.truth_stamp(use_core=True),
                     "file": cp.name, "sha256": _h(cp), "n": len(core),
                     "fails": cfail},
        },
        "divider_commanded": es.emit_div_stamp(),
        "divider_readback": divrb,
        "controls_from": str(BANKED_SOCKET.relative_to(SW.parent)),
        "predicted_core_from": str((UCORE_BEFORE if a.expect == "before"
                                    else UCORE_AFTER).relative_to(SW.parent)),
        "rows": rows,
        "pair_match": pair_ok, "pair_diverge": pair_bad,
        "control_repro": ctrl_ok, "control_moved": ctrl_moved,
        "prediction_hit": pred_hit, "prediction_miss": pred_miss,
        "seconds": round(time.time() - t0, 1),
        "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (out / "manifest.json").write_text(json.dumps(man, indent=1))

    print(f"\nPAIRWISE (core vs socket, same images): MATCH {pair_ok} / "
          f"{len(PROBES)}   DIVERGE {pair_bad}")
    print(f"POSITIVE CONTROL (socket vs WAVE 26 banked socket): "
          f"REPRO {ctrl_ok} / {len(PROBES)}   MOVED {ctrl_moved}")
    print(f"CORE vs the registered `{a.expect}` column: HIT {pred_hit} / "
          f"{len(PROBES)}   MISS {pred_miss}")
    print(f"DIVIDER READBACK: {divrb}")
    if "UNPINNED" in divrb:
        print("STOP: UNPINNED divider readback -- RIG-INTEGRITY FINDING")
    print(f"columns -> {sp}  sha256 {man['legs']['socket']['sha256'][:16]}…")
    print(f"           {cp}  sha256 {man['legs']['core']['sha256'][:16]}…")

    if ctrl_moved or sfail or cfail or "UNPINNED" in divrb:
        return 2
    return 0 if pred_miss == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
