#!/bin/bash
# WAVE 19 -- THE ONE DRIVER FOR EVERY SWEEP OF THIS LANDING.  It is
# `sw/run_wave16_g6.sh` with the scratch-worktree REFUSAL relaxed to "the main
# tree OR a scratch worktree under ~/.cache/ucsimt-tmp/wave19/", because THIS
# WAVE IS A LANDING and V-2's no-exception pair is drawn on the landed tree
# itself -- the tree's own SDC ALREADY carries no exception, so there is no SDC
# edit to make and none to keep out of the tree.
#
#   $1 = the sweep's TREE ROOT
#   $2 = the sweep's tag, e.g. `w17-presel-withexc` / `w17-base-noexc`
#   $3 = half selector: both (default) / control / retention
#
# ⚠ EVERY SWEEP OF THIS WAVE IS DRAWN BY THIS SCRIPT AND ONLY BY THIS SCRIPT,
# at the SAME seed set {1,2,3,4,5}, BOTH configurations.  A difference in
# driver, flags or seed set between arms is exactly the contamination class
# WAVE 11 found and WAVE 12 removed.
#
# ⚠ `set -u`, NEVER `set -e`: `quartus_gate.py` EXITS NON-ZERO ON A RED VERDICT
# and R-3's arms are REGISTERED to draw RED.  WAVE 13 lost half a sweep to
# `set -e`.
#
# THE SINGLE-WRITER GUARD IS BY EXACT BINARY NAME, ONE PATTERN PER `pgrep -x`
# CALL -- `pgrep -x a b` is an ERROR whose failure branch reads as "idle".
# ⚠ `pgrep -f <script>` SELF-MATCHES the waiting shell and is never used here.
#
# `hdl/nec_test_ucore.qsf` is restored with `git checkout -- <that exact path>`
# around every Quartus run (the declared §70.7 exemption; `quartus_map`
# rewrites it).  NEVER a bare `git checkout`, NEVER `git checkout .`: 21
# pre-existing modified files in this working tree are the USER'S OWN
# UNCOMMITTED WORK.
set -u
MAIN="$(cd "$(dirname "$0")/.." && pwd)"
ARM="$1"; TAG="$2"; HALF="${3:-both}"
OUT="$ARM/sw/testdata/wave19/$TAG"
mkdir -p "$OUT"
cd "$ARM" || exit 2

case "$ARM" in
  "$MAIN") : ;;
  "$HOME/.cache/ucsimt-tmp/wave19/"*) : ;;
  *) echo "REFUSING: $ARM is neither the main tree nor a scratch worktree under ~/.cache/ucsimt-tmp/wave19/"; exit 2 ;;
esac

guard () {
    for b in quartus_map quartus_fit quartus_sta quartus_asm quartus_sh; do
        while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
    done
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
}

echo "=== WAVE 19 $TAG   root=$ARM   half=$HALF   $(date -u +%FT%TZ) ==="
git -C "$ARM" rev-parse HEAD
echo "--- tracked hdl/ modifications in this tree (must be 0: this wave's SDC is unedited) ---"
git -C "$ARM" status --porcelain hdl/ | grep -v '^??'
echo "--- uncommented timing exceptions in this tree's SDC ---"
grep -cE '^[[:space:]]*set_(multicycle_path|false_path)' "$ARM/hdl/nec_test.sdc"

if [ "$HALF" = both ] || [ "$HALF" = control ];   then sweep control   ""            ; fi
if [ "$HALF" = both ] || [ "$HALF" = retention ]; then sweep retention "--retention" ; fi

echo "WAVE 19 SWEEP $TAG: DONE  $(date -u +%FT%TZ)"
