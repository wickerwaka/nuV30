# WAVE 19 — **LAND ARM-B.**  PRE-REGISTRATION.

**Committed BEFORE the first `hdl/` edit of this wave.**  `git status
--porcelain hdl/` (tracked) reads **0** at this commit, measured, not recalled.

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.  `docs/notes/standing_gates.md` §A governs every timing figure.

| | |
|---|---|
| **Tree at entry** | `6de3955b5a` (WAVE 18's registration), tracked `hdl/` clean |
| **The mechanism** | WAVE 15's **ARM-B** = candidate **C2**, the 1BL-lead select off the phase split's own `s1q` shadow |
| **Its measured figures (WAVE 15, on the split tree, NOT this tree)** | `worst-of-5` **CONTROL 34.48 / RETENTION 34.41** |
| **What is in the tree now (WAVE 17, measured)** | **CONTROL 33.00 / RETENTION 33.20**, `nec_test.sdc` with **no timing exception** |
| **Tool** | Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns; Verilator 5.032 |

---

## §0 ⚠⚠ THE STANDING REQUIREMENT IS ALREADY MET AND THIS WAVE MUST NOT REGRESS IT

**USER RULING 2026-09-08, verbatim: *"I don't want custom sdc rules, period."***

WAVE 17 landed the phase split, `nec_test.sdc` carries **zero** live
`set_multicycle_path` / `set_false_path` / `set_max_delay` lines, G6 passes
**10 of 10 draws** of both configurations, and **FLASH #22 put that bitstream in
silicon on 2026-09-19.**

> **ARM-B IS AN IMPROVEMENT ON A MET REQUIREMENT.  IT IS NOT A ROUTE TO ONE.**
> If it does not hold the requirement, it does not land — **V-2 and V-6 below.**

---

## §1 JOB 1 — **ARM-B IS AN *ADDITION ON TOP OF* ARM-A, NOT A REPLACEMENT OF IT.  ESTABLISHED THREE WAYS, BEFORE ANY EDIT.**

The ambiguity is real: WAVE 15 measured ARM-A and ARM-B as two **alternative**
arms against a common base, while WAVE 16 §10 item 3 calls ARM-B *"a one-hunk
change on top of what is now in the tree."*  **Those are different claims and
only one of them can be right.**  It is settled here from the artifacts, before
the answer could be convenient.

### 1.1 The two WAVE 15 arm diffs are IDENTICAL except in the EU

`diff -u` of `sw/testdata/wave15/arm_presel.diff` and
`sw/testdata/wave15/arm_s1q.diff`, restricted to their `hdl/` + `sw/r7_lint.py`
content, differs **only inside `hdl/rtl/ucore/v30u_eu.sv`**.  The BIU's
two-level publication (`q_ripe_lead_n0` / `q_ripe_lead_n1`, the `pop_eff`
reference and its two `$fatal` clauses), `v30_core.sv`'s wire and port renames
and `sw/r7_lint.py`'s two declared-carrier entries are **character for
character the same in both arms.**

### 1.2 And the bytes say so

A reference worktree `~/.cache/ucsimt-tmp/wave19/ref_armb`, detached at
`850ef46559` with `arm_s1q.diff` applied to `hdl/` and `sw/r7_lint.py` — the
same construction WAVE 17 §9.1 kept `ref_arm` for — compared file by file
against **this tree**:

| file | this tree vs the ARM-B reference |
|---|---|
| `hdl/rtl/ucore/v30u_biu.sv` | **SAME** — `8e54248ef1bd5567…` |
| `hdl/rtl/ucore/v30_core.sv` | **SAME** — `e4ecf911e8874ed9…` |
| `sw/r7_lint.py` | **SAME** — `4ec672df0afc4fb8…` |
| `hdl/rtl/ucore/v30u_eu.sv` | **DIFFERS** — this tree `c70dee375f9b9df5…`, ARM-B `31ff3a50f503da77…` |

**Three of the four files ARM-B touches are already in the tree, byte for
byte.**  ⚠ And the fourth is verified to be ARM-A's own: this tree's
`v30u_eu.sv` is **sha256-identical to `~/.cache/ucsimt-tmp/wave17/ref_arm`'s**,
which is WAVE 15's ARM-A arm — WAVE 17 §3.4's composition claim, re-measured
here independently rather than carried.

### 1.3 **THE ANSWER**

> **ARM-B = ARM-A + ONE EDIT TO ONE FILE.**  It is an **ADDITION**.  Nothing
> ARM-A landed is removed, reverted or re-derived.  The one thing that *changes*
> inside that addition is **where the select happens**: ARM-A's two-line
> combinational `wire q_ripe_lead_n = (q_pop && q_ripe && !q_flush) ? n1 : n0;`
> becomes `wire s1w_qripe_pop = q_pop && q_ripe && !q_flush;` — **the select
> predicate is shadowed and the mux moves into stage 2.**  The published pair is
> untouched, the BIU is untouched, and the two consumer sites
> (`v30u_eu_step.svh`, `v30u_eu_arm_decode2.svh`) stay **byte-unchanged** and
> still read a wire spelt `q_ripe_lead_n`.

**THE EDIT, IN FULL, IS COMMITTED WITH THIS PRE-REGISTRATION** at
`sw/testdata/wave19/armb_delta.diff` (**86 lines, 7 hunks, ONE FILE**, sha256
`b4ea3a43ce441a62…`), derived mechanically as `diff -u` between this tree and
the ARM-B reference — **not hand-written, and not chosen after seeing a
result.**

⚠ **ONE COSMETIC DEFECT IS LANDED DELIBERATELY.**  The `S1W` comment block in
WAVE 15's ARM-B arm has ragged continuation indentation.  **It is kept exactly
as measured**, because byte-identity to the artifact that drew 34.48 / 34.41 is
worth more than alignment, and tidying it would break §7's composition proof.

---

## §2 JOB 2 — **THE FLOP, AND ITS SAVE-STATE DISPOSITION, DECLARED BEFORE THE EDIT**

### 2.1 What it is

> **`qripe_pop` — ONE BIT.  It holds `q_pop && q_ripe && !q_flush`: whether the
> EU's own act on the BIU queue this clock is a pop that takes effect.**

It is **not a new register**.  It is **bit 778 of `s1q`**, the phase split's
stage-1 shadow, which the landing widens **`S1W` 778 → 779**.  `s1q` is
captured on `ce_half` and consumed by stage 2 on `ce`, exactly as its other 778
bits are.

### 2.2 Architectural or DERIVED — and the bar is read, not assumed

`sw/ss_flop_whitelist_ucore.txt`'s **DERIVED** class admits a register only if
it *"is a PURE FUNCTION of registers that ARE SSA-mapped, and is recomputed from
the SAME next-state expression under the SAME commit condition as those
registers"*, with the derivation **checkable by eye in one named place**.

`s1q` is **already on that class**, admitted at WAVE 17.  The new bit is
checked against the same bar, term by term:

| term | what it is | SSA status |
|---|---|---|
| `q_pop` | `q_demand`, a stage-1 EU quantity | pure function of `ce`-committed EU registers — the existing `s1q` argument |
| `q_flush` | `row_acts_ok && s1w_row_flush`, stage-1 EU | same |
| **`q_ripe`** | `v30u_biu.sv:848`, `poppable != 0` where `poppable = f(r_grn_ttl, r_q_cnt, r_grn_n)` | **all three are SSA-mapped** — `SSA_B_GRN_TTL`, `SSA_B_Q_CNT`, `SSA_B_GRN_N` (`v30u_biu.sv:2858-2860`) |

> **DISPOSITION: DERIVED, on the EXISTING `s1q` entry.  NO NEW WHITELIST ENTRY
> IS ADDED.**

⚠ **ONE DECLARED WHITELIST EDIT, AND IT IS A JUSTIFICATION, NOT AN ENTRY.**  The
`s1q` justification enumerates *"the seven REGISTERED BIU views the wire cone
reads"* — `eu_access_active`, `eu_opr_free`, `eu_rd_done_n`, `eu_slot_busy`,
`eu_wr_done_n`, `eu_wr_eval`, `q_byte`.  **`q_ripe` is not among them and this
landing makes the cone read it**, so the justification gains it as an **eighth**
view with the three SSA addresses named.  **Amending a justification to stay
true is required; adding an entry to silence a gap is forbidden, and none is
added.**

### 2.3 **DOES THE SAVE-STATE STREAM BREAK?  THE REGISTERED PREDICTION IS *NO*.**

`ss_lint` counts architectural flops **by name**; `s1q` is one whitelisted name
and a 1-bit widening of it changes **no save-state address**.  WAVE 15 §6
measured exactly this on the ARM-B arm.

**Registered prediction, to be MEASURED and reported either way:**

| quantity | this tree (measured 2026-09-19, before the edit) | **predicted after** |
|---|---|---|
| `SS_VERSION` | **0x8F** | **0x8F — UNCHANGED** |
| `SS_COUNT` | **232** (1 + 109 BIU + 122 EU) | **232 — UNCHANGED** |
| `SS_TAG` | **0x8FE8** | **0x8FE8 — UNCHANGED** |
| architectural flops | **229**, 0 UNMAPPED | **229 — UNCHANGED** |
| whitelist entries | **4** (`tsel`, `ending`, `dec_q`, `s1q`) | **4 — UNCHANGED** |
| EU comb/next-state regs skipped | **430** | **432** — `qripe_pop` and `q_ripe_lead_n`, both written inside the one `always @*` |
| BIU comb/next-state regs skipped | **205** | **205 — UNCHANGED** |
| `hdl/rtl/ucore/v30u_ss_pkg.sv` | — | **UNTOUCHED by every commit of this wave** |

> ### ⚠⚠ **IF ANY OF THE FIRST FIVE ROWS MOVES, IT IS A SAVE-STATE STREAM BREAK — THE FIRST OF THIS CAMPAIGN — AND IT WILL BE REPORTED AS ONE IN THE RESULTS HEADLINE, NOT ABSORBED INTO A TABLE.**

⚠ **AND THE COMPILER, NOT `ss_lint`, IS THE AUTHORITY ON *"one flop"*.**  WAVE 15
§6 recorded that `wave15_arms.py`'s textual *"no non-blocking assignment"* check
**printed "no flop added" for ARM-B and was wrong** — a parameter widening is
invisible to a `<=` scan.  The registered reading is the fit report's per-entity
`dedicated_logic_registers`: **`v30u_eu` 1,326 → 1,327**, `v30u_biu` **434 →
434**, on this tree's no-exception SDC.
⚠ **SDC-DEPENDENT (WAVE 16 §4.1): a register count may only be compared across
builds that share an SDC.**  Both sides of this A/B do.

---

## §3 THE BARS

### **V-1 — EQUIVALENCE, FIRST AND IN FULL, BEFORE SIDE ON THE PRE-EDIT TREE.**

Every leg **IDENTICAL**, not merely passing.  The BEFORE ladder runs on the
unedited tree at this commit; the AFTER ladder on the landing; both through
**one driver** and compared **by scored line, never by raw log text**.

`check_core --opcodes all --cases 0` **169,000** at `--ce-div` **2, 3, 4 AND 8**
with div 1 **refused** · **the exact 181: `FA` 500/500, `FB` 500/500, `INT.FB`
200/200** · `8F.0` 500 · the four HLT sweeps ⚠ **WITH `--waits 0/1/2/3`**
**279/283** · `v0.1-w1` / `-w3` 1,200 · `EB` 200 · the four `evt` cells
200/1,200/200/1,200 · `v0.1-w1evt-biased` 1,200 · `ulockstep` **17,350 ALL
LOCKSTEP** · `ghost_launch_law` 200/200 · `check_boot` 220 and 400 ·
`check_ab_sim` 187 · `sm3_s16_score` **1,320/1,371** · `r7_lint` ·
`demux_off_gate` · `test_artifact` **45/45** · `chainflat_relocation_check`
**9/9** · `ucrom_mif_check` · **`core_portlist_lint`** ·
`test_quartus_gate` **287/287** · **`chain_lfsr_gate`'s four signatures
BYTE-IDENTICAL** · **`fz2_replay` scored content IDENTICAL, compared FIELD BY
FIELD BY NAME with the ROW COUNT PRINTED FIRST.**

⚠ **THREE INSTRUMENT HAZARDS ARE REGISTERED IN ADVANCE AND EACH CARRIES ITS
CONTROL:**

1. **`fz2_replay` IS STRUCTURALLY VACUOUS IN A GIT WORKTREE** — `.gitignore:9`
   hides `sw/testdata/campaigns/*/captures/` and it runs **GREEN over ZERO
   rows** (trap #8).  **Both legs run in the MAIN TREE**, the row count is
   printed before the verdict, and a **DIFFERING `tb_sys_receipt`** between the
   legs is the control that the two legs ran different binaries.
2. **`wave16_ladder_cmp.py` REPORTS A MISSING LOG AS *IDENTICAL*** (WAVE 17
   §3.1a, booked as its owed item 9).  This wave does **not** edit that shared
   instrument.  It uses a **NEW** comparator, `sw/wave19_ladder_cmp.py`, which
   is that file plus the `core_portlist_lint` leg plus **one clause counting a
   MISSING LOG as VACUOUS**, and the clause is **demonstrated non-vacuous** by
   deleting a log from a scratch copy and requiring a non-zero exit.  ⚠ **A
   NEW instrument is not a repair of the old one**, and no figure of this wave
   is quoted from `wave16_ladder_cmp.py`.
3. ⚠ **`check_core --suite-dir` TAKES `--waits` AND DEFAULTS TO 0.**  The
   sweeps are spelt `0/1/2/3` in the driver, as WAVE 16 and WAVE 17 spelt them.

### **V-2 — THE REQUIREMENT MUST NOT REGRESS.**

With **no exception** in `nec_test.sdc`, `python3 sw/quartus_gate.py --seeds 5`
**PASSES bars E1-E5 on EVERY draw of BOTH configurations** — 10 of 10.

* Report `worst-of-5@seeds{1,2,3,4,5}` against this tree's **CONTROL 33.00 /
  RETENTION 33.20** and against WAVE 15's predicted **34.48 / 34.41**.
* ⚠ **`core_domain` k = 1.0 and `off_class` EMPTY on every receipt** — that is
  what proves the deletion is still reaching the compiler, in WAVE 13's
  polarity (a draw fitted to an exception would read k = 2.0).
* ⚠ **`grep -c set_multicycle_path` IS THE WRONG INSTRUMENT.**  It reads **2**
  on the correctly-deleted file — the commented DO-NOT-RESTORE record at
  `:237-238`.  **The anchored form
  `grep -cE '^[[:space:]]*set_(multicycle_path|false_path|max_delay)'` reads 0
  on this tree, measured before the edit**, and it is the one that is scored.
  The unanchored form is kept beside it as a **known-wrong control**.
* A **regression** is: any draw failing E1-E5, or `worst-of-5` falling below
  **32.0 MHz** on either configuration.  ⚠ **A `worst-of-5` below 33.00 / 33.20
  but above 32.0 is NOT automatically a revert** — it is a result to report and
  to hand to the coordinator, because V-6's revert condition is the
  **requirement**, not the improvement.  This resolution is written **before any
  draw exists**, because WAVE 16 §3.2 recorded a bar that had none.

### **V-3 — `cutset_lint` PASSES.**

This tree reads **`FAIL — 80 members / 1 violation`**, X4 naming **`['q_ripe_lead_n']`**
and nothing else (measured 2026-09-19).  ARM-B's claim is that it goes
**PASS**, at **81 members / 0 violations** (WAVE 15 §2).  `phase_split_lint`
must also **PASS**, at **157 members / 779 bits / 0 violations** (it reads
**156 / 778 / 0** now).

> ⚠ **IF `cutset_lint` DOES NOT PASS, ARM-B'S MAIN ARGUMENT OVER ARM-A IS GONE
> AND THIS DOCUMENT'S SUCCESSOR MUST SAY SO PLAINLY**, rather than landing
> ARM-B on the timing alone.  **V-6 governs: that is a STOP-AND-REPORT, not an
> automatic revert and not a decision this wave may take.**

### **V-4 — THE FLOP AND ITS SAVE STATE.**

§2's table is the registered prediction.  `ss_lint --core ucore` must exit
**0**.  **Any movement of `SS_VERSION` / `SS_COUNT` / `SS_TAG` is reported as a
STREAM BREAK in the results headline.**  The compiler's per-entity
`dedicated_logic_registers` is the authority on the flop count and is read only
between the two same-SDC sides.

### **V-5 — `E11` TRUE ON EVERY DRAW.**

⚠ Read at **DISTRIBUTION** level as `E11_no_build_stamp`, **not** from each
seed's `bars` dict (trap #9).  ⚠ And the per-seed column resolves **relative**
receipt paths, so it is read with the CWD in the sweep's own tree (WAVE 15 §4,
WAVE 16 §7).

### **V-6 — THE REVERT CONDITION.**

**If V-2 fails, or ANY leg of V-1 moves, THE LANDING DOES NOT HAPPEN**: revert
`hdl/` by explicit path, report, and keep both documents.
**No bar is softened to make a landing possible.**

⚠ **V-3 failing is NOT automatically a revert.**  It removes ARM-B's non-timing
argument; whether ~1.4 MHz alone justifies a flop and a possible stream break is
**the coordinator's call.**  **Report it and stop rather than deciding.**

---

## §4 WHAT I EXPECT, WRITTEN DOWN SO IT CAN BE WRONG

1. **V-1 passes with every leg identical.**  ARM-B is behaviour-identical to
   ARM-A: it moves a select across a register boundary whose two sides the
   split's own `$fatal` already proves equal at every `ce`.
2. **The `ss_lint` "comb/next-state regs skipped" line MOVES, 430 → 432.**
   ⚠ WAVE 17 §3.3 predicted this line would not move and was **wrong**; the
   lesson is taken and the prediction is made in the other direction here.
3. **`cutset_lint` goes PASS at 81 / 0** and `phase_split_lint` at 157 / 779.
4. **`worst-of-5` lands between 33.00 and 34.48 on CONTROL** and between 33.20
   and 34.41 on RETENTION.  ⚠ **This is NOT a prediction that WAVE 15's exact
   figures reproduce.**  WAVE 17 §6 reproduced WAVE 15 to the bitstream byte on
   byte-identical inputs — but these inputs are **not** byte-identical to WAVE
   15's `s1q` arm: that arm sat on `850ef46559`, and this tree carries WAVE 18's
   `sw/` changes and two REP bug fixes.  **`input_manifest` will tell, and it is
   reported either way.**
5. **The design does not shrink.**  ⚠ Recorded as an expectation only —
   `ucore_provenance.md` §74.4a says A&S combinational counts are not
   reproducible run to run, and WAVE 16 §3.3 could not score this.

---

## §5 ⚠⚠ THE FABRIC DEBT — RE-OPENED THE MOMENT THIS LANDS

**FLASH #22 WAS TAKEN ON 2026-09-19 ON EXACTLY THE TREE THIS WAVE CHANGES.**
The bitstream in silicon is built from `d5f5fca539`, whose `hdl/` is
byte-identical to WAVE 17's landing `d3c295cdef`.

> ### **THIS LANDING CHANGES THE EU'S NEXT-STATE STRUCTURE AND ADDS A BIT TO ITS SHADOW.  THE INSTANT IT LANDS, NO FLASH #22 FIGURE MAY BE QUOTED AGAINST THE TREE, AND THE FABRIC CONFIRMATION IS OWED AGAIN.**

`CLAUDE.md`'s correctness target is **SILICON MATCH**.  This wave pays no part
of that debt and **re-opens it on the day it was paid.**

---

## §6 DISCIPLINE, DECLARED IN ADVANCE

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**  No Codex.  No
  nested subagent.
* **THE WAITS BLOCK; THEY DO NOT POLL A TURN.**  One foreground
  `until ! pgrep -x <binary> …` per Quartus stage, **one pattern per call**;
  ⚠ `pgrep -f <script>` self-matches the waiting shell and is not used.
* Drivers carry **`set -u`, NEVER `set -e`** — `quartus_gate` exits non-zero on
  RED and a RED verdict is a RESULT (trap #6).
* ⚠ **`cmd | tail -1; rc=$?` CAPTURES `tail`'s EXIT CODE.**  It broke
  `t30_sweep.sh` for over a year and both WAVE 18 and the coordinator made it
  in the last two days.  **Every rc in this wave is captured to a variable or
  read from `${PIPESTATUS[0]}`.**
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` ARE NEVER USED.**
  **21 tracked files in this working tree are the user's own uncommitted
  work**; they are counted before and after.  **`git add` BY EXPLICIT PATH
  ONLY**, and **`sw/testdata/receipts/*.jsonl` IS NOT COMMITTED** (WAVE 16
  §12.1's miss, WAVE 17's rule) — receipts are committed **BY VALUE** under
  `sw/testdata/wave19/` and `sw/testdata/g6dist/w19-*/`.
* ⚠ `hdl/nec_test_ucore.qsf` is restored by `git checkout -- <that exact path>`
  around every Quartus run.  ⚠ `quartus_map` on the **FSM** revision rewrites
  `hdl/nec_test.qsf` and `.qpf` in place (WAVE 18) — **no FSM revision is
  compiled by this wave.**
* `~/.cache/ucsimt-tmp/wave19/` for every intermediate; **nothing in `/tmp`.**
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL, REPORTED FIRST.**  **Twelve
  instruments in this campaign have returned confident, wrong answers, and one
  could not run at all while the ledger carried a green row for it.**  A gate's
  REGISTERED ROW and its ABILITY TO RUN are two different facts.
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
