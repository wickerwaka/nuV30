# WAVE 15 — **THE CHOICE, AND THE BARS.  COMMITTED BEFORE THE FIRST `hdl/` EDIT AND BEFORE THE FIRST QUARTUS STAGE.**

Part one is `docs/notes/qripe_reform_derivation_2026-09-13.md` (`96dd1030cb`),
committed before this and naming no winner.  **This document chooses, gives the
reason, and registers Q-1 … Q-8.  Nothing under `hdl/` has been written when it
is committed** — `git status --porcelain hdl/` (tracked) is **0**.

**THIS WAVE FINDS AND SIZES A MECHANISM.  IT LANDS NOTHING.**
**OFFLINE ONLY — NO BOARD, NO FLASH, NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.

---

## §1 THE CHOICE — **C1, WITH C5 AS ITS IMPLEMENTATION.  ARM-A = `qripe_presel`.**

> ### **THE BIU PUBLISHES THE RIPE-LEAD LEVEL FOR EACH OF THE TWO THINGS THE EU CAN DO TO THE QUEUE THIS CLOCK — POP, OR NOT — AND THE EU PICKS THE ONE IT IS DOING.**

Both levels are **pure functions of BIU registers** (and of `q_flush`, which is
not on the binding arc, §2.2 of part one).  The EU selects with
`q_pop && q_ripe && !q_flush`: `q_pop` and `q_flush` are its **own**
combinational outputs and `q_ripe` is a BIU **register** port it already has.
The EU's pop never leaves the EU on this path.

**WHY C1 AND NOT THE OTHERS:**

* **It is what §2.1's partition permits and nothing more.**  The dependence on
  the EU is ONE BIT entering at ONE place, so ONE extra published level covers
  it exactly.  A large fitted table, a many-cased rule, or a per-opcode special
  case would be a signal of misunderstanding; this is a **threshold change**:
  `lead0` asks "is there at least one", `lead1` asks "is there at least two",
  of the SAME pure-register quantity.  A 1978 die has no unit boundary to cross
  and would compute both comparisons off the queue counter as a matter of
  course.
* **It attacks the carrier that was MEASURED to bind** — `bnd_fire → q_pop →
  q_cnt → q_ripe_lead_n`, on 200 of 200 binding paths of both configurations of
  the split tree.
* **It adds no flop**, so no pipeline stage can be subdivided and WAVE 10's
  over-answer cannot recur (WAVE 14 §3.1's argument, inherited).
* **It is split-independent.**  It is scored on the split tree because that is
  where the arc binds, but the edit references nothing the split introduced.
* **C1′ is rejected** because it cannot be *measured*: leaving the mux in the
  BIU keeps `q_ripe_lead_n` on the arc by name and Q-3 could not distinguish a
  real win from a re-labelling.
* **C2 is not chosen now** — see §4, where it is registered as a conditional
  second arm so that it cannot be chosen after a result is seen.
* **C3, C4, C6 are refuted** in part one §3, on simplicity, on the 181 goldens
  and on the spec respectively.  **C7 is forbidden by the 2026-09-08 user
  ruling and is not re-opened.**

### 1.1 THE EDIT, DECLARED IN ADVANCE

**`hdl/rtl/ucore/v30u_biu.sv`** — five compensated sites and one new publish:

1. line 1919, the pop: `q_cnt = q_cnt - 4'd1;` → `pop_eff = 1'b1;`
   (the `q_head` advance is UNCHANGED).
2. line 2064, the flush: add `pop_eff = 1'b0;` beside `q_cnt = 4'd0;`.
3. lines 2142 and 2305, `occ`: subtract `pop_eff`.
4. line 2173, `qi`: subtract `pop_eff`.
5. at the END of the next-state block: `q_cnt_np = q_cnt;` then
   `if (pop_eff) q_cnt = q_cnt - 4'd1;` — so **every downstream consumer of
   `q_cnt`, the register commit and `+utrace` included, is byte-for-byte
   unchanged in VALUE**, and `q_cnt_np` is the pop-free basis.
6. THE EU CONTRACT block: `q_ripe_lead_n` → `q_ripe_lead_n0` / `q_ripe_lead_n1`,
   both off `q_cnt_np`, `grn_n`, `grn_ttl`.

**`hdl/rtl/ucore/v30u_eu.sv`** — the port `q_ripe_lead_n` becomes the two ports
`q_ripe_lead_n0` / `q_ripe_lead_n1`, and an internal
`wire q_ripe_lead_n = (q_pop && q_ripe && !q_flush) ? q_ripe_lead_n1 :
q_ripe_lead_n0;`  **so both consumer sites
(`v30u_eu_step.svh`, `v30u_eu_arm_decode2.svh`) are BYTE-UNCHANGED.**

**`hdl/rtl/ucore/v30_core.sv`** — the two wires and the two port maps.

**THE IDENTITY IS ASSERTED IN THE RTL, `ifndef SYNTHESIS`, EVERY CLOCK** — the
original expression is kept VERBATIM as a reference and `$fatal`s if the
published pair composed with `pop_eff` ever differs from it, and a second
clause `$fatal`s if `pop_eff != (q_pop && q_ripe && !q_flush)` (which is what
makes the EU's local select formula sound).  This is the `V30_MUXED_AD`
precedent (`v30_core.sv`'s nine-way mux, kept as a sim-only reference compared
every fabric clock).  **Non-vacuity is demonstrated by perturbing one term.**

---

## §2 THE BARS, REGISTERED

| bar | what it demands |
|---|---|
| **Q-1** | the spec derivation and the candidate enumeration are COMMITTED BEFORE a candidate is chosen — `96dd1030cb`, and this document is the choice |
| **Q-2** | **EQUIVALENCE, IN FULL, BEFORE ANY TIMING FIGURE IS QUOTED** (§3) |
| **Q-3** | **THE ROUND TRIP IS MEASURABLY GONE**: `q_ripe_lead_n*` **BY NAME** on **0 of 200** POP-A paths of the arm, against **200 of 200** on the base measured in the SAME run.  The base reading is the mandatory positive control — a classifier that cannot say YES cannot be trusted when it says NO |
| **Q-4** | paired A/B, ≥ 5 seeds, both configurations, ONE driver, ONE seed set {1,2,3,4,5}, **`E11` true on every draw**, read at DISTRIBUTION level and from each per-seed receipt, never from a seed's `bars` dict |
| **Q-5** | the recovered fraction stated against WAVE 14's ceiling (+6.293 CONTROL / +4.688 RETENTION) and the gap (1.506 / 0.855); `worst-of-5` on both arms; **does it close CONTROL?  does it close RETENTION?** |
| **Q-6** | `ss_lint` exits 0; **any added flop is named, counted and justified**; `SS_COUNT` / `SS_VERSION` / `SS_TAG` movement reported.  ⚠ ARM-A is registered to add **NO** flop, so any movement here is a MISS |
| **Q-7** | `git status --porcelain hdl/` (tracked) shows **0** at start and at end.  **NOTHING IS LANDED** |
| **Q-8** | if no legal mechanism is found, SAY SO.  **Do not manufacture one and do not weaken F7** |

### 2.1 THE NUMERIC BARS, FIXED NOW

* **Q-3**: arm POP-A `q_ripe_lead_n*` count **= 0**; base **= 200**.  Anything
  between is reported as measured and the mechanism is **not** claimed to have
  removed the round trip.
* **Q-5, the primary point**: the paired mean Δ (base T_min − arm T_min) is
  quoted with a 95 % CI from a **tabulated** t (df = 4, t = 2.776).  The
  **recovered fraction** is Δ / 6.293 (CONTROL) and Δ / 4.688 (RETENTION).
  **CLOSES** means the arm's **`worst-of-5` T_min ≤ 31.250 ns** (≥ 32.0 MHz),
  no exception of any kind — the same bar WAVE 14 used.
* ⚠ **`worst-of-5` IS THE QUOTED FIGURE, NEVER A BEST DRAW.**
  `standing_gates.md` §A governs; one green build is not closure.

### 2.2 WHAT IS EXPECTED, SO THAT BEING WRONG IS VISIBLE

1. The excursion the arm deletes is **3 LUT levels / 1.777 ns** of the binding
   path and is replaced by 1 AND + 1 MUX in the EU, so a **census-shaped**
   guess is ~1.2 ns.  ⚠ **A CENSUS DOES NOT SIZE A CANDIDATE IN EITHER
   DIRECTION** — WAVE 14 measured this same mechanism's census **2.3× / 1.7×
   LOW** and WAVES 8 and 10 measured two others 5.9× and 5.3× HIGH.  **The
   number above is written down so that it can be scored as wrong, not as a
   prediction.**
2. **Expected**: RETENTION (gap 0.855 ns) closes and CONTROL (gap 1.506 ns) is
   marginal.  Recorded now so the outcome cannot be re-described.
3. **Expected**: the design does not shrink.  Both WAVE 14 arms grew the core's
   combinational ALUTs; ARM-A duplicates a 4-bit compare and should too.

---

## §3 Q-2 — THE EQUIVALENCE LADDER, NAMED IN ADVANCE.  **EVERY LEG RUNS BEFORE A SINGLE NANOSECOND IS QUOTED.**

Run in the arm's own worktree, on that arm's own freshly built and separately
receipted binaries, with the BASE worktree as the positive control on every leg
that has one.

| leg | bar |
|---|---|
| `check_core --core ucore --opcodes all --cases 0` | **169,000 / 169,000**, exit 0 — **and the 181 goldens of part one §1.5 named and shown to pass** (`FA` 500/500, `FB` 500/500, `INT.FB` 200/200) |
| the same at `--ce-div 2, 3, 4, 8` | 169,000 each; `--ce-div 1` **refused** (exit 2) |
| `chain_lfsr_gate` | PASS, **four signatures BYTE-IDENTICAL** to the base's |
| `fz2_replay` | scored content **IDENTICAL** — **the named fields compared directly, never a digest computed here** |
| `ulockstep --golden all --cases 50` | **17,350 ALL LOCKSTEP** |
| the four HLT sweeps | **97 · 93 · 45 · 44 = 279/283** (`--waits 1/2/3` on the w1/w2/w3 suites) |
| `check_boot --core ucore` | **220** and **400** |
| `check_ab_sim --core ucore` | **187** |
| `sm3_s16_score --core ucore` | **1,320 / 1,371** |
| `r7_lint` | PASS |
| `demux_off_gate` | PASS |
| `test_artifact` | **45 / 45** |
| `test_quartus_gate` | **287 / 287** |
| `ucrom_mif_check` | PASS |
| `ss_lint --core ucore` | exit 0, census IDENTICAL to the base's |
| `phase_split_lint`, `cutset_lint` | PASS (the split tree's own lints) |
| **the RTL identity assertion** | no `$fatal` on any of the above, and **non-vacuity demonstrated** by perturbing one term |

⚠ `standing_gates.md`'s `ss_lint` row is **KNOWN STALE** (it reads 226 / 214 /
0x8D against the split tree's 232 / 229 / 0x8F).  **Measure, report the
disagreement, and never treat a stale row as a failure.**

**A MECHANISM THAT FAILS EQUIVALENCE IS REFUTED, NOT "NEARLY THERE".**

---

## §4 THE CONDITIONAL SECOND ARM, REGISTERED NOW SO IT CANNOT BE CHOSEN LATER

**ARM-B = C2 = ARM-A + the select taken off the `s1q` shadow.**  It is built
**iff** ARM-A passes Q-2 in full **and** fails to close BOTH configurations at
Q-5, **and** the Quartus budget allows it.  Its cost is declared in advance:

* **ONE FLOP** — `s1q` 778 → 779 bits — which Q-6 permits only because it is
  declared here, before it is built.  `SS_COUNT` must **not** move: `s1q` is
  derived state and is deliberately not save-state mapped
  (`v30u_eu.sv`'s THE PHASE SPLIT block).
* one membership entry in the pack **and** the unpack, which
  `sw/phase_split_lint.py` checks character for character.
* it is **SPLIT-DEPENDENT** and therefore meaningless on a tree without the cut.
* its free falsifier already exists: the split's own premise assertion
  (`v30u_eu.sv:4206`) `$fatal`s if the sampled bit is not constant across the
  CPU cycle.

If ARM-A closes both, ARM-B is **not** built and that is recorded.
If ARM-A fails Q-2, **the wave reports C0** — no legal mechanism found — and
ARM-B is not used to rescue it.

---

## §5 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.**  ⚠ A fabric confirmation has been
  owed since WAVE 7 and was doubled at WAVE 12; this wave **records** it and
  **does not discharge it**, and lands nothing, so it adds no new debt.
* Every arm lives in a scratch git worktree under `~/.cache/ucsimt-tmp/wave15/`.
  **The main tree's `hdl/` is never written.**
* ONE driver for every sweep, seed set {1,2,3,4,5}, both configurations.
* Single-writer guard by **`pgrep -x`, EXACT BINARY NAME, ONE PATTERN PER
  CALL**; `pgrep -f <script>` self-matches and is never used.  **The waits
  BLOCK; they do not poll a turn.**
* The driver carries **`set -u`, NEVER `set -e`** — `quartus_gate` exits
  non-zero on RED and the base arm is expected to draw RED.
* `hdl/nec_test_ucore.qsf` restored by `git checkout -- <that exact path>`
  around every Quartus run, in the arm's own worktree.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` ARE NEVER USED** —
  21 pre-existing modified files are the user's own uncommitted work.
  `git add` **BY EXPLICIT PATH ONLY**.
* `~/.cache/ucsimt-tmp/wave15/` for every intermediate; nothing in `/tmp`.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  Nine instruments in this
  campaign have produced confident, wrong, vacuous results.
* **A number with no artifact id is not quotable.**
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
