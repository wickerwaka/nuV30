#!/usr/bin/env python3
"""qsf_lint -- THE ONE QUARTUS REVISION IS IN CANONICAL FORM.

This is bar **E1** of `sw/quartus_gate.py` since WAVE 21 (2026-09-19), receipt
key `E1_qsf_canonical`.  It REPLACES `sw/gen_ucore_qsf.py --check`, whose bar
read

    "hdl/nec_test_ucore.qsf is a faithful derivative of hdl/nec_test.qsf"

-- a sentence that made the ARCHIVED FSM revision the original and the ucore
revision the derivative.  Under the user ruling of 2026-09-19 ("Ucore is the
only valid implementation in this code base") that precedence is inverted, so
the old bar's claim is VOID rather than merely unmeasurable.  `hdl/nec_test.qsf`
and `hdl/files.qip` are deleted; `hdl/nec_test_ucore.qsf` is now AUTHORED and is
the project's only revision.  `docs/notes/fsm_removal_prereg_2026-09-19.md` §2.

--------------------------------------------------------------------------- #
WHAT THIS BAR PROVES
--------------------------------------------------------------------------- #
`hdl/nec_test_ucore.qsf` -- the one revision the compiler reads -- is in
CANONICAL FORM: it carries none of the assignments Quartus MATERIALISES into it
from `source sys/sys.tcl`, and it declares exactly one file list and exactly one
output directory.

That matters because **Quartus REWRITES the revision .qsf it compiles**,
appending everything it picked up from the sourced Tcl (measured on
`hdl/sys/sys.tcl`: 107 `set_location_assignment`, 50 `set_instance_assignment`,
8 `set_global_assignment` including `PRE_FLOW_SCRIPT_FILE`).  So this file MOVES
on every build, by the compiler -- which is why `quartus_gate.INPUT_FLIP_EXEMPT`
excuses it from bar E7, and why the gate stashes its bytes before a build and
restores them after.  A green run here says: **no previous build's in-place
rewrite has been left in the tree, and no assignment reaches the compiler that
is not in the committed revision file.**

--------------------------------------------------------------------------- #
WHAT THIS BAR DOES **NOT** PROVE -- stated, because a bar with no limits is a
bar nobody checked
--------------------------------------------------------------------------- #
  * NOT "the two A/B bitstreams differ by the CORE and nothing else".  THAT
    GUARANTEE IS RETIRED AND NOTHING REPLACES IT: there is no second core and no
    second revision for it to be about.  Every A/B claim resting on it is
    HISTORY as of WAVE 21 and must be read against `fb9365c01c` or earlier.
  * NOT faithfulness to a second file.  There is no template any more; the
    revision file IS the source of truth.  Nothing now cross-checks the settings
    against a second copy -- and the replacement for that cross-check is that
    there is only one copy to get wrong.
  * NOT anything about the CONTENTS of `files_ucore.qip`.  The list is SOURCED,
    not derived.  Its gates are that the build elaborates at all, plus
    `check_ucore_tables` (G0) and `ucrom_mif_check` on the tables it names.
  * NOT that the settings are CORRECT.  A wrong `set_global_assignment` is a
    green `qsf_lint`.
  * NOT anything about what Quartus DOES with the settings -- E2-E11 and the
    `truefmax` classes are that.

--------------------------------------------------------------------------- #
exit 0 = canonical.   exit 1 = NOT canonical, every offending line named.
exit 2 = CANNOT MEASURE (file missing or unreadable).  A lint that cannot
         measure must not print PASS.

    sw/qsf_lint.py [--check] [--qsf PATH]
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QSF = ROOT / "hdl" / "nec_test_ucore.qsf"

# The assignments `source sys/sys.tcl` supplies and Quartus then WRITES BACK
# into the revision file.  Canonical form has ZERO `set_location_assignment` and
# no `PRE_FLOW_SCRIPT_FILE`; the `PARTITION_HIERARCHY` instance assignment is
# the revision's OWN and is the single allowed `set_instance_assignment`.
MATERIALISED_PREFIX = "set_location_assignment"
OWN_INSTANCE = "set_instance_assignment -name PARTITION_HIERARCHY"
PRE_FLOW = "PRE_FLOW_SCRIPT_FILE"

REQUIRED_ONCE = {
    "source files_ucore.qip":
        lambda s: s == "source files_ucore.qip",
    "set_global_assignment -name PROJECT_OUTPUT_DIRECTORY":
        lambda s: s.startswith("set_global_assignment -name "
                               "PROJECT_OUTPUT_DIRECTORY"),
}
REQUIRED_PRESENT = ("source sys/sys.tcl",)


def check(path=QSF):
    """-> (rc, lines) -- rc 0/1/2 and the report lines, in order."""
    out = []
    if not path.exists():
        return 2, [f"qsf_lint: CANNOT MEASURE -- {path} does not exist"]
    try:
        text = path.read_text()
    except OSError as e:                                     # noqa: BLE001
        return 2, [f"qsf_lint: CANNOT MEASURE -- {path}: {e}"]
    if not text.strip():
        return 2, [f"qsf_lint: CANNOT MEASURE -- {path} is empty"]

    bad = []
    counts = {k: 0 for k in REQUIRED_ONCE}
    present = {k: False for k in REQUIRED_PRESENT}
    n_loc = n_pre = n_inst_other = 0
    for i, raw in enumerate(text.splitlines(), 1):
        s = raw.strip()
        if s.startswith("#"):
            continue
        if s.startswith(MATERIALISED_PREFIX):
            n_loc += 1
            if n_loc <= 3:
                bad.append(f"  {path.name}:{i}: MATERIALISED -- {s[:90]}")
        elif s.startswith("set_instance_assignment") \
                and not s.startswith(OWN_INSTANCE):
            n_inst_other += 1
            if n_inst_other <= 3:
                bad.append(f"  {path.name}:{i}: MATERIALISED -- {s[:90]}")
        elif PRE_FLOW in s:
            n_pre += 1
            bad.append(f"  {path.name}:{i}: MATERIALISED -- {s[:90]}")
        for k, pred in REQUIRED_ONCE.items():
            if pred(s):
                counts[k] += 1
        for k in REQUIRED_PRESENT:
            if s == k:
                present[k] = True

    rc = 0
    if n_loc or n_inst_other or n_pre:
        rc = 1
        out.append(f"qsf_lint: NOT CANONICAL -- {n_loc} set_location_assignment,"
                   f" {n_inst_other} foreign set_instance_assignment, "
                   f"{n_pre} {PRE_FLOW}")
        out.extend(bad)
        if n_loc > 3 or n_inst_other > 3:
            out.append("  ... (first three of each shown)")
        out.append("  Quartus rewrote this file during a build and it was left "
                   "in the tree.")
        out.append("  restore it:  git checkout -- hdl/nec_test_ucore.qsf")
    for k, n in counts.items():
        if n != 1:
            rc = 1
            out.append(f"qsf_lint: expected exactly one `{k}` in "
                       f"{path.name}, found {n}")
    for k, ok in present.items():
        if not ok:
            rc = 1
            out.append(f"qsf_lint: `{k}` is MISSING from {path.name}")
    if rc == 0:
        out.append(f"qsf_lint: {path.name} is CANONICAL "
                   f"(0 materialised assignments, one file list, "
                   f"one output directory)")
    return rc, out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="the default and the only mode; accepted so the "
                         "gate's historical `--check` spelling keeps working")
    ap.add_argument("--qsf", default=str(QSF),
                    help="the revision .qsf to check (for the positive "
                         "controls; the gate never passes this)")
    a = ap.parse_args()
    rc, lines = check(Path(a.qsf))
    print("\n".join(lines))
    return rc


if __name__ == "__main__":
    sys.exit(main())
