# WAVE 16 — **ARM-A IS LANDED, IT IS BEHAVIOURALLY EXACT ON *THIS* TREE, IT COSTS NOTHING WITH THE EXCEPTION — AND WITHOUT THE SPLIT ITS SIGN IS REVERSED.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/qripe_landing_prereg_2026-09-18.md` at
**`24e1060467`**, committed **before the first `hdl/` edit**
(`git status --porcelain hdl/` tracked was 0 at that commit).
The landing is **`f174e1a24a`**.

**OFFLINE ONLY — NO BOARD, NO FLASH, NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.

| | |
|---|---|
| **Base of the A/B** | `24e1060467` (the prereg commit = today's tree, unedited) |
| **The arm** | `f174e1a24a` = ARM-A `qripe_presel` |
| **Verilator binaries** | base **`a8be6a1a62171ff7…`**, ARM-A **`88691d894591a611…`** (output bytes `c3073dfad5bc1250…`, declared-inputs hash `895ae94e2e82f17d`) |
| **The rebased patch** | `sw/testdata/wave16/arm_presel_unsplit.diff` |
| **Ladders** | `sw/testdata/wave16/ladder_{before,after}/`, comparison `r1_ladder_cmp.txt` |
| **Distributions** | `sw/testdata/g6dist/w16-{presel-withexc,base-noexc,presel-noexc}-{control,retention}-n5/` |
| **Tool** | Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns; Verilator 5.032 |
| **Cost** | 6 sweeps · 30 fits · 6 maps · ~4 h of Quartus, plus two full equivalence ladders and three RTL perturbations |

---

## §0 THE HEADLINE, IN SIX SENTENCES

> **1. THE MECHANISM IS SPLIT-INDEPENDENT, AND THE PATCH PROVED IT BEFORE ANY
> MEASUREMENT DID.**  WAVE 15's `arm_presel.diff` applies to today's unsplit
> tree with **ONE CONTEXT-LINE RENAME and not one added line changed** — the
> split spells two EU wires `s1w_retire_ok_n` / `s1w_bnd_fire`, this tree spells
> them `retire_ok_n` / `bnd_fire`.
>
> **2. R-1 IS MET IN FULL ON THIS TREE.**  **36 of 37 ladder legs IDENTICAL by
> their scored lines**, including 169,000/169,000 at `--ce-div` 2/3/4/8 with div
> 1 refused, **the exact 181** (`FA` 500/500 · `FB` 500/500 · `INT.FB` 200/200),
> `ulockstep` **17,350 ALL LOCKSTEP**, the four `chain_lfsr` signatures
> **BYTE-IDENTICAL**, and **`fz2_replay` 305 rows × 11 fields IDENTICAL compared
> BY NAME** over a **non-zero** population.  The one moving line is not a flop —
> §2.2.
>
> **3. R-2 IS MET: WITH THE EXCEPTION, THE LANDING COSTS NOTHING.**
> `worst-of-5` **CONTROL 40.62 → 41.42 (+0.80 MHz)** and **RETENTION 41.63 →
> 41.55 (−0.08 MHz)**, **10 of 10 draws PASS E1-E5**, and the paired 95 % CI
> **contains zero on both configurations, on both T_min and Fmax**.
>
> **4. ⚠⚠ R-3 IS THE WAVE'S REAL FINDING AND IT IS NEGATIVE: WITHOUT THE SPLIT,
> ARM-A'S SIGN IS REVERSED ON CONTROL.**  The no-exception paired mean is
> **−1.256 ns [−1.656, −0.855], t = −8.71** where the split tree measured
> **+2.847 ns [+2.377, +3.316], t = +16.8** — *opposite signs, both
> significant.*  `worst-of-5` **27.78 → 26.75 (−1.03 MHz)**.  RETENTION is
> **+0.508 ns [−1.093, +2.110], t = +0.88** — indistinguishable from zero —
> against the split tree's +1.429.
>
> **5. SO THE TWO-LANDING PLAN IS NOT A CONVENIENCE, IT IS A REQUIREMENT, AND
> NOW IT HAS A NUMBER.**  ARM-A buys the campaign nothing until the cut moves
> the binding class onto the arc it shortens.  **The goal state is not reached
> and was registered in advance as unreachable by this wave.**
>
> **6. LAW 5 IS NOW SIX FOR SIX AND FOR THE FIRST TIME WITH THE SIGN FLIPPED.**
> *"A candidate's value is not a property of the candidate"* previously meant
> 0.527 ns vs 6.629 ns — same sign, different size.  It now means **+2.847 vs
> −1.256.**  A mechanism measured on one tree may be a COST on another.

---

## §1 R-1 — **EQUIVALENCE ON THIS TREE.  MET.**  IT CAME FIRST AND NO NANOSECOND WAS QUOTED BEFORE IT.

The BEFORE ladder ran on the **unedited** tree (`24e1060467`), the AFTER ladder
on ARM-A, through **one script** (`sw/wave16_ladder.sh`) with identical
arguments.  Compared by **`sw/wave16_ladder_cmp.py`**, which declares per leg
which lines ARE its scored content and compares only those.

⚠ **THE COMPARATOR CARRIES ITS OWN POSITIVE CONTROL AND IT PASSES.**
`--selftest` perturbs one character of `cc_all`'s scored line and the
comparison must notice; it does (`differing legs: ['ss_lint', 'cc_all']`).
**Comparing raw log TEXT reports every leg as differing** — trap #10 — so the
raw logs are retained and the SCORED LINES are what is compared.

### 1.1 THE LADDER, LEG BY LEG

| leg | base (unedited) | **ARM-A** |
|---|---|---|
| `check_core --opcodes all --cases 0` | **169,000/169,000** | **IDENTICAL** |
| …`--ce-div 2 / 3 / 8` | 169,000 each | **IDENTICAL** |
| …`--ce-div 1` | **REFUSED**, clause cited, rc 2 | **IDENTICAL** |
| **the exact 181 — `FA` / `FB` / `INT.FB`** | **500/500 · 500/500 · 200/200** | **IDENTICAL** |
| `8F.0` | 500/500 | IDENTICAL |
| the four HLT sweeps, `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = **279/283** | IDENTICAL |
| `v0.1-w1` / `-w3` / `EB` | 1,200 · 1,200 · 200 | IDENTICAL |
| the four `evt` cells + biased | 200 · 1,200 · 200 · 1,200 · 1,200 | IDENTICAL |
| `ulockstep --golden all --cases 50` | **17,350/17,350 ALL LOCKSTEP** | IDENTICAL |
| `ghost_launch_law score` | 200/200 = 100.0 % | IDENTICAL |
| `check_boot` / `check_boot 400` | 220 · 400 MATCH | IDENTICAL |
| `check_ab_sim` | 187 MATCH | IDENTICAL |
| `sm3_s16_score --core ucore` | **1,320/1,371**, census `{busstat_other 24, ARCH 27}` | IDENTICAL |
| `r7_lint` | **PASS** 0/0/0 | **PASS**, with two DECLARED entries (§1.3) |
| `demux_off_gate` | PASS | PASS |
| `test_artifact` | **45/45** | 45/45 |
| `test_quartus_gate` | **287/287** ⚠ | 287/287 |
| `chainflat_relocation_check` | PASS, 9 arms | PASS, 9 arms |
| `ucrom_mif_check` | PASS, word for word | PASS |
| `chain_lfsr_gate` | PASS, CHAIN_MAX 7, depth [6], 0 overflows | **all 14 scored lines IDENTICAL** |
| `ss_lint --core ucore` | PASS 232 / 228 flops / 0 UNMAPPED / 3 whitelist | **verdict and census IDENTICAL**; one diagnostic moved (§2.2) |
| `phase_split_lint` | **exit 2, COULD NOT RUN** | IDENTICAL |
| `cutset_lint` | **exit 2, COULD NOT RUN** | IDENTICAL |
| `fz2_replay`, 305 seeds | AGREEMENT **301/305**, `first_bad` identical **101/101** | **305 × 11 IDENTICAL** |

The four `chain_lfsr` signatures, identical on both trees:
`1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78`,
**and every gap count and liveness row with them.**

**Every `rc` is identical leg for leg**, the three non-zero ones included:
`hlt_w1`/`hlt_w2`/`hlt_w3` rc 1 (the four standing family-D cells), `s16` rc 1
(the standing 51-cell residue), `cc_div1_refused` rc 2 (the contract refusal),
`phase_split_lint`/`cutset_lint` rc 2.

### 1.2 `fz2_replay` IS NON-VACUOUS, AND THAT WAS CHECKED FIRST

WAVE 15 caught this tool **running GREEN over ZERO rows** in a scratch worktree
(`.gitignore:9` hides `sw/testdata/campaigns/*/captures/`).  Both legs here ran
**in the main tree**, and the comparator prints the ROW COUNT before the
verdict: **305 and 305.**  `tb_sys_receipt` **DIFFERS** between the legs
(`2499c1b322b0c400…` vs `8e616b9f24ed28a2…`), which is the control that the two
legs ran **different binaries** — a run in which it matched would be the
vacuity.  Compared **field by field by name**, never by a digest computed here.

### 1.3 THE DECLARED COST: `sw/r7_lint.py` GAINS TWO ENTRIES, ARGUMENT UNCHANGED

C1 splits `q_ripe_lead_n`, a **DECLARED UNRESOLVED** carrier since §73, into two
nets.  Without the list edit `r7_lint` **FAILS with two undeclared unresolved
carriers, correctly** — WAVE 15's own `q2_report.txt` recorded exactly that.
The edit is inside the arm's own diff, the argument is the same character for
character (both nets are driven from the queue's procedural next-state and
neither is the READY sample), and **the superseded entry is kept above the two
new ones so a reader can see the list did not grow by forgetting anything.**

---

## §2 THREE DISAGREEMENTS WITH THE STANDING TABLES, ALL REGISTERED BEFORE THEY WERE SCORED

All three were measured from the tree and written into the pre-registration
**before** the first `hdl/` edit, so none can be mistaken for a failure.

### 2.1 `ss_lint` AND `test_quartus_gate` — THE BRIEF'S FIGURES ARE THE SPLIT TREE'S

| quantity | `standing_gates.md` | briefed | **THIS TREE, MEASURED** |
|---|---|---|---|
| `SS_COUNT` | 226 | 232 | **232** |
| architectural flops | 214 | 229 | **228** |
| whitelist entries | — | 4 | **3** |
| `SS_VERSION` / `SS_TAG` | 0x8D | 0x8F | **0x8F / 0x8FE8** |
| `test_quartus_gate` | — | 286 | **287 / 287** |

**229 flops / 4 whitelist entries is the SPLIT tree's reading** — the split adds
`s1q` as a fourth whitelisted DERIVED-state name.  **228 / 3 is the unsplit
tree's, and it is what R-4 is scored against.**  `standing_gates.md`'s row is
stale and **a stale row is never treated as a failure.**

### 2.2 THE ONE MOVING LADDER LINE IS NAMED, NOT ABSORBED — AND IT IS NOT A FLOP

```
base: BIU (v30u_biu.sv): 91 architectural flops -> 91 SSA-mapped, 0 whitelisted,
      0 UNMAPPED; 0 sim-only exempt (203 comb/next-state regs skipped)
arm : BIU (v30u_biu.sv): 91 architectural flops -> 91 SSA-mapped, 0 whitelisted,
      0 UNMAPPED; 0 sim-only exempt (205 comb/next-state regs skipped)
```

**203 → 205** is the census counting the mechanism's **two declared
combinational temporaries**, `pop_eff` and `q_cnt_np`, both named in the
pre-registration §1.1 before the edit existed.  **ARCHITECTURAL FLOPS ARE
UNMOVED** — 91 → 91 SSA-mapped, 0 UNMAPPED, census 228 / 3 whitelist,
`SS_COUNT` 232, `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8 — and §4 confirms it against
the compiler's own per-entity count on **all 20 draws of both configurations**.
**R-7 does not fire on a count of registers the flop census SKIPS**, and the
distinction is stated here rather than left for a reader to infer.

### 2.3 `cutset_lint` ON THE UNSPLIT TREE — **IT REFUSES, WHICH IS THE INSTRUMENT WORKING**

> `=== cutset_lint: COULD NOT RUN (the split is absent)` — **exit 2**, and its
> own source says *"This lint has nothing to check and says so rather than
> passing: exit 2, COULD NOT RUN, never exit 0."*  `phase_split_lint` does the
> same.

Measured **identically on both sides**, base and ARM-A.  Consequence, stated
plainly: **WAVE 15's X4 firing on ARM-A CANNOT BE REPRODUCED ON THIS TREE, AND
ITS ABSENCE IS NOT A REPAIR.**  C1 does not create a bypass — it **relocates**
one that was always there through the BIU port — and the lint able to see it is
precisely the one this tree does not have.  **When the split lands, X4 will fire
on this landed RTL, and that is expected, not a regression.**

---

## §3 R-2 — **NO TIMING REGRESSION WITH THE EXCEPTION.  MET.**

`sw/run_wave16_g6.sh` (WAVE 15's driver, the scratch-worktree refusal relaxed to
"the main tree OR a `wave16` scratch worktree" because this is a landing),
`quartus_gate.py --seeds 5`, seed set **{1,2,3,4,5}**, both configurations,
one shared `quartus_map` per sweep, `pgrep -x` by exact binary name one pattern
per call, `hdl/nec_test_ucore.qsf` restored by that exact path around every run.

| sweep | receipt | verdict | manifest | worst-of-5 | vs WAVE 12 |
|---|---|---|---|---:|---:|
| `w16-presel-withexc-control-n5` | `92f840c9edf797ae…` | **PASS** | `e7677ff860dc526b…` (98) | **41.42** | 40.62 → **+0.80** |
| `w16-presel-withexc-retention-n5` | `f65fb69543f6dec0…` | **PASS** | `e7677ff860dc526b…` | **41.55** | 41.63 → **−0.08** |

Draws: CONTROL **41.42 · 41.71 · 42.26 · 43.79 · 44.57** (spread 3.15);
RETENTION **41.55 · 42.66 · 43.11 · 43.12 · 44.75** (spread 3.20).
Worst setup **+7.106 … +8.530** and **+7.180 … +8.773** — positive on every
draw.  **10 of 10 per-seed receipts `PASS` with 5 bars each and ZERO failing
bars**, `off_class` **EMPTY on all 10**, manifest **IDENTICAL between the two
configurations** (the check that the RTL edit reached the compiler and the
configurations differ by the `--verilog_macro` alone), `configuration`
**DERIVED from the reports** on both and the retention sweep **self-labelling
`RETENTION (X1_AD_RETENTION=1)`** (E-6).

### 3.1 THE PAIRED READING, AND IT CONTAINS ZERO BOTH WAYS

| | paired mean T_min | 95 % CI | t | paired mean Fmax | 95 % CI |
|---|---:|---|---:|---:|---|
| CONTROL | **−0.455 ns** | [−1.372, +0.462] | −1.38 | +0.132 MHz | [−3.760, +4.024] |
| RETENTION | **−0.538 ns** | [−1.535, +0.459] | −1.50 | −0.206 MHz | [−2.307, +1.895] |

**Every one of the four intervals contains zero.**  §4 item 2 of the
pre-registration predicted **Δ ≈ 0** and that is **RIGHT**: with the exception
in place the binding cone is the microcode front end (WAVE 7), not this round
trip, so there is nothing here for the mechanism to shorten or lengthen.

### 3.2 ⚠ AND THE BAR AS I WROTE IT HAS A DEFECT, WHICH I RECORD RATHER THAN RESOLVE IN MY OWN FAVOUR

R-2 says *"A regression fails R-2"* **and names no resolution.**  RETENTION's
`worst-of-5` moved **−0.08 MHz**, which is **2.5 % of that sweep's own 3.20 MHz
spread** and **0.04 ns of T_min**, with the paired interval containing zero on
both quantities.  **A bar written without a resolution cannot distinguish a
regression from a draw**, and that is a defect in the registration, not a
licence.  **R-2 is scored MET** on the two clauses that ARE resolvable — *every
draw PASS E1-E5*, met 10 of 10, and *no measurable movement*, met with four
zero-containing intervals — **and the −0.08 MHz is quoted as the measured
figure, not rounded away.**
⚠ **A cross-wave caveat**: WAVE 12's pair was drawn by its own driver, not
`run_wave16_g6.sh`.  The gate, the flags and the seed set are the same; the
driver is not.  Stated because law 4 of this campaign is about exactly such an
unlabelled variable.

### 3.3 AREA, MEASURED AND CAVEATED

`v30_core` combinational ALUTs: with the exception, BIU **1,102 → 1,128
(+26)** / EU **5,505 → 5,519 (+14)** on CONTROL, but BIU **1,138 → 1,122
(−16)** / EU **5,576 → 5,479 (−97)** on RETENTION; whole-design ALMs
8,105-8,144 → 8,107-8,144 (CONTROL) and 8,161-8,200 → 8,270-8,296 (RETENTION).
⚠ **§4 item 5 (*"the design does not shrink"*) is therefore NOT CONFIRMED AND
NOT REFUTED**: the measurement changes sign between configurations, and
`ucore_provenance.md` §74.4a says A&S combinational counts are **not
reproducible run to run.**  **Reported, not concluded.**

---

## §4 R-4 — **REGISTER ACCOUNTING.  NOT ONE FLOP, ON ALL 20 DRAWS OF THE TWO SAME-SDC A/Bs.  MET.**

The authority is the compiler's own per-entity count, and it is read **only
between same-SDC pairs** (§4.1).

| A/B | `v30u_biu` | `v30u_eu` | whole-design `map_registers` |
|---|---:|---:|---:|
| **WITH exception**, base (WAVE 12) → ARM-A | **438 → 438** | **731 → 731** | ctl 5094 → 5094 · ret 5116 → **5117 (+1)** |
| **NO exception**, base → ARM-A | **434 → 434** | **728 → 728** | ctl 5086 → 5087 (+1) · ret 5108 → 5107 (−1) |

* **ARM-A adds no flop and the compiler says so on every one of the 20 draws.**
* `ss_lint` exits 0; `SS_COUNT` **232**, `SS_VERSION` **0x8F**, `SS_TAG`
  **0x8FE8**, census **228 flops / 0 UNMAPPED / 3 whitelist entries** — all
  unmoved, both sides (§2.2 for the one diagnostic that moved).
* ⚠ **The whole-design `map_registers` wobbles by ±1 OUTSIDE `v30_core`** —
  +1, +1, −1 across the three pairs.  **The same unexplained class** as WAVE 14
  §3.4, WAVE 15 §6 and WAVE 7's `sys_top` 424 → 422.  **Recorded, not
  explained.**
* `fit_registers` **VARIES across the seeds of every sweep** (physical synthesis
  duplicates registers) and is **not read as evidence**.

### 4.1 ⚠ A FINDING NOBODY REGISTERED: **THE PER-ENTITY REGISTER COUNTS ARE SDC-DEPENDENT**

The **same RTL** reads `v30u_biu` **438** / `v30u_eu` **731** with the CE
multicycle and **434 / 728** without it — measured on two pairs that differ in
`hdl/nec_test.sdc` and in nothing else (`git diff d3aa3900c5 HEAD -- hdl/`
touches that file alone).  These are **fit-report hierarchy counts**, so the
fitter's response to the constraint moves them.  **Consequence: a register count
may only be compared across builds that share an SDC**, and R-4 above is scored
that way.  The brief's *"`v30u_eu` 1,326 registers at WAVE 15"* is the **split
tree's** figure and is not comparable to either column here.

---

## §5 R-3 — **ARM-A's STANDALONE BENEFIT WITHOUT THE SPLIT.  RED AS REGISTERED — AND ON CONTROL THE SIGN IS REVERSED.**

Not a pass/fail bar.  The no-exception tree is today's `hdl/` with WAVE 9
edit (c) (`bacf7f9fd9`) applied to `hdl/nec_test.sdc` **and nothing else**, in
two scratch worktrees under `~/.cache/ucsimt-tmp/wave16/`; **it is never
landed**, and the main tree's SDC is untouched by this wave.
Both worktrees carry **0 uncommented `set_multicycle_path` / `set_false_path`**,
their `hdl/nec_test.sdc` is **byte-identical to `d3aa3900c5`'s**
(`f0e1228ddd8f8a72…`), and `diff -rq` over their whole `hdl/` trees differs in
**exactly the three mechanism files and nothing else.**

| sweep | receipt | verdict | manifest | worst-of-5 |
|---|---|---|---|---:|
| `w16-base-noexc-control-n5` | `e3b02e2499a0cbc5…` | RED | `2e3fffa743ab2b22…` | **27.78** |
| `w16-base-noexc-retention-n5` | `1d594802a1573bea…` | RED | `2e3fffa743ab2b22…` | **27.01** |
| `w16-presel-noexc-control-n5` | `7fe41b895534d3e3…` | RED | `d8b2b1a152ff8392…` | **26.75** |
| `w16-presel-noexc-retention-n5` | `d475eb0429d31850…` | RED | `d8b2b1a152ff8392…` | **27.33** |

`E11` **pass** on all 4 distributions and all 20 per-seed receipts;
`off_class` **EMPTY on all 20** (the no-exception configuration reached the
compiler every time, in WAVE 13's polarity); manifests identical within each
arm.  **All four RED, exactly as registered.**

### 5.1 ⚠⚠ THE FREE CONTROL IS EXACT: THE BASE ARM REPRODUCES WAVE 13 ON 10 OF 10 DRAWS

| | CONTROL draws | RETENTION draws |
|---|---|---|
| WAVE 13 `w13-unsplit-noexc` | 27.78 · 28.52 · 28.52 · 28.84 · 29.06 | 27.01 · 27.58 · 27.81 · 28.17 · 28.58 |
| **WAVE 16 `w16-base-noexc`** | **27.78 · 28.52 · 28.52 · 28.84 · 29.06** | **27.01 · 27.58 · 27.81 · 28.17 · 28.58** |

**Identical to the thousandth on Fmax, T_min, worst setup, ALMs, `map_reg`,
`biu_reg`, `eu_reg`, `biu_alut` and `eu_alut` — and the `input_manifest` is the
same 98-file hash `2e3fffa743ab2b22…`.**  Different day, different worktree,
different wave.  **This is the control that makes the arm column readable, and
nobody registered it.**

### 5.2 THE PAIRED DIFFERENCE, AND THE COMPARISON THE WAVE EXISTS TO MAKE

Δ = base T_min − arm T_min; **positive means the arm's arc is SHORTER**.
95 % CI from a **tabulated** t (df = 4, t = 2.776).

| | per-seed Δ ns (1..5) | **paired mean** | 95 % CI | t | worst-of-5 | ΔMHz |
|---|---|---:|---|---:|---:|---:|
| **CONTROL** | −1.395 · −1.041 · −0.945 · −1.149 · −1.748 | **−1.256** | **[−1.656, −0.855]** | **−8.71** | 27.78 → **26.75** | **−1.03** |
| **RETENTION** | −0.551 · +1.096 · +2.040 · +1.046 · −1.090 | **+0.508** | [−1.093, +2.110] | +0.88 | 27.01 → **27.33** | **+0.32** |

> ### **ON THE SPLIT TREE THIS MECHANISM WAS WORTH +2.847 ns (CONTROL) AND +1.429 (RETENTION).  ON THIS TREE IT IS −1.256 AND +0.508.  THE CONTROL SIGN IS REVERSED AND BOTH READINGS ARE SIGNIFICANT — t = +16.8 THERE, t = −8.71 HERE.**

**Every seed of the CONTROL leg is negative**, the spread is 0.32 ns, and the
whole interval sits below zero.  **This is not noise and it is not the
instrument**: the base arm reproduces WAVE 13 exactly in the same six sweeps,
and the scorer's own positive control (`wave14_ceiling.py --selftest`) **PASSES**
against WAVE 13's committed bytes.

### 5.3 WHY — SAID AS A READING, NOT AS A MEASUREMENT

WAVE 15 §1.3 measured that on the **split** tree the binding `ce → ce` path's
data section carried `bnd_fire → q_pop → q_cnt → q_ripe_lead_n` on **200 of 200
paths of both configurations**: the cut had moved the binding class **onto** this
arc, having shortened everything else it could reach.  On the **unsplit** tree
the binding structure is the whole 2-period `ce → ce` cone, and WAVE 10 already
found this round trip there to be *"a placement lottery"*.  Relocating the
select therefore **adds one AND and one MUX to a cone that is already binding
and removes nothing from it.**
⚠ **This paragraph is a READING of two measurements, not a third measurement.**
No STA anatomy was run on the unsplit arms; **`sta_biu_roundtrip.tcl`'s
`q_ripe_lead_n` counter is confounded by this very mechanism** (WAVE 15 §3.2 —
its matcher is a substring test and now matches the EU's own mux), and choosing
a replacement marker after seeing this result is exactly how a result gets
chosen.  **Booked, not taken.**

### 5.4 §4's EXPECTATIONS, SCORED

| expectation | outcome |
|---|---|
| item 1 — *R-1 passes identically* | **RIGHT.** 36 of 37 legs, and the 37th is not a flop. |
| item 2 — *R-2 does not regress, Δ ≈ 0* | **RIGHT.** All four paired intervals contain zero. |
| item 3 — *R-3 is RED on both configurations* | **RIGHT.** All four sweeps RED. |
| item 4 — *R-3's Δ will not equal +2.847 / +1.429* | **RIGHT, and more so than intended** — the CONTROL sign reversed.  Law 5 is six for six. |
| item 5 — *the design does not shrink* | ⚠ **NOT SCOREABLE.** The sign changes between configurations and A&S combinational counts are not reproducible run to run (§3.3). |

---

## §6 R-5 — **THE REFERENCE PREDICATE IS PRESERVED AND NON-VACUOUS.  MET, AND THE THIRD PERTURBATION'S NON-FIRING IS WAVE 15's OWN, REPRODUCED.**

The original expression is kept **verbatim** as an `ifndef SYNTHESIS` reference
and `$fatal`-checked at **every `ce`** in two clauses (the `V30_MUXED_AD`
precedent).  `sw/wave16_nonvacuity.py` applies WAVE 15's three perturbations
character for character, rebuilds, runs `FA`, and restores `v30u_biu.sv` from a
byte copy.

| perturbation | clause | result |
|---|---|---|
| `q_ripe_lead_n1`'s `grn_ttl == 2'd1` → `== 2'd2` | (1) | **FIRES**, `FA` at **4,685,000**: *"composed=0 reference=1 (pop_eff=1 q_cnt=2 q_cnt_np=3 grn_n=2 grn_ttl=1)"* |
| `pop_eff` armed from `q_pop` alone | (2) | **FIRES**, `FA` at **85,000**: *"pop_eff=1 but q_pop=1 q_ripe=0 q_flush=0"* |
| the flush's `pop_eff = 1'b0` deleted | either | ⚠ **DOES NOT FIRE — `FA` 500/500 without it.** |

⚠ **THE FIRST TWO FIRE AT THE IDENTICAL SIMULATION TIMES AND WITH THE IDENTICAL
MESSAGE BODIES WAVE 15 RECORDED ON THE SPLIT TREE** (§2.1: 4,685,000 and
85,000).  A free control nobody registered, and it says the falsifier's reach is
a property of the mechanism rather than of the tree it sits in.
⚠ **AND THE THIRD NON-FIRING REPRODUCES TOO**: the pop/flush coincidence is
**not reached by the golden population** — now measured on a second, structurally
different tree.  **The term is kept because the flush provably overwrites the
count**, and this is reported as measured, not restated.

`v30u_biu.sv` restored and verified **sha256-identical** to the pristine copy
(`8e54248ef1bd5567…`); the rebuilt clean binary is **byte-identical** to the
ladder's ARM-A binary (same `build_key`, same declared-inputs hash
`895ae94e2e82f17d`, same output sha256 `c3073dfad5bc1250…`) — so the R-1 column
and the tree that was committed are the same bytes.

---

## §7 R-6 — **`E11` TRUE ON EVERY DRAW.  MET.**

`E11_no_build_stamp` reads **`pass` on all SIX distribution receipts and all
THIRTY per-seed receipts**, `files_scanned` 98, `file_present` False,
`token_hits` empty.

⚠ **AND THE REGISTERED TRAP FIRED AND WAS OBEYED.**  Scored from the main tree,
the worktree sweeps' per-seed column read **`*** FAIL on [1,2,3,4,5] ***`** with
every numeric column `None` — because **the per-seed receipt paths inside a
distribution are RELATIVE** (WAVE 15 §4, booked as owed item 5).  Re-scored with
the CWD in each arm's own worktree, every column is present and **E11 reads
`ok` on all 20**.  **No figure was quoted from the broken invocation.**

---

## §8 R-7 — **THE REVERT CONDITION.  NOT FIRED.**

* **No leg of R-1 moved.**  The single moving line is a count of registers the
  flop census SKIPS, it is +2, and the two are the mechanism's own declared
  combinational temporaries (§2.2).
* **R-2 did not regress** on the two resolvable clauses, and the one
  unresolvable one is recorded as a defect in the bar (§3.2).
* **R-3 is RED, and R-7 says that is not a revert condition.**

**THE LANDING STANDS AT `f174e1a24a`.  No bar was softened to make it possible.**

⚠ **AND THE HONEST CONSEQUENCE, STATED BECAUSE IT IS THE WAVE'S MOST IMPORTANT
OUTPUT:** ARM-A in the tree **alone** is worth **nothing** to the campaign's
requirement and **costs 1.03 MHz** of the no-exception CONTROL build.  It is
harmless where the tree actually stands today — the with-exception build is
unmoved and PASSES 10 of 10 — and it is a **prerequisite for measuring the
split's landing**, which is why the handoff ordered it first.  **Whether it
should sit in the tree while the split does not is a decision for the
coordinator, and it is not one this wave may take on its own behalf.**

---

## §9 THE BARS, SCORED

| bar | verdict |
|---|---|
| **R-1** equivalence on this tree, BEFORE side first, every leg IDENTICAL | **MET.**  36 of 37 legs identical by their scored lines; the 37th is `ss_lint`'s "comb/next-state regs skipped" 203 → 205, which is not a flop and was named in advance.  The comparator's own positive control PASSES. |
| **R-2** no timing regression WITH the exception, every draw PASS E1-E5 | **MET.**  10 of 10 PASS, 0 failing bars, `off_class` empty, manifests identical within the arm.  `worst-of-5` **41.42 (+0.80)** / **41.55 (−0.08)**; all four paired 95 % CIs contain zero.  ⚠ The bar's own missing resolution is recorded (§3.2). |
| **R-3** ARM-A's standalone no-exception benefit, for the record | **MEASURED, AND NEGATIVE ON CONTROL.**  All four sweeps RED as registered.  **CONTROL −1.256 ns [−1.656, −0.855], t = −8.71, worst-of-5 27.78 → 26.75**; RETENTION **+0.508 ns [−1.093, +2.110], t = +0.88, 27.01 → 27.33**.  Against **+2.847 / +1.429** on the split tree — **the CONTROL sign is reversed.**  Free control: the base arm reproduces WAVE 13 on **10 of 10** draws exactly. |
| **R-4** `ss_lint` 0, NO FLOP, SS constants unchanged | **MET.**  `v30u_biu` 438 → 438 and `v30u_eu` 731 → 731 with the exception; 434 → 434 and 728 → 728 without it; 20 draws.  `SS_COUNT` 232 / 0x8F / 0x8FE8 / 228 flops / 0 UNMAPPED unmoved.  ⚠ ±1 whole-design wobble outside `v30_core`, recorded not explained.  ⚠ NEW FINDING: the per-entity counts are **SDC-dependent** (§4.1). |
| **R-5** the reference predicate preserved and non-vacuous | **MET.**  2 of 3 perturbations FIRE, at the **identical** times and with the **identical** message bodies WAVE 15 recorded; the third's non-firing reproduces WAVE 15's own recorded non-firing.  File restored sha256-identical. |
| **R-6** `E11` true on every draw | **MET.**  6 distributions + 30 per-seed receipts.  ⚠ The relative-path trap fired and was obeyed; nothing was quoted from the broken invocation. |
| **R-7** the revert condition | **NOT FIRED.**  The landing stands.  No bar softened. |
| §2 — what `cutset_lint` does on the unsplit tree | **exit 2, COULD NOT RUN (the split is absent)**, identically on both sides.  WAVE 15's X4 cannot be reproduced here and **its absence is not a repair.** |

---

## §10 WHAT IS OWED

1. ⚠⚠ **THE FABRIC CONFIRMATION, AND IT IS NOW THREE STRUCTURAL CHANGES DEEP.**
   WAVE 7's chain flattening, WAVE 12's `build_id.v` removal, and **now this
   landing, which changes the BIU's queue port and the EU's decode.**
   **NO FABRIC FIGURE TAKEN ON FLASH #21 OR EARLIER MAY BE QUOTED AGAINST THIS
   TREE.**  Nothing was flashed here.  **This is the largest debt in the
   campaign and it grew.**
2. **THE SPLIT IS THE OTHER HALF AND R-3 IS THE ARGUMENT FOR TAKING IT.**  Land
   edits (a) `6e822bf750`, (b) `5cf3254104`, (c) `bacf7f9fd9` together — (c) is
   what deletes the exception and is the point — and re-run the no-exception
   sweeps as the requirement's own gate.  **Expect ARM-A's sign to flip back**;
   if it does not, the split's own like-for-like figure is what must be
   re-examined, not this wave's.
3. **ARM-B REMAINS OPEN AND IS WORTH ~0.8-1.0 MHz MORE** (34.48 / 34.41 against
   33.00 / 33.20 on the split tree).  It is **ARM-A plus** the select off the
   `s1q` shadow, costs **one declared flop**, and **passes `cutset_lint`**.
   Swapping to it after the split lands is a one-hunk change on top of what is
   now in the tree.
4. ⚠ **WHEN THE SPLIT LANDS, `cutset_lint` WILL FIRE X4 ON THIS RTL** and that
   is WAVE 15 §2.4's finding arriving, not a regression introduced by the split.
   Written down now so it cannot be mistaken later.
5. ⚠ **`sta_biu_roundtrip.tcl`'s `q_ripe_lead_n` COUNTER IS NOW CONFOUNDED IN
   THE TREE, NOT JUST IN AN ARM.**  Its matcher is a substring test and the EU's
   own mux is named `q_ripe_lead_n~N`.  Any future wave quoting it must use the
   BIU-node column.  **A membership-scoped replacement is one clause away and is
   NOT taken here**, because choosing a marker after seeing a refusal is how a
   result gets chosen.
6. **`standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS WAVE** (the
   WAVE 11-15 precedent; the coordinator decides).  Now unregistered: bar
   **E11**; `test_quartus_gate` **287/287**; the stale `ss_lint` row against
   this tree's **232 / 228 / 3 / 0x8F / 0x8FE8**; and **this landing itself**.
7. ⚠ **`fz2_replay` IS STILL VACUOUS IN A GIT WORKTREE AND STILL EXITS 0.**
   This wave avoided it by running the leg in the main tree.  **The permanent
   fix belongs in `fz2_replay.py` — refuse a zero-row population — and is
   BOOKED for the second time.**
8. ⚠ **`wave14_ceiling.py` MUST BE RUN WITH ITS CWD IN THE SWEEP'S OWN TREE.**
   Booked by WAVE 15, fired again here (§7).  One line would make it resolve
   receipt paths against the distribution's own directory.  **Not taken.**
9. **`check_core --ss-sweep` IS STILL ON NO REGISTERED LADDER** — booked by
   WAVES 2, 3, 4, 9, 13, 14, 15.  **Booked for the eighth time.**
10. **WAVE 11's one-fit repair** and the **±1 register wobble** are inherited and
    untouched.
11. **THE TWO R-3 WORKTREES ARE RETAINED WITH THEIR NETLISTS**, deliberately:
    `~/.cache/ucsimt-tmp/wave16/wt_{base,presel}_noexc`, detached at
    `24e1060467` and `f174e1a24a` with WAVE 9 edit (c) applied to
    `hdl/nec_test.sdc` and nothing else, each holding the build tree its last
    fit left behind.  **§5.3's reading is a reading and not a measurement**, and
    these are the two netlists an STA anatomy of the unsplit arms would have to
    run on — kept so that such a wave does not have to re-fit 10 draws to get
    them.  `git worktree list` shows both; neither is on any branch.

---

## §11 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
* No Codex.  No nested subagent.
* **THE WAITS BLOCKED; THEY DID NOT POLL A TURN.**  One `until ! pgrep -x …`
  loop per wait, and R-3's four sweeps were launched by **one** wrapper
  (`sw/testdata/wave16/run_all_r3.sh`) that waited out R-2 and then ran them
  **strictly sequentially** behind the guard, so no two Quartus stages could
  race and no sweep needed a turn of its own.
* Single-writer guard by **`pgrep -x`, EXACT BINARY NAME, ONE PATTERN PER
  CALL**; ⚠ `pgrep -f <script>` self-matches and was never used.
* Drivers carry **`set -u`, NEVER `set -e`** — four of the six sweeps were
  registered to draw RED and did.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  `hdl/nec_test_ucore.qsf` was restored by `git checkout -- <that exact path>`
  around every Quartus run.  **`git add` BY EXPLICIT PATH ONLY** on every
  commit.  **The 21 pre-existing modified files that are the user's own
  uncommitted work are untouched**, verified at the end.
* `~/.cache/ucsimt-tmp/` for every intermediate; **nothing in `/tmp`.**
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL, REPORTED FIRST**: the ladder
  comparator's `--selftest`, `wave14_ceiling.py --selftest`, `fz2_replay`'s row
  count and differing `tb_sys_receipt`, the base arm's exact reproduction of
  WAVE 13, and R-5's two firings.  **Two registered traps fired and were
  obeyed** (§7, and the confounded round-trip counter in §5.3).
* **A CENSUS DOES NOT SIZE A CANDIDATE IN EITHER DIRECTION.**  No census was
  offered for R-3 and none is quoted.
* **No figure in this wave is a fabric figure, and `standing_gates.md` §A
  governs: one green build is not closure, and the same tree has drawn 19.42 and
  45.91 MHz.**
* **Record what was measured, not what was expected** — §5.4 leaves one
  expectation unscoreable and one more emphatically right than intended.


## §12 ⚠⚠ TWO HOUSEKEEPING FACTS, ONE OF THEM A MISS I MADE AND AM RECORDING

### 12.1 **I SWEPT 20 PRE-EXISTING RECEIPT ROWS THAT WERE NOT THIS WAVE'S — WAVE 7's HAZARD, IN A FILE I DID NOT EXPECT IT IN**

`sw/testdata/receipts/verilator_binary.jsonl` was **one of the 21 pre-existing
modified files** and I staged it by explicit path with the landing, because this
wave's own Verilator receipts append to it.  **The landing commit `f174e1a24a`
therefore carries 20 rows dated 2026-09-10 … 2026-09-13 that belong to WAVE 15's
era and not to this wave** (rows 21-32 of the 32 appended, dated 2026-09-19, are
mine).

**MEASURED, NOT ASSUMED:** the previously-committed 756 lines are a
**byte-exact prefix** of the 788 committed here (`cmp` over `head -756`), and
every one of the 20 swept rows is byte-identical to what stood in the working
tree.  **Nothing was lost, altered or reordered — only the attribution is
wrong**, which is exactly the shape WAVE 7 recorded when it swept the user's
in-progress rename.  **History is NOT rewritten to hide it**; the fact is
recorded here instead.  *`git add` by explicit path is necessary and not
sufficient: an append-only ledger the wave writes to may ALREADY be dirty.*

### 12.2 **THE TWO QUARTUS RECEIPT LEDGERS ARE DELIBERATELY LEFT UNCOMMITTED**

`sw/testdata/receipts/quartus_bitstream.jsonl` and
`sw/testdata/receipts/quartus_distribution.jsonl` are **also** among the 21
pre-existing modified files, and this wave's 30 per-seed and 6 distribution
receipts appended to them.  **Committing either would sweep more of the user's
rows**, so **neither is committed** and this wave's rows stay in the working
tree.  **Nothing is lost by that choice**: every receipt is committed in full,
by value, under `sw/testdata/g6dist/w16-*/` — `distribution.json` plus
`seed{1..5}_quartus_gate.json`, `seed{1..5}.sta.summary` and
`seed{1..5}.truefmax.txt` for all six sweeps — and §3 and §5 quote their `id`s
from there.

### 12.3 **THIS WAVE ADDED NO `hdl/*.log`** — checked against the directory, not recall

`ls hdl/*.log` is **15 files**; **14 are the pre-existing untracked
`quartus_gate_*.log`** with their original dates (2026-08-11 … 2026-09-12),
byte-untouched, and the 15th is `hdl/quartus_gate_build.log`, **gitignored**
(`hdl/.gitignore:44`) and dated **2026-08-20**.  Every Quartus transcript of this
wave went to `--log` under `sw/testdata/wave16/` and is committed compressed in
`sw/testdata/wave16/logs/`.

---

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
