# WAVE 17 — **LAND THE PHASE SPLIT.  THIS IS THE WAVE THAT MEETS THE REQUIREMENT, OR SAYS BY HOW MUCH IT DOES NOT.**  PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST `hdl/` EDIT OF THE MAIN TREE.**  Results go in a
SEPARATE `docs/notes/phase_split_landing_results_2026-09-18.md`.

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM MAY BE PROGRAMMED BY THIS
WAVE.**  No Codex.  No nested subagent.  `docs/notes/standing_gates.md` §A
governs every timing figure — **one green build is not closure, and the same
tree has drawn 19.42 and 45.91 MHz.**

| | |
|---|---|
| **Tree at entry** | `4a796cc754` (`master`), `git status --porcelain hdl/` tracked = **0** |
| **What is already landed** | WAVE 7 chain flattening `2ceb8c3ba3` · WAVE 12 `build_id.v` removal `04efdc8d47` · **WAVE 16 ARM-A `qripe_presel` `f174e1a24a`** |
| **What this wave lands** | WAVE 9's three edits: **(a)** `6e822bf750` · **(b)** `5cf3254104` · **(c)** `bacf7f9fd9` |
| **The 20 uncommitted files** | the USER'S OWN WORK.  `git add` BY EXPLICIT PATH ONLY; `sw/testdata/receipts/*.jsonl` is **NOT** committed by this wave |

---

## §0 THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood.  A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

## §0.1 THE STANDING REQUIREMENT (USER RULING 2026-09-08, verbatim)

> **"I don't want custom sdc rules, period."**

**It is not re-opened, and THIS WAVE IS THE REQUIREMENT ITSELF.**  Edit (c)
deletes the exception; the no-exception build must then PASS.  A build *with*
the multicycle is a control, never the objective.

---

## §1 WHY THIS WAVE EXISTS — **WAVE 16's R-3 IS THE ARGUMENT, AND IT IS NEGATIVE**

WAVE 16 landed ARM-A `qripe_presel` on the UNSPLIT tree with equivalence
established in full (36 of 37 ladder legs identical, the exact 181 goldens,
four byte-identical `chain_lfsr` signatures, `fz2_replay` 305 × 11 by name, not
one architectural flop moved).  **And it measured the mechanism, on that tree,
to be a COST:**

| | CONTROL | RETENTION |
|---|---|---|
| ARM-A's no-exception paired Δ, **unsplit** (WAVE 16 R-3) | **−1.256 ns** [−1.656, −0.855], t = −8.71 | +0.508 ns [−1.093, +2.110], t = +0.88 |
| the same mechanism, **split** (WAVE 15) | **+2.847 ns** [+2.377, +3.316], t = +16.8 | +1.429 ns [+0.562, +2.296], t = 4.57 |
| no-exception `worst-of-5` | 27.78 → **26.75** | 27.01 → **27.33** |

**ARM-A pays only with the cut**, because the cut is what moves the binding
class onto the arc ARM-A shortens (WAVE 15 §1.3: BIU nodes in the data section
of the binding `ce → ce` path, **200 of 200** on the split tree).  So the two
landings are not a convenience; the requirement needs BOTH, and today's tree
holds exactly one of them.

### 1.1 THE SCOREBOARD THIS WAVE IS SCORED AGAINST

All figures `worst-of-5@seeds{1..5}`, stamp-free (bar **E11**), one driver.

| tree | CONTROL | RETENTION | source |
|---|---:|---:|---|
| unsplit, no exception | 27.78 | 27.01 | WAVE 13, **reproduced exactly by WAVE 16 on 10 of 10 draws** |
| unsplit + ARM-A, no exception | 26.75 | 27.33 | WAVE 16 R-3 |
| split only, no exception | 30.53 (0/5 PASS) | 31.15 (3/5 PASS) | WAVE 13 N-1 |
| **split + ARM-A, no exception** | **33.00 (5/5)** | **33.20 (5/5)** | **WAVE 15 — THIS WAVE'S PREDICTED OUTCOME** |
| split + ARM-B, no exception | 34.48 (5/5) | 34.41 (5/5) | WAVE 15, **not this wave's landing** |

**Bar: Fmax ≥ 32.0 MHz on EVERY draw, BOTH configurations, with no exception.**

⚠ **DO NOT ASSUME IT CLEARS.**  WAVE 15's 33.00 / 33.20 were drawn in scratch
worktrees at `850ef46559` by `sw/run_wave15_g6.sh`; this wave draws them in the
MAIN TREE at a landing commit by `sw/run_wave17_g6.sh`.  **Campaign law 4** —
*an unlabelled variable can be bigger than the one you are characterising* — was
paid for in this campaign and applies to a changed driver and a changed tree
path as much as to a date stamp.  **The margin over the bar is 1.00 / 1.20 MHz
and it is not large.**

---

## §2 WHAT IS BUILT, AND HOW IT COMPOSES — **MEASURED IN A SCRATCH WORKTREE, NOT ASSUMED**

| commit | edit |
|---|---|
| `6e822bf750` | **(a)** `CE_HALF` becomes an UNCONDITIONAL port of `v30_core` + RULING 1's two SS freeze clauses move down with it |
| `5cf3254104` | **(b)** the cut set — `v30u_eu_preload.svh`, the **778-bit** `s1q` shadow |
| `bacf7f9fd9` | **(c)** DELETE the CE multicycle from `hdl/nec_test.sdc` (+ the `nominal["SAME"]` 2.0 → 1.0 check, the probe labels, and `test_quartus_gate`'s era assertion) |

`hdl/` is **byte-identical between WAVE 13's base `5f8128b88b` and WAVE 16's
base `24e1060467`** (`git diff --stat 5f8128b88b 24e1060467 -- hdl/` is EMPTY),
so the only thing between WAVE 13's split tree and this tree is ARM-A itself.

### 2.1 ⚠ **ONE HUNK OF EDIT (b) DOES NOT APPLY, AND IT IS THE MIRROR OF WAVE 15's RENAME.  IT IS RE-DERIVED, AND THE RE-DERIVATION IS DECLARED HERE BEFORE IT IS USED.**

Checked one commit at a time in a **detached scratch worktree** at
`~/.cache/ucsimt-tmp/wave17/dry` (the main tree's `hdl/` is untouched at this
commit):

* **(a)** applies **cleanly**, all three files, no offset.
* **(c)** applies **cleanly**; `sw/quartus_gate.py` hunk #1 at an **offset of 66
  lines** and `sw/test_quartus_gate.py` hunk #1 at an **offset of 11 lines** —
  the two files WAVE 12 rewrote for bar E11, exactly as WAVE 13 recorded.
  **AN OFFSET IS NOT FUZZ.**
* **(b)** — **hunk #40 of `hdl/rtl/ucore/v30u_eu.sv` FAILS**, and `git apply` is
  atomic per file, so the whole file is refused:

```
error: while searching for:
                (((st == S_EPOP) || (st == S_TAIL_POP) || tailw_go) &&
                 retire_ok_n && !bnd_fire);

assign q_pop   = q_demand;
assign q_first = (st == S_OPC_POP) ? pop_is_first
error: patch failed: hdl/rtl/ucore/v30u_eu.sv:2206
```

**The reason is ARM-A**, which inserted its `q_ripe_lead_n` select between
`assign q_pop = q_demand;` and `assign q_first = …`, so the hunk's TRAILING
CONTEXT no longer follows.  This is the **mirror** of the one context-line
rename WAVE 16 §0.1 recorded going the other way (`s1w_retire_ok_n` /
`s1w_bnd_fire` → `retire_ok_n` / `bnd_fire`).

**THE RE-DERIVATION, DECLARED AND BOUNDED:** `~/.cache/ucsimt-tmp/wave17/rederive_b.py`
(committed with the results as `sw/wave17_rederive_b.py`) **trims trailing
CONTEXT lines from that one hunk and decrements both line counts.**  It asserts
it rewrote **exactly one** hunk.  **The diff between the original patch and the
re-derived one is TWO LINES and no changed line is among them:**

```
< @@ -2206,7 +2211,7 @@ wire q_demand = ((st == S_OPC_POP) && !bnd_fire) ||
> @@ -2206,6 +2211,6 @@ wire q_demand = ((st == S_OPC_POP) && !bnd_fire) ||
<  assign q_first = (st == S_OPC_POP) ? pop_is_first
```

**The change `retire_ok_n && !bnd_fire` → `s1w_retire_ok_n && !s1w_bnd_fire` is
untouched.**  With that one hunk re-derived, (b) applies with **61 hunks
succeeding** in `v30u_eu.sv` (offsets 1 and 19 lines, ARM-A's own two insertions)
and the other four files cleanly.

### 2.2 ⚠⚠ **AND THE COMPOSITION IS PROVED AGAINST AN INDEPENDENT REFERENCE: THE RESULT IS BYTE-IDENTICAL TO THE TREE WAVE 15 MEASURED AT 33.00 / 33.20.**

WAVE 15's ARM-A arm is reconstructible exactly: `850ef46559` (WAVE 13's split
tree) **+** `sw/testdata/wave15/arm_presel.diff` restricted to `hdl/` and
`sw/r7_lint.py`.  Built in a second scratch worktree
(`~/.cache/ucsimt-tmp/wave17/ref_arm`, applies cleanly).

> ### **`diff -rq dry/hdl ref_arm/hdl` IS EMPTY.  127 FILES EACH, ZERO DIFFERENCES.**

and file by file, `sha256` prefixes:

| file | composed | WAVE 15 reference |
|---|---|---|
| `hdl/rtl/ucore/v30_core.sv` | `e4ecf911e8874ed9…` | **same** |
| `hdl/rtl/ucore/v30u_eu.sv` | `c70dee375f9b9df5…` | **same** |
| `hdl/rtl/ucore/v30u_biu.sv` | `8e54248ef1bd5567…` | **same** |
| `hdl/rtl/ucore/v30u_eu_preload.svh` | `42052f5258da6c18…` | **same** |
| `hdl/nec_test.sdc` | `f0e1228ddd8f8a72…` | **same** (and the value WAVE 16 §5 recorded for the no-exception SDC) |
| `hdl/tb/tb_demux_min.sv` | `8a09517364517293…` | **same** |
| `sw/r7_lint.py` · `sw/cutset_lint.py` · `sw/ss_flop_whitelist_ucore.txt` | — | **same** |

**THIS IS THE STRONGEST STATEMENT THIS WAVE CAN MAKE IN ADVANCE**: whatever
Quartus does, the RTL that goes in is **the same bytes WAVE 15 drew 33.00 /
33.20 from.**  ⚠ **It is not a prediction that the numbers reproduce** — the
driver, the tree path and the day differ, and campaign law 4 says an unlabelled
variable can be the larger one.

⚠ **EDIT (a) IS AN INTERFACE CHANGE.**  `CE_HALF` leaves `ifdef V30_MUXED_AD`
and becomes an unconditional port; a de-muxed downstream integrator that did not
connect it will fail to elaborate — the intended, SURFACED consequence.  It has
been built and reverted **three** times (WAVE 4, WAVE 9, WAVE 13).
**`demux_off_gate` MUST PASS**, and its summary line moves *"the three muxed
ports are GONE"* → *"the two"*, which is registered here as a **known mover, not
a regression**: splicing `.CE_HALF` into a define-off build now SUCCEEDS, and
asserting that it fails would be asserting something false.  Its `AD` and
`AD_OE` clauses must still REFUSE **naming their pins**.

### 2.3 SAVE STATE — **USER RULING 2026-09-08, STANDING**

The 778-bit shadow is **DERIVED** and goes on that class of
`sw/ss_flop_whitelist_ucore.txt` as its **fourth** entry, `s1q`, beside `dec_q`.
`SS_COUNT` / `SS_VERSION` / `SS_TAG` **MUST NOT MOVE**.  Save-state writes are
forbidden at `CE_HALF` as well as at `CE`, enforced by two `$error` clauses in
`v30_core.sv` that edit (a) carries.

⚠ **THE FLOP COUNT IS TREE-DEPENDENT AND THE FIGURES MAY NOT BE CROSSED.**  The
UNSPLIT tree reads **228 flops / 3 whitelist entries**; the SPLIT tree reads
**229 / 4**.  Both are measured, both are right, and **WAVE 16 §4.1's finding —
per-entity register counts are SDC-DEPENDENT — forbids comparing a count across
builds that do not share an SDC.**

---

## §3 THE BARS.  **VERBATIM, AND THEY ARE NOT NEGOTIABLE AFTER A RESULT IS SEEN.**

**S-1  THE REQUIREMENT.**  With the CE multicycle DELETED, `quartus_gate.py
--seeds 5` PASSES E1-E5 on **EVERY** draw (Fmax ≥ 32.0, worst setup > 0, TNS
0.000 setup AND hold, 0 errors / 0 latches / 0 `lpm_divide`), **BOTH**
configurations.  **This is the campaign's success condition and it has never
been met.**

**S-2**  The exception is GONE and CHECKED: no uncommented
`set_multicycle_path`, no "CE multicycle" info line, every receipt's
`core_domain` k = 1.  ⚠ `grep -c set_multicycle_path` is the WRONG instrument —
the file keeps two COMMENTED *"DO NOT RESTORE"* lines; **anchor the match.**

**S-3  PIN IDENTITY**, BEFORE side on the pre-edit tree **first**: the full
ladder at its registered values · **`chain_lfsr_gate`'s four signatures
BYTE-IDENTICAL** · **`fz2_replay` scored content IDENTICAL, compared FIELD BY
FIELD BY NAME with the row count printed first** (⚠ it is structurally vacuous
in a git worktree — `.gitignore:9` hides the captures and it runs GREEN over
ZERO rows; this wave runs it in the MAIN TREE).  Include `check_core --opcodes
all --cases 0` 169,000, the exact 181 (`FA`/`FB`/`INT.FB`), `8F.0` 500, HLT
sweeps ⚠ WITH `--waits 0/1/2/3` 279/283, `ulockstep` 17,350 ALL LOCKSTEP,
`ghost_launch_law` 200/200, `check_boot` 220 and 400, `check_ab_sim` 187,
`sm3_s16_score` 1,320/1,371, `r7_lint`, `test_artifact` 45/45,
`chainflat_relocation_check` 9/9, `ucrom_mif_check`, `test_quartus_gate`
**287/287**.
⚠ `standing_gates.md`'s `ss_lint` row is **KNOWN STALE** (226 / 214 / 0x8D
against this tree's 232 / 228 / 0x8F) — **measure, report the disagreement,
never treat a stale row as a failure.**

**S-4**  `ss_lint` exits 0, `SS_COUNT` / `SS_VERSION` / `SS_TAG` **UNCHANGED**,
0 UNMAPPED, whitelist grown by **exactly `s1q`**.

**S-5**  `check_core --opcodes all --cases 0` = 169,000 at `--ce-div 2, 3, 4 AND
8`; `--ce-div 1` still **REFUSED**.  The split makes **S-1 of the ce/ce_half
contract** (*at least one `ce_half` between consecutive `ce`s*) load-bearing for
the EU — without it stage 2 consumes a STALE stage 1 — **so this is a
correctness bar, not a formality.**

**S-6**  **`demux_off_gate` PASSES** (edit (a)'s interface change).

**S-7**  **`cutset_lint` X4 WILL FIRE AND THAT IS EXPECTED, NOT A REGRESSION** —
WAVE 15 measured it and WAVE 16 §2.3 / §10 item 4 recorded **IN ADVANCE** that
it would, because ARM-A **relocates** a bypass that was always there through the
BIU port where the lint could not see it.  **`phase_split_lint` must PASS.**
Report both; **do not "fix" X4 in this wave** — choosing a lint outcome after
seeing it is what this campaign refuses.

**S-8**  **`E11` true on every draw** (⚠ at DISTRIBUTION level as
`E11_no_build_stamp`, **not** in each seed's `bars`).

**S-9**  **NO REGRESSION WITH the exception**: a `--seeds 5` pair on the tree's
pre-edit SDC is **not required**, but if one is taken it is reported against
WAVE 16's **CONTROL 41.42 / RETENTION 41.55**.

**S-10  THE REVERT CONDITION.**  If **S-1** fails, or any leg of
**S-3 / S-4 / S-5 / S-6** moves, **THE LANDING DOES NOT HAPPEN**: revert all
three edits, report the GAP to 32.0 explicitly, and keep both documents.
**Do not soften a bar to make a landing possible and do not re-scope after
seeing a result.**
⚠ **IF S-1 PASSES, SAY SO PLAINLY**: it is the requirement met after seventeen
waves, and it should be stated as a fact with its receipts, not celebrated.

---

## §4 THE ORDER OF OPERATIONS, REGISTERED SO IT CANNOT BE CHOSEN AFTERWARDS

1. the **BEFORE ladder** on the UNEDITED main tree — `sw/wave16_ladder.sh`
   (WAVE 16's own 37-leg driver, **UNEDITED**, so the instrument is the same one
   that established ARM-A's equivalence) into `sw/testdata/wave17/before/`;
   started before this document was written and touching no `hdl/` file;
2. **this document**;
3. edits **(a)**, then **(b)** (with §2.1's one re-derived hunk), then **(c)** —
   three commits, in WAVE 9's order, (c) last because **this wave is not asking
   WAVE 13's N-3 question** and needs no intermediate unsplit-no-exception arm;
4. the **AFTER ladder**, `ss_lint`, `demux_off_gate`, the divisor sweep, the two
   lints — **S-3 / S-4 / S-5 / S-6 / S-7**;
5. the composition proof re-taken **on the committed tree**, against
   `ref_arm` — `diff -rq` over `hdl/`;
6. **S-1**: `quartus_gate.py --seeds 5` and `--retention --seeds 5`, one driver,
   seed set **{1,2,3,4,5}**, both configurations, with NO exception;
7. the verdict, and **S-10 if the revert triggers**.

⚠ **THE BEFORE LADDER IS TAKEN ON A TREE THAT ALREADY HOLDS ARM-A.**  That is
deliberate and is what makes S-3 a statement about **the split**: WAVE 16
already established ARM-A's own equivalence against the pre-ARM-A tree, leg for
leg, so the only mechanism under test here is the cut.

---

## §5 WHAT THIS WAVE PREDICTS, WRITTEN DOWN SO IT CAN BE WRONG

1. **S-3 / S-4 / S-5 / S-6 hold**, with exactly the two registered movers WAVE 13
   saw (`ss_lint`'s 228 → 229 flops and 3 → 4 whitelist entries;
   `demux_off_gate`'s *"three"* → *"two"* summary line) — and, because ARM-A is
   in this tree and was not in WAVE 13's before-side, **`ss_lint`'s
   "comb/next-state regs skipped" count is already at ARM-A's value on BOTH
   sides and should NOT move here.**
2. **S-7: `cutset_lint` FAILS on X4** and `phase_split_lint` PASSES.  ⚠ On the
   pre-edit tree BOTH exit **2, COULD NOT RUN** (WAVE 16 §2.3), so this is the
   one leg whose BEFORE side is structurally absent and whose AFTER side is
   therefore not a comparison.
3. **S-1: both configurations clear 32.0 on all five draws**, in the
   neighbourhood of WAVE 15's 33.00 / 33.20.  **The margin is ~1 MHz and a
   single draw below 32.0 fails the bar** — including one at, say, 31.9.
4. **The fitted design gets SMALLER** despite +778 bits of flop, as WAVE 4,
   WAVE 9 and WAVE 13 each measured.  ⚠ A&S combinational counts are **not
   reproducible run to run** (`ucore_provenance.md` §74.4a), so this is
   REPORTED, never concluded.
5. **`v30u_eu`'s and `v30u_biu`'s per-entity register counts will not be
   comparable to WAVE 16's**, because the SDC differs (WAVE 16 §4.1).  Any
   register accounting in the results is scored **only between same-SDC pairs.**

---

## §6 DISCIPLINE, DECLARED IN ADVANCE

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
  ⚠ **THE FABRIC CONFIRMATION IS OWED SINCE WAVE 7, DOUBLED AT WAVE 12, TRIPLED
  AT WAVE 16 — AND THIS LANDING MAKES IT FOUR STRUCTURAL CHANGES DEEP.**  It is
  **RECORDED, NOT DISCHARGED**, and **no fabric figure taken on FLASH #21 or
  earlier may be quoted against this tree.**  It is not this wave's to pay.
* **BLOCK, DO NOT POLL.**  One foreground
  `until ! pgrep -x quartus_fit >/dev/null 2>&1; do sleep 60; done` with a large
  `timeout`.  WAVE 13 stalled by polling and needed resuming by hand.
* **Single-writer guard before any Quartus stage** — `pgrep -x`, EXACT binary
  name, **ONE PATTERN PER CALL** (`pgrep -x a b` is an ERROR whose failure
  branch reads as *"idle"*); ⚠ `pgrep -f <script>` **SELF-MATCHES** the waiting
  shell and is never used.
* ⚠⚠ **NEVER `git stash`, `git checkout .`, or `git reset --hard`.**  **20
  pre-existing modified files are the USER'S OWN UNCOMMITTED WORK.**  WAVE 12
  swept them with `git stash`; WAVE 16 swept 20 rows of the user's own
  `sw/testdata/receipts/verilator_binary.jsonl` into a commit.  **`git add` BY
  EXPLICIT PATH, and `sw/testdata/receipts/*.jsonl` IS NOT COMMITTED BY THIS
  WAVE** — receipts go in by value under `sw/testdata/g6dist/w17-*/`.
* ⚠ `git checkout -- hdl/nec_test_ucore.qsf` by **that exact path** between
  Quartus runs, or the next sweep dies at E1.
* ⚠ A driver `set -e` **dies on a RED sweep** — `quartus_gate` exits non-zero on
  RED.  Drivers carry `set -u` and never `set -e`.
* `~/.cache/ucsimt-tmp` for every intermediate; **nothing in `/tmp`.**
* ⚠ **DO NOT CARRY A FIGURE FROM ONE TREE TO ANOTHER.**  Register counts are
  SDC-dependent; `ss_lint` differs split vs unsplit; the coordinator has made
  this error three times.  **Measure on the tree you are on.**
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  **TEN instruments in this
  campaign have returned confident, wrong answers** (handoff §9).  Assume the
  next one is also wrong until its control says otherwise.
* ⚠ **COMPARE CONTENT, NOT A DIGEST COMPUTED BY THIS WAVE.**  *A number with no
  artifact id is not quotable.*
* ⚠ A Verilator artifact receipt is **NOT** reproducible across rebuilds of a
  byte-identical tree — *"the receipt moved, so the edit reached the binary"* is
  INVALID.
* Truthful commit messages; **never assert a gate that is not met.**
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
