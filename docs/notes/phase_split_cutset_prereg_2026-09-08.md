# THE PHASE SPLIT, DONE AS A CUT SET — WAVE 4.  PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST EDIT UNDER `hdl/`.**  Tree at entry
`6d0c770e9146ab79bbd9343a756ac848cd31df35` (`master`),
`git status --porcelain hdl/` clean of tracked modifications (twelve
pre-existing untracked `hdl/quartus_gate_*.log` files, which are not this
wave's and which this wave does not `git add`).

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WILL BE PROGRAMMED.**
No Codex consultation.  No nested subagent.

Predecessors, read in full before this document was written:
`phase_split_anatomy_2026-09-08.md` (WAVE 1),
`phase_split_landing_results_2026-09-08.md` (WAVE 2, **FAILED**, §11.6 is the
diagnosis), `l2_registered_row_results_2026-09-08.md` (WAVE 3, **REFUTED BY
L-8**, §5.2 is the LOOP finding and §5.3 names the candidate cut).

---

## §0 THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
Complex or confusing observed behavior is likely simple systems interacting
in ways not yet understood.  A large fitted table, a many-cased rule, or a
per-opcode special case is a signal of misunderstanding, not a deliverable.

## §0.1 THE STANDING REQUIREMENT (USER RULING 2026-09-08, verbatim)

> **"I don't want custom sdc rules, period."**  and *"Don't try to reframe my
> original ask."*

The target state is that the ucore closes timing with **NO
`set_multicycle_path` and no other core-specific exception in the integrator's
SDC**.  It is a product requirement, not a trade.  It is **NOT RE-OPENED HERE**
and no build with the multicycle is anything but a control.

**THE SCOREBOARD ON ENTRY, MEASURED (WAVE 3 §4.2):** no-exception
`worst-of-5` is **22.18 MHz** (CONTROL) / **22.16** (RETENTION) against the
**32.0 MHz** bar — **9.82 / 9.84 MHz short.**

---

## §1 WHY THIS WAVE EXISTS, IN THREE SENTENCES OF MEASUREMENT

1. **THE EU IS A LOOP, NOT A SERIES CHAIN** (WAVE 3 §5.2): `upc_*` →
   `ucdecode` → `ucrom` → `row` → row decode → operand/EA select → the unrolled
   chain → `upc_*_n` → `upc_*`, one traversal per CPU clock, ~43.5 ns, broken
   by exactly ONE register bank.  Registering a table RELOCATES the break and
   leaves the chain in BOTH halves; L2 measured **+0.36 MHz** for it, inside
   the baseline's own 0.76 MHz five-draw spread.
2. **A `ce_half` SUB-CYCLE REGISTER IS THEREFORE THE ONLY MECHANISM
   AVAILABLE** — any `ce`-gated register inside the loop makes the loop take
   two CPU clocks and breaks cycle-exactness; a `ce_half` register costs no CPU
   clock.
3. **WAVE 2 CUT IN THE RIGHT PLACE AND STILL FAILED, AND ITS §11.6 SAYS WHY**:
   its shadow held the loop-carried `_n` set (495 bits) and the binding path
   had **103 arrival points of which ZERO named the shadow**.  `row` and the
   row-decoded fields are module-level WIRES that the loop body reads DIRECTLY,
   so stage 2 bypassed the register entirely.  **IT WAS NOT A CUT SET.  It was
   a register placed BESIDE the loop, not ACROSS it.**

> **THE RULE FOR THIS WAVE, AND IT IS THE WHOLE OF IT: A CUT SET PROVEN BY
> CONSTRUCTION, NEVER A CUT POINT FOUND IN A NET CENSUS.**  Every combinational
> path from a stage-1 source to a stage-2 sink must pass through a shadowed
> signal, and that must be true BECAUSE STAGE 2 CANNOT NAME A PRE-CUT WIRE —
> not because a census says so.  A Quartus net name is not an RTL seam: WAVE 2
> refuted that identification for `Decoder28#1`, and the same caveat governs
> WAVE 3 §5.3's `Selector1552#1`, which is **NOT** the object this wave cuts at
> and is not used to choose anything here.

---

## §2 THE FIRST JOB, DONE FIRST: THE TWO SHAPES, MEASURED BEFORE THE DESIGN

`sw/cutset_census.py` (committed with this document, run on the entry tree)
derives both candidate crossing sets FROM THE SOURCE.  Its live set is
`r7_lint`'s own, not a guess: the three asynchronous pins (`pin_int`,
`pin_nmi`, `pin_poll_n`) plus `r7_lint`'s ONE declared live-`READY` carrier
(`eu_rd_edge`, with its data twin `eu_rd_edge_d`) plus its TWO declared
UNRESOLVED carriers (`eu_slot_busy_n`, `q_ripe_lead_n`).

```
module-level wires declared      : 268
  ...LIVE-TAINTED                : 4
read by the NEXT-STATE BLOCK     : 70

SHAPE (B) crossing wires (clean) : 70 names / 183 bits
SHAPE (B) + wave 2's `_n` set    : 183 + 495 = 678 bits

SHAPE (A) `row` only             : 29 bits  (+ wave 2's 495 = 524)

LIVE-TAINTED wires the block reads (STAGE-2 SOURCES, not shadowable): 0
```

| shape | what crosses | width |
|---|---|---:|
| **(A)** `row` (29 b) shadowed, the row decode RE-DONE inside stage 2, plus wave 2's loop-carried `_n` set | 29 + 495 | **524 bits** |
| **(B)** the DECODED outputs — all 70 module-level wires the next-state block reads — plus wave 2's loop-carried `_n` set | 183 + 495 | **678 bits** |

**THE STOP THRESHOLD IS 900 BITS.  BOTH ARE UNDER IT.**

**THE WAVE TAKES (B), AND THE REASON IS THE BALANCE, DECIDED BEFORE ANY
RESULT.**  (A) is cheaper in flops and moves the row decode, the operand /
queue-state select, the ALU flag rails (`sig_flags`, `sig_mask` — 32 of the
183 bits) and the accumulated address (`acc_off_nog`, 16 bits) INTO the
downstream half, which is the half WAVE 3's census already puts at 21.1 ns.
(B) keeps the ~21.7 ns front end upstream where the census puts it.  The two
widths are REPORTED because the brief asks for both; the choice is made on the
balance and not on the count.

**A THIRD, UNMEASURED FACT THIS CENSUS ESTABLISHES AND IT IS THE ONE THAT
MAKES THE WAVE POSSIBLE: NOT ONE of the 70 wires the next-state block reads is
live-tainted.**  The union of module INPUTS their cones reach is
`{eu_access_active, eu_opr_free, eu_rd_done_n, eu_slot_busy, eu_wr_done_n,
eu_wr_eval, q_byte}` — seven, every one of them the BIU's own REGISTERED view
(`v30u_biu.sv`'s "THE EU CONTRACT"), none of them `r7_lint`'s carriers, and
none of them downstream of `t1_half2` (which has zero consumers in the BIU's
next-state logic, `t1_half2_anatomy_2026-08-13.md` §1.3).  So the ENTIRE
front-end wire cone is phase-stable and the cut set is not a subset chosen for
convenience — **it is everything.**

---

## §3 THE DESIGN

**STAGE 1** — evaluated in the `ce -> ce_half` window, captured on `ce_half`:
the microcode ROM read, the row-field decode, **the whole module-level
combinational wire cone the next-state block reads**, the BIU completion
sampling and the recognition arm (WAVE 2's blocks (a)-(f)).
**STAGE 2** — evaluated in the `ce_half -> ce` window, captured on `ce`: the
unrolled `for (chain = 0; chain < CHAIN_MAX; ...)` loop, block (g)'s pin
pipelines, and the `dec_addr_next` tail.

**HOW STAGE 2 IS MADE UNABLE TO NAME A PRE-CUT WIRE.**  Each of the 70 wires
is RENAMED at its declaration and at every reference OUTSIDE the next-state
block to `s1w_<name>`; a module-level `reg <name>` of the same width is
declared in its place; STAGE 1 assigns `<name> = s1w_<name>` once, at its head;
`<name>` joins the pack and the unpack.  **No line of `v30u_eu_step.svh` or of
any other include changes**, because the name the loop body writes is now bound
to the shadowed `reg` rather than to the wire.  A stage-2 read of the pre-cut
value would have to write `s1w_` and that is what the lint forbids.

WAVE 2's three non-mechanical decisions are RE-USED VERBATIM and are not
re-argued here (`phase_split_landing_results_2026-09-08.md` §2.1): the
unconditional `CE_HALF` port, `poll_pipe_n`'s move to block (g), and the
`(ss_we || srst || ce_half)` commit condition with the preload re-run in the
`ss_we` arm (RULING 2's option (i): **no rule is widened**).

---

## §4 THE REGISTERED BARS

They are the coordinator's, carried VERBATIM.  C-11 and C-12 are ADDED by this
document.  Results go in a SEPARATE `phase_split_cutset_results_2026-09-08.md`.

| bar | statement |
|---|---|
| **C-1** | **THE REQUIREMENT.** With the CE multicycle DELETED from `nec_test.sdc`, `sw/quartus_gate.py --seeds 5` PASSES E1-E5 on EVERY draw (Fmax >= 32.0 MHz, worst setup > 0, TNS 0.000 setup AND hold, 0 errors / 0 latches / 0 lpm_divide), on BOTH configurations. **This is the wave's success condition and the campaign's.** |
| **C-2** | THE EXCEPTION IS GONE AND IT IS CHECKED: no `set_multicycle_path` and no "CE multicycle" info line; every receipt's `core_domain` reports k = 1. |
| **C-3** | **THE CUT SET IS COMPLETE, PROVEN TWO WAYS.** (a) BY CONSTRUCTION: the new lint passes, and is demonstrated FIRING on a deliberately re-introduced bypass; (b) BY MEASUREMENT: on a no-exception fit, the worst `ce -> ce` path's arrival points **DO** name the shadow — the direct refutation of WAVE 2's "103 arrival points, zero named it". Report the count. |
| **C-4** | PIN IDENTITY. `chain_lfsr_gate`'s four signatures BYTE-IDENTICAL with every gap count and census; `fz2_replay` scored-content sha256 IDENTICAL; the full ladder of C-5. Take the BEFORE side on the unedited tree first. |
| **C-5** | THE LADDER, EVERY LEG AT ITS REGISTERED VALUE: `r7_lint` PASS · `check_core --opcodes all --cases 0` 169,000 · `8F.0` 500 · HLT sweeps ⚠ WITH `--waits 0/1/2/3` 97·93·45·44 = 279/283 · `v0.1-w1`/`-w3` 1,200 · `EB` 200 · the four evt cells 200/1,200/200/1,200 · `v0.1-w1evt-biased` 1,200 · `ulockstep --golden all --cases 50` 17,350 ALL LOCKSTEP · `ghost_launch_law` 200/200 · `check_boot` 220 and 400 · `check_ab_sim` 187 · `sm3_s16_score` 1,320/1,371 · `demux_off_gate` PASS · `test_artifact` 45/45 · `test_quartus_gate` · `ucrom_mif_check` PASS.  ⚠ VERIFY EACH AGAINST `standing_gates.md` FIRST; several rows there are KNOWN STALE on `master` — measure, report the disagreement as a finding, and never treat a stale row as a failure. |
| **C-6** | `ss_lint --core ucore` exits 0; `SS_COUNT`/`SS_VERSION`/`SS_TAG` UNCHANGED; 0 UNMAPPED; whitelist grown by exactly the shadow's entry. |
| **C-7** | `check_core --opcodes all --cases 0` = 169,000 at `--ce-div 2, 3, 4 AND 8`; `--ce-div 1` still REFUSED. The split makes S-1 load-bearing for the EU, so this is a correctness bar, not a cross-check. |
| **C-8** | THE TWO STAGES, MEASURED on a no-exception fit: worst `* -> shadow` and worst `shadow -> *`, with delays and levels, plus the worst `ce -> ce` path that touches NEITHER (WAVE 2's failure signature). The third must not exist; if it does, name it — that is the next cut. |
| **C-9** | NON-VACUITY: the shadow is load-bearing (perturbing one bit breaks a named gate leg); the lint fires on a re-introduced bypass; S-1's `$fatal` fires and its message names the EU's dependence. |
| **C-10** | THE REVERT CONDITION. If C-1 fails, or any leg of C-4/C-5/C-6/C-7 moves, THE LANDING DOES NOT HAPPEN. Revert, report, keep both documents. **Do not soften a bar to make a landing possible, and do not re-scope the cut after seeing a result.** A wave that reports "still N MHz short, and here is the arc" has done its job — report the GAP explicitly. |
| **C-11** *(added)* | **THE PHASE-STABILITY PREMISE IS ASSERTED AT RUNTIME, NOT ARGUED.** WAVE 2's `ifndef SYNTHESIS` `$fatal` on `s1q !== s1_bus` at every `ce` is kept and now covers 678 bits including the whole wire cone. It must not fire on ANY leg of C-5, C-7 or `chain_lfsr_gate`. ⚠ A FIRE IS A FINDING, NOT A NUISANCE: it would mean one of the seven BIU inputs §2 names is not phase-stable, and the term must move to stage 2 as `poll_pipe_n` did — reported, not silenced. |
| **C-12** *(added)* | **`demux_off_gate` MUST PASS** and `CE_HALF` is an unconditional port again (WAVE 2's edit (a), `ebe0c9fcbd`). ⚠ REPORTED IN BOTH DIRECTIONS: that edit DELETES `demux_off_gate`'s `CE_HALF` GONE-clause, because splicing that pin into a define-off build now SUCCEEDS and asserting that it fails would be asserting something false; the `AD` and `AD_OE` clauses are untouched and are what keep the leg non-vacuous.  ⚠ It also SUPERSEDES the two RULING-1 clauses `master` carries under `ifdef V30_MUXED_AD`: they move DOWN into the bus-shape-independent SS block, where they are asserted in EVERY configuration. That is strictly more than `master` asserts, and it is a widening of the RULING's REACH, not of any rule. |

### 4.1 THE PREDICTION, PRE-REGISTERED SO IT CAN BE REFUTED

**C-1's outcome is NOT predicted GREEN.**  What is predicted, and what may be
scored against this document:

* **P-a** the no-exception CONTROL `worst-of-5` is **> 26.0 MHz** — i.e. the
  cut set moves the goal state by more than WAVE 3's +0.36 MHz and by more than
  the 0.76 MHz instrument spread.  *A miss here means the front end is not
  where the census puts it.*
* **P-b** on a no-exception fit the worst `ce -> ce` path's arrival points
  name the shadow — **C-3(b)**, against WAVE 2's zero.
* **P-c** the shadow is **678 bits declared**; the number that SURVIVES
  synthesis will be smaller (WAVE 2 measured 465 of 495) and nothing is
  claimed from that count.

**None of P-a/P-b/P-c is a revert condition.**  C-10 is.

---

## §5 DISCIPLINE, RESTATED SO IT IS SCORED

* OFFLINE ONLY.  **NO BOARD.  NO FLASH.**  A fabric confirmation is recorded as
  OWED (WAVE 2 §10 item 1 and WAVE 3 §6 item 1, unchanged and unpaid).
* Single-writer guard before any Quartus stage (`pgrep -x`, EXACT name).
* `/tmp` discipline: `~/.cache/ucsimt-tmp`, never `/tmp`.
* ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection — use
  `get_pins`.  ⚠ `string match` on a register name carrying a bus index FAILS
  (`[3]` is a character class) — use `[string first $p $s] == 0`.
* ⚠ Verilator `$stop`s on the first procedural `$error`; each clause gets its
  own probe.  ⚠ Do NOT `git add -A hdl/`.
* ⚠ **A VERILATOR ARTIFACT RECEIPT IS NOT REPRODUCIBLE ACROSS REBUILDS OF A
  BYTE-IDENTICAL TREE** (WAVE 3 §6 item 9, measured).  "The receipt moved,
  therefore the edit reached the binary" is an INVALID inference and is not
  made here; reach is proved by a behavioural falsifier on the rebuilt binary
  and, on the Quartus side, by the content-hashed `input_manifest`.
* Record what was measured, not what was expected.

---

# AMENDMENT A-1 — **THE CUT SET WAS NOT COMPLETE, AND THE LINT COULD NOT SEE IT**

**COMMITTED BEFORE THE FIRST EDIT IT GOVERNS.**  It amends §2 and §3 of this
document.  **IT CHANGES NO BAR.  C-1 … C-12 STAND VERBATIM.**

## A-1.1 WHAT WAS MEASURED, AND IT IS A MEASUREMENT AND NOT A RE-READING

The landed cut set (edit (b), `3e0a4dfc3b`) was scored: **C-1 FAILED**, CONTROL
`worst-of-5` **22.15 MHz**, RETENTION **22.90**, RED on ten of ten draws, against
WAVE 3's pre-L2 no-exception baseline of 21.82.  `sw/sta_cutset_diag.tcl` on the
worst CONTROL draw (seed 3) then said:

```
  worst ce->ce   modrm_reg[1] -> opc_base[3]   slack -13.888   44 levels   data 44.502
    arrival points: 107   of which name |s1q : 0        <<<< C-3(b)
    ...and of which live in v30u_biu : 0   v30u_eu : 3   elsewhere : 104
  STAGE 1 (anything -> s1q), worst:  modrm_reg[1] -> s1q[625]   +8.326   17 levels   22.271 ns
  STAGE 2 (s1q -> anything), worst:  s1q[14] -> opc_base[3]     -8.808   36 levels   39.462 ns
  top 200 ce->ce: STAGE 1 count 0 . STAGE 2 count 0 . NEITHER count 200
```

**ZERO of 107, AGAIN — WAVE 2's SIGNATURE, ONE LAYER IN.**  The arrival-point
dump names the leak to the node:

```
  modrm_reg[1] -> opc_sel[1]~2 -> Add4~2 -> sigma[1]~0 -> s1_bus[65]~43
              -> LessThan7 -> Selector5/3 -> sigma[13]~42 -> Mux264~6
              -> v1~22 -> Add57 (the EA add) -> ... -> the chain -> opc_base[3]
```

## A-1.2 THE CAUSE — **"MODULE-LEVEL COMBINATIONAL VALUE" IS NOT "WIRE"**

`v30u_eu.sv` has **SIX OTHER combinational `always @*` blocks** — the ALU, the
BCD unit, the iterative stepper, the Source1 select, the Source2 select and the
reset function — and they drive module-level **`reg`s**, which are exactly as
combinational and exactly as pre-cut as a `wire`.  `sw/cutset_census.py` walked
CONTINUOUS ASSIGNMENTS only, so it returned 70 names / 183 bits and called that
"everything the block reads"; `sw/cutset_lint.py`'s X4 asked the same too-narrow
question and answered **PASS**.

**TEN NAMES / 100 BITS WERE MISSING**, and they are precisely the segment
WAVE 1 §2 measured at 9.34 ns — the operand / queue-state select — plus the
iterative unit:

`s1_val` (16) · `s1_byte` (1) · `s1_wbyte` (1) · `s2_val` (16) · `s2_wbyte` (1) ·
`it_val` (16) · `it_tmpa` (16) · `it_flags` (16) · `it_fmask` (16) ·
`it_writes_tmpa` (1).

**THE CORRECTED LINT FAILS ON THE LANDED TREE AND NAMES ALL TEN** — that is the
falsifier, run before the amendment's edit:

```
  module combinational values the block names : 10 (must be 0)
  VIOLATION X4: ... ['it_flags','it_fmask','it_tmpa','it_val','it_writes_tmpa',
                     's1_byte','s1_val','s1_wbyte','s2_val','s2_wbyte']
=== cutset_lint: FAIL   (70 members / 1 violations)
```

**The exclusion of the block's own scratch is a RULE, not a list**: a name the
PRELOAD assigns is the next-state block's own mirror or scratch and is not a
pre-cut value.  That is what excludes `rep_chained`, which the reset block and
the next-state block share as a scratch name.

## A-1.3 WHAT THIS AMENDMENT DOES, AND WHAT IT DELIBERATELY DOES NOT

**IT COMPLETES THE REGISTERED CUT SET.  IT DOES NOT MOVE THE CUT.**  The
boundary is unchanged — the front end upstream, the unrolled chain downstream —
and the ten names are added to the SAME shadow by the SAME mechanism (rename to
`s1w_`, alias once at the head of stage 1, pack, unpack).  **No `.svh` is
edited.**  This is the same class of correction WAVE 2 recorded in its §0 — *"a
CORRECTION IN THE SAFE DIRECTION, recorded rather than smoothed over"* — made
against an instrument defect and not against a result.

> ⚠ **AND IT IS STATED PLAINLY SO A READER CAN DISAGREE WITH IT.**  The brief
> says *"do not re-scope the cut after seeing a result."*  The judgment here is
> that COMPLETING a set the instrument mis-derived is not re-scoping, because
> the cut, the stages, the mechanism and every bar are unchanged and the
> correction is forced by the design's own registered claim (C-3(a), "THE CUT
> SET IS COMPLETE").  **The first cut set's result stands and is reported in
> full and is not withdrawn**; this is scored SEPARATELY and beside it, and if
> the coordinator reads it as a re-scope, the primary result is unaffected.

**THE WIDTH, MEASURED BEFORE THE EDIT:**

| | names | bits |
|---|---:|---:|
| the wire cone (edit (b), landed) | 70 | 183 |
| **+ the `always @*`-driven module regs (A-1)** | **+10** | **+100** |
| = the completed crossing set | 80 | **283** |
| + wave 2's loop-carried `_n` set | | + 495 |
| **= `S1W`** | | **778** |

**THE STOP THRESHOLD IS 900.  778 IS UNDER IT.**  Live-tainted members: **0** —
the ten add no module input to the union of §2, which stays the seven registered
BIU views.

**THE PREDICTION, PRE-REGISTERED SO IT CAN BE REFUTED.**  §4.1's P-a/P-b/P-c
stand.  Added:

* **P-d** the corrected lint reads PASS with `module combinational values the
  block names : 0`, and the worst `ce -> ce` path's arrival points **name the
  shadow** (C-3(b)).
* **P-e** STAGE 2's worst (`s1q -> *`) falls from **39.462 ns**.  *A miss here
  says the chain alone is over budget and the split cannot close whatever
  crosses it — which would be the campaign's answer, not this wave's failure.*

None of P-a…P-e is a revert condition.  **C-10 is.**
