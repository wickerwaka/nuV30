# WAVE 27 — Z-5.  EVERY CONSUMER OF `tests/v30/v0.2`, WITH ITS DISPOSITION

**The enumeration is mechanical; the disposition is manual; and the brief is
right that this is a FLOOR.**  What the mechanical pass did NOT find, and what
found it, is § WHAT THE GREP MISSED at the end — it is the most important
section of this file.

## Method

```
grep -rn 'v0\.2\|v02' sw/ docs/ tests/ hdl/ *.md          # every mention
grep -rn 'tests/v30/v0\.2'  --exclude-dir=.git .          # every PATH reference
grep -rn 'iterdir\|glob'    sw/*.py | grep -i 'tests\|v30' # every DIRECTORY SWEEP
```
Then **every executable hit was RUN**, before and after the deletion, and its
exit code and first lines of output compared.  A hit that only appears in prose
is dispositioned on reading; a hit in code is dispositioned on its measured
behaviour.

## A. CODE — runtime consumers

| file | what it was | disposition | evidence |
|---|---|---|---|
| `sw/suitemeta.py` | `CONTROL_SUITES` carried `("v0.2", EMITTER)`; its check (4) probe **selected `v0.2` by list position** | **REPAIRED — and this is the one that broke.**  Row removed; probe now selected by the PROPERTY it needs.  See § WHAT THE GREP MISSED | `--selfcheck` **PASS, 14 checks, 3 dialects, 0 skipped**; negative control exits 1 |
| `sw/collision_scan.py` | `--dir` defaulted to `tests/v30/v0.2` | **REPOINTED** to `tests/v30/v0.3`.  Suite-agnostic tool; the default was the only tie | `--help` shows the new default |
| `sw/validate_suite.py` | `--dir` defaulted to `tests/v30/v0.2` | **REPOINTED** to `tests/v30/v0.3`, same reason | `--help` |
| `sw/w26_consumer_census.py` | `SUITES` listed `v0.2`; `mod3_cases()` returns `(0, 0)` for a missing suite | **REPOINTED + THE DROP IS PRINTED.**  Left alone it would have reported `v0.2  8D cases 0  mod==3 0` — *"checked, and empty"* for a suite that does not exist.  It now prints `v0.2 RETIRED … NOT counted, NOT assumed empty` and the denominator reads 3 | run: **PASS**, `-> 0 case(s) over 3 suites` |
| `sw/check_core.py` | one comment naming the old `KeyError` | **MARKED HISTORY** (`RET-3` named in place).  No code path reads the suite: `--suite-dir` is a CLI argument and its default is `v0.1` | `--suite-dir` default is `SUITE = tests/v30/v0.1` |
| `sw/ucsim_smoke.py` | `--suite` defaulted to `tests/v30/v0.2` | **LEFT, WITH REASON.**  It is a **RET-1** casualty: `import simbin` then a refusal in `main()`, so the default is never opened.  Editing a retired tool's dead default would imply it can run | run after the deletion: exits 1 with the **RET-1 `ModelRetired` banner**, not `FileNotFoundError` |
| `sw/ucsim_coverage_report.py` | a hard-coded `tests/v30/v0.2  347000/347000` line in the report it emits, and the same in its usage block | **LEFT, WITH REASON.**  `simbin.retired(...)` fires at **line 46, before `main()`** — the report can never be emitted | run after the deletion: exits 1 on the RET-1 banner |
| `sw/ucsim_check.py`, `sw/emit_suite.py`, `sw/pla3_check.py` | comments/prose only | **LEFT.**  `ucsim_check` is RET-1-retired; `emit_suite`'s four are pointers to `v02_suspected_divergences.md`, which is retained and now carries a WAVE 27 header; `pla3_check`'s is a statement about where a measurement came from, which stays true | `pla3_check` run: **OK (21 checks)** |
| `hdl/tb/tb_v30_core.sv:523` | a comment quoting the `7.17 M` case-count arithmetic | ⚠ **LEFT, DELIBERATELY — Z-7 forbids any `hdl/` edit in this wave.**  Booked for whoever next opens that file | `git diff -- hdl/` is EMPTY |

## B. CODE — directory sweeps that could pick the archive up

| file | what it does | disposition |
|---|---|---|
| `sw/s16_dispwin.py --goldens` | iterates **every** subdirectory of `tests/v30/` and counts display windows | **LEFT, WITH REASON, AND REPORTED.**  It is a MEASUREMENT TOOL, never a gate (`CLAUDE.md`: *"never quote them as a pass"*), it already swept `rep_cl0-INV3-archive` by the same rule, and its output is labelled per directory.  `v02-unique-archive` becomes one more labelled row.  ⚠ **Its `ALL GOLDEN SUITES` total therefore MOVES** — stated here so nobody reads that as a regression |
| everything else | no tool globs `tests/v30/*` as a suite list | — |

## C. DOCUMENTS

| document | disposition |
|---|---|
| `docs/notes/invalidation_ledger.md` | **RET-3 WRITTEN.**  The register entry, with every gate that died and the recovery section that says **YOU CANNOT** |
| `docs/notes/standing_gates.md` | **LEG REMOVED** from the §W22 authoritative table (struck row naming RET-3, both last figures, and that neither may be quoted); the NOT-IN-GIT warning rewritten to record that it came true; the redundancy paragraph replaced by the measurement; `suitemeta` 17 → 14 checks |
| `CLAUDE.md` | **WAVE 27 BANNER** at the head of the gate quick reference; the `7,341,126` and `7.17 M` totals marked as historical; the NOT-IN-GIT caveat corrected |
| `docs/notes/v02_suspected_divergences.md` | **WAVE 27 HEADER PREPENDED** above WAVE 24's — the case coordinates it names now point into a suite that is gone.  Retained, unedited below the line |
| `docs/notes/v0.2_reemission_worklist.md` | **WAVE 27 HEADER PREPENDED.**  ⚠ Retained because it is **evidence**: it records a re-emission pass over `v0.2` that DID happen, and that is the leading candidate for RET-3's unresolved 7,127-vs-7,137 erratum |
| `docs/notes/suite_scorer_{prereg,results}_2026-09-19.md`, `suite_divergence_*_2026-09-20.md`, `tb_relatch_*`, `ea_qualifier_results_*`, `lea_mod3_results_*`, `ucore_gaps_2026-08-04.md`, `ucsim_*`, `bringup_log.md`, `docs/facts/pla_model.md`, `rep_cl0_*`, `README.md`, `ROADMAP.md`, `tests/v30/v0.1/README.md` | **LEFT AS WRITTEN — they are DATED WAVE RECORDS.**  Rewriting a prior wave's registered result to match today's tree is exactly WAVE 26's doc-discrepancy **D-9**, and a ratchet is only readable against its own history.  RET-3 is the single place the reader is sent |
| `tests/v30/v0.3/README.md` | ⚠ **NOT TOUCHED — it is one of the USER's own modified files** (Z-8).  Its `7,137` is contradicted in RET-3 instead |
| `sw/testdata/wave22/manifest-v0.2.txt` | **LEFT, AND CITED ONE LAST TIME.**  All 347 form files and all four provenance files hashed identically to it at the moment of deletion, which is the proof that what went is what was scored.  It is now permanently unverifiable and RET-3 says so |

## ⚠ WHAT THE GREP MISSED — and what found it

**The mechanical enumeration found `sw/suitemeta.py:230` — the `("v0.2",
EMITTER)` row — and the obvious disposition was "delete the row, the `EMITTER`
dialect survives on `mod3_illegal`."  That disposition is correct and it is
not sufficient.**

`selfcheck`'s check (4) is the non-vacuity control: empty the delegation target
and demand that some mask MOVE.  It chose its probe as *the first delegating
suite in `CONTROL_SUITES` with forms on disk*.  That was `v0.2`, which happens
to carry **16 real (non-`0xFFFF`) masks**.  With the row gone the probe fell
through to `mod3_illegal`, **whose single form's mask is `0xFFFF`**, so emptying
the target changed nothing and the gate reported

```
NON-VACUOUS CONTROL DID NOT FIRE: an EMPTY delegation target left every
mod3_illegal mask equal to v0.1's, so check (3) proves nothing
suitemeta --selfcheck: FAIL -- 1 violation(s), 13 check(s) passed
```

**Nothing in the grep output pointed at check (4).**  What found it was
**running the tool after the edit** — which is why every executable hit in the
tables above was run on both sides of the deletion rather than read.

**THE REPAIR STATES THE REQUIREMENT INSTEAD OF RELYING ON LIST ORDER**: the
probe is *a delegating suite with at least one non-`0xFFFF` mask*, and if none
is on disk the gate **records a violation rather than passing**.  Probe is now
`v0.3`, firing 16 of 370.  **NEGATIVE CONTROL, run:** restricted to `v0.1` +
`mod3_illegal` the selfcheck **exits 1** — it refuses, it never silently passes.
