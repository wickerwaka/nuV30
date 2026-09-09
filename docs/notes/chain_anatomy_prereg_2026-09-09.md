# THE CHAIN ANATOMY — WAVE 5.  PRE-REGISTRATION.

**Committed BEFORE the first measurement fit.  Instruments at `25f6292560`,
committed before this file.**

**MEASUREMENT ONLY.  NO RTL.  OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO
BITSTREAM PROGRAMMED.  No Codex consulted.  No nested subagent spawned.**

**THIS WAVE PROPOSES NO DESIGN AND LANDS NOTHING.**  It is not a gate, it
writes no receipt, and no figure in it may be quoted as a pass.
`docs/notes/standing_gates.md` §A governs every timing figure it prints.

| | |
|---|---|
| **Tree at entry** | `25f6292560` (`master`); `git status --porcelain hdl/` carries **0 tracked modifications** (12 pre-existing untracked `hdl/quartus_gate_*.log` files, none of this wave's) |
| **Instruments** | `sw/chain_srcmap.py`, `sw/sta_chain_anatomy.tcl`, `sw/run_chain_anatomy.py`, `sw/chain_anat_report.py` — all at `25f6292560` |
| **Configuration** | **NO-EXCEPTION** (the CE multicycle deleted from `hdl/nec_test.sdc` for the measurement fit only, restored in a `finally`), **3 CONTROL seeds + 1 RETENTION** |
| **Tool** | Quartus 17.1.0 Lite Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns |
| **Artifacts** | `sw/testdata/chainanat/` |

---

## §0 WHY THIS WAVE EXISTS

Four waves; three refuted levers.

* **WAVE 2** — the phase split at the chain entry: **RED 22.78**.  The shadow
  was not a cut set; **0 of 103** arrival points named it.
* **WAVE 3** — register the ROW table (L2): **+0.36 MHz, refuted by its own
  bar.**  Finding: **the EU is a LOOP** (`upc_* → ucdecode → ucrom → row →
  decode → operand/EA → the chain → upc_*_n`), ~43.5 ns, and one register bank
  relocates the cut without shortening the loop.
* **WAVE 4** — the split done as a proper cut set, 778 bits: **RED on 20 of
  20**, `worst-of-5` **23.50** (CONTROL) / **23.57** (RETENTION).  Its real
  result: **STAGE 1 = 21.556 ns / 19 levels (fits); STAGE 2 = THE UNROLLED
  CHAIN ALONE = 37.224 ns / 40 levels = 26.86 MHz, BIU-free, 6.0 ns over
  budget by itself.**

**THE CHAIN IS NOW THE WHOLE PROBLEM AND NOBODY HAS MEASURED IT FROM THE
INSIDE.**  The user chose *"measure the chain first"* over three proposed
designs.  **SCOREBOARD: no-exception `worst-of-5` 23.50 MHz against 32.0; the
`ce → ce` arc must reach roughly 29.6 ns.**

### THE STANDING REQUIREMENT (USER RULING 2026-09-08, verbatim)

> **"I don't want custom sdc rules, period."**

The ucore must close with **NO `set_multicycle_path`** in the integrator's SDC.
It is a product requirement, not a trade, and **this wave does not re-open it.**

### THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood.  A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

---

## §1 WHAT THE CHAIN IS

`hdl/rtl/ucore/v30u_eu.sv`, an unrolled bounded loop, `CHAIN_MAX = 7` copies of
`v30u_eu_step.svh`:

```
for (chain = 0; chain < CHAIN_MAX; chain = chain + 4'd1)
    if (!stop) begin
        if ((chain != 4'd0) && !st_zero_ok(st_n)) stop = 1'b1;
        else `include "v30u_eu_step.svh"
    end
```

Each arm STALLS, COMPLETES, or is ZERO-COST and falls through inside the same
edge.  **Only 9 of the 33 states can stand at position ≥ 1** (`st_zero_ok`):
`S_TAKE_OPC` `S_DECODE` `S_DECODE2` `S_EA_CALC` `S_BIND` `S_ENTER` `S_TAIL`
`S_TAIL_POP` `S_INSTR_END`.  **24 of the 33 arms carry `if (chain == 4'd0)`**
and fold out of positions ≥ 1, so **position 0 is FAT and 1-6 are THIN.**
Occupancy census over the golden suite: **24 / 9 / 5 / 3 / 2 / 1**; measured
max depth **6**; `CHAIN_MAX = 7` is 6 plus one spare.

---

## §2 THE SIX QUESTIONS

* **Q1 — THE PER-POSITION PROFILE.**  On the worst `ce → ce` path, how much
  delay and how many levels does EACH chain position contribute?  Position 0
  versus the folded positions, separately and named.  **The headline.**
* **Q2 — THE CUMULATIVE PROFILE.**  For each position boundary `k`, the
  `(upstream ns, downstream ns)` of the WHOLE `ce → ce` arc, front end
  included; the best-balanced `k` and its worse half; **and an explicit YES/NO
  on whether ANY `k` gives both halves ≤ 29.6 ns.**
* **Q3 — WHAT DOMINATES INSIDE A POSITION.**  Which chainable states / case
  arms sit on the critical path and what each costs.
* **Q4 — WHAT IS SHARED ACROSS COPIES.**  Does the fitter CSE across the seven
  copies, or is each genuinely independent?  **With evidence.**
* **Q5 — THE FLOOR.**  If positions 1-6 were free, what would the arc be?
  **Approximated honestly and LABELLED as an approximation.**
* **Q6 — THE BIU ROUND TRIP.**  WAVE 4 found the binding arc LEAVES the EU and
  comes back: `u_biu|q_cnt` → **`q_ripe_lead_n`**, `r7_lint`'s own declared
  UNRESOLVED carrier, 3.7 ns of 41.3.  Where does it enter relative to the
  chain positions, and is it inside or outside the chain's own cone?

---

## §3 THE BARS, REGISTERED HERE BEFORE THE FIRST MEASUREMENT FIT

| bar | statement |
|---|---|
| **E-1** | **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL AND IT IS REPORTED FIRST.**  Each must be demonstrated able to say YES on a case known to be YES.  **A MISS HERE VOIDS THE WAVE.**  Five of this campaign's instruments have produced confident, wrong, VACUOUS nulls; every one was caught only by a positive control, and one (WAVE 2's `sta_phase_split_diag.tcl`) was committed UNRUNNABLE. |
| **E-2** | Q1's per-position attribution is **STABLE ACROSS SEEDS** — all four draws reported.  A profile that differs per draw is a property of the PLACEMENT, not of the tree, and must be reported as such. |
| **E-3** | Q2 is delivered as a **table over every boundary `k`**, with an explicit **YES/NO** on *"does any `k` give both halves ≤ 29.6 ns"*. |
| **E-4** | Q3 **names its top contributors with delays**, or reports that **no single arm dominates**. |
| **E-5** | Q4 answers shared-vs-independent **WITH EVIDENCE, not by assertion**. |
| **E-6** | `git status --porcelain hdl/` shows **NO tracked modification at start and at end**.  **NOTHING under `hdl/` is edited.**  Any SDC change for a measurement fit is reverted before the wave finishes and is never committed. |

### 3.1 THE FIVE POSITIVE CONTROLS THIS WAVE COMMITS TO IN ADVANCE

Registered here so that a control added after seeing a result is visibly not
one of them.

| control | the case known to be YES | what a MISS means |
|---|---|---|
| **PC-0** `chain_srcmap` | the parser must independently recover **33 arms / 24 guarded / 9 unguarded**, and the 9 unguarded names must EQUAL the 9 `st_zero_ok()` states parsed separately out of `v30u_eu.sv` | the parser has not understood the file; **the arm map is REFUSED** (exit 3) and Q3 carries no attribution |
| **PC-1** the resolver | `-through` a `get_pins` collection of a node ON the worst path must return **≥ 1** path; the `get_nodes` collection of the SAME node returns **0** (WAVE 1 §0.2, re-demonstrated LIVE rather than cited) | the classifier cannot say YES; **nothing below may be quoted** |
| **PC-2** the walker | on the worst `ce → ce` path it must reach the **DEST** phase, find **≥ 3** data cells, and reproduce **Quartus's own `-data_delay` to 0.01 ns** | the walker is mis-phasing the path (WAVE 1 §3.0's defect, which reported walker failures as results) |
| **PC-3** the segmenter | a path **FORCED `-through` an `st_zero_ok` pin** — a boundary crossing BY CONSTRUCTION — must segment to **≥ 1 boundary**; the **SAME path under a marker name that does not exist** must segment to **0** | the segmentation is either blind or matching everything |
| **PC-4** the BIU matcher | a path **FORCED `-through` a `|u_biu|` pin** must count **≥ 1** BIU node, with WAVE 4 §6.1 item 1's known-wrong `v30u_biu:` TYPE-prefix test printed beside it | Q6 cannot be answered |

### 3.2 THE SEGMENTER'S BASIS, STATED BEFORE IT IS USED

**The marker is `st_zero_ok`, and it is the SOURCE's own position marker**: the
loop enters every position ≥ 1 through `if ((chain != 4'd0) && !st_zero_ok(st_n))`.
It **survives synthesis as a named node** — measured on this design before the
instrument was written (`sw/testdata/cutset/diag_ctl_seed3.arrivalpoints.txt`
carries `st_zero_ok~14` and `st_zero_ok~16`).  A maximal consecutive run of
arrival points whose base name is `st_n`, `stop` or `st_zero_ok` is **ONE
BOUNDARY**.

⚠ **REGISTERED LIMIT, WRITTEN BEFORE ANY RESULT.**  The count is a **LOWER
BOUND on positions crossed**, not an identification of boundary *i* with chain
position *i*: Quartus may fold a position this path does not enter, a single
position may assign `st_n` more than once (`S_MODRM` does), and the fitter may
duplicate.  **The document will say SEGMENTS, not POSITIONS**, wherever the
distinction can matter.  `CHAIN_MAX = 7` bounds it.

### 3.3 WHAT MAY NOT BE CONCLUDED FROM THIS WAVE

* **Q2's table is an UNCUT-NETLIST ESTIMATE.**  WAVE 1 §6 item 1: after a real
  cut both halves are re-synthesised and the numbers move.  **The one
  calibration point the campaign owns is WAVE 4**, whose realised STAGE 2
  (37.224 ns) is to be compared against WAVE 1's uncut estimate for the same
  seam, and the comparison is to be REPORTED whichever way it comes out.
* **A Quartus net name is not by itself an RTL seam** (WAVE 1 §6 item 1; WAVE
  2 REFUTED that identification for `Decoder28#1`).  Any candidate named in
  *"WHAT THE ANATOMY SAYS"* carries that caveat verbatim.
* **The RETENTION leg is a CROSS-CHECK, not the source of any conclusion**, and
  the document will say so.
* **One green build is not closure** — `standing_gates.md` §A; the same tree
  has drawn 19.42 and 45.91 MHz.  Four draws are not a distribution.

### 3.4 THE HONEST NULL, REGISTERED IN ADVANCE

> **If the honest answer is "no two-way split can work and trimming cannot find
> 7.6 ns either", THE DOCUMENT SAYS THAT.**  It is the most valuable thing this
> wave could report and it is not a failure of the wave.  **No bar is to be
> softened and no candidate manufactured to avoid it.**

---

## §4 DISCIPLINE

* OFFLINE ONLY.  **NO BOARD.  NO FLASH.**  No Codex.  No nested subagents.
* Single-writer guard before any Quartus stage (`pgrep -x`, EXACT binary name).
* `/tmp` discipline: `~/.cache/ucsimt-tmp`, never `/tmp`, for large
  intermediates.
* ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection —
  `get_pins`, and PC-1 re-proves it live.
* ⚠ `string match` on a name carrying a bus index FAILS (`[3]` is a character
  class) — every prefix test is `string first ... == 0`.
* ⚠ `hdl/nec_test_ucore.qsf` is `git checkout --`'d between Quartus runs; WAVE
  4 §7 item 6 lost a sweep to not doing it.
* ⚠ **Do NOT `git add -A hdl/`.**
* A number with no artifact id is not quotable.  Everything is saved under
  `sw/testdata/chainanat/` and named in the results document.
* Commit order: **instruments, then this pre-registration, then the results.**
* **Record what was measured, not what was expected.  Anything unexplained is
  reported as unexplained.**
