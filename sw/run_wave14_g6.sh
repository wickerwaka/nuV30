#!/bin/bash
# WAVE 14 -- THE ONE DRIVER FOR ALL THREE ARMS.
#
#   $1 = the arm's WORKTREE ROOT (a scratch git worktree under
#        ~/.cache/ucsimt-tmp/wave14/ -- the MAIN tree is never built in)
#   $2 = the arm's tag, e.g. `w14-base` / `w14-tie` / `w14-hold`
#   $3 = half selector: both (default) / control / retention
#
# ⚠ THE THREE ARMS MUST BE DRAWN BY THIS SCRIPT AND ONLY BY THIS SCRIPT, at the
# SAME seed set {1,2,3,4,5}, BOTH configurations.  A difference in driver, flags
# or seed set between arms is exactly the contamination class WAVE 11 found and
# WAVE 12 removed, and WAVE 13's N-3 is the precedent for how the pair is drawn.
#
# ⚠ `set -u`, NEVER `set -e`: `quartus_gate.py` EXITS NON-ZERO ON A RED VERDICT
# and every arm of this wave is expected to draw RED (the split tree is 1.47 /
# 0.85 MHz short).  WAVE 13 lost half a sweep to `set -e` and recorded it.
#
# THE SINGLE-WRITER GUARD IS BY EXACT BINARY NAME, ONE PATTERN PER `pgrep -x`
# CALL -- `pgrep -x a b` is an ERROR whose failure branch reads as "idle".
# ⚠ `pgrep -f <script>` SELF-MATCHES the waiting shell and is never used here.
#
# `hdl/nec_test_ucore.qsf` is restored with `git checkout -- <that exact path>`
# around every Quartus run (the declared §70.7 exemption; `quartus_map` rewrites
# it).  NEVER a bare `git checkout`.
#
# AFTER each sweep the netlist the last fit left behind is measured by the two
# COMMITTED instruments, neither of them written for this wave:
#   sw/sta_cutset_diag.tcl     -- WAVE 4/9's STAGE 1 (* -> s1q) / STAGE 2
#                                 (s1q -> *) anatomy and the EU->BIU->EU
#                                 round-trip detector.  P-3's evidence.
#   sw/sta_biu_roundtrip.tcl   -- WAVE 10's census with PC-W1..PC-W5.  P-1.
# ⚠ `sw/sta_phase_split_diag.tcl` IS NOT USED: it is committed UNRUNNABLE
# (a trailing `#` comment on a `set` line; Tcl has no such comment), which
# WAVE 4 measured and recorded in `sta_cutset_diag.tcl`'s own header.
set -u
MAIN="$(cd "$(dirname "$0")/.." && pwd)"
ARM="$1"; TAG="$2"; HALF="${3:-both}"
QB="$HOME/intelFPGA_lite/17.1/quartus/bin"
OUT="$ARM/sw/testdata/wave14/$TAG"
mkdir -p "$OUT"
cd "$ARM" || exit 2

case "$ARM" in
  "$HOME/.cache/ucsimt-tmp/wave14/"*) : ;;
  *) echo "REFUSING: $ARM is not a scratch worktree under ~/.cache/ucsimt-tmp/wave14/"; exit 2 ;;
esac

guard () {
    for b in quartus_map quartus_fit quartus_sta quartus_asm quartus_sh; do
        while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
    done
}

anatomy () {   # $1 = cfg
    local cfg="$1"
    guard
    local seedrow
    seedrow="$(grep -m1 'Fitter Initial Placement Seed' \
        hdl/output_files_ucore/nec_test_ucore.fit.rpt 2>/dev/null)"
    echo "ANATOMY $TAG $cfg on the netlist left by: ${seedrow:-*** NO SEED ROW ***}"
    echo "${seedrow:-NO SEED ROW}" > "$OUT/anatomy_${cfg}.seedecho.txt"
    ( cd hdl && "$QB/quartus_sta" -t "$MAIN/sw/sta_cutset_diag.tcl" \
        nec_test nec_test_ucore "$OUT/cutset_diag_${cfg}.txt" ) \
        > "$OUT/cutset_diag_${cfg}.log" 2>&1
    echo "  sta_cutset_diag rc=$?"
    guard
    ( cd hdl && "$QB/quartus_sta" -t "$MAIN/sw/sta_biu_roundtrip.tcl" \
        nec_test nec_test_ucore "$OUT/roundtrip_${cfg}" 200 400 ) \
        > "$OUT/roundtrip_${cfg}.log" 2>&1
    echo "  sta_biu_roundtrip rc=$?"
    git checkout -- hdl/nec_test_ucore.qsf
}

sweep () {   # $1 = cfg, $2 = extra flag
    local cfg="$1" extra="$2"
    guard
    git checkout -- hdl/nec_test_ucore.qsf
    # shellcheck disable=SC2086
    python3 sw/quartus_gate.py --seeds 5 $extra --label "$TAG-$cfg-n5" \
        --log "$OUT/g6_${cfg}_n5.log" \
        || echo "quartus_gate $cfg rc=$? (RED is a result, not an error)"
    git checkout -- hdl/nec_test_ucore.qsf
    anatomy "$cfg"
}

echo "=== WAVE 14 $TAG   root=$ARM   half=$HALF   $(date -u +%FT%TZ) ==="
git -C "$ARM" rev-parse HEAD
git -C "$ARM" status --porcelain hdl/ | grep -v '^??'

if [ "$HALF" = both ] || [ "$HALF" = control ];   then sweep control   ""            ; fi
if [ "$HALF" = both ] || [ "$HALF" = retention ]; then sweep retention "--retention" ; fi

echo "WAVE 14 ARM $TAG: DONE  $(date -u +%FT%TZ)"
