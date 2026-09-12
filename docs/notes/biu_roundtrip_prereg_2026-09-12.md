# WAVE 10 — **RESOLVE THE CONTRADICTION, THEN SIZE THE ROUND TRIP.**  THE PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST QUARTUS STAGE OF THIS WAVE.**
**MEASUREMENT ONLY.  NOTHING IS LANDED IN THE CORE.**  OFFLINE ONLY — no board,
no flash, no bitstream.  `git status --porcelain hdl/` carries **0 tracked
modifications** at the start of this wave and must carry 0 at the end (K-6).

## §0 THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood.  A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

## §0.1 THE STANDING REQUIREMENT (USER RULING 2026-09-08, verbatim)

> **"I don't want custom sdc rules, period."**

The NO-EXCEPTION configuration is the GOAL STATE and every figure this wave
takes is a no-exception figure.  It is not re-opened.

**SCOREBOARD AS THIS WAVE OPENS.**  Today's tree is WAVE 7's (uncut, flattened):
no-exception `worst-of-5` **CONTROL 28.32 MHz / RETENTION 28.90 MHz** against
**32.0**.  WAVE 9's split measured 30.06 / 31.17 and **was REVERTED** —
`cbb556a097` — so those two figures describe a tree that does not exist today.

---

## §1 THE CONTRADICTION

| | WAVE 8 §4 | WAVE 9 §5.4 |
|---|---|---|
| the round trip `q_cnt → q_ripe_lead_n` | **0.000 ns on 0 of 1,200 CONTROL paths** | **200 of 200 top paths**, mean span **2.786 ns** |
| its own positive control | PASSED | PASSED (after repair) |
| tree | UNCUT (WAVE 7 flattened) | CUT (WAVE 9's split) |
| configuration / draws | 3 CONTROL + 1 RETENTION | 1 CONTROL |

⚠ WAVE 8's single RETENTION draw carried it on **400/400 at 1.894 ns** while all
three of its CONTROL draws read zero.  With n=1 it could not separate
configuration from draw, and it said so.

---

## §2 K-2 — **THE PREDICATE RECONCILIATION.  ALREADY TAKEN, OFFLINE, AND
REGISTERED HERE AS TAKEN.**

`sw/biu_predicate_reconcile.py` (committed at `4f95708213`, before this file) is
a re-analysis of **both waves' own committed artifacts** with no Quartus in the
loop, so it is deterministic and reproducible from the tree.  It was run before
this pre-registration was written and **its result is stated here rather than
predicted**, because predicting the outcome of a deterministic re-read of
committed bytes would be theatre.  The result is in §7 of the results document
and its headline is:

> **THE TWO INSTRUMENTS ASK THE SAME QUESTION ABOUT WHAT TO LOOK FOR AND A
> DIFFERENT QUESTION ABOUT WHERE TO LOOK — AND THE DIFFERENCE IN WHERE IS NOT
> THE RESOLUTION.**

The four axes, each measured:

| axis | same question? | how it was established |
|---|---|---|
| **AX-1** the MATCH | **YES** | both predicates select the **identical node set on every one of 109,876 arrival points** of both waves' committed artifacts, 0 disagreements |
| **AX-2** the SECTION (data-only vs all points) | **YES on this design** | 0 BIU nodes anywhere in a clock section |
| **AX-3** the POPULATION | **NO** | WAVE 8 `-npaths 400 -nworst 1` = 400 **distinct** endpoint pairs; WAVE 9 `-npaths 200` = top-200 by slack, no diversity constraint |
| **AX-4** the SPAN CONVENTION | **NO** | WAVE 8 includes the interconnect INTO the first BIU node, WAVE 9 does not — worth **+0.274 … +0.300 ns**, and it cannot turn 0.000 into 2.786 |

⚠ **AND AX-3 IS NOT THE RESOLUTION**: the WORST path belongs to both populations
by construction, and on all three of WAVE 8's CONTROL draws it carries **0** BIU
nodes while WAVE 9's carries **8**.

**WHAT IS LEFT IS THREE CONFOUNDS IN THE DESIGN, NOT IN THE QUESTION: the TREE,
the CONFIGURATION and the DRAW.  §3 measures all three with ONE instrument.**

---

## §3 K-3 — **THE RE-MEASUREMENT.  ONE INSTRUMENT, FOUR CELLS.**

`sw/sta_biu_roundtrip.tcl` asks **both** population questions in **one** STA
session and reports **both** span conventions, so a draw cannot answer one and
not the other.  No-exception configuration on every draw.

| cell | tree | configuration | seeds |
|---|---|---|---:|
| **U-C** | UNCUT — today's HEAD `de3fd2896a` | CONTROL | 1,2,3,4,5 |
| **U-R** | UNCUT | RETENTION | 1,2,3 |
| **C-C** | CUT — WAVE 9's `bacf7f9fd9`, in a scratch worktree | CONTROL | 1,2,3 |
| **C-R** | CUT | RETENTION | 1,2,3 |

U-C takes five seeds because it doubles as the **REF arm of the ceiling probe**
(§4).  The cut tree is measured in a **scratch git worktree** and never in the
main tree (K-6).  ⚠ `bacf7f9fd9` already carries the multicycle deletion, so the
driver patches **nothing** there — and prints that it patched nothing, because a
silent no-op and a silent patch must not look alike.

### 3.1 THE VERDICT MAP — **REGISTERED BEFORE THE DATA, SO IT CANNOT BE CHOSEN
AFTER IT**

Let `k(cell)` be the number of that cell's draws on which **POPULATION A** (the
top-N, WAVE 9's question) carries the round trip on **≥ 90 %** of its paths.

* **P-1  REPRODUCIBILITY OF WAVE 8.**  `k(U-C) ≤ 1 of 5`.  A miss means WAVE 8
  §4 does not reproduce and the whole comparison is void.
* **P-2  REPRODUCIBILITY OF WAVE 9.**  `k(C-C) ≥ 2 of 3`.  A miss means WAVE 9
  §5.4 does not reproduce.
* **P-3  THE CONFIGURATION AXIS.**  `k(U-R) ≥ 2 of 3` — i.e. WAVE 8's single
  retention draw was not a fluke.
* **P-4  ANY CELL THAT SPLITS IS A DRAW EFFECT.**  A cell reading neither 0 of n
  nor n of n is reported as **A PLACEMENT OUTCOME**, and **no tree or
  configuration attribution may be made for that cell.**  This clause exists
  because WAVE 5 saw exactly that shape (2 of 4) and WAVE 8 saw all-or-nothing.
* **P-5  THE POPULATION AXIS, MEASURED NOT ARGUED.**  Within each draw,
  POPULATION A and POPULATION B are compared.  If they disagree in ANY cell,
  **AX-3 is a live difference of question and is reported as one**; if they
  agree everywhere, AX-3 is registered as **harmless on this design**.

**AN UNRESOLVED CONTRADICTION REPORTED AS UNRESOLVED IS A VALID OUTCOME OF THIS
WAVE.  A CONTRADICTION EXPLAINED AWAY AFTER THE FACT IS NOT.**

---

## §4 K-4 / K-5 — **THE CEILING PROBE.  SIZE IT, BECAUSE A CENSUS CANNOT.**

WAVE 8 §7.6 established the rule the hard way: its census attributed **3.805 ns**
to `ucrom` and building the substitution out recovered **0.644** — **5.9×
overstated**, because a per-name ns figure includes the interconnect INTO those
cells and interconnect is INHERITED by whatever replaces them.
**A CENSUS RANKS CANDIDATES; IT DOES NOT SIZE THEM.**  WAVE 9's **2.786 ns** is
therefore a RANKING and this wave must measure the SIZE.

### 4.1 ⚠⚠ THE ARM IS BEHAVIOUR-BREAKING BY CONSTRUCTION

**`qripe_reg`** registers `q_ripe_lead_n` inside `v30u_biu.sv`, severing
`q_cnt → poppable_n → q_ripe_lead_n → the EU chain`.  The EU is contracted (F7)
to read the BIU's NEXT level here; the arm hands it the PREVIOUS one.

* **NO EQUIVALENCE IS CLAIMED FOR IT.**
* **IT IS NOT PROPOSED AS A DESIGN.**  A real mechanism is a later wave's
  problem.
* **IT IS NEVER LANDED.**  It lives in a scratch git worktree.
* **IT ANSWERS EXACTLY ONE QUESTION**: *what is the most this mechanism could
  ever be worth?*

**`qripe_tie`** (secondary, reported SEPARATELY and never as the ceiling) ties
the output and lets the compiler prune the cone — an upper bound that is
optimistic by construction because it deletes area no real mechanism gets to
delete.

### 4.2 THE BARS

* **K-4a  `check_core --core ucore --opcodes all --cases 0` MUST FAIL on the
  arm, and the failure is REPORTED, not excused.**  A probe that still passes
  has not cut anything and its ceiling is **VOID**.
* **PC-C1  THE POSITIVE CONTROL, REPORTED BEFORE ANY DELTA.**  The REF arm is
  the design itself, so its worst no-exception `ce → ce` arc, meaned over its 5
  draws, must land within **±15 %** of WAVE 8 §3.1's **32.969 ns** (that wave's
  4-draw mean of the same tree, same configuration, same no-exception SDC).
  **A miss voids the ceiling.**
* **PC-C2  THE DELETION REACHED THE COMPILER.**  `sta_truefmax_probe.tcl` runs
  beside the census on every draw and the core `SAME` class must read
  **k = 1.0**.  A draw whose `SAME` still reads 2.0 may not be quoted.
* **METHOD**: two arms compiled IDENTICALLY, **in the full design**, map-once /
  fit-once, **5 seeds each**, same driver, same SDC patch, same instrument.
  ⚠ The round trip LEAVES `v30u_eu`, so WAVE 6/8's `v30u_eu`-only standalone
  project **cannot contain it** (`q_ripe_lead_n` is an input port there and
  ports are false-pathed).  Compiling in the full design is therefore not a
  weakening of that method but the only form of it that can see this arc — and
  it needs **no out-of-context transfer at all.**

### 4.3 THE REGISTERED PREDICTION

* **P-6**  `Δ = mean(REF worst arc) − mean(ARM worst arc)` is **< 2.786 ns**.
  *Reason*: WAVE 8's 5.9× rule.  **If `Δ ≥ 2.786` the census did NOT overstate
  here, and that is itself a finding and is reported as one.**
* **P-7**  The ceiling is quoted with an uncertainty derived from the two arms'
  own per-seed spreads, **and WAVE 8's 5.9 × census overstatement is quoted
  beside it** (K-5).  A point estimate with no spread is not quotable.
* **P-8**  Whether the round trip ALONE clears 32.0 on the uncut tree is decided
  by `mean(REF arc) − Δ` against the **31.250 ns** budget, and reported whatever
  the answer.  WAVE 9's own estimate said **~31.5 MHz — short**.

---

## §5 K-7 — **THE ENDGAME ARITHMETIC, TO BE STATED WITH ITS NUMBERS**

Whatever the measurements say, the results document states:

1. what the round trip is worth (measured ceiling, with uncertainty);
2. whether **round trip alone** clears 32.0 on the uncut tree;
3. whether **round trip + the phase split** clears it — the split's own ceiling
   on the cut tree measured `max(STAGE 1 20.235, STAGE 2 27.922) = 27.922 ns`
   = **34.99 MHz**, and it is currently blocked BY this round trip;
4. ⚠ carrying **THE CUTTING PENALTY, A CONSTANT ~15.2 ns** — WAVE 4 **+15.295**
   on a 43.485 ns arc, WAVE 9 **+15.188** on a 32.969 ns arc, the same to
   **0.11 ns**.  Any arithmetic involving a FUTURE cut carries it.

---

## §6 THE BARS, AS REGISTERED

| bar | statement |
|---|---|
| **K-1** | **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL, REPORTED FIRST.  A MISS VOIDS THE WAVE.**  `sta_biu_roundtrip.tcl` PC-W1..PC-W5; `biu_predicate_reconcile.py` PC-R0..PC-R2.  Every `-through` is ONE PIN at a time (`get_pins`, never `get_nodes`) with the bulk form printed beside it as the known-wrong control.  **PC-W5 handles BOTH destination pin forms (`\|d` AND `\|asdata`)** — WAVE 9 §5.1's control failed on exactly that. |
| **K-2** | The predicate reconciliation is stated explicitly — what each classifier asked and whether they are the same question.  **This is the wave's headline whatever the answer.** |
| **K-3** | Predicates match ⇒ ONE instrument across both trees and both configurations, ≥ 3 draws each.  §3. |
| **K-4** | The ceiling probe is labelled BEHAVIOUR-BREAKING everywhere it appears, equivalence is NOT claimed, and `check_core` is reported as FAILING on it. |
| **K-5** | The size carries its uncertainty and quotes WAVE 8's 5.9× census overstatement beside it. |
| **K-6** | `git status --porcelain hdl/` shows NO tracked modification at start and at end.  Probe arms live in a scratch worktree.  **NOTHING IS LANDED.** |
| **K-7** | The endgame arithmetic of §5 is stated with its numbers. |

## §6.1 DISCIPLINE, DECLARED

* OFFLINE ONLY.  **NO BOARD.  NO FLASH.**  ⚠ **A FABRIC CONFIRMATION HAS BEEN
  OWED SINCE WAVE 7** (`chainflat_landing_results_2026-09-09.md`: the EU's
  decode changed and a fabric figure taken on FLASH #21 or earlier may not be
  quoted against this tree).  **IT IS NOT THIS WAVE'S TO DISCHARGE AND IT IS
  RECORDED HERE AS STILL OWED.**
* No Codex.  No nested subagents.
* Single-writer guard (`pgrep -x`, EXACT binary name) before every Quartus stage.
* `hdl/nec_test_ucore.qsf` is `git checkout --`'d after every Quartus stage.
* `git add` BY EXPLICIT PATH ONLY — ~18 pre-existing modified files in the
  working tree are NOT this wave's and are left alone.
* `~/.cache/ucsimt-tmp/`, never `/tmp`.
* **COMPARE CONTENT, NOT A DIGEST COMPUTED BY THE COMPARER.**  Every count in
  §2 is a count of lines in a named committed file.
* No figure in this wave is a receipt, a gate or a design Fmax.
  `standing_gates.md` §A governs.
