# WAVE 17 — **THE REQUIREMENT IS MET.  THE CE MULTICYCLE IS DELETED AND THE ucore CLOSES TIMING ON EVERY DRAW OF BOTH CONFIGURATIONS.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/phase_split_landing_prereg_2026-09-18.md` at
**`693dcb98d9`**, committed **before the first `hdl/` edit of the main tree**
(`git status --porcelain hdl/` tracked was **0** at that commit).  Its bars
**S-1 … S-10 are quoted verbatim below and not one of them was softened,
re-derived or re-scoped after a result was seen.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.  `docs/notes/standing_gates.md` §A governs every timing figure.

| | |
|---|---|
| **Tree at entry** | `4a796cc754` (WAVE 16's results), tracked `hdl/` clean |
| **The landing** | **(a) `1c71c4f5e3` · (b) `a35a29c082` · (c) `d3c295cdef`** |
| **Ladders** | `sw/testdata/wave17/{before,after}/`, 39 legs each, one unedited driver |
| **Verilator binaries** | BEFORE **`1b572c1931852b2a…`** (output `c3073dfad5bc1250…` — WAVE 16's ARM-A bytes) · AFTER **`ca4efe751c23c1d8…`** (output `2333b6552d97d05e…`) |
| **Distributions** | `sw/testdata/g6dist/w17-split-presel-noexc-{control,retention}-n5/`, receipts **`802659ce76f59dc8…`** and **`082adea30d9117f9…`** |
| **`input_manifest`** | **`c3305d40f62e497f…` / 99 files, on BOTH configurations — and it is WAVE 15's presel manifest byte for byte** |
| **Tool** | Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns; Verilator 5.032 |
| **Cost** | 2 sweeps · 10 fits · 2 maps · 83 min of Quartus, plus two full 39-leg ladders |

---

## §0 THE HEADLINE

> ### **1. S-1 IS MET.  WITH ZERO TIMING EXCEPTIONS IN `nec_test.sdc`, `quartus_gate.py --seeds 5` RETURNS `PASS` ON ALL FIVE DRAWS OF THE CONTROL CONFIGURATION AND ALL FIVE OF THE RETENTION CONFIGURATION.**
>
> **CONTROL `worst-of-5` = 33.00 MHz** (draws 33.00 · 33.48 · 33.93 · 34.14 ·
> 34.39) and **RETENTION `worst-of-5` = 33.20 MHz** (33.20 · 33.64 · 33.72 ·
> 33.84 · 33.96), against a bar of **32.0**.  Worst setup **+0.943 … +2.172 ns**
> and **+1.125 … +1.807 ns** — positive on every draw.  **TNS 0.000 setup AND
> hold on all four clock domains of all ten draws**, 0 error lines, 0 latches,
> 0 `lpm_divide`, `off_class` EMPTY on all ten against a nominal of **k = 1.0**,
> `E11` pass on both distributions and all ten per-seed receipts.
>
> **This is the campaign's success condition, written down on 2026-09-08 and
> unmet through sixteen waves.  It is met.  That is a fact with receipts, and it
> is stated as one.**
>
> **2. THE TREE IS BIT-EXACT.  33 OF 37 SCORED LADDER LEGS IDENTICAL, AND ALL
> FOUR MOVERS WERE REGISTERED BEFORE THEY WERE SEEN.**  169,000/169,000 at
> `--ce-div` 2, 3, 4 **and** 8 with div 1 refused · **the exact 181 — `FA`
> 500/500, `FB` 500/500, `INT.FB` 200/200** · `ulockstep` **17,350 ALL
> LOCKSTEP** · the four HLT sweeps **279/283** · `sm3_s16_score` 1,320/1,371
> with its census unmoved · **the four `chain_lfsr` signatures BYTE-IDENTICAL**
> over 1.6 M fabric clocks · **`fz2_replay` 305 rows × 11 fields IDENTICAL,
> compared BY NAME** · `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8
> unmoved, `v30u_ss_pkg.sv` untouched.
>
> **3. AND THE LANDING REPRODUCES WAVE 15 TO THE BITSTREAM.**  The composed
> tree is sha256-identical to WAVE 15's ARM-A arm on **all 127 tracked files of
> `hdl/`**, the `input_manifest` is the same 99-file hash, **every one of the
> eleven distribution scalars and 13 of the 15 per-seed field names are
> IDENTICAL on all ten draws** — and **`nec_test_ucore.rbf` is BYTE-IDENTICAL
> on 10 of 10 draws**, four days and two trees apart.  The two fields that
> differ are the receipt id and the `.fit.summary`/`.sof` hashes, which embed a
> path and a timestamp.
>
> **4. ONE HUNK OF EDIT (b) HAD TO BE RE-DERIVED AND THE RE-DERIVATION IS TWO
> LINES OF CONTEXT.**  Declared in the pre-registration before it was used.
>
> **5. `cutset_lint` FAILS X4 NAMING `q_ripe_lead_n`, EXACTLY AS WAVE 15
> MEASURED AND WAVE 16 REGISTERED IN ADVANCE.  IT WAS NOT TOUCHED.**
>
> **6. ⚠ NOTHING WAS FLASHED, AND THE FABRIC DEBT IS NOW FOUR STRUCTURAL
> CHANGES DEEP.**  This wave changes the EU's clocking.  **No fabric figure
> taken on FLASH #21 or earlier may be quoted against this tree.**

---

## §1 S-1 — **THE REQUIREMENT.  MET, ON EVERY DRAW OF BOTH CONFIGURATIONS.**

`sw/run_wave17_g6.sh` (WAVE 16's driver, wave tag changed, **no logic
altered**), `quartus_gate.py --seeds 5` and `--seeds 5 --retention`, seed set
**{1,2,3,4,5}**, one shared `quartus_map` per sweep, both launched by **one**
wrapper that ran them **strictly sequentially** behind the `pgrep -x`
single-writer guard, with `hdl/nec_test_ucore.qsf` restored by
`git checkout -- <that exact path>` around every run.

### 1.1 CONTROL — receipt `802659ce76f59dc8…`, verdict **PASS**, 2,480 s

| seed | Fmax | worst setup | ALMs | core k (SAME/INTO/OUTOF) | `off_class` | E11 | bars | |
|---|---:|---:|---:|---|---|---|---|---|
| 1 | 34.39 | **+2.172** | 8,275 / 41,910 (20 %) | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| **2** | **33.00** | **+0.943** | 8,273 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 3 | 33.48 | +1.384 | 8,224 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 4 | 33.93 | +1.776 | 8,252 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 5 | 34.14 | +1.957 | 8,245 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |

> **`worst-of-5@seeds{1,2,3,4,5}` = 33.00 MHz** · median 33.93 · best 34.39 ·
> spread 1.39 · **5 of 5 PASS** · margin over the bar **+1.00 MHz**

### 1.2 RETENTION — receipt `082adea30d9117f9…`, verdict **PASS**, 2,518 s

| seed | Fmax | worst setup | ALMs | core k | `off_class` | E11 | bars | |
|---|---:|---:|---:|---|---|---|---|---|
| 1 | 33.64 | +1.521 | 8,250 / 41,910 (20 %) | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 2 | 33.84 | +1.702 | 8,246 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 3 | 33.96 | +1.807 | 8,206 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| 4 | 33.72 | +1.594 | 8,193 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |
| **5** | **33.20** | **+1.125** | 8,221 | 1.0 / 1.0 / 1.0 | `[]` | pass | 5/5 | **PASS** |

> **`worst-of-5@seeds{1,2,3,4,5}` = 33.20 MHz** · median 33.72 · best 33.96 ·
> spread 0.76 · **5 of 5 PASS** · margin over the bar **+1.20 MHz**
> ⚠ **RETENTION IS THE SHIPPING CONFIGURATION** — every flashed bitstream in
> this project is built `WITH X1_AD_RETENTION=1`, and it is the tighter
> distribution and the larger margin here.

### 1.3 EVERY BAR OF S-1, ITEM BY ITEM, ON ALL TEN DRAWS

| clause | measured |
|---|---|
| Fmax ≥ 32.0 | **10 of 10**, minimum 33.00 |
| worst setup > 0 | **10 of 10**, minimum **+0.943 ns** |
| TNS 0.000 setup AND hold | **10 of 10, all four domains each, both directions** |
| 0 errors, every stage Successful | **10 of 10** (`E2`, `error_lines` 0) |
| 0 latches | **10 of 10** |
| 0 `lpm_divide` | **10 of 10** |
| per-seed `bars` | **5 bars each, ZERO failing, 10 of 10** |
| `verdict` | **PASS on 10 of 10 per-seed receipts and on BOTH distributions** |
| `configuration` DERIVED from the reports (E-6) | CONTROL/DEFAULT and **RETENTION (X1_AD_RETENTION=1)**, self-labelled |
| `.rbf` distinct within a sweep (E-9) | **5 of 5, both** |
| `E8_seed_honoured` | asked = command line = settings, 10 of 10 |

### 1.4 ⚠ HOW THIS FIGURE MAY AND MAY NOT BE QUOTED

* **THE REQUIREMENT IS MET AND THAT IS NOT A `worst-of-5` ARTEFACT**: the bar
  says *every draw*, and every draw clears it.  Scoring on a median or a best
  would have been choosing a statistic; nothing here needed to.
* ⚠ **ONE GREEN BUILD IS NOT CLOSURE AND TEN ARE NOT EITHER.**
  `standing_gates.md` §A governs: **the same tree has drawn 19.42 and 45.91
  MHz.**  What is established is that this RTL, this SDC and this tool close on
  **these ten draws at these five seeds**, twice, on two different days.
* ⚠ **THE MARGIN IS ~1 MHz.**  CONTROL's worst draw clears by **0.943 ns of
  setup**.  A downstream integrator on a different device, speed grade or
  target frequency has **no margin to spend**, and this document makes no claim
  about one.
* ⚠ **AND IT IS NOT SILICON.**  `CLAUDE.md`'s correctness target is SILICON
  MATCH.  Nothing here has been on a board (§8).

---

## §2 S-2 — **THE EXCEPTION IS GONE AND IT IS CHECKED, THREE WAYS, ON ALL TEN DRAWS.  MET.**

1. **`hdl/nec_test.sdc` carries ZERO uncommented `set_multicycle_path` and ZERO
   `set_false_path`**, anchored:
   `grep -cE '^[[:space:]]*set_(multicycle_path|false_path)'` = **0** (it was
   **2**, at `:193-194`, before edit (c)).  ⚠ **The unanchored
   `grep -c set_multicycle_path` reads 2 on the correctly-deleted file**, and
   both matches are `#`-prefixed lines at **`:237-238`**, inside the deletion
   banner's historical quotation under *"⚠ DO NOT RESTORE IT FROM `git show`"*.
   **The pre-registration named this instrument as the wrong one before the
   file was edited.**
2. **No *"CE multicycle"* `post_message`.**  The live line reads *"nec_test.sdc:
   NO ce->ce exception — N ce-gated v30u core registers are checked
   SINGLE-CYCLE"*.  The only *"CE multicycle"* text left in the file is inside
   the same commented banner.
3. **Every receipt's `core_domain` measures `SAME`, `INTO` and `OUTOF` at
   k = 1.0 against a nominal of 1.0, with `off_class` EMPTY, on 20 of 20
   readings across 10 of 10 draws.**  Edit (c) moves `nominal["SAME"]` 2.0 →
   1.0, so a draw still fitted to the exception would measure k = 2.0 and land
   in `off_class` — **the check that the deletion reached the compiler.**
   The per-class figures: `SAME` worst-of-5 **33.00** / med 33.93 / best 34.39;
   `INTO` 55.97 / 65.45 / 68.17; `OUTOF` 84.82 / 112.87 / 119.12 (CONTROL).
   **The whole-design Fmax EQUALS the core `SAME` figure on every draw** — the
   binding cone is inside the core, at k = 1.

⚠ **THE POLARITY IS WAVE 9's AND WAVE 13's, NOT WAVE 7's.**  WAVE 7 deleted the
exception temporarily and left the nominal at 2.0, so its proof was
`off_class == ['SAME']` at k = 1.0.  This is a landing, the nominal falls with
the constraint, and **a conforming draw reports EMPTY.**  *A reader comparing
`off_class` across waves without reading the nominal will draw the opposite
conclusion from the right data.*

---

## §3 S-3 — **PIN IDENTITY.  MET.  33 OF 37 SCORED LEGS IDENTICAL; ALL FOUR MOVERS REGISTERED IN ADVANCE.**

The **BEFORE** ladder ran on the unedited tree at `4a796cc754`, **before the
pre-registration was written and touching no `hdl/` file**; the **AFTER** ladder
on the landing `d3c295cdef`.  One driver, `sw/wave16_ladder.sh`, **UNEDITED** —
deliberately the same instrument that established ARM-A's equivalence at WAVE 16
— and compared by `sw/wave16_ladder_cmp.py`, which declares per leg which lines
are its scored content.

⚠ **THE COMPARATOR'S OWN POSITIVE CONTROL PASSES.**  `--selftest` perturbs one
character of `cc_all`'s scored line and the comparison must notice; it does
(`differing legs: ['ss_lint', 'phase_split_lint', 'cutset_lint', 'cc_all',
'demux_off']`, with `cc_all` present **only** under the selftest).
**Comparing raw log TEXT reports every leg as differing** — trap #10 — so the
raw logs are retained and the SCORED LINES are what is compared.

### 3.1 THE LADDER, LEG BY LEG

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
| `ulockstep --golden all --cases 50` | **17,350/17,350 ALL LOCKSTEP** | **IDENTICAL** (349 scored lines) |
| `ghost_launch_law score` | 200/200 = 100.0 % | IDENTICAL |
| `check_boot` / `check_boot 400` | 220 · 400 MATCH | IDENTICAL |
| `check_ab_sim` | 187 MATCH | IDENTICAL |
| `sm3_s16_score --core ucore` | **1,320/1,371**, census `{busstat_other 24, ARCH 27}` | **IDENTICAL** |
| `r7_lint` | **PASS** 0/0/0 | **PASS** 0/0/0 — IDENTICAL |
| `test_artifact` | **45/45** | IDENTICAL |
| `test_quartus_gate` | **287/287 PASS** | **287/287 PASS — IDENTICAL** (edit (c) replaces one check with one check) |
| `chainflat_relocation_check` | PASS, 9 arms, reconstruction exact | IDENTICAL |
| `ucrom_mif_check` | PASS, word for word | IDENTICAL |
| `chain_lfsr_gate` | PASS, `CHAIN_MAX` 7, depth [6], 0 overflows | **all 14 scored lines IDENTICAL** |
| **`fz2_replay`, 305 seeds** | AGREEMENT **301/305**, `first_bad` identical **101/101** | **305 × 11 IDENTICAL** |
| `ss_lint --core ucore` | PASS, 228 flops, 3 whitelist | **MOVED — §3.3, registered** |
| `phase_split_lint` | **exit 2, COULD NOT RUN** | **PASS 156 / 778 / 0** |
| `cutset_lint` | **exit 2, COULD NOT RUN** | **FAIL — X4, §4** |
| `demux_off_gate` | PASS, *"the three muxed ports are GONE"* | **PASS, *"the two"*** — §5 |

**`_rc.txt` is `diff`-identical on 37 of the 39 legs**; the two that move are
`phase_split_lint` (2 → 0) and `cutset_lint` (2 → 1), both of them legs that
**could not run at all** before the split existed.

The four `chain_lfsr` signatures, identical on both trees:
`1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78`,
**and every gap count and liveness row with them.**
⚠ **THAT IS ALSO 1.6 M CLOCKS OF THE SHADOW'S OWN `$fatal`**: the split asserts
`s1q !== s1_bus` at **every `ce`**, and across 4 × 400,000 fabric clocks plus
169,000 goldens at four divisors plus 17,350 `ulockstep` scenarios **it never
fired once.**

### 3.1a ⚠⚠ AN INSTRUMENT FINDING OF THIS WAVE'S OWN, CAUGHT BY THE COMPARATOR'S OWN POSITIVE CONTROL: **`wave16_ladder_cmp.py` READS `*.log` AND REPORTS A MISSING LOG AS *IDENTICAL***

Packaging the artifacts, I `gzip`ped the two ladder directories and re-ran the
comparison to store it.  It printed:

```
=== 37 legs: 37 IDENTICAL, 0 DIFFERING, 0 VACUOUS ===
SELFTEST: perturbing one scored line of cc_all was *** NOT DETECTED ***
```

**Every leg had become "IDENTICAL" because every leg's log was gone.**
`scored()` returns the single line `['*** MISSING LOG ***']` for an absent file,
two absent files compare equal, and **the `0 VACUOUS` counter does not count
that case** — so a comparison over ZERO real data reports a perfect score.

**IT WAS CAUGHT ONLY BECAUSE `--selftest` RUNS IN THE SAME INVOCATION AND SAID
IT COULD NOT SAY DIFFERENT.**  This is the campaign's own rule earning its keep
for the eleventh time: *assume the next instrument is also wrong until its
control says otherwise.*  The logs were restored, the comparison re-run on the
real bytes, and **the ladder directories are committed UNCOMPRESSED (340 K and
380 K) so the comparator stays runnable against them.**  The `§3.1` table and
every figure in it are from the restored run; **nothing in this document is
quoted from the vacuous one**, and its output is retained at the head of
`sw/testdata/wave17/s3_ladder_cmp.txt`'s history rather than hidden.

**BOOKED, NOT FIXED** (fixing a shared instrument mid-landing is how a result
gets chosen): `wave16_ladder_cmp.py` should count a MISSING LOG as VACUOUS and
exit non-zero, exactly as `wave15_fz2cmp.py` was made to do for a zero-row
population.

### 3.2 `fz2_replay` IS NON-VACUOUS, AND THAT WAS CHECKED FIRST

Trap #8: the tool is **structurally vacuous in a git worktree** —
`.gitignore:9` hides `sw/testdata/campaigns/*/captures/` and it runs GREEN over
**zero rows**.  Both legs here ran **in the main tree**, and
`sw/wave15_fz2cmp.py` prints the ROW COUNT before the verdict: **305 and 305**.
`tb_sys_receipt` **DIFFERS** (`8e616b9f24ed28a2…` → `fbb3e15ea1fb5f9f…`) and so
does `tb_sys_tree`, which is the control that the two legs ran **different
binaries** — a run in which they matched would be the vacuity.  The 11 fields
compared **by name**: `cid`, `fabric_bad`, `fabric_first`, `family`, `has_evt`,
`k`, `seed`, `sys`, `tier`, `wait_mode`, `win`.  **305 rows × 11 fields:
IDENTICAL.**  No digest computed here is quoted.

### 3.3 ⚠ `ss_lint`'s THIRD LINE MOVED AND MY OWN §5 PREDICTION WAS WRONG ABOUT IT

```
BEFORE: EU (v30u_eu.sv +19 includes): 137 architectural flops -> 134 SSA-mapped,
        3 whitelisted, 0 UNMAPPED; 3 sim-only exempt (349 comb/next-state regs skipped)
AFTER : EU (v30u_eu.sv +20 includes): 138 architectural flops -> 134 SSA-mapped,
        4 whitelisted, 0 UNMAPPED; 3 sim-only exempt (430 comb/next-state regs skipped)
```

The **registered** movers are there: **228 → 229** architectural flops and
**3 → 4** whitelist entries, which is S-4's *"grown by exactly `s1q`"*.
**Two numbers moved that the pre-registration did not name**: `+19 includes` →
`+20` (the new `v30u_eu_preload.svh`) and **`349` → `430` comb/next-state regs
skipped**.

> ⚠ **PRE-REGISTRATION §5 ITEM 1 SAID THE SKIPPED COUNT *"should NOT move
> here"*.  THAT PREDICTION IS WRONG AND IS RECORDED AS WRONG.**  Its reasoning
> was about ARM-A's two combinational temporaries (`pop_eff`, `q_cnt_np`) being
> already present on both sides — which is true — and it **failed to account for
> the cut set's own stage-1 combinational wires**, of which there are 81.  They
> are **not flops**: the census SKIPS them by declaration, the architectural
> count moved by exactly the one whitelisted shadow, and `0 UNMAPPED` holds on
> both blocks and both sides.

### 3.4 THE COMPOSITION PROOF, RE-TAKEN ON THE COMMITTED TREE

WAVE 15's ARM-A arm is reconstructible as `850ef46559` +
`sw/testdata/wave15/arm_presel.diff` (built in a scratch worktree, applies
cleanly).  At `d3c295cdef`:

> ### **ALL 127 TRACKED FILES OF `hdl/` ARE sha256-IDENTICAL TO IT, THE TRACKED FILE SETS ARE IDENTICAL, AND `diff -rq` OVER THE TWO `hdl/` TREES REPORTS ONLY GITIGNORED BUILD ARTEFACTS.**

`hdl/nec_test.sdc` is **`f0e1228ddd8f8a72…`**, the value WAVE 16 §5 recorded for
the no-exception SDC.  **The RTL and the SDC this wave landed are the same bytes
WAVE 15 drew 33.00 / 33.20 from** — which is why §6 reads the way it does.

---

## §4 S-7 — **`cutset_lint` FIRES X4 AND `phase_split_lint` PASSES.  BOTH AS REGISTERED.  NEITHER WAS TOUCHED.**

`sw/phase_split_lint.py`: **PASS — 156 members / 778 bits / 0 violations**,
`live-in-stage1: none`.

`sw/cutset_lint.py`: **FAIL — 80 members / 1 violation**, and the violation is
verbatim:

> `VIOLATION X4: the next-state block reads module-level COMBINATIONAL VALUE(S)
> DIRECTLY — a wire, or a `reg` driven by one of the module's other `always @*`
> blocks — so they are NOT in the cut set and stage 2 bypasses the shadow
> exactly as WAVE 2 did: **`['q_ripe_lead_n']`**`

with `s1w_ in block : 0`, `live-tainted members : none`, and `includes closed :
19`.

**IT NAMES ARM-A's MUX AND NOTHING ELSE.**  WAVE 15 §2.4 measured this firing
and explained it — **C1 does not create a bypass, it RELOCATES one that was
always there through the BIU port, where the lint could not see it**; on the
base tree `q_ripe_lead_n` is an input **PORT** and `cutset_lint` exempts ports,
but the value on that port is `f(q_pop)` and `q_pop` is stage-1 combinational
logic, so *stage 2 has been reading stage-1 logic through the BIU all along* —
which is precisely why this arc binds on 200 of 200 paths of the split tree.
WAVE 16 §2.3 and §10 item 4 wrote down **in advance** that it would fire here.

> **IT WAS NOT "FIXED".**  Choosing a lint outcome after seeing it is what this
> campaign refuses.  **The registered successor is ARM-B**, which passes
> `cutset_lint` (81 members / 0) at the cost of one declared flop and is worth
> ~1.2-1.5 MHz more (WAVE 15: 34.48 / 34.41).  It is §8 item 2, not this wave's.

⚠ **AND THE X4 FIRING IS NOT A COMPARISON.**  On the pre-edit tree BOTH lints
exit **2, COULD NOT RUN (the split is absent)** — so this is the one leg whose
BEFORE side is structurally absent, and its AFTER side is read against WAVE 15's
committed measurement, not against a before column.

---

## §5 S-4, S-5, S-6 — **SAVE STATE, DIVISOR INDEPENDENCE, THE INTERFACE CHANGE.  ALL MET.**

### 5.1 S-4 — SAVE STATE DID NOT MOVE

`ss_lint --core ucore` exits **0**.  `SS_VERSION` **0x8F** / `SS_COUNT` **232**
(1 + 109 BIU + 122 EU) / `SS_TAG` **0x8FE8** — **ALL UNCHANGED** — and
`hdl/rtl/ucore/v30u_ss_pkg.sv` is **untouched by every commit of this wave**
(`git diff 4a796cc754 HEAD -- hdl/rtl/ucore/v30u_ss_pkg.sv` is EMPTY).
**0 UNMAPPED on both blocks, both sides.**  The whitelist grows by **exactly
one entry**, **`s1q`**, on the **DERIVED** class beside `dec_q`, naming the
place the derivation is checkable by eye (the pack/unpack pair in `THE CUT`) and
with the derivation **`$fatal`-asserted at every `ce` rather than assumed** —
1.6 M `chain_lfsr` clocks and every golden case, never fired.

⚠ **THE FLOP FIGURES ARE THE SPLIT TREE's AND MAY NOT BE DIFFERENCED AGAINST
THE UNSPLIT ONES.**  This tree reads **229 flops / 4 whitelist**; WAVE 16's
unsplit tree read **228 / 3**.  Both are right.

⚠ **`standing_gates.md`'s `ss_lint` ROW IS STALE AND IS NOT TREATED AS A
FAILURE.**  `standing_gates.md:1399` registers **226 addresses / 214 flops /
`SS_VERSION` 0x8D / `SS_TAG` 0x8DE2**; this tree measures **232 / 229 / 0x8F /
0x8FE8**.  The row is behind by the wave-5/6/7 landings and was known stale at
WAVE 13, WAVE 15 and WAVE 16.  **Measured, reported, unmoved by this wave** —
`standing_gates.md` and `CLAUDE.md` are not edited here (the WAVE 11-16
precedent; the coordinator decides).

### 5.2 S-5 — DIVISOR INDEPENDENCE.  **A CORRECTNESS BAR HERE, NOT A FORMALITY.**

**169,000 / 169,000 at `--ce-div` 2, 3, 4 AND 8**; `--ce-div 1` **REFUSED**,
clause cited, exit 2 — all four identical to the BEFORE side.

The split makes the ce/ce_half contract's **S-1** clause (*at least one
`ce_half` falls between consecutive `ce`s*) load-bearing for the EU: **without
it stage 2 consumes a STALE stage 1 and the core computes the wrong next
state.**  Edit (a) is what lets `v30_core.sv`'s `$fatal` say so, in every
configuration, and its message now names the EU as well as the BIU's T1
turnaround.

### 5.3 S-6 — `demux_off_gate` PASSES, AND ITS ONE MOVING WORD IS EDIT (a)'s POINT

**PASS** — *"the de-muxed core builds and runs, **the two** muxed ports are
GONE, and the define is what removes them."*  It said *"the three"* before.
Registered in the pre-registration §2.2 and in WAVE 9 §2.3 / WAVE 13 §5.2.1:
splicing `.CE_HALF` into a define-off build now **SUCCEEDS**, because `CE_HALF`
is an unconditional port, and **asserting that it fails would be asserting
something false**.  Its `AD` and `AD_OE` splice clauses still **REFUSE naming
their pins**, which is what keeps the leg non-vacuous.

⚠ **THIS IS AN INTERFACE CHANGE AND IT IS SURFACED, NOT HIDDEN.**  A de-muxed
downstream integrator that did not connect `CE_HALF` **will fail to elaborate.**
That is the intended consequence; it is why the edit has been built and reverted
three times (WAVE 4, WAVE 9, WAVE 13); and it is now in the tree.

---

## §6 ⚠⚠ THE FREE CONTROL NOBODY REGISTERED: **THE LANDING REPRODUCES WAVE 15 TO THE BITSTREAM, ON TEN OF TEN DRAWS**

Because §3.4 proves the inputs identical, the ten fits are a **like-for-like
re-run of WAVE 15's presel column four days later, in a different tree, by a
different driver.**  Compared field by field by name against the committed
`sw/testdata/g6dist/w15-presel-{control,retention}-n5/`:

| quantity | result |
|---|---|
| `input_manifest` | **`c3305d40f62e497f…` / 99 files — IDENTICAL, both configurations** |
| distribution scalars (`fmax`, `worst_setup_ns`, `alms`, `worst_of_n`, `verdict`, `n_seeds`, `input_manifest`, `bars`, `by_class`, `binding_class_flips`, `paired`) | **11 of 11 IDENTICAL, both configurations** |
| per-seed field names | **13 of 15 IDENTICAL on all 5 seeds of both configurations** (65 of 75 comparisons) — `alms`, `configuration`, `core_domain`, `core_fmax_mhz`, `fmax_mhz`, `seed`, `seed_echo`, `seed_honoured`, `tns_violations`, `truefmax`, `truefmax_full`, `verdict`, `worst_setup_ns` |
| the two that differ | `receipt_id` (an identity field, **required** to differ) and `outputs`, in which **only `nec_test_ucore.fit.summary` and `nec_test_ucore.sof` move** — both embed a project path and a compile timestamp |
| **`nec_test_ucore.rbf` sha256** | ⚠⚠ **BYTE-IDENTICAL ON 10 OF 10 DRAWS.**  CONTROL `853eda3050f08b2f` · `45e2e10111b571ef` · `aaf256f16390c63d` · `9c82ddbfbc3cc3f1` · `d194050f783c70fa`; RETENTION `20fac47ef98e00fa` · `a4b1613fe9aa540b` · `4ff753fc95f81c33` · `63ea9426026aacbd` · `c1e36e046dd1fe68` |
| per-entity `dedicated_logic_registers` and `combinational_aluts` | **10 of 10 draws IDENTICAL** — `v30u_biu` **434** regs / **1,151** ALUTs (CONTROL), `v30u_eu` **1,326** regs / **5,075** ALUTs; RETENTION 1,138 / 5,044 |

> ### **THIS IS THE STRONGEST CROSS-WAVE REPRODUCTION THIS CAMPAIGN HAS RECORDED.  WAVE 16 §5.1 reproduced WAVE 13 *"identical to the thousandth"* on Fmax; this reproduces the BITSTREAM PAYLOAD.**

**It is also the answer to the one thing §1.4 of the pre-registration worried
about.**  The brief warned that a changed driver and a changed tree path are
exactly the unlabelled-variable class campaign **law 4** was paid for.
**Measured: on identical inputs they are worth 0.000 ns** — and that is only
sayable because WAVE 12 removed `build_id.v` and bar **E11** refuses its return.

⚠ **WHAT THIS DOES *NOT* SAY.**  It says nothing about the distribution's width
at other seeds, on another device, or after any RTL change.  A byte-identical
`.rbf` from byte-identical inputs is **the compiler being deterministic**, which
is a property of the tool, not evidence about the design.  `standing_gates.md`
§A still governs.

### 6.1 AREA, AND THE SHRINKING NOBODY HAS EXPLAINED

The split adds **778 bits of flop** and the fitted design is **8,193-8,275 ALMs
(20 %)** against WAVE 16's unsplit no-exception column at 24-29 % in the
campaign's earlier waves and WAVE 13's split at 8,006-8,030.  **The design does
not get bigger.**  WAVE 4 §3.2, WAVE 9 §3 and WAVE 13 §2.4 each recorded the
same shape.  ⚠ **REPORTED, NOT CONCLUDED** — A&S combinational counts are not
reproducible run to run (`ucore_provenance.md` §74.4a), and pre-registration §5
item 4 asked for exactly this and gets no explanation from this wave either.

---

## §7 S-8, S-9, S-10 — **E11, THE OPTIONAL CONTROL, AND THE REVERT THAT DID NOT FIRE**

**S-8 — `E11` TRUE ON EVERY DRAW.  MET.**  `E11_no_build_stamp` reads
**`pass` on BOTH distribution receipts and all TEN per-seed receipts**:
`files_scanned` **99**, `file_present` **False**, `token_hits` **{}**.  ⚠ Read
at **DISTRIBUTION level** as `E11_no_build_stamp`, not from each seed's `bars`
(trap #9) — and the per-seed receipts were read **from inside this tree**, so
WAVE 15's and WAVE 16's relative-path trap did not arise.

**S-9 — THE WITH-EXCEPTION PAIR WAS NOT TAKEN.**  S-9 says it *"is not
required"*.  It was **not run**, so **no figure is quoted against WAVE 16's
CONTROL 41.42 / RETENTION 41.55**, and none may be inferred: the with-exception
build of this tree **has not been compiled by anybody**.  Stated as an absence,
because absence must not read as data.

**S-10 — THE REVERT CONDITION.  NOT FIRED.**

* **S-1 PASSED** on every draw of both configurations.
* **No leg of S-3 moved** except the four registered movers, of which one is
  S-4's own bar, two are lints that could not previously run, and one is
  edit (a)'s registered consequence.
* **S-4, S-5, S-6 all MET.**

> **THE LANDING STANDS AT `d3c295cdef`.  NO BAR WAS SOFTENED, NOTHING WAS
> RE-SCOPED AFTER A RESULT, AND NO STATISTIC WAS CHOSEN AFTER SEEING ONE.**

### 7.1 THE BARS, SCORED

| bar | verdict |
|---|---|
| **S-1** the requirement — E1-E5 on EVERY draw, BOTH configurations, no exception | ⭐ **MET.**  CONTROL `worst-of-5` **33.00** (5/5 PASS, margin +1.00), RETENTION **33.20** (5/5 PASS, margin +1.20).  10 of 10 receipts PASS, 5 bars each, **zero failing bars**; TNS 0.000 setup AND hold, all four domains, all ten draws; 0 errors / 0 latches / 0 `lpm_divide`.  §1 |
| **S-2** the exception is GONE and CHECKED | **MET**, three ways — anchored grep **0**, no *"CE multicycle"* info line, and **k = 1.0 with `off_class` EMPTY on 20 of 20 class readings across 10 of 10 draws.**  §2 |
| **S-3** pin identity, BEFORE side first | **MET.**  **33 of 37 scored legs IDENTICAL**, `_rc.txt` identical on 37 of 39; four `chain_lfsr` signatures **BYTE-IDENTICAL**; `fz2_replay` **305 × 11 IDENTICAL by name** over a non-zero population; the comparator's positive control PASSES.  All four movers registered in advance.  ⚠ One unregistered sub-line moved and **my §5 prediction about it was wrong** (§3.3).  §3 |
| **S-4** save state | **MET.**  `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 **UNCHANGED**, `v30u_ss_pkg.sv` untouched, 0 UNMAPPED, whitelist **3 → 4** grown by **exactly `s1q`**, derivation `$fatal`-asserted and never fired.  §5.1 |
| **S-5** divisor independence | **MET.**  169,000/169,000 at div 2, 3, 4 and 8; div 1 REFUSED.  §5.2 |
| **S-6** `demux_off_gate` | **MET — PASS**, with its registered *"three"* → *"two"* line and its `AD`/`AD_OE` clauses still refusing by pin name.  §5.3 |
| **S-7** `cutset_lint` X4 expected, `phase_split_lint` PASS | **AS REGISTERED.**  `phase_split_lint` **PASS 156 / 778 / 0**; `cutset_lint` **FAIL — X4 naming `q_ripe_lead_n` and nothing else.**  **NOT TOUCHED.**  §4 |
| **S-8** `E11` on every draw | **MET.**  2 distributions + 10 per-seed receipts, 99 files scanned, 0 hits.  §7 |
| **S-9** the with-exception pair | **NOT TAKEN** (registered as optional).  No figure quoted, none inferable.  §7 |
| **S-10** the revert condition | **NOT FIRED.  The landing stands.**  §7 |

---

## §8 WHAT IS OWED

1. ⚠⚠ **THE FABRIC CONFIRMATION, AND IT IS NOW FOUR STRUCTURAL CHANGES DEEP.**
   WAVE 7's chain flattening, WAVE 12's `build_id.v` removal, WAVE 16's ARM-A,
   and **now the phase split, which changes the EU's CLOCKING and promotes a
   core port.**  `CLAUDE.md`'s correctness target is **SILICON MATCH**, and
   **nothing in this campaign has been on a board since FLASH #21.**
   **NO FABRIC FIGURE TAKEN ON FLASH #21 OR EARLIER MAY BE QUOTED AGAINST THIS
   TREE.**  Nothing was flashed here.  **This is the largest debt in the
   campaign and it grew again — and it is now the only thing between the
   requirement being MET IN SIMULATION and being MET.**
2. **ARM-B REMAINS OPEN AND IS NOW THE ONLY KNOWN MARGIN.**  WAVE 15 measured
   it at **34.48 / 34.41** against this landing's 33.00 / 33.20, it **passes
   `cutset_lint`** (closing §4's X4 on its own terms rather than by editing a
   lint), and it costs **one declared flop**.  It is ARM-A plus the select off
   the `s1q` shadow — **a one-hunk change on top of what is now in the tree**,
   and the shadow it needs is now landed.  ⚠ Its figures are WAVE 15's and must
   be re-measured on this tree, which §6 suggests will be cheap and exact.
3. **`standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS WAVE** (the
   WAVE 11-16 precedent; the coordinator decides).  Now unregistered, and the
   list has grown: bar **E11**; `test_quartus_gate` **287/287**; the stale
   `ss_lint` row against this tree's **232 / 229 / 4 / 0x8F / 0x8FE8**;
   **`CE_HALF` as an unconditional core port** (an interface change a downstream
   integrator must know about); **`demux_off_gate`'s "two muxed ports"**; the
   **`s1q` whitelist entry**; `phase_split_lint` and `cutset_lint` as legs that
   now RUN; **and this landing itself, with `nec_test.sdc` carrying no timing
   exception for the first time.**
4. ⚠ **`cutset_lint` IS RED IN THE TREE AS OF THIS COMMIT**, by design and with
   §4's reason.  It must not be read as a routine failing gate: either ARM-B
   lands and it goes green on its own terms, or the invariant's scope is
   deliberately re-registered.  **Whichever, it is a decision and not a
   repair.**  Written down so it cannot be mistaken later.
5. ⚠ **`fz2_replay` IS STILL VACUOUS IN A GIT WORKTREE AND STILL EXITS 0.**
   This wave avoided it by running the leg in the main tree.  The permanent fix
   belongs in `fz2_replay.py` — refuse a zero-row population — and is **BOOKED
   for the third time.**
6. **`check_core --ss-sweep` IS STILL ON NO REGISTERED LADDER** — booked by
   WAVES 2, 3, 4, 9, 13, 14, 15, 16.  **Booked for the ninth time.**  It is the
   one place the shadow's derivation is not covered by the runtime assert, which
   excludes `ss_we` by construction, and the shadow is now LANDED — so the
   repetition has stopped being cheap.
7. **WAVE 11's one-fit repair** (re-derive WAVE 9's `+15.188 ns` cutting
   constant against a same-stamp arc) and the **±1 whole-design register wobble
   outside `v30_core`** are inherited and untouched.
8. ⚠ **`sta_biu_roundtrip.tcl`'s `q_ripe_lead_n` counter is confounded in the
   tree** (WAVE 16 §10 item 5) and **`sta_chain_anatomy.tcl` cuts on
   `st_zero_ok` pins the WAVE 7 fold deleted.**  Any future STA anatomy of this
   tree needs an instrument chosen **before** a result is seen.
9. ⚠ **`wave16_ladder_cmp.py` REPORTS A MISSING LOG AS `IDENTICAL` AND NOT AS
   VACUOUS** (§3.1a).  One clause would make an absent log count as VACUOUS and
   exit non-zero.  **BOOKED, NOT FIXED** — a shared instrument is not edited in
   the middle of the landing it is scoring.
10. **`sw/testdata/receipts/*.jsonl` IS DELIBERATELY LEFT UNCOMMITTED** — §9.

---

## §9 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
* No Codex.  No nested subagent.
* **THE WAITS BLOCKED; THEY DID NOT POLL A TURN.**  One `until ! pgrep -x …`
  guard per Quartus stage, and **both sweeps were launched by ONE wrapper** that
  ran them strictly sequentially, so no two Quartus stages could race and
  neither sweep needed a turn of its own.
* Single-writer guard by **`pgrep -x`, EXACT BINARY NAME, ONE PATTERN PER
  CALL**; ⚠ `pgrep -f <script>` self-matches and was never used.
* Drivers carry **`set -u`, NEVER `set -e`** — `quartus_gate` exits non-zero on
  RED and a RED verdict is a RESULT.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  `hdl/nec_test_ucore.qsf` was restored by `git checkout -- <that exact path>`
  around every Quartus run and measured clean after both sweeps.  **`git add` BY
  EXPLICIT PATH ONLY** on every commit.
* ⚠ **AND WAVE 16's OWN §12.1 MISS WAS NOT REPEATED.**  The **20 pre-existing
  modified files that are the user's own uncommitted work are UNTOUCHED**,
  verified at the end.  **`sw/testdata/receipts/verilator_binary.jsonl`,
  `quartus_bitstream.jsonl` and `quartus_distribution.jsonl` are NOT COMMITTED**
  — this wave's rows stay in the working tree — because committing an
  append-only ledger the wave writes to sweeps whatever was already dirty in it.
  **Nothing is lost by that choice**: every receipt is committed in full, BY
  VALUE, under `sw/testdata/g6dist/w17-*/` (`distribution.json` plus
  `seed{1..5}_quartus_gate.json`, `seed{1..5}.sta.summary` and
  `seed{1..5}.truefmax.txt` for both sweeps), and §1 quotes their ids from
  there.
* **THIS WAVE ADDED NO `hdl/*.log`** — checked against the directory, not
  recall: `ls hdl/*.log` is **15 files**, **14 are the pre-existing untracked
  `quartus_gate_*.log`** with their original dates (Aug 11 … Sep 12) and the
  15th is the gitignored `hdl/quartus_gate_build.log` dated Aug 20.  Both
  Quartus transcripts of this wave went to `--log` under
  `sw/testdata/wave17/w17-split-presel-noexc/`.
* `~/.cache/ucsimt-tmp/` for every intermediate; **nothing in `/tmp`.**
* ⚠ **CONTENT COMPARED, NOT A DIGEST COMPUTED HERE**: the ladder leg by leg on
  scored lines queried by name, `chain_lfsr` row for row, `fz2_replay` field by
  field, and the cross-wave reproduction by NAMED FIELD with the row count
  printed first.  *A number with no artifact id is not quotable.*
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL, REPORTED FIRST**: the ladder
  comparator's `--selftest` fires in the same run as its verdict;
  **`sw/wave13_score.py` was pointed at WAVE 15's COMMITTED presel
  distributions BEFORE it was pointed at anything new, and reproduced their
  published 33.00 / 33.20 exactly**; `fz2_replay`'s row count and its
  **differing** `tb_sys_receipt`; and §6's whole reproduction column.
  ⚠ **ONE OF THEM FIRED AND WAS OBEYED** — §3.1a, where the ladder
  comparator scored 37 of 37 IDENTICAL over no data at all and its own
  `--selftest` is the only reason this document does not quote it.
* **A CENSUS DOES NOT SIZE A CANDIDATE IN EITHER DIRECTION.**  No census is
  offered or quoted here.
* **Record what was measured, not what was expected** — §3.3 records a
  prediction of mine that was wrong, and §6 records a control nobody registered
  that turned out to be the wave's second result.

---

## §10 THE CAMPAIGN'S SCOREBOARD, CLOSED

Bar: **Fmax ≥ 32.0 MHz on every draw, both configurations, with no exception.**
All figures `worst-of-5@seeds{1..5}`, stamp-free (`E11`), one driver per wave.

| tree | CONTROL | RETENTION | |
|---|---:|---:|---|
| unsplit, no exception (W13, reproduced exactly by W16) | 27.78 | 27.01 | RED |
| unsplit + ARM-A (W16) | 26.75 | 27.33 | RED — **ARM-A alone COSTS 1.03 MHz** |
| split only (W13) | 30.53 | 31.15 | RED (0/5, 3/5) |
| **split + ARM-A — THIS LANDING** | **33.00** | **33.20** | ⭐ **PASS 5/5 and 5/5** |
| split + ARM-B (W15, not landed) | 34.48 | 34.41 | open, §8 item 2 |

> ### **WAVE 16's R-3 SAID ARM-A ALONE WAS WORTH −1.256 ns AND WOULD ONLY PAY WITH THE CUT.  IT PAID.  THE TWO-LANDING PLAN WAS A REQUIREMENT, NOT A CONVENIENCE, AND IT IS COMPLETE.**

And the campaign's own laws held: **law 5** (*a candidate's value is not a
property of the candidate*) is what predicted the sign flip; **law 4** (*an
unlabelled variable can be bigger than the one you are characterising*) is what
made §6's zero-delta measurable at all; and **the measure-first waves produced
every landing this campaign has** — this one included, because WAVE 13 measured
the split, WAVE 14 sized the round trip, WAVE 15 found the mechanism, and
WAVE 16 sized it on the tree that did not want it.

**What remains is silicon.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
