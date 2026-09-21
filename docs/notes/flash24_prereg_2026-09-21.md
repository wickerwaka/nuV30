# FLASH #24 — PRE-REGISTRATION: **THE FABRIC CONFIRMATION OF THE `ea_pair_valid` FIX, AND A NULL THAT IS NOT A NULL — IT IS A POINT PREDICTION OF SIX NAMED SEEDS CLOSING**

**USER AUTHORISATION 2026-09-21, verbatim: *"Flash it"***.  It discharges the
fabric debt WAVE 26 declared in `ea_qualifier_results_2026-09-20.md` §9.

**COMMITTED BEFORE ANY BOARD CONTACT.**  Both Quartus builds are already taken
(they are offline and precede the board), their figures are in §2, and **no
probe has touched the board in this session.**  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

    branch       master
    HEAD         74a2e62cd2   (WAVE 27 tip; `hdl/` tracked-clean and
                 byte-identical to WAVE 26's landing 427a3f5a10)
    bitstream    nec_test_ucore.sof  3066d40a558486c61becf490c451d351a5c3da8156109f6fbedd2927f0ae1833
                 nec_test_ucore.rbf  44cfd64791781752e89f1a86be9cafd85471dc32fb1aa9ce17ee4ae8023418c7
                 RETENTION (X1_AD_RETENTION=1), draw@seed1
                 receipt 8077ba94656880ef44afdc461c67083ab2e24111464be285f89bf52199a6f8dc
    resident     FLASH #23, sof 0f4fcfa5cd55bc32…, flashed 2026-09-19T23:48:27Z
    flash log    sw/testdata/flash_log.jsonl  26 entries  sha256 13a81a43f30c380ae63ead0e72b2c3069ce5d9d590de51ce8eed340df76d0c04

Every bar below is reported in the form it is registered in.  **A miss is
reported as a miss.  Nothing is re-registered after the fact.**

---

## 0. ⭐ JOB 0 — **WHAT IS IN THIS BITSTREAM THAT WAS NOT IN FLASH #23.  FROM THE MANIFEST, BY HASH — NOT FROM READING THE RTL.**

`git log --oneline 6de3e322b5..HEAD` = **44 commits**, of which **five** touch
`hdl/`:

| commit | what it is | in the ucore revision? |
|---|---|---|
| `a2d619d2d8` | **WAVE 21** — remove the ARCHIVED FSM core (`hdl/rtl/core/*`, −10,143 lines) | **NO** — `files_ucore.qip` never listed a `rtl/core/` file (FLASH #23 §1.2) |
| `0c7c9df595` | **WAVE 21** — re-base the Quartus project onto the ucore (one revision, authored `.qsf`) | **YES, as PLUMBING**: it is why `hdl/nec_test.qsf` LEAVES the manifest and `files_ucore.qip` moves |
| `a09f34defd` | **WAVE 21** — delete the FSM probe block from `hdl/tb/tb_v30_core.sv` | **NO** — `hdl/tb/` is not a declared input |
| `56bdf8d851` | **WAVE 25** — the TB settle window (`hdl/tb/tb_v30_core.sv`) | **NO** — same reason |
| **`427a3f5a10`** | ⭐ **WAVE 26 — the `ea_pair_valid` second-addend fix** (4 files, all `hdl/rtl/ucore/`) | **YES, AND IT IS THE ONLY BEHAVIOUR-CAPABLE CHANGE IN THE WINDOW** |

### 0.1 The manifest diff, file by file, against **the FLASH #23 bitstream's own receipt**

```
old  99 files  ee6a4eff46e483d3      new  98 files  07796a3630faee56
ONLY IN FLASH23 : ['hdl/nec_test.qsf']        ONLY IN TREE : []
MOVED (6):
    hdl/files_ucore.qip                    cc8d2a70f699d83f -> 4ef85d1b529113eb   [WAVE 21 plumbing]
    hdl/nec_test_ucore.qsf                 709a8ee98a08c6bb -> d80e4b96041688b7   [WAVE 21 plumbing; §70.7 exempt class]
    hdl/rtl/ucore/v30u_eu.sv               31ff3a50f503da77 -> 4bd5ecd88194a3e1   <-- WAVE 26
    hdl/rtl/ucore/v30u_eu_arm_bind.svh     b0ec842b70279f02 -> 3a26f19bf252d851   <-- WAVE 26
    hdl/rtl/ucore/v30u_eu_arm_ea_calc.svh  ce3a84ed0ea573b7 -> f0899a88f21db96a   <-- WAVE 26
    hdl/rtl/ucore/v30u_eu_step.svh         92f9c171227c2939 -> 3774e7368f894fce   <-- WAVE 26
rtl/core entries in the new manifest: 0
```

### 0.2 ⭐ And a SECOND, INDEPENDENT instrument says the same thing from the socket's side

`fz2_replay`'s **fabric era guard**, run at HEAD **before the flash**, reads the
RESIDENT bitstream's receipt and re-hashes **its** declared inputs against the
tree.  **It REFUSED, exit 1** (`sw/testdata/wave28/era_guard_preflash.txt`):

```
    bitstream   0f4fcfa5cd55bc32…  flashed 2026-09-19T23:48:27Z  git 6de3e322b5-dirty
    receipt     5f686aeb054522e8…  FLASH#23 RETENTION draw@seed1-seed1
    its inputs  92/99 hash IDENTICAL in the tree at HEAD
      MOVED     hdl/files_ucore.qip · hdl/nec_test.qsf   <-- RTL
      MOVED     hdl/nec_test_ucore.qsf   [EXEMPT …]
      MOVED     hdl/rtl/ucore/v30u_eu.sv · …_arm_bind.svh · …_arm_ea_calc.svh · …_step.svh   <-- RTL
    ERA MISMATCH -- REFUSING TO SCORE.
```

**A GUARD THAT PASSES BEFORE A FLASH IS A GUARD THAT IS NOT WORKING.**  It
names the same six files §0.1 names, from the other direction.

> **THE ONLY BEHAVIOUR-CAPABLE DELTA IN FLASH #24 IS WAVE 26's ONE MUX.**  The
> other three moved files are the Quartus project's own plumbing, and WAVE 21
> measured a 36-leg zero-delta ladder across them.

---

## 1. WHAT IS BEING CONFIRMED, AND WHAT WOULD REFUTE IT

> **THE LAW**: *the address adder's B rail is loaded on EVERY EA calculation
> with the SECOND ADDEND — the index register where the form has one and
> nothing is added after it, the displacement otherwise, and ZERO where there
> is nothing to add.*

Offline it measures `b2_ea_lane_ucore` **13 / 13**, a fresh directed socket
capture **21 / 21**, and `lea_mod3_gate` L4 **2-of-2 DIVERGE → 0-of-2**.
**Every one of those is Verilator or a socket capture of the real chip.  The
SYNTHESISED core has never run the fix.**  This repo has a refuted-in-fabric
precedent (**F42**, `ucore_provenance.md` §52.9) and that is why this wave
exists.

**RE-MEASURED AT HEAD BEFORE THIS DOCUMENT WAS COMMITTED**, so §3's prediction
is a derivation and not a memory: `sw/w26_ea_lane2_ucore.py --capture
sw/testdata/wave26/b2b` reads **MATCH 21 · DIVERGE 0 · NO-SILICON 0**, RTL leg
receipt `2d709c79dd6a3e09…`
(`sw/testdata/wave28/ucore_verilator_recheck.log`).

---

## 2. THE BUILD — G6, **ONE DRAW PER CONFIGURATION** (`E-1` … `E-9`)

**USER RULING 2026-08-13**: *"only run more than one seed if the compile is
explicitly being done to measure fmax."*  This is a landing leg, not an Fmax
claim, so it is **`draw@seed1`** and **may not be quoted as a band.**

| # | bar | **measured** |
|---|---|---|
| **E-1** | `hdl/nec_test.sdc` **EXCEPTION-FREE** — anchored `grep -cE '^[[:space:]]*(set_multicycle_path\|set_false_path\|set_max_delay)'` | ⭐ **0.**  The unanchored count is **2** and both are the commented DO-NOT-RESTORE record, **which is why the anchor is the instrument**.  `nec_test.sdc` is byte-untouched.  *"I don't want custom sdc rules, period."* — held |
| **E-2** | `qsf_lint --check` (E1) | **CANONICAL**, both builds |
| **E-3** | Fmax ≥ 32 MHz | **CONTROL 34.35** · **RETENTION 34.59** |
| **E-4** | worst setup > 0 | **CONTROL +2.135 ns** · **RETENTION +2.337 ns** |
| **E-5** | TNS 0.000 **setup AND hold, every domain** | **0.000 on all four domains, both builds, both directions** |
| **E-6** | ⚠ **the RETENTION build is made by `--retention`, and the ENV-VAR FORM IS REFUSED** | `X1_AD_RETENTION=1 python3 sw/quartus_gate.py --dry-run` → **exit 2**, naming the FLASH #18 finding.  `quartus_map` received **`--verilog_macro=X1_AD_RETENTION=1`** on its command line (in the receipt's `sweep.map_command`).  `configuration` is **DERIVED from the reports** and self-labels **`RETENTION (X1_AD_RETENTION=1)`** |
| **E-7** | ⚠ **E-9 — the two `.rbf`s MUST DIFFER** | **CONTROL `aa931892f7a69668…` ≠ RETENTION `44cfd64791781752…`.**  A matching pair would mean the macro never reached the compiler |
| **E-8** | 0 latches · 0 `lpm_divide` · 0 error lines | **0 / 0 / 0**, both builds |
| **E-9** | input stability (E7) | **PASS**, 1 file moved, the one declared exemption `hdl/nec_test_ucore.qsf`, **OFFENDING []** |

    CONTROL    Fmax 34.35  setup +2.135  ALMs 8,438 / 41,910 (20 %)  regs 6,843
               receipt ed3a61f3ee0bc553…   rbf aa931892f7a69668…   PASS
    RETENTION  Fmax 34.59  setup +2.337  ALMs 8,495 / 41,910 (20 %)  regs 7,104
               receipt 8077ba94656880ef…   rbf 44cfd64791781752…   PASS   <-- THE FLASHED ONE

⭐ **AND BOTH `.rbf`s ARE BYTE-IDENTICAL TO WAVE 26's OWN seed-1 DRAWS** — `aa931892f7a69668…`
and `44cfd64791781752…`, a day and two trees apart, with Fmax reproducing to
the hundredth (34.35 / 34.59).  **This is the fourth cross-wave
bitstream-payload reproduction of the campaign** and it is recorded, not
barred.

---

## 3. ⭐⭐ **THE PRIMARY BAR — THE EA-LANE LAW IN FABRIC** (`P-1` … `P-5`)

### 3.1 HOW THE CORE LEG IS DRIVEN — **STATED IN ADVANCE, BECAUSE THE BRIEF REQUIRES IT**

WAVE 26's 21 rows are **SOCKET** captures (`use_core=False`): they measure
**silicon**, which no bitstream can move.  Confirming the **core** needs a
**core leg**, and the two must be scored **pairwise on the same images**.

**NEW RIG: `sw/w28_ea_lane_fabric.py`** (committed with this document, before
first board contact).  `emit_case`'s record source is `emit_suite._capture`,
which passes `use_core=emit_suite.EMIT_USE_CORE` straight into
`v30run.run_image`; the final register column is parsed out of the
**store-stub dump in the captured bus rows**, so it is bus-observable and
engine-agnostic.  For each of the **21** probes the rig captures the **same
composed image twice, back-to-back in one session**:

    leg `socket`   EMIT_USE_CORE = False   the socketed uPD70116  -- SILICON
    leg `core`     EMIT_USE_CORE = True    the in-FPGA v30_core   -- THE DUT

`use_core` is passed **EXPLICITLY on every capture** because the board's CFG is
sticky, and each leg's provenance is stamped **from the value actually passed**.

⚠ **`emit_suite._truth_stamp()` IS NOT USED FOR THE CORE LEG AND MAY NOT BE.**
It returns the constant `"SOCKET (real chip, use_core=False)"` whenever
`ENGINE == "chip"` and **never consults `EMIT_USE_CORE`** — so on a core leg it
writes a provenance line that is false.  Its own docstring says *"A provenance
line that cannot be wrong is not provenance."*  **It can be wrong**; registered
here as doc-discrepancy **D-1** and the rig stamps its own legs.

### 3.2 THE POINT PREDICTIONS

| # | bar | **registered** |
|---|---|---|
| **P-1** | ⭐ **THE HEADLINE — the core reproduces the chip on the EA lane** | **PAIRWISE MATCH 21 / 21**, core vs socket, same images, same session.  **A POINT.  20 / 21 is a MISS and is reported as one** |
| **P-1b** | of which WAVE 24's set | the first **13** rows (`C1 C2 C3 R1 R2 M0…M7`) **13 / 13** |
| **P-2** | the **positive control** — the socket column reproduces WAVE 26's banked socket column | **REPRO 21 / 21**, value for value: `C1 1234 · C2 BEEF · C3 2222 · R1 4121 · R2 1121 · M0 8888 · M1 9999 · M2 8888 · M3 9999 · M4 1111 · M5 1111 · M6 2345 · M7 1111 · P0 1121 · P1 1111 · P2 1121 · P3 2345 · P4 2345 · P5 1131 · P6 2345 · P7 1101`.  **A socket row that moves is a RIG FINDING, not a result**, and is a STOP |
| **P-3** | ⭐ **THE NON-VACUITY CONTROL, TAKEN BEFORE THE FLASH** | on the RESIDENT FLASH #23 bitstream the **core** leg must **DIVERGE**: pairwise **MATCH 7 / 21**, and the core column must equal the pre-landing Verilator column **value for value** — `C1 1234 · C2 beef · C3 2222 · R1 9211 · R2 4dcc · M0 8888 · M1 9999 · M2 8888 · M3 9999 · M4 9211 · M5 9211 · M6 9211 · M7 9211 · P0 8888 · P1 8888 · P2 9211 · P3 9211 · P4 9999 · P5 9211 · P6 9211 · P7 9211` (`sw/testdata/wave26/b2b/ucore_columns_before.json`).  **A rig that reads 21/21 on BOTH bitstreams is measuring the socket twice** |
| **P-4** | ⚠ the sharpest single row | **`P1` (`89 40 00`, `[BW+IX+0]`)** — a `mod=01` form whose displacement is ZERO.  Silicon says **`1111`**; *"B = the index"* predicts `8888`.  The fabric core must read **`1111`** |
| **P-5** | ⚠ **P-3's values are a POINT PREDICTION ACROSS TWO HARNESSES** and are registered as such.  The pre-landing column was measured on **Verilator `tb_bootrun`**; P-3 scores the **FPGA core**.  **If they differ, that is a FINDING about the two harnesses and is reported as one, not smoothed over** |

---

## 4. **THE NULL — AND IT IS NOT A NULL.  SIX NAMED SEEDS ARE PREDICTED TO CLOSE.** (`C-1` … `C-9`)

FLASH #23's primary bar was a null because ARM-B was behaviour-identical.
**This fix is not**: it changed `lea_mod3_gate`'s L4 offline.  So the movement
is **DERIVED OFFLINE FIRST**, on this tree, before the board — and registered.

**THE INSTRUMENT**: `sw/fz2_replay.py --ledger <F23> --all-failures
--pass-sample 150 --leg ret --no-fabric-era-guard --jobs 3`, i.e. FLASH #23's
own **Q-2 closing control** run *predictively*: the offline core is the NEW
RTL, the fabric column it is scored against is the OLD one, so the
disagreements ARE the prediction.  **`--no-fabric-era-guard` is used
deliberately and is said beside the number** — that is the flag's one honest
use.  `tb_sys` rebuilt first, receipt **`03c861175b6313d5…`**; **252 seeds in
37 s, 0 errors**; raw at `sw/testdata/wave28/w28_replay_prediction.json`.

```
                          replay PASS  replay FAIL
  fabric PASS                     150            0
  fabric FAIL                       6           96
  AGREEMENT 246 / 252 = 97.6 %      first_bad IDENTICAL on 96 of 96
```

| # | bar | **registered** |
|---|---|---|
| **C-1** | corpus identity | 960 + 2,880 = **3,840** seeds, **48 strata**, `fz2_w1 lint` **PASS / 0 hits / 48 stratum rows** |
| **C-2** | completeness | **48 / 48 strata, every `rc 0`** |
| **C-3** | the flash pin | `distinct_eras` **1**, `absent` 0, `incomplete` 0, `build_stale` 0, every row's `era.sof_sha256` = **`3066d40a558486c6…`** |
| **C-4** | ⭐ **THE HEADLINE** | **96 failures** of a denominator of **3,837**.  **A POINT.**  Tolerance for the aggregate is FLASH #23's 0.2604 % noise floor, band **[86, 106]**; **the point is 96 and a point miss is a miss** |
| **C-5** | ⭐⭐ **THE SIX, BY NAME** | **`fz2c/406054` · `fz2c/408019` · `fz2e/518038` · `fz2e/520013` · `fz2e/529009` · `fz2e/531039` LEAVE the ledger.**  Their F23 `diverging_rows / first_bad_row` were `3141/470 · 1087/1617 · 194/429 · 2615/960 · 8/908 · 4/1012`.  ⭐ **THREE OF THEM ARE THREE OF FLASH #23's OWN `C-14` "M10 LEA-mod3 six"** — named as non-movers there, predicted as movers here, **by the fix that owns the mechanism** |
| **C-6** | membership flips **outside the six** | **0 ENTERED, 0 LEFT.**  **Budget 10 seeds** (FLASH #23's; it used 0).  Every unregistered flip itemised |
| **C-7** | ⭐ **THE SURVIVING SEAT TABLE — ALL 96 SEAT FOR SEAT** | every survivor present with **the same `diverging_rows` AND the same `first_bad_row`** as FLASH #23.  Digest recipe: `sha256` of `"\n".join("<seed> <diverging_rows> <first_bad_row>")` over the entries **sorted by seed**.  FLASH #23's 102 → **`004050f1a841e5f4b022b1d938e5cb965739034e73eda1f8f7a4de8ddc3c6d27`**; the predicted 96 → **`9d89bb62b6507f3b37d75e63eb3a291f7d45f7b321efc862747e4c4daea5d7cb`** |
| **C-8** | direction | **0 `first_bad` EARLIER anywhere in the corpus**, and **0 LOST** |
| **C-9** | the row metric | Σ`diverging_rows` **94,014 → 86,965** (−7,049, the six seeds' own rows exactly).  A delta must reconcile to **ZERO unexplained rows** |
| **C-9b** | family counts of the 96 | `A1` 5 · `A2` 4 · **`A3` 13** (was 15) · `B1` 1 · `B2` 2 · `C1` 1 · `C2` 8 · `C3` 1 · `C4` 1 · `D1` 8 · `D2` 7 · **`D3` 3** (was 4) · **`E1` 35** (was 38) · `E2` 2 · `NEW/UNCLASSIFIED` 5 = **96** |
| **C-9c** | discards | ⚠ **`_ps3_8080` is a SOCKET-leg predicate (A-2) that no RTL change can reach** and it has re-rolled on nine consecutive eras.  **REPORTED WITH BOTH BASES, NOT BARRED**; F23's were `fz2c/402059`, `fz2e/509069`, `fz2e/516044` |

---

## 5. `mod3_illegal` — **STAYS 0 / 128, AND PREDICTING OTHERWISE WOULD BE A MISUNDERSTANDING** (`M-1`)

| # | bar | registered |
|---|---|---|
| **M-1** | `check_core --core ucore --suite-dir tests/v30/mod3_illegal --opcodes all --cases 0` | **0 / 128 arch, 128 / 128 cycles.**  WAVE 23 §3 established this is a **TESTBENCH STIMULUS** artefact: the 128 goldens have no ModR/M predecessor, their outcome depends on *pre-window* `ea_residue`, and `tb_v30_core.sv:1120` injects fourteen architectural registers and nothing else.  **A flash cannot move an offline testbench figure**, and the suite is a frozen artifact under WAVE 22's manifest `67161a0c409c7fc6…` |
| **M-2** | **STOP S-4, carried forward verbatim from WAVE 23** | **`ea_residue` is NOT injected into the TB.**  Not now, not to make M-1 move |

---

## 6. FIRST LIGHT, THE ERA GUARD, AND THE CLOSING CONTROLS (`N-1` … `N-4`)

| # | bar | registered |
|---|---|---|
| **N-1** | **first light** | `check_ab_hw all 800` → **MATCH 800 rows on ALL THREE legs** (chip-vs-golden, core-vs-chip, core-vs-golden) |
| **N-2** | the era guard, **AFTER** the flash | `fz2_replay` fabric era guard **PASSES with NO bypass**, the only moved file the declared `.qsf` exemption |
| **N-3** | the closing control | `fz2_replay --all-failures --pass-sample 150 --leg ret` **run in the main tree** (it is structurally vacuous in a worktree): **agreement ≥ 99 %** over `<failures> + 150` = **246** on the C-4 point, `first_bad` **IDENTICAL** on the failures |
| **N-4** | closing chip proof | `check_ab_hw chip 800` **MATCH over 800 rows**, `use_core=0` explicit, **AFTER EVERYTHING** |

---

## 7. BOARD DISCIPLINE — **NON-NEGOTIABLE** (`B-1` … `B-7`)

| # | |
|---|---|
| **B-1** | **SINGLE-WRITER CHECK FIRST**, `pgrep -x`, ONE pattern per call.  **`pgrep -f` SELF-MATCHES and is not used for this.**  BLOCK, do not poll |
| **B-2** | **`div_guard()` ON EVERY PROBE.**  An **UNPINNED** readback is a **RIG-INTEGRITY FINDING AND A HARD STOP** — reported, never worked around.  The probe count and the unpinned count are both reported |
| **B-3** | **`use_core` PASSED EXPLICITLY ON EVERY PROBE — THE CFG IS STICKY.**  Socket legs `use_core=False`; core legs `use_core=True`; **each leg is named in the output and in the manifest** |
| **B-4** | **FULL PER-CLOCK ROWS RETAINED + sha256**, never digests alone |
| **B-5** | **`board_idle()` LAST**, run and verified |
| **B-6** | transport errors, quarantines and `RigMismatch` counts **reported with the capture count** |
| **B-7** | `sw/safe_flash.sh` **with its VERIFY leg**; the try count recorded; `flash_log.jsonl` **26 → 27 entries**, both sha256s recorded |

---

## 8. HARD STOPS — **STOP AND REPORT.  DO NOT ITERATE.**

**THE USER AUTHORISED *A* FLASH, NOT A DEBUGGING SESSION ON HARDWARE.**  If any
of these fires: capture the evidence, run `board_idle()`, and **STOP**.  **Do
not re-flash.  Do not adjust and retry.  Do not flash a different bitstream.**

| # | stop |
|---|---|
| **S-1** | `safe_flash` VERIFY fails → the board is presumed unreachable.  STOP; a physical power cycle is the user's |
| **S-2** | any **UNPINNED** `div_guard` readback |
| **S-3** | the **socket column moves** (P-2 < 21/21) → the rig, not the core, and nothing downstream is quotable |
| **S-4** | `check_ab_hw all 800` first light is not MATCH ×3 |
| **S-5** | a `RigMismatch`, a quarantine, or a transport error the retry path does not absorb |
| **S-6** | `flash_log.jsonl` does not go 26 → 27, or its pre-flash sha256 is not `13a81a43f30c380a…` |
| **S-7** | **P-1 misses.**  ⚠ **THIS IS NOT A STOP — IT IS THE RESULT.**  If the fabric refutes the fix that is the single most valuable thing this wave can report, and it is reported in full with the offline columns beside it.  **No RTL is edited in this wave to make it pass** |

---

## 9. WHAT THIS SITTING CAN AND CANNOT ESTABLISH

* **CAN**: that the *synthesised* core reproduces silicon on the EA lane, on
  21 constructed probes, pairwise, with a non-vacuity control taken on the
  previous bitstream; and what the fix is worth on the 3,840-seed corpus.
* **CANNOT**: anything about `mod = 01/10` forms with a **segment override**, a
  byte displacement on a two-register form other than `P0`/`P1`, or a
  `mod = 10` two-register form other than `P4` — WAVE 26 §5 declared those
  unmeasured and this wave does not measure them either.
* **CANNOT**: an Fmax claim.  `draw@seed1` per configuration, `N = 1 < 5`.
* **CANNOT**: move `mod3_illegal`, and §5 says why in advance.

---

## 10. DISCIPLINE, DECLARED IN ADVANCE

* **No Codex.  No nested subagents.**
* **21 modified + 21 untracked USER files are present.**  **NO `git stash`, NO
  `git checkout .`, NO `git reset --hard`.**  Every `git add` **BY EXPLICIT
  PATH**.  `sw/testdata/receipts/*.jsonl` is **NEVER** staged — receipts are
  committed **by value** under `sw/testdata/wave28/` and `sw/testdata/g6dist/`.
  The only `git checkout --` is by exact single path on
  `hdl/nec_test_ucore.qsf`, between Quartus runs.
* **`${PIPESTATUS[0]}`**, never `tail`'s exit code.
* `~/.cache/ucsimt-tmp`, never `/tmp`.
* **Every classifier carries a positive control** (P-2 is the EA rig's; the era
  guard's pre-flash refusal is the corpus's).
* **Record what was measured, not what was expected.  A missed prediction is
  reported as registered, never restated.**
* Doc discrepancies as a **FLOOR**, each with its disposition.

---

## Appendix A — REVIEWER RE-RUN

```sh
# JOB 0 -- the manifest diff, by name, against the FLASH #23 receipt
python3 - <<'PY'
import json
o=json.load(open('sw/testdata/g6dist/FLASH#23 RETENTION draw@seed1/seed1_quartus_gate.json'))['input_manifest']
n=json.load(open('sw/testdata/g6dist/FLASH#24 CONTROL draw@seed1/seed1_quartus_gate.json'))['input_manifest']
print(o['n_files'],o['sha256'][:16],'->',n['n_files'],n['sha256'][:16])
print('only-old',sorted(set(o['files'])-set(n['files'])),'only-new',sorted(set(n['files'])-set(o['files'])))
print('moved',[k for k in set(o['files'])&set(n['files']) if o['files'][k]!=n['files'][k]])
PY

# THE PREDICTED 96-SEAT DIGEST (C-7)
python3 - <<'PY'
import json,hashlib
d=json.load(open('sw/testdata/fz2/fz2_failure_ledger_f23_2026-09-19.json'))
closed={'fz2c/406054','fz2c/408019','fz2e/518038','fz2e/520013','fz2e/529009','fz2e/531039'}
s=[e for e in d['failures'] if e['seed'] not in closed]
print(len(s), hashlib.sha256('\n'.join('%s %s %s'%(e['seed'],e['diverging_rows'],e['first_bad_row'])
      for e in sorted(s,key=lambda x:x['seed'])).encode()).hexdigest())
PY

# the two builds -- THE ENV-VAR FORM IS REFUSED (exit 2)
python3 sw/quartus_gate.py            --seeds 1 --label "FLASH#24 CONTROL draw@seed1"
python3 sw/quartus_gate.py --retention --seeds 1 --label "FLASH#24 RETENTION draw@seed1"
X1_AD_RETENTION=1 python3 sw/quartus_gate.py --dry-run ; echo $?   # 2

# the EA lane in fabric -- BEFORE the flash (non-vacuity), then AFTER
python3 sw/w28_ea_lane_fabric.py --out sw/testdata/wave28/ea_fabric_preflash  --expect before
python3 sw/w28_ea_lane_fabric.py --out sw/testdata/wave28/ea_fabric_postflash --expect after
```

---

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
