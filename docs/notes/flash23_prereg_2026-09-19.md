# FLASH #23 — PRE-REGISTRATION: **THE FABRIC CONFIRMATION OF ARM-B, AND ITS PRIMARY PREDICTION IS A NULL THAT IS DERIVED THIS TIME AND NOT ASSUMED**

Committed **before any Quartus build and before any board contact.**

Flashing is authorised by the **USER, 2026-09-19, verbatim: *"flash it"***, in
direct response to ARM-B landing.  That authorisation is for **this** flash.  It
is **not** a licence to iterate on the board.  §9 is the stop list and it is
obeyed literally.

    branch      master
    HEAD        a82e0cb4a7
    board now   FLASH #22, nec_test_ucore.sof 1ab9a37149e6e90f…,
                .rbf 20fac47ef98e00fa…, built from d5f5fca539 WITH
                X1_AD_RETENTION=1, flash_log.jsonl 25 entries (VERIFIED, not
                carried: `wc -l` reads 25)
    manifest    99 declared inputs, ee6a4eff46e483d3…  (MEASURED at HEAD)
    hdl/        tracked-clean (`git status --porcelain hdl/` shows only the 14
                pre-existing untracked quartus_gate_*.log files)
    user work   21 modified tracked files, counted at entry, to be counted again

Every bar below is reported in the form it is registered in.  **Nothing is
re-registered after the fact.  A miss is a miss.**

---

## 0. ⭐ JOB 0 — **THE DELTA IS ARM-B ALONE, AND IT IS ESTABLISHED FROM THE REVISION'S OWN FILE LIST AND FROM HASHES, NOT FROM REASONING**

**FLASH #22 carried FOUR structural changes at once** (WAVE 7's chain
flattening, WAVE 12's `build_id.v` removal, WAVE 16's ARM-A, WAVE 17's phase
split) and its attribution had to be a narrowing.  **This one carries ONE.**

### 0.1 THE WINDOW, ENUMERATED — **the error FLASH #22 §9.1 made is not repeated**

`git log --oneline d5f5fca539..HEAD` is **13 commits**.  **Exactly TWO touch
`hdl/`** (`git log --oneline d5f5fca539..HEAD -- hdl/ sim/`):

| commit | date | what it is | in the ucore bitstream? |
|---|---|---|---|
| **`9ccc6d0177`** | 2026-09-19 | **WAVE 18** — the **ARCHIVED FSM core** gets the de-muxed bus ports, tied to zero.  `hdl/rtl/core/v30_core.sv`, +52 lines | ⭐ **NO — §0.2** |
| **`ce39ed61bf`** | 2026-09-19 | **WAVE 19 — ARM-B.**  `hdl/rtl/ucore/v30u_eu.sv`, +33 −5 | **YES, and it is the only one** |

`git diff --stat d5f5fca539..HEAD -- hdl/` is those **two files and nothing
else**.  **`sim/` is untouched in the window.**

**AND THE CAPTURE / SCORING HARNESS IS UNTOUCHED TOO** —
`git diff --stat d5f5fca539..HEAD --` over `sw/fz2_w1.py`, `sw/fz2_ledger.py`,
`sw/fz2_replay.py`, `sw/fz2_immaterial.py`, `sw/check_ab_hw.py`,
`sw/s13_board.py`, `sw/quartus_gate.py`, `sw/safe_flash.sh`,
`sw/ucrom_mif_check.py`, `sw/v30run.py`, `sw/fuzz_campaign.py` is **EMPTY**.
The `sw/` changes in the window are `core_portlist_lint.py` (new offline lint),
`run_wave19_g6.sh`, `t30_sweep.sh` (an archived sweep's exit-code fix),
`ss_flop_whitelist_ucore.txt` (ARM-B's *justification* text, no entry added),
the `wave19_*` drivers and committed artifacts.  **None is on the capture path
and none can move a scored row.**

### 0.2 **THE ARCHIVED FSM CORE IS NOT IN THE ucore REVISION.  ESTABLISHED FROM THE FILE LIST.**

* `hdl/nec_test_ucore.qsf:108` reads **`source files_ucore.qip`**.
* `hdl/files_ucore.qip` lists **`rtl/ucore/v30_ss_pkg.sv`, `rtl/ucore/v30_core.sv`,
  `rtl/ucore/v30u_biu.sv`, `rtl/ucore/v30u_ucrom.sv`, `rtl/ucore/v30u_eu.sv`**
  and **zero files under `rtl/core/`**.
* `quartus_gate.input_manifest()` at HEAD: **99 files**, and the count of
  entries whose path contains `rtl/core` is **0**.  The only `v30_core.sv` in
  the manifest is `hdl/rtl/ucore/v30_core.sv`.

> **WAVE 18's edit cannot be in this bitstream.  It is not a declared input of
> the revision being built.**

### 0.3 ⭐ **AND THE MANIFEST SAYS IT DIRECTLY: OF 99 DECLARED INPUTS, EXACTLY ONE MOVED SINCE THE FLASHED BITSTREAM**

Diffed **file by file by name** against the FLASH #22 RETENTION receipt's own
`input_manifest` (`sw/testdata/flash22/g6-retention-draw-seed1/distribution.json`):

```
old  99 files  c3305d40f62e497f      new  99 files  ee6a4eff46e483d3
ONLY IN FLASH22: []          ONLY IN TREE: []
MOVED FILES (1):
    hdl/rtl/ucore/v30u_eu.sv   c70dee375f9b9df54aec -> 31ff3a50f503da773796
```

Those two hashes are **exactly** WAVE 19 §1.2's ARM-A and ARM-B `v30u_eu.sv`.

> ### **THE DELTA BETWEEN THE BITSTREAM IN THE SOCKET AND THE BITSTREAM THIS SITTING BUILDS IS ONE FILE, AND THAT FILE'S CHANGE IS ARM-B.  THIS IS THE CLEANEST ATTRIBUTION THIS CAMPAIGN HAS HAD.**

### 0.4 **WHY THE NULL IS DERIVED AND NOT ASSUMED**

FLASH #22's null was mis-derived because two **functional bug fixes**
(`e61f2e0988`, `c59d205479`) sat unnamed in its window.  **There are no bug
fixes in this window**: §0.1 enumerates all 13 commits, only two reach `hdl/`,
one of those is outside the revision, and the remaining one is ARM-B — which
WAVE 19 measured **behaviour-identical offline in the strongest form this repo
has**:

* `check_core --opcodes all --cases 0` **169,000/169,000 at `--ce-div` 2, 3, 4
  AND 8**, div 1 refused;
* **the exact 181** — `FA` 500/500 · `FB` 500/500 · `INT.FB` 200/200;
* `ulockstep --golden all --cases 50` **17,350 ALL LOCKSTEP**;
* the four HLT sweeps **279/283**; `sm3_s16_score` **1,320/1,371**;
* the four **`chain_lfsr` signatures BYTE-IDENTICAL** over 1.6 M fabric clocks
  — **with the widened shadow's own `$fatal` live throughout and never firing**;
* **`fz2_replay` 302 rows × 11 fields IDENTICAL, compared BY NAME**;
* `ss_lint` **0x8F / 232 / 0x8FE8 / 229 flops / 4 entries — UNMOVED.  NO
  SAVE-STATE STREAM BREAK.**

**So "nothing moves" is the right prediction for this tree, and any movement is
a FINDING TO ITEMISE.**

### 0.5 THE NOISE FLOOR GOVERNS EVERY AGGREGATE CLAIM

`docs/notes/fz2_capture_noise_2026-08-10.md`: **10 / 3,840 = 0.2604 %**
ledger-class flips.  FLASH #17 spent 7 · #18 spent 0 · #19 spent 6 · #20 spent
6 · #21 spent 3 · **#22 spent 7.**

**The unregistered-flip budget for this sitting is 10 seeds.**  Because the
prediction is a null, **every flip is unregistered by construction**, and each
is itemised with tier, `escaped`, `ps3_8080`, family and both eras'
`diverging_rows` / `first_bad_row`.

⚠ **THE SEEDS MOST LIKELY TO MOVE, NAMED IN ADVANCE AND GIVEN NO EXTRA
BUDGET.**  The prior is FLASH #22's own: **its two unattributed entrants of
FLASH #21 were exactly two of the six that left.**  So:

* **`fz2e/516077`** — FLASH #22's ONE entrant, explicitly unattributed
  (F22 §9.3 item 2): `KNOWN_ACCEPTED/cadence`, `STALLED`, `NODUMP`, `done`
  False on **both** legs, **10 rows at `first_bad` 1214**, and **no retained
  FLASH #21 capture**, so it was never in any offline zero-behaviour
  population.  **If one seat moves, the prior says it is this one.**
* **`fz2e/527051`** — three different values in three eras (1,003 → 913 →
  ABSENT), heavily `escaped`, class unexplained.  Currently **ABSENT**.
* The four other F22 entrants that the era brought in (`fz2e/521006`,
  `fz2e/529058`, `fz2e/532032`, `fz2e/534041`) — first-era seats with no
  cross-era history.

⚠ **THE ESCAPED-SEED CAVEAT, STATED IN ADVANCE**: seeds carrying a large
`escaped` count reach memory the harness does not model and their row streams
are known to be less stable than the rest of the corpus.

### 0.6 ⚠ **THE POPULATION THE CLOSING CONTROL IS SCORED AGAINST — 302, NOT 305, AND IT IS NAMED BEFORE IT IS MEASURED**

WAVE 19 §9 item 3 reports `fz2_replay`'s population reading **302** where WAVES
16 and 17 read **305**, measured on the UNEDITED tree, and books it unexplained.
**It is named here, not diagnosed here.**  What the tool's own printed line
says, read from the committed logs and quoted rather than inferred:

```
wave16/ladder_after  population 305 seeds with banked socket rows (105 fabric-FAIL, 200 fabric-PASS)
wave17/after         population 305 seeds with banked socket rows (105 fabric-FAIL, 200 fabric-PASS)
wave19/after         population 302 seeds with banked socket rows (102 fabric-FAIL, 200 fabric-PASS)
```

**The population is `replayable ledger failures + pass sample`, and it tracked
the live ledger across FLASH #22's archive-by-rename.**  That is an observation
of the printed decomposition, **not an explanation and not a bar.**

> **THIS SITTING'S CLOSING CONTROL (`Q-2`) USES `--all-failures --pass-sample
> 150 --leg ret`, SO ITS POPULATION IS `<F23 ledger failures> + 150`, AND ON
> THE NULL THAT IS `102 + 150 = 252` — THE SAME POPULATION SIZE FLASH #22
> SCORED.  The number is registered here so that a denominator change cannot
> pass unnoticed, which is exactly how FLASH #22's null went wrong.**

---

## 1. THE S-1 DERIVATION — **RE-RUN AS A CONTROL, AND MET BEFORE THE BOARD IS TOUCHED** (`D-1` … `D-4`)

The phase split (WAVE 17, already in fabric) makes clause **S-1** (*at least one
`CE_HALF` falls between consecutive `CE`s*) **load-bearing for the EU**: a
violation means the EU consumes a **stale stage-1 shadow.**  ⚠ **`v30_core.sv`'s
`$fatal` is `ifndef SYNTHESIS`, so FABRIC HAS NO ASSERTION.**  **ARM-B widens
that shadow by one bit**, so the derivation is re-run rather than carried.

`nec_bus.sv` + `system_large.sv` are **unchanged in this window** (§0.1), so the
structure is the same one FLASH #22 derived — and it is re-measured on **this**
tree anyway, because carrying a figure across trees is the error this project
names.

| # | bar |
|---|---|
| **D-1** | `python3 sw/f22_s1_derive.py` exits **0**: over **every `D` in [2, 63]**, `coincident == 0`, `s1_violations == 0`, gap min == max == 1 |
| **D-2** | its **NON-VACUITY NULL**: `D = 0` FAILS on **C-a**, `D = 1` FAILS on **S-1** |
| **D-3** | `D = 8`, the divider of record: **CE 512 / CE_HALF 512 / coincident 0 / S-1 violations 0** over 4,096 fabric clocks |
| **D-4** | **`div_guard()` PINNED on 100 % of board probes** (§9.6 is the stop) |

### 1.1 THE RESULT, MEASURED ON THIS TREE BEFORE THIS DOCUMENT WAS COMMITTED

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

> ### **D-1, D-2 AND D-3 ARE MET BEFORE THE BOARD IS TOUCHED.  IT IS SAFE TO FLASH ON THIS COUNT.**

⚠ **IT TRANSFERS TO NO OTHER INTEGRATOR** — it is an argument about `nec_bus` +
`system_large`'s single `div_cnt`.

---

## 2. THE BUILD — G6, **ONE DRAW PER CONFIGURATION** (`E-1` … `E-12`)

**Per the seeds ruling of 2026-08-13**: a flash wave's compile **VERIFIES THE
BITSTREAM**; it is **not an Fmax measurement.**  Both legs are `--seeds 1`,
i.e. **`draw@seed1`**, and **no band, no spread, no worst-of-N and no Fmax claim
is made anywhere in this sitting.**  `standing_gates.md` §A governs — **one
green build is not closure, and the same tree has drawn 19.42 and 45.91 MHz.**

| # | bar |
|---|---|
| **E-1** | `gen_ucore_qsf --check` PASSES before each draw |
| **E-2** | 0 compile errors, every stage Successful, 0 latches, 0 `lpm_divide` |
| **E-3** | `divclk` Fmax **≥ 32.0** — the campaign's own bar, and the only one that transfers to this tree |
| **E-4** | worst setup slack **> 0** on every domain |
| **E-5** | **TNS 0.000, setup AND hold, every domain** |
| **E-6** | the RETENTION receipt's **DERIVED** `configuration` self-labels **`RETENTION (X1_AD_RETENTION=1)`** — derived from the reports, **never from the flag** |
| **E-7** | the CONTROL receipt's **DERIVED** `configuration` self-labels `CONTROL/DEFAULT` |
| **E-8** | the RETENTION `.rbf` **DIFFERS** from the CONTROL `.rbf` — the check that `--verilog_macro` reached the compiler |
| **E-9** | the **99-file** input manifest reads **`ee6a4eff46e483d3…`** on both draws |
| **E-10** | the fitter honoured `--seed=1` on **both** readings (`Info: Command:` **and** `Fitter Initial Placement Seed`) |
| **E-11** | **`E11_no_build_stamp` `pass` on both receipts** — `files_scanned` 99, `file_present` False, `token_hits` `{}`.  Read at receipt level, **not** from each seed's `bars` |
| **E-12** | both receipts committed **BY VALUE** under `sw/testdata/flash23/` |

⚠ **THE ENV-VAR FORM IS REFUSED BY DESIGN.**  `X1_AD_RETENTION=1 python3
sw/quartus_gate.py` exits 2 naming the FLASH #18 finding.  The RETENTION leg is
**`python3 sw/quartus_gate.py --seeds 1 --retention`** and nothing else.

⚠ **RETENTION IS THE SHIPPING CONFIGURATION** and **the RETENTION build is the
one that is flashed.**

### 2.1 THE EXPECTED NEIGHBOURHOOD — **REGISTERED, AND NOT A BAR**

The manifest is byte-identical to WAVE 19's ARM-B sweeps, whose **seed-1** draws
are committed.  WAVE 19 §6 further measured the `.rbf` **byte-identical on 10 of
10 draws** against WAVE 15's independent ARM-B arm.  **So this is what is
expected; a differing draw is NOT a failure of this sitting — it is
`standing_gates.md` §A evidence and will be quoted as such:**

| | expected (**NOT a bar**), from `sw/testdata/g6dist/w19-armb-noexc-*-n5/seed1_quartus_gate.json` |
|---|---|
| CONTROL `draw@seed1` | **34.68 MHz**, worst setup **+2.419 ns**, ALMs **8,434 / 41,910 (20 %)**, `.rbf` **`e91a67badeef2c17…`**, `.sof` `3b22d3f9708a45aa…`, receipt `2392bb5bf46ca765…` |
| RETENTION `draw@seed1` | **34.99 MHz**, worst setup **+2.670 ns**, ALMs **8,443**, `.rbf` **`3d4a2e86190d10d7…`**, `.sof` `b3530709b2d59c80…`, receipt `569f1ec3e82e85eb…` |

⚠ **THE `.sof` IS EXPECTED TO DIFFER AND THE `.rbf` IS NOT** — the `.sof`
embeds a project path and a compile timestamp; the `.rbf` does not.

⚠ **NO FLASH #21-ERA `≥ 38.0 MHz` STOP IS ADOPTED** — that figure was measured
on a tree whose SDC carried the CE multicycle.  **The bar is the campaign's own
32.0**, and this tree's characterised `worst-of-5` is 34.48 / 34.41.

**HARD STOP: RETENTION `draw@seed1` < 32.0 MHz, or any of E-2 / E-4 / E-5 RED
→ NOTHING IS FLASHED.**

---

## 3. **N-1 — THE M10K MICROCODE BAR**, AND **N-2 — FIRST LIGHT**

| # | bar |
|---|---|
| **N-1** | `python3 sw/ucrom_mif_check.py` **PASS on the FLASHED (RETENTION) build's own `db`** — 8192 × 12 against `ucdecode.hex` **and** 1028 × 29 against `ucrom.hex`, **every word**, an address absent from the `.mif` counting as a MISMATCH and not a skip.  ⚠ **The tool prints `FAIL` and exits 0** (FLASH #21 §2, still booked): **its verdict is read by eye, never from `$?`** |
| **N-1b** | its **non-vacuity control** in the same sitting: one flipped bit → `[BAD]`, then restored and PASS re-confirmed, sha256-identical to the copy taken first |
| **N-2** | **FIRST LIGHT** — `python3 sw/check_ab_hw.py all 800` **MATCH over 800 rows on all three legs** (chip-vs-golden, core-vs-chip, core-vs-golden) |

**HARD STOP: N-1 not PASS → NOTHING IS FLASHED.  N-2 missing on any leg → STOP
AND REPORT (§9).**

---

## 4. THE FLASH (`F-1`)

**`sw/safe_flash.sh` ONLY**, with its VERIFY leg, on the **RETENTION** build.

| # | bar |
|---|---|
| **F-1** | flash succeeds, **VERIFY OK**, `flash_log.jsonl` **25 → 26 entries** (**exactly one**; the 25 is MEASURED at HEAD, not carried), tail `verify: "OK"`; `.sof` and `.rbf` sha256 recorded here and in the results |

Single-writer is asked of the board **before first contact** and again inside
`preflight`; **`--force` is not used.**  `div_guard()` on every probe.  Socket
legs are **`use_core=False`, passed explicitly every time** — the board's CFG is
sticky.

---

## 5. THE CORPUS — **THE PREDICTION IS "NOTHING MOVES"** (`C-1` … `C-16`)

`fz2_w1 control` → `fz2_w1 preflight --board` → `fz2_w1 capture` →
`fz2_ledger`, scored against the FLASH #22 ledger
`sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json`.

Before the capture, `fz2c` and `fz2e` are archived **by rename** to
`*-F22-archive` and the manifests re-pinned by `fuzz_campaign.py new`; the F22
era's `fz2_bars` / `fz2_capture` / `fz2_control` / `fz2_preflight` JSONs are
archived to `*_F22-archive.json` **before** anything overwrites them.
**Nothing is deleted.**

⚠ **`fz2_ledger`'s OWN PRINTED `LEFT` / `ENTERED` DIFF IS NOT THIS ERA'S** — its
default comparison ledger is the committed F13-era
`fz2_failure_ledger_2026-08-09.json`, which is why FLASH #22's driver log prints
`LEFT 101 / ENTERED 5` where the F21 → F22 movement was `LEFT 6 / ENTERED 1`.
**The F22 → F23 movement is computed explicitly, seat by seat, in Python.**

### 5.1 THE HEADLINE

| # | bar | **registered** |
|---|---|---|
| **C-1** | corpus identity | 960 + 2,880 = **3,840**, **48 strata**, `fz2_w1 lint` **PASS / 0 hits / 48 stratum rows** |
| **C-2** | completeness | **48 / 48 strata, every `rc 0`** |
| **C-3** | the flash pin | `distinct_eras` **1**, `absent` 0, `incomplete` 0, `build_stale` 0, every row's `era.sof_sha256` = **FLASH #23's** |
| **C-4** | ⭐ **THE HEADLINE — THE NULL** | **102 failures of a denominator of 3,838, EXACTLY.**  Tolerance: the 0.2604 % noise floor, i.e. a **band of [92, 112]**; **the POINT is 102 and a point miss is reported as a miss** |
| **C-5** | membership flips | **0 ENTERED, 0 LEFT.**  Budget **10 seeds.**  Every flip itemised |
| **C-6** | ⭐ **THE SEAT TABLE — ALL 102 SEAT-FOR-SEAT** | every FLASH #22 failure present with **the same `diverging_rows` AND the same `first_bad_row`**.  Registered as the canonical seat digest **`c411a808926ca3bc392700b5c09e6f6a2c96a8fe41a7ad90597a632fb95d65f8`** (derivation in Appendix A) |
| **C-7** | direction | **0 LOST** and **0 `first_bad` EARLIER** anywhere in the corpus |
| **C-8** | the row metric | Σ`diverging_rows` **94,014** · `rows_diverging` **93,955** · `rows_compared` **11,327,106** · seed match **97.3424 %** · row match **99.1705 %**.  Reported; **a delta must reconcile to ZERO unexplained rows** |
| **C-9** | discards | **2** (`fz2e/509069`, `fz2e/515039`), denominator **3,838**.  ⚠ `_ps3_8080` is a **SOCKET-leg** predicate (A-2) that **no RTL change can reach**; it has re-rolled on **eight** consecutive eras, so this is **reported with both bases and NOT barred** |
| **C-9b** | family counts | `A1` 5 · `A2` 4 · `A3` 15 · `B1` 1 · `B2` 2 · `C1` 1 · `C2` 8 · `C3` 1 · `C4` 1 · `D1` 8 · `D2` 7 · `D3` 4 · `E1` 38 · `E2` 2 · `NEW/UNCLASSIFIED` 5 = **102**; §38.9 missed-trap overlay **4** (`fz2c/406073`, `fz2c/407064`, `fz2e/518039`, `fz2e/518044`) |

### 5.2 THE NAMED NON-MOVERS — REGISTERED VALUE FOR VALUE

`diverging_rows / first_bad_row`, both columns, read from the FLASH #22 ledger:

| # | group | **registered** |
|---|---|---|
| **C-10** | KM's three | `fz2c/404041`, `fz2e/501066`, `fz2e/513019` — **ABSENT** |
| **C-11** | phantom-T1's three | `fz2c/404071` **1 / 243** · `fz2e/514044` **1 / 234** · `fz2e/516001` **1 / 583** |
| **C-12** | §64.1's four | `fz2c/405002` **840 / 527** · `fz2c/405013` **921 / 1331** · `fz2c/405072` **891 / 636** · `fz2e/512056` **984 / 1475** |
| **C-13** | W7-4's remaining one | `fz2c/410047` **3589 / 227**.  ⚠ `fz2e/535027` **LEFT at FLASH #22** and is registered **ABSENT** |
| **C-14** | M10's LEA-mod3 six | `fz2c/406054` **3141 / 470** · `fz2c/408019` **1087 / 1617** · `fz2e/518038` **194 / 429** · `fz2e/522019` **3075 / 396** · `fz2e/524034` **3479 / 457** · `fz2e/530001` **20 / 442**.  ⚠ `fz2e/520066` **8 / 1249** is a regression check ONLY |
| **C-14b** | FLASH #20's two movers | `fz2c/406063` **3165 / 249** · `fz2e/528010` **7 / 1383** |
| **C-14c** | **FLASH #21's three flippers** | `fz2e/513024`, `fz2e/526056`, `fz2e/527051` — **ABSENT ×3** |
| **C-14d** | **FLASH #22's own six departures** | `fz2c/407000`, `fz2e/513024`, `fz2e/514072`, `fz2e/516065`, `fz2e/526056`, `fz2e/535027` — **ABSENT ×6** |
| **C-14e** | **FLASH #22's five entrants** (§0.5's likely movers) | `fz2e/516077` **10 / 1214** · `fz2e/521006` **8 / 369** · `fz2e/529058` **4 / 1799** · `fz2e/532032` **2 / 3029** · `fz2e/534041` **1402 / 1090** |
| **C-15** | **the falsifier** | **`fz2c/404040` stays ABSENT from the ledger** |

### 5.3 `fz2_immaterial falsify` ON THE F23 LEDGER (`C-16`)

**MEASURED ON THE F22 LEDGER BEFORE THIS DOCUMENT WAS COMMITTED**, so the
registration is a derivation and not a guess:

| # | **registered** |
|---|---|
| **C-16a** | the `IMMATERIAL` class is **22 members, COSMETIC 17 · TRANSIENT 5**, **0 entrants and 0 leavers**, working residue **80** |
| **C-16b** | the partition is **FUNCTIONAL 41 · TIMING 28 · TRANSIENT 5 · COSMETIC 17 · UNSCOREABLE 11 = 102**, `TIMING_RECONVERGED` **7** |
| **C-16c** | ⚠ **`falsify` IS REGISTERED TO *FAIL*, AT EXACTLY `G6 4 / 8` AND `G7 1 / 23`, WITH `G1 · G2 · G3 · G4 · G5 · G8` PASS.**  This is **INHERITED DOCUMENT STALENESS FROM FLASH #21 AND #22** (`fz2_materiality_census` and the immaterial document are still pinned to the F20 era's 44 / 30 / 106 / 84) and it is **NOT this wave's finding and NOT repaired here.**  **Registering it to PASS would be registering something I have already measured to be false** |
| **C-16d** | `fz2e/528010` COSMETIC at **7** rows; `fz2c/409065` **12** · `fz2e/521049` **10** · `fz2e/525017` **8** COSMETIC; `fz2c/408021` **22** TRANSIENT with `bs=12` |

---

## 6. THE DIRECTED-CELL SPOT-CHECKS — **REGISTERED AS OPTIONAL**

Socket legs measure **SILICON**, which no bitstream can move.  A fabric leg
measures the **synthesised core**, which a behaviour-preserving landing must not
move either.  **These are declared OPTIONAL in advance**: run only if §2–§5 are
clean and time permits, and **if they are not run this document says so and no
figure is inferred from their absence.**

| # | leg | registered |
|---|---|---|
| **S-1** *(opt)* | `tf0f_cell run --strata nop,x1b,z1b` + `score` | **0 chip-column movers** over 512 |
| **S-2** *(opt)* | restoration | every bank copied aside **before** and restored **byte-identical** by sha256 |

⚠ **`x1_retention` / `x1_fabric` ARE NOT RUNNABLE AND ARE NOT QUOTED**
(GEN-DRIFTED since FLASH #19), so **the 283-cell HLT sweep column does not exist
for this bitstream.**  Neither are `timed_scenario`, `timed_ins_replay`,
`timed_wvec_gate`, `timed_enter_replay`, nor the four v1 fuzz banks (SUP-1 / D9).

---

## 7. THE ERA GUARD AND THE CLOSING CONTROL

| # | bar |
|---|---|
| **Q-1** | `fz2_replay`'s **fabric era guard MUST REFUSE at HEAD BEFORE the flash**, by name, on the `hdl/` file that postdates FLASH #22 — **a guard that passes before the flash is a guard that is not working** — and **PASS with NO bypass** after it.  ⚠ **The refusal is expected to name ONE moved RTL file** (`v30u_eu.sv`) where FLASH #22's named nineteen — which is §0.3 restated by a second, independent instrument |
| **Q-2** | closing control `fz2_replay --all-failures --pass-sample 150 --leg ret` — **agreement ≥ 99 %**, with `first_bad` **IDENTICAL** on the failures, over a population of **`<failures> + 150` = 252 on the null** (§0.6).  ⚠ Run **in the main tree**: the tool is structurally vacuous in a git worktree and the **row count is printed before the verdict** |
| **Q-3** | `use_core=0` **chip proof `check_ab_hw chip 800` MATCH after everything**; **`div_guard` PINNED on 100 % of probes, 0 unpinned**; **`board_idle()` clean and LAST**; **0 transport errors** reported **with the capture count** |

---

## 8. THE STANDING GATES ON THIS ERA (`C-17`)

**MEASURED AT HEAD BEFORE THIS DOCUMENT WAS COMMITTED — every row, without
exception.**  FLASH #22 §10's finding was that **one** of its ten rows was
carried across trees and it was the one that was wrong; **no row here is
carried.**

| gate | registered (**measured at HEAD**) |
|---|---|
| `ss_lint --core ucore` | **PASS, rc 0 — `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8**, BIU 109 + EU 122 symbols, **229 architectural flops, 4 whitelist entries, 0 UNMAPPED** (BIU 91 → 91 mapped, 205 comb skipped; EU 138 → 134 + 4, **432** comb skipped) |
| `r7_lint` | **PASS, rc 0 — 0 undeclared carriers, 0 undeclared unresolved, 41 `stop` sites, 0 violations** |
| **`cutset_lint`** | ⭐ **PASS, rc 0 — 81 members / 0 violations**, `live-tainted members: none`.  ⚠ **`standing_gates.md` §A still says this gate is "RED IN THE TREE BY DESIGN"; that paragraph is OUT OF DATE since `ce39ed61bf` and its repair is the coordinator's, not this wave's** |
| `phase_split_lint` | **PASS, rc 0 — 157 members / 779 bits / 0 violations**, `live-in-stage1: none` |
| `gen_ucore_qsf --check` | **PASS, rc 0** — *"nec_test_ucore.qsf is up to date"*; re-run before every Quartus run |
| `test_artifact` | **45 / 45, rc 0, NON-VACUOUS** |
| `fz2_w1 lint` | **PASS, rc 0 — 0 hits, 48 stratum rows** |
| `f22_s1_derive` | **PASS, rc 0**, nulls FAIL at `D = 0` and `D = 1` (§1.1) |
| `check_fuzz_bank` | **measured at HEAD in this sitting and reported as measured** — WAVE 18 (`9ccc6d0177`) repaired the elaboration break FLASH #22 §10 found.  **Whatever it reads is what is registered; no FLASH #21 or #18 figure is carried** |
| `fz2_w1 bars` | **11 / 11 MET**, leaf-diffed against the F22 archive with any moved verdict named |
| `fz2_w1 control` (C-6 board legs) | **9 legs**, holds `[2, 20, 300]` proved on `pin_int` and `pin_nmi`, **N1 negative control PASS**, **0 unpinned** |
| `fz2_w1 preflight --board` | **OK** — single writer, era pinned to FLASH #23's receipt **self-labelling RETENTION**, regeneration sample **0 hits**, RBCHECK **8 registers**, MATCH 800 ×3 |
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
5. `safe_flash` VERIFY not OK → **STOP.  A physical power cycle is the remedy,
   and it is the user's, not mine.**
6. **Any `div_guard` UNPINNED readback** → **RIG-INTEGRITY FINDING, HARD STOP.
   Report and stop; do NOT work around it.**
7. Any `RigMismatch` / transport quarantine.
8. A failed single-writer check that is not resolved (**`--force` is not used**).
9. **`check_ab_hw` first light failing on any of its three legs.**
10. **The null moving outside its registered budget** (C-5 > 10 flips) →
    capture, itemise, `board_idle()`, **STOP**.

**FLASH #19's re-run rule is adopted verbatim**: if a leg fails, **the failing
leg is re-run ONCE on the same bitstream before anything is concluded**, and the
finding is reported **before** any repair is attempted.  **NO REPAIR IS
ATTEMPTED IN THIS SITTING.**

---

## 10. WHAT THIS SITTING CAN AND CANNOT ESTABLISH

**CAN**: that **ARM-B — one file, 86 lines, bit 778 of the `s1q` shadow, the
`q_ripe_lead_n` select moved behind the phase cut — is behaviour-neutral IN
FABRIC**, on this part's whole corpus, and that the ~2.4 MHz no-exception
margin it bought costs nothing in silicon.  ⭐ **And unlike FLASH #22 this is
an ATTRIBUTION, not a narrowing**: §0.3 shows the socket's bitstream and this
one differ by exactly one declared input.

**CANNOT**: measure Fmax — one draw per configuration, by ruling.  Say anything
about a downstream integrator's own enable train (§1's caveat).  Or **attribute
FLASH #22's six closures**, which remain window-attributed to the two REP fixes
(F22 §9.2) and are untouched here.

---

## 11. DISCIPLINE, DECLARED IN ADVANCE

* **SINGLE-WRITER CHECK FIRST**, before any board or Quartus contact: `pgrep -x
  <binary>`, **ONE PATTERN PER CALL**; ⚠ `pgrep -f <script>` **self-matches**
  the waiting shell and is never used.
* ⚠ **BLOCK, DO NOT POLL** on every Quartus stage: one foreground
  `until ! pgrep -x quartus_fit >/dev/null 2>&1; do sleep 60; done`.
* ⚠ **NO `cmd | tail -1; rc=$?`** — it captures `tail`'s status.  Every exit
  code is captured to a variable before the pipe, or read from the tool
  directly.  ⚠ **And `${PIPESTATUS[0]}` IS A BASH-ISM: this session's shell is
  `zsh`, where the array is `${pipestatus[1]}`** — the safe form is used, and
  §10.4 of WAVE 19 is the sister trap (zsh does not word-split an unquoted
  parameter, so a gate invoked through `$var` never runs).
* **No Codex.  No nested subagents.**
* ⚠⚠ **`git stash`, `git checkout .` and `git reset --hard` ARE NEVER USED.**
  **21 tracked files in this working tree are the user's own uncommitted
  work**, counted at entry and to be counted again at exit.  **`git add` BY
  EXPLICIT PATH**, and **`sw/testdata/receipts/*.jsonl` IS NOT COMMITTED.**
  Receipts are committed **BY VALUE** under `sw/testdata/flash23/`.
* ⚠ `git checkout -- hdl/nec_test_ucore.qsf` **by that exact path** between
  Quartus runs — the one declared §70.7 exemption.  ⚠ **`quartus_map` on the
  FSM revision rewrites `hdl/nec_test.qsf` and `.qpf` in place** (WAVE 18 §8):
  **no FSM revision is compiled in this sitting.**
* ⚠ **DO NOT CARRY A FIGURE FROM ONE TREE TO ANOTHER.**  Every figure in §8 and
  §5 was measured or derived on **this** tree, from **this** tree's artifacts.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  **FOURTEEN instruments in
  this campaign have returned confident, wrong answers**, one of which **could
  not run at all while the ledger carried a green row for it.**  A gate's
  registered row and its ability to run are two different facts.
* /tmp discipline: `~/.cache/ucsimt-tmp/flash23/`, **never `/tmp`**.
* **RETAIN FULL PER-CLOCK ROWS + sha256 — NEVER DIGESTS ALONE.**
* **A number with no artifact id is not quotable.  Record what was measured,
  not what was expected.**

---

## Appendix A — REVIEWER RE-RUN

```bash
git rev-parse HEAD                                   # a82e0cb4a7
git log --oneline d5f5fca539..HEAD                   # §0.1's thirteen
git diff --stat d5f5fca539..HEAD -- hdl/ sim/        # the two files

# ⭐ JOB 0 -- the manifest diff, file by file by name
python3 - <<'PY'
import json, sys
sys.path.insert(0,'sw'); import quartus_gate as q
old=json.load(open('sw/testdata/flash22/g6-retention-draw-seed1/distribution.json'))['input_manifest']
new=q.input_manifest()
of,nf=old['files'],new['files']
print(old['n_files'],old['sha256'][:16],'->',new['n_files'],new['sha256'][:16])
print('only-old',sorted(set(of)-set(nf)),'only-new',sorted(set(nf)-set(of)))
print('moved',[(k,of[k][:20],nf[k][:20]) for k in sorted(set(of)&set(nf)) if of[k]!=nf[k]])
print('rtl/core entries in the ucore manifest:',len([k for k in nf if 'rtl/core' in k]))
PY
# 99 c3305d40f62e497f -> 99 ee6a4eff46e483d3 / only-old [] only-new []
# moved [('hdl/rtl/ucore/v30u_eu.sv','c70dee375f9b9df54aec','31ff3a50f503da773796')]
# rtl/core entries in the ucore manifest: 0

python3 sw/f22_s1_derive.py                          # D-1..D-3, with its nulls

# THE SEAT DIGEST (C-6), from the FLASH #22 ledger
python3 - <<'PY'
import json, hashlib
L=json.load(open('sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json'))
s={f['seed']:(f['diverging_rows'], f['first_bad_row']) for f in L['failures']}
c=json.dumps(sorted((k,)+tuple(v) for k,v in s.items()), sort_keys=True)
print(len(s), hashlib.sha256(c.encode()).hexdigest(), sum(v[0] for v in s.values()))
PY
# 102 c411a808926ca3bc392700b5c09e6f6a2c96a8fe41a7ad90597a632fb95d65f8 94014

# the build -- ONE draw each, draw@seed1.  THE ENV-VAR FORM IS REFUSED.
python3 sw/quartus_gate.py --seeds 1             --label "FLASH#23 CONTROL draw@seed1"
git checkout -- hdl/nec_test_ucore.qsf
python3 sw/quartus_gate.py --seeds 1 --retention --label "FLASH#23 RETENTION draw@seed1"
python3 sw/ucrom_mif_check.py                        # N-1, on the RETENTION db

sw/safe_flash.sh hdl/output_files_ucore/nec_test_ucore.sof
python3 sw/check_ab_hw.py all 800                    # N-2, first light

python3 sw/fz2_w1.py control ; python3 sw/fz2_w1.py preflight --board
python3 sw/fz2_w1.py capture
python3 sw/fz2_ledger.py --out sw/testdata/fz2/fz2_failure_ledger_f23_2026-09-19.json
python3 sw/fz2_replay.py --ledger <F23> --all-failures --pass-sample 150 --leg ret --jobs 8
python3 sw/fz2_immaterial.py --ledger <F23> falsify
python3 sw/fz2_w1.py bars ; python3 sw/fz2_w1.py lint
python3 sw/check_ab_hw.py chip 800                   # close-out
```

## Appendix B — THE BAR IN ONE TABLE, FOR THE SCORER

| clause | registered |
|---|---|
| ⭐ **JOB 0** | the bitstream delta is **ONE declared input of 99**, `hdl/rtl/ucore/v30u_eu.sv`, and it is ARM-B; the archived FSM core is **not in the revision** |
| **D-1 … D-4** | S-1 derivation PASS over all D in [2,63], nulls FAIL at D = 0 and D = 1, D = 8 clean, `div_guard` PINNED 100 % |
| E-1 … E-12 | G6 green on both `draw@seed1` legs, manifest **99 / `ee6a4eff46e483d3…`**, `.rbf`s **differing**, E11 pass on both |
| **N-1 / N-1b** | `ucrom_mif_check` **PASS on the flashed `db`**; control FAILs |
| **N-2** | first light **MATCH 800 ×3** |
| **F-1** | VERIFY OK, `flash_log` **25 → 26** |
| ⭐ **C-4** | **102 / 3,838 EXACTLY** (band [92, 112]) |
| ⭐ **C-5** | **0 entered, 0 left**, budget **10** |
| ⭐ **C-6** | seat digest **`c411a808926ca3bc…`**, **102 / 102** |
| C-7 | **0 LOST, 0 `first_bad` earlier** |
| C-8 | Σ`div` **94,014**, reconciling to **0 unexplained rows** |
| C-9 / C-9b | discards **2** (reported, not barred); families 5/4/15/1/2/1/8/1/1/8/7/4/38/2/5; overlay **4** |
| C-10 … C-15 | the named non-movers **value for value**; `fz2c/404040` **ABSENT** |
| C-16 | class **22**, partition **41/28/5/17/11**, `TIMING_RECONVERGED` **7**, **`falsify` FAIL at G6 4/8 and G7 1/23** (inherited doc staleness) |
| C-17 | **every standing-gate row measured at HEAD**, none carried |
| S-1 … S-2 *(opt)* | 0 chip movers; banks restored byte-identical |
| Q-1 | era guard **REFUSING before the flash NAMING ONE MOVED RTL FILE**, **PASS with no bypass** after |
| Q-2 | closing control **≥ 99 %**, `first_bad` identical, population **`<failures> + 150` = 252 on the null**, printed first |
| Q-3 | chip proof **MATCH 800**, `div_guard` **PINNED**, `board_idle()` **clean and last**, **0 transport errors** |
