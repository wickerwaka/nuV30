# WAVE 24 — PRE-REGISTRATION. **THE REMAINING SUITE DIVERGENCES.**

Committed **before the first `tests/` edit** and before the first board
*probe*.  Session `https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

**USER INSTRUCTION 2026-09-20**: *"Lets fix the known divergences in the test
suites."*  Scope chosen by the user: **offline doc work** + **socket board
re-capture of the 2 `VOID` goldens**.  `hdl/` IS FROZEN.

> **SIMPLICITY (user directive 2026-08-01, verbatim):** this is 80's era
> hardware — nothing on the die is wasted.  Complex or confusing observed
> behavior is likely simple systems interacting in ways not yet understood.  A
> large fitted table, a many-cased rule, or a per-opcode special case is a
> signal of misunderstanding, not a deliverable.

---

## §0  ⚠ ERRATUM AGAINST THIS WAVE'S OWN BAR Y-1, DECLARED BEFORE IT IS SCORED

Y-1 asks for the pre-registration **before first board contact**.  Before
writing this file I ran, in one command,
`ssh root@mister-nec 'uname -a; uptime'` — a **read-only liveness check**.  It
wrote no CFG, took no capture, selected no core and touched no divider.  It is
board *contact* on the strictest reading, and it is declared here rather than
glossed.  **No board PROBE has been run and none will be until this file is
committed.**

---

## §1  THE DATE CHECK (bar Y-2), REGISTERED AS A PREDICTION

**USER RULING 2026-09-19**: *"treat the documentation as hearsay until proven
otherwise.  Ucore is the only valid implementation."*  WAVE 23 lost its premise
to a 2026-07-27 capture artifact read as current.

**THE SHARPEST FORM OF THE CHECK IS NOT "PRE-ARCHIVE", IT IS "PRE-ENGINE".**
`hdl/rtl/ucore/` first appears at **`0bfea2bfd0`, 2026-08-03**.  The FSM core
was archived `80d9cc8228`, **2026-08-04**, and REMOVED 2026-09-19 (RET-2).

| document | dated | vs the ucore's first commit (2026-08-03) | prediction |
|---|---|---|---|
| `docs/notes/v02_suspected_divergences.md` | 2026-07-18 | **16 days BEFORE the engine existed** | every finding is FSM-era |
| `docs/notes/v03_divergence_ledger.md` | 2026-07-19 … 07-23 | **BEFORE** | FSM-era |
| `tests/v30/v0.3/known_divergences.json` | 2026-07-25 | **BEFORE** | FSM-era (already established, ledger §D) |
| `tests/v30/mod3_illegal/metadata.json` | 2026-07-27 | **BEFORE** | FSM-era (WAVE 23 D-1) |
| `tests/v30/v20suite/` | upstream 2024-05-25 | **a DIFFERENT PART** (µPD70108 V20) | not an engine claim at all |

**P-0**: every one of the four in-repo suite documents predates the existence of
the only implementation this repo now has.  **An FSM-era finding is not evidence
about the ucore and may not be quoted as one.**

---

## §2  PART A — OFFLINE

### A-1 · the seven `v0.2` cases, by name

`INT.90/239`, `INT.9D/44`, `INT.9D/62`, `INT.9D/954`, `INT.FB/142`,
`INT.FB/368`, `INT.FB/730`.

**P-A1 (POINT)**: all seven PASS.  Scored by whole-form inclusion —
`check_core --core ucore --suite-dir tests/v30/v0.2 --opcodes INT.90,INT.9D,INT.FB
--cases 0`, predicted **1000/1000 on each of the three forms**, which contains
the seven by construction.  **If any form is short of 1000 the failing indices
are listed and, if any of the seven is among them, it is a LIVE LEAD and is
reported as one.**

*Basis for the prediction, stated so it is falsifiable*: the document's own
final section (2026-07-18) says the seven are a `final.flags` **capture
convention** artifact, closed by a host-side re-derivation of 269 v0.2 pin-event
goldens — i.e. the SUITE was edited, not the RTL.  The suite on disk therefore
already carries the fix.

### A-2 · `v03_divergence_ledger.md`

**P-A2 (POINT)**: the ledger's own closing claim is *"62 → 0"*.  Re-scored
against the ucore with the exemption list **OFF**, the union of the forms the
ledger's five families name contains **exactly 2 failures, the `F4bc` `VOID`
pair**, and **0** failures in families F1 (25 × `0F31` cycle-only), F2 (24 ×
BCD 4S), F3 (10 pin-event) and F4a (1).  Anything else is a live lead.

### A-3 · the `v20suite` eight — **ONE MECHANISM OR NONE**

WAVE 22 offered *the V20's 4-byte prefetch queue against the V30's 6-byte one*
and labelled it UNPROVEN.  **This wave registers a DIFFERENT, structural
hypothesis and a two-sided control that decides between them.**

> **H-W (the registered hypothesis)** — *the scored window's register sample is
> not frozen at the closing F pop.*  `hdl/tb/tb_v30_core.sv:477` latches
> `fin_regs` at the closing F pop, but `:483-491` then keeps a 16-CPU-cycle
> `fin_wait` window in which, **if a load was pending at the close**, the
> WHOLE register file (except the retired IP) is re-latched later — on the
> comment's own stated assumption that *"the following NOPs keep retiring"*.
> The V20 goldens are external captures that place **non-`0x90` bytes
> immediately after the instruction under test**; this repo's own emitted
> suites cannot, because `emit_suite._operand_abuts_code` (margin 8) rejects
> such placements.  So the extra instruction executes and is captured.
>
> **H-W is a TESTBENCH-WINDOW mechanism, not a part difference.  If it holds,
> WAVE 22's prefetch-depth hypothesis is REFUTED.**

**CONTROL C-INJ (positive, pre-registered before it is run).**  Take the first
**20 PASSING** cases of form `03` (`add r16, word [mem]` — a memory READ, so a
load is pending at the close) whose two bytes immediately after the instruction
are (a) absent from `initial.ram`/`final.ram` and (b) not inside the operand
word.  Write `FF CC` (= **`DEC SP`**) there and re-score `--arch-only`.

* **PREDICT: ≥ 16 of 20 FAIL, each with `sp` exactly `exp - 1`.**
* **PREDICT: the flags delta is `DEC SP`'s** on every failing case.

**CONTROL C-NULL (negative).**  The same 20 cases with `90 90` written at the
same two addresses.  **PREDICT: 20 / 20 PASS.**

**If C-INJ fires below 16/20, H-W is REFUTED and reported as refuted.**  If both
controls behave as registered, the eight are **instrument-failure, one
mechanism, and the disposition is PROPOSED AND NOT TAKEN** (the brief forbids
taking it): `3,124,992 / 3,125,000 ARCH` stays the quotable figure this wave.

---

## §3  PART B — BOARD, SOCKET ONLY

### B-1 · re-capture the two `VOID` goldens

**THE COLLISION IS SHOWN BEFORE ANYTHING IS REGENERATED** — arithmetic from the
banked case alone, no engine:

| case | instruction at | preload span (2 × `63 C0`, PC−4) | operand EA | phys | overlap |
|---|---|---|---|---|---|
| `0F1B`/3917 `clr1 word [bx+di],05h` | `999D:4263` → `9DC33` | **`DC2F`–`DC32`** | `DS*16+BX+DI` = `9DC30` | **`DC30`** | **YES** — want `89`, image holds `C0` |
| `83.5`/8683 `sub word [bx],01h` | `DE8E:AEBB` → `E979B` | **`9797`–`979A`** | `DS*16+BX` = `E9799` | **`9799`** | **YES** — want `A7`, image holds `63` |

**P-B1a**: those two `(phys, want, got)` triples reproduce the
`v03_divergence_ledger.md` F4bc text *exactly* (`dc30 / 89 / C0`,
`9799 / A7 / 63`) and the measured divergence rows (`exp 0x63C0` on both).
**If either does not overlap, B-1 STOPS and is reported as a finding.**

**P-B1b**: re-emitted with `emit_suite reemit --validate` at the same output
index, both new cases satisfy `_operand_survives -> None` (the F4bc guard now
runs at compose time) and **PASS `check_core`**.

⚠ **DECLARED IN ADVANCE — THE REPLACEMENT IS NOT THE SAME STIMULUS.**  The
generator has drifted since the 2026-07 emission: `0F1B`'s banked index 3917
came from seed-attempt **3919** (`0F1B.seeds.json`: 7,321 of 10,000 indices have
`idx != seed`), and re-composing either case's recorded seed today yields a
different instruction encoding and a different `CS:IP`.  **A re-captured golden
at index N is a NEW case at that index, not a corrected copy of the old one**,
and `XX.seeds.json` cannot express a within-index reroll (`.../{idx}/{r}`) in
its `[idx, seed]` map.  Both facts go in the ledger entry.

**P-B1c (the ladder figure, registered BEFORE the run)**: `v0.3` list-applied is
**3,699,998 / 3,699,998 `[2 documented pre-existing excluded]`** today.  With
both exemptions retired and both replacements passing it becomes
**3,700,000 / 3,700,000 full, no exclusion note** — the denominator gains 2 and
the numerator gains 2.  **If either replacement fails, the exemption for that
case is NOT retired and the figure is reported as measured, not as registered.**

**P-B1d**: the originals are archived **byte-identical** before any file is
rewritten (`sw/testdata/wave24/void-archive/`), with sha256 of the whole
pre-edit `*.json.gz` recorded on both sides.  Nothing is destroyed.

### B-2 · the ModR/M retained-EA-lane divergence — **a coordinator extension, declared as one**

WAVE 23 §4 found it and could not close it: the board was forbidden and the two
silicon rows' **byte encodings were inferred from a prose field**
(`metadata.json::stale_ea_probe`'s `pre` is English).  ⚠ And the committed
`sw/char_mod3.py`'s own probe list does **not** contain those two rows — the
freeze's `rig` field says *"char_mod3.py **+ inline freeze**"* — so the bytes
are **not recoverable from any artifact** and must be CONSTRUCTED.

**THE STIMULUS, CONSTRUCTED AND STATED AS BYTES.**  Register setup = WAVE 23's
(`char_mod3.SETUPS[0]` values) with the body at **`PS=0x0000`, `PC=0x8100`** so
the live composer accepts it and the column is directly comparable with WAVE
23's measured ucore column.  Probe instruction is always
**`8D F7` = `LEA SI, DI` at `mod == 3`**.

| # | predecessor | **bytes, constructed** | EA |
|---|---|---|---|
| C1 | `MOV [1234h],AW` | `A3 34 12` | `1234` |
| C2 | `MOV [BEEFh],AW` | `A3 EF BE` | `BEEF` |
| C3 | `NOP` | `90` | — |
| R1 | `MOV [3010h],AH` | `88 26 10 30` | `3010` |
| R2 | `MOV CW,[4455h]` | `8B 0E 55 44` | `4455` |
| M0 | `MOV [BW+IX],AW` | `89 00` | `BW+IX` = `BBBB` |
| M1 | `MOV [BW+IY],AW` | `89 01` | `CCCC` |
| M2 | `MOV [BP+IX],AW` | `89 02` | `DDDD` |
| M3 | `MOV [BP+IY],AW` | `89 03` | `EEEE` |
| M4 | `MOV [IX],AW` | `89 04` | `7777` |
| M5 | `MOV [IY],AW` | `89 05` | `8888` |
| M6 | `MOV [1234h],AW` | `89 06 34 12` | `1234` |
| M7 | `MOV [BW],AW` | `89 07` | `4444` |

**P-B2a (the CONTROLS decide whether the rig is speaking).**  C1 and C2 must
reproduce silicon's recorded `si_loaded` **`0x1234` and `0xBEEF` exactly**.
**If they do not, the stimulus is not the 2026-07-27 rig's and NOTHING ELSE IN
B-2 IS QUOTED.**

**P-B2b (the law under test, one sentence).**  *On a ModR/M predecessor the
retained EA lane holds the **completed** effective address.*  Registered point
predictions for silicon, `AW = 0x1111`:

`M0 CCCC · M1 DDDD · M2 EEEE · M3 FFFF · M4 8888 · M5 9999 · M6 2345 · M7 5555`

against WAVE 23's measured **ucore** column
`M0 8888 · M1 9999 · M2 8888 · M3 9999 · M4 9211 · M5 9211 · M6 9211 · M7 9211`.

**FALSIFIER (WAVE 23's, discharged either way)**: if silicon does **not** give
`EA + scratch` on these eight, the retained-EA-lane law is refuted and WAVE 23
§4's two-point reading is withdrawn.

⚠ **`hdl/` IS NOT EDITED WHATEVER THE ANSWER.**  A confirmed divergence is
BOOKED with its falsifier for a later RTL wave.

### B-3 · `mod3_illegal` — **COSTED, NOT TAKEN**

A route only.  **No re-capture of `mod3_illegal` in this wave.**  Injecting
`ea_residue` remains WAVE 23's **STOP S-4** and stays forbidden.

---

## §4  STOPS — any one of these ENDS the board session and is reported

* **S-1** `div_readback` reports **UNPINNED** on any probe → rig-integrity
  finding, hard stop, no work-around.
* **S-2** any capture runs with `use_core` not explicitly `False`.
* **S-3** any flash, of anything.  **THE BOARD CARRIES FLASH #23 AND MUST STILL
  CARRY IT AT THE END.**
* **S-4** (inherited from WAVE 23) injecting `ea_residue` through the backdoor.
* **S-5** a `tests/` golden overwritten before its byte-identical archive exists.
* **S-6** any edit under `hdl/`.

---

## §5  BARS Y-1 … Y-9 (the brief's, restated so they can be scored)

| bar | what it asks |
|---|---|
| **Y-1** | this file committed before first board PROBE and first `tests/` edit (see §0's erratum) |
| **Y-2** | every suite doc's FSM-era status checked **by date** and reported; A-1/A-2 each with the measurement that settles it |
| **Y-3** | A-3 proved / refuted / undecidable, **one mechanism or none** |
| **Y-4** | B-1 complete: collision shown, regenerated, re-captured, exemption retired, original archived, ledger entry |
| **Y-5** | B-2 captured with CONSTRUCTED encodings, mechanism reported, `hdl/` untouched, falsifier registered |
| **Y-6** | the ladder is ZERO-DELTA **except `v0.3`, which moves by P-B1c and only by it** |
| **Y-7** | nothing in `hdl/` edited |
| **Y-8** | the user's 21 modified + 16 untracked files untouched; `git add` by explicit path; no `sw/testdata/receipts/*.jsonl` |
| **Y-9** | doc discrepancies as a **FLOOR**, each with a disposition |

---

## §6  WHAT THIS WAVE WILL NOT DO

* No `hdl/` edit, no Quartus, no flash, no Codex, no nested subagent.
* No `mod3_illegal` re-capture, no `ea_residue` injection.
* No disposition TAKEN on the `v20suite` eight — only proposed.
* No deletion of any document: FSM-era findings are **marked**, never removed.
