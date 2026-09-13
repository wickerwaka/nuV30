# WAVE 14 — PRE-REGISTRATION.  **SIZE THE `q_ripe_lead_n` ROUND TRIP ON THE SPLIT TREE, WITH A PROBE THAT ADDS NO FLOP.**

Committed **BEFORE the first `hdl/` edit of any tree and BEFORE the first
Quartus stage.**

**MEASUREMENT ONLY.  NOTHING IS LANDED.  OFFLINE ONLY — NO BOARD, NO FLASH,
NOTHING PROGRAMMED.**  No Codex.  No nested subagent.

---

## §0 THE QUESTION

**What is the `q_cnt → poppable_n → q_ripe_lead_n → EU` EU→BIU→EU round trip
worth ON THE SPLIT TREE?**

WAVE 13 measured the phase split like-for-like at **+2.75 MHz (CONTROL) /
+4.14 (RETENTION)**, leaving a gap to 32.0 MHz of **1.47 / 0.85 MHz**.  WAVE 9
§5.4 named the round trip as the binding class on **200 of 200** paths of the
split tree and WAVE 10 measured it present on **6 of 6** split-tree draws
against **5 of 13** unsplit ones.  **For the first time a named mechanism may be
the same size as the remaining gap, and nobody has measured it in the
configuration that matters.**

WAVE 10 sized it only on the UNSPLIT tree — **+0.527 ns, 95 % CI
[−0.185, +1.239], t = 1.68**, against a census figure of 2.786 (a **5.3×**
overstatement, matching WAVE 8's **5.9×** on `ucrom`).  Its cut-tree arm read
**+6.629 ns and OVER-ANSWERED**: that arm inserted a REGISTER, whose 25.249 ns
arc is BELOW WAVE 9's two-stage ceiling of 27.922, so it had **subdivided
STAGE 2** and was measuring "sever the round trip AND add a third pipeline
stage".  **Two honest readings disagree by ~4 MHz.  Settling that is this
wave.**

---

## §1 THE ARMS.  **ALL THREE COMPILED FROM ONE BASE COMMIT, IN SCRATCH GIT WORKTREES.**

**BASE = the SPLIT tree = `850ef46559`** — WAVE 13's tree with its three edits
(c) `d3aa3900c5`, (a) `e067df84e4`, (b) `35395c8cc2` applied, i.e. WAVE 9's
`bacf7f9fd9` / `6e822bf750` / `5cf3254104` re-applied byte-for-byte (WAVE 13 §6
established `git diff <WAVE 9 commit> -- <its files>` EMPTY after each pick).
Taking the WHOLE commit also brings edit (c)'s `sw/` half — the no-exception
SDC **and** `quartus_gate.py`'s nominal of 1.0 — so **`off_class` EMPTY at
k = 1.0 is this wave's N-2-equivalent check** and the polarity is WAVE 13's, not
WAVE 7's.

⚠ **THE BASE ARM IS DRAWN FRESH IN THIS WAVE.**  WAVE 13's 30.53 / 31.15 are a
CROSS-CHECK that may be reported, **never this wave's control.**

| arm | the edit to `hdl/rtl/ucore/v30u_biu.sv` | flops added |
|---|---|---|
| **BASE** | none | — |
| **ARM-T `qripe_tie`** | `assign q_ripe_lead_n = 1'b1;` — WAVE 10's booked-and-never-run probe, implemented at `sw/biu_ceiling_proto.py:108` | **0** |
| **ARM-H `qripe_hold`** | `assign q_ripe_lead_n = (poppable != 4'd0) \|\| ((r_grn_ttl == 2'd1) && (r_q_cnt != 4'd0));` — the SAME function computed off the REGISTERS that already exist (`poppable`, `v30u_biu.sv:842`, already drives `q_ripe`) instead of off the procedural next-state | **0** |

**BOTH ARMS ARE BEHAVIOUR-BREAKING BY CONSTRUCTION.  NO EQUIVALENCE IS CLAIMED
FOR EITHER.  NEITHER IS PROPOSED AS A DESIGN.  NEITHER IS EVER LANDED.**
ARM-T deletes the mechanism (the EU is handed a constant); ARM-H hands the EU
**last clock's** level where the F7 contract promises the **next** one.

### 1.1 WHY TWO ARMS, AND WHY BOTH ARE REGISTERED NOW

They fail in **opposite directions**, and registering both before either is run
is what stops the answer being chosen afterwards:

* **ARM-T over-answers by PRUNING.**  A constant `q_ripe_lead_n` lets the
  compiler delete the `poppable_n` cone **and constant-fold every EU consumer of
  it** — area and depth no real mechanism gets to delete.  WAVE 10's own
  pre-registration says so: *"reported SEPARATELY and never as the ceiling."*
* **ARM-H does not prune.**  `q_ripe_lead_n` stays a live, varying signal with
  its whole fanout intact; only the ~4-gate `poppable_n` comparator dies.  It is
  `qripe_reg`'s semantics **with no flop**, which is exactly what WAVE 10's
  cut-tree arm could not do.

> **REGISTERED QUOTING RULE, BEFORE ANY RESULT IS SEEN: the CEILING this wave
> quotes is the SMALLER of the two paired means, `min(Δ_T, Δ_H)`, because both
> are UPPER BOUNDS on what a real mechanism could buy and the smaller upper
> bound is the better bound.  BOTH are reported with their intervals.  Neither
> is discarded.**

---

## §2 THE MEASUREMENT

* `python3 sw/quartus_gate.py --seeds 5 [--retention]`, **seed set {1,2,3,4,5}**,
  **ONE driver** (`sw/run_wave14_g6.sh`, main tree, `--root` per arm), **both
  configurations**, **six sweeps / thirty fits**.  Map once per sweep, fit per
  seed, db cleaned by `quartus_gate` itself.
* This compile's **explicit purpose is measuring Fmax**, which is the condition
  the 2026-08-13 user ruling attaches to `--seeds N ≥ 5`.
* Paired on the seed; the ceiling is the **paired mean of the per-seed
  differences** with its **sd, standard error and 95 % CI** (WAVE 10's form).
* **Anatomy**, on the netlist each sweep leaves behind:
  `sw/sta_wave14_anatomy.tcl` reports the worst `ce → ce` arc, **STAGE 1
  (`* → s1q`)** and **STAGE 2 (`s1q → *`)**, the `$v30u_ce` register count, and
  whether the round trip is on the binding arc — with its positive controls.

---

## §3 THE BARS

| bar | what it demands |
|---|---|
| **P-1** | **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL, REPORTED FIRST.  A MISS VOIDS THE WAVE.**  `get_pins` **ONE PIN AT A TIME**, never `get_nodes`; a bulk `-through` printed beside it as a KNOWN-WRONG control (WAVE 10's fired on 14 of 34 draws); `\|d` and `\|asdata` both handled; an M10K port register may expose ZERO pins. |
| **P-2** | The probe SEVERS the path — **`check_core --core ucore --opcodes all --cases 0` FAILS on BOTH arms**, and the failure is reported as the evidence it is.  The SAME instrument on the BASE arm is the positive control and must read **169,000 / 169,000**. |
| **P-3** | The probe adds **NO REGISTER** and does **NOT subdivide STAGE 2**.  Demonstrated by (a) A&S and fitter register counts and the `$v30u_ce` netlist count, arm against base; (b) `ss_lint --core ucore` on each arm; (c) the worst `s1q → *` arc reported on BOTH arms.  ⚠ **If the arm's STAGE 2 is shorter for the wrong reason, this wave has rebuilt WAVE 10's mistake and MUST say so rather than quote the number.** |
| **P-4** | Paired A/B, **≥ 5 seeds, both configurations, one driver, one seed set**, and **`E11_no_build_stamp` true on every draw** — read at **DISTRIBUTION level** and per seed (⚠ NOT from inside a seed's `bars` dict, where the query returns nothing and reads as a miss). |
| **P-5** | The ceiling is reported **with its uncertainty**, beside WAVE 10's unsplit **+0.527 ns [−0.185, +1.239]** and the standing law that **a census ranks candidates but does not size them** (5.9× on `ucrom`, 5.3× on this mechanism). |
| **P-6** | **THE ENDGAME ARITHMETIC, WITH NUMBERS**: does *split + this ceiling* clear **32.0** on RETENTION (gap 0.85 MHz) and CONTROL (gap 1.47)?  Stated plainly, including whether a real behaviour-preserving mechanism of this size would finish the campaign. |
| **P-7** | **`git status --porcelain hdl/` shows NO tracked modification at start and at end.**  Every arm lives in a scratch worktree under `~/.cache/ucsimt-tmp/wave14/`; **NOTHING IS LANDED**; both arms are removed at the end. |

### 3.1 WHAT WOULD MAKE THIS WAVE'S ANSWER WORTHLESS, WRITTEN DOWN NOW

* A register count that moves on either arm (**P-3 fails outright**).
* `check_core` still passing on an arm (**the probe cut nothing**).
* A single false `E11` (**voids the pairing**, WAVE 13 N-4's precedent).
* Quoting one arm and suppressing the other (**forbidden by §1.1's rule**).
* Differencing any figure here against a **pre-WAVE-12** one (WAVE 12 §8).

---

## §4 WHAT IS EXPECTED, SO THAT BEING WRONG IS VISIBLE

No bar depends on these.  They are written down so that the result can
contradict them:

1. `Δ_H < Δ_T`, because ARM-T prunes and ARM-H does not.
2. Both fall **well short** of WAVE 10's cut-tree `+6.629 ns`, which included a
   third pipeline stage.
3. **A ceiling too small to close the 1.47 / 0.85 MHz gap is a VALID AND
   VALUABLE RESULT** — it would retire the last named mechanism, and that is
   worth knowing.  It will be reported as measured, not as hoped.

---

## §5 DISCIPLINE, DECLARED IN ADVANCE

* OFFLINE ONLY.  **NO BOARD.  NO FLASH.**  ⚠ A fabric confirmation has been
  owed since WAVE 7 and doubled at WAVE 12; **recorded, not this wave's to
  discharge.**
* Single-writer guard before every Quartus stage: `pgrep -x <binary>`, **ONE
  PATTERN PER CALL**; ⚠ `pgrep -f <script>` SELF-MATCHES the waiting shell.
* **BLOCK, DO NOT POLL.**
* ⚠ **NEVER `git stash`, `git checkout .`, `git reset --hard`** — 21
  pre-existing modified files are the USER'S OWN UNCOMMITTED WORK.
  `git checkout -- hdl/nec_test_ucore.qsf` **by that exact path** between
  Quartus runs; `git add` **BY EXPLICIT PATH ONLY**.
* ⚠ The driver carries **`set -u`, NOT `set -e`** — `quartus_gate` exits
  non-zero on RED and a RED arm is a registered expected outcome.
* `~/.cache/ucsimt-tmp`, never `/tmp`.
* **COMPARE CONTENT, NOT A DIGEST COMPUTED HERE.**  *A number with no artifact
  id is not quotable.*
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
