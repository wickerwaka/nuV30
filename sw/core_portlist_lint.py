#!/usr/bin/env python3
"""core_portlist_lint - THE TWO `v30_core`s MUST HAVE THE SAME PORT LIST.

`hdl/rtl/core/v30_core.sv` (ARCHIVED, trace-fitted) and
`hdl/rtl/ucore/v30_core.sv` (the standing core) are DROP-IN alternatives: same
module name, same port list, selected by the RTL FILE LIST alone.  Two files in
the tree are SHARED between them and instantiate `v30_core` by name --
`hdl/tb/tb_v30_core.sv` and `hdl/rtl/system_large.sv` -- so a port that exists
in one core and not the other breaks every consumer of the other one.

THIS LINT EXISTS BECAUSE THAT HAPPENED AND NOTHING SAW IT FOR FIVE WEEKS.
`b7083b45a5` (2026-08-14) gave the ucore ADDR_O / DATA_O / STATUS_O and
connected all three in BOTH shared files.  Verilator then refused to elaborate
the archived core (`%Error-PINNOTFOUND`) and every offline gate that binds it
died: check_fuzz_bank, check_enter_nesting, check_ab_sim --core fsm,
t30_sweep.sh, and `check_core --core fsm` itself.  It was found by accident on
2026-09-19.  `docs/notes/wave18_archived_gates_prereg_2026-09-19.md`.

⚠ AND QUARTUS DOES NOT CATCH IT.  Measured on this tree, 2026-09-19, Quartus
17.1 Analysis & Elaboration of the `nec_test` (FSM) revision with all three
pins undeclared: **0 errors**, summary line "52 warnings", and the three pins
appear ONLY as `Critical Warning | Named port was not declared by the
instantiated entity` inside the Port Connectivity Checks REPORT FOLDER of
`nec_test.map.rpt`.  A bitstream would have been built and flashed.  So the
synthesis leg is not a substitute for this lint; it is the reason for it.

SCOPE, stated so a green run is readable:
  * The comparison is made under `V30_MUXED_AD` (with and without
    `V30_BACKDOOR`), which is the ONLY configuration the archived core has: its
    `AD`/`AD_OE`/`CE_HALF` are unconditional, so it is buildable with the define
    ON and nothing else (CLAUDE.md, the de-mux banner).  The define-OFF
    configuration is UCORE-ONLY BY CONSTRUCTION and is deliberately not compared
    -- `sw/demux_off_gate.py` is that configuration's gate.
  * It compares NAME, DIRECTION and RANGE TEXT.  It says nothing about what a
    port CARRIES: the archived core's ADDR_O/DATA_O/STATUS_O are tied to zero
    and declared NOT IMPLEMENTED in the RTL beside the tie-off.  A lint that
    claimed otherwise would be the vacuous kind.

Exit 0 = the two port lists agree in every compared configuration.
Exit 1 = they differ; every differing port is named with its side.
Exit 2 = the lint could not parse a port list, i.e. it could not measure.  A
         lint that cannot measure must not print PASS.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FSM = ROOT / "hdl" / "rtl" / "core" / "v30_core.sv"
UCORE = ROOT / "hdl" / "rtl" / "ucore" / "v30_core.sv"

# The configurations compared.  `V30_MUXED_AD` is not optional -- see SCOPE.
CONFIGS = [
    ("V30_MUXED_AD", {"V30_MUXED_AD"}),
    ("V30_MUXED_AD+V30_BACKDOOR", {"V30_MUXED_AD", "V30_BACKDOOR"}),
]

PORT_RE = re.compile(
    r"^(?P<dir>input|output|inout)\s+"
    r"(?:(?:reg|wire|logic)\s+)?"
    r"(?P<range>\[[^\]]*\]\s*)?"
    r"(?P<name>[A-Za-z_][A-Za-z_0-9$]*)\s*$")


class ParseError(Exception):
    pass


def _strip_comments(text):
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return "\n".join(ln.split("//")[0] for ln in text.splitlines())


def module_header(path):
    """The text between `module v30_core (` and its matching `);`, comments out.

    RAISES rather than returning something empty: an unfound header is a
    measurement failure, not an empty port list."""
    src = _strip_comments(path.read_text())
    m = re.search(r"^\s*module\s+v30_core\s*\(", src, flags=re.M)
    if not m:
        raise ParseError(f"{path}: no `module v30_core (` found")
    i = m.end()
    depth = 1
    while i < len(src) and depth:
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
        i += 1
    if depth:
        raise ParseError(f"{path}: unterminated `module v30_core (` port list")
    return src[m.end():i - 1]


def active_lines(header, defines):
    """Resolve `ifdef/ifndef/else/endif` against `defines`.  Nested is handled.

    An unbalanced conditional RAISES -- silently mis-resolving one would make
    the lint report the wrong port list with full confidence."""
    out, stack = [], []
    for ln in header.splitlines():
        s = ln.strip()
        d = re.match(r"`(ifdef|ifndef|elsif|else|endif)\b\s*(\w+)?", s)
        if d:
            kw, sym = d.group(1), d.group(2)
            if kw == "ifdef":
                stack.append(sym in defines)
            elif kw == "ifndef":
                stack.append(sym not in defines)
            elif kw == "elsif":
                if not stack:
                    raise ParseError("`elsif outside a conditional")
                stack[-1] = (not stack[-1]) and (sym in defines)
            elif kw == "else":
                if not stack:
                    raise ParseError("`else outside a conditional")
                stack[-1] = not stack[-1]
            else:
                if not stack:
                    raise ParseError("`endif outside a conditional")
                stack.pop()
            continue
        if all(stack):
            out.append(ln)
    if stack:
        raise ParseError("unbalanced `ifdef in the port list")
    return "\n".join(out)


def ports(path, defines):
    """-> ordered list of (name, direction, range_text).  RAISES on any entry
    it cannot parse, because a skipped entry is an invisible difference."""
    body = active_lines(module_header(path), defines)
    got = []
    for chunk in body.split(","):
        c = " ".join(chunk.split())
        if not c:
            continue
        m = PORT_RE.match(c)
        if not m:
            raise ParseError(f"{path}: unparsed port declaration {c!r}")
        rng = " ".join((m.group("range") or "").split())
        got.append((m.group("name"), m.group("dir"), rng))
    if not got:
        raise ParseError(f"{path}: port list parsed EMPTY")
    return got


def compare(fsm_path, ucore_path, verbose=True):
    bad = 0
    for label, defines in CONFIGS:
        a = ports(fsm_path, defines)
        b = ports(ucore_path, defines)
        da = {n: (d, r) for n, d, r in a}
        db = {n: (d, r) for n, d, r in b}
        only_fsm = [n for n, _, _ in a if n not in db]
        only_uc = [n for n, _, _ in b if n not in da]
        differ = [n for n in da if n in db and da[n] != db[n]]
        order = [n for n, _, _ in a] != [n for n, _, _ in b]
        n_bad = len(only_fsm) + len(only_uc) + len(differ)
        if verbose:
            print(f"core_portlist_lint: {label}: fsm {len(a)} ports, "
                  f"ucore {len(b)} ports, "
                  f"{'MATCH' if not n_bad else f'{n_bad} DIFFERENCE(S)'}"
                  f"{'' if not order or n_bad else ' (names match, ORDER differs -- '
                     'legal for named connection, reported not failed)'}")
        for n in only_fsm:
            print(f"  ONLY IN fsm   : {n} {da[n][0]} {da[n][1]}".rstrip())
        for n in only_uc:
            print(f"  ONLY IN ucore : {n} {db[n][0]} {db[n][1]}".rstrip())
        for n in differ:
            print(f"  DIFFERS       : {n}  fsm={da[n]}  ucore={db[n]}")
        bad += n_bad
    return bad


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fsm", default=str(FSM),
                    help="archived-core file (override is for the NON-VACUITY "
                         "control: point it at a pre-repair copy)")
    ap.add_argument("--ucore", default=str(UCORE))
    a = ap.parse_args()
    try:
        bad = compare(Path(a.fsm), Path(a.ucore))
    except ParseError as ex:
        print(f"core_portlist_lint: CANNOT MEASURE -- {ex}")
        print("  A lint that cannot parse the port list does not get to say "
              "PASS.  Fix the parse or the file; exit 2.")
        return 2
    if bad:
        print(f"\ncore_portlist_lint: FAIL | {bad} port difference(s) between "
              f"hdl/rtl/core/v30_core.sv and hdl/rtl/ucore/v30_core.sv")
        print("  The two cores are DROP-IN alternatives and hdl/tb/tb_v30_core.sv"
              " and\n  hdl/rtl/system_large.sv instantiate whichever is in the "
              "file list.  A port\n  in one and not the other breaks the other "
              "core's every consumer.\n  docs/notes/fsm_core_archive_2026-08-04.md"
              " §6a / §6b.")
        return 1
    print("\ncore_portlist_lint: PASS | the two v30_core port lists agree in "
          f"{len(CONFIGS)} configuration(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
