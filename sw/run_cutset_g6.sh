#!/bin/bash
# WAVE 4 (the ce/ce_half PHASE SPLIT DONE AS A CUT SET) -- C-1's G6 legs:
# `--seeds 5`, BOTH configurations, back to back, WITH THE CE MULTICYCLE ALREADY
# DELETED FROM `hdl/nec_test.sdc` (edit (c), `742b52f643`).  This is the GOAL
# STATE and not a probe: no SDC is patched and none is restored.
#
# ⚠ `set -e` IS DELIBERATELY NOT USED, and that is WAVE 2 §10 item 6's finding
# taken: `quartus_gate --seeds N` EXITS NON-ZERO ON A RED DISTRIBUTION, so a
# `set -e` driver stops measuring the moment the first measurement is bad -- it
# reports less the more there is to report.  WAVE 2's retention sweep had to be
# launched by hand for exactly this.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
OUT=sw/testdata/cutset
mkdir -p "$OUT"

# single-writer guard: no other driver and no stage binary may be in flight.
for d in run_adcone_anatomy.sh run_adcone_g6.sh run_phase_split_anatomy.sh \
         run_phase_split_g6.sh run_l2_g6.sh; do
    while pgrep -f "$d" >/dev/null 2>&1; do sleep 30; done
done
for b in quartus_map quartus_fit quartus_sta quartus_asm quartus_sh; do
    while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
done

python3 sw/quartus_gate.py --seeds 5 --label cutset-w4-noexc-control-n5 \
    --log "$OUT/g6_noexc_control_n5.log"
echo "CONTROL sweep exit $?"
python3 sw/quartus_gate.py --seeds 5 --retention --label cutset-w4-noexc-retention-n5 \
    --log "$OUT/g6_noexc_retention_n5.log"
echo "RETENTION sweep exit $?"
echo "G6 BOTH CONFIGURATIONS DONE"
