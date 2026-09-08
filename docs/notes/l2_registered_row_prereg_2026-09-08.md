# L2 — THE REGISTERED ROW.  PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST EDIT.**  Tree `41c922626a` (`master`).
**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM PROGRAMMED.**
No Codex consulted.  No nested subagent spawned.

Results go in a SEPARATE `docs/notes/l2_registered_row_results_2026-09-08.md`.

---

## §0 THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood. A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

## §0.1 THE STANDING REQUIREMENT THIS WAVE SERVES (USER RULING 2026-09-08)

> **"I don't want custom sdc rules, period."**

The target state is that the ucore closes timing on a downstream FPGA with **no
`set_multicycle_path` and no other core-specific exception in the integrator's
SDC**.  **THE NO-EXCEPTION CONFIGURATION IS THE GOAL STATE.**  A build WITH the
multicycle is a CONTROL, never the objective.  This wave is ONE STEP of the
shortening and **is not expected to finish the job**; the number this wave owes
the campaign is *how far short it leaves us*, in MHz, against 32.0.

The arithmetic that stands: `ce -> ce` is >= 2 fabric clocks and each
cross-phase arc >= 1, both derived contract-free in `hdl/nec_test.sdc`.  So the
binding `ce -> ce` cone must reach ~25 ns (one fabric clock at ~40 MHz) either
by being SHORTENED or by a BALANCED PHASE SPLIT.  WAVE 1 measured it at
**48.245 ns** uncut; WAVE 2's peel left it at **43.731 ns** and was reverted.

---

## §1 THE EDIT, WRITTEN OUT BEFORE IT IS MADE

L1 (`adcone_l1_results_2026-08-13.md`, landed `9bf70f2eec`) registered the
DECODE table on the `ce` edge that makes its address.  L2 is **L1's
construction applied to the SECOND table**, and to nothing else.  Scope is
**L2 ALONE** (user ruling 2026-09-08): no phase split, no other lever, no
bundling.

Today, after L1, in `hdl/rtl/ucore/v30u_eu.sv`:

```verilog
wire [12:0] dec_addr_next = (srst && !ss_we) ? {upc_page_r, upc_opc_r, upc_loc_r[3:2]}
                                             : {upc_page_n, upc_opc_n, upc_loc_n[3:2]};
reg  [9:0]  dec_q;            // L1: ucdecode[dec_addr_next], committed by THE COMMIT
wire [8:0]  dec_bank = dec_q[8:0];
v30u_ucrom u_ucrom (.dec_addr(dec_addr_next), .dec_valid(dec_valid_next),
                    .dec_bank(dec_bank_next),
                    .rom_addr({dec_bank, upc_loc[1:0]}), .rom_word(row));
```

`row` is COMBINATIONAL off `{dec_bank, upc_loc[1:0]}` — **both of which are
already registers**, which is precisely the L1 precondition.

**THE EDIT.**  `u_ucrom`'s `rom_addr` becomes the address the register bank is
ABOUT TO COMMIT, and its word is taken on the edge that commits it:

```verilog
wire [10:0] rom_addr_next = {dec_bank_next,
                             (srst && !ss_we) ? upc_loc_r[1:0] : upc_loc_n[1:0]};
reg  [28:0] row_q;            // L2: ucrom[rom_addr_next], committed by THE COMMIT
wire [28:0] row = row_q;
```

with `row_q <= rom_word_next;` inside THE COMMIT, beside `dec_q`.

### 1.1 WHY IT IS THE SAME VALUE ON EVERY CLOCK

`row(c)` today is `ucrom[{dec_bank(c), upc_loc(c)[1:0]}]`.  Both operands are
registers of the one bank, committed by the one condition
`if (ss_we || srst || ce)`:

* `dec_bank(c) = dec_bank_next(c-1)` — `dec_q` is committed unconditionally
  inside the bank (L1 put the `srst` mirroring inside `dec_addr_next`);
* `upc_loc(c) = [(srst && !ss_we) ? upc_loc_r : upc_loc_n](c-1)`.

So `{dec_bank(c), upc_loc(c)[1:0]}` **is** `rom_addr_next(c-1)`, and
`row_q(c) = ucrom[rom_addr_next(c-1)] = row(c)`.  When the bank does not
commit, neither `dec_q` nor `upc_loc` moves, and `row_q` does not move either
because it is committed by the same condition.

**THIS IS NOT RETIMING ACROSS A CLOCK** and it is **NOT the BANNED M10K
conversion**: an M10K with a registered address AND a registered output puts
the row one clock LATE and costs a cycle; this puts the LOOKUP one clock early
and the OUTPUT on time.

### 1.2 THE FALSIFIER, AND IT IS THE L1 ONE

L1's correctness rests on one grep: `dec_addr_next` must select on the SAME
condition (`srst && !ss_we`) and from the SAME sources as THE COMMIT's own
`upc_*` lines.  **L2's is the same shape and is stated verbatim beside the
code**: `rom_addr_next`'s low two bits must select on `(srst && !ss_we)`
between `upc_loc_r[1:0]` and `upc_loc_n[1:0]`, i.e. character for character
THE COMMIT's `upc_loc` line, and its high nine bits must be `dec_bank_next`,
i.e. character for character what `dec_q`'s commit line stores into
`dec_bank`.  **If a future edit gives `upc_loc` or `dec_q` a third arm, this
line must gain it too.**

### 1.3 THE CLOCK BEFORE THE FIRST COMMIT, NAMED IN ADVANCE

`row_q` powers up 0 where the combinational read would give `ucrom[0]`, which
F44's own probe proves is non-zero.  **It is masked twice over**: `dec_q` also
powers up 0, so `dec_valid` is 0, so `row_nop` is 1, and **every one of the
row's field decodes is taken through `row_nop`** (`v30u_eu.sv:642-657`,
`e_s1 … e_hasc`).  And, as L1 already argued, every harness asserts `srst`
before it observes anything and `srst` forces the commit.
Falsifier: the whole pin-sensitive ladder (L-1).

### 1.4 THE TRAP THAT IS EXPECTED, AND WHICH IS A MEASUREMENT, NOT A BELIEF

`dec_bank_next` is the **combinational** `ucdecode` output at `dec_addr_next`.
So the new `row_q` D-pin path is

```
upc_* -> dec_addr_next -> ucdecode -> dec_bank_next -> ucrom -> row_q
```

— **both ROMs in series again**, on the D pin, which is the chain L1 broke on
the Q side.  The expectation, WHICH IS REASONING FROM SOURCE AND NOT A
MEASUREMENT, is that this trades ~4.3-5.0 ns off the ~43-48 ns binding `ce->ce`
arc for a NEW ~10 ns class that is nowhere near binding.  **L-8 measures it.
If the new class binds, L2 in this form is REFUTED and this wave says so and
reverts** — it does not reshape the construction mid-wave.

A SYNTHESIS CONSEQUENCE IS ALSO EXPECTED AND IS **RECORDED, NOT ENGINEERED**:
`ucdecode` became an M10K at L1 *because its address came straight off a
register*.  A combinational `dec_bank_next` read cannot be served by a block
memory (a memory's address is always registered), so **the M10K inference may
well be lost and ~230 ALMs come back**.  ⚠ **DO NOT "fix" this by registering
`{dec_bank, upc_loc[1:0]}` and letting Quartus infer an address-registered +
output-registered M10K** — that is two clocks of latency and puts the row a
cycle LATE.  That is the BANNED conversion `v30u_ucrom.sv`'s header and L1's
comment both name.  **No memory is forced and none is forbidden; the outcome
is reported.**

### 1.5 SAVE STATE — `row_q` IS **DERIVED** (USER RULING 2026-09-08, STANDING)

`row_q` is a pure function of `dec_bank` and `upc_loc[1:0]`, both SSA-mapped,
recomputed from the same next-state expressions under the same commit
condition.  A restore that writes the mapped addresses reconstructs it ON THAT
VERY EDGE, and mapping it would give one fact two sources of truth — the exact
argument the DERIVED class header in `sw/ss_flop_whitelist_ucore.txt` states,
and the exact ground on which `dec_q` sits there already.  It goes on the
**DERIVED** class beside `dec_q`, with a justification naming the place the
derivation is checkable by eye (`rom_addr_next`, immediately above THE COMMIT).
**`SS_COUNT`, `SS_VERSION` and `SS_TAG` MUST NOT MOVE.**

---

## §2 THE BARS

The bars in §2.1 are the coordinator's and are carried VERBATIM.  §2.2 adds
this wave's own.  **No bar in either section may be softened to make a landing
possible.**

### 2.1 THE REGISTERED BARS

**L-1  PIN IDENTITY — THE LANDING BAR.**  All three:
   (a) `sw/chain_lfsr_gate.py` — the four per-seed signatures BYTE-IDENTICAL to
       the pre-edit run, with `CHAIN_DEPTH_MAX`, `entry_st`, `coincide` and
       every gap count identical too;
   (b) `sw/fz2_replay.py` scored-content sha256 IDENTICAL pre- and post-edit
       (the `tb_sys` binary receipt is the one field that may move, and must);
   (c) the full ladder of L-2 at its registered values.
   ⚠ Take the BEFORE side on the UNEDITED tree first, so the A/B is real.

**L-2  THE LADDER, EVERY LEG AT ITS REGISTERED VALUE:**
   `r7_lint` PASS 0 violations · `check_core --opcodes all --cases 0` 169,000 ·
   `--opcodes 8F.0` 500 · HLT sweeps ⚠ WITH `--waits 0/1/2/3`
   97 · 93 · 45 · 44 = 279/283 · `v0.1-w1`/`-w3` 1,200 each ·
   `v0.1-w1 --opcodes EB` 200 · the four evt cells 200/1,200/200/1,200 ·
   `v0.1-w1evt-biased` 1,200 · `ulockstep --golden all --cases 50` 17,350 ALL
   LOCKSTEP · `ghost_launch_law score` 200/200 · `check_boot --core ucore` 220
   and 400 · `check_ab_sim --core ucore` 187 · `sm3_s16_score --core ucore`
   1,320/1,371 · `demux_off_gate` PASS · `test_artifact` 45/45 ·
   `test_quartus_gate` · `ucrom_mif_check` PASS.
   ⚠ VERIFY EACH AGAINST `standing_gates.md` BEFORE RUNNING.  **Several rows
   there are known STALE on `master`** (WAVE 2 §6.1 found `ss_lint` and
   `test_quartus_gate` disagreeing with measurement).  Where the file and the
   tree disagree, **MEASURE**, report the disagreement as a finding, and do not
   treat a stale row as a failure.

**L-3**  `sw/ss_lint.py --core ucore` exits 0, `SS_COUNT` / `SS_VERSION` /
   `SS_TAG` UNCHANGED, 0 UNMAPPED, whitelist grown by exactly `row_q`'s entry.

**L-4**  `check_core --opcodes all --cases 0` is 169,000/169,000 at `--ce-div
   2, 3, 4 AND 8`; `--ce-div 1` still REFUSED.

**L-5  THE CONTROL BUILD** (the tree's current SDC, multicycle present):
   `sw/quartus_gate.py --seeds 5` PASSES E1-E5 on every draw, both
   configurations.  Report `worst-of-5@seeds{1..5}` against the pre-L2 figure
   (WAVE 1 measured CONTROL 40.09 / 38.99 / 40.83 on seeds 1/2/3).

**L-6  THE GOAL-STATE MEASUREMENT, AND THE POINT OF THE WAVE.**  With the CE
   multicycle DELETED from `nec_test.sdc`, run `--seeds 5` on BOTH
   configurations and report, for every draw: verdict, Fmax, worst setup,
   `core_domain` k and `off_class`.  **This is EXPECTED to be RED and a RED
   result is NOT a failure of this wave** — it is the measurement of how far
   short we are.  **Report the NUMBER and the GAP to 32.0 MHz explicitly.**

**L-7  THE NEW ARC, WHICH IS THE NEXT WAVE'S INPUT.**  On a no-exception fit,
   report the worst `ce -> ce` path: data delay, logic levels, endpoints, and
   its top nets segment by segment.  Say what fraction the ROM head still
   accounts for and what is now the largest single contributor.
   **Re-use WAVE 1's instruments** (`sw/sta_phase_split_scan.tcl`,
   `sw/sta_adcone_anatomy.tcl`) rather than writing new ones, and heed their
   recorded traps: `get_timing_paths -through` SILENTLY IGNORES a `get_nodes`
   collection (use `get_pins`), and `string match` on a register name carrying
   a bus index FAILS because `[3]` is a character class (use a literal
   `[string first $p $s] == 0`).

**L-8  THE NEW D-PIN CLASS.**  Report the worst path ENDING at `row_q`, with
   its delay and levels, and state whether it binds.  **If it does, L2 in this
   form is REFUTED — say so and revert.**

**L-9  NON-VACUITY**: `row_q` is load-bearing (perturbing one bit breaks a
   named gate leg), and the L1-style address-mirroring falsifier is stated and
   demonstrated.

**L-10 THE REVERT CONDITION.**  If ANY leg of L-1/L-2/L-3/L-4 moves, or L-5
   fails, or L-8 shows the new class binding, **THE LANDING DOES NOT HAPPEN.**
   Revert, report what was measured, keep both documents.  **Do not soften a
   bar to make a landing possible.**  **L-6 being RED is NOT a revert
   condition.**

### 2.2 THIS WAVE'S OWN ADDED BARS

**L-6b  THE GOAL-STATE BASELINE, TAKEN ON THE UNEDITED TREE AND TAKEN FIRST.**
   Without it, L-6's number cannot be attributed to anything.  With the CE
   multicycle deleted, `--seeds 5` **CONTROL only**, on the **PRE-L2** tree.
   Reported as `worst-of-5@seeds{1..5}`, and the L-6 CONTROL figure is quoted
   against it as a delta.  ⚠ **RETENTION is NOT baselined** — an added hour of
   compile for a second copy of the same comparison — so **no pre/post delta
   may be quoted for the RETENTION no-exception column**, only its absolute
   figure and its gap to 32.0.
   ⚠ It carries the same map-variance exposure L1 §2.0 records: the AFTER side
   necessarily carries a new map and historical map variance is ~2.3 MHz
   (CONTROL).  A delta smaller than that is reported as being inside it.

**L-11  THE DELETION IS CHECKED, NOT ASSERTED.**  The no-exception sweeps of
   L-6/L-6b patch `hdl/nec_test.sdc` for the duration of the sweep and restore
   it with `git checkout --`; they are a **PROBE, NOT A LANDING**, and their
   receipts will read `-dirty`, which is correct and is stated.  The check that
   the compiler read the deletion is that **`core_domain`'s `SAME` class falls
   from k = 2.0 to k = 1.0**, which — because `quartus_gate.py`'s `nominal`
   table is NOT edited by this wave — appears as a **NON-EMPTY `off_class`
   naming `SAME`**.  A no-exception draw whose `off_class` is EMPTY, or whose
   `SAME` still reads k = 2.0, means the deletion did not reach the compiler
   and its Fmax may not be quoted.

**L-12  NOTHING OUTSIDE THE WAVE MOVES.**  `git status --porcelain hdl/` shows
   0 tracked modifications at the end.  `hdl/nec_test_ucore.qsf` is the one
   declared §70.7 exemption and is restored with `git checkout --` if it moves.
   ⚠ **`git add -A hdl/` IS FORBIDDEN** — it sweeps in the twelve pre-existing
   untracked `quartus_gate_*.log` files (WAVE 2 §10 item 7(b)).  The twenty
   pre-existing tracked modifications outside `hdl/` and `docs/notes/` (a
   repo-wide rename in flight) are NOT this wave's and are not committed by it.

**L-13  THE OWED FABRIC BAR IS RESTATED, NOT DISCHARGED.**  If the M10K
   inference for `ucdecode` survives or a new one appears, L1's owed fabric bar
   (`adcone_l1_results_2026-08-13.md` §3.3) still stands: `ucrom_mif_check` on
   that build's own `db` plus a first-light `check_ab_hw` MATCH 800 ×3 before
   any flash.  **This wave flashes nothing.**

---

## §3 DISCIPLINE, RESTATED SO IT IS SCOREABLE

* OFFLINE ONLY.  **NO BOARD.  NO FLASH.**  Fabric confirmation recorded as owed.
* No Codex consultation.  No nested subagent spawning.
* Single-writer guard before any Quartus stage (`pgrep -x`, EXACT name).
* /tmp discipline: `~/.cache/ucsimt-tmp`, never `/tmp`.
* Receipted binaries rebuilt properly (`python3 sw/check_core.py --build --core
  ucore`); `artifact.require()` asserts-or-dies, `artifact.ensure()` is
  build-if-needed-then-require (CLAUDE.md erratum 2026-08-17).
* ⚠ Verilator `$stop`s on the first procedural `$error`, so one assertion masks
  the next (WAVE 2 §9) — each L-9 clause gets its own probe.
* Truthful commit messages: never assert a gate that is not met.
* **A number with no artifact id is not quotable.**
* Verify a flag exists (`--help`) before trusting a run that used it, AND that
  it is not merely accepted-and-ignored.
* Record what was measured, not what was expected.  Anything unexplained is
  reported as unexplained, not explained after the fact.

---

## §4 THE INSTRUMENTS, NAMED BEFORE THEY ARE RUN

| what | instrument | new? |
|---|---|---|
| the ladder, before and after | `sw/phase_split_ladder.sh` + `sw/phase_split_ladder_diff.py` | WAVE 2's, re-used verbatim |
| pin identity (a) | `sw/chain_lfsr_gate.py` | standing |
| pin identity (b) | `sw/fz2_replay.py` + `sw/phase_split_replay_sha.py` | standing / WAVE 2's |
| save state | `sw/ss_lint.py --core ucore` | standing |
| G6 sweeps | `sw/quartus_gate.py --seeds 5` [`--retention`] | standing |
| the no-exception probe | `sw/l2_noexc_g6.py` — **NEW**, modelled line for line on `sw/phase_split_p8d.py` (patch one file, build, revert in a `finally`), inverted: it DELETES rather than restores, and it does not stop measuring when the first sweep comes back RED (WAVE 2 §10 item 6) | NEW |
| L-7 the arc | `sw/sta_phase_split_scan.tcl`, `sw/sta_adcone_anatomy.tcl` | WAVE 1's, re-used |
| L-8 the D-pin class | `sw/sta_adcone_anatomy.tcl` / `sta_truefmax_probe.tcl` output | re-used |

`sw/l2_noexc_g6.py` is a NEW file rather than an edit to `sw/phase_split_p8d.py`
deliberately: **an `sw/` edit between two halves of one measurement is an edit
that was not measured** (WAVE 2 §10 item 6's own reason for not fixing the
driver in flight).

---

## §5 WHAT THIS WAVE DOES **NOT** DO

* It does not phase-split.  It does not touch `CE_HALF`, the contract, or
  `v30_core.sv`.
* It does not land an SDC change.  `hdl/nec_test.sdc` is byte-identical at the
  end of the wave to what it is at the start.
* It does not re-open the no-exception requirement, argue the exception is
  small or portable, or propose keeping it.
* It does not flash, and it does not quote any fabric figure.
* **It does not claim L2 finishes the job.**  It reports the gap.
