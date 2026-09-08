#!/bin/bash
# ANATOMY DRIVER for the ce/ce_half PHASE-SPLIT wave.
#
# The `sw/run_adcone_anatomy.sh` / `sw/run_intcone_anatomy.sh` driver, aimed at
# the BINDING `ce -> ce` cone itself.  Replicates `quartus_gate.py --seeds`
# exactly -- ONE pre-flow, ONE `quartus_map`, then
# `quartus_fit --seed=S --recompile=off` per seed -- and runs
# `sta_phase_split_scan.tcl` plus `sta_truefmax_probe.tcl` after each fit.
#
# ⚠ IT IS NOT A GATE AND IT WRITES NO RECEIPT.  The quotable Fmax numbers come
# from `sw/quartus_gate.py`; this driver exists only because the gate deletes
# each fit's `db` before the next one and an anatomy needs the fitted netlist.
#
# The `truefmax` leg is here because the anatomy's premise -- that the binding
# class is `SAME` at k=2 -- is a CLAIM about the draw, and a claim measured on
# one tree and quoted against another is what `standing_gates.md` §A exists to
# forbid.  Every draw re-measures it.
#
#   sw/run_phase_split_anatomy.sh <outdir> [--retention] <seed> [<seed> ...]
set -e
Q="$HOME/intelFPGA_lite/17.1/quartus/bin"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$1"; shift
MACRO=""
LABEL="CONTROL"
if [ "$1" = "--retention" ]; then
    MACRO="--verilog_macro=X1_AD_RETENTION=1"; LABEL="RETENTION"; shift
fi
mkdir -p "$ROOT/$OUT"

# single-writer guard (distribution gate §12): match stage binaries by EXACT
# name, never by argv -- `pgrep -f` would match this script itself.
for b in quartus_map quartus_fit quartus_sta quartus_asm; do
    if pgrep -x "$b" >/dev/null 2>&1; then
        echo "REFUSING: $b is already running -- two writers on one hdl/db" >&2
        exit 9
    fi
done

# the tree this measures, recorded beside the numbers: a scan with no commit
# id is not quotable (`standing_gates.md`'s receipt requirement, in spirit --
# this is not a receipt, so the id is written by hand and by rule).
{
    echo "configuration_requested: $LABEL"
    echo "verilog_macro: ${MACRO:-<none>}"
    echo "git_head: $(cd "$ROOT" && git rev-parse HEAD)"
    echo "git_dirty_tracked_hdl: $(cd "$ROOT" && git status --porcelain hdl/ | grep -v '^??' | wc -l)"
    echo "seeds: $*"
    echo "started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$ROOT/$OUT/run.txt"

cd "$ROOT/hdl"
rm -rf db incremental_db
"$Q/quartus_sh" -t sys/build_id.tcl preflow nec_test nec_test_ucore
# shellcheck disable=SC2086
"$Q/quartus_map" $MACRO nec_test -c nec_test_ucore > "$ROOT/$OUT/map.log" 2>&1
echo "MAP done ($LABEL)"

for S in "$@"; do
    "$Q/quartus_fit" --seed="$S" --recompile=off nec_test -c nec_test_ucore \
        > "$ROOT/$OUT/fit$S.log" 2>&1
    "$Q/quartus_sta" nec_test -c nec_test_ucore > "$ROOT/$OUT/sta$S.log" 2>&1
    cp output_files_ucore/nec_test_ucore.sta.summary "$ROOT/$OUT/seed$S.sta.summary"
    grep -E "Fitter Initial Placement Seed" \
        output_files_ucore/nec_test_ucore.fit.rpt | head -2 \
        > "$ROOT/$OUT/seed$S.seedecho.txt" || true
    "$Q/quartus_sta" -t "$ROOT/sw/sta_truefmax_probe.tcl" \
        nec_test nec_test_ucore "$ROOT/$OUT/seed$S" \
        > "$ROOT/$OUT/truefmax$S.log" 2>&1 || echo "truefmax rc=$? seed $S"
    "$Q/quartus_sta" -t "$ROOT/sw/sta_phase_split_scan.tcl" \
        nec_test nec_test_ucore "$ROOT/$OUT/seed$S" 50 \
        > "$ROOT/$OUT/scan$S.log" 2>&1 || echo "SCAN rc=$? seed $S  (a CONTROL FAILURE exits 4)"
    echo "SEED $S done"
done
echo "completed: $(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ROOT/$OUT/run.txt"
echo "ALL DONE ($LABEL)"
