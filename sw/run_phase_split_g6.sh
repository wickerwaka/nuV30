#!/bin/bash
# WAVE 2 (the ce/ce_half PHASE SPLIT) -- P-1's G6 legs: `--seeds 5`, BOTH
# configurations, back to back.  Each invocation carries its own single-writer
# guard inside quartus_gate.py's sweep path; this script waits for any stage
# binary AND any driver to be idle first, so two sweeps cannot overlap on one
# `hdl/db` (the defect `timing50_distribution_2026-08-13.md` §12 found in
# flight).
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=sw/testdata/phasesplit/wave2
mkdir -p "$OUT"
for d in run_adcone_anatomy.sh run_adcone_g6.sh run_phase_split_anatomy.sh; do
    while pgrep -f "$d" >/dev/null 2>&1; do sleep 30; done
done
for b in quartus_map quartus_fit quartus_sta quartus_asm; do
    while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
done
python3 sw/quartus_gate.py --seeds 5 --label phasesplit-w2-control-n5 \
    --log "$OUT/g6_control_n5.log"
python3 sw/quartus_gate.py --seeds 5 --retention --label phasesplit-w2-retention-n5 \
    --log "$OUT/g6_retention_n5.log"
echo "G6 BOTH CONFIGURATIONS DONE"
