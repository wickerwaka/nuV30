# WAVE 26 — PRE-REGISTRATION.  **THE RETAINED EA LANE IS WRITTEN ON EVERY EA CALCULATION, WITH THE ADDRESS ADDER'S SECOND ADDEND.**

Committed **BEFORE the first `hdl/` edit of this wave** and **BEFORE the first
board contact**.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

**USER INSTRUCTION 2026-09-20: *"Do both fixes, tb first"***.  The testbench
fix is WAVE 25, landed `56bdf8d851`.  **THIS IS THE SECOND FIX, AND IT MOVES
THE BITSTREAM.**

---

## §0  THE STATE OF THE TREE AT THIS COMMIT

* `git diff -- hdl/` is **EMPTY**.  No `hdl/` byte has moved in this wave.
* **Read-only diagnostics HAVE been run** and are declared here rather than
  discovered later.  They are whole-program replays through the existing
  `sw/lea_mod3_gate.Runner` with **perturbed register setups** — no RTL edit,
  no backdoor injection, no board.  What they established is §2.  *Nothing
  below was chosen after seeing a silicon row: the law is WAVE 24's, measured
  on the socket on 2026-09-20 and committed at `2c052ad6bb`.*
* Baseline re-measured on this tree **before** anything: `sw/b2_ea_lane_ucore.py`
  = **MATCH 7 / 13, DIVERGE 6 / 13**, binary receipt `f028eba6c8011658…`.

---

## §1  THE RULE, IN ONE SENTENCE

> **The retained EA lane is written on EVERY EA calculation, and what it takes
> is the address adder's SECOND ADDEND — the index register for a
> two-register form, the displacement for a displacement form, and ZERO when
> there is nothing to add.**

That is the law WAVE 24 measured from silicon
(`suite_divergence_results_2026-09-20.md` §6.2), on thirteen directed socket
probes whose controls reproduce the frozen 2026-07-27 rows exactly.

**NO OPCODE TABLE.  NO PER-FORM CASE.  NO `mod`-SPECIFIC BRANCH.**  If the
edit needs more than that one rule, the mechanism is misunderstood and this
wave **STOPS AND REPORTS** rather than fitting (STOP **S-1**).

---

## §2  WHAT THE READ-ONLY DIAGNOSTIC ALREADY ESTABLISHED (declared, not claimed as a result)

Perturbing one register at a time and one body address, over
`<predecessor> 8D F7`:

| probe | base | `AW+1` | `BW+1` | `IX+1` | `IY+1` | `BP+1` | body `PC+0x10` |
|---|---|---|---|---|---|---|---|
| `C3` `90` | `2222` | **+2** | 0 | 0 | 0 | 0 | 0 |
| `M0` `89 00` | `8888` | **+1** | 0 | **+1** | 0 | 0 | 0 |
| `M4` `89 04` | `9211` | **+1** | 0 | 0 | 0 | 0 | **+16** |
| `M6` `89 06 34 12` | `9211` | **+1** | 0 | 0 | 0 | 0 | **+16** |
| `M7` `89 07` | `9211` | **+1** | 0 | 0 | 0 | 0 | **+16** |

Read with `v30u_eu_arm_bind.svh:81-84` (`tmpa_n = ea_residue_n;
if (ea_pair_valid_n) tmpb_n = ea_pair_rhs_n;`) this says:

* on the two-register forms the ucore's sum is `ea_residue` + `ea_pair_rhs`,
  and `ea_residue` carries **`AW`** (the value the store's own row left in
  `tmpa`, refreshed into the lane by `v30u_eu_step.svh:399`) while
  `ea_pair_rhs` carries the index.  **The sum is right and the ROLES ARE
  SWAPPED against silicon's**;
* on the single-addend forms `ea_pair_valid` is 0, so `tmpb` is left holding
  the loader's stale branch target — **which is the `0x8100` the divergence
  shows**, and it tracks the body address exactly (`+16` for `PC+0x10`).

**The `ea_residue_n = ea` written at `v30u_eu_arm_ea_calc.svh:35` is therefore
DEAD by the time the next instruction binds** — every ordinary `tmpa` write
between the two overwrites it.

---

## §3  PREDICTIONS — POINT, AND SCORED AS REGISTERED

| # | prediction |
|---|---|
| **P-1** | `sw/b2_ea_lane_ucore.py` reads **MATCH 13 / 13, DIVERGE 0 / 13** |
| **P-2** | the four rows that ALREADY match — `M0` `8888`, `M1` `9999`, `M2` `8888`, `M3` `9999` — **DO NOT MOVE** (WAVE 24 §6.3's registered falsifier) |
| **P-3** | the three controls `C1` `1234`, `C2` `beef`, `C3` `2222` **DO NOT MOVE** |
| **P-4** | `sw/lea_mod3_gate.py` stays **PASS** with `mod3_illegal` **UNMOVED at ARCH 0/128, cycles 128/128** — those 128 have no ModR/M predecessor at all.  ⚠ L4 is a *KNOWN-RED* observational leg reading the frozen `metadata.json`; **if the fix moves L4's ucore column, that is reported, not suppressed** |
| **P-5** | **THE LADDER IS ZERO-DELTA**, measured BOTH SIDES, except as P-6 allows |
| **P-6** | ⚠ **`ss_lint` MAY MOVE — DECLARED IN ADVANCE.**  The minimal edit needs **no new flop** (it changes what an existing rail is loaded with), so the expectation is **232 addresses / 229 flops / 4 whitelist / 0 UNMAPPED, UNMOVED, and NO `SS_VERSION` bump**.  **If the implementation turns out to need a flop or a widened rail, the map moves, `SS_VERSION` is bumped, and 0 UNMAPPED is NOT NEGOTIABLE** |
| **P-7** | **G6-C**, the registered floor: **`worst-of-5` CONTROL ≥ 33.00 MHz and RETENTION ≥ 33.00 MHz**, against the no-exception baseline **34.48 / 34.41** (WAVE 19 `armb_landing_results_2026-09-19.md`).  ⚠ **THE FLOOR IS REGISTERED HERE, BEFORE THE SWEEP.**  33.00 is chosen because it is the tree's own WAVE 16/17 measured no-exception `worst-of-5` CONTROL figure and is >1 MHz above the G6 PASS bar of 32.0; a draw below it is a REGRESSION and is reported as one |
| **P-8** | `mod=01` / `mod=10` — **THERE IS NO SILICON REFERENCE FOR THEM AND THIS WAVE DOES NOT ASSUME ONE BY SYMMETRY.**  If the board leg (§5) closes the gap, what was constructed and measured is stated.  If it does not, the fix's behaviour there is declared **PREDICTED, NOT MEASURED** |

---

## §4  BARS AND STOPS

**G6-A** `hdl/nec_test.sdc` **MUST REMAIN EXCEPTION-FREE** —
`grep -cE '^[[:space:]]*(set_multicycle_path|set_false_path|set_max_delay)'`
= **0**.  The unanchored count is 2 and both are the commented DO-NOT-RESTORE
record.  **Adding an exception to make the fix close is FORBIDDEN and is
STOP S-2.**

**G6-B** `python3 sw/quartus_gate.py` PASSES: Fmax ≥ 32 MHz, worst setup > 0,
setup AND hold TNS 0.000 every domain, E1 = `qsf_lint --check`.

**G6-C** P-7 above, a **5-seed sweep**, `worst-of-5` reported.

**G6-D** `cutset_lint` **81 / 0** and `phase_split_lint` **157 / 779 / 0**.
**If the mechanism wants a pre-cut wire, STOP AND REPORT — the cut set is NOT
widened** (STOP **S-3**).

**G6-E** `ss_lint` per P-6; **0 UNMAPPED is not negotiable**.

**STOPS**

| id | condition |
|---|---|
| **S-1** | the fix cannot be expressed as §1's single rule — **STOP, report, do not fit** |
| **S-2** | any live SDC exception is needed — **STOP, do not land** |
| **S-3** | a pre-cut wire is needed — **STOP, report, do not widen the cut set** |
| **S-4** | **INJECTING `ea_residue` THROUGH THE TESTBENCH BACKDOOR REMAINS FORBIDDEN** (WAVE 23's S-4, carried forward verbatim): it chooses an initial condition after seeing the answer |
| **S-5** | an UNPINNED divider readback on any board probe — **HARD STOP** |
| **S-6** | `sw/testdata/flash_log.jsonl` is not **26 entries / sha256 `13a81a43f30c380a…`** at the end — **HARD STOP.  NOTHING IS FLASHED IN THIS WAVE** |
| **S-7** | a ladder leg moves that is not attributed case-by-case — **report as registered, do not restate** |

---

## §5  THE SILICON BAR — B-3, AND WHAT IT COSTS

WAVE 24 §7 costed a `mod3_illegal` re-capture with a **declared predecessor**
at ~2 minutes of board time and recommended taking it *"as the silicon bar of
the RTL wave that fixes the qualifier, not before"*.

⚠ **`tests/v30/mod3_illegal/` IS FROZEN under WAVE 22's committed sha256
manifest `67161a0c409c7fc6…`, and `sw/lea_mod3_gate.py` READS ITS EXPECTED
VALUES OUT OF `metadata.json`.**  Therefore, **in this order or not at all**:

1. archive the suite byte-identical **before** any touch, with sha256 recorded;
2. an `invalidation_ledger.md` entry naming the register, before the replacement;
3. the gate **re-measured on BOTH sides** of the move.

**IF THE RE-CAPTURE CANNOT BE MADE READABLE BY THE SCORER, IT IS NOT SHIPPED**
— WAVE 24's §5 precedent, which refused exactly that trade.  The RTL fix does
**not** depend on it: §1's law is already anchored on thirteen socket rows.

**BOARD IS AUTHORISED FOR CAPTURE ONLY.  NO FLASH.**  Socket only
(`use_core=False`, passed explicitly every time — the CFG is STICKY);
`div_guard()` on every probe; full per-clock rows + sha256 retained;
`board_idle()` and a closing `use_core=0` chip proof.

---

## §6  THE FABRIC DEBT, STATED BEFORE IT IS INCURRED

This edit is in `hdl/rtl/ucore/`.  **It moves the bitstream.**  Therefore, the
moment it lands:

> **FLASH #23 STOPS COVERING THIS TREE.  A RE-FLASH IS OWED AND IS NOT TAKEN
> IN THIS WAVE.  NO FABRIC FIGURE TAKEN ON FLASH #23 OR EARLIER MAY BE QUOTED
> AGAINST THE LANDED TREE.**

It will be written into the results **and** into `CLAUDE.md`'s banner.

---

## §7  WHAT THIS WAVE WILL NOT DO

* No `git stash`, `git checkout .`, `git reset --hard`.  Every `git add` by
  explicit path; `sw/testdata/receipts/*.jsonl` never staged.
* No Codex.  No nested subagents.
* No flash.
* No SDC edit.
* No new gate built to make an old one pass.
