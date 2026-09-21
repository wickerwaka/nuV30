# FLASH #24 — RESULTS, AS REGISTERED: **THE `ea_pair_valid` FIX IS IN SILICON-ON-FPGA AND THE EA LANE IS 21 / 21 PAIRWISE IN FABRIC.  THE SIX PREDICTED SEEDS CLOSED, BY NAME, AND ONE UNREGISTERED SEED OPENED — SO THE FIX IS NET +5 AND ITS FIRST MEASURED COST IS NAMED.**

Pre-registration `eb3be735a1`
(`docs/notes/flash24_prereg_2026-09-21.md`), committed **before any board
contact** — both Quartus builds preceded it and are offline.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

Every bar is reported in the form it was registered in.  **Nothing is
re-registered after the fact.  A miss is a miss, and there are two.**

    branch       master
    HEAD         74a2e62cd2 -> prereg eb3be735a1 (the built tree)
    hdl/         tracked-clean; byte-identical to WAVE 26's landing 427a3f5a10
    bitstream    nec_test_ucore.sof  3066d40a558486c61becf490c451d351a5c3da8156109f6fbedd2927f0ae1833
                 nec_test_ucore.rbf  44cfd64791781752e89f1a86be9cafd85471dc32fb1aa9ce17ee4ae8023418c7
                 RETENTION (X1_AD_RETENTION=1), draw@seed1
                 receipt 8077ba94656880ef44afdc461c67083ab2e24111464be285f89bf52199a6f8dc
    flash        2026-09-21T18:19:30Z, sw/safe_flash.sh, VERIFY ok on TRY 1
    flash log    26 -> 27 entries   13a81a43f30c380a… -> 7496b4be2d1771c9…
    authorised   USER, 2026-09-21: "Flash it"

---

## 0. THE HEADLINE

> ### **1. ⭐⭐⭐ THE PRIMARY BAR IS MET ON THE POINT.  `PAIRWISE MATCH 21 / 21`, CORE vs SOCKET, SAME IMAGES, SAME SESSION.**
>
> The FPGA core now reproduces the socketed uPD70116 on **every one** of the
> 21 directed `LEA SI,DI (mod=3)` probes, including all eight `mod = 01/10`
> rows WAVE 26 composed *after* the RTL was written.  **`P1` — the sharpest
> row, a `mod = 01` form whose displacement is ZERO — reads `1111` in fabric,
> which is what silicon says and not what *"B = the index"* predicts.**
> **P-1 · P-1b · P-2 · P-4 all MET.**
>
> ### **2. ⭐⭐ AND THE NON-VACUITY CONTROL, TAKEN BEFORE THE FLASH, HIT 21 OF 21 TOO — IN THE OTHER DIRECTION.**
>
> On the RESIDENT FLASH #23 bitstream the same rig read **PAIRWISE 7 / 21**,
> and the FPGA core's column was **value-for-value identical to the
> PRE-LANDING Verilator column**, 21 rows of 21.  **A rig that reads 21/21 on
> both bitstreams is measuring the socket twice; this one does not.**  P-5
> registered the cross-harness risk as a possible FINDING — **it did not
> materialise: the FPGA core and `tb_bootrun` agree exactly, on both trees.**
>
> ### **3. ⭐⭐ THE SIX PREDICTED SEEDS CLOSED, BY NAME, AND THE 96 SURVIVORS ARE BYTE-IDENTICAL SEAT FOR SEAT.**
>
> `fz2c/406054 · fz2c/408019 · fz2e/518038 · fz2e/520013 · fz2e/529009 ·
> fz2e/531039` — **exactly the six**, derived offline before the board was
> touched.  **Three of them are three of FLASH #23's own `C-14` "M10 LEA-mod3
> six", registered there as NON-movers.**  The survivor digest is
> **`9d89bb62b6507f3b37d75e63eb3a291f7d45f7b321efc862747e4c4daea5d7cb` —
> IDENTICAL to the registered one**, **0 seat movers**, **0 `first_bad`
> EARLIER anywhere**.
>
> ### **4. ⚠⚠ AND ONE SEED OPENED THAT WAS NOT REGISTERED.  `C-4` AND `C-6` ARE MISSED AND ARE REPORTED AS MISSED.**
>
> The ledger reads **97**, not the registered **96**; **ENTERED is 1, not
> 0** — **`fz2e/527035`**, a raw-tier random-byte seed, **1 of a 10-seed
> budget**.  It was **outside the 252-seed offline population** (the sample is
> 150 of ~3,738 passing seeds), so the instrument had no opportunity to
> predict it.  ⭐ **AND IT IS ATTRIBUTED, NOT GUESSED**: replayed on a
> PRE-LANDING worktree against the *same* image and the *same* banked socket
> rows it scores **`bad: 0`**; on the landed tree it scores **753**, `first_bad`
> 431, **reproducing fabric to the row**.  **The one delta is the four
> `hdl/rtl/ucore/` files.  It is the fix's first measured cost, and the fix is
> net +5.**
>
> ### **5. THE SAME A/B PROVES THE SIX CLOSURES ARE THE FIX'S, NOT THE ERA'S.**
>
> On the pre-landing worktree the six closers score **FAIL 6 / 6 with
> `first_bad` IDENTICAL to FLASH #23's fabric**; on the landed tree they score
> **PASS 6 / 6**.  Same seeds, same images, same socket rows, one delta.
>
> ### **6. THE ERA GUARD SAID IT TWICE AND THE CLOSING CONTROL IS PERFECT.**
>
> **REFUSED before the flash** naming the six moved files; **PASSED after it
> with NO bypass and `98 / 98` inputs identical — the `.qsf` exemption was not
> even needed.**  `fz2_replay --all-failures --pass-sample 150 --leg ret`:
> **247 / 247 = 100.0 %**, `first_bad` **IDENTICAL on 97 / 97**, 0 errors.
>
> ### **7. HYGIENE PERFECT.**  First light **MATCH 800 ×3** (twice), **63
> `div_guard` probes and ZERO UNPINNED**, 0 `RigMismatch`, 0 quarantines,
> 0 transport errors, 3,840 seeds in **10.9 min**, 48 / 48 strata all `rc 0`,
> closing chip proof **MATCH over 800 rows**, `board_idle` **clean and LAST**.
> `fz2_w1 bars` **11 / 11 MET** — **up from FLASH #23's 10 / 11**, with C-6's
> `hold_rows_off` back to **0**.
>
> ### **8. G6 GREEN ON BOTH CONFIGURATIONS, AND BOTH `.rbf`s REPRODUCE WAVE 26's OWN DRAWS BYTE FOR BYTE.**
> CONTROL **34.35 / +2.135 / 8,438 ALMs** · RETENTION **34.59 / +2.337 /
> 8,495 ALMs**, TNS 0.000 setup AND hold on all four domains of both, 0
> latches / 0 `lpm_divide` / 0 error lines, **`.rbf`s DIFFER (E-9)** and
> **`configuration` DERIVED self-labels RETENTION (E-6)**.

---

## 1. ⭐ **JOB 0 — WHAT IS IN FLASH #24 THAT WAS NOT IN FLASH #23.  FROM HASHES, TWICE, BY TWO INDEPENDENT INSTRUMENTS.**

`git log --oneline 6de3e322b5..HEAD` = **44 commits**; **five** touch `hdl/`.

| commit | what | in the ucore revision? |
|---|---|---|
| `a2d619d2d8` | WAVE 21 — remove the ARCHIVED FSM core (−10,143 lines of `hdl/rtl/core/`) | **NO** |
| `0c7c9df595` | WAVE 21 — re-base the Quartus project onto the ucore | **YES, as PLUMBING** |
| `a09f34defd` | WAVE 21 — delete the FSM probe block from `hdl/tb/tb_v30_core.sv` | **NO** (`hdl/tb/` is not a declared input) |
| `56bdf8d851` | WAVE 25 — the TB settle window (`hdl/tb/tb_v30_core.sv`) | **NO** |
| ⭐ `427a3f5a10` | **WAVE 26 — the `ea_pair_valid` second-addend fix**, 4 files, all `hdl/rtl/ucore/` | **YES — AND IT IS THE ONLY BEHAVIOUR-CAPABLE CHANGE IN THE WINDOW** |

### 1.1 The manifest diff (§0.1 of the prereg, re-stated as measured)

```
old  99 files  ee6a4eff46e483d3      new  98 files  07796a3630faee56
ONLY IN FLASH23 : ['hdl/nec_test.qsf']       ONLY IN TREE : []
MOVED (6): files_ucore.qip · nec_test_ucore.qsf   [WAVE 21 plumbing]
           v30u_eu.sv · _arm_bind.svh · _arm_ea_calc.svh · _step.svh  [WAVE 26]
rtl/core entries in the new manifest: 0
```

### 1.2 The second instrument, from the socket's side — **and it said it in BOTH directions**

* **BEFORE the flash**: `fz2_replay`'s fabric era guard **REFUSED, exit 1**,
  `92 / 99` identical, naming the same six files.
  (`sw/testdata/wave28/era_guard_preflash.txt`)
* **AFTER the flash**: **PASS with NO bypass**, and — stronger than registered
  — **`its inputs 98/98 hash IDENTICAL in the tree at HEAD`**, i.e. even the
  declared `.qsf` exemption was not needed.

---

## 2. THE BUILD — G6 (`E-1` … `E-9`)

| # | bar | registered | **measured** | verdict |
|---|---|---|---|---|
| **E-1** | `nec_test.sdc` anchored exception count | **0** | ⭐ **0** (unanchored 2 = the commented DO-NOT-RESTORE record; the file is byte-untouched) | **MET** |
| **E-2** | `qsf_lint --check` | CANONICAL | **CANONICAL**, both builds | **MET** |
| **E-3** | Fmax ≥ 32 MHz | ≥ 32 | **CONTROL 34.35 · RETENTION 34.59** | **MET** |
| **E-4** | worst setup > 0 | > 0 | **+2.135 · +2.337 ns** | **MET** |
| **E-5** | TNS 0.000 setup **and** hold, every domain | 0.000 | **0.000 on all four domains of both builds, both directions** | **MET** |
| **E-6** | `--retention`, env var REFUSED, configuration DERIVED | exit 2 / self-label | ⭐ **`X1_AD_RETENTION=1 python3 sw/quartus_gate.py --dry-run` → exit 2** naming the FLASH #18 finding; `quartus_map` command line carries `--verilog_macro=X1_AD_RETENTION=1`; `configuration` **DERIVED** = `RETENTION (X1_AD_RETENTION=1)` | **MET** |
| **E-7** | **E-9**, the two `.rbf`s differ | differ | ⭐ **`aa931892f7a69668…` ≠ `44cfd64791781752…`** | **MET** |
| **E-8** | 0 latches · 0 `lpm_divide` · 0 error lines | 0/0/0 | **0 / 0 / 0**, both | **MET** |
| **E-9** | input stability (E7) | 1 exempt file | **PASS**, `OFFENDING []` | **MET** |

    CONTROL    34.35 MHz  +2.135 ns  8,438 / 41,910 ALMs (20 %)  regs 6,843
               receipt ed3a61f3ee0bc553…   rbf aa931892f7a69668…   PASS
    RETENTION  34.59 MHz  +2.337 ns  8,495 / 41,910 ALMs (20 %)  regs 7,104
               receipt 8077ba94656880ef…   rbf 44cfd64791781752…   PASS  <-- FLASHED

⭐ **BOTH `.rbf`s ARE BYTE-IDENTICAL TO WAVE 26's OWN seed-1 DRAWS**
(`aa931892f7a69668…`, `44cfd64791781752…`) with Fmax reproducing to the
hundredth (34.35 / 34.59) a day and two trees apart — **the fourth cross-wave
bitstream-payload reproduction of the campaign.**  Recorded, not barred.
⚠ **N = 1 per configuration.  NOT an Fmax claim** (USER RULING 2026-08-13).

---

## 3. ⭐⭐⭐ **THE PRIMARY BAR — THE EA-LANE LAW IN FABRIC**

**THE RIG**: `sw/w28_ea_lane_fabric.py`, committed with the pre-registration.
For each of the 21 probes it captures the **same composed image twice,
back-to-back in one session** — `EMIT_USE_CORE = False` (the socketed chip)
then `EMIT_USE_CORE = True` (the in-FPGA `v30_core`) — and scores them
**PAIRWISE**.  `use_core` is passed explicitly on every capture and each leg
stamps its own provenance from the value actually passed.

### 3.1 ⚠ THE NON-VACUITY CONTROL, **TAKEN BEFORE THE FLASH** (P-3, P-5)

`--expect before`, on the resident FLASH #23 bitstream
(`sw/testdata/wave28/ea_fabric_preflash/`):

```
PAIRWISE (core vs socket, same images): MATCH 7 / 21   DIVERGE 14
POSITIVE CONTROL (socket vs WAVE 26 banked socket): REPRO 21 / 21   MOVED 0
CORE vs the registered `before` column: HIT 21 / 21   MISS 0
DIVIDER READBACK: div=8 (4 MHz), commanded by this connection
```

**P-3 MET ON THE POINT, ALL 21 VALUES.**  The FPGA core read
`R1 9211 · R2 4dcc · M4…M7 9211 · P0 8888 · P1 8888 · P2 9211 · P3 9211 ·
P4 9999 · P5 9211 · P6 9211 · P7 9211` — the pre-landing Verilator column,
value for value.

⭐ **P-5's REGISTERED RISK DID NOT MATERIALISE.**  It was registered that a
cross-harness difference (Verilator `tb_bootrun` vs the FPGA core inside
`system_large`) would be a FINDING.  **There is none: 21 / 21 on the pre-flash
tree and 21 / 21 on the post-flash tree.**

### 3.2 ⭐ THE BAR ITSELF (P-1, P-1b, P-2, P-4)

`--expect after`, on FLASH #24 (`sw/testdata/wave28/ea_fabric_postflash/`):

| tag | predecessor | prose | **SOCKET** | **CORE** | | W26 socket |
|---|---|---|---:|---:|---|---|
| `C1` | `a3 34 12` | `MOV [1234h],AW` | `1234` | **`1234`** | MATCH | REPRO |
| `C2` | `a3 ef be` | `MOV [BEEFh],AW` | `beef` | **`beef`** | MATCH | REPRO |
| `C3` | `90` | `NOP` (no EA) | `2222` | **`2222`** | MATCH | REPRO |
| `R1` | `88 26 10 30` | `MOV [3010h],AH` | `4121` | ⭐ **`4121`** | MATCH | REPRO |
| `R2` | `8b 0e 55 44` | `MOV CW,[4455h]` | `1121` | ⭐ **`1121`** | MATCH | REPRO |
| `M0`–`M3` | `89 00…03` | two-register | `8888 9999 8888 9999` | **same** | MATCH ×4 | REPRO ×4 |
| `M4` | `89 04` | `MOV [IX],AW` | `1111` | ⭐ **`1111`** | MATCH | REPRO |
| `M5` | `89 05` | `MOV [IY],AW` | `1111` | ⭐ **`1111`** | MATCH | REPRO |
| `M6` | `89 06 34 12` | `MOV [1234h],AW` | `2345` | ⭐ **`2345`** | MATCH | REPRO |
| `M7` | `89 07` | `MOV [BW],AW` | `1111` | ⭐ **`1111`** | MATCH | REPRO |
| `P0` | `89 40 10` | `[BW+IX+10h]` | `1121` | ⭐ **`1121`** | MATCH | REPRO |
| **`P1`** | `89 40 00` | **`[BW+IX+0]`** | **`1111`** | ⭐⭐ **`1111`** | MATCH | REPRO |
| `P2` | `89 46 10` | `[BP+10h]` | `1121` | ⭐ **`1121`** | MATCH | REPRO |
| `P3` | `89 84 34 12` | `[IX+1234h]` | `2345` | ⭐ **`2345`** | MATCH | REPRO |
| `P4` | `89 81 34 12` | `[BW+IY+1234h]` | `2345` | ⭐ **`2345`** | MATCH | REPRO |
| `P5` | `89 45 20` | `[IY+20h]` | `1131` | ⭐ **`1131`** | MATCH | REPRO |
| `P6` | `89 87 34 12` | `[BW+1234h]` | `2345` | ⭐ **`2345`** | MATCH | REPRO |
| `P7` | `89 44 f0` | `[IX−10h]` | `1101` | ⭐ **`1101`** | MATCH | REPRO |

```
PAIRWISE (core vs socket, same images): MATCH 21 / 21   DIVERGE 0
POSITIVE CONTROL (socket vs WAVE 26 banked socket): REPRO 21 / 21   MOVED 0
CORE vs the registered `after` column: HIT 21 / 21   MISS 0
DIVIDER READBACK: div=8 (4 MHz), commanded by this connection
```

| # | bar | registered | measured | verdict |
|---|---|---|---|---|
| **P-1** | pairwise core vs socket | **21 / 21** | ⭐ **21 / 21** | **MET, ON THE POINT** |
| **P-1b** | WAVE 24's thirteen | 13 / 13 | ⭐ **13 / 13** | **MET** |
| **P-2** | the socket positive control | 21 / 21 REPRO, value for value | ⭐ **21 / 21, 0 MOVED**, both runs | **MET** |
| **P-3** | the pre-flash non-vacuity control | 7 / 21, values named | ⭐ **7 / 21, HIT 21/21 on the named values** | **MET** |
| **P-4** | `P1` reads `1111` | `1111` | ⭐ **`1111`** | **MET** |
| **P-5** | a cross-harness difference is a FINDING | — | **NONE** | **no finding** |

Column files with sha256 in each manifest:
`ea_fabric_preflash/8D_socket.json.gz` `320cecc565b0ff63…` ·
`8D_core.json.gz` `1bc4662f1c37119c…` ·
`ea_fabric_postflash/8D_socket.json.gz` `4ee8da5568307c32…` ·
`8D_core.json.gz` `38e61b897e8ae324…`.  **Full per-clock rows retained in
every one.**

> ### ⭐ **THE F42 PRECEDENT DID NOT REPEAT.**  WAVE 26's law was derived on
> Verilator and on the socket; the synthesised core, asked the same 21
> questions through the same pads, gives the same 21 answers.

---

## 4. **THE CORPUS — SIX CLOSED AS REGISTERED, ONE OPENED THAT WAS NOT**

`fz2_w1 lint` → `control` → `preflight --board` → `capture` → `fz2_ledger`,
scored against `fz2_failure_ledger_f23_2026-09-19.json`.  `fz2c`/`fz2e` were
**archived by rename** to `*-F23-archive` (493 + 145 capture files retained
beside the new 493 + 145) and the manifests re-pinned by `fuzz_campaign.py
new`; the four F23 era JSONs archived to `*_F23-archive.json` **before**
anything overwrote them.  **Nothing was deleted.**

| # | bar | registered | **measured** | verdict |
|---|---|---|---|---|
| **C-1** | corpus identity | 3,840 / 48 strata / lint PASS | **3,840**, **48 strata**, lint **PASS / 0 hits / 48 stratum rows** | **MET** |
| **C-2** | completeness | 48/48, every `rc 0` | **48 / 48, every `rc 0`, every `n = 80`**, 960 + 2,880 in **10.9 min** | **MET** |
| **C-3** | the flash pin | `distinct_eras` 1 | **`distinct_eras` 1 · `absent` 0 · `incomplete` 0 · `build_stale` 0** over 3,840; era sof **`3066d40a558486c6…`** | **MET** |
| **C-4** | ⭐ **THE HEADLINE** | **96**, band [86, 106] | ⚠ **97** — **inside the band, the POINT MISSED BY ONE** | ⚠ **MISSED, reported as registered** |
| **C-5** | ⭐⭐ **the six, by name** | the six named | ⭐ **EXACTLY THOSE SIX LEFT**, by family `A3` 2 · `D3` 1 · `E1` 3 | **MET ON THE POINT** |
| **C-6** | flips outside the six | **0 ENTERED, 0 LEFT**, budget 10 | ⚠ **0 LEFT · 1 ENTERED — `fz2e/527035`.  1 of 10 budgeted** | ⚠ **MISSED, within budget, itemised** |
| **C-7** | ⭐ the surviving seat table | digest `9d89bb62b6507f3b…`, 96/96 | ⭐ **digest `9d89bb62b6507f3b37d75e63eb3a291f7d45f7b321efc862747e4c4daea5d7cb` — IDENTICAL; 96 / 96 seats EXACT, 0 movers in EITHER column** | **MET** |
| **C-8** | direction | 0 LOST, 0 `first_bad` EARLIER | ⭐ **0 LOST · 0 `first_bad` EARLIER ANYWHERE** | **MET** |
| **C-9** | the row metric | Σ 94,014 → 86,965, **0 unexplained** | **94,014 → 87,718**, and it **RECONCILES EXACTLY**: `86,965 (survivors) + 753 (the entrant) = 87,718`.  **ZERO unexplained rows.**  `rows_diverging` 93,955 → **87,660**; row match 99.1705 % → **99.2263 %** | **MET** |
| **C-9b** | families | `…A3 13 · D3 3 · E1 35 · NEW 5 = 96` | **A1 5 · A2 4 · A3 13 · B1 1 · B2 2 · C1 1 · C2 8 · C3 1 · C4 1 · D1 8 · D2 7 · D3 3 · E1 35 · E2 2 · NEW/UNCLASSIFIED 6 = 97** — every cell as registered, **`NEW` 5 → 6 is the one entrant** | **MET but for the entrant** |
| **C-9c** | discards | reported, not barred | ⚠ **3 → 1** (`fz2e/509069` alone; `fz2c/402059` and `fz2e/516044` stopped entering 8080 at runtime), denominator **3,837 → 3,839**.  **A SOCKET-leg predicate (A-2) no RTL change can reach — TENTH consecutive era it has moved** | **reported, not barred** |
| **C-9d** | §38.9 missed-trap overlay | 4 | **4, the SAME four** (`fz2c/406073`, `fz2c/407064`, `fz2e/518039`, `fz2e/518044`) | **unmoved** |

Seed match **97.3417 % → 97.4733 %**.

### 4.1 ⭐⭐ **THE SIX, AND THE A/B THAT MAKES THEM THE FIX'S**

| seed | family | F23 `rows / first_bad` | F24 |
|---|---|---:|---|
| `fz2c/406054` | `E1 same-status data cycle, different address` | 3141 / 470 | **ABSENT** |
| `fz2c/408019` | `E1` | 1087 / 1617 | **ABSENT** |
| `fz2e/518038` | `E1` | 194 / 429 | **ABSENT** |
| `fz2e/520013` | `D3 both fetched, different address` | 2615 / 960 | **ABSENT** |
| `fz2e/529009` | `A3 cycle-time slip (non-qs)` | 8 / 908 | **ABSENT** |
| `fz2e/531039` | `A3` | 4 / 1012 | **ABSENT** |

⭐ **`fz2c/406054`, `fz2c/408019` and `fz2e/518038` ARE THREE OF FLASH #23's
`C-14` "M10 LEA-mod3 six"**, registered *there* as non-movers, predicted *here*
as movers, **by the wave that owns the mechanism.**

**THE A/B**, on a `git worktree` at `56bdf8d851` (WAVE 25, i.e. the tree
immediately before the landing), `tb_sys` rebuilt there, receipt
`3ca720bf73bf3ed8…`, scored against the **same banked socket rows** and the
**same regenerated images**:

```
  pre-landing core, the six closers :  replay FAIL 6 / 6,  first_bad IDENTICAL on 6
  landed core,      the six closers :  replay PASS 6 / 6      (§4 and the prediction run)
```

**Same seeds, same images, same socket rows.  One delta: the four
`hdl/rtl/ucore/` files.**

### 4.2 ⚠⚠ **THE ONE ENTRANT — `fz2e/527035` — ITEMISED AND ATTRIBUTED**

```
seed  fz2e/527035   tier raw   family NEW/UNCLASSIFIED   banked_verdict FUNCTIONAL
sub   func:W@29     first_bad_row 431   diverging_rows 753   compare_window 4000
arch  AW,BP,BW,CW,DS0,DS1,DW,IX,IY,PC,PS,PSW,SP   (arch_match False)
mech  REACHED       done_chip True   done_core True
image 41614003a4e52c86…  (regenerates EXACTLY; no GEN-DRIFT)
```

* **It was OUTSIDE the 252-seed offline population.**  The pre-registration's
  prediction was derived from 102 known failures **plus a 150-seed sample of
  ~3,738 passing seeds**, i.e. **6.6 % of the corpus.**  The instrument had no
  opportunity to see this seed.  **That is exactly what the 10-seed budget is
  for, and 1 of 10 was used.**
* ⭐ **IT IS THE FIX's, AND THAT IS MEASURED, NOT INFERRED FROM THE WINDOW
  ALONE.**  On the pre-landing worktree, same image, same banked socket rows:
  **`bad: 0`, `first: None`** — the old core PASSES it.  On the landed tree:
  **`bad: 753`, `first: 431`** — and fabric reads **753 / 431** too.  **The
  offline and fabric columns agree to the row.**
* **It is a RAW-tier random-byte program** (`lea_mod3_pos` is `None`; it is not
  a directed LEA seed).  **It is NOT classified further here** — classifying it
  is a wave of its own, and guessing a family would be exactly the absorption
  `fz2_ledger` refuses to do.
* **NET: the fix closes six and opens one.  +5 on a 3,839-seed denominator.**

### 4.3 `fz2_w1 bars` — ⭐ **11 / 11 MET, UP FROM FLASH #23's 10 / 11**

`C-1` MET (rate clauses validated on the disjoint `fz2v`/960) · `C-2` MET ·
`C-3` MET (`bad_0f_pairs` 0, `gen` ok) · `C-4` MET (`distinct_eras` 1) ·
`C-5` MET (**`gen_drift` 0, `wvec_mismatch` 0** over 3,840) · ⭐ **`C-6` MET —
`hold_rows_exact` 4,638 / `hold_rows_off` 0**, where FLASH #23 read 4,637 / 1 ·
`C-7` MET (`at_or_over` 0) · **`C-8` MET — `div_guards` 63, `unpinned` 0** ·
`C-9` MET (192 stable / 0 unstable / 0 errors) · **`C-10` MET — quarantines 0,
run errors 0, `halted` null** · `C-11` MET.
census `rows-exact` **97.71** / `arch-exact` **90.31**; enriched **97.36** /
**90.66**.

### 4.4 `fz2_immaterial falsify` — **MEASURED, NOT REGISTERED, AND UNCHANGED IN KIND**

**G1 · G2 · G3 · G4 · G5 · G8 PASS; G6 and G7 FAIL** — the same inherited
document staleness FLASH #23 registered as **C-16c** (the census document is
still pinned to the F20 era's 44 / 30 / 106 / 84).  **NOT this wave's finding
and NOT repaired here.**  The live derivation is **`FUNCTIONAL 37 · TIMING 28 ·
COSMETIC 16 · TRANSIENT 5 · UNSCOREABLE 11 = 97`, `IMMATERIAL` 21, working
residue 76**, `TIMING_RECONVERGED` 7.  G7's *"named but NOT derived:
`fz2e/529009`"* is **one of the six closers** — the document names a seed that
has left.

---

## 5. `mod3_illegal` — **UNMOVED AT 0 / 128** (`M-1`, `M-2`)

`check_core --core ucore --suite-dir tests/v30/mod3_illegal --opcodes all
--cases 0` reads **0 / 128 arch, 128 / 128 cycles** (`ladder/x_mod3.log`).
**M-1 MET.**  WAVE 23 §3's reason is structural and a flash cannot reach it:
the 128 goldens have no ModR/M predecessor, their outcome depends on
*pre-window* `ea_residue`, and `tb_v30_core.sv:1120` injects fourteen
architectural registers and nothing else.
**M-2 MET: `ea_residue` was NOT injected into the TB.  STOP S-4 held.**

---

## 6. FIRST LIGHT, THE ERA GUARD, THE CLOSING CONTROLS (`N-1` … `N-4`)

| # | bar | registered | **measured** | verdict |
|---|---|---|---|---|
| **N-1** | first light | MATCH 800 ×3 | ⭐ **`chip-vs-golden` MATCH 800 · `core-vs-chip` MATCH 800 · `core-vs-golden` MATCH 800** — and again inside `preflight --board` | **MET, twice** |
| **N-2** | era guard after the flash | PASS, no bypass | ⭐ **PASS, `98 / 98` inputs IDENTICAL — the `.qsf` exemption not even needed** | **MET, stronger than registered** |
| **N-3** | closing control | ≥ 99 % over 246 | ⭐ **247 / 247 = 100.0 %**, `first_bad` **IDENTICAL on 97 / 97**, 0 errors, 21 s; 100 % in **every wait mode, both stimulus classes and all fifteen families** | **MET** |
| **N-4** | closing chip proof | MATCH 800 | ⭐ **`chip-vs-golden: MATCH over 800 rows`**, `use_core=0` explicit, after everything | **MET** |

---

## 7. BOARD HYGIENE (`B-1` … `B-7`)

| | |
|---|---|
| authorisation | **USER, 2026-09-21: *"Flash it"*** |
| single-writer | `pgrep -x ssh` → **none**, `pgrep -x quartus_pgm` → **none**, before first contact; `preflight` confirmed **no v30/serve process on the board → SINGLE WRITER** |
| `use_core` | **passed EXPLICITLY on every probe.**  Socket legs `use_core=False`, core legs `use_core=True`, **each named in the rig's output and in its manifest**; board left `use_core=0` |
| divider | **`div_guard` on every probe.**  `fz2_w1 bars` **C-8: `div_guards` 63, `unpinned` 0**; the capture's own 48 strata all PINNED; both EA-rig sessions ended `div=8 (4 MHz), commanded by this connection`.  ⭐ **ZERO UNPINNED ANYWHERE.  STOP S-2 did not fire** |
| probes | **42 + 42** (the two EA runs) **+ 3,840** (the corpus) **+ 9 control legs / 51 checks** **+ 800 ×3 ×2** (first light, twice) **+ 800** (closing proof) **+ `board_idle`** |
| retention | **full per-clock rows retained everywhere**, each column file's sha256 in its manifest; 493 + 145 corpus captures **and the FLASH #23 era retained beside them** at `*-F23-archive/captures/` |
| `fz2_w1 control` | **9 legs / 51 checks / 51 PASS / 0 FAIL**, holds `[2, 20, 300]` proved on `pin_int` and `pin_nmi`, **N1 negative control PASS**, 10 div guards / 0 unpinned |
| `preflight --board` | **OK** — single writer, era pinned to receipt `8077ba946568…` **self-labelling RETENTION**, regeneration sample **192 seeds / 0 hits**, RBCHECK **8 registers**, MATCH 800 ×3 |
| transport errors | **0** |
| `RigMismatch` | **0** |
| quarantines | **0** |
| `flash_log.jsonl` | **26 → 27**, `13a81a43f30c380a…` → `7496b4be2d1771c9…`, `verify: OK`, **TRY 1** |
| `board_idle()` | ⭐ **run LAST, clean**, `use_core=0` left selected, divider PINNED |

**NO HARD STOP FIRED.  S-1 … S-6 all silent.  S-7 (a missed P-1) did not
arise.**

---

## 8. THE OFFLINE LADDER (`F-9`)

Driver `sw/testdata/wave28/w28_ladder.sh`, logs by value at
`sw/testdata/wave28/ladder/`, **every `RC` captured with `${PIPESTATUS[0]}`**.
This wave edits **no `hdl/`**, so the registered expectation is
**zero-delta against WAVE 27**.

<!-- LADDER-TABLE -->

---

## 9. ⚠ FLASH #23 IS HISTORY.  **FLASH #24 IS THE BOARD.**

**NO FABRIC FIGURE TAKEN ON FLASH #23 OR EARLIER MAY BE QUOTED AGAINST THIS
TREE.**  Stated here, in `CLAUDE.md`'s banner, and in `standing_gates.md`.

---

## 10. DOCUMENTATION DISCREPANCIES — **REPORTED AS A FLOOR**

| # | where | what is wrong | disposition |
|---|---|---|---|
| **D-1** | `sw/emit_suite.py::_truth_stamp()` | it returns the constant `"SOCKET (real chip, use_core=False)"` whenever `ENGINE == "chip"` and **never consults `EMIT_USE_CORE`**, so on a **core** leg it writes a provenance line that is **false**.  Its own docstring says *"A provenance line that cannot be wrong is not provenance."* | **RECORDED, SOURCE NOT EDITED.**  `sw/w28_ea_lane_fabric.py` stamps each leg from the value it actually passed, and says in its module docstring why it may not use `_truth_stamp()`.  Fixing `emit_suite` is a change to the golden emitter's provenance line and belongs to whoever next needs a core-leg emitter |
| **D-2** | `sw/fz2_ledger.py:89` `CURRENT` | it is still pinned to **`fz2_failure_ledger_f20_2026-08-12.json`** — **four eras stale**.  Its own comment says *"`CURRENT` is the live one … so there is ONE place to move when the next re-capture lands"*, and it has not moved since FLASH #20.  Consequence, measured twice this sitting: `fz2_replay` and `fz2_immaterial` both **defaulted to the F20 ledger and refused** (`CAPTURE SHA MISMATCH`, `ERA MISMATCH`) until `--ledger` was passed | ⚠ **RECORDED, NOT MOVED.**  Moving it re-points every consumer's default in one edit and this wave did not register that.  **Every consumer PRINTS the file it read**, which is why both refusals were legible — the mechanism works, the pin is stale |
| **D-3** | `CLAUDE.md` gate quick reference | it still presents `ss_lint` as **`0x8D / 226 / 0x8DE2 / 214 flops`** and the WAVE 7 banner as *"232 / 228 flops"*; the tree measures **232 / 229 / 4 whitelist / 0 UNMAPPED** | **PRE-EXISTING, RE-CONFIRMED.**  `standing_gates.md` §B is correct; `CLAUDE.md` is not.  WAVE 26 and earlier already booked it; not repaired here because this wave's `CLAUDE.md` edit is the FLASH banner |
| **D-4** | `docs/notes/ea_qualifier_results_2026-09-20.md` | it has **TWO `## §10` headings** (*"BOARD HYGIENE"* and *"WHAT THIS WAVE DELIBERATELY DID NOT DO"*), so a section reference to §10 in that document is ambiguous | **RECORDED, NOT FIXED** — editing a prior wave's results document to renumber a heading changes an artifact nothing measured |
| **D-5** | the brief for this wave | it names the WAVE 26 results document as **`docs/notes/ea_second_addend_results_2026-09-20.md`**; the file in the tree is **`docs/notes/ea_qualifier_results_2026-09-20.md`** | **RECORDED.**  Nothing to fix in the tree; noted so the next reader searching by that name finds it |
| **D-6** | `sw/fz2_ledger.py` printed diff | its *"6 NEW FAILURE(S)"* block is the **`NEW/UNCLASSIFIED` family count**, not the era-over-era ENTERED count — the ENTERED count is **1** and is printed separately by `--diff`.  The two are adjacent in the output and read alike | **RECORDED.**  This wave used the explicit `--diff` line and re-derived both numbers in Python; the caution is the same one FLASH #18 recorded about `fz2_ledger`'s default comparison ledger |

⚠ **THE COUNT IS A FLOOR AND THE METHOD SAYS SO.**  D-1 was found by needing a
core leg; D-2 by **two gates exiting non-zero**; D-3 by re-reading the banner
being edited; D-4/D-5 by reading the briefing against the tree.  **No gate
enumerates claims of this kind.**

---

## 11. WHAT THIS WAVE DELIBERATELY DID NOT DO

* **No RTL edit.**  Not to make `mod3_illegal` move, not to close the one
  entrant, not for anything.  `git diff -- hdl/` is **EMPTY** on tracked files.
* **No SDC exception.**  E-1 was met without one.
* **No re-flash, no second bitstream, no adjust-and-retry.**  One flash, one
  VERIFY, try 1.
* **No classification of `fz2e/527035`.**  It is itemised and A/B-attributed;
  giving it a family by guesswork is the absorption the ledger exists to refuse.
* **No `fz2_ledger.CURRENT` move** and **no `fz2_immaterial` document
  re-derivation** — both registered as not-this-wave's.
* **No `git stash`, `git checkout .` or `git reset --hard`**; every `git add`
  by explicit path; `sw/testdata/receipts/*.jsonl` **never staged**; the only
  `git checkout --` was by exact single path on `hdl/nec_test_ucore.qsf`,
  between the two Quartus runs.
* **Nothing deleted**: the FLASH #23 corpus era is archived **by rename** and
  retained beside the new one, and the temporary pre-landing worktree was
  removed with `git worktree remove` after its two logs were kept by value.
* **No Codex, no nested subagent.**

---

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
