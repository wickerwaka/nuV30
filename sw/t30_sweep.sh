#!/usr/bin/env bash
# t30_sweep.sh - full standing sweep gate before the task #30 reflash (RR-era
# bar for EU decode-path changes). Runs all lints + standing gates + every
# golden suite against the current RTL. Any non-full suite total or failed
# gate = regression. Detached, logged.
#
# *** THIS IS THE ARCHIVED FSM CORE'S SWEEP (2026-08-04). ***
# Every leg below is FSM-structural: check_race_law / ea_step_lint /
# prefix_clear_lint / check_ff_t4 / check_mod3_illegal all read or mutate
# hdl/rtl/core/*.sv and have no ucore counterpart.  `--core fsm` and
# `--core fsm` on ss_lint are now passed EXPLICITLY so this script keeps its
# meaning after check_core.py's default flipped fsm -> ucore on 2026-08-04.
# It is an ON-DEMAND gate (run before re-activating the FSM core), not part of
# the standing set.  See docs/notes/fsm_core_archive_2026-08-04.md and
# docs/notes/standing_gates.md.
#
# NOTE: the FSM core's v0.1 total on the CORRECTED comparator (the TB's
# composed-AD mask removed at U5) is 168,400/169,000, not 169,000 - the 600
# HLT.INT/HLT.RES/HLT.NMI cases are 0/600 (F51, unfixed here). "Any non-full
# suite total = regression" must be read against that, not against 169,000.
#
# ⚠⚠ 2026-09-19 — THIS SWEEP COULD NOT FAIL, AND DID NOT FOR OVER A YEAR OF
# INVOCATIONS.  Every leg was `cmd 2>&1 | tail -1`: no `rc` captured, nothing
# aggregated, and NO `exit` anywhere that depended on a leg's result.  `set -uo
# pipefail` was present WITHOUT `-e`, so `pipefail` accomplished nothing —
# nothing ever tested `$?`.  The script's status was `tail`'s, which always
# succeeds, and it printed "DONE" unconditionally.  A leg that FAILED, or that
# CRASHED OUTRIGHT (three do, as of this date), produced a line and the sweep
# still exited 0.  Line 4's own "Any non-full suite total or failed gate =
# regression" was an INTENT THE SCRIPT DID NOT IMPLEMENT — the
# comment-is-not-a-gate pattern `sw/r7_lint.py` exists for.
# Found by WAVE 18 (`docs/notes/*wave18*`), which hit the identical
# `| tail -1; rc=$?` mistake in its own reporting and caught it with a control.
#
# ⚠ THE LIMIT OF THIS REPAIR, STATED RATHER THAN IMPLIED: it aggregates EXIT
# CODES.  A leg that exits 0 while PRINTING a failing total is still not
# caught.  Line 4's rule is about suite TOTALS; this is about exit status.
# Booked, not taken.
# --------------------------------------------------------------------------- #
# ⚠⚠ WAVE 21, 2026-09-19 -- THIS SWEEP IS RETIRED.  IT IS THE ARCHIVED FSM
# CORE'S REGRESSION SWEEP, AND `hdl/rtl/core/` NO LONGER EXISTS IN THIS TREE.
#
# USER INSTRUCTION 2026-09-19: "Remove the FSM core, fix whatever dependencies
# exist".  Every leg below is FSM-structural or `--core fsm`, and each of those
# tools now REFUSES BY NAME (`sw/fsmcore.py`).  Running them would print
# fourteen identical refusals; this script says it ONCE instead.
#
# ITS LAST REGISTERED FIGURE, and it is not a green one: measured 2026-09-19 by
# WAVE 18, the sweep correctly reports FAILED because three of its legs
# (`check_ff_t4`, `check_mod3_illegal`, and `check_enter_nesting` as a RED) are
# v1-anchor casualties -- `staleness_audit_2026-09-19.md` §4.  Its per-leg
# BEFORE figures, measured on 2026-09-20 immediately before the removal, are in
# `docs/notes/invalidation_ledger.md` RET-2.
#
# NOT DELETED: a refusal that names the decision is readable; a missing script
# is not.  The v0.1 / v0.3 / f4a / f0lock suites it swept are UNAFFECTED and are
# still swept against the ucore by `sw/check_core.py` (the standing ladder).
# --------------------------------------------------------------------------- #
SW="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -c "import sys; sys.path.insert(0, sys.argv[1]); import fsmcore; \
fsmcore.refuse(\"sw/t30_sweep.sh -- the ARCHIVED FSM core's regression sweep\")" "$SW"

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
echo "=== T30 full standing sweep  $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="

NLEG=0
NFAIL=0
FAILLIST=""

step() { echo; echo "### $*"; }

# leg <name> <cmd...> -- run it, print its verdict LINE, and keep its REAL exit
# code.  The output is captured into a variable so `$?` is the TOOL's, never
# `tail`'s.  That distinction is the whole point of this function.
leg() {
    local name="$1"; shift
    local out rc
    out="$("$@" 2>&1)"; rc=$?
    printf '%s\n' "$out" | tail -1
    NLEG=$((NLEG + 1))
    if [ "$rc" -ne 0 ]; then
        printf '  ^^ LEG FAILED: %s (exit %d)\n' "$name" "$rc"
        NFAIL=$((NFAIL + 1))
        FAILLIST="${FAILLIST}    - ${name} (exit ${rc})"$'\n'
    fi
}

step "lints"
leg "ss_lint --core fsm" python3 sw/ss_lint.py --core fsm
leg "prefix_clear_lint" python3 sw/prefix_clear_lint.py 
leg "ea_step_lint" python3 sw/ea_step_lint.py      
leg "check_race_law" python3 sw/check_race_law.py    
leg "optable --selfcheck" python3 sw/optable.py --selfcheck
leg "fuzz_campaign lint" python3 sw/fuzz_campaign.py lint --n 10000 --raw-n 100000

step "standing gates"
leg "check_ff_t4" python3 sw/check_ff_t4.py       
leg "check_mod3_illegal" python3 sw/check_mod3_illegal.py

step "v0.1 w0 (169k, all forms)"
leg "v0.1 w0" python3 sw/check_core.py --core fsm --suite-dir tests/v30/v0.1 --opcodes all --cases 0 --waits 0
step "v0.1-w1"
leg "v0.1-w1" python3 sw/check_core.py --core fsm --suite-dir tests/v30/v0.1-w1 --opcodes all --cases 0 --waits 1
step "v0.1-w3"
leg "v0.1-w3" python3 sw/check_core.py --core fsm --suite-dir tests/v30/v0.1-w3 --opcodes all --cases 0 --waits 3
step "f0lock_tranche"
leg "f0lock_tranche" python3 sw/check_core.py --core fsm --suite-dir tests/v30/f0lock_tranche --opcodes all --cases 0 --waits 0
step "f4a_boundary"
leg "f4a_boundary" python3 sw/check_core.py --core fsm --suite-dir tests/v30/f4a_boundary --opcodes all --cases 0 --waits 0
step "v0.3 w0 (3.7M, all forms)"
leg "v0.3 w0" python3 sw/check_core.py --core fsm --suite-dir tests/v30/v0.3 --opcodes all --cases 0 --waits 0

echo
if [ "$NFAIL" -ne 0 ]; then
    echo "=== T30 sweep FAILED: $NFAIL of $NLEG legs did not exit 0  $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
    printf '%s' "$FAILLIST"
    exit 1
fi
echo "=== T30 sweep PASS: all $NLEG legs exit 0  $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
