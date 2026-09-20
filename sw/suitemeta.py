#!/usr/bin/env python3
"""suitemeta - THE SUITE-METADATA DIALECT ADAPTER.  ONE RULE, THREE DIALECTS.

WHY THIS MODULE EXISTS
----------------------
`tests/v30/` holds golden suites emitted by three different producers over a
year, and they do not carry their metadata the same way.  Four sites in `sw/`
read `meta["opcodes"]` UNCONDITIONALLY, so a suite whose manifest has no such
map dies with `KeyError: 'opcodes'` -- which is why `tests/v30/v0.2` (347,000
cases) had never been scored by anything, and was recorded in
`docs/notes/ucore_gaps_2026-08-04.md` §F.2 as a tooling defect.

It is not a defect.  It is a DIALECT MISMATCH, and the rule that resolves it is
ONE SENTENCE:

    A suite's opcode map comes from its own `metadata.json` when that file has
    one, and from `v0.1`'s otherwise.

THE THREE DIALECTS.  Each is ONE predicate.  There is no per-suite branch and no
per-opcode special case anywhere in this file, and if a fourth case ever looks
necessary that is a FINDING to report, not a case to add (SIMPLICITY, user
directive 2026-08-01: *this is 80's era hardware -- nothing on the die is
wasted.  Complex or confusing observed behavior is likely simple systems
interacting in ways not yet understood.  A large fitted table, a many-cased
rule, or a per-opcode special case is a signal of misunderstanding, not a
deliverable.*)

    sst       metadata.json exists AND carries `opcodes`
              -> the map is its own.
              tests/v30/v0.1 (the SingleStepTests-style V30 emission) and
              tests/v30/v20suite (upstream SingleStepTests V20).

    emitter   metadata.json exists and carries NO `opcodes`
              -> DELEGATES to v0.1.
              tests/v30/v0.2 (emitter manifest: forms / variants /
              cases_per_form / waits / use_core / emitter_commit / seed_base)
              and tests/v30/mod3_illegal (a directed freeze: experiment /
              finding / n_goldens / stale_ea_probe).  These are ONE dialect --
              both say "metadata, but not an opcode map" -- and treating them as
              two would be the many-cased rule the principle forbids.

    absent    no metadata.json at all
              -> DELEGATES to v0.1.
              tests/v30/v0.3 (its per-opcode state lives in `XX.seeds.json`),
              and every wait-state / pin-event / derived tranche
              (`v0.1-w1`, `v0.1-w3`, the four `*evt` cells, `f4a_boundary`,
              `f0lock_tranche`, `s10-hltsweep-*`, `s16-dispwalk-*`, ...).

WHY DELEGATION AND NOT `0xFFFF`
-------------------------------
`ucore_gaps_2026-08-04.md` §F.2 suggested falling back to `flags_mask = 0xFFFF`.
That masks NOTHING and is therefore STRICTER, which sounds safer and is wrong:
the mask encodes the flag bits the part leaves UNDEFINED for that form
(`docs/facts/undefined_flags.md`), so comparing them raw manufactures failures
that are not divergences.  Delegation gives a suite the real masks for the forms
it actually contains.

The choice still MOVES A NUMBER, so it is not made silently: `--raw-flags`
already exists on `sw/check_core.py` and WAVE 22 scores `v0.2` on BOTH legs
(`docs/notes/suite_scorer_prereg_2026-09-19.md` §1.1).

WHERE THIS RULE USED TO LIVE
----------------------------
⚠ In `sw/ucsim_check.py::load_meta` -- **the C++ model's scorer**, whose CLI has
refused since WAVE 20 (`invalidation_ledger.md` RET-1) but which
`sw/timed_gate.py`, `sw/timed_probe.py` and `sw/uarch.py` still imported to get
the rule.  It was the only place in the tree that implemented BOTH halves
(file-absent AND `opcodes`-absent); `sw/check_core.py` implemented only the
file-absent half, which is exactly the `KeyError`.

So the dead model's scorer was the live tree's dialect authority.  Under the
USER RULING of 2026-09-19 -- *"Ucore is the only valid implementation in this
code base, if it has dependencies on any other implementations those need to be
removed"* -- the rule moves HERE and `ucsim_check` becomes one of its consumers.
Nothing is ported: the semantics below are the ones it had, and the positive
control proves it form for form.

FALSIFIER
---------
`python3 sw/suitemeta.py --selfcheck` -- each of the three dialects REACHED by a
real suite on disk, delegation ANNOUNCED rather than silent, and a delegated
`flags_mask` equal to `v0.1`'s for the same form over every form of every
delegating suite present.  Non-vacuity is checked in the same run by pointing a
delegating suite at an EMPTY map and requiring the equality to fail.
"""
import argparse
import json
import re
import sys
from pathlib import Path

SW = Path(__file__).resolve().parent
ROOT = SW.parent
TESTS = ROOT / "tests" / "v30"

#: The delegation target.  It is `v0.1` because `v0.1` is the V30 suite whose
#: manifest carries the project's own opcode/flags-mask database -- the same
#: choice `sw/check_core.py` has always made for the wait-state tranches and the
#: same one `ucsim_check.load_meta` made for both halves of the rule.
V01 = TESTS / "v0.1"

#: The dialects, DECLARED.  Order is the detection order, which is also
#: most-specific-first; each entry is (name, predicate, delegates?).
#: `raw` is the suite's own manifest dict or None when it has no manifest.
SST = "sst"
EMITTER = "emitter"
ABSENT = "absent"

DIALECTS = (
    (SST,     "metadata.json exists AND carries `opcodes`",       False),
    (EMITTER, "metadata.json exists, carries NO `opcodes`",       True),
    (ABSENT,  "no metadata.json at all",                          True),
)


class SuiteMeta:
    """A suite's metadata, with the dialect it is written in made explicit.

    `.raw`        the suite's OWN manifest (dict), or {} for dialect `absent`.
                  Non-opcode keys (`waits`, `cases_per_form`, `emitter_commit`,
                  `n_goldens`, ...) are read from here and are NEVER delegated:
                  a delegated opcode map says nothing about the suite's own
                  capture conditions.
    `.opcodes`    the resolved opcode map.
    `.dialect`    one of `sst` / `emitter` / `absent`.
    `.source`     the Path the opcode map was actually read from.
    `.delegated`  True when `.source` is not this suite's own manifest.
    """

    def __init__(self, suite, raw, opcodes, dialect, source, delegated):
        self.suite = Path(suite)
        self.raw = raw
        self.opcodes = opcodes
        self.dialect = dialect
        self.source = Path(source)
        self.delegated = bool(delegated)

    # -- the announcement.  Delegation is never silent: a caller prints this. --
    def note(self):
        rel = self.source.relative_to(ROOT) if ROOT in self.source.parents \
            else self.source
        if not self.delegated:
            return (f"[suitemeta] {self.suite.name}: dialect '{self.dialect}' "
                    f"-- opcode map from its own {rel.name}")
        return (f"[suitemeta] {self.suite.name}: dialect '{self.dialect}' "
                f"-- NO opcode map of its own; DELEGATING to {rel}")

    # -------------------------- the resolved policy -------------------------- #
    def entry(self, form):
        """The opcode entry for a form.  Grouped forms `XX.N` fall back to the
        base entry `XX`, which is where the SingleStepTests schema puts the
        shared fields (`docs/notes/singlesteptests_v20.md`)."""
        base = form.split(".")[0]
        return self.opcodes.get(form) or self.opcodes.get(base, {}) or {}

    def flags_mask(self, form):
        """`sw/emit_suite.py::_flags_mask_of` semantics, unchanged: a grouped
        form `XX.N` takes its mask from `opcodes[XX]["reg"][N]`, NOT from the
        base entry -- the old top-level lookup silently masked nothing."""
        entry = self.entry(form)
        if "." in form and "reg" in entry:
            sub = form.split(".", 1)[1]
            return entry["reg"].get(sub, {}).get("flags-mask", 0xFFFF)
        return entry.get("flags-mask", 0xFFFF)

    def dont_care(self, form):
        """The manifest `dont_care` entry for a form with its `when` predicate
        compiled -- a tiny fixed grammar, never `eval()`.  Returns
        (spec, pred) or (None, None).  Ported verbatim in semantics from
        `sw/ucsim_check.py::dont_care_spec`; the 8F.0 mod3 ghost read is the
        only user."""
        dc = (self.opcodes.get(form) or {}).get("dont_care")
        if not dc:
            return None, None
        m = _WHEN_RE.match(dc.get("when", "").strip())
        if not m:
            return dc, None
        i0, v0, i1, msk, v1 = m.groups()

        def pred(b, i0=int(i0), v0=int(v0, 0), i1=i1, msk=msk, v1=v1):
            if len(b) <= i0 or b[i0] != v0:
                return False
            if i1 is None:
                return True
            i1i = int(i1)
            return len(b) > i1i and (b[i1i] & int(msk, 0)) == int(v1, 0)

        return dc, pred


_WHEN_RE = re.compile(r"^bytes\[(\d+)\]\s*==\s*(0x[0-9A-Fa-f]+|\d+)"
                      r"(?:\s+and\s+\(bytes\[(\d+)\]\s*&\s*(0x[0-9A-Fa-f]+|\d+)\)"
                      r"\s*==\s*(0x[0-9A-Fa-f]+|\d+))?$")


def load(suite, delegate_to=None):
    """THE RULE, in six lines.  `delegate_to` is for the non-vacuity control
    only -- production callers never pass it."""
    suite = Path(suite)
    target = Path(delegate_to) if delegate_to is not None else V01
    own = suite / "metadata.json"
    if own.exists():
        raw = json.load(open(own))
        if "opcodes" in raw:
            return SuiteMeta(suite, raw, raw["opcodes"], SST, own, False)
        dialect = EMITTER
    else:
        raw, dialect = {}, ABSENT
    src = target / "metadata.json"
    ops = json.load(open(src)).get("opcodes", {}) if src.exists() else {}
    return SuiteMeta(suite, raw, ops, dialect, src, True)


def dialect_of(suite):
    """The dialect name alone, without reading the delegation target."""
    own = Path(suite) / "metadata.json"
    if not own.exists():
        return ABSENT
    return SST if "opcodes" in json.load(open(own)) else EMITTER


# --------------------------------------------------------------------------- #
# THE POSITIVE CONTROL.  W-4 of docs/notes/suite_scorer_prereg_2026-09-19.md.
# --------------------------------------------------------------------------- #
#: Every dialect must be REACHED by a real suite on disk, or the control cannot
#: claim the dialect exists.  (suite, expected dialect).
CONTROL_SUITES = (
    ("v0.1",         SST),
    ("v20suite",     SST),
    ("v0.2",         EMITTER),
    ("mod3_illegal", EMITTER),
    ("v0.3",         ABSENT),
    ("v0.1-w1",      ABSENT),
)


def selfcheck(verbose=True):
    def say(*a):
        if verbose:
            print(*a)

    ok, fail, skipped = 0, [], []
    say("suitemeta --selfcheck -- the dialect adapter's own falsifier")
    say(f"  delegation target: {V01.relative_to(ROOT)}")
    say()

    # (1) every declared dialect is reached by a real suite, with the dialect
    #     the declaration says.
    say("  (1) DIALECT REACHABILITY")
    reached = set()
    for name, want in CONTROL_SUITES:
        s = TESTS / name
        if not s.is_dir():
            skipped.append(f"{name}: not on disk")
            say(f"      {name:<14} SKIP (not on disk)")
            continue
        got = dialect_of(s)
        m = load(s)
        if got != want or m.dialect != want:
            fail.append(f"{name}: dialect {got!r}/{m.dialect!r}, want {want!r}")
            say(f"      {name:<14} FAIL  {got!r}/{m.dialect!r} != {want!r}")
            continue
        reached.add(want)
        ok += 1
        say(f"      {name:<14} {want:<8} delegated={m.delegated!s:<5} "
            f"{len(m.opcodes)} opcode entries")
    for name, _desc, _dg in DIALECTS:
        if name not in reached:
            fail.append(f"dialect {name!r} NOT REACHED by any suite on disk "
                        f"-- the control cannot claim it exists")
            say(f"      dialect {name!r}: NOT REACHED")

    # (2) delegation is ANNOUNCED, never silent.
    say("  (2) DELEGATION IS ANNOUNCED")
    for name, want in CONTROL_SUITES:
        s = TESTS / name
        if not s.is_dir():
            continue
        m = load(s)
        note = m.note()
        if m.delegated and "DELEGATING" not in note:
            fail.append(f"{name}: delegated but note() does not say so")
            say(f"      {name:<14} FAIL silent delegation")
            continue
        if not m.delegated and "DELEGATING" in note:
            fail.append(f"{name}: not delegated but note() claims it is")
            say(f"      {name:<14} FAIL false delegation claim")
            continue
        ok += 1
        say(f"      {name:<14} {'announced' if m.delegated else 'own map'}")

    # (3) a delegated flags_mask EQUALS v0.1's, for every form the suite has.
    say("  (3) DELEGATED flags_mask == v0.1's, form for form")
    base = load(V01)
    for name, want in CONTROL_SUITES:
        s = TESTS / name
        if not s.is_dir() or want == SST:
            continue
        forms = sorted(p.name[:-8] for p in s.glob("*.json.gz"))
        m = load(s)
        bad = [f for f in forms if m.flags_mask(f) != base.flags_mask(f)]
        if bad:
            fail.append(f"{name}: {len(bad)} form(s) mask-differ from v0.1: "
                        f"{bad[:6]}")
            say(f"      {name:<14} FAIL {len(bad)} of {len(forms)} differ")
            continue
        ok += 1
        nz = sum(1 for f in forms if m.flags_mask(f) != 0xFFFF)
        say(f"      {name:<14} {len(forms)} forms identical, "
            + (f"{nz} carrying a real (non-0xFFFF) mask -- so the delegation "
               f"CHANGES this suite's comparison" if nz else
               "NONE carrying a real mask -- for THIS suite the delegation is "
               "vacuous, and check (4) is what makes (3) non-vacuous overall"))

    # (4) NON-VACUITY.  Point a delegating suite at an EMPTY map: (3) must FAIL.
    #     If it does not, (3) was proving nothing.
    say("  (4) NON-VACUITY (the control must be able to fail)")
    # ⚠ the empty target goes in a TEMP DIR, not in the repo: a falsifier that
    # writes into `sw/testdata/` leaves an untracked artifact behind every time
    # it runs, and a gate should not dirty the tree it checks.
    import tempfile                                       # noqa: PLC0415
    _tmp = tempfile.TemporaryDirectory(prefix="suitemeta_selfcheck_")
    empty = Path(_tmp.name)
    (empty / "metadata.json").write_text(json.dumps({"opcodes": {}}))
    probe = None
    for name, want in CONTROL_SUITES:
        s = TESTS / name
        if s.is_dir() and want != SST and any(s.glob("*.json.gz")):
            probe = s
            break
    if probe is None:
        skipped.append("non-vacuity: no delegating suite with forms on disk")
        say("      SKIP (no delegating suite with forms on disk)")
    else:
        m = load(probe, delegate_to=empty)
        forms = sorted(p.name[:-8] for p in probe.glob("*.json.gz"))
        differ = [f for f in forms if m.flags_mask(f) != base.flags_mask(f)]
        if not differ:
            fail.append("NON-VACUOUS CONTROL DID NOT FIRE: an EMPTY delegation "
                        f"target left every {probe.name} mask equal to v0.1's, "
                        "so check (3) proves nothing")
            say("      FAIL -- empty target changed nothing")
        else:
            ok += 1
            say(f"      fired: {len(differ)} of {len(forms)} {probe.name} forms "
                f"move when the target is emptied")

    say()
    for s in skipped:
        say(f"  SKIPPED: {s}")
    if fail:
        say(f"suitemeta --selfcheck: FAIL -- {len(fail)} violation(s), "
            f"{ok} check(s) passed")
        for f in fail:
            say(f"  - {f}")
        return 1
    say(f"suitemeta --selfcheck: PASS -- {ok} checks, "
        f"{len(DIALECTS)} dialects reached, {len(skipped)} skipped")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--selfcheck", action="store_true",
                    help="the adapter's own falsifier (W-4)")
    ap.add_argument("--show", metavar="SUITE",
                    help="print one suite's resolved dialect and a mask sample")
    a = ap.parse_args()
    if a.show:
        s = Path(a.show)
        if not s.is_dir():
            s = TESTS / a.show
        m = load(s)
        print(m.note())
        print(f"  raw manifest keys : "
              f"{sorted(k for k in m.raw if k != 'opcodes')}")
        print(f"  opcode entries    : {len(m.opcodes)}")
        forms = sorted(p.name[:-8] for p in s.glob("*.json.gz"))[:8]
        for f in forms:
            print(f"  {f:<8} flags-mask 0x{m.flags_mask(f):04X}")
        return 0
    if a.selfcheck:
        return selfcheck()
    ap.error("nothing to do: pass --selfcheck or --show SUITE")


if __name__ == "__main__":
    sys.exit(main())
