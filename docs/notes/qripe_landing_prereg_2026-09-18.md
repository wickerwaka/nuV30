# WAVE 16 — **LAND THE `q_ripe_lead_n` REFORMULATION (ARM-A `qripe_presel`).  PRE-REGISTRATION, COMMITTED BEFORE THE FIRST `hdl/` EDIT.**

**THIS IS A LANDING.**  It is the first of the two landings
`docs/notes/timing_campaign_handoff_2026-09-14.md` §5 names, and it is taken
first **because ARM-A is split-independent while ARM-B needs the cut.**

`git status --porcelain hdl/` (tracked) is **0** when this document is
committed, verified against the tree and not against recall.

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.

---

## §0 THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood.  A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

## §0.1 THE STANDING REQUIREMENT (verbatim, user ruling 2026-09-08)

> **"I don't want custom sdc rules, period."**

**Not re-opened.**  The NO-EXCEPTION build is the campaign's goal state; a
with-exception build is a control, never the objective.  **This wave does not
reach the goal state and says so in advance**: the phase split is not in the
tree, so R-3's no-exception sweep is expected RED, and R-3 is registered as a
RECORD, not a bar.

---

## §1 WHAT IS BEING LANDED, AND WHAT IT IS NOT

**ARM-A `qripe_presel`, exactly as `sw/testdata/wave15/arm_presel.diff` carries
it** for the four source files it touches:
`hdl/rtl/ucore/v30_core.sv`, `hdl/rtl/ucore/v30u_biu.sv`,
`hdl/rtl/ucore/v30u_eu.sv` and `sw/r7_lint.py`.
⚠ **The diff's `sw/testdata/receipts/*.jsonl` hunks are NOT applied** — those
are WAVE 15's own appended build receipts, not part of the mechanism.

### 1.1 THE MECHANISM, IN ONE SENTENCE

> **The BIU publishes the 1BL retire-lead level for each of the two things the
> EU can do to the queue this clock — pop, or not — and the EU picks the one it
> is doing.**

Both levels are pure functions of BIU registers; the EU's select is
`q_pop && q_ripe && !q_flush` — two of its own combinational outputs and a BIU
**register** port it already has.  It is the **same function against two
thresholds** ("at least one", "at least two") and **it adds no flop.**
Implemented by moving the pop's decrement to the end of the next-state block
with four compensated read sites (`occ` twice, `qi`, the publish), and keeping
the original predicate **verbatim** as an `ifndef SYNTHESIS` reference,
`$fatal`-checked every `ce`.

### 1.2 F7 IS WHAT IT MUST NOT BREAK

The value the EU's clocked step reads at `q_ripe_lead_n` must be the BIU's queue
level **for the clock the edge OPENS**, including the effect of the EU's own pop
on this clock.  Breaking it costs **181 goldens — `FA` 74 + `FB` 68 +
`INT.FB` 39**, all `ONE_BYTE_LOGIC` forms, `wait_retire_lead`'s only caller.
**Nothing here severs it**; it re-associates which side of the module boundary
the selection happens on.

### 1.3 WHAT THIS WAVE IS NOT

* It does **not** land the phase split, and therefore **does not** satisfy §0.1.
* It does **not** choose ARM-B away.  ARM-B is ARM-A **plus** a select taken off
  the `s1q` shadow; it is split-dependent, so it cannot be landed here, and
  swapping to it after the split lands remains open.
* It does **not** flash.  See §5.

---

## §2 ⚠⚠ THE GAP IN WAVE 15's EVIDENCE THAT THIS WAVE MUST CLOSE

**WAVE 15 ESTABLISHED EQUIVALENCE AND BENEFIT ON THE *SPLIT* TREE ONLY.**  Its
three binaries were base / ARM-A / ARM-B **with the split applied**
(`qripe_reform_results_2026-09-13.md`: base commit of every arm `850ef46559`).
On **today's UNSPLIT tree**:

* **its equivalence is NOT yet established** — R-1 re-establishes it in full,
  BEFORE side first, on the unedited tree;
* **its benefit is NOT yet measured** — R-3 measures it, for the record;
* **the cut-set lint may not even apply.**  Registered in advance, from the
  tree: `sw/cutset_lint.py` and `sw/phase_split_lint.py` **both exit 2,
  "COULD NOT RUN (the split is absent)"**, on the unedited tree, measured
  before this document was written.  **WAVE 15's X4 firing therefore cannot be
  reproduced here and its absence is not a repair.**  Reported in the results
  either way.

---

## §3 THE BARS

### R-1  **EQUIVALENCE ON THIS TREE — THE LANDING BAR, AND IT COMES FIRST.**

The BEFORE side is run on the **unedited** tree, so the A/B is real.  **Every
leg must be IDENTICAL base vs ARM-A, not merely passing.**

| leg | bar |
|---|---|
| `check_core --core ucore --opcodes all --cases 0` | **169,000 / 169,000** |
| the same at `--ce-div` **2, 3, 4, 8** | 169,000 each; **`--ce-div 1` REFUSED** |
| **the exact 181** | **`FA` 500/500 · `FB` 500/500 · `INT.FB` 200/200** |
| `8F.0` | 500/500 |
| the four HLT sweeps ⚠ **WITH `--waits 0/1/2/3`** | **97 · 93 · 45 · 44 = 279/283** |
| `v0.1-w1` / `-w3` | 1,200 each |
| `v0.1-w1 --opcodes EB` | 200 |
| the four `evt` cells | 200 · 1,200 · 200 · 1,200 |
| `v0.1-w1evt-biased` | 1,200 |
| `ulockstep --golden all --cases 50` | **17,350 ALL LOCKSTEP** |
| `ghost_launch_law score` | 200/200 |
| `check_boot --core ucore` and `400` | **220** and **400** MATCH |
| `check_ab_sim --core ucore` | **187** MATCH |
| `sm3_s16_score --core ucore` | **1,320 / 1,371** |
| `r7_lint` | PASS |
| `demux_off_gate` | PASS |
| `test_artifact` | **45 / 45** |
| `chainflat_relocation_check` | **9 / 9** |
| `ucrom_mif_check` | PASS |
| `chain_lfsr_gate` | PASS, **four signatures BYTE-IDENTICAL** |
| `fz2_replay` | **scored content IDENTICAL, compared FIELD BY FIELD BY NAME** — never a digest computed here, and **the ROW COUNT printed before the verdict** |
| `ss_lint --core ucore` | exit 0, census IDENTICAL (see R-4) |
| `test_quartus_gate` | as measured, IDENTICAL both sides |
| `cutset_lint`, `phase_split_lint` | as measured (§2), IDENTICAL both sides |

⚠ **THE STANDING TABLES DISAGREE WITH THIS TREE AND THE DISAGREEMENTS ARE
REGISTERED NOW, MEASURED BEFORE THIS DOCUMENT WAS COMMITTED, SO THAT NEITHER
CAN BE MISTAKEN FOR A FAILURE LATER:**

1. `standing_gates.md`'s `ss_lint` row is **stale** at 226 / 214 / `SS_VERSION`
   0x8D.  **This tree reads `SS_COUNT` 232 / 228 architectural flops / 0
   UNMAPPED / 3 whitelist entries, `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8.**
   ⚠ **The brief's "232 / 229" is the SPLIT tree's figure** — the split adds
   `s1q` as a fourth whitelisted DERIVED flop.  **228 / 3 is the unsplit
   tree's, and it is what R-4 is scored against.**
2. `test_quartus_gate` reads **287 / 287** on this tree with an `hdl/db` on
   disk.  The brief registered **286**; the tree says 287.  **Measured,
   reported, and not treated as a failure either way.**
3. `cutset_lint` and `phase_split_lint` **exit 2, COULD NOT RUN** (§2).

**A stale row is never treated as a failure, and a disagreement is reported as
a disagreement.**

### R-2  **NO TIMING REGRESSION, WITH THE EXCEPTION** (the tree's current SDC)

`sw/quartus_gate.py --seeds 5`, **BOTH configurations**, every draw **PASS
E1-E5**.  `worst-of-5@seeds{1,2,3,4,5}` reported against **WAVE 12's stamp-free
CONTROL 40.62 / RETENTION 41.63**.  **A regression fails R-2.**

### R-3  **ARM-A's STANDALONE BENEFIT, FOR THE RECORD — NOT A PASS/FAIL BAR**

The **no-exception** sweep, `--seeds 5`, **both configurations, base and ARM-A,
same driver and the same seed set {1,2,3,4,5}.**  **RED IS EXPECTED** — the
split is not in the tree.  The no-exception tree is today's `hdl/` with WAVE 9
edit (c) (`bacf7f9fd9`) applied to `hdl/nec_test.sdc` **and nothing else**, in a
scratch worktree; **it is never landed.**

Reported: the paired per-seed Δ, the paired mean with a 95 % CI from a
**tabulated** t (df = 4, t = 2.776), and `worst-of-5` both arms — compared to
ARM-A's **on-split** benefit of **+2.847 ns CONTROL / +1.429 ns RETENTION**.

⚠ **A CANDIDATE'S VALUE IS NOT A PROPERTY OF THE CANDIDATE** — WAVE 14 measured
the same one-line edit at **0.527 ns** on one tree and **6.629 ns** on another —
**so a different number here is a FINDING, not an error.**
⚠ The base-noexc leg is also a **free control** against WAVE 13's
`w13-unsplit-noexc` **27.78 / 27.01**, whose `hdl/` differs from this tree's by
the SDC alone (`git diff d3aa3900c5 HEAD -- hdl/` touches `nec_test.sdc` and
nothing else — measured).

### R-4  **REGISTER ACCOUNTING**

`ss_lint --core ucore` exits 0; **NO FLOP ADDED** — ARM-A is flopless, and the
authority is the compiler's own per-entity count (`v30u_eu` **1,326** registers
at WAVE 15, `v30u_biu` **434**).  `SS_COUNT` / `SS_VERSION` / `SS_TAG` and the
flop census **UNCHANGED at 232 / 0x8F / 0x8FE8 / 228 flops**.  **Any movement is
a finding and must be explained, not absorbed.**

### R-5  **THE `ifndef SYNTHESIS` REFERENCE PREDICATE IS PRESERVED AND NON-VACUOUS**

The original expression kept **verbatim**, `$fatal`-checked every `ce`, and
**demonstrated firing** when one term is perturbed — both clauses:
(1) the identity `pop_eff ? lead1 : lead0 == reference`, and
(2) `pop_eff == (q_pop && q_ripe && !q_flush)`.
**This is the mechanism's own falsifier and it is what makes the landing safe.**
⚠ WAVE 15 §2.1 recorded that deleting the flush's `pop_eff = 1'b0` **did NOT
fire** — the pop/flush coincidence is not reached by the golden population.
**That is re-measured here and reported as measured, not restated.**

### R-6  **`E11` TRUE ON EVERY DRAW**

⚠ Recorded as `E11_no_build_stamp` at **DISTRIBUTION** level and read from each
per-seed receipt file — **not** from a seed's `bars` dict, where a query returns
nothing and reads as a miss.  ⚠ And the per-seed read requires the scorer's CWD
to be the sweep's own tree (WAVE 15 §4).

### R-7  **THE REVERT CONDITION**

**If any leg of R-1 moves, or R-2 regresses, THE LANDING DOES NOT HAPPEN:
revert, report, keep both documents.  Do not soften a bar to make a landing
possible.**  **R-3 being RED is NOT a revert condition.**

---

## §4 WHAT IS EXPECTED, WRITTEN DOWN SO THAT BEING WRONG IS VISIBLE

1. **R-1 passes identically.**  The mechanism is behaviour-preserving by
   construction and WAVE 15 measured it so on a tree whose `hdl/rtl/ucore/`
   differs from this one only by the split.  If it does not, R-7 fires.
2. **R-2 does not regress.**  The with-exception build's binding cone is the
   microcode front end (WAVE 7), not this round trip, so the prediction is
   **Δ ≈ 0** and any large movement in either direction is a finding.
3. **R-3 is RED on both configurations** — the unsplit no-exception baseline is
   27.78 / 27.01 and the bar is 32.0, a gap of ~3.5 / ~4.5 MHz that one
   mechanism worth ~1-3 ns cannot close.
4. **R-3's Δ will NOT equal +2.847 / +1.429.**  Law 5 says a candidate's value
   is not a property of the candidate.  A census-shaped guess is not offered;
   **only the built A/B sizes it.**
5. **The design does not shrink** — ARM-A duplicates a 4-bit compare.  WAVE 15
   measured BIU 1,112 → 1,151 and EU 4,969 → 5,075 combinational ALUTs.

---

## §5 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
  ⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND WAS DOUBLED AT
  WAVE 12.  THIS LANDING MAKES IT A THIRD STRUCTURAL CHANGE.  It is RECORDED
  here and it is not this wave's to discharge.  A fabric figure taken on
  FLASH #21 or earlier may not be quoted against this tree.**
* No Codex.  No nested subagent.
* ⚠ **BLOCK, DO NOT POLL** — one foreground
  `until ! pgrep -x quartus_fit >/dev/null 2>&1; do sleep 60; done` with a large
  timeout.  WAVE 13 stalled by polling.
* Single-writer guard by **`pgrep -x`, EXACT BINARY NAME, ONE PATTERN PER
  CALL**; ⚠ `pgrep -f <script>` self-matches the waiting shell and is never
  used.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` ARE NEVER USED** —
  **21 pre-existing modified files are the USER'S OWN UNCOMMITTED WORK** and
  WAVE 12 swept them once.  `hdl/nec_test_ucore.qsf` is restored by
  `git checkout -- hdl/nec_test_ucore.qsf`, **that exact path**, around every
  Quartus run.  **`git add` BY EXPLICIT PATH ONLY** (WAVE 7 swept the user's
  in-progress rename into its own commit).
* ⚠ A driver carries **`set -u`, NEVER `set -e`** — `quartus_gate` exits
  non-zero on a RED verdict and R-3 is registered to draw RED.
* ⚠ **`fz2_replay` IS STRUCTURALLY VACUOUS IN A GIT WORKTREE**
  (`.gitignore:9`) and **exits 0 over zero rows.**  R-1's `fz2_replay` legs are
  therefore run **in the main tree, where the captures exist**, and the **ROW
  COUNT is printed before the verdict.**
* `~/.cache/ucsimt-tmp/` for every intermediate; **nothing in `/tmp`.**
* ⚠ **A CENSUS DOES NOT SIZE A CANDIDATE IN EITHER DIRECTION** — five for five
  across this campaign.  **Only a built A/B sizes anything.**
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  Ten instruments in this
  campaign have returned confident, wrong answers
  (`timing_campaign_handoff_2026-09-14.md` §9).  **Assume the next one is wrong
  until its control says otherwise.**
* Truthful commit messages.  **A number with no artifact id is not quotable.**
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
