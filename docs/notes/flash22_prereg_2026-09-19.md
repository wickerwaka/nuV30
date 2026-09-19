# FLASH #22 — PRE-REGISTRATION: **THE FABRIC CONFIRMATION OF THE NO-SDC TIMING CAMPAIGN, AND ITS PRIMARY PREDICTION IS A NULL**

Committed **before any Quartus build and before any board contact**, together
with `sw/f22_s1_derive.py`, the S-1 derivation checker, which is **run and
proved non-vacuous below, before the board is touched**.

Flashing is authorised by the **USER, 2026-09-19, verbatim: *"Flash it."***
That authorisation is for **this** flash.  It is **not** a licence to iterate
on the board.  §9 is the stop list and it is obeyed literally.

    branch      master
    HEAD        8115b166d7
    board now   FLASH #21, nec_test_ucore.sof a84577f6499f132d…, built from
                325b2092d7 WITH X1_AD_RETENTION=1, flash_log.jsonl 24 entries
    manifest    99 declared inputs, c3305d40f62e497f…  (MEASURED at HEAD)
    hdl/        tracked-clean, and BYTE-IDENTICAL to the WAVE 17 landing
                `d3c295cdef` (`git diff --stat d3c295cdef HEAD -- hdl/` empty)

Every bar below is reported in the form it is registered in.  **Nothing is
re-registered after the fact.  A miss is a miss.**  **The null prediction means
ANY corpus movement is a FINDING TO ITEMISE, not a failure to argue away.**

---

## 0. WHAT THIS FLASH CARRIES, AND WHY THE PREDICTION IS A NULL

**FOUR STRUCTURAL CHANGES SIT BETWEEN THE TREE AND THE LAST BITSTREAM, AND NONE
OF THEM HAS EVER BEEN IN FABRIC.**

| # | wave | mechanism | commit |
|---|---|---|---|
| 1 | **WAVE 7** | the EU's **chain flattening** — the sevenfold unroll deleted, nine arm bodies in `v30u_eu_arm_<state>.svh`.  **A re-derivation of the EU's decode.** | `2ceb8c3ba3` |
| 2 | **WAVE 12** | **`build_id.v` removed** (+ bar `E11`).  **Moves the bitstream.** | `04efdc8d47` |
| 3 | **WAVE 16** | ARM-A **`qripe_presel`** — the BIU's queue port reformulated, the `q_ripe_lead_n` round trip removed. | `f174e1a24a` |
| 4 | **WAVE 17** | **the phase split** — the EU cut across `ce`/`ce_half` with a 778-bit shadow, **`CE_HALF` promoted to an UNCONDITIONAL PORT**, and **every timing exception deleted from `nec_test.sdc`.** | `1c71c4f5e3` · `a35a29c082` · `d3c295cdef` |

⚠ **THIS IS THE FIRST BITSTREAM EVER BUILT WITH NO SDC TIMING EXCEPTION.**  If
something is wrong in fabric, **that and the `CE_HALF` port change are the first
two things to suspect.**

**ALL FOUR ARE BEHAVIOUR-PRESERVING IN SIMULATION AND THAT IS ESTABLISHED IN
THE STRONGEST FORM THIS REPO HAS**, on two full ladders (WAVE 16 §1, WAVE 17
§3):

* `check_core --opcodes all --cases 0` **169,000/169,000 at `--ce-div` 2, 3, 4
  AND 8**, with div 1 REFUSED;
* **the exact 181** — `FA` 500/500 · `FB` 500/500 · `INT.FB` 200/200;
* `ulockstep --golden all --cases 50` **17,350 ALL LOCKSTEP**;
* the four **`chain_lfsr` signatures BYTE-IDENTICAL** over 1.6 M fabric clocks;
* **`fz2_replay` 305 rows × 11 fields IDENTICAL, compared BY NAME** over a
  non-zero population;
* `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 unmoved.

**SO THE PRIMARY PREDICTION OF THIS SITTING IS A NULL**, and a null is the
strongest form available here: four landings, one of which re-derives the EU's
decode and one of which re-times the EU, **none of which may move a single
seed.**

### 0.1 THE NOISE FLOOR GOVERNS EVERY AGGREGATE CLAIM

`docs/notes/fz2_capture_noise_2026-08-10.md`: **10 / 3,840 = 0.2604 %**
ledger-class flips.  FLASH #17 spent 7 · #18 spent 0 · #19 spent 6 · #20 spent
6 · #21 spent 3.

**The unregistered-flip budget for this sitting is 10 seeds.**  Because the
prediction is a null, **every flip is unregistered by construction**, and each
is itemised with tier, `escaped`, `ps3_8080` and both eras' `diverging_rows` /
`first_bad_row`.

⚠ **THE SEEDS MOST LIKELY TO MOVE, NAMED IN ADVANCE AND GIVEN NO EXTRA
BUDGET.**  Three seeds are the known-unstable class, and if anything moves this
is where the prior says it moves.  **They are inside the 10-seed budget like
everything else and no separate allowance is made for them:**

* **`fz2e/513024`** and **`fz2e/526056`** — FLASH #21's two ENTRANTS, and
  FLASH #21 §10 OPEN item 1 says they are **unattributed**: no FLASH #20
  capture was retained for either, so neither was in the population on which
  the earlier landings were measured byte-identical.
* **`fz2e/527051`** — has read **three different values in three eras**
  (1,003 → 913 → ABSENT) on a heavily `escaped` seed, and **nothing explains
  the class** (FLASH #21 §10 OPEN item 7).

⚠ **THE ESCAPED-SEED CAVEAT, STATED IN ADVANCE**: seeds carrying a large
`escaped` count reach memory the harness does not model and their row streams
are known to be less stable than the rest of the corpus.

---

## 1. ⚠⚠ **THE S-1 DERIVATION — THE ONE STRUCTURAL RISK THE SPLIT INTRODUCES.  THIS IS A PRE-FLASH GATE (`D-1` … `D-4`).**

**THE HAZARD, STATED PLAINLY.**  Clause **S-1** of the ce/ce_half contract is
*"at least one `CE_HALF` falls between consecutive `CE`s"*.  **Before the phase
split, violating S-1 left the address on AD for a write cycle** — a pin defect
on a muxed bus.  **After the split, violating S-1 means the EU consumes a STALE
STAGE-1 SHADOW and computes the wrong next state** — a functional failure.
`v30_core.sv:283-292` `$fatal`s on it, **but the whole block is `ifndef
SYNTHESIS`, so FABRIC HAS NO ASSERTION.**  The argument must therefore be
**STRUCTURAL**, about the rig's counter, and it must be made **before the
bitstream is programmed.**

**WHAT THE RIG DOES** — `hdl/rtl/nec_bus.sv:170-190`, arithmetic verbatim:

```
reg [5:0] div_cnt;
wire [5:0] div_max = cfg_clk_div - 6'd1;
wire [5:0] half    = {1'b0, cfg_clk_div[5:1]};   // floor(D/2)
wire tick_rise  = div_cnt == div_max;            // -> CE
wire tick_fall  = div_cnt == half - 6'd1;        // -> CE_HALF
always_ff @(posedge clk)
    div_cnt <= tick_rise ? 6'd0 : div_cnt + 6'd1;
```

and `hdl/rtl/system_large.sv:513-521` wires **`CE = bus_tick_rise`,
`CE_HALF = bus_tick_fall`** — under `SYNTHESIS`, ungated (the `m10_park` gate is
`ifndef SYNTHESIS` and cannot exist in a bitstream).  **BOTH ENABLES COME OFF
ONE COUNTER**, which is why this is derivable at all.

**THE DERIVATION, IN ONE SENTENCE.**  `div_cnt` walks `0 … D-1` and is reset to
0 by `tick_rise` itself, so each CPU period is the interval `[0, D-1]`;
`tick_fall` fires at `floor(D/2) - 1` and `tick_rise` at `D - 1`, and for every
`D ≥ 2` we have `0 ≤ floor(D/2) - 1 < D - 1`, so **within every period the fall
occurs exactly once, the rise occurs exactly once, and the fall occurs STRICTLY
EARLIER** — which is C-a (never coincident) and S-1 (exactly one `CE_HALF`
between consecutive `CE`s) simultaneously.

**AT THE DIVIDER OF RECORD, `D = 8`**: `half = 4`, fall at `div_cnt == 3`, rise
at `div_cnt == 7` — **`CE_HALF` sits 4 fabric clocks after the previous `CE` and
4 clocks before the next.**

**WHAT WOULD HAPPEN IF IT DID NOT HOLD**, and the two values where it does not:

* **`D = 1`**: `half = 0`, so `half - 6'd1` **UNDERFLOWS to 63**, a count
  `div_cnt` never reaches because `tick_rise` resets it to 0 on every clock.
  **`CE` every fabric clock, `CE_HALF` never → S-1 VIOLATED**, and the EU would
  read a stage-1 shadow one CPU clock stale on every step.  *(This is exactly
  the value `check_core` refuses with the clause cited.)*
* **`D = 0`**: `div_max = 63` and `half - 1 = 63` — **the two strobes COINCIDE →
  C-a VIOLATED.**

**WHY NEITHER IS REACHABLE IN THIS SITTING**, from the artifacts and not from
recall: `nec_bus.sv:42` declares the port *"sys clocks per CPU clock, **even,
>= 4**"*; `hps_axi_slave.sv:260` **resets `cfg_clk_div` to `6'd8`**;
`sw/v30run.py:49` sets **`DIV_OF_RECORD = 8`** and `sw/fz2_w1.py:443` **PINS
`div=8` on the capture path**; and `s13_board.div_guard()` **asks the transport
what it commanded and records the answer** on every probe — an UNPINNED readback
being a rig-integrity HARD STOP (§9.5).  The only lever that could reach `D ≤ 1`
is a host write of `cfg_clk_div`, and `div_guard` is the instrument that would
see it.

| # | bar |
|---|---|
| **D-1** | `python3 sw/f22_s1_derive.py` exits **0**: over **every `D` in [2, 63]**, `coincident == 0` and `s1_violations == 0`, and **exactly one `CE_HALF` between consecutive `CE`s** (`gap min == max == 1`) |
| **D-2** | its **NON-VACUITY NULL**: `D = 0` must FAIL on **C-a** and `D = 1` must FAIL on **S-1**.  A checker that cannot fail is not a checker |
| **D-3** | `D = 8` — the divider of record, the reset default, and the value `fz2_w1` pins — reads **CE 512 / CE_HALF 512 / coincident 0 / S-1 violations 0** over 4,096 fabric clocks |
| **D-4** | **`div_guard()` PINNED on 100 % of board probes** (§9.5 is the stop) |

### 1.1 THE RESULT, MEASURED BEFORE THIS DOCUMENT WAS COMMITTED

```
  ALL D in [2, 63]: violations = []   -> NONE
  THE DIVIDER OF RECORD, D = 8: CE 512 / CE_HALF 512 / coincident 0 /
                                S-1 viol 0 / exactly 1-1 CE_HALF between
                                consecutive CEs
  --- NON-VACUITY (the null: these MUST fail) ---
    D = 0: coincident 64,   S-1 viol 0     -> FAILS as required (C-a)
    D = 1: coincident 0,    S-1 viol 4095  -> FAILS as required (S-1)
  S-1 DERIVATION: PASS
```

> ### **D-1, D-2 AND D-3 ARE MET BEFORE THE BOARD IS TOUCHED.  THE RIG'S ENABLE TRAIN SATISFIES S-1 STRUCTURALLY AT EVERY DIVIDER THE RIG CAN LEGALLY BE SET TO, AND IT IS SAFE TO FLASH ON THAT COUNT.**

⚠ **WHAT THIS DOES NOT SAY.**  It is an argument about the **rig's** enable
train — `nec_bus` + `system_large` — and it transfers to **no other
integrator.**  A downstream integrator whose `CE_HALF` is not derived from the
same counter must make this derivation for itself, and since the split it is a
**functional** requirement, not a pin one.  ⚠ And `nec_bus.sv` and
`hps_axi_slave.sv` are **UNCHANGED since FLASH #21** (`git diff 325b2092d7 HEAD`
is empty on both), so the train this derives is the train that was already in
the socket — **what changed is what a violation would cost.**

---

## 2. THE BUILD — G6, **ONE DRAW PER CONFIGURATION**

**Per the seeds ruling of 2026-08-13**: a landing/flash wave's compile
**VERIFIES THE BITSTREAM**; it is **not an Fmax measurement**.  Both legs are
`--seeds 1`, i.e. **`draw@seed1`**, and **no band, no spread, no worst-of-N and
no Fmax claim is made anywhere in this sitting.**  `standing_gates.md` §A
governs — one green build is not closure, and the same tree has drawn 19.42 and
45.91 MHz.

| # | bar |
|---|---|
| **E-1** | `gen_ucore_qsf --check` PASSES before each draw |
| **E-2** | 0 compile errors, every stage Successful, 0 latches, 0 `lpm_divide` |
| **E-3** | `divclk` Fmax **≥ 32.0** — **the campaign's own bar, and the only one that transfers to this tree** |
| **E-4** | worst setup slack **> 0** on every domain |
| **E-5** | **TNS 0.000, setup AND hold, every domain** |
| **E-6** | the RETENTION receipt's **DERIVED** `configuration` self-labels **`RETENTION (X1_AD_RETENTION=1)`** — derived from the reports, **never from the flag** |
| **E-7** | the CONTROL receipt's **DERIVED** `configuration` self-labels `CONTROL/DEFAULT` |
| **E-8** | the RETENTION `.rbf` **DIFFERS** from the CONTROL `.rbf` — the check that `--verilog_macro` reached the compiler |
| **E-9** | the **99-file** input manifest reads **`c3305d40f62e497f…`** on both draws |
| **E-10** | the fitter honoured `--seed=1` on **both** readings (`Info: Command:` **and** the `Fitter Initial Placement Seed` row) |
| **E-11** | **`E11_no_build_stamp` `pass` on both receipts** — `files_scanned` 99, `file_present` False, `token_hits` `{}`.  Read at receipt level, **not** from each seed's `bars` (trap #9) |
| **E-12** | both receipts committed **BY VALUE** under `sw/testdata/flash22/` |

⚠ **THE ENV-VAR FORM IS REFUSED BY DESIGN.**  `X1_AD_RETENTION=1 python3
sw/quartus_gate.py` exits 2 naming the FLASH #18 finding.  The RETENTION leg is
**`python3 sw/quartus_gate.py --seeds 1 --retention`** and nothing else, and
`--verilog_macro` is passed **unquoted** (`subprocess` has no shell).

⚠ **RETENTION IS THE SHIPPING CONFIGURATION.**  Every flashed bitstream in this
project is built `WITH X1_AD_RETENTION=1`, and **the RETENTION build is the one
that is flashed.**

### 2.1 THE EXPECTED NEIGHBOURHOOD — **REGISTERED, AND NOT A BAR**

`hdl/` is byte-identical to `d3c295cdef`, so WAVE 17's committed **seed-1**
receipts describe exactly these inputs.  WAVE 17 §6 further measured the `.rbf`
**byte-identical on 10 of 10 draws** across two trees and four days on this
manifest.  **So this is what is expected, and a differing draw is NOT a failure
of this sitting — it is `standing_gates.md` §A evidence and will be quoted as
such:**

| | expected (**NOT a bar**), from `sw/testdata/g6dist/w17-split-presel-noexc-*-n5/seed1_quartus_gate.json` |
|---|---|
| CONTROL `draw@seed1` | **34.39 MHz**, worst setup **+2.172 ns**, ALMs **8,275 / 41,910 (20 %)**, `.rbf` **`853eda3050f08b2f…`**, `.sof` `698c26d5e51cb28d…`, receipt `95e307bdcfb134e6…` |
| RETENTION `draw@seed1` | **33.64 MHz**, worst setup **+1.521 ns**, ALMs **8,250**, `.rbf` **`20fac47ef98e00fa…`**, `.sof` `055d2057a2c63dd8…`, receipt `002395d5cb618dad…` |

⚠ **THE `.sof` IS EXPECTED TO DIFFER AND THE `.rbf` IS NOT.**  WAVE 17 §6
measured that `nec_test_ucore.sof` embeds a project path and a compile
timestamp while the `.rbf` does not.  **A differing `.rbf` is a finding to
report, not a stop.**

⚠ **THE FLASH #21-ERA `≥ 38.0 MHz` STOP DOES NOT TRANSFER AND IS NOT ADOPTED.**
That number was measured on a tree whose SDC carried the CE multicycle; this
tree has **no timing exception at all** and its characterised `worst-of-5` is
**33.00 (CONTROL) / 33.20 (RETENTION)**.  Carrying the older figure across would
be exactly the error `CLAUDE.md` warns about.  **The bar is the campaign's own
32.0.**

**HARD STOP: RETENTION `draw@seed1` < 32.0 MHz, or any of E-2 / E-4 / E-5 RED
→ NOTHING IS FLASHED.**

---

## 3. **N-1 — THE M10K MICROCODE BAR**, AND **N-2 — FIRST LIGHT**

| # | bar |
|---|---|
| **N-1** | `python3 sw/ucrom_mif_check.py` **PASS on the FLASHED (RETENTION) build's own `db`** — 8192 × 12 against `ucdecode.hex` **and** 1028 × 29 against `ucrom.hex`, **every word**, an address absent from the `.mif` counting as a MISMATCH and not a skip.  ⚠ **The tool prints `FAIL` and exits 0** (FLASH #21 §2, still booked): **its verdict is read by eye, never from `$?`** |
| **N-1b** | its **non-vacuity control** in the same sitting: one flipped bit → `[BAD]`, then restored and PASS re-confirmed |
| **N-2** | **FIRST LIGHT** — `python3 sw/check_ab_hw.py all 800` **MATCH over 800 rows on all three legs** (chip-vs-golden, core-vs-chip, core-vs-golden) |

**HARD STOP: N-1 not PASS → NOTHING IS FLASHED.  N-2 missing on any leg → STOP
AND REPORT (§9).**

⚠ **WAVE 7 RE-DERIVED THE EU's DECODE, SO N-1 IS NOT A FORMALITY THIS TIME.**
The decode table's *content* is unchanged and `ucrom_mif_check` compares it word
for word against the same `.hex` files; what changed is the logic that reads it.

---

## 4. THE FLASH (`F-1`)

**`sw/safe_flash.sh` ONLY**, with its VERIFY leg, on the **RETENTION** build.

| # | bar |
|---|---|
| **F-1** | flash succeeds, **VERIFY OK**, `flash_log.jsonl` **24 → 25 entries** (**exactly one**), tail `verify: "OK"`; `.sof` and `.rbf` sha256 recorded here and in the results |

Single-writer is asked of the board **before first contact** and again inside
`preflight`; **`--force` is not used.**  `div_guard()` on every probe.  Socket
legs are **`use_core=False`, passed explicitly every time** — the board's CFG is
sticky.

---

## 5. THE CORPUS — **THE PREDICTION IS "NOTHING MOVES"** (`C-1` … `C-16`)

`fz2_w1 control` → `fz2_w1 preflight --board` → `fz2_w1 capture` →
`fz2_ledger`, scored against the FLASH #21 ledger
`sw/testdata/fz2/fz2_failure_ledger_f21_2026-08-13.json`.

Before the capture, `fz2c` and `fz2e` are archived **by rename** to
`*-F21-archive` and the manifests re-pinned by `fuzz_campaign.py new`; the F21
era's `fz2_bars` / `fz2_capture` / `fz2_control` JSONs are archived to
`*_F21-archive.json` **before** anything overwrites them.  **Nothing is
deleted.**

### 5.1 THE HEADLINE

| # | bar | **registered** |
|---|---|---|
| **C-1** | corpus identity | 960 + 2,880 = **3,840**, **48 strata**, `fz2_w1 lint` **PASS / 0 hits / 48 stratum rows** |
| **C-2** | completeness | **48 / 48 strata, every `rc 0`** |
| **C-3** | the flash pin | `distinct_eras` **1**, `absent` 0, `incomplete` 0, `build_stale` 0, every row's `era.sof_sha256` = **FLASH #22's** |
| **C-4** | ⭐ **THE HEADLINE — THE NULL** | **107 failures of a denominator of 3,838, EXACTLY.**  Tolerance: the 0.2604 % noise floor, i.e. a **band of [97, 117]**; **the POINT is 107 and a point miss is reported as a miss** |
| **C-5** | membership flips | **0 ENTERED, 0 LEFT.**  Budget **10 seeds**.  Every flip itemised |
| **C-6** | ⭐ **THE SEAT TABLE — ALL 107 SEAT-FOR-SEAT** | every FLASH #21 failure present with **the same `diverging_rows` AND the same `first_bad_row`**.  Registered as the canonical seat digest **`c79a41282d08c53a22d9752481fc0bce6c63d57823371db7fd3eeb8f67ad3264`** (derivation in Appendix A) |
| **C-7** | direction | **0 LOST** and **0 `first_bad` EARLIER** anywhere in the corpus |
| **C-8** | the row metric | Σ`diverging_rows` **103,803** · `rows_diverging` **103,742** · `rows_compared` **11,330,674** · seed match **97.2121 %** · row match **99.0844 %**.  Reported; **a delta must reconcile to ZERO unexplained rows** |
| **C-9** | discards | **2** (`fz2e/509069`, `fz2e/514037`), denominator **3,838**.  ⚠ `_ps3_8080` is a **SOCKET-leg** predicate (A-2) that **no RTL change can reach**; it has re-rolled on seven consecutive eras (2 → 2 → 3 → 1 → 3 → 1 → 2), so this is **reported with both bases and NOT barred** |
| **C-9b** | family counts | `A1` 5 · `A2` 4 · `A3` 15 · `B1` 1 · `B2` 2 · `C1` 1 · `C2` 9 · `C3` 1 · `C4` 1 · `D1` 9 · `D2` 8 · `D3` 4 · `E1` 39 · `E2` 2 · `NEW/UNCLASSIFIED` 6 = **107**; §38.9 missed-trap overlay **4** (`fz2c/406073`, `fz2c/407064`, `fz2e/518039`, `fz2e/518044`) |

### 5.2 THE NAMED NON-MOVERS — REGISTERED VALUE FOR VALUE

`diverging_rows / first_bad_row`, both columns, read from the FLASH #21 ledger:

| # | group | **registered** |
|---|---|---|
| **C-10** | KM's three | `fz2c/404041`, `fz2e/501066`, `fz2e/513019` — **ABSENT** |
| **C-11** | phantom-T1's three | `fz2c/404071` **1 / 243** · `fz2e/514044` **1 / 234** · `fz2e/516001` **1 / 583** |
| **C-12** | §64.1's four | `fz2c/405002` **840 / 527** · `fz2c/405013` **921 / 1331** · `fz2c/405072` **891 / 636** · `fz2e/512056` **984 / 1475** |
| **C-13** | W7-4's surviving two | `fz2c/410047` **3589 / 227** · `fz2e/535027` **3226 / 296** |
| **C-14** | M10's LEA-mod3 six | `fz2c/406054` **3141 / 470** · `fz2c/408019` **1087 / 1617** · `fz2e/518038` **194 / 429** · `fz2e/522019` **3075 / 396** · `fz2e/524034` **3479 / 457** · `fz2e/530001` **20 / 442**.  ⚠ `fz2e/520066` **8 / 1249** is a regression check ONLY — it SELECTED F-B′'s `eu_word` term and its own value is not evidence |
| **C-14b** | FLASH #20's two movers | `fz2c/406063` **3165 / 249** · `fz2e/528010` **7 / 1383** |
| **C-14c** | **FLASH #21's own three flippers** (§0.1) | `fz2e/513024` **991 / 703** · `fz2e/526056` **3232 / 755** · `fz2e/527051` **ABSENT** |
| **C-15** | **the falsifier** | **`fz2c/404040` stays ABSENT from the ledger** |

### 5.3 `fz2_immaterial falsify` ON THE F22 LEDGER (`C-16`)

**MEASURED ON THE F21 LEDGER BEFORE THIS DOCUMENT WAS COMMITTED**, so the
registration is a derivation and not a guess:

| # | **registered** |
|---|---|
| **C-16a** | the `IMMATERIAL` class is **22 members, COSMETIC 17 · TRANSIENT 5**, **0 entrants and 0 leavers**, working residue **85** |
| **C-16b** | the partition is **FUNCTIONAL 46 · TIMING 29 · TRANSIENT 5 · COSMETIC 17 · UNSCOREABLE 10 = 107**, `TIMING_RECONVERGED` **7** |
| **C-16c** | ⚠ **`falsify` IS REGISTERED TO *FAIL*, AT EXACTLY `G6 3 / 8` AND `G7 1 / 23`, WITH `G1 · G2 · G3 · G4 · G5 · G8` PASS.**  This is **INHERITED DOCUMENT STALENESS FROM FLASH #21** (`fz2_materiality_census` and the immaterial document are still pinned to the F20 era's 44 / 30 / 106 / 84) and it is **NOT this wave's finding and NOT repaired here** — a document edit on the day it is load-bearing is what this campaign's rules distrust.  **Registering it to PASS would be registering something I have already measured to be false** |
| **C-16d** | `fz2e/528010` COSMETIC at **7** rows; `fz2c/409065` **12** · `fz2e/521049` **10** · `fz2e/525017` **8** COSMETIC; `fz2c/408021` **22** TRANSIENT with `bs=12` |

---

## 6. THE DIRECTED-CELL SPOT-CHECKS — **REGISTERED AS OPTIONAL**

Socket legs measure **SILICON**, which no bitstream can move.  A fabric leg
measures the **synthesised core**, which four behaviour-preserving landings must
not move either.  **These are declared OPTIONAL in advance**: they are run only
if §2–§5 are clean and time permits, and **if they are not run this document
says so and no figure is inferred from their absence.**

| # | leg | registered |
|---|---|---|
| **S-1** *(opt)* | `ghost_pred_cell run` (socket) + `run --fabric` + `f20_cell` | **socket column BYTE-IDENTICAL** to the bank (a socket-column mover is a **RIG FINDING** and **outranks the cell**); **CHIP vs FABRIC 398 / 122**; **FABRIC vs CORE 528 / 528, 0 differing** |
| **S-2** *(opt)* | `tf0f_cell run --strata nop,x1b,z1b` + `score` | **0 chip-column movers** over 512 |
| **S-3** *(opt)* | restoration | every bank copied aside **before** and restored **byte-identical** by sha256; F22 rows retained **beside** them, never merged over them |

⚠ **`ghost_pred_cell core` IS NOT ON THE ARTIFACT LAYER** (FLASH #20 §8, still
booked).  **If any `core` column is re-taken, `artifact.require()` is called by
hand on both `tb_sys` legs first and the receipt ids recorded beside the
column.**

⚠ **`x1_retention` / `x1_fabric` ARE NOT RUNNABLE AND ARE NOT QUOTED**
(GEN-DRIFTED since FLASH #19), so **the 283-cell HLT sweep column does not exist
for this bitstream.**  Neither are `timed_scenario`, `timed_ins_replay`,
`timed_wvec_gate`, `timed_enter_replay`, nor the four v1 fuzz banks (SUP-1 /
D9).

---

## 7. THE ERA GUARD AND THE CLOSING CONTROL

| # | bar |
|---|---|
| **Q-1** | `fz2_replay`'s **fabric era guard MUST REFUSE at HEAD BEFORE the flash**, by name, on the `hdl/` files that postdate FLASH #21 — **a guard that passes before the flash is a guard that is not working** — and **PASS with NO bypass** after it |
| **Q-2** | closing control `fz2_replay --all-failures --pass-sample 150 --leg ret` — **agreement ≥ 99 %**, with `first_bad` **IDENTICAL** on the failures.  ⚠ Run **in the main tree**: the tool is structurally vacuous in a git worktree (`.gitignore:9`) and the **row count is printed before the verdict** |
| **Q-3** | `use_core=0` **chip proof `check_ab_hw chip 800` MATCH after everything**; **`div_guard` PINNED on 100 % of probes, 0 unpinned**; **`board_idle()` clean and LAST**; **0 transport errors** reported **with the capture count** |

---

## 8. THE STANDING GATES ON THIS ERA (`C-17`)

**Measured at HEAD before this document was committed, so they are registered
as derivations:**

| gate | registered |
|---|---|
| `ss_lint --core ucore` | **PASS — `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8**, BIU 109 + EU 122 symbols, **229 architectural flops, 4 whitelist entries, 0 UNMAPPED**.  ⚠ **This is the SPLIT tree's census and may NOT be differenced against the unsplit 228 / 3, nor against `standing_gates.md:1399`'s stale 226 / 214 / 0x8D** |
| `r7_lint` | **PASS — 0 undeclared carriers, 3 declared tainted (`eu_rd_edge`, `rd_edge_psw_take`, `rd_edge_take_raw`), 41 `stop` sites, 0 violations.**  ⚠ **41, not the 51 of the pre-WAVE-7 tree** — the chain fold deleted the rest |
| `gen_ucore_qsf --check` | **PASS** before every Quartus run |
| `test_artifact` | **45 / 45, NON-VACUOUS** |
| `fz2_w1 lint` | **PASS — 0 hits, 48 stratum rows** |
| `fz2_w1 bars` | **11 / 11 MET**, leaf-diffed against the F21 archive with any moved verdict named |
| `fz2_w1 control` (C-6 board legs) | **9 legs**, holds `[2, 20, 300]` proved on `pin_int` and `pin_nmi`, **N1 negative control PASS**, **0 unpinned** |
| `fz2_w1 preflight --board` | **OK** — single writer, era pinned to FLASH #22's receipt **self-labelling RETENTION**, regeneration sample **0 hits**, RBCHECK **8 registers**, MATCH 800 ×3 |
| `check_fuzz_bank` | **PASS — 621 banked seeds**, stable 621 / improved 0 / worse 0, `gen_drift` 0, `regen_err` 0, float-floor 0, new-sig TIMING 0 |
| `check_ab_hw all 800` / `chip 800` | first light **MATCH ×3**; close-out **MATCH over 800 rows** |
| §38.9 missed-trap overlay | **4** |

---

## 9. HARD STOPS — **STOP AND REPORT, DO NOT ITERATE**

**THE USER AUTHORISED *A* FLASH, NOT A DEBUGGING SESSION ON HARDWARE.**  If any
of the following fires: **capture the evidence, run `board_idle()`, and STOP.**
**Do not re-flash.  Do not adjust and retry.  Do not flash a different
bitstream.**

1. **`sw/f22_s1_derive.py` not PASS, or its nulls not failing** → nothing is
   built and nothing is flashed.  *(Measured MET, §1.1.)*
2. RETENTION `draw@seed1` **< 32.0 MHz**, or any G6 essential RED (E-2 / E-4 /
   E-5) → **nothing is flashed.**
3. **N-1 `ucrom_mif_check` not PASS on the flashed build's `db`** → **nothing
   is flashed.**
4. The RETENTION receipt self-labelling `CONTROL/DEFAULT`, or its `.rbf` equal
   to CONTROL's (E-6 / E-8) → **nothing is flashed on that build.**
5. `safe_flash` VERIFY not OK → **STOP.  A physical power cycle is the
   remedy, and it is the user's, not mine.**
6. **Any `div_guard` UNPINNED readback** → **RIG-INTEGRITY FINDING, HARD STOP.
   Report and stop; do NOT work around it.**
7. Any `RigMismatch` / transport quarantine.
8. A failed single-writer check that is not resolved (**`--force` is not
   used**).
9. **`check_ab_hw` first light failing on any of its three legs.**
10. **The null moving outside its registered budget** (C-5 > 10 flips) →
    capture, itemise, `board_idle()`, **STOP**.
11. S-1 *(opt)*'s **socket column moving** — a rig finding outranks the cell.

**FLASH #19's re-run rule is adopted verbatim**: if a leg fails, **the failing
leg is re-run ONCE on the same bitstream before anything is concluded**, and the
finding is reported **before** any repair is attempted.  **NO REPAIR IS
ATTEMPTED IN THIS SITTING.**

---

## 10. WHAT THIS SITTING CAN AND CANNOT ESTABLISH

**CAN**: that a bitstream whose EU decode has been re-derived (the sevenfold
unroll deleted), whose BIU queue port has been reformulated, whose EU is cut
across two clock-enable phases behind a 778-bit shadow, and **whose SDC carries
no timing exception at all**, runs this part's whole corpus **identically** to
one that has none of those; and that four landings measured behaviour-preserving
offline are behaviour-preserving **in fabric**.

**CANNOT**: attribute anything to any ONE of the four landings — **they are
flashed as a bundle and a bundle's benefit is not evidence for any member of
it.**  It also **cannot measure Fmax**: one draw per configuration, by ruling.
And it establishes **nothing** about a downstream integrator's own enable train
(§1's closing caveat).

---

## 11. DISCIPLINE, DECLARED IN ADVANCE

* **SINGLE-WRITER CHECK FIRST**, before any board or Quartus contact: `pgrep -x
  <binary>`, **ONE PATTERN PER CALL** (`pgrep -x a b` is an ERROR whose failure
  branch reads as "idle"); ⚠ `pgrep -f <script>` **self-matches** the waiting
  shell and is never used.
* ⚠ **BLOCK, DO NOT POLL** on every Quartus stage: one foreground
  `until ! pgrep -x quartus_fit >/dev/null 2>&1; do sleep 60; done`.
* **No Codex.  No nested subagents.**
* ⚠⚠ **`git stash`, `git checkout .` and `git reset --hard` ARE NEVER USED.**
  **21 tracked files in this working tree are the user's own uncommitted work.**
  **`git add` BY EXPLICIT PATH**, and **`sw/testdata/receipts/*.jsonl` IS NOT
  COMMITTED** — an append-only ledger this wave writes to may already be dirty
  (WAVE 17 §9.1).  Receipts are committed **BY VALUE** under
  `sw/testdata/flash22/`.
* ⚠ `git checkout -- hdl/nec_test_ucore.qsf` **by that exact path** between
  Quartus runs — the one declared §70.7 exemption.
* ⚠ **DO NOT CARRY A FIGURE FROM ONE TREE TO ANOTHER.**  Register counts are
  SDC-dependent; `ss_lint` reads **232 / 229 / 4** here and 228 / 3 unsplit; the
  `≥ 38.0` Fmax STOP is another tree's.  **Every figure in §8 was measured on
  this tree.**
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  **ELEVEN instruments in this
  campaign have returned confident, wrong answers**, the newest of which
  **reports a MISSING LOG AS IDENTICAL**.  Assume the next one is also wrong
  until its control says otherwise.
* /tmp discipline: `~/.cache/ucsimt-tmp/`, **never `/tmp`**.
* **RETAIN FULL PER-CLOCK ROWS + sha256 — NEVER DIGESTS ALONE.**
* **A number with no artifact id is not quotable.  Record what was measured, not
  what was expected.**

---

## Appendix A — REVIEWER RE-RUN

```bash
git rev-parse HEAD                                   # 8115b166d7
git diff --stat d3c295cdef HEAD -- hdl/              # empty: the WAVE 17 tree
python3 sw/f22_s1_derive.py                          # D-1..D-3, with its nulls
python3 -c "import sys;sys.path.insert(0,'sw');import quartus_gate as q;m=q.input_manifest();print(m['n_files'],m['sha256'][:16])"
                                                     # 99 c3305d40f62e497f

# THE SEAT DIGEST (C-6), from the FLASH #21 ledger
python3 - <<'PY'
import json, hashlib
L=json.load(open('sw/testdata/fz2/fz2_failure_ledger_f21_2026-08-13.json'))
s={f['seed']:(f['diverging_rows'], f['first_bad_row']) for f in L['failures']}
c=json.dumps(sorted((k,)+tuple(v) for k,v in s.items()), sort_keys=True)
print(len(s), hashlib.sha256(c.encode()).hexdigest())
PY
# 107 c79a41282d08c53a22d9752481fc0bce6c63d57823371db7fd3eeb8f67ad3264

# the build -- ONE draw each, draw@seed1.  THE ENV-VAR FORM IS REFUSED.
python3 sw/quartus_gate.py --seeds 1             --label "FLASH#22 CONTROL draw@seed1"
git checkout -- hdl/nec_test_ucore.qsf
python3 sw/quartus_gate.py --seeds 1 --retention --label "FLASH#22 RETENTION draw@seed1"
python3 sw/ucrom_mif_check.py                        # N-1, on the RETENTION db

sw/safe_flash.sh hdl/output_files_ucore/nec_test_ucore.sof
python3 sw/check_ab_hw.py all 800                    # N-2, first light

python3 sw/fz2_w1.py control ; python3 sw/fz2_w1.py preflight --board
python3 sw/fz2_w1.py capture
python3 sw/fz2_ledger.py --out sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json
python3 sw/fz2_replay.py --ledger <F22> --all-failures --pass-sample 150 --leg ret --jobs 8
python3 sw/fz2_immaterial.py --ledger <F22> falsify
python3 sw/fz2_w1.py bars ; python3 sw/fz2_w1.py lint
python3 sw/check_ab_hw.py chip 800                   # close-out
```

## Appendix B — THE BAR IN ONE TABLE, FOR THE SCORER

| clause | registered |
|---|---|
| **D-1 … D-4** | S-1 derivation PASS over all D in [2,63], nulls FAIL at D = 0 and D = 1, D = 8 clean, `div_guard` PINNED 100 % |
| E-1 … E-12 | G6 green on both `draw@seed1` legs, manifest **99 / `c3305d40f62e497f…`**, `.rbf`s **differing**, E11 pass on both |
| **N-1 / N-1b** | `ucrom_mif_check` **PASS on the flashed `db`**; control FAILs |
| **N-2** | first light **MATCH 800 ×3** |
| **F-1** | VERIFY OK, `flash_log` **24 → 25** |
| ⭐ **C-4** | **107 / 3,838 EXACTLY** (band [97, 117]) |
| ⭐ **C-5** | **0 entered, 0 left**, budget **10** |
| ⭐ **C-6** | seat digest **`c79a41282d08c53a…`**, **107 / 107** |
| C-7 | **0 LOST, 0 `first_bad` earlier** |
| C-8 | Σ`div` **103,803**, reconciling to **0 unexplained rows** |
| C-9 / C-9b | discards **2** (reported, not barred); families 5/4/15/1/2/1/9/1/1/9/8/4/39/2/6; overlay **4** |
| C-10 … C-15 | the named non-movers **value for value**; `fz2c/404040` **ABSENT** |
| C-16 | class **22**, partition **46/29/5/17/10**, `TIMING_RECONVERGED` **7**, **`falsify` FAIL at G6 3/8 and G7 1/23** (inherited doc staleness) |
| S-1 … S-3 *(opt)* | 0 chip movers; ghost-pred 398/122, 528/528, socket byte-identical; banks restored |
| Q-1 | era guard **REFUSING before the flash**, **PASS with no bypass** after |
| Q-2 | closing control **≥ 99 %**, `first_bad` identical, **non-zero row count printed first** |
| Q-3 | chip proof **MATCH 800**, `div_guard` **PINNED**, `board_idle()` **clean and last**, **0 transport errors** |
