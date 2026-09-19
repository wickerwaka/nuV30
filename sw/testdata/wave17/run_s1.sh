#!/bin/bash
# WAVE 17 -- S-1.  BOTH no-exception sweeps, STRICTLY SEQUENTIAL behind the
# single-writer guard, so no two Quartus stages can race.  `set -u`, NEVER
# `set -e`: quartus_gate exits non-zero on RED and a RED verdict is a RESULT.
set -u
cd /home/wickerwaka/src/nec_test
bash sw/run_wave17_g6.sh /home/wickerwaka/src/nec_test w17-split-presel-noexc control
bash sw/run_wave17_g6.sh /home/wickerwaka/src/nec_test w17-split-presel-noexc retention
echo "WAVE 17 S-1: BOTH SWEEPS DONE $(date -u +%FT%TZ)"
