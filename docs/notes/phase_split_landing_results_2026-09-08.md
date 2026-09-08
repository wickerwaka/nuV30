# THE ce/ce_half PHASE-SPLIT LANDING — WAVE 2.  RESULTS, SCORED AS REGISTERED.

Pre-registration **`18c3adc9cf`**
(`docs/notes/phase_split_landing_prereg_2026-09-08.md`), committed **BEFORE THE
FIRST EDIT UNDER `hdl/`**.  WAVE 1 measurement `c89d0bde0c` / `a21195f38f`
(`phase_split_anatomy_2026-09-08.md`).  Closest precedent
`adcone_l1_results_2026-08-13.md` (L1).

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**
No Codex consulted.  No nested subagent spawned.

| | |
|---|---|
| **Tree at entry** | `a21195f38f` (`master`), `git status --porcelain hdl/` clean of tracked modifications |
| **The three edits** | (a) `ebe0c9fcbd` · (b) `c720fbde54` · (c) `d867b3d4cd` |
| **BEFORE artifacts** | `sw/testdata/phasesplit/wave2/before/` |
| **AFTER artifacts** | `sw/testdata/phasesplit/wave2/edit_a/`, `…/edit_b/`, `…/after/` |
| **Tool** | Verilator 5.032; Quartus 17.1.0 Lite Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns |

---

## §0 THE SHADOW REGISTER'S WIDTH — THE FIRST JOB, DONE FIRST

WAVE 1 §6 item 2 declared the phase register's width UNMEASURED and named it
wave 2's first job.  It was measured **before the design was committed to and
before any edit under `hdl/`**, and the measurement is in the pre-registration
(§2), not here, because that is what pre-registering it means.

> **495 BITS, over 76 concatenation entries (66 named signals).**
> Threshold for STOPPING was 600.  **UNDER IT; the wave proceeded.**

Two figures, both true, and they are not the same figure:

| | |
|---|---:|
| `sw/phase_split_width.py`, the conservative upper bound quoted in the prereg | **490 bits / 63 names** |
| THE LANDED SHADOW, once the cut is placed at `stop = 1'b0` and the membership rule is fixed at *"every `_n` or scratch name STAGE 1 ASSIGNS"* | **495 bits / 66 names** |
| for scale, the WHOLE `_n` set — what a shadow of all of stage 1's variable state would have cost | **~832 bits / 139 names** |

The landed set is 5 bits and 3 names LARGER than the prereg's figure, and the
reason is a CORRECTION IN THE SAFE DIRECTION, recorded rather than smoothed
over: the prereg's script intersected *assigned in stage 1* with *mentioned in
stage 2*, which is the right set for "what does stage 2 READ".  It is the wrong
set for what the shadow must carry, because **every `_n` is COMMITTED**, so a
`_n` stage 1 assigns and stage 2 never mentions must still reach the commit
through the shadow or its stage-1 value is lost.  The membership rule is
therefore *assigned in stage 1*, full stop, and it added
`first_pop_seen_n`, `poll_pipe_n`, `rd_age0_n` and `rdh_byte`
(6 bits) while the cut's move past `stop = 1'b0` removed `stop` (1 bit).
`sw/phase_split_lint.py` checks the landed number against the RTL's own `S1W`.

**Had the simple thing been done — shadow the whole `_n` set — the wave would
have STOPPED at 832 bits.**  The crossing set is 59 % of it.

---

## §1 THE VERDICT TABLE

| bar | verdict |
|---|---|
| **P-1** the landing bar (G6 `--seeds 5`, E1-E5 on every draw, both configurations) | **FAILED — `RED` on TEN of TEN draws.  CONTROL `worst-of-5` **22.78**, RETENTION **21.61**, against a 32.0 MHz bar.  See §11.** |
| **P-2** the exception is GONE, and that is CHECKED | **MET** — `nec_test.sdc` carries ZERO uncommented `set_multicycle_path`, emits no *CE multicycle* info line, and every receipt reports `SAME` at **k = 1.0000** with an EMPTY `off_class` |
| **P-3** CONTROL `worst-of-5@seeds{1..5}` in [34.0, 40.0] MHz | **REFUTED PREDICTION — measured 22.78, BELOW the interval's floor by 11.22 MHz.**  Reported as registered, not re-derived |
| **P-4** pin identity — chain_lfsr signatures, fz2_replay sha256, the ladder | **MET, on all three legs** |
| **P-5** save state does not move | **MET** |
| **P-6** the ladder at its registered values | **MET, with two registered movers and one `standing_gates.md` disagreement reported below** |
| **P-7** divisor independence at div 2, 3, 4, 8; div 1 still REFUSED | **MET** |
| **P-8** non-vacuity on all four | **MET, 4 of 4** |
| **P-10** (added) the phase-stability premise asserted at runtime | **MET, and it CAUGHT ONE** |
| **P-11** (added) no live input in stage 1 | **MET, audited by gate not by eye** |
| **P-12** (added) the interface change reported in both directions | **MET** |

---

## §2 WHAT WAS LANDED

**STAGE 1** (evaluated `ce -> ce_half`, captured on `ce_half`): the microcode
row read, the row-field decode, the operand / queue-state select, the EA add,
the completion sampling and the recognition arm — `v30u_eu.sv`'s blocks (a)-(f).
**STAGE 2** (evaluated `ce_half -> ce`, captured on `ce`): the whole unrolled
chain loop, block (g)'s pin pipelines, and the `dec_addr_next` tail.

**THE CUT IS WAVE 1's NAMED ONE** — `Decoder28#1`, the ENTRY to
`for (chain = 0; chain < CHAIN_MAX; ...)`, measured at 46.8/53.2 · 49.8/50.2 ·
46.1/53.9 · 46.1/53.9 per cent over four draws.  It was not re-scoped after
seeing a result.

### 2.1 THE FOUR THINGS THAT ARE NOT MECHANICAL

**(a) `CE_HALF` IS AN UNCONDITIONAL PORT NOW** (prereg §4, P-12).  It lived
under `V30_MUXED_AD` on the reading that its only consumer was
`v30u_biu|t1_half2`.  That reading is false after the split: `ce_half` is the
EU's stage-1 capture edge, i.e. CORE CLOCKING, orthogonal to the bus shape.
`AD`, `AD_OE` and `DATA_I` are untouched.  Reported in both directions:
`hdl/tb/tb_demux_min.sv` now DRIVES `ce_half` at the CPU cycle's midpoint, and
`sw/demux_off_gate.py`'s GONE leg LOSES its `CE_HALF` clause — splicing that pin
in now SUCCEEDS, so asserting that it fails would be asserting something false.
Its `AD` and `AD_OE` clauses are untouched and still REFUSE naming their pins,
which is what keeps the leg non-vacuous (measured: 2/2 REFUSED, plus the ON
control).

**(b) STAGE 1 RUNS UNCONDITIONALLY, AND THE `ss_we` ARM RE-RUNS THE BLOCK'S
HEAD.**  This is the answer to RULING 2, and it is **option (i): NO RULE IS
WIDENED.**  The head moved VERBATIM into `hdl/rtl/ucore/v30u_eu_preload.svh` and
is included twice.

* The shadow's commit condition is **`(ss_we || srst || ce_half)`** — the
  register bank's own condition with `ce_half` in place of `ce`.
* `ss_we` is in it because the **A2 RESUME-DRAIN EDGE** is where the shadow is
  re-derived: the resume contract ALREADY requires a clock on which `ss_we_q` is
  still high and every stream word has landed, and stage 1 evaluated there is
  stage 1 of the FULLY RESTORED machine.  That is *reconstructed on that very
  edge*, verbatim, and the edge is NAMED.
* Running stage 1 under `ss_we` would otherwise corrupt a restore, because an
  `ss_we` clock commits `_n` for EVERY register and a `_n` the stream has not
  addressed yet must still read as its own flop.  Re-running the preload at the
  head of the `ss_we` arm undoes stage 1 exactly, so that arm is byte-identical
  to the pre-split one.
* **`srst` is in it because of the FIRST `ce` AFTER RESET**, which the brief
  asks to be handled explicitly.  `v30_core.sv`'s `ce_half_since_ce` starts
  ASSERTED so a run's first `CE` is not an S-1 violation, which means no
  `CE_HALF` need have preceded it and the shadow might never have been
  captured.  With `srst` in the commit condition the shadow tracks stage 1 on
  EVERY reset clock, and RESET is asserted at the head of every run, so it is
  current at that first `ce`.  **No `_r` mirror is written**: stage 1 evaluated
  on the reset state IS the value wanted, where a mirror would be a second
  source of truth for it.

**(c) `poll_pipe_n` MOVED FROM BLOCK (a) TO BLOCK (g), AND IT IS REQUIRED.**
`pin_poll_n` is a live asynchronous input; a pin may not be captured on
`ce_half`.  Block (g) — *"THE PIN PIPELINES, ADVANCED AT THE END OF THE EDGE"* —
is where `int_p_n` and `nmi_p_n` have always been advanced, and it is the same
clock: nothing between the two positions reads `poll_pipe_n`, and the module's
other readers read the FLOP.  **It was the only one of the three pin pipelines
advanced at the START of the edge**, and the split is what made that visible.
`ulockstep`'s `POLL.REL` form reads 50/50 LOCKSTEP after the move, as before.

**(d) THE PACK AND THE UNPACK ARE ONE LIST, WRITTEN TWICE AND CHECKED.**  At
THE CUT, `s1_bus = { … };` and `{ … } = s1q;` carry CHARACTER-IDENTICAL
concatenations.  That identity is the whole of the correctness argument and it
is a GATE, not a comment: **`sw/phase_split_lint.py`** (new, standing, 0.1 s)
fails unless the two lists match, their summed declared widths equal `S1W`,
every member is declared, `v30u_eu_preload.svh` is included exactly twice with
the second immediately before the `ss_write` include, the commit condition is
`(ss_we || srst || ce_half)`, and NO LIVE INPUT appears in stage 1.

```
  pack sites   : 1
  unpack sites : 1
  members      : 76
  summed width : 495   S1W = 495
  preload incl : 2
  live-in-stage1: none
=== phase_split_lint: PASS   (76 members / 495 bits / 0 violations)
```

---

## §3 P-10 — THE PREMISE IS ASSERTED, NOT ARGUED, AND IT CAUGHT ONE

The theorem's precondition is that every stage-1 output is unchanged between
`ce_half(n)` and `ce(n+1)`.  `v30u_eu.sv` carries, `ifndef SYNTHESIS`:

```
if (ce && !srst && !ss_we && (s1q !== s1_bus))
    $fatal(1, "v30u_eu: PHASE-SPLIT PREMISE VIOLATED …");
```

Stage 1 is re-evaluated live at every `ce` and must equal the shadow captured at
`ce_half`.  **It did not fire once** across 169,000 goldens at four divisors,
17,350 `ulockstep` scenarios, 283 HLT-sweep cells, the 1,371-cell S16 walk, the
four `evt` cells, `check_boot` 220 and 400, `check_ab_sim`'s 187 rows and
4 × 400,000 `chain_lfsr` clocks of arbitrary bytes with LFSR memory, LFSR
`READY` and LFSR `INT`.

**THAT IS A MEASUREMENT, NOT AN INFERENCE, AND IT IS WHY P-4's BYTE-IDENTITY
MEANS "THE PREMISE HELD" RATHER THAN "NO TEST REACHED THE DIFFERENCE".**

⚠ **AND IT IS NOT VACUOUS: IT IS WHAT FOUND `poll_pipe_n`.**  The first form of
the peel left `pin_poll_n`'s shift in stage 1 — the design's own membership rule
put `poll_pipe_n` in the shadow — and the audit that P-11 became was written
because of it.  §2.1(c).

---

## §4 P-11 — NO LIVE INPUT IN STAGE 1, AUDITED BY GATE

`phase_split_lint.py`'s clause **L7** greps the region between the preload and
THE CUT for the module's live inputs plus `r7_lint`'s one declared exception and
its two declared unresolved carriers:

| signal | why it is on the list | in stage 1? |
|---|---|---|
| `pin_int` | asynchronous input | no (block (g)) |
| `pin_nmi` | asynchronous input | no (block (g)) |
| `pin_poll_n` | asynchronous input | **no — MOVED to block (g) by this landing** |
| `eu_rd_edge` | `r7_lint`'s ONE declared live-`READY` carrier | no (it is on `psw`'s `D` pin, R7′) |
| `eu_rd_edge_d` | same cone | no |
| `eu_slot_busy_n` | `r7_lint`'s declared UNRESOLVED carrier | no (stage 2 only) |
| `q_ripe_lead_n` | `r7_lint`'s declared UNRESOLVED carrier | no (stage 2 only) |

`live-in-stage1: none`.  Recorded as a grep with its result, and it is a
standing gate rather than a one-off, which is the difference between an audit
and a note.

⚠ **THE THREE BIU SIGNALS STAGE 1 *DOES* READ ARE REGISTER-ONLY BY THE BIU's OWN
DECLARATION, AND THAT IS WHY THEY ARE NOT ON THE LIST.**  `eu_rdata_n` is
`r_rd_land`, a register (`v30u_biu.sv:917`, *"`rd_land` is written by the read
path ONLY, so `eu_rdata_n` stays register-only lookahead"*); `eu_rd_done_n` and
`eu_wr_done_n` are `(r_done_ctr == 2'd1)` gated by `r_done_wr`, both registers
(*"the pulse is known one clock ahead FROM THE REGISTERS"*).  `r7_lint` PASSES
with 1 carrier / 3 tainted / 51 `stop` sites, unchanged, which is the standing
check that no fourth one appeared.

---

## §5 P-4 — PIN IDENTITY.  THE PROOF THAT NOTHING MOVED.

### 5.1 (a) `chain_lfsr_gate` — **BYTE-IDENTICAL, 4 OF 4**

The load-bearing gate for this wave: its CE train is built to the contract and
nothing narrower, so it exercises the ADJACENT `ce`/`ce_half` case the split's
worst budget assumes.  4 seeds × 400,000 fabric clocks of ARBITRARY BYTES.

| seed | before | after |
|---|---|---|
| 1 | `1d01c9b269ffaa94` | **`1d01c9b269ffaa94`** |
| 2 | `b39b040a98b28e5d` | **`b39b040a98b28e5d`** |
| 3 | `0997b773cd99c030` | **`0997b773cd99c030`** |
| 4 | `d05b6c3c3d9fbe78` | **`d05b6c3c3d9fbe78`** |

`CHAIN_DEPTH_MAX` 6 · `entry_st` 25 · `coincide` 0 · every `ce_clocks` · **all
eight gap counts** · and the whole live-cycle census (`fpops`, `qpops`, `INTA`,
`IOR`, `IOW`, `HALT`, `CODE`, `MEMR`, `MEMW`) **identical on every seed** —
`diff` over the three row kinds is EMPTY.  The Verilator receipt moved
`ed97205b2049a08a…` → `87af9ef616c4c9dc…`, **which it must**.

### 5.2 (b) `fz2_replay` — **SCORED-CONTENT sha256 IDENTICAL**

`--all-failures --pass-sample 200 --leg ret`, 305 seeds on `tb_sys ret`:

```
before  scored-content sha256 de949fd373ed77de7f7d980a1728538de1b6ddaf6e200a9e61ba69bd1a8b2942
        tb_sys receipt 348a83b12a629aea…
after   scored-content sha256 de949fd373ed77de7f7d980a1728538de1b6ddaf6e200a9e61ba69bd1a8b2942
        tb_sys receipt 07410940b89ff6a3…
SCORED CONTENT: IDENTICAL     tb_sys receipt: MOVED, as it must
```

`sw/phase_split_replay_sha.py` hashes `rows` and `tables` — the SCORED content —
and prints the artefact identity beside it, so the two facts are one string.

⚠ **BOTH LEGS RAN WITH `--no-fabric-era-guard`, AND THAT IS STATED RATHER THAN
WORKED AROUND.**  The guard REFUSED on the **pre-edit** tree already: `hdl/` has
moved since FLASH #20's bitstream, so this tree was a cross-era read *before
this wave touched it*.  **What these two legs measure is BEFORE vs AFTER on ONE
TREE.  They say nothing about fabric, and no fabric claim is made from them.**
The same caveat L1 recorded, for the same reason.

### 5.3 (c) THE LADDER — 29 of 31 SAME, and BOTH movers are registered

`sw/phase_split_ladder_diff.py sw/testdata/phasesplit/wave2/before …/edit_b`

*See §6.*  The two that moved:

* **`ss_lint`** — `ss_flopcensus` 228 → **229** architectural flops, whitelist
  3 → **4** entries.  **That is P-5's registered "the whitelist grown by exactly
  the shadow's entry"**, not a regression.
* **`demux_off_gate`** — its own summary line, *"three muxed ports"* → *"two"*.
  Edit (a)'s registered P-12 change, and a re-wording, not a measurement.

---

## §6 P-6 — THE LADDER, LEG BY LEG

Measured on the UNEDITED tree (`before/`, ucore binary receipt
`8109d500651f4501…`) and on the landed one (`edit_b/`, receipt
`2e46b852d72d6b10…`), plus a confirming run after the SDC deletion (`after/`).

| leg | registered | before | after |
|---|---|---|---|
| `r7_lint` | PASS, 0 violations | PASS — 1 carrier / 3 tainted / 51 `stop` | **same** |
| `check_core --opcodes all --cases 0` | 169,000/169,000 | 169,000/169,000 | **169,000/169,000** |
| `check_core --opcodes 8F.0 --cases 0` | 500/500 | 500/500 | **500/500** |
| HLT sweeps, `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = 279/283 | 97 · 93 · 45 · 44 | **97 · 93 · 45 · 44 = 279/283** |
| `v0.1-w1` / `-w3` | 1,200 / 1,200 | 1,200 / 1,200 | **1,200 / 1,200** |
| `v0.1-w1 --opcodes EB` | 200 | 200 | **200** |
| the four `evt` cells w0/w1/w2/w3 | 200 / 1,200 / 200 / 1,200 | same | **200 / 1,200 / 200 / 1,200** |
| `v0.1-w1evt-biased` | 1,200 | 1,200 | **1,200** |
| `ulockstep --golden all --cases 50` | 17,350 ALL LOCKSTEP | 17,350/17,350 | **17,350/17,350, ALL CASES LOCKSTEP** |
| `ghost_launch_law score` | 200/200 | 200/200 | **200/200 = 100.0 %** |
| `check_boot --core ucore` | 220 and 400 | MATCH 220, MATCH 400 | **MATCH over 220 and over 400 rows** |
| `check_ab_sim --core ucore` | MATCH 187 rows | MATCH 187 | **MATCH over 187 rows** |
| `sm3_s16_score --core ucore` | 1,320/1,371 | 1,320/1,371 | **1,320/1,371**, census `busstat_other` 24 · `ARCH` 27 |
| `demux_off_gate` | PASS, 3 legs | PASS | **PASS, 3 legs** (P-12 wording; `FPOPS` 2,742 · `BS_KINDS` 7 · `WRITES` 1,390 · `ADDR_MOVES` 7,729) |
| `test_artifact` | 45/45 | 45/45 | **45/45** |
| `test_quartus_gate` | 254/254 (255 with a build tree) | **255/255** | **255/255** |
| `ucrom_mif_check` | PASS | PASS | **PASS** |
| `ss_lint --core ucore` | see P-5 | 232 / 228 flops / 3 wl | **232 / 229 flops / 4 wl** |

### 6.1 ⚠ THREE DISAGREEMENTS WITH `standing_gates.md`, REPORTED AS FINDINGS

The prereg's own instruction is that where its list and `standing_gates.md`
disagree, `standing_gates.md` governs and the disagreement is itself a finding.
Three exist, and **all three are `standing_gates.md` being STALE ON `master`,
none of them caused by this wave** — every one was measured on the UNEDITED tree
before the first edit:

1. **`test_quartus_gate` reads 255/255 on this tree**, with a build tree on
   disk.  `standing_gates.md` line 494 registers **200/200**; CLAUDE.md's quick
   reference registers **254 (255 with a build tree)**.  The measured figure
   agrees with CLAUDE.md and not with `standing_gates.md`.  **`standing_gates.md`
   line 494 is stale.**
2. **`ss_lint` reads `SS_COUNT` 232 / 228 flops / 3 whitelist entries on this
   tree.**  `standing_gates.md` §B registers **226 addresses / 214 flops /
   `SS_VERSION` 0x8D / `SS_TAG` 0x8DE2** — the `fuzz-v2-on-relanding` figures.
   `master`'s `v30u_ss_pkg.sv` carries **`SS_VERSION` 0x8F** ("ucore map v15,
   operand-width tags") and `SS_COUNT` 232, so `SS_TAG` is **0x8FE8**.
   **`standing_gates.md`'s row is a different branch's.**
3. **The four `evt` cells, `v0.1-w1evt-biased`, `check_boot 400` and
   `check_ab_sim` are not carried as rows in `standing_gates.md` §B's ucore
   table at all** — they are in CLAUDE.md's quick reference.  Not a
   disagreement, a gap, and named so it is not mistaken for one.

**None of the three is this wave's to fix and none is fixed here.**  They are
booked in §10.

---

## §7 P-5 — SAVE STATE DOES NOT MOVE

```
ss_lint: PASS (109x2 BIU + 122x2 EU + tag = 232; constants OK)
BIU: 91 architectural flops -> 91 SSA-mapped, 0 whitelisted, 0 UNMAPPED
EU : 138 architectural flops -> 134 SSA-mapped, 4 whitelisted, 0 UNMAPPED
ss_flopcensus: PASS (229 architectural flops, all SSA-mapped or whitelisted; 4 whitelist entries)
```

| | before | after |
|---|---:|---:|
| `SS_COUNT` | 232 | **232 — UNCHANGED** |
| `SS_VERSION` | 0x8F | **0x8F — UNCHANGED** |
| `SS_TAG` | 0x8FE8 | **0x8FE8 — UNCHANGED** |
| UNMAPPED | 0 | **0** |
| whitelist entries | 3 | **4 — grown by EXACTLY the shadow's entry** |
| EU architectural flops | 137 | 138 |

**`v30u_ss_pkg.sv` IS UNTOUCHED BY THIS WAVE.**  The shadow is on
`sw/ss_flop_whitelist_ucore.txt`'s **DERIVED** class beside L1's `dec_q`, and
the entry names the place the derivation is checkable by eye (THE CUT's two
character-identical concatenations) and the edge it is reconstructed on (the A2
resume-drain clock).  **RULING 2's option (i) — no rule is widened, and the
DERIVED-class header is untouched.**

**P-5 MET.**  ⚠ Note the census's *architectural flop* count is a count of
REGISTER NAMES, not bits: the 495-bit shadow is one name.

---

## §8 P-7 — DIVISOR INDEPENDENCE

The split makes S-1 load-bearing for the EU and not only the BIU, so this is a
bar and no longer a cross-check.

| `--ce-div` | before | after |
|---|---|---|
| 2 | 169,000/169,000 | **169,000/169,000** |
| 3 | 169,000/169,000 | **169,000/169,000** |
| 4 (default) | 169,000/169,000 | **169,000/169,000** |
| 8 | 169,000/169,000 | **169,000/169,000** |
| **1** | **REFUSED**, exit 2, clause cited | **REFUSED**, exit 2, clause cited |

**P-7 MET.**  Note div 2 is the ADJACENT train — M72's catch-up burst rate — and
it is the shape the shadow's one-`ce_half` guarantee is thinnest on.

---

## §9 P-8 — NON-VACUITY, DEMONSTRATED AND RECORDED

`sw/phase_split_nonvacuity.py` (new, standing).  Each case CONSTRUCTS the
condition by a temporary patch, rebuilds, runs, and REVERTS with
`git checkout --`; the tree is verified clean at the end (`hdl/ restored:
CLEAN`).

| case | probe | result |
|---|---|---|
| **(a) A1** `SS_WE && CE_HALF` | let `CE_HALF` run through the SS park (drop the TB's `!ss_park` term) | **FIRED** — *"SS_WE asserted while CE_HALF high (core not frozen — the phase-split shadow would re-capture from a half-restored register file)"* |
| **(a) A2** `CE_HALF && ss_we_q` | the same probe with **A1 silenced so A2 can be reached** | **FIRED** — *"CE_HALF resumed with SS command staging undrained"* |
| **(b)** S-1 `$fatal`, naming the EU | withhold `CE_HALF` entirely (`ce_half <= 1'b0`) | **FIRED**, and the message contains **"STAGE-1 capture edge"** — i.e. it names the EU's dependence, not only `t1_half2`/`ad_oe_data` |
| **(c)** the shadow is LOAD-BEARING | flip ONE BIT: `{ … } = s1q ^ 495'd1` | **FIRED** — `check_core --opcodes 90 --cases 5` falls **5/5 → 3/5**, `first-div: (3, 'qop')×2`, `row 3 qop: exp 'F' got '-'` |
| **(d)** the multicycle's deletion is what changes the timing | a CONTROL build with the multicycle RESTORED | **FIRED — see §11.5** |

⚠ **A1 AND A2 NEED TWO PROBES AND THE REASON IS ITSELF A FINDING: VERILATOR
TREATS A PROCEDURAL `$error` AS AN ASSERTION AND `$stop`s ON THE FIRST ONE.**  A
single probe raising `CE_HALF` across the whole park fires A1 and the run ends
there, so A2 would have read "DID NOT FIRE" for a reason with nothing to do with
A2.  Silencing the neighbouring clause is the only honest way to show the
neighbour is reachable; A2's own clause is untouched and is what fires.  This is
recorded because a naive single-probe run would have reported a MISS that was an
instrument artefact.

---

## §10 WHAT IS OWED, AND WHAT IS BOOKED RATHER THAN TAKEN

1. **A FABRIC CONFIRMATION IS OWED AND UNPAID.**  Nothing here has been on a
   board and no bitstream was programmed.  The phase split moves WHEN a value
   is captured inside the core, and the AD output latch is machine state with a
   functional consumer (F58), so a first-light `check_ab_hw` MATCH 800 ×3 plus
   an `x1_fabric` column is owed before any figure from this tree is quoted
   against silicon.  **A later wave's debt, recorded as such.**
2. **`standing_gates.md` §A/§B carries three stale or missing ucore rows**
   (§6.1): `test_quartus_gate` at 200/200, the `ss_lint` row at the
   `fuzz-v2-on-relanding` 226/214/0x8D figures, and no rows for the four `evt`
   cells / `w1evt-biased` / `check_boot 400` / `check_ab_sim` in the ucore
   table.  Measured on the UNEDITED tree, so none is this wave's doing.
   **BOOKED, not fixed** — a coordinator-territory edit.
3. **`--ss-sweep` IS NOT ON THIS WAVE'S REGISTERED LADDER AND WAS NOT SCORED AS
   A BAR.**  The design's SS behaviour is argued in §2.1(b) and the two new
   `$error` clauses are its guards, but the G5 save-state sweep is not one of
   P-6's legs and no claim is made from it.  **BOOKED: score `check_core
   --ss-sweep` before the next flash**, because the resume path is the one place
   the shadow's derivation is not covered by the P-10 assert (which excludes
   `ss_we` by construction).
4. **THE L2 LEVER IS NOT BUNDLED** (RULING 3).  The `ucrom` registration is
   untouched.
5. **THE SHADOW'S AREA COST IS WHATEVER G6 MEASURED AND IS NOT PREDICTED
   ANYWHERE.**  §11's ALM column is the only statement about it: 10,011-10,103
   ALMs (24 %) across all ten draws, and the P-8(d) control at 10,130.
6. **`sw/run_phase_split_g6.sh` STOPS MEASURING ON THE FIRST BAD MEASUREMENT.**
   `set -e` plus `quartus_gate --seeds N`'s non-zero exit on a RED distribution
   aborted the driver after the CONTROL sweep; the RETENTION sweep had to be
   launched by hand.  A one-word fix (`|| true` on the first invocation, or
   `set +e` around the pair) and it is NOT taken here, because an `sw/` edit
   between two halves of one measurement is an edit that was not measured.
   **BOOKED**, and the same shape as this repo's other accepted-and-ignored
   findings: the tool did what it was told and what it was told was wrong.
7. **`sw/phase_split_lint.py` EXITS 2 ("COULD NOT RUN") ON THE REVERTED TREE**
   and is deliberately NOT registered in `standing_gates.md`.  It gates the
   split, and the split is not in the tree; a lint that passed here would pass
   vacuously.  It is retained for the next attempt.

---

## §11 P-1 / P-2 / P-3 — G6, `--seeds 5`, BOTH CONFIGURATIONS

### 11.1 ⚠⚠⚠ **P-1 IS FAILED.  THE SPLIT DOES NOT CLOSE.**

**CONTROL — `worst-of-5@seeds{1,2,3,4,5}` = 22.78 MHz.  VERDICT `RED`.**
Record `sw/testdata/g6dist/phasesplit-w2-control-n5/distribution.json`, id
**`d2638a1a6cbc14e0…`**; 89-file input manifest **`ffb47fa31c18045e…`**;
E7 `n_moved` 1 / `moved_offending` 0 (the one declared §70.7 exemption,
`hdl/nec_test_ucore.qsf`), E8 5/5 seeds honoured, E10 N = 5.

| seed | Fmax | worst setup | ALMs | core class | k | `off_class` | receipt |
|---|---:|---:|---:|---|---:|---|---|
| 1 | **22.87** | **-12.481** | 10,039 | `SAME` | 1.0000 | EMPTY | `1031c163fcd60e8e…` |
| **2** | **22.78** | **-12.650** | 10,048 | `SAME` | 1.0000 | EMPTY | `1d8a708f5ada9f1a…` |
| 3 | **22.89** | **-12.445** | 10,103 | `SAME` | 1.0000 | EMPTY | `7f64d1ec481a41a0…` |
| 4 | **23.37** | **-11.531** | 10,045 | `SAME` | 1.0000 | EMPTY | `d02ff223e509806f…` |
| 5 | **22.78** | **-12.648** | 10,043 | `SAME` | 1.0000 | EMPTY | `308ead5e123ddbd2…` |

> worst 22.78 · median 22.87 · best 23.37 · spread **0.59** — and the whole-design
> figure EQUALS the core-domain figure on every draw, because `SAME` binds the
> whole design.  Every draw carries a setup TNS violation on `divclk`
> (seed 1: **-5,785.535**); E5 therefore fails on all five as well as E3 and E4.
> ALMs **10,039-10,103 (24 %)**, against WAVE 1's pre-split tree — the shadow's
> 495 bits are visible in `fit_registers`, not in the ALM percentage.

**RETENTION — `worst-of-5@seeds{1,2,3,4,5}` = 21.61 MHz.  VERDICT `RED`.**
Record `sw/testdata/g6dist/phasesplit-w2-retention-n5/distribution.json`, id
**`83ac64b7154f5e1c…`**; same 89-file input manifest **`ffb47fa31c18045e…`** as the CONTROL sweep, which is
the check that the two configurations differ by the `--verilog_macro` and
nothing else.  The receipt self-labels **RETENTION (X1_AD_RETENTION=1)**.

| seed | Fmax | worst setup | ALMs | core class | k | `off_class` | receipt |
|---|---:|---:|---:|---|---:|---|---|
| 1 | **22.57** | **-13.060** | 10,075 | `SAME` | 1.0000 | EMPTY | `23a28fa692b2535c…` |
| 2 | **21.63** | **-14.982** | 10,035 | `SAME` | 1.0000 | EMPTY | `54ea126da1224ca8…` |
| 3 | **21.70** | **-14.834** | 10,011 | `SAME` | 1.0000 | EMPTY | `73bd5c2d9634f723…` |
| **4** | **21.61** | **-15.017** | 10,038 | `SAME` | 1.0000 | EMPTY | `bb9598516eaf3eb6…` |
| 5 | **22.57** | **-13.052** | 10,054 | `SAME` | 1.0000 | EMPTY | `b6bde06ecc1e5158…` |

> worst 21.61 · median 21.7 · best 22.57.  **FIVE OF FIVE `RED` HERE TOO**, and the
> figures are 1.2 MHz BELOW the CONTROL sweep's, which is the ordinary
> retention-vs-control sign and not a finding.  `SAME` binds on every draw at
> `k = 1.0000` with an EMPTY `off_class`, exactly as on CONTROL.
>
> ⚠ **THE RETENTION SWEEP HAD TO BE LAUNCHED BY HAND, AND THAT IS AN INSTRUMENT
> FINDING WORTH KEEPING.**  `sw/run_phase_split_g6.sh` carries `set -e` and
> `quartus_gate --seeds 5` exits NON-ZERO on a RED distribution, so the CONTROL
> sweep's RED **aborted the driver before the retention leg ran**.  A driver
> that stops measuring the moment the first measurement is bad is a driver that
> reports less the more there is to report.  Booked in §10.

**P-1 asked for E1-E5 on EVERY draw — Fmax ≥ 32.0 MHz, worst setup > 0, TNS
0.000 setup AND hold on every domain — and said "a single failing draw fails
P-1".**  **TEN OF TEN DRAWS ARE `RED` — five CONTROL and five RETENTION**, every one failing E3 (Fmax ≥ 32.0),
E4 (worst setup > 0) and E5 (TNS 0.000) together, by **9.4 MHz and 11.5-12.7 ns**.
This is not a marginal miss and it is not a draw-to-draw question: the spread
over five seeds is **0.59 MHz**.

**P-3 asked for CONTROL `worst-of-5@seeds{1..5}` in [34.0, 40.0] MHz.**
**MEASURED: 22.78 MHz.  The interval's floor is 34.0.  MISSED BY 11.22 MHz.**
**It is reported as a REFUTED PREDICTION and is NOT re-derived.**  The
pre-split HEAD figure P-3 named for comparison is 38.99 (worst of WAVE 1's
three CONTROL draws, `phase_split_anatomy_2026-09-08.md` §1).

### 11.2 P-2 IS **MET**, AND IT IS THE ONE BAR THAT MATTERED FOR DIAGNOSIS

The exception really is gone and the compiler really did read that:

* `hdl/nec_test.sdc` contains **ZERO uncommented `set_multicycle_path`** and
  **zero `set_false_path`** (the only surviving matches are inside the
  historical quotation in the deletion banner).
* No *"CE multicycle"* info line is emitted; the surviving `post_message` says
  *"NO ce->ce exception — N ce-gated v30u core registers are checked
  SINGLE-CYCLE"*.
* **Every receipt reports `SAME` at `k = 1.0000` with an EMPTY `off_class`.**
  A receipt still showing k = 2 would have failed P-2 however good its Fmax;
  none does.

**P-2 being MET is what makes P-1's failure interpretable rather than
ambiguous**: the 22.8-22.9 MHz figures are the honest single-cycle cost of the
arc as it now stands, not an artefact of an exception the compiler ignored.

### 11.3 THE DIAGNOSIS — **THE CUT DID NOT DIVIDE THE BINDING ARC**, AND WHY

The binding path is IDENTICAL in kind on every draw:

```
from : …|v30u_eu:u_eu|v30u_ucrom:u_ucrom|altsyncram:ucdecode_rtl_0|
       altsyncram_t2f1:auto_generated|ram_block1a0~PORT_A_WRITE_ENABLE_REG
to   : …|v30u_eu:u_eu|opc_base[4]
k = 1.0000   slack = -12.481   ->  T_min 43.731 ns  =  22.87 MHz
```

It launches at the **microcode ROM's own M10K** and lands on a **committed EU
state register**, and **IT DOES NOT PASS THROUGH THE SHADOW.**  Three facts from
the source say why, and none of them is a guess:

1. **`row` IS A MODULE-LEVEL WIRE, NOT A `_n`** (`v30u_eu.sv:604`,
   `wire [28:0] row;` straight out of `u_ucrom`).  Its twelve field decodes
   (`r_s1`, `r_d1`, `r_s2`, `r_d2`, `r_f`, `r_w`, `r_e`, `r_type`, `r_aluop`, …,
   `:615-623`) are wires too.  **The shadow's membership rule is "every `_n` or
   scratch name STAGE 1 ASSIGNS", so no wire can be in it** — and the chain
   reads these wires LIVE.  The microcode row read and its decode are therefore
   in STAGE 2's cone whatever the shadow carries.
2. **THE EA ADD IS INSIDE THE LOOP BODY** — `v30u_eu_step.svh:385-389`,
   `ea = gpr_n[R_BW] + gpr_n[R_IX];` and its seven siblings.  WAVE 1 §2 put
   `Add57` UPSTREAM of `Decoder28`; in the RTL it is DOWNSTREAM of the loop
   entry, i.e. in stage 2.  (Its *operands* do come from the shadow — `gpr_n` is
   a member — but its *select* comes from `row`.)
3. **THE OPERAND / QUEUE-STATE SELECT IS A MODULE-LEVEL WIRE CONE TOO**:
   `opr_free_now` (`v30u_eu.sv:814`), `f_wait` (`:849`), `row_pre_wait`
   (`:2270`).  Read live by the chain; not `_n`; not in the shadow.

**So the peel moved blocks (a)-(f) — the completion sampling and the
recognition arm — into stage 1, and left the whole
`ROM -> row decode -> operand select -> EA add -> chain -> dec_addr_next` arc
in stage 2 as ONE cone.**  Measured against WAVE 1's uncut 48.245 ns, stage 2 is
**43.731 ns**: the cut took roughly **4.5 ns, ~9 %, off an arc whose census
predicted 53 %.**

⚠ **THIS IS WAVE 1 §6 ITEM 1 COMING TRUE, AND IT WAS WRITTEN THERE AS THE
CAVEAT:** *"Every number in §4 is read off the UNCUT netlist, where Quartus has
merged logic freely across the prospective boundary … After a real cut both
stages are re-synthesised and the numbers move.  This anatomy bounds the shape
of the cut.  It does not predict an Fmax."*  It also refutes, BY MEASUREMENT,
the inference §5.2 drew from §5.1's own warning.  §5.1 said *"A cut is only real
if the source can say it, and a Quartus net name is not by itself an RTL
seam"*; §5.2 then identified `Decoder28#1` with the RTL's loop entry because
`Decoder28` is the first unrolled copy's state decoder.  **THAT
IDENTIFICATION IS WRONG**: `Decoder28` sits DOWNSTREAM of logic the RTL
evaluates inside the loop and of wires the RTL never registers, so the netlist
point and the RTL seam are different points, and the 22-25 ns the census
attributed to `Decoder28#1`'s upstream is not what the RTL cut removes.

### 11.4 WHAT THE MEASUREMENT SAYS THE NEXT CUT WOULD HAVE TO BE

Stated because the next wave should not have to re-derive it, and **not
attempted here** — re-scoping the cut after seeing a result is exactly what the
pre-registration forbids:

* **The binding arc's launch is the microcode ROM.**  Any cut that divides it
  must put a REGISTER between the ROM read and the chain.  That is either
  **L2 — registering `ucrom` the way L1 registered `ucdecode`** (deliberately
  NOT bundled here, RULING 3, and `adcone_l1_results_2026-08-13.md` §4.3 item 4
  already books it), or a shadow whose members are the **ROW DECODE's outputs**
  (`r_s1`/`r_d1`/`r_type`/`r_aluop`/…) rather than the loop-carried `_n` set.
* **A phase-split shadow of the row decode is NOT obviously the same shape as
  this one**, because `row` is a function of `upc_*` — registers that commit on
  `ce` — so it IS phase-stable and the theorem admits it.  What is unmeasured is
  whether the ROM read plus the decode fits in the `ce -> ce_half` window and
  what the remainder costs.
* **The `_n`-set shadow this wave built is not thereby useless**, but nothing
  here measures a benefit for it and **no benefit is claimed**.  It is reverted.



---

### 11.5 P-8(d) — **THE DELETION IS WHAT CHANGES THE TIMING, AND IT COSTS THE PEEL NOTHING**

A CONTROL build on the **SAME peeled RTL** with the multicycle RESTORED for the
one build (`sw/phase_split_p8d.py`, one file patched and reverted with
`git checkout --`; the receipt records `git d867b3d4cd-dirty (tree DIRTY)`,
which is correct and is why it is a probe and not a gate):

```
E2 zero errors    PASS        E3 Fmax          PASS   39.23 MHz
E4 worst setup    PASS +7.002 E5 TNS           PASS   [] (0.000 setup AND hold, all four domains)
ALMs 10,130 / 41,910 (24 %)   latches 0   lpm_divide 0
receipt 2cea84f898ea2cd0…     label phasesplit-w2-P8D-mcp-restored
```

and the `sta_truefmax_probe` run on THAT netlist with THAT SDC
(`sw/testdata/phasesplit/wave2/p8d_truefmax.truefmax.txt`):

```
SAME  $v30u_ce -> $v30u_ce    k = 2.0000   slack = +11.519   ->  39.23 MHz
```

**`k` READS 2.0000 AGAIN.**  P-8(d) is fired: the exception's presence is what
the compiler's budget follows, and its absence is what the 22.78 measures.

⚠ **AND IT ANSWERS A QUESTION THE BARS DID NOT ASK, WHICH THE NEXT WAVE NEEDS:
THE PEEL ITSELF IS TIMING-NEUTRAL.**  39.23 MHz on the peeled RTL with the
exception, against WAVE 1's pre-split CONTROL draws of **40.09 / 38.99 / 40.83**
on the same class.  The 495-bit shadow neither bought nor cost measurable Fmax;
it simply did not divide the arc that binds.  On this draw the whole design
binds OUTSIDE the core at 41.24 MHz (`ucdecode M10K -> nec_bus|ad_in_q[9]`, the
observation class), exactly as L1 left it.

### 11.6 THE DIAGNOSIS, MEASURED ON THE NETLIST AND NOT INFERRED

`sw/sta_phase_split_diag.tcl` on the CONTROL seed-5 fit
(`sw/testdata/phasesplit/wave2/diag_ctl_seed5.txt`).  Its POSITIVE CONTROL is
run first, because `get_timing_paths -through` is the instrument WAVE 1 §0.2
records as able to answer NO silently:

```
  $v30u_ce 2040   shadow registers matching |s1q* : 465
  worst ce->ce
    from  : …|v30u_eu|v30u_ucrom|altsyncram:ucdecode_rtl_0|…|ram_block1a5~PORT_A_WRITE_ENABLE_REG
    to    : …|v30u_eu|modrm_reg[1]
    slack :  -12.648   logic levels 43
    arrival points: 103   of which name |s1q : 0        <<<<<<
  positive control: -through the destination's own D pin resolves 2 pin(s)
    -> paths returned: 1   (MUST be 1; 0 means the question cannot say YES)
  shadow bits whose Q pin lies on a path INTO the binding destination: 100
  STAGE 1 (anything -> s1q), worst:  to s1q[442]              slack  +8.077   14 levels
  STAGE 2 (s1q -> anything), worst:  s1q[190]~DUPLICATE -> modrm_reg[1]
                                                              slack  -4.734   34 levels
```

**THE BINDING PATH HAS 103 ARRIVAL POINTS AND NOT ONE OF THEM IS THE SHADOW.**
The classifier can say YES — its positive control returns the path, and 100
shadow bits DO reach the same destination on other paths — so the ZERO means
what it says.

And the two stages the cut DID make are both far better than the arc that binds:

| | slack | logic levels |
|---|---:|---:|
| STAGE 1, worst (`… -> s1q`) | **+8.077** | 14 |
| STAGE 2, worst (`s1q -> …`) | **-4.734** | 34 |
| **the BINDING arc, which touches NEITHER** | **-12.648** | **43** |

**The cut works on everything it covers and the design is bound by an arc it
does not cover, by 7.9 ns.**

⚠ **465 OF THE 495 SHADOW BITS SURVIVED SYNTHESIS.**  Thirty were optimised
away — recorded, not explained; the membership rule is a conservative
upper bound by construction (§0), so bits that no reachable stage-2 read
depends on are expected to fold, and nothing in the wave depends on the count.

---

## §12 VERDICT


**P-1 FAILED.**  P-9 is unambiguous about what follows: *"If P-1 fails … THE
LANDING DOES NOT HAPPEN.  Revert the RTL and the SDC, report what was measured,
and keep the pre-registration and the results document.  A wave that reports
'the split does not close' has done its job.  DO NOT soften a bar to make a
landing possible, and do not re-scope the cut after seeing a result."*

**No bar was softened.  The cut was not re-scoped.  Nothing was flashed.**

| what | outcome |
|---|---|
| **THE SPLIT ITSELF** — the peel (`c720fbde54`) and the SDC deletion (`d867b3d4cd`) | **REVERTED**, `362245b825` |
| **THE FUNCTIONAL RESULT** — the split IS bit-exact | **ESTABLISHED, and it is the wave's real finding after the failure.**  169,000 goldens at four divisors, 17,350 `ulockstep` scenarios, 4 × 400,000 LFSR clocks byte-identical, `fz2_replay`'s scored content sha256-identical, and the theorem asserted per clock and never once violated |
| **THE CUT** — WAVE 1's `Decoder28#1` identified with the RTL's loop entry | **REFUTED BY MEASUREMENT.**  §11.3 |
| **THE SHADOW'S WIDTH** — WAVE 1 §6 item 2's open question | **ANSWERED: 495 bits / 66 names**, against ~832 for the whole `_n` set |
| **THE INTERFACE CHANGE + RULING 1's CLAUSES** (`ebe0c9fcbd`) | **REVERTED TOO, AND THE REASON IS NOT MECHANICAL.**  §12.3 |

### 12.1 WHAT THIS WAVE ACTUALLY ESTABLISHED, AND IT IS NOT NOTHING

1. **THE THEOREM HOLDS ON THIS DESIGN, AND IT IS NOW MEASURED RATHER THAN
   ARGUED.**  A `ce_half`-captured shadow of the EU's loop-carried state is
   BIT-EXACT: every golden leg, every `ulockstep` scenario and all 1.6 M
   `chain_lfsr` clocks are byte-identical, with the phase-stability premise
   asserted on every clock (`s1q !== s1_bus` → `$fatal`) and never fired.  **A
   later wave that wants a different cut does not have to re-establish this.**
2. **THE ONE PLACE THE PREMISE DID NOT HOLD WAS FOUND BY THE ASSERT, NOT BY
   ARGUMENT**: `poll_pipe_n` shifted a live pin in block (a).  It was the only
   one of the three pin pipelines advanced at the START of the edge, and P-11 is
   now a standing lint clause rather than a note.
3. **THE SHADOW'S COST IS MEASURED**: 495 bits, and the ALM column shows what
   that bought in area (§11.1).
4. **THE `Decoder28#1` IDENTIFICATION IS REFUTED**, with the three source facts
   that refute it (§11.3), and the shape of the cut that WOULD divide the arc is
   named (§11.4) without being attempted.
5. **A STANDING LINT AND A NON-VACUITY PROBE EXIST NOW** —
   `sw/phase_split_lint.py` and `sw/phase_split_nonvacuity.py` — and the second
   found that **Verilator `$stop`s on the first procedural `$error`**, which
   would have made a naive single-probe run report a MISS that was an instrument
   artefact (§9).

### 12.3 THE REVERT'S SCOPE, AND THE ONE JUDGMENT IN IT

**ALL THREE EDITS ARE REVERTED**, `hdl/` and the four `sw/` files the SDC
deletion touched restored to `a21195f38f` byte for byte.  Kept, because P-9 asks
for them in the same sentence: **the pre-registration, this document, the
measurement tools (`sw/phase_split_*.py`, `sw/run_phase_split_g6.sh`,
`sw/sta_phase_split_diag.tcl`) and every artifact under
`sw/testdata/phasesplit/wave2/`.**

⚠ **EDIT (a) — THE `CE_HALF` PORT MOVE — WAS REVERTED TOO, AND THAT IS A
JUDGMENT, SO IT IS STATED AS ONE.**  It was measured GREEN (30 of 31 ladder legs
byte-identical) and could have been kept.  It was not, because **its
justification does not survive the revert**: `CE_HALF` was made unconditional
*because the EU's stage 1 needed it in every configuration*, and with the split
gone `CE_HALF` really is bus-shape machinery again, exactly as `v30_core.sv`'s
own pre-existing paragraph says.  Keeping it would leave a BREAKING INTERFACE
CHANGE — a de-muxed downstream integrator that did not connect `CE_HALF` fails
to elaborate — standing for a feature that is no longer there.

**BUT USER RULING 1 IS A USER DIRECTIVE AND IS NOT A CASUALTY OF P-1.**  Its two
clauses are RE-LANDED in a separate, minimal commit, **under `ifdef
V30_MUXED_AD` beside C-a and S-1**, which needs no interface change:

```
if (SS_WE && CE_HALF)   $error("SS_WE asserted while CE_HALF high …");
if (CE_HALF && ss_we_q) $error("CE_HALF resumed with SS command staging undrained …");
```

Without the define there is no `CE_HALF` port, so both clauses are **VACUOUS BY
CONSTRUCTION** there — which is the reason C-a and S-1 already live under it,
written in that block since 2026-08-14.  **The ruling is satisfied in every
configuration in which it can be stated**, and the configuration in which it
cannot is the one with no second enable to state it about.  Non-vacuity is
`sw/phase_split_nonvacuity.py` A1 and A2, unchanged and still firing.

*If the coordinator would rather have the unconditional port, edit (a) is
`ebe0c9fcbd` and re-applying it is one `git cherry-pick`.*

### 12.4 THE REVERT IS MEASURED, NOT ASSERTED

* `git diff a21195f38f -- hdl/ sw/demux_off_gate.py sw/quartus_gate.py
  sw/sta_truefmax_probe.tcl sw/test_quartus_gate.py sw/ss_flop_whitelist_ucore.txt`
  is **EMPTY** apart from RULING 1's two clauses in `v30_core.sv` — i.e.
  byte-identical to the tree the wave entered on.
  `hdl/rtl/ucore/v30u_eu_preload.svh` is deleted.
* **The whole ladder re-run on the reverted tree is 31 of 31 SAME**
  (`sw/testdata/phasesplit/wave2/reverted/`, `sw/phase_split_ladder_diff.py`):
  every figure back at its registered value including `ss_lint` 232 / 228 flops
  / 3 whitelist entries and `demux_off_gate`'s original *"three muxed ports"*
  line.  RULING 1's re-landed clauses move NOTHING.
* `sw/phase_split_nonvacuity.py` on the reverted tree: **A1 FIRED, A2 FIRED,
  B FIRED, C correctly SKIPPED** ("the mechanism it probes is not in this tree
  yet"), `hdl/ restored: CLEAN`, exit 0.
* `sw/phase_split_lint.py` exits **2, COULD NOT RUN**, as designed.
* `hdl/nec_test_ucore.qsf` moved during the sweeps — the declared §70.7
  exemption, E7's single permitted mover — and was restored with
  `git checkout --`.  **Recorded because a file that moves and is put back is
  still a file that moved**, which is WAVE 1's own precedent.

### 12.2 THE THREE NUMBERS THAT MAY BE QUOTED FROM THIS WAVE

⚠ **AND THE ONE THAT MAY NOT.**  `standing_gates.md` §A governs every timing
figure: the same tree has drawn 19.42 and 45.91 MHz, and one green build is not
closure — which cuts BOTH ways, so **these RED draws are not a proof that no
phase split can close, only that THIS one did not on these ten draws.**  What
makes them strong is not the count but §11.3: the binding path's endpoints and
the three source facts are the same on every draw, and they are structural.


