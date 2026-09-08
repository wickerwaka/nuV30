#!/usr/bin/env python3
"""Compare two `sw/phase_split_ladder.sh` output directories, leg by leg.

The ladder's value is not that each leg passes, it is that each leg reads THE
SAME as the pre-edit run.  This extracts the SCORE LINE of every leg and
diffs it -- which is P-4(c) and P-6 in one string.

Usage: phase_split_ladder_diff.py BEFORE_DIR AFTER_DIR
"""
import re, sys, os, glob

# per-leg: the regex whose LAST match is that leg's score line
PAT = {
    "r7_lint":           r"=== r7_lint: .*",
    "ss_lint":           r"ss_lint: PASS.*|ss_flopcensus: PASS.*",
    "cc_all":            r"TOTAL: .*",
    "cc_8f0":            r"TOTAL: .*",
    "hlt_w0":            r"TOTAL: .*",
    "hlt_w1":            r"TOTAL: .*",
    "hlt_w2":            r"TOTAL: .*",
    "hlt_w3":            r"TOTAL: .*",
    "v01_w1":            r"TOTAL: .*",
    "v01_w3":            r"TOTAL: .*",
    "v01_w1_EB":         r"TOTAL: .*",
    "evt_w0":            r"TOTAL: .*",
    "evt_w1":            r"TOTAL: .*",
    "evt_w2":            r"TOTAL: .*",
    "evt_w3":            r"TOTAL: .*",
    "evt_biased":        r"TOTAL: .*",
    "cc_all_div2":       r"TOTAL: .*",
    "cc_all_div3":       r"TOTAL: .*",
    "cc_all_div8":       r"TOTAL: .*",
    "cc_div1_refused":   r".*is OUTSIDE THE ce/ce_half CONTRACT and is REFUSED.*",
    "ulockstep":         r"TOTAL \d+/\d+ cases lockstep|ULOCKSTEP-GOLDEN: .*",
    "ghost_launch":      r"== ALL THREE POPULATIONS: .*",
    "check_boot":        r"BOOT REPLAY MATCHES over .*",
    "check_boot400":     r"BOOT REPLAY MATCHES over .*",
    "check_ab_sim":      r"AB SIM MATCHES CHIP BOOT over .*",
    "s16":               r"S16 TOTAL \(ucore\): .*",
    "demux_off":         r"=== demux_off_gate: .*",
    "test_artifact":     r"=== test_artifact: .*",
    "test_quartus_gate": r"\d+ / \d+ checks pass",
    "ucrom_mif":         r"ucrom_mif_check: .*",
    "chain_lfsr":        r"  seed \d+: .*|chain_lfsr_gate: .*",
}
MULTI = {"chain_lfsr", "ss_lint"}     # keep every match, not just the last

def score(d, leg):
    p = os.path.join(d, leg + ".log")
    if not os.path.exists(p):
        return None
    txt = open(p, errors="replace").read()
    m = re.findall(PAT[leg], txt)
    if not m:
        return "(no score line)"
    # drop volatile receipt ids from chain_lfsr rows? no -- they are not on the
    # score lines; the receipt line is separate and is EXPECTED to move.
    return " | ".join(m) if leg in MULTI else m[-1]

def main():
    a, b = sys.argv[1], sys.argv[2]
    same = moved = missing = 0
    for leg in PAT:
        x, y = score(a, leg), score(b, leg)
        if x is None or y is None:
            print(f"  {leg:20s} MISSING  ({'before' if x is None else 'after'})")
            missing += 1
            continue
        if x == y:
            print(f"  {leg:20s} SAME     {x[:110]}")
            same += 1
        else:
            print(f"  {leg:20s} *** MOVED ***")
            print(f"      before  {x}")
            print(f"      after   {y}")
            moved += 1
    print(f"\n=== ladder diff: {same} SAME / {moved} MOVED / {missing} MISSING")
    return 0 if (moved == 0 and missing == 0) else 1

if __name__ == "__main__":
    sys.exit(main())
