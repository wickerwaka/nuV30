#!/usr/bin/env python3
"""gen_ucore_qsf -- RETIRED 2026-09-19 (WAVE 21).  IT DERIVED THE ucore
REVISION FROM THE FSM ONE, AND THERE IS NO FSM ONE.

It wrote `hdl/nec_test_ucore.qsf` from `hdl/nec_test.qsf` by changing exactly
two lines, and it was bar **E1** of `sw/quartus_gate.py` -- the gate on every
RTL landing and every flash in this project.  Its bar text, verbatim from
FLASH #23's own CONTROL receipt:

    "hdl/nec_test_ucore.qsf is a faithful derivative of hdl/nec_test.qsf"

**THAT SENTENCE MAKES THE ARCHIVED FSM REVISION THE ORIGINAL.**  Under the user
ruling of 2026-09-19 -- *"Ucore is the only valid implementation in this code
base, if it has dependencies on any other implementations those need to be
removed.  Documentation that gives those other implementations precedence is
suspect."* -- that precedence is inverted, so the claim is VOID rather than
merely unmeasurable.  `hdl/nec_test.qsf` and `hdl/files.qip` are deleted,
`hdl/nec_test_ucore.qsf` is AUTHORED, and there is ONE revision.

⚠ **AND IT WAS NOT THE BLOCKER THE BRIEF SAID IT WAS.**  `derive()` was pure
text substitution on ONE settings file: it never opened `hdl/files.qip` and
never read `hdl/rtl/core/`.  **MEASURED: it ran GREEN with the entire FSM core
deleted** (`fsm_removal_results_2026-09-19.md` §Z-4a).  The re-basing was a
deliberate act under the ruling, not a repair forced by the deletion.

WHAT REPLACED IT, AND WHAT DID NOT
----------------------------------
`sw/qsf_lint.py --check` is bar E1 now, receipt key `E1_qsf_canonical`.  It
proves the ONE revision is in CANONICAL FORM -- that no build's in-place Quartus
rewrite was left in the tree.  **The other half of the old bar -- "the two A/B
bitstreams differ by the CORE and nothing else" -- IS RETIRED AND NOTHING
REPLACES IT**, because there is no second core and no second revision for it to
be about.

The POST-BUILD RESTORE this file used to perform (`sw/quartus_gate.py` ran it
with no arguments after every compile, because Quartus rewrites the revision
.qsf it reads) is now done INSIDE `quartus_gate.py`, from bytes it stashes
before the build.  That needs no second file and no `git`.

`docs/notes/invalidation_ledger.md` **RET-2**.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fsmcore                                              # noqa: E402

fsmcore.refuse(
    "sw/gen_ucore_qsf.py -- it derived hdl/nec_test_ucore.qsf from "
    "hdl/nec_test.qsf, the ARCHIVED FSM core's revision.  There is one "
    "revision now and it is AUTHORED.  Bar E1 is `sw/qsf_lint.py --check`")
