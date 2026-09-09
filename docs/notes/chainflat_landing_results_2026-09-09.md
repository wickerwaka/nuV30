# WAVE 7 — **THE CHAIN FLATTENING IS LANDED.**  RESULTS, SCORED AS REGISTERED.

Pre-registration **`aba01feb07`**
(`docs/notes/chainflat_landing_prereg_2026-09-09.md`), committed **BEFORE THE
FIRST `hdl/` EDIT**.  The landing is **`2ceb8c3ba3`**.  Source: WAVE 6
(`docs/notes/chainflat_results_2026-09-09.md`, `e542f4a6ae`), its
pre-registration `39e201aa6c` and its amendment `a734dd3d79`.

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**  No Codex
consulted.  No nested subagent spawned.  `docs/notes/standing_gates.md` §A
governs every timing figure below; **one green build is not closure**.

| | |
|---|---|
| **Tree, before** | `aba01feb07` (`master`) — the pre-registration, `hdl/` untouched |
| **Tree, after** | `2ceb8c3ba3` |
| **The RTL edit** | `hdl/rtl/ucore/v30u_eu.sv` (the pass + the assertion + two declarations), `v30u_eu_step.svh` (nine arms become nine `` `include ``s + the header), **ten NEW files** — `v30u_eu_arm_<state>.svh` ×9 and `v30u_eu_chain_pos.svh` — and one comment in `hdl/files_ucore.qip` |
| **Artifacts** | `sw/testdata/wave7/{before,after}/` (both ladders, leg by leg), `sw/testdata/g6dist/wave7-chainflat-*/`, `sw/testdata/chainanat-wave7*/`, `sw/chainflat_relocation_check.py` |
| **Tool** | Verilator 5.032; Quartus 17.1.0 Lite Build 590, `5CSEBA6U23I7`, Slow 1100 mV 100 C |

---

## §0 THE HEADLINE

> ### **THE UNROLL IS GONE.  THE FUNCTION IS BYTE-IDENTICAL ON EVERY INSTRUMENT THIS REPO HAS, THE DESIGN LOST ~20 % OF ITS ALMs, AND IT STILL DOES NOT REACH 32 MHz WITHOUT THE SDC EXCEPTION.**

| the question | the measurement |
|---|---|
| **does the flattened core compute the same function?** | **YES, AND IT IS A GATE, NOT AN ARGUMENT.**  4 LFSR signatures byte-identical with every gap count and the whole liveness census · `fz2_replay` scored-content sha256 identical over 305 seeds · the ladder **31 legs SAME / 0 MOVED** · 169,000/169,000 at `--ce-div` 2, 3, 4 **and** 8 · `ulockstep` 17,350 ALL LOCKSTEP |
| **and does it walk the same states?** | **YES — 8,447,821 CE edges, 46 sequences, WAVE 6's `CHAIN_PROBE` census BYTE-IDENTICAL after the fold.**  Not merely the same outcome: the same states at the same positions in the same order |
| **did a flop move?** | **NO.**  `ss_lint` 232 addresses / **228 architectural flops** / 0 UNMAPPED, `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8 — identical.  WAVE 6 measured 807 → 807 in isolation and the design agrees |
| **G-5 — the landing's own timing bar, WITH the exception** | **MET.  10 of 10 draws PASS.  CONTROL `worst-of-5` 41.06 MHz · RETENTION 41.06**, against WAVE 3's pre-landing CONTROL band of **37.29 – 39.51**.  **No regression; +1.55 MHz on its best draw** |
| **G-6 — THE SCOREBOARD, WITHOUT the exception** | ⚠ **STILL RED, as pre-registered.  CONTROL `worst-of-5` 22.18 → 28.32 MHz (+6.14), RETENTION 22.16 → 28.90 (+6.74).  THE GAP TO 32.0 FELL FROM 9.82 TO 3.68 MHz — 62.5 % of it, in one landing** |
| **G-7 — the out-of-context correction, which is the most interesting number this wave produces** | ⚠ **THE HARNESS WAS RIGHT.  WAVE 6 predicted −9.431 ns out of context; the DESIGN realised −9.413 ns** (5-draw means, no-exception, CONTROL).  **The correction is +0.018 ns — 0.2 %.**  WAVE 5's +11.3 … +20.0 ns mispredictions did **not** recur, and §6.3 says why they are a different kind of estimate |
| **G-8 — area** | **−1,780 whole-design ALMs (−17.6 %), 24 % → 20 % of the device, and NOT ONE FLOP.**  In the EU's own A&S row, combinational ALUTs fell **9,185 → 6,126, −33.3 %** — MORE than the harness predicted |
| **does it reach 32 MHz?** | ⚠ **NO.  3.68 MHz short (CONTROL) / 3.10 (RETENTION), and the binding path is now entirely inside the microcode ROM.**  **The chain is no longer the binding structure — the front end is**, which is exactly what WAVE 6 §5.4 predicted and what no wave has yet attacked |

⚠ **AND ONE INSTRUMENT STOPPED WORKING, CORRECTLY.**  `sw/sta_chain_anatomy.tcl`
— WAVE 5's segmenter — **REFUSES on the landed tree, 4 draws of 4**, at its own
control PC-3: *`st_zero_ok` pins in the netlist: 0*.  The fold removes the
marker the segmenter cuts on, so the instrument has nothing to cut with, and it
says so instead of reporting *"0 boundaries"*.  §6.4.

---

## §1 WHAT LANDED, AND WHY IT IS NOT THE PROTOTYPE

WAVE 6's `sw/testdata/chainflat/flat_prototype.diff` replaced

```
    for (chain = 0; chain < CHAIN_MAX; chain = chain + 4'd1)   // SEVEN copies
        ... `include "v30u_eu_step.svh" ...
```

with position 0's 33-arm `case` once, then the nine chainable arms once each in
topological order.  **That substitution is what landed.**  Three things about
it are this wave's and not WAVE 6's.

### 1.1 ONE SOURCE OF TRUTH PER ARM (G-11)

The prototype's generator **carved the nine arm bodies into scratch files and
left the originals in the step case**, so the prototype tree carries **two
copies of every chainable arm**.  That is fine for a measurement and
unacceptable in a tree people edit: the next person to fix `S_DECODE2` would
fix one of them.

The nine bodies now live in `hdl/rtl/ucore/v30u_eu_arm_<state>.svh` and are
`` `include ``d from **both** sites — `v30u_eu_step.svh`'s `case (st_n)` (chain
position 0) and `v30u_eu.sv`'s flattened pass (positions ≥ 1).  Each file
carries the `sim/` statement position it is a cut point in, which is WAVE 6 §1's
table put where the code is.  It is the file's own idiom: `v30u_eu_row.svh`,
`v30u_eu_1bl.svh`, `v30u_eu_iend_late.svh` and `v30u_eu_wd1.svh` were already
included from more than one place.

### 1.2 THE PER-POSITION BOOKKEEPING IS A FILE, NOT TEN TRANSCRIPTIONS

`v30u_eu_chain_pos.svh` holds what the loop body used to do once per iteration —
`chain_used`, §51.2's `(position, state)` pair census and WAVE 6's ordered-tuple
census — and is included at the head of every position.  **It is entirely
`` `ifndef SYNTHESIS ``**, so a chain position costs its arm and no bookkeeping.
The probe's file handle moved to a module-level `cp_fd` because the old
`begin : cprobe` named block cannot be declared ten times in one scope.

### 1.3 `CHAIN_MAX` STOPPED COSTING AND KEPT CLAIMING

Before, `CHAIN_MAX` was the number of unrolled copies: the bound was enforced
**structurally** and the `$fatal` detected the enforcement biting.  The flat
pass provides nine positions ≥ 1 by construction, so **the bound costs nothing
and is now a pure claim** — and it is asserted **more directly than before**,
split into the two things the loop's single `!stop` test conflated:

```
  (i)  chain_open  -- the pass ended with `stop` still low: some arm handed over
                      to a state the topological order has already passed (a
                      BACKWARD edge in a graph asserted to be a DAG) or to a
                      state st_zero_ok does not name.  THE FALSIFIER FOR THE
                      FLATTENING ITSELF.
  (ii) chain_used > CHAIN_MAX - 1  -- the DEPTH bound, which used to be
                      structural and is now measured.
```

Both `$fatal`, both say `CHAIN OVERFLOW`, both are demonstrated non-vacuous in
§7.  **`localparam bit [3:0] CHAIN_MAX = 4'd7;` keeps its exact text and its
value**, so `sw/chain_lfsr_gate.py` — which reads that line out of the RTL
rather than carrying a second copy of the number it checks, and whose
`--nonvacuity` mode rewrites it to `4'd4` — **works UNEDITED.  No gate file was
touched by this landing.**

### 1.4 THE `st_zero_ok` FAIL-SAFE IS KEPT, AND SO IS ITS PURPOSE

`if (!stop && !st_zero_ok(st_n)) stop = 1'b1;` stands at the entry to positions
≥ 1 — once, where the loop applied it once per iteration.  Its purpose was
*spend a clock rather than hang in fabric*, and the flat form keeps it two ways:
the line itself, and the fact that **there is no loop left to hang in** — an
unhandled state simply reaches the end of the pass, the edge ends, `st_n` is
unchanged, and the next clock re-enters it at position 0 where its arm is
unguarded.  §7 case C/D measures that the line is what makes the difference.

### 1.5 THE 24 `if (chain == 4'd0)` GUARDS ARE KEPT AND ARE NOW VACUOUS

`v30u_eu_step.svh` is included at position 0 only, so `chain` is 0 wherever a
guard is read and all 24 are true.  They are kept, and the header says so
plainly, because they are the **machine-readable record of which arms are
position-0-only** — the exact complement of `st_zero_ok`, and the text
`sw/chainflat_graph.py`'s control PC-A1 cross-derives that function from by a
third route.  Deleting them would delete an instrument to save logic the
synthesiser already folds.

---

## §2 G-1 — **PIN IDENTITY.  MET ON ALL THREE CLAUSES.**

**The BEFORE side was taken on the UNEDITED tree first**, so the A/B is real:
`sw/testdata/wave7/before/` is `aba01feb07`, `sw/testdata/wave7/after/` is
`2ceb8c3ba3`, same script (`sw/phase_split_ladder.sh`, WAVE 2's, re-used
verbatim), same machine, same day.

### 2.1 (a) `chain_lfsr_gate` — **BYTE-IDENTICAL**

4 seeds × 400,000 fabric clocks of arbitrary bytes in an all-LFSR environment.

| seed | signature, BEFORE | signature, AFTER |
|---|---|---|
| 1 | `1d01c9b269ffaa94` | **`1d01c9b269ffaa94`** |
| 2 | `b39b040a98b28e5d` | **`b39b040a98b28e5d`** |
| 3 | `0997b773cd99c030` | **`0997b773cd99c030`** |
| 4 | `d05b6c3c3d9fbe78` | **`d05b6c3c3d9fbe78`** |

`CHAIN_DEPTH_MAX` **6** · `entry_st` **25 (`S_EPOP`)** · `coincide` **0** ·
`ce_clocks` 66,648 / 66,664 / 66,521 / 66,559 · **all eight gap counts on all
four seeds** · and the whole per-seed liveness census
(`fpops`/`qpops`/`INTA`/`IOR`/`IOW`/`HALT`/`CODE`/`MEMR`/`MEMW`) — **`diff`
empty over every scored line.**  These are the same four signatures WAVE 6's REF
and FLAT arms produced, which is a third, independent agreement.

The Verilator receipt moved, `d5c4a40eae278859…` → `79daa658d25a6795…`.
⚠ **THAT IS NOT EVIDENCE OF ANYTHING** — WAVE 3 measured that a receipt is not
reproducible across rebuilds of a byte-identical tree.  What the edit reached is
established in §2.4.

### 2.2 (b) `fz2_replay` — **SCORED-CONTENT sha256 IDENTICAL**

`fz2_replay --all-failures --pass-sample 200 --leg ret --no-fabric-era-guard`,
**305 seeds** replayed through `tb_sys` and scored against the banked SOCKET
rows with the corpus's own column policy and window:

```
scored-content sha256   de949fd373ed77de7f7d980a1728538de1b6ddaf6e200a9e61ba69bd1a8b2942   (BOTH)
rows                    305 vs 305
tb_sys receipt          efe6a258ebc085b3…  ->  16f66ab3c23e3f52…   MOVED, as it must
```

⚠ **`--no-fabric-era-guard` is stated rather than worked around** — it is L1's
standing caveat, unchanged: this tree has been a cross-era read since before
this wave touched it.  **What this leg measures is BEFORE vs AFTER on ONE tree.
It says nothing about fabric and no fabric claim is made from it.**

### 2.3 (c) THE LADDER — **31 legs SAME / 0 MOVED / 0 MISSING**

`sw/phase_split_ladder_diff.py sw/testdata/wave7/before sw/testdata/wave7/after`
exits 0.  This is G-2, G-3 and G-4 in one string; the values are §3.

### 2.4 ⚠ HOW WE KNOW THE EDIT REACHED THE TOOLS, SINCE A RECEIPT DOES NOT SAY SO

Four positive proofs, none of them a moved receipt:

1. **The Quartus INPUT MANIFEST is content-hashed and it lists the new files.**
   `sha256 53881d3c633e866e…`, **98 files** (was 88 in the pre-arm-file era),
   with `v30u_eu_arm_*.svh` ×9 and `v30u_eu_chain_pos.svh` each carrying their
   own hash.  A file the compiler did not read is not in that manifest.
2. **§7 case B**: reordering two blocks of the new pass in a scratch copy
   `$fatal`s with the new assertion's own message.
3. **§7 case D**: deleting the new fail-safe line changes a run that completes
   into a run that `$fatal`s.
4. **§6**: `v30u_eu`'s combinational ALUT count fell by a third and the whole
   design's ALMs by ~20 %.  The old text cannot produce that.

---

## §3 G-2 / G-3 / G-4 — THE LADDER, LEG BY LEG

**Every leg was verified against `docs/notes/standing_gates.md` before it was
scored.**  Both sides of the A/B are printed; the registered value is the third
column.

| leg | BEFORE | AFTER | registered |
|---|---|---|---|
| `r7_lint` | PASS, 0/0/0 | **PASS**, 0 undeclared carriers, 0 undeclared unresolved, 0 `stop` sites | PASS |
| `ss_lint --core ucore` | PASS, 232 / 228 flops / 0 UNMAPPED | **PASS, 232 addresses (109×2 BIU + 122×2 EU + tag), 228 architectural flops, 0 UNMAPPED** | see the ⚠ below |
| `check_core --opcodes all --cases 0` | 169,000/169,000 | **169,000 / 169,000** | 169,000 |
| `check_core --opcodes 8F.0` | 500/500 | **500 / 500** | 500 |
| HLT sweeps ⚠ `--waits 0/1/2/3` | 97 · 93 · 45 · 44 | **97 · 93 · 45 · 44 = 279/283** | 279/283 |
| `v0.1-w1` / `-w3` | 1,200 / 1,200 | **1,200 / 1,200** | 1,200 |
| `v0.1-w1 --opcodes EB` | 200 | **200** | 200 |
| the four `evt` cells | 200 / 1,200 / 200 / 1,200 | **200 / 1,200 / 200 / 1,200** | as registered |
| `v0.1-w1evt-biased` | 1,200 | **1,200** | 1,200 |
| `ulockstep --golden all --cases 50` | ALL LOCKSTEP | **17,350 / 17,350, ALL CASES LOCKSTEP** | 17,350 |
| `ghost_launch_law score` | 200/200 | **200/200 = 100.0 %** | 200/200 |
| `check_boot --core ucore` | 220 | **MATCH over 220 rows** | 220 |
| `check_boot 400 --core ucore` | 400 | **MATCH over 400 rows** | 400 |
| `check_ab_sim --core ucore` | 187 | **MATCH over 187 rows** | 187 |
| `sm3_s16_score --core ucore` | 1,320/1,371 | **1,320 / 1,371** | 1,320/1,371 |
| `demux_off_gate` | PASS | **PASS** | PASS |
| `test_artifact` | 45/45 | **45 / 45** | 45/45 |
| `test_quartus_gate` | 255/255 | **255 / 255** | ⚠ see below |
| `ucrom_mif_check` | PASS | **PASS** | PASS |
| `chain_lfsr_gate` | PASS | **PASS** — `CHAIN_MAX` 7, observed depth 6, 0 overflows | PASS |
| **G-4** `check_core all` at `--ce-div 2 / 3 / 8` | 169,000 each | **169,000 / 169,000 on all three** | 169,000 |
| **G-4** `--ce-div 1` | REFUSED | **REFUSED**, exit 2, clause cited | refused |

### 3.1 THE TWO KNOWN-STALE `standing_gates.md` ROWS — MEASURED, REPORTED, NOT TREATED AS FAILURES

* **`test_quartus_gate`** — `standing_gates.md` line 494 says **200/200**.
  **Measured 255/255 on BOTH sides.**  The row is stale by the Q-checks added
  since; the tool's own summary line is the live figure and it did not move
  across this landing.
* **`ss_lint`** — `standing_gates.md` line 1310 carries another branch's
  **226 addresses / 214 flops / `SS_VERSION` 0x8D / `SS_TAG` 0x8DE2**.
  **`master` reads 232 / 228 / `SS_VERSION` 0x8F / `SS_TAG` 0x8FE8**
  (`v30u_ss_pkg.sv:136`, *"ucore map v15 (operand-width tags)"*), and it reads
  that on **both** sides of this landing.  **Neither row was edited by this
  wave**; both disagreements are reported here.

### 3.2 G-3 — **NOT ONE FLOP MOVED**

`SS_VERSION` **0x8F**, `SS_COUNT` **232**, `SS_TAG` **0x8FE8**, **0 UNMAPPED**,
**228 architectural flops** — BIU 91 → 91 mapped, EU 137 → 134 mapped + 3
whitelisted — identical on both sides.  WAVE 6 measured registers 807 → 807 in
isolation and **the design agrees: no flop was added or removed.**

The one census line that moved is the one that must:
`EU (v30u_eu.sv +9 includes)` → **`+19 includes`**, and the EU's
*comb/next-state regs skipped* count **348 → 349** — that is `chain_open`, a
combinational next-state signal and not a flop.  **`v30u_ss_pkg.sv` was not
touched.**

---

## §4 WAVE 6's `CHAIN_PROBE` CENSUS — **PRESERVED, AND IT REPRODUCES EXACTLY**

The pre-registration required WAVE 6's sequence census to keep working or its
retirement to be argued.  It works, and re-run on the LANDED tree it is
**identical to WAVE 6's artifact line for line**
(`diff` against `sw/testdata/chainflat/dyncensus.txt` from
`=== THE DYNAMIC CENSUS ===` onward is empty):

* **8,447,821 CE edges** censused over two populations with nothing in common —
  the golden suite through `check_core` (which scored **169,000 / 169,000** on
  the probe build) and 4 × 400,000 LFSR clocks;
* **46 distinct sequences**, **0 table overflows**, max observed depth **6**;
* **PC-B1** states at position ≥ 1 == `st_zero_ok`'s nine: **PASS**;
* **PC-B2** every observed sequence walks the static adjacency edge for edge:
  **PASS**;
* **PC-B3 NON-VACUITY** — dropping the static edge
  `S_1BL_CHG -> S_INSTR_END` makes PC-B2 FAIL: **PASS**;
* **PC-B4** observed depth ≤ static depth: **PASS**;
* the whole distribution byte-identical, **68.98 % of edges at depth 1** and
  **13.68 % at depth 6** as before.

⚠ **THAT IS ALSO AN INDEPENDENT EQUIVALENCE RESULT AND IT IS THE SHARPEST ONE
HERE.**  The census records **which states occupied which positions of each CE
edge**.  It is identical after the flattening, so the flat pass does not merely
compute the same architectural outcome — **it walks the same states in the same
order at the same positions, 8,447,821 times.**

---

## §5 G-11 / G-12 / G-13 — THE THREE BARS THIS DOCUMENT ADDED

`python3 sw/chainflat_relocation_check.py` — **PASS**, and it is a standing
falsifier, not a one-off script.

| bar | result |
|---|---|
| **G-11** each of the nine bodies exists in `hdl/` **exactly once** | **MET, 9/9.**  Each is found in exactly one file, its own `v30u_eu_arm_<state>.svh` |
| **G-12** each body is **byte-identical** to its pre-edit text | **MET, 9/9** — 5 · 30 · 148 · 34 · 119 · 8 · 5 · 24 · 29 lines, **relocated, never rewritten** |
| **G-12** inlining the includes back reconstructs the pre-edit `case (st_n)` | **MET — IDENTICAL to `aba01feb07` from `case (st_n)` onward.**  The only deliberate change to that file outside the nine arms is its header comment |
| **G-13** the emitted order is a topological order of the static graph, re-derived at landing time | **MET.**  `sw/chainflat_graph.py` on the landed tree: `st_zero_ok` states **9**, **cycles: NONE (it is a DAG)**, order `S_TAIL_POP S_TAIL S_INSTR_END S_TAKE_OPC S_EA_CALC S_DECODE S_DECODE2 S_BIND S_ENTER` — **identical to WAVE 6's, derived independently** — and **all seven** chainable→chainable edges run FORWARD in it: `S_TAKE_OPC→S_DECODE` 3→5, `S_DECODE→S_DECODE2` 5→6, `S_EA_CALC→S_BIND` 4→7, `S_BIND→S_ENTER` 7→8, `S_TAIL→S_INSTR_END` 1→2, `S_TAIL_POP→S_INSTR_END` 0→2, `S_INSTR_END→S_TAKE_OPC` 2→3.  **BACKWARD EDGES: none** |

---

## §6 THE QUARTUS LEGS — G-5, G-6, G-7, G-8

⚠ **`docs/notes/standing_gates.md` §A GOVERNS EVERY FIGURE BELOW.  ONE GREEN
BUILD IS NOT CLOSURE; the same tree has drawn 19.42 and 45.91 MHz.**  Every
sweep is MAP ONCE, FIT ONCE PER SEED over 5 seeds, so the five draws are a
distribution of ONE mapped netlist.  Both configurations, every time.

### 6.1 G-5 — **THE LANDING'S OWN TIMING BAR, WITH the exception.  MET, 10 of 10 draws PASS.**

`sw/quartus_gate.py --seeds 5` and `--seeds 5 --retention`, the tree's current
SDC unchanged.

| draw | CONTROL Fmax | worst setup | ALMs | | RETENTION Fmax | worst setup | ALMs |
|---|---:|---:|---:|---|---:|---:|---:|
| seed 1 | 42.98 | +7.982 | 8,117 | | 41.06 | +6.898 | 8,135 |
| seed 2 | 43.01 | +7.999 | 8,090 | | 42.65 | +7.803 | 8,149 |
| seed 3 | 41.26 | +7.013 | 8,079 | | 44.10 | +8.574 | 8,125 |
| seed 4 | **41.06** | +6.896 | 8,103 | | 41.87 | +7.367 | 8,137 |
| seed 5 | 42.02 | +7.450 | 8,098 | | **41.06** | +6.898 | 8,139 |

> ### **CONTROL `worst-of-5@seeds{1,2,3,4,5}` = 41.06 MHz · RETENTION = 41.06 MHz.  E1–E5 PASS on ALL TEN DRAWS.  TNS 0.000 setup AND hold on every domain, 0 errors, 0 latches, 0 `lpm_divide`.**

**AGAINST THE PRE-LANDING FIGURE THE BAR NAMES — WAVE 3's CONTROL 37.29–39.51 —
THIS IS +1.55 MHz ON THE BEST PRE-LANDING DRAW AND +3.77 ON THE WORST.  THERE
IS NO REGRESSION.  G-5 IS MET.**

Records: `sw/testdata/g6dist/wave7-chainflat-control-n5/distribution.json`
**`2772002011546f6f…`** (verdict PASS) and
`…-retention-n5/distribution.json` **`569b46b853a43d2b…`** (verdict PASS,
**self-labelling `RETENTION (X1_AD_RETENTION=1)` DERIVED from the reports** —
E-6, unchanged).  `E8_seed_honoured` PASS on every draw, read back from
Quartus's own *Fitter Initial Placement Seed* row.

⚠ **AND THE BINDING ARC HAS MOVED OUT OF THE CHAIN.**  On **all five** CONTROL
draws the whole-design binding path launches inside the microcode ROM —
`v30u_ucrom|altsyncram:ucdecode_rtl_0|…|ram_block1a*~PORT_A_WRITE_ENABLE_REG`.
`binding_class_flips` **5**.  That is WAVE 6 §5.4's structural prediction —
*"after the fold the chain is no longer the binding structure; the front end
is"* — **confirmed IN THE DESIGN and not in a harness.**

### 6.2 G-6 — **THE SCOREBOARD, WITHOUT the exception.  RED, AS EXPECTED, AND THE GAP FELL BY TWO THIRDS.**

`sw/l2_noexc_g6.py --seeds 5 --label wave7-chainflat-noexc --configs
control,retention` — it deletes the `ce → ce` multicycle from
`hdl/nec_test.sdc` for the duration of the sweeps and restores it with
`git checkout --` in a `finally`.  **No SDC change was landed; the USER RULING
of 2026-09-08 was not re-opened.**

| draw | CONTROL Fmax | worst setup | `core_domain` k | `off_class` | | RETENTION Fmax | worst setup | k | `off_class` |
|---|---:|---:|---:|---|---|---:|---:|---:|---|
| seed 1 | 29.22 | −2.970 | 1.0 | `SAME` | | 28.94 | −3.302 | 1.0 | `SAME` |
| seed 2 | **28.32** | −4.063 | 1.0 | `SAME` | | 29.46 | −2.694 | 1.0 | `SAME` |
| seed 3 | 29.02 | −3.211 | 1.0 | `SAME` | | 30.07 | −2.005 | 1.0 | `SAME` |
| seed 4 | 29.00 | −3.233 | 1.0 | `SAME` | | **28.90** | −3.349 | 1.0 | `SAME` |
| seed 5 | 28.72 | −3.573 | 1.0 | `SAME` | | 29.24 | −2.948 | 1.0 | `SAME` |

**Every draw RED, as pre-registered.  RED IS NOT A REVERT CONDITION.**

> ### **THE SCOREBOARD**
>
> | | pre-landing (WAVE 3 / L2) | **WAVE 7** | move | **GAP to 32.0** |
> |---|---:|---:|---:|---:|
> | **CONTROL, no exception, `worst-of-5`** | 22.18 | **28.32** | **+6.14** | 9.82 → **3.68** |
> | **RETENTION, no exception, `worst-of-5`** | 22.16 | **28.90** | **+6.74** | 9.84 → **3.10** |
>
> **THE NO-EXCEPTION GAP FELL BY 62.5 % (CONTROL) AND 68.5 % (RETENTION) IN ONE
> LANDING.  IT IS STILL A GAP, AND THE GOAL STATE IS STILL RED.**

⚠ **THE DELETION IS CHECKED, NOT ASSERTED, ON EVERY ONE OF THE TEN DRAWS.**
`off_class` is `['SAME']` with `k_measured = 1.0` against a nominal of 2.0 on
10 of 10 — a draw with an EMPTY `off_class`, or one whose `SAME` still read
k = 2.0, was fitted to the exception and its Fmax would answer a different
question.  None did.

Records: `sw/testdata/g6dist/wave7-chainflat-noexc-control-n5/distribution.json`
**`3df71113402c82f9…`** and `…-noexc-retention-n5/distribution.json`
**`4de850c056501ebf…`**.  `hdl/nec_test.sdc restored: CLEAN` printed by the
driver's own `finally`, and `git status --porcelain hdl/` is empty afterwards.

⚠ **AND THE BINDING PATH IS THE MICROCODE ROM, ON BOTH CONFIGURATIONS.**
CONTROL's worst draw is bound
`ucdecode_rtl_0|…|ram_block1a7~PORT_A_WRITE_ENABLE_REG →
ucdecode_rtl_0|…|ram_block1a5~porta_address_reg6` — **an M10K's own write-enable
to another M10K's address register, with the chain nowhere on it.**
RETENTION's is `ram_block1a6~PORT_A_WRITE_ENABLE_REG → eff_op[2]~2_OTERM2188`.
**The next 3 ns are in the front end, exactly where WAVE 5 §9.2 pointed and
where no wave has yet measured a change.**

### 6.3 G-7 — **THE OUT-OF-CONTEXT CORRECTION.  WAVE 6's HARNESS WAS RIGHT TO 0.018 ns.**

The brief called this *"the most interesting number this wave produces"*, and it
is, because it settles a question WAVE 5 and WAVE 6 disagreed about.

* **WAVE 5** measured out-of-context estimates mispredicting a realised
  downstream half by **+11.3 to +20.0 ns**, and the loop by **+15.30 ns**, and
  said so before WAVE 6 existed.
* **WAVE 6** measured its own positive control reproducing WAVE 5's *in-situ*
  per-folded-position figure to **0.025 ns**, and argued from that that its
  harness was representative.
* **The prediction on the table was −9.431 ns** (WAVE 6's registered seeds
  1 – 3; −9.315 over all six).

**THE QUANTITY COMPARED IS THE SAME ON BOTH SIDES AND IT COMES FROM ONE TOOL**:
the no-exception CONTROL sweep's per-draw path period `T = 31.250 − slack`,
which is exactly what Quartus's own restricted Fmax inverts (`1000/43.774 =
22.84`, `1000/34.220 = 29.22` — checked on every draw).

| | pre-landing, 5 draws | WAVE 7, 5 draws | **delta** |
|---|---|---|---:|
| CONTROL periods (ns) | 43.736 · 43.774 · 43.814 · 43.949 · 45.093 | 34.220 · 34.461 · 34.483 · 34.823 · 35.313 | |
| **mean** | **44.073** | **34.660** | **−9.413** |
| worst | 45.093 | 35.313 | −9.780 |
| RETENTION mean | 44.142 | 34.110 | −10.032 |

> ## **WAVE 6 PREDICTED −9.431 ns OUT OF CONTEXT.  THE DESIGN REALISED −9.413 ns.  THE CORRECTION IS +0.018 ns — 0.2 %.**
>
> On the worst draw it is **−0.349 ns** (the design gave slightly MORE than the
> harness predicted).  **WAVE 5's +11.3 … +20.0 ns mispredictions did not
> recur.**

⚠ **AND HERE IS WHY THEY DID NOT, STATED AS A READING AND LABELLED AS ONE —
IT IS NOT A MEASUREMENT.**  WAVE 5's mispredicting estimates were of a
**realised half after a structural split**: they predicted what a partition
*that did not yet exist* would deliver, and the fitter's freedom to reassociate
across the new boundary is precisely what they could not model.  WAVE 6's was a
**DIFFERENCE between two builds compiled identically**, with the front end
byte-identical between them — and WAVE 6 §6.3 said so at the time
(*"the comparison is a DIFFERENCE, and the difference is the defensible
part"*).  **The evidence now says a DIFFERENCE transfers and a PARTITION
PREDICTION does not.  One landing is one data point and it is not a law.**

⚠ **THE ABSOLUTE NUMBER STILL DOES NOT TRANSFER, AND THAT IS UNCHANGED.**
WAVE 6's FLAT arm measured **34.682 ns** in isolation and this design measures
**34.660 ns** — a coincidence of 0.02 ns between two different circuits, and it
must not be quoted as a prediction.  WAVE 6's REF arm was 43.997 against the
design's 44.073 for the same reason.  **What agreed is the delta.**

⚠ **AND ONE BASELINE CAVEAT, WHICH MAKES THE LANDING LOOK *WORSE*, SO IT IS
STATED PLAINLY.**  The pre-landing five draws above are `sw/testdata/g6dist/
l2-noexc-control-n5` (`ad70054b87509dbb…`), taken 2026-09-08 at the L2 landing.
That is the figure the pre-registration names and the one G-6 is scored
against.  **It is not the same commit as `aba01feb07`** — the REP `CL == 0` ALU
fixes (`be4eb2c32f`, `e61f2e0988`, `c59d205479`) landed between them.
Re-measured on `aba01feb07` ITSELF (§6.4's control run, same tool, same seeds),
the pre-landing tree reads **T_min 46.599 ns / 21.46 MHz on seed 1** where L2
read 43.774 / 22.84 — i.e. the tree had got **~2.8 ns SLOWER** before this wave
touched it.  **Scored against its own immediate predecessor the fold is worth
MORE than −9.4 ns, and this document deliberately quotes the SMALLER,
pre-registered comparison.**

### 6.4 ⚠ WAVE 5's SEGMENTER REFUSES ON THE LANDED TREE, AND THAT IS THE INSTRUMENT WORKING

`sw/run_chain_anatomy.py --control-seeds 1,2,3 --retention-seeds 1`, the WAVE 5
per-position profiler, on the landed tree (`sw/testdata/chainanat-wave7/`):

```
  PC-3 SEGMENTER  st_zero_ok pins in the netlist: 0
       boundaries on the FORCED path, real markers : -1  (MUST be >= 1)
       *** PC-3 FAILED ***
  === CONTROLS: *** FAILED -- NOTHING BELOW MAY BE QUOTED *** ===
```

**4 draws of 4**, control and retention alike.  The segmenter cuts the arc into
chain positions by finding netlist pins named after `st_zero_ok`; **after the
fold there are none** — WAVE 6 measured that cone count going **13 → 0** on
FLAT, because the nine `st_n == S_X` guards make the nine-way OR redundant and
Quartus deletes it.  **The instrument has nothing to cut with and says so
instead of reporting "0 boundaries"** — which is exactly the hardening WAVE 5
§1.1 put in after its own PC-4 nearly reported absence as agreement.

**THE REFUSAL IS NON-VACUOUS, AND THAT IS MEASURED, NOT ARGUED.**  The same
tool, same seeds, run on the PRE-LANDING commit `aba01feb07` in a clean git
worktree (`sw/testdata/chainanat-wave7-prelanding/`):

```
  PC-3 SEGMENTER  st_zero_ok pins in the netlist: 10
       boundaries on the FORCED path, real markers : 4  (MUST be >= 1)
       boundaries on the SAME path, a fake marker  : 0  (MUST be 0)
  === CONTROLS: ALL PASS ===
```

and its arc profile is WAVE 5's, recognisably — **43.035 ns, 4 boundaries,
segment 0 = 21.833 ns (50.7 %), the four folded positions 3.617 · 8.372 · 4.595
· 4.618 = 21.202 ns.**  **The tool is fine.  The structure it measures is
gone.**

**AND BECAUSE IT PASSES THERE, THE PRE-LANDING RUN IS ALSO THE SAME-TOOL,
SAME-SEED, SAME-COMMIT A/B FOR G-7.**  `sta_truefmax_probe.tcl`'s `SAME` class
(`ce → ce`, k = 1.0000 on every draw, so the deletion reached the compiler in
both trees):

| draw | `aba01feb07` T_min | `2ceb8c3ba3` T_min | delta |
|---|---:|---:|---:|
| CONTROL seed 1 | 46.599 (21.46 MHz) | **34.220 (29.22)** | −12.379 |
| CONTROL seed 2 | 43.309 (23.09) | **35.313 (28.32)** | −7.996 |
| CONTROL seed 3 | 45.624 (21.92) | **34.461 (29.02)** | −11.163 |
| **mean of the three** | **45.177** | **34.665** | **−10.512** |
| RETENTION seed 1 | 43.522 (22.98) | **34.552 (28.94)** | −8.970 |

⚠ **THESE FOUR FITS REPRODUCE THE G-6 SWEEP'S NUMBERS TO THE THOUSANDTH ON THE
LANDED SIDE** (34.220 · 35.313 · 34.461 · 34.552 against §6.2's slacks
−2.970 · −4.063 · −3.211 · −3.302) — an independent fit of the same seeds
through a different driver, which is the control that the sweep is
reproducible.

⚠ **AND ON THIS BASIS THE FOLD IS WORTH −10.512 ns, NOT −9.413.**  Three draws
are not a distribution and this is **NOT** the scored figure; §6.3's
pre-registered comparison against L2 is.  It is reported because it is the
comparison against the landing's own immediate predecessor, and because
**quoting only the smaller number would be choosing a baseline after seeing the
result.**  Both are here.


### 6.5 G-8 — AREA

**A&S per entity, no-exception CONTROL map, one map per tree, `aba01feb07` vs
`2ceb8c3ba3`.**  ⚠ `ucore_provenance.md` §74.4a governs: **A&S combinational
counts are not reproducible run to run** (this wave saw `v30u_eu` read 6,066 and
6,126 on two maps of the identical tree), so the comb figures are quoted with
that spread in mind.  **The REGISTER counts are reproducible, and they are the
ones G-3 turns on.**

| entity | comb ALUTs, PRE | comb ALUTs, POST | delta | regs, PRE → POST |
|---|---:|---:|---:|---:|
| **`v30u_eu:u_eu`** | **9,185** (own 8,564) | **6,126** (own 5,513) | **−3,059 (−33.3 %)** | **728 → 728** |
| `v30_core:u_core` | 10,269 | 7,250 | −3,019 (−29.4 %) | 1,162 → 1,162 |
| `system_large` | 11,577 | 8,561 | −3,016 (−26.1 %) | 2,340 → 2,340 |
| `emu:emu` | 12,200 | 9,189 | −3,011 (−24.7 %) | 2,969 → 2,969 |
| `sys_top` (whole design) | 15,297 | 12,295 | −3,002 (−19.6 %) | 5,086 → 5,084 |
| `v30u_biu:u_biu` | 1,083 | 1,123 | +40 (+3.7 %) | 434 → 434 |
| `v30u_ucrom` | 621 | 613 | −8 | 0 → 0 |

> **WAVE 6 measured −29.3 % of the combinational ALUTs in isolation, with not
> one flop.  IN THE DESIGN THE EU LOST 33.3 %, AND NOT ONE FLOP.**  The fold
> delivered MORE area in the design than in the harness, and the whole design —
> which contains a great deal that is not the core — lost **19.6 %** of its
> combinational ALUTs.

**FITTED ALMs, five draws per configuration, no-exception:**

| | PRE (L2) | POST | delta |
|---|---|---|---:|
| CONTROL | 10,091 – 10,132, **24 %** of the device | **8,314 – 8,363, 20 %** | **≈ −1,780 (−17.6 %)** |
| RETENTION | 10,114 – 10,163, 24 % | 8,357 – 8,385, 20 % | ≈ −1,772 (−17.5 %) |

and on the WITH-exception G-5 sweeps, **8,079 – 8,117 (19 %)** CONTROL /
**8,125 – 8,149 (19 %)** RETENTION.

**THE RETENTION MAPS SAY THE SAME THING, which is the cross-check that this is
the fold and not the configuration:** `v30u_eu` **9,195 → 6,100 (−33.7 %)**,
`sys_top` **15,341 → 12,265 (−20.1 %)**, and registers **728 → 728** in the EU,
**2,990 → 2,990** in `emu`, **2,361 → 2,361** in `system_large` — with the same
**−2 in `sys_top`'s own row (424 → 422)** and nowhere else.  The retention
model's own **+21 registers** (§73.9) are present and unmoved on both trees
(`emu` 2,969 → 2,990 control → retention, both sides), which is the positive
proof that the retention maps really are retention maps.

⚠ **TWO THINGS RECORDED AND NOT EXPLAINED.**
**(a)** `v30u_biu` grew **+40 combinational ALUTs (1,083 → 1,123)** while
nothing in the BIU was edited.  It is within the §74.4a non-reproducibility band
for A&S combinational counts across two different maps, and **its register count
did not move**; recorded, not explained, and **not claimed as a cost of the
landing.**
**(b)** whole-design dedicated logic registers read **5,086 → 5,084**, −2.
The **−2 is entirely in `sys_top`'s OWN row (424 → 422), OUTSIDE `emu:emu`** —
`emu`, `system_large`, `v30_core`, `v30u_biu` and `v30u_eu` are **identical to
the register**.  **Not one flop moved anywhere inside the design.**  The two
sit in the MiSTer framework's top level; §74.4a's sibling observation (a
whole-design count wobbling by ±1 in an unrelated module) is the standing note.


---

## §7 G-9 — NON-VACUITY.  **THE ASSERTION FIRES, AND THE FAIL-SAFE IS REACHED**

Four legs, each a scratch copy of `hdl/rtl/ucore/` built standalone against
`tb_chain_lfsr` and run for 200,000 fabric clocks.  **The shipped RTL is never
touched.**

| leg | construction | measured |
|---|---|---|
| **A  CONTROL** | the tree as landed | **exit 0, 0 CHAIN OVERFLOW, `RESULT OK`** — the assertion is silent when it should be |
| **B  clause (i), the BACKWARD EDGE** | the `S_DECODE` block moved AFTER the `S_DECODE2` block, i.e. one fall-through edge now runs backward through the emitted order | **FIRES.**  `%Fatal ... v30u_eu: CHAIN OVERFLOW -- the flattened chain pass ended with stop still low (entered in st=25, now st=3, ...)`.  **This is the falsifier for the flattening's own premise and it works** |
| **C  the FAIL-SAFE, PRESENT** | `S_PFX_CHG`'s `stop = 1'b1;` deleted, so a position-0 arm falls through to `S_OPC_POP` — a state that is NOT one of the nine — with `stop` low | **exit 0, 0 CHAIN OVERFLOW, `RESULT OK`.**  The clock is spent; nothing hangs |
| **D  the FAIL-SAFE, DELETED** | C's perturbation **plus** the `if (!stop && !st_zero_ok(st_n)) stop = 1'b1;` line removed | **FIRES.**  `CHAIN OVERFLOW ... (entered in st=4, now st=0, ...)`.  **C's silence is the fail-safe's doing and not an accident of the stimulus** |
| **clause (ii), the DEPTH BOUND** | `python3 sw/chain_lfsr_gate.py --nonvacuity` — the gate's own mode, which copies the ucore to scratch, rewrites `CHAIN_MAX` to `4'd4` and requires the `$fatal` | **H-3 MET — fired on 4/4 seeds**, unedited gate, at a bound below the observed maximum |

**Both `CHAIN OVERFLOW` clauses are demonstrated reachable, and the fail-safe is
demonstrated to be doing the thing it is kept for.**

---

## §8 THE BARS, SCORED

| bar | verdict |
|---|---|
| **G-1** PIN IDENTITY, three clauses, BEFORE taken on the unedited tree first | **MET on all three.**  (a) four `chain_lfsr_gate` signatures BYTE-IDENTICAL with `CHAIN_DEPTH_MAX`, `entry_st`, `coincide`, every gap count and the whole liveness census — `diff` empty; (b) `fz2_replay` scored-content sha256 **`de949fd373ed77de…` on BOTH sides**, 305 seeds, the `tb_sys` receipt the one field that moved; (c) the ladder **31 SAME / 0 MOVED / 0 MISSING**.  §2 |
| **G-2** the ladder at its registered values, verified against `standing_gates.md` first | **MET, every leg.**  169,000 · 500 · 279/283 (⚠ with `--waits 0/1/2/3`) · 1,200/1,200 · 200 · 200/1,200/200/1,200 · 1,200 · 17,350 ALL LOCKSTEP · 200/200 · 220 · 400 · 187 · 1,320/1,371 · PASS · 45/45 · 255/255 · PASS · PASS.  **The two known-stale rows are MEASURED AND REPORTED, not treated as failures**: `test_quartus_gate` reads **255/255** against the file's 200/200, and `ss_lint` reads `master`'s **232 / 228 / 0x8F** against the file's cross-branch 226 / 214 / 0x8D.  §3, §3.1 |
| **G-3** `ss_lint` 0, map UNCHANGED, 0 UNMAPPED, **no flop added or removed** | **MET.**  `SS_VERSION` **0x8F** · `SS_COUNT` **232** · `SS_TAG` **0x8FE8** · **228 architectural flops** · 0 UNMAPPED, identical on both sides; `v30u_ss_pkg.sv` untouched.  The only moved census line is `+9 includes` → **`+19 includes`** and comb/next-state regs 348 → 349 (`chain_open`).  §3.2 |
| **G-4** 169,000 at `--ce-div` 2, 3, 4 and 8; `--ce-div 1` refused | **MET.**  169,000/169,000 on all four; `--ce-div 1` exits 2 citing the clause.  §3 |
| **G-5** `quartus_gate --seeds 5` PASSES E1–E5 on every draw, both configurations; no regression against WAVE 3's 37.29–39.51 | **MET.  10 of 10 draws PASS.  CONTROL `worst-of-5` 41.06 · RETENTION 41.06**, TNS 0.000 setup AND hold every domain.  **+1.55 MHz on WAVE 3's best pre-landing draw.**  §6.1 |
| **G-6** the scoreboard WITHOUT the exception, both configurations, gap stated | **MEASURED AND RED, AS PRE-REGISTERED — NOT A REVERT CONDITION.  CONTROL 28.32 (gap 3.68), RETENTION 28.90 (gap 3.10)**, against a pre-landing 22.18 / 22.16 (gap 9.82 / 9.84).  Every draw's verdict, Fmax, worst setup, `core_domain` k and `off_class` in §6.2; **`off_class` `['SAME']` k = 1.0 on 10 of 10, so the deletion reached the compiler every time.**  §6.2 |
| **G-7** the out-of-context correction | **MEASURED, AND IT IS THE WAVE'S SHARPEST RESULT.  WAVE 6 predicted −9.431 ns; the design realised −9.413 ns.  The correction is +0.018 ns.**  §6.3, with the reason WAVE 5's +11.3 … +20.0 ns does not recur stated as a READING and labelled as one |
| **G-8** area, `v30u_eu` and the whole design, against WAVE 6's −29.3 % / 807 → 807 | **MEASURED.**  §6.5 |
| **G-9** the `CHAIN OVERFLOW` assertion still fires; the `st_zero_ok` fail-safe still reachable and demonstrated | **MET, four legs with a control.**  Clause (i) fires on a constructed BACKWARD edge; clause (ii) fires 4/4 under `chain_lfsr_gate --nonvacuity`; the fail-safe turns a `$fatal` into a spent clock, and **deleting it turns the spent clock back into a `$fatal`** — so its silence is its doing.  §7 |
| **G-10** the revert condition | **NOT TRIGGERED.**  No leg of G-1 / G-2 / G-3 / G-4 moved; G-5 did not regress, it improved.  **No bar was softened and no gate file was edited to make the landing possible.**  G-6 is RED and that was registered in advance as expected |
| **G-11** one source of truth per arm | **MET, 9/9**, `sw/chainflat_relocation_check.py`.  §5 |
| **G-12** the include is transparent — bodies relocated, never rewritten | **MET, 9/9 byte-identical, and the reconstruction of `case (st_n)` is IDENTICAL to `aba01feb07`.**  §5 |
| **G-13** the emitted order is a topological order, re-derived at landing time | **MET.**  DAG confirmed, 7 of 7 chainable edges FORWARD, 0 backward.  §5 |

### 8.1 WHAT IS OWED

1. ⚠ **THE FABRIC CONFIRMATION.  NOTHING HAS BEEN ON A BOARD.**  This landing
   changes the EU's decode, and **a bitstream will have to prove it**.  Every
   fabric figure in this repo was taken on FLASH #21 or earlier and **may not be
   quoted against this tree**.  Recorded as owed, deliberately not taken: the
   brief is OFFLINE ONLY.
2. **THE FRONT END.**  G-6's binding path is inside the microcode ROM on both
   configurations and **the remaining 3.10 – 3.68 MHz is there**.  It has never
   been attacked.  WAVE 5 §9.2 named it; this wave is the first to make it the
   *only* thing left.
3. **WAVE 5's SEGMENTER NEEDS A NEW MARKER** if the per-position profile is ever
   wanted again — `st_zero_ok` no longer exists in the netlist.  **Deliberately
   not done here**: choosing a new marker after seeing that the old one refused
   is the shape of fitting, and no number in this document depends on it.
4. **THE 24 VACUOUS `if (chain == 4'd0)` GUARDS.**  They cost nothing and they
   carry the position-0-only property that `sw/chainflat_graph.py` PC-A1 reads.
   A later wave may want to replace the text with something that is not a dead
   conditional; **it must keep a machine-readable complement of `st_zero_ok`
   when it does.**


---

## §9 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**  No
  Codex.  No nested subagent.
* Single-writer guard by EXACT binary name before every Quartus stage;
  `hdl/nec_test_ucore.qsf` restored with `git checkout --` between runs (the
  declared §70.7 exemption — `quartus_map` rewrites it), and `hdl/` verified
  clean after every group.
* The no-exception legs patch `hdl/nec_test.sdc` for the duration and restore it
  in a `finally`; **no custom SDC rule was added, and the USER RULING of
  2026-09-08 was not re-opened.**
* `~/.cache/ucsimt-tmp/` for every intermediate; nothing large in `/tmp`.
* Receipted binaries rebuilt through their own recipes.  **A moved Verilator
  receipt is not evidence** (WAVE 3); §2.4 gives four things that are.
* `git add -A hdl/` was never used — every `hdl/` path was added by name.
* **A number with no artifact id is not quotable.**  Every figure above is in
  `sw/testdata/wave7/`, `sw/testdata/g6dist/wave7-chainflat-*/` or
  `sw/testdata/chainanat-wave7*/`.
* **Recorded what was measured, not what was expected.**

### 9.1 ONE INSTRUMENT MISTAKE, RECORDED

The first CONTROL sweep was launched with **`--no-asm`**, which skips
`quartus_asm`.  `quartus_gate`'s **E2** bar is *"0 compile errors, **every stage
Successful**"*, and with no `asm` stage it reads `asm: None` and **E2 can never
pass** — every draw came back `RED` with E3, E4, E5 and E8 all green.  That is
not a timing result and it is not a G-5 failure; it is a bar that cannot be met
by a build that does not exist.  **The sweep was discarded, its artifact
directory deleted, and both legs re-run in full WITH `quartus_asm`.**  The
re-run reproduced every Fmax to the hundredth (42.98 · 43.01 · 41.26 on seeds
1–3, both times), which is the control that only the missing stage differed.
*Registered here because "a bar cannot be met by this invocation" looks
identical to "the tree got worse" in a summary line.*

### 9.2 A SECOND INSTRUMENT NOTE — `l2_noexc_g6.py` OVERWRITES L2's COMMITTED LOGS

`sw/l2_noexc_g6.py` hard-codes its per-leg log path as
`sw/testdata/l2/g6_{cfg}_noexc_n{n}.log`, so this wave's no-exception sweeps
**overwrote WAVE 3's committed ones in place**.  Noticed at staging, restored
with `git checkout --`, and **nothing in this document reads those files** — the
figures come from `sw/testdata/g6dist/wave7-chainflat-noexc-*/
distribution.json`, which the tool names per `--label` and therefore does not
collide.  Recorded rather than fixed: a path fix is a change to a tool whose
output another wave's document cites, and it belongs to whoever next needs it.

