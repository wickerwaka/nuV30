# THE CHAIN ANATOMY — WAVE 5.  RESULTS, SCORED AS REGISTERED.

Pre-registration **`c99556b145`**
(`docs/notes/chain_anatomy_prereg_2026-09-09.md`), committed **BEFORE the first
measurement fit**; instruments **`25f6292560`**, committed before it; the PC-4
repair **`c24d9b97f0`**, committed before the run it governs.

**MEASUREMENT ONLY.  NO RTL.  OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM
WAS PROGRAMMED.**  No Codex consulted.  No nested subagent spawned.
**THIS WAVE PROPOSES NO DESIGN AND LANDS NOTHING.**  It is **NOT A GATE**, it
writes **no receipt**, and **no figure in it may be quoted as a pass**;
`docs/notes/standing_gates.md` §A governs every timing figure below.

| | |
|---|---|
| **Tree** | `c24d9b97f0` (`master`).  `git status --porcelain hdl/` carries **0 tracked modifications at the start and 0 at the end** (twelve pre-existing untracked `hdl/quartus_gate_*.log` files, not this wave's, never `git add`ed) |
| **Configuration** | **NO-EXCEPTION** — the CE multicycle deleted from `hdl/nec_test.sdc` for the measurement fits only, restored by the driver's `finally`.  **3 CONTROL seeds + 1 RETENTION** |
| **Instruments** | `sw/chain_srcmap.py`, `sw/sta_chain_anatomy.tcl`, `sw/run_chain_anatomy.py`, `sw/chain_anat_report.py` |
| **Artifacts** | `sw/testdata/chainanat/` — `{control_seed1,control_seed2,control_seed3,retention_seed1}.{txt,arrivalpoints.txt,truefmax.txt,seedecho.txt}`, `report.txt`, `srcmap.json`, `srcmap_control.txt`, `driver.out`, `run.log.gz`, and `ABORTED-PC4-VACUITY/` (retained, **quoted nowhere**) |
| **Tool** | Quartus 17.1.0 Lite Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns |

---

## §0 THE HEADLINE — **THE REGISTERED HONEST NULL IS THE ANSWER**

§3.4 of the pre-registration said, before any fit:

> *If the honest answer is "no two-way split can work and trimming cannot find
> 7.6 ns either", THE DOCUMENT SAYS THAT.*

**IT SAYS THAT, AND IT SAYS IT WITH THREE MEASURED NUMBERS.**

| | measured, 4 draws | |
|---|---|---|
| the whole `ce → ce` arc, no exception | **43.088 – 44.223 ns**, mean **43.485**, spread **1.135** | needs **29.6** |
| **the folded chain — EVERY position ≥ 1 on the arc, added up** | **17.185 – 22.078 ns**, mean **19.766** (39.6 – 51.2 % of the arc) | |
| **THE FLOOR — the arc with EVERY folded position deleted AND THE DELETION CHARGED NOTHING** | **27.205 – 31.613 ns**, mean **29.490** | **the requirement is 29.6** |

> **DELETING THE ENTIRE FOLDED CHAIN — all of it, for free — LANDS ON 29.49 ns
> MEAN AGAINST A 29.6 ns REQUIREMENT.  It is OVER the requirement on 2 of the 4
> draws.  There is no margin in the chain to find.**

And the two-way split is not merely unpromising, it has already been measured:

> **CUTTING THE LOOP GROWS IT.  Same NO-EXCEPTION configuration, same bar:
> this wave's UNSPLIT tree measures the whole arc at 43.485 ns mean; WAVE 4's
> tree, differing only by a complete 778-bit cut set at the chain entry,
> measured 21.556 + 37.224 = 58.780 ns.  +15.30 ns, +35 %.**  Every uncut
> `(upstream, downstream)` pair in §3's table plus that growth lands where WAVE
> 4 actually landed — **37.2 ns downstream, 26.86 MHz** — and not at 29.6.

**THE 43.5 ns IS NOT IN THE FOLDED CHAIN.  IT IS IN THE FRONT END AND CHAIN
POSITION 0'S OWN BODY**, which measure **21.010 – 26.190 ns** together (48.8 –
60.4 % of the arc), of which the front end alone — the microcode ROM read, the
row decode, the operand / queue-state select and the EA add — is **19.710 –
25.611 ns**.  WAVE 3 §5.2 found the loop; this measures which half of it is
long, and **it is not the half three waves have been aiming at.**

---

## §1 E-1 — THE POSITIVE CONTROLS.  **REPORTED FIRST.  ALL PASS ON ALL FOUR DRAWS.**

| draw | PC-1 resolver | PC-2 walker | PC-3 segmenter | PC-4 BIU | |
|---|---|---|---|---|---|
| CONTROL seed 1 | PASS | PASS | PASS | PASS | |
| CONTROL seed 2 | PASS | PASS | PASS | PASS | |
| CONTROL seed 3 | PASS | PASS | PASS | PASS | |
| RETENTION seed 1 | PASS | PASS | PASS | PASS | |

**E-1 IS MET.**  What each one actually demonstrated, on this netlist, not by
citation:

* **PC-0 `chain_srcmap`** — the parser independently recovered **33 state arms /
  24 carrying `if (chain == 4'd0)` / 9 without**, and the **9 unguarded names
  are EXACTLY the 9 states `st_zero_ok()` returns true for**, parsed separately
  out of `v30u_eu.sv`: `S_BIND S_DECODE S_DECODE2 S_EA_CALC S_ENTER S_INSTR_END
  S_TAIL S_TAIL_POP S_TAKE_OPC`.  `sw/testdata/chainanat/srcmap_control.txt`.
* **PC-1 the resolver** — `-through` a **`get_pins`** collection of one node on
  the worst arc returns **1** path; the **`get_nodes`** collection of the SAME
  node returns **0**.  WAVE 1 §0.2 re-demonstrated LIVE on every draw.
* **PC-2 the walker** — reached the DEST phase on all four, found **54 · 45 ·
  43 · 43** data cells, and **reproduced Quartus's own `-data_delay` to
  0.000 ns** on every draw.
* **PC-3 the segmenter** — on a path FORCED `-through` an `st_zero_ok` pin (a
  boundary crossing BY CONSTRUCTION) it reports **≥ 1 boundary**; **the same
  path under a marker name that does not exist reports 0.**
* **PC-4 the BIU matcher** — a path forced through **one named pin**
  (`…|u_biu|q_ripe_lead_n~4|combout`) carries **8** BIU nodes, and the same path
  under WAVE 4 §6.1's known-wrong `v30u_biu:` TYPE prefix carries **0**.

### 1.1 ⚠⚠ **PC-4 WAS VACUOUS, AND ITS OWN FAILURE ON THE FIRST REAL DRAW IS WHAT SAID SO**

This is the wave's instrument finding and it is the vacuous-gate pattern again.

PC-4's first form asked
`get_timing_paths -from $v30u_ce -to $v30u_ce -through <1,176 BIU pins>` and
counted BIU nodes on what came back.  On the **development** netlist (WAVE 4's
leftover `db`) that read **8** and **PASSED** — but *that* netlist's worst
`ce → ce` arc CARRIES the round trip, so an **IGNORED `-through`** returns a
path with BIU nodes on it anyway.  **The control agreed for the wrong reason.**
On the first real draw of this wave it read **0 BIU nodes on a path forced
through 1,176 BIU pins**, the control REFUSED (exit 4, nothing below quotable),
and the run was aborted.

**The fix is not a wider bar.**  `-through` is now given **ONE PIN AT A TIME**,
**the pin that answered is NAMED**, and **the bulk form is KEPT AND PRINTED
BESIDE IT as the known-wrong control** — so the signature can never come back
silently.  It is printed on every draw of the final run:

```
  PC-4 BIU        |u_biu| combout pins: 1176   (single-pin tries: 1)
       BIU nodes on a path forced through ONE NAMED PIN : 8  (MUST be >= 1)
       the pin that answered : emu|system_large|u_core|u_biu|q_ripe_lead_n~4|combout
       ...that same path under the TYPE prefix          : 0
       ...and the BULK -through of 1176 pins yields     : 0  BIU nodes
```

**A BULK FIGURE BELOW THE SINGLE-PIN FIGURE IS `-through` BEING ACCEPTED AND
IGNORED.**  The aborted run is retained at
`sw/testdata/chainanat/ABORTED-PC4-VACUITY/` and **nothing is quoted from it.**

### 1.2 TWO MORE DEFECTS, BOTH FOUND BY AN INSTRUMENT PRINTING NOTHING

Recorded because nothing else caught them and because they are one shape.

1. **The seed-honoured check read the wrong file.**  It looked at
   `hdl/<rev>.fit.rpt`; the report is in `hdl/output_files_ucore/`.  It printed
   `*** NO SEED ROW ***` — **absence** reported where `quartus_gate.py`'s own E8
   comment says absence must never read as agreement.
2. **`sta_truefmax_probe.tcl` writes `<arg>.truefmax.txt`**, so passing
   `<stem>.truefmax` produced `<stem>.truefmax.truefmax.txt` and the reporter's
   `SAME k = 1.0` check could not find it.

### 1.3 THE CONFIGURATION CHECKS — BOTH MET, BOTH POSITIVE

* **The multicycle deletion reached the compiler**: `SAME` measures
  **k = 1.0000** on all four draws (a draw whose `SAME` still read 2.0 would
  have been fitted to the exception and would answer a different question).
* **The seed reached the fitter**, read back from Quartus's own *Fitter Initial
  Placement Seed* row: **1 / 2 / 3 / 1**, as asked.
* **The retention macro reached the compiler**, proved POSITIVELY rather than by
  the flag: `observation endpoints` reads **64** on the retention draw against
  **44** on all three controls.

---

## §2 Q1 / E-2 — THE PER-POSITION PROFILE

`sw/sta_chain_anatomy.tcl` §C, all four draws, `sw/testdata/chainanat/report.txt`.

| draw | worst `ce → ce` arc | levels | boundaries | **seg 0** (front end + position 0's body) | per FOLDED position | folded total |
|---|---:|---:|---:|---:|---|---:|
| CONTROL seed 1 | **43.375** | 42 | 3 | **26.190** (60.4 %) | 7.95 · 4.21 · 4.42 | **17.185** |
| CONTROL seed 2 | **44.223** | 45 | 3 | **25.505** (57.7 %) | 7.26 · 3.79 · 6.11 | **18.718** |
| CONTROL seed 3 | **43.088** | 43 | 4 | **21.010** (48.8 %) | 3.87 · 6.33 · 4.10 · 6.20 | **22.078** |
| RETENTION seed 1 ⧉ | **43.254** | 41 | 4 | **22.171** (51.3 %) | 3.99 · 7.47 · 2.99 · 6.37 | **21.083** |

⧉ **THE RETENTION DRAW IS A CROSS-CHECK AND IS NOT THE SOURCE OF ANY CONCLUSION
IN THIS DOCUMENT.**  It agrees with the CONTROL draws on every structural
finding, which is what a core-internal class should do.

**Aggregates over the four draws:**

| | min | max | spread | mean |
|---|---:|---:|---:|---:|
| the arc | 43.088 | 44.223 | **1.135** | **43.485** |
| **seg 0** | 21.010 | 26.190 | 5.180 | **23.719** |
| **the folded chain, total** | 17.185 | 22.078 | 4.893 | **19.766** |
| **one folded position** (n = 14) | 2.993 | 7.945 | 4.952 | **5.359** |

**THE HEADLINE OF Q1: POSITION 0 IS FAT AND THE FOLDED POSITIONS ARE THIN, AND
THE RTL SAYS SO IN ADVANCE.**  24 of the 33 arms carry `if (chain == 4'd0)`;
only 9 can stand at a position ≥ 1.  Measured, the fold is worth roughly
**23.7 ns for segment 0 against 5.4 ns for each folded position.**

### 2.1 SEGMENT 0 READ IN TWO — **A DECLARED HEURISTIC**

Segment 0 carries the FRONT END *and* chain position 0's body, and position 0
has **no `st_zero_ok` guard** to mark the join.  The reading taken is the first
`Decoder<N>` cone on the arc — the position-0 `case (st_n)` decode:

| draw | FRONT END | the cone | position 0's body + everything after |
|---|---:|---|---:|
| CONTROL seed 1 | **20.292** | `Decoder28` | 23.083 |
| CONTROL seed 2 | **19.710** | `Decoder28` | 24.513 |
| CONTROL seed 3 | **25.611** | `Decoder32` | 17.477 |
| RETENTION seed 1 | **20.043** | `Decoder28` | 23.211 |

⚠ **THIS IS A READING, NOT A MEASUREMENT.**  WAVE 1 §5.2 identified `Decoder28`
as the chain entry independently on its own draws, which corroborates it — and
**WAVE 2 REFUTED the identification of `Decoder28#1` with an RTL seam.**  A
`Decoder<N>` cone belonging to some other case statement would move this row.
Seed 3's is `Decoder32`, and its front end reads 5.9 ns longer than the other
three; that is exactly the sensitivity being declared.

### 2.2 **E-2 IS SPLIT, AND IT IS REPORTED SPLIT**

E-2 asked whether the per-position attribution is STABLE ACROSS SEEDS.  **It is
stable in the aggregate and NOT stable per segment.**

* **STABLE**: the arc (spread **1.135 ns** over four draws), the fact that the
  arc launches at the `ucdecode`/`ucrom` M10K and lands on `modrm_reg` on every
  draw, the front-end/folded partition to within ~5 ns, and the per-position
  mean.
* **NOT STABLE**: the **number of boundaries** (3 · 3 · 4 · 4), the individual
  segment spans (2.99 – 7.95 ns), and which `Decoder<N>` opens position 0.

**So the per-segment split is a property of the PLACEMENT, and the front-end vs
folded-chain partition is a property of the TREE.**  Every conclusion in §0 and
§5 rests on the second and none on the first.

---

## §3 Q2 / E-3 — THE CUMULATIVE PROFILE, AND THE YES/NO

For each boundary `k`: `(upstream ns, downstream ns)` of the WHOLE arc, front
end included.

| draw | k | upstream | downstream | worse half | both ≤ 29.6 ? |
|---|---:|---:|---:|---:|---|
| **CONTROL s1** (43.375) | **0** | **26.190** | **17.185** | **26.190** | **YES** |
| | 1 | 34.135 | 9.240 | 34.135 | no |
| | 2 | 38.340 | 5.035 | 38.340 | no |
| **CONTROL s2** (44.223) | **0** | **25.505** | **18.718** | **25.505** | **YES** |
| | 1 | 32.764 | 11.459 | 32.764 | no |
| | 2 | 36.550 | 7.673 | 36.550 | no |
| **CONTROL s3** (43.088) | **0** | **21.010** | **22.078** | **22.078** | **YES** |
| | **1** | **24.875** | **18.213** | **24.875** | **YES** |
| | 2 | 31.204 | 11.884 | 31.204 | no |
| | 3 | 35.300 | 7.788 | 35.300 | no |
| **RETENTION s1** ⧉ (43.254) | **0** | **22.171** | **21.083** | **22.171** | **YES** |
| | **1** | **26.159** | **17.095** | **26.159** | **YES** |
| | 2 | 33.629 | 9.625 | 33.629 | no |
| | 3 | 36.622 | 6.632 | 36.622 | no |

**THE BEST-BALANCED `k` IS `k = 0` — THE CHAIN ENTRY — ON ALL FOUR DRAWS**, with
a worse half of 26.190 / 25.505 / 22.078 / 22.171 ns.

### 3.1 **E-3's ANSWER: `YES` ON THE UNCUT ARITHMETIC — AND THE CAMPAIGN HAS ALREADY MEASURED THAT `YES` TO BE FALSE**

> **THE UNCUT ANSWER IS YES.  THE MEASURED ANSWER IS NO, AND THE MEASUREMENT
> ALREADY EXISTS: IT IS WAVE 4.**

WAVE 4 took **exactly the cut this table calls best** — a complete 778-bit cut
set at the chain entry, in the same NO-EXCEPTION configuration, on the same
bar — and measured **STAGE 1 = 21.556 ns / 19 levels** and
**STAGE 2 = 37.224 ns / 40 levels**.  Its uncut estimate for the same seam
(WAVE 1 §4, `Decoder28#1`) had been **22.8 up / 25.9 down**.

| | uncut estimate | **realised after the cut** | error |
|---|---:|---:|---:|
| upstream half | 22.8 (WAVE 1) / 21.0 – 26.2 (here) | **21.556** | ≈ 0 |
| **downstream half** | 25.9 (WAVE 1) / **17.2 – 22.1 (here)** | **37.224** | **+11.3 … +20.0 ns** |
| the whole loop | 43.485 (here, unsplit, same configuration) | **58.780** | **+15.30 ns, +35 %** |

**THE UPSTREAM HALF PREDICTS WELL AND THE DOWNSTREAM HALF DOES NOT, BECAUSE A
CUT DOES NOT DIVIDE THE ARC — IT GROWS IT.**  Uncut, Quartus merges logic freely
across the prospective boundary; after the cut both halves are re-synthesised
and cannot.  Measured here, within one configuration: **+15.30 ns.**

So the honest reading of the table is:

> **NO `k` GIVES BOTH HALVES ≤ 29.6 ns IN A BUILD THAT EXISTS.**  Every
> downstream figure in the table (17.2 – 22.1 ns at `k = 0`) plus the measured
> +15.3 ns of cutting lands at **32 – 37 ns**, which is what WAVE 4 measured
> (**37.224**) and is **26.86 MHz**.  WAVE 1 §6 item 1 said the estimates were
> not predictions; this is the size of the gap between them.

---

## §4 Q3 / E-4 — WHAT DOMINATES INSIDE A POSITION

Attribution via `sw/chain_srcmap.py`, with **the fold applied**: only the 9
`st_zero_ok` arms can stand at a position ≥ 1, so a node inside a folded segment
can only have been written by one of those 9, and a name like `opc_base_n`
(`S_BIND` / `S_INSTR_END` / `S_IRQ_D`) collapses there.

### 4.1 **NO SINGLE ARM DOMINATES.  THE REPEATED COST IS STRUCTURAL.**

E-4 is answered in its second form.  What the folded segments contain, in order,
across the draws — the same shape every time:

```
CONTROL s1  seg 1 (7.945)  Decoder32 -> ld_b_n[TAKE_OPC] -> Ram20 -> Ram20 -> eu_halted_n[DECODE2]
CONTROL s3  seg 2 (6.329)  Decoder32 -> ld_b_n[TAKE_OPC] -> Ram20 -> Ram20 -> p
RETENTION   seg 2 (7.470)  Decoder32 -> ld_b_n[TAKE_OPC] -> Ram18 -> Ram20 -> always6 -> eu_halted_n[DECODE2]
CONTROL s2  seg 1 (7.259)  Selector1620 x3 -> pv[BIND,DECODE,DECODE2] -> always6 -> Selector1742 x2
```

and the TAIL segment, on every draw:

```
CONTROL s1  seg 3 (4.416)  seg_override_n[DECODE,INSTR_END] -> opc_base[BIND,INSTR_END] x2 -> modrm_reg[INSTR_END] x2
CONTROL s2  seg 3 (6.108)  Decoder38 -> opc_base[BIND,INSTR_END] x2 -> modrm_reg[INSTR_END] x2
CONTROL s3  seg 4 (6.195)  Decoder38 -> opc_base[BIND,INSTR_END] x2 -> modrm_reg[INSTR_END] x2
RETENTION   seg 4 (6.366)  Decoder38 -> opc_from_modrm_n[BIND,INSTR_END] -> opc_base x2 -> r_kind -> modrm_reg
```

**THE PER-POSITION COST IS ONE `case (st_n)` DECODER PLUS ONE REGISTER-FILE
READ, AND IT REPEATS ONCE PER POSITION.**  `Ram12` / `Ram18` / `Ram20` are the
`gpr [0:7]` / `sreg [0:3]` arrays (`v30u_eu.sv:236-237`), and the reason there
is one per position is in the source: **`S_EA_CALC` is one of the nine arms that
can stand at a position ≥ 1, and its body opens with an eight-way read of
`gpr_n`** (`ea = gpr_n[R_BW] + gpr_n[R_IX]` and its seven siblings).  Every copy
of the chain therefore reads the register file again.  **WAVE 1 §2 measured the
same thing in a different vocabulary** — *"`Ram15` and `Ram21` are the
register-file read, and there is one per chain position"*.

The arms that are actually named on the arc are the ones the RTL says are
zero-cost: **`S_TAKE_OPC` → `S_DECODE` → `S_DECODE2`** (`ld_b_n`, then the file
read, then `eu_halted_n` / `pv`) and **`S_BIND` / `S_INSTR_END`** at the tail
(`opc_base`, `opc_from_modrm_n`, `modrm_reg`, `r_kind`).  The weighted
attribution reads `INSTR_END = 3.0 – 3.5` and `BIND = 1.0 – 2.0` in the tail
segment on every draw.

### 4.2 SEGMENT 0 IS **NOT** A CASE ARM, AND THAT IS THE POINT

Segment 0's nodes are **14 – 22 of 17 – 24 UNATTRIBUTED** — `ucrom`, `Mux277`,
`Mux354`, `Mux358`, `Mux359`, `Equal218`, `Equal243`, `Selector1552`, `s1_val`,
`e_s1`, `s1_now`, `ind_now`, `q_cnt`, `q_ripe_lead_n`, `Add46`.  **They are not
in `v30u_eu_step.svh` at all**: they are the microcode ROM read, the row decode,
the Source-1 / Source-2 operand selects and the queue-state logic — the FRONT
END.  `chain_srcmap` classifies `sigma`, `s1_val` and `it_val` as FRONT-END and
finds no arm for them, which is the correct answer and not a gap.

---

## §5 Q4 / E-5 — SHARED OR INDEPENDENT.  **INDEPENDENT, ON THREE INDEPENDENT PIECES OF EVIDENCE**

**E-5 is answered with evidence, not by assertion.**

**(a) THE COPY CENSUS — the fold is visible in the netlist.**  Distinct
`combout` nodes per RTL base name inside `v30u_eu`, identical on all three
CONTROL draws (they share one map, as `map-once / fit-N` requires):

| signal | class | CONTROL (all three) | RETENTION |
|---|---|---:|---:|
| `st_n` | CHAINABLE | **158** | 167 |
| `ld_b_n` | CHAINABLE | **62** | 62 |
| `pv` | CHAINABLE | **44** | 43 |
| `opc_base` | CHAINABLE | 19 + 44 indexed = **63** | 63 |
| `m_kind` | CHAINABLE | 25 + 9 = **34** | 23 |
| `stop` | CHAINABLE | **18** | 17 |
| `seg_override_n` | CHAINABLE | **18** | 14 |
| `st_zero_ok` | CHAINABLE | **9** | 12 |
| `sigma` | FRONT-END | 133 indexed | 140 |
| `s1_val` | FRONT-END | **53** | 56 |
| `it_val` | FRONT-END | **8** | 8 |
| `rst_ctr_n` | POS0-ONLY | **0** | 0 |
| `ld_dlo_n` | POS0-ONLY | **0** | 0 |
| `ld_ripe_prev_n` | POS0-ONLY | **0** | 0 |
| `nmi_latch_n` | POS0-ONLY | **1** | 1 |
| `rloop_n_n` | POS0-ONLY | **1** | 1 |
| `zzz_no_such_signal` | NEGATIVE CONTROL | **0** | 0 |

**The CHAINABLE / POS0-ONLY ratio is the fold, measured**: a signal only a
guarded arm writes has **0 or 1** cones; a signal a chainable arm writes has
**9 – 158**.  The negative control reads 0, so the census can say NO.

**(b) THE SAME BASE NAME APPEARS IN CONSECUTIVE SEGMENTS AT DIFFERENT NODE
INSTANCES.**  CONTROL seed 1's arc carries `ld_b_n` in segment 0 **and** in
segment 1, and `Ram12` in segment 0 with `Ram20` in segment 1; the retention
draw carries `Ram18` **and** `Ram20` inside one segment.  Structurally parallel,
different instances: **each position computes it again.**

**(c) NOTHING ON ANY ARC IS REUSED ACROSS POSITIONS.**  The per-position shape
in §4.1 recurs with a *different* `Decoder<N>` (`Decoder28` · `Decoder32` ·
`Decoder36` · `Decoder38`) and a *different* `Ram<N>` at each position.

> **THEREFORE: MAKING EACH POSITION CHEAPER SCALES BY THE NUMBER OF POSITIONS ON
> THE ARC — 3 or 4 here — NOT BY 1.**  And that is the arithmetic that makes §0
> binding rather than hopeful: 3-4 positions × ~5.4 ns each **is** the 19.8 ns,
> and 19.8 ns is not 13.9 ns short of nothing — it is the whole of what could
> ever be recovered from the chain, and recovering all of it still leaves 29.5.

⚠ **ONE COUNTER-OBSERVATION, RECORDED**: `st_zero_ok` shows **9** cones (12 on
retention) where the design has at most 6 positions ≥ 1, and `st_n` shows
**158**.  These are Quartus decomposing wide muxes and duplicating for fanout,
**not** evidence of sharing — but they are the reason the copy census is offered
as evidence (a) and not as an arithmetic.

---

## §6 Q5 — THE FLOOR.  **AND IT IS THE WAVE'S SECOND HEADLINE**

Two readings, both **APPROXIMATIONS AND LABELLED AS SUCH.**

**(a) THE ARITHMETIC FLOOR** — the worst arc with every intermediate segment and
every boundary run removed, i.e. **segment 0 plus the tail segment that reaches
the destination register**, charging the removal nothing:

| draw | seg 0 | + tail | **floor** |
|---|---:|---:|---:|
| CONTROL seed 1 | 26.190 | 4.416 | **30.606** |
| CONTROL seed 2 | 25.505 | 6.108 | **31.613** |
| CONTROL seed 3 | 21.010 | 6.195 | **27.205** |
| RETENTION seed 1 ⧉ | 22.171 | 6.366 | **28.537** |
| | | **mean** | **29.490** |

**AGAINST A REQUIREMENT OF 29.6 ns.**  Two of the four draws are **OVER** it.

**(b) THE MEASURED FLOOR** — the worst `ce → ce` arc that crosses **zero** chain
boundaries, over 1,000 endpoint-diverse paths per draw:

| draw | 0 boundaries | 1 | 2 | 3 | 4 |
|---|---:|---:|---:|---:|---:|
| CONTROL seed 1 | **41.366** | 37.533 | 42.389 | 43.377 | 41.347 |
| CONTROL seed 2 | **40.169** | 37.233 | 41.809 | 44.223 | 41.186 |
| CONTROL seed 3 | **32.624** | 34.338 | 40.546 | 41.401 | 43.090 |
| RETENTION seed 1 ⧉ | **31.848** | — | 41.548 | 42.261 | 43.504 |

**A `ce → ce` ARC THAT NEVER CROSSES A CHAIN BOUNDARY IS ALREADY 31.8 – 41.4 ns.**

⚠ **BOTH READINGS ARE APPROXIMATIONS, SAID PLAINLY.**  (a) assumes a change that
removes 19.8 ns of logic and costs nothing, and **no change is free — the one
measured change in this campaign cost +15.3 ns** (§3.1).  (b) is a population of
paths that *happen* not to cross more boundaries, not the same design with
positions 1-6 deleted; a 0-boundary path still runs through the front end and
through one position's body.

⚠ **AND NOTE THE SLACK-ORDERED SCAN, WHICH IS DEGENERATE AND SAYS SOMETHING**:
ranked by slack, **996 of the top 1,000 paths on CONTROL seed 1 cross exactly 3
boundaries** (802/1000 at 3 and 198 at 4 on seed 2).  The binding population is
one arc shape repeated, which is why the endpoint-diverse scan exists at all.

---

## §7 Q6 — THE BIU ROUND TRIP.  **IT IS IN THE FRONT END, OUTSIDE THE CHAIN, AND IT IS DRAW-DEPENDENT**

| draw | on the binding arc? | enters at | leaves at | **span** | which segment |
|---|---|---:|---:|---:|---|
| CONTROL seed 1 | **ABSENT** | — | — | — | — |
| CONTROL seed 2 | **8 nodes** | 13.895 | 16.789 | **2.894** | **segment 0** |
| CONTROL seed 3 | **8 nodes** | 13.876 | 16.572 | **2.696** | **segment 0** |
| RETENTION seed 1 ⧉ | **ABSENT** | — | — | — | — |

The cone is exactly WAVE 4's: `u_biu|q_cnt~N` → (`Add46~0` on seed 2) →
`u_biu|q_ripe_lead_n~N` — and it is grounded in the source, not only in the
netlist:

```
v30u_eu.sv:2211   assign q_pop = q_demand;              (combinational, EU -> BIU)
v30u_biu.sv:853   wire pop_now = q_pop && q_ripe;
v30u_biu.sv:1919  if (pop_l) q_cnt = q_cnt - 4'd1;      (next-state, combinational)
v30u_biu.sv:922   wire [3:0] poppable_n = (grn_ttl != 0) ? (q_cnt - grn_n) : q_cnt;
v30u_biu.sv:923   assign q_ripe_lead_n = (poppable_n != 0) || …   (BIU -> EU)
```

**THE ANSWERS Q6 ASKS FOR:**

* **WHERE relative to the chain positions** — it enters at **13.9 ns** of a
  43 – 44 ns arc and leaves at **16.6 – 16.8 ns**, i.e. **entirely inside
  segment 0, UPSTREAM of the first chain boundary** on both draws that carry it.
* **INSIDE or OUTSIDE the chain's own cone** — **OUTSIDE.**  It is a FRONT-END
  feature on this tree.
* **What it is worth** — **2.70 – 2.89 ns**, against WAVE 4's 3.7 ns of 41.3 on
  the SPLIT tree.

⚠ **AND IT REVISES WAVE 4's PICTURE WITHOUT CONTRADICTING IT.**  WAVE 4 found
the round trip on the binding arc of the **split** tree and named it *"the next
arc"*.  On the **reverted** tree it is on **2 of 4** draws and, when present, it
is upstream of every chain boundary.  **Closing it would take ~2.8 ns off the
front end on the draws that have it and nothing at all on the draws that do
not** — which is consistent with WAVE 4 §8.1 item 3's own conclusion that
closing it *"is measured NOT to be enough"*.

⚠ `q_ripe_lead_n` is one of **`r7_lint`'s two DECLARED UNRESOLVED carriers**, and
that declaration is about **READY-liveness**, not about combinational round
trips: `r7_lint` PASSES on this tree (0 undeclared carriers / 0 undeclared
unresolved / 0 `stop` sites, 51 `stop` sites scanned).  **The round trip is not
an `r7_lint` violation and `r7_lint` is not the instrument that would see it.**

---

## §8 THE `SAME` CLASS PER DRAW — **NOT A G6 RESULT AND NOT QUOTABLE AS Fmax**

One `sta_truefmax_probe` row per draw, off an anatomy driver that **writes no
receipt**.  It is printed because §1.3 needs the `k`, not because it is a number.

| draw | `SAME` k | slack | T_min | (MHz) | `$v30u_ce` |
|---|---:|---:|---:|---:|---:|
| CONTROL seed 1 | 1.0000 | −13.764 | 45.014 | 22.22 | 2,029 |
| CONTROL seed 2 | 1.0000 | −14.574 | 45.824 | 21.82 | 2,068 |
| CONTROL seed 3 | 1.0000 | −13.092 | 44.342 | 22.55 | 2,065 |
| RETENTION seed 1 ⧉ | 1.0000 | −13.660 | 44.910 | 22.27 | **1,607** |

They sit in family with WAVE 3's registered pre-L2 no-exception baseline
(**21.82** `worst-of-5`), which is what a reverted tree should read, and **below**
WAVE 4's 23.50 — which is WAVE 4's cut set, which this tree does not have.
**Four draws are not a distribution; `standing_gates.md` §A governs.**

⚠ **RECORDED AND NOT EXPLAINED: the RETENTION draw's `$v30u_ce` reads 1,607
where the three CONTROL draws read 2,029 / 2,068 / 2,065** — ~450 fewer
registers in the same collection, agreed by two independent instruments
(`sta_truefmax_probe.tcl` and `sta_chain_anatomy.tcl`).  The three CONTROL draws
also disagree among themselves by 39 registers **off one shared map**, which is
fitter duplication and is expected (WAVE 1 §6.1 measured 2,109 / 2,096 / 2,101 /
2,084 the same way).  **The 450 is not.**  It is a cross-check leg and nothing in
this document rests on it, but it is not explained and is not dismissed.

---

## §9 WHAT THE ANATOMY SAYS

**⚠ EVERY CANDIDATE BELOW CARRIES WAVE 1 §6 ITEM 1's CAVEAT VERBATIM: *a Quartus
net name is not by itself an RTL seam*, and WAVE 2 REFUTED exactly that
identification for `Decoder28#1`.  THIS WAVE PROPOSES NO DESIGN AND LANDS
NOTHING.  The user decides what follows.**

### 9.1 THE TWO THINGS THAT ARE NOT CANDIDATES ANY MORE

1. **A TWO-WAY `ce`/`ce_half` SPLIT.**  Four waves have aimed at it.  This wave
   measures why it cannot land: the best-balanced boundary on all four draws is
   the chain entry, WAVE 4 cut exactly there with a complete cut set, and **the
   cut GREW the loop by 15.30 ns (+35 %)** to 58.780 ns.  The downstream half
   realised at **37.224 ns** against an uncut estimate of 17.2 – 22.1.  **No
   choice of `k` in §3's table survives that correction.**
2. **TRIMMING THE FOLDED CHAIN.**  The whole folded chain is **19.766 ns mean**,
   and deleting *all* of it for *free* leaves **29.490 ns mean** against a
   **29.6 ns** requirement — **over it on 2 of 4 draws.**  The requirement asks
   the arc to fall **43.485 → 29.6, i.e. −13.885 ns (−31.9 %)**; there is
   19.766 ns of folded chain, so the trim would have to take **70 % of it and
   cost nothing.**

### 9.2 WHAT THE MEASUREMENT POINTS AT INSTEAD, NAMED AND NOT PROPOSED

* **THE FRONT END IS THE LONGER HALF AND HAS NEVER BEEN THE TARGET.**
  **19.710 – 25.611 ns**, 45 – 59 % of the arc: the `ucdecode`/`ucrom` M10K read,
  the row decode, the Source-1/Source-2 operand selects, the EA add and the
  queue-state logic.  WAVE 3 §5.2 established that the EU is a LOOP and that the
  chain sits in **both** halves of any cut at a ROM boundary; WAVE 4 measured the
  chain; **nobody has measured a change to the front end.**
* **THE PER-POSITION REGISTER-FILE READ.**  `S_EA_CALC` is one of the nine arms
  that can stand at a position ≥ 1 and it opens with an eight-way read of
  `gpr_n`, so **every unrolled copy reads the register file again** — measured as
  a distinct `Ram<N>` in every folded segment on every draw, and measured
  independently by WAVE 1 §2.  It is the one repeated cost with a single named
  cause.  **Its size is not measured here** and no claim is made about what
  hoisting it would buy.
* **THE BIU ROUND TRIP IS WORTH 2.70 – 2.89 ns ON 2 OF 4 DRAWS AND 0.000 ON THE
  OTHER TWO**, and it is in the front end.  It is not a chain question.

### 9.3 THE SENTENCE THE PRE-REGISTRATION ASKED FOR

> **No two-way `ce`/`ce_half` split reaches 29.6 ns on this design, and trimming
> the folded chain cannot find the 13.9 ns either — because the folded chain is
> only 19.8 ns of a 43.5 ns arc, and removing every last nanosecond of it, at no
> cost, still leaves 29.5 ns against a 29.6 ns requirement.  The arc's longer
> half is the front end and chain position 0's own body, and it has not been the
> target of any wave so far.**

---

## §10 WHAT IS **NOT** MEASURED HERE

1. **NOTHING WAS SIMULATED AND NOTHING WAS BUILT DIFFERENTLY.**  No RTL changed;
   `git diff c24d9b97f0 -- hdl/` is empty.  Every figure is read off four fits of
   the tree as it stands.
2. **THE POST-CHANGE DELAYS.**  §3's table and §6's floor are UNCUT-netlist
   arithmetic.  The one calibration the campaign owns is WAVE 4's, and it says
   the arithmetic under-predicts by ~15 ns on the loop and ~11 – 20 ns on a
   downstream half.
3. **WHAT ANY TRIM WOULD COST.**  §9.2 names the register-file read; it does not
   measure what removing it would do to the arc, to the ALM count or to
   behaviour, and it must not be quoted as if it did.
4. **THE DRAW POPULATION IS 3 + 1.**  Not a distribution.  `standing_gates.md`
   §A governs: the same tree has drawn 19.42 and 45.91 MHz.
5. **`CHAIN_MAX` ITSELF.**  The bound is 7 and the measured occupancy 6; this
   wave crossed **3 or 4** boundaries on its binding arcs and says nothing about
   whether the bound could be lower — that is an RTL question and this wave
   edits no RTL.
6. **THE `$v30u_ce` = 1,607 RETENTION READING** (§8) is unexplained.

---

## §11 E-1 … E-6, SCORED

| bar | verdict |
|---|---|
| **E-1** every classifier carries a positive control, reported FIRST; a miss VOIDS the wave | **MET on the scored run — and it MISSED FIRST and the run was ABORTED for it.**  PC-4 was vacuous, failed on the first real draw, was repaired (single-pin `-through`, the pin NAMED, the bulk form kept as the known-wrong control), and the aborted run is retained at `ABORTED-PC4-VACUITY/` and quoted nowhere.  On the scored run: **PC-1 · PC-2 · PC-3 · PC-4 PASS on 4 of 4 draws**, PC-0 PASS.  §1 |
| **E-2** Q1's attribution is stable across seeds; report all four draws | **MET, AND REPORTED SPLIT.**  All four draws reported.  **STABLE**: the arc (spread 1.135 ns), the endpoints, the front-end/folded partition.  **NOT STABLE**: the boundary count (3 · 3 · 4 · 4), the individual segment spans and which `Decoder<N>` opens position 0 — *"a property of the placement, not of the tree"*, and reported as such.  §2.2 |
| **E-3** Q2 as a table over `k` with an explicit YES/NO on 29.6 ns | **MET.**  Table in §3, every `k` on every draw.  **YES on the uncut arithmetic (`k = 0`, all four draws); NO in any build that exists**, with WAVE 4's +15.30 ns as the measured correction.  §3.1 |
| **E-4** Q3 names its top contributors with delays, or reports that no single arm dominates | **MET in the second form: NO SINGLE ARM DOMINATES.**  The repeated cost is structural — one `case (st_n)` decoder plus one register-file read per position, 2.99 – 7.95 ns each, mean 5.359 — and the named arms are `S_TAKE_OPC` → `S_DECODE2` and `S_BIND` / `S_INSTR_END`.  §4 |
| **E-5** Q4 answers shared-vs-independent WITH EVIDENCE | **MET — INDEPENDENT, on three pieces of evidence**: the copy census with its negative control, the same base name at different instances in consecutive segments, and a different `Decoder<N>` and `Ram<N>` per position.  One counter-observation recorded.  §5 |
| **E-6** `git status --porcelain hdl/` clean at start AND end; nothing under `hdl/` edited | **MET.**  Clean at both ends; `git diff c24d9b97f0 -- hdl/` is EMPTY.  The SDC patch that made the NO-EXCEPTION fits was applied by `sw/run_chain_anatomy.py` and reverted by its `finally` (`hdl/ restored: CLEAN` in `driver.out`); `hdl/nec_test_ucore.qsf` — the declared §70.7 exemption — moved during every Quartus stage and was `git checkout --`'d after each one.  **`git add -A hdl/` was never used**; the twelve pre-existing untracked `hdl/quartus_gate_*.log` files are still untracked |

---

## §12 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM PROGRAMMED.**  No Codex.
  No nested subagent.
* Single-writer guard by EXACT binary name before every Quartus stage; the
  driver additionally REFUSES to run on a tracked-dirty `hdl/`.
* **MAP ONCE PER CONFIGURATION, FIT ONCE PER SEED** — the three CONTROL draws
  share one map, which is what makes them three draws of one tree.
* **THE ABORTED RUN IS DECLARED, NOT OMITTED.**  It saw a §A block and no
  result; every number in this document comes from the run taken after the PC-4
  repair.
* No large intermediate was written to `/tmp`; `run.log` (1.0 MB) is committed
  gzipped beside the artifacts it documents.
* **A number with no artifact id is not quotable.**  Every figure above is in
  `sw/testdata/chainanat/`, named per §Tree table.
