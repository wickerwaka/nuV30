# WAVE 7 — **LAND THE CHAIN FLATTENING.**  PRE-REGISTRATION.

Committed **BEFORE THE FIRST `hdl/` EDIT OF THIS WAVE.**  Source: WAVE 6
(`docs/notes/chainflat_results_2026-09-09.md`, `e542f4a6ae`), its
pre-registration `39e201aa6c` and its amendment `a734dd3d79`; the prototype is
`sw/testdata/chainflat/flat_prototype.diff`.

**THIS IS A LANDING.**  OFFLINE ONLY.  **NO BOARD.  NO FLASH.  NO BITSTREAM IS
PROGRAMMED.**  No Codex.  No nested subagent.  `docs/notes/standing_gates.md`
§A governs every timing figure; **one green build is not closure**.

---

## §0 THE STANDING DESIGN PRINCIPLE, VERBATIM (user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood.  A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

**THIS LANDING IS THAT PRINCIPLE CASHED IN.**  WAVE 6 measured that the
sevenfold unroll is a TRANSLITERATION ARTIFACT of the C++ model's control flow:
the nine chainable states are exactly the statement positions with no
`charge()` between them; the fall-through graph is a **DAG**, so one clock's
walk visits each state **at most once**; the register file is read at **exactly
one position and written at none** in all 25 observed sequences of depth ≥ 2;
and **68.98 % of 8,447,821 CE edges do not chain at all** while all seven
copies are paid combinationally on every one of them.

---

## §1 WHAT IS BEING LANDED

WAVE 6's **FLAT** arm: the bounded `for (chain = 0; chain < CHAIN_MAX; ...)`
loop — **seven full copies of a 33-arm `case`** — replaced by

* **position 0**: the 33-arm `case`, ONCE; then
* **positions ≥ 1**: the **NINE** chainable arms, **ONCE EACH**, in
  TOPOLOGICAL ORDER, each guarded by `st_n == S_X`.

The substitution is exact because the fall-through graph is a DAG over exactly
those nine states, so a walk is a SUBSEQUENCE of any topological order.  **That
is an argument.  The gate is G-1.**

⚠ **IT IS RE-DERIVED INTO THE TREE, NOT BLIND-APPLIED.**  WAVE 6's generator
carved the nine arm bodies out of `v30u_eu_step.svh` into scratch files and
left the originals in place, so the prototype tree carries **two copies of each
chainable arm**.  A landing may not.  The nine arm bodies move into
`hdl/rtl/ucore/v30u_eu_arm_<state>.svh` and are `` `include ``d from **both**
sites — the `case` at position 0 and the flattened position ≥ 1 — so there is
**ONE source of truth per arm**.  This is the file's existing idiom
(`v30u_eu_row.svh`, `v30u_eu_iend_late.svh`, `v30u_eu_1bl.svh`, …).

### 1.1 WHAT IS PRESERVED, AND EACH IS A BAR

| preserved | how |
|---|---|
| the `CHAIN OVERFLOW` `$fatal` — **the bound is a CLAIM and must stay asserted continuously** | it stays, in the clocked observer, and it is SPLIT into the two things the loop's single `!stop` test was conflating: **(i) the walk terminated inside the pass** and **(ii) the depth stayed under `CHAIN_MAX`**.  Both `$fatal`, both name `CHAIN OVERFLOW` |
| `sw/chain_lfsr_gate.py` reading `CHAIN_MAX` OUT OF THE RTL | **`localparam bit [3:0] CHAIN_MAX = 4'd7;` KEEPS ITS EXACT DECLARED SHAPE AND VALUE**, so the gate's regex, its H-1 bar (`depth ≤ CHAIN_MAX − 1`) and its `--nonvacuity` rewrite to `4'd4` all work **with the gate unedited**.  ⚠ **If any edit to `chain_lfsr_gate.py` proves necessary it is itself a change and is justified in the results document** |
| the `st_zero_ok` fail-safe's PURPOSE — spend a clock rather than hang in fabric | the explicit `if (!stop && !st_zero_ok(st_n)) stop = 1'b1;` is kept at the entry to positions ≥ 1, exactly as the prototype has it; and the flattened pass is straight-line code, so an unhandled state ends the edge structurally and the successor clock re-enters it at position 0 |
| WAVE 6's `` `ifdef CHAIN_PROBE `` sequence census | it keeps working, re-keyed off the running position index instead of the loop variable.  It is exercised in this wave and its output compared |

### 1.2 WHAT `CHAIN_MAX` MEANS AFTER THE LANDING — DECLARED IN ADVANCE

Before: the number of UNROLLED COPIES, so the bound was enforced structurally
and the `$fatal` detected the enforcement biting.  After: the flattened pass
provides nine positions ≥ 1 by construction, so **`CHAIN_MAX` is no longer a
resource limit — it is purely the DECLARED DEPTH BOUND, checked directly
against the measured depth** (`chain_used > CHAIN_MAX − 1` ⇒ `$fatal`).  **The
claim is unchanged and it is now asserted more directly than before.**  The
value stays **7** so that every historical figure remains comparable and the
gate stays unedited.

---

## §2 THE BARS.  THEY ARE THE COORDINATOR'S AND THEY ARE NOT SOFTENED

**G-1  PIN IDENTITY — THE LANDING BAR.**  All three:
  * **(a)** `sw/chain_lfsr_gate.py` — the four per-seed signatures
    **BYTE-IDENTICAL** to the pre-edit run, with `CHAIN_DEPTH_MAX`, `entry_st`,
    `coincide` and **every gap count** identical too;
  * **(b)** `sw/fz2_replay.py` scored-content **sha256 IDENTICAL** pre- and
    post-edit (the `tb_sys` binary receipt is the ONE field that may move, and
    **must**);
  * **(c)** the full ladder of G-2.
  **The BEFORE side is taken on the UNEDITED tree FIRST**, so the A/B is real.

**G-2  THE LADDER, EVERY LEG AT ITS REGISTERED VALUE.**  `r7_lint` PASS ·
`check_core --opcodes all --cases 0` **169,000** · `8F.0` **500** · the HLT
sweeps ⚠ **WITH `--waits 0/1/2/3`** **97 · 93 · 45 · 44 = 279/283** ·
`v0.1-w1`/`-w3` **1,200** · `EB` **200** · the four `evt` cells
**200/1,200/200/1,200** · `v0.1-w1evt-biased` **1,200** ·
`ulockstep --golden all --cases 50` **17,350 ALL LOCKSTEP** ·
`ghost_launch_law` **200/200** · `check_boot` **220** and **400** ·
`check_ab_sim` **187** · `sm3_s16_score` **1,320/1,371** · `demux_off_gate`
PASS · `test_artifact` **45/45** · `test_quartus_gate` · `ucrom_mif_check` PASS
· `chain_lfsr_gate` PASS.
⚠ **EVERY LEG IS VERIFIED AGAINST `standing_gates.md` FIRST.**  Two rows there
are KNOWN STALE on `master` (`test_quartus_gate` 200/200 against a measured
255; the `ss_lint` row carries another branch's 226/214/0x8D against `master`'s
232/228/0x8F).  **Measure, report the disagreement, and never treat a stale row
as a failure.**

**G-3  `ss_lint --core ucore` exits 0**; `SS_COUNT` / `SS_VERSION` / `SS_TAG`
**UNCHANGED**; **0 UNMAPPED**.  WAVE 6 measured registers **807 → 807**, so
**NO FLOP may be added or removed.  A moved flop count is a finding.**

**G-4  `check_core --opcodes all --cases 0` = 169,000 at `--ce-div` 2, 3, 4
AND 8**; `--ce-div 1` still **REFUSED**.

**G-5  THE LANDING'S OWN TIMING BAR — WITH the exception, the tree's current
SDC.**  `sw/quartus_gate.py --seeds 5` PASSES E1–E5 on every draw, BOTH
configurations.  `worst-of-5` reported against the pre-landing figures (WAVE 3
measured CONTROL 37.29–39.51).  **A REGRESSION HERE FAILS G-5.**

**G-6  THE SCOREBOARD — WITHOUT the exception**, `--seeds 5`, both
configurations.  Every draw's verdict, Fmax, worst setup, `core_domain` k and
`off_class`, and **the GAP to 32.0 stated explicitly**.  **RED IS EXPECTED AND
IS NOT A REVERT CONDITION.**  Pre-landing is **22.18**.

**G-7  THE OUT-OF-CONTEXT CORRECTION.**  WAVE 6 measured **−9.431 ns** in a
standalone project.  Report the **IN-CORE** delta on the same arc and **the
difference between them**.  WAVE 5 measured out-of-context estimates
mispredicting by **+11.3 to +20.0 ns**; WAVE 6's positive control reproduced
WAVE 5's in-situ per-position figure to **0.025 ns**.  **This wave settles
which.  Report it whatever it says.**

**G-8  AREA.**  Combinational ALUTs and registers for `v30u_eu` and for the
whole design, against WAVE 6's isolated **−29.3 % / 807 → 807**.

**G-9  NON-VACUITY.**  The `CHAIN OVERFLOW` assertion still **FIRES** when its
condition is constructed, and the `st_zero_ok` fail-safe is still **reachable
and demonstrated**.

**G-10  THE REVERT CONDITION.**  If ANY leg of G-1 / G-2 / G-3 / G-4 moves, or
G-5 regresses, **THE LANDING DOES NOT HAPPEN**: revert, report, keep both
documents.  **Do not soften a bar to make a landing possible.**  **G-6 being
RED is NOT a revert condition.**

### 2.1 ADDED BY THIS DOCUMENT (they may only make the landing harder)

**G-11  ONE SOURCE OF TRUTH PER ARM.**  After the landing, each of the nine
chainable arm bodies exists in the tree **exactly once**.  Checked
mechanically, and the check is reported.

**G-12  THE INCLUDE IS TRANSPARENT.**  `verilator -E` on
`v30u_eu_step.svh`'s expansion, blank lines removed, must show the nine arm
bodies **byte-identical to their pre-edit text** — the bodies are RELOCATED,
never rewritten.  A diff is a MISS and is reported as one.

**G-13  THE FLATTENED PASS IS A TOPOLOGICAL ORDER OF THE STATIC GRAPH.**
Re-derived from `sw/chainflat_graph.py` at landing time, not copied from WAVE
6's report, and every fall-through edge among the nine checked to run FORWARD
in the emitted order.  A backward edge would silently drop a step, and it is
the one way this substitution can be wrong.

---

## §3 WHAT IS DELIBERATELY NOT DONE

1. **NO BOARD, NO FLASH, NO BITSTREAM.**  **THE FABRIC CONFIRMATION IS OWED**
   and is recorded as owed: this changes the EU's decode and a bitstream will
   eventually have to prove it.
2. **NO Fmax CLAIM.**  Five draws are not a distribution; the same tree has
   drawn 19.42 and 45.91 MHz (`ucore_provenance.md` §74.4).
3. **NO CUSTOM SDC RULE IS ADDED OR RE-OPENED.**  USER RULING 2026-09-08:
   *"I don't want custom sdc rules, period."*  The no-exception build is the
   goal state and G-6 measures it.
4. **`CHAIN_MAX` IS NOT CHANGED IN VALUE OR IN DECLARED SHAPE.**
5. **THE FRONT END IS NOT TOUCHED.**  WAVE 6 measured it to be what binds
   after the fold; it is the next wave's problem.

---

## §4 DISCIPLINE, DECLARED

* OFFLINE ONLY.  NO BOARD.  NO FLASH.  No Codex.  No nested subagent.
* Single-writer guard by EXACT binary name (`pgrep -x`) before any Quartus
  stage; `hdl/nec_test_ucore.qsf` `git checkout --`'d between Quartus runs.
* `~/.cache/ucsimt-tmp/` for every intermediate; nothing large in `/tmp`.
* Receipted binaries rebuilt through their own recipes
  (`python3 sw/check_core.py --build --core ucore`).  ⚠ **A Verilator artifact
  receipt is NOT reproducible across rebuilds of a byte-identical tree
  (WAVE 3), so "the receipt moved, therefore the edit reached the binary" is an
  INVALID inference.**  Reach is proved another way and the proof is named.
* ⚠ Verilator `$stop`s on the first `$error`.  ⚠ `git add -A hdl/` is never
  used.
* **A number with no artifact id is not quotable.**
* **Record what was measured, not what was expected.**
