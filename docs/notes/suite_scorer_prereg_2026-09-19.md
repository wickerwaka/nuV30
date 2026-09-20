# WAVE 22 — GIVE THE 7.17 M ARCHITECTURAL CASES A SCORER AGAIN

**PRE-REGISTRATION.  Committed BEFORE the first `sw/` edit and BEFORE the first
scored run.**  Date 2026-09-19.  Branch `master`.  Offline only: no board, no
flash, no Quartus, **no `hdl/` edit of any kind**.

WAVE 20 removed the C++ model (`sim/`, ledger `RET-1`).  Its own largest-loss
field reads:

> *"`v0.2` 347,000 + `v0.3` 3,699,998 + `v20suite` 3,125,000 = 7.17 M
> ARCHITECTURAL CASES NOW HAVE NO SCORER AT ALL."*

The USER has authorised closing that gap.  **USER RULING 2026-09-19 governs the
method**: *"treat the documentation as hearsay until proven otherwise. Ucore is
the only valid implementation … Documentation that gives those other
implementations precedence is suspect."*

---

## §0  WHAT I MEASURED BEFORE WRITING THIS, AND IT MOVES THE PROBLEM

Every row below was measured on this tree today, read-only, before any edit.
**It is registered here because several of these facts contradict the briefing
and the standing documents, and a bar written on a false premise is not a bar.**

### §0.1  THE SUITES' REAL SIZES — and the one number that was never 3,699,998

Counted by loading every `*.json.gz` in each suite directory:

| suite | forms | cases ON DISK | docs say | delta |
|---|---|---|---|---|
| `v0.1` | 347 | **169,000** | 169,000 | 0 |
| `v0.2` | 347 | **347,000** | 347,000 | 0 |
| `v0.3` | 370 | **3,700,000** | 3,699,998 | **+2** |
| `v20suite` | 360 | **3,125,000** | 3,125,000 | 0 |
| `mod3_illegal` | 1 file (`goldens.json.gz`) | **128** | 128 | 0 |

**The `+2` is not an error in either place — it is two different denominators
wearing one number**, and the resolution is in `sw/ucsim_check.py`'s own
docstring: `known_divergences.json` is read **BY CLASS**, `VOID` excluded from
the total and `EDGE` not (the model's checker is architectural and the `EDGE`
entry is recorded *arch-CLEAN*).  `3,700,000 − 2 VOID = 3,699,998`.
**`sw/check_core.py` is a CYCLE-ROW checker and excludes all three**, so the
ucore's denominator on the same suite is **3,699,997**.  Registered here so the
results document can quote either without appearing to have moved a goalpost.

### §0.2  ⚠ THE LARGEST FINDING, AND IT IS NOT ABOUT A SCORER

**`v0.2`, `v0.3` AND `v20suite` ARE NOT IN GIT.**  Measured:

| suite | files on disk | files tracked | tracked `*.json.gz` |
|---|---|---|---|
| `v0.1` | 350 | 350 | **347** |
| `v0.2` | 351 | **1** (`.gitignore`) | **0** |
| `v0.3` | 746 | 3 | **0** |
| `v20suite` | 364 | 3 | **0** |
| `mod3_illegal` | 2 | 2 | 1 |

It is DELIBERATE and documented in each suite's own `.gitignore`: `v0.2` —
*"superseded by v0.3; kept disk-only … Whole suite untracked"*; `v0.3` —
*"disk-only for now (916 MB); storage/versioning decided at the
upstream-contribution stage (task #17)"*; `v20suite` — `*.json.gz`, the upstream
SingleStepTests cache its README calls *"not committed (re-fetchable)"*.

**So a figure measured on any of the three is measured against bytes that exist
only on this machine.**  Giving them a scorer does NOT give them a repo-
reproducible GATE, and this wave will not claim one.  Mitigation, registered:
every scored leg records the suite's **per-file sha256 manifest digest** beside
its total, so the figure has an artifact id even though the artifact is not in
the tree.  Measured manifests (`sha256` of the sorted `sha256sum` listing):

```
v0.1          350 files  af07d949a38c166d…
v0.2          351 files  cbc0fde9d9586996…
v0.3          745 files  6abe383d34ac0fa5…   (+ iords/ subdir)
v20suite      363 files  67b8c7d7c83e8af5…   (+ iords/ subdir)
mod3_illegal    2 files  67161a0c409c7fc6…
```

### §0.3  ⚠ `v0.3` SUPERSEDES `v0.2` OUTRIGHT — SO THE "7.17 M" DOUBLE-COUNTS

`tests/v30/v0.3/README.md`, verbatim: *"This tranche is the 10,000-cases-each /
370-form full-scale emission and **supersedes v0.2 outright** (v0.2 was the
1,000-case predecessor; it is retained on disk for its historical role …  but is
obsolete)"* — and *"v0.3 uses the same seed scheme as v0.2 (base `v30-v0.2`), so
its first 1,000 cases per form are prefix-identical to v0.2 wherever the reroll
history agrees … 2.1 % of prefix cases (7,137 of 347,000) differ, entirely from
reroll-history divergence."*

**`v0.2` is therefore ~97.9 % redundant with `v0.3`'s own first thousand per
form.**  The un-scored architectural population is not 7.17 M distinct cases; it
is `v0.3` 3,700,000 + `v20suite` 3,125,000 + `v0.2`'s ~7,137 genuinely distinct
records.  `v0.2` is still scored in this wave — it is cheap, it is an
independently captured population where it diverges, and it is the suite the gap
document says *cannot be run at all*.  But the headline is corrected here rather
than inherited.

### §0.4  THE THREE SUITES' ACTUAL RUNNABILITY — the gap is smaller than written

Measured with `--core ucore` on this tree, one form each:

| suite | runs through `check_core --suite-dir` TODAY? | measured |
|---|---|---|
| `v0.1` | yes | the standing gate, 169,000/169,000 |
| `v0.2` | **NO** — `KeyError: 'opcodes'` at `sw/check_core.py:878` | reproduced |
| `v0.3` | **YES, TODAY, UNCHANGED** — `--opcodes 00 --cases 0` = **10000/10000 full** | reproduced |
| `v20suite` | **YES with `--arch-only`** — `--opcodes 00 --cases 4 --arch-only` = ARCH 4/4; WITHOUT it 0/2 (it is a V20 capture; the flag's own help says *"For the V20 suite"*) | reproduced |
| `mod3_illegal` | **NO** — same `KeyError` dialect | (same site) |

**So `v0.2`'s `KeyError` is the ONE hard blocker, and `v0.3`/`v20suite` were
never blocked — they were never RUN.**  The gap document's *"`v0.2` cannot be
run … `KeyError: 'opcodes'` at `check_core.py:709`"* is right in symptom, stale
in line number (878), and its cause statement — *"the emitter schema"* — is a
DIALECT MISMATCH rather than a defect: there are **three metadata dialects and
the scorer speaks one and a half.**

### §0.5  `known_divergences.json` — WHAT IT ACTUALLY IS, READ BEFORE ANY SCORING

**One file exists in the whole `tests/` tree**: `tests/v30/v0.3/known_divergences.json`,
970 bytes, **three entries**.  Read in full:

| form/idx | class | claim | provenance |
|---|---|---|---|
| `0F1B` / 3917 | **VOID** | *"instrument-failure #3 (ram-vs-instruction physical collision; phys 0xdc30 want 0x89 got 0xC0) … arch+cycle"* | `v03_divergence_ledger.md` F4bc, **2026-07-23** |
| `83.5` / 8683 | **VOID** | same class, phys 0x9799 want 0xA7 got 0x63 | same |
| `646F` / 8988 | **EDGE** | *"known pre-existing 1/10000 cycle edge, repnc OUTSW cx=13 (REP OUTS loop timing, rows 28-32) … **arch-CLEAN (cycle-only)**"* | `v03_divergence_ledger.md:159` |

Its own `_doc` field names the two commits it was established against:
*"byte-identical divergence on the pre-fix RTL (**8fd94df**) and the fixed RTL
(**4508e08**)"*.  **I checked both commits.  They are 2026-07-25, and
`git ls-tree 4508e08 hdl/rtl/` lists `hdl/rtl/core` and NO `hdl/rtl/ucore` —
the ucore did not exist yet.**

**So the provenance is NOT the C++ model the brief suspected.  It is the
ARCHIVED FSM CORE, removed from this tree by WAVE 21 (`RET-2`).**  That is the
same disease with a different name: an accepted-residue list established against
an implementation that no longer exists, inherited by the ucore without ever
being re-tested against it — including by `ucore_gaps_2026-08-04.md` §F.3, whose
229,999/229,999 block-I/O figure carries *"1 documented pre-existing excluded:
646F/[8988]"* as an inheritance.

The two `VOID` entries make an **engine-independent** claim (the emitted golden
image collided code with operand — a property of the capture, established
host-side by readback), so they plausibly survive the engine change.  The
`EDGE` entry makes an **ENGINE** claim about a core that is gone.

**DISPOSITION, REGISTERED: `v0.3` IS SCORED BOTH WAYS** — with the list and with
it disabled — and both numbers are reported.  No exemption is inherited
silently.  A new flag `--no-known-divergences` is added to `sw/check_core.py`
for the second leg (it changes no default).

### §0.6  `tests/v30/v20suite/metadata.toml` — the user's untracked file, MEASURED, NOT TOUCHED

It sits beside the TRACKED `metadata.json` the scorer reads.  **I parsed both
and compared without modifying either.  THEY ARE SEMANTICALLY IDENTICAL**: the
same 8 header keys with byte-equal values (`version` 1.0.2, `cpu` V20,
`generator` arduino8088 v1.1, `date` 2024/05/25, …), the same **282** opcode
entries, **0 keys only in one side, 0 entries differing**.  The `.toml` is
upstream SingleStepTests' native form; the `.json` is the converted copy.

**There is nothing to decide between them and this wave decides nothing.**  It
is reported to the user, left untracked, not `git add`ed, not edited.  (One
adjacent discrepancy, also not resolved here: the suite's README cites upstream
*"suite v1.0.3"* while both metadata files say **1.0.2**.)

### §0.7  `sw/ucsim_check.py` — ESTABLISHED, NOT ASSUMED

Its CLI **already refuses**: `python3 sw/ucsim_check.py --suite tests/v30/v0.2`
prints the `RET-1` banner and exits non-zero.  **But it is still a LIVE LIBRARY**:
`sw/timed_gate.py`, `sw/timed_probe.py` and `sw/uarch.py` all
`from ucsim_check import flags_mask_of, load_meta`.  **And `ucsim_check.load_meta`
is the only place in the tree that already implements the full dialect rule** —
it falls back to `v0.1`'s metadata both when the file is absent AND when it
carries no `opcodes` map, which is exactly the half `check_core` is missing.

**So the model's dead scorer is today the tree's dialect authority, and three
live tools import it to get there.  That is the precedence inversion the user's
ruling names, in its purest form.**  It is NOT ported and it is NOT rewritten:
the rule moves to a new module and `ucsim_check` becomes one of its consumers.

### §0.8  `--residue stale-ea` — THE FLAG EXISTS, ON A REFUSING TOOL

It is `sw/ucsim_check.py`'s, not `sw/check_core.py`'s (`check_core --help`
carries no `--residue`).  `sw/check_mod3_illegal.py`, the other scorer of that
suite, exits **2** with the `RET-2` FSM banner.  **`mod3_illegal` therefore has
no live scorer at all**, and the briefing's *"needs `--residue stale-ea`"* names
a flag reachable only through a refusal.

### §0.9  `--core sim` — ENUMERATED, NOT ESTIMATED

Mechanically enumerated over every `add_argument("--core"…)` in `sw/`:
**45 declarations, of which 24 still offer `"sim"`** in `choices` or `default`
(the brief's estimate was ~40).  **13 of the 24 DEFAULT to `sim`.**  They live in
**20 files**.  All 20 have a working `ucore` leg — none needs a whole-tool
refusal.

⚠ **AND THE TOKEN IS AMBIGUOUS, WHICH IS WHY A GREP IS NOT A DISPOSITION.**  In
this repo `"sim"` also names **a board-capture LEG KEY** — `sw/fz2_a2_replay.py`
declares `LEG = {"real": "socket (use_core=0)", "sim": "fabric core
(use_core=1)"}` — so `j["sim"]` in `sw/f21_wt1.py`, `sw/ie_pinfall_cell.py`,
`sw/tf0f_cell.py` and others means **the FPGA core**, not the C++ model, and
must not be touched.  Following WAVE 21's method finding (*"a token appearing in
an enumeration is not a token that was dispositioned"*), **§4 below registers
that each of the 24 gets an individually recorded disposition, and that the
reported count is a FLOOR.**

---

## §1  WHAT THIS WAVE BUILDS — THE DIALECT ADAPTER

**The rule is ONE SENTENCE, and it is the one `ucsim_check` already had:** *a
suite's opcode map comes from its own `metadata.json` when that file has one,
and from `v0.1`'s otherwise.*  There are therefore **THREE dialects, not four** —
`v0.2` and `mod3_illegal` are the SAME dialect, and the briefing's table splits
them:

| dialect | detector | example suites | opcode map source |
|---|---|---|---|
| **`sst`** | `metadata.json` exists AND has `opcodes` | `v0.1`, `v20suite` | itself |
| **`emitter`** | `metadata.json` exists, NO `opcodes` | `v0.2`, `mod3_illegal` | **delegates to `v0.1`** |
| **`absent`** | no `metadata.json` | `v0.3`, every `v0.1-w*`/`*evt`/derived tranche | **delegates to `v0.1`** |

New module **`sw/suitemeta.py`**, with `load(suite) -> SuiteMeta` carrying
`.dialect`, `.source`, `.delegated`, `.opcodes`, `.flags_mask(form)`,
`.dont_care(form)`.  **The four sites that read `meta["opcodes"]` directly**
(`sw/check_core.py:878`, `sw/emit_suite.py:2282`, `sw/uarch.py:49`,
`sw/ucsim_check.py:118`/`:133`) are re-pointed at it, and the three live
importers stop reaching the model's scorer for the rule.

**SIMPLICITY (user directive 2026-08-01, verbatim): *this is 80's era hardware —
nothing on the die is wasted. Complex or confusing observed behavior is likely
simple systems interacting in ways not yet understood. A large fitted table, a
many-cased rule, or a per-opcode special case is a signal of misunderstanding,
not a deliverable.***  Applied here: **no per-suite and no per-opcode branch.**
Three declared dialects, one predicate each, one delegation target shared by two
of them.  If the implementation needs a fourth case, that is a finding to report,
not a case to add.

**W-4's POSITIVE CONTROL: `python3 sw/suitemeta.py --selfcheck`** — asserts each
of the three dialects is REACHED by a real suite on disk (`sst` by `v0.1`,
`emitter` by `v0.2`, `absent` by `v0.3`), that delegation is ANNOUNCED rather
than silent, and that a `flags_mask` resolved through a delegating dialect equals
the one `v0.1` resolves for the same form.  **Non-vacuity: it must FAIL when the
delegation target is pointed at a map that lacks the form.**

### §1.1  THE ONE POLICY CHOICE, AND IT IS SCORED BOTH WAYS

Delegation gives `v0.2` **`v0.1`'s real flags-masks**.  The gap document's
suggestion was instead *"fall back to `flags_mask = 0xFFFF`"* — which masks
nothing and is STRICTER.  Masking is the correct comparison (the mask encodes
flag bits the part leaves undefined for that form), but the choice moves the
number, so **`v0.2` is scored on BOTH legs**: primary = delegated masks,
control = `--raw-flags` (0xFFFF, nothing masked).  Both are reported.

---

## §2  THE BARS

### W-1 — pre-registration
**MET by this document's commit**, which precedes the first `sw/` edit and the
first scored run.  Falsifier: `git log` order.

### W-2 — `v0.1` ZERO-DELTA ACROSS THE ADAPTER  ⬅ THE CONTROL
`python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.1 --opcodes all
--cases 0`, run BEFORE the adapter and AFTER it, with per-form lines captured
both times.

* **PASS** — the two runs' per-form line sets are **byte-identical**, and the
  total is **169,000/169,000 full (cycles 169,000, arch 169,000)**.
* **STOP** — any per-form line differs, in either direction, by one case.
  *"If your adapter moves `v0.1` by one case, the adapter is wrong."*

### W-3 — EACH SUITE HAS A REAL TOTAL WITH A FAILURE TAXONOMY
**⚠ THE RATE IS A RESULT, NOT A BAR.  A suite scoring below 100 % is a
REPORTABLE MEASUREMENT and the harness will not be tuned until it goes green.**
These suites have never been scored against the ucore; the totals are unknown.

What is registered is the SHAPE of an acceptable outcome, and the predictions
that the run is allowed to refute:

| leg | command | PASS = | PREDICTION (refutable) |
|---|---|---|---|
| `v0.2` primary | `--suite-dir tests/v30/v0.2 --opcodes all --cases 0 --waits 0` | completes; prints a total over **347,000**; taxonomy reported | **≥ 99.0 %** — same 347 forms as `v0.1`, which is 100 % |
| `v0.2` mask control | `… --raw-flags` | completes; total reported beside the primary | **≤ the primary** (nothing masked is stricter) |
| `v0.3` with the list | `--suite-dir tests/v30/v0.3 --opcodes all --cases 0 --waits 0` | completes; total over **3,699,997** (3 excluded) | **≥ 99.0 %** |
| `v0.3` without the list | `… --no-known-divergences` | completes; total over **3,700,000** | the 2 `VOID` cases **FAIL** (contaminated goldens, engine-independent); the 1 `EDGE` case is **THE OPEN QUESTION** and either answer is a result |
| `v20suite` | `--suite-dir tests/v30/v20suite --opcodes all --cases 0 --arch-only` | completes; ARCH total over **3,125,000** | **≥ 99.0 %** — it is the independent µPD70108 oracle and `pilot_v20` once closed it at 100 % against the model |
| `mod3_illegal` | `--suite-dir tests/v30/mod3_illegal --opcodes goldens --cases 0` | completes; total over **128** | **most or all 128 FAIL** on the destination register — the suite's whole subject is a stale-EA residue no injected engine reproduces. The FINDING is whether the divergence is **CONFINED** to that register, which is the metadata's own claim |

**FINDING bands, pre-registered so no band is chosen after the fact:**
`≥ 99.9 %` = as expected · `99.0 – 99.9 %` = FINDING, taxonomy reported ·
`< 99.0 %` = FINDING, reported as a measured number with its taxonomy and NOT
repaired in this wave · `0 %` or a non-case crash = **STOP**.

**HARD STOPS, any leg:** `SIM FAILED` · `EU BOUND VIOLATED ON A GOLDEN CASE`
(`check_core`'s own hard failure — the store bound is a theorem on golden
corpora) · any belief that an `hdl/` edit is required.

**Taxonomy instrument**: `--result-log` today writes ONLY on the `--arch-only`
branch.  It is extended to the cycle branch so every leg emits per-form JSONL
(`opcode`, `cases`, `passed`, `failed`, first-divergence classes).  This is an
additive change to a reporting path; `v0.1`'s W-2 control covers it.

### W-3b — `v0.3` RUNTIME PLAN, REGISTERED BEFORE THE RUN
Measured today, `--cases 0`, one form at a time, `--core ucore`:
`00` **5.55 s** · `E8` 6.31 s · `F6.4` 7.82 s · `9A` 7.83 s · `F3A5` 7.22 s ·
`F36F` 10.32 s · `CC` 10.42 s.  **Mean ≈ 8.0 s per 10,000-case form.**

**ESTIMATE: 370 forms × 8.0 s ≈ 2,960 s ≈ 50 minutes.**  `v20suite` is 360 forms
/ 3,125,000 on the cheaper `--arch-only` path; budget the same.

**PLAN: run both in FULL, detached and logged, `v0.3` and `v20suite`
concurrently (8 cores available).  BUDGET 2.5 h per leg.**  If a leg exceeds its
budget it is NOT silently truncated: the per-form `--result-log` is already on
disk form by form, and the results document reports **exactly which forms
completed**, with the remainder booked as un-run.  No slice is substituted for a
whole and then quoted as one.

### W-4 — THE ADAPTER DECLARES EACH DIALECT
Three dialects, one predicate each, no per-suite or per-opcode special case.
Positive control `sw/suitemeta.py --selfcheck`, non-vacuous (§1).

### W-5 — THE LIVE LADDER IS ZERO-DELTA
Measured before and after, same commands, from the briefing's list:
`check_core --core ucore --opcodes all --cases 0` **169,000** at `--ce-div`
**2 / 3 / 4 / 8** with **div 1 REFUSED** · the four HLT sweeps **WITH
`--waits 0/1/2/3`** = **279/283** · `ss_lint` **232 / 229 flops / 4 whitelist /
0 UNMAPPED / `SS_VERSION` 0x8F / `SS_TAG` 0x8FE8** · `cutset_lint` **PASS 81/0** ·
`phase_split_lint` **157/779/0** · `r7_lint` PASS · `qsf_lint --check` PASS ·
`core_portlist_lint` PASS **4 configs** · `test_quartus_gate` **302/302** ·
`test_artifact` **45/45** · `chainflat_relocation_check` **9/9** ·
`chain_lfsr_gate` four signatures BYTE-IDENTICAL · `demux_off_gate` PASS ·
`check_ucore_tables` (G0) PASS **9,988** · `check_boot` **220** and **400** ·
`check_ab_sim --core ucore` **187** · `ghost_launch_law` **200/200** ·
`check_fuzz_bank` PASS **621**.
**Every one of those figures is HEARSAY until this wave measures it**, and where
a measurement disagrees with the briefing or with `standing_gates.md`, **the
measurement is reported and the document is fixed.**

### W-6 — NOTHING IN `hdl/` IS EDITED AT ALL
`git diff --stat -- hdl/` is EMPTY at the wave's end.  If an `hdl/` edit ever
looks necessary: **STOP AND REPORT.**

### W-7 — THE USER'S UNCOMMITTED WORK IS UNTOUCHED
**NO `git stash`, NO `git checkout .`, NO `git reset --hard`, EVER.**
`git add` BY EXPLICIT PATH only.  `sw/testdata/receipts/*.jsonl` is **NOT**
staged; any receipt this wave needs is committed BY VALUE under the wave's own
directory.  `tests/v30/v20suite/metadata.toml` is not added, not edited.

### W-8 — NO GATE DIES SILENTLY
Anything retired or re-pointed gets a ledger entry naming its last measured
figure and what replaces it — **"nothing" is an acceptable answer if it is
said.**

---

## §3  THE `sim` HALF OF THE PRECEDENCE CLEANUP

**24 `--core` declarations in 20 files offer a `"sim"` that no longer exists**
(§0.9).  Today each of them already REFUSES when `sim` is selected — the refusal
comes from `sw/simbin.py`'s `RET-1` banner, reached through `tf.run_sim` — so the
defect is not a crash, it is that **`--help` and `choices` still advertise a dead
engine, and 13 tools DEFAULT to it.**

Registered shape, following WAVE 21's `sw/fuzz_campaign.py` precedent
(`default=None` + refuse-with-instruction) rather than inventing one:

* `"sim"` leaves every `choices` list, and every help string stops naming it as
  an engine.
* **A declaration whose `default` was `"ucore"` keeps its default** — every
  registered `--core ucore` invocation runs verbatim.
* **A declaration whose `default` was `"sim"` becomes `default=None` and
  REFUSES BY NAME**, citing `RET-1` and saying to pass `--core ucore`
  explicitly.  ⚠ **It does NOT silently become `ucore`**: re-pointing a
  registered model invocation onto a different engine would produce a number
  under the old command line, which is *"re-label, never re-register"* — the
  thing `sw/fsmcore.py`'s own banner forbids.
* `sw/simbin.py` gains `refuse(who, code=2)`, mirroring `sw/fsmcore.refuse`, so
  a tool says NO with a banner instead of raising a traceback.
* A single argparse `type=` validator is the whole mechanism — **one declaration
  form applied 24 times, not 24 special cases.**

**⚠ THE COUNT IS REPORTED AS A FLOOR, AND EACH HIT GETS A RECORDED
DISPOSITION** — fixed / marked-history / deliberately-left-with-reason — because
the token `"sim"` also names a board-capture leg key (§0.9) and a swept token is
not a dispositioned token.  **No gate is built for this in the same sitting that
needs it**: WAVE 21 booked that deliberately on the grounds that its first green
would be unfalsifiable, and that reasoning is adopted here unchanged.

---

## §4  WHAT THIS WAVE WILL NOT DO

* **No `hdl/` edit.**  The requirement is in silicon at FLASH #23.
* **No board, no flash, no Quartus, no Codex, no nested subagent.**
* **No harness tuning to make a suite green.**  A low rate is the deliverable.
* **No resolution of `metadata.toml` vs `metadata.json`** — the user's call.
* **No inherited exemption**: `known_divergences.json` is scored both ways and
  its FSM provenance is stated, but **the list is not edited and no entry is
  deleted** on a single wave's reading.  Re-provenancing it is booked.
* **No re-derivation of `v0.2` as a distinct population.**  §0.3 establishes it
  is ~97.9 % redundant with `v0.3`; quantifying the exact distinct remainder is
  booked, not taken.
