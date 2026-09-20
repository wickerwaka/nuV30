#!/usr/bin/env python3
"""G-LC6 directed strio gate (board-free standing gate). Proves the Family-5
strio-single uline-1 veto (`eu_rsv_strio` -> BIU `pick_t3`, v30_eu.sv:1688 /
v30_biu.sv:676) is INTACT: builds hand-crafted non-REP OUTSB gadgets that force
the T3-eval veto cell (found by sw/biu_law_lc6_gadget.py) and asserts the model
bus stream matches the frozen baseline. Breaking the veto (pick_t3 -> pick_any)
changes the stream -> this gate FAILS. Closes the board-free half of G-LC6 (the
last narrow-law hole the standing gates missed). Uses the CURRENT Verilator
binary (build it first). NO board.

Exit 0 = LC6 veto intact, non-zero = changed (mutation caught / regression).
"""

# --------------------------------------------------------------------------- #
# WAVE 21, 2026-09-19 -- THE ARCHIVED FSM CORE IS RETIRED AND SO IS THIS TOOL.
# it mutates hdl/rtl/core/v30_biu.sv through biu_law_lc6_gadget
# It is NOT deleted: a refusal that names the decision is readable, a missing
# file is not.  `docs/notes/invalidation_ledger.md` RET-2 carries this tool's
# LAST REGISTERED FIGURE.  ⚠ That figure is an FSM figure and may not be
# re-labelled onto a ucore leg -- re-register, never re-label.
# --------------------------------------------------------------------------- #
import sys as _sys                                            # noqa: E402
from pathlib import Path as _Path                             # noqa: E402
_sys.path.insert(0, str(_Path(__file__).resolve().parent))
import fsmcore as _fsmcore                                    # noqa: E402
_fsmcore.refuse("sw/check_lc6_gate.py -- it mutates hdl/rtl/core/v30_biu.sv through biu_law_lc6_gadget")

import sys
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "sw"))
import biu_law_lc6_gadget as G                       # noqa: E402

BASELINE = ROOT / "sw/lc6_gate_baseline.json"
# (op, j_lead, k_fill, ws, wmax) — the frozen discriminating gadget configs.
CFG = [(0x6E, 0, 0, 0, 0), (0x6E, 0, 7, 5, 1), (0x6E, 0, 9, 0, 0)]


def digest_sha(op, j, k, ws, wmax):
    img = G.build_image(op, j, k)
    return hashlib.sha256(G.digest(img, ws, wmax).encode()).hexdigest()[:16]


def main():
    ref = json.loads(BASELINE.read_text())
    bad = []
    for op, j, k, ws, wmax in CFG:
        key = f"{op:#x}:j{j}:k{k}:ws{ws}:wmax{wmax}"
        cur = digest_sha(op, j, k, ws, wmax)
        if ref.get(key) != cur:
            bad.append((key, ref.get(key), cur))
    if bad:
        print("check_lc6_gate: FAIL (strio uline-1 veto changed)")
        for key, r, c in bad:
            print(f"  - {key}: ref={r} cur={c}")
        return 1
    print(f"check_lc6_gate: PASS ({len(CFG)} strio-single gadgets, "
          f"eu_rsv_strio/pick_t3 veto intact)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
