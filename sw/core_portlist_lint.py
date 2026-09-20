#!/usr/bin/env python3
"""core_portlist_lint - EVERY NAMED CONNECTION TO `v30_core` IS A DECLARED PORT.

⚠ THIS GATE CHANGED ITS SECOND OPERAND ON 2026-09-19 (WAVE 21).  READ THIS.

WAVE 18 built it to compare the TWO `v30_core`s -- `hdl/rtl/core/v30_core.sv`
(the ARCHIVED, trace-fitted core) against `hdl/rtl/ucore/v30_core.sv` -- because
they were DROP-IN alternatives and a port in one and not the other broke every
consumer of the other.  **The archived core was REMOVED FROM THE TREE by WAVE 21
(`invalidation_ledger.md` RET-2), so that comparison has no second operand and
NOTHING REPLACES IT: there is one core.**

WHAT THIS GATE MEASURES NOW, and it is the SAME DEFECT CLASS with the operand
that still exists:

    for each (instantiation site, define set) this tree actually BUILDS,
    every `.NAME(...)` named connection to `v30_core` must be a port the
    module DECLARES under that same define set.

That is exactly what broke: `b7083b45a5` (2026-08-14) added ADDR_O / DATA_O /
STATUS_O to the ucore and connected all three in `hdl/tb/tb_v30_core.sv` and
`hdl/rtl/system_large.sv`; Verilator then refused to elaborate the other core
(`%Error-PINNOTFOUND`) and five offline gates died for five weeks with nothing
watching.  The direction of the check is now CONNECTION -> DECLARATION, which is
the direction the error comes from, and it covers the FABRIC configuration
(`SYNTHESIS` + `V30_MUXED_AD`) that no Verilator run in this tree exercises.

⚠ AND QUARTUS DOES NOT CATCH IT.  Measured on this tree, 2026-09-19, Quartus
17.1 Analysis & Elaboration with three pins undeclared: **0 errors**, summary
"52 warnings", and the pins appear ONLY as `Critical Warning | Named port was
not declared by the instantiated entity` inside the Port Connectivity Checks
REPORT FOLDER of `nec_test.map.rpt`.  A bitstream would have been built and
flashed.  The synthesis leg is not a substitute for this lint; it is the reason
for it.

SCOPE, stated so a green run is readable:
  * The CONFIGURATIONS are the ones the tree's own builders pass, not a
    cross-product: `sw/check_core.py:253` for `tb_v30_core.sv`,
    `sw/check_ab_sim.py:119` / `sw/x1_retention.py:151` for `system_large.sv`
    under Verilator, `hdl/nec_test_ucore.qsf`'s VERILOG_MACROs for the fabric
    build of the same file, and `sw/demux_off_gate.py` for `tb_demux_min.sv`.
    If a builder's define set changes, THIS TABLE MUST CHANGE WITH IT -- that
    coupling is the gate's one maintenance cost and it is declared, not hidden.
  * It compares NAMES under `ifdef` resolution.  It says NOTHING about what a
    port CARRIES, about widths at the connection, or about whether the
    expression connected is sane -- a lint that claimed otherwise would be the
    vacuous kind.
  * A DECLARED PORT LEFT UNCONNECTED is legal (Verilator warns, Quartus prunes)
    and is REPORTED, never failed.

Exit 0 = every named connection is a declared port, in every configuration.
Exit 1 = a connection names a port the module does not declare -- named, with
         its site and configuration.
Exit 2 = the lint could not parse a port list or an instantiation, i.e. it
         could not measure.  A lint that cannot measure must not print PASS.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UCORE = ROOT / "hdl" / "rtl" / "ucore" / "v30_core.sv"

# --------------------------------------------------------------------------- #
# THE CONFIGURATIONS -- each one is a real build command in this tree, named.
# (label, instantiating file, defines)
# --------------------------------------------------------------------------- #
SITES = [
    ("tb_v30_core / check_core.py:253",
     ROOT / "hdl" / "tb" / "tb_v30_core.sv",
     {"V30_BACKDOOR", "V30_MUXED_AD", "V30_PFX_ASSERT"}),
    ("system_large / Verilator (check_ab_sim, tb_sys)",
     ROOT / "hdl" / "rtl" / "system_large.sv",
     {"V30_MUXED_AD"}),
    ("system_large / FABRIC (nec_test_ucore.qsf VERILOG_MACROs)",
     ROOT / "hdl" / "rtl" / "system_large.sv",
     {"V30_MUXED_AD", "SYNTHESIS"}),
    ("tb_demux_min / demux_off_gate.py (the DE-MUXED configuration)",
     ROOT / "hdl" / "tb" / "tb_demux_min.sv",
     set()),
]

PORT_RE = re.compile(
    r"^(?P<dir>input|output|inout)\s+"
    r"(?:(?:reg|wire|logic)\s+)?"
    r"(?P<range>\[[^\]]*\]\s*)?"
    r"(?P<name>[A-Za-z_][A-Za-z_0-9$]*)\s*$")

CONN_RE = re.compile(r"\.\s*([A-Za-z_][A-Za-z_0-9$]*)\s*\(")


class ParseError(Exception):
    pass


def _strip_comments(text):
    """Comments out, by a SCANNER and not by a regex.

    ⚠ THE REGEX FORM WAS WRONG AND IT WAS SILENT.  WAVE 18's version did
    `re.sub(r"/\\*.*?\\*/", " ", text, flags=re.S)` FIRST, over the raw text.
    `hdl/tb/tb_v30_core.sv:40` is a LINE comment that contains `hdl/rtl/core/*.sv`
    -- so the block-comment regex matched from that `/*` all the way to the
    `*/` of `/* verilator lint_off PINCONNECTEMPTY */` on line 254 and DELETED
    the `v30_core dut (` instantiation along with 200 other lines.  It never
    showed because WAVE 18 only ever fed this function the two `v30_core.sv`
    files, which happen not to contain the pattern.  Found 2026-09-19 (WAVE 21)
    the first time the function was pointed at the TB, and it presented as
    `no v30_core <name> ( instantiation found`, i.e. as exit 2 CANNOT MEASURE
    -- which is the only reason it was not a silent wrong answer."""
    out, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c == '"':                       # string literal -- copied verbatim
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:min(j + 1, n)])
            i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            out.append(" ")
            i = n if j < 0 else j + 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _balanced(src, start):
    """src[start] is just past an opening `(` -- return the index of its match.

    RAISES on an unterminated list: silently truncating one would make the lint
    report a short port list with full confidence."""
    i, depth = start, 1
    while i < len(src) and depth:
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
        i += 1
    if depth:
        raise ParseError("unterminated `(` ... `)`")
    return i - 1


def module_header(path):
    """The text between `module v30_core (` and its matching `);`."""
    src = _strip_comments(path.read_text())
    m = re.search(r"^\s*module\s+v30_core\s*\(", src, flags=re.M)
    if not m:
        raise ParseError(f"{path}: no `module v30_core (` found")
    try:
        end = _balanced(src, m.end())
    except ParseError:
        raise ParseError(f"{path}: unterminated `module v30_core (` port list")
    return src[m.end():end]


def instance_bodies(path):
    """Every `v30_core <name> ( ... );` body in `path`.  RAISES if there is none
    -- a site with no instantiation is a STALE ENTRY in SITES, which is a
    measurement failure and not a pass."""
    src = _strip_comments(path.read_text())
    out = []
    for m in re.finditer(r"\bv30_core\s+([A-Za-z_][A-Za-z_0-9$]*)\s*\(", src):
        end = _balanced(src, m.end())
        out.append((m.group(1), src[m.end():end]))
    if not out:
        raise ParseError(f"{path}: no `v30_core <name> (` instantiation found")
    return out


def active_lines(text, defines):
    """Resolve `ifdef/ifndef/elsif/else/endif` against `defines`.  Nested OK.

    An unbalanced conditional RAISES -- silently mis-resolving one would make
    the lint report the wrong list with full confidence."""
    out, stack = [], []
    for ln in text.splitlines():
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
        raise ParseError("unbalanced `ifdef")
    return "\n".join(out)


def ports(path, defines):
    """-> ordered [(name, direction, range_text)].  RAISES on any entry it
    cannot parse, because a skipped entry is an invisible difference."""
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


def connections(path, defines):
    """-> [(instance_name, [connected port names])] under `defines`."""
    out = []
    for inst, body in instance_bodies(path):
        names = CONN_RE.findall(active_lines(body, defines))
        if not names:
            raise ParseError(f"{path}: instance {inst} has NO named "
                             f"connections under {sorted(defines) or '{}'}")
        out.append((inst, names))
    return out


def check(core_path=UCORE, sites=SITES, verbose=True):
    """-> (n_bad, n_configs).  RAISES ParseError (-> exit 2) if it cannot
    measure."""
    bad = 0
    for label, path, defines in sites:
        declared = {n: (d, r) for n, d, r in ports(core_path, defines)}
        for inst, names in connections(path, defines):
            undeclared = [n for n in names if n not in declared]
            unconnected = [n for n in declared if n not in set(names)]
            if verbose:
                print(f"core_portlist_lint: {label}"
                      f"\n    defines {sorted(defines) or '(none)'}"
                      f"  instance `{inst}`"
                      f"  {len(declared)} declared, {len(names)} connected"
                      f"  -> {'OK' if not undeclared else
                              f'{len(undeclared)} UNDECLARED'}")
            for n in undeclared:
                print(f"    ⚠ CONNECTED BUT NOT DECLARED: .{n} "
                      f"-- {path.relative_to(ROOT)} -> v30_core")
            if unconnected and verbose:
                print(f"    (declared and left unconnected, LEGAL and "
                      f"reported: {', '.join(sorted(unconnected))})")
            bad += len(undeclared)
    return bad, len(sites)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--core", default=str(UCORE),
                    help="the v30_core to read the port list from (override is "
                         "for the NON-VACUITY controls only)")
    ap.add_argument("--site", default=None,
                    help="restrict to the one SITES label containing this "
                         "substring (for the controls)")
    a = ap.parse_args()
    sites = SITES if not a.site else [s for s in SITES if a.site in s[0]]
    if not sites:
        print(f"core_portlist_lint: CANNOT MEASURE -- no site matches "
              f"{a.site!r}")
        return 2
    try:
        bad, n = check(Path(a.core), sites)
    except (ParseError, OSError) as ex:
        print(f"core_portlist_lint: CANNOT MEASURE -- {ex}")
        print("  A lint that cannot parse the port list or the instantiation "
              "does not get\n  to say PASS.  Fix the parse or the file; exit 2.")
        return 2
    if bad:
        print(f"\ncore_portlist_lint: FAIL | {bad} named connection(s) to "
              f"v30_core name a port it does not declare")
        print("  Verilator REFUSES this (%Error-PINNOTFOUND); Quartus ACCEPTS "
              "AND IGNORES it\n  as a Critical Warning in a report folder no "
              "gate reads.  WAVE 18 lost five\n  weeks of gate coverage to "
              "exactly this.  docs/notes/wave18_archived_gates_"
              "results_2026-09-19.md.")
        return 1
    print(f"\ncore_portlist_lint: PASS | every named connection to v30_core is "
          f"a declared port, in {n} configuration(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
