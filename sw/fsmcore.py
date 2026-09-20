#!/usr/bin/env python3
"""fsmcore -- THE ARCHIVED FSM CORE IS RETIRED.  THIS FILE IS THE DECLARATION.

`hdl/rtl/core/` -- the trace-fitted V30 core, archived 2026-08-04 and removed
from the working tree by WAVE 21 on 2026-09-19 -- is GONE.  This module exists
for the same reason `sw/simbin.py` survived RET-1: so that a tool which bound
the removed artifact dies with a SENTENCE naming the decision, instead of a
`FileNotFoundError`, a Verilator `%Error-PINNOTFOUND`, or -- worst of all --
silently scoring against a stale binary left in `hdl/tb/obj_dir/`.

    THE RULE (RET-1, restated): NO GATE DIES SILENTLY AND NONE DIES WITH A
    `FileNotFoundError`.

USER INSTRUCTION 2026-09-19, verbatim:
    "Remove the FSM core, fix whatever dependencies exist"

USER RULING 2026-09-19, verbatim, which widened it:
    "Ucore is the only valid implementation in this code base, if it has
    dependencies on any other implementations those need to be removed.
    Documentation that gives those other implementations precedence is
    suspect."

The ledger entry is `docs/notes/invalidation_ledger.md` **RET-2**, and it
carries every retired gate with its LAST REGISTERED FIGURE.  `git rm` keeps
history: NOTHING WAS DESTROYED, and the recovery commands are in the entry and
in `RECOVER` below.

⚠ A NOTE ON FIGURES, because this is how a retirement becomes a lie.  The
figures the retired gates carried are the FSM CORE's.  A tool re-pointed at the
`ucore` is a DIFFERENT MEASUREMENT and may NOT inherit them -- RE-REGISTER,
NEVER RE-LABEL (RET-1's falsifier #3).
"""

RET = "docs/notes/invalidation_ledger.md  RET-2"

RECOVER = """\
  git checkout fb9365c01c -- hdl/rtl/core/ hdl/files.qip hdl/nec_test.qsf
  git checkout fb9365c01c -- sw/gen_ucore_qsf.py sw/race_law_equiv_tb.sv
  git checkout fb9365c01c -- sw/check_core.py sw/check_seq.py
  python3 sw/check_core.py --build --core fsm"""


class FsmCoreRetired(RuntimeError):
    """Raised by every verb that needed the archived FSM core."""


def banner(who):
    return (
        f"\nFSM CORE RETIRED -- {who}\n"
        f"\n"
        f"  hdl/rtl/core/ was removed from the working tree by WAVE 21 on\n"
        f"  2026-09-19, under the user instruction \"Remove the FSM core, fix\n"
        f"  whatever dependencies exist\".  The ucore\n"
        f"  (hdl/rtl/ucore/) is the project's only implementation.\n"
        f"\n"
        f"  ledger:   {RET}\n"
        f"  archive:  docs/notes/fsm_core_archive_2026-08-04.md (now HISTORY)\n"
        f"  wave:     docs/notes/fsm_removal_prereg_2026-09-19.md\n"
        f"            docs/notes/fsm_removal_results_2026-09-19.md\n"
        f"\n"
        f"  nothing was destroyed -- `git rm` keeps history.  to recover:\n"
        f"{RECOVER}\n"
        f"\n"
        f"  ⚠ any figure this tool used to print is an FSM figure.  A ucore\n"
        f"    leg is a DIFFERENT MEASUREMENT: re-register, never re-label.\n"
    )


def retired(who):
    """Raise.  `who` names the caller so the message says what was refused."""
    raise FsmCoreRetired(banner(who))


def refuse(who, code=2):
    """Print the banner and exit `code` (default 2 = CANNOT MEASURE).

    For a `main()` that should say NO rather than traceback."""
    import sys
    print(banner(who), file=sys.stderr)
    raise SystemExit(code)


if __name__ == "__main__":
    refuse("sw/fsmcore.py is a declaration, not a tool")
