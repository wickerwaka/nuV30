# WAVE 21 — REMOVE THE ARCHIVED FSM CORE — **PRE-REGISTRATION**

**Committed BEFORE the first edit to `hdl/` or `sw/`.**  Written against
`fb9365c01c` (`master`), the tip of WAVE 20.

**USER INSTRUCTION, verbatim (2026-09-19):**

> *"Remove the FSM core, fix whatever dependencies exist"*

**This OVERRIDES WAVE 20's audit recommendation** (`staleness_audit_2026-09-19.md`
§2: *"KEEP THE RTL, RETIRE FOUR OF ITS TEN GATES"*).  The removal is authorised.
**The dependency repair is the substance of the wave** — the audit's §2 named one
blocker (`gen_ucore_qsf.py --check`, which is `quartus_gate.py`'s bar **E1**) and
this document disposes of it before anything is deleted.

---

## §0 THE STANDING DESIGN PRINCIPLE, verbatim (user directive 2026-08-01)

SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.  Complex
or confusing observed behavior is likely simple systems interacting in ways not
yet understood.  A large fitted table, a many-cased rule, or a per-opcode
special case is a signal of misunderstanding, not a deliverable.

---

## §1 WHAT GOES, BY PATH — measured, `git ls-files`

| path | bytes |
|---|---|
| `hdl/rtl/core/v30_eu.sv` | 292,906 |
| `hdl/rtl/core/v30_biu.sv` | 111,724 |
| `hdl/rtl/core/v30_ss_pkg.sv` | 25,826 |
| `hdl/rtl/core/v30_core.sv` | 16,799 |
| `hdl/rtl/core/race_law.svh` | 14,809 (**GENERATED** by `sw/gen_race_law.py`) |
| `hdl/rtl/core/int9d_race.hex` | 5,120 (**A MEASURED CONTRACT — NOT a generated file**) |
| **total** | **467,184 bytes, 6 files** |

Plus the FSM Quartus file list `hdl/files.qip` (1,058 bytes) and the FSM-only
Verilator harness `sw/race_law_equiv_tb.sv`.

⚠ **`int9d_race.hex` IS SILICON, NOT RTL.**  `sw/exp_race.py:8` calls it *"the
measured contract"* for the POP-PSW/INT race.  It is therefore **ARCHIVED BY
RENAME into `docs/facts/`**, not removed — the RET-1 precedent (`sim/README.md`
→ `docs/notes/…`).  `race_law.svh` is generated FROM it and is not archived.

---

## §1a ⚠⚠ USER RULING 2026-09-19 — THE SCOPE IS WIDER THAN "REMOVE A CORE"

**VERBATIM, relayed by the coordinator after this document's first draft and
BEFORE any edit to `hdl/` or `sw/`:**

> *"These are the kinds of discrepancies I am asking you to audit and resolve.
> There have been a lot of iterations in this project and you need to treat the
> documentation as hearsay until proven otherwise.  Ucore is the only valid
> implementation in this code base, if it has dependencies on any other
> implementations those need to be removed.  Documentation that gives those
> other implementations precedence is suspect."*

Three binding consequences:

1. **`nec_test_ucore.qsf` BECOMES PRIMARY** and is AUTHORED, not generated.
   `gen_ucore_qsf.py` is RETIRED; E1 is REPLACED (§2).  The ruling authorises
   the re-basing, so **Z-2 no longer has a STOP branch.**
2. **EVERY DOC CLAIM IS HEARSAY UNTIL PROVED IN THE ARTIFACT** — this brief,
   `CLAUDE.md`, `standing_gates.md`, `fsm_core_archive_2026-08-04.md` and WAVE
   20's audit included.  **Where a doc and the code disagree, the code wins and
   the doc is FIXED IN THIS WAVE.**  The COUNT of discrepancies found and
   resolved is a first-class deliverable (§9).
3. **SCOPE: remove the ucore's dependencies on EVERY other implementation and
   demote the documentation that gives them precedence** — `files.qip` as the
   DEFAULT list with ucore as the variant, `nec_test`/`.qpf` as the primary
   revision, `check_seq.CORE = "fsm"`, every `--core fsm` leg, the `CORE_RTL`
   dict's shape, every `--core` choice list that still offers `sim` or `fsm`,
   and any live coupling to the RET-1 model.

### ⚠ CORRECTION TO THIS WAVE'S OWN BRIEF, measured

The brief (and WAVE 20 §2) says `gen_ucore_qsf.py --check` *"derives the ucore
revision FROM the FSM revision"* and calls it **the blocker**.  **MEASURED: that
overstates it.**  `derive()` is PURE TEXT SUBSTITUTION on `hdl/nec_test.qsf`; it
never opens `hdl/files.qip` and never reads `hdl/rtl/core/`.  **Deleting the FSM
RTL does not break E1 at all.**  The dependency is on ONE SETTINGS FILE, not on
the core.  **So the re-basing in §2 is a DELIBERATE ACT UNDER THE RULING, not a
repair forced by the deletion** — and that distinction is why Z-4 must score the
two changes SEPARATELY (§6).

---

## §2 ⚠⚠ E1 — RETIRED AND REPLACED.  THE DECISION, BEFORE THE EDIT

### What E1 asserted, and why the ruling voids it

`sw/gen_ucore_qsf.py --check` is bar **E1** of `sw/quartus_gate.py`, on the path
of **every RTL landing and every flash in this project**.  Its bar text, verbatim
from FLASH #23's own receipt (`sw/testdata/flash23/g6-control-draw-seed1/
seed1_quartus_gate.json`, key `E1_gen_ucore_qsf/bar`):

> *"hdl/nec_test_ucore.qsf is a faithful derivative of hdl/nec_test.qsf"*

That sentence makes **the FSM revision the ORIGINAL and the ucore revision the
DERIVATIVE.**  Under the ruling that precedence is inverted, so the bar's claim
is **VOID, not merely unmeasurable.**  It is not repaired and it is not kept.

### THE DECISION — one project, one revision, authored

1. `hdl/files.qip` (the FSM file list) — **DELETED**.
2. `hdl/nec_test.qsf` (the FSM revision) — **DELETED**.
3. `hdl/nec_test_ucore.qsf` — **PROMOTED TO PRIMARY AND AUTHORED.**  Its
   `GENERATED FILE -- do not edit` header is replaced by a header that says it is
   the project's one revision, hand-maintained.  **Every assignment the compiler
   reads is otherwise BYTE-IDENTICAL** — settings, macros, `source sys/sys.tcl`,
   `source files_ucore.qip`, `PROJECT_OUTPUT_DIRECTORY output_files_ucore`, the
   `PARTITION_HIERARCHY` line.
4. `hdl/nec_test.qpf` — loses `PROJECT_REVISION = "nec_test"`.  **One revision.**
5. `sw/gen_ucore_qsf.py` — **RETIRED** (`RET-2`).  It keeps its file so that
   running it prints the retirement and exits 2 rather than vanishing.
6. `sw/qsf_lint.py` — **NEW**, and it is E1's replacement (§2b).
7. `sw/quartus_gate.py` — E1's *call* becomes `qsf_lint --check`; the receipt key
   becomes **`E1_qsf_canonical`**; the post-build "regenerate" becomes a
   **RESTORE OF THE BYTES `quartus_gate` ITSELF STASHED before the build**, which
   needs no second file and no `git`.

### ⚠ WHAT IS DELIBERATELY **NOT** RENAMED, AND WHY — measured

The revision stays **`nec_test_ucore`** and the output directory stays
**`output_files_ucore`**.  Three measured reasons, and the third is decisive:

* every receipt, every `flash_log.jsonl` entry and **FLASH #23 itself** records
  this revision name; `quartus_gate.REVISION` (`:126`) keys every report path
  off it;
* `ucore` is the NAME OF THE IMPLEMENTATION, not a variant marker — with one
  implementation the suffix reads as identity, and nothing in the tree now
  offers a second revision to be a variant OF;
* ⚠ **A REVISION RENAME PLAUSIBLY BREAKS Z-4.**  Quartus programming files
  carry the design/revision identity, so renaming the revision could move the
  `.rbf` for a purely cosmetic reason — and Z-4 says a moved `.rbf` STOPS THE
  WAVE.  **Renaming would spend the wave's one falsifier on a cosmetic change.**
  BOOKED as a naming item with this reasoning, not taken.

## §2b `sw/qsf_lint.py` — THE REPLACEMENT, AND ITS LIMITS

**WHAT IT PROVES.**  *`hdl/nec_test_ucore.qsf` — the ONE revision the compiler
reads — is in CANONICAL FORM: it carries none of the assignments Quartus
materialises into it from `source sys/sys.tcl`, and it declares exactly one file
list and exactly one output directory.*

Checkable, and MEASURED on this tree before the edit:

| property | canonical (measured today) | after a Quartus build (`sys.tcl`'s own counts) |
|---|---|---|
| `set_location_assignment` | **0** | + **107** |
| `set_instance_assignment` | **1** (`PARTITION_HIERARCHY`) | + **50** |
| `PRE_FLOW_SCRIPT_FILE` | **absent** | present (`sys/gen_cdf.tcl`) |
| `source files_ucore.qip` | exactly **1** | 1 |
| `PROJECT_OUTPUT_DIRECTORY` | exactly **1** | 1 |
| `source sys/sys.tcl` | present | present |

So a green `qsf_lint --check` says: **no previous build's in-place rewrite has
been left in the tree, and no assignment reaches the compiler that is not in the
committed revision file.**  That is the half of E1 that had a referent, and it is
the half `quartus_gate.py`'s `INPUT_FLIP_EXEMPT` and its post-build regeneration
were built on.

**WHAT IT DOES NOT PROVE — stated because a bar with no limits is a bar nobody
checked:**

* **NOT** *"two bitstreams differ by the core and nothing else"*.  **THAT
  GUARANTEE IS RETIRED AND NOTHING REPLACES IT** — there is no second core and no
  second revision for it to be about.  Every A/B claim resting on it
  (`receipt_diff.py`'s *"FSM vs ucore bitstream"* row,
  `fsm_core_archive_2026-08-04.md` §6's synthesis paragraph) becomes HISTORY on
  this commit and must be read against `fb9365c01c` or earlier.
* **NOT** faithfulness to a second file.  There is no template; the revision file
  **is** the source of truth.  **Nothing now cross-checks the settings against a
  second copy — that cross-check is RETIRED, and the replacement for it is that
  there is only one copy to get wrong.**
* **NOT** anything about the CONTENTS of `files_ucore.qip`.  The list is
  *sourced*, not derived; its gates are that the build elaborates at all, plus
  `check_ucore_tables` (G0) and `ucrom_mif_check` on the tables it names.
* **NOT** that the settings are CORRECT.  A wrong `set_global_assignment` is a
  green `qsf_lint`.
* **NOT** anything about what Quartus DOES with the settings — E2-E11 and the
  `truefmax` classes are that.

**NON-VACUITY IS DEMONSTRATED, NOT ASSERTED**: the results document carries
positive controls (a spliced `set_location_assignment` → exit 1 naming it; a
deleted `source files_ucore.qip` → exit 1; an unreadable file → exit 2 CANNOT
MEASURE, never PASS).

---

## §3 `core_portlist_lint` — WHAT IT BECOMES

WAVE 18's gate compares the TWO cores' port lists.  With one core it has no
second operand.  **It is RE-POINTED, not retired**, because the defect it was
built for is still live and Quartus still accepts-and-ignores it:

> *the ucore's `v30_core` port list vs the NAMED PORT CONNECTIONS at every
> instantiation of `v30_core` in the tree* — `hdl/tb/tb_v30_core.sv` and
> `hdl/rtl/system_large.sv`, the two files WAVE 18 found were shared.

That is the same class WAVE 18 found (`%Error-PINNOTFOUND` / Quartus *"Named
port was not declared by the instantiated entity"*, 0 errors, buried in a report
folder no gate reads) with the operand that still exists.  It keeps its exit
convention: **0** agree, **1** a connection names a port the module does not
declare (or an instantiation is missing under a configuration), **2** CANNOT
MEASURE.  **Non-vacuity is demonstrated by positive controls in the results
document, not asserted.**

⚠ **WHAT IT NO LONGER PROVES**: that two independently-written cores agree.
Nothing replaces that; there is one core.

---

## §4 THE MECHANISM FOR EVERY OTHER CONSUMER — ONE DECLARATION, AS RET-1 DID

RET-1's rule, applied verbatim: **NO GATE DIES SILENTLY AND NONE DIES WITH A
`FileNotFoundError`.**

**`sw/fsmcore.py` is NEW and it is the retirement declaration** — the analogue
of `sw/simbin.py` after RET-1.  It exports `FsmCoreRetired` and `retired(who)`,
which raises one banner naming the user directive, `invalidation_ledger.md`
**RET-2**, and the recovery command.  Every tool that bound the archived core
calls it, so a reader gets a sentence instead of a missing file.

Dispositions, by group:

| group | tools | disposition |
|---|---|---|
| **FSM-structural** (read/mutate `hdl/rtl/core/*.sv`) | `check_race_law`, `gen_race_law`, `prefix_clear_lint`, `ea_step_lint`, `biu_law_mutation`, `biu_law_lc3_gadget`, `biu_law_lc6_gadget`, `biu_law_lc3_seedsearch`, `biu_law_gatesearch`, `exp_race` | `fsmcore.retired()` — exit 2, named |
| **FSM TB binary** (`check_seq.CORE = "fsm"` / `check_seq.BIN`) | `check_ff_t4`, `check_mod3_illegal`, `check_enter_nesting`, `check_fuzz_bank`, `causal_wrand.run_tb_internal` (+ its ~20 `class5_*` readers), `sweep_popa`, `sweep_dispphase`, `exact_predict`, `dumpeu`, `f7a_arbitrate`, `pi1a_trace`, `repro_segleak` | the PIN refuses: `check_seq.CORE = None` and `tb_bin(None)` raises; `check_seq.BIN` raises through a module `__getattr__` |
| **explicit `--core fsm` legs** | `check_core`, `check_ab_sim`, `ss_lint`, `ss_flopcensus`, `r7_lint` | the choice is REFUSED, exit 2, naming RET-2 |
| **the aggregate sweep** | `sw/t30_sweep.sh` | refuses, exit 2 (not deleted — a refusal is readable, a missing script is not) |
| **re-pointed** | `check_core.BIN` / `OBJ` / `RTL` | see §5 |
| **RETIRED, replaced** | `sw/gen_ucore_qsf.py` | `sw/qsf_lint.py` (§2b) |
| **`--core` choice lists** | every `sw/*.py` whose `--core` still offers `fsm` or the RET-1 `sim` | the choice list collapses to `ucore`; a `sim`/`fsm` default becomes `ucore`.  ⚠ **A DEFAULT CHANGE IS A CHANGE OF MEASUREMENT** and every one is listed in the results |

⚠ **THE FIVE `FileNotFoundError` FILES OF RET-1 ARE NOT TOUCHED.**
`sw/t7_sim_ab.py`, `sw/t7_sim_proof.py`, `sw/testdata/rep_cl0/{modeldrive,
rep_cl0_repro,repdrive}.py` are the USER'S OWN UNCOMMITTED WORK.  This wave
leaves them exactly as it found them.

---

## §5 A FINDING THIS WAVE ALREADY HAS, REGISTERED BEFORE IT IS FIXED

`sw/check_core.py:180` declares:

> *"Legacy module-level constants, both pinned to the FSM layout and both with
> NO consumers anywhere in the tree (checked 2026-08-04): `BIN` above and `RTL`
> here."*

**THAT IS FALSE TODAY, AND IT HAS FIVE CONSUMERS OF `BIN` AND TWO OF `OBJ`,
MEASURED:** `sw/emit_suite.py:2258`, `sw/f4a_boundary_battery.py:73`,
`sw/char_divergence.py:26`, `sw/validate_strio_sim.py:158`,
`sw/class5_hext.py:58`; `sw/pi1a_trace.py:29` and `sw/repro_segleak.py:33` take
`CC.OBJ`.  **`emit_suite.py` calls `CC.build()` — which builds the DEFAULT
`ucore` into `obj_dir_ucore` — and then executes `CC.BIN`, which is the
ARCHIVED core's binary in the unsuffixed `obj_dir`.**  The trap the comment
warned about was already sprung.

**DISPOSITION: `check_core.BIN` / `OBJ` / `RTL` are RE-POINTED to the `ucore`.**
Five tools that were silently running the archived core now run the standing
one.  **That is a CHANGE OF ENGINE and it is declared here**: no registered
figure is inherited across it, and none of the seven tools carries a figure on
any standing ladder (checked against `standing_gates.md` §A/§B — the
`f4a_boundary` 160/160 and `f0lock_tranche` 400/400 rows are taken through
`check_core --suite-dir`, not through `f4a_boundary_battery.py`).

---

## §6 THE BARS — as the brief registers them

| bar | statement |
|---|---|
| **Z-1** | the dependency enumeration is COMPLETE and MEASURED over `sw/`, `hdl/`, `tests/`, Makefiles, `.qip`/`.qsf`/`.qpf`/`.tcl`/`.sh`, with its METHOD and its LIMITS stated |
| **Z-2** | E1's disposition is decided, registered and justified — §2 above |
| **Z-3** | **NO GATE DIES SILENTLY.** every retired gate gets a `RET-2` row carrying its LAST REGISTERED FIGURE and what replaces it (*nothing* is acceptable if written); every affected tool is RUN afterwards and its behaviour recorded; **zero tools left raising an import or file error** |
| **Z-4** | **THE BITSTREAM FALSIFIER.** one CONTROL `quartus_gate.py` build after the removal must **PASS**, and its `.rbf` must be **BYTE-IDENTICAL** to FLASH #23's CONTROL draw.  **A differing `.rbf` STOPS THE WAVE** and is reported as a finding — it would mean the FSM core was reaching the ucore revision |
| **Z-5** | the live ladder is UNMOVED except where a leg is formally retired; BEFORE side taken FIRST |
| **Z-6** | **NOTHING in `hdl/rtl/ucore/` or `hdl/nec_test.sdc` is edited.**  If the removal appears to require either, STOP AND REPORT |
| **Z-7** | 21 of the user's files are uncommitted work.  **NEVER `git stash` / `git checkout .` / `git reset --hard`.  `git add` BY EXPLICIT PATH**, and never `sw/testdata/receipts/*.jsonl` |
| **Z-8** | `git rm` retains history.  The ledger says so, with the commit to recover from |

### Z-4's PREDICTION, registered before the build — **AND IT IS TWO BUILDS**

WAVE 20 established by hash that `files_ucore.qip` lists five `rtl/ucore/` files
and **zero** under `rtl/core/`.  Confirmed independently this session by reading
`quartus_gate.input_files()` (`:154-172`): the manifest is `nec_test.qsf`,
`nec_test_ucore.qsf`, `files_ucore.qip`, `nec_test.sdc`, `nec_test.sv`, the
entries `files_ucore.qip` names, all of `hdl/rtl/ucore/`, and `hdl/sys/` —
**99 files on FLASH #23's own receipt, and NOT ONE of them is `hdl/files.qip` or
under `hdl/rtl/core/`.**

**THE TARGET, from FLASH #23's CONTROL receipt**
(`sw/testdata/flash23/g6-control-draw-seed1/seed1_quartus_gate.json`):

| | |
|---|---|
| `.rbf` sha256 | **`e91a67badeef2c17262b5239e0700672f3be69eeb44e749e5c9d53ae1302a613`** |
| `.sof` sha256 | `d6d3a6d3c2c85159dd3ada90e9d906a50b54ad26d33ca5c80c4a979d7481c5a9` |
| `input_manifest` sha256 / files | `ee6a4eff46e483d3…` / **99** |
| configuration | CONTROL/DEFAULT (no `X1_AD_RETENTION`), DERIVED |
| Fmax / worst setup | 34.68 MHz / +2.419 ns |

**BECAUSE THE RULING MAKES THE RE-BASING A SEPARATE ACT FROM THE DELETION, Z-4
IS SCORED AS TWO BUILDS**, so that a moved `.rbf` names its own cause:

| | tree state | prediction |
|---|---|---|
| **Z-4a** | FSM RTL + `files.qip` REMOVED; `hdl/nec_test.qsf`, `hdl/nec_test_ucore.qsf`, `.qpf` **UNTOUCHED** | `.rbf` **BYTE-IDENTICAL** to `e91a67ba…`.  A difference means the FSM core WAS reaching the ucore revision — **STOP, and report** |
| **Z-4b** | the `.qsf` re-basing applied on top (`nec_test.qsf` + `.qpf` revision deleted, revision file authored) | `.rbf` **BYTE-IDENTICAL** to `e91a67ba…`.  A difference means the re-basing changed what the compiler reads — **STOP, and report**; the `.qsf` diff is then the whole suspect list |

⚠ **THE MANIFEST WILL MOVE AND THAT IS NOT Z-4.**  `hdl/nec_test.qsf` is one of
the 99 files; deleting it takes the manifest to 98 and moves its sha256.
`hdl/nec_test_ucore.qsf` changes content (its header).  **Manifest movement and
`.rbf` movement are different claims and only the second is Z-4.**

### What is expected to MOVE, registered so a mover is not read as a surprise

* the `input_manifest()` sha256 and its file count (**99 → 98**);
* `fz2_replay`'s ERA GUARD, already RED on this tree for 4 moved files
  (`staleness_audit_2026-09-19.md` §7), gains more.  **It is the guard working.**
* `sw/test_quartus_gate.py`'s total: the E1 bar is being replaced, so any test
  asserting its text or receipt key MUST move.  **Registered: the total may move
  from 287; it must not FALL by an un-named test, and every moved test is listed
  in the results with what it now asserts.**
* `sw/quartus_gate.py`'s own `tool_sha256` (it is receipted).

### ⚠ `check_fuzz_bank` IS A CASUALTY AND IT IS REGISTERED AS ONE

`sw/check_fuzz_bank.py:76` replays every banked seed through
`check_seq.run_tb(...)` **with no `core=`**, i.e. through
`check_seq.CORE = "fsm"` — **the archived core's binary**, resolved eagerly at
`:112`.  Its registered figure **`PASS | 621 | stable 621 | improved 0 | worse 0
| gen_drift 0 | regen_err 0 | float-floor 0 | new-sig TIMING 0`** is therefore an
**FSM** figure, and it cannot survive the removal.

**IT IS NOT RE-POINTED TO THE ucore.**  The banked `replay_verdict` column was
computed by this same function on the FSM TB (`fuzz_bank.py:261`), so a ucore
replay would compare a ucore verdict against an FSM-derived column — a
guaranteed FAIL that says nothing, and per RET-1 falsifier #3 a re-pointed leg
may not inherit the retired leg's figure.  **It is RETIRED in `RET-2` with its
last figure, replaced by NOTHING**, and re-pointing it is BOOKED as a
`fuzz_bank` column re-derivation (the `ERR-1` / `cfb_rederive` pattern), not
taken here.

---

## §7 DISCIPLINE, as registered

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.**  The board carries FLASH #23; it is
  left alone.  **This removal incurs NO NEW FABRIC DEBT — CONDITIONAL ON Z-4.**
  If the `.rbf` is byte-identical the flashed bitstream is unaffected by
  construction; if it is not, the wave stops and the debt question is moot
  because nothing lands.
* No Codex.  No nested subagents.
* Single-writer guard before any Quartus stage: `pgrep -x <binary>`, one pattern
  per call.  **BLOCK, DO NOT POLL.**
* `git checkout -- hdl/nec_test_ucore.qsf` by that exact path between Quartus
  runs.  ⚠ The FSM revision's `.qsf` and `.qpf` are being DELETED, so no
  Quartus stage is ever run on the `nec_test` revision in this wave — the
  deletion happens BEFORE the Z-4 build, not after.
* `cmd | tail -1; rc=$?` captures `tail`'s status.  Every leg in this wave's
  scripts captures to a variable first.
* /tmp discipline: `~/.cache/ucsimt-tmp/wave21`, never `/tmp`.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**
* Truthful commit messages.  A number with no artifact id is not quotable.
* **Record what was measured, not what was expected.**

---

## §8 WHAT THIS WAVE WILL NOT DO

* not touch `hdl/rtl/ucore/` or `hdl/nec_test.sdc` (**Z-6**);
* not touch the user's 21 uncommitted files;
* not delete a branch, a worktree, an `obj_dir`, a Quartus log, or one byte of
  `sw/testdata/` or `tests/`;
* not push;
* not re-anchor the v1-anchor casualty family — that is WAVE 20 §4's open item
  and a board decision;
* not re-derive `fuzz_bank`'s `replay_verdict` column (§6);
* not run the board.

---

## §9 THE DOC-DISCREPANCY DELIVERABLE (ruling consequence 2)

Every claim this wave relied on was checked against the artifact.  The results
document carries the full table with, for each row: **the file and line, what it
asserts, what the artifact says, and the disposition (FIXED here / BOOKED with
evidence).**  Four are already measured and are registered here so they cannot be
quietly dropped:

| # | where | the claim | the artifact |
|---|---|---|---|
| **D-1** | `hdl/files_ucore.qip:10-11` | the file list is *"Selected by the `V30_CORE` environment variable, read in nec_test.qsf"*, i.e. `V30_CORE=ucore quartus_sh --flow compile nec_test` | **`V30_CORE` occurs EXACTLY ONCE in the whole tree — in that comment.**  Nothing reads it.  Following the instruction builds the **FSM** core and reports success: **accepted-and-ignored, class E-6, sitting in a build instruction.**  `gen_ucore_qsf.py`'s own docstring contradicts it (the settings parser has no `if`; Error 125048) |
| **D-2** | `sw/check_core.py:180` | `BIN` and `RTL` have *"NO consumers anywhere in the tree (checked 2026-08-04)"* | **FIVE consumers of `BIN`, TWO of `OBJ`** — §5 |
| **D-3** | `sw/ss_lint.py:28` | *"`--core fsm` (default) is the standing gate"* | the default is **`ucore`** (`:175`), and has been since 2026-08-04 |
| **D-4** | the brief / `staleness_audit_2026-09-19.md` §2 | `gen_ucore_qsf --check` *"derives the ucore revision from the FSM revision"* and is **the blocker** to removal | it is text substitution on ONE settings file; it never opens `files.qip` or `hdl/rtl/core/` — §1a |

⚠ **`CLAUDE.md`'s WAVE 20 items W-1, W-2, W-3** (`timed_scenario` /
`timed_ins_replay` wrongly listed as anchor casualties; the stale `ss_lint` row
at 0x8D/226/214; the WAVE 7 banner's *"228 flops"*) are **doc claims that are
false about this tree**, already measured by WAVE 20 and left unfixed by it.
Under the ruling they are **IN SCOPE and FIXED IN THIS WAVE.**
