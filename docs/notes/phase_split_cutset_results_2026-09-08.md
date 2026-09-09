# THE PHASE SPLIT, DONE AS A CUT SET — WAVE 4.  RESULTS, SCORED AS REGISTERED.

Pre-registration **`2e5b11a193`**
(`docs/notes/phase_split_cutset_prereg_2026-09-08.md`), committed **BEFORE THE
FIRST EDIT UNDER `hdl/`**; **AMENDMENT A-1 `bc047724d9`**, committed before the
edit *it* governs.

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**
No Codex consulted.  No nested subagent spawned.

| | |
|---|---|
| **Tree at entry** | `6d0c770e91` (`master`), `git status --porcelain hdl/` clean of tracked modifications |
| **The edits** | (a) `c46004eba1` · (b) `3e0a4dfc3b` · (c) `742b52f643` · **A-1** `a0e45d8076` |
| **The instruments** | `50403d8321`, `9805a468bc`, `630eedbb04`, `fe734779ce`, `9c5e7637d3`, `d1fc858c02` |
| **Artifacts** | `sw/testdata/cutset/{before,after,after_a1}/`, `sw/testdata/cutset/diag_*`, `sw/testdata/g6dist/cutset-w4{,-a1}-noexc-{control,retention}-n5/` |
| **Tool** | Verilator 5.032; Quartus 17.1.0 Lite Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns |

---

## §0 THE HEADLINE — **C-1 IS FAILED, AND THE MEASUREMENT SAYS THE MECHANISM CANNOT REACH THE BAR**

| | CONTROL `worst-of-5` | RETENTION `worst-of-5` | **GAP to 32.0 MHz** |
|---|---:|---:|---:|
| WAVE 3's pre-L2 no-exception BASELINE (`9ce05a8350929355…`) | 21.82 | *not baselined* | 10.18 |
| WAVE 2, the loop-carried `_n` set alone (495 b) | 22.78 | 21.61 | 9.22 |
| WAVE 3, L2 the registered ROW | 22.18 | 22.16 | 9.82 |
| **WAVE 4, the cut set as first landed (678 b)** | **22.15** | **22.90** | **9.85 / 9.10** |
| **WAVE 4 + A-1, the COMPLETED cut set (778 b)** | **23.50** | **23.57** | **8.50 / 8.43** |

**TWENTY OF TWENTY DRAWS ARE `RED`.**  Records: `c8dfcc062bb4412f…` /
`e14d4cadd1553f6e…` (manifest `4f2637bfec77a35e…`) and `56e7892e0ef74ecb…` /
`729c20c4e2e4df16…` (manifest `d61aecdf37d6c8d6…`).

### 0.1 ⚠⚠ **AND THE WAVE'S REAL RESULT IS NOT THAT NUMBER.  IT IS THIS ONE:**

> **STAGE 2 — `s1q -> anything`, the EU's unrolled chain ALONE, with the ROM
> read, the whole row decode, the operand selects, the ALU flag rails and the
> iterative unit ALL captured on `ce_half` and out of it — measures
> `s1q[555] -> opc_base[3]`, 40 logic levels, DATA DELAY 37.224 ns, against a
> 31.25 ns single-cycle budget.  ZERO of its 105 arrival points are in the BIU:
> it is the EU's own chain end to end.**
>
> **A `ce`/`ce_half` PHASE SPLIT CANNOT CLOSE THIS DESIGN AT 32 MHz HOWEVER THE
> CROSSING SET IS DRAWN, BECAUSE THE DOWNSTREAM HALF IS ALREADY 6.0 ns OVER
> BUDGET ON ITS OWN — 26.9 MHz.**  That is P-e's answer, and it is the
> campaign's answer rather than this wave's failure.

STAGE 1 is comfortably inside: `… -> s1q[732]`, 19 levels, **21.556 ns**.
**The cut is BALANCED at 21.6 / 37.2 only because there is 58.8 ns of arc to
divide, not 43.5.**

---

## §1 THE VERDICT TABLE

| bar | verdict |
|---|---|
| **C-1** the requirement (G6 `--seeds 5`, E1-E5 every draw, BOTH configurations, no exception) | **FAILED — `RED` on 20 of 20 draws.**  CONTROL `worst-of-5` **22.15** (first cut set) / **23.50** (A-1); RETENTION **22.90** / **23.57**.  §5 |
| **C-2** the exception is GONE and it is CHECKED | **MET** — zero uncommented `set_multicycle_path`, zero `set_false_path`, no *"CE multicycle"* info line, and **every one of the 20 receipts reports `SAME` at `k = 1.0000` with an EMPTY `off_class`** |
| **C-3(a)** the cut set is complete BY CONSTRUCTION, lint passes and is demonstrated FIRING | **MET on the A-1 tree, and the ROUTE TO IT IS THE WAVE'S SECOND FINDING** — the lint passed on the FIRST cut set while the cut set was INCOMPLETE, because its completeness clause asked too narrow a question.  §3 |
| **C-3(b)** on a no-exception fit the worst `ce -> ce` path's arrival points DO name the shadow | **MISSED, TWICE, AND IT IS THE POINT.  0 of 107 on the first cut set; 0 of 107 on A-1.**  Against WAVE 2's 0 of 103.  §4 |
| **C-4** pin identity | **MET on both trees** — `chain_lfsr_gate` 4 of 4 signatures and every gap count and census BYTE-IDENTICAL, `fz2_replay` scored-content sha256 IDENTICAL over 305 seeds, ladder 29 of 31 SAME with both movers registered |
| **C-5** the ladder at its registered values | **MET on both trees**, with **three `standing_gates.md` disagreements reported as findings — and ONE OF THEM IS AN ERRATUM AGAINST WAVES 2 AND 3**.  §2 |
| **C-6** save state does not move | **MET** — `SS_COUNT` 232 / `SS_VERSION` 0x8F / `SS_TAG` 0x8FE8 / 0 UNMAPPED, ALL UNCHANGED; whitelist 3 → **4**, grown by exactly the shadow's entry |
| **C-7** divisor independence | **MET on both trees** — 169,000/169,000 at `--ce-div` 2, 3, 4 and 8; `--ce-div 1` REFUSED, clause cited |
| **C-8** the two stages measured, and the third class named | **DELIVERED, AND THE THIRD CLASS EXISTS ON BOTH TREES.**  §4 |
| **C-9** non-vacuity | **B, B2 and C FIRE.  A MISSED and is reported as MISSED**; A2, added and declared, fires on the same one bit.  §6 |
| **C-10** the revert condition | **TRIGGERED, AND OBEYED.**  §8 |
| **C-11** the phase-stability premise asserted at runtime | **MET — it did not fire once**, across 169,000 goldens at four divisors on both trees, 17,350 `ulockstep` scenarios, 283 HLT-sweep cells, the 1,371-cell S16 walk, the four `evt` cells, `check_boot` 220 and 400, `check_ab_sim`'s 187 rows and 4 × 400,000 `chain_lfsr` clocks — now over **778** bits including the whole wire cone, the operand selects and the iterative unit |
| **C-12** `demux_off_gate` passes, `CE_HALF` unconditional | **MET** — PASS, 3 legs, `FPOPS` 2,742 · `BS_KINDS` 7 · `WRITES` 1,390 · `ADDR_MOVES` 7,729, both GONE clauses REFUSED naming their pins.  Its summary line reads *"the two muxed ports are GONE"*, the registered P-12 wording change |
| **P-a** no-exception CONTROL `worst-of-5` > 26.0 MHz | **REFUTED — 22.15, then 23.50.**  Reported as registered, not re-derived |
| **P-b** the binding path's arrival points name the shadow | **REFUTED** (= C-3(b)) |
| **P-c** 778 bits declared, fewer survive synthesis | **MET** — **668 of 778** survive on the A-1 fit (591 of 678 on the first).  Nothing is claimed from the count |
| **P-d** the corrected lint reads 0, and the arrival points name the shadow | **HALF MET**: the lint reads **0**; the arrival points still read **0 of 107** |
| **P-e** STAGE 2's worst falls from 39.462 ns | **MET, AND IT IS THE ANSWER: 39.462 -> 37.224 ns.**  The registered clause said in advance that a small fall *"says the chain alone is over budget and the split cannot close whatever crosses it — which would be the campaign's answer, not this wave's failure."*  It is |

---

## §2 C-4 / C-5 / C-7 — THE LADDER AND PIN IDENTITY

`sw/phase_split_ladder.sh` on the UNEDITED tree (`sw/testdata/cutset/before/`),
on the first cut set (`…/after/`) and on A-1 (`…/after_a1/`), diffed leg by leg
by `sw/phase_split_ladder_diff.py`.

**`=== ladder diff: 29 SAME / 2 MOVED / 0 MISSING` on BOTH edited trees**, and
both movers are registered and are not measurements:

* **`ss_lint`** — `ss_flopcensus` 228 → **229** architectural flops, whitelist
  3 → **4**.  That is C-6's *"grown by exactly the shadow's entry"*.
* **`demux_off_gate`** — its own summary line, *"three muxed ports"* → *"two"*.
  Edit (a)'s registered C-12 change, and a re-wording.

| leg | registered | before | first cut set | **A-1** |
|---|---|---|---|---|
| `r7_lint` | PASS | PASS — 0 undeclared carriers / 0 undeclared unresolved / 0 `stop` sites | same | **same** |
| `check_core --opcodes all --cases 0` | 169,000 | 169,000/169,000 | same | **same** |
| `8F.0` | 500 | 500/500 | same | **same** |
| HLT sweeps `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = 279/283 | 97 · 93 · 45 · 44 | same | **same** |
| `v0.1-w1` / `-w3` | 1,200 / 1,200 | 1,200 / 1,200 | same | **same** |
| `v0.1-w1 --opcodes EB` | 200 | 200 | same | **same** |
| the four `evt` cells | 200 / 1,200 / 200 / 1,200 | same | same | **same** |
| `v0.1-w1evt-biased` | 1,200 | 1,200 | same | **same** |
| `ulockstep --golden all --cases 50` | 17,350 ALL LOCKSTEP | **17,350/17,350, ALL CASES LOCKSTEP** | same | **same** |
| `ghost_launch_law score` | 200/200 | 200/200 = 100.0 % | same | **same** |
| `check_boot --core ucore` | 220 and 400 | MATCH 220, MATCH 400 | same | **same** |
| `check_ab_sim --core ucore` | 187 | MATCH over 187 rows | same | **same** |
| `sm3_s16_score --core ucore` | 1,320/1,371 | 1,320/1,371 | same | **same** |
| `demux_off_gate` | PASS | PASS | PASS (C-12 wording) | **PASS** |
| `test_artifact` | 45/45 | 45/45 | same | **same** |
| `test_quartus_gate` | see §2.1 | **255/255** | same | **same** |
| `ucrom_mif_check` | PASS | PASS | same | **same** |
| **C-7** `--ce-div 2 / 3 / 8` | 169,000 each | 169,000/169,000 each | same | **same** |
| **C-7** `--ce-div 1` | REFUSED | REFUSED, clause cited | same | **same** |

**C-4(a) `chain_lfsr_gate` — BYTE-IDENTICAL, 4 OF 4, ON BOTH EDITED TREES.**
4 seeds × 400,000 fabric clocks of arbitrary bytes with LFSR memory, LFSR
`READY` and LFSR `INT`: `1d01c9b269ffaa94` · `b39b040a98b28e5d` ·
`0997b773cd99c030` · `d05b6c3c3d9fbe78`, with `CHAIN_DEPTH_MAX` 6 · `entry_st`
25 · `coincide` 0 · every `ce_clocks` · **all eight gap counts** · and the whole
live-cycle census identical; `diff` over the three row kinds is EMPTY.

**C-4(b) `fz2_replay` — SCORED-CONTENT sha256 IDENTICAL**,
`de949fd373ed77de7f7d980a1728538de1b6ddaf6e200a9e61ba69bd1a8b2942` on all three
runs, 305 seeds on `tb_sys ret`.  The `tb_sys` receipt moved
(`4e3bcc731801d658…` → `ba7470b89525f77c…` → `a3e86ee212993ec1…`), **which is
NOT quoted as evidence of anything** — WAVE 3 §6 item 9 measured that a receipt
moves across rebuilds of a byte-identical tree.  ⚠ Both legs ran with
`--no-fabric-era-guard`, which is stated rather than worked around: the guard
REFUSED on the **pre-edit** tree already, so what these legs measure is BEFORE
vs AFTER on ONE TREE and they say nothing about fabric.

### 2.1 ⚠ THREE DISAGREEMENTS WITH `standing_gates.md` — AND THE THIRD IS AN ERRATUM AGAINST WAVES 2 AND 3

All measured on the UNEDITED tree before the first edit.

1. **`test_quartus_gate` reads 255/255 on this tree** (with a build tree on
   disk).  `standing_gates.md` line 494 registers **200/200**; CLAUDE.md's quick
   reference registers 254 (255 with a build tree).  The measurement agrees with
   CLAUDE.md.  **`standing_gates.md` line 494 is STALE.**  *(WAVE 2 §6.1 item 1
   and WAVE 3 §1.5 item 1 said the same and are confirmed.)*
2. **`ss_lint` reads `SS_COUNT` 232 / 228 flops / 3 whitelist entries.**
   `standing_gates.md` §B registers **226 / 214 / `SS_VERSION` 0x8D / `SS_TAG`
   0x8DE2** — the `fuzz-v2-on-relanding` figures.  `master`'s `v30u_ss_pkg.sv`
   carries 0x8F and `SS_COUNT` 232, so `SS_TAG` is **0x8FE8**.  **That row is a
   different branch's.**  *(Confirmed.)*
3. ⚠⚠ **ERRATUM — WAVE 2 §6.1 ITEM 3 AND WAVE 3 §1.5 ITEM 3 ARE FACTUALLY
   WRONG, AND THIS WAVE CHECKED THE ARTIFACT INSTEAD OF THE RECALL.**  Both say
   *"the four `evt` cells, `v0.1-w1evt-biased`, `check_boot 400` and
   `check_ab_sim` are not carried as rows in `standing_gates.md` §B's ucore
   table at all."*  **THEY ARE.**  §B's ucore table carries *the four `evt`
   cells* (line 1298), *`w1evt-biased` (preserved)* (1299), *boot march ⧉ …
   `--timed 220` and `--timed 400`* (1303) and *the core inside the real
   integration ⧉ … 187 rows MATCH* (1313).  **A gap was reported where none
   exists, twice, and neither wave opened the file to check.**  CLAUDE.md's own
   standing rule is the one that catches this: *"Verify against the artifact,
   not against recall."*  Booked in §7; not fixed here, because editing another
   wave's results document is coordinator territory.

**None of the three is this wave's doing and none is fixed here.**

---

## §3 C-3(a) — **THE CUT SET WAS NOT COMPLETE, AND THE FIRST LINT COULD NOT SEE IT**

### 3.1 WHAT THE FIRST CUT SET WAS, AND WHY IT PASSED ITS OWN LINT

`sw/cutset_census.py` derived the crossing set from the source and returned
**70 names / 183 bits, ZERO live-tainted**; the design took shape (B) on the
balance, as pre-registered; `sw/cutset_lint.py` read **PASS — 70 members /
0 violations / `module wires the block names: 0`**.  The RTL is the registered
construction and nothing about it was improvised: each wire keeps its logic as
`s1w_<x>`, the short name becomes a `reg`, STAGE 1 assigns `<x> = s1w_<x>` once
at its head, the reg joins the pack and the unpack, and **no `.svh` is edited**.

**AND IT WAS STILL A BYPASS.**  `v30u_eu.sv` has **SIX other combinational
`always @*` blocks** — the ALU, the BCD unit, the iterative stepper, the
Source1 select, the Source2 select and the reset function — and they drive
module-level **`reg`s**, which are exactly as combinational and exactly as
pre-cut as a `wire`.  The census walked CONTINUOUS ASSIGNMENTS ONLY.  **TEN
NAMES / 100 BITS WERE MISSING**:

`s1_val` (16) · `s1_byte` (1) · `s1_wbyte` (1) · `s2_val` (16) · `s2_wbyte` (1)
— the Source1 / Source2 operand selects, **which is exactly the 9.34 ns segment
WAVE 1 §2 measured** — and `it_val` · `it_tmpa` · `it_flags` · `it_fmask` (16
each) · `it_writes_tmpa` (1), the one shared iterative stepper.

The netlist said so before the amendment was written, and the arrival-point dump
named the leak to the node
(`sw/testdata/cutset/diag_ctl_seed3.arrivalpoints.txt`):

```
  modrm_reg[1] -> opc_sel[1]~2 -> Add4~2 -> sigma[1]~0 -> s1_bus[65]~43
              -> LessThan7 -> Selector5/3 -> sigma[13]~42 -> Mux264~6
              -> v1~22 -> Add57~1 (the EA add) -> ... -> the chain -> opc_base[3]
```

### 3.2 A-1 — THE COMPLETED SET, AND WHAT IT COST

**80 names / 283 bits + wave 2's 495 = `S1W` 778**, against the registered STOP
of 900.  Live-tainted members: **0** — the ten add no module input to the union,
which stays the seven registered BIU views (`eu_access_active`, `eu_opr_free`,
`eu_rd_done_n`, `eu_slot_busy`, `eu_wr_done_n`, `eu_wr_eval`, `q_byte`).

```
=== cutset_lint: PASS   (80 members / 0 violations)
  module combinational values the block names : 0 (must be 0)
=== phase_split_lint: PASS   (156 members / 778 bits / 0 violations)
```

**A-1 is worth +1.35 MHz on CONTROL (22.15 → 23.50) and +0.67 on RETENTION.**
Area: ALMs **9,882-9,925 → 9,903-9,950 (24 %)**, `fit_registers`
**6,073-6,111 → 6,437-6,482**.  ⚠ Both cut sets are **SMALLER in ALMs than the
un-split baseline** (WAVE 3's no-exception baseline drew 10,210-10,252), despite
~500 more flops.  **Recorded, not explained**; `standing_gates.md` §A governs and
A&S combinational counts are not reproducible run to run (§74.4a).

---

## §4 C-3(b) / C-8 — **THE TWO STAGES, AND THE THIRD CLASS**

`sw/sta_cutset_diag.tcl` on a fresh **CONTROL** fit of each tree's worst draw
(seed 3 for the first cut set, seed 2 for A-1), with WAVE 1 §0.2's positive
control passing on both (*"paths returned: 1"*).

| | first cut set (678 b) | **A-1 (778 b)** |
|---|---|---|
| `$v30u_ce` | 2,179 | 2,512 |
| shadow bits surviving synthesis | 591 of 678 | **668 of 778** |
| **worst `ce -> ce`** | `modrm_reg[1] -> opc_base[3]`  −13.888, 44 levels, **44.502 ns** | `ucdecode M10K -> opc_base[3]~DUP`  −11.309, 45 levels, **41.302 ns** |
| **arrival points naming `\|s1q`** | **0 of 107** | **0 of 107** |
| arrival points in `v30u_biu` | **0** | **8** |
| **STAGE 1** (`* -> s1q`) worst | +8.326, 17 levels, **22.271 ns** | +8.071, 19 levels, **21.556 ns** |
| **STAGE 2** (`s1q -> *`) worst | −8.808, 36 levels, **39.462 ns** | −6.633, 40 levels, **37.224 ns** |
| top 200 `ce -> ce`: STAGE 1 / STAGE 2 / **NEITHER** | 0 / 0 / **200** | 0 / 0 / **200** |

### 4.1 **C-8's THIRD CLASS EXISTS ON BOTH TREES, AND ON A-1 IT IS NAMED**

C-8 says *"The third must not exist; if it does, name it — that is the next
cut."*  It exists.  On A-1 the binding arc **LEAVES THE EU AND COMES BACK**, and
the dump names it to the node
(`sw/testdata/cutset/diag_a1_ctl_seed2.arrivalpoints.txt`):

```
  ucdecode M10K -> ucrom~782/428/90 -> r_farjmp~1 -> comb~15 -> Mux277~15/3/8
     -> s1_now[0]~2 -> ind_now[0]~1
     -> u_biu|q_cnt~4 -> u_biu|q_cnt~5 -> u_biu|q_ripe_lead_n~0/~5     <<< 3.7 ns
     -> Mux358~7 -> Mux359~2 -> Decoder37~8 -> ld_b_n~1 -> Ram14~7 -> pv~10
     -> ... -> opc_base[3]~DUPLICATE
```

**THAT IS AN EU → BIU → EU COMBINATIONAL ROUND TRIP**, and it is `r7_lint`'s own
**DECLARED UNRESOLVED CARRIER `q_ripe_lead_n`** — declared, known, and never
connected to the phase-split campaign until now.  The EU's row decode reaches the
BIU through this module's own combinational OUTPUTS (which are LIVE on purpose:
the BIU must decide an act from the level DURING the clock that names it), the
BIU's `q_cnt` / `q_ripe_lead_n` cone is combinational, and the EU's chain reads
it back.  **A cut set inside `v30u_eu.sv` cannot divide it, and no lint about
`v30u_eu.sv`'s own names can see it.**  The same sentence is already in the
source and has been since the §52.3 reset pass:

> *"…and ran `v30u_eu|wb_seg[0]~0` -> `v30u_biu|grn_n` -> `q_ripe_lead_n` -> the
> EU's twelve chain positions, 58.9 ns against 31.25 ns."* — `v30u_biu.sv`

### 4.2 ⚠⚠ **AND CUTTING IT WOULD NOT BE ENOUGH — WHICH IS THE WAVE'S ANSWER**

**The worst STAGE 2 path has ZERO BIU nodes on it** (measured: `grep -c u_biu`
over its 105 arrival points = **0**).  It is `s1q[555]~DUPLICATE -> opc_base[3]`,
40 levels, **37.224 ns**, entirely inside the EU's own unrolled chain.

So even with the round trip cut, the binding class becomes STAGE 2 at
**37.224 ns = 26.86 MHz**, against a 31.25 ns budget.

> **THE DOWNSTREAM HALF OF THE SPLIT IS 6.0 ns OVER BUDGET BY ITSELF.  NO
> CHOICE OF CROSSING SET CHANGES THAT, BECAUSE THE CROSSING SET IS WHAT FEEDS
> STAGE 2 AND STAGE 2 IS THE UNROLLED CHAIN.**  The next mechanism has to make
> the CHAIN shorter — fewer positions in series, or the chain itself split
> across a second phase — not move more of its inputs upstream.

---

## §5 C-1 / C-2 — G6, `--seeds 5`, BOTH CONFIGURATIONS, TWICE

Every draw: `SAME` at **k = 1.0000** with an **EMPTY `off_class`**, E7
`n_moved` 1 / `moved_offending` 0 (the declared §70.7 exemption,
`hdl/nec_test_ucore.qsf`), E8 5/5 seeds honoured, E10 N = 5.  **C-2 MET on all
twenty**, which is what makes C-1's failure interpretable rather than ambiguous.

### 5.1 THE FIRST CUT SET — manifest `4f2637bfec77a35e…`

**CONTROL, record `c8dfcc062bb4412f…`, `worst-of-5@seeds{1,2,3,4,5}` = 22.15 MHz — `RED`**

| seed | Fmax | worst setup | ALMs | binding cone |
|---|---:|---:|---:|---|
| 1 | 22.39 | −13.412 | 9,882 (24 %) | `ucdecode M10K -> r_kind[0]` |
| 2 | 22.48 | −13.228 | 9,894 | `ucdecode M10K -> modrm_reg[1]` |
| **3** | **22.15** | **−13.888** | 9,925 | `modrm_reg[1] -> opc_base[3]` |
| 4 | 22.32 | −13.558 | 9,887 | `ucdecode M10K -> m_kind[1]` |
| 5 | 22.86 | −12.500 | 9,886 | `ucdecode M10K -> modrm_reg[0]~DUP` |

> worst 22.15 · median 22.39 · best 22.86 · **spread 0.71**

**RETENTION, record `e14d4cadd1553f6e…`, `worst-of-5` = 22.90 MHz — `RED`**:
22.95 · 22.93 · **22.90** · 23.65 · 23.47, ALMs 10,049-10,104.

### 5.2 A-1, THE COMPLETED CUT SET — manifest `d61aecdf37d6c8d6…`

**CONTROL, record `56e7892e0ef74ecb…`, `worst-of-5` = 23.50 MHz — `RED`**

| seed | Fmax | worst setup | ALMs | binding cone |
|---|---:|---:|---:|---|
| 1 | 24.55 | −9.491 | 9,903 (24 %) | `ucdecode M10K -> opc_base[4]` |
| **2** | **23.50** | **−11.309** | 9,929 | `ucdecode M10K -> opc_base[3]~DUP` |
| 3 | 24.47 | −9.621 | 9,944 | `ucdecode M10K -> m_kind[0]` |
| 4 | 24.20 | −10.071 | 9,950 | `ucdecode M10K -> m_kind[0]~DUP` |
| 5 | 24.06 | −10.312 | 9,906 | `ucdecode M10K -> opc_base[3]` |

> worst 23.50 · median 24.20 · best 24.55 · **spread 1.05**

**RETENTION, record `729c20c4e2e4df16…`, `worst-of-5` = 23.57 MHz — `RED`**:
24.84 · 24.20 · 24.10 · 24.77 · **23.57**, ALMs 9,876-9,923.

⚠ **The two configurations' bands OVERLAP on both waves, so no
control-vs-retention delta may be computed** (the distribution gate's own rule).
⚠ **The manifests DIFFER between the two waves and are IDENTICAL between the two
configurations of each wave** — which is the check that A-1's edit reached the
compiler and that the configurations differ by the `--verilog_macro` and nothing
else.

---

## §6 C-9 — NON-VACUITY

`sw/cutset_nonvacuity.py`, on the A-1 tree.  Each case constructs its condition
by a temporary patch, rebuilds where it must, runs, and reverts with
`git checkout --`; `hdl/ restored: CLEAN`.

| case | probe | result |
|---|---|---|
| **A** the shadow is LOAD-BEARING | `} = s1q ^ 778'd1` in front of `check_core --opcodes 90 --cases 5` | ⚠ **DID NOT FIRE — 5/5.**  The LSB of the concatenation is its LAST member, and after A-1 that is `it_writes_tmpa`; **`90` is a NOP and exercises no iterative step.**  Before A-1 the LSB was `wr_out_n` and the same probe fired (WAVE 2 P-8(c)) |
| **A2** *(added, and the miss is reported not replaced)* | the SAME one bit in front of `check_core --opcodes all --cases 0` | **FIRED.**  Choosing a different BIT after seeing a result would be choosing an instrument after seeing a result; choosing a WIDER POPULATION for the same instrument is not |
| **B** the lint fires on a re-introduced bypass | `s1w_row_bus` spliced back into `v30u_eu_step.svh` — WAVE 2's exact defect | **X2 AND X4 FIRE**, `cutset_lint: FAIL` |
| **B2** …and on a bypass no `s1w_` prefix betrays | a read of `sigma`, a module wire never in the cut set | **X4 FIRES** — and X2 cannot, by construction, which is what shows X4 is not a restatement of X2 |
| **C** S-1's `$fatal` names the EU | `ce_half <= 1'b0` in the TB | **FIRES**, and the message contains **"STAGE-1 capture edge"** |

### 6.1 ⚠ **THREE DEFECTS IN THIS WAVE'S OWN INSTRUMENTS, ALL FOUND BY MAKING THEM SAY NO**

They are recorded because nothing else caught them and because they are all one
shape — **an instrument that cannot say NO**, the vacuous-gate pattern.

1. **`sta_cutset_diag.tcl`'s BIU clause matched the TYPE prefix `v30u_biu:`.**
   Quartus prints the type prefix on REGISTER names and OMITS it on
   COMBINATIONAL node names, so it found every BIU flop and **not one BIU LUT** —
   and it is the LUTs that make a round trip.  It reported **`v30u_biu : 0` on a
   path carrying EIGHT BIU nodes.**  Now `|u_biu|`; re-run on the same fit it
   reads 8 and prints the first and last.  `9c5e7637d3`.
2. **`cutset_lint`'s X2 scanned only `v30u_eu.sv` and not the includes** — so a
   bypass in `v30u_eu_step.svh`, where the chain body lives, was invisible to
   it.  C-9 case B reported X2 *"DID NOT FIRE"* on exactly that probe.  Fixed.
3. **The declaration parser dropped every `wire` that follows a block.**
   Statements are split on `;`, so the first declaration after an
   `always`/`case`/`function` block begins with that block's `end`/`endcase`
   tokens and a `startswith("wire")` test drops it.  **`sigma` — the ALU's own
   result rail — was invisible**, which is why B2 could not fire.  Fixed; the
   declaration count goes **421 → 430** and, **measured, the cut set does not
   change: still 80 names / 283 bits with the leak count still 0.**  The bug cost
   the PROBE its target and cost the CUT SET nothing.

### 6.2 ⚠ A FOURTH, WHICH IS WAVE 2's AND IS STILL IN THE TREE

**`sw/sta_phase_split_diag.tcl` AS COMMITTED CANNOT RUN.**  Its
`set fh [open [lindex $quartus(args) 2] w]   # 2, not 0 …` carries a TRAILING
`#`, and **Tcl has no trailing comment**, so `set` receives the comment words and
dies with *"wrong # args"*.  Measured here: WAVE 4's copy of that line failed
exactly so on its first run, and the fix is to put the comment on its own line.
WAVE 2 §10 item 7(a) recorded the INDEX half of that defect; the corrected line
was evidently never executed.  **Not fixed here** — it belongs to a reverted
wave's retained instruments — but named so the next reader does not lose an hour.

---

## §7 WHAT IS OWED, AND WHAT IS BOOKED RATHER THAN TAKEN

1. **A FABRIC CONFIRMATION IS OWED AND UNPAID.**  Nothing here has been on a
   board and no bitstream was programmed.  The wave REVERTS, so nothing is owed
   *for it*; WAVE 2 §10 item 1 and WAVE 3 §6 item 1 are restated unchanged.
2. **`standing_gates.md` §A/§B carries two stale ucore rows** (§2.1 items 1-2),
   both of them WAVE 2 §10 item 2's and WAVE 3 §6 item 3's, still unfixed.
   **BOOKED** — a coordinator-territory edit.
3. ⚠ **AND ITEM 3 OF THAT SAME BOOKING IS AN ERRATUM, NOT A GAP** (§2.1 item 3).
   The four rows two waves reported missing from `standing_gates.md` §B's ucore
   table **are in it**.  **BOOKED** as a correction to two results documents.
4. **`check_core --ss-sweep` IS STILL NOT ON ANY REGISTERED LADDER.**  WAVE 2
   §10 item 3 booked it; WAVE 3 §6 item 10 re-booked it; this wave does not run
   it either.  The resume path is the one place the shadow's derivation is not
   covered by the C-11 assert, which excludes `ss_we` by construction.  **BOOKED
   for the third time**, and the repetition is itself worth noticing.
5. **THE `srst` ADDRESS-MIRRORING ARM OF L1 IS STILL UNFALSIFIED** by the
   standing ladder (WAVE 3 §2 case D).  Unchanged.
6. ⚠ **`hdl/nec_test_ucore.qsf` MUST BE RESTORED BETWEEN QUARTUS RUNS, AND THIS
   WAVE LOST A SWEEP TO NOT DOING IT.**  `run_cutset_diag.sh`'s `quartus_map`
   rewrote it, and the next `quartus_gate` sweep died at **E1** — *"nec_test_ucore.qsf
   is STALE"* — with `RED at E1, nothing built`.  One `git checkout --` and it
   ran.  The §70.7 exemption is a permitted MOVER, not a permitted LEAVER.
7. **NOTHING IN `sim/`, `v30u_ss_pkg.sv` OR ANY `.svh` WAS TOUCHED** by any edit
   of this wave.  `git add -A hdl/` was never used; the twelve pre-existing
   untracked `hdl/quartus_gate_*.log` files are still untracked.

---

## §8 THE VERDICT AND THE REVERT

**C-1 FAILED.  C-10 IS UNAMBIGUOUS:** *"If C-1 fails, or any leg of
C-4/C-5/C-6/C-7 moves, THE LANDING DOES NOT HAPPEN.  Revert, report, keep both
documents.  Do not soften a bar to make a landing possible, and do not re-scope
the cut after seeing a result.  A wave that reports 'still N MHz short, and here
is the arc' has done its job — report the GAP explicitly."*

**THE GAP IS 8.50 MHz (CONTROL) AND 8.43 MHz (RETENTION).**

**No bar was softened.  Nothing was flashed.**  The one judgment is AMENDMENT
A-1, and it is stated in the pre-registration in terms a reader can disagree
with: completing a set the instrument mis-derived is not re-scoping, because the
cut, the stages, the mechanism and every bar are unchanged — and **the first cut
set's result is reported in full and is not withdrawn.**

### 8.1 WHAT THIS WAVE ESTABLISHED, AND IT IS NOT NOTHING

1. **THE SPLIT IS BIT-EXACT AT 778 BITS**, over a crossing set that now includes
   the microcode row, the whole row decode, the operand selects, the ALU flag
   rails and the iterative unit — 169,000 goldens at four divisors, 17,350
   `ulockstep` scenarios, 1.6 M `chain_lfsr` clocks byte-identical, 305
   `fz2_replay` seeds sha256-identical, **with the phase-stability premise
   asserted on every clock and never once violated.**
2. **THE MECHANISM'S CEILING IS MEASURED AND IT IS BELOW THE BAR.**  STAGE 2 —
   the unrolled chain alone, BIU-free — is **37.224 ns = 26.86 MHz** against a
   31.25 ns budget.  **A `ce`/`ce_half` split cannot deliver 32 MHz on this
   design however the crossing set is drawn.**  Three waves have now aimed at
   what feeds the chain; the chain is the wall, and this is the measurement that
   says so.
3. **THE NEXT ARC IS NAMED TO THE NODE**: the EU → BIU → EU combinational round
   trip through `q_cnt` → **`q_ripe_lead_n`**, `r7_lint`'s own declared
   UNRESOLVED carrier, worth 3.7 ns of the binding 41.3 — **and closing it is
   measured NOT to be enough**, which is more useful than closing it would have
   been.
4. **A STANDING LINT EXISTS AND HAS BEEN MADE TO FAIL FOUR WAYS** —
   `sw/cutset_lint.py`, with X4's completeness clause covering wires AND the
   `always @*`-driven module regs, demonstrated firing on two different kinds of
   re-introduced bypass.
5. **FOUR INSTRUMENT DEFECTS WERE FOUND BY MAKING INSTRUMENTS SAY NO** (§6.1,
   §6.2), three of them this wave's own.

### 8.2 THE THREE NUMBERS THAT MAY BE QUOTED FROM THIS WAVE

**CONTROL `worst-of-5` 23.50 MHz** (`56e7892e0ef74ecb…`), **RETENTION 23.57**
(`729c20c4e2e4df16…`), and **STAGE 2's worst at 37.224 ns**.

⚠ **AND THE ONE THAT MAY NOT.**  `standing_gates.md` §A governs every timing
figure: the same tree has drawn 19.42 and 45.91 MHz, and one green build is not
closure — **which cuts both ways, so these twenty RED draws are not a proof that
no phase split can close, only that these did not on these draws.**  What makes
them strong is not the count but §4.2: STAGE 2's length and its endpoints are
structural, and they are measured with the BIU excluded by counting.
