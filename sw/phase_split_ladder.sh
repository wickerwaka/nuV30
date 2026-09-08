#!/bin/bash
# WAVE 2 (ce/ce_half phase split) -- the P-6 ladder, run identically on the
# BEFORE and AFTER trees.  $1 = output directory.
set -u
OUT="$1"; mkdir -p "$OUT"
export TMPDIR="$HOME/.cache/ucsimt-tmp"
run () { n="$1"; shift; echo "### $n"; ( time "$@" ) > "$OUT/$n.log" 2>&1; echo "$n rc=$?" | tee -a "$OUT/_rc.txt"; }

run r7_lint            python3 sw/r7_lint.py
run ss_lint            python3 sw/ss_lint.py --core ucore
run cc_all             python3 sw/check_core.py --core ucore --opcodes all --cases 0
run cc_8f0             python3 sw/check_core.py --core ucore --opcodes 8F.0 --cases 0
run hlt_w0             python3 sw/check_core.py --core ucore --suite-dir tests/v30/s10-hltsweep-w0 --opcodes all --cases 0 --waits 0
run hlt_w1             python3 sw/check_core.py --core ucore --suite-dir tests/v30/s10-hltsweep-w1 --opcodes all --cases 0 --waits 1
run hlt_w2             python3 sw/check_core.py --core ucore --suite-dir tests/v30/s13-hltsweep-w2 --opcodes all --cases 0 --waits 2
run hlt_w3             python3 sw/check_core.py --core ucore --suite-dir tests/v30/s13-hltsweep-w3 --opcodes all --cases 0 --waits 3
run v01_w1             python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w1 --opcodes all --cases 0 --waits 1
run v01_w3             python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w3 --opcodes all --cases 0 --waits 3
run v01_w1_EB          python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w1 --opcodes EB --cases 0 --waits 1
run evt_w0             python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w0evt --opcodes all --cases 0 --waits 0
run evt_w1             python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w1evt --opcodes all --cases 0 --waits 1
run evt_w2             python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w2evt --opcodes all --cases 0 --waits 2
run evt_w3             python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w3evt --opcodes all --cases 0 --waits 3
run evt_biased         python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1-w1evt-biased --opcodes all --cases 0 --waits 1
run ulockstep          python3 sw/ulockstep.py --golden all --cases 50
run ghost_launch       python3 sw/ghost_launch_law.py score
run check_boot         python3 sw/check_boot.py --core ucore
run check_boot400      python3 sw/check_boot.py 400 --core ucore
run check_ab_sim       python3 sw/check_ab_sim.py --core ucore
run s16                python3 sw/sm3_s16_score.py --core ucore
run demux_off          python3 sw/demux_off_gate.py
run test_artifact      python3 sw/test_artifact.py
run test_quartus_gate  python3 sw/test_quartus_gate.py
run ucrom_mif          python3 sw/ucrom_mif_check.py
run chain_lfsr         python3 sw/chain_lfsr_gate.py
run tbsys_build        python3 sw/x1_retention.py build --leg ret
run fz2_replay         python3 sw/fz2_replay.py --all-failures --pass-sample 200 --leg ret --no-fabric-era-guard --jobs 6 --out "$OUT/fz2_replay.json"
# P-7 divisor independence
run cc_all_div2        python3 sw/check_core.py --core ucore --opcodes all --cases 0 --ce-div 2
run cc_all_div3        python3 sw/check_core.py --core ucore --opcodes all --cases 0 --ce-div 3
run cc_all_div8        python3 sw/check_core.py --core ucore --opcodes all --cases 0 --ce-div 8
run cc_div1_refused    python3 sw/check_core.py --core ucore --opcodes all --cases 0 --ce-div 1
echo "LADDER DONE"
