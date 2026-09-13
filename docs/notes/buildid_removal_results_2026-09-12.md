# WAVE 12 — **`build_id.v` IS GONE.  THE PROJECT'S QUARTUS FIGURES ARE COMPARABLE TO EACH OTHER FOR THE FIRST TIME.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/buildid_removal_prereg_2026-09-12.md`, committed at
**`ec0d00c267` BEFORE THE FIRST EDIT**.  Landing **`04efdc8d47`**.

**A LANDING.  OFFLINE ONLY — NO BOARD, NO FLASH, NOTHING PROGRAMMED.**
⚠ **THIS CHANGE MOVES THE BITSTREAM.**

---

## §0 THE HEADLINE

> **1. THE `V` ELEMENT IS OPTIONAL, AND THAT WAS ESTABLISHED BEFORE THE FIRST
> EDIT.**  `hps_io` is the only consumer of `CONF_STR` in `hdl/sys/`; it serves
> the string **byte-positionally, with no parsing of any element**, and past the
> end the HPS reads 0.  The element is a MiSTer *Main* userland convention that
> supplies the OSD version text.  It was deleted, which is the instruction
> exactly.
>
> **2. IT IS NOT GENERATED.**  A full clean `quartus_sh --flow compile` — the
> ONLY path that honours `PRE_FLOW_SCRIPT_FILE`, and therefore the only one on
> which the stamp could still appear — produced **no `hdl/build_id.v`**, with
> **0** `Error (10054)`, **0** `Generated:` lines and **0** occurrences of the
> macro in the whole 2,000-line transcript.  The hook still ran (`Evaluation of
> Tcl script sys/gen_cdf.tcl was successful`) and still wrote a
> **byte-identical `jtag.cdf`** — the positive control that the leg is not
> vacuous.
>
> **3. THE NONDETERMINISM IS GONE, AND IT IS MEASURED GONE.**  The two
> conditions WAVE 11 measured **1.647 ns / 1.34 MHz apart at one seed** now
> return **`$v30u_ce` 2,175 and T_min 35.992 ns — BOTH ARMS, Δ = 0.000 ns**,
> with byte-identical `truefmax` artifacts and **whole 390,761-byte Quartus
> transcripts that differ in ONE LINE, a progress timestamp.**  (§3.)
>
> **4. THE PROJECT HAS A STAMP-FREE G6 BASELINE, AND EVERY BAR IS MET.**
> G6 **PASS** on both configurations, `--seeds 5`: **CONTROL `worst-of-5`
> 40.62 MHz**, **RETENTION 41.63**, TNS 0.000 setup and hold on all 10 draws.
> **The 32-leg ladder is ZERO-DELTA** — 27 of 27 scored legs byte-identical,
> the four `chain_lfsr` signatures unmoved, `fz2_replay`'s scored content
> hashing the same.  The one intended move is `test_quartus_gate` **255 →
> 287**, which is bar E11's own falsifier.  (§4, §5, §6.)
>
> **5. AND THE GATE THAT KEEPS IT GONE EXISTS AND FIRES.**  `quartus_gate`
> bar **E11** REFUSES (exit 2, reason named) if `hdl/build_id.v` reappears or
> the stamp macro re-enters any file the compiler reads — on every path, with
> no quiet exemption — and `hdl/sys/` is vendored, so that is not hygiene.
> (§6.)

---

## §1 ⚠ THE QUESTION THE BRIEF REQUIRED ANSWERING FIRST — **`CONF_STR`'s `V` ELEMENT IS OPTIONAL**

Asked and answered **in the pre-registration, before the first edit**, from the
vendored framework's own source:

| evidence | what it shows |
|---|---|
| `hdl/sys/hps_io.sv:30` — `module hps_io #(parameter CONF_STR, … STRLEN=$size(CONF_STR)>>3)` | `CONF_STR` is a **parameter** and its length is **derived**.  There is no fixed layout and no required element count |
| `hdl/sys/hps_io.sv:243` — `assign conf_byte = CONF_STR[{(STRLEN - byte_cnt),3'b000} +:8];` and `confstr_rom` at `:1027` for the BRAM variant | the string is served to the HPS **byte by byte, positionally, indexed by `byte_cnt`**.  **No element is located, named, counted or decoded in hardware** |
| `hdl/sys/hps_io.sv:393` — `'h14: if(byte_cnt <= STRLEN) io_dout[7:0] <= conf_byte;` | past the end the HPS reads **0**, the terminator.  A shorter string terminates one byte earlier **by the same mechanism** |
| `hps_io` is the **only** consumer of `CONF_STR` anywhere under `hdl/sys/` | nothing else could depend on it |

The `V` element is a **MiSTer *Main* (ARM userland) convention** supplying the
version text shown at the bottom of the OSD menu.  **Its absence costs that text
and nothing else**, and no gate, measurement or capture in this repository goes
through the OSD.  **So it was deleted.**  Had it been structurally required this
wave would have STOPPED and reported: a fixed literal is a different thing from
*"isn't used"*, and that would have been the user's call, not this wave's.

⚠ **`hdl/sys/` IS VENDORED MiSTer FRAMEWORK CODE, AND THAT IS WHY M-6 EXISTS.**
A future `sys/` update restores `sys/build_id.tcl` and re-points
`PRE_FLOW_SCRIPT_FILE` at it — **with no edit anyone made and no diff anyone
reviews** — and `nec_test.sv` is a project file that a merge would carry the
element back into.  §6 is the gate that refuses such a build.

---

## §2 M-1 — **IT IS NOT GENERATED.  DEMONSTRATED, NOT ASSERTED.**  **MET.**

`python3 sw/quartus_gate.py` on `04efdc8d47`, i.e. `quartus_sh --flow compile`:
**the only path that honours `PRE_FLOW_SCRIPT_FILE`**, and therefore the only
path on which the stamp could still be regenerated.  Two controls were set up by
hand before it: `hdl/build_id.v` absent, and **`hdl/jtag.cdf` moved aside**, so
that its reappearance proves the hook still *ran*.

| clause | measured |
|---|---|
| the PRE_FLOW hook ran, and ran the renamed script | `Info: Command: quartus_sh -t sys/gen_cdf.tcl compile nec_test nec_test_ucore` · `Info (23030): Evaluation of Tcl script sys/gen_cdf.tcl was successful` |
| its remaining job still works | `hdl/jtag.cdf` regenerated, **`cmp` BYTE-IDENTICAL** to the pre-WAVE-12 file (`generateCDF` kept verbatim) |
| **no stamp was written** | `hdl/build_id.v` **ABSENT** after a full compile |
| the old generator's own announcement | **0** `Generated:` lines |
| the failure mode the stamp's absence used to cause | **0** `Error (10054)` / `can't open` |
| the macro anywhere in the transcript | **0** occurrences |
| the compile itself | **`quartus_gate: PASS`** — `E2_zero_errors` 0/0, **Fmax 44.07 MHz**, worst setup **+8.561 ns**, TNS `[]` (0.000 every domain), **ALMs 8,123 / 41,910 (19 %)**, 0 latches, 0 `lpm_divide`, `E7_input_stability` 0 moved.  Receipt `df6e531f5b06ae5f…`, `sw/testdata/wave12/m1/m1_quartus_gate.json`, 469 s |

⚠ **THE LEG IS NON-VACUOUS AND THE RECORD SAYS SO**: on 2026-08-13 this exact
absence produced `Error (10054): can't open Verilog Design File "build_id.v"` —
**measured, exit 3 in 11 s** (`quartus_gate.build_commands()`'s own docstring).
A&S getting past `nec_test.sv` is therefore not a null result.

⚠ **THIS RECEIPT IS NOT M-4'S FIGURE.**  It is ONE draw at Quartus's own default
seed and it is quoted here only as *the compile completed*.  §4 is the
distribution.

---

## §3 M-3 — **THE FALSIFIER.  THE NONDETERMINISM IS GONE, AND IT IS MEASURED GONE.**  **MET.**

WAVE 11's own pipeline, unchanged: `sw/run_biu_roundtrip.py --clean-db
--control-seeds 1 --retention-seeds ''`, no-exception SDC from the one shared
anchor, single-writer guard, `.qsf` restored after every stage.  **Two arms, and
the only difference between them is the file WAVE 11 proved was worth
1.647 ns** — written by hand, because nothing generates it any more.

| arm | `hdl/build_id.v` | `sha256` | `$v30u_ce` | **T_min** | MHz |
|---|---|---|---:|---:|---:|
| **W12-A** | `` `define …DATE "260909" `` | `11e55ef99ab705c5…` | **2,175** | **35.992** | **27.78** |
| **W12-B** | `` `define …DATE "260912" `` | `5b4d6ad10ee2a48f…` | **2,175** | **35.992** | **27.78** |

⚠ **THE TWO `sha256`s ARE WAVE 11's OWN, AND THE 260909 ONE IS THE VALUE A
COMMITTED RECEIPT HOLDS** (`sw/testdata/g6dist/wave7-chainflat-noexc-control-n5/seed1_quartus_gate.json`, its `build_id` field).  They were reproduced here
byte for byte, not recalled.  `sw/testdata/wave12/m3/build_id_manifest.txt`.

### 3.1 THE REGISTERED PREDICTION, SCORED

| registered | measured |
|---|---|
| the SAME `$v30u_ce` | **2,175 = 2,175** |
| the SAME `T_min` **to the thousandth** | **35.992 = 35.992 ns.  Δ = 0.000 ns** |
| **BYTE-IDENTICAL** `truefmax` artifacts | **BYTE-IDENTICAL from line 2 on** (line 1 is the output path, which names the arm) — all five exception classes, every endpoint, every slack, 79 lines |
| — | the round-trip census `.txt` **IDENTICAL** (70 lines) and `.arrivalpoints.txt` **IDENTICAL** (90 lines) |

> ### **WAVE 11 MEASURED THESE TWO CONDITIONS 1.647 ns / 1.34 MHz APART AT THIS SEED.  WAVE 12 MEASURES THEM 0.000 ns APART.**

### 3.2 ⚠ THE ONE RESIDUE, REPORTED AS A NUMBER AND NOT AS A HEDGE

`*.rows.txt` — the 600-row `report_timing` dump — is **not** positionally
identical: **62 of 600 rows sit at a different rank.**  It is **PURE TIE
ORDERING, AND THAT IS PROVED, NOT ASSERTED**:

* **THE 600-ROW MULTISET IS IDENTICAL.**  Strip the rank column, sort, `diff`:
  **0 differing lines.**  Both arms report the same 600 paths with the same
  slacks, the same delays and the same endpoint pairs.
* **EVERY ONE OF THE 62 DISPLACED ROWS HAS THE SAME SLACK AND THE SAME CLASS AS
  the row it swapped with** — 19 distinct slack values, every group internally
  tied.  What differs is `report_timing`'s order *within* an equal-slack group.
* **Two different designs cannot produce identical slacks on 600 paths.**  The
  fitted design is the same one; the report's tie-break is not a property of it.

⚠ **NO `.rbf` WAS COMPARED, AND THE PRE-REGISTRATION DID NOT ASK FOR ONE.**
WAVE 11's pipeline is `map` + `fit` + `sta` with **no assembler stage**, so
neither arm produces a bitstream.  What was compared instead is the complete
timing artifact set, which is the quantity the wave is about.  Stated rather
than quietly omitted.

### 3.2a **AND THE STRONGEST EVIDENCE IS THE ONE NOBODY REGISTERED: THE WHOLE COMPILE IS THE SAME COMPILE.**

The two arms' **complete Quartus transcripts** — `quartus_map` + `quartus_fit`
+ two `quartus_sta` runs, **390,761 bytes each, byte-for-byte the same size** —
were normalised for the arm's own name, wall-clock dates and elapsed/memory
figures, and `diff`ed:

> ### **TWO DIFFERING LINES.  THEY ARE THE SAME LINE IN EACH FILE, AND IT IS A PROGRESS TIMESTAMP** (`Info (11172): 2026.09.12.19:55:36` against `…20:05:58`).

Every resource count, every fitter message, every physical-synthesis line,
every SDC collection probe and every warning is identical.  **WAVE 11's arms
differed in the register-duplication counts, in the binding endpoint's NAME and
in 236 post-fit registers.  These two do not differ anywhere.**
`sw/testdata/wave12/m3/*.run.log.gz`.

### 3.3 ⚠ WHAT THIS LEG IS *NOT*

It is **not** a comparison against WAVE 11's numbers.  `2,175 / 35.992` is this
tree at this seed under the no-exception SDC; `2,154 / 34.220` and
`1,918 / 35.867` are the OLD tree under two stamps.  **The element's removal is
itself a perturbation of the same class as changing its characters**, so the
figures may not be differenced (§8).  The comparison that matters is
**A against B**, and they are the same.

⚠ **THE ARMS DELIBERATELY BYPASS E11.**  `run_biu_roundtrip.py` calls
`quartus_map`/`quartus_fit` directly and has no stamp bar, so a planted
`build_id.v` does not stop it.  That is what makes the leg possible at all —
and `quartus_gate` would have **refused** both arms, which §6 demonstrates
end to end.

---

## §4 M-4 — **G6 PASSES ON BOTH CONFIGURATIONS.  THE FIRST STAMP-FREE BASELINE.**  **MET.**

`python3 sw/quartus_gate.py [--retention] --seeds 5`, the tree's own SDC (the CE
multicycle is present; this wave does not touch it), one shared map and five
fits per configuration, single-writer guard and `.qsf` restore between legs.

| | verdict | **`worst-of-5@seeds{1,2,3,4,5}`** | all five draws | median | spread | worst setup | ALMs |
|---|---|---:|---|---:|---:|---:|---|
| **CONTROL** | **PASS** | **40.62 MHz** (seed 3) | 40.62 · 40.81 · 43.29 · 44.07 · 44.30 | 43.29 | 3.68 | +6.629 … +8.676 | 8,105–8,144 (19 %) |
| **RETENTION** | **PASS** | **41.63 MHz** (seed 4) | 41.63 · 42.69 · 42.88 · 43.71 · 45.31 | 42.88 | 3.68 | +7.226 … +9.180 | 8,161–8,200 (19–20 %) |

* **TNS 0.000 setup AND hold on every domain, all 10 draws** (`E5_tns` `[]`),
  0 errors, 0 latches, 0 `lpm_divide`.
* **`E11_no_build_stamp` reads `pass: true` in all 10 per-seed receipts** plus
  both distribution receipts, each recording 98 files scanned and 0 hits.
* **The `configuration` field is DERIVED from the reports on all 10** — five
  read `CONTROL/DEFAULT (no X1_AD_RETENTION)` and five read
  `RETENTION (X1_AD_RETENTION=1)` — and **all ten `.rbf`s are distinct**, which
  is the check that `--verilog_macro` reached the compiler (E-6, E-9).
* Records: `sw/testdata/g6dist/wave12-nostamp-control-n5/distribution.json`
  (id `7119d222f5f9db67…`) and `…-retention-n5/`.
* The core-domain half of the pair (NOT a gate, no bar reads it): CONTROL
  `SAME` worst-of-5 **44.79**, RETENTION **45.37**.

### 4.1 ⚠ HOW THIS FIGURE MAY AND MAY NOT BE QUOTED

> ### **THIS IS THE FIRST G6 DISTRIBUTION THE PROJECT HAS TAKEN ON A TREE WITH NO BUILD STAMP.  IT IS A NEW BASELINE, NOT A DELTA.**

* **AGAINST THE PASS BARS IT IS SCORED, AND IT PASSES**: Fmax ≥ 32 MHz on every
  draw, worst setup > 0 on every draw, TNS 0.000 setup and hold on every domain.
* ⚠ **AGAINST WAVE 7's 41.06 IT IS REPORTED AND NOT SCORED.**  WAVE 7's
  `worst-of-5` was drawn at stamp **260909**; this tree has no stamp at all, and
  removing the element is a perturbation of the same class and order as changing
  its characters (§8).  **CONTROL 40.62 against 41.06 is −0.44 MHz and that
  number is not attributable to anything.**  `standing_gates.md` §A governs and
  one green sweep is not closure.
* ⚠ **THE SPREAD IS 3.68 MHz ON BOTH CONFIGURATIONS** — coincidentally
  identical, reported as measured.  WAVE 7's five seeds spanned 0.603 ns
  (≈ 0.5 MHz at that operating point) on the NO-EXCEPTION configuration; these
  are WITH-exception sweeps and the two spreads are not comparable either.
  **No claim is made that removing the stamp narrowed or widened the remaining
  distribution**, and §10 records that as still uncharacterised.
* **RETENTION IS +1.01 MHz ABOVE CONTROL on the worst-of-5.**  The sign has
  flipped repeatedly across this project's history (`standing_gates.md` §A);
  **recorded, not explained.**
* ⚠ **`E11` MAKES THIS THE FIRST SWEEP WHOSE RECEIPTS PROVE THE CONDITION.**
  Every earlier sweep's receipt recorded which stamp it was taken under;
  none recorded that there was none, because there always was one.

---

## §5 M-5 — **THE FULL LADDER, BEFORE SIDE.**  TAKEN FIRST, ON THE UNCHANGED TREE.

`sw/phase_split_ladder.sh` — WAVE 7's own ladder driver, 32 legs, unedited —
run **before the first edit**, into `sw/testdata/wave12/before/`.
**Its `_rc.txt` is `diff`-identical to WAVE 7's `sw/testdata/wave7/before/_rc.txt`
leg for leg**, including the four registered non-zero exits (`hlt_w1/2/3`, `s16`)
and the registered refusal (`cc_div1_refused` rc=2).

| leg | registered | measured BEFORE |
|---|---|---|
| `check_core --opcodes all --cases 0` | 169,000 | **169,000 / 169,000** |
| `8F.0` | 500 | **500 / 500** |
| HLT sweeps, `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = **279/283** | **48+49 · 44+49 · 20+25 · 19+25 = 279/283**, survivors `w1.INT (10,busstat)×2` · `w2.INT (12,busstat)` · `w3.INT (14,busstat)` |
| `ulockstep --golden all --cases 50` | 17,350 | **17,350 / 17,350**, ALL LOCKSTEP |
| `check_boot` 220 / 400 | MATCH | **MATCH / MATCH** |
| `check_ab_sim` | 187 | **187 rows MATCH** |
| `sm3_s16_score --core ucore` | 1,320/1,371 | **1,320 / 1,371** |
| `ss_lint` | 232 / 228 flops | **PASS — 232, 228 architectural flops, 0 UNMAPPED** |
| `r7_lint` | PASS | **PASS — 0 violations** |
| `demux_off_gate` | PASS | **PASS** |
| `test_artifact` | 45/45 | **45 / 45** |
| `ucrom_mif_check` | PASS | **PASS** |
| `chain_lfsr_gate` | 4 signatures | **PASS, CHAIN_MAX 7, depth [6], 0 overflows**, `1d01c9b269ffaa94 · b39b040a98b28e5d · 0997b773cd99c030 · d05b6c3c3d9fbe78` |
| `test_quartus_gate` | 255/255 | **255 / 255** |
| `v0.1-w1` / `-w3` / `EB` | 1,200 · 1,200 · 200 | **1,200 · 1,200 · 200** |
| the four `evt` cells + biased | 200 · 1,200 · 200 · 1,200 · 1,200 | **identical** |
| `fz2_replay --all-failures --pass-sample 200 --leg ret` | — | 305 seeds, 101/101 `first_bad` identical |
| `check_core --ce-div 2 / 3 / 8` and `--ce-div 1` refused | — | rc 0 · 0 · 0 · **2** |

### 5.1 ⚠ THE TWO ROWS `standing_gates.md` HAS STALE — **MEASURED AND REPORTED, NOT TREATED AS FAILURES**

* **`ss_lint`.**  `standing_gates.md:1399` registers **226 addresses / 214
  flops / `SS_VERSION` 0x8D**.  The tree measures **232 / 228 / 0x8F**, which is
  **CLAUDE.md's WAVE 7 banner exactly** (*"232 / 228 flops / 0 UNMAPPED,
  `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8"*).  `standing_gates.md` is behind the
  CLAUDE.md banner by the wave-5/6/7 landings.  **The row is stale; the gate is
  green; nothing here moved it.**
* **`sm3_s16_score`.**  `standing_gates.md:1939` and CLAUDE.md both register
  **1,320 / 1,371** and that is what it measures.  The row that is out of date
  is the one in `standing_gates.md:2099` describing the `tb_v30_core` offline
  column at **1,347 / 1,371** — a *different instrument* on a different scale,
  and not this ladder's leg.  Named so that the next reader does not difference
  the two.

**NEITHER IS EDITED BY THIS WAVE.**  The blast radius is reported; the
coordinator decides (the WAVE 11 precedent, its bar L-6).

### 5.2 THE AFTER SIDE — **ZERO DELTA.**  **M-5 MET.**

The SAME 32-leg driver, run on the landed tree into `sw/testdata/wave12/after/`.

* **`_rc.txt` IS `diff`-IDENTICAL TO THE BEFORE SIDE, LEG FOR LEG** — all 32,
  including the four registered non-zero exits and the registered `--ce-div 1`
  refusal (rc=2).
* **THE SCORED FIGURES ARE BYTE-IDENTICAL**: 56 scored lines across every leg,
  compared as a multiset and then again leg by leg — **27 of 27 legs SAME.**
  `169,000` · `500` · `279/283` with the same four survivors and the same
  first-divergence coordinates · `17,350 ALL LOCKSTEP` · `220`/`400` · `187` ·
  `1,320/1,371` · `ss_lint` 232/228 · `r7_lint` 0 violations · `test_artifact`
  45/45 · `ucrom_mif_check` PASS · `demux_off_gate` PASS · `1,200`/`1,200`/`200`
  · every `evt` cell · `--ce-div 2/3/8`.
* **`chain_lfsr_gate`: the FOUR SIGNATURES ARE BYTE-IDENTICAL** —
  `1d01c9b269ffaa94 · b39b040a98b28e5d · 0997b773cd99c030 · d05b6c3c3d9fbe78`,
  with `CHAIN_MAX 7`, observed depth `[6]`, 0 overflows, 4 × 400,000 clocks.
* **`fz2_replay`: the scored-content `sha256` is IDENTICAL** —
  `b20fd311a10dc6e3…` over 305 rows — and so are the `tb_sys` receipt
  `567a334ca43b2feb…` and its declared tree hash.

#### 5.2.1 THE SEVEN LEGS WHOSE LOG TEXT MOVED, EACH ACCOUNTED FOR

A raw `diff -r` reports 7 of 35 files changed.  **None is a scored quantity**,
and they are enumerated rather than filtered away:

| leg | why it moved |
|---|---|
| `test_quartus_gate.log` | **255 → 287 checks, BY CONSTRUCTION.**  This is M-6's Q17 and it is the one intended move in the ladder.  Registered in advance, not discovered after |
| `chain_lfsr.log`, `check_ab_sim.log`, `tbsys_build.log` | the BEFORE run **REBUILT** its Verilator binaries and printed the g++/verilator transcript; the AFTER run found them current.  **The scored content of all three is identical**, receipts included |
| `demux_off.log` | Verilator's own `walltime` / `speed` lines |
| `fz2_replay.log`, `fz2_replay.json` | progress timings and the run timestamp.  **The scored rows hash identically** |

⚠ **`nec_test.sv` IS IN NO VERILATOR BUILD, AND THAT WAS CHECKED, NOT ASSUMED**
— no file list in `check_core`, `check_ab_sim`, `x1_retention`,
`chain_lfsr_gate` or `demux_off_gate` names it, and the only textual reference
to it in `sw/` is `quartus_gate.py`'s `input_files()`.  So the ladder's
invariance has a structural reason as well as a measurement.  **The measurement
was taken anyway**, because a structural argument is not a gate.

---

## §6 M-6 — **THE GATE THAT KEEPS IT REMOVED.  `quartus_gate` BAR E11.**  **MET.**

⚠ **IT IS `E11`, NOT `E10` — AN ERRATUM AGAINST THIS WAVE'S OWN FIRST DRAFT.**
`E10_promotion_width` already exists in `quartus_gate.py`'s distribution bars.
The new bar was written as `E10`, the collision was found by reading the file
rather than by recalling it, and it was renamed before anything was measured.
**The pre-registration names no bar number**, so nothing registered is affected.

### 6.1 ONE PREDICATE, TWO CHECKS

> *No file the compiler reads mentions the stamp macro, and `hdl/build_id.v`
> does not exist.*

The scanned list is **`input_files()` — the SAME closed list the manifest
already hashes** (98 files: both `.qsf`s, `nec_test.sdc`, `nec_test.sv`, the
whole `hdl/rtl/ucore/`, and every `.tcl`/`.v`/`.sv`/`.qip`/`.vhd` under
`hdl/sys/`).  So a **re-vendored generator is caught by its own text**, a
re-added ``include`` by the reference it needs, and a leftover generated file by
existing at all.  **THE TWO CHECKS ARE SEPARATE AND EACH IS TESTED ALONE**, so a
sources-only reintroduction cannot hide behind the file check or the reverse.

* **IT REFUSES, IT DOES NOT MERELY RECORD** — exit **2**, the reason named, the
  offending file named, and what it costs quoted.  A build under a re-introduced
  stamp is not comparable to one without it, and an incomparable figure that
  scores is worse than no figure.
* **NO QUIET PATH.**  The check runs in `main()` before `--dry-run`,
  `--parse-only`, the single build and the sweep alike.  *One rule with no
  exceptions is the only kind that survives*: the stamp came back into a build
  nobody edited.
* **AND IT IS RECORDED**: every receipt now carries `E11_no_build_stamp` with
  the scanned count and the hit map, in place of the old `build_id` field.
  ⚠ **The old field was not dishonest — it declared the exclusion in words, in
  every receipt, for months.  What was missing was a RULE.  This is the rule.**
* `BUILD_STAMP_TOKEN` is assembled from two halves (`"BUILD_" + "DATE"`) so that
  `quartus_gate.py` and its falsifier can **quote the token they refuse** without
  tripping a scan of themselves.  Named in the code, not hidden.

### 6.2 THE FALSIFIER, AND EVERY CLAUSE DEMONSTRATED FIRING

`sw/test_quartus_gate.py` **Q17**, and `Q1`/`Q9` re-registered for the
four-stage recipe.  **255 → 287 checks, PASS.**

| clause | demonstration |
|---|---|
| **the positive control, reported first** | the REAL tree passes; 98 files scanned == `len(input_files())`; `build_stamp_refusal()` returns `None`; the stamp file, the vendored generator and the hook's reference to it are all really gone |
| a synthetic CLEAN tree passes | the instrument is not stuck RED |
| **a regenerated `build_id.v`** | E11 **FIRES**, names the file with its `sha256`, and **the token clause stays quiet** — two clauses, not one |
| **the macro back in the RTL** | E11 **FIRES**, `token_hits == {"nec_test.sv": 1}`, and **the file clause stays quiet** |
| **a re-vendored `sys/build_id.tcl`** | E11 **FIRES** on the generator's own text — *the case the bar exists for* |
| **end to end** | a stamp planted in the real `hdl/`, `quartus_gate --dry-run` and `--dry-run --seeds 5` both **exit 2** naming the file, then the plant is removed in a `finally` and the gate **goes back to exit 0** |

⚠ **THE END-TO-END PROBE USES `--dry-run` DELIBERATELY**: it builds nothing, and
E11 is registered as having no quiet path, so a dry run is exactly where a
carved-out exemption would show up as a non-refusal.

---

## §7 WHAT CHANGED, FILE BY FILE

| file | change |
|---|---|
| `hdl/nec_test.sv` | the `` `include "build_id.v" `` and the `"V,v",…` element are gone; `"v,0;"` is the last element and loses its trailing comma.  ⚠ **The macro's NAME is deliberately not spelled anywhere in the file** — E11 scans it, and a comment that tripped the gate it documents would be a gate nobody could keep green.  The comment says so |
| `hdl/sys/build_id.tcl` → **`hdl/sys/gen_cdf.tcl`** | `generateBuildID_Verilog` **DELETED**.  **`generateCDF` KEPT BYTE FOR BYTE** — verified by reconstructing the original's kept region and comparing content, not by eye.  ⚠ **The CDF half is not this wave's business**: it writes `jtag.cdf`, which `sys.tcl:213` names as `CDF_FILE`.  Removing it would have been a SECOND change to the build, outside the instruction |
| `hdl/sys/sys.tcl:211` | `PRE_FLOW_SCRIPT_FILE` → `sys/gen_cdf.tcl` |
| `hdl/.gitignore` | the `build_id.v` entry is **REMOVED, deliberately**.  An ignored file that came back would be invisible to `git status`, **and that invisibility is half of why it hid for the whole campaign** |
| `sw/quartus_gate.py` | `preflow_command()` and `build_id_state()` deleted; **the `--retention` recipe is the RECORDED FOUR STAGES again** — the fifth stage existed only to write the stamp (added 2026-08-13, removed here; the four have never changed in content or order).  New bar **E11** |
| `sw/test_quartus_gate.py` | **Q17**, E11's own falsifier; Q1 and Q9 re-registered.  255 → **287** checks |
| `sw/run_adcone_anatomy.sh`, `sw/run_adcone_census.sh`, `sw/run_phase_split_anatomy.sh`, `sw/run_intcone_anatomy.sh` | the explicit `quartus_sh -t sys/build_id.tcl preflow` line deleted — its only purpose was the stamp |
| `sw/run_biu_roundtrip.py` | the `build_id.v` copy block deleted.  ⚠ Its care was well placed and **it was not enough**: it kept the stamp identical *within* a run and WAVE 11 found it differing *between waves* |

### 7.1 A CONSEQUENCE WORTH NAMING ON ITS OWN

**`input_manifest` NO LONGER HAS A DECLARED HOLE.**  The one build input it
could not hash does not exist.  `input_files()` is 98 files, `sha256`
`72d48c643b09a6aa…`, and there is nothing recorded beside it any more.

### 7.2 M-2 — **IT IS NOT USED.**  **MET, AND STATED PRECISELY.**

`sw/testdata/wave12/m2/m2_scan.txt`.

* **The macro token: ZERO occurrences** in any of the 98 files the compiler
  reads, in any `.qsf`, in any `.tcl` on any build path, and in any driver.
* **The string `build_id`** survives in exactly two roles, both named:
  **(a)** comments recording *what was removed and why* — `nec_test.sv`,
  `gen_cdf.tcl`, `.gitignore`, the four shell drivers, `run_biu_roundtrip.py`;
  **(b)** `quartus_gate.py`'s own `BUILD_STAMP_FILE = "build_id.v"` and the
  falsifier's use of it — **the gate's name for the thing it refuses.**
  **No executable reference to the file remains anywhere.**
* **RECORDS ARE LEFT ALONE AND COUNTED**: 11 `hdl/quartus_gate_*.log` build
  transcripts and 216 `sw/testdata/**` artifacts carry the old strings.  They
  are true records of builds that really were taken under a stamp, every one of
  them names its own stamp in its own receipt, and **not one is edited.**

---

## §9 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
* ⚠⚠ **THIS CHANGE MOVES THE BITSTREAM.**  `CONF_STR` loses ~26 characters and
  the OSD byte-mux is re-fitted; WAVE 11 measured that class of perturbation at
  up to 1.647 ns.  **A fabric figure taken on FLASH #21 or earlier may not be
  quoted against this tree** — already true since WAVE 7 for the EU's decode,
  and now true for a second, independent reason.
* ⚠⚠ **THE FABRIC CONFIRMATION OWED SINCE WAVE 7 IS STILL OWED, AND IT IS NOT
  THIS WAVE'S TO DISCHARGE.**  Nothing was flashed.
* Single-writer guard (`pgrep -x`, EXACT binary names) before every Quartus
  stage; `hdl/nec_test_ucore.qsf` `git checkout --`'d between runs.
* `~/.cache/ucsimt-tmp/`, never `/tmp`.
* **CONTENT COMPARED, NOT A SELF-COMPUTED DIGEST.**  The M-3 arms are `diff`ed
  whole against each other and against WAVE 11's committed artifacts; the two
  stamp `sha256`s are **the values WAVE 11 recorded, and the 260909 one is the
  value a COMMITTED RECEIPT holds** (`sw/testdata/g6dist/wave7-chainflat-noexc-control-n5/seed1_quartus_gate.json`, its `build_id` field) — reproduced here, not recalled.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  The M-3 scorer was run
  against WAVE 11's own three arms first and **reproduces 2,154 / 34.220 ·
  1,936 / 34.773 · 1,918 / 35.867 exactly and calls their artifacts DIFFERENT**
  — so a "they are identical" verdict on WAVE 12's arms is an instrument that is
  known to be able to say otherwise.  E11's falsifier likewise reports the real
  tree's PASS first and then fires every clause.
* No Codex.  No nested subagents.
* `git add` **BY EXPLICIT PATH ONLY**.

### 9.1 ⚠ AN INCIDENT, REPORTED BECAUSE IT HAPPENED

A malformed placeholder shell command in this session ran **`git stash`**, which
swept the **21 pre-existing modified files that are the user's and not this
wave's** into a stash.  It was noticed on the very next command, `git stash pop`
restored all 21, `git stash list` is **empty**, and **no commit of this wave
contains any of them** (`git show --stat` on both commits names only this wave's
files).  Nothing was lost.  **It is recorded because a truthful ledger records
the near-misses too**, and because the rule it nearly broke — *`git add` by
explicit path only, the user's working tree is not yours* — is in the brief for
the reason WAVE 7 demonstrated.

---

## §8 WHAT THIS DOES TO THE CAMPAIGN'S FIGURES

**IT CHANGES NOTHING THAT WAS ALREADY MEASURED, AND IT CHANGES EVERYTHING ABOUT
WHAT CAN BE MEASURED NEXT.**

* **WAVE 11's blast-radius table (`pcc0_settle_results_2026-09-12.md` §4.1)
  stands exactly as written.**  Every historical figure is still one stamp's
  draw, every cross-stamp delta still carries its unquantified term, and
  **removing the stamp does not retroactively repair a figure taken under one.**
  This wave does not re-derive a single historical number and does not overturn
  a single landing.
* **WAVE 11's rule — *two Quartus figures may be differenced only if they were
  compiled under the same `BUILD_DATE` stamp* — is now SATISFIED BY
  CONSTRUCTION for every build from `04efdc8d47` onward**, and that is the whole
  product of this wave.  The rule does not go away; it becomes trivially true
  going forward and stays a live caution about everything before.
* ⚠ **THE BOUNDARY IS A HARD ONE.**  A figure from before this commit and a
  figure from after it differ by the *removal of the element itself*, which is a
  perturbation of the same class and the same order as changing its two
  characters.  **A pre-WAVE-12 Quartus figure may not be differenced against a
  post-WAVE-12 one** any more than two stamps could be differenced against each
  other.  §4's baseline is therefore registered as a **NEW baseline**, not as a
  delta against WAVE 7's.
* **WAVE 11's §6 repair item — re-derive WAVE 9's `+15.188` against a same-stamp
  uncut arc — is UNAFFECTED AND STILL OWED.**  It needs a *same-stamp* pair, and
  the cheapest same-stamp pair available now is **two builds of this tree**.  It
  is one map and one fit and it is not this wave's.
* **Every FUNCTIONAL gate is untouched by construction** — none of them goes
  through Quartus and `build_id.v` was in no Verilator build.  §5 measures that
  rather than asserting it.

---

## §10 WHAT IS OWED

1. ⚠⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND IS STILL OWED.**
   The chain flattening changed the EU's decode; **a fabric figure taken on
   FLASH #21 or earlier may not be quoted against this tree.**  Nothing was
   flashed here and **it is not this wave's debt to discharge.**  ⚠ **THIS WAVE
   ADDS A SECOND REASON FOR THE SAME PROHIBITION**: the bitstream moved again.
2. **WAVE 11's one-fit repair** — re-derive WAVE 9's `+15.188 ns` cutting
   constant against a same-stamp uncut arc.  Still open, and now cheap: any two
   builds of this tree are same-stamp by construction.
3. **G-7's stamp provenance** (WAVE 11 §4.1, §6.5) was never established and is
   not established here.
4. **THE STAMP DIMENSION WAS NEVER CHARACTERISED AND NOW CANNOT BE, ON THIS
   TREE.**  Three stamps, one seed, one tree is all the evidence there will be.
   Whether `worst-of-N` over fitter seeds is a conservative or an optimistic
   estimator of the true worst case is **still not known**; what is known is that
   it is now a worst-of-N over the *only* dimension left.  **No claim is made
   that the remaining distribution is narrower** — §4 measures the seed spread
   and nothing else.
5. **`docs/notes/standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS
   WAVE.**  Two things want registering by the coordinator: the new bar **E11**
   and `test_quartus_gate` **287/287** in the standing set, and §5.1's stale
   `ss_lint` row.
6. **NOTHING IS CLAIMED ABOUT THE OSD.**  The version text is gone from the menu
   and nobody has looked at a menu.  The claim made is the RTL one, from
   `hps_io`'s source, and it is in §1.

### 9.2 ⚠ A SECOND ERRATUM, AGAINST THIS WAVE'S OWN LANDING COMMIT

`04efdc8d47` rewrote `hdl/.gitignore` through a Python `read_text`/`write_text`
round trip, and **the file had CRLF terminators**: the whole file silently
converted to LF, so a ONE-LINE change showed as **57 insertions and 57
deletions**.  Caught by reading the commit's own `--stat`, repaired at
`f527f35be0`, and the diff against the pre-landing tree is now exactly the
intended hunk.  `hdl/.gitignore` is **not** in `input_files()`, so no receipt and
no input manifest was affected by the defect or by the repair.
⚠ **`hdl/sys/gen_cdf.tcl` carries LF where `build_id.tcl` carried CRLF, and that
one is LEFT AS IT IS**: it **is** a build input, M-1's receipt
`df6e531f5b06ae5f…` was measured on those exact bytes, and changing a build
input after measuring it would invalidate a receipt to fix nothing.  **Recorded,
not repaired.**

---

## §11 THE BARS, SCORED

| bar | verdict |
|---|---|
| **M-1** it is not generated, demonstrated not asserted | **MET.**  §2.  A full `--flow compile` — the only PRE_FLOW-honouring path — produced no `hdl/build_id.v`, 0 `Error (10054)`, 0 `Generated:` lines, 0 macro occurrences, with a byte-identical `jtag.cdf` as the positive control that the hook still ran |
| **M-2** it is not used | **MET, AND STATED PRECISELY.**  §7.2.  **ZERO** occurrences of the stamp macro in any of the 98 files the compiler reads, any `.qsf`, any `.tcl` on any build path, or any driver.  The surviving `build_id` strings are comments recording the removal, plus the gate's own name for what it refuses.  **No executable reference remains.**  11 build logs and 216 `sw/testdata/` artifacts are RECORDS and are untouched |
| **M-3** the falsifier — the nondeterminism measurably gone | **MET ON ALL THREE REGISTERED QUANTITIES.**  §3.  Same `$v30u_ce` (2,175), same `T_min` to the thousandth (35.992), byte-identical `truefmax`.  **Δ = 0.000 ns where WAVE 11 measured 1.647.**  Residue reported as a number: 62 of 600 `rows.txt` lines at a different RANK, proved pure tie-ordering (multiset `diff` 0 lines; every displaced row equal-slack, equal-class) |
| **M-4** G6 PASSES on both configurations, `--seeds 5` | **MET.**  §4.  CONTROL `worst-of-5` **40.62 MHz**, RETENTION **41.63**, TNS 0.000 setup and hold on all 10 draws, 0 errors / 0 latches / 0 `lpm_divide`, configurations DERIVED, all ten `.rbf`s distinct.  Reported against WAVE 7's 41.06 and **NOT scored against it**, with the reason |
| **M-5** the full ladder is zero-delta | **MET.**  §5.  32 legs, `_rc.txt` `diff`-identical, **27 of 27 scored legs byte-identical**, 56 scored lines unmoved, four `chain_lfsr` signatures byte-identical, `fz2_replay` scored-content `sha256` identical.  Seven log files moved and **each is accounted for**; the only one that matters is `test_quartus_gate` 255 → 287, which is M-6 |
| **M-6** the gate that keeps it removed | **MET.**  §6.  Bar **E11** (not E10 — collision, erratum in §6), refusing with exit 2 on every path.  `test_quartus_gate` 287/287 with Q17: the real tree as positive control, then **every clause demonstrated FIRING** — regenerated file, macro back in the RTL, re-vendored `sys/build_id.tcl` — plus an end-to-end refusal of the tool itself with the plant removed in a `finally` |
| **M-7** the revert condition | **NOT TRIGGERED.**  M-4 passed on both configurations and no leg of M-5 moved.  **No bar was softened and none needed to be.** |

### 11.1 ⚠ THE TWO THINGS THIS WAVE GOT WRONG, BOTH CAUGHT AND BOTH RECORDED

1. **The new bar was written as `E10`, which already exists** (`E10_promotion_width`).
   Found by reading the file rather than recalling it, renamed to **E11** before
   anything was measured.  §6.
2. **A malformed placeholder command ran `git stash`**, sweeping the user's 21
   pre-existing modified files.  Caught on the next command, `git stash pop`
   restored all 21, and no commit of this wave contains any of them.  §9.1.

**Neither is a measurement defect.  Both are in this document because a ledger
that records only what went right is not a ledger.**
