# WAVE 8 — **THE FRONT END.  THE ANATOMY, THE RANKED LIST, AND ONE MEASURED LEVER.**  RESULTS, SCORED AS REGISTERED.

Pre-registration **`f0c4dac496`** (`docs/notes/frontend_anatomy_prereg_2026-09-09.md`),
committed **BEFORE THE FIRST QUARTUS STAGE**; instruments **`05211a1959`**,
committed before it; the standalone harness **`a623e098db`**, committed
**before the anatomy named a candidate**, with `ARMS` deliberately empty.

**MEASUREMENT ONLY.  NOTHING IS LANDED IN THE CORE.  NO RTL UNDER
`hdl/rtl/ucore/` WAS EDITED.**  **OFFLINE ONLY — NO BOARD, NO FLASH, NO
BITSTREAM WAS PROGRAMMED.**  No Codex consulted.  No nested subagent spawned.
This document is **NOT A GATE**, it writes **no receipt**, and **no figure in it
may be quoted as a pass**; `docs/notes/standing_gates.md` §A governs every
timing figure — **one green build is not closure.**

| | |
|---|---|
| **Tree** | `8deb1e7d8e` … `3940385586` (`master`) — WAVE 7's HEAD.  `git status --porcelain hdl/` carries **0 tracked modifications at the start and 0 at the end** (twelve pre-existing untracked `hdl/quartus_gate_*.log` files, not this wave's, never `git add`ed) |
| **Configuration** | **NO-EXCEPTION** — the CE multicycle deleted from `hdl/nec_test.sdc` for the measurement fits only, restored by the driver's `finally`.  **3 CONTROL seeds + 1 RETENTION** |
| **Instruments** | `sw/frontend_srcmap.py`, `sw/sta_frontend_anatomy.tcl`, `sw/run_frontend_anatomy.py`, `sw/frontend_anat_report.py`, `sw/sta_node_id.tcl`, `sw/frontend_proto.py` |
| **Artifacts** | `sw/testdata/frontend/anat/` (4 draws × `.txt` / `.arrivalpoints.txt` / `.population.txt` / `.truefmax.txt` / `.seedecho.txt`, plus `report.txt`, `nodeid_ret1.nodeid.txt`, `driver.out`, `run.log`) and `sw/testdata/frontend/ucflat/` |
| **Tool** | Quartus 17.1.0 Lite Build 590, `5CSEBA6U23I7`, Slow 1100 mV 100 C, `divclk` 31.250 ns; Verilator 5.032 |

---

## §0 THE HEADLINE

> ### **THE ARC IS 33.0 ns AND MUST REACH 29.6.  THE BIU ROUND TRIP IS GONE FROM THE CONTROL ARC ENTIRELY.  THE LARGEST NAMED THING LEFT IS THE MICROCODE ROM READ — `ucrom`, 3.805 ns ON 100 % OF 1,600 PATHS — AND IT IS THE ONE CANDIDATE THAT CLEARS THE 1.5 ns BAR WITH ROOM.**

| the question the brief asked | the measurement |
|---|---|
| **(1) the positive controls** | **PC-1 · PC-2 · PC-3 · PC-4 · PC-5 ALL PASS on 4 of 4 draws**, plus PC-M0–PC-M3 / PC-S1–PC-S3 offline and PC-N1 on the node identifier.  **FIVE controls MISSED first and every one was fixed as an instrument defect, never by widening a bar.**  §1 |
| **(2) where the 33.0 ns sits** | `CHAIN` **9.395** · `ANON` **9.481** · **`ROMHEAD` 5.232 (17.0 %, on 100 % of paths)** · `ARRAYMUX` 1.765 · everything else ≤ 1.9.  §3 |
| **(3) the BIU round trip's current value** | ⚠ **ZERO on every CONTROL draw — 0 of 1,200 endpoint-diverse paths carry a `|u_biu|` node**, where WAVE 5 measured 2.70–2.89 ns on 2 of 4 PRE-flattening draws.  The ONE retention draw carries it on 400 of 400 at **1.894 ns**, and with n = 1 **this wave cannot say whether that is the configuration or the draw, and does not.**  §4 |
| **(4) does `S_EA_CALC`'s `gpr_n` read still cost anything?** | **YES, 1.765 ns/path on 93.6 % of paths** (`ARRAYMUX`).  ⚠ But the **EA ADDER** itself (`Add72`, netlist fanout `ea_pair_rhs`) is **0.05–0.07 ns/path and is NOT on the binding population.**  §5 |
| **(5) the ranked candidate list** | §6.  **One candidate clears 1.5 ns with room: `ucrom` at 3.805 ns.**  Two more are between 1.5 and 2.4 and are *not* single RTL mechanisms. |
| **(6) the top candidate's standalone A/B** | §7 |
| **the marker rule (STEP 0)** | ⚠ **IT DOES NOT PICK A NEW MARKER.**  On the pre-landing tree and on the landed tree the rule yields the identical set **`{st_n, stop}`**.  WAVE 7's PC-3 refusal was a defect in the control's **pin selection**, not in the segmentation.  §2 |

---

## §1 E-1 / H-1 — **THE POSITIVE CONTROLS.  REPORTED FIRST.**

### 1.1 THE STA's OWN CONTROLS, PER DRAW

| draw | PC-1 resolver | PC-2 walker | PC-3 segmenter | PC-4 BIU | PC-5 ROM head | |
|---|---|---|---|---|---|---|
| CONTROL seed 1 | PASS | PASS | PASS | PASS | PASS | |
| CONTROL seed 2 | PASS | PASS | PASS | PASS | PASS | |
| CONTROL seed 3 | PASS | PASS | PASS | PASS | PASS | |
| RETENTION seed 1 ⧉ | PASS | PASS | PASS | PASS | PASS | |

**H-1 IS MET.**  What each one demonstrated on this netlist, not by citation:

* **PC-1 the resolver** — `-through` a **`get_pins`** collection of one node returns **1** path; the **`get_nodes`** collection of the SAME node returns **0**.  WAVE 1 §0.2, re-demonstrated live on every draw.
* **PC-2 the walker** — reached the DEST phase on all four and **reproduced Quartus's own `-data_delay` to 0.000 ns** on every draw.
* **PC-3 the segmenter, RE-BASED** — a path forced through **ONE NAMED** marker pin reports ≥ 1 boundary; the same path under a marker that does not exist reports 0.  **And the pin census is printed for every marker INCLUDING the zeros**: `st_n` **43**, `stop` **9**, **`st_zero_ok` 0** — the name WAVE 5 cut on, printed beside them as a *named known-absent control* so WAVE 7's condition stays visible instead of becoming invisible.
* **PC-4 the BIU matcher** — a path forced through **one named pin** (`…|u_biu|q_ripe_lead_n~5|combout`) carries **10** BIU nodes; the same path under WAVE 4 §6.1's known-wrong `v30u_biu:` TYPE prefix carries **0**; and the **BULK** `-through` of 1,227 pins is printed beside it and reads **8**.
* **PC-5 the ROM-head matcher** (new) — same shape: one named `|u_ucrom|` pin gives **10** ROM nodes, the bulk form is printed beside it.

⚠ **A BULK FIGURE BELOW THE SINGLE-PIN FIGURE IS `-through` BEING ACCEPTED AND
IGNORED** (WAVE 5 §1.1).  It is printed on every draw and relied on never.

### 1.2 THE SOURCE MAP's OWN CONTROLS, OFFLINE

| control | verdict |
|---|---|
| **PC-M0** `chain_srcmap` still recovers 33 arms / 24 guarded / 9 == `st_zero_ok` | **PASS** |
| **PC-M1** the marker rule gives `{st_n, stop}` on the pre-landing tree **and** the landed tree | **PASS** |
| **PC-M2a** boundary COUNT identical to WAVE 5's marker set on **4 of 4** committed pre-landing draws | **PASS** |
| **PC-M2b** with the `st_zero_ok` points DELETED from the stream, the two marker sets give **byte-identical** segmentations | **PASS** |
| **PC-M2c** ⚠ **THE ORIGINAL BAR, STILL COMPUTED AND STILL PRINTED** | raw-stream segmentations identical on **2 of 4**; max \|Δcut\| **1.135 ns** = one `st_zero_ok` cell |
| **PC-M3** a marker that does not exist gives **0** boundaries | **PASS** |
| **PC-S1** the STAGE rule reproduces WAVE 5 §5(a)'s FRONT-END / CHAINABLE partition on **10 of 10** names — from the SOURCE where WAVE 5 got it from the NETLIST copy census | **PASS** |
| **PC-S2** an invented signal classifies `UNMAPPED` | **PASS** |
| **PC-S3** the `BIU` / `ROMHEAD` / `OUTSIDE` hierarchy overrides fire | **PASS** |
| **PC-N1** the node identifier: a name that exists returns ≥ 1 LUT with ≥ 1 fanin; `zzz_no_such_node` returns 0 | **PASS** |

### 1.3 ⚠⚠ **FIVE CONTROLS MISSED FIRST.  EVERY ONE WAS FIXED AS AN INSTRUMENT DEFECT AND NONE BY WIDENING A BAR.**

This is the sixth wave in a row in which a control caught its own instrument,
so they are itemised rather than summarised.

1. **PC-M2's first form** — *"identical to the thousandth on the raw stream"* —
   was authored, run, and **MISSED on 2 of 4 draws, before any Quartus stage of
   this wave existed.**  Diagnosed to ONE NAMED CELL: an `st_zero_ok` LUT
   sitting immediately after the last `st_n` of a marker run
   (`st_n~85|combout` 44.585 → `st_zero_ok~6|combout` 45.267 on seed 2), which
   WAVE 5's set swallows into the boundary run and the rule's set does not.
   Restated as M2a/M2b/M2c — **and the original form is still computed and
   still printed on every run**, because a bar that is replaced silently is a
   bar that was softened.
2. **PC-S1 reported `sigma` UNMAPPED.**  The ASSIGN_RE inherited from
   `chain_srcmap.py` matches PROCEDURAL targets only, and `v30u_eu.sv`'s front
   end is mostly `wire [15:0] x = …` and `assign x = …`.  Both forms added.
3. **PC-S1 reported `opc_base` and `m_kind` in the pin-pipeline section.**  The
   chain writes `opc_base_n`; Quartus names the cone after the FLOP.  The `_n`
   shadow is the module's own declared naming law (`v30u_eu.sv`, *THE
   NEXT-STATE SHADOW*: *"One `_n` per state register"*) and is now a clause.
4. **PC-N1 read 0 LUTs for `ucrom`, a name with 612 of them** — the pattern
   `*|u_eu|<name>~*|combout` cannot reach a node one hierarchy level deeper,
   and `ucrom`'s LUTs live at `…|u_eu|u_ucrom|ucrom~157|combout`.
5. **PC-N1 read 0 LUTs for `Add57`** — a carry chain's output pin is
   `cout`/`sumout`, **not `combout`**.

Every one is recorded in the code beside the line that fixes it.

### 1.4 THE CONFIGURATION CHECKS — ALL POSITIVE, NONE ASSUMED

* **The multicycle deletion reached the compiler**: `sta_truefmax_probe.tcl`'s
  `SAME` class measures **k = 1.0000 on all four draws**.
* **The seed reached the fitter**, read back from Quartus's own *Fitter Initial
  Placement Seed* row: 1 / 2 / 3 / 1, as asked.
* ⚠ **AND THE THREE CONTROL DRAWS REPRODUCE WAVE 7's G-6 SWEEP TO THE
  THOUSANDTH, THROUGH A DIFFERENT DRIVER** — `SAME` T_min **34.220 · 35.313 ·
  34.461** against `chainflat_landing_results_2026-09-09.md` §6.2's per-seed
  slacks **−2.970 · −4.063 · −3.211** (`T = 31.250 − slack`).  **That is the
  control that this anatomy is measuring the same tree the scoreboard is.**

---

## §2 STEP 0 / H-2 — **THE MARKER RULE, AND IT DOES NOT PICK A NEW MARKER**

WAVE 7 recorded that *choosing a marker after seeing the refusal is
fitting-shaped* and deliberately did not choose one.  The rule, committed at
`05211a1959` before the tool was run against the post-flattening netlist:

> A base name is a **CHAIN-POSITION BOUNDARY MARKER** iff it is **(i)** READ by
> a chain position's ENTRY GUARD in `v30u_eu.sv`'s chain pass **AND**
> **(ii)** ASSIGNED inside a chain ARM BODY.

Clause (i) is what makes it a boundary; clause (ii) is what makes it
**loop-carried** — a name a guard reads but no arm writes is an INPUT to the
whole pass, not a carrier between positions.

| tree | guards read | arm-assigned → **MARKERS** |
|---|---|---|
| **PRE**-landing `aba01feb07` | `chain` `cp_seen` `d0` `st_n` `st_zero_ok` `stop` | **`st_n` `stop`** |
| **POST**-landing (worktree) | the nine `S_*` constants, `st_n`, `st_zero_ok`, `stop` | **`st_n` `stop`** |

> ### **THE SAME SET ON BOTH TREES.  WAVE 5's SET WAS `{st_n, stop}` PLUS ONE NAME THAT WAS NEVER A CARRIER.**
>
> `st_zero_ok` is a **function**; no arm assigns it.  WAVE 7's PC-3 refusal was
> a defect in the control's **PIN SELECTION** — it forced its path through an
> `st_zero_ok` pin *specifically* — and not in the segmentation.  The repair is
> WAVE 5's own PC-4 repair pattern applied to PC-3: try each marker's pins ONE
> AT A TIME, NAME the pin that answered, print every marker's pin count
> INCLUDING the zeros.

**AND THE CLAIM IS FALSIFIABLE, WHICH IS PC-M2b**: on WAVE 7's committed
pre-landing arrival points, deleting the `st_zero_ok` points from the stream
makes the two marker sets give **byte-identical** segmentations on all four
draws.  On the landed tree the question is moot: **`st_zero_ok` has 0 pins.**

---

## §3 DELIVERABLE B — **THE POPULATION CENSUS.  H-3 MET, AND REPORTED SPLIT.**

400 endpoint-diverse paths per draw (`-nworst 1`), **1,600 paths**.  Reported
STRICT (Quartus's own synthesised names read `ANON`) and again CARRY-FORWARD
(each `ANON` point attributed to the next NAMED point downstream) — **the
carry-forward is a READING and says so on every line it appears on.**

### 3.1 THE WORST ARC, PER DRAW

| draw | arc ns | levels | chain boundaries | `SAME` k / T_min | endpoints |
|---|---:|---:|---:|---|---|
| CONTROL seed 1 | **32.549** | 29 | 1 | 1.0000 / 34.220 | `ucdecode` M10K → `ucdecode` M10K addr reg |
| CONTROL seed 2 | **33.669** | 31 | 2 | 1.0000 / 35.313 | same shape |
| CONTROL seed 3 | **32.744** | 31 | 1 | 1.0000 / 34.461 | same shape |
| RETENTION seed 1 ⧉ | **32.916** | 32 | 2 | 1.0000 / 34.552 | same shape |
| | **mean 32.969** | | | | **spread 1.120** |

⧉ **THE RETENTION DRAW IS A CROSS-CHECK AND IS NOT THE SOURCE OF ANY
CONCLUSION IN THIS DOCUMENT** — except where §4 says so explicitly, and there
it is reported as a single draw and nothing is concluded from it.

⚠ **THE ARC IS A LOOP AND IT CLOSES ON THE MICROCODE TABLE ON EVERY DRAW.**  It
launches inside the `ucdecode` M10K and lands on the `ucdecode` M10K's own
port-A address register.  On seed 1, **19 of the 20 worst endpoint-diverse
paths run `ram_block1aN → ram_block1aM`** — the binding population is one loop
shape repeated.

### 3.2 THE CENSUS, CROSS-DRAW (H-3: TREE property vs DRAW property)

| stage | mean ns/path (min..max) | % of arc | presence |
|---|---|---:|---:|
| `ANON` | 9.481 (7.704..10.844) | 30.9 % | 100.0 % |
| `CHAIN` | 9.395 (6.417..10.565) | 30.6 % | 100.0 % |
| **`ROMHEAD`** | **5.232 (4.834..5.736)** | **17.0 %** | **100.0 %** |
| `BIU` | 1.894 — **see §4** | 6.2 % | 1 draw of 4 |
| `ARRAYMUX` | 1.765 (1.320..2.012) | 5.8 % | 93.6 % |
| `THE ROW'S OWN TRANSFERS` | 1.693 | 5.6 % | 1 draw of 4 |
| `THE MICRO-ROW STANDING ON upc` | 1.126 (0.228..2.177) | 3.7 % | 67.7 % |
| `STALLS (the five named wires)` | 0.869 (0.134..1.604) | 2.8 % | 47.1 % |
| `COMBINATIONAL OUTPUTS` | 0.744 | 2.4 % | 65.8 % |
| `AMBIG` | 0.677 | 2.2 % | 86.5 % |
| `(g) THE PIN PIPELINES` | 0.638 (0.425..0.763) | 2.1 % | 36.9 % |
| `THE ALU` | 0.360 (0.023..0.753) | 1.2 % | 43.6 % |
| `UNMAPPED` | 0.114 | 0.4 % | 17.8 % |

**WHAT IS A TREE PROPERTY**: the arc (spread 1.120 ns), the endpoints (the
microcode loop on 4 of 4), **`ROMHEAD` (4.834–5.736, on 100 % of 1,600
paths)**, `CHAIN`'s total, and `ARRAYMUX`'s presence rate.
**WHAT IS A DRAW PROPERTY**: the boundary count (1 · 2 · 1 · 2), the individual
segment spans, which `Mux<N>` opens a segment, and — **loudly — whether the BIU
round trip is on the arc at all.**

⚠ **25–36 % OF EVERY ARC CARRIES NO RTL IDENTIFIER.**  That is a real limit of
the instrument, reported as a percentage on every census, never hidden.

---

## §4 DELIVERABLE C — **THE BIU ROUND TRIP.  ZERO ON EVERY CONTROL DRAW.**

`q_cnt → q_ripe_lead_n`, `r7_lint`'s own declared UNRESOLVED carrier, which
WAVE 5 measured at **2.70–2.89 ns on 2 of 4** pre-flattening draws and called
*"roughly half the remaining gap"*.

| draw | on the worst arc | paths carrying it | mean span when present | mean over ALL paths |
|---|---|---:|---:|---:|
| CONTROL seed 1 | **ABSENT** | **0 / 400** | — | **0.000** |
| CONTROL seed 2 | **ABSENT** | **0 / 400** | — | **0.000** |
| CONTROL seed 3 | **ABSENT** | **0 / 400** | — | **0.000** |
| RETENTION seed 1 ⧉ | 1.910 ns | **400 / 400** | 1.894 | 1.894 |

> ### **ON THE CONTROL CONFIGURATION IT IS WORTH 0.000 ns, ON 0 OF 1,200 ENDPOINT-DIVERSE PATHS.  IT IS NOT A CANDIDATE.**

⚠ **AND THE RETENTION DRAW IS NOT A REFUTATION OF THAT, NOR A CONFIRMATION OF
ANYTHING.**  It carries the round trip on **every** path at 1.894 ns.  That is
an all-or-nothing pattern — the fitter either put the loop through the BIU or
it did not — and **with ONE retention draw this wave cannot distinguish a
configuration effect from a draw effect, and does not try.**  WAVE 5 saw the
same all-or-nothing shape (present on 2 of 4, absent on 2 of 4) on the
pre-flattening tree, which is the reading that it is a placement outcome; that
is a READING and it is labelled one.  **The falsifier is cheap and is BOOKED,
NOT TAKEN: three more retention draws.**

⚠ **PC-4 PASSED ON ALL FOUR DRAWS**, so the absence is a measurement and not an
instrument failure: forced through one named `q_ripe_lead_n` pin the counter
returns **10 BIU nodes** on exactly the draws that report 0 on the free
population.  **Absence was made to prove itself.**

---

## §5 DELIVERABLE D — **THE SURVIVING REGISTER-FILE READ, AND THE EA ADDER**

WAVE 6 folded six register-file reads into one.  The survivor is still there.

| | mean ns/path | presence | max |
|---|---:|---:|---:|
| `ARRAYMUX` (`gpr` / `sreg` / `tmps` read mux) | **1.765** (1.320..2.012) | **93.6 %** | 3.464 |

⚠ **THE EA ADDER IS NOT ON THE BINDING POPULATION.**  `Add72` — identified from
the netlist by its fanout, `ea_pair_rhs` — is **0.05–0.07 ns/path**.  The
`ARRAYMUX` cost is the row's **operand** read (`s1_val` / `s2_val`'s
`gpr[…]` / `sreg[…]` case), not the effective-address add.  **§9.2 of WAVE 5
named `S_EA_CALC`'s eight-way `gpr_n` read as "the one repeated cost with a
single named cause"; after the fold the READ survives at 1.765 ns and the ADD
does not appear at all.**

---

## §6 STEP 2 — **THE RANKED CANDIDATE LIST.  RANKED BY MEASURED ns.**

Cross-draw over **1,600 endpoint-diverse paths**, four draws.  The admission
test of the pre-registration §3 was applied **before** ranking and its
exclusions are printed.

| # | mechanism | **measured mean ns/path** | min..max | presence | admitted? |
|---:|---|---:|---|---:|---|
| **1** | **`ucrom` — the 612-LUT COMBINATIONAL microcode ROM read** (`v30u_ucrom.sv`, `assign rom_word = ucrom[rom_addr]`) | **3.805** | 3.386..4.357 | **100.0 %** | **YES** |
| 2 | `always6` — the loader / ModR-M decode cone (87 LUTs; netlist fanin `ld_b`, `ld_rm`, `ld_page`, `ld_pla`, `opc_sel`, `opc_base`, `rowq`) | 2.319 | 1.724..2.686 | 96.9 % | ⚠ **NO — not a single named RTL mechanism** (clause 1) |
| 3 | `st_n` — the chain's own next state | 1.780 | 1.077..2.885 | 100.0 % | ⚠ **NO — this is the chain, and WAVE 7 has just taken 33 % of the EU's area out of it** |
| 4 | `ld_b_n` — the loaded byte | 1.681 | 1.392..2.044 | 93.7 % | ⚠ NO — same |
| 5 | **the REP/LOOP decrement-and-test** — `Add57` 1.533 + `Equal243` 0.820 + `Equal264` 0.679 | **3.032 combined** | — | 75 / 54 / 79 % | ⚠ **PARTIAL — see 6.2** |
| 6 | `Ram9` + `Ram11` — the operand register-file read | 1.765 | 1.320..2.012 | 93.6 % | YES, but below #1 |
| 7 | `portadataout` — the `ucdecode` M10K's own clk→q | 1.046 | 1.046..1.046 | 100.0 % | ⚠ **NO — a DEVICE property, not an RTL mechanism** (clause 1) |
| 8 | the BIU round trip | **0.000** | 0.000..0.000 | **0 of 1,200 CONTROL paths** | **NO — nothing to take** |
| — | *register a microcode table output* | — | — | — | **EXCLUDED BEFORE RANKING — REFUTED-BY-WAVE-3** (prereg §0.2) |
| — | *a `ce`/`ce_half` phase split* | — | — | — | **EXCLUDED BEFORE RANKING** — WAVE 2 and WAVE 4 both RED, WAVE 5 §9.1 measured why |

### 6.1 WHY #1 IS #1, IN ONE SENTENCE, AND IT IS AN ASYMMETRY AND NOT A GUESS

> **`ucdecode` is 8,192 × 12 = 98,304 bits and costs 1.046 ns because it is in
> M10K with a REGISTERED ADDRESS.  `ucrom` is 1,028 × 29 = 29,812 bits and
> costs 3.805 ns because it is in LUTs — and it is in LUTs because its address
> `{dec_bank, upc_loc[1:0]}` is not available until 1.046 ns into the clock,
> `dec_bank` being the other table's output.  THE TWO LOOKUPS ARE IN SERIES
> INSIDE ONE CLOCK.**

**That is read off the netlist, not argued**: `sta_node_id.tcl` reports
`ucrom` = **612 LUTs** whose ONLY register-level fanin is the `ucdecode` M10K
blocks `ram_block1a0…1a8` **and `upc_loc`** — exactly
`rom_addr = {dec_bank, upc_loc[1:0]}`, and nothing else.

### 6.2 ⚠ #5 IS IDENTIFIED BUT NOT PROVEN, AND IT IS REPORTED AS SUCH

`Add57` is a **31-LUT carry chain** whose nearest NAMED predecessor is `v1`
(the row's Source-1 value) on ~100 % of its occurrences and whose nearest NAMED
successor is the chain's `stop` / `st_n`.  `Equal243` and `Equal264` sit in the
same cone with the same neighbours.  **Every 16-bit `- 16'd1` in the entire EU
is the REP/LOOP counter** — `v30u_eu_cond.svh:23,33` and
`v30u_eu_step.svh:381,382` — and `v30u_eu_cond.svh:24` is
`taken = (count_n != 16'd0)`, with `count_n = v1` written by `wd1.svh`'s
`5'd17` arm.  **The identification is strong and it is NOT PROVEN**: the netlist
gave `Add57` no register-level neighbours at all, so `sta_node_id.tcl` could
not close it.  It is **BOOKED, NOT OPENED.**

### 6.3 THE REGISTERED STOP CONDITION — **NOT TRIGGERED**

The pre-registration said: *"if no admitted candidate is worth ≥ 1.5 ns, the
wave SAYS SO AND STOPS AT STEP 2."*  **The top admitted candidate is worth
3.805 ns — 2.5× the bar — so the wave proceeds to STEP 3.  The bar was not
lowered and nothing was promoted by lowering it.**

---

## §7 STEP 3 — **THE STANDALONE A/B: `ucflat`**

**THE ARM, and it is ONE substitution**: compose the two build-time tables into
ONE, indexed by the full 15-bit micro-address `{upc_page, upc_opc, upc_loc}`,
read through **the same single register that exists today**.

```
  TODAY   dec_addr_next -> [ucdecode M10K, registered address] -> dec_bank
                        -> {dec_bank, upc_loc[1:0]} -> [ucrom, 612 LUTs] -> row
  ARM     uaddr_next    -> [ucflat  M10K, registered address] -> {valid, row}
```

### 7.1 ⚠⚠ **IT IS NOT WAVE 3's REFUTED MOVE, AND THE DIFFERENCE IS COUNTABLE**

WAVE 3 **ADDED** a second register, `row_q`, beside the existing `dec_q`, and
its own bar **L-8 fired**: the NEW `upc → ucdecode → ucrom → row_q` D-pin class
BOUND on 3 of 10 draws.

**THIS ARM ADDS NO REGISTER.**  `flat_q` **REPLACES** `dec_q` one for one, so
the loop still contains exactly ONE register and **no new D-pin class can
appear** — the one that exists (`dec_addr_next` → the `ucdecode` M10K's address
register) becomes (`uaddr_next` → the `ucflat` M10K's address register), **two
bits wider and otherwise identical**.  The pre-registration §0.2 excludes
*"register a microcode table output"*; this registers nothing new.

The correctness argument is **L1's own**, extended from two bits of `upc_loc`
to four: `v30u_eu.sv`'s MICRO-ROW header says the decode of the micro-address
the bank is *about to commit* may be read on the edge that commits it, because
`dec_addr_next` is character for character the selection the bank applies to
`upc_*`.  `uaddr_next` is that same selection over all four `upc_loc` bits.
The `srst` mirroring arm is carried over verbatim.

### 7.2 THE COMPOSITION IS CHECKED, NOT ASSERTED

| | |
|---|---:|
| entries | 32,768 |
| valid entries | **6,624** = 4 × the 1,656 valid decodes |
| distinct row words | 505 |
| **self-check, by an index derivation DELIBERATELY DIFFERENT from the write loop's** | **32,768 checked / 0 bad** |

⚠ **F44's OWN PROBE FIRED DURING BRING-UP.**  The first form of the arm's
module kept the shipped `hdl/rtl/ucore/` `HEXDIR`, could not find
`ucflat.hex`, and **`$fatal`'d — instead of running with an all-zero ROM and a
compile that succeeds**, which is exactly the failure mode F44 exists for.  The
arm now carries its own `HEXDIR` and **`hdl/` is never written** (bar H-5).

### 7.3 **THE EQUIVALENCE GATE — MET.  NO DELAY FIGURE WAS QUOTED BEFORE IT PASSED.**

| | REF | **ARM `ucflat`** |
|---|---|---|
| `check_core --core ucore --opcodes all --cases 0` | **169,000 / 169,000** | **169,000 / 169,000** |
| `tb_chain_lfsr` seed 1 | `1d01c9b269ffaa94` | **`1d01c9b269ffaa94`** |
| seed 2 | `b39b040a98b28e5d` | **`b39b040a98b28e5d`** |
| seed 3 | `0997b773cd99c030` | **`0997b773cd99c030`** |
| seed 4 | `d05b6c3c3d9fbe78` | **`d05b6c3c3d9fbe78`** |
| `CHAIN_DEPTH_MAX` | 6 · 6 · 6 · 6 | 6 · 6 · 6 · 6 |

**PC-E0 PASS.**  ⚠ And those four signatures are **the same four WAVE 6 and
WAVE 7 published**, which is a third independent agreement.

### 7.4 THE POSITIVE CONTROL — **MET, AND IT IS STRONGER THAN REGISTERED**

The pre-registration required the REF arm's mean worst reg→reg data delay to
land within **±15 %** of this wave's own in-situ no-exception `ce → ce` arc
mean, with both printed side by side.

| | ns |
|---|---:|
| **in-situ**, no-exception `ce → ce` arc, 4 draws | **32.969** |
| **REF arm**, standalone, 5 seeds | **34.693** |
| **difference** | **+5.2 %** — inside ±15 %, **MET** |

⚠ **AND A SECOND CONTROL NOBODY REGISTERED, WHICH IS THE SHARPEST ONE HERE.**
This wave's REF arm is WAVE 6's FLAT arm — WAVE 7 landed exactly that tree —
and the harness reproduces it **to the thousandth on every seed**:

| seed | WAVE 6 FLAT | **WAVE 8 REF** | ALMs, WAVE 6 | **ALMs, WAVE 8** |
|---|---:|---:|---:|---:|
| 1 | 33.498 | **33.498** | 5,399 | **5,399** |
| 2 | 34.999 | **34.999** | 5,416 | **5,416** |
| 3 | 35.118 | **35.118** | 5,407 | **5,407** |
| 4 | 34.963 | **34.963** | 5,383 | **5,383** |
| 5 | 34.889 | **34.889** | 5,404 | **5,404** |
| registers | 807 | **807** | | |

**Five delays and five area figures byte-identical across two waves, two
harness invocations and a day.**

### 7.5 **THE COMPARISON — AND IT REFUTES THE CENSUS'S NAIVE READING**

MAP ONCE PER PROJECT, FIT ONCE PER SEED, **five seeds each**, identically
compiled, no `set_multicycle_path`, 31.250 ns.

| draw | REF data ns | **ARM `ucflat`** | delta |
|---|---:|---:|---:|
| seed 1 | 33.498 | **34.269** | **+0.771** ⚠ |
| seed 2 | 34.999 | **33.646** | −1.353 |
| seed 3 | 35.118 | **33.272** | −1.846 |
| seed 4 | 34.963 | **34.372** | −0.591 |
| seed 5 | 34.889 | **34.687** | −0.202 |
| **mean** | **34.693** | **34.049** | **−0.644** |
| spread | 1.620 | 1.415 | |
| **`worst-of-5`** | 35.118 | **34.687** | **−0.431** |

> ## ⚠ **THE MEASURED DELTA IS −0.644 ns (−1.9 %), THE STANDARD ERROR OF THAT MEAN IS ±0.455 ns, AND THE SIGN IS NOT CONSISTENT — ONE SEED OF FIVE GOT WORSE BY 0.771 ns.**
>
> **The census attributed 3.805 ns to `ucrom`.  Building it recovers 0.644.
> THE CENSUS OVERSTATES THE ACHIEVABLE SAVING BY 5.9×.**

**AREA AND MEMORY, the price:**

| | REF | ARM | delta |
|---|---:|---:|---:|
| fitted ALMs | 5,383 – 5,416 | **4,856 – 4,882** | **−9.8 %** |
| **RAM segments** | **10** | **120** | **+110** |
| registers | 807 | 809 | +2 |

### 7.6 **WHY, MEASURED CELL FOR CELL — AND THIS IS THE WAVE'S METHOD FINDING**

The two arms' arcs begin identically and diverge at exactly one place:

```
REF  (seed 1)   M10K clk->q   1.046   ->  route 1.887
                ucrom~810     0.510
                ucrom~493     0.560       THREE LUT LEVELS  = 1.163 ns
                ucrom~130     0.093
                                           ... leaves the ROM head at 10.211

ARM  (seed 3)   M10K clk->q   1.046   ->  route 1.919
                mux2|l2_w20_n0_mux_dataout~0   0.517
                                           ONE cross-M10K OUTPUT MUX = 0.517 ns
                                           ... leaves the ROM head at  9.251
```

> ### **THREE `ucrom` LUT LEVELS (1.163 ns) BECAME ONE CROSS-M10K OUTPUT MUX (0.517 ns).  THE SAVING IS 0.646 ns AND THE MEASURED MEAN DELTA IS −0.644 ns.  THEY ARE THE SAME NUMBER.**

**AND THE REST OF THE ROM HEAD IS UNTOUCHED AND UNTOUCHABLE BY RTL**: the M10K's
own **clk→q is 1.046 ns on BOTH arms on every draw**, and the **~1.9 ns of
interconnect leaving the memory block** is on both arms too.  A 983,040-bit ROM
needs **120 M10K segments** and 120 segments need muxing, so the flattening does
not remove the lookup's cost — **it moves it.**

> ## ⚠⚠ **THE METHOD FINDING, AND IT IS A WARNING FOR EVERY RANKED LIST THIS CAMPAIGN PRODUCES**
>
> **A PER-NAME ns FIGURE IN AN ARRIVAL-POINT CENSUS INCLUDES THE INTERCONNECT
> *INTO* THAT NAME'S CELLS, AND INTERCONNECT IS NOT REMOVED BY REMOVING THE
> CELLS — IT IS INHERITED BY WHATEVER REPLACES THEM.**  `ucrom`'s 3.805 ns is
> 1.2 ns of LUT and 2.6 ns of routing; only the LUT half was ever available, and
> even that came back as a 0.5 ns mux.  **A census RANKS candidates.  It does
> not SIZE them.  Only a built A/B sizes one** — which is exactly why the
> pre-registration required STEP 3 before anything could be proposed.
>
> This sits beside WAVE 6/WAVE 7's finding rather than contradicting it: *a
> DIFFERENCE between two identically-compiled builds transfers* (0.2 %) — and
> this wave measures a **second** thing, that *an ATTRIBUTED SHARE of an uncut
> arc is not a difference and does not transfer* (5.9× here, +11.3…+20.0 ns in
> WAVE 5).

### 7.7 ⚠ **WHAT THIS A/B DOES NOT ESTABLISH**

1. **THE −0.644 ns IS OUT OF CONTEXT AND ITS TRANSFER IS UNVALIDATED FOR THIS
   CLASS OF CHANGE.**  WAVE 6's harness predicted an in-design delta to **0.2 %**
   — but that change was a pure combinational re-association with the front end
   byte-identical between arms.  **This one moves 983,040 bits into block RAM in
   a design that already uses 221 RAM segments**, and placement and congestion
   for +110 segments are precisely what a standalone project cannot model.
   **WAVE 5's +11.3 … +20.0 ns is the other end of that band and is quoted here
   for exactly that reason (H-4).**
2. **IT IS NOT AN Fmax CLAIM.**  No receipt was written; `standing_gates.md` §A
   governs; five draws are five draws.
3. **THE DELTA IS NOT STATISTICALLY DISTINGUISHABLE FROM ZERO** on five paired
   seeds (mean −0.644, SEM 0.455, one seed of five positive).  It is reported as
   what it is.
4. **NOTHING WAS LANDED** and no `ss_lint` / `r7_lint` / ladder leg was run on
   the arm, because a prototype that is not proposed does not need them.  The
   arm's `flat_q` is 30 bits where `dec_q` is 10, so a landing would owe the
   save-state whitelist an entry and the flop census a re-measurement.

### 7.8 F44, PROVED POSITIVELY

⚠ **THE DRIVER'S OWN `hex_loaded` FIELD READ `false` ON EVERY ARM DRAW, AND IT
WAS A REPORTING DEFECT THAT LOOKED EXACTLY LIKE THE FAILURE IT EXISTS TO
CATCH.**  `parse_reports` searched the map report for the literal string
`ucrom.hex`; the arm's table is `ucflat.hex`.  **Nothing was quoted until the
load was proved by other means**, and the check now reads the compiler's own
inferred-memory record instead of a filename.

**THE POSITIVE PROOF, from Quartus's own reports:**

| | |
|---|---|
| inferred instance | `v30u_ucrom:u_ucrom\|altsyncram:ucflat_rtl_0` |
| `OPERATION_MODE` / `WIDTHAD_A` / `NUMWORDS_A` | **ROM / 15 / 32768** |
| `INIT_FILE` | `db/cf.ram0_v30u_ucrom_f358d0ef.hdl.mif` |
| the MIF itself | `WIDTH=30; DEPTH=32768;` with **exactly 6,624 non-zero words** |
| RAM segments | REF **10** → ARM **120** |

**6,624 is the composer's own count of valid entries, to the entry.**  An
all-zero table cannot produce a 983,040-bit inferred ROM with 6,624 non-zero
initialisation words.

⚠ **AND 32,768 `Warning (10230)` TRUNCATION WARNINGS** — the generator writes
eight hex digits into a 30-bit array, which is the same class the shipped
`v30u_ucrom.sv` header already documents for `ucdecode`'s 12-bit-for-10-bit
file.  Harmless, and recorded rather than tidied away.

---

## §8 THE BARS, SCORED

| bar | verdict |
|---|---|
| **H-1** every classifier carries a positive control, reported FIRST; a miss VOIDS the wave; single-pin `-through` with the bulk form printed beside it | **MET.**  PC-1…PC-5 PASS on 4 of 4 draws; PC-M0–M3, PC-S1–S3, PC-N1, PC-E0 and the A/B's registered positive control all PASS.  **Every `-through` is ONE PIN, the pin that answered is NAMED, and the bulk form is printed** (PC-4: 10 single-pin vs 8 bulk).  ⚠ **FIVE controls MISSED first and every one was fixed as an instrument defect** — §1.3 |
| **H-2** the marker rule is COMMITTED BEFORE the tool is run against the post-flattening netlist | **MET at `05211a1959`**, before any Quartus stage.  **And the rule does not pick a new marker**: `{st_n, stop}` on the pre-landing tree and on the landed tree alike.  §2 |
| **H-3** the anatomy is over a POPULATION and across seeds, with the tree-property / draw-property split stated | **MET.**  1,600 endpoint-diverse paths, 4 draws, STRICT and CARRY-FORWARD, and the split is stated in §3.2 — **including the loudest instance of it, the BIU round trip.** |
| **H-4** every candidate's figure carries its uncertainty, and a standalone figure carries the out-of-context caveat with WAVE 6's 0.2 % and WAVE 5's +11.3…+20.0 ns | **MET.**  Every row of §6 carries min..max and presence; §7.5 carries the SEM and the inconsistent sign; §7.7 quotes both bands |
| **H-5** `git status --porcelain hdl/` shows NO tracked modification at start and end; SDC reverted; A/B arms OUTSIDE `hdl/rtl/ucore/` | **MET.**  Clean at both ends; the driver's `finally` printed `hdl/ restored: CLEAN`; both arms live in `~/.cache/ucsimt-tmp/wave8/` and **`hdl/` was never written by the harness** |
| **H-6** NOTHING IS LANDED IN THE CORE; the wave ends with a ranked list and at most one prototype delta | **MET.**  `git diff 8deb1e7d8e -- hdl/` is EMPTY.  One ranked list (§6), **one** prototype delta (§7) |

### 8.1 THE SENTENCE THE WAVE OWES

> **The front end's 33.0 ns arc is a LOOP that closes on the microcode table on
> every draw.  Its largest NAMED piece is the `ucrom` read at 3.805 ns on 100 %
> of 1,600 paths — and when that piece is actually built away, by composing the
> two build-time tables into one M10K lookup that adds no register, it is worth
> −0.644 ± 0.455 ns, about 11 % of the remaining 5.7 ns, for +110 M10K
> segments, with the sign inconsistent across five seeds.  The reason is
> measured and it is general: three LUT levels became one cross-M10K output
> mux, and the 1.046 ns of M10K clk→q and ~1.9 ns of interconnect leaving the
> memory — three quarters of the ROM head — are the same on both arms and are
> not an RTL question at all.  THE BIU ROUND TRIP, which WAVE 5 called roughly
> half the gap, is worth 0.000 ns on 0 of 1,200 CONTROL paths.  This wave does
> not propose landing anything.**

### 8.2 WHAT IS OWED, AND WHAT IS BOOKED RATHER THAN TAKEN

1. ⚠ **THE FABRIC CONFIRMATION.  NOTHING HAS BEEN ON A BOARD SINCE WAVE 7
   CHANGED THE EU's DECODE.**  Every fabric figure in this repo was taken on
   **FLASH #21 or earlier** and **may not be quoted against this tree**.
   Recorded as owed, deliberately not discharged: the brief is OFFLINE ONLY.
2. **THE BIU ROUND TRIP's ONE RETENTION DRAW.**  It is on 400/400 paths there
   and 0/1,200 on CONTROL.  **Three more retention draws would say whether that
   is the configuration or the placement.**  BOOKED, NOT TAKEN — taking it after
   seeing one draw is choosing a population after seeing a result.
3. **`Add57`'s IDENTIFICATION.**  Strong (every 16-bit `- 16'd1` in the EU is
   the REP/LOOP counter) and **not proven** (`sta_node_id.tcl` found it no
   register-level neighbours).  BOOKED.
4. **THE `ucflat` ARM IS NOT CONDEMNED, IT IS SIZED.**  If a later wave finds
   3 ns elsewhere and needs the last 0.6, it is measured, it is equivalence-
   gated at 169,000/169,000 with four byte-identical signatures, and its price
   is +110 M10K segments.  **It re-opens on evidence that the design's memory
   budget can carry it AND that the remaining gap is within 0.6 ns of closing.**

---

## §9 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**  No
  Codex.  No nested subagent.
* Single-writer guard by EXACT binary name before every Quartus stage;
  `hdl/nec_test_ucore.qsf` `git checkout --`'d after every group (the declared
  §70.7 exemption); `hdl/` verified clean after every group.
* The anatomy's no-exception legs patch `hdl/nec_test.sdc` for the duration and
  restore it in a `finally`; **no custom SDC rule was added, and the USER RULING
  of 2026-09-08 was not re-opened.**  The A/B's SDC is the harness's own and
  `hdl/nec_test.sdc` was never opened by it.
* `~/.cache/ucsimt-tmp/wave8/` for every intermediate; nothing large in `/tmp`.
* **`git add -A` was never used** — every path was added by name, and the ~18
  pre-existing modified files in the working tree that are NOT this wave's were
  left untouched.
* **A number with no artifact id is not quotable.**  Every figure above is in
  `sw/testdata/frontend/anat/` or `sw/testdata/frontend/ucflat/`.
* **Recorded what was measured, not what was expected.**  The wave's top
  candidate was expected to be worth ~3.8 ns and is worth 0.6, and that is the
  headline.
