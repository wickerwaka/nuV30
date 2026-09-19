# WAVE 19 — **ARM-B IS LANDED.  IT IS BEHAVIOURALLY EXACT, IT CLOSES `cutset_lint`, IT COSTS ONE FLOP AND NO SAVE-STATE ADDRESS, AND IT REPRODUCES WAVE 15's 34.48 / 34.41 TO THE BITSTREAM BYTE ON TEN OF TEN DRAWS.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/armb_landing_prereg_2026-09-19.md` at
**`70f2f7bc30`**, committed **before the first `hdl/` edit**
(`git status --porcelain hdl/` tracked was **0** at that commit, measured).
Its bars **V-1 … V-6 are scored below in the form they were registered in.
Not one was softened, re-derived or re-scoped after a result was seen.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.  `docs/notes/standing_gates.md` §A governs every timing figure.

| | |
|---|---|
| **Tree at entry** | `6de3955b5a` (WAVE 18's registration), tracked `hdl/` clean |
| **The landing** | **`ce39ed61bf`** |
| **The edit** | `sw/testdata/wave19/armb_delta.diff` — **86 lines, 7 hunks, ONE FILE**, sha256 `b4ea3a43ce441a62…`, derived mechanically |
| **Applier** | `sw/wave19_apply.py`, three refusal controls, all three fire |
| **Ladders** | `sw/testdata/wave19/{before,after}/`, **40 legs each**, one driver, committed UNCOMPRESSED |
| **Distributions** | `sw/testdata/g6dist/w19-armb-noexc-{control,retention}-n5/`, receipts **`3c983b10a73fb494…`** and **`a5a59e9ed3726729…`** |
| **`input_manifest`** | **`ee6a4eff46e483d3…` / 99 files, BOTH configurations — and it is WAVE 15's ARM-B manifest byte for byte** |
| **Tool** | Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns; Verilator 5.032 |
| **Cost** | 2 sweeps · 10 fits · 2 maps · 57 min of Quartus, plus two full 40-leg ladders |

---

## §0 THE HEADLINE

> ### **1. THE REQUIREMENT IS NOT ONLY HELD, IT IS WIDENED.  WITH ZERO TIMING EXCEPTIONS IN `nec_test.sdc`, `quartus_gate.py --seeds 5` RETURNS `PASS` ON ALL FIVE DRAWS OF *BOTH* CONFIGURATIONS.**
>
> **CONTROL `worst-of-5` = 34.48 MHz** (draws 34.48 · 34.68 · 34.68 · 34.91 ·
> 34.95) and **RETENTION `worst-of-5` = 34.41 MHz** (34.41 · 34.72 · 34.85 ·
> 34.99 · 35.24), against a bar of **32.0** — **margins +2.48 and +2.41**,
> against the landed tree's **+1.00 / +1.20**.  Worst setup **+2.245 … +2.638 ns**
> and **+2.185 … +2.872 ns**, positive on every draw.  **TNS 0.000 setup AND
> hold on all four clock domains of all ten draws**, 0 error lines, 0 latches,
> 0 `lpm_divide`, `core_domain` **k = 1.0 on all three classes with `off_class`
> EMPTY on all ten**, `E11` pass on both distributions and all ten per-seed
> receipts.
>
> ### **2. ⭐ V-3 IS MET: `cutset_lint` GOES `FAIL 80 / 1` → `PASS 81 / 0`.  THE X4 THAT HAS BEEN RED *BY DESIGN* IN THE TREE SINCE WAVE 17 IS CLOSED — ON ARM-B'S OWN TERMS, WITHOUT EDITING A LINT.**
>
> That is the non-timing argument the flop was supposed to buy, and it is
> delivered.  `phase_split_lint` **PASS 157 / 779 / 0**.
>
> **3. THERE IS NO SAVE-STATE STREAM BREAK, AND IT WAS PREDICTED BEFORE THE
> EDIT.**  `ss_lint` exits 0; **`SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG`
> 0x8FE8 / 229 architectural flops / 4 whitelist entries / 0 UNMAPPED — ALL
> UNCHANGED**; `v30u_ss_pkg.sv` untouched by every commit of this wave.  **The
> one flop is a 1-bit widening of `s1q`, a name already on the whitelist's
> DERIVED class**, and the compiler's own count says so: **`v30u_eu` 1,326 →
> 1,327 on all twenty draws**, `v30u_biu` 434 → 434.
>
> **4. THE TREE IS BIT-EXACT.  39 OF 40 `rc` VALUES AND 35 OF 38 SCORED LADDER
> LEGS IDENTICAL, AND ALL THREE MOVERS WERE REGISTERED BEFORE THEY WERE SEEN.**
> 169,000/169,000 at `--ce-div` 2, 3, 4 **and** 8 with div 1 refused · **the
> exact 181 — `FA` 500/500, `FB` 500/500, `INT.FB` 200/200** · `ulockstep`
> **17,350 ALL LOCKSTEP** · the four HLT sweeps **279/283** · `sm3_s16_score`
> 1,320/1,371 with its census unmoved · **the four `chain_lfsr` signatures
> BYTE-IDENTICAL** · **`fz2_replay` 302 rows × 11 fields IDENTICAL, compared BY
> NAME** over a non-zero, printed population.
>
> **5. ⭐⭐ AND THE LANDING REPRODUCES WAVE 15's ARM-B ARM TO THE BITSTREAM, ON
> TEN OF TEN DRAWS OF BOTH CONFIGURATIONS.**  `input_manifest` identical,
> 30 of 38 distribution scalars identical, **all twelve compared per-seed fields
> identical on 5 of 5 of each configuration**, and **`nec_test_ucore.rbf`
> BYTE-IDENTICAL on 10 of 10.**  Six days and three trees apart.
>
> **6. ⚠⚠ NOTHING WAS FLASHED, AND THE FABRIC DEBT IS RE-OPENED ON THE DAY IT
> WAS PAID.**  FLASH #22 was taken **2026-09-19**, on the tree this wave
> changes.  **NO FLASH #22 FIGURE MAY BE QUOTED AGAINST THIS TREE.**

---

## §1 JOB 1 — **ARM-B IS AN *ADDITION ON TOP OF* ARM-A.  ESTABLISHED THREE WAYS, BEFORE THE EDIT, AND CONFIRMED AFTERWARDS BY THE BITSTREAM.**

The ambiguity was real and is settled from artifacts, not from reading.

### 1.1 The two WAVE 15 arm diffs differ ONLY inside the EU

`diff -u` over their `hdl/` + `sw/r7_lint.py` content: the BIU's two-level
publication, `v30_core.sv`'s wires and ports, and `sw/r7_lint.py`'s two declared
carriers are **character for character the same in both arms.**

### 1.2 And the bytes said so, before anything was edited

A reference worktree `~/.cache/ucsimt-tmp/wave19/ref_armb`, detached at
`850ef46559` with `arm_s1q.diff` applied — the construction WAVE 17 §9.1 kept
`ref_arm` for — against the pre-edit tree:

| file | sha256 | |
|---|---|---|
| `hdl/rtl/ucore/v30u_biu.sv` | `8e54248ef1bd5567…` | **SAME** |
| `hdl/rtl/ucore/v30_core.sv` | `e4ecf911e8874ed9…` | **SAME** |
| `sw/r7_lint.py` | `4ec672df0afc4fb8…` | **SAME** |
| `hdl/rtl/ucore/v30u_eu.sv` | tree `c70dee375f9b9df5…` vs ARM-B `31ff3a50f503da77…` | **DIFFERS** |

⚠ **And the fourth file was verified to be ARM-A's own**: the pre-edit tree's
`v30u_eu.sv` is **sha256-identical to `~/.cache/ucsimt-tmp/wave17/ref_arm`'s**,
which is WAVE 15's ARM-A arm.  WAVE 17 §3.4's composition claim, **re-measured
here independently rather than carried.**

### 1.3 **THE ANSWER**

> **ARM-B = ARM-A + ONE EDIT TO ONE FILE.  IT IS AN ADDITION.**  Nothing ARM-A
> landed is removed, reverted or re-derived.  What changes *inside* the addition
> is **where the select happens**: ARM-A's two-line combinational
> `wire q_ripe_lead_n = (q_pop && q_ripe && !q_flush) ? n1 : n0;` becomes
> `wire s1w_qripe_pop = q_pop && q_ripe && !q_flush;` — the predicate is
> shadowed and the mux moves into stage 2.  The BIU is untouched, the published
> pair is untouched, and the two consumer sites (`v30u_eu_step.svh`,
> `v30u_eu_arm_decode2.svh`) stay **byte-unchanged**, still reading a wire spelt
> `q_ripe_lead_n`.

### 1.4 THE EDIT WAS MECHANICAL, AND *"IT APPLIED"* IS NOT THE EVIDENCE — THE HASH IS

`sw/wave19_apply.py --apply` applies the committed delta and then **REQUIRES**
`v30u_eu.sv` to hash to `31ff3a50f503da77…`.  It did.  **A patch that applies
is not a patch that applied correctly.**

**Its two refusal clauses each carry a positive control and all three FIRE
(rc 3):**

| control | result |
|---|---|
| a `v30u_eu.sv` that is neither tree (`~/.cache/ucsimt-tmp/wave16/wt_base_noexc`, the unsplit ARM-A tree) | **REFUSES**, rc 3 |
| the `s1q` whitelist entry ABSENT | **REFUSES**, rc 3 |
| the `s1q` whitelist entry DUPLICATED | **REFUSES**, rc 3 |

⚠ **AND ONE COSMETIC DEFECT WAS LANDED DELIBERATELY AND SAID SO IN ADVANCE**:
the `S1W` comment block's ragged continuation indentation is WAVE 15's, kept
exactly, because byte-identity to the artifact that drew 34.48 / 34.41 is worth
more than alignment — and §6 is what that buys.

### 1.5 THE WHOLE-TREE COMPOSITION, AFTER THE EDIT

> **126 of this tree's 127 tracked `hdl/` files are sha256-IDENTICAL to the
> ARM-B reference.**

The **one** that differs is **`hdl/rtl/core/v30_core.sv` — the ARCHIVED FSM
core**, moved by **WAVE 18's own landing `9ccc6d0177`** (`git log` names it) and
nothing to do with ARM-B.  The ucore's three files are identical.  ⚠ **And it is
not in the ucore revision's `input_manifest`**, which §6 shows is byte-identical
to WAVE 15's — measured, not assumed.

---

## §2 V-1 — **EQUIVALENCE.  MET.**  IT CAME FIRST AND NO NANOSECOND WAS QUOTED BEFORE IT.

The **BEFORE** ladder ran on the **unedited** tree at the pre-registration
commit; the **AFTER** ladder on the landing.  One driver,
**`sw/wave19_ladder.sh` = `sw/wave16_ladder.sh` with EXACTLY ONE LINE ADDED**
(`core_portlist_lint`, WAVE 18's gate, created after that ladder was written) —
demonstrated by `diff`, and **`sw/wave16_ladder.sh` itself is not edited.**

### 2.1 `_rc.txt`: 39 OF 40 IDENTICAL, AND THE 40th IS V-3's BAR

```
5c5
< cutset_lint rc=1
---
> cutset_lint rc=0
```

**That is the entire `rc` diff over 40 legs.**  The three standing non-zero
codes are unmoved: `hlt_w1`/`w2`/`w3` rc 1 (the four family-D cells), `s16` rc 1
(the standing 51-cell residue), `cc_div1_refused` rc 2 (the contract refusal).

### 2.2 THE LADDER, LEG BY LEG

| leg | BEFORE | AFTER |
|---|---|---|
| `check_core --opcodes all --cases 0` | **169,000/169,000** | **IDENTICAL** |
| …`--ce-div 2 / 3 / 8` | 169,000 each | **IDENTICAL** |
| …`--ce-div 1` | **REFUSED**, clause cited, rc 2 | **IDENTICAL** |
| **the exact 181 — `FA` / `FB` / `INT.FB`** | **500/500 · 500/500 · 200/200** | **IDENTICAL** |
| `8F.0` | 500/500 | IDENTICAL |
| the four HLT sweeps, `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = **279/283** | **IDENTICAL** |
| `v0.1-w1` / `-w3` / `EB` | 1,200 · 1,200 · 200 | IDENTICAL |
| the four `evt` cells + biased | 200 · 1,200 · 200 · 1,200 · 1,200 | IDENTICAL |
| `ulockstep --golden all --cases 50` | **17,350/17,350 ALL LOCKSTEP** | **IDENTICAL** |
| `ghost_launch_law score` | 200/200 | IDENTICAL |
| `check_boot` / `check_boot 400` | 220 · 400 MATCH | IDENTICAL |
| `check_ab_sim` | 187 MATCH | IDENTICAL |
| `sm3_s16_score --core ucore` | **1,320/1,371**, census `{busstat_other 24, ARCH 27}` | **IDENTICAL** |
| `r7_lint` | **PASS** 0/0/0 | **IDENTICAL** |
| **`core_portlist_lint`** | **PASS**, 2 configurations, ports MATCH | **IDENTICAL** |
| `demux_off_gate` | PASS, *"the two muxed ports are GONE"* | IDENTICAL |
| `test_artifact` | **45/45** | IDENTICAL |
| `test_quartus_gate` | **287/287 PASS** | **IDENTICAL** |
| `chainflat_relocation_check` | PASS, 9 arms | IDENTICAL |
| `ucrom_mif_check` | PASS | IDENTICAL |
| `chain_lfsr_gate` | PASS, 14 scored lines | **all 14 IDENTICAL** |
| `ss_lint --core ucore` | PASS, 232 / 229 / 4 | **MOVED by ONE SUB-LINE — §4, registered** |
| `phase_split_lint` | PASS **156 / 778 / 0** | **PASS 157 / 779 / 0** — registered |
| `cutset_lint` | **FAIL — 80 / 1, X4** | ⭐ **PASS — 81 / 0** — §3 |
| **`fz2_replay`** | 302 rows | **302 × 11 IDENTICAL by name** — §2.4 |

The four `chain_lfsr` signatures, identical on both trees:
`1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78`,
**and every gap count and liveness row with them.**

> ⚠ **THAT IS ALSO 1.6 M FABRIC CLOCKS OF THE *WIDENED* SHADOW'S OWN `$fatal`.**
> `v30u_eu.sv:4248` compares the WHOLE of `s1q` against `s1_bus` at every `ce`,
> so **`qripe_pop`'s constancy across the CPU cycle is asserted by construction,
> not claimed.**  ARM-B's own comment calls this *"this arm's free falsifier"*;
> the assertion was read, not taken on trust.  Across 4 × 400,000 `chain_lfsr`
> clocks, 169,000 goldens at four divisors and 17,350 `ulockstep` scenarios
> **it never fired once.**

### 2.3 THE COMPARATOR'S OWN POSITIVE CONTROL PASSES, IN THE SAME INVOCATION

`--selftest` perturbs one character of `cc_all`'s scored line and the comparison
must notice; it does (`differing legs: ['ss_lint', 'phase_split_lint',
'cutset_lint', 'cc_all']`, with `cc_all` present **only** under the selftest).
**Comparing raw log TEXT reports every leg as differing** — trap #10 — so the
raw logs are retained and the SCORED LINES are what is compared.

### 2.4 `fz2_replay` IS NON-VACUOUS, AND THAT WAS CHECKED FIRST

Trap #8: structurally vacuous in a git worktree, **GREEN over zero rows**.  Both
legs ran **in the main tree**; the comparator prints the ROW COUNT before the
verdict — **302 and 302** — and `tb_sys_receipt` (`fbb3e15ea1fb5f9f…` →
`215e4a2d8ccc4c93…`) and `tb_sys_tree` **DIFFER**, which is the control that
the two legs ran **different binaries**.  The eleven fields compared by name:
`cid`, `fabric_bad`, `fabric_first`, `family`, `has_evt`, `k`, `seed`, `sys`,
`tier`, `wait_mode`, `win`.  **302 rows × 11 fields: IDENTICAL.**  The
zero-row refusal was demonstrated too (**rc 4**, *"VACUOUS: 0 rows scored"*).

⚠⚠ **AND THE POPULATION IS 302 WHERE WAVE 16 AND WAVE 17 BOTH READ 305.**
**Measured on the UNEDITED tree, before any edit, so it is not ARM-B's.**
FLASH #22's archive-by-rename of `fz2c` / `fz2e` sits in the window.
**REPORTED, NOT EXPLAINED** — and it is exactly why V-1 compares BEFORE to AFTER
**on this tree** instead of to a carried figure.  *A figure carried across trees
is the error `CLAUDE.md` names and FLASH #22 §10 was caught by.*

---

## §3 V-3 — ⭐ **`cutset_lint` PASSES.  ARM-B'S NON-TIMING ARGUMENT IS DELIVERED IN FULL.**  **MET.**

```
BEFORE:  === cutset_lint: FAIL   (80 members / 1 violations)
         VIOLATION X4: the next-state block reads module-level COMBINATIONAL
         VALUE(S) DIRECTLY ... ['q_ripe_lead_n']
AFTER :  === cutset_lint: PASS   (81 members / 0 violations)
         s1w_ in block: 0   live-tainted members: none   includes closed: 19
```

The mechanism is exactly the one WAVE 15 §2.4 named and WAVE 16 §2.3 and §10
item 4 **registered in advance**: ARM-A did not *create* a bypass, it
**relocated** one that had always crossed the BIU port where the lint could not
see it.  ARM-B puts that one value **behind the cut**, so `q_ripe_lead_n`
becomes a stage-2 `reg` written inside the next-state block itself and the
81st cut-set member is `qripe_pop`.

> **The lint went green because the invariant it checks is now true, not because
> the lint was changed.**  `sw/cutset_lint.py` is **byte-untouched** by this
> wave, and so is `sw/phase_split_lint.py`.

`phase_split_lint`: **PASS — 157 members / 779 bits / 0 violations**,
`live-in-stage1: none`.

**`standing_gates.md` §A's line *"`cutset_lint` IS RED IN THE TREE BY DESIGN …
either ARM-B lands and it goes green on its own terms, or the invariant's scope
is deliberately re-registered"* is discharged by the first branch.**

---

## §4 V-4 — **THE FLOP, AND NO STREAM BREAK.**  **MET, AND THE PREDICTION WAS RIGHT IN BOTH DIRECTIONS.**

### 4.1 What the flop is

> **`qripe_pop` — ONE BIT, holding `q_pop && q_ripe && !q_flush`.**  It is **not
> a new register**: it is **bit 778 of `s1q`**, `S1W` **778 → 779**.

### 4.2 The save state did not move

| quantity | BEFORE | **AFTER** | registered prediction |
|---|---|---|---|
| `SS_VERSION` | 0x8F | **0x8F** | UNCHANGED ✔ |
| `SS_COUNT` | 232 | **232** (1 + 109 BIU + 122 EU) | UNCHANGED ✔ |
| `SS_TAG` | 0x8FE8 | **0x8FE8** | UNCHANGED ✔ |
| architectural flops | 229, 0 UNMAPPED | **229, 0 UNMAPPED** | UNCHANGED ✔ |
| whitelist entries | 4 | **4** | UNCHANGED ✔ |
| BIU comb/next-state skipped | 205 | **205** | UNCHANGED ✔ |
| **EU comb/next-state skipped** | 430 | **432** | **432, PREDICTED** ✔ |
| `v30u_ss_pkg.sv` | — | **untouched**, `git diff` EMPTY | ✔ |

> ### **THERE IS NO SAVE-STATE STREAM BREAK.  `ss_lint --core ucore` EXITS 0.**

⚠ **THE ONE `ss_lint` SUB-LINE THAT MOVED IS THE ONE THE PRE-REGISTRATION SAID
WOULD.**  §2.3 and §4 item 2 registered **430 → 432** — `qripe_pop` and
`q_ripe_lead_n`, both written inside the one `always @*` and therefore
**combinational by declaration**.  **WAVE 17 §3.3 predicted this same line would
NOT move and was wrong; the lesson was taken in the other direction here.**

### 4.3 The whitelist edit is a JUSTIFICATION, not an entry

**No entry was added.**  `s1q`'s DERIVED justification gains an **eighth**
registered BIU view, `q_ripe`, because the cone now reads it and a justification
that did not name it would be untrue.  The admission is checked against the
class's own bar, term by term:

* `q_ripe` = `poppable != 4'd0` (`v30u_biu.sv:848`), and
  `poppable = f(r_grn_ttl, r_q_cnt, r_grn_n)` — **all three SSA-mapped**, at
  `SSA_B_GRN_TTL` / `SSA_B_Q_CNT` / `SSA_B_GRN_N` (`v30u_biu.sv:2858-2860`).
* `q_pop` and `q_flush` are stage-1 EU quantities — the existing `s1q` argument,
  unchanged.

So the new bit **is** a pure function of SSA-mapped registers, recomputed under
the same commit condition `(ss_we || srst || ce_half)` as the other 778 — and
its derivation is `$fatal`-asserted at every `ce` (§2.2), not assumed.

### 4.4 **THE COMPILER'S OWN COUNT — ONE FLOP, ON ALL TWENTY DRAWS**

Read only between the two **same-SDC** sides (WAVE 16 §4.1: per-entity counts
are SDC-dependent; both sides here carry the no-exception SDC).

| configuration | `v30u_biu` | **`v30u_eu`** | whole-design `map_registers` |
|---|---:|---:|---:|
| CONTROL, W17 ARM-A → W19 ARM-B | **434 → 434** | **1,326 → 1,327** | 5,687 → **5,688 (+1)** |
| RETENTION, W17 ARM-A → W19 ARM-B | **434 → 434** | **1,326 → 1,327** | 5,708 → **5,709 (+1)** |

Constant across all five seeds of every sweep.

⚠ **AND FOR ONCE THE ±1 WHOLE-DESIGN WOBBLE DID NOT APPEAR**: the whole-design
delta is **+1**, which is **exactly** the entity delta, on **both**
configurations.  WAVE 7, WAVE 14 §3.4, WAVE 15 §6 and WAVE 16 §4 each recorded
an unexplained ±1 **outside** `v30_core`.  **It is absent here.  Recorded, not
explained, and not offered as evidence that it is gone.**

⚠ `fit_registers` **varies across the seeds of every sweep** (physical synthesis
duplicates registers) and is **not read as evidence**.

⚠ **THE TEXTUAL FLOP CHECK WOULD STILL BE WRONG.**  WAVE 15 §6 recorded that a
`<=` scan prints *"no flop added"* for ARM-B because its flop arrives as a
**parameter widening**.  That trap is unchanged; **the fit report is the
authority and is what is quoted.**

---

## §5 V-2 — **THE REQUIREMENT DID NOT REGRESS.  IT IMPROVED, ON EVERY DRAW OF BOTH CONFIGURATIONS.**  **MET.**

`sw/run_wave19_g6.sh` (WAVE 17's driver, wave tag changed, no logic altered),
`quartus_gate.py --seeds 5` and `--seeds 5 --retention`, seed set
**{1,2,3,4,5}**, one shared `quartus_map` per sweep, **both launched by ONE
wrapper** that ran them **strictly sequentially** behind the `pgrep -x`
single-writer guard, with `hdl/nec_test_ucore.qsf` restored by
`git checkout -- <that exact path>` around every run.

### 5.1 THE EXCEPTION IS STILL GONE, AND IT IS CHECKED THREE WAYS

1. **`hdl/nec_test.sdc` carries ZERO uncommented exceptions**, anchored:
   `grep -cE '^[[:space:]]*set_(multicycle_path|false_path|max_delay)'` = **0**,
   measured on this tree before the edit and after.  ⚠ **The unanchored
   `grep -c set_multicycle_path` reads 2** — the commented DO-NOT-RESTORE record
   — **and the pre-registration named it as the wrong instrument before the
   sweeps ran.**  It is kept beside the anchored form as a known-wrong control.
2. **`nec_test.sdc` is not touched by any commit of this wave.**
3. **Every receipt's `core_domain` measures `SAME`, `INTO` and `OUTOF` at
   k = 1.0 against a nominal of 1.0, with `off_class` EMPTY, on 30 of 30 class
   readings across 10 of 10 draws** — a draw still fitted to an exception would
   measure k = 2.0 and land in `off_class`.  **That is the check that the
   deletion is still reaching the compiler**, in WAVE 13's polarity.

### 5.2 CONTROL — receipt `3c983b10a73fb494…`, verdict **PASS**, 1,864 s

| seed | Fmax | worst setup | ALMs | core k | `off_class` | E11 | bars | |
|---|---:|---:|---:|---|---|---|---|---|
| 1 | 34.68 | +2.419 | 8,434 / 41,910 (20 %) | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 2 | 34.68 | +2.413 | 8,429 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 3 | 34.91 | +2.609 | 8,436 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| **4** | **34.48** | **+2.245** | 8,413 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 5 | 34.95 | +2.638 | 8,432 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |

> **`worst-of-5@seeds{1,2,3,4,5}` = 34.48 MHz** · median 34.68 · best 34.95 ·
> spread 0.47 · **5 of 5 PASS** · margin over the bar **+2.48 MHz**

### 5.3 RETENTION — **THE SHIPPING CONFIGURATION** — receipt `a5a59e9ed3726729…`, verdict **PASS**, 1,562 s

| seed | Fmax | worst setup | ALMs | core k | `off_class` | E11 | bars | |
|---|---:|---:|---:|---|---|---|---|---|
| 1 | 34.99 | +2.670 | 8,443 / 41,910 (20 %) | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 2 | 34.85 | +2.558 | 8,448 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 3 | 35.24 | +2.872 | 8,460 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| **4** | **34.41** | **+2.185** | 8,459 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 5 | 34.72 | +2.446 | 8,461 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |

> **`worst-of-5@seeds{1,2,3,4,5}` = 34.41 MHz** · median 34.85 · best 35.24 ·
> spread 0.83 · **5 of 5 PASS** · margin over the bar **+2.41 MHz**

### 5.4 EVERY CLAUSE, ON ALL TEN DRAWS

| clause | measured |
|---|---|
| Fmax ≥ 32.0 | **10 of 10**, minimum 34.41 |
| worst setup > 0 | **10 of 10**, minimum **+2.185 ns** |
| TNS 0.000 setup AND hold | **10 of 10, all four domains each, both directions** |
| 0 errors, every stage Successful | **10 of 10** (`E2`, `error_lines` 0) |
| 0 latches · 0 `lpm_divide` | **10 of 10** |
| per-seed `bars` | **5 bars each, ZERO failing, 10 of 10** |
| `verdict` | **PASS on 10 of 10 per-seed receipts and BOTH distributions** |
| `configuration` DERIVED from the reports (E-6) | CONTROL/DEFAULT and **RETENTION (X1_AD_RETENTION=1)**, self-labelled |
| `.rbf` distinct within a sweep (E-9) | **5 of 5, both** |
| `E8_seed_honoured` | asked = command line = settings, 10 of 10 |

### 5.5 THE PAIRED READING — **AGAINST THE LANDED TREE, AND EVERY INTERVAL EXCLUDES ZERO**

⚠ **The scorer's positive control was run FIRST**: `sw/wave14_ceiling.py
--selftest` reproduces WAVE 13's **committed** `w13-split-noexc-*` draws,
worst-of-5, spread and register columns from their bytes on disk — **SELFTEST
PASS** — and `sw/wave13_score.py` was pointed at **WAVE 17's committed pair
before it was pointed at anything new** and reproduced its published **33.00 /
33.20** exactly.

Δ = arm T_min − base T_min; **positive means the arm's arc is SHORTER**.
95 % CI from a **tabulated** t (df = 4, t = 2.776).

| | per-seed Δ ns (1..5) | **paired mean** | 95 % CI | t | **worst-of-5** | **ΔMHz** |
|---|---|---:|---|---:|---:|---:|
| **CONTROL** | +0.247 · +1.470 · +1.225 · +0.469 · +0.681 | **+0.818** | **[+0.180, +1.457]** | **+3.56** | 33.00 → **34.48** | **+1.48** |
| **RETENTION** | +1.149 · +0.856 · +1.065 · +0.591 · +1.321 | **+0.996** | **[+0.647, +1.346]** | **+7.91** | 33.20 → **34.41** | **+1.21** |

Paired Fmax: **+0.952 MHz [+0.223, +1.681]** and **+1.170 MHz [+0.766,
+1.574]**.  **Every seed is positive on both configurations and all four
intervals sit above zero.**

> ⚠⚠ **AND THIS PAIRED READING IS ARITHMETIC, NOT AN INDEPENDENT MEASUREMENT —
> SAID PLAINLY BECAUSE IT WOULD OTHERWISE READ AS ONE.**  §6 shows both sides
> are byte-reproductions of WAVE 15's two arms, so the difference is *required*
> to equal WAVE 15's own (3.665 − 2.847 = +0.818; 2.425 − 1.429 = +0.996) — and
> it does, to the thousandth.  **What it confirms is the determinism, not the
> effect a second time.**  The effect's evidence is WAVE 15's paired A/B; this
> wave re-drew it on the landed tree and got the same fits.

### 5.6 THE REGISTERED RESOLUTION WAS NOT NEEDED

V-2 registered, **before any draw existed**, that a `worst-of-5` between 32.0
and the tree's 33.00 / 33.20 would be a result to report and hand to the
coordinator rather than an automatic revert.  **It did not arise: both figures
are above the tree's, on every draw.**  The resolution is recorded because
WAVE 16 §3.2 wrote a bar that had none.

### 5.7 AREA — **THE DESIGN DOES NOT SHRINK, AND HERE THAT IS SCOREABLE**

`v30_core` combinational ALUTs, CONTROL: BIU **1,151 → 1,285**, EU
**5,075 → 5,142**; RETENTION: BIU 1,138 → 1,259, EU 5,044 → 5,163.  Whole-design
fitted ALMs **8,224-8,275 → 8,413-8,436** (CONTROL) and **8,193-8,250 →
8,443-8,461** (RETENTION), 20 % of 41,910 throughout.

⚠ **WAVE 16 §3.3 could not score this because its sign changed between
configurations.  Here it does not** — the design grows on both, by ~180 ALMs.
Pre-registration §4 item 5 expected exactly that and is **RIGHT**.  Still
reported with `ucore_provenance.md` §74.4a's caveat: A&S combinational counts
are not reproducible run to run.

### 5.8 ⚠ HOW THESE FIGURES MAY AND MAY NOT BE QUOTED

* **The requirement is met on every draw, and that is not a `worst-of-5`
  artefact** — the bar says *every draw*, and every draw clears it by ≥ 2.41 MHz.
* ⚠ **ONE GREEN BUILD IS NOT CLOSURE AND TEN ARE NOT EITHER.**
  `standing_gates.md` §A governs: **the same tree has drawn 19.42 and 45.91
  MHz.**  What is established is that this RTL, this SDC and this tool close on
  **these ten draws at these five seeds**.
* ⚠ **THE MARGIN IS ~2.4 MHz**, up from ~1.0.  A downstream integrator on a
  different device, speed grade or target frequency is still not promised
  anything by this document.
* ⚠ **AND IT IS NOT SILICON.**  `CLAUDE.md`'s correctness target is SILICON
  MATCH.  **Nothing here has been on a board** (§7).

---

## §6 ⭐⭐ **THE LANDING REPRODUCES WAVE 15's ARM-B ARM TO THE BITSTREAM, ON TEN OF TEN DRAWS OF BOTH CONFIGURATIONS**

Because §1.5 makes the inputs identical, the ten fits are a **like-for-like
re-run of WAVE 15's `s1q` column six days later, in a different tree, by a
different driver.**  Compared **field by field by name** against the committed
`sw/testdata/g6dist/w15-s1q-{control,retention}-n5/` — **no digest is computed
here.**

| quantity | result |
|---|---|
| `input_manifest` | **`ee6a4eff46e483d3…` / 99 files — IDENTICAL, both configurations** |
| distribution scalars | **30 of 38 IDENTICAL**, both configurations.  The 8 that differ are `artifact_dir`, `completed`, `git`, `name`, `per_seed`, `stages`, `started`, `tree` — **identity, path and clock fields, required to differ** |
| per-seed fields (`fmax_mhz`, `worst_setup_ns`, `alms`, `verdict`, `configuration`, `core_fmax_mhz`, `seed`, `seed_echo`, `seed_honoured`, `tns_violations`, `truefmax`, `core_domain`) | **12 of 12 IDENTICAL on 5 of 5 seeds of BOTH configurations — 120 of 120 comparisons** |
| **`nec_test_ucore.rbf` sha256** | ⚠⚠ **BYTE-IDENTICAL ON 10 OF 10 DRAWS.**  CONTROL `e91a67badeef2c17` · `2b4ac40b44019e9b` · `eeb28ed32aa826fc` · `f4239199a0e070ba` · `d20488f4f8af524a`; RETENTION `3d4a2e86190d10d7` · `d516afb97a6f78b4` · `e2ce25c6239855f8` · `13b8374abfe8bf15` · `3681c9c8b3ae14bc` |

> ### **THIS IS THE SECOND TIME THIS CAMPAIGN HAS REPRODUCED A BITSTREAM PAYLOAD ACROSS WAVES.**  WAVE 17 §6 did it for ARM-A; this does it for ARM-B.  **And it is the strongest available proof that §1.4's mechanical edit composed to the artifact WAVE 15 measured** — not merely to something that behaves like it.

⚠ **WHAT THIS DOES *NOT* SAY.**  A byte-identical `.rbf` from byte-identical
inputs is **the compiler being deterministic**, which is a property of the tool,
not evidence about the design.  It says nothing about other seeds, another
device, or any later RTL change.  `standing_gates.md` §A still governs.

⚠ **AND IT MEANS 34.48 / 34.41 ARE WAVE 15's FITS, RE-DRAWN — NOT A SECOND,
INDEPENDENT SIZING.**  §5.5 already says so; it is repeated here because the
reproduction is easy to mistake for corroboration of the *effect* when it is
corroboration of the *composition*.

---

## §7 ⚠⚠ THE FABRIC DEBT — **RE-OPENED ON THE DAY IT WAS PAID**

**FLASH #22 was taken 2026-09-19, hours before this wave, on a bitstream built
from `d5f5fca539`, whose `hdl/` is byte-identical to WAVE 17's landing
`d3c295cdef`.**  It was the first bitstream ever built with no SDC timing
exception, and it booted: `MATCH 800 ×3`, corpus 102 failures of 3,838, 0
transport errors.

> ### **THIS LANDING CHANGES THE EU'S NEXT-STATE STRUCTURE AND WIDENS ITS SHADOW BY A BIT.  THE `.rbf` MOVES.  NO FLASH #22 FIGURE MAY BE QUOTED AGAINST THIS TREE.**

`CLAUDE.md`'s correctness target is **SILICON MATCH**.  **This wave pays no part
of that debt and re-opens it in full.**  Nothing was flashed; nothing was on a
board; no board was contacted.

**⭐ One thing makes the re-payment cheap, and it is measured, not hoped:**
FLASH #22 §0 item 5 established that WAVES 7, 12, 16 and 17 are **confirmed
behaviour-neutral in fabric** by their own before/after ladders, and this wave's
V-1 puts ARM-B in the same class **offline**.  **Offline neutrality is not
fabric neutrality** — that is the whole content of the debt — but a re-flash has
one new mechanism to confirm, not five.

---

## §8 THE BARS, SCORED

| bar | verdict |
|---|---|
| **V-1** equivalence, BEFORE side first, every leg IDENTICAL | **MET.**  `_rc.txt` identical on **39 of 40** legs; **35 of 38** scored legs IDENTICAL; all three movers registered in advance and each is a lint or a census sub-line, **not a behavioural leg**.  `fz2_replay` **302 × 11 IDENTICAL by name** over a non-zero printed population with a DIFFERING `tb_sys_receipt`.  The comparator's own positive control PASSES.  §2 |
| **V-2** the requirement must not regress; every draw PASSES E1-E5, both configurations | **MET, AND IMPROVED.**  **10 of 10 PASS, zero failing bars**; `worst-of-5` **CONTROL 34.48 (+1.48 over the tree's 33.00)** and **RETENTION 34.41 (+1.21 over 33.20)** — **WAVE 15's predicted 34.48 / 34.41 exactly**.  TNS 0.000 setup AND hold, all four domains, all ten draws; `core_domain` k = 1.0 and `off_class` EMPTY on 30 of 30 readings; anchored SDC grep **0**.  §5 |
| **V-3** `cutset_lint` PASSES | ⭐ **MET.**  **FAIL 80 / 1 → PASS 81 / 0.**  The lint is byte-untouched; the invariant it checks is now true.  `phase_split_lint` **PASS 157 / 779 / 0**.  §3 |
| **V-4** the flop named, counted, save-state disposition registered before the edit | **MET.**  `qripe_pop`, ONE BIT, `s1q` bit 778, `S1W` 778 → 779, **DERIVED on the EXISTING whitelist entry, no entry added**.  `ss_lint` exits 0; **`SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 / 229 flops / 4 entries ALL UNCHANGED — NO STREAM BREAK.**  Compiler: **`v30u_eu` 1,326 → 1,327 on all 20 draws**, `v30u_biu` 434 → 434.  §4 |
| **V-5** `E11` true on every draw | **MET.**  `E11_no_build_stamp` **pass on BOTH distribution receipts and all TEN per-seed receipts**, `files_scanned` 99, `file_present` False, `token_hits` `{}`.  ⚠ Read at DISTRIBUTION level (trap #9); the per-seed receipts were read from **inside this tree**, so WAVE 15's and WAVE 16's relative-path trap did not arise. |
| **V-6** the revert condition | **NOT FIRED.**  V-2 did not fail; **no leg of V-1 moved** except the three registered movers, of which one **is** V-3's bar, one is V-4's, and one is a census sub-line that is not a flop.  **THE LANDING STANDS AT `ce39ed61bf`.  NO BAR WAS SOFTENED.** |
| §4 item 1 — *V-1 passes with every leg identical* | **RIGHT.** |
| §4 item 2 — *`ss_lint`'s skipped count moves 430 → 432* | **RIGHT**, and it is the correction of WAVE 17 §3.3's wrong prediction about the same line. |
| §4 item 3 — *`cutset_lint` 81 / 0, `phase_split_lint` 157 / 779* | **RIGHT**, both exactly. |
| §4 item 4 — *`worst-of-5` between 33.00 and 34.48 / 33.20 and 34.41* | ⚠ **RIGHT ONLY AT THE ENDPOINT, AND FOR A REASON I DID NOT PREDICT.**  I wrote *"this is NOT a prediction that WAVE 15's exact figures reproduce"* and guessed the inputs would differ because WAVE 18 moved `hdl/rtl/core/v30_core.sv`.  **They did not differ: that file is not in the ucore revision's manifest**, the manifest is byte-identical, and the figures reproduced **exactly** — §6. |
| §4 item 5 — *the design does not shrink* | **RIGHT, and scoreable this time** (§5.7) — it grows on **both** configurations, unlike WAVE 16 §3.3. |

---

## §9 WHAT IS OWED

1. ⚠⚠ **THE FABRIC CONFIRMATION.**  Re-opened by this landing on the day
   FLASH #22 paid it.  **NO FLASH #22 FIGURE MAY BE QUOTED AGAINST THIS TREE.**
   §7.  **It is the largest debt in the campaign and the only thing between the
   requirement being MET IN SIMULATION and being MET.**
2. **`q_flush` IS THE ONLY REMAINING TERM OF THIS MECHANISM AND ITS SIZE IS
   MEASURED** — WAVE 15 §3.4: 2 LUT levels, ~0.5 ns, on 200 of 200 ARM-B CONTROL
   paths.  Splitting it is the same mechanism's third level.  **NOT taken**, for
   WAVE 15's own reason and because nothing needs it.
3. ⚠ **`fz2_replay`'s POPULATION MOVED 305 → 302** between WAVE 17 and this wave,
   measured on the unedited tree.  FLASH #22's archive-by-rename is in the
   window.  **Reported, not explained; a falsifier is one `git log` away and is
   NOT taken here**, because diagnosing an instrument in the wave it is scoring
   is how a result gets chosen.
4. ⚠ **`fz2_replay` IS STILL VACUOUS IN A GIT WORKTREE AND STILL EXITS 0.**  This
   wave avoided it by running both legs in the main tree.  The permanent fix
   belongs in `fz2_replay.py` — refuse a zero-row population — **BOOKED for the
   fourth time.**
5. ⚠ **`wave16_ladder_cmp.py` STILL REPORTS A MISSING LOG AS `IDENTICAL`**
   (WAVE 17 §8 item 9).  It is **NOT edited here.**  §10 demonstrates the defect
   and a corrected successor side by side; whether the shared instrument should
   be changed is the coordinator's call, not a repair to slip into a landing.
6. **`check_core --ss-sweep` IS STILL ON NO REGISTERED LADDER** — booked by
   WAVES 2, 3, 4, 9, 13, 14, 15, 16, 17.  **Booked for the tenth time**, and the
   shadow it would cover **just got a bit wider.**
7. **`standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS WAVE** (the
   WAVE 11-18 precedent; the coordinator decides).  Now unregistered, and the
   list has grown: bar **E11**; `test_quartus_gate` **287/287**; the stale
   `ss_lint` row against this tree's **232 / 229 / 4 / 0x8F / 0x8FE8**;
   **`CE_HALF` as an unconditional core port**; `demux_off_gate`'s *"two muxed
   ports"*; the `s1q` whitelist entry; **`cutset_lint` NO LONGER RED — §A's
   "RED IN THE TREE BY DESIGN" paragraph is now OUT OF DATE and must be
   rewritten**; FLASH #22 itself; and **this landing, with its new
   `worst-of-5` pair.**
8. **WAVE 11's one-fit repair**, the **±1 whole-design register wobble** (absent
   here, §4.4), and **`sta_biu_roundtrip.tcl`'s confounded `q_ripe_lead_n`
   counter** (WAVE 15 §3.2 — ⚠ and ARM-B moves that node again) are inherited
   and untouched.
9. ⚠ **`sta_cutset_diag.tcl`'s C-8 string classifier under-reports because a
   physical-synthesis duplicate of `s1q` is filed under a fanout-net name**
   (handoff §10 item 4).  `s1q` is now 779 bits.  Inherited, untouched.
10. **THE ARM-B REFERENCE WORKTREE IS RETAINED DELIBERATELY** —
    `~/.cache/ucsimt-tmp/wave19/ref_armb`, detached at `850ef46559` with
    `arm_s1q.diff` applied, the independent reference §1.2, §1.5 and §6 are
    scored against.  WAVE 17's `ref_arm` and WAVE 16's two R-3 worktrees are
    untouched.  `git worktree list` shows all four; none is on a branch.

---

## §10 ⚠ INSTRUMENT FINDINGS OF THIS WAVE

### 10.1 **THE OLD LADDER COMPARATOR'S DEFECT, DEMONSTRATED BESIDE ITS FIX — AND THE SHARED FILE WAS NOT TOUCHED**

WAVE 17 §3.1a found that `wave16_ladder_cmp.py` returns a sentinel **line** for
an absent log, so two absent logs compare EQUAL and a comparison over **zero
real data** scores perfectly.  It booked the fix and did not take it.

This wave does not take it either — it writes a **new** instrument,
`sw/wave19_ladder_cmp.py`, carrying the extra leg and **one clause** (an absent
log returns the empty list, routing it to the VACUOUS branch).  **Both were then
pointed at the same inputs:**

| inputs | `wave16_ladder_cmp.py` | `wave19_ladder_cmp.py` |
|---|---|---|
| two EMPTY directories | `37 legs: 37 IDENTICAL, 0 DIFFERING, 0 VACUOUS`, **exit 0** | `38 legs: 0 IDENTICAL, 0 DIFFERING, **38 VACUOUS**`, **exit 1** |
| `cc_all.log` absent on BOTH sides | `cc_all  IDENTICAL (1 scored line)  *** MISSING LOG ***`, **exit 0** | `cc_all  *** NO SCORED LINE MATCHED — VACUOUS LEG ***`, **exit 1** |
| `cc_all.log` absent on ONE side | *(both)* `*** DIFFERS ***`, exit 1 — correct and loud | same |

**A NEW INSTRUMENT IS NOT A REPAIR OF THE OLD ONE**, and **no figure in this
document is quoted from `wave16_ladder_cmp.py`.**

### 10.2 ⚠ A SHELL CONSTRUCTION THAT SILENTLY DID NOTHING, CAUGHT ONLY BECAUSE A CONTROL REFUSED TO FIRE

Building the applier's duplicate-entry control, `{ echo; grep '^s1q ' f; } >> f`
**did not append** — `grep -c` read 1 before and 1 after — so the control ran
against an unmodified file and **reported rc 0 where 3 was required.**  It was
re-done in Python, the duplicate appeared (`after: 2`), and the clause **fired
correctly (rc 3)**.

> **The control did not fail; it refused to say what it was supposed to say, and
> that is the only reason the no-op was noticed.**  A control whose *expected*
> outcome is a refusal is the one shape that cannot be faked by a no-op — and it
> nearly was, by reporting success.

### 10.3 THE APPLIER IS ITSELF AN INSTRUMENT AND CARRIES THREE CONTROLS

§1.4.  All three refuse (rc 3).  **It asserts the output hash rather than
trusting `git apply`'s exit code**, which is the `artifact.require()` habit
applied to a patch.

### 10.4 ⚠⚠ **AND IT HAPPENED ONE MORE TIME, IN THE FINAL VERIFICATION SWEEP: A LOOP REPORTED `rc=2` FOR A GATE IT NEVER INVOKED**

Closing out, a convenience loop re-ran the standing lints at HEAD and printed:

```
gen_ucore_qsf.py --check     rc=2
```

**The gate exits 0.**  The loop held its command in a variable,
`g="sw/gen_ucore_qsf.py --check"`, and ran `python3 $g` — and **this session's
shell is `zsh` 5.9, which does NOT word-split an unquoted parameter.**  Python
was handed a single filename *"sw/gen_ucore_qsf.py --check"*, failed to open it,
and exited 2.  Diagnosed **positively**, not assumed:

```
--- unquoted $g (what the loop did) ---
rc=2 :: python3: can't open file '.../sw/gen_ucore_qsf.py --check': No such file
--- word-split explicitly ---
rc=0 :: gen_ucore_qsf: nec_test_ucore.qsf is up to date
```

`gen_ucore_qsf --check` is **PASS**, and it was also PASS when the driver ran it
before the sweeps.

> **THIS IS §C's META-FINDING IN MINIATURE, ARRIVING UNINVITED IN MY OWN
> CLOSING CHECK: *a gate's REGISTERED ROW and its ABILITY TO RUN are two
> different facts.*  WAVE 18 found gates that could not run while the ledger
> carried green rows for them.  This is the mirror — a gate that runs fine,
> reported RED by a harness that never invoked it.  A LOUD RED CAN BE AS FALSE
> AS A SILENT GREEN, and the only thing that separated them here was reading the
> error text instead of the exit code.**

⚠ **The finding is about the closing loop, not about any scored leg.**  Every
figure in this document comes from the ladder driver and `quartus_gate`, both of
which invoke their tools as argument vectors, never through an unquoted
variable.  **No bar was scored by the defective loop.**

---

## §11 DISCIPLINE, DECLARED AND KEPT

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**  No Codex.  No
  nested subagent.
* **THE WAITS BLOCKED; THEY DID NOT POLL A TURN.**  One `until ! pgrep -x …`
  guard per Quartus stage inside the driver, and **both sweeps were launched by
  ONE wrapper** that ran them strictly sequentially, so no two Quartus stages
  could race.  Single-writer guard by **`pgrep -x`, EXACT BINARY NAME, ONE
  PATTERN PER CALL**, asked before the first stage; ⚠ `pgrep -f <script>`
  self-matches and was never used.
* Drivers carry **`set -u`, NEVER `set -e`.**
* ⚠ **NO `cmd | tail -1; rc=$?` ANYWHERE.**  Every exit code in this wave was
  captured to a variable before the pipe, or read from the tool directly.  That
  construction broke `t30_sweep.sh` for over a year and caught WAVE 18 and the
  coordinator in the last two days.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  `hdl/nec_test_ucore.qsf` was restored by `git checkout -- <that exact path>`
  around every Quartus run and measured **clean** after both sweeps, as were
  `hdl/nec_test.qsf` and `hdl/nec_test.qpf` — **no FSM revision was compiled**
  (WAVE 18's in-place-rewrite hazard).  `gen_ucore_qsf --check` **PASS** before
  the sweeps.
* ⚠ **`git add` BY EXPLICIT PATH ONLY**, and **`sw/testdata/receipts/*.jsonl`
  IS NOT COMMITTED** (WAVE 16 §12.1's miss, WAVE 17's rule): this wave's
  Verilator and Quartus rows stay in the working tree, because committing an
  append-only ledger the wave writes to sweeps whatever was already dirty in it.
  **Nothing is lost**: every receipt is committed **BY VALUE** under
  `sw/testdata/g6dist/w19-*/` and `sw/testdata/wave19/`, and §5 quotes their
  `id`s from there.
* **THE 21 PRE-EXISTING MODIFIED TRACKED FILES THAT ARE THE USER'S OWN
  UNCOMMITTED WORK ARE UNTOUCHED** — counted **21** before and **21** after.
* **THIS WAVE ADDED NO `hdl/*.log`** — checked against the directory, not
  recall: `ls hdl/*.log` is **15 files**, the same 14 pre-existing untracked
  `quartus_gate_*.log` (Aug 11 … Sep 12) plus the gitignored
  `hdl/quartus_gate_build.log` (Aug 20).  Both Quartus transcripts went to
  `--log` under `sw/testdata/wave19/w19-armb-noexc/`.
* `~/.cache/ucsimt-tmp/wave19/` for every intermediate; **nothing in `/tmp`**
  except two throwaway scratch files outside the project.
* ⚠ **CONTENT COMPARED, NOT A DIGEST COMPUTED HERE**: the ladder leg by leg on
  scored lines queried by name, `chain_lfsr` row for row, `fz2_replay` field by
  field with the row count printed first, and §6's cross-wave reproduction by
  NAMED FIELD.  *A number with no artifact id is not quotable.*
* **EVERY CLASSIFIER CARRIED A POSITIVE CONTROL, REPORTED FIRST**: the ladder
  comparator's `--selftest` (in the same invocation as its verdict);
  `wave14_ceiling.py --selftest` against WAVE 13's committed bytes;
  `wave13_score.py` pointed at WAVE 17's committed pair **before** anything new
  and reproducing 33.00 / 33.20; `fz2_replay`'s printed row count, its differing
  `tb_sys_receipt` and its zero-row refusal; the applier's three refusals; and
  the old-vs-new comparator demonstration.  ⚠ **One of them caught a no-op**
  (§10.2).
* **A CENSUS DOES NOT SIZE A CANDIDATE IN EITHER DIRECTION.**  None is offered
  or quoted.
* **Record what was measured, not what was expected** — §8's last five rows
  include one expectation of mine that was **right for a reason I got wrong**
  (§4 item 4), and §5.5 and §6 both say plainly that the reproduction is
  evidence about composition and determinism, **not a second sizing of the
  effect.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
