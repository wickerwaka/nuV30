#!/bin/bash
# WAVE 16 -- R-3's FOUR NO-EXCEPTION SWEEPS, STRICTLY SEQUENTIAL behind the
# single-writer guard, launched ONCE so that no two Quartus stages can race and
# so that the wave does not poll a turn per sweep.
# `set -u`, NEVER `set -e`: every one of these sweeps is REGISTERED to draw RED.
set -u
MAIN=/home/wickerwaka/src/nec_test
W=$HOME/.cache/ucsimt-tmp/wave16
guard () {
    for b in quartus_map quartus_fit quartus_sta quartus_asm quartus_sh; do
        while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
    done
}
# wait out R-2 in the main tree first
until grep -q 'WAVE 16 SWEEP w16-presel-withexc: DONE' "$HOME/.cache/ucsimt-tmp/w16_r2.out" 2>/dev/null; do sleep 30; done
guard
bash "$MAIN/sw/run_wave16_g6.sh" "$W/wt_base_noexc"   w16-base-noexc   both > "$HOME/.cache/ucsimt-tmp/w16_r3_base.out"   2>&1
guard
bash "$MAIN/sw/run_wave16_g6.sh" "$W/wt_presel_noexc" w16-presel-noexc both > "$HOME/.cache/ucsimt-tmp/w16_r3_presel.out" 2>&1
echo "WAVE 16 R-3: ALL FOUR NO-EXCEPTION SWEEPS DONE  $(date -u +%FT%TZ)"
