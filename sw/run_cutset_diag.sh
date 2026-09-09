#!/bin/bash
# WAVE 4 -- C-3(b) / C-8's DIAGNOSIS LEG.  It re-maps and re-fits ONE CONTROL
# draw and runs `sw/sta_cutset_diag.tcl` on THAT netlist.
#
# ⚠ WHY A FRESH FIT AND NOT THE `db` THE SWEEP LEFT BEHIND.  The sweep runs
# CONTROL then RETENTION back to back, so the surviving `db` is the RETENTION
# sweep's LAST seed -- a different configuration and a different seed from the
# CONTROL draw the wave quotes.  Diagnosing one netlist and quoting another is
# how a diagnosis stops being about the thing it names.  $1 = seed (default 3,
# the worst CONTROL draw), $2 = output file.
#
# ⚠ IT IS A PROBE AND NOT A GATE: it writes no receipt, and no Fmax may be
# quoted from it.  The quotable figures come from `sw/quartus_gate.py`.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/hdl"
SEED="${1:-3}"
OUT="${2:-sw/testdata/cutset/diag_ctl_seed${SEED}.txt}"
Q="$(dirname "$(command -v quartus_sh)")"

for b in quartus_map quartus_fit quartus_sta quartus_asm quartus_sh; do
    while pgrep -x "$b" >/dev/null 2>&1; do sleep 30; done
done

"$Q/quartus_map" nec_test -c nec_test_ucore                       || exit 1
"$Q/quartus_fit" --seed="$SEED" --recompile=off nec_test -c nec_test_ucore || exit 1
"$Q/quartus_sta" -t "$ROOT/sw/sta_cutset_diag.tcl" nec_test nec_test_ucore "$ROOT/$OUT"
echo "diag written to $OUT"
