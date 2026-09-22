# WAVE 29 — **THE PROVENANCE STAMP IS ONE DERIVATION AND IT CAN REFUSE.  THE BRIEF SAID FOUR WRITERS; THE TREE HAD SEVEN, AND THE ONE THE CENSUS MISSED WAS FOUND BY THIS WAVE'S OWN GATE.**

**USER INSTRUCTION 2026-09-21: *"Fix the `_truth_stamp` provenance bug"*.**

Session `https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.
Implementation `40642891fb`.

    branch        master
    HEAD at start 41d5713ad0  (WAVE 28 / FLASH #24 ladder)
    hdl/          TRACKED-CLEAN, NOT TOUCHED -- `git status --porcelain hdl/`
                  has no tracked entry, before and after
    board         FLASH #24, untouched.  sw/testdata/flash_log.jsonl 27 entries,
                  sha256 7496b4be2d1771c91c8367f371f7102d9e5ee7158655d8cf8fd2a2a9988d827d
                  -- byte-identical to the brief's registered value
    Quartus       NOT RUN.  No bitstream built, nothing flashed
    ledger        docs/notes/invalidation_ledger.md -- a SEVENTH register, PRV-n,
                  and its first entry PRV-1

---

## 0. THE HEADLINE

> ### 1. ⭐⭐ **THE REPORTED DEFECT IS REAL AND IT IS LATENT — VERIFIED, NOT INHERITED.**
>
> `_truth_stamp()` did return the socket constant from `ENGINE == "chip"` alone
> and never consulted `EMIT_USE_CORE`.  **But both call sites are guarded** — each
> is preceded by `if ENGINE == "chip" and EMIT_USE_CORE is not False: raise
> RunError(...)` (`emit_suite.py:2529`, `:2695`) and `cmd_reemit` has a third
> (`:2475`).  **Measured, all three: they fire.**  ⭐ **So no golden in the tree
> carries a false stamp by that path**, and the wave was sized on that finding
> rather than on the brief's headline.
>
> ### 2. ⭐⭐⭐ **THE LARGER DEFECT WAS SEVEN WRITERS OF ONE CLAIM, AND THE BRIEF'S CENSUS OF FOUR WAS AN UNDERCOUNT — FOR THE EXACT REASON THE WAVE IS ABOUT.**
>
> `sw/char_enter.py` writes the class **twice**, spelled `"SOCKET "
> "(use_core=False)"` and `"SOCKET (use_core=False)"`.  **The census grep looked
> for `SOCKET (real chip`, so it missed both.**  They were found by WAVE 29's own
> gate, on its first run, by a check that looks for a *literal-valued
> `truth_source`* rather than for a particular string.  ⭐ **A TYPED PROVENANCE
> CLAIM CANNOT BE AUDITED BY GREP — that is not a remark, it is this wave's
> measurement.**
>
> ### 3. ⭐⭐ **P-5's AUDIT: ONE RECORD IN THE TREE IS MISLABELLED, NONE IS FALSE, AND NOTHING WAS EDITED.**
>
> `tests/v30/s10-hltsweep-w1/emit_log.txt` asserts `SOCKET (real chip,
> use_core=False)` **and** `No board contact` **in the same sentence**.  Every
> FACT in it is true; the **CLASS LABEL** is a capture's, and that run made none.
> **A MISLABELLED CLASS, NOT A FALSE CLAIM** — and the ledger had no word for
> the difference, so **a SEVENTH register was opened whose disposition is
> ANNOTATE, NEVER REWRITE**: `PRV-1`.
>
> ### 4. ⚠ **AND AN ERRATUM AGAINST THE LEDGER'S OWN CONTROL SENTENCE.**
>
> `invalidation_ledger.md:1696` says *"every `emit_log.txt` opens `# TRUTH
> SOURCE: SOCKET (real chip, use_core=False)`, and the four suites predating
> that header carry the equivalent in `metadata.json`."*  **Both clauses are
> false as written**: `tests/v30/v0.1/emit_log.txt` is **7,168 lines with ZERO
> truth lines**, and `v0.1`/`v20suite`'s `metadata.json` are the SingleStepTests
> dialect with **no `truth_source`, no `use_core`, no `capture` field**.  ⭐ **The
> conclusion it supports survives and is STRONGER than a stamp** — `v0.1` has no
> stamp because the `use_core` flag did not exist when it was emitted — **but it
> is an argument, not a record, and this is the first document that says so.**

---

## 1. THE SINGLE DERIVATION — ONE RULE, THREE INPUTS, FOUR CLASSES, ONE REFUSAL (P-1, P-2)

`sw/emit_suite.py`: `truth_stamp(use_core=<the pin>, banked=None)`, public,
replacing the private `_truth_stamp()`.  **No per-caller special case exists in
it.**

| class | when | the line |
|---|---|---|
| **SOCKET** | engine `chip`, position **False** | `SOCKET (real chip, use_core=False)` — **byte-identical to the historical constant**, so every existing record stays comparable |
| **FPGA CORE** | engine `chip`, position **True** | `FPGA v30_core inside system_large (use_core=True) -- THE DUT, NOT SILICON` |
| **VERILATOR TB** | engine `tb` | `VERILATOR TB core=<core> -- NOT A GOLDEN, NOT SILICON` |
| **BANKED REPLAY** | `banked=` given | `BANKED REPLAY, re-parsed offline -- NO BOARD CONTACT IN THIS PROCESS.  <the bank>` |
| **REFUSED** | see below | raises `TruthSourceError(RunError)` |

⭐ **`BANKED REPLAY` IS THE THIRD TRUTH CLASS THE BRIEF ASKED FOR, AND IT IS
NEITHER OF THE OTHER TWO.**  `s12_census regold` re-derives goldens from a
banked `.raw.hex.gz` and touches nothing: the bytes came off silicon in an
**earlier** session whose own `manifest.json` is the record, and **this** process
made no capture.  Forcing that into "socket" is exactly the defect; forcing it
into "verilator" would be a different lie.

### 1.1 THE THREE INPUTS, AND WHICH ONE IS EVIDENCE

1. **`ENGINE`** — this module's record source.
2. **the A/B POSITION** — `EMIT_USE_CORE`, the pin `_capture` actually passes to
   `run_image`; or one **named explicitly for a SINGLE LEG** of a two-leg
   experiment (`w28_ea_lane_fabric`, `exp_iret`, `char_enter`).
3. ⭐ **`v30run.board_witness()` — NEW, and the only one of the three that is
   EVIDENCE rather than intention.**  `run_image` appends one record **the
   instant the CFG command is accepted**, carrying the `use_core` value it
   actually sent, the div, the waits and the path.  Recorded *before* the run
   rather than after it, because **a capture that failed still touched the
   board**, and a provenance instrument that forgets the failures is not a
   witness.

⚠ **`use_core=None` IS RECORDED AS `None` AND IS NOT A SYNONYM FOR `False`.**
It means `ServeRunner.cfg` sent `'-'` and left the board's **STICKY CFG** alone,
so the A/B position of that capture is unknown to this process.  **That is the
case a derived stamp must refuse on**, and it is why the witness stores the
value rather than a boolean *"touched"*.  The legacy path, which cannot set
`use_core` at all, records `None` for the same reason.

### 1.2 THE WITNESS IS A CONTRADICTION TEST, AND THE CODE SAYS SO

⚠ **ITS SCOPE IS `run_image`, WHICH IS ONE-SIDED, AND THAT LIMIT IS WRITTEN INTO
`v30run.py` RATHER THAN GLOSSED.**  A tool that drives `ServeRunner` directly
(`v30run.cmd_profile`, `t11_clientpath_gate`) is invisible to it.  So the
witness **CAN CONTRADICT A CLAIM AND CANNOT CERTIFY ONE**, and `truth_stamp`
uses it only that way: an empty witness is not consulted, and nothing infers
*"no board was touched"* from it.

### 1.3 THE REFUSALS (P-2)

It **raises**, it does not fall back — every caller is about to write a
provenance line, and a line nobody can establish must stop the write:

* the position is **`None`** — the sticky CFG decided;
* the board **WAS** commanded into a position this stamp does not claim (a
  mid-emission `EMIT_USE_CORE` mutation — exactly what `x1_fabric`,
  `u4_f42_fabric`, `f13_formfab`, `sm3_s16_fabric` and `w28_ea_lane_fabric` do
  on purpose; they must stamp PER LEG and now they cannot fail to);
* **`banked=`** is claimed and a board **was** commanded;
* **engine `tb`** and a board **was** commanded;
* **both** `banked=` and a position (two truth classes for one record);
* **`ENGINE`** has no class.

### 1.4 ⚠ ONE RESIDUAL, NAMED, AND ANSWERED BY THE FILE'S OWN PRECEDENT

The golden emitters write their header stamp **BEFORE the first capture**, so on
that path the witness is empty and the stamp is the pin, uncross-checked.
`cmd_emit` therefore writes a **second** line at the END of the emission —
`# TRUTH WITNESS: N board command(s), use_core position(s) commanded = [...]` —
placed beside the existing `# DIVIDER:` line **and for the identical reason
already written there**: *"a line written at the end records what the connection
actually COMMANDED, not what this file intends."*  It names an empty witness as
empty, which on a chip emission is itself a finding.

---

## 2. THE WRITERS AFTER THE CHANGE, AND THE ONE-PLACE GREP (P-3)

    $ grep -rn --include='*.py' "SOCKET (real chip" sw/
    sw/emit_suite.py:453:        return "SOCKET (real chip, use_core=False)"

    $ grep -rn --include='*.py' "FPGA v30_core inside" sw/
    sw/emit_suite.py:454:    return ("FPGA v30_core inside system_large (use_core=True) "

**EXACTLY ONE PLACE EACH, BOTH INSIDE `truth_stamp()`.**  (The gate re-derives
this over **388 tracked `sw/*.py`** every run, and assembles the needles from
fragments so that it is not itself the second writer it forbids.)

| # | writer | before | after |
|---|---|---|---|
| 1 | `emit_suite.truth_stamp()` :453 | DERIVED from `ENGINE`; **ignored `EMIT_USE_CORE`** | **THE derivation** |
| 2 | `s10_board.py` :266 | hard-coded constant | `es.truth_stamp()` |
| 3 | `s13_board.py` :148 | hard-coded constant | `es.truth_stamp()` |
| 4 | `s12_census.py` :370 | hard-coded constant, **on a run that touches no board** | `es.truth_stamp(banked=…)` — **the third class** |
| 5 | `char_mod3.py` :158 | hard-coded constant (JSON manifest) | `es.truth_stamp()` |
| 6 | **`char_enter.py` :184, :249 → :190, :256** | ⚠ **TWO hard-coded constants the census MISSED**, spelled differently | `es.truth_stamp(use_core=False)` |
| 7 | `exp_iret.py` :322 | hard-coded constant (JSON manifest), **a two-leg experiment** | `es.truth_stamp(use_core=False)` — the leg the field describes |
| 8 | `w28_ea_lane_fabric.py` :219, :223, :112 | per-leg typed constants + a per-ROW label | `es.truth_stamp(use_core=…)` ×3 — **so a row and the manifest above it cannot disagree** |
| — | `b2_ea_lane.py` :149, `w26_ea_lane2.py` :153 | called `es._truth_stamp()` | the renamed public function |

⚠ **`sw/exp_iret.py` IS RET-2-RETIRED AND CANNOT RUN** — it imports `exp_race`,
which refuses for the removed FSM core.  Its constant was **dead code**.  It is
repaired anyway and that is stated rather than quietly skipped.

⚠ **`sw/f13_formfab.py` writes NO stamp at all** and labels its two legs
`chip`/`core` structurally in the record.  It is a two-position tool with no
provenance claim to get wrong; recorded so a later reader does not "fix" it into
one.

⚠ **FIVE FILES WERE NOT TOUCHED BECAUSE THEY ARE THE USER'S OWN UNCOMMITTED
WORK** (`sw/t7_sim_ab.py`, `sw/t7_sim_proof.py`, `sw/char_divergence.py`,
`sw/fz2_a1_replay.py`, `sw/fz2_a10_replay.py`, `sw/_s14_ret_draw.sh`, the three
`rep_cl0` scripts).  **None of them writes a provenance stamp** — checked, not
assumed.

---

## 3. THE GATE, AND ITS FOUR POSITIVE CONTROLS (P-3, P-4)

**NEW STANDING GATE: `python3 sw/truth_stamp_lint.py` — PASS 23/23, ~1 s,
offline, exit 0/1.**  Artifact `sw/testdata/wave29/truth_stamp_lint.log`.

| leg | what it holds |
|---|---|
| **G1/G2** | the socket string and the FPGA-core string each occur **EXACTLY ONCE** in 388 tracked `sw/*.py`, at `emit_suite.py`, **inside `truth_stamp()`**; and this gate is not itself a writer |
| **G3** | **no other file writes a provenance VALUE from a literal** — a quoted-valued `"truth_source"` key, or a `TRUTH SOURCE:` prose line whose next token is not a substitution.  ⭐ **THIS IS THE LEG THAT FOUND `char_enter`** |
| **P-4** | the four classes and **seven refusals**, by perturbation of the pin / the engine / the witness |
| **P-4d** | the three **pre-existing** emitter guards still fire |

### 3.1 THE FOUR CONTROLS THE BRIEF REGISTERED, MEASURED

| | registered | measured |
|---|---|---|
| **(a)** with `EMIT_USE_CORE=True` the stamp **changes or refuses**, and must NOT read socket | changes | ⭐ **`FPGA v30_core inside system_large (use_core=True) -- THE DUT, NOT SILICON`** — not the socket string, and it says NOT SILICON |
| **(b)** with the engine a TB it **names the TB** | names it | ⭐ **`VERILATOR TB core=ucore -- NOT A GOLDEN, NOT SILICON`** |
| **(c)** the banked-replay class **names itself** | names itself | ⭐ **`BANKED REPLAY, re-parsed offline -- NO BOARD CONTACT IN THIS PROCESS.  <bank>`** — and it is neither of the other two strings |
| **(d)** the existing guards **still fire** | all three | ⭐ **`cmd_emit`, `cmd_emit_boundary`, `cmd_reemit` all raise `RunError` naming the truth source** |

Plus the **seven refusals**, each measured with its message: position `None` ·
`banked=` + a position · unknown `ENGINE` · a socket claim contradicted by a
`use_core=True` board command · a `banked` claim with a board command on record
· a `tb` claim with a board command on record · a capture that left the sticky
CFG alone.  And two positive companions: **the position the board WAS commanded
into still stamps**, and ⭐ **an argparse `0`/`1` normalises EXACTLY as
`ServeRunner.cfg` does** — `cfg` sends `int(bool(use_core))` for every non-None
value, so `0`/`1` and `False`/`True` are the SAME position to the board and
treating them as different claims would have been a SECOND RULE where the
hardware has one.  **`None` is the only unstampable position**, and the same
normalisation is applied to the witness, so `x1_fabric` and `sm3_s16_fabric`
(which pin the module to ints) are compared on the value the hardware
received.

### 3.2 ⭐ THE GATE'S OWN NON-VACUITY, BOTH DIRECTIONS (artifact `sw/testdata/wave29/truth_stamp_nonvacuity.log`)

*Fifteen instruments in this campaign returned confident wrong answers, so this
one is falsified in both directions before it is quoted.*

| control | perturbation | result |
|---|---|---|
| **NV-1** | a second socket literal spliced into `sw/b2_ea_lane.py:149` | ⭐ **FAIL 21/23, rc=1** — *both* the one-place check (`hits=['sw/b2_ea_lane.py:149', 'sw/emit_suite.py:453']`) and the no-second-writer check fired, **each naming the path and line** |
| **NV-2** | `truth_stamp` reverted to the WAVE 28 behaviour (`pos = False`, the pin ignored) | ⭐ **FAIL, rc=1** — the FPGA-CORE class check FAILED reading `SOCKET (real chip, use_core=False)`, **and two refusals stopped refusing** (`position None`, `non-boolean position`) |
| restore | both perturbations reverted | **PASS 23/23**, and `git diff` shows no residue of either |

---

## 4. P-5 — THE AUDIT OF THE EXISTING PROVENANCE RECORDS.  **READ, NOT REWRITTEN.**

⚠⚠ **NOT ONE BYTE OF ANY EXISTING PROVENANCE RECORD WAS EDITED.**  `CLAUDE.md`:
*"deleting a true record corrupts a truthful ledger exactly as badly as
inventing one."*  Retroactively "correcting" a provenance line destroys the
evidence of what the tree believed when the artifact was made — which is the
only thing that lets a later reader find the defect at all.

**READ**: all **18** `emit_log.txt` / `capture.log` files in the tree, plus
`tests/v30/v0.3/reemit.log` (0 truth lines, claims nothing), plus every
per-suite `metadata.json` provenance field, plus the `v0.2` records WAVE 27
preserved at `tests/v30/v02-unique-archive/provenance/` (`emit_log.txt.gz`,
`metadata.json.gz`, `run_manifest.json.gz`).

### 4.1 ⭐ IS ANY EXISTING PROVENANCE LINE FALSE?  **NO — AND THAT IS A MEASUREMENT.**

**No record in the tree claims the socket for a run that used the FPGA core.**
Every writer of a socket claim either sits behind a `use_core`-refusal guard
(`emit_suite.cmd_emit` / `cmd_emit_boundary` / `cmd_reemit`;
`s10_board`/`s13_board` assert `es.EMIT_USE_CORE is False` at import) or passes
`use_core=False` **explicitly on every capture** (`char_mod3`, `char_enter`,
`exp_iret`).  The tools that set `EMIT_USE_CORE = True` (`x1_fabric`,
`u4_f42_fabric`, `sm3_s16_fabric`, `f13_formfab`, `x1_retention`,
`w28_ea_lane_fabric`) reach `emit_case`, never `cmd_emit`, and `cmd_emit`'s
guard would refuse them.  **No `VERILATOR TB` line exists anywhere**, so no
golden was emitted offline.

### 4.2 ⭐ WHAT I FILED: **`PRV-1`, A SEVENTH LEDGER REGISTER**

| | |
|---|---|
| the record | `tests/v30/s10-hltsweep-w1/emit_log.txt` — the provenance of 46 of 49 `HLT.INT` goldens on the standing `279/283` sweep |
| what is wrong | it asserts **`SOCKET (real chip, use_core=False)`** and **`No board contact`** in the same sentence.  Its writer, `s12_census.py cmd_regold`, **touches no board** |
| is it FALSE? | ⭐ **NO.**  Every fact is true, the bank is named by path, its sha is in the named manifest, and the contradiction is visible in the same sentence.  **A MISLABELLED CLASS, NOT A FALSE CLAIM** |
| rig defect | **NONE.**  The banked raws are true silicon and stay in every gate set |
| writer defect | `s12_census.py:364`, **FIXED** this wave — `truth_stamp(banked=…)` now REFUSES if the process commanded the board at all, so *"No board contact"* is checked rather than typed |
| **disposition** | ⚠ **THE FILE IS NOT EDITED.**  `PRV-1` is its annotation |
| gate status | **UNMOVED** — the w1 sweep is `93/95`, the four sweeps `279/283` |

⭐ **WHY A NEW REGISTER.**  Filing this as `ERR-n` would have said something
untrue: `ERR-n`'s disposition is **RECOMPUTED IN PLACE**, and its subject is a
column *computed from* a capture.  A provenance line is not computed from the
capture — it is the **statement about where the capture came from** — and
recomputing it in place is the corruption the rule forbids.  **So `PRV-n`'s
disposition is the OPPOSITE of `ERR-n`'s: ANNOTATE, NEVER REWRITE.**  Not an
`INV` (rig defect NONE, every byte true silicon), not a `SUP`/`EXC` (no
population moved), not a `DEV` (no gate's claim narrowed — a gate was created).

### 4.3 FOUR FURTHER AUDIT FINDINGS, EACH WITH ITS REASON FOR **NOT** BEING A `PRV`

| # | finding | why not a `PRV-n` |
|---|---|---|
| **A-1** | ⚠ **AN ERRATUM AGAINST THE LEDGER'S OWN CONTROL SENTENCE** (`invalidation_ledger.md:1696`, the composed-AD-mask row): *"every `emit_log.txt` opens `# TRUTH SOURCE: …`, and the four suites predating that header carry the equivalent in `metadata.json`."*  **Measured: `tests/v30/v0.1/emit_log.txt` is 7,168 lines with ZERO truth lines** (it is a reroll log), **and `v0.1`/`v20suite`'s `metadata.json` are the SingleStepTests dialect with no `truth_source`, no `use_core`, no `capture`.**  Only `v0.2` carries the equivalent — `"use_core": false` + `"capture": "socketed chip (use_core=False) = golden reference"`, in **both** the preserved `metadata.json` and `run_manifest.json` | it is an erratum against a **DOCUMENT**, not a record of provenance.  ⭐ **AND THE CONCLUSION SURVIVES, STRONGER**: `v0.1` has no stamp because **the `use_core` flag did not exist when it was emitted** — `emit_suite.py`'s own pin comment records it (*"use_core was added AFTER v0.1 emission (2035cce, post-8b5a7d7), so v0.1 always used the socket"*) — and an argument from a flag's non-existence beats a stamp.  ⚠ **But it is an argument, not a record, and no document said so before this one.**  The sentence is **recorded, NOT rewritten** |
| **A-2** | **FIVE SPELLINGS OF ONE CLAIM across the goldens**: `SOCKET (real chip, use_core=False)` · `SOCKET (use_core=False, EMIT_USE_CORE)` (`mod3_illegal`) · `SOCKET (use_core=False)` (`enter_nesting` ×2) · `socketed chip (use_core=False) = golden reference` (`v0.2`) · PRV-1's compound | no record is mislabelled — they are all true, in five dialects.  ⭐ **It is the audit's own evidence for why the repair had to be ONE WRITER, and for why the brief's census was an undercount** |
| **A-3** | **`tests/v30/s10-hltsweep-w0/` has NO provenance record at all** (two `.json.gz`, no `emit_log.txt`), while `w1` has PRV-1's and `s13-hltsweep-w2`/`-w3` have board-written ones | an ABSENT record makes no claim, so there is nothing to mislabel.  Recorded because a reader comparing the four sweeps will see the asymmetry |
| **A-4** | **`tests/v30/v0.3/emit_log.txt` stamps `seed_base=v30-v0.2`** on all three of its truth lines while living in the `v0.3` directory | `seed_base` is not a truth source; it is the documented fixed base the suite was emitted under.  Recorded so it is not read as a misplacement |

---

## 5. THE LADDER (P-6)

*Filled in by the ladder's own run; see §5.1.*

---

## 6. DOCUMENTATION DISCREPANCIES — **REPORTED AS A FLOOR** (P-10)

| # | where | what is wrong | disposition |
|---|---|---|---|
| **D-1** | `docs/notes/flash24_results_2026-09-21.md` §10 D-1 | it reports `_truth_stamp()`'s defect and dispositions it *"RECORDED, SOURCE NOT EDITED … belongs to whoever next needs a core-leg emitter"*, **and names FOUR writers** | ⭐ **DISCHARGED by this wave, and its census CORRECTED to seven.**  The FLASH #24 document is **NOT edited** — it is a results document and its D-1 was true when written |
| **D-2** | `docs/notes/invalidation_ledger.md:1696` | see **A-1** — both clauses false as written | **RECORDED in `PRV-1`'s audit section, NOT rewritten.**  The conclusion it supports is re-derived from a stronger premise in the same place |
| **D-3** | `sw/w28_ea_lane_fabric.py` module docstring | it said *"`emit_suite._truth_stamp()` MAY NOT BE USED HERE"* | **UPDATED** — it now records that WAVE 29 fixed the derivation instead, and that each leg is still stamped from the value it passed, by the one writer, and now checked |
| **D-4** | `CLAUDE.md` gate quick reference | `ss_lint` still presented as `0x8D / 226 / 0x8DE2 / 214 flops`; the tree measures **232 / 229 / 4 whitelist / 0 UNMAPPED** | **PRE-EXISTING, RE-CONFIRMED for the fourth consecutive wave** (WAVE 26, 28 booked it).  `standing_gates.md` §B is correct.  Not repaired here — this wave's `CLAUDE.md` edit is the banner |
| **D-5** | `sw/exp_iret.py:84` | it passes `stub_linear=TARGET` to `v30run.run_test`, whose own docstring says **`stub_linear=` IS GONE** and that a caller passing it *"should hear so"* — so the call would raise `TypeError`.  The file is **already dead** at import (RET-2, via `exp_race`) | **RECORDED, NOT FIXED.**  Reviving a RET-2-retired instrument is not this wave's, and its provenance stamp was repaired without reviving it |
| **D-7** | ⚠ **`sw/s12_census.py cmd_regold` — PRV-1's OWN WRITER — RE-DERIVES `0 of 49` GOLDENS TODAY**, measured: `python3 sw/s12_census.py regold --form HLT.INT --waits 1` prints `HLT.INT w1: 0/49 goldens re-derived`, every delay failing `only 12 register words before the done marker`.  **PRE-EXISTING and provably not this wave's** — `git diff HEAD~1 -- sw/s12_census.py` touches only the `if args.write and tests:` write block, which the empty `tests` never reaches.  It is a **WAVE 24 §E-class finding** (*"the emitter and the scorer are in different image eras, and no gate sees it"*, `invalidation_ledger.md` § E) | **RECORDED, NOT FIXED — and it has a CONSEQUENCE that is stated rather than hidden**: the corrected `BANKED REPLAY` stamp **could NOT be exercised end-to-end through its real writer**, because that writer produces no goldens to stamp.  It is verified by the gate's own control (P-4 (c)) and by reading the one line it would write, **not by a live regold**.  ⚠ A future wave that repairs `regold` owes the end-to-end leg |
| **D-6** | the brief for this wave | it names **four** writers and calls `s12_census`'s the only board-free one; the tree has **seven** (ten call sites), and `char_enter`'s two were missed because they spell the class differently | ⭐ **RECORDED — and it is the wave's own finding, not a complaint.**  The undercount has the same cause as the defect |

⚠ **THE COUNT IS A FLOOR AND THE METHOD SAYS SO.**  D-1/D-3 were found by doing
the work; **D-6 by a GATE**, on its first run; **D-7 by trying to exercise the
repair end-to-end and failing**; A-1 by reading the ledger's
control sentence against the artifact; D-5 by importing a file.  **No gate
enumerates claims of this kind.**

---

## 7. WHAT THIS WAVE DELIBERATELY DID NOT DO (P-7, P-8, P-9)

* **NOTHING IN `hdl/`.**  `git status --porcelain hdl/` has no tracked entry,
  before or after.
* **NO QUARTUS, NO BOARD, NO FLASH.**  FLASH #24 stands — `flash_log.jsonl` 27
  entries, sha256 `7496b4be2d1771c9…`, byte-identical to the registered value.
* **NO EDIT TO ANY EXISTING PROVENANCE RECORD**, and no re-emission.  A
  re-emission is a new capture and belongs to whatever wave takes it.
* **NO EDIT TO A PRIOR WAVE'S RESULTS DOCUMENT.**  FLASH #24's D-1 was true
  when written; it is discharged here, not rewritten there.
* **NO USER FILE TOUCHED.**  The nine user-modified `sw/` and `rep_cl0` scripts
  and the four `class5_*` docs are untouched; **checked that none of them writes
  a provenance stamp** rather than assumed.
* **NO `git stash`, `git checkout .`, `git reset --hard`**; every `git add` by
  explicit path; **`sw/testdata/receipts/*.jsonl` NEVER STAGED**.
* **NO GATE RETIRED, so nothing to ledger under P-9** — this wave adds a gate
  and removes none.  `check_fuzz_bank` stays RET-2 and was not run.
* **No Codex, no nested subagent.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
