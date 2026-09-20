#!/usr/bin/env python3
"""simbin -- THE C++ MODEL IS RETIRED.  THIS MODULE IS ITS HEADSTONE.

    RETIRED 2026-09-19 (WAVE 20), by USER DIRECTIVE:
        "The old C model has not been maintained, remove it."

    The register entry is `docs/notes/invalidation_ledger.md` **RET-1** --
    what went, why, every gate that died with it, and how to get it back.

WHY THIS FILE STILL EXISTS, AND WHY IT IS NOT A `git rm`.

`sw/simbin.py` was the SINGLE DECLARATION of what `sim/build/v30sim` was a
function of, and **134 tools in `sw/` reach it by import** -- 37 directly and
97 transitively.  Four of the transitive importers are LIVE STANDING GATES
that never touch the model (`check_fuzz_bank`, `fz2_replay`, `fz2_w1`,
`ghost_launch_law`); deleting this module would kill them at `import`, for a
reason that has nothing to do with what they measure.  So the single
declaration survives the artifact it declared, and now declares its
retirement instead.

**THE RULE THIS FILE ENFORCES: NO GATE DIES SILENTLY, AND NONE DIES WITH A
`FileNotFoundError`.**  Every entry point below raises `ModelRetired` -- one
sentence naming the directive, the ledger entry and the recovery command.  A
tool that used the model now says so; it does not stack-trace three frames
down inside `subprocess`.

WHAT WAS RETIRED, MEASURED
    39 tracked files, 491,759 bytes, 10,089 lines of C++ in 36 sources.
    Last source change `be4eb2c32f` (2026-08-17) -- and the ucore took a
    functional fix the model never got (`c59d205479`, 2026-08-20, "Fix REP
    termination before interrupt withdrawal", `hdl/rtl/ucore/` only).  That
    commit is the measured end of "the model is the SPEC".

WHAT REPLACED ITS ONE LOAD-BEARING USE
    GATE G0 (`sw/check_ucore_tables.py`) used the model as the microcode
    ROM's INDEPENDENT REFERENCE.  It now reads a FROZEN SNAPSHOT of
    `v30sim dump-tables` -- `sw/testdata/g0-tables/` -- hashed against the
    ROM it describes, and REFUSES (exit 2) rather than scoring if that ROM
    moves.  G0 still reports 9,988 entries identical on both legs.

HOW TO GET THE MODEL BACK -- nothing was destroyed, `git rm` keeps history

    git checkout be4eb2c32f930e12575da5a6359b4fead3c28f96 -- sim/
    git checkout <the commit before RET-1> -- sw/simbin.py
    python3 sw/simbin.py --build

The file this replaced is that same commit's `sw/simbin.py`; read it there
for the receipt-layer declaration (§A-§C) rather than reconstructing it.
"""
import argparse
import sys
from pathlib import Path

SW = Path(__file__).resolve().parent
ROOT = SW.parent
sys.path.insert(0, str(SW))

SIMDIR = ROOT / "sim"
BUILD = SIMDIR / "build"

# Kept as a PATH CONSTANT and nothing more.  Six modules bind `SIM =
# simbin.SIM` at import time (`check_boot`, `timed_gate`, `ulockstep`,
# `qdepth_probe`, `s13_board`, `ucsim_coverage_report`); a module-level
# `__getattr__` that raised here would kill `ghost_launch_law` -- a live gate
# that never runs the model -- at import.  The refusal belongs on the verbs.
SIM = BUILD / "v30sim"
ROM = ROOT / "docs" / "V20BITS.TXT"
GOLDEN = ROOT / "docs" / "V20UC.TXT"

RECOVER = "be4eb2c32f930e12575da5a6359b4fead3c28f96"

_MSG = """
  ============================================================
  THE C++ MODEL (`sim/`) IS RETIRED.  {why}
  ============================================================
  RETIRED 2026-09-19 (WAVE 20) by user directive:
      "The old C model has not been maintained, remove it."
  REGISTER : docs/notes/invalidation_ledger.md  RET-1
             -- it names every gate that died with it.
  NOT LOST : `git rm` keeps history.  To restore the model:
                 git checkout {rec} -- sim/
                 git checkout <commit before RET-1> -- sw/simbin.py
                 python3 sw/simbin.py --build
  G0       : the microcode tables keep an independent reference --
             sw/testdata/g0-tables/ (a frozen `v30sim dump-tables`).
  ============================================================"""


class ModelRetired(RuntimeError):
    """Raised by every `simbin` verb.  It is NOT a FileNotFoundError and it is
    NOT an ImportError: a tool that hits this has been told what happened, by
    whom, and how to undo it."""


def _retired(why=""):
    raise ModelRetired(_MSG.format(why=why or "", rec=RECOVER))


# --------------------------------------------------------------------------- #
# the verbs.  Every one of them refuses, and names itself while doing it.
# --------------------------------------------------------------------------- #
def retired(why=""):
    """Explicit refusal, for a tool that resolves the binary by bare path
    instead of through `ensure()`.  Call it first thing in `main()`."""
    _retired(why)


def recipe():
    _retired("`simbin.recipe()` -- there is no artifact left to declare.")


def ensure(why="", force=False, quiet=True):
    _retired(f"`simbin.ensure()` asked for: {why or 'a --core sim scorer'}")


def require_bin(why=""):
    _retired(f"`simbin.require_bin()` asked for: {why or 'a --core sim scorer'}")


def receipt_id():
    _retired("`simbin.receipt_id()` -- the model has no receipt any more.")


def disasm_gate():
    _retired("`simbin --disasm` -- the ROM disasm gate ran IN the model.")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for f in ("--build", "--force", "--require", "--disasm", "--id"):
        ap.add_argument(f, action="store_true")
    ap.parse_args()
    print(_MSG.format(why="Nothing here builds, requires or scores.",
                      rec=RECOVER))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
