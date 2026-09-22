#!/usr/bin/env python3
"""THE PROVENANCE-STAMP GATE (WAVE 29).  ~0.5 s, offline, exit 0 / 1 / 2.

    python3 sw/truth_stamp_lint.py

WHY IT EXISTS
-------------
A provenance line is how this repo knows a golden came off SILICON, and
SILICON MATCH is the project's only correctness bar -- so a false provenance
line is the worst class of instrument defect here.

`emit_suite.truth_stamp()`'s own docstring has said since 2026-08 that *"a
provenance line that cannot be wrong is not provenance"*, and it was written
because the constant socket string, written unconditionally, once produced a
suite whose own log claimed it came off silicon.  **THAT REPAIR WAS MADE IN ONE
FILE AND NEVER PROPAGATED.**  As of WAVE 28 the same claim had FOUR writers in
`sw/` and only one derived it:

    emit_suite._truth_stamp()   DERIVED from ENGINE -- but ignored EMIT_USE_CORE
    s10_board.py:263            HARD-CODED CONSTANT
    s13_board.py:145            HARD-CODED CONSTANT
    s12_census.py:364           HARD-CODED CONSTANT -- and it re-derives goldens
                                OFFLINE from a banked capture, touching no
                                board, and stamped them "real chip" anyway
    (plus char_mod3, exp_iret, w28_ea_lane_fabric on the JSON-manifest side)

A comment is not a gate.  This file is the gate: it holds the one-place
property by GREP, and it is NON-VACUOUS IN BOTH DIRECTIONS -- it also runs
`truth_stamp()`'s four honest outcomes and its refusals as positive controls,
so a derivation that silently stopped refusing fails here.

⚠ THIS FILE MUST NOT CONTAIN THE STAMP STRINGS AS LITERALS -- it would then be
the second writer its own G1 forbids.  They are assembled from fragments below,
and the assembly is itself checked (a fragment typo makes G1 report 0, not 1).
"""
import re
import subprocess
import sys
from pathlib import Path

SW = Path(__file__).resolve().parent
sys.path.insert(0, str(SW))

# The two chip-side class strings, assembled so this file is not a writer.
SOCKET = "SOCKET" + " (real chip, use_core=False)"
DUT = "FPGA" + " v30_core inside system_large (use_core=True)"

fails, checks = [], 0


def ck(name, ok, detail=""):
    global checks
    checks += 1
    print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f" -- {detail}" if detail
                                                     else ""))
    if not ok:
        fails.append(name)


def pyfiles():
    out = subprocess.run(["git", "ls-files", "sw/*.py", "sw/**/*.py"],
                         cwd=SW.parent, capture_output=True, text=True)
    fs = [SW.parent / f for f in out.stdout.split() if f.endswith(".py")]
    return [f for f in fs if f.exists() and "testdata" not in f.parts]


def grep(needle, files):
    hits = []
    for f in files:
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if needle in line:
                hits.append(f"{f.relative_to(SW.parent)}:{i}")
    return hits


def main():
    files = pyfiles()
    me = SW / "truth_stamp_lint.py"

    # ---------------------------------------------------------------- G1/G2
    # P-3: the string exists in EXACTLY ONE PLACE in sw/.
    print(f"G1/G2  the one-place grep over {len(files)} tracked sw/*.py")
    for label, needle in (("SOCKET", SOCKET), ("FPGA-CORE", DUT)):
        hits = grep(needle, files)
        ck(f"{label} literal occurs exactly once",
           len(hits) == 1 and hits[0].startswith("sw/emit_suite.py"),
           f"hits={hits}")
    ck("this gate is not itself a writer",
       not grep(SOCKET, [me]) and not grep(DUT, [me]))

    import emit_suite as es
    import v30run as v3
    src = (SW / "emit_suite.py").read_text()
    body = src.split("def truth_stamp(")[1].split("\ndef ")[0]
    ck("both literals live inside truth_stamp()",
       SOCKET in body and DUT in body)

    # ---------------------------------------------------------------- G3
    # No other file may write a provenance VALUE from a literal.  Two shapes:
    # a JSON key with a quoted value, and a `TRUTH SOURCE:` prose line whose
    # next character is not an f-string substitution.
    print("G3  no second writer of a provenance value")
    key = re.compile(r'"truth_source"\s*:\s*["\']')
    prose = re.compile(r'TRUTH SOURCE:\s*(?!\{|"\s*\+|\{\{)[A-Za-z(]')
    bad = []
    for f in files:
        if f == me:
            continue
        for i, line in enumerate(f.read_text().splitlines(), 1):
            if key.search(line) or prose.search(line):
                bad.append(f"{f.relative_to(SW.parent)}:{i}: {line.strip()}")
    ck("no literal-valued truth_source / TRUTH SOURCE in sw/", not bad,
       "; ".join(bad))

    # ---------------------------------------------------------------- P-4
    # The four honest outcomes and the refusals, MEASURED.  The witness is
    # saved and restored around every perturbation: it is a provenance record
    # and this gate does not leave one edited.
    print("P-4  the four truth classes and the refusals, by perturbation")
    saved_pin, saved_eng = es.EMIT_USE_CORE, es.ENGINE
    saved_wit = list(v3._board_witness)

    def restore():
        es.EMIT_USE_CORE, es.ENGINE = saved_pin, saved_eng
        v3._board_witness[:] = saved_wit

    def refuses(name, fn):
        try:
            got = fn()
        except es.TruthSourceError as e:
            ck(name + " REFUSES", True, str(e).split(" -- ")[0][:64])
            return
        ck(name + " REFUSES", False, f"returned {got!r}")

    try:
        # (0) the default: the pin is False and nothing was captured -> SOCKET
        ck("class SOCKET  (pin False)", es.truth_stamp() == SOCKET)

        # (a) EMIT_USE_CORE=True -- the stamp MUST change and MUST NOT say socket
        es.EMIT_USE_CORE = True
        s = es.truth_stamp()
        ck("class FPGA CORE  (pin True) is not the socket string",
           s != SOCKET and DUT in s and "NOT SILICON" in s, s)
        restore()

        # (b) the engine is a TB -- it MUST name the TB
        es.ENGINE = "tb"
        s = es.truth_stamp()
        ck("class VERILATOR TB names the TB",
           "VERILATOR TB" in s and "NOT SILICON" in s and SOCKET not in s, s)
        restore()

        # (c) the banked-replay class names ITSELF
        s = es.truth_stamp(banked="bank X")
        ck("class BANKED REPLAY names itself and no board",
           "BANKED REPLAY" in s and "NO BOARD CONTACT" in s
           and SOCKET not in s and DUT not in s, s)
        restore()

        # (d) the refusals
        refuses("position None", lambda: es.truth_stamp(use_core=None))
        refuses("banked + a position",
                lambda: es.truth_stamp(use_core=False, banked="b"))
        # NOT a refusal: `ServeRunner.cfg` sends int(bool(use_core)), so an
        # argparse 0/1 is the SAME position to the board as False/True.  The
        # control is that the normalisation is the board's own, not a second
        # rule -- `x1_fabric` and `sm3_s16_fabric` pin the module to ints.
        ck("an int position normalises exactly as `cfg` does",
           es.truth_stamp(use_core=0) == SOCKET
           and DUT in es.truth_stamp(use_core=1))

        es.ENGINE = "chippp"
        refuses("unknown ENGINE", es.truth_stamp)
        restore()

        # the WITNESS half: a claim the board contradicts.  v3._witness() is
        # the recorder run_image itself calls; calling it here simulates one
        # board command without any transport.
        v3._witness("h", True, 8, 0, "serve")
        refuses("socket claim contradicted by a use_core=True board command",
                lambda: es.truth_stamp(use_core=False))
        s = es.truth_stamp(use_core=True)
        ck("the position the board WAS commanded into still stamps", DUT in s)
        refuses("banked claim with a board command on record",
                lambda: es.truth_stamp(banked="b"))
        es.ENGINE = "tb"
        refuses("tb claim with a board command on record", es.truth_stamp)
        restore()

        v3._witness("h", None, None, 0, "legacy")
        refuses("a capture that left the board's STICKY CFG alone",
                lambda: es.truth_stamp(use_core=False))
        restore()

        # the witness line itself
        ck("truth_witness_stamp names an empty witness as empty",
           "NO run_image BOARD COMMAND" in es.truth_witness_stamp())
        v3._witness("h", False, 8, 0, "serve")
        w = es.truth_witness_stamp()
        ck("truth_witness_stamp counts what ran",
           "1 board command(s)" in w and "False" in w, w)
        restore()

        # (P-4d) THE EXISTING GUARDS STILL FIRE.  Each is checked at the top of
        # its command, before any board contact.
        print("P-4d  the pre-existing emitter guards")
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            es.EMIT_USE_CORE = True
            for name, fn in (
                    ("cmd_emit", lambda: es.cmd_emit(None, [], 0, td, "s", 0)),
                    ("cmd_emit_boundary",
                     lambda: es.cmd_emit_boundary(None, [], 0, td, "s", 0)),
                    ("cmd_reemit", lambda: es.cmd_reemit(None, {}, td, "s"))):
                try:
                    fn()
                    ck(f"{name} refuses a non-socket truth source", False,
                       "it did not raise")
                except es.RunError as e:
                    ck(f"{name} refuses a non-socket truth source",
                       "truth source" in str(e), str(e)[:60])
        restore()
    finally:
        restore()

    print(f"\n{'PASS' if not fails else 'FAIL'}  {checks - len(fails)}/{checks}"
          f" checks" + (f"  failed: {fails}" if fails else ""))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
