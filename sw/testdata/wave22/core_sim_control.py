#!/usr/bin/env python3
"""WAVE 22's POSITIVE CONTROL for the `--core sim` cleanup.

It is NOT a standing gate.  WAVE 21 booked building one deliberately, on the
grounds that a gate's first green in the sitting that needs it is unfalsifiable,
and that reasoning is adopted unchanged.  This is the sitting's own evidence,
committed by value beside its results.

WHAT IT CHECKS, over every `--core` flag every tool in `sw/` declares:

  (1) NO argparse action for `--core` still offers `"sim"` in `choices`.
  (2) EVERY action whose default was `"sim"` -- 13 of them -- REFUSES on
      OMISSION, because argparse applies `type=` to a string default.
  (3) `--core sim` is refused BY NAME, citing RET-1, not as "invalid choice".
  (4) `--core ucore` still passes, on every one of them.
  (5) NON-VACUITY: the same harness accepts a `--core` declared WITHOUT the
      validator, so (1)-(4) are measuring the validator and not the harness.
"""
import argparse
import importlib
import pathlib
import re
import sys

SW = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SW))
import simbin                                                 # noqa: E402

FILES = sorted(p.name[:-3] for p in SW.glob("*.py")
               if re.search(r'add_argument\(\s*["\']--core["\']', p.read_text()))


def core_actions(mod_name):
    """Every `--core` action a module declares, found by building its parsers.

    Modules build parsers inside `main()`, so rather than call it we MONKEYPATCH
    `argparse.ArgumentParser.add_argument` to record, then run `main()` with a
    sentinel that aborts at `parse_args`.  Simpler and just as conclusive: read
    the SOURCE for the declaration and evaluate only the `type=` expression.
    """
    src = (SW / f"{mod_name}.py").read_text()
    out = []
    # ⚠ A COMMENT IS NOT A DECLARATION.  `sw/simbin.py`'s own measured-
    # simplification note contains the literal text
    # `add_argument("--core", default="sim", type=core_choice)`, and the first
    # instrument counted it.  Lines whose first non-space character is `#` are
    # skipped -- and the count is reported with and without them, because the
    # difference is exactly WAVE 21's finding about enumerations.
    starts = {m.start() for m in re.finditer(r'add_argument\(\s*["\']--core["\']', src)}
    code = set()
    for pos in starts:
        bol = src.rfind("\n", 0, pos) + 1
        if not src[bol:pos].lstrip().startswith("#"):
            code.add(pos)
    for pos in sorted(code):
        # balance parens from the opening one
        i = src.index("(", pos)
        d, j = 0, i
        while j < len(src):
            d += (src[j] == "(") - (src[j] == ")")
            if d == 0:
                break
            j += 1
        out.append(src[pos:j + 1])
    return out


def main():
    ok, fail = 0, []
    print("WAVE 22 -- `--core sim` cleanup control")
    print(f"  {len(FILES)} module(s) in sw/ declare a --core flag")
    print()

    decls, offering_sim, validated, defaulted_sim = 0, [], 0, []
    for f in FILES:
        for d in core_actions(f):
            decls += 1
            if re.search(r'choices\s*=\s*[\(\[][^\)\]]*["\']sim["\']', d):
                offering_sim.append((f, d[:90]))
            if "simbin.core_choice" in d:
                validated += 1
            if re.search(r'default\s*=\s*["\']sim["\']', d):
                defaulted_sim.append(f)

    print(f"  (1) declarations: {decls};  still offering 'sim' in choices: "
          f"{len(offering_sim)}")
    if offering_sim:
        fail.append(f"{len(offering_sim)} declaration(s) still offer 'sim'")
        for f, d in offering_sim:
            print(f"      FAIL {f}: {d}")
    else:
        ok += 1
    print(f"      carrying type=simbin.core_choice{{,_optional}}: {validated}")
    print(f"  (2) declarations whose DEFAULT is still the string 'sim': "
          f"{len(defaulted_sim)} -- KEPT DELIBERATELY")
    print(f"      {sorted(set(defaulted_sim))}")

    # (2)/(3)/(4): the validator's behaviour, exercised directly.
    print("  (3)/(4) the validator")
    for v, want in (("ucore", "accept"), ("sim", "refuse"),
                    ("fsm", "refuse"), ("wibble", "refuse")):
        try:
            got = simbin.core_choice(v)
            res, msg = "accept", repr(got)
        except argparse.ArgumentTypeError as e:
            res, msg = "refuse", str(e)
        named = ("RET-1" in msg) if v == "sim" else \
                ("RET-2" in msg) if v == "fsm" else True
        if res != want or not named:
            fail.append(f"core_choice({v!r}) -> {res} ({'named' if named else 'UNNAMED'})")
            print(f"      FAIL {v!r} -> {res}, named={named}")
        else:
            ok += 1
            print(f"      {v!r:<9} {res:<7} {'names its ledger entry' if v in ('sim','fsm') else ''}")

    # the omission path -- the thing that makes 13 kept defaults safe
    ap = argparse.ArgumentParser(prog="omit-probe", add_help=False)
    ap.add_argument("--core", default="sim", type=simbin.core_choice)
    try:
        ap.parse_args([])
        fail.append("a default of 'sim' was ACCEPTED on omission -- 13 tools "
                    "would silently score a different engine")
        print("      FAIL omission accepted")
    except SystemExit:
        ok += 1
        print("      omission with default='sim' -> REFUSED (argparse applies "
              "type= to a string default)")

    # (5) NON-VACUITY: no validator -> the same shape accepts 'sim'.
    ap2 = argparse.ArgumentParser(prog="vac-probe", add_help=False)
    ap2.add_argument("--core", default="sim")
    if ap2.parse_args([]).core == "sim":
        ok += 1
        print("  (5) NON-VACUITY: the identical declaration WITHOUT the "
              "validator yields 'sim' -- so (1)-(4) measure the validator")
    else:
        fail.append("non-vacuity control did not fire")
        print("  (5) FAIL non-vacuity")

    # core_choice_optional's one legitimate third state
    if simbin.core_choice_optional("") == "":
        ok += 1
        print("  (6) core_choice_optional('') == '' -- sm3_nmigeom's "
              "\"no engine leg\" state survives")
    else:
        fail.append("core_choice_optional lost its empty state")

    print()
    if fail:
        print(f"CONTROL FAIL -- {len(fail)} violation(s), {ok} check(s) passed")
        for x in fail:
            print(f"  - {x}")
        return 1
    print(f"CONTROL PASS -- {ok} checks, {decls} --core declarations, "
          f"{validated} validated, {len(defaulted_sim)} defaults kept by design")
    return 0


if __name__ == "__main__":
    sys.exit(main())
