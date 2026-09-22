#!/usr/bin/env bash
# WAVE 29 -- the offline ladder, run leg by leg into its own log.
#
# EVERY LEG's RC IS CAPTURED WITH ${PIPESTATUS[0]}, NEVER `tail`'s.
# The leg set is WAVE 28's 38 legs, PLUS this wave's own new gate
# (`truth_stamp_lint`), which is the ONE new leg this wave registers.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.." || exit 1
OUT="${1:?usage: w29_ladder.sh <outdir>}"
mkdir -p "$OUT"
: > "$OUT/rc.txt"

run() {           # run <legname> <cmd...>
    local leg="$1"; shift
    echo "== $leg: $*" >&2
    "$@" > "$OUT/$leg.log" 2>&1
    local rc=$?
    echo "$leg RC=$rc" >> "$OUT/rc.txt"
    echo "   $leg RC=$rc" >&2
}

CC="python3 sw/check_core.py --core ucore"

run v01_div4  $CC --opcodes all --cases 0 --ce-div 4
run v01_div2  $CC --opcodes all --cases 0 --ce-div 2
run v01_div3  $CC --opcodes all --cases 0 --ce-div 3
run v01_div8  $CC --opcodes all --cases 0 --ce-div 8
run v01_div1  $CC --opcodes all --cases 0 --ce-div 1
run hlt_w0    $CC --suite-dir tests/v30/s10-hltsweep-w0 --opcodes all --cases 0 --waits 0
run hlt_w1    $CC --suite-dir tests/v30/s10-hltsweep-w1 --opcodes all --cases 0 --waits 1
run hlt_w2    $CC --suite-dir tests/v30/s13-hltsweep-w2 --opcodes all --cases 0 --waits 2
run hlt_w3    $CC --suite-dir tests/v30/s13-hltsweep-w3 --opcodes all --cases 0 --waits 3
run v03       $CC --suite-dir tests/v30/v0.3 --opcodes all --cases 0
run v20suite  $CC --suite-dir tests/v30/v20suite --opcodes all --cases 0 --arch-only
run x_mod3    $CC --suite-dir tests/v30/mod3_illegal --opcodes all --cases 0
run x_w1      $CC --suite-dir tests/v30/v0.1-w1 --opcodes all --cases 0 --waits 1
run x_w3      $CC --suite-dir tests/v30/v0.1-w3 --opcodes all --cases 0 --waits 3
run x_w1_EB   $CC --suite-dir tests/v30/v0.1-w1 --opcodes EB --cases 0 --waits 1
run x_f4a     $CC --suite-dir tests/v30/f4a_boundary --opcodes all --cases 0
run x_f0lock  $CC --suite-dir tests/v30/f0lock_tranche --opcodes all --cases 0
run boot220   python3 sw/check_boot.py --core ucore 220
run boot400   python3 sw/check_boot.py --core ucore 400
run ab_sim    python3 sw/check_ab_sim.py --core ucore
run ghost_law python3 sw/ghost_launch_law.py score
run lea_mod3  python3 sw/lea_mod3_gate.py
run chainlfsr python3 sw/chain_lfsr_gate.py
run chainflat python3 sw/chainflat_relocation_check.py
run demux_off python3 sw/demux_off_gate.py
run r7_lint   python3 sw/r7_lint.py
run ss_lint   python3 sw/ss_lint.py --core ucore
run cutset    python3 sw/cutset_lint.py
run phasespl  python3 sw/phase_split_lint.py
run artifact  python3 sw/test_artifact.py
run quartusg  python3 sw/test_quartus_gate.py
run qsf_lint  python3 sw/qsf_lint.py --check
run portlist  python3 sw/core_portlist_lint.py
run ucrom_mif python3 sw/ucrom_mif_check.py
run g0_tables python3 sw/check_ucore_tables.py
run pla3      python3 sw/pla3_check.py
run suitemeta python3 sw/suitemeta.py --selfcheck
run w27_archive python3 sw/w27_v02_archive_check.py
run truthstamp python3 sw/truth_stamp_lint.py

echo "LADDER DONE" >> "$OUT/rc.txt"
echo "LADDER DONE" >&2
