#!/usr/bin/env python3
"""FLASH #22 -- THE S-1 DERIVATION FOR THE RIG'S ENABLE TRAIN, WITH ITS OWN
NULL.

WHY THIS FILE EXISTS.  The ce/ce_half phase split (WAVE 17) makes clause S-1
of the ce/ce_half contract -- *at least one `CE_HALF` falls between consecutive
`CE`s* -- LOAD-BEARING FOR THE EU, not just for the BIU's T1 turnaround.
`v30_core.sv`'s `$fatal` on S-1 is `ifndef SYNTHESIS`, so **FABRIC HAS NO
ASSERTION**.  Before a bitstream carrying the split is programmed, the rig's
own enable train must be shown to satisfy S-1 STRUCTURALLY.

WHAT THE RIG DOES (hdl/rtl/nec_bus.sv:170-190, verbatim arithmetic):

    reg [5:0] div_cnt;
    wire [5:0] div_max = cfg_clk_div - 6'd1;
    wire [5:0] half    = {1'b0, cfg_clk_div[5:1]};      // floor(D/2)
    wire tick_rise  = div_cnt == div_max;
    wire tick_fall  = div_cnt == half - 6'd1;
    always_ff @(posedge clk)
        div_cnt <= tick_rise ? 6'd0 : div_cnt + 6'd1;

and `hdl/rtl/system_large.sv` wires CE = tick_rise, CE_HALF = tick_fall.

This model reproduces that arithmetic in 6-bit wrapping integers -- including
the `half - 1` UNDERFLOW at D<=1, which is the whole hazard -- and walks the
counter, scoring C-a (never coincident) and S-1 (a CE_HALF between consecutive
CEs) on the delivered enable stream.

NON-VACUITY: D = 0 and D = 1 MUST FAIL, or this checker is not a checker.
"""
import sys

M = 64  # 6-bit


def train(D, clocks=4096):
    """Yield (ce, ce_half) per fabric clock for cfg_clk_div == D."""
    div_max = (D - 1) % M
    half = (D >> 1) % M
    fall_at = (half - 1) % M
    cnt = 0
    for _ in range(clocks):
        rise = (cnt == div_max)
        fall = (cnt == fall_at)
        yield rise, fall
        cnt = 0 if rise else (cnt + 1) % M


def score(D, clocks=4096):
    coincident = 0
    ces = 0
    halves = 0
    s1_viol = 0
    half_since_ce = True          # same reset value as v30_core.sv:280
    gaps = []                     # CE_HALFs between consecutive CEs
    pending = 0
    seen_first_ce = False
    for ce, ch in train(D, clocks):
        if ce and ch:
            coincident += 1
        if ce:
            ces += 1
            if not half_since_ce:
                s1_viol += 1
            if seen_first_ce:
                gaps.append(pending)
            seen_first_ce = True
            pending = 0
        if ch:
            halves += 1
            if seen_first_ce:
                pending += 1
        if ch:
            half_since_ce = True
        elif ce:
            half_since_ce = False
    return {"D": D, "ce": ces, "ce_half": halves,
            "coincident": coincident, "s1_violations": s1_viol,
            "min_gap": min(gaps) if gaps else None,
            "max_gap": max(gaps) if gaps else None,
            "ok": coincident == 0 and s1_viol == 0 and ces > 0}


def main():
    print("== FLASH #22 -- S-1 / C-a FOR THE RIG'S ENABLE TRAIN "
          "(nec_bus.sv divider, system_large.sv wiring)")
    print("   CE = tick_rise, CE_HALF = tick_fall, both off ONE counter.\n")
    bad = []
    print("   D  |   CE   CE_HALF | coincident(C-a) | S-1 viol | gap min/max")
    print("  ----+----------------+-----------------+----------+------------")
    for D in range(0, 64):
        r = score(D)
        mark = "" if r["ok"] else "   <<< VIOLATES"
        if D <= 2 or D in (3, 4, 8, 16, 32, 63) or not r["ok"]:
            print(f"  {D:3d} | {r['ce']:5d} {r['ce_half']:7d} | "
                  f"{r['coincident']:15d} | {r['s1_violations']:8d} | "
                  f"{r['min_gap']}/{r['max_gap']}{mark}")
        if not r["ok"]:
            bad.append(D)

    print()
    # THE DECLARED OPERATING RANGE.  nec_bus.sv:42 declares cfg_clk_div
    # "even, >= 4"; hps_axi_slave.sv:260 resets it to 8; v30run.DIV_OF_RECORD
    # is 8 and every board driver PINS it.
    legal = [D for D in range(2, 64)]
    viol = [D for D in legal if not score(D)["ok"]]
    print(f"  ALL D in [2, 63]: violations = {viol}   "
          f"-> {'NONE' if not viol else 'PRESENT'}")
    r8 = score(8)
    print(f"  THE DIVIDER OF RECORD, D = 8: CE {r8['ce']} / CE_HALF "
          f"{r8['ce_half']} / coincident {r8['coincident']} / S-1 viol "
          f"{r8['s1_violations']} / exactly {r8['min_gap']}"
          f"-{r8['max_gap']} CE_HALF between consecutive CEs")

    print("\n  --- NON-VACUITY (the null: these MUST fail) ---")
    nulls_ok = True
    for D in (0, 1):
        r = score(D)
        why = ("C-a: CE and CE_HALF coincide" if r["coincident"]
               else "S-1: CEs with no CE_HALF between them")
        verdict = "FAILS as required" if not r["ok"] else "*** PASSED -- THE CHECKER IS VACUOUS ***"
        print(f"    D = {D}: coincident {r['coincident']}, S-1 viol "
              f"{r['s1_violations']}  -> {verdict}  ({why})")
        if r["ok"]:
            nulls_ok = False

    ok = (not viol) and nulls_ok
    print(f"\n  S-1 DERIVATION: {'PASS' if ok else 'FAIL'}   "
          f"(legal range clean: {not viol}; nulls fail: {nulls_ok})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
