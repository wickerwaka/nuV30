# WAVE 6 — THE CHAIN FLATTENING STUDY.  RESULTS, SCORED AS REGISTERED.

Pre-registration **`39e201aa6c`**
(`docs/notes/chainflat_prereg_2026-09-09.md`), committed **before the first
Quartus stage**; instruments **`d45de50a28`**, committed before it.

**THIS IS A STUDY.  IT PROPOSES NO DESIGN FOR THE CORE AND LANDS NOTHING IN
IT.**  MEASUREMENT ONLY.  OFFLINE ONLY.  **NO BOARD.  NO FLASH.  NO BITSTREAM
WAS PROGRAMMED.**  No Codex consulted.  No nested subagent spawned.  It is
**NOT A GATE**, it writes **no receipt**, and **no figure in it may be quoted
as a pass**; `docs/notes/standing_gates.md` §A governs every timing figure
below.

| | |
|---|---|
| **Tree** | `39e201aa6c` (`master`) |
| **The one RTL edit** | `hdl/rtl/ucore/v30u_eu.sv`, a sequence census strictly inside the existing `` `ifdef CHAIN_PROBE `` (undefined by default, sim-only).  **F-3: no other tracked file under `hdl/` is modified, at the start or at the end** |
| **Artifacts** | `sw/testdata/chainflat/` — `static_graph.txt`, `static_controls.txt`, `probe_invisible.txt`, `dyncensus.{txt,json}`, `compose.{txt,json}`, `compose_controls.txt`, `proto.json`, `verify.txt`, `flat_prototype.diff`, `cf_ref.qsf`, `cf.sdc`, `{ref,flat}.{map,fit}.rpt.gz`, `{ref,flat}_seed{1..6}.{txt,arrivalpoints.txt,census.txt}`, `report.{txt,json}`, `synth_seeds{123,456}.{out,json,log.gz}` |
| **Amendment** | **A-1** `a734dd3d79` (`docs/notes/chainflat_amendment_A1_2026-09-09.md`), committed **before the seed 4/5/6 fits existed** |
| **Tool** | Verilator 5.032; Quartus 17.1.0 Lite Build 590, `5CSEBA6U23I7`, Slow 1100 mV 100 C |

---

## §0 THE HEADLINE

> ### **THE UNROLL IS AN ARTIFACT.  FLATTENING FINDS NANOSECONDS — ABOUT 9.3 OF THEM ON THE STANDALONE HARNESS — AND IT STILL DOES NOT REACH 29.6.**

| the question | the measurement |
|---|---|
| **is the 7-copy unroll a modelling artifact or a description of the die?** | **ARTIFACT**, on four independent measurements (§6.1) |
| **would a flattened composed cone be shorter?** | **YES.  MEASURED.**  worst reg → reg arc **43.969 → 34.538 ns**, **−9.431 ns / −21.4 %**, ranges disjoint by 7.045 ns |
| **and smaller?** | **combinational ALUTs 10,052 → 7,104, −29.3 %**, with **not one flop** added or removed |
| **does it compute the same function?** | **YES, and that is a gate, not an argument**: **169,000 / 169,000** and four **byte-identical** LFSR signatures |
| **the irreducible serial depth — the floor** | **4 of 6 positions** on the deep mass, **2 of 3** on the shallow mass, **5** maximum anywhere |
| **does it close the campaign's −13.9 ns gap?** | ⚠ **NO, AND NOT CLOSE.**  Carried at face value onto the design's 43.485 ns arc it lands near **34.2 ns against a 29.6 ns requirement**, and WAVE 5 already measured that deleting the *entire* folded chain for free leaves **29.490 ns** |

⚠ **AND THE FIGURE IS NOT A PREDICTION FOR THE CORE.**  It is a standalone
harness.  WAVE 5 measured out-of-context estimates mispredicting a realised
downstream half by **+11.3 to +20.0 ns** and the loop by **+15.30 ns**.  §6.3
states the uncertainty in full.

⚠ **ONE REGISTERED BAR MISSED AND IT IS REPORTED AS A MISS, NOT RESTATED.**
**P-1(c)** asked for `ld_ripe_prev_n` ≤ 1 cone and measured **3, on all six
draws of both arms**.  P-1 is therefore MISSED and, by the pre-registration,
that voids deliverable D on the strength of the original bar.  The bar is not
widened.  Amendment **A-1** (`a734dd3d79`), committed **before the seed 4/5/6
fits existed**, states the erratum — the harness makes `q_ripe` a VIRTUAL INPUT
PIN, so the cone has nothing to fold into — registers a mechanism-shaped
replacement, and **scores it only on the three draws that did not select it**.
**P-1′(c) and P-1″ are MET on seeds 4, 5, 6.**  Every quotation of §5 carries
P-1(c)'s miss beside it.

---

## §1 THE SPEC SAYS THE DECOMPOSITION IS PHYSICAL AND THE **UNROLL** IS NOT

The brief asked whether the step decomposition is physical or a C++
convenience.  `sim/loader_impl.h` and `sim/exec_impl.h` answer it, and the
answer is **both, in different places.**

**THE CLOCK BOUNDARIES ARE PHYSICAL.**  The model is a straight-line C++
function whose only notion of time is `biu.charge(n)` and the `wait_*()` calls.
Every one of those is a MEASURED cycle count with its own provenance entry —
`loader_impl.h`'s own comment block gives the schedule it was fitted to
(*"opcode 0, modrm 1, disp8 3, disp16 2 and 4"*).  A state that costs a clock
is a description of the die.

**THE NINE ZERO-COST STATES ARE C++ PROGRAM-COUNTER POSITIONS.**  They are
exactly the statement positions with **no `charge()` between them and their
predecessor**:

| chainable state | the SPEC statement it is a cut point in |
|---|---|
| `S_TAKE_OPC` | `pop_opcode()`'s `bool pre = biu.opcode_pending(); … if (!pre) biu.charge(1);` — when `pre` is true there is **no charge**, `loader_impl.h:240-245` |
| `S_DECODE` | `uint16_t v = pla3::kNative[b]; if (!pla3::is_prefix(v)) break;` — `loader_impl.h:252-253` |
| `S_DECODE2` | the post-loop `one_byte_logic` / width / ModR-M fan-out, `loader_impl.h:283-373` |
| `S_EA_CALC` | `ea_compute(m, rm, disp)` — one pure function call, `loader_impl.h:394` |
| `S_BIND` | the OPC select and operand binding, `loader_impl.h:414-484` |
| `S_ENTER` | `out.entry = {page, opc, 0}` and `run_micro`'s prologue, `loader_impl.h:512-515` / `exec_impl.h:1185-1188` |
| `S_TAIL` | `if (pend_.active) { if (!opr_fresh_) deliver_read(); emit_pending(); }` after the row loop breaks, `exec_impl.h:1629-1634` |
| `S_TAIL_POP` | `const bool deferred = !biu_.opcode_pending(); … biu_.opcode_prefetch(…); if (deferred) biu_.charge(1);`, `exec_impl.h:1646-1652` |
| `S_INSTR_END` | `step()` returns; the successor's `begin_sequence()` / `clear_consumed()` and `loader_decode`'s per-instruction latch reset, `exec_impl.h:1114-1117` / `loader_impl.h:190-211` |

**They exist because an RTL state machine has no program counter and a C++
function does.**  The die has neither: it settles the whole clock's decode in
one combinational cone, and at 8 MHz it has 125 ns in which to do it.  A ~43 ns
settle is comfortable there and impossible on a 31.25 ns fabric clock.

⚠ **AND THE COORDINATOR'S EARLIER CLAIM THAT FABRIC-CLOCK ITERATION IS "WHAT
THE DIE ACTUALLY DOES" IS FALSE AND IS NOT REPEATED HERE.**  `ce_half` and
every split tried so far are FPGA-side pipelining.

---

## §2 DELIVERABLE A — THE REACHABLE CHAIN GRAPH, TWO WAYS.  **F-1 IS MET**

### 2.1 STATIC, from the source (`sw/chainflat_graph.py`)

The tool enumerates the paths through all 33 arms of `v30u_eu_step.svh` with
its includes spliced, and reports per path whether it falls through **without
`stop`**, under what source-level condition, and to which state.  It performs
**five declared symbolic reductions and no others** (R1 `st_n` tracking, R2
repeated-condition reuse, R3 prune subtrees touching neither `st_n` nor `stop`,
R4 `chain == 4'd0` decided true, R5 `stop` decided from the tracked value); a
path it cannot decide is REPORTED, never dropped.

**THE CONTROLS, REPORTED FIRST** (`static_controls.txt`):

| control | verdict |
|---|---|
| **PC-A1** 33 arms + `default`; **24** carry `if (chain == 4'd0)`, **9** do not; the 9 open names are EXACTLY the 9 `st_zero_ok()` returns true for, parsed separately out of `v30u_eu.sv` | **PASS** |
| **PC-A2** the FALL-THROUGH TARGETS the path enumeration produces == that same 9 — a THIRD derivation, from control flow, of a set the source states twice | **PASS** |
| **PC-A3 NON-VACUITY** — one `stop = 1'b1;` deleted from `S_PFX_CHG` in a scratch copy: PC-A2 must FAIL and the target set must GROW | **PASS** — PC-A2 fails and `S_OPC_POP` joins the target set |

**THE GRAPH** (`static_graph.txt`): **24 fall-through edges**, and **it is a
DAG — no cycles**, checked.  Because it is a DAG, **one clock edge's walk
visits each state AT MOST ONCE.**  That single property is what the rest of
this study rests on.

The sub-graph among the nine is three short spines:

```
   S_TAKE_OPC -> S_DECODE -> S_DECODE2                       (then stop)
   S_EA_CALC  -> S_BIND    -> S_ENTER                        (then stop)
   S_TAIL / S_TAIL_POP -> S_INSTR_END -> S_TAKE_OPC -> ...
```

**STATIC MAXIMUM OCCUPANCY: 6 positions**, and the longest walks are exactly
three: `S_ROW`, `S_EPOP` or `S_TAIL_W` at position 0, then
`… -> S_INSTR_END -> S_TAKE_OPC -> S_DECODE -> S_DECODE2`.  **75 distinct
maximal sequences** in total (28 of depth 1, 17 · 12 · 8 · 7 · 3 at depths
2 – 6).

### 2.2 DYNAMIC, from the silicon-scoring simulator (`sw/chainflat_probe.py`)

The `CHAIN_PROBE` extension records the ORDERED tuple of states occupying
positions 0..N−1 of **one CE edge**, de-duplicated in a linear-probed table and
counted.  Two populations with nothing in common:

* **golden** — `tests/v30/v0.1` through `check_core --core ucore --opcodes all
  --cases 0`, which scored **169,000 / 169,000** on the probe build:
  **8,181,529 CE edges**, 41 distinct sequences;
* **lfsr** — `hdl/tb/tb_chain_lfsr.sv`, 4 seeds × 400,000 clocks of arbitrary
  bytes: **266,292 CE edges**, 43 distinct sequences.

**8,447,821 CE edges censused, 46 distinct sequences, 0 table overflows.**

| control | verdict |
|---|---|
| **PC-B1** the states seen at position ≥ 1 == `st_zero_ok`'s nine, and nothing else | **PASS** (it is `ucore_provenance.md` §51.2's census, re-measured) |
| **PC-B2 = F-1** every observed sequence is a walk of the STATIC adjacency, edge for edge | **PASS** |
| **PC-B3 NON-VACUITY** dropping ONE static edge the census walks must make PC-B2 FAIL | **PASS** |
| **PC-B4** observed depth ≤ static depth | **PASS** — **6 and 6** |

> ### **F-1 IS MET.  THE TWO GRAPHS AGREE ON WHICH STATES CHAIN AND TO WHAT DEPTH, AND THE COMPARISON WAS DEMONSTRATED TO BE ABLE TO SAY NO.**

**One asymmetry, reported and not a disagreement:** the static graph admits
**75** maximal sequences and only **46** were observed.  A static graph is an
over-approximation by construction — it cannot know that `S_1BL_CHG` is only
reached with `opc_valid_n` low, for instance — so *static ⊇ dynamic* is the
correct relation and *dynamic ⊄ static* would have been the finding.  The
29 unobserved are listed in `static_graph.txt`.

---

## §3 DELIVERABLE B — THE SEQUENCE CENSUS

`sw/testdata/chainflat/dyncensus.txt`.  **The distribution, not a summary:**

| depth | distinct sequences | CE edges | share |
|---:|---:|---:|---:|
| **1** | 21 | 5,827,366 | **68.98 %** |
| 2 | 8 | 129,516 | 1.53 % |
| **3** | 6 | 1,325,827 | **15.69 %** |
| 4 | 4 | 2,772 | 0.03 % |
| 5 | 4 | 6,651 | 0.08 % |
| **6** | 3 | 1,155,689 | **13.68 %** |

The head of the census, which is where the mass is:

| CE edges | share | depth | sequence |
|---:|---:|---:|---|
| 2,571,711 | 30.44 % | 1 | `S_ROW` |
| 1,193,888 | 14.13 % | 1 | `S_RLOOP` |
| 1,078,534 | 12.77 % | 3 | `S_NORM_CHG -> S_BIND -> S_ENTER` |
| 1,074,568 | 12.72 % | **6** | `S_ROW -> S_TAIL -> S_INSTR_END -> S_TAKE_OPC -> S_DECODE -> S_DECODE2` |
| 599,727 | 7.10 % | 1 | `S_OPC_POP` |
| 555,209 | 6.57 % | 1 | `S_PRERD` |
| 463,736 | 5.49 % | 1 | `S_EPOP` |
| 160,551 | 1.90 % | 3 | `S_OPC_POP -> S_DECODE -> S_DECODE2` |

**FLATTENING IS TRACTABLE, AND THE CENSUS IS WHY: 46 sequences, three of them
at the maximum depth, and they share one tail.**  All three depth-6 walks end
in `S_INSTR_END -> S_TAKE_OPC -> S_DECODE -> S_DECODE2` and differ only in
their first one or two positions.

⚠ **AND THE NUMBER THAT MATTERS MOST TO THE QUESTION IS 68.98 %.**  On more
than two thirds of all CE edges **the chain does not chain at all** — one
position, one arm, `stop`.  **Seven guarded copies of a 33-arm `case` are paid
combinationally on every one of those edges.**

---

## §4 DELIVERABLE C — WHAT THE COMPOSED FUNCTION TOUCHES

`sw/chainflat_compose.py`; `compose.txt` / `compose.json`.

⚠ **THE READ/WRITE SETS ARE OVER-APPROXIMATIONS AND THE TWO ANSWERS THEY
SUPPORT POINT IN OPPOSITE DIRECTIONS, WHICH IS WHY THEY ARE LABELLED
SEPARATELY.**  An over-approximated WRITE set makes an INVARIANCE claim
*conservative* — a name in no write set is invariant for certain.  An
over-approximated READ set makes a carried-dependency depth an **UPPER BOUND** —
a flattened form can be no deeper and may be shallower.

**THE CONTROLS** (`compose_controls.txt`):

| control | verdict |
|---|---|
| **PC-C2** the register file (`gpr` / `sreg`) is written by **NO** chainable arm; the negative control `zzz_no_such_signal` is found nowhere | **PASS** |
| **PC-C3 NON-VACUITY** inject `gpr_n[0] = 0` into `S_EA_CALC`'s text and PC-C2 must flip | **PASS** |
| PC-C1 (reported, not a bar) every position-0-only arm writes something no chainable arm writes | 3 arms do not (`S_PFX_CHG`, `S_EXT_POP`, `S_1BL_LEAD`) — they legitimately write only shared names |

### 4.1 **THE REGISTER FILE IS READ AT EXACTLY ONE POSITION AND WRITTEN AT NONE — IN EVERY OBSERVED SEQUENCE**

WAVE 5 §4.1 measured *"one `case (st_n)` decoder plus one register-file read per
position, and it repeats once per position"*, with a distinct `Ram<N>` in every
folded segment on every draw, and named the cause: **`S_EA_CALC` is one of the
nine and its body opens with an eight-way read of `gpr_n`.**

This wave measures, from the source and against the census, that **at most one
of those reads can ever matter**:

* **no chainable arm writes `gpr` or `sreg`** (PC-C2, with its non-vacuity);
* in **every one of the 25 observed sequences of depth ≥ 2**, the register file
  is read at **exactly one position** and written at **none** —
  `regfile_constant_for_every_reader: True`, 6 sequences reach it, all at
  position 1.

**The other five copies of the register-file read compute a value that is
identical to the first by construction, and the netlist still contains them.**
That is the single clearest measurement in this wave that the multiplicity of
the unroll has no counterpart in the function it computes.

### 4.2 THE IRREDUCIBLE SERIAL DEPTH — **THE FLOOR**

For each sequence, the longest chain of read-after-write dependencies between
positions.  This is what a flattened form **cannot** beat.

| depth | serial depth (upper bound) | CE edges |
|---:|---:|---:|
| 2 | 1 | 71,732 |
| 2 | 2 | 57,784 |
| 3 | **2** | 1,097,667 |
| 3 | 3 | 228,160 |
| 4 | 3 | 788 |
| 4 | 4 | 1,984 |
| 5 | 3 | 73 |
| 5 | 4 | 6,578 |
| **6** | **4** | **1,154,455** |
| 6 | 5 | 1,234 |

**THE FLOOR IS 4 OF 6 ON THE DEEP MASS AND 2 OF 3 ON THE SHALLOW MASS**, and
the campaign-wide maximum over every observed sequence is **5**.

* The dominant depth-6 walk
  `S_ROW -> S_TAIL -> S_INSTR_END -> S_TAKE_OPC -> S_DECODE -> S_DECODE2`
  (1,074,568 edges) has **serial depth 4**: two of its six positions are
  **not** serially dependent on their predecessor and could be evaluated in
  parallel by a composition.
* The dominant depth-3 walk `S_NORM_CHG -> S_BIND -> S_ENTER`
  (1,078,534 edges) has **serial depth 2**: `S_NORM_CHG` writes only `st_n`, so
  position 0 carries **no data at all** into position 1.

**THE NAMES THAT CARRY** (an under-approximation is what a floor needs, so the
carriers are named rather than only counted).  On the dominant depth-6 walk:

```
  0 -> 1  opc_valid_n  pend_active_n        1 -> ...  (nothing)
  0 -> 2  poste_n                           2 -> 4    pfxcnt_n
  0 -> 3  opc_byte_n  pc_n                  3 -> 4    ld_b_n
  0 -> 5  irq_shadow_n  psw_n               4 -> 5    ld_ext_n  pv  rep_kind_n
```

Read down the diagonal, the genuinely serial spine is
**`opc_byte_n` → `ld_b_n` → `pv` → the decode**: position 3 (`S_TAKE_OPC`)
copies the pre-popped opcode into `ld_b_n`, position 4 (`S_DECODE`) reads it to
index the PLA, position 5 (`S_DECODE2`) reads the PLA result.  **That is three
stages and it is real.**  Everything upstream of it — positions 0 – 2 — feeds
it only through `opc_byte_n`, which is a REGISTER written at position 0 and
read at position 3.

### 4.3 THE FOLD OPPORTUNITIES, MEASURED

* **12 CHAIN-INVARIANT INPUTS** — read inside the chain and written by no arm
  that can occupy a non-final position, so every unrolled copy recomputes an
  identical value: `bnd_take`, `brk_arm`, `brk_seen`, `brk_smp_n`,
  `irq_nmi_lvl`, `irq_take`, `ld_byte_n`, `ld_pla_n`, `q_byte`, `q_ripe`,
  `q_ripe_lead_n`, `retire_ok_n`.
* **DEAD WRITES DOWN ONE CHAIN.**  On the dominant depth-6 walk, **14
  registers** written at position 0 (`S_ROW`) are overwritten at position 2
  (`S_INSTR_END`) **without being read in between** — `al_adjust_n`,
  `al_bitarm_n`, `al_eaconst_n`, `al_op_n`, `al_spent_n`, `al_tmp_n`,
  `bus_word_n`, `opr_fresh_n`, `opr_loaded_n`, `pop_is_first_n`, `rep_chain_n`,
  `row_paired_n`, `row_posted_n`, `rowq_n` — plus five more dead 2 → 4
  (`ld_ext_n`, `lock_pfx_n`, `rep_kind_n`, `seg_override_n`, `seg_ovr_n`) and
  two dead 2 → 5.  **Only the last write survives the edge.**
* **26 registers are written at more than one position** on that walk.

**THE HEART OF DELIVERABLE C, IN ONE SENTENCE:** *the composition has a real
serial spine of 4 stages out of 6, and everything else in the unroll — five
sixths of the register-file reads, twelve invariant recomputations, and
twenty-one dead writes per deep edge — is multiplicity the function does not
have.*

---

## §5 DELIVERABLE D — THE SYNTHESIS EXPERIMENT, IN ISOLATION

### 5.1 WHAT WAS BUILT

Two **standalone** projects — `v30u_eu` as its own top with virtual pins, which
is `ucore_provenance.md` §51.1's harness — same device `5CSEBA6U23I7`, same
`HIGH PERFORMANCE EFFORT`, **no `set_multicycle_path`** (USER RULING
2026-09-08), `create_clock -period 31.250 [get_ports clk]`, MAP ONCE PER
PROJECT and FIT ONCE PER SEED over 3 seeds.  **Neither is the design and
neither is proposed for `hdl/rtl/ucore/`.**

* **REF** — a byte-identical copy of `hdl/rtl/ucore/`, verified by `diff -r`.
* **FLAT** — the same tree with ONE substitution, generated mechanically by
  `sw/chainflat_proto.py`: the `for (chain = 0; chain < CHAIN_MAX; ...)` loop —
  **seven full copies of the 33-arm `case`** — replaced by *position 0's 33-arm
  case ONCE, then the nine chainable arms ONCE EACH in topological order, each
  guarded by `st_n == S_X`*.  The arms are carved out of `v30u_eu_step.svh`
  **verbatim, comments and all**; the body is relocated, never rewritten.

The topological order the generator derived and used:

```
  S_TAIL_POP  S_TAIL  S_INSTR_END  S_TAKE_OPC  S_EA_CALC
  S_DECODE    S_DECODE2  S_BIND  S_ENTER
```

### 5.2 **P-2 — THE EQUIVALENCE GATE.  MET.**

The substitution is exact only if a walk visits each state at most once, which
is A(i)'s DAG result.  **That is an argument; this is the gate:**

| | REF | FLAT |
|---|---|---|
| `check_core --core ucore --opcodes all --cases 0` | **169,000 / 169,000** | **169,000 / 169,000** |
| `tb_chain_lfsr` signature, seed 1 | `1d01c9b269ffaa94` | `1d01c9b269ffaa94` |
| seed 2 | `b39b040a98b28e5d` | `b39b040a98b28e5d` |
| seed 3 | `0997b773cd99c030` | `0997b773cd99c030` |
| seed 4 | `d05b6c3c3d9fbe78` | `d05b6c3c3d9fbe78` |
| `CHAIN_DEPTH_MAX` | 6 · 6 · 6 · 6 | 6 · 6 · 6 · 6 |

**BYTE-IDENTICAL ON ALL FOUR SEEDS AND 169,000 / 169,000 ON BOTH.  THE
FLATTENED FORM COMPUTES THE SAME FUNCTION.**

### 5.3 **P-1 — THE POSITIVE CONTROL.  REPORTED FIRST, AND IT MISSED.**

**THE STA'S OWN CONTROLS PASS ON ALL SIX DRAWS OF BOTH ARMS** — PC-1 (a
`get_pins` `-through` returns 1 path where the `get_nodes` collection of the
SAME node returns 0), PC-2 (the walker reproduces Quartus's `-data_delay` to
**0.000 ns**), PC-3 (a path forced through one NAMED `st_n` pin reports ≥ 1
boundary; the same path under a marker name that does not exist reports 0).

| P-1 clause | seed 1 | 2 | 3 | 4 | 5 | 6 | verdict |
|---|---|---|---|---|---|---|---|
| **(a)** ≥ 2 chain boundaries on the worst arc | 3 | 4 | 4 | 3 | 4 | 4 | **MET** |
| **(b)** segment 0 the largest single segment | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | **MET** |
| **(c)** `st_n` ≥ 20 | 129 | 131 | 129 | 129 | 129 | 129 | met |
| **(c)** `rst_ctr_n` ≤ 1 | 0 | 0 | 0 | 0 | 0 | 0 | met |
| **(c)** `ld_dlo_n` ≤ 1 | 0 | 0 | 0 | 0 | 0 | 0 | met |
| **(c)** `ld_ripe_prev_n` ≤ 1 | **3** | **3** | **3** | **3** | **3** | **3** | **MISSED** |
| **(c)** `zzz_no_such_signal` == 0 | 0 | 0 | 0 | 0 | 0 | 0 | met |

> ## ⚠ **P-1(c) IS MISSED ON ALL SIX DRAWS, SO P-1 IS MISSED, AND BY THE PRE-REGISTRATION THAT VOIDS DELIVERABLE D ON THE STRENGTH OF THE ORIGINAL BAR.  THE BAR IS NOT WIDENED.**

**P-1d, WHICH IS THE PART THE BRIEF ACTUALLY NAMED, REPRODUCES ALMOST EXACTLY.**
Per-folded-position delay over all 22 folded segments on the six REF draws:
**min 1.318 · max 9.350 · mean 5.384 ns**, against WAVE 5's **in-situ mean
5.359 ns** (band 2.993 – 7.945) — **a difference of 0.025 ns.**  The registered
band was [2.0, 9.0] on the mean and **it is MET**.

**THE ERRATUM AND ITS REPLACEMENT ARE `docs/notes/chainflat_amendment_A1_
2026-09-09.md` (`a734dd3d79`), COMMITTED BEFORE THE SEED 4/5/6 FITS EXISTED.**
The mechanism: in the design `q_ripe` comes out of `v30u_biu` and the cone that
computes `ld_ripe_prev_n = q_ripe` folds into its driver; **in this harness
`v30u_eu` is its own top and `q_ripe` is a VIRTUAL INPUT PIN**, so
`ld_ripe_prev_n` is a next-state signal on a pin with nothing to fold into and
Quartus keeps and duplicates it.  It reads **3 on FLAT as well as on REF, on all
six draws** — a harness artefact, not a chain property.  **An absolute count was
the wrong shape for a claim that is about DISCRIMINATION.**

**THE REPLACEMENT, SCORED ONLY ON SEEDS 4/5/6 — THE DRAWS THAT DID NOT SELECT
IT** (`ucore_provenance.md` §64.1):

| bar | seed 4 | seed 5 | seed 6 | verdict |
|---|---|---|---|---|
| **P-1′(c)** `min(st_n, ld_b_n, pv, opc_base) ≥ 10 × max(rst_ctr_n, ld_dlo_n, ld_ripe_prev_n, nmi_latch_n, rloop_n_n)`, and `zzz_no_such_signal == 0` | 58 ≥ 30, zzz 0 | 58 ≥ 30, zzz 0 | 58 ≥ 30, zzz 0 | **MET** |
| **P-1″** every CHAINABLE base name has FEWER cones on FLAT, and NO FRONT-END name has fewer | ✓ | ✓ | ✓ | **MET** |

⚠ **The factor 10 is declared as partly post-hoc** (§2 of the amendment): it is
an order of magnitude chosen for the mechanism, written after seeing seeds 1 – 3
where the same expression reads ≈ 19, and it is therefore scored **only** on
4 – 6.

**P-1″ IS THE MEASUREMENT THAT MAKES THE COMPARISON READABLE, AND IT CARRIES NO
THRESHOLD AT ALL** — the fold is visible name by name, and it is SPECIFIC:

| base name | class | REF | FLAT |
|---|---|---:|---:|
| `st_n` | CHAINABLE | 129 | **47** |
| `pv` | CHAINABLE | 87 | **21** |
| `opc_base` | CHAINABLE | 75 – 77 | **16** |
| `ld_b_n` | CHAINABLE | 58 | **12** |
| `m_kind` | CHAINABLE | 26 | **8** |
| `stop` | CHAINABLE | 19 | **9** |
| `st_zero_ok` | CHAINABLE | 13 | **0** |
| `seg_override_n` | CHAINABLE | 13 | **3** |
| `sigma` | FRONT-END | 121 | **122** |
| `s1_val` | FRONT-END | 56 | **56** |
| `it_val` | FRONT-END | 9 | **9** |
| `zzz_no_such_signal` | NEGATIVE CONTROL | 0 | **0** |

**Every chainable name falls 2.1 – 4.8× and not one front-end name moves.  The
substitution removed the chain's copies and nothing else.**

### 5.4 THE COMPARISON — **MEASURED**

**MAP ONCE PER PROJECT, FIT ONCE PER SEED, six seeds each** (1 – 3 registered,
4 – 6 added by amendment A-1 with `--skip-map`, so all six are draws of one
map).  `map_errors 0` on both; the `$readmemh` check is **POSITIVE** on both —
the `ucrom.hex(1)` truncation warning is present, which is what proves the ROM
LOADED (F44: a wrong `HEXDIR` yields an all-zero ROM and a compile that
succeeds).

#### AREA (Analysis & Synthesis, one map per project)

| | ALMs (est.) | **combinational ALUTs** | dedicated logic registers |
|---|---:|---:|---:|
| **REF** (7 copies) | 7,098 | **10,052** | 807 |
| **FLAT** (1 copy per arm) | 5,255 | **7,104** | 807 |
| **delta** | **−1,843 (−26.0 %)** | **−2,948 (−29.3 %)** | **0** |

Fitted ALMs, per seed: REF **7,328 · 7,372 · 7,319 · 7,342 · 7,358 · 7,328**;
FLAT **5,399 · 5,416 · 5,407 · 5,383 · 5,404 · 5,412**.

> **P-4a asked for a fall of ≥ 25 % in combinational ALUTs.  MEASURED −29.3 %.
> P-4a IS MET — and the register count did not move by one flop, which is what
> a pure re-association of combinational logic should do.**

#### DELAY — the worst reg → reg arc, no exception, 31.250 ns period

| draw | REF slack | REF data ns | REF cells | REF bnds | | FLAT slack | FLAT data ns | FLAT cells | FLAT bnds |
|---|---:|---:|---:|---:|---|---:|---:|---:|---:|
| seed 1 | −14.912 | **44.562** | 51 | 3 | | −3.528 | **33.498** | 36 | 1 |
| seed 2 | −12.606 | **42.163** | 46 | 4 | | −4.356 | **34.999** | 37 | 1 |
| seed 3 | −14.367 | **45.182** | 51 | 4 | | −3.923 | **35.118** | 42 | 2 |
| seed 4 ⧉ | −13.969 | 43.503 | 43 | 3 | | −5.047 | 34.963 | 38 | 1 |
| seed 5 ⧉ | −13.315 | 43.956 | 45 | 4 | | −4.400 | 34.889 | 42 | 2 |
| seed 6 ⧉ | −13.989 | 44.618 | 50 | 4 | | −4.080 | 34.624 | 45 | **0** |

⧉ seeds 4 – 6 are amendment A-1's draws.  **P-4a and P-4b are SCORED ON SEEDS
1 – 3, where they were registered**; 4 – 6 are reported beside them and are not
used to re-score them.

| | REF | FLAT | delta |
|---|---:|---:|---:|
| **mean worst-arc data delay, seeds 1 – 3 (the registered scoring)** | **43.969** | **34.538** | **−9.431 ns (−21.4 %)** |
| mean, all six draws | 43.997 | 34.682 | −9.315 ns (−21.2 %) |
| range | 42.163 – 45.182 | 33.498 – 35.118 | |
| worst-arc logic levels | 43 – 51 cells | 36 – 45 cells | |
| chain boundaries on the binding arc | 3 – 4 | **0 – 2** | |

> ## **P-4b IS REFUTED, AND IT IS REFUTED IN THE STUDY'S FAVOUR.**
> It registered *"FLAT's worst arc within ±15 % of REF's"*, on the reasoning
> that deliverable C measures the serial spine to be unchanged.  **MEASURED
> −21.4 %.**  The ranges do not overlap: the SLOWEST flat draw (35.118) is
> **7.045 ns faster than the FASTEST reference draw** (42.163).

**AND THE STRUCTURAL READING, WHICH IS THE PART THAT IS NOT A NUMBER:** the
binding arc's chain-boundary count falls from **3 – 4 to 0 – 2**, and on FLAT
seed 6 **the worst arc crosses NO chain boundary at all** — one 34.212 ns
segment.  **After the fold the chain is no longer the binding structure.  The
front end is** — which is exactly where WAVE 5 §9.2 pointed and where no wave
has yet measured a change.

### 5.5 WHY THE FLATTENED FORM IS FASTER, AND WHY IT IS NOT FASTER STILL

The serial spine deliverable C measured did NOT go away and the measurement
says so: FLAT still crosses 1 – 2 chain boundaries on 5 of 6 draws and its
segment 0 is 19.5 – 22.3 ns, essentially REF's.  **What went away is the
multiplicity:**

* **one `case (st_n)` decoder per position became one `st_n == S_X` compare per
  arm** — the `st_n` cone count falls 129 → 47;
* **six register-file reads became one** — `S_EA_CALC`'s eight-way `gpr_n` read
  exists once, and §4.1 measured that at most one could ever have mattered;
* **the twelve chain-invariant inputs are computed once**, and the twenty-one
  dead writes per deep edge have one destination instead of several.

The residue is the genuinely serial part: on the dominant depth-6 walk,
`opc_byte_n → ld_b_n → pv → the decode`.  FLAT seed 1's segment 1 reads
`always6 · ld_b_n · ld_b_n · Ram11 · Ram11 · Decoder27 · pv · ld_pla_n ·
always6` — **that is the spine, once, and it is 13.424 ns.**

---

## §6 DELIVERABLE E — THE VERDICT

### 6.1 **ARTIFACT OR DESCRIPTION?  ARTIFACT — ON FOUR INDEPENDENT MEASUREMENTS**

The 33-state DECOMPOSITION is a description: its clock boundaries are
`biu.charge(n)` calls with measured cycle counts behind them (§1).  **The
SEVENFOLD UNROLL is not.**

1. **THE SPEC.**  The nine states that can occupy a position ≥ 1 are exactly the
   C++ statement positions with **no `charge()` between them and their
   predecessor** — program-counter positions of a straight-line function, which
   an RTL state machine has to re-serialise and a die does not (§1).
2. **THE GRAPH IS A DAG.**  A walk visits each state **at most once** (§2.1,
   checked).  Seven copies exist to host at most six distinct states, each
   occurring once.  **The multiplicity has no counterpart in the function.**
3. **THE REGISTER FILE.**  In **every one of the 25 observed sequences of depth
   ≥ 2** it is read at exactly ONE position and written at NONE (§4.1).  WAVE 5
   measured a distinct `Ram<N>` in every folded segment on every draw; **at most
   one of those reads can ever matter.**
4. **69 % OF CE EDGES DO NOT CHAIN AT ALL** (§3) — one position, one arm,
   `stop` — and seven guarded copies are paid combinationally on every one of
   them.

And then the direct test: **removing the multiplicity — one copy per arm in
topological order instead of seven copies of everything — leaves the function
BYTE-IDENTICAL** (169,000/169,000; four identical LFSR signatures) **and takes
29.3 % of the combinational area and 21.4 % of the arc with it.**  A
description does not have 29 % of itself removable with no behavioural change.

### 6.2 **WOULD FLATTENING FIND NANOSECONDS?  YES — ABOUT 9.3, IN ISOLATION**

**MEASURED, and the sign was not registered in this direction:** the
pre-registration's P-4b said the arc would move by **less than ±15 %**, on the
reasoning that the serial spine is unchanged.  **It moved −21.4 %.**  That
reasoning was right about the spine and wrong about what dominates: what the
unroll costs is not the spine, it is **six copies of a 33-way decoder and six
copies of a register-file read**, and those are what the fold deletes.

**THE ESTIMATE, WITH ITS UNCERTAINTY:**

* **central value −9.431 ns** (registered seeds 1 – 3), **−9.315 ns** over all
  six draws;
* **draw-to-draw spread**: REF 42.163 – 45.182 (3.019 ns), FLAT 33.498 – 35.118
  (1.620 ns).  **The two ranges are disjoint by 7.045 ns**, which is the honest
  statement of separation on 3 + 3 registered draws (6 + 6 in total);
* **it is a DIFFERENCE between two builds compiled identically**, which is what
  the experiment was for, and the front end is byte-identical between them.

### 6.3 ⚠ **F-4 — WHAT THIS FIGURE IS NOT**

> **A STANDALONE-PROTOTYPE FIGURE IS NOT A PREDICTION FOR THE CORE.**

* WAVE 5 measured out-of-context estimates mispredicting a **realised**
  downstream half by **+11.3 to +20.0 ns**, and the loop by **+15.30 ns**, and
  said so before this wave existed.
* This harness has **no BIU and no `system_large`**.  WAVE 5 §7 measured the BIU
  round trip on the binding arc of **2 of 4** design draws, worth 2.70 – 2.89 ns,
  and it is in the front end — which this experiment does not touch.
* Six draws are **not a distribution**.  `standing_gates.md` §A governs: the
  same tree has drawn 19.42 and 45.91 MHz.
* **The comparison is a DIFFERENCE, and the difference is the defensible part.**
  The absolute 34.7 ns is not a design number and must not be quoted as one.

**AND THE ARITHMETIC THAT MATTERS TO THE CAMPAIGN, DONE OUT LOUD AND LABELLED
AS ARITHMETIC:** the design's arc is **43.485 ns** (WAVE 5) and this harness's
REF arc is **43.997 ns** — close enough that the harness is clearly measuring
the same structure.  Carrying **−9.3 ns** onto it lands at **≈ 34.2 ns**
against a requirement of **29.6**.  ⚠ **THAT IS STILL 4.6 ns OVER**, and it is
an *upper bound on the benefit*, not a lower one, because every realised change
this campaign has measured cost more than its estimate.  Independently, WAVE 5
measured the **free-deletion floor at 29.490 ns mean, over the requirement on 2
of 4 draws** — so **no chain change, flattening included, reaches 29.6 by
itself.**  What flattening recovers is about **47 % of the 19.766 ns the folded
chain costs**, which is the largest single recovery any wave in this campaign
has measured, and it is not enough on its own.

### 6.4 THE SENTENCE

> **The seven-copy unroll is an artifact of transliterating a straight-line C++
> function into a state machine, not a description of the die's decoder: the
> chain graph is a DAG over nine states, a clock's walk visits each at most
> once, 69 % of clocks walk only one, and the register file — read once per
> copy in the netlist — is read at exactly one position and written at none in
> every sequence that occurs.  Flattening it to one copy per arm is
> behaviourally byte-identical and measures, in isolation, −29.3 % of the
> combinational area and −9.4 ns of a 44 ns arc, which is the largest single
> recovery this campaign has measured.  It is still not enough: carried onto
> the design it lands near 34 ns against a 29.6 ns requirement, and WAVE 5
> already measured that deleting the whole folded chain for free leaves 29.5.
> The remaining gap is in the front end, and no wave has yet measured a change
> to it.**

### 6.5 WHAT THIS WAVE DOES **NOT** SAY

1. **IT PROPOSES NO DESIGN AND LANDS NOTHING.**  `hdl/rtl/ucore/` carries only
   the sim-only `CHAIN_PROBE` extension.  The FLAT tree is a scratch artifact
   and the core does not reference it.
2. **IT DOES NOT SAY THE −9.4 ns WOULD BE REALISED IN THE DESIGN.**  §6.3.
3. **IT DOES NOT SAY THE FLAT FORM IS CORRECT ENOUGH TO LAND.**  It is scored
   on the golden suite and the LFSR harness; it has had no `ulockstep`, no
   `tb_sys`, no S16 walk, no `ss_lint`, no `r7_lint`, no fabric.
4. **IT MEASURES NOTHING ABOUT `CHAIN_MAX`.**  The bound is untouched.
5. **IT SAYS NOTHING ABOUT AREA IN THE DESIGN.**  A standalone `v30u_eu` is not
   `system_large`.

---

## §7 F-1 … F-5, SCORED

| bar | verdict |
|---|---|
| **F-1** the static and dynamic graphs agree on which states chain and to what depth | **MET.**  PC-B2 PASS over **8,447,821 CE edges** and 46 distinct sequences from two populations with nothing in common: **every observed sequence is a walk of the static adjacency, edge for edge**, the states at position ≥ 1 are exactly `st_zero_ok`'s nine on both sides, and the depths agree at **6 and 6**.  **NON-VACUOUS**: dropping ONE static edge the census walks makes the comparison FAIL.  The static graph admits 75 maximal sequences to the dynamic's 46, which is the correct relation (*static ⊇ dynamic*) and is reported.  §2 |
| **F-2** the synthesis experiment's positive control reproduces WAVE 5 | ⚠ **SPLIT, AND THE SPLIT IS REPORTED AS A MISS.**  The BRIEF's three properties all reproduce: *position 0 fat* — segment 0 is the largest single segment on **6 of 6** draws; *~5.36 ns per folded position* — measured **5.384 ns** mean over 22 folded segments against WAVE 5's in-situ **5.359**, a difference of **0.025 ns**; *copies independent* — `st_n` 129 cones against 0/0/3 for the position-0-only names and **0** for the negative control, and the fold is visible name by name between the two builds (P-1″).  **BUT the pre-registration's own numeric sub-clause P-1(c) — `ld_ripe_prev_n` ≤ 1 — MEASURED 3 ON ALL SIX DRAWS AND IS MISSED.**  The bar is NOT widened.  Amendment **A-1**, committed before the seed 4/5/6 fits existed, states the erratum (the harness makes `q_ripe` a virtual input pin), registers a mechanism-shaped replacement, and scores it **only on the three draws that did not select it**: **P-1′(c) MET, P-1″ MET on seeds 4, 5, 6.**  §5.3 |
| **F-3** `hdl/rtl/ucore/` untouched except the permitted `ifdef CHAIN_PROBE` extension; `git status --porcelain hdl/` shows no other tracked modification at start and end | **MET.**  `git diff d45de50a28^ HEAD -- hdl/` is **one file, +115 lines, 0 deletions**, entirely inside `` `ifdef CHAIN_PROBE ``.  **PROVED POSITIVELY, not asserted**: `verilator -E` on the file before and after, blank lines removed, is **IDENTICAL at 4,226 lines** (`probe_invisible.txt`), and the same comparison **with** `-DCHAIN_PROBE` shows **+95 lines** — non-vacuous both ways.  `git status --porcelain hdl/` carries **0 tracked modifications** at the start and at the end (twelve pre-existing untracked `hdl/quartus_gate_*.log` files, not this wave's, never `git add`ed).  **`git add -A hdl/` was never used.**  The synthesis driver never opens `hdl/nec_test.qsf`, `hdl/nec_test_ucore.qsf` or `hdl/nec_test.sdc`, so WAVE 5's `git checkout --` dance has nothing to restore here — and it checks that by refusing on a tracked-dirty `hdl/` and re-checking at the end (`hdl/ at end: CLEAN`, both runs).  **Nothing is landed in the core.** |
| **F-4** every estimate carries its uncertainty and its out-of-context caveat | **MET.**  §6.2 gives the central value with the per-arm ranges and their 7.045 ns separation; §6.3 states, in the pre-registration's own words, that **a standalone-prototype figure is NOT a prediction for the core**, with WAVE 5's measured **+11.3 … +20.0 ns** and **+15.30 ns** mispredictions quoted beside it, the missing BIU named, and the six draws declared not to be a distribution |
| **F-5** the verdict is stated plainly either way, and a NO is reported as the result it is | **MET.**  §6.4.  The answer came out **YES on "is it an artifact"** and **YES on "does flattening find nanoseconds"**, and **NO on the only question that would have closed the campaign's gap** — and the NO is stated first, in §0, with the arithmetic done out loud |

### 7.1 THE REGISTERED BARS OF §3.2, SCORED

| bar | verdict |
|---|---|
| **P-1** the positive control | ⚠ **MISSED on (c).**  (a) MET 6/6, (b) MET 6/6, (c) missed on `ld_ripe_prev_n` 6/6.  **P-1d MET** (mean 5.384 in [2.0, 9.0]) |
| **P-1′(c) / P-1″** (amendment A-1) | **MET on seeds 4, 5, 6** — the draws that did not select them |
| **P-2** the equivalence gate | **MET.**  169,000/169,000 on both arms; four LFSR signatures byte-identical; `CHAIN_DEPTH_MAX` 6 on both |
| **P-3** the measurement | **MET.**  Map once per project, fit once per seed, 3 + 3 seeds; `map_errors` 0 on both; the `$readmemh` check **POSITIVE** on both |
| **P-4a** comb ALUTs fall ≥ 25 % | **MET.**  **−29.3 %** (10,052 → 7,104), registers unmoved at 807 |
| **P-4b** the arc within ±15 % | ⚠ **REFUTED, IN THE STUDY'S FAVOUR.**  **−21.4 %** on the registered seeds |
| **P-5** the out-of-context caveat | **MET.**  §6.3 |
| **P-6** the verdict stated plainly | **MET.**  §6.4 |
| **P-7** discipline | **MET.**  See F-3 |

---

## §8 THE STANDING LADDER, RE-SCORED ON THE PROBE EDIT

Every one of these was run **after** the `CHAIN_PROBE` extension landed in
`hdl/rtl/ucore/v30u_eu.sv`.

| gate | result |
|---|---|
| `check_core --core ucore --opcodes all --cases 0` | **169,000 / 169,000** |
| `ulockstep --golden all --cases 50` | **17,350 / 17,350**, ALL CASES LOCKSTEP |
| `chain_lfsr_gate` | **PASS** — `CHAIN_MAX` 7, observed depth **6**, **0** overflows, 4 seeds × 400,000 clocks, `CE_COINCIDE` 0 |
| `check_boot --core ucore` and `--timed 220` | **MATCH over 220 rows** on both |
| `r7_lint` | **PASS** — 0 undeclared carriers / 0 undeclared unresolved / 0 `stop` sites |
| `ss_lint --core ucore` | **PASS** — 228 architectural flops, 0 UNMAPPED — **and IDENTICAL to the pre-edit file measured the same way** (the probe adds no architectural flop) |
| `test_artifact` | **45 / 45** |
| `demux_off_gate` | **PASS** |
| `ucrom_mif_check` | **PASS** |

---

## §9 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**  No
  Codex.  No nested subagent.
* Single-writer guard by EXACT binary name before every Quartus stage; the
  driver refuses on a tracked-dirty `hdl/` and re-checks at the end.
* The probe binaries are built into `~/.cache/ucsimt-tmp/chainflat/` and the
  artifact layer is **never asked to promote one** — `-DCHAIN_PROBE` is not in
  `check_core.recipe()`, so a probe build in `hdl/tb/obj_dir_ucore/` would carry
  a receipt naming bytes it does not come from.
* `~/.cache/ucsimt-tmp/` for every intermediate; nothing large in `/tmp`.
* **A number with no artifact id is not quotable.**  Every figure above is in
  `sw/testdata/chainflat/`.

### 9.1 TWO INSTRUMENT DEFECTS, BOTH FOUND BY AN INSTRUMENT PRINTING NOTHING

Recorded because they are the same shape as WAVE 5 §1.2's, and because nothing
else caught them.

1. **`sw/chainflat_probe.py` with no leg selected wrote the census down to
   zero.**  Invoked bare it produced a valid-looking 550-byte artifact
   containing **0 sequences**, over a real 46-sequence one.  It now **REFUSES**
   (exit 2) and says why.
2. **`sw/chainflat_report.py` had six regexes with `^` and no `re.M`**, which
   anchors at the start of the whole string: every field parsed to `None` and
   the reporter died on its first row.  An instrument returning nothing where it
   should return a number.  Fixed, with the reason recorded beside them.
