# L2 — THE REGISTERED ROW.  RESULTS, SCORED AS REGISTERED.

Pre-registration `f18edcd799` (`l2_registered_row_prereg_2026-09-08.md`),
committed **before the first edit**.  Edit `26c2b45e84`.  Branch `master`, HEAD
verified at `41c922626a` on entry.  **OFFLINE ONLY.  NO BOARD, NO FLASH, NO
BITSTREAM PROGRAMMED.  No Codex consulted, no nested subagent spawned.**

Tool: Quartus 17.1.0 Build 590 Lite, 5CSEBA6U23I7, Slow 1100 mV 100 C,
`divclk` 31.250 ns.

---

## §0 HEADLINE — **THE GOAL STATE MOVED 0.36 MHz AND IS STILL 9.8 MHz SHORT**

| | |
|---|---|
| **THE EDIT** | **NINE lines of functional RTL.** The microcode ROW table is read on the `ce` edge that makes its address, exactly as L1 read the DECODE table. No SDC edit. |
| **⚠ THE VERDICT** | **L2 IS REFUTED BY ITS OWN REGISTERED BAR L-8, AND IS REVERTED.** On **3 of the 10 goal-state draws** the worst `ce -> ce` path **ENDS AT `row_q`** — the new D-pin class BINDS. L-10 is unambiguous about what follows and no bar was softened. |
| **L-6, THE GOAL STATE — THE POINT OF THE WAVE** | **CONTROL `worst-of-5` 21.82 -> 22.18 MHz (+0.36).  RETENTION 22.16.  THE GAP TO 32.0 MHz IS 9.82 MHz (CTL) / 9.84 (RET).** RED on 10 of 10 draws, as expected, and a RED result is not a failure of this wave. |
| **WHY IT BOUGHT ALMOST NOTHING — THE FINDING** | **THE TWO ROMs AND THE EU'S TWELVE-POSITION CHAIN ARE A *LOOP*, NOT A SERIES CHAIN.** Cutting the loop at *either* ROM boundary leaves the whole chain in *both* halves, so both halves measure ~43 ns and the binding figure barely moves. Pre-L2 the arc was `ucdecode M10K -> ucrom(LUT) -> decode -> chain -> EU`; post-L2 it is `ucrom M10K -> decode -> chain -> EU` **and** `EU -> chain -> ucdecode(LUT) -> ucrom addr reg`, at **43.5** and **42.8-44.8 ns**. **The premise that registering the row table shortens the binding arc is refuted by measurement.** |
| **THE ROM HEAD IS NOW 0 % OF THE CONE, AND IT DID NOT HELP** | Pre-L2 the ROM head was the first **5.1 ns** of a 42.676 ns arc (~12 %). Post-L2 **neither table appears in the >= 25 % net census at all** — and the arc is **43.509 ns**, i.e. **LONGER**. |
| **L-5, THE CONTROL BUILD** | **PASSES E1-E5 on all ten draws.** CONTROL `worst-of-5` **37.29**, RETENTION **39.26**. ⚠ **Against the nearest receipted like-for-like (`rep-int-term-control-20260820`, 38.25) that is −0.96 MHz**: in the with-exception configuration L2 is a small REGRESSION. |
| **PIN IDENTITY** | **BYTE-IDENTICAL on every leg with a control**: 4 × 400,000 LFSR clocks, 305 `fz2_replay` seeds by sha256, and 30 of 31 ladder legs — the one mover being L-3's own registered whitelist growth. |
| **SYNTHESIS** | **THE M10K MOVED FROM `ucdecode` TO `ucrom`**, `row_q` packed in as its port-A address register across six M10K blocks, and `dec_q[8:0]` pruned. Pre-registered as a possibility (§1.4); **recorded, not engineered.** |
| **⚠ L-9's SECOND CLAUSE IS NOT MET** | The `srst` address-mirroring arm — the correctness argument itself — **is unfalsifiable by every leg of the standing ladder**, and the CONTROL shows **L1's arm is equally unfalsifiable**. Pre-existing, structural, and named. |
| **WHAT THE NEXT WAVE NEEDS** | **`Selector1552#1` — on 100 % of the top 50 paths, REG-ONLY, and split 21.745 / 21.127 ns.** That is a **0.6 ns-balanced** cut of the arc, and it is in the EU's own rails, not in the microcode head. §5.3. |

---

## §1 L-1 / L-2 / L-3 / L-4 — THE FUNCTIONAL LADDER

`hdl/rtl/ucore/v30u_eu.sv` is the only RTL file this wave edits and
`sw/ss_flop_whitelist_ucore.txt` the only other functional file.  **`hdl/nec_test.sdc`
is byte-identical at the end of the wave to what it was at the start.**

The edit is **nine lines of functional RTL** (the rest of the diff is the
argument, written beside the code as L1's was):

```verilog
wire [10:0] rom_addr_next;
wire [28:0] row_next;
reg  [28:0] row_q;
wire [28:0] row       = row_q;
    .rom_addr (rom_addr_next),
    .rom_word (row_next)
assign rom_addr_next = {dec_bank_next,
        (srst && !ss_we) ? upc_loc_r[1:0] : upc_loc_n[1:0]};
        row_q <= row_next;
```

### 1.1 L-1(a) — `chain_lfsr_gate`: **4 OF 4 SIGNATURES BYTE-IDENTICAL**

4 seeds × 400,000 fabric clocks of arbitrary bytes, with LFSR memory, LFSR
`READY` and LFSR `INT`.

| seed | before | after |
|---|---|---|
| 1 | `1d01c9b269ffaa94` | **`1d01c9b269ffaa94`** |
| 2 | `b39b040a98b28e5d` | **`b39b040a98b28e5d`** |
| 3 | `0997b773cd99c030` | **`0997b773cd99c030`** |
| 4 | `d05b6c3c3d9fbe78` | **`d05b6c3c3d9fbe78`** |

`CHAIN_DEPTH_MAX` 6 · `entry_st` 25 · `coincide` 0 · `ce_clocks` · **all eight
gap counts** · and the per-seed live bus census (`fpops`/`qpops`/`INTA`/`IOR`/
`IOW`/`HALT`/`CODE`/`MEMR`/`MEMW`) **all identical**, `diff` empty.

The Verilator binary receipt moved — `9d77ce50cb738eda…` →
`8618efdbcfde05ad…`.  ⚠ **THAT IS NOT EVIDENCE OF ANYTHING, AND THIS WAVE
MEASURED WHY — SEE §6 ITEM 9.**  A receipt is not reproducible across rebuilds
of a byte-identical tree, so a MOVED receipt does not show that an edit reached
the binary.  **What does show it is L-9 case A**: perturbing one bit of `row_q`
on a rebuilt binary takes `check_core 8F.0` to **0/500** (§2), and on the
Quartus side the content-hashed **input manifest** moves
(`69f1a5d56283ad56…` → `f65b2a9661b5223e…`).

### 1.2 L-1(b) — `fz2_replay`: **SCORED CONTENT sha256 IDENTICAL**

`fz2_replay --all-failures --pass-sample 200 --leg ret --no-fabric-era-guard`,
305 seeds replayed through `tb_sys`, scored against the banked **socket** rows
with the corpus's own column policy and window:

```
scored-content sha256   de949fd373ed77de7f7d980a1728538de1b6ddaf6e200a9e61ba69bd1a8b2942   (BOTH)
rows                    305 vs 305
tb_sys receipt          d62c64fa6675666a…  ->  a54626406e98b294…   MOVED
```

⚠ **AND THE `tb_sys` RECEIPT MOVES ON A BYTE-IDENTICAL TREE TOO** — the
REVERTED run, whose RTL is byte-identical to the BEFORE run's, produced a THIRD
value, `4e3bcc731801d658…`.  §6 item 9.  **The sha256 of the scored content is
the measurement; the receipt line is not.**

⚠ **BOTH LEGS RAN WITH `--no-fabric-era-guard`, AND THAT IS STATED RATHER THAN
WORKED AROUND** — it is L1's own caveat, unchanged: this tree has been a
cross-era read since before this wave touched it.  **What these two legs measure
is BEFORE vs AFTER on ONE tree.  They say nothing about fabric, and no fabric
claim is made from them.**

### 1.3 L-1(c) / L-2 / L-4 — THE LADDER: **30 of 31 SAME, 1 MOVED**

`sw/phase_split_ladder.sh` (WAVE 2's, re-used verbatim) on the UNEDITED tree
(`sw/testdata/l2/before/`) and on the landed one (`sw/testdata/l2/after/`),
diffed leg by leg by `sw/phase_split_ladder_diff.py`.

| leg | registered | measured, BOTH sides |
|---|---|---|
| `r7_lint` | PASS, 0 violations | **PASS** — 0 undeclared carriers, 0 undeclared unresolved, 0 `stop` sites |
| `check_core --opcodes all --cases 0` | 169,000 | **169,000/169,000** |
| `check_core --opcodes 8F.0` | 500 | **500/500** |
| HLT sweeps ⚠ `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = 279/283 | **97 · 93 · 45 · 44 = 279/283** |
| `v0.1-w1` / `-w3` | 1,200 each | **1,200 / 1,200** |
| `v0.1-w1 --opcodes EB` | 200 | **200/200** |
| the four `evt` cells w0/w1/w2/w3 | 200 / 1,200 / 200 / 1,200 | **200 / 1,200 / 200 / 1,200** |
| `v0.1-w1evt-biased` | 1,200 | **1,200/1,200** |
| `ulockstep --golden all --cases 50` | 17,350 ALL LOCKSTEP | **ALL CASES LOCKSTEP** |
| `ghost_launch_law score` | 200/200 | **200/200 = 100.0 %** |
| `check_boot --core ucore` | 220 and 400 | **MATCH over 220** and **over 400** rows |
| `check_ab_sim --core ucore` | 187 | **MATCH over 187 rows** |
| `sm3_s16_score --core ucore` | 1,320/1,371 | **1,320/1,371** |
| `demux_off_gate` | PASS | **PASS**, 3 legs |
| `test_artifact` | 45/45 | **45/45** |
| `test_quartus_gate` | — | **255/255** |
| `ucrom_mif_check` | PASS | **PASS** |
| **L-4** `--ce-div 2 / 3 / 8` | 169,000 each | **169,000/169,000 each** |
| **L-4** `--ce-div 1` | REFUSED | **REFUSED**, clause cited |
| `ss_lint --core ucore` | see L-3 | **the one mover — L-3's own registered growth** |

**`=== ladder diff: 30 SAME / 1 MOVED / 0 MISSING`.**

### 1.4 L-3 — SAVE STATE: **`SS_COUNT`, `SS_VERSION` AND `SS_TAG` DO NOT MOVE**

```
before  ss_lint: PASS (109x2 BIU + 122x2 EU + tag = 232; constants OK)
        ss_flopcensus: PASS (228 architectural flops; 3 whitelist entries)
after   ss_lint: PASS (109x2 BIU + 122x2 EU + tag = 232; constants OK)
        ss_flopcensus: PASS (229 architectural flops; 4 whitelist entries)
        EU: 138 architectural flops -> 134 SSA-mapped, 4 whitelisted, 0 UNMAPPED
```

`hdl/rtl/ucore/v30u_ss_pkg.sv` is **untouched**: `SS_VERSION` **0x8F**,
`SS_COUNT` **232**, `SS_TAG` **0x8FE8**, unchanged.  **0 UNMAPPED.**  The
whitelist grew by **exactly one entry**, `row_q`, on the **DERIVED** class beside
`dec_q`, naming `rom_addr_next` as the place the derivation is checkable by eye.
**L-3 MET on every clause.**

### 1.5 ⚠ THREE DISAGREEMENTS WITH `standing_gates.md`, ALL PRE-EXISTING

The prereg's own instruction (L-2) is to MEASURE where the file and the tree
disagree and to report the disagreement as a finding.  All three were measured
**on the UNEDITED tree before the first edit**, and **all three are WAVE 2 §6.1's,
unfixed**:

1. **`test_quartus_gate` reads 255/255 on this tree.**  `standing_gates.md`
   registers 200/200; CLAUDE.md's quick reference registers 254 (255 with a
   build tree).  The measurement agrees with CLAUDE.md.  **`standing_gates.md`
   is stale.**
2. **`ss_lint` reads `SS_COUNT` 232 / 228 flops / 3 whitelist entries.**
   `standing_gates.md` §B registers 226 / 214 / `SS_VERSION` 0x8D / `SS_TAG`
   0x8DE2 — the `fuzz-v2-on-relanding` figures.  `master` carries 0x8F / 232, so
   `SS_TAG` is **0x8FE8**.  **That row is a different branch's.**
3. **The four `evt` cells, `v0.1-w1evt-biased`, `check_boot 400` and
   `check_ab_sim` have no rows in `standing_gates.md` §B's ucore table** — they
   are in CLAUDE.md's quick reference.  A gap, not a disagreement, named so it
   is not mistaken for one.

**None is this wave's to fix and none is fixed here.**  They are booked in §6.

---

## §2 L-9 — NON-VACUITY: **ONE CLAUSE MET, ONE NOT, AND THE CONTROL SAYS WHY**

`sw/l2_nonvacuity.py`.  Each case is ONE temporary, reverted perturbation with
its own rebuild and its own run — Verilator `$stop`s on the first procedural
`$error`, and the same discipline applies to a perturbation: two at once cannot
be attributed (WAVE 2 §9).

| case | perturbation | leg | result |
|---|---|---|---|
| **A** | `row_q <= row_next ^ 29'h1` | `check_core 8F.0` | **0/500** (cycles 249, arch 0) — **NON-VACUOUS** |
| **C** | *none* (positive control) | `8F.0`, `check_boot` | 500/500, MATCH 220 — the harness can say YES |
| **B** | the `srst` arm dropped from `rom_addr_next` | `8F.0` · `check_boot 220` · `check_core all` | 500/500 · MATCH · **169,000/169,000** — ⚠ **VACUOUS** |
| **B2** | the same | `8F.0 --ss-sweep` | 500/500 — ⚠ **VACUOUS** |
| **D** | **CONTROL**: the SAME arm dropped from **L1's** `dec_addr_next` | all four legs | ALL PASS — ⚠ **VACUOUS** |

**L-9's FIRST CLAUSE IS MET**: `row_q` is load-bearing, and one inverted bit
takes a named gate leg to 0/500.

**L-9's SECOND CLAUSE IS NOT MET, AND IT IS REPORTED AS MEASURED.**  The
`srst` mirroring — the half of the construction that L1's comment and this
wave's §1.2 both call *the whole of the correctness argument* — **is not
falsifiable by any leg of the standing ladder.**

**CASE D IS WHY THAT IS NOT AN L2 FINDING.**  The identical perturbation of
**L1's** `dec_addr_next`, landed 2026-08-13 and green ever since, is **equally
vacuous on the same four legs**.  The gap is **pre-existing and structural**,
not introduced here.  The arms are still correct and they stay; what is missing
is a gate, and a correctness argument no gate can falsify is an argument, not a
gate.

A MECHANISM IS PROPOSED AND IS **NOT** ESTABLISHED: `srst` is held for many
clocks by every harness, so by the second reset clock the bank already carries
`upc_*_r` and the chain's `upc_*_n` computed from that state may coincide with
it — which would make both arms redundant IN SIMULATION while remaining
necessary in general (`upc_*_r` is 0/0/0, or 7/0x03/0 in 8080 mode, and
`upc_*_n` is not).  **UNPROVEN.**  Its falsifier would be a single-clock-`srst`
probe, which does not exist.  **BOOKED, NOT BUILT** — building a gate to close a
bar after seeing it fail is choosing an instrument after seeing a result.

---

## §3 L-5 — THE CONTROL BUILD (the tree's current SDC, multicycle PRESENT)

Both sweeps `verdict PASS`; **E1-E5 met on every draw**, TNS **0.000 setup AND
hold on every domain of all ten**, `off_class` **EMPTY** on all ten (the
exception is present and the compiler honoured it), and the core-domain class is
**`SAME` at k = 2.0000 on 10 of 10**, equal to the whole-design figure — i.e.
**the core binds the design in this configuration.**

Input manifest **`f65b2a9661b5223e…`** on both, against the pre-L2 baseline
sweep's **`69f1a5d56283ad56…`** — the check that the edit reached the compiler.

**CONTROL** — record **`9428e7ee3aeeaac6…`**, `sw/testdata/g6dist/l2-control-n5/`

| seed | Fmax (= core `SAME`, k=2) | worst setup | ALMs | binding cone |
|---|---:|---:|---:|---|
| 1 | 38.90 | +8.815 | 10,011 (24 %) | `c_int_q -> f_wait` |
| 2 | 38.90 | +7.427 | 10,047 | `modrm_reg[0]~DUP -> ad_in_q[6]` |
| 3 | 37.83 | +7.494 | 9,995 | `modrm_reg[1] -> ad_in_q[0]` |
| **4** | **37.29** | **+8.182** | 9,976 | `opc_base[3] -> ad_in_q[6]` |
| 5 | 39.51 | +7.626 | 9,978 | `al_op[1]~DUP -> ad_in_q[3]` |

> **`worst-of-5@seeds{1,2,3,4,5}` = 37.29 MHz** · median 38.90 · best 39.51 ·
> spread 2.22

**RETENTION** — record **`d5ccbb0913139345…`**, `…/l2-retention-n5/`, receipt
self-labelling `RETENTION (X1_AD_RETENTION=1)`

| seed | Fmax | worst setup | ALMs |
|---|---:|---:|---:|
| 1 | 39.27 | +7.498 | 9,999 (24 %) |
| **2** | **39.26** | **+7.168** | 9,985 |
| 3 | 40.13 | +7.928 | 9,974 |
| 4 | 41.59 | +7.421 | 9,983 |
| 5 | 40.29 | +7.777 | 10,039 |

> **`worst-of-5@seeds{1,2,3,4,5}` = 39.26 MHz** · median 40.13 · best 41.59

### 3.1 THE COMPARISON, AND ⚠ **IT IS A SMALL REGRESSION**

| reference | what it is | figure |
|---|---|---|
| `rep-int-term-control-20260820`, record `d5c4eb20727e96c6…` | **RECEIPTED, seed-matched, `worst-of-5`**, at `f688db385b` — ⚠ **TWO `v30u_eu.sv` commits behind `master`** (the rep_cl0 / REP-vs-INT landings) | **CONTROL 38.25 MHz**, ALMs 10,281-10,334 (25 %) |
| `rep-int-term-retention-single-20260820` | **n = 1, NOT promotion grade** | RETENTION 39.63 (seed 1) |
| `phase_split_anatomy_2026-09-08.md` §1 | ⚠ **DECLARED THERE AS "NOT a G6 result and not quotable as Fmax"** — `sta_truefmax_probe` rows off an anatomy driver with no receipt | CONTROL `SAME` 40.09 / 38.99 / 40.83 at seeds 1/2/3 |

**L2 CONTROL: 38.25 -> 37.29 = −0.96 MHz**, ALMs −~250 (25 % -> 24 %).  On the
seed-matched non-receipted rows it is 40.09/38.99/40.83 -> 38.90/38.90/37.83.

**L-5 IS MET AS REGISTERED** — the bar is *"PASSES E1-E5 on every draw, both
configurations"*, and it does, on 10 of 10.  **The Fmax comparison is REPORTED,
not a bar**, and it is reported as what it is: **in the with-exception
configuration L2 costs about 1 MHz.**  ⚠ It is inside the ~2.3 MHz historical
map variance (`standing_gates.md` §A, §74.4 — the same tree has drawn 19.42 and
45.91), and the AFTER side necessarily carries a new map, so it is **recorded,
not explained.**

---

## §4 L-6 / L-6b — **THE GOAL-STATE MEASUREMENT**

### 4.1 THE THREE SWEEPS

⚠ **ALL THREE ARE PROBES, NOT LANDINGS.**  `sw/l2_noexc_g6.py` patches
`hdl/nec_test.sdc` for the duration and restores it with `git checkout --` in a
`finally`; their receipts read `-dirty`, which is correct, and `hdl/` was
verified CLEAN after each.  **`hdl/nec_test.sdc` is byte-identical at the end of
this wave to what it was at the start.**

⚠ **L-11 IS MET ON 15 OF 15 DRAWS AND IT IS WHY THESE FIGURES ARE QUOTABLE**:
every draw reports `off_class` **`['SAME']`** with `k_measured` **1.0** against
`k_nominal` **2.0**.  `sw/quartus_gate.py` is NOT edited by this wave, so the
exception's absence shows up as an off-class row rather than as silence.  A
no-exception draw with an EMPTY `off_class` would mean the deletion never
reached the compiler; none is.

**L-6b — THE BASELINE, PRE-L2, TAKEN FIRST** — record **`9ce05a8350929355…`**,
`sw/testdata/g6dist/l2-baseline-noexc-control-n5/`, manifest `69f1a5d56283ad56…`

| seed | Fmax | worst setup | ALMs | binding `ce -> ce` |
|---|---:|---:|---:|---|
| 1 | 22.22 | −13.764 | 10,215 | `ucdecode M10K -> modrm_reg[1]` |
| **2** | **21.82** | **−14.574** | 10,230 | `ucdecode M10K -> modrm_reg[0]` |
| 3 | 22.55 | −13.092 | 10,252 | `ucdecode M10K -> modrm_reg[1]` |
| 4 | 22.11 | −13.970 | 10,210 | `ucdecode M10K -> modrm_reg[1]` |
| 5 | 22.58 | −13.040 | 10,233 | `ucdecode M10K -> modrm_reg[0]~DUP` |

> **`worst-of-5` = 21.82 MHz** · spread 0.76 · **RED 5/5** · one cone shape on
> 5 of 5

**L-6 CONTROL — POST-L2** — record **`ad70054b87509dbb…`**, `…/l2-noexc-control-n5/`

| seed | Fmax | worst setup | ALMs | binding `ce -> ce` |
|---|---:|---:|---:|---|
| 1 | 22.84 | −12.524 | 10,091 | `ucrom M10K -> sigma[2]` |
| 2 | 22.75 | −12.699 | 10,126 | `ucrom M10K -> Equal56` |
| **3** | **22.18** | **−13.843** | 10,102 | `ucrom M10K -> eff_op[0]` |
| 4 | 22.82 | −12.564 | 10,132 | `ucrom M10K -> eff_op[2]~DUP` |
| 5 | 22.86 | −12.486 | 10,107 | `eff_op[2]~DUP -> eff_op[1]` |

> **`worst-of-5` = 22.18 MHz** · spread 0.68 · **RED 5/5**

**L-6 RETENTION — POST-L2** — record **`c002c844d0d63a31…`**, `…/l2-noexc-retention-n5/`

| seed | Fmax | worst setup | ALMs | binding `ce -> ce` |
|---|---:|---:|---:|---|
| 1 | 23.37 | −11.538 | 10,136 | `eff_op[0] -> `**`row_q`**` (ucrom porta_address_reg2)` |
| 2 | 23.11 | −12.020 | 10,140 | `ucrom M10K -> opc_sel[2]` |
| 3 | 22.38 | −13.433 | 10,125 | `-> `**`row_q`**` (porta_address_reg5)` |
| 4 | 22.30 | −13.586 | 10,114 | `-> `**`row_q`**` (porta_address_reg6)` |
| **5** | **22.16** | **−13.883** | 10,163 | `ucrom M10K -> Mux100` |

> **`worst-of-5` = 22.16 MHz** · spread 1.21 · **RED 5/5**

### 4.2 **THE NUMBER, AND THE GAP**

| | pre-L2 | post-L2 | Δ | **GAP TO 32.0 MHz** |
|---|---:|---:|---:|---:|
| **CONTROL, no exception, `worst-of-5`** | **21.82** | **22.18** | **+0.36** | **9.82 MHz** |
| **RETENTION, no exception, `worst-of-5`** | *not baselined* | **22.16** | — | **9.84 MHz** |

**L-6 IS RED, AS PRE-REGISTERED, AND A RED RESULT IS NOT A FAILURE OF THIS
WAVE.**  What it measures is that **the goal state is 9.8 MHz short**, that
**L2 moved it by 0.36 MHz**, and that **0.36 MHz is inside the noise of the
instrument** (the baseline's own five draws spread 0.76 MHz).

⚠ **NO RETENTION pre/post DELTA MAY BE QUOTED** — L-6b was CONTROL only, as
registered.  Only the absolute figure and its gap.

⚠ **AND THE TWO CONFIGURATIONS' BANDS OVERLAP** ([22.18, 22.86] vs
[22.16, 23.37]), so **no control-vs-retention delta may be computed** either
(the distribution gate's own rule).

---

## §5 L-7 / L-8 — THE ARC, AND THE NEW CLASS

### 5.1 L-8 — **THE NEW D-PIN CLASS BINDS.  L2 IN THIS FORM IS REFUTED.**

The bar: *"Report the worst path ENDING at `row_q` … and state whether it binds.
If it does, L2 in this form is REFUTED — say so and revert."*

**IT BINDS.**  On **goal-state RETENTION seeds 1, 3 and 4 the worst
`$v30u_ce -> $v30u_ce` path's DESTINATION is `row_q`**, realised as the `ucrom`
M10K's port-A address register:

```
seed 1   -> …|v30u_ucrom:u_ucrom|altsyncram:ucrom_rtl_0|…|ram_block1a5~porta_address_reg2
         k = 1.0000   slack = -11.538   T_min 42.788 ns  =  23.37 MHz
seed 3   -> …|ram_block1a12~porta_address_reg5   slack = -13.433   44.683 ns  22.38 MHz
seed 4   -> …|ram_block1a20~porta_address_reg6   slack = -13.586   44.836 ns  22.30 MHz
```

On the other seven goal-state draws the worst path **LAUNCHES** at the same
M10K (`…~PORT_A_WRITE_ENABLE_REG`), i.e. it is the *other* half.  **The two
halves are 42.8-44.8 ns and 43.3-45.1 ns — they are the same length**, which is
the whole finding: see §5.2.

⚠ **`sw/sta_l2_rowq_probe.tcl` REFUSED to emit an L-8 row, and its refusal is
CORRECT AND WAS ANTICIPATED IN THE COMMIT THAT ADDED IT.**  The `row_q`
collection is **EMPTY** on the post-fit netlist because **`row_q` was PACKED
INTO THE INFERRED MEMORY** — the probe's own memory-node diagnostic lists **84
nodes** under `ucrom_rtl_0`, six M10K blocks' worth of
`ram_block1aN~porta_address_regM`.  This is exactly what happened to L1's
`dec_q`, it is named in that commit message in advance, and **the L-8 figure is
therefore read off the RECEIPTED per-seed `truefmax` artifacts instead**, which
name the same nodes.  `dec_q`'s collection now reads **2** — `dec_q[8:0]` was
pruned, as §1.4 said it would be.

### 5.2 L-7 — THE ARC, AND WHY THE LEVER DOES NOT WORK

`sw/sta_phase_split_scan.tcl` (WAVE 1's, re-used), on the surviving
**no-exception CONTROL seed-5** fit, with the SDC patch in place so `read_sdc`
matches the netlist's own budget.  Positive control **PASSED** — 30/30
pin-dependent on the `LIVE -> $v30u_ce` path, both live sets.

| | **pre-L2** (`prel2_noexc_seed5`) | **post-L2** (`l2_noexc_ctl_seed5`) |
|---|---|---|
| worst `ce -> ce` data delay | **42.676 ns** | **43.509 ns** |
| logic levels / cells | 41 / 48 | **44 / 44** |
| endpoints | `ucdecode M10K -> modrm_reg[0]` | `ucrom M10K -> sigma[2]` |
| **the ROM head's share** | `ucdecode` clk→q **1.046** + `ucrom#1..#4` at **3.019 / 4.183 / 4.840 / 5.067** = **~5.1 ns, ~12 %** | **ZERO — neither table appears in the ≥ 25 % net census at all** |
| what fills the cone | `st_n#1..#9` 7.6 → 35.5 ns, `Add57#1..#7` ~13.5 | `Mux271/277/349/350/360`, `Add57#1..#3`, `Ram12#1..#2` (the GPR file) 4.5 → 19.9 ns, then **`st_n#1..#8` 22.7 → 34.1**, then `Decoder36/38`, `opc_base`, `modrm_reg` |

**THE ROM HEAD LEFT THE CONE AND THE CONE GOT LONGER.**  That is not a paradox
and it is not map noise: **the arc runs the other way now.**  Pre-L2 there was
ONE long arc (`ucdecode M10K -> ucrom LUT -> row decode -> chain -> EU`) and one
short one (`EU -> chain -> dec_addr_next -> ucdecode addr reg`).  Post-L2 the
`ucrom` LUT read came OFF the first arc and the `ucdecode` LUT read went ONTO
the second, and **the second arc is now as long as the first**:

```
pre-L2    A  ucdecode M10K -> ucrom(LUT) -> decode -> chain -> EU        45.0 ns   BINDS
          B  EU -> chain -> dec_addr_next -> ucdecode addr reg           shorter
post-L2   A' ucrom M10K -> decode -> chain -> EU                         43.3-45.1 ns
          B' EU -> chain -> dec_addr_next -> ucdecode(LUT) -> ucrom addr 42.8-44.8 ns
```

**THE TWO ROMs AND THE TWELVE-POSITION CHAIN ARE A LOOP, NOT A SERIES CHAIN.
THE CHAIN IS IN *BOTH* HALVES OF ANY CUT TAKEN AT A ROM BOUNDARY** — because
`row` feeds the chain and the chain produces `upc_*_n`, which feeds the ROMs,
which feed `row`.  So registering a table relocates the cut without shortening
the loop, and **the ~2 ns it moves is one ROM read swapped for the other.**
This refutes, by measurement, the premise the lever was chosen on
(`adcone_anatomy_2026-08-13.md` §4: *"the ROW table admits the identical
construction"* — it does, and the construction is bit-exact, and it does not
buy the arc).

### 5.3 **WHAT IS NOW THE LARGEST CONTRIBUTOR, AND THE CUT THE NEXT WAVE WANTS**

On the post-L2 census the arc is two roughly equal pieces, and the cut between
them is **already named by the instrument**:

| net | paths | up.mean | dn.mean | REG-ONLY | \|up − dn\| |
|---|---:|---:|---:|:---:|---:|
| **`v30u_eu\|Selector1552#1`** | **50 / 50 (100 %)** | **21.745** | **21.127** | **yes** | **0.618 ns** |
| `v30u_eu\|p#1` | 50 (100 %) | 20.795 | 22.077 | yes | 1.282 |
| `v30u_eu\|st_n#1` | 50 (100 %) | 22.738 | 20.134 | yes | 2.604 |

* **Upstream of it (~21.7 ns): the ROW DECODE and the OPERAND / EA front end** —
  `e_s1`, `Mux271#1..3`, `Mux277#1..3`, `Mux349`, `Mux350#1..3`, `Mux360#1..2`,
  **`Add57#1..#3` (the EA add)**, **`Ram12#1..2` (the GPR file read)**, `opr_n`,
  `v1`, `ld_b_n`, `p`.
* **Downstream of it (~21.1 ns): THE UNROLLED CHAIN** — `st_n#1` … `st_n#8`
  spanning 22.7 → 34.1 ns with `st_zero_ok`, `seg_override_n`, `Selector1620`,
  `pv`, `always6`, `Decoder36`, `Decoder38`, then `opc_from_modrm_n`,
  `opc_base[3]`, `modrm_reg`.

**THE LARGEST SINGLE CONTRIBUTOR IS THE TWELVE-POSITION CHAIN**, ~11.4 ns of
net-to-net span for the `st_n` positions alone and ~21 ns for the whole
downstream half; the microcode head contributes **nothing**.  ⚠ **WAVE 2 §11.4
already said this in a different vocabulary** — *"any cut that divides it must
put a REGISTER between the ROM read and the chain"* — and L2 is the measurement
that **a register between the ROM read and the chain is not enough, because the
chain closes the loop back onto the ROM.**

⚠ **`Selector1552#1` IS AN OBSERVATION, NOT A RECOMMENDATION.**  WAVE 1 §6 item
1's caveat governs it exactly as it governed `Decoder28#1`, whose identification
with an RTL seam WAVE 2 **refuted by measurement**: *"a Quartus net name is not
by itself an RTL seam."*  It is offered as the next wave's starting point and
nothing more.

---

## §6 WHAT IS OWED, AND WHAT IS BOOKED RATHER THAN TAKEN

1. **A FABRIC CONFIRMATION IS OWED AND UNPAID.**  Nothing here has been on a
   board and no bitstream was programmed.  **The wave reverted, so nothing is
   owed *for L2*** — but L1's own owed bar is unchanged and restated: no
   bitstream whose microcode table is a block memory has been in fabric, F44's
   failure mode is a silent empty table, and `ucrom_mif_check` plus a first-light
   `check_ab_hw` MATCH 800 ×3 are owed before any flash.  **L-13.**
2. ⚠ **THE `srst` ADDRESS-MIRRORING ARM OF *L1* IS UNFALSIFIED BY THE STANDING
   LADDER** (§2, case D).  That is a live, pre-existing gap in a LANDED
   mechanism, not a casualty of this wave's revert.  A single-clock-`srst`
   probe would close it.  **BOOKED, NOT BUILT** — building a gate to close a bar
   after seeing it fail is choosing an instrument after seeing a result.
3. **`standing_gates.md` §A/§B CARRIES THREE STALE OR MISSING ucore ROWS**
   (§1.5), all three WAVE 2 §10 item 2's, all three still unfixed, all three
   re-measured here on the UNEDITED tree.  **BOOKED** — a coordinator-territory
   edit, and this wave does not make it.
4. ⚠ **`ucrom.hex` EMITS 1,028 `Warning (10230)` TRUNCATION LINES ON EVERY
   QUARTUS MAP**, one per row (*"truncated value with size 32 to match size of
   target (29)"*).  **PRE-EXISTING** — the pre-L2 baseline log carries the same
   1,028 — and it is the same defect `v30u_ucrom.sv`'s header records for
   `ucdecode`, which was fixed by declaring the array **twelve** bits wide for a
   ten-bit word.  The same fix (`reg [31:0] ucrom`, bits [31:29] constant zero)
   would silence it.  **NOT TAKEN**: it is an `hdl/` edit and this wave's `hdl/`
   is byte-identical to the tree it entered on.
5. **THE `--probe` MODE WAS ADDED AFTER THE BASELINE SWEEP AND USED ON THAT
   SWEEP'S SURVIVING `db`.**  Declared in its commit; the sweep itself did not
   run under it.
6. ⚠ **THIS WAVE'S OWN INSTRUMENT MISTAKE**: `sw/l2_noexc_g6.py`'s summary
   printer indexed `off_class` as dicts where it is a list of class-name
   strings, and raised `TypeError` **after** the sweep and **after** the
   `finally` restored the SDC — so the measurement survived and only the printed
   summary was lost.  Fixed, with the history in the comment.  Recorded because
   nothing else caught it.
9. ⚠ **A VERILATOR ARTIFACT RECEIPT IS NOT REPRODUCIBLE ACROSS REBUILDS OF A
   BYTE-IDENTICAL TREE, AND THIS WAVE MEASURED IT DIRECTLY.**  Two consecutive
   `python3 sw/check_core.py --build --core ucore` runs on an UNCHANGED tree
   produced **`beafbd521aa1333d…`** and then **`8a98e3e5a8eb4f79…`**; and the
   `tb_sys ret` binary read **`d62c64fa6675666a…`** on the BEFORE tree and
   **`4e3bcc731801d658…`** on the REVERTED tree, which is byte-identical to it.
   (The likely cause is the PID-named staging directory
   `hdl/tb/.obj_dir_ucore.staging.<pid>` reaching the binary through a path
   literal; **NOT ESTABLISHED — no bisect was run.**)
   **CONSEQUENCE, AND IT CUTS AGAINST THIS WAVE'S OWN FIRST DRAFT: "the receipt
   MOVED, which is the check that the edit reached the binary" IS NOT A VALID
   INFERENCE**, here or in `adcone_l1_results_2026-08-13.md` §1.1, which makes
   the same move.  A moved receipt is consistent with no edit at all.  **What
   IS valid** is a content hash of the compiled inputs (Quartus's
   `input_manifest`, which is stable and did move: `69f1a5d56283ad56…` →
   `f65b2a9661b5223e…`) or a behavioural falsifier on the rebuilt binary (L-9
   case A).  Both were taken here.
   ⚠ **NOTHING IN `sw/artifact.py`'s CONTRACT IS BROKEN BY THIS** — `require()`
   still asserts that the declared inputs and outputs hash to the tree, and a
   STALE binary still cannot score.  What is refuted is only the reading of a
   receipt as a *fingerprint of the source*.  **BOOKED, NOT FIXED**: an `sw/`
   edit to the artifact layer is out of this wave's scope and would be measured
   by `sw/test_artifact.py`, which is 45/45 here.
10. **NO `check_core --ss-sweep` GATE IS ON THE REGISTERED LADDER.**  It was used
   here only as an L-9 probe leg.  WAVE 2 §10 item 3 booked the same thing.
11. **THE L2 CONSTRUCTION ITSELF IS NOT CONDEMNED — ONLY THIS PLACEMENT OF IT.**
   It is bit-exact (§1), it costs one flop group and no SSA address, and it
   moved the M10K to the smaller table.  What is refuted is the claim that it
   shortens the binding `ce -> ce` arc.  **If it is ever wanted for another
   reason, `26c2b45e84` is the whole of it and re-applying it is one
   `git cherry-pick`.**


---

## §7 THE VERDICT AND THE REVERT

**L-8 FIRED.  L-10 IS UNAMBIGUOUS ABOUT WHAT FOLLOWS**: *"If ANY leg of
L-1/L-2/L-3/L-4 moves, or L-5 fails, or L-8 shows the new class binding, THE
LANDING DOES NOT HAPPEN.  Revert, report what was measured, keep both
documents.  Do not soften a bar to make a landing possible."*

**No bar was softened.  The construction was not re-shaped after seeing the
result.  Nothing was flashed.**

| bar | outcome |
|---|---|
| **L-1** pin identity, three clauses | **MET** — `chain_lfsr` 4/4 signatures and every gap count byte-identical, `fz2_replay` scored-content sha256 identical over 305 seeds, ladder 30/31 SAME with the one mover registered |
| **L-2** the ladder at its registered values | **MET**, every leg (§1.3) |
| **L-3** save state | **MET** — `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 unchanged, 0 UNMAPPED, whitelist grown by exactly `row_q` |
| **L-4** divisor independence | **MET** — 169,000/169,000 at `--ce-div` 2, 3, 4 and 8; `--ce-div 1` REFUSED |
| **L-5** the control build | **MET** — E1-E5 on 10 of 10 draws.  ⚠ Fmax −0.96 MHz vs the nearest receipted like-for-like, REPORTED |
| **L-6** the goal state | **MEASURED: 22.18 (CTL) / 22.16 (RET), RED 10/10, GAP 9.82 / 9.84 MHz.**  Not a revert condition |
| **L-6b** the goal-state baseline | **MEASURED: 21.82** — so L2 is worth **+0.36 MHz**, inside the baseline's own 0.76 MHz spread |
| **L-7** the new arc | **DELIVERED** (§5.2, §5.3) — and it is the wave's most valuable output |
| **L-8** the new D-pin class | ⚠ **IT BINDS, on 3 of 10 goal-state draws.  L2 IN THIS FORM IS REFUTED.** |
| **L-9** non-vacuity | **FIRST CLAUSE MET** (`row_q` load-bearing).  ⚠ **SECOND CLAUSE NOT MET** — and the CONTROL shows the gap is L1's too |
| **L-10** the revert condition | **TRIGGERED, AND OBEYED** |
| **L-11** the deletion is checked | **MET on 15 of 15 no-exception draws** |
| **L-12** nothing outside the wave moves | **MET** — see §7.1 |
| **L-13** the owed fabric bar | **RESTATED, NOT DISCHARGED**; nothing was flashed |

### 7.1 THE REVERT IS MEASURED, NOT ASSERTED

* `git diff <pre-L2 tree> -- hdl/ sw/ss_flop_whitelist_ucore.txt` is **EMPTY**:
  both files are byte-identical to the tree the edit was made on.
* **`hdl/nec_test.sdc` was never landed against and is byte-identical** to the
  tree the wave entered on; the three no-exception sweeps patched it and
  restored it in a `finally`, and `git status --porcelain hdl/` was verified
  clean of tracked changes after each.
* **`git add -A hdl/` WAS NEVER USED** (WAVE 2 §10 item 7(b)); the twelve
  pre-existing untracked `hdl/quartus_gate_*.log` files are still untracked, and
  the ~20 pre-existing tracked modifications outside `hdl/` and `docs/notes/`
  (a repo-wide rename in flight) were not committed by this wave.
* **THE WHOLE LADDER RE-RUN ON THE REVERTED TREE** — `sw/testdata/l2/reverted/`,
  `sw/phase_split_ladder_diff.py` against `sw/testdata/l2/before/` — see §7.2.

### 7.2 THE REVERTED LADDER

```
=== ladder diff (before vs reverted): 31 SAME / 0 MOVED / 0 MISSING
```

Every figure back at its registered value, **including `ss_lint` at 228
architectural flops / 3 whitelist entries** — the one leg that moved for L2 is
the one leg that moved back.  `chain_lfsr_gate`'s four signatures and every gap
count are **identical to the BEFORE run**, and `fz2_replay`'s scored-content
sha256 is **`de949fd373ed77de…` on all three runs** (before, L2, reverted).

### 7.3 WHAT THIS WAVE ESTABLISHED, AND IT IS NOT NOTHING

1. **THE GOAL STATE HAS A RECEIPTED BASELINE FOR THE FIRST TIME.**  Before this
   wave the only no-exception `--seeds 5` figures in the repo were WAVE 2's, on
   a REVERTED peeled RTL.  **`master` with no exception is 21.82 MHz**, record
   `9ce05a8350929355…`, and the campaign now has a scoreboard.
2. **THE ROM/CHAIN LOOP IS MEASURED, NOT ARGUED** (§5.2).  A cut at either ROM
   boundary is worth ~2 ns because the chain is in both halves.  **Two waves
   have now aimed at the microcode head; the head is not the problem, and this
   is the measurement that says so.**
3. **L2 IS BIT-EXACT AND THE CONSTRUCTION IS SOUND** — 169,000 goldens at four
   divisors, 17,350 `ulockstep` scenarios, 1.6 M `chain_lfsr` clocks and 305
   `fz2_replay` seeds, all byte-identical.  A later wave that wants the
   construction for a different reason does not have to re-establish it:
   `26c2b45e84` is the whole of it.
4. **A LANDED MECHANISM'S CORRECTNESS ARGUMENT WAS FOUND UNFALSIFIABLE** (§2,
   case D), by a control that was run because the L2 case failed.
5. **THE NEXT CUT IS NAMED AND MEASURED** (§5.3): `Selector1552#1`, 100 % of the
   top 50 paths, REG-ONLY, split **21.745 / 21.127** — with WAVE 1 §6's caveat
   and WAVE 2's refutation of exactly that kind of identification attached.
