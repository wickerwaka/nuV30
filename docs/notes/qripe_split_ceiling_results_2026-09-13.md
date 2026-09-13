# WAVE 14 — **THE ROUND TRIP IS WORTH `6.29 ns` (CONTROL) AND `4.69` (RETENTION) ON THE SPLIT TREE, AND THE GAP IS `1.51` AND `0.86`.  A MECHANISM WORTH A QUARTER OF THE CEILING FINISHES THE CAMPAIGN.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/qripe_split_ceiling_prereg_2026-09-13.md`, committed
at **`fff90bd829` BEFORE THE FIRST `hdl/` EDIT OF ANY TREE AND BEFORE THE FIRST
QUARTUS STAGE.**  Its bars **P-1 … P-7 are scored below and not one was
softened, re-derived or re-scoped after a result was seen.**

**MEASUREMENT ONLY.  NOTHING IS LANDED.  OFFLINE ONLY — NO BOARD, NO FLASH,
NOTHING PROGRAMMED.**  No Codex.  No nested subagent.
`git status --porcelain hdl/` carried **0 tracked modifications at the start and
carries 0 at the end**; the main tree's `hdl/` was **never written at all**.

| | |
|---|---|
| **Base commit of every arm** | `850ef46559` — WAVE 13's SPLIT tree |
| **The arms** | `~/.cache/ucsimt-tmp/wave14/wt_{base,qripe_tie,qripe_hold}`, scratch git worktrees, all removed at the end |
| **The distributions** | `sw/testdata/g6dist/w14-{base,tie,hold}-{control,retention}-n5/` |
| **The STA anatomy and logs** | `sw/testdata/wave14/w14-{base,tie,hold}/`, `sw/testdata/wave14/logs/` |
| **Tool** | Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` **31.250 ns**; Verilator 5.032 |
| **Cost** | 6 sweeps · 30 fits · 6 maps · 4 h 49 m wall |

---

## §0 THE HEADLINE, IN FIVE SENTENCES

> **1. THE CEILING IS BIG, AND IT IS THE FIRST TIME A NAMED MECHANISM HAS BEEN
> LARGER THAN THE REMAINING GAP.**  Paired A/B over five seeds, both
> configurations, one driver, one seed set: severing the round trip is worth
> **+6.293 ns (CONTROL, 95 % CI [+5.808, +6.779], t = 36.0)** and **+4.688 ns
> (RETENTION, [+3.933, +5.444], t = 17.2)** of `ce → ce` arc.  **THE GAP IS
> 1.506 ns AND 0.855 ns.**
>
> **2. WAVE 10's CUT-TREE READING WAS RIGHT AND ITS OWN CAVEAT AGAINST IT IS
> REFUTED.**  It measured **+6.629 ns** with an arm that added a REGISTER and
> disowned the figure because the arm might have subdivided STAGE 2.  **An arm
> that adds NO REGISTER AT ALL reproduces it (+6.29 / +6.40 on CONTROL).**  The
> ~4 MHz disagreement between WAVE 10 §5.3's two readings is **settled in favour
> of the larger one.**
>
> **3. THE TWO ARMS AGREE, WHICH RETIRES THE PRUNING WORRY EMPIRICALLY.**
> `qripe_tie` (a constant, which lets the compiler fold the consumers) and
> `qripe_hold` (the same function off registers that already exist, which folds
> nothing) differ by **0.108 ns on CONTROL and 0.035 ns on RETENTION** — far
> inside either interval.  ⚠ And **neither arm made the design smaller**: the
> core's combinational ALUTs went **UP**, 6,689 → 7,090 / 6,931.
>
> **4. THE CENSUS UNDERSTATED IT — THE FIRST TIME IN THIS CAMPAIGN.**  WAVE 9's
> census said **2.786 ns**; this wave's own census on its own base netlists says
> **2.149 / 2.562**.  The measured difference is **2.3× and 1.7× LARGER** than
> the census figure.  WAVE 8 measured **5.9× over** on `ucrom` and WAVE 10
> **5.3× over** on this same mechanism on the UNSPLIT tree.  **The standing law
> survives and is sharpened: a census ranks candidates and does not size them —
> IN EITHER DIRECTION.**
>
> **5. THE ENDGAME: A REAL MECHANISM NEED RECOVER ONLY 24 % (CONTROL) OR 18 %
> (RETENTION) OF THIS CEILING TO CLEAR 32.0 MHz.**  Both probe arms clear it on
> **20 of 20 draws**, worst single draw **36.45 MHz**.  ⚠ **NEITHER ARM IS A
> DESIGN AND NEITHER IS PROPOSED AS ONE.**

---

## §1 P-1 — **THE POSITIVE CONTROLS.  REPORTED FIRST.  ALL PASS.**

### 1.1 THE SCORER, BEFORE IT SAW ANY NEW DATA

`sw/wave14_ceiling.py --selftest` reproduces WAVE 13's **committed**
`w13-split-noexc-*` distributions from their bytes: worst-of-5 **30.53** and
**31.15**, draws and spreads exact.  **It also earned its keep before the wave
ran**: it reported `fit_registers` **VARYING 6,689 / 6,713 / 6,729 / 6,732 /
6,740 across the five seeds of one sweep** — physical synthesis duplicates
registers — so **the FITTER count cannot be P-3's test**, and `map_registers`
plus the per-entity `ucore_hierarchy` counts, which are CONSTANT across all five
draws, are the columns P-3 is read from.  *That was learned from a control
before any new data existed, which is what a control is for.*

### 1.2 THE STA CONTROLS, ON ALL SIX LEGS

`sw/sta_biu_roundtrip.tcl` (WAVE 10's, unedited) ran on the netlist every sweep
left behind.  **`=== CONTROLS: ALL PASS ===` and `AX CONTROLS: ALL PASS` on 6 of
6 legs:**

| leg | PC-W1 `get_pins`→paths / `get_nodes`→paths | PC-W2 single pin | PC-W4 **bulk (known-wrong)** |
|---|---|---:|---:|
| base / control | 1→1 / 1→**0** | 8 | 1,216 pins → **6** |
| base / retention | 1→1 / 1→**0** | 8 | 1,290 → **8** |
| tie / control | 1→1 / 1→**0** | 21 | 2,031 → **23** |
| tie / retention | 1→1 / 1→**0** | 20 | 1,913 → **14** |
| hold / control | 1→1 / 1→**0** | 11 | 2,049 → **15** |
| hold / retention | 1→1 / 1→**0** | 10 | 1,854 → **13** |

**PC-W1 fires live on every leg** — the same name as `get_pins` returns a path
and as `get_nodes` returns none (WAVE 1 §0.2).  **PC-W4, the bulk `-through`, is
BELOW the single-pin figure on 2 of 6 legs** (6 against 8 on base/control, 14
against 20 on tie/retention), EQUAL on 1 and above on 3 — the
accepted-and-ignored trap, caught again, printed and **relied on nowhere.**
Every `-through` in this wave is ONE PIN AT A TIME.  PC-W5a answered through `get_registers` and
PC-W5b exercised **both** write-pin forms (`|d` on `ind[0]`, `|asdata` on
`upc_page[0]`), and all four pin forms on the binding destination read **0**,
which is the **M10K port register** finding, reproduced.

### 1.3 ⚠⚠ **A CONTROL THAT WAS MISSING WAS BUILT, AND IT REFUTED THIS WAVE'S OWN FIRST SUSPICION**

`sta_cutset_diag.tcl`'s **STAGE rows had no working positive control** — its own
*"-through the destination's own D pin"* clause reads **0 pins on all six legs**
(the M10K port register again).  And its STAGE rows on the ARM netlists looked
wrong: *"STAGE 1 (anything → s1q), worst … to : …|u_eu|v1~24_OTERM7145"* — a
destination whose printed name does not contain `s1q`.  On hold/retention STAGE
1, STAGE 2 and the global worst were **the same path.**  The obvious reading was
that `-to <collection>` had been **silently ignored**, the WAVE 1 §0.2 family.

**IT WAS NOT.**  `sw/sta_wave14_shadow_pc.tcl`, written for this and run on all
three arms' netlists:

| clause | base | tie | hold |
|---|---|---|---|
| **PC-S2** force `-to` ONE register **by NODE OBJECT** (no name to spell) — the returned destination must be that register | **PASS** | **PASS** | **PASS** |
| **PC-S3** free query, destinations tested by **COLLECTION MEMBERSHIP**, never by eyeballing a string | **5 of 5 IN** | **5 of 5 IN** | **5 of 5 IN** |
| **PC-S4** the same query as `get_nodes` (known-wrong) | 5,067 nodes → **0 paths** | 5,191 → **0** | 5,171 → **0** |

> ### **THE FINDING: A PHYSICAL-SYNTHESIS DUPLICATE OF AN `s1q` SHADOW REGISTER IS *REPORTED* UNDER A NAME THAT NO LONGER CONTAINS `s1q` — IT IS NAMED AFTER ITS FANOUT NET (`psw_n~13_OTERM7509`, `v1~22_OTERM5576`) — WHILE `get_registers {*s1q*}` STILL MATCHES IT.  `-to` WAS HONOURED THE WHOLE TIME.**
>
> **CONSEQUENCE, AND IT IS A REAL DEFECT IN A COMMITTED INSTRUMENT**:
> `sta_cutset_diag.tcl`'s **C-8 classification and its `of which name |s1q`
> counter test the NAME STRING**, so on a netlist where the fitter has renamed
> shadow duplicates they **UNDER-REPORT**.  On this wave's arms they print
> `STAGE 1 / STAGE 2 / NEITHER = 0 / 0 / 200` while the worst path on
> hold/retention is provably **shadow → shadow**.  **The `-from`/`-to` STAGE
> rows are sound; the string-matched classification is not.**  Booked; nothing
> in this wave's verdict rests on the string counter.
>
> ⚠ This is the fourth time this campaign has caught a confident instrument, and
> the third *different* failure mode of the same Quartus name/collection
> boundary.  **It was caught by building the control that was missing, not by
> trusting the row.**

### 1.4 P-2's CONTROL, WHICH IS THE STRONGEST ONE AVAILABLE

**The BASE arm reproduces WAVE 13's SPLIT arm on 10 of 10 draws, EXACTLY.**
Different worktree, different day, different driver, same seed set:

| | seed 1 | 2 | 3 | 4 | 5 | worst-of-5 |
|---|---|---|---|---|---|---|
| **CONTROL** W13 / **W14** | 31.11 / **31.11** | 30.53 / **30.53** | 30.85 / **30.85** | 30.98 / **30.98** | 30.62 / **30.62** | **30.53 both** |
| **RETENTION** W13 / **W14** | 32.43 / **32.43** | 32.75 / **32.75** | 31.15 / **31.15** | 32.53 / **32.53** | 31.82 / **31.82** | **31.15 both** |

**Worst setup slack and ALM count are identical on all ten as well** (e.g.
CONTROL seed 2 `−1.506 ns / 8,024 ALMs` on both), and the `input_manifest` is
the same 99-file `d4ecdeff14444248…`.  **Post-WAVE-12 this pipeline is
reproducible to the thousandth of a nanosecond across days and worktrees** —
which is what WAVE 12 was for, and it is quoted here as a CONTROL, not as a
claim about PC-C0.

---

## §2 P-2 — **THE PROBE SEVERS THE PATH.  `check_core` FAILS ON BOTH ARMS, AND THAT IS THE EVIDENCE.**  **MET.**

`python3 sw/check_core.py --core ucore --opcodes all --cases 0`, run in each
arm's own worktree on that arm's own freshly built, **separately receipted**
Verilator binary:

| arm | receipt | TOTAL | exit | |
|---|---|---|---|---|
| **BASE** (the control) | `9814d2f215757bb1…` | **169,000 / 169,000** | 0 | **PASSES — the instrument works on the unprobed split tree** |
| **ARM-T `qripe_tie`** | `d45351ad4fce7a11…` | **168,819 / 169,000** (cycles), 168,973 arch | **1** | **FAILS as required** |
| **ARM-H `qripe_hold`** | `8dac93933cd89108…` | **168,819 / 169,000** (cycles), 168,973 arch | **1** | **FAILS as required** |

**181 cases fail on each arm, and it is the SAME count WAVE 10's `qripe_reg`
produced.**  *A probe that still passes has not cut anything.*

**AND THE STA AGREES INDEPENDENTLY.**  `q_ripe_lead_n` **BY NAME** on the
binding populations:

| | POP-A (top 200) | POP-B (400, `-nworst 1`) |
|---|---:|---:|
| base / control | **200 of 200** | 381 of 400 |
| base / retention | **200 of 200** | 364 of 400 |
| **tie / control** | **0** | **0** |
| **tie / retention** | **0** | **0** |
| **hold / control** | **0** | **0** |
| **hold / retention** | **0** | **0** |

**On the base tree the mechanism is on every path of the binding class; on both
arms it is on none.**

⚠⚠ **BOTH ARMS ARE BEHAVIOUR-BREAKING BY CONSTRUCTION.  NO EQUIVALENCE IS
CLAIMED FOR EITHER.  NEITHER IS PROPOSED AS A DESIGN.  NEITHER IS LANDED.**
ARM-T hands the EU a constant; ARM-H hands it **last clock's** level where the
F7 contract promises the **next** one.

---

## §3 P-3 — **NO REGISTER WAS ADDED, SO NO STAGE COULD BE SUBDIVIDED.  THIS IS WHAT SEPARATES THIS WAVE FROM WAVE 10's OVER-ANSWER.**  **MET.**

### 3.1 THE STRUCTURAL ARGUMENT, WHICH IS ONE SENTENCE

> **A PIPELINE STAGE BOUNDARY *IS* A REGISTER.  NEITHER ARM ADDS ONE.  THEREFORE
> NEITHER ARM CAN HAVE SUBDIVIDED A STAGE.**

WAVE 10's cut-tree arm added a flop and its arc fell **below** the two-stage
ceiling, which is why it disowned its own +6.629 ns.  There is no such
possibility here, and it is demonstrated four independent ways.

### 3.2 (a) AT THE SOURCE, BEFORE A FIT WAS SPENT

`sw/wave14_arms.py` refuses any arm whose diff adds a line carrying a
non-blocking assignment.  **ARM-T: 5 added lines, 0 with `<=`.  ARM-H: 13 added
lines, 0 with `<=`.**  Both edits are `assign`/`wire` only, both in
`hdl/rtl/ucore/v30u_biu.sv`, and **nothing else in either tree is touched.**

### 3.3 (b) IN THE RTL FLOP CENSUS — **NOT ONE FLOP MOVED**

`python3 sw/ss_lint.py --core ucore`, exit **0** on all three arms, **byte-for-byte
the same census**:

> `SS_VERSION` **0x8F** / `SS_COUNT` **232** (109×2 BIU + 122×2 EU + tag) /
> `SS_TAG` **0x8FE8**; BIU **91** architectural flops → 91 SSA-mapped, 0
> UNMAPPED; EU **138** → 134 mapped + 4 whitelisted, 0 UNMAPPED;
> `ss_flopcensus` **229 architectural flops** — **IDENTICAL ON ALL THREE ARMS.**

⚠ **WAVE 10's `qripe_reg` COULD NOT HAVE PASSED THIS** — its own results
document records that it would break `ss_lint` by adding a flop with no
save-state address, and it was never run.  Beside it, `r7_lint` **PASS**,
`phase_split_lint` **PASS (156 members / 778 bits / 0 violations)** and
`cutset_lint` **PASS (80 members / 0 violations)** on all three arms.

### 3.4 (c) IN THE COMPILER'S OWN COUNTS — **`v30_core` IS 1,760 REGISTERS ON ALL SIX SWEEPS**

| sweep | whole-design A&S regs | **`v30_core` total regs** | `v30u_biu` own | `v30u_eu` own | `v30_core` ALUTs |
|---|---:|---:|---:|---:|---:|
| base / control | 5,686 | **1,760** | **434** | **1,326** | 6,689 |
| base / retention | 5,708 | **1,760** | **434** | **1,326** | 6,748 |
| tie / control | 5,687 | **1,760** | **434** | **1,326** | 7,090 |
| tie / retention | 5,708 | **1,760** | **434** | **1,326** | 7,022 |
| hold / control | 5,686 | **1,760** | **434** | **1,326** | 6,931 |
| hold / retention | 5,707 | **1,760** | **434** | **1,326** | 6,927 |

**Every register count inside the core is identical on every arm and every
configuration.**  ⚠ The **whole-design** A&S count wobbles by **±1** (tie/control
+1, hold/retention −1) — **outside `v30_core`, in the vendored MiSTer framework,
recorded and NOT explained**, the same class as WAVE 7's `sys_top` 424 → 422.
⚠ And **the arms did not shrink the design**: the core's combinational ALUTs
**grew** by 242–401.  *So much for the tie arm winning by deletion.*

### 3.5 (d) IN THE STAGE ANATOMY — **AND IT CORRECTS WAVE 10's REASONING**

Worst `ce → ce`, worst `* → s1q` (STAGE 1) and worst `s1q → *` (STAGE 2), by
DATA DELAY, on the seed-5 netlist of each sweep (`sta_cutset_diag.tcl`, the
`-from`/`-to` rows, whose soundness §1.3 established):

| leg | worst `ce → ce` | **STAGE 1** | **STAGE 2** | worst arc is the round trip? |
|---|---:|---:|---:|---|
| **base / control** | **31.433** (32 lv) | 18.963 (12) | **27.880** (26) | **YES** — `q_cnt~3\|datae` → `q_ripe_lead_n~3\|combout`, 6 BIU nodes |
| **base / retention** | **30.130** (31) | 19.788 (16) | **28.019** (26) | **YES** — `q_cnt~2\|datac` → `q_ripe_lead_n~5\|combout`, 8 BIU nodes |
| tie / control | 25.022 (21) | 24.672 (22) | 23.716 (23) | no — 23 BIU nodes but **not** `q_ripe_lead_n` |
| tie / retention | 25.610 (25) | 25.610 (25) | 25.419 (26) | no — **0 BIU nodes** |
| hold / control | 26.514 (25) | 26.181 (25) | 25.930 (23) | no — **0 BIU nodes** |
| hold / retention | 26.677 (27) | 26.677 (27) | 26.677 (27) | no — **0 BIU nodes** |

Base reproduces WAVE 9 §5 closely (STAGE 1 20.235 → **18.963 / 19.788**, STAGE 2
**27.922 → 27.880 / 28.019**) and reproduces its central claim exactly: **the
binding arc is ABOVE both stages, it is the round trip, and POP-A carries it on
200 of 200 paths** — the class no cut inside `v30u_eu` can divide.

> ### ⚠⚠ **AND HERE IS WAVE 10 §4.4's INFERENCE, CORRECTED.**
>
> WAVE 10 concluded that an arm whose arc lands **below** the two-stage ceiling
> must have SUBDIVIDED a stage.  **On these arms STAGE 2 itself falls — 27.880
> → 23.716 (tie/control), 28.019 → 25.419 (tie/retention) — with NO REGISTER
> ADDED ANYWHERE.**  And **STAGE 1 rises at the same time**, 18.963 → 24.672.
> **BOTH STAGES MOVED, IN OPPOSITE DIRECTIONS.**  A subdivision only shortens;
> this is the fitter re-spending effort once the 31.4 ns arc it was chasing is
> gone.  **A SHORTER STAGE 2 IS NOT EVIDENCE OF SUBDIVISION**, and WAVE 10's
> caveat against its own +6.629 ns does not survive.
>
> On the arms the worst `ce → ce` arc lies within **0.35 ns** of
> `max(STAGE 1, STAGE 2)` on all four probe legs and **equals it to the
> thousandth on two of them** (tie/retention 25.610, hold/retention 26.677) —
> the two-stage ceiling is **met, not broken.**  On the base legs the arc stands
> **3.55 ns and 2.11 ns ABOVE** that maximum, which is the third class WAVE 9
> named and this wave's arms delete.

---

## §4 P-4 — **PAIRED, FIVE SEEDS, BOTH CONFIGURATIONS, ONE DRIVER, ONE SEED SET, `E11` TRUE EVERYWHERE.**  **MET.**

`sw/run_wave14_g6.sh` drew all six sweeps, `quartus_gate.py --seeds 5 [--retention]`,
seed set **{1,2,3,4,5}**, one shared `quartus_map` per sweep, `pgrep -x` by exact
binary name one pattern per call, `hdl/nec_test_ucore.qsf` restored by that exact
path around every Quartus run.

| sweep | verdict | id | `input_manifest` | **E11** | `.rbf` distinct | worst-of-5 |
|---|---|---|---|---|---|---:|
| `w14-base-control-n5` | RED | `d565b21a4b6402e0…` | `d4ecdeff14444248…` (99) | **pass**, 99 scanned, 0 hits | 5/5 | **30.53** |
| `w14-base-retention-n5` | RED | `fb06b349a2ca1353…` | `d4ecdeff14444248…` (99) | **pass** | 5/5 | **31.15** |
| `w14-tie-control-n5` | **PASS** | `9119600631b7d287…` | `8910f61ba025a3c7…` (99) | **pass** | 5/5 | **37.39** |
| `w14-tie-retention-n5` | **PASS** | `06386e856c7ae3e7…` | `8910f61ba025a3c7…` (99) | **pass** | 5/5 | **36.45** |
| `w14-hold-control-n5` | **PASS** | `ed7d743c740a88b1…` | `70a60f5d70e27fc8…` (99) | **pass** | 5/5 | **36.87** |
| `w14-hold-retention-n5` | **PASS** | `7f26da36b4d89148…` | `70a60f5d70e27fc8…` (99) | **pass** | 5/5 | **37.16** |

* **`E11_no_build_stamp` reads `pass` on all SIX distribution receipts and all
  THIRTY per-seed receipts** — `hdl/build_id.v` absent, `token_hits` **{}**, 99
  files scanned.  **A single false E11 would have voided the pairing.  There is
  none.**  ⚠ It is read at **DISTRIBUTION level and per receipt**, never from
  inside a seed's `bars` dict, where the query returns nothing.
* **THREE MANIFESTS, IDENTICAL BETWEEN THE TWO CONFIGURATIONS OF EACH ARM**:
  the configurations differ by the `--verilog_macro` and nothing else, and the
  arms differ by the RTL edit — which is the check that the edit reached the
  compiler.
* **`configuration` DERIVED from the reports on all six** (E-6); every retention
  sweep self-labels `RETENTION (X1_AD_RETENTION=1)`.
* **`off_class` EMPTY with measured k = 1.0 against a nominal of 1.0 on all
  30 draws** — the no-exception configuration reached the compiler every time,
  in WAVE 13's polarity.
* ⚠ **ONE RECORDED ANOMALY**: on `w14-base-control` seed 4 the `truefmax` probe
  exited **rc = 2 with a COMPLETE artifact (all five classes)**; `quartus_gate`
  accepted it and recorded the rc, which is what it is written to do.  That
  draw's row carries k = 1.0 and `off_class` `[]` like every other.

---

## §5 P-5 — **THE CEILING, WITH ITS UNCERTAINTY.**  **MET.**

Paired on the seed, `Δ` = base T_min − arm T_min (positive = the arm's arc is
shorter).  95 % CI from a **tabulated** t (df = 4, t = 2.776); the scorer
**refuses** rather than approximate an untabulated df.

### 5.1 CONTROL

| | per-seed Δ ns (1..5) | **paired mean** | sd | se | **95 % CI** | t | ΔMHz mean | worst-of-5 |
|---|---|---:|---:|---:|---|---:|---:|---:|
| **ARM-T `qripe_tie`** | +6.146 · +6.160 · +6.950 · +6.294 · +5.917 | **+6.293** | 0.391 | 0.175 | **[+5.808, +6.779]** | **+35.97** | +7.424 | 30.53 → **37.39** |
| **ARM-H `qripe_hold`** | +7.249 · +6.515 · +6.575 · +6.126 · +5.541 | **+6.401** | 0.628 | 0.281 | [+5.622, +7.181] | +22.79 | +7.600 | 30.53 → **36.87** |

### 5.2 RETENTION — **THE SHIPPING CONFIGURATION**

| | per-seed Δ ns (1..5) | **paired mean** | sd | se | **95 % CI** | t | ΔMHz mean | worst-of-5 |
|---|---|---:|---:|---:|---|---:|---:|---:|
| **ARM-T `qripe_tie`** | +4.062 · +4.531 · +4.673 · +5.091 · +5.260 | **+4.723** | 0.474 | 0.212 | [+4.134, +5.312] | +22.27 | +5.756 | 31.15 → **36.45** |
| **ARM-H `qripe_hold`** | +4.684 · +3.957 · +5.644 · +4.640 · +4.517 | **+4.688** | 0.608 | 0.272 | **[+3.933, +5.444]** | **+17.24** | +5.688 | 31.15 → **37.16** |

### 5.3 THE QUOTED CEILING, BY THE RULE REGISTERED BEFORE ANY RESULT WAS SEEN

The pre-registration fixed the quoted ceiling as **`min(Δ_T, Δ_H)`** — both are
upper bounds and the smaller upper bound is the better one.

> | | **CEILING** | 95 % CI | from |
> |---|---:|---|---|
> | **CONTROL** | **+6.293 ns** | [+5.808, +6.779] | ARM-T |
> | **RETENTION** | **+4.688 ns** | [+3.933, +5.444] | ARM-H |
>
> **THE TWO ARMS AGREE TO 0.108 ns (CONTROL) AND 0.035 ns (RETENTION).**  §1.1
> of the pre-registration expected `Δ_H < Δ_T` because ARM-T prunes; **on
> CONTROL the ordering is the other way round and on RETENTION they are the same
> number.  THE EXPECTATION WAS WRONG AND IT IS RECORDED AS WRONG.**  The
> pruning concern that motivated running two arms is, measured, immaterial —
> and §3.4's ALUT counts say why: the tie arm does not delete logic, it grows
> it.

### 5.4 BESIDE IT, AS REGISTERED — WAVE 10 AND THE CENSUS LAW

| | figure | this wave |
|---|---|---|
| WAVE 10, the **UNSPLIT** tree, 10 seeds | **+0.527 ns**, 95 % CI **[−0.185, +1.239]**, t = 1.68 — *not distinguishable from zero* | **+6.293 / +4.688**, t = 36.0 / 17.2 |
| WAVE 10, the **CUT** tree, register-inserting arm | **+6.629 ns** — disowned as an over-answer | **reproduced at +6.29 / +6.40 with NO register** |
| WAVE 9's census of this mechanism | **2.786 ns** | overstatement **−2.26×**, i.e. an **UNDERSTATEMENT** |
| this wave's own census, base netlists, POP-A mean span | 2.149 (ctl) / 2.562 (ret) | understatement **2.93× / 1.83×** |
| WAVE 8, `ucrom` | census **3.805**, built out **0.644** — **5.9× OVER** | — |
| WAVE 10, this mechanism, unsplit | census 2.786, measured 0.527 — **5.3× OVER** | — |

> ### **A CENSUS RANKS CANDIDATES AND DOES NOT SIZE THEM.  THE LAW HELD THREE TIMES AND THIS IS THE FIRST TIME IT MISSED *LOW*.**  Two census figures were 5-6× too big; this one is 1.7–2.9× too small.  **The law is about the census being uninformative as a size, not about a direction — and anyone who read it as "the census is an upper bound" was reading a coincidence.**

### 5.5 WHY THE SAME EDIT IS WORTH 0.53 ns ON ONE TREE AND 6.29 ON ANOTHER

It is WAVE 10 §4.5's own sentence, now with the confirming measurement:
**the mechanism did not change; what else was on the arc did.**  On the unsplit
tree the microcode-ROM loop binds and the round trip is on the arc 5 draws in
13.  On the split tree the split has shortened everything it could reach, the
round trip binds **200 of 200 paths on both configurations**, and removing it
recovers a great deal.  **A CANDIDATE'S VALUE IS NOT A PROPERTY OF THE
CANDIDATE.**  ⚠ **WAVE 10 §5.5's *"the BIU round trip is not the remaining gap
and should not be the next wave"* was a verdict about the UNSPLIT tree.  On the
split tree it is REVERSED, by WAVE 10's own principle.**

---

## §6 P-6 — **THE ENDGAME ARITHMETIC, WITH NUMBERS.**  **MET.**

The bar is **32.0 MHz**, i.e. **T_min ≤ 31.250 ns**, no exception of any kind.
The base arm's own `worst-of-5`, drawn in this wave: **CONTROL 30.53 MHz
(T_min 32.756 ns)**, **RETENTION 31.15 MHz (32.105 ns)**.

|  | CONTROL | RETENTION |
|---|---:|---:|
| base `worst-of-5` T_min | 32.756 ns (30.53 MHz) | 32.105 ns (31.15 MHz) |
| **GAP to 31.250 ns** | **1.506 ns (1.47 MHz)** | **0.855 ns (0.85 MHz)** |
| − the CEILING | 32.756 − **6.293** = 26.463 → **37.79 MHz** | 32.105 − **4.688** = 27.417 → **36.47 MHz** |
| − the BOTTOM of the 95 % CI | 32.756 − 5.808 = 26.948 → **37.11 MHz** | 32.105 − 3.933 = 28.172 → **35.50 MHz** |
| **fraction of the ceiling a real mechanism must recover** | **1.506 / 6.293 = 23.9 %** | **0.855 / 4.688 = 18.2 %** |
| **against the CI bottom** | 25.9 % | 21.7 % |

**AND DIRECTLY, WITHOUT ARITHMETIC**: both probe arms are a **G6 PASS on every
one of their twenty draws**, both configurations — worst single draw **36.45
MHz**, 4.45 MHz clear of the bar, with TNS 0.000 setup and hold on every domain
and positive worst setup everywhere.

> ### **THE ANSWER, PLAINLY.**
>
> **YES.  A BEHAVIOUR-PRESERVING MECHANISM THAT RECOVERED EVEN A QUARTER OF THIS
> CEILING WOULD FINISH THE CAMPAIGN ON BOTH CONFIGURATIONS.**  That is a
> qualitatively different position from WAVE 10's: there the ceiling was
> **0.527 ns against a 4.06 ns gap**, so a real mechanism had to be worth **more
> than 7× the measured ceiling** — impossible.  Here it must be worth **less
> than a quarter of it.**
>
> ⚠ **AND NOTHING HERE SAYS SUCH A MECHANISM EXISTS.**  The probes are not
> designs.  The EU is contracted (F7) to read the BIU's NEXT level at
> `q_ripe_lead_n`, and both arms break exactly that contract; **181 golden cases
> say so.**  What this wave establishes is that the *budget* is there — that a
> reformulation which keeps the F7 semantics and takes even a fifth of this arc
> out of the `ce → ce` cone closes the gap.  **Whether one exists is the next
> wave's question, and it is now a question worth asking**, which it was not
> after WAVE 10.
>
> ⚠ **`standing_gates.md` §A GOVERNS.**  One green build is not closure and the
> converse holds too; these are `worst-of-5` figures from one instrument on one
> machine, and the same tree has drawn 19.42 and 45.91 MHz in this project's
> history.

---

## §7 P-7 — **NOTHING IS LANDED.**  **MET.**

* `git status --porcelain hdl/` (tracked): **0 at the start, 0 at the end.**
  The main tree's `hdl/` was **never written by this wave at all** — every arm,
  including the base, lives in a scratch git worktree under
  `~/.cache/ucsimt-tmp/wave14/`, and all three are **removed** (`git worktree
  list` shows only the main tree).
* **No file under `hdl/` is modified by any commit of this wave.**
* Both probe arms are reverted by construction: they existed only as worktrees.

---

## §8 THE BARS, SCORED

| bar | verdict |
|---|---|
| **P-1** every classifier carries a positive control, reported first; a miss voids the wave | **MET.**  §1.  Scorer selftest reproduces WAVE 13's committed distributions **and found the unusable column before any new data existed**; `sta_biu_roundtrip`'s PC-W1..PC-W5 and the AX controls **ALL PASS on 6 of 6 legs**, every `-through` ONE PIN, the bulk form printed and **below** the single-pin figure on 4 of 6; **the STAGE rows' missing control was BUILT (`sta_wave14_shadow_pc.tcl`) and it REFUTED this wave's own first suspicion** (§1.3); and the base arm reproduces WAVE 13 on **10 of 10 draws exactly**. |
| **P-2** the probe severs the path; `check_core` FAILS and is reported as evidence | **MET.**  **168,819 / 169,000, exit 1, on BOTH arms**, against the base's **169,000 / 169,000, exit 0**.  The STA agrees independently: `q_ripe_lead_n` on **200 of 200** base paths and **0 of 200** on every arm leg.  §2 |
| **P-3** the probe adds **NO REGISTER** and does **NOT subdivide STAGE 2** | **MET, four ways.**  0 added lines carry `<=`; `ss_lint` **229 flops, `SS_COUNT` 232, identical on all three arms**; **`v30_core` 1,760 registers / `v30u_eu` 1,326 / `v30u_biu` 434 on all six sweeps**; and the STAGE rows show **both stages moving in OPPOSITE directions**, which a subdivision cannot do.  ⚠ **This wave therefore did NOT rebuild WAVE 10's mistake — and it CORRECTS the inference WAVE 10 made** (§3.5). |
| **P-4** paired, ≥ 5 seeds, both configurations, one driver, one seed set, E11 true on every draw | **MET.**  6 sweeps / 30 fits, seed set {1,2,3,4,5}, one driver; **E11 `pass` on all 6 distributions and all 30 per-seed receipts**, read at distribution level; three manifests, identical within each arm; `.rbf` 5/5 distinct in every sweep; `off_class` EMPTY at k = 1.0 on all 30.  §4 |
| **P-5** the ceiling with its uncertainty, beside WAVE 10 and the census law | **MET.**  **CONTROL +6.293 ns [+5.808, +6.779]**, **RETENTION +4.688 ns [+3.933, +5.444]**, by the `min(Δ_T, Δ_H)` rule registered in advance; both arms reported; WAVE 10's +0.527 [−0.185, +1.239] quoted beside it; **the census understated 2.3× / 1.7×, the first miss in that direction.**  §5 |
| **P-6** the endgame arithmetic, stated with numbers | **MET.**  Gap **1.506 / 0.855 ns**; ceiling **6.293 / 4.688**; a real mechanism needs **23.9 % / 18.2 %** of it.  Both probe arms are a G6 PASS on 20 of 20 draws.  §6 |
| **P-7** `hdl/` clean at start and end; nothing landed | **MET.**  The main tree's `hdl/` was never written; all three worktrees removed.  §7 |
| §4 item 1 of the prereg (`Δ_H < Δ_T`) | ⚠ **WRONG, AND RECORDED AS WRONG.**  On CONTROL `Δ_H > Δ_T` by 0.108 ns; on RETENTION they differ by 0.035.  No bar depended on it. |
| §4 item 2 (both fall well short of +6.629) | ⚠ **WRONG, AND RECORDED AS WRONG.**  CONTROL **reproduces** it. |
| §4 item 3 (a ceiling too small to close the gap is a valid result) | **NOT EXERCISED** — the ceiling is 4–5× the gap. |

---

## §9 WHAT IS OWED

1. ⚠⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND WAS DOUBLED AT
   WAVE 12.  IT IS STILL OWED.**  **A fabric figure taken on FLASH #21 or
   earlier may not be quoted against this tree.**  Nothing was flashed here and
   **this wave lands nothing, so it adds no new debt.**
2. **THE NEXT MECHANISM IS NAMED AND ITS BUDGET IS NOW MEASURED**: a
   **behaviour-preserving** reformulation of `q_cnt → poppable_n →
   q_ripe_lead_n → EU` that takes ≥ 24 % (CONTROL) / 18 % (RETENTION) of that
   arc out of the `ce → ce` cone **while keeping the F7 NEXT-level contract**.
   ⚠ It must be scored on the SPLIT tree, and **the split does not currently
   land** (WAVE 13 N-1 failed) — so such a wave is *two* landings, not one.
3. ⚠ **`sta_cutset_diag.tcl`'s C-8 CLASSIFIER AND ITS `of which name |s1q`
   COUNTER UNDER-REPORT** on any netlist where physical synthesis has renamed
   shadow duplicates after their fanout net (§1.3).  **Its `-from`/`-to` STAGE
   rows are sound and are what this wave used.**  A membership-tested
   replacement is one `lsearch` away; **not taken here, because changing an
   instrument in the wave that measures with it is how a result gets chosen.**
4. **THE ±1 WHOLE-DESIGN A&S REGISTER WOBBLE** (§3.4) is outside `v30_core`,
   reproducible in sign per arm, and **not explained.**
5. **RETENTION's CEILING IS 1.6 ns SMALLER THAN CONTROL's** (4.688 vs 6.293)
   although its base is faster.  **Recorded, not explained**; `standing_gates.md`
   §A governs.
6. **`check_core --ss-sweep` IS STILL NOT ON ANY REGISTERED LADDER** — booked by
   WAVE 2, 3, 4, 9 and 13.  **Booked for the sixth time**, and the repetition is
   again worth noticing.
7. **`docs/notes/standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS
   WAVE.**  The coordinator decides (the WAVE 11/12/13 precedent).  Still
   unregistered from WAVE 13: the stale `ss_lint` row (226 / 214 / 0x8D against
   the tree's 232 / 229 / 0x8F — ⚠ note **229**, not 228, on the split tree,
   which grows by the shadow's `s1q` whitelist entry) and WAVE 12's bar **E11**.

---

## §10 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
* **NOTHING IS LANDED.**  `hdl/` in the main tree was never written; the three
  worktrees are removed.
* Single-writer guard before every Quartus stage, **`pgrep -x` by EXACT binary
  name, ONE PATTERN PER CALL**; ⚠ `pgrep -f <script>` self-matches and was never
  used.  **The waits BLOCKED; they did not poll a turn.**
* The driver carries **`set -u`, NOT `set -e`** — `quartus_gate` exits non-zero
  on RED and the base arm was expected to draw RED.  It did, twice, and the
  script continued, which is WAVE 13's lesson applied.
* `hdl/nec_test_ucore.qsf` `git checkout -- <that exact path>`'d around every
  Quartus run, in the arm's own worktree.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  The **21 pre-existing modified files that are the user's own uncommitted
  work** and the 14 untracked `hdl/quartus_gate_*.log` files are **untouched**;
  `git add` was **BY EXPLICIT PATH ONLY** on every commit.  ⚠ **AND THIS WAVE
  ADDS NO `hdl/*.log`** — checked against `ls hdl/*.log`, not against recall:
  every Quartus transcript went to `--log` inside the arm's own worktree and is
  committed under `sw/testdata/wave14/`.
* `~/.cache/ucsimt-tmp/wave14/` for every intermediate; nothing in `/tmp`.
* **CONTENT COMPARED, NOT A SELF-COMPUTED DIGEST**: every figure is quoted from
  a named committed artifact, the WAVE 13 comparison is field by field over ten
  draws, and the shadow membership test compares **collection membership**, not
  a string a human read off a line.
* No Codex.  No nested subagent.
* **No figure in this wave is a receipt, a gate or a design Fmax.**
  `standing_gates.md` §A governs; one green build is not closure.
* **Record what was measured, not what was expected** — and §8's last three rows
  are two expectations that were wrong, left visible.

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
