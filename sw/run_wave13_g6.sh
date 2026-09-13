#!/bin/bash
# WAVE 13 (the phase split, re-measured like-for-like on the stamp-free tree)
# -- one ARM of N-1 / N-3: `quartus_gate.py --seeds 5`, BOTH configurations,
# back to back, at the SAME seed set {1,2,3,4,5}.
#
#   $1 = the arm's tag, e.g. `w13-unsplit-noexc` or `w13-split-noexc`
#
# ⚠ THE TWO ARMS MUST BE DRAWN BY THIS SCRIPT AND ONLY BY THIS SCRIPT.  N-3 is a
# LIKE-FOR-LIKE delta; a difference in driver, flags or seed set between the
# arms is exactly the class of contamination WAVE 11 found and WAVE 12 removed.
#
# THE SINGLE-WRITER GUARD IS BY EXACT BINARY NAME, ONE PATTERN PER `pgrep -x`
# CALL -- `pgrep -x a b` is an ERROR and its failure branch reads as "idle".
#
# `hdl/nec_test_ucore.qsf` is restored with `git checkout -- <that exact path>`
# between the two runs: `quartus_map` rewrites it (the declared SS70.7 exemption,
# E7's single permitted mover) and WAVE 4 lost a whole sweep to not doing it.
# NEVER a bare `git checkout`: 21 pre-existing modified files in this working
# tree are the USER'S and not this wave's.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
TAG="$1"
OUT="sw/testdata/wave13/$TAG"
mkdir -p "$OUT"

guard () {
    for b in quartus_map quartus_fit quartus_sta quartus_asm quartus_sh; do
        while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
    done
}

guard
git checkout -- hdl/nec_test_ucore.qsf
python3 sw/quartus_gate.py --seeds 5 --label "$TAG-control-n5" \
    --log "$OUT/g6_control_n5.log"
git checkout -- hdl/nec_test_ucore.qsf

guard
python3 sw/quartus_gate.py --seeds 5 --retention --label "$TAG-retention-n5" \
    --log "$OUT/g6_retention_n5.log"
git checkout -- hdl/nec_test_ucore.qsf

echo "WAVE 13 G6 ARM $TAG: BOTH CONFIGURATIONS DONE"
