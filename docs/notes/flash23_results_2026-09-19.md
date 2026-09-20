# FLASH #23 — RESULTS, AS REGISTERED: **ARM-B IS IN SILICON AND THE NULL IS PERFECT.  102 OF 102 SEATS EXACT IN BOTH COLUMNS, ZERO FLIPS OF A TEN-SEED BUDGET, ZERO UNEXPLAINED ROWS — AND THE ATTRIBUTION IS ONE FILE OF NINETY-NINE, PROVED BY HASH TWICE BY TWO INDEPENDENT INSTRUMENTS.**

Pre-registration `docs/notes/flash23_prereg_2026-09-19.md`, committed
**`6de3e322b58c63b24b3968dc00914b87e2b84cfe`** — **before any Quartus build and
before any board contact.**

Every bar is reported in the form it was registered in.  **Nothing is
re-registered after the fact.  A miss is a miss.**

    branch      master
    HEAD        a82e0cb4a7  ->  prereg 6de3e322b5 (the built tree)
    hdl/        tracked-clean; the ONLY declared input that moved since the
                previous bitstream is hdl/rtl/ucore/v30u_eu.sv (ARM-B)
    bitstream   nec_test_ucore.sof 0f4fcfa5cd55bc32…
                nec_test_ucore.rbf 3d4a2e86190d10d7…
                RETENTION (X1_AD_RETENTION=1), draw@seed1, receipt 5f686aeb054522e8…
    flash log   25 -> 26 entries, VERIFY ok try 1, 2026-09-19T23:48:27Z
    authorised  USER, 2026-09-19: "flash it"

---

## 0. THE HEADLINE

> ### **1. ⭐⭐ THE NULL IS MET IN EVERY CLAUSE, AND IT IS THE FIRST PERFECT ONE THIS CAMPAIGN HAS SCORED.**
>
> **102 failures of 3,837** against a registered **102** — **the POINT, exactly,
> not merely the band.**  **0 ENTERED · 0 LEFT — ZERO flips of a ten-seed
> budget.**  The **seat digest is BYTE-IDENTICAL**
> (`c411a808926ca3bc392700b5c09e6f6a2c96a8fe41a7ad90597a632fb95d65f8`), **102
> of 102 seats reproduce EXACTLY in BOTH columns**, `first_bad` **0 EARLIER
> anywhere**, Σ`diverging_rows` **94,014 → 94,014** reconciling to **ZERO
> unexplained rows**, and **every one of the fifteen family cells is
> unmoved.**  Stronger still: a field-by-field comparison of all 102 ledger
> entries over **19 fields = 1,938 comparisons** finds **1,836 identical and
> the only differing field is `capture_sha256`** — the raw file's own hash,
> which must differ because the capture is new.
>
> **2. ⭐ AND THE ATTRIBUTION IS AN ATTRIBUTION, NOT A NARROWING.**  FLASH #22
> carried four structural changes and could only exclude.  Here, of the ucore
> revision's **99 declared inputs, EXACTLY ONE MOVED** —
> `hdl/rtl/ucore/v30u_eu.sv`, `c70dee375f9b9df5…` → `31ff3a50f503da77…`, which
> are WAVE 19's own ARM-A and ARM-B hashes.  **WAVE 18's edit to the ARCHIVED
> FSM core is not a declared input of this revision at all**
> (`files_ucore.qip` lists zero `rtl/core/` files; the manifest has zero such
> entries).  **`fz2_replay`'s fabric era guard said the same thing
> independently, from the socket's own receipt: `its inputs 98/99 hash
> IDENTICAL … MOVED hdl/rtl/ucore/v30u_eu.sv <-- RTL`.**
>
> **3. THE OFFLINE CORE AGREES WITH FABRIC AT 100.0 % OVER 252 SEEDS** — 102
> fabric-FAIL and 150 fabric-PASS, **252 / 252**, `first_bad` **IDENTICAL on
> 102 / 102**, 0 errors, and **the population printed 252, which is EXACTLY the
> `102 + 150` registered in advance.**  100 % agreement in every wait mode,
> every stimulus class and **every one of the fifteen ledger families.**
>
> **4. FIRST LIGHT `MATCH 800 ×3`, TWICE**, `ucrom_mif_check` **PASS on the
> flashed build's own `db`** with its flipped-bit control **FAILING**, **61
> `div_guard` probes and ZERO UNPINNED**, 0 `RigMismatch`, 0 quarantines,
> 0 transport errors, 3,840 seeds captured in **12.1 min**, closing chip proof
> **MATCH over 800 rows**, `board_idle` **clean and last**.
>
> **5. G6 REPRODUCED WAVE 19's SEED-1 DRAWS TO THE BITSTREAM BYTE ON BOTH
> CONFIGURATIONS**: CONTROL **34.68 / +2.419 / 8,434** and RETENTION **34.99 /
> +2.670 / 8,443**, both PASS, TNS 0.000 setup AND hold on all four domains,
> and **both `.rbf`s BYTE-IDENTICAL to WAVE 19's**, a day and two trees apart.
> **This is the third cross-wave bitstream-payload reproduction of the
> campaign.**
>
> **6. ⚠ TWO REGISTERED NON-STOPS, BOTH REPORTED AS MISSES, AND THEY ARE THE
> SAME SEED.**  `fz2_w1 bars` read **10 / 11**, not the registered 11 / 11:
> **C-6's `hold_rows_exact` is 4,637 / `hold_rows_off` 1** where FLASH #22 read
> 4,638 / 0.  The one off-row is **`fz2e/516044`**, `runs []`, `term_fired 0` —
> **and `fz2e/516044` is one of this era's three `_ps3_8080` discards**, which
> is also why the **denominator moved 3,838 → 3,837** (discards 2 → 3,
> membership fully re-rolled for the **ninth** consecutive era).  **One seed
> ran away into 8080 at runtime; its terminator never fired, so its pin run was
> never counted.**  `_ps3_8080` is a **SOCKET-leg predicate (A-2) that no RTL
> change can reach**, and the discard count was registered *reported, not
> barred* — **but `bars` 11/11 was registered as a bar, and it is MISSED.**

---

## 1. ⭐ **JOB 0 — THE DELTA IS ARM-B ALONE.  ESTABLISHED THREE WAYS, TWO OF THEM BY HASH, AND NOT ONE OF THEM BY READING THE RTL.**

### 1.1 The window, enumerated

`git log --oneline d5f5fca539..HEAD` = **13 commits.**  Only **two** touch
`hdl/` and **none** touches `sim/`:

| commit | what it is | in the bitstream? |
|---|---|---|
| `9ccc6d0177` | WAVE 18 — the **ARCHIVED FSM core** gets de-muxed ports (`hdl/rtl/core/v30_core.sv`, +52) | **NO** |
| `ce39ed61bf` | **WAVE 19 — ARM-B** (`hdl/rtl/ucore/v30u_eu.sv`, +33 −5) | **YES, and only this** |

`git diff --stat d5f5fca539..HEAD -- sw/fz2_w1.py sw/fz2_ledger.py sw/fz2_replay.py
sw/fz2_immaterial.py sw/check_ab_hw.py sw/s13_board.py sw/quartus_gate.py
sw/safe_flash.sh sw/ucrom_mif_check.py sw/v30run.py sw/fuzz_campaign.py` is
**EMPTY** — **the whole capture and scoring harness is byte-unchanged**, so no
scored quantity can move by instrument.

### 1.2 The archived core is not in the revision — **FROM THE FILE LIST**

* `hdl/nec_test_ucore.qsf:108` → **`source files_ucore.qip`**
* `files_ucore.qip` lists **five `rtl/ucore/` files and ZERO under `rtl/core/`**
* `quartus_gate.input_manifest()` at HEAD: **99 files, 0 containing `rtl/core`**;
  the only `v30_core.sv` present is `hdl/rtl/ucore/v30_core.sv`

### 1.3 ⭐ The manifest diff — **99 files compared by name against the FLASHED bitstream's own receipt**

```
old  99 files  c3305d40f62e497f      new  99 files  ee6a4eff46e483d3
ONLY IN FLASH22: []          ONLY IN TREE: []
MOVED FILES (1):
    hdl/rtl/ucore/v30u_eu.sv   c70dee375f9b9df54aec -> 31ff3a50f503da773796
```

### 1.4 ⭐⭐ And a SECOND, INDEPENDENT instrument said it from the socket's side

`fz2_replay`'s fabric era guard, run **at HEAD before the flash**, reads the
resident bitstream's receipt and re-hashes **its** declared inputs against the
tree:

```
    bitstream   1ab9a37149e6e90f…  flashed 2026-09-19T14:23:40Z  git d5f5fca539-dirty
    receipt     a43b7a487bb63bbd…  FLASH#22 RETENTION draw@seed1-seed1
    its inputs  98/99 hash IDENTICAL in the tree at HEAD
      MOVED     hdl/rtl/ucore/v30u_eu.sv   <-- RTL
```

> ### **THE PRE-REGISTRATION REGISTERED THAT THE GUARD WOULD NAME *ONE* MOVED RTL FILE WHERE FLASH #22's NAMED NINETEEN.  IT NAMED ONE.  TWO INSTRUMENTS BUILT FOR DIFFERENT PURPOSES AGREE ON THE SAME SINGLE FILE.**

### 1.5 Why the null was DERIVED and not assumed

FLASH #22's null was mis-derived because two functional REP bug fixes sat
unnamed in its window.  §1.1's enumeration is the check that was missing, run
first this time: **there is no behaviour-capable commit in this window but
ARM-B**, and WAVE 19 measured ARM-B behaviour-identical offline on a 40-leg
ladder (169,000 × 4 divisors, the exact 181, `ulockstep` 17,350, four
byte-identical `chain_lfsr` signatures, `fz2_replay` 302 × 11 identical by
name, `ss_lint` 0x8F / 232 / 0x8FE8 unmoved).

---

## 2. THE S-1 DERIVATION (`D-1` … `D-4`) — **ALL MET, AND MET BEFORE THE BOARD WAS TOUCHED**

ARM-B **widens the stage-1 shadow by a bit**, and `v30_core.sv`'s S-1 `$fatal`
is **`ifndef SYNTHESIS`** — **fabric has no assertion** — so the argument must
be structural and it was re-run on this tree rather than carried.

| # | bar | measured | verdict |
|---|---|---|---|
| **D-1** | every `D` in [2, 63]: 0 coincident, 0 S-1 violations, gap min == max == 1 | **`violations = []` over all 62 divisors** | **MET** |
| **D-2** | the nulls must FAIL | **`D = 0`: 64 coincident → C-a.  `D = 1`: 4,095 S-1 violations → S-1.** Both FAIL as required | **MET — NON-VACUOUS** |
| **D-3** | `D = 8`, the divider of record | **CE 512 / CE_HALF 512 / coincident 0 / S-1 violations 0**, exactly one `CE_HALF` between consecutive `CE`s | **MET** |
| **D-4** | `div_guard()` PINNED on 100 % of board probes | **61 probes across the sitting, 0 UNPINNED** — §7 | **MET** |

Retained verbatim at `sw/testdata/flash23/s1_derivation.txt`.

⚠ **IT TRANSFERS TO NO OTHER INTEGRATOR** — it is an argument about `nec_bus` +
`system_large`'s single `div_cnt`, and since the split it is a **functional**
requirement, not a pin one.

---

## 3. THE BUILD — G6, ONE DRAW PER CONFIGURATION (`E-1` … `E-12`)

Quartus 17.1.0 Build 590, 5CSEBA6U23I7.  Each leg from a deleted `db` /
`incremental_db` / `output_files_ucore`, `hdl/nec_test_ucore.qsf` restored by
`git checkout -- <that exact path>` before each.  **Per the seeds ruling this
compile VERIFIES THE BITSTREAM.  No band, no spread, no worst-of-N, no Fmax
claim.**

| | **CONTROL `draw@seed1`** | **RETENTION `draw@seed1` (FLASHED)** |
|---|---|---|
| verdict | **PASS** | **PASS** |
| receipt (per-seed) | `912dda1267e2357e…` | **`5f686aeb054522e8…`** |
| receipt (distribution) | `13c9e64654f6be2a…` | `e5bae24d68e358e0…` |
| configuration (**DERIVED from `flow.rpt` + `map.rpt`**) | `CONTROL/DEFAULT (no X1_AD_RETENTION)` | **`RETENTION (X1_AD_RETENTION=1)`** |
| **Fmax (`divclk`)** | **34.68** | **34.99** |
| **worst setup** | **+2.419** | **+2.670** |
| **TNS setup / hold** | **0.000 every domain, both directions** | **0.000 every domain, both directions** |
| hold slacks | +0.246 / +0.271 / +0.329 / +0.352 | +0.182 / +0.269 / +0.368 / +0.396 |
| ALMs | **8,434 / 41,910 (20 %)** | **8,443 / 41,910 (20 %)** |
| map / fit registers | 5,688 / 6,849 | 5,709 / 6,854 |
| errors / latches / `lpm_divide` | 0 / 0 / 0 | 0 / 0 / 0 |
| **99-file input manifest** | `ee6a4eff46e483d3…` | `ee6a4eff46e483d3…` |
| **`.rbf` sha256** | **`e91a67badeef2c17262b5239e0700672f3be69eeb44e749e5c9d53ae1302a613`** | **`3d4a2e86190d10d7e08c686449cb0692ad7a395f0e42eef79fe0d1e67512c055`** |
| `.sof` sha256 | `d6d3a6d3c2c85159dd3a…` | **`0f4fcfa5cd55bc322ecb4d1089fd6e823fd6cb0e809c03dcc6f2e496eaadd7c7`** |
| compile | 544 s | 562 s |

| # | bar | verdict |
|---|---|---|
| E-1 | `gen_ucore_qsf --check` before each draw | **MET** — *"up to date"*, both |
| E-2 | 0 errors, every stage Successful, 0 latches, 0 `lpm_divide` | **MET** ×2 (`error_lines` 0) |
| E-3 | Fmax ≥ 32.0 | **MET** — **+2.99 MHz above the bar on the flashed leg** |
| E-4 | worst setup > 0 every domain | **MET** ×2 |
| E-5 | **TNS 0.000 setup AND hold, every domain** | **MET** ×2, all four domains |
| **E-6** | RETENTION receipt self-labels RETENTION, **DERIVED** | **MET** |
| E-7 | CONTROL receipt self-labels `CONTROL/DEFAULT`, **DERIVED** | **MET** |
| **E-8** | the `.rbf`s DIFFER | **MET** — `3d4a2e86…` ≠ `e91a67ba…` |
| E-9 | manifest `ee6a4eff46e483d3…`, 99 files | **MET** ×2 |
| E-10 | seed honoured, **both readings** | **MET** — `Info: Command:` **1** and `Fitter Initial Placement Seed` **1**, both legs |
| E-11 | `E11_no_build_stamp` | **MET** ×2 — `pass` True, `files_scanned` **99**, `file_present` **False**, `token_hits` **`{}`** |
| E-12 | receipts committed **BY VALUE** | **MET** — `sw/testdata/flash23/g6-{control,retention}-draw-seed1/` |

### 3.1 THE EXPECTED NEIGHBOURHOOD — REGISTERED AS NOT-A-BAR, AND HIT TO THE BITSTREAM BYTE

| | expected (not a bar) | **measured** |
|---|---|---|
| CONTROL | 34.68 / +2.419 / 8,434, `.rbf` `e91a67badeef2c17…` | **34.68 / +2.419 / 8,434, `.rbf` BYTE-IDENTICAL** |
| RETENTION | 34.99 / +2.670 / 8,443, `.rbf` `3d4a2e86190d10d7…` | **34.99 / +2.670 / 8,443, `.rbf` BYTE-IDENTICAL** |

The `.sof` differs on both legs, **exactly as registered** — it embeds a project
path and a compile timestamp; the `.rbf` does not.

⚠ **This is the compiler being deterministic on identical inputs, a property of
the tool and not evidence about the design.**  `standing_gates.md` §A still
governs: **the same tree has drawn 19.42 and 45.91 MHz.**  ⚠ And no `≥ 38.0 MHz`
stop was adopted: that figure belongs to a tree whose SDC carried the CE
multicycle, and carrying it across would have wrongly blocked this flash at
34.99.

---

## 4. **N-1, N-1b, N-2 — THE MICROCODE AND FIRST LIGHT**

| # | bar | measured | verdict |
|---|---|---|---|
| **N-1** | `ucrom_mif_check` PASS on the **flashed** build's own `db` | **PASS** — `ram0_…f358d0ef.hdl.mif` **8192 × 12** vs `ucdecode.hex` (1,656 non-zero), **every one of 8192 words identical**; `ram1_…f358d0ef.hdl.mif` **1028 × 29** vs `ucrom.hex`, **every one of 1028 words identical** | **MET** |
| **N-1b** | non-vacuity control, same sitting | one flipped bit → **`[BAD] … DIFFER 1 word(s), first [0]`, `@0: mif 0x136b9cb1 vs hex 0x136b9cb0`**, `FAIL (1 problem(s))`; restored and **PASS re-confirmed**, the file sha256-identical to the copy taken first (`ba46faca4bcc7688…`) | **MET** |
| **N-2** | **FIRST LIGHT** `check_ab_hw all 800` | **chip-vs-golden MATCH over 800 rows · core-vs-chip MATCH over 800 · core-vs-golden MATCH over 800** — and **again inside `preflight`** | **MET ×3, twice** |

⚠ **The tool prints `FAIL` and exits 0** (FLASH #21 §2, still booked).  It was
read **by eye**, never from `$?`, and N-1b is what makes that readable.

---

## 5. THE FLASH (`F-1`)

| # | bar | measured | verdict |
|---|---|---|---|
| **F-1** | VERIFY OK, `flash_log.jsonl` **25 → 26** (exactly one) | **ok try 1**; **26 entries**; tail `{"ts":"2026-09-19T23:48:27Z", "sha256":"0f4fcfa5cd55…", "git_describe":"6de3e322b5-dirty", "verify":"OK"}` | **MET** |

Single writer asked **before first contact** (`no v30/serve process on the board
-> SINGLE WRITER`; all six Quartus binaries idle, `pgrep -x`, one pattern per
call) and **again inside `preflight`**; **`--force` never used.**  `quartus_pgm`
reported *"Configuration succeeded — 1 device(s) configured"*, **0 errors /
0 warnings**, and VERIFY returned `use_core: False`, `cfg: 0x1ff0008`
(**div 8**), `pwr_good: True`.

---

## 6. THE CORPUS — **THE NULL**

`fz2_w1 control` → `preflight --board` → `capture` → `fz2_ledger`, scored
against `sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json`.  `fz2c` and
`fz2e` were **archived by rename** to `*-F22-archive` (494 + 149 capture files
retained) and the manifests re-pinned by `fuzz_campaign.py new`; the four F22
era JSONs were archived to `*_F22-archive.json` **before** anything overwrote
them.  **Nothing was deleted.**

### 6.1 THE HEADLINE TABLE

| # | bar | registered | **measured** | verdict |
|---|---|---|---|---|
| **C-1** | corpus identity | 3,840 / 48 strata / lint PASS | **3,840**, **48 strata**, `fz2_w1 lint` **PASS / 0 hits / 48 stratum rows** (run before AND after) | **MET** |
| **C-2** | completeness | 48/48, every `rc 0` | **48 / 48, every `rc 0`**, 960 + 2,880, **12.1 min** | **MET** |
| **C-3** | the flash pin | `distinct_eras` 1 | **`distinct_eras` 1 · `absent` 0 · `incomplete` 0 · `build_stale` 0** over 3,840 | **MET** |
| **C-4** | ⭐ **THE NULL** | **102**, band [92, 112] | ⭐ **102** — **THE POINT, EXACTLY** | **MET** |
| **C-5** | membership flips | **0 entered, 0 left**, budget 10 | ⭐ **0 ENTERED · 0 LEFT · 0 FLIPS** | **MET** |
| **C-6** | ⭐ the seat table | digest `c411a808926ca3bc…`, 102/102 | ⭐ **digest `c411a808926ca3bc392700b5c09e6f6a2c96a8fe41a7ad90597a632fb95d65f8` — IDENTICAL**; **102 / 102 seats EXACT, 0 movers in EITHER column** | **MET** |
| **C-7** | direction | 0 LOST, 0 `first_bad` EARLIER | **0 LOST; 0 `first_bad` earlier ANYWHERE** | **MET** |
| **C-8** | the row metric | Σ`div` 94,014, reconciling to 0 | **94,014 → 94,014**, reconciled term by term, **0 unexplained rows**; `rows_diverging` **93,955** unmoved | **MET** |
| **C-9** | discards | 2, denominator 3,838, **not barred** | ⚠ **3**, denominator **3,837** — membership FULLY re-rolled: `fz2e/515039` out, **`fz2c/402059` and `fz2e/516044` in** (`fz2e/509069` unchanged) | **reported, not barred — a SOCKET-leg predicate (A-2) no RTL change can reach; NINTH consecutive era it has moved** |
| **C-9b** | families / overlay | 5·4·15·1·2·1·8·1·1·8·7·4·38·2·5 = 102; overlay 4 | ⭐ **every one of the fifteen cells IDENTICAL**; overlay **the same four** | **MET** |

Corpus headline fields: seed match **97.3417 %** (3,735 / 3,837), row match
**99.1705 %** — **the same to four decimals as FLASH #22's 99.1705 %** — rows
compared **11,326,175** (−931 against F22, which is the third discard's own
rows leaving the denominator).

### 6.2 ⭐ **C-5 / C-6 — THERE IS NOTHING TO ITEMISE.  THE ITEMISATION IS A FIELD-BY-FIELD PROOF INSTEAD.**

Because no seat moved, the usual flip table is empty.  In its place, the two
ledgers' **102 shared entries were compared over all 19 fields by name**:

```
fields compared: 19  ['arch','arch_match','banked_sub','banked_verdict','capture',
                      'capture_sha256','cid','compare_window','diverging_rows',
                      'done_chip','done_core','family','first_bad_row','image_sha256',
                      'k','mech','new_failure','seed','tier']
102 seats x 19 fields = 1938 comparisons
  capture_sha256   differs on 102 seats     <-- the raw file's own hash; it MUST differ
  ... and NOTHING else differs at all
```

> **`arch`, `arch_match`, `done_chip`, `done_core`, `family`, `mech`, `k`,
> `compare_window`, `tier`, `image_sha256`, `banked_verdict`, `banked_sub`,
> `diverging_rows` and `first_bad_row` are identical on every seat.  1,836 of
> 1,938 comparisons identical, and the 102 that are not are the one field that
> is required to move.**

### 6.3 **C-8 — THE ROW METRIC RECONCILES TO ZERO, TRIVIALLY AND EXACTLY**

```
Sum diverging_rows    F22  94,014   ->   F23  94,014
  seats LEFT       -0        seats ENTERED   +0
  the 102 shared seats       + 0
  -----------------------------------
  reconciled prediction     94,014
  measured                  94,014
  UNEXPLAINED                    0 rows      over 11,326,175 compared rows
```

### 6.4 THE NAMED NON-MOVERS — **30 OF 30, VALUE FOR VALUE**

| # | group | verdict |
|---|---|---|
| **C-10** | KM's three | **ABSENT** ×3 — **MET** |
| **C-11** | phantom-T1's three | **1/243 · 1/234 · 1/583** — **MET** |
| **C-12** | §64.1's four | **840/527 · 921/1331 · 891/636 · 984/1475** — **MET** |
| **C-13** | W7-4's one (+ the F22 departure) | `fz2c/410047` **3589/227** — **MET**; `fz2e/535027` **ABSENT** as registered — **MET** |
| **C-14** | M10's LEA-mod3 six | **3141/470 · 1087/1617 · 194/429 · 3075/396 · 3479/457 · 20/442** — **MET**; `fz2e/520066` **8/1249** unmoved (regression check only) |
| **C-14b** | FLASH #20's two movers | `fz2c/406063` **3165/249** · `fz2e/528010` **7/1383** — **MET** |
| **C-14c** | FLASH #21's three flippers | **ABSENT** ×3 — **MET** |
| **C-14d** | FLASH #22's six departures | **ABSENT** ×6 — **MET** |
| **C-14e** | ⭐ FLASH #22's five entrants — **the seeds §0.5 named as most likely to move** | `fz2e/516077` **10/1214** · `fz2e/521006` **8/369** · `fz2e/529058` **4/1799** · `fz2e/532032` **2/3029** · `fz2e/534041` **1402/1090** — **ALL FIVE UNMOVED** — **MET** |
| **C-15** | **the falsifier** | **`fz2c/404040` ABSENT** — **MET** |

> **The prior said that if anything moved it would be `fz2e/516077`, FLASH
> #22's unattributed entrant, because FLASH #21's two unattributed entrants
> were exactly two of the six that left at #22.  It did not move.  Neither did
> the other four first-era seats.**

### 6.5 `fz2_immaterial falsify` (C-16)

| # | registered | measured | verdict |
|---|---|---|---|
| **C-16a** | class **22**, COSMETIC 17 · TRANSIENT 5, 0 entrants, 0 leavers | **22 members, COSMETIC 17 · TRANSIENT 5** | **MET** |
| **C-16b** | **41 · 28 · 5 · 17 · 11 = 102**, `TIMING_RECONVERGED` 7 | **41 FUNCTIONAL · 28 TIMING · 5 TRANSIENT · 17 COSMETIC · 11 UNSCOREABLE = 102**, `TIMING_RECONVERGED` **7** | **MET** |
| **C-16c** | **FAIL at `G6 4/8`, `G7 1/23`**, G1-G5 + G8 PASS | **FAIL. `G6 4 / 8` · `G7 1 / 23`; G1 · G2 · G3 · G4 · G5 · G8 PASS**, with the same four doc cells (`FUNCTIONAL 44≠41`, `TIMING 30≠28`, `UNSCOREABLE 10≠11`, `total 106≠102`) | **MET — the registered FAIL, reproduced clause for clause** |
| **C-16d** | the five seats | `fz2e/528010` **7** COSMETIC · `fz2c/409065` **12** · `fz2e/521049` **10** · `fz2e/525017` **8** · `fz2c/408021` **22** TRANSIENT with `bs=12` | **all five exactly** | **MET** |

**The working residue is `80 material+unproven of 102 diverging of 3,837`** —
quoted in that form, never as `80 / 3,837`.

⚠ **A seed-for-seed diff of the 22 members against FLASH #22 could NOT be
taken**: `fz2_immaterial census` reads each entry's capture by path, and the F22
captures were archived by rename, so the F22 census returns **0 members** in
this tree.  **That is an instrument limitation, stated, not a finding** — and
§6.2's field-by-field identity over all 102 entries is the stronger statement
anyway, since the IMMATERIAL disposition is derived from exactly those fields.

---

## 7. THE ERA GUARD AND THE CLOSING CONTROL

| # | bar | measured | verdict |
|---|---|---|---|
| **Q-1** | REFUSE before the flash **naming ONE moved RTL file**, PASS with no bypass after | ⭐ **REFUSED at HEAD before the flash**: *"its inputs **98/99** hash IDENTICAL"*, **MOVED: `hdl/rtl/ucore/v30u_eu.sv` `<-- RTL`, and nothing else**, exit 1.  After the flash it **PASSES at 99/99 with NO bypass** | **MET in both halves, and the refusal's CONTENT was registered in advance** |
| **Q-2** | ≥ 99 %, `first_bad` identical, population `<failures>+150` = **252**, printed first | ⭐ **population `252 seeds with banked socket rows (102 fabric-FAIL, 150 fabric-PASS)`** → **AGREEMENT 252 / 252 = 100.0 %**, `first_bad` **IDENTICAL on 102 / 102**, **0 errors**, 24 s.  100 % in every wait mode (fixed 98, wrand 93, wvec 61), both stimulus classes (112 / 140) and **all fifteen families**.  `tb_sys` receipt **`215e4a2d8ccc4c93…`** | **MET in the strongest available form** |
| **Q-3** | chip proof, PINNED, idle last | `check_ab_hw chip 800` **MATCH over 800 rows**, `use_core=0`; **`div_guard` PINNED on 61 / 61 probes, 0 unpinned**; **`board_idle` OK, `use_core=0` left selected**, and **LAST** | **MET** |

**Q-1's refusal is not a formality — it is the check that the guard can still
say no**, and this time its *content* was pre-registered: one file, and it named
one file.

⚠ **AN INSTRUMENT NOTE, CAUGHT BY THE TOOL ITSELF**: the first attempt at Q-2
passed `--report sw/testdata/fz2/fz2_replay_f23.json`, which **READS** a run
file; the writer is `--out`.  The tool raised `FileNotFoundError` and produced
nothing.  **A flag that does something other than what you assumed, refusing
loudly, is the good case** — the bad case is the one that runs vacuously.

---

## 8. DIV GUARD, TRANSPORT AND CAPTURE COUNTS

| quantity | measured |
|---|---|
| `div_guard` probes | **61** — `fz2_w1 control` 10 · `preflight` 2 · `capture` 48 · `idle` 1, plus the corpus reading `fz2_w1 bars` **C-8 `div_guards` 63 / `unpinned` 0** |
| **UNPINNED readbacks** | **0.  ZERO.  Every reading `div=8 (4 MHz), commanded by this connection -> PINNED`** |
| seeds captured | **3,840** in **12.1 min** |
| strata `rc != 0` | **0 of 48** |
| quarantines / run-error lines / `RigMismatch` / `halted` | **0 / 0 / 0 / None** (`fz2_w1 bars` C-10 MET) |
| transport errors | **0** |
| replay errors | **0** on the 252-seed control and **0** on the era-guard probe |
| **full per-clock rows retained** | **644 capture files / 31 MB** at `sw/testdata/campaigns/{fz2c,fz2e}/captures/`, **and the FLASH #22 era retained BESIDE them** (643 files / 30 MB at `*-F22-archive/captures/`).  **Nothing merged over anything, nothing deleted** |
| **sha256, not a digest alone** | **all 102 ledger failures carry a `capture_sha256`**; the sha256 over the sorted `(seed, capture_sha256)` pairs is **`6b73be02d28eb887e079184e506c653e83fc816b80414b17a2e42e392732b5e7`** |

---

## 9. THE STANDING GATES ON THIS ERA (`C-17`)

**Every row was measured at HEAD before the pre-registration was committed** —
FLASH #22 §10's finding was that one of its ten rows had been carried across
trees and it was the one that was wrong.

| gate | registered | measured | verdict |
|---|---|---|---|
| `ss_lint --core ucore` | 0x8F / 232 / 0x8FE8, **229 flops, 4 whitelist, 0 UNMAPPED** | **exactly that**, rc 0 — BIU 109 + EU 122 symbols; BIU 91 → 91 mapped (205 comb skipped); EU 138 → 134 + 4 (**432** comb skipped) | **MET** |
| `r7_lint` | PASS, **41 `stop` sites**, 0 violations | **PASS, rc 0 — 0 undeclared carriers, 0 undeclared unresolved, 41 `stop` sites, 0 violations** | **MET** |
| **`cutset_lint`** | **PASS — 81 / 0** | ⭐ **PASS, rc 0 — 81 members / 0 violations**, `live-tainted members: none` | **MET** |
| `phase_split_lint` | PASS — 157 / 779 / 0 | **PASS, rc 0 — 157 members / 779 bits / 0 violations** | **MET** |
| `gen_ucore_qsf --check` | PASS before every Quartus run | **PASS ×3** | **MET** |
| `test_artifact` | 45 / 45, NON-VACUOUS | **45 / 45**, *"rejects a perturbed input, a stale artifact, a receipt-less artifact, a wrong-named output and a mismatched tool — NON-VACUOUS"* | **MET** |
| `f22_s1_derive` | PASS, nulls FAIL | **PASS, rc 0**, both nulls FAIL | **MET** |
| **`check_fuzz_bank`** | *"whatever it reads is what is registered"* | ⭐ **`PASS \| 621 banked seeds \| stable 621 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0`** — **the gate FLASH #22 §10 found unrunnable RUNS AGAIN**, repaired by WAVE 18's `9ccc6d0177` | **MET, and measured on THIS tree** |
| `fz2_w1 lint` | PASS / 0 hits / 48 stratum rows | **exactly that**, before AND after the capture | **MET** |
| **`fz2_w1 bars`** | **11 / 11 MET** | ⚠ **10 / 11 — C-6 MISSED** (`hold_rows_exact` **4,637** / `hold_rows_off` **1**); C-1 MET · C-2 MET · C-3 MET · C-4 `distinct_eras` 1 MET · C-5 `gen_drift` **0** / `wvec_mismatch` **0** MET · C-7 `at_or_over` 0 MET · C-8 **63 / 0** MET · C-9 **192 stable / 0 unstable / 0 errors** MET · C-10 **0 / 0** MET · C-11 banked 480 + 143 MET | **MISSED — §10** |
| `fz2_w1 control` | 9 legs, holds `[2,20,300]`, N1 PASS, 0 unpinned | **9 legs / 51 checks / 51 PASS, 0 FAIL**, holds **[2, 20, 300]** on `pin_int` and `pin_nmi`, TVECs `(0, 48896)` and `(3056, 8)`, **N1 negative control PASS**, `div_guards` 10 / unpinned 0 | **MET** |
| `fz2_w1 preflight --board` | OK, era self-labelling RETENTION, 0 hits, RBCHECK 8, MATCH 800 ×3 | **OK** — single writer, resident bitstream carries this tree's rig RTL (receipt **`5f686aeb0545…`**, *"FLASH#23 RETENTION draw@seed1-seed1"*), **192-seed regeneration sample 0 hits**, **RBCHECK 8 registers**, **MATCH 800 ×3** | **MET** |
| `check_ab_hw all 800` / `chip 800` | MATCH ×3; MATCH 800 | **MATCH ×3 (twice)**; close-out **MATCH over 800 rows** | **MET** |
| §38.9 missed-trap overlay | 4 | **4, the same four** | **MET** |

---

## 10. ⚠ **THE ONE MISS, AND IT IS ONE SEED WEARING TWO HATS**

**`fz2_w1 bars` read 10 / 11 where I registered 11 / 11.  That is a MISS and it
is reported as one.**

```
C-6   MISSED   hold_rows_exact 4637   hold_rows_off 1
      bad_detail: [{"seed": "fz2e/516044", "sched": "stim", "pin": "pin_int",
                    "hold": 300, "runs": [], "term_fired": 0}]
      directives 4638 · directive_ok 4637 · directive_bad 1
      holds_evaluated {"20": 3279, "300": 679, "2": 680}
```

**The single off-row is `fz2e/516044`, with an EMPTY run list and `term_fired`
0 — and `fz2e/516044` is one of this era's three `_ps3_8080` discards**
(`fz2c/402059`, `fz2e/509069`, `fz2e/516044`).  The seed entered 8080 mode at
runtime, so it never reached its terminator, so the pin-hold instrument had no
counted run to measure.

> ### **THE C-6 MISS AND THE DENOMINATOR MOVE ARE THE SAME EVENT.  ONE SEED RE-ROLLED INTO THE `_ps3_8080` CLASS AND IT TOOK ONE ROW OUT OF THE HOLD CENSUS WITH IT.**

⚠ **`_ps3_8080` IS A SOCKET-LEG PREDICATE (A-2) THAT NO RTL CHANGE CAN REACH**,
and it has re-rolled on **nine consecutive eras** (2 → 2 → 3 → 1 → 3 → 1 → 2 →
2 → **3**).  The discard *count* was registered **reported, not barred**, and
it is reported.  **But `bars` 11/11 was registered as a bar with no such
clause, and it is MISSED.  The miss is not re-scored on the strength of the
explanation.**

⚠ **C-6 has read off-rows before**: 4,636 / **2** on the FLASH #12 corpus
(`CLAUDE.md`, FLASH #18 line).  4,637 / 1 is inside that history and outside my
registration.  **Both facts are true and only the second one is a bar.**

---

## 11. HARD STOPS

**NONE FIRED.**

`f22_s1_derive` **PASS with both nulls failing** · RETENTION `draw@seed1`
**34.99 ≥ 32.0** · **N-1 PASS on the flashed `db`** with its control FAILing ·
the RETENTION receipt self-labelled **RETENTION** and its `.rbf` **differed**
from CONTROL's · `safe_flash` **VERIFY ok try 1** · **0 `div_guard` UNPINNED
anywhere in the sitting (61 probes)** · **0 `RigMismatch`, 0 quarantines,
0 run-error lines, 0 transport errors** · single writer asked before first
contact and again in `preflight`, **`--force` never used** · first light
**MATCH 800 ×3** · **C-5's flip count is ZERO of a 10-seed budget** · closing
chip proof **MATCH 800** · `board_idle()` **clean and last**.

**THE REGISTERED NON-STOPS, REPORTED WITH THEIR DENOMINATORS**: C-9's discard
re-roll (2 → 3, denominator 3,838 → 3,837), and **C-17's `fz2_w1 bars` row at
10 / 11 (§10)** — which is a MISS, not a non-stop, and is reported as a miss.

⚠ **NOTHING WAS RE-FLASHED.  NOTHING WAS ADJUSTED AND RETRIED.  NO REPAIR WAS
ATTEMPTED.**  The user authorised *a* flash and got exactly one: `flash_log`
**25 → 26**, one entry.

---

## 12. WHAT THIS SITTING ESTABLISHED, AND WHAT IT LEAVES OPEN

**ESTABLISHED**

1. ⭐⭐ **ARM-B IS BEHAVIOUR-NEUTRAL IN FABRIC**, on this part's whole 3,840-seed
   corpus: **102 of 102 seats exact in both columns, zero flips, zero
   unexplained rows over 11.3 million compared rows, every family cell
   unmoved, and all 30 named non-movers value for value.**  Offline neutrality
   became fabric neutrality.
2. ⭐ **AND IT IS AN ATTRIBUTION, NOT A NARROWING** — of 99 declared inputs
   exactly one moved, proved by hash from the tree **and** independently by the
   era guard from the socket's own receipt.  **This is the first single-mechanism
   fabric confirmation the timing campaign has taken.**
3. **THE ~2.4 MHz NO-EXCEPTION MARGIN COSTS NOTHING IN SILICON.**  The bitstream
   with **zero SDC timing exceptions** and ARM-B's folded `q_ripe_lead_n` select
   boots, runs the corpus, and closes out on a chip proof.
4. **S-1 STILL HOLDS STRUCTURALLY FOR THE RIG'S ENABLE TRAIN AT EVERY LEGAL
   DIVIDER**, re-derived on this tree with its own null **before** the board was
   touched — which matters more here than at FLASH #22, because ARM-B widens the
   shadow a violation would corrupt.
5. **THE OFFLINE CORE AND FABRIC AGREE AT 100.0 % OVER 252 SEEDS**, `first_bad`
   identical on 102 / 102, over a population whose size was registered in advance.
6. **G6 REPRODUCED A SECOND SITTING'S DRAWS TO THE BITSTREAM BYTE** on both
   configurations — the campaign's third such reproduction.
7. **`check_fuzz_bank` RUNS AGAIN AND READS PASS 621** on this tree, closing
   FLASH #22 §10's open item 3 by measurement rather than by decision.

**OPEN, WITH THEIR FALSIFIERS**

1. ⚠ **`fz2_w1 bars` C-6 at 4,637 / 1** (§10).  *Falsifier*: if `fz2e/516044`
   leaves the `_ps3_8080` class in a later era, C-6 must return to 4,638 / 0
   with no other change.
2. **The `_ps3_8080` discard predicate has re-rolled for the NINTH consecutive
   era and nothing explains the class.**  Inherited, untouched.
3. **FLASH #22's six closures remain attributed to a WINDOW, not a commit** —
   the two REP fixes (F22 §9.2).  Untouched here.
4. **`fz2e/516077` and FLASH #22's other four entrants are still
   unattributed** — but they are now **reproduced across two independent
   captures on two different bitstreams**, value for value, which is new
   evidence that they are seats and not capture noise.
5. **The IMMATERIAL census document is now three eras stale** (C-16c),
   deliberately not edited in the sitting that measured with it.
6. **`ucrom_mif_check` still prints `FAIL` and exits 0** (FLASH #21, unrepaired).
7. **`fz2_replay` is still structurally vacuous in a git worktree** (WAVE 19 §9
   item 4, booked for the fifth time).  Avoided here by running in the main tree.
8. ⚠ **`standing_gates.md` and `CLAUDE.md` ARE NOT EDITED BY THIS WAVE** (the
   WAVE 11-19 precedent; the coordinator decides).  Now owed, on top of WAVE
   19's list: **FLASH #23 itself**; **§A's *"`cutset_lint` IS RED IN THE TREE BY
   DESIGN"* paragraph, which is OUT OF DATE since `ce39ed61bf` and now measures
   PASS 81 / 0**; the `ss_lint` row (**232 / 229 / 4 / 0x8F / 0x8FE8**);
   `r7_lint`'s **41 `stop` sites**; bar **E11**; **`CE_HALF` as an unconditional
   core port**; ARM-B's `worst-of-5` pair **34.48 / 34.41**; and
   **`check_fuzz_bank` RUNNING AGAIN.**

**WHAT IT CANNOT ESTABLISH**: it measures **no Fmax** — one draw per
configuration, by ruling, and `standing_gates.md` §A governs.  It says
**nothing** about any other integrator's enable train.  And a null is evidence
of neutrality on **this corpus**, not a proof of equivalence.

---

## 13. DISCIPLINE, DECLARED AND KEPT

* **Single-writer asked FIRST**, of Quartus (`pgrep -x`, **one pattern per
  call**, six binaries, six calls) and of the board (`ssh … ps w`), **before any
  contact**, and again inside `preflight`.  `pgrep -f <script>` was never used
  against a script name.
* **THE WAITS BLOCKED; THEY DID NOT POLL A TURN** — one foreground
  `while pgrep -x quartus_… ; do sleep 20; done` per build, and the same shape
  for the capture and the replay.
* ⚠ **NO `cmd | tail -1; rc=$?` ANYWHERE.**  Every exit code was captured to a
  variable or read directly.  ⚠ **And `${PIPESTATUS[0]}` was found to print
  EMPTY in this session's `zsh`** — the array is `${pipestatus[1]}` there — so
  the construction was abandoned for direct capture rather than repaired.
* **No Codex.  No nested subagents.**
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  `hdl/nec_test_ucore.qsf` restored by `git checkout -- <that exact path>` before
  each Quartus run; `hdl/nec_test.qsf` and `hdl/nec_test.qpf` measured clean
  throughout — **no FSM revision was compiled** (WAVE 18's in-place-rewrite
  hazard).  **`git add` BY EXPLICIT PATH ONLY**, and
  **`sw/testdata/receipts/*.jsonl` IS NOT COMMITTED** — receipts are committed
  **BY VALUE** under `sw/testdata/flash23/`.
* **THE 21 PRE-EXISTING MODIFIED TRACKED FILES THAT ARE THE USER'S OWN
  UNCOMMITTED WORK ARE UNTOUCHED** — counted **21** before and **21** after, by
  name.
* **Archive by rename, never delete**: `fz2c`/`fz2e` → `*-F22-archive`, the four
  era JSONs → `*_F22-archive.json`.  The F22 per-clock rows are retained beside
  the F23 ones.
* `~/.cache/ucsimt-tmp/flash23/` for every intermediate; **nothing in `/tmp`.**
* **EVERY CLASSIFIER CARRIED A POSITIVE CONTROL, REPORTED FIRST**: the S-1
  checker's two nulls; `ucrom_mif_check`'s flipped bit (with a sha256-verified
  restore); `fz2_replay`'s **pre-flash REFUSAL** and its **printed population
  count**; `test_artifact`'s five rejections; `fz2_w1 control`'s **N1 negative
  control**; and the manifest diff, which was computed **against the flashed
  bitstream's own committed receipt** rather than against a remembered number.
* ⚠ **AND ONE INSTRUMENT TRAP WAS WALKED INTO AND CAUGHT**: a background
  `nohup … &` reported *"exit code 0"* for the **launching shell** while
  `check_fuzz_bank` was still running, and its partial 3-line output read as
  *"the gate produced no verdict"*.  **The gate had simply not finished.**  It
  was allowed to finish and read **PASS 621**.  *A launcher's exit code is not
  a tool's exit code* — the same shape as WAVE 19 §10.4's `rc=2` for a gate that
  was never invoked.
* ⚠ **CONTENT COMPARED, NOT A DIGEST ASSUMED**: the ledger seat for seat over
  **all 19 fields by name**, the row metric reconciled term by term, the 30
  named non-movers value for value, the manifest file by file by name, and the
  IMMATERIAL class counted from its own member lines.
* **Record what was measured, not what was expected** — §10 records the one bar
  I registered and missed, and §6.5 records a comparison I could **not** take
  and why.

---

## Appendix A — REVIEWER RE-RUN

```bash
git rev-parse HEAD                                  # the results commit
git log --oneline d5f5fca539..HEAD                  # the thirteen; two touch hdl/

# JOB 0 -- the manifest diff against the PREVIOUS bitstream's own receipt
python3 - <<'PY'
import json, sys
sys.path.insert(0,'sw'); import quartus_gate as q
old=json.load(open('sw/testdata/flash22/g6-retention-draw-seed1/distribution.json'))['input_manifest']
new=q.input_manifest(); of,nf=old['files'],new['files']
print([(k,of[k][:20],nf[k][:20]) for k in sorted(set(of)&set(nf)) if of[k]!=nf[k]])
print('rtl/core entries:', len([k for k in nf if 'rtl/core' in k]))
PY
# [('hdl/rtl/ucore/v30u_eu.sv','c70dee375f9b9df54aec','31ff3a50f503da773796')]   /   0

python3 sw/f22_s1_derive.py                         # D-1..D-3 with its nulls

# C-4..C-8 -- the null, seat for seat and FIELD FOR FIELD
python3 - <<'PY'
import json, hashlib, collections
A={f['seed']:f for f in json.load(open('sw/testdata/fz2/fz2_failure_ledger_f22_2026-09-19.json'))['failures']}
B={f['seed']:f for f in json.load(open('sw/testdata/fz2/fz2_failure_ledger_f23_2026-09-19.json'))['failures']}
print('entered',sorted(set(B)-set(A)),'left',sorted(set(A)-set(B)))
keys=sorted({k for f in A.values() for k in f}); d=collections.Counter()
for s in set(A)&set(B):
    for k in keys:
        if A[s].get(k)!=B[s].get(k): d[k]+=1
print('fields differing over the shared seats:', dict(d))
s={f['seed']:(f['diverging_rows'],f['first_bad_row']) for f in B.values()}
c=json.dumps(sorted((k,)+tuple(v) for k,v in s.items()), sort_keys=True)
print(len(s), hashlib.sha256(c.encode()).hexdigest(), sum(v[0] for v in s.values()))
PY
# entered [] left []
# fields differing over the shared seats: {'capture_sha256': 102}
# 102 c411a808926ca3bc392700b5c09e6f6a2c96a8fe41a7ad90597a632fb95d65f8 94014

python3 sw/fz2_replay.py --report sw/testdata/fz2/fz2_replay_f23.json   # 252/252
python3 sw/fz2_immaterial.py --ledger sw/testdata/fz2/fz2_failure_ledger_f23_2026-09-19.json falsify
python3 sw/fz2_w1.py bars ; python3 sw/fz2_w1.py lint
python3 sw/ss_lint.py --core ucore ; python3 sw/r7_lint.py ; python3 sw/cutset_lint.py
python3 sw/phase_split_lint.py ; python3 sw/test_artifact.py ; python3 sw/check_fuzz_bank.py
```

## Appendix B — THE BAR IN ONE TABLE

| clause | registered | measured | verdict |
|---|---|---|---|
| ⭐ **JOB 0** | one declared input of 99; archived core absent | **one: `v30u_eu.sv`**; 0 `rtl/core` entries; era guard **98/99** | **MET, twice over** |
| **D-1 … D-4** | derivation PASS, nulls FAIL, D=8 clean, PINNED 100 % | all four | **MET** |
| E-1 … E-12 | G6 green both legs, manifest 99/`ee6a4eff46e483d3…`, `.rbf`s differing, E11 pass | all, both legs | **MET** |
| **N-1 / N-1b** | PASS on the flashed `db`; control FAILs | **PASS** 8192 + 1028 words; **`[BAD]` on one flipped bit** | **MET** |
| **N-2** | first light MATCH 800 ×3 | **MATCH ×3, twice** | **MET** |
| **F-1** | VERIFY OK, log 25 → 26 | **ok try 1, 26 entries** | **MET** |
| ⭐ **C-4** | **102**, band [92,112] | **102 — the POINT** | **MET** |
| ⭐ **C-5** | 0 entered, 0 left, budget 10 | **0 / 0 / 0 flips** | **MET** |
| ⭐ **C-6** | digest `c411a808…`, 102/102 | **digest IDENTICAL; 102 / 102 EXACT** | **MET** |
| C-7 | 0 LOST, 0 earlier | **0 / 0** | **MET** |
| C-8 | Σ 94,014, 0 unexplained | **94,014, 0 unexplained** | **MET** |
| C-9 | discards 2 (reported, not barred) | **3**, denominator **3,837**, membership re-rolled | **reported, not barred** |
| C-9b | families; overlay 4 | **all fifteen cells identical**; overlay **4** | **MET** |
| C-10 … C-15 | 30 non-movers, `404040` ABSENT | **30 of 30** | **MET** |
| C-16a … C-16d | class 22 (17+5); 41/28/5/17/11; FAIL at G6 4/8, G7 1/23; the five seats | **all four exactly** | **MET** |
| **C-17** | fourteen standing gates | **thirteen MET**; **`fz2_w1 bars` 10 / 11 — C-6** | **MISSED on one — §10** |
| Q-1 | REFUSE naming ONE file before, PASS after | **98/99 REFUSED naming `v30u_eu.sv`, 99/99 PASS after, no bypass** | **MET** |
| Q-2 | ≥ 99 %, `first_bad` identical, population 252 | **252 / 252 = 100.0 %, 102 / 102, population 252** | **MET** |
| Q-3 | chip proof, PINNED, idle last | **MATCH 800, 61/61 PINNED, idle OK and last** | **MET** |

**A FABRIC FIGURE TAKEN ON ANY EARLIER FLASH MAY NOT BE QUOTED AGAINST THIS
TREE.**
