# THE NO-SDC TIMING CAMPAIGN — HANDOFF, 2026-09-14

**Snapshot at HEAD `ea8cfc064d`.** Written by the coordinator. Every figure
below was verified against the committed artifact, not against recall; where a
figure is reported rather than verified it says so.

---

## §1 THE REQUIREMENT

**USER RULING 2026-09-08, verbatim:**

> **"I don't want custom sdc rules, period."**

and, in the same message, *"Don't try to reframe my original ask."*

The target state is that the ucore closes timing on a downstream FPGA with **no
`set_multicycle_path` and no other core-specific exception in the integrator's
SDC**. It is a product decision, not an engineering optimum to be re-derived.

**Do not re-open it.** Arguments of the form *"the exception is only five
lines"*, *"it is contract-free and portable verbatim since the 2026-08-13
correction"*, *"M72 closed with it"* and *"a phase split can only match the
multicycle's ceiling"* are **all true and all beside the point.** The
coordinator made every one of them and was told to stop.

**Consequence for measurement:** the NO-EXCEPTION build is the goal state. A
build *with* the multicycle is a control, never the objective. A wave that
improves the with-exception Fmax while leaving the no-exception build RED has
not advanced the campaign and must say so.

---

## §2 WHERE IT STANDS

### 2.1 What is landed in the tree

| wave | mechanism | commit | state (verified from the tree) |
|---|---|---|---|
| **7** | chain flattening — the sevenfold unroll deleted | `2ceb8c3ba3` | **LANDED** (9 `v30u_eu_arm_*.svh` present) |
| **12** | `build_id.v` removed + bar `E11` | `04efdc8d47` | **LANDED** (no `build_id.v`, generator deleted, E11 in `quartus_gate.py`) |

### 2.2 What is NOT landed

| mechanism | commits | state |
|---|---|---|
| the phase split | `6e822bf750` (a) · `5cf3254104` (b) · `bacf7f9fd9` (c) | **reverted** — `v30u_eu_preload.svh` absent, 2 live `set_multicycle_path` lines |
| the `q_ripe_lead_n` reformulation | WAVE 15 arms, `sw/testdata/wave15/arm_{presel,s1q}.diff` | **never landed** |

`hdl/` carries **0 tracked modifications**. The working tree holds **21
pre-existing modified files that are the user's own uncommitted work** — see
§7.

### 2.3 The scoreboard

Bar: **Fmax ≥ 32.0 MHz on every draw, both configurations, with no exception.**
All figures `worst-of-5@seeds{1..5}`, stamp-free, same driver, same seed set.

| tree | CONTROL | RETENTION |
|---|---:|---:|
| unsplit, no exception (WAVE 13) | 27.78 | 27.01 |
| **+ phase split** (WAVE 13/14/15 base) | 30.53 (0/5 pass) | 31.15 (3/5 pass) |
| **+ split + reformulation ARM-A** | **33.00 (5/5)** | **33.20 (5/5)** |
| **+ split + reformulation ARM-B** | **34.48 (5/5)** | **34.41 (5/5)** |

**Both variants clear the bar on every draw of both configurations.**

⚠ **RETENTION is the shipping configuration** — every flashed bitstream in this
project is built `WITH X1_AD_RETENTION=1`.

---

## §3 THE ANSWER

### 3.1 Mechanism 1 — the phase split

The EU's `ce → ce` cone is cut across the two enable phases: stage 1 evaluates
`ce → ce_half` and is captured on `ce_half`; stage 2 evaluates `ce_half → ce`.
A **778-bit shadow** (`v30u_eu_preload.svh`), a **cut set proven by
construction** with a lint, and `CE_HALF` promoted to an **unconditional port**
(a de-muxed build has none, so `demux_off_gate` breaks otherwise).

Save state: the shadow is **DERIVED** and goes on that class of
`sw/ss_flop_whitelist_ucore.txt`; `SS_COUNT`/`SS_VERSION`/`SS_TAG` do not move.
This rests on **USER RULING 2026-09-08**: save-state writes are forbidden at
`CE_HALF` as well as at `CE`, enforced by two `$error` clauses in
`v30_core.sv`.

Worth **+2.75 MHz (CONTROL) / +4.14 (RETENTION)**, measured like-for-like.

### 3.2 Mechanism 2 — the `q_ripe_lead_n` reformulation

**F7 requires** that the value the EU's clocked step reads at `q_ripe_lead_n`
is the BIU's queue level *for the clock the edge opens*, including the effect
of the EU's own pop on that clock. Breaking it costs **181 goldens** — `FA` 74
+ `FB` 68 + `INT.FB` 39, every one a `ONE_BYTE_LOGIC` form, the only caller of
`wait_retire_lead`.

The loop is `EU q_pop → pop_l → q_cnt → poppable_n → q_ripe_lead_n → EU`. The
partition: `q_ripe_lead_n = f(BIU registers, q_pop, q_flush)` — **two bits**,
but a flush overwrites the pop's decrement, so **three levels, not four**. The
binding round trip is the *pop* one (`bnd_fire` → `q_demand`/`q_pop`).

**The fix:** the BIU publishes the retire-lead level for each of the two things
the EU can do this clock — pop, or not — **both pure functions of BIU
registers**; the EU selects locally with `q_pop && q_ripe && !q_flush`. It is
the same function against two thresholds: *at least one* and *at least two*.

### 3.3 Equivalence is established in the strongest form

Not *"the arm passes"* but **"the arm produces the identical number to the base
on every leg"**, across three separately-receipted binaries:

169,000/169,000 at `--ce-div` 2/3/4/8 with div 1 refused · **the exact 181:
`FA` 500/500, `FB` 500/500, `INT.FB` 200/200** · `ulockstep` ALL LOCKSTEP ·
HLT sweeps 279/283 · `check_boot` 220 and 400 · `check_ab_sim` 187 · S16
census `{busstat_other 24, ARCH 27}` · **four `chain_lfsr` signatures
byte-identical** · `ss_lint` 229 flops · **`fz2_replay` 305 rows × 11 fields
compared by name, never by a digest.**

---

## §4 THE OPEN DECISION — ARM-A vs ARM-B

**This is the user's call and it is the only thing blocking a landing plan.**

| | **ARM-A** `qripe_presel` | **ARM-B** |
|---|---|---|
| flops added | **none** | one, declared |
| depends on the split? | **no** — split-independent | yes, needs the cut |
| lints | leaves `cutset_lint` **X4 firing** | **passes every lint** |
| CONTROL / RETENTION | 33.00 / 33.20 | 34.48 / 34.41 |
| margin over the bar | +1.00 / +1.20 | +2.48 / +2.41 |

**On X4:** ARM-A does not *create* a bypass — it **relocates** one that was
always there, through the BIU port where the lint could not see it. The lint is
right to fire; whether that is acceptable is a judgement about the invariant's
scope, not a defect report.

---

## §5 THE LANDING PLAN — IT IS TWO LANDINGS

The phase split **does not land on its own** (WAVE 13's N-1 failed at
30.53/31.15). The reformulation alone has never been sized on the unsplit tree.
So the requirement needs **both**, and the repo's per-mechanism rule applies:
*a bundle's benefit is not evidence for any member of it.* Each is already
sized separately, so the attribution exists.

Suggested order:

1. **Land the reformulation first.** ARM-A is split-independent, so it can land
   and be measured on today's tree with the multicycle still present — a clean,
   low-risk landing with its own G6 and ladder.
2. **Then land the split** (edits (a), (b), (c) together — (c) is what deletes
   the exception and is the point), re-running the no-exception sweeps as the
   requirement's own gate.
3. **Then flash.** See §6.

⚠ Edit (a) promotes `CE_HALF` to an unconditional port. That is an **interface
change** visible to any integrator, and it has been built and reverted twice.
`demux_off_gate` must pass.

---

## §6 THE FABRIC DEBT — OWED, UNPAID, AND NOW THREE CHANGES DEEP

**Nothing has been on a board since FLASH #21.** The correctness bar for this
project is **silicon match**, not simulation.

Between the tree and the last bitstream now sit:

1. **WAVE 7's chain flattening** — a re-derivation of the EU's decode;
2. **WAVE 12's `build_id.v` removal** — which moves the bitstream;
3. (pending) whatever of §5 lands.

**No fabric figure taken on FLASH #21 or earlier may be quoted against this
tree**, for two independent reasons. The coordinator's standing recommendation
is that a flash should not wait for a third.

---

## §7 WORKING-TREE HAZARDS — READ BEFORE ANY AGENT TOUCHES THIS REPO

* **There are 21 pre-existing modified files that are the USER'S OWN
  UNCOMMITTED WORK.** WAVE 12 ran `git stash` and swept all of them; it was
  caught on the next command and `git stash pop` restored them, but **never
  `git stash`, `git checkout .`, or `git reset --hard`.**
* **`git add` by explicit path only.** WAVE 7 swept the user's in-progress
  `nec_test` → `nuV30` rename into its own results commit. The content was the
  user's and correct; only the attribution was wrong.
* `hdl/nec_test_ucore.qsf` must be restored with
  `git checkout -- hdl/nec_test_ucore.qsf` — **that exact path** — between
  Quartus runs, or the next sweep dies at E1. Quartus rewrites the revision
  file it compiles; this is the one declared §70.7 exemption.
* **Block, do not poll.** A fit outlives a polling turn. One foreground
  `until ! pgrep -x quartus_fit >/dev/null 2>&1; do sleep 60; done` with a large
  timeout. WAVE 13 stalled by polling and had to be resumed by hand.

---

## §8 MEASUREMENT LAWS THIS CAMPAIGN ESTABLISHED

These are the most transferable output and they were each paid for.

1. **A CENSUS RANKS CANDIDATES; IT DOES NOT SIZE THEM — IN EITHER DIRECTION.**
   Five for five: `ucrom` **5.9× over** (W8), the round trip **5.3× over** on
   the unsplit tree (W10), **2.3×/1.7× under** on the split tree (W14), and
   W15's own guess **2.4× under**. **Only a built A/B sizes anything.**
2. **A DIFFERENCE BETWEEN TWO IDENTICALLY-COMPILED BUILDS TRANSFERS; A
   PARTITION PREDICTION DOES NOT.** W6 predicted −9.431 ns from a standalone
   project and W7 realised −9.413. But an *uncut netlist predicting where a cut
   will land* mispredicted by **+11.3 to +20.0 ns** (W5). ⚠ W7's famous
   "+0.018 ns, right to 0.2 %" is **cross-stamp and therefore void** — see
   law 4 — though the method survived independent re-use at W10 and W14.
3. **A CUT DOES NOT DIVIDE AN ARC — IT GROWS IT, BY A CONSTANT.** W4 measured
   **+15.295 ns** on a 43.485 ns arc, W9 **+15.188** on a 32.969 ns arc: the
   same to **0.11 ns** across a 10.5 ns tree change. Budget ~15.2 ns for any
   future cut of this loop. ⚠ W4's leg is clean (both arms one stamp); W9's is
   cross-stamp, so the precision is partly luck.
4. **AN UNLABELLED VARIABLE CAN BE BIGGER THAN THE ONE YOU ARE
   CHARACTERISING.** `hdl/build_id.v`, a gitignored two-character date stamp in
   the OSD string, was an extra fitter seed worth **1.647 ns / 1.34 MHz** —
   where five *seeds* at one stamp spanned **0.603 ns**. The `worst-of-N`
   distribution gate had been characterising the smaller dimension for a month.
   Removed at W12; bar **E11** refuses its return.
5. **A CANDIDATE'S VALUE IS NOT A PROPERTY OF THE CANDIDATE.** The same
   one-line edit measured **0.527 ns** on one tree and **6.629 ns** on another.
6. **SEVERING IS NOT REFORMULATING.** A behaviour-breaking probe sizes a
   *ceiling*; it is not a design. Label it, claim no equivalence, and **check
   that `check_core` FAILS on it** — a probe that still passes has not cut
   anything.

---

## §9 THE VACUOUS-INSTRUMENT REGISTER

**Ten instruments in this campaign returned confident, wrong answers. Every
single one was caught by a positive control, and several passed for the wrong
reason before failing honestly.** Assume the next one is also wrong until its
control says otherwise.

| # | the trap |
|---|---|
| 1 | `get_timing_paths -through` **silently ignores a `get_nodes` collection** — returns "no path" for everything. Use `get_pins`. |
| 2 | A **bulk `-through`** collection can be accepted-and-ignored; it fired on **14 of 34 draws**. Pass **one pin at a time** and keep the bulk form printed beside it as a known-wrong control. |
| 3 | `string match "$name*"` **fails on any bus-indexed register** — `[3]` is a character class. Use `[string first $p $s] == 0`. |
| 4 | A synchronous-load register is written through **`\|asdata`, not `\|d`**; an **M10K port register exposes zero pin objects**. |
| 5 | Verilator **`$stop`s on the first procedural `$error`**, so one assertion masks the next. Give each clause its own probe. |
| 6 | A driver `set -e` **dies on a RED sweep**, because `quartus_gate` exits non-zero on RED. |
| 7 | `pgrep -f <script>` **self-matches the waiting shell**; `pgrep -x a b` is an **error** whose failure branch reads as "idle". One pattern per call. |
| 8 | **`fz2_replay` is structurally vacuous in a git worktree** — `.gitignore:9` hides the captures, and it ran GREEN over ZERO rows. |
| 9 | Bar **`E11` lives at DISTRIBUTION level** (`E11_no_build_stamp`), not in each seed's `bars` — a per-seed query returns nothing and reads as a miss. |
| 10 | **Comparing raw log TEXT** reports every leg as differing (timestamps, paths, receipts). **Compare the scored quantities.** Likewise a regex sweep for 16-hex strings picks up receipts alongside signatures. |

⚠ **And two errors of quotation, both the coordinator's:** a self-computed hash
was quoted as if it were the tool's registered quantity, and the correction
then quoted a value appearing in **no artifact at all**. The fact was true;
both numbers were unsupported. **Compare named fields directly. A number with
no artifact id is not quotable.**

---

## §10 OWED AND BOOKED

1. **The fabric confirmation** (§6) — the largest debt.
2. **`standing_gates.md` registration**, never taken because waves were told not
   to edit it: bar **E11**; `test_quartus_gate` **286/286** (⚠ the coordinator
   briefed 287 from W12's report — the tree reads 286); and its **stale
   `ss_lint` row** at 226/214/0x8D against this tree's **232/229/0x8F**.
3. **WAVE 11's one-fit repair** — re-derive W9's `+15.188` cutting constant
   against a same-stamp arc. Now cheap; `sw/testdata/wave13/` holds the pair.
4. `sta_cutset_diag.tcl`'s **C-8 string classifier** under-reports, because a
   physical-synthesis duplicate of `s1q` is filed under a fanout-net name. It
   needs a membership test.
5. `check_core --ss-sweep` is **on no ladder** — booked six times.
6. Unexplained and recorded: ±1 whole-design A&S register wobble outside
   `v30_core`; retention's W14 ceiling sitting 1.6 ns below control's;
   `q_flush` as the measured residual (2 LUT levels, ~0.5 ns).

---

## §11 WAVE INDEX

| # | what it did | outcome |
|---|---|---|
| 1 | phase-split anatomy | cut named at the chain-loop entry |
| 2 | split at that cut | **RED 22.78** — the shadow was not a cut set |
| 3 | L2, register the ROW table | **+0.36 MHz**, refuted by its own bar. **Finding: the EU is a LOOP** |
| 4 | split as a proper cut set | **RED 20/20**; stage 2 = the 7-copy chain, 37.224 ns |
| 5 | chain anatomy | free-deletion floor **29.49 ns** — trimming cannot reach 29.6 |
| 6 | flattening study | **the unroll is an ARTIFACT**; −9.431 ns predicted |
| 7 | **land the flattening** | **LANDED.** gap 9.82 → 3.68 MHz, −33 % EU area, not one flop moved |
| 8 | front-end anatomy | top candidate built out to **0.64 ns**, not 3.8 |
| 9 | split on the flattened tree | **RED**, but +1.74/+2.27 and both stages fit |
| 10 | the BIU round trip | contradiction resolved: **a placement lottery** |
| 11 | **PC-C0** | **the build stamp** — an unlabelled variable bigger than the seed |
| 12 | **remove `build_id.v`** | **LANDED.** Δ = 0.000 ns where W11 measured 1.647 |
| 13 | split like-for-like | **RED**, but +2.75/+4.14 and **3 draws cleared 32.0** |
| 14 | size the round trip | ceiling **+6.293 / +4.688 ns** — the budget exists |
| 15 | find a legal mechanism | **FOUND.** Behaviour-identical, no flop, **clears both** |

**Waves 2, 3, 4 each committed to a lever before measuring it and were refuted.
Waves 1, 5, 6, 8, 10, 11, 14 measured first. The measure-first waves produced
every landing this campaign has.**

---

*Handoff ends. The campaign has its answer; what remains is a decision (§4), two
landings (§5), and a bitstream (§6).*
