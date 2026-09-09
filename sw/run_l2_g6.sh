#!/bin/bash
# L2 (WAVE 3) -- L-5 and L-6: four `--seeds 5` sweeps, back to back.
#
#   L-5  the CONTROL configuration of the campaign's own vocabulary: the tree's
#        CURRENT SDC, with the CE multicycle PRESENT.  Both build configurations.
#   L-6  THE GOAL STATE (USER RULING 2026-09-08, "I don't want custom sdc rules,
#        period"): the same two builds with the exception DELETED.
#
# ⚠ NO `set -e`, DELIBERATELY.  `quartus_gate --seeds N` exits non-zero on a RED
# distribution and WAVE 2's driver carried `set -e`, so its CONTROL sweep's RED
# aborted the run before the RETENTION leg
# (`phase_split_landing_results_2026-09-08.md` §10 item 6).  L-6 is EXPECTED to
# be RED on every draw; a driver that stopped there would measure nothing.
#
# ⚠ THE NO-EXCEPTION PAIR RUNS **LAST, RETENTION FIRST AND CONTROL SECOND**, so
# the `hdl/db` that survives the whole run is a NO-EXCEPTION CONTROL fit -- which
# is what L-7's arc anatomy and L-8's row_q probe must be taken on, and the next
# clean build deletes it.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=sw/testdata/l2
mkdir -p "$OUT"

# single-writer guard (distribution gate §12): EXACT binary names, never -f,
# which would match this script itself.
for b in quartus_map quartus_fit quartus_sta quartus_asm; do
    while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
done

echo "=== L-5 CONTROL (exception PRESENT) ==="
python3 sw/quartus_gate.py --seeds 5 --label l2-control-n5 \
    --log "$OUT/g6_control_n5.log"
echo "L-5 control exit $?"
git checkout -- hdl/nec_test_ucore.qsf 2>/dev/null || true

echo "=== L-5 RETENTION (exception PRESENT) ==="
python3 sw/quartus_gate.py --seeds 5 --retention --label l2-retention-n5 \
    --log "$OUT/g6_retention_n5.log"
echo "L-5 retention exit $?"
git checkout -- hdl/nec_test_ucore.qsf 2>/dev/null || true

echo "=== L-6 THE GOAL STATE (exception DELETED), retention then control ==="
python3 sw/l2_noexc_g6.py --seeds 5 --label l2-noexc --configs retention,control
echo "L-6 driver exit $?"
git checkout -- hdl/nec_test_ucore.qsf 2>/dev/null || true

echo "ALL FOUR SWEEPS DONE"
git status --porcelain hdl/ | grep -v '^??' && echo "*** hdl/ DIRTY ***" || echo "hdl/ clean of tracked changes"
