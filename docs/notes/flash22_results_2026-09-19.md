# FLASH #22 — RESULTS, AS REGISTERED: **THE NO-SDC BITSTREAM IS IN SILICON AND IT BOOTS.  THE NULL MOVED BY SIX SEATS, EVERY ONE OF THEM AN IMPROVEMENT — AND THE NULL WAS MIS-DERIVED BY ME, BECAUSE THE TREE CARRIES TWO BUG FIXES MY PRE-REGISTRATION DID NOT NAME.**

Pre-registration `docs/notes/flash22_prereg_2026-09-19.md`, committed
**`d5f5fca539`** — **before any Quartus build and before any board contact** —
together with `sw/f22_s1_derive.py`, the S-1 derivation checker, **run and
proved non-vacuous before the board was touched.**

Every bar is reported in the form it was registered in.  **Nothing is
re-registered after the fact.  A miss is a miss.**

    branch      master
    HEAD        8115b166d7  ->  prereg d5f5fca539 (the built tree)
    hdl/        tracked-clean and BYTE-IDENTICAL to the WAVE 17 landing d3c295cdef
    bitstream   nec_test_ucore.sof 1ab9a37149e6e90f…
                nec_test_ucore.rbf 20fac47ef98e00fa…
                RETENTION (X1_AD_RETENTION=1), draw@seed1
    flash log   24 -> 25 entries, VERIFY ok try 1, 2026-09-19T14:23:40Z
    authorised  USER, 2026-09-19: "Flash it."

---

## 0. THE HEADLINE

> ### **1. THE FIRST BITSTREAM EVER BUILT WITH NO SDC TIMING EXCEPTION IS IN SILICON, AND FIRST LIGHT IS `MATCH 800 ×3` ON ALL THREE LEGS.**
>
> A bitstream whose EU decode has been re-derived (the sevenfold unroll
> deleted), whose BIU queue port has been reformulated, whose EU is **cut
> across two clock-enable phases behind a 778-bit shadow**, whose `CE_HALF` is
> now an **unconditional core port**, and whose `nec_test.sdc` carries **zero
> `set_multicycle_path` and zero `set_false_path`** — boots, runs the whole
> 3,840-seed corpus in 12.1 minutes with **0 transport errors and 0
> quarantines**, and closes out on a `use_core=0` chip proof of **MATCH over
> 800 rows**.  **The campaign's requirement is now met in silicon and not only
> in simulation.**
>
> **2. ⚠⚠ THE PRIMARY PREDICTION — THE NULL — MISSED ITS POINT, AND THE FIRST
> THING TO SAY IS THAT MY DERIVATION OF IT WAS WRONG.**  §0 of the
> pre-registration named **four** landings and argued the null from *"all four
> are behaviour-preserving in simulation"*.  **The tree carries two further RTL
> commits that are FUNCTIONAL BUG FIXES**, neither named by me and neither
> behaviour-preserving: **`e61f2e0988` *"FIX the REP CL==0 defect in the ucore
> RTL"*** (2026-08-17) and **`c59d205479` *"Fix REP termination before
> interrupt withdrawal"*** (2026-08-20).  **Against a tree containing those, the
> corpus SHOULD move, in the improving direction.  "Nothing moves" was never the
> right prediction and I registered it anyway.**  §9 is the erratum.
>
> **3. AND THE MOVEMENT IS ENTIRELY ONE-SIDED — THE CORPUS GOT BETTER AND
> NOTHING GOT WORSE.**  **102 failures of 3,838** against a registered 107
> (band [97, 117] **MET**, point **MISSED by −5**).  **6 seeds LEFT the ledger,
> 1 ENTERED** — 7 flips of a 10-seed budget.  **All 101 shared seats reproduce
> EXACTLY, 0 movers in either column**, `first_bad` **0 EARLIER anywhere**, and
> the row metric **reconciles to ZERO unexplained rows** over 3,840 seeds and
> 11,327,106 compared rows.
>
> **4. THE MOVEMENT IS NOT CAPTURE NOISE, AND THE OFFLINE CORE SAYS SO AT
> 100.0 %.**  The closing control replays **252 seeds — 102 fabric-FAIL and 150
> fabric-PASS — at 252 / 252 = 100.0 % agreement**, with `first_bad`
> **IDENTICAL on 102 / 102**, 0 errors, over a **non-zero, printed** population.
>
> **5. ⭐ AND THE ATTRIBUTION IS NARROWED ON COMMITTED ARTIFACTS ALONE, WITH
> FOUR OF THE SIX LANDINGS EXCLUDED BY THEIR OWN BEFORE/AFTER LADDERS.**  At the
> FLASH #21 tree the offline core **FAILED all six departing seeds at EXACTLY
> their fabric values**; at `aba01feb07` — **WAVE 7's own immediate
> predecessor** — it **already PASSED them**.  **WAVE 7, WAVE 12, WAVE 16 and
> WAVE 17 are therefore ALL EXCLUDED**, and the only behaviour-capable commits
> left in the window are **the two REP fixes.**  A narrowing, not a proof;
> falsifier registered (§9.3).
>
> **6. THE S-1 DERIVATION WAS MADE BEFORE THE FLASH AND IT WAS SAFE TO FLASH.**
> Over **every legal divider `D` in [2, 63]**: `coincident` 0, `S-1 violations`
> 0, **exactly one `CE_HALF` between consecutive `CE`s**.  Non-vacuous: `D = 0`
> fails on C-a and `D = 1` fails on S-1.
>
> **7. G6 REPRODUCED WAVE 17's SEED-1 DRAWS TO THE BITSTREAM BYTE ON BOTH
> CONFIGURATIONS**: CONTROL **34.39 / +2.172 / 8,275** and RETENTION
> **33.64 / +1.521 / 8,250**, with both `.rbf`s **byte-identical to WAVE 17's**,
> four days and two sittings apart.
>
> **8. ⚠ ONE STANDING GATE CANNOT RUN AT ALL AND HAS NOT BEEN ABLE TO FOR FIVE
> WEEKS.**  `check_fuzz_bank` binds to the **ARCHIVED FSM core** and
> `tb_v30_core.sv` has driven `ADDR_O`/`DATA_O`/`STATUS_O` since the demux
> landing **`b7083b45a5` (2026-08-14)**; the archived core has none of them.
> **I registered it to PASS 621 by carrying FLASH #21's figure across trees —
> the exact error `CLAUDE.md` names.**  §10.

---

## 1. ⚠⚠ **THE S-1 DERIVATION — `D-1` … `D-4`.  ALL MET, AND MET BEFORE THE BOARD WAS TOUCHED.**

**THE HAZARD.**  The phase split makes clause **S-1** (*at least one `CE_HALF`
between consecutive `CE`s*) **LOAD-BEARING FOR THE EU**: before the split a
violation left the address on AD for a write cycle; after it, **the EU consumes
a STALE STAGE-1 SHADOW and computes the wrong next state.**  `v30_core.sv`'s
`$fatal` is **`ifndef SYNTHESIS`, so FABRIC HAS NO ASSERTION** and the argument
must be structural.

**IT IS STRUCTURAL, AND IT IS ONE COUNTER.**  `CE = bus_tick_rise` and
`CE_HALF = bus_tick_fall` both come off `nec_bus.sv`'s single `div_cnt`, which
walks `0 … D-1` and is reset to 0 **by `tick_rise` itself**.  `tick_fall` fires
at `floor(D/2) - 1`, `tick_rise` at `D - 1`, and **for every `D ≥ 2`,
`0 ≤ floor(D/2) - 1 < D - 1`** — so in every period the fall fires exactly once,
the rise fires exactly once, and **the fall is strictly earlier.**  That is C-a
and S-1 simultaneously.

| # | bar | measured | verdict |
|---|---|---|---|
| **D-1** | every `D` in [2, 63]: 0 coincident, 0 S-1 violations, gap min == max == 1 | **`violations = []` over all 62 divisors** | **MET** |
| **D-2** | the nulls must FAIL | **`D = 0`: 64 coincident → C-a. `D = 1`: 4,095 S-1 violations → S-1.** Both FAIL as required | **MET — NON-VACUOUS** |
| **D-3** | `D = 8`, the divider of record | **CE 512 / CE_HALF 512 / coincident 0 / S-1 violations 0**, exactly one `CE_HALF` between consecutive `CE`s, 4 fabric clocks either side | **MET** |
| **D-4** | `div_guard()` PINNED on 100 % of board probes | **76 probes across the sitting, 0 UNPINNED** — §7 | **MET** |

`D = 1` is the one value that breaks S-1, and it breaks it by **6-bit
underflow**: `half = 0`, so `half - 6'd1` wraps to **63**, a count `div_cnt`
never reaches because `tick_rise` resets it every clock — **`CE` every fabric
clock and `CE_HALF` never.**  It is unreachable here: `nec_bus.sv:42` declares
the port *"even, >= 4"*, `hps_axi_slave.sv:260` resets it to **`6'd8`**,
`v30run.DIV_OF_RECORD` is **8**, `fz2_w1.py:443` **pins** it, and `div_guard()`
**asks the transport what it commanded and records the answer** on every probe.
**Every one of the 76 readings in this sitting said `div=8 (4 MHz), commanded by
this connection -> PINNED`.**

> ### **IT WAS SAFE TO FLASH ON THIS COUNT, AND THAT WAS ESTABLISHED IN WRITING AND IN CODE BEFORE THE BOARD WAS TOUCHED.**

⚠ **IT TRANSFERS TO NO OTHER INTEGRATOR.**  This is an argument about
`nec_bus` + `system_large`.  A downstream integrator whose `CE_HALF` is not
derived from the same counter must make this derivation for itself — and since
the split it is a **functional** requirement, not a pin one.  ⚠ `nec_bus.sv` and
`hps_axi_slave.sv` are **unchanged since FLASH #21**, so the train this derives
is the train that was already in the socket: **what changed is what a violation
would cost.**

---

## 2. THE BUILD — G6, ONE DRAW PER CONFIGURATION (`E-1` … `E-12`)

Quartus 17.1.0 Build 590, 5CSEBA6U23I7. Each leg from a deleted `db` /
`incremental_db` / `output_files_ucore`, `hdl/nec_test_ucore.qsf` restored by
`git checkout -- <that exact path>` before each.  **Per the seeds ruling this
compile VERIFIES THE BITSTREAM.  No band, no spread, no worst-of-N, no Fmax
claim.**

| | **CONTROL `draw@seed1`** | **RETENTION `draw@seed1` (FLASHED)** |
|---|---|---|
| verdict | **PASS** | **PASS** |
| receipt | `ed2b9bc8b1dcda32…` | **`a43b7a487bb63bbd…`** |
| configuration (**DERIVED from `flow.rpt` + `map.rpt`**) | `CONTROL/DEFAULT (no X1_AD_RETENTION)` | **`RETENTION (X1_AD_RETENTION=1)`** |
| **Fmax (`divclk`)** | **34.39** | **33.64** |
| **worst setup** | **+2.172** | **+1.521** |
| **TNS setup / hold** | **0.000 every domain, both directions** | **0.000 every domain, both directions** |
| hold slacks | +0.256 / +0.258 / +0.429 / +0.548 | +0.258 / +0.272 / +0.350 / +0.406 |
| ALMs | **8,275 / 41,910 (20 %)** | **8,250 / 41,910 (20 %)** |
| fit registers | 6,921 | 6,840 |
| errors / latches / `lpm_divide` | 0 / 0 / 0 | 0 / 0 / 0 |
| **99-file input manifest** | `c3305d40f62e497f…` | `c3305d40f62e497f…` |
| **`.rbf` sha256** | **`853eda3050f08b2f6d23f064fe99139639a04650f4f2857b2e69c4c6fa24be0d`** | **`20fac47ef98e00fa9a5529d267ab20687904b033a55bce8d7ea26a0940f704d1`** |
| `.sof` sha256 | `dc18e5e5173a6989f923…` | **`1ab9a37149e6e90fe499c54bca51622840717db776aa3f7d931aeff12ee2b53f`** |
| compile | 435 s | 471 s |

| # | bar | verdict |
|---|---|---|
| E-1 | `gen_ucore_qsf --check` before each draw | **MET** — *"up to date"*, both |
| E-2 | 0 errors, every stage Successful, 0 latches, 0 `lpm_divide` | **MET** ×2 (`error_lines` 0, five stages, 0 errors each) |
| E-3 | Fmax ≥ 32.0 | **MET** — **+1.64 MHz above the bar on the flashed leg** |
| E-4 | worst setup > 0 every domain | **MET** ×2 |
| E-5 | **TNS 0.000 setup AND hold, every domain** | **MET** ×2, all four domains |
| **E-6** | RETENTION receipt self-labels RETENTION, **DERIVED** | **MET** — derived from the reports; `configuration_requested` is a separate field |
| E-7 | CONTROL receipt self-labels `CONTROL/DEFAULT`, **DERIVED** | **MET** |
| **E-8** | the `.rbf`s DIFFER | **MET** — `20fac47e…` ≠ `853eda30…` |
| E-9 | manifest `c3305d40f62e497f…`, 99 files | **MET** ×2 |
| E-10 | seed honoured, **both readings** | **MET** — `Info: Command:` **1** and `Fitter Initial Placement Seed` **1**, both legs |
| E-11 | `E11_no_build_stamp` | **MET** ×2 — `pass` True, `files_scanned` **99**, `file_present` **False**, `token_hits` **`{}`** |
| E-12 | receipts committed **BY VALUE** | **MET** — `sw/testdata/flash22/g6-{control,retention}-draw-seed1/` |

⚠ **THE ENV-VAR FORM WAS EXERCISED AS A CONTROL AND IT REFUSED**:
`X1_AD_RETENTION=1 python3 sw/quartus_gate.py` **exited 2** naming the FLASH #18
finding.  The RETENTION leg used `--retention`, and the dry run confirms the
macro reaches `quartus_map` **unquoted**:
`quartus_map --verilog_macro=X1_AD_RETENTION=1 nec_test -c nec_test_ucore`.

### 2.1 THE EXPECTED NEIGHBOURHOOD — REGISTERED AS NOT-A-BAR, AND HIT TO THE BITSTREAM BYTE

| | expected (not a bar) | **measured** |
|---|---|---|
| CONTROL | 34.39 / +2.172 / 8,275, `.rbf` `853eda3050f08b2f…` | **34.39 / +2.172 / 8,275, `.rbf` BYTE-IDENTICAL** |
| RETENTION | 33.64 / +1.521 / 8,250, `.rbf` `20fac47ef98e00fa…` | **33.64 / +1.521 / 8,250, `.rbf` BYTE-IDENTICAL** |

**Two sittings, four days apart, a different driver and a different label — and
the same bitstream payload byte for byte on both configurations.**  The `.sof`
differs on both legs, **exactly as registered**: it embeds a project path and a
compile timestamp; the `.rbf` does not.  ⚠ This is **the compiler being
deterministic on identical inputs**, a property of the tool and not evidence
about the design.  `standing_gates.md` §A still governs: the same tree has drawn
19.42 and 45.91 MHz.

⚠ **THE FLASH #21-ERA `≥ 38.0 MHz` STOP WAS NOT ADOPTED AND THAT WAS REGISTERED
IN ADVANCE.**  It was measured on a tree whose SDC carried the CE multicycle.
Had it been carried across, **this flash would have been wrongly blocked at
33.64.**

---

## 3. **N-1, N-1b, N-2 — THE MICROCODE AND FIRST LIGHT**

| # | bar | measured | verdict |
|---|---|---|---|
| **N-1** | `ucrom_mif_check` PASS on the **flashed** build's own `db` | **PASS** — `ram0_…f358d0ef.hdl.mif` **8192 × 12** vs `ucdecode.hex` (1,656 non-zero), **every one of 8192 words identical**; `ram1_…f358d0ef.hdl.mif` **1028 × 29** vs `ucrom.hex`, **every one of 1028 words identical** | **MET** |
| **N-1b** | non-vacuity control, same sitting | one flipped bit → **`[BAD] … DIFFER 1 word(s), first [0]`, `@0: mif 0x201 vs hex 0x200`**; restored and **PASS re-confirmed**, the file **sha256-identical to the copy taken first** (`186910652a6d7aa3…`) | **MET** |
| **N-2** | **FIRST LIGHT** `check_ab_hw all 800` | **chip-vs-golden MATCH over 800 rows · core-vs-chip MATCH over 800 · core-vs-golden MATCH over 800** — and **again inside `preflight`** | **MET ×3, twice** |

⚠ **The tool prints `FAIL` and exits 0** (FLASH #21 §2, still booked).  It was
read **by eye**, never from `$?`, and the non-vacuity control is what makes that
readable.

---

## 4. THE FLASH (`F-1`)

| # | bar | measured | verdict |
|---|---|---|---|
| **F-1** | VERIFY OK, `flash_log.jsonl` **24 → 25** (exactly one) | **ok try 1**; **25 entries**; tail `{"ts":"2026-09-19T14:23:40Z", "sha256":"1ab9a37149e6…", "git_describe":"d5f5fca539-dirty", "verify":"OK"}` | **MET** |

Single writer asked **before first contact** (`no v30/serve process on the board
-> SINGLE WRITER`, 0 local serve clients) and **again inside `preflight`**;
**`--force` never used.**  `quartus_pgm` reported *"Configuration succeeded — 1
device(s) configured"*, 0 errors / 0 warnings, and VERIFY returned
`use_core: False`, `cfg: 0x1ff0008` (**div 8**).

---

## 5. THE CORPUS — **THE NULL**

`fz2_w1 control` → `preflight --board` → `capture` → `fz2_ledger`, scored
against `sw/testdata/fz2/fz2_failure_ledger_f21_2026-08-13.json`.  `fz2c` and
`fz2e` were **archived by rename** to `*-F21-archive` and the manifests re-pinned
by `fuzz_campaign.py new`; the F21 `fz2_bars`/`fz2_capture`/`fz2_control`/
`fz2_preflight` JSONs were archived to `*_F21-archive.json` **before** anything
overwrote them.  **Nothing was deleted.**

### 5.1 THE HEADLINE TABLE

| # | bar | registered | **measured** | verdict |
|---|---|---|---|---|
| **C-1** | corpus identity | 3,840 / 48 strata / lint PASS | **3,840**, **48 strata**, `SEED_LIST_SHA256` **`45d25f31a325c496…`**; `fz2_w1 lint` **PASS / 0 hits / 48 stratum rows** | **MET** |
| **C-2** | completeness | 48/48, every `rc 0` | **48 / 48, every `rc 0`**, 960 + 2,880, **12.1 min**, 727.4 s of board time | **MET** |
| **C-3** | the flash pin | `distinct_eras` 1 | **`distinct_eras` 1 · `absent` 0 · `incomplete` 0 · `build_stale` 0** over 3,840, era **`1ab9a37149e6…`** | **MET** |
| **C-4** | ⭐ **THE NULL** | **107 / 3,838**, band [97, 117] | **102 / 3,838** | **POINT MISSED (−5). BAND MET.** |
| **C-5** | membership flips | **0 entered, 0 left**, budget 10 | **ENTERED 1 · LEFT 6 = 7 flips** | **MISSED — 7 of a 10-seed budget.  §5.2** |
| **C-6** | ⭐ the seat table | digest `c79a41282d08c53a…`, 107/107 | digest **`c411a808926ca3bc…`** — **DIFFERS**; but **101 / 101 shared seats EXACT, 0 movers in EITHER column** | **DIGEST MISSED; the seat-for-seat clause MET on all 101** |
| **C-7** | direction | 0 LOST, 0 `first_bad` EARLIER | **1 LOST** (the entrant); **0 `first_bad` earlier ANYWHERE** | **MISSED on LOST; MET on EARLIER** |
| **C-8** | the row metric | Σ`div` 103,803, reconciling to 0 | **94,014**, reconciling to **0 unexplained rows** — §5.3 | **as registered** |
| **C-9** | discards | 2, denominator 3,838, **not barred** | **2**, denominator **3,838** — but the MEMBERSHIP re-rolled: `fz2e/514037` out, **`fz2e/515039` in** (`fz2e/509069` unchanged) | **reported, not barred — a SOCKET-leg predicate (A-2) no RTL change can reach; 8th consecutive era it has moved** |
| **C-9b** | families / overlay | 5·4·15·1·2·1·9·1·1·9·8·4·39·2·6 = 107; overlay 4 | **5·4·15·1·2·1·8·1·1·8·7·4·38·2·5 = 102** — five cells **−1** each, exactly the five departing seeds' families; **overlay `['fz2c/406073','fz2c/407064','fz2e/518039','fz2e/518044']` UNCHANGED** | **families MISSED (tracking C-4); overlay MET** |

Corpus headline fields: seed match **97.3424 %** (was 97.2121), row match
**99.1705 %** (was 99.0844), rows compared **11,327,106**, rows diverging
**93,955**, matched **3,736**.

### 5.2 **C-5 — THE SEVEN FLIPS, ITEMISED.  SIX OUT, ONE IN.**

| seed | tier | F21 `div`/`first` | F22 | banked verdict / mech | arch | what it is |
|---|---|---|---|---|---|---|
| `fz2c/407000` | raw | **388 / 3045** | **ABSENT** | FUNCTIONAL `func:W@430` / REACHED | PC | **LEFT** — D1 chip fetched, core did not |
| `fz2e/513024` | soup | **991 / 703** | **ABSENT** | FUNCTIONAL `func:R@28` / REACHED | 14 registers | **LEFT** — ⭐ **NAMED IN ADVANCE** (§0.1): FLASH #21's own unattributed entrant |
| `fz2e/514072` | soup | **938 / 326** | **ABSENT** | FUNCTIONAL `func:W@13` / REACHED | OK | **LEFT** — D2 core fetched, chip did not |
| `fz2e/516065` | soup | **1024 / 472** | **ABSENT** | FUNCTIONAL `func:W@10` / REACHED | CW,IX,IY,PSW | **LEFT** — C2 INTA-vectored delivery |
| `fz2e/526056` | raw | **3232 / 755** | **ABSENT** | KNOWN_ACCEPTED `cadence` / STALLED | NODUMP | **LEFT** — ⭐ **NAMED IN ADVANCE** (§0.1): FLASH #21's other unattributed entrant |
| `fz2e/535027` | raw | **3226 / 296** | **ABSENT** | FUNCTIONAL `func:R@6` / REACHED | 12 registers | **LEFT** — ⚠ **C-13's registered non-mover, and NOT named in advance.  This is the miss.** |
| **`fz2e/516077`** | soup | ABSENT | **10 / 1214** | KNOWN_ACCEPTED `cadence` / STALLED | NODUMP | **ENTERED** — `done` False on **both** legs |

**SIX OF THE SEVEN FLIPS ARE SEATS CLOSING.  THE ONE ENTRANT IS A 10-ROW
STALL.**  A capture perturbation is directionless; **this is 6:1.**

⚠ **TWO OF THE THREE MOVED NON-MOVERS WERE NAMED IN ADVANCE AND THE THIRD WAS
NOT.**  §0.1 registered `fz2e/513024`, `fz2e/526056` and `fz2e/527051` as *"the
seeds most likely to move, given no extra budget"*, and two of them moved.
**`fz2e/535027` (C-13) was not named and its movement is an unqualified miss of
C-13.**

### 5.3 **C-8 — THE ROW METRIC RECONCILES TO ZERO**

```
Sum diverging_rows    F21 103,803   ->   F22  94,014

  fz2c/407000  LEFT       -   388
  fz2e/513024  LEFT       -   991
  fz2e/514072  LEFT       -   938
  fz2e/516065  LEFT       - 1,024
  fz2e/526056  LEFT       - 3,232
  fz2e/535027  LEFT       - 3,226
  fz2e/516077  ENTERED    +    10
  the 101 shared seats    +     0
  -----------------------------------
  reconciled prediction     94,014
  measured                  94,014
  UNEXPLAINED                    0 rows
```

**Zero unexplained rows over 3,840 seeds and 11,327,106 compared rows**, and
**the `+ 0` line is the substance: not one of the 101 shared seats moved a
single row.**

### 5.4 THE NAMED NON-MOVERS — **24 OF 27, VALUE FOR VALUE**

| # | group | verdict |
|---|---|---|
| **C-10** | KM's three | **ABSENT** ×3 — **MET** |
| **C-11** | phantom-T1's three | **1/243 · 1/234 · 1/583** — **MET** |
| **C-12** | §64.1's four | **840/527 · 921/1331 · 891/636 · 984/1475** — **MET** |
| **C-13** | W7-4's two | `fz2c/410047` **3589/227** MET; **`fz2e/535027` LEFT THE LEDGER** — **MISSED** |
| **C-14** | M10's LEA-mod3 six | **3141/470 · 1087/1617 · 194/429 · 3075/396 · 3479/457 · 20/442** — **MET**; `fz2e/520066` **8/1249** unmoved (regression check only) |
| **C-14b** | FLASH #20's two movers | `fz2c/406063` **3165/249** · `fz2e/528010` **7/1383** — **MET** |
| **C-14c** | FLASH #21's three flippers | `fz2e/527051` **ABSENT** MET; **`fz2e/513024` and `fz2e/526056` LEFT** — **MISSED, and named in advance** |
| **C-15** | **the falsifier** | **`fz2c/404040` ABSENT** — **MET** |

### 5.5 `fz2_immaterial falsify` (C-16)

| # | registered | measured | verdict |
|---|---|---|---|
| **C-16a** | class **22**, COSMETIC 17 · TRANSIENT 5, 0 entrants, 0 leavers | **22 members, COSMETIC 17 · TRANSIENT 5**, and **the same 22 seeds, seed for seed** | **MET** |
| **C-16b** | **46 · 29 · 5 · 17 · 10 = 107**, `TIMING_RECONVERGED` 7 | **41 FUNCTIONAL · 28 TIMING · 5 TRANSIENT · 17 COSMETIC · 11 UNSCOREABLE = 102**, `TIMING_RECONVERGED` **7** | **MISSED — and it is C-4's arithmetic**: −5 FUNCTIONAL, −1 TIMING, **+1 UNSCOREABLE** = the entrant, which is `NODUMP` |
| **C-16c** | **FAIL at `G6 3/8`, `G7 1/23`**, G1-G5 + G8 PASS | **FAIL. `G6 4 / 8` · `G7 1 / 23`; G1 · G2 · G3 · G4 · G5 · G8 PASS** | **PARTIALLY MISSED** — the verdict and G7 are as registered; **G6 is 4, not 3**, because `UNSCOREABLE` 10 → 11 makes a **fourth** doc cell disagree.  Still pure inherited document staleness; **not repaired here** |
| **C-16d** | the five seats | `fz2e/528010` **7** COSMETIC · `fz2c/409065` **12** · `fz2e/521049` **10** · `fz2e/525017` **8** · `fz2c/408021` **22** TRANSIENT with `bs=12` | **all five exactly** | **MET** |

**The working residue is `80 material+unproven of 102 diverging of 3,838`** —
and it is quoted in that form, never as `80 / 3,838`.

---

## 6. THE ERA GUARD AND THE CLOSING CONTROL

| # | bar | measured | verdict |
|---|---|---|---|
| **Q-1** | REFUSE before the flash, PASS with no bypass after | **It REFUSED at HEAD before the flash**, by name: *"its inputs **68/88** hash IDENTICAL"*, listing **19 MOVED RTL files** (`nec_test.sdc`, `v30_core.sv`, `v30u_biu.sv`, `v30u_eu.sv`, the seven `v30u_eu_*` includes, `v30u_ss_pkg.sv`, `system_large.sv`, `files_ucore.qip`, `nec_test.qsf`, `nec_test.sv`, `sys/build_id.tcl`, `sys/sys.tcl`) plus `nec_test_ucore.qsf` **`[EXEMPT …§70.7]`**.  After the flash it **PASSES at 99/99 with NO bypass** | **MET in both halves** |
| **Q-2** | ≥ 99 %, `first_bad` identical, non-zero population printed first | **population `252 seeds with banked socket rows (102 fabric-FAIL, 150 fabric-PASS)`** → **AGREEMENT 252 / 252 = 100.0 %**, `first_bad` **IDENTICAL on 102 / 102**, **0 errors**, 23 s.  `tb_sys` receipt **`fbb3e15ea1fb5f9f…`** via `artifact.require()` | **MET in the strongest available form** |
| **Q-3** | chip proof, PINNED, idle last | `check_ab_hw chip 800` **MATCH over 800 rows**, `use_core=0`; **`div_guard` PINNED on 76 / 76 probes, 0 unpinned**; **`board_idle` OK, `use_core=0` left selected**, and **LAST** | **MET** |

**Q-1's refusal is not a formality — it is the check that the guard can still
say no**, and the pre-flash reading is the wave's own proof that the tree and
the socket had diverged by 20 files.

---

## 7. DIV GUARD, TRANSPORT AND CAPTURE COUNTS (`T-6`, `T-8`, `T-9`)

| quantity | measured |
|---|---|
| `div_guard` probes | **76** — `fz2_w1 control` 10 · `preflight` 2 · `capture` 48 · `idle` 1, plus the corpus reading `fz2_w1 bars` **C-8 `div_guards` 63 / `unpinned` 0** |
| **UNPINNED readbacks** | **0.  ZERO.  Every reading `div=8 (4 MHz), commanded by this connection -> PINNED`** |
| seeds captured | **3,840** in **727.4 s** of board time (12.1 min) |
| strata `rc != 0` | **0 of 48** |
| quarantines / run-error lines / `RigMismatch` | **0 / 0 / 0** (`fz2_w1 bars` C-10 MET) |
| transport errors | **0**, `halted: None` |
| replay errors | **0** on the 252-seed control and **0** on the 7-seed flip probe |
| **full per-clock rows retained** | **643 capture files / 30.1 MB** at `sw/testdata/campaigns/{fz2c,fz2e}/captures/`, **and the FLASH #21 era retained BESIDE them** (647 files / 30.3 MB at `*-F21-archive/captures/`).  **Nothing merged over anything, nothing deleted** |
| **sha256, not a digest alone** | **all 102 ledger failures carry a `capture_sha256`**; the sha256 over the sorted `(seed, capture_sha256)` pairs is **`f4e9fcc89b077f13210cd428671afe0c1511040cd12cd9842e41a5275a7daead`** |

---

## 8. THE STANDING GATES ON THIS ERA (`C-17`)

| gate | registered | measured | verdict |
|---|---|---|---|
| `ss_lint --core ucore` | 0x8F / 232 / 0x8FE8, **229 flops, 4 whitelist, 0 UNMAPPED** | **exactly that** — BIU 109 + EU 122 symbols; BIU 91 flops → 91 mapped; EU 138 → 134 mapped + 4 whitelisted | **MET** |
| `r7_lint` | PASS, 3 declared tainted, **41 `stop` sites**, 0 violations | **PASS — 0 undeclared carriers, 0 undeclared unresolved, 3 tainted (`eu_rd_edge`, `rd_edge_psw_take`, `rd_edge_take_raw`), 41 `stop` sites, 0 violations** | **MET** |
| `gen_ucore_qsf --check` | PASS before every Quartus run | **PASS ×3** | **MET** |
| `test_artifact` | 45 / 45, NON-VACUOUS | **45 / 45**, *"rejects a perturbed input, a stale artifact, a receipt-less artifact, a wrong-named output and a mismatched tool — NON-VACUOUS"* | **MET** |
| `fz2_w1 lint` | PASS / 0 hits / 48 stratum rows | **exactly that** | **MET** |
| `fz2_w1 bars` | **11 / 11 MET** | **11 / 11 MET** — C-6 `hold_rows_exact` **4,638** / `hold_rows_off` **0**; C-4 `distinct_eras` 1; C-5 `gen_drift` **0** / `wvec_mismatch` **0**; C-7 `at_or_over` 0; C-8 63 / 0; C-9 **192 stable / 0 unstable / 0 errors**; C-10 0 / 0; C-11 banked 480 + 143 | **MET** |
| `fz2_w1 control` | 9 legs, holds `[2,20,300]`, N1 PASS, 0 unpinned | **9 legs / 51 checks / 51 PASS**, holds **[2, 20, 300]** on `pin_int` and `pin_nmi`, TVECs `(0, 48896)` and `(3056, 8)`, **N1 negative control PASS**, `div_guards` 10 / unpinned 0 | **MET** |
| `fz2_w1 preflight --board` | OK, era self-labelling RETENTION, 0 hits, RBCHECK 8, MATCH 800 ×3 | **OK** — single writer, resident bitstream carries this tree's rig RTL (receipt **`a43b7a487bb6…`**), **192-seed regeneration sample 0 hits**, **RBCHECK 8 registers**, **MATCH 800 ×3** | **MET** |
| `check_ab_hw all 800` / `chip 800` | MATCH ×3; MATCH 800 | **MATCH ×3 (twice)**; close-out **MATCH over 800 rows** | **MET** |
| §38.9 missed-trap overlay | 4 | **4, the same four** | **MET** |
| **`check_fuzz_bank`** | **PASS — 621 banked seeds** | ⚠ **CANNOT RUN — the build fails.**  §10 | **MISSED** |

---

## 9. ⚠⚠ **THE ERRATUM IN MY OWN PRE-REGISTRATION, AND THE ATTRIBUTION IT OPENS**

### 9.1 THE ERRATUM

**My pre-registration's §0 said the tree carries FOUR structural changes and
derived the null from *"all four are behaviour-preserving in simulation".*  THAT
LIST IS INCOMPLETE AND THE DERIVATION IS THEREFORE WRONG.**  I took the brief's
four, verified that `hdl/` had not moved since `d3c295cdef`, **and never ran
`git log 325b2092d7..HEAD`** — which is the enumeration the claim actually
needed.  Run now:

| commit | date | what it is |
|---|---|---|
| `5f63289db4` | 2026-08-14 | ce/ce_half CONTRACT CORRECTION — SDC + an `ifndef SYNTHESIS` assert |
| `b7083b45a5` | 2026-08-14 | **the de-muxed bus interface** — `ADDR_O`/`DATA_O`/`STATUS_O`, `V30_MUXED_AD` |
| `930216440f` | 2026-08-14 | `v30u_eu.sv` latch-inference / narrow-subscript warning cleanup |
| **`e61f2e0988`** | **2026-08-17** | ⭐ **FIX the REP CL==0 defect in the ucore RTL — the ALU width is the operand's** |
| **`c59d205479`** | **2026-08-20** | ⭐ **Fix REP termination before interrupt withdrawal** |
| `2ceb8c3ba3` | 2026-09-09 | WAVE 7 — the chain flattening |
| `04efdc8d47` | 2026-09-11 | WAVE 12 — `build_id.v` removed |
| `f174e1a24a` | 2026-09-18 | WAVE 16 — ARM-A `qripe_presel` |
| `1c71c4f5e3` · `a35a29c082` · `d3c295cdef` | 2026-09-18 | WAVE 17 — the phase split |

*(The WAVE 9, WAVE 13 and earlier split attempts each have a matching REVERT and
net out.)*

**TWO OF THESE ARE FUNCTIONAL BUG FIXES.**  A bug fix is the opposite of
behaviour-preserving: **it is supposed to move seats.**  So *"fabric must not
move"* was never the right prediction for this tree, **and the corpus closing
six seats and opening none is what a landed bug fix looks like.**

**THE BARS STAND AS REGISTERED AND THE MISSES ARE REPORTED AS MISSES.**  C-4's
point, C-5, C-6's digest, C-7's LOST, C-13, C-14c and C-16b are **MISSED**, and
they are not re-scored on the strength of this erratum.  *A prediction that was
wrong for a reason discovered afterwards is still a prediction that was wrong.*

### 9.2 THE ATTRIBUTION, ON COMMITTED ARTIFACTS ALONE

**Four of the six landings are EXCLUDED by their own committed before/after
ladders**, and this needed no new build:

| tree | artifact | `fz2c/407000` | `fz2e/514072` | `fz2e/516065` | `fz2e/535027` |
|---|---|---|---|---|---|
| **`325b2092d7`** — the FLASH #21 build | `fz2_replay_f21.json` | **FAIL 388/3045** | **FAIL 936/326** | **FAIL 1024/472** | **FAIL 3226/296** |
| `aba01feb07` — **WAVE 7's own immediate predecessor** | `wave7/before/fz2_replay.json` | **PASS `bad 0`** | **PASS `bad 0`** | **PASS `bad 0`** | **PASS `bad 0`** |
| `2ceb8c3ba3` — WAVE 7 landed | `wave7/after/` | PASS | PASS | PASS | PASS |
| `24e1060467` — + WAVE 12, before ARM-A | `wave16/ladder_before/` | PASS | PASS | PASS | PASS |
| `f174e1a24a` — + ARM-A | `wave16/ladder_after/` | PASS | PASS | PASS | PASS |
| `4a796cc754` / `d3c295cdef` — before / after the split | `wave17/{before,after}/` | PASS | PASS | PASS | PASS |
| **FLASH #22 fabric, today** | this ledger | **PASS** | **PASS** | **PASS** | **PASS** |

> ### **THE OFFLINE CORE AT THE FLASH #21 TREE FAILED ALL SIX DEPARTING SEEDS AT EXACTLY THEIR FABRIC VALUES, AND AT `aba01feb07` — BEFORE WAVE 7 — IT ALREADY PASSED THEM.  SO WAVE 7, WAVE 12, WAVE 16 AND WAVE 17 ARE ALL EXCLUDED, AND THE CAUSE LIES STRICTLY IN `325b2092d7 … aba01feb07`.**

Of the five commits in that window, **three cannot change a scored row by
construction**: the contract correction is an `ifndef SYNTHESIS` assert plus an
SDC budget; the demux landing is registered byte-identical with `V30_MUXED_AD`
**ON**, which every build here has; and the latch cleanup removes warnings.
**That leaves the two REP fixes.**

⚠ **THIS IS A NARROWING, NOT A PROOF, AND IT IS LABELLED AS ONE.**  Six landings
were flashed as a bundle and **a bundle's benefit is not evidence for any member
of it.**  What is established is that **the four timing-campaign landings did not
cause it**, and that is established on committed before/after data and not on
anything measured today.

### 9.3 REGISTERED FALSIFIERS — **BOOKED, NOT CHASED**

1. **Attribute the six closures.**  Build `tb_sys ret` at **`930216440f`**
   (immediately before the first REP fix) and at **`c59d205479`** (after both)
   and replay the six.  If the first fails them and the second passes them, the
   REP fixes own the movement.  ⚠ **`fz2_replay` is structurally vacuous in a
   git worktree** (`.gitignore:9` hides the captures) — the population count
   must be printed and non-zero, or the answer is meaningless.
2. **`fz2e/516077`, the one entrant.**  `KNOWN_ACCEPTED/cadence`, `STALLED`,
   `NODUMP`, `done` False on **both** legs, 10 rows at `first_bad` 1214.  It has
   **no retained FLASH #21 capture**, so it was never in any offline
   zero-behaviour population — the identical structural hole FLASH #21 §4.1
   recorded for its own two entrants, **and those two are exactly the two that
   left today.**
3. ⚠ **FIVE OF THE SIX DEPARTING SEEDS CANNOT BE REPLAYED FROM THE F22 BANK AT
   ALL**: the harness retains a capture only for a seed that fails, so a seed
   that stops failing stops being replayable in its own era.  The F21 captures
   are retained at `*-F21-archive/captures/` and are the material for
   falsifier 1.  **The two that could be scored were: `fz2c/407000`
   (fabric PASS) and `fz2e/516077` (fabric FAIL) — offline agreement 2 / 2.**

---

## 10. ⚠ **`check_fuzz_bank` CANNOT RUN, IT HAS NOT BEEN ABLE TO FOR FIVE WEEKS, AND I REGISTERED IT TO PASS BY CARRYING A FIGURE ACROSS TREES**

```
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:255:6: Pin not found: 'ADDR_O'
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:256:6: Pin not found: 'DATA_O'
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:257:6: Pin not found: 'STATUS_O'
```

`check_fuzz_bank` binds to the **ARCHIVED FSM core** through `check_seq.BIN`
(`--top-module tb_v30_core -I hdl/rtl/core`).  `tb_v30_core.sv` has driven the
de-muxed ports since **`b7083b45a5` (2026-08-14)** — `git log -S ADDR_O` names
it — and `hdl/rtl/core/v30_core.sv` has **0 occurrences** of `ADDR_O`, because
the demux landing deliberately did **not** touch the archived core.

* **IT IS NOT THIS WAVE'S DOING AND NOT WAVE 17's.**  The last promoted
  `Vtb_v30_core` is dated **Aug 13 21:41** — the FLASH #21 sitting.  **Five
  weeks, and no gate saw it**, because `check_fuzz_bank` is an *ARCHIVED —
  on demand* gate that nothing runs.  The same shape as `CLAUDE.md`'s
  `s10_board`/`s13_board` rig-integrity finding.
* **THE ARTIFACT LAYER BEHAVED CORRECTLY**: *"NOTHING WAS PROMOTED.  The
  previous artifact and its receipt are untouched."*  Staging cleaned; no stale
  binary could have scored.
* ⚠ **AND THE REGISTRATION WAS MINE AND IT WAS THE NAMED ERROR.**  I registered
  *"PASS — 621 banked seeds"* by **copying FLASH #21's row**, on a tree five
  weeks and nine landings later.  `CLAUDE.md`: *"DO NOT CARRY A FIGURE FROM ONE
  TREE TO ANOTHER — measure on the tree you are on."*  **Eight of the ten §8
  rows were measured at HEAD before the document was committed; this one was
  not, and it is the one that was wrong.**
* **REGISTERED FALSIFIER, NOT REPAIRED HERE**: either `tb_v30_core.sv` gates its
  three de-muxed pins behind the core it is elaborating, or the archived FSM
  core gains them, or `check_fuzz_bank` is struck from every gate list as
  unrunnable.  **It is a decision, not a repair**, and it is not taken in a
  sitting that is measuring with the tree.

---

## 11. HARD STOPS

**NONE FIRED.**

`f22_s1_derive` **PASS with both nulls failing** · RETENTION `draw@seed1`
**33.64 ≥ 32.0** · **N-1 PASS on the flashed `db`** with its control FAILing ·
the RETENTION receipt self-labelled **RETENTION** and its `.rbf` **differed**
from CONTROL's · `safe_flash` **VERIFY ok try 1** · **0 `div_guard` UNPINNED
anywhere in the sitting (76 probes)** · **0 `RigMismatch`, 0 quarantines,
0 run-error lines, 0 transport errors** · single writer asked before first
contact and again in `preflight`, **`--force` never used** · first light
**MATCH 800 ×3** · **C-5's 7 flips are INSIDE the registered 10-seed budget** ·
closing chip proof **MATCH 800** · `board_idle()` **clean and last**.

**THE REGISTERED NON-STOPS, REPORTED WITH THEIR DENOMINATORS**: C-4's point
(−5 failures, band met), C-5's 7 flips of 10, C-6's digest (with 101/101 shared
seats exact beneath it), C-7's one LOST, C-9's discard re-roll, C-9b's five
family cells, C-13 and C-14c, C-16b and C-16c's `G6 4/8`, and §10's unrunnable
gate.

⚠ **NOTHING WAS RE-FLASHED.  NOTHING WAS ADJUSTED AND RETRIED.  NO REPAIR WAS
ATTEMPTED.**  The user authorised *a* flash and got exactly one: `flash_log`
**24 → 25**, one entry.

---

## 12. WHAT THIS SITTING ESTABLISHED, AND WHAT IT LEAVES OPEN

**ESTABLISHED**

1. ⭐ **THE NO-SDC-EXCEPTION ucore RUNS ON SILICON.**  First light MATCH 800 ×3,
   the whole 3,840-seed corpus, a 252-seed offline control at 100.0 %, and a
   closing chip proof — on a bitstream with **zero timing exceptions**, a
   **re-derived EU decode**, a **reformulated BIU queue port** and an **EU cut
   across two clock-enable phases**.  **The campaign's requirement is met in
   silicon.**
2. **S-1 HOLDS STRUCTURALLY FOR THE RIG'S ENABLE TRAIN AT EVERY LEGAL DIVIDER**,
   derived from one counter, with its own null, **before** the board was
   touched — which is what made flashing a re-timed EU into an
   assertion-free fabric a defensible act rather than a hopeful one.
3. **101 OF 101 SHARED CORPUS SEATS REPRODUCE EXACTLY** in both columns, and the
   row metric reconciles to **zero unexplained rows** over 11.3 million rows.
4. **THE CORPUS IMPROVED AND NOTHING REGRESSED**: 6 seats closed, 1 opened,
   **0 `first_bad` earlier anywhere**, seed match 97.2121 → **97.3424 %**, row
   match 99.0844 → **99.1705 %**.
5. **THE FOUR TIMING-CAMPAIGN LANDINGS DID NOT CAUSE THE MOVEMENT** — excluded on
   committed before/after ladders, not on anything measured today.
6. **G6 REPRODUCED A SECOND SITTING'S DRAWS TO THE BITSTREAM BYTE** on both
   configurations.

**OPEN, WITH THEIR FALSIFIERS**

1. **The six closures are attributed to a window, not a commit** (§9.2, §9.3
   item 1).  The prime suspects are the two REP fixes.
2. **`fz2e/516077`, the one entrant, is unattributed** (§9.3 item 2).
3. **`check_fuzz_bank` is unrunnable and it is a decision, not a repair** (§10).
4. **The IMMATERIAL census document is now two eras stale** (C-16c) —
   deliberately not edited in the sitting that measured with it.
5. **`ucrom_mif_check` still prints `FAIL` and exits 0** (FLASH #21, unrepaired).
6. **The discard predicate `_ps3_8080` has re-rolled for the eighth consecutive
   era** and nothing explains the class.
7. ⚠ **`standing_gates.md` and `CLAUDE.md` ARE NOT EDITED BY THIS WAVE** (the
   WAVE 11-17 precedent; the coordinator decides).  Now owed: **FLASH #22
   itself**, the `ss_lint` row (**232 / 229 / 4 / 0x8F / 0x8FE8**), `r7_lint`'s
   **41 `stop` sites**, bar **E11**, **`CE_HALF` as an unconditional core
   port**, and **§10's unrunnable gate.**

**WHAT IT CANNOT ESTABLISH**: which landing did what — six were flashed as a
bundle.  It measures **no Fmax**: one draw per configuration, by ruling.  And it
says **nothing** about any other integrator's enable train (§1's caveat).

---

## 13. DISCIPLINE, DECLARED AND KEPT

* **Single-writer asked FIRST**, of Quartus (`pgrep -x`, **one pattern per
  call**, five binaries, five calls) and of the board (`ssh … ps w`), **before
  any contact**, and again inside `preflight`.  `pgrep -f <script>` was never
  used against a script name.
* **THE WAITS BLOCKED; THEY DID NOT POLL A TURN** — one foreground
  `until ! pgrep -x quartus_… ; do sleep 60; done` per build.
* **No Codex.  No nested subagents.**
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  `hdl/nec_test_ucore.qsf` restored by `git checkout -- <that exact path>` before
  each Quartus run.  **`git add` BY EXPLICIT PATH ONLY**, and
  **`sw/testdata/receipts/*.jsonl` IS NOT COMMITTED** — receipts are committed
  **BY VALUE** under `sw/testdata/flash22/`.  **The user's pre-existing modified
  tracked files were counted before and after and are untouched.**
* **Archive by rename, never delete**: `fz2c`/`fz2e` → `*-F21-archive`, the four
  era JSONs → `*_F21-archive.json`.  The F21 per-clock rows are retained beside
  the F22 ones.
* `~/.cache/ucsimt-tmp/flash22/` for every intermediate; **nothing in `/tmp`.**
* **EVERY CLASSIFIER CARRIED A POSITIVE CONTROL, REPORTED FIRST**: the S-1
  checker's two nulls; `ucrom_mif_check`'s flipped bit; `fz2_replay`'s **printed
  row count** and its **pre-flash REFUSAL**; `test_artifact`'s five rejections;
  `fz2_w1 control`'s **N1 negative control**; the env-var **refusal** of
  `quartus_gate`.  ⚠ **AND ONE OF THEM CAUGHT A VACUOUS RUN IN THIS SITTING**:
  the 7-seed flip probe printed `population 2` and `NOT SCOREABLE 5` — had the
  count not been printed, *"2 / 2 = 100 %"* would have read as an answer about
  seven seeds.
* ⚠ **CONTENT COMPARED, NOT A DIGEST ASSUMED**: the ledger seat for seat on both
  columns by name, the row metric reconciled term by term, the named non-movers
  value for value, and the cross-wave attribution by reading each committed
  `fz2_replay.json`'s own `sys.bad` field.
* **Record what was measured, not what was expected** — §9 records that my own
  null was mis-derived, and §10 that my own §8 row was carried across trees.

---

## Appendix A — THE BAR IN ONE TABLE

| clause | registered | measured | verdict |
|---|---|---|---|
| **D-1 … D-4** | derivation PASS, nulls FAIL, D=8 clean, PINNED 100 % | all four | **MET** |
| E-1 … E-12 | G6 green both legs, manifest 99/`c3305d40f62e497f…`, `.rbf`s differing, E11 pass | all, both legs | **MET** |
| **N-1 / N-1b** | PASS on the flashed `db`; control FAILs | **PASS** 8192 + 1028 words; **`[BAD]` on one flipped bit** | **MET** |
| **N-2** | first light MATCH 800 ×3 | **MATCH ×3** | **MET** |
| **F-1** | VERIFY OK, log 24 → 25 | **ok try 1, 25 entries** | **MET** |
| **C-4** | **107 / 3,838**, band [97,117] | **102 / 3,838** | **POINT MISSED, BAND MET** |
| **C-5** | 0 entered, 0 left, budget 10 | **1 entered, 6 left = 7** | **MISSED, inside budget** |
| **C-6** | digest `c79a4128…`, 107/107 | digest `c411a808…`; **101 / 101 shared EXACT** | **DIGEST MISSED, seats MET** |
| C-7 | 0 LOST, 0 earlier | **1 LOST, 0 earlier** | **MISSED / MET** |
| C-8 | Σ 103,803, 0 unexplained | **94,014, 0 unexplained** | **as registered** |
| C-9 / C-9b | discards 2; families; overlay 4 | **2 (re-rolled)**; five cells −1; **overlay 4** | **reported / MISSED / MET** |
| C-10 … C-15 | 27 non-movers, `404040` ABSENT | **24 of 27**; C-13 and C-14c moved | **MISSED on 3, MET on 24** |
| C-16a / C-16d | class 22 (17+5); the five seats | **22, same seeds; all five** | **MET** |
| C-16b / C-16c | 46/29/5/17/10; FAIL at G6 3/8, G7 1/23 | **41/28/5/17/11**; **G6 4/8**, G7 1/23 | **MISSED** |
| C-17 | ten standing gates | **nine MET**; **`check_fuzz_bank` CANNOT RUN** | **MISSED on one — §10** |
| Q-1 | REFUSE before, PASS after | **68/88 REFUSED pre-flash, 99/99 PASS after, no bypass** | **MET** |
| Q-2 | ≥ 99 %, `first_bad` identical, non-zero | **252 / 252 = 100.0 %, 102 / 102** | **MET** |
| Q-3 | chip proof, PINNED, idle last | **MATCH 800, 76/76 PINNED, idle OK** | **MET** |

## Appendix B — REVIEWER RE-RUN

```bash
git rev-parse HEAD                                  # the results commit
git log --oneline 325b2092d7..HEAD -- hdl/rtl hdl/nec_test.sdc   # §9.1's enumeration
python3 sw/f22_s1_derive.py                         # D-1..D-3 with its nulls

python3 - <<'PY'                                    # C-4..C-8, seat for seat
import json, hashlib
A=json.load(open('sw/testdata/fz2/fz2_failure_ledger_f21_2026-08-13.json'))
B=json.load(open('sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json'))
FA={f['seed']:f for f in A['failures']}; FB={f['seed']:f for f in B['failures']}
sh=sorted(set(FA)&set(FB))
print('shared', len(sh), 'moved',
      sum(1 for s in sh if (FA[s]['diverging_rows'],FA[s]['first_bad_row'])
                        != (FB[s]['diverging_rows'],FB[s]['first_bad_row'])))
print('entered', sorted(set(FB)-set(FA)), 'left', sorted(set(FA)-set(FB)))
s={f['seed']:(f['diverging_rows'],f['first_bad_row']) for f in B['failures']}
c=json.dumps(sorted((k,)+tuple(v) for k,v in s.items()), sort_keys=True)
print(len(s), hashlib.sha256(c.encode()).hexdigest())
PY
# shared 101 moved 0 / entered ['fz2e/516077']
# left ['fz2c/407000','fz2e/513024','fz2e/514072','fz2e/516065','fz2e/526056','fz2e/535027']
# 102 c411a808926ca3bc392700b5c09e6f6a2c96a8fe41a7ad90597a632fb95d65f8

python3 - <<'PY'                                    # §9.2's exclusion table
import json
for p in ('fz2/fz2_replay_f21','wave7/before/fz2_replay','wave7/after/fz2_replay',
          'wave16/ladder_before/fz2_replay','wave16/ladder_after/fz2_replay',
          'wave17/before/fz2_replay','wave17/after/fz2_replay'):
    d=json.load(open(f'sw/testdata/{p}.json')); r={x['seed']:x for x in d['rows']}
    print(p, (d.get('git') or {}).get('describe'),
          [(s, r[s]['sys']['bad']) for s in
           ('fz2c/407000','fz2e/514072','fz2e/516065','fz2e/535027') if s in r])
PY

python3 sw/fz2_replay.py --report sw/testdata/fz2/fz2_replay_f22.json   # 252/252
python3 sw/fz2_immaterial.py --ledger sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json falsify
python3 sw/fz2_w1.py bars ; python3 sw/fz2_w1.py lint
python3 sw/ss_lint.py --core ucore ; python3 sw/r7_lint.py ; python3 sw/test_artifact.py
```

**A FABRIC FIGURE TAKEN ON ANY EARLIER FLASH MAY NOT BE QUOTED AGAINST THIS
TREE.**
