# WAVE 13 — **THE PHASE SPLIT, MEASURED LIKE-FOR-LIKE FOR THE FIRST TIME.  IT IS WORTH +2.75 / +4.14 MHz AND THE GAP IS 1.47 / 0.85.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/phase_split_pinned_prereg_2026-09-13.md`, committed
at **`b4060b3944` BEFORE THE FIRST `hdl/` EDIT**.  Its bars **N-1 … N-9 are
quoted verbatim below and not one of them was softened, re-derived or re-scoped
after a result was seen.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**
No Codex consulted.  No nested subagent spawned.

| | |
|---|---|
| **Tree at entry** | `5f8128b88b` (`master`), `git status --porcelain hdl/` clean of tracked modifications |
| **The edits** | (c) `d3aa3900c5` · (a) `e067df84e4` · (b) `35395c8cc2` |
| **The arms** | `sw/testdata/g6dist/w13-{unsplit,split}-noexc-{control,retention}-n5/` |
| **The ladder** | `sw/testdata/wave13/{before,after}/` |
| **The revert** | see §8 |
| **Tool** | Verilator 5.032; Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` **31.250 ns** |

---

## §0 THE HEADLINE, IN FOUR SENTENCES

> **1. N-1 IS FAILED, AND THE GAP IS THE SMALLEST THIS CAMPAIGN HAS EVER
> MEASURED.**  With no exception of any kind in `nec_test.sdc`, CONTROL's
> `worst-of-5` is **30.53 MHz** (0 of 5 draws PASS) and RETENTION's is **31.15**
> (**3 of 5 draws PASS** — 32.43 · 32.53 · 32.75 — with seeds 3 and 5 RED).
> **THE GAP TO 32.0 IS 1.47 MHz (CONTROL) AND 0.85 (RETENTION).**
>
> **2. N-3 IS DELIVERED AND IT IS THE WAVE'S PRODUCT.**  Both arms drawn on
> THIS stamp-free tree, by ONE driver, at ONE seed set: UNSPLIT **27.78 /
> 27.01** against SPLIT **30.53 / 31.15**.  **THE PHASE SPLIT IS WORTH
> +2.75 MHz (CONTROL) AND +4.14 (RETENTION).**
>
> **3. THAT IS LARGER THAN WAVE 9 REPORTED, IN EXACTLY THE DIRECTION WAVE 11
> PREDICTED AND BY MORE THAN THE STAMP.**  WAVE 9 quoted +1.74 / +2.27 by
> differencing a `260912` split arm — the SLOW stamp — against a `260909`
> baseline — the FAST one.  Like-for-like it is **+1.01 and +1.87 larger.**
>
> **4. THE TREE IS BIT-EXACT AND THE SAVE STATE DID NOT MOVE.**  **29 SAME /
> 2 MOVED / 0 MISSING** on the 33-leg ladder with **both movers registered
> before they were seen**; the four `chain_lfsr` signatures byte-identical over
> 1.6 M clocks; `fz2_replay` scored content identical **field by field**;
> `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 unchanged.  **N-1 still
> fails, so the split does not land** (§8).

---

## §1 N-3 — **THE LIKE-FOR-LIKE DELTA.  THE FIRST STAMP-FREE MEASUREMENT OF THE PHASE SPLIT'S BENEFIT.**  **DELIVERED.**

Both arms: `sw/run_wave13_g6.sh`, `quartus_gate.py --seeds 5` and
`--seeds 5 --retention`, seed set **{1,2,3,4,5}**, one shared `quartus_map` per
configuration, the single-writer guard by EXACT binary name **one pattern per
`pgrep -x` call**, and `hdl/nec_test_ucore.qsf` restored with
`git checkout -- <that exact path>` around every run.

> | | UNSPLIT, no exception | SPLIT, no exception | **THE SPLIT IS WORTH** | **GAP TO 32.0** |
> |---|---:|---:|---:|---:|
> | **CONTROL `worst-of-5`** | **27.78** | **30.53** | **+2.75 MHz** | **1.47** |
> | **RETENTION `worst-of-5`** | **27.01** | **31.15** | **+4.14 MHz** | **0.85** |

### 1.1 WHY THIS NUMBER IS DIFFERENT FROM EVERY EARLIER ONE

**EVERY PHASE-SPLIT FIGURE BEFORE THIS WAVE WAS CROSS-STAMP.**  WAVE 11 measured
`hdl/build_id.v` — a gitignored `%y%m%d` date stamp in a string the CPU never
sees — at **1.647 ns / 1.34 MHz at one seed**, against WAVE 7's **0.603 ns**
over five fitter seeds: *the uncontrolled dimension was the larger one*.
WAVE 12 removed it and measured the nondeterminism gone at **Δ = 0.000 ns**.

WAVE 9's split draws are stamp **`260912`**, the SLOW one; the WAVE 7 baseline
it improved on is **`260909`**, the FAST one.
`pcc0_settle_results_2026-09-12.md` §4.1 said so at the time and said which way
it was signed: *"the split's true benefit against a same-stamp baseline is
**LARGER**, not smaller."*

> ### **MEASURED: +2.75 AGAINST WAVE 9's REPORTED +1.74, AND +4.14 AGAINST ITS +2.27.  THE PREDICTION HELD IN SIGN ON BOTH CONFIGURATIONS AND THE MISSING BENEFIT IS 1.01 AND 1.87 MHz.**

⚠ **AND IT IS NOT SIMPLY *"THE STAMP WAS WORTH 1.34 MHz"*.**  The CONTROL
discrepancy (1.01) is close to WAVE 11's one-seed stamp figure and the RETENTION
one (1.87) is larger than it.  **NO ATTRIBUTION IS MADE.**  A `worst-of-5` is
not a single draw, WAVE 11's 1.647 ns was measured at seed 1 on one tree, and
WAVE 12 §8 forbids differencing a pre-WAVE-12 figure against a post-WAVE-12 one
in the first place.  **What is established is that WAVE 9's delta was
understated and by how much a same-tree measurement now says it was.**

### 1.2 ⚠ HOW THESE FIGURES MAY AND MAY NOT BE QUOTED

* **THE +2.75 / +4.14 ARE QUOTABLE AS THE PHASE SPLIT'S BENEFIT**, and they are
  quotable *because* both arms are post-WAVE-12, same tree, same driver, same
  seed set, with **E11 true on all twenty draws** (N-4).
* ⚠ **NEITHER ARM MAY BE DIFFERENCED AGAINST WAVE 7's 28.32 / 28.90 OR WAVE 9's
  30.06 / 31.17.**  WAVE 12 §8's boundary is hard: removing the OSD element is a
  perturbation of the same class and order as changing its two characters.
  27.78 is **not** "WAVE 7's 28.32, minus 0.54".
* ⚠ **`standing_gates.md` §A GOVERNS**: the same tree has drawn 19.42 and
  45.91 MHz.  One green build is not closure — **and the converse holds too**,
  so ten RED-or-mixed draws are not a proof that no phase split can close, only
  that these did not on these draws.

### 1.3 A CROSS-CHECK NOBODY REGISTERED, REPORTED BECAUSE IT LANDED

The UNSPLIT CONTROL arm's **seed 1 reads 27.78 MHz**.  WAVE 12 §3 measured this
same configuration — unsplit RTL, no exception, seed 1, CONTROL, stamp-free —
at **T_min 35.992 ns = 27.78 MHz**, through an entirely different pipeline
(`run_biu_roundtrip.py`: `quartus_map` + `quartus_fit` + `quartus_sta`, no
assembler, no receipt).  **Two drivers, one answer.**

---

## §2 N-1 — **THE REQUIREMENT.  FAILED, ON A DISTRIBUTION THAT DOES NOT REACH 32.0.**

`sw/testdata/wave13/n1_n3_score.txt` holds the scorer's full output.

### 2.1 CONTROL — record `dade9aa471fb265d…`, `worst-of-5@seeds{1,2,3,4,5}` = **30.53 MHz**

| seed | Fmax | worst setup | ALMs | core `SAME` k | `off_class` | E11 |
|---|---:|---:|---:|---:|---|---|
| 1 | 31.11 | −0.895 | 8,018 (19 %) | 1.0 | `[]` | pass |
| **2** | **30.53** | **−1.506** | 8,024 | 1.0 | `[]` | pass |
| 3 | 30.85 | −1.162 | 8,011 | 1.0 | `[]` | pass |
| 4 | 30.98 | −1.025 | 8,030 | 1.0 | `[]` | pass |
| 5 | 30.62 | −1.413 | 8,006 | 1.0 | `[]` | pass |

> worst **30.53** · median 30.85 · best 31.11 · **spread 0.58** · **0 of 5 PASS**

### 2.2 RETENTION — record `87e9df8c2ffbd54d…`, `worst-of-5` = **31.15 MHz**

| seed | Fmax | worst setup | ALMs | core `SAME` k | `off_class` | E11 | |
|---|---:|---:|---:|---:|---|---|---|
| 1 | **32.43** | **+0.414** | 8,255 (20 %) | 1.0 | `[]` | pass | **PASS** |
| 2 | **32.75** | **+0.713** | 8,228 | 1.0 | `[]` | pass | **PASS** |
| **3** | **31.15** | **−0.855** | 8,215 | 1.0 | `[]` | pass | RED |
| 4 | **32.53** | **+0.509** | 8,221 | 1.0 | `[]` | pass | **PASS** |
| 5 | 31.82 | −0.177 | 8,240 | 1.0 | `[]` | pass | RED |

> worst **31.15** · median 32.43 · best 32.75 · spread 1.60 · **3 of 5 PASS**

### 2.3 ⚠⚠ **THREE DRAWS CLEARED 32.0 AND N-1 IS STILL FAILED, BECAUSE N-1 SAYS *EVERY DRAW*.**

> ### **THESE ARE THE FIRST NO-EXCEPTION DRAWS THIS CAMPAIGN HAS EVER PUT ABOVE THE BAR.  THAT IS WORTH RECORDING.  IT IS NOT WORTH RE-READING THE BAR FOR.**

**RETENTION seed 5 misses by 0.177 ns of setup and seed 3 by 0.855.**  A
`worst-of-N` gate exists precisely so that a favourable draw cannot be quoted as
closure; scoring this arm on its median (32.43) or its best (32.75) would be
choosing a statistic after seeing the result.  **No bar was softened.  Nothing
was re-scoped.**  E2 (0 errors, every stage Successful) passes on all ten;
E3/E4/E5 fail together on the RED draws, which is one failure reported three
ways and not three.

### 2.4 WHAT IS RECORDED AND NOT EXPLAINED

* **THE SPLIT MAKES THE DESIGN SMALLER, FOR THE THIRD WAVE RUNNING.**  It adds
  **778 bits of flop** and CONTROL's fitted design falls **8,318–8,353 →
  8,006–8,030 ALMs**.  WAVE 9 §3 and WAVE 4 §3.2 recorded the same shape.  A&S
  combinational counts are not reproducible run to run (§74.4a);
  `standing_gates.md` §A governs.
* **CONTROL's SPREAD IS 0.58 MHz**, the tightest this arm has shown (unsplit
  1.28, WAVE 9 0.89), while RETENTION's is **1.60** (unsplit 1.57, WAVE 9 0.49).
  **No claim is made that the distribution narrowed** — WAVE 12 §10 item 4
  records the remaining spread as uncharacterised, and one sweep does not
  characterise it.
* **RETENTION IS ABOVE CONTROL ON BOTH ARMS OF THIS WAVE** (+0.62 split, −0.77
  unsplit).  The sign has flipped repeatedly across this project's history
  (`standing_gates.md` §A); **recorded, not explained.**

---

## §3 N-2 — **THE EXCEPTION IS GONE AND IT IS CHECKED, THREE WAYS, ON ALL TWENTY DRAWS.**  **MET.**

1. **`hdl/nec_test.sdc` carries ZERO uncommented `set_multicycle_path` and ZERO
   `set_false_path`.**  Two matches survive in the file and both are inside the
   deletion banner's historical quotation of the lines that were removed
   (`nec_test.sdc:237-238`, under *"⚠ DO NOT RESTORE IT FROM `git show`"*).
2. **No *"CE multicycle"* `post_message`.**  The live one reads *"NO ce->ce
   exception — N ce-gated v30u core registers are checked SINGLE-CYCLE"*.
3. **Every receipt's `core_domain` reports `SAME`, `INTO` and `OUTOF` at
   measured k = 1.0 against a nominal of 1.0, with an EMPTY `off_class`, on
   20 of 20 draws.**  The nominal fell with the constraint (edit (c) moves
   `nominal["SAME"]` 2.0 → 1.0), so a draw still fitted to the exception would
   land in `off_class` and be reported.  **None did, on either arm.**

⚠ **THE POLARITY IS WAVE 9's, NOT WAVE 7's.**  WAVE 7 deleted the exception
temporarily and left the nominal at 2.0, so its proof was `off_class ==
['SAME']` at k = 1.0.  This is a landing attempt, so the nominal falls with the
constraint and a conforming draw reports EMPTY.  **A reader comparing the two
`off_class` fields across waves without reading the nominal will draw the
opposite conclusion from the right data.**

---

## §4 N-4 — **BAR E11 IS TRUE ON EVERY ONE OF THE TWENTY DRAWS.**  **MET.**  *This is what makes N-3 like-for-like.*

`E11_no_build_stamp` reads `pass` on **all four distribution receipts and all
twenty per-seed receipts**: `hdl/build_id.v` absent, `token_hits` **{}**,
**98 files scanned** on the unsplit arm and **99** on the split arm (the cut
set's `v30u_eu_preload.svh`).

**A SINGLE FALSE E11 WOULD HAVE VOIDED N-3.  THERE IS NONE.**

Recorded beside it, because a landing needs them:

| | UNSPLIT | SPLIT |
|---|---|---|
| `input_manifest` | **`2e3fffa743ab2b22…` / 98 files** | **`d4ecdeff14444248…` / 99 files** |
| identical between the two configurations of the arm | **YES** — so they differ by the `--verilog_macro` and nothing else | **YES** |
| different between the arms | — | **YES — the check that the RTL edits reached the compiler** |
| `configuration` DERIVED from the reports | 5 CONTROL + 5 RETENTION | 5 CONTROL + 5 RETENTION |
| `.rbf`s distinct within a sweep (E-9) | 5 of 5, both | 5 of 5, both |

---

## §5 N-5 / N-6 / N-7 / N-8 — **THE TREE IS BIT-EXACT AND THE SAVE STATE DID NOT MOVE.**

### 5.1 THE BEFORE SIDE, TAKEN ON THE UNEDITED TREE FIRST (`a5fc545f2d`)

`sw/phase_split_ladder.sh` — WAVE 7's own 33-leg driver, unedited — into
`sw/testdata/wave13/before/`.  Its `_rc.txt` is **`diff`-identical to WAVE 12's
after-side leg for leg**, and `phase_split_ladder_diff.py` reads **31 SAME /
0 MOVED / 0 MISSING** against it.  Every leg at its registered value.

### 5.2 N-6 — THE AFTER SIDE.  **29 SAME / 2 MOVED / 0 MISSING**, and `_rc.txt` `diff`-IDENTICAL BEFORE vs AFTER on all 33 legs

| leg | registered | measured, BOTH SIDES |
|---|---|---|
| `r7_lint` | PASS | **PASS — 0 undeclared carriers / 0 undeclared unresolved / 0 `stop` sites** |
| `check_core --opcodes all --cases 0` | 169,000 | **169,000 / 169,000** |
| `8F.0` | 500 | **500 / 500** |
| HLT sweeps, ⚠ `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = **279/283** | **97 · 93 · 45 · 44** |
| `v0.1-w1` / `-w3` | 1,200 / 1,200 | **1,200 / 1,200** |
| `v0.1-w1 --opcodes EB` | 200 | **200** |
| the four `evt` cells | 200 / 1,200 / 200 / 1,200 | **identical** |
| `v0.1-w1evt-biased` | 1,200 | **1,200** |
| `ulockstep --golden all --cases 50` | 17,350 ALL LOCKSTEP | **ALL CASES LOCKSTEP** |
| `ghost_launch_law score` | 200/200 | **200/200 = 100.0 %** |
| `check_boot --core ucore` | 220 and 400 | **MATCH 220, MATCH 400** |
| `check_ab_sim --core ucore` | 187 | **MATCH over 187 rows** |
| `sm3_s16_score --core ucore` | 1,320/1,371 | **1,320 / 1,371** |
| `test_artifact` | 45/45 | **45 / 45** |
| `test_quartus_gate` | 287/287 | **287 / 287** |
| `ucrom_mif_check` | PASS | **PASS** |
| **N-8** `--ce-div 2 / 3 / 8` | 169,000 each | **169,000 / 169,000 each** |
| **N-8** `--ce-div 1` | REFUSED | **REFUSED, clause cited, exit 2** |

**N-8 IS A CORRECTNESS BAR HERE, NOT A FORMALITY**: the split makes S-1 (*at
least one `ce_half` between consecutive `ce`s*) load-bearing for the EU, because
without it stage 2 consumes a STALE stage 1.

#### 5.2.1 THE TWO MOVERS, BOTH REGISTERED BEFORE THEY WERE SEEN, NEITHER A MEASUREMENT

* **`ss_lint`** — `ss_flopcensus` **228 → 229** architectural flops, whitelist
  **3 → 4**.  That IS N-7's *"grown by exactly the shadow's entry"*, and the
  entry is **`s1q`** on the **DERIVED** class beside `dec_q`.
* **`demux_off_gate`** — its own summary line, *"the three muxed ports are
  GONE"* → *"the two"*.  Edit (a)'s registered consequence (prereg §2,
  WAVE 9 §2.3): splicing `.CE_HALF` into a define-off build now SUCCEEDS, and
  asserting that it fails would be asserting something false.  **The gate
  PASSES**, and its `AD` and `AD_OE` clauses still REFUSE **naming their pins**,
  which is what keeps the leg non-vacuous.

### 5.3 N-5 — PIN IDENTITY.  **MET, AND THE COMPARISON IS OF CONTENT.**

* **`chain_lfsr_gate` — `diff`-BYTE-IDENTICAL ROW FOR ROW, BEFORE vs AFTER.**
  Signatures `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` ·
  `d05b6c3c3d9fbe78`; `CHAIN_MAX` 7, `CHAIN_DEPTH_MAX` **6**, `entry_st` **25**,
  `ce_clocks` 66,648 / 66,664 / 66,521 / 66,559, `g0` 8,233 / 8,394 / 8,114 /
  8,204, `coincide` **0**, 0 overflows, 4 × 400,000 fabric clocks.
  ⚠ **THAT IS ALSO 1.6 M CLOCKS OF THE SHADOW'S OWN `$fatal`**: the split
  asserts `s1q !== s1_bus` at every `ce`, and it never fired.
* **`fz2_replay` — SCORED CONTENT IDENTICAL, COMPARED FIELD BY FIELD** over all
  305 rows and the tables.  N-5 says *"compare the named fields directly, NOT a
  digest you computed yourself"*, so `sw/wave13_replay_fieldcmp.py` walks
  `rows` and `tables` key by key.  **ITS POSITIVE CONTROL FIRES IN THE SAME
  RUN**: perturb one field of one row of a copy and it reports
  `rows[0].cid` **by name**.  The repo's own registered instrument agrees —
  scored-content sha256 **`de949fd373ed77de…`**, the value `CLAUDE.md`
  registers.  The `tb_sys` receipt moved (`567a334ca43b2feb…` →
  `19aba976791630b9…`) and is **NOT quoted as evidence of anything**: a
  Verilator receipt moves across rebuilds of a byte-identical tree.

### 5.4 N-7 — SAVE STATE DID NOT MOVE.  **MET.**

`ss_lint --core ucore` exits **0**.  `SS_VERSION` **0x8F** / `SS_COUNT` **232**
(109×2 BIU + 122×2 EU + tag) / `SS_TAG` **0x8FE8** — **ALL UNCHANGED** — and
`hdl/rtl/ucore/v30u_ss_pkg.sv` is **untouched by every commit of this wave**.
**0 UNMAPPED** on both blocks and on both sides.  The whitelist grows by
**exactly one entry**, `s1q`, admitted on the DERIVED ground, naming the place
the derivation is checkable by eye, and with the derivation `$fatal`-asserted
rather than assumed.

### 5.5 SUPPORTING, NOT SCORED — the two lints on the cut tree

`sw/cutset_lint.py` **PASS — 80 members / 0 violations**, `live-tainted
members: none`; `sw/phase_split_lint.py` **PASS — 156 members / 778 bits /
0 violations**, `live-in-stage1: none`.

⚠ **NEITHER IS QUOTED AS A NON-VACUITY DEMONSTRATION.**  WAVE 9 §6 ran
`sw/cutset_nonvacuity.py` and made both FAIL on three kinds of re-introduced
bypass (B / B2 / **B3**, the last being the arm-file case that would otherwise
have let the lint pass vacuously on every tree since WAVE 7).  **This wave
re-applies that cut set byte for byte and does not re-derive its
falsification.**  Stated so the PASS above is read for what it is.

### 5.6 ⚠ THE STALE ROW — **MEASURED AND REPORTED, NOT TREATED AS A FAILURE**

`standing_gates.md:1399` registers `ss_lint` at **226 addresses / 214 flops /
`SS_VERSION` 0x8D**.  The tree measures **232 / 228 / 0x8F** on the *before*
side, which is CLAUDE.md's WAVE 7 banner exactly.  The row is behind by the
wave-5/6/7 landings.  **N-6 registered this in advance**; the row is stale, the
gate is green, and **nothing in this wave moved it**.  `standing_gates.md` and
`CLAUDE.md` are **NOT EDITED BY THIS WAVE** — the coordinator decides
(the WAVE 11 / WAVE 12 precedent).

---

## §6 THE CHERRY-PICKS — **ALL THREE APPLIED; NOTHING WAS RE-DERIVED**

Registered in the pre-registration as *"the results document reports whether the
sequenced pick fuzzed, conflicted or applied, and says so either way."*

| edit | files | how it applied |
|---|---|---|
| **(c)** `bacf7f9fd9` | `nec_test.sdc`, `quartus_gate.py`, `sta_truefmax_probe.tcl`, `test_quartus_gate.py` | SDC and probe at their recorded positions; **`quartus_gate.py` hunk #1 at an OFFSET of 66 lines** and **`test_quartus_gate.py` hunk #1 at an OFFSET of 11 lines** — the two files WAVE 12 rewrote for bar E11 |
| **(a)** `6e822bf750` | `v30_core.sv`, `tb_demux_min.sv`, `demux_off_gate.py` | **all three cleanly, no offset** |
| **(b)** `5cf3254104` | `v30_core.sv`, `v30u_eu.sv`, **new** `v30u_eu_preload.svh`, `cutset_lint.py`, `ss_flop_whitelist_ucore.txt` | **all five cleanly, no offset** |

> ### **AN OFFSET IS NOT FUZZ.**  The context matched exactly, no hunk was rejected, and **`git diff <the WAVE 9 commit> -- <its files>` is EMPTY after each pick** — the tree is byte-identical to WAVE 9's at each stage.  **NOTHING WAS RE-DERIVED.**

WAVE 12 did not touch `hdl/rtl/ucore/`, which is why (a) and (b) were clean; the
two offsets in (c) are exactly the files WAVE 12 did rewrite.

⚠ **EDIT (c) WAS APPLIED FIRST AND WAVE 9 APPLIED IT LAST.**  That inversion was
registered **in advance**, in the pre-registration's §4.1, with its reason: this
wave is not asking WAVE 9's J-8 (*no regression WITH the exception*), it is
asking N-3's question, and that needs the UNSPLIT arm compiled under **the same
SDC and the same driver** as the split arm.  Applying (c) to the unsplit RTL is
**functionally inert and OVER-constraining, never under-**: no Verilator gate
can see an SDC, and the intermediate tree is a correct design measured against a
budget it does not need.  **Its RED result is N-3's baseline, not a result
against the design**, and that too was registered before it was drawn.

---

## §7 THE VERDICT TABLE, SCORED AS REGISTERED

| bar | verdict |
|---|---|
| **N-1** the requirement (`--seeds 5`, E1-E5 EVERY draw, BOTH configurations, no exception) | **FAILED.**  CONTROL `worst-of-5` **30.53** (0 of 5 PASS), RETENTION **31.15** (**3 of 5 PASS**, seeds 3 and 5 RED).  **GAP 1.47 / 0.85 MHz.**  §2 |
| **N-2** the exception is GONE and CHECKED | **MET** — zero uncommented `set_multicycle_path` / `set_false_path`, no *"CE multicycle"* info line, and **every one of the twenty receipts reports k = 1.0 against a nominal of 1.0 with an EMPTY `off_class`**.  §3 |
| **N-3** the like-for-like delta, DUE WHATEVER N-1 SAYS | **DELIVERED, AND IT IS THE WAVE'S PRODUCT.**  UNSPLIT **27.78 / 27.01** → SPLIT **30.53 / 31.15** = **+2.75 / +4.14 MHz**, one tree, one driver, one seed set.  **+1.01 and +1.87 larger than WAVE 9's cross-stamp figures, in the direction WAVE 11 predicted.**  §1 |
| **N-4** E11 true on EVERY receipt | **MET on all 20 draws** and all four distributions — 98 / 99 files scanned, 0 hits, no `build_id.v`.  **N-3 is not voided.**  §4 |
| **N-5** pin identity | **MET** — `chain_lfsr_gate` four signatures and every gap count **`diff`-BYTE-IDENTICAL**; `fz2_replay` scored content **IDENTICAL FIELD BY FIELD** over 305 rows, with the comparator's positive control firing in the same run.  §5.3 |
| **N-6** the ladder at its registered values | **MET** — `_rc.txt` `diff`-identical on all 33 legs, **29 SAME / 2 MOVED / 0 MISSING**, both movers registered in advance and neither a measurement.  §5.2 |
| **N-7** save state does not move | **MET** — `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 / 0 UNMAPPED, ALL UNCHANGED; `v30u_ss_pkg.sv` untouched; whitelist 3 → **4**, grown by **exactly the shadow's one entry**.  §5.4 |
| **N-8** divisor independence | **MET** — 169,000 / 169,000 at `--ce-div` 2, 3, 4 and 8; `--ce-div 1` REFUSED, clause cited.  §5.2 |
| **N-9** the disposition | **THE REVERT ARM IS TAKEN.**  N-1 failed, so the split does not land; all three edits are reverted, the gap is reported explicitly in both directions, and **N-3 is delivered anyway.**  §8 |

---

## §8 N-9 — **THE DISPOSITION, APPLIED AS WRITTEN**

N-9 is unambiguous and was written before either outcome was known:

> *"If N-1 FAILS — revert all three edits, report the GAP to 32.0 explicitly,
> and N-3 is still delivered.  A wave that reports 'still N MHz short, measured
> cleanly for the first time' has done its job.  Do not soften a bar to make a
> landing possible and do not re-scope after seeing a result."*

> ### **THE GAP IS 1.47 MHz (CONTROL) AND 0.85 MHz (RETENTION).**
>
> **RETENTION's worst draw misses by 0.855 ns of setup and its second-worst by
> 0.177 ns.  THREE OF ITS FIVE DRAWS CLEAR THE BAR AND THAT IS NOT WHAT N-1
> ASKED.**

**No bar was softened.  Nothing was re-scoped after a result.  Nothing was
flashed and no board was touched.**  The revert is `§8.1`; both documents are
kept; every artifact is retained.

### 8.1 THE REVERT, MEASURED AND NOT ASSERTED

See the revert commit for the measured statement.  What is reverted: edits
**(a) `e067df84e4`**, **(b) `35395c8cc2`** and **(c) `d3aa3900c5`**.  What is
**deliberately NOT reverted**: this wave's own instruments
(`sw/run_wave13_g6.sh`, `sw/wave13_score.py`,
`sw/wave13_replay_fieldcmp.py`) and every artifact under
`sw/testdata/wave13/` and `sw/testdata/g6dist/w13-*`.  They touch no `hdl/`
file, and the score they produced is the wave's product.

---

## §9 WHAT THIS WAVE ESTABLISHED, AND IT IS NOT NOTHING

1. **THE PHASE SPLIT'S BENEFIT IS NOW A MEASURED, SAME-TREE, SAME-STAMP
   QUANTITY: +2.75 MHz (CONTROL) and +4.14 (RETENTION).**  Every earlier figure
   for it was cross-stamp and every earlier figure **understated it**.
2. **THE GAP IS 1.47 / 0.85 MHz AND IT IS THE SMALLEST THIS CAMPAIGN HAS
   MEASURED.**  RETENTION's median draw is **above** the bar.
3. **THE MECHANISM IS BIT-EXACT AT 778 BITS** over 169,000 goldens at four
   divisors, 17,350 `ulockstep` scenarios, 1.6 M `chain_lfsr` clocks
   byte-identical and 305 `fz2_replay` rows identical field by field — **with
   the phase-stability premise `$fatal`-asserted every `ce` and never once
   violated**, and `SS_COUNT` / `SS_VERSION` / `SS_TAG` unmoved.
4. **WAVE 9's DIAGNOSIS IS UNCHALLENGED AND IS WHERE THE REMAINING GAP LIVES.**
   WAVE 9 §5.4 named the binding class to the node on **200 of 200** paths: the
   EU → BIU → EU combinational round trip through `q_cnt` → **`q_ripe_lead_n`**,
   `r7_lint`'s own declared UNRESOLVED carrier, **2.786 ns**, whose midpoint is
   **outside `v30u_eu`** so no cut set inside that module can divide it.  This
   wave did not re-run that diagnosis — it re-ran the *measurement* — and
   nothing here contradicts it.  ⚠ **Against a shortfall now of 1.47 / 0.85 MHz
   rather than WAVE 9's 1.94 / 0.83, that arc remains the named next
   mechanism**, and `sw/sta_cutset_biu_census.tcl` is the instrument that scores
   it.
5. **AN INSTRUMENT DEFECT OF THIS WAVE'S OWN, CAUGHT AND RECORDED.**
   `sw/run_wave13_g6.sh` carried `set -e`, and `quartus_gate.py` **exits
   non-zero on a `RED` verdict** — so the driver died after the UNSPLIT CONTROL
   sweep, before RETENTION and before its `.qsf` restore.  **A driver that stops
   on the result it was written to measure is an instrument defect, not a build
   failure.**  Caught by this wave's own stall detector; the CONTROL
   distribution was already written and unaffected; `hdl/nec_test_ucore.qsf` was
   measured CLEAN afterwards; the cost was a restart of one half.  Fixed with
   `set -u`, RED tolerated with the reason named in the file, and a half
   selector so a resumed arm never re-draws a completed leg.
6. **AND A SECOND ONE, IN THE SESSION'S OWN WAITERS.**  `pgrep -f
   phase_split_ladder.sh` **SELF-MATCHES** the waiting shell's own command line,
   so a waiter written that way never sees the ladder exit and reads "still
   running" forever.  The ladder's `_rc.txt` is the authority for completion and
   is what was read.  ⚠ **`pgrep -x` by EXACT BINARY NAME — the form the brief
   mandates for the Quartus guard — does not have this failure mode**, and
   `run_wave13_g6.sh` uses it, one pattern per call.

---

## §10 WHAT IS OWED

1. ⚠⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND IS STILL OWED.**
   WAVE 7 changed the EU's decode; **WAVE 12 added a second, independent reason**
   by moving the bitstream.  **A fabric figure taken on FLASH #21 or earlier may
   not be quoted against this tree.**  Nothing was flashed here and **this wave
   reverts, so nothing new is owed for it.**
2. **THE NEXT MECHANISM IS NAMED AND IT IS NOT A PHASE SPLIT**: break the
   EU → BIU → EU combinational round trip through `q_ripe_lead_n`.  WAVE 9 §8.3
   item 2 booked it; the shortfall it must cover is now **1.47 / 0.85 MHz**.
3. **WAVE 11's ONE-FIT REPAIR** — re-derive WAVE 9's `+15.188 ns` cutting
   constant against a same-stamp uncut arc — is **STILL OPEN**.  ⚠ **This wave
   makes it cheaper than WAVE 12 said**: `sw/testdata/wave13/` now holds a
   same-tree, same-stamp UNSPLIT/SPLIT pair at five seeds each, so the arithmetic
   needs no new compile, only the arc probes.
4. **`docs/notes/standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS
   WAVE.**  Two things want registering by the coordinator: §5.6's stale
   `ss_lint` row (226 / 214 / 0x8D against the tree's 232 / 228 / 0x8F), and
   WAVE 12's still-unregistered bar **E11** with `test_quartus_gate` **287/287**.
5. **`check_core --ss-sweep` IS STILL NOT ON ANY REGISTERED LADDER.**  Booked by
   WAVE 2, WAVE 3, WAVE 4 and WAVE 9; **not run here either.**  The resume path
   is the one place the shadow's derivation is not covered by the runtime
   assert, which excludes `ss_we` by construction.  **BOOKED for the fifth
   time**, and the repetition is itself worth noticing.
6. **NOTHING IS CLAIMED ABOUT WHY RETENTION BEATS CONTROL** on both arms of this
   wave, nor about why the split shrinks the fitted design.  Both are recorded
   in §2.4 and neither is explained.

---

## §11 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
* Single-writer guard before every Quartus stage, `pgrep -x` by EXACT binary
  name, **one pattern per call**.
* `hdl/nec_test_ucore.qsf` `git checkout -- <that exact path>`'d around every
  Quartus run, and measured clean after each arm.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  The **21 pre-existing modified files that are the user's own uncommitted
  work** and the 14 untracked `hdl/quartus_gate_*.log` files are **untouched**;
  `git add` was **BY EXPLICIT PATH ONLY** on every commit.  ⚠ **AND THIS WAVE
  ADDS NONE TO THAT CLASS — CHECKED AGAINST `ls hdl/*.log` AND `git status`,
  NOT AGAINST RECALL.**  An earlier draft of this section asserted two new
  `hdl/quartus_gate_w13_*.log` files by analogy with WAVE 9; **there are none**,
  because this wave passed `--log` into `sw/testdata/wave13/<arm>/` instead.
  The four per-sweep Quartus transcripts live there, `gzip`ped and COMMITTED.
  *An assertion by analogy is not a measurement, and the correction is left
  visible rather than silently deleted.*
* `~/.cache/ucsimt-tmp` for every intermediate; nothing large in `/tmp`.
* **CONTENT COMPARED, NOT A SELF-COMPUTED DIGEST**: the ladder is diffed leg by
  leg on scored quantities queried by name, `chain_lfsr` row for row, and
  `fz2_replay` field by field — with the repo's own registered sha256 tool run
  beside the field comparator and agreeing.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  `sw/wave13_score.py`
  reproduces WAVE 12's committed `wave12-nostamp-control-n5` distribution
  exactly (40.62 at seed 3, draws 40.62 · 40.81 · 43.29 · 44.07 · 44.30, spread
  3.68, ALMs 8,105–8,144) before it was pointed at anything new;
  `sw/wave13_replay_fieldcmp.py` carries `--selftest` and fires it in the same
  run as every verdict it gives; `phase_split_ladder_diff.py` was shown able to
  say MOVED (on WAVE 12's `test_quartus_gate` 255 → 287) before it was asked to
  say SAME.
* No Codex.  No nested subagent.
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
