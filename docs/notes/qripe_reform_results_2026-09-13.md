# WAVE 15 — **A LEGAL MECHANISM EXISTS, IT IS BEHAVIOURALLY EXACT, AND IT CLOSES BOTH CONFIGURATIONS.**  RESULTS, SCORED AS REGISTERED.

Pre-registration in two parts, **both committed before the first `hdl/` edit of
any tree and before the first Quartus stage**: the derivation and the candidate
enumeration at **`96dd1030cb`** (naming no winner), the choice and the bars
Q-1 … Q-8 at **`2dbeb896fd`**.  Instruments at **`b237b54957`** with
**AMENDMENT A-1**; **AMENDMENT A-2** at **`46d7c01aec`**, committed while the
driver was still on the BASE arm and **no arm timing existed**.

**THIS WAVE FINDS AND SIZES A MECHANISM.  IT LANDS NOTHING.**
**OFFLINE ONLY — NO BOARD, NO FLASH, NOTHING PROGRAMMED.**  No Codex.  No
nested subagent.  `git status --porcelain hdl/` (tracked) carried **0** at the
start and carries **0** at the end; the main tree's `hdl/` was **never written**.

| | |
|---|---|
| **Base commit of every arm** | `850ef46559` — WAVE 13's SPLIT tree, WAVE 14's base |
| **The arms** | `~/.cache/ucsimt-tmp/wave15/wt_{base,qripe_presel,qripe_s1q}`, scratch git worktrees |
| **The distributions** | `sw/testdata/g6dist/w15-{base,presel,s1q}-{control,retention}-n5/` |
| **The STA anatomy, ladders and diffs** | `sw/testdata/wave15/` |
| **Tool** | Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns; Verilator 5.032 |
| **Cost** | 6 sweeps · 30 fits · 6 maps · 3 h 41 m wall, plus three full equivalence ladders |

---

## §0 THE HEADLINE, IN SIX SENTENCES

> **1. THE MECHANISM IS ONE SENTENCE.**  *The BIU publishes the 1BL retire-lead
> level for each of the two things the EU can do to the queue this clock — pop,
> or not — and the EU picks the one it is doing.*  Both levels are pure
> functions of BIU registers; the select is `q_pop && q_ripe && !q_flush`, two
> of the EU's own outputs and a BIU **register** port it already had.  It is the
> **same function against two thresholds** ("at least one" / "at least two") and
> **it adds no flop.**
>
> **2. IT IS BEHAVIOURALLY EXACT, AND THE 181 GOLDENS SAY SO FIRST.**
> `check_core --opcodes all --cases 0` is **169,000/169,000** at `--ce-div`
> 2, 3, 4 **and** 8 with div 1 refused; **`FA` 500/500, `FB` 500/500,
> `INT.FB` 200/200** — the exact 181 cases both WAVE 14 probes failed;
> `ulockstep` **17,350 ALL LOCKSTEP**; `chain_lfsr`'s four signatures
> **BYTE-IDENTICAL**; `fz2_replay` **305 rows × 11 fields IDENTICAL**, compared
> by name.
>
> **3. IT CLOSES BOTH CONFIGURATIONS.**  `worst-of-5` **30.53 → 33.00 MHz
> (CONTROL)** and **31.15 → 33.20 MHz (RETENTION)**, both **G6 PASS on 10 of 10
> draws**, against a bar of 32.0.  Paired over five seeds: **+2.847 ns
> [+2.377, +3.316], t = 16.8** and **+1.429 ns [+0.562, +2.296], t = 4.57** —
> **45.2 % and 30.5 % of WAVE 14's ceiling, against the 23.9 % / 18.2 % that
> was needed.**
>
> **4. THE ROUND TRIP IS GONE FROM THE BINDING CLASS ON CONTROL AND NEARLY GONE
> ON RETENTION.**  BIU nodes in the data section of the top-200: **200 of 200 →
> 0 of 200 (CONTROL)** and **200 → 30 (RETENTION)**; mean excursion **2.149 ns →
> 0.000** and **2.562 → 0.183**.  ⚠ **Q-3a, the bar as literally registered,
> reads MISSED 200/200 on every arm leg — and §3.2 shows why: the instrument's
> matcher is a SUBSTRING test and the node it now matches is the EU's own mux.**
>
> **5. THE REGISTERED SUCCESSOR IS BIGGER, AND IT WAS REGISTERED BEFORE IT WAS
> BUILT.**  ARM-B (C2, the select off the `s1q` shadow, **one declared flop**)
> gives **34.48 / 34.41 MHz worst-of-5**, **+3.665 ns [+3.224, +4.106]** and
> **+2.425 ns [+1.413, +3.438]** — **58.2 % and 51.7 % of the ceiling** — and it
> is the arm that passes `cutset_lint`.
>
> **6. TWO INSTRUMENT FINDINGS, BOTH CAUGHT BY CONTROLS.**  `fz2_replay` is
> **structurally vacuous in a git worktree** (`.gitignore:9`) and **ran green
> over zero rows** before it was repaired; and **`cutset_lint` X4 fires on
> ARM-A and is right to** — C1 *relocates* a bypass that was always there, which
> is a finding about the tree, not about C1.

---

## §1 Q-1 — **THE DERIVATION AND THE ENUMERATION WERE COMMITTED BEFORE A CANDIDATE WAS CHOSEN.**  **MET.**

`96dd1030cb` carries the spec derivation and **eight** candidates C0 … C7 with
costs and falsifiers, and names no winner.  `2dbeb896fd` chooses **C1** with the
reason and registers Q-1 … Q-8.  Neither commit touches `hdl/`.

### 1.1 WHAT F7 REQUIRES — THE ANSWER, IN ONE SENTENCE

> **The value the clocked step reads must be the BIU's queue level for the clock
> the edge OPENS, WHICH INCLUDES THE EFFECT OF THE EU'S OWN POP ON THIS CLOCK.**

`q_ripe_lead_n` is `BiuTimed::wait_retire_lead`'s predicate — *"the queue's
front byte is ready by `clk_ + 1`"* — and that function has **exactly one
caller**, `loader_impl.h:334`, inside the `ONE_BYTE_LOGIC` arm.  Since the chain
flattening (WAVE 7) one clock can walk
`S_EPOP · S_TAIL · S_INSTR_END · S_TAKE_OPC · S_DECODE · S_DECODE2`, so the
opcode pop and the 1BL decode that reads the predicate happen **in the same
clock**.  **Breaking it costs 181 goldens: `FA` 74 + `FB` 68 + `INT.FB` 39, and
every one of them is a ONE_BYTE_LOGIC form** (WAVE 14's own
`logs/p2_equiv.log.gz`).  Nothing else in 169,000 moves.

### 1.2 THE PARTITION, WHICH IS THE WHOLE PROBLEM — AND IT IS TWO BITS

Walking every write to the three operands of the predicate:

> `q_ripe_lead_n = f(BIU registers, q_pop, q_flush)`

`q_pop` enters at **one** place (the 4-bit decrement, `v30u_biu.sv:1919`);
`q_flush` at one (the zeroing, `:2064`); the T4 push and the `grn_ttl` aging are
**pure register functions**.  A flush **overwrites** the count after the pop has
decremented it, so the two do not interact and there are **three levels, not
four**.

### 1.3 AND THE BINDING CARRIER WAS IDENTIFIED FROM WAVE 14's OWN COMMITTED NETLISTS, BEFORE ANY ARM EXISTED

The binding `ce → ce` path's data section carries **exactly one EU node before
the BIU excursion**, the same on both configurations: **`s1_bus[103]`**, which
is **`bnd_fire`** by counting the pack list's widths from the LSB — and
`bnd_fire` reaches the BIU through **`q_demand` / `q_pop`** and nothing else.
**The round trip that binds is the POP one.**  §3.4 shows the arms confirming
it: with the pop split off, the residual carrier is **`q_flush`**, the other bit
of §1.2, and nothing else.

---

## §2 Q-2 — **EQUIVALENCE, IN FULL, BEFORE ANY TIMING FIGURE WAS QUOTED.**  **ARM-A: BEHAVIOURALLY MET IN FULL, ONE STRUCTURAL LINT FAILS.  ARM-B: MET IN FULL.**

Every leg below was run and read **before** the first Quartus sweep finished,
and A-2 (`46d7c01aec`) records them with the driver still on the base arm.
Full log: `sw/testdata/wave15/q2_report.txt`; the ladders themselves in
`sw/testdata/wave15/logs/`.

Three separately receipted Verilator binaries: base **`a85a4104f7a69ed8…`**,
ARM-A **`74a2a09796d70878…`**, ARM-B **`f40ce2fe6e11102d…`**.

| leg | base | **ARM-A `qripe_presel`** | **ARM-B `qripe_s1q`** |
|---|---|---|---|
| `check_core --opcodes all --cases 0` | **169,000/169,000** | **169,000/169,000** | **169,000/169,000** |
| …`--ce-div 2 / 3 / 8` | 169,000 each | **identical** | **identical** |
| …`--ce-div 1` | REFUSED | REFUSED | REFUSED |
| **`FA` / `FB` / `INT.FB` — the 181** | 500 / 500 / 200 | **500 / 500 / 200** | **500 / 500 / 200** |
| `8F.0` | 500/500 | 500/500 | 500/500 |
| the four HLT sweeps | 97 · 93 · 45 · 44 = **279/283** | **identical** | **identical** |
| `v0.1-w1` / `-w3` / `EB` | 1,200 · 1,200 · 200 | identical | identical |
| the four `evt` cells + biased | 200 · 1,200 · 200 · 1,200 · 1,200 | identical | identical |
| `ulockstep --golden all --cases 50` | **17,350 ALL LOCKSTEP** | **identical** | **identical** |
| `ghost_launch_law` | 200/200 | identical | identical |
| `check_boot` / 400 | 220 · 400 MATCH | identical | identical |
| `check_ab_sim` | 187 MATCH | identical | identical |
| `sm3_s16_score --core ucore` | `busstat_other` 24 · `ARCH` 27 | identical | identical |
| `chain_lfsr_gate` | PASS, 4 sigs | **BYTE-IDENTICAL** | **BYTE-IDENTICAL** |
| `demux_off_gate` | PASS | PASS | PASS |
| `test_artifact` | 45/45 | 45/45 | 45/45 |
| `test_quartus_gate` | **286/286** ⚠ | 286/286 | 286/286 |
| `ucrom_mif_check` | **PASS** (re-run with a build tree) | **PASS** | **PASS** |
| `chainflat_relocation_check` | PASS, 9 arms | PASS | PASS |
| `r7_lint` | PASS | **PASS** with two declared entries (§2.2) | **PASS** |
| `ss_lint --core ucore` | PASS **232**, 229 flops, 0 UNMAPPED | **identical** | **identical** |
| `phase_split_lint` | PASS 156 / 778 | PASS 156 / 778 | **PASS 157 / 779** |
| `cutset_lint` | PASS 80 / 0 | ⚠ **FAIL — X4** (§2.4) | **PASS 81 / 0** |
| **`fz2_replay`, 305 seeds** | AGREEMENT 301/305, `first_bad` identical 101 | **305 × 11 IDENTICAL** | **305 × 11 IDENTICAL** |

The four `chain_lfsr` signatures, identical on all three trees:
`1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78`,
**and every gap count and liveness row with them.**

### 2.1 THE RTL CARRIES ITS OWN FALSIFIER, AND IT IS DEMONSTRATED ABLE TO FAIL

The original predicate is kept **verbatim** as a sim-only reference and compared
at **every `ce`** (the `V30_MUXED_AD` precedent), in two clauses: the identity
`pop_eff ? lead1 : lead0 == reference`, and `pop_eff == (q_pop && q_ripe &&
!q_flush)` — the second being what makes the EU's local select formula sound,
since the EU cannot see `pop_eff`.

| perturbation | clause | result |
|---|---|---|
| one term of `q_ripe_lead_n1` moved `grn_ttl == 1` → `== 2` | (1) | **FIRES**, `FA` at 4,685,000: *"composed=0 reference=1 (pop_eff=1 q_cnt=2 q_cnt_np=3 grn_n=2 grn_ttl=1)"* |
| `pop_eff` armed from `q_pop` alone | (2) | **FIRES**, `FA` at 85,000: *"pop_eff=1 but q_pop=1 q_ripe=0 q_flush=0"* |
| the flush's `pop_eff = 1'b0` deleted | either | ⚠ **DID NOT FIRE — 169,000/169,000 without it.**  **The pop/flush coincidence is not reached by the golden population.**  Reported as measured; the term is kept because the flush provably overwrites the count. |

### 2.2 THE DECLARED COST: `r7_lint` GAINS TWO ENTRIES AND THE ARGUMENT IS UNCHANGED

C1 splits `q_ripe_lead_n` — a **declared unresolved carrier** since §73 — into
two nets, and without the list edit `r7_lint` **FAILS with two undeclared
unresolved carriers**, correctly.  The edit is **inside the arm's own diff**
(`sw/wave15_arms.py` applies it, so it shows up in `git diff` beside the RTL),
the original entry is kept above the two new ones so a reader can see nothing
was dropped, and the argument is the same one character for character.

### 2.3 ⚠⚠ **A RIG FINDING: `fz2_replay` IS STRUCTURALLY VACUOUS IN A GIT WORKTREE — AND IT RAN GREEN OVER ZERO ROWS.**

`.gitignore:9` ignores `sw/testdata/campaigns/*/captures/`, so a scratch
worktree holds **none** of the banked captures.  `fz2_replay.retained()` then
returns `{}`, the tool prints *"population 0 seeds"* / *"NOT SCOREABLE: 106"* —
**and exits 0.**  It did exactly that here, and the two JSONs compared
"IDENTICAL" **over zero rows**.  Caught only because the comparison was written
to print the ROW COUNT before the verdict.

**Repaired by symlink** (untracked; no tracked file touched).  The leg is then
**305 seeds** — WAVE 7's own denominator — with the base reading **AGREEMENT
301 / 305 = 98.7 %** and `first_bad` identical on 101 of the 101 both-FAIL
seeds, and **base vs each arm 305 rows × 11 fields IDENTICAL**, compared
**by name, never by a digest computed here** (`sw/wave15_fz2cmp.py`, which now
**refuses with exit 4** on a zero-row population).
⚠ **Every wave that runs gates in a scratch worktree inherits this.**

### 2.4 ⚠⚠ **`cutset_lint` X4 FIRES ON ARM-A AND IT IS RIGHT TO — C1 RELOCATES A BYPASS, IT DOES NOT DELETE IT**

> On the base tree `q_ripe_lead_n` is an input **PORT**, and `cutset_lint`
> exempts ports.  But the value on that port is `f(q_pop)` and `q_pop` is
> stage-1 combinational logic, so **the EU's stage 2 has been reading stage-1
> logic through the BIU all along** — which is *precisely why this arc binds on
> 200 of 200 paths of the split tree while the split shortened everything else
> it could reach.*  X4 cannot see through a module boundary; when C1 brings the
> mux inside the EU, it can.

A-2.4 wrote the consequence **as a prediction, before any timing was read**:
*"C1 should shorten this arc but cannot remove it from the `ce → ce` cone,
because the select still launches in stage 1."*  ⚠ **THE PREDICTION IS HALF
WRONG AND IT IS RECORDED AS WRONG**: the arc is shortened (§3), the select does
still launch in stage 1 — **but the BIU excursion is gone from 200 of 200
CONTROL paths, and C1 closes both configurations anyway.**

### 2.5 THREE DISAGREEMENTS WITH THE STANDING TABLES, NONE A FAILURE OF ANY ARM

1. **`test_quartus_gate` reads 286/286 on this tree, not the briefed 287/287.**
   Identical on all three arms.
2. **`standing_gates.md`'s `ss_lint` row is stale** (226 / 214 / `SS_VERSION`
   0x8D) against this tree's **232 / 229**.  Known-stale since WAVE 13.
   **Measured, reported, not treated as a failure.**
3. **`ucrom_mif_check` exits 2 in a fresh worktree** — *"NOTHING TO CHECK: no
   `hdl/db`"*.  **Re-run after the sweeps, when a build tree exists, it is
   `PASS` on all three arms.**

---

## §3 Q-3 — **THE ROUND TRIP, MEASURED THREE WAYS.  THE REGISTERED COLUMN IS CONFOUNDED; THE DISCRIMINATING ONE IS UNAMBIGUOUS.**  **Q-3a MISSED, Q-3b MET ON ARM-A/CONTROL, AND THE DIFFERENCE IS EXPLAINED.**

Instrument: **WAVE 10's `sta_biu_roundtrip.tcl`, UNEDITED**, run by WAVE 14's
driver on the netlist the last fit of each sweep left behind.  **Its own
controls read `=== CONTROLS: ALL PASS ===` on 6 of 6 legs.**  Scoring:
`sw/wave15_q3.py`, **pure post-processing of the rows that instrument writes**,
whose `--selftest` **PASSES** against WAVE 14's committed rows.  Full log:
`sw/testdata/wave15/q3_report.txt`.

### 3.1 THE POSITIVE CONTROL, FIRST

**The BASE arm reads 200 of 200 on Q-3a AND Q-3b in the same invocation as every
arm**, on both configurations.  The classifier can say YES.

### 3.2 ⚠⚠ **Q-3a READS 200/200 ON EVERY ARM LEG, AND IT IS THE INSTRUMENT MATCHING THE EU's OWN MUX**

`sta_biu_roundtrip.tcl`'s matcher is `string first "q_ripe_lead_n" $name` — a
**substring** test, chosen in A-1 precisely so a rename could not pass it.  C1
moves the selection into the EU, where the SystemVerilog wire is still called
`q_ripe_lead_n`, so Quartus emits `…|u_eu|q_ripe_lead_n~0|combout` and the
counter matches it.

> **Q-3a therefore cannot distinguish "the predicate is consumed" from "the
> excursion exists", and after this mechanism those are exactly the two things
> that differ.  IT IS SCORED AS MISSED, AND THE MISS IS AN INSTRUMENT RESULT,
> NOT A MECHANISM RESULT.**  A-1 anticipated the shape of this — it is why Q-3b
> exists — but not this particular direction.  **Recorded as registered, not
> restated.**

### 3.3 Q-3b / Q-3c — **BIU NODES IN THE DATA SECTION OF THE BINDING CLASS**

| leg | paths | **carrying a BIU node** | max BIU nodes/path | **mean excursion (WAVE 9 span)** | max |
|---|---:|---:|---:|---:|---:|
| base / CONTROL | 200 | **200** | 8 | **2.149 ns** | 2.659 |
| **ARM-A / CONTROL** | 200 | **0** | 0 | **0.000** | 0.000 |
| ARM-B / CONTROL | 200 | 200 | **2** | **0.497** | 0.514 |
| base / RETENTION | 200 | **200** | 10 | **2.562 ns** | 2.787 |
| **ARM-A / RETENTION** | 200 | **30** | 6 | **0.183** (1.219 over the 30) | 2.019 |
| ARM-B / RETENTION | 200 | **8** | 2 | **0.022** (0.555 over the 8) | 0.570 |

⚠ **The base's 2.149 / 2.562 reproduce WAVE 14 §5.4's census figures to the
thousandth**, on a different day in a different worktree — **a free control
nobody registered.**

**Q-3b (EU→BIU→EU *carrying* `q_ripe_lead_n*`): ARM-A CONTROL 0 of 200 — MET.
ARM-A RETENTION 30 of 200 — MISSED.  ARM-B CONTROL 200 of 200 and RETENTION
8 of 200 — MISSED.**  Reported as registered.

### 3.4 **AND THE RESIDUAL EXCURSION IS `q_flush` — THE OTHER BIT OF §1.2, MEASURED**

ARM-B / CONTROL's worst arc, the only leg where a BIU node is on every path:

```
 …|u_eu|row_pre_deliver~1|combout    18.842
 …|u_biu|q_cnt~3|combout             19.754     <- 2 BIU nodes, 0.514 ns
 …|u_eu|q_ripe_lead_n~13|combout     20.082
```

`row_pre_deliver` and **`row_acts_ok`** share their first four terms
(`v30u_eu.sv:2272` and `:2420`), so Quartus named the shared node after the
former — and **`q_flush = row_acts_ok && s1w_row_flush`**.

> **With the pop split off, the one EU act still reaching `q_ripe_lead_n`'s
> operands is the FLUSH, and §1.2 named it in advance from the source.  The
> excursion it leaves is 2 LUT levels and 0.5 ns against the pop's 8 and
> 2.1 ns.**  Splitting it too is a third level (`q_flush ? L_f : …`) and is
> **NOT taken here** — it is not needed to close either configuration, and
> taking it in the wave that measured its size is how a result gets chosen.

---

## §4 Q-4 — **PAIRED, FIVE SEEDS, BOTH CONFIGURATIONS, ONE DRIVER, ONE SEED SET, `E11` TRUE EVERYWHERE.**  **MET.**

`sw/run_wave15_g6.sh` — **WAVE 14's driver with the wave tag changed and nothing
else** — drew all six sweeps, `quartus_gate.py --seeds 5 [--retention]`, seed
set **{1,2,3,4,5}**, one shared `quartus_map` per sweep, `pgrep -x` by exact
binary name one pattern per call, `hdl/nec_test_ucore.qsf` restored by that
exact path around every Quartus run, all three arms run **strictly
sequentially** so no two stages could race past the guard.

| sweep | verdict | `input_manifest` | **E11** | worst-of-5 |
|---|---|---|---|---:|
| `w15-base-control-n5` | RED | `d4ecdeff14444248…` (99) | **pass**, all 5 receipts | **30.53** |
| `w15-base-retention-n5` | RED | `d4ecdeff14444248…` | **pass** | **31.15** |
| `w15-presel-control-n5` | **PASS** | `c3305d40f62e497f…` | **pass** | **33.00** |
| `w15-presel-retention-n5` | **PASS** | `c3305d40f62e497f…` | **pass** | **33.20** |
| `w15-s1q-control-n5` | **PASS** | `ee6a4eff46e483d3…` | **pass** | **34.48** |
| `w15-s1q-retention-n5` | **PASS** | `ee6a4eff46e483d3…` | **pass** | **34.41** |

* **`E11_no_build_stamp` reads `pass` on all SIX distribution receipts and all
  THIRTY per-seed receipts.**  ⚠ Read at DISTRIBUTION level and from each
  receipt file, never from a seed's `bars` dict.  ⚠ **And the per-seed read
  requires the scorer's CWD to be the arm's own worktree** — the receipt paths
  in a distribution are RELATIVE, and run from elsewhere every per-seed column
  reads `None` and E11 reads *"FAIL on [1,2,3,4,5]"*.  **Measured here first,
  reported, and no figure was quoted from the broken invocation.**
* **THREE MANIFESTS, IDENTICAL BETWEEN THE TWO CONFIGURATIONS OF EACH ARM** —
  which is the check that each RTL edit reached the compiler, and that the
  configurations differ by the `--verilog_macro` alone.
* **`configuration` DERIVED from the reports on all six** (E-6); every retention
  sweep self-labels `RETENTION (X1_AD_RETENTION=1)`.
* **`off_class` EMPTY on all 30 draws** — the no-exception configuration reached
  the compiler every time, in WAVE 13's polarity.
* **THE FREE CONTROL, AND IT IS EXACT: THE BASE ARM REPRODUCES WAVE 13 AND
  WAVE 14 ON 10 OF 10 DRAWS.**  CONTROL 30.53 · 30.62 · 30.85 · 30.98 · 31.11
  (spread 0.58); RETENTION 31.15 · 31.82 · 32.43 · 32.53 · 32.75 (spread 1.60);
  seed-2 CONTROL `−1.506 ns / 8,024 ALMs`; manifest `d4ecdeff14444248…`.
  **Different day, different worktree, different wave — identical to the
  thousandth.**

---

## §5 Q-5 — **THE RECOVERED FRACTION.  BOTH CONFIGURATIONS CLOSE ON BOTH ARMS.**  **MET.**

Paired on the seed, `Δ` = base T_min − arm T_min (positive = the arm's arc is
shorter), 95 % CI from a **tabulated** t (df = 4, t = 2.776).
**CLOSES** = `worst-of-5` T_min ≤ 31.250 ns (≥ 32.0 MHz), no exception of any
kind.

### 5.1 CONTROL — gap **1.506 ns**, WAVE 14 ceiling **+6.293 ns**

| | per-seed Δ ns (1..5) | **paired mean** | 95 % CI | t | **worst-of-5** | **% of ceiling** | **CLOSES?** |
|---|---|---:|---|---:|---:|---:|---|
| **ARM-A `qripe_presel`** | +3.067 · +2.449 · +2.546 · +2.801 · +3.370 | **+2.847** | **[+2.377, +3.316]** | **+16.8** | 30.53 → **33.00** | **45.2 %** | **YES** |
| **ARM-B `qripe_s1q`** | +3.314 · +3.919 · +3.771 · +3.270 · +4.051 | **+3.665** | [+3.224, +4.106] | +23.1 | 30.53 → **34.48** | **58.2 %** | **YES** |

### 5.2 RETENTION — **THE SHIPPING CONFIGURATION** — gap **0.855 ns**, ceiling **+4.688 ns**

| | per-seed Δ ns (1..5) | **paired mean** | 95 % CI | t | **worst-of-5** | **% of ceiling** | **CLOSES?** |
|---|---|---:|---|---:|---:|---:|---|
| **ARM-A `qripe_presel`** | +1.107 · +0.989 · +2.662 · +1.085 · +1.302 | **+1.429** | **[+0.562, +2.296]** | **+4.57** | 31.15 → **33.20** | **30.5 %** | **YES** |
| **ARM-B `qripe_s1q`** | +2.256 · +1.845 · +3.727 · +1.676 · +2.623 | **+2.425** | [+1.413, +3.438] | +6.65 | 31.15 → **34.41** | **51.7 %** | **YES** |

> ### **THE ANSWER, PLAINLY.**
>
> **A BEHAVIOUR-PRESERVING MECHANISM EXISTS, IT NEEDED 23.9 % / 18.2 % OF
> WAVE 14's CEILING, AND IT DELIVERS 45.2 % / 30.5 % WITH NO FLOP AND NO SDC
> EXCEPTION.  IT CLOSES CONTROL AND IT CLOSES RETENTION.**  The lower bound of
> every one of the four confidence intervals is above the gap it has to clear.
>
> ⚠ **`standing_gates.md` §A GOVERNS.**  These are `worst-of-5` figures from one
> instrument on one machine; one green build is not closure, and the same tree
> has drawn 19.42 and 45.91 MHz in this project's history.  **This wave lands
> nothing and no figure in it is a design Fmax.**

### 5.3 THE CENSUS LAW, SCORED AGAIN — **AND IT MISSED LOW AGAIN**

The pre-registration §2.2 wrote down a **census-shaped guess of ~1.2 ns**,
explicitly *not* as a prediction, from the 3 LUT levels / 1.777 ns the excursion
occupied on the base's worst arc.

| | census-shaped guess | **measured** | ratio |
|---|---:|---:|---:|
| CONTROL | 1.2 ns | **+2.847** | **2.4× UNDERSTATED** |
| RETENTION | 1.2 ns | **+1.429** | 1.2× understated |

WAVE 14 measured this same mechanism's census **2.3× / 1.7× low**; WAVE 8
measured `ucrom` **5.9× high** and WAVE 10 measured this mechanism on the
unsplit tree **5.3× high**.  **A CENSUS RANKS CANDIDATES AND DOES NOT SIZE THEM,
IN EITHER DIRECTION.  The law is now five for five.**

### 5.4 THE OTHER TWO EXPECTATIONS §2.2 WROTE DOWN

| expectation | outcome |
|---|---|
| *"RETENTION closes and CONTROL is marginal"* | ⚠ **WRONG, AND RECORDED AS WRONG.**  CONTROL recovered the LARGER fraction (45.2 % vs 30.5 %) and cleared its bar by **+1.00 MHz**; RETENTION cleared by **+1.20 MHz**.  Both closed comfortably. |
| *"the design does not shrink"* | **RIGHT.**  `v30_core` combinational ALUTs grew on every arm: BIU 1,112 → 1,151 (ARM-A ctl) / 1,285 (ARM-B ctl), EU 4,969 → 5,075 / 5,142; whole-design ALMs 8,024 → 8,273 / 8,429 at seed 2. |

---

## §6 Q-6 — **REGISTER ACCOUNTING.  ARM-A ADDS NO FLOP; ARM-B ADDS EXACTLY THE ONE IT DECLARED.**  **MET.**

| | `ss_lint` | `SS_COUNT` / flops | `map_registers` | `v30u_biu` regs | **`v30u_eu` regs** |
|---|---|---|---:|---:|---:|
| base ctl / ret | PASS | **232 / 229 / 0 UNMAPPED** | 5,686 / 5,708 | 434 | **1,326** |
| **ARM-A** ctl / ret | PASS | **232 / 229 / 0 — IDENTICAL** | 5,687 / 5,708 | 434 | **1,326 — NOT ONE FLOP** |
| **ARM-B** ctl / ret | PASS | **232 / 229 / 0 — IDENTICAL** | 5,688 / 5,709 | 434 | **1,327 — +1, AS DECLARED** |

* **ARM-A adds no flop and the compiler's own per-entity count says so** on all
  ten of its draws.
* **ARM-B's one flop is `s1q` 778 → 779 bits**, declared in the pre-registration
  §4 **before it was built**, and it shows up in the compiler's count as
  `v30u_eu` **1,326 → 1,327**.
  ⚠ **`ss_lint`'s census does NOT move, and that is correct, not a miss**: it
  counts flops **by name**, `s1q` is one whitelisted DERIVED-state name, and a
  1-bit widening of it changes no save-state address.  `SS_VERSION` 0x8F,
  `SS_COUNT` 232, `SS_TAG` 0x8FE8 are unmoved on all three arms.
* ⚠ **`sw/wave15_arms.py`'s textual "no non-blocking assignment" check PRINTS
  "no flop added" FOR ARM-B, AND THAT IS THE CHECK BEING WRONG.**  ARM-B's flop
  arrives as a **parameter widening**, which no `<=` scan can see.  Recorded in
  A-2.5 **before ARM-B was built**, and the compiler's count is the authority.
* ⚠ **The whole-design `map_registers` wobbles by ±1 between arms** (5,686 /
  5,687 / 5,688), OUTSIDE `v30_core` — the same unexplained class as WAVE 14
  §3.4 and WAVE 7's `sys_top` 424 → 422.  **Recorded, not explained.**
* **`fit_registers` VARIES across the seeds of every sweep** (physical synthesis
  duplicates registers) and is therefore **not read as evidence**, exactly as
  WAVE 14's scorer selftest established before this wave began.

---

## §7 Q-7 — **NOTHING IS LANDED.**  **MET.**

* `git status --porcelain hdl/` (tracked): **0 at the start, 0 at the end.**
  The main tree's `hdl/` was **never written by this wave at all** — every arm,
  the base included, lives in a scratch git worktree under
  `~/.cache/ucsimt-tmp/wave15/`.
* **No file under `hdl/` is modified by any commit of this wave.**
* **THIS WAVE ADDS NO `hdl/*.log`** — checked against `ls hdl/*.log`, not
  against recall: the 14 pre-existing untracked `quartus_gate_*.log` files are
  byte-untouched with their original dates, and every Quartus transcript of this
  wave went to `--log` inside the arm's own worktree and is committed under
  `sw/testdata/wave15/`.
* The 21 pre-existing modified files that are the **user's own uncommitted
  work** are untouched.  ⚠ **`git stash`, `git checkout .` and
  `git reset --hard` WERE NEVER USED**; `git add` was **BY EXPLICIT PATH ONLY**
  on every commit; `hdl/nec_test_ucore.qsf` was restored by
  `git checkout -- <that exact path>` in the arm's own worktree only.

---

## §8 Q-8 — **A LEGAL MECHANISM WAS FOUND.  F7 IS NOT WEAKENED.**

The Q-8 escape was not needed and was not used.  **F7 is untouched**: the step
still reads the BIU's next level including this clock's own pop, the 181
goldens all pass, and the RTL `$fatal`s every clock the published pair composed
with the EU's select fails to equal the original predicate.  **What changed is
which side of the module boundary the selection happens on** — the BIU answers
both questions off its own registers, and the EU, which is the one who knows
what it is doing, picks.

---

## §9 THE BARS, SCORED

| bar | verdict |
|---|---|
| **Q-1** derivation + enumeration committed before a candidate is chosen | **MET.**  `96dd1030cb` (eight candidates, no winner named) then `2dbeb896fd` (the choice + the bars).  Neither touches `hdl/`. |
| **Q-2** equivalence, in full, before any timing figure | **ARM-A: BEHAVIOURALLY MET IN FULL** — every leg identical to the base including the 181 goldens, `ulockstep` 17,350, four byte-identical `chain_lfsr` signatures and `fz2_replay` 305 × 11 — **with ONE STRUCTURAL LINT FAILING (`cutset_lint` X4), which §2.4 shows is a finding about the tree.**  **ARM-B: MET IN FULL**, `cutset_lint` included. |
| **Q-3** the round trip measurably gone, with a mandatory positive control | ⚠ **SPLIT, AND REPORTED AS REGISTERED.**  The control PASSES (base 200/200 on both columns, every invocation).  **Q-3a MISSED 200/200 on all four arm legs — and the cause is measured: a substring matcher now matching the EU's own mux node (§3.2).**  **Q-3b MET on ARM-A/CONTROL (0 of 200)** and MISSED on the other three (30 / 200 / 8).  The discriminating quantity — BIU nodes in the data section — falls **200 → 0** (ARM-A ctl), **200 → 30** (ARM-A ret), **200 → 8** (ARM-B ret), with the mean excursion **2.149 → 0.000** and **2.562 → 0.183 ns**. |
| **Q-4** paired, ≥ 5 seeds, both configurations, one driver, one seed set, E11 true | **MET.**  6 sweeps / 30 fits, seed set {1,2,3,4,5}, one driver, arms strictly sequential; **E11 `pass` on all 6 distributions and all 30 per-seed receipts**; three manifests identical within each arm; `off_class` EMPTY on all 30; **and the base reproduces WAVE 13/14 on 10 of 10 draws exactly.** |
| **Q-5** the recovered fraction, stated against ceiling and gap | **MET.**  CONTROL **+2.847 ns [+2.377, +3.316] = 45.2 %** of 6.293 against a 1.506 gap; RETENTION **+1.429 ns [+0.562, +2.296] = 30.5 %** of 4.688 against 0.855.  **BOTH CLOSE.**  ARM-B: 58.2 % / 51.7 %.  `worst-of-5` reported for every arm. |
| **Q-6** register accounting; any added flop named, counted, justified | **MET.**  ARM-A: `v30u_eu` 1,326, `v30u_biu` 434 — **not one flop**, on all ten draws.  ARM-B: **1,327, the single declared flop**, and `SS_COUNT`/`SS_VERSION`/`SS_TAG` unmoved because `s1q` is derived state.  ⚠ The generator's textual flop check cannot see a parameter widening, recorded before ARM-B was built. |
| **Q-7** `hdl/` clean at start and end; nothing landed | **MET.**  0 and 0; `hdl/` never written; no new `hdl/*.log`; the user's 21 modified files untouched. |
| **Q-8** if no legal mechanism, say so | **NOT EXERCISED — one was found**, and F7 was not weakened to get it. |
| §2.2 item 1 (the ~1.2 ns census guess) | ⚠ **WRONG, AND RECORDED AS WRONG.**  2.4× understated on CONTROL. |
| §2.2 item 2 (*"RETENTION closes, CONTROL marginal"*) | ⚠ **WRONG, AND RECORDED AS WRONG.**  CONTROL recovered the larger fraction. |
| §2.2 item 3 (*"the design does not shrink"*) | **RIGHT.**  ALUTs grew on every arm. |
| A-2.4's prediction (*"C1 cannot remove the arc from the `ce → ce` cone"*) | ⚠ **HALF WRONG, AND RECORDED AS WRONG.**  The BIU excursion is gone from **200 of 200** CONTROL paths; the select does still launch in stage 1; C1 closes both configurations regardless. |

---

## §10 WHAT IS OWED

1. ⚠⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND WAS DOUBLED AT
   WAVE 12.  IT IS STILL OWED.**  **A fabric figure taken on FLASH #21 or
   earlier may not be quoted against this tree.**  Nothing was flashed here and
   **this wave lands nothing, so it adds no new debt.**
2. **THE LANDING IS TWO LANDINGS, NOT ONE.**  Every figure above is on the
   **SPLIT** tree, and **the split does not currently land** (WAVE 13 N-1
   failed).  A landing wave must land the split and then land C1 — each with its
   own pre-registration, and the second scored against the first.
   ⚠ **And the choice between ARM-A and ARM-B is a real decision, not a
   ranking**: ARM-A is **split-independent and adds no flop** but leaves
   `cutset_lint` X4 firing; ARM-B **passes every lint** and is worth ~0.8–1.0 ns
   more, but **adds a flop and is meaningless without the cut.**  *Neither is
   recommended here; both are measured.*
3. **`q_flush` IS THE RESIDUAL AND ITS SIZE IS MEASURED** — 2 LUT levels,
   ~0.5 ns, on 200 of 200 ARM-B CONTROL paths.  Splitting it is the same
   mechanism's third level and is **not taken**, because it is not needed and
   because taking it in the wave that measured it is how a result gets chosen.
4. ⚠ **`fz2_replay` IS VACUOUS IN A GIT WORKTREE AND EXITS 0** (§2.3).  The
   repair here was a symlink made by hand.  **A permanent fix belongs in
   `fz2_replay.py` itself — refuse a zero-row population — and is BOOKED, not
   taken.**
5. ⚠ **`sw/wave14_ceiling.py` MUST BE RUN WITH ITS CWD IN THE ARM's WORKTREE**
   (§4).  Run from elsewhere it silently reports every per-seed column as `None`
   and E11 as FAIL.  Booked.
6. ⚠ **THE Q-3a COLUMN IS CONFOUNDED BY THIS MECHANISM** (§3.2) and any future
   wave quoting `sta_biu_roundtrip.tcl`'s `q_ripe_lead_n` counter against a tree
   carrying C1 must use the BIU-node column instead.  **A membership-scoped
   replacement is one clause away; NOT taken here**, for the same reason as (3).
7. **`sta_cutset_diag.tcl`'s C-8 string classifier still under-reports**
   (WAVE 14 §9 item 3) and **the ±1 whole-design register wobble is still
   unexplained** (WAVE 14 §9 item 4).  Both inherited, neither touched.
8. **`check_core --ss-sweep` IS STILL NOT ON ANY REGISTERED LADDER** — booked by
   WAVES 2, 3, 4, 9, 13 and 14.  **Booked for the seventh time.**
9. **`docs/notes/standing_gates.md` AND `CLAUDE.md` ARE NOT EDITED BY THIS
   WAVE.**  The coordinator decides (the WAVE 11–14 precedent).  Still
   unregistered: the stale `ss_lint` row, WAVE 12's bar `E11`, and now
   **`test_quartus_gate` 286 vs the briefed 287** (§2.5).

---

## §11 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NOTHING PROGRAMMED.**
* **NOTHING IS LANDED.**  `hdl/` in the main tree was never written.
* Single-writer guard before every Quartus stage, **`pgrep -x` by EXACT BINARY
  NAME, ONE PATTERN PER CALL**; ⚠ `pgrep -f <script>` self-matches and was never
  used.  **The waits BLOCKED; they did not poll a turn.**  All three arms ran
  **strictly sequentially** through one wrapper so no two stages could race.
* The driver carries **`set -u`, NOT `set -e`** — `quartus_gate` exits non-zero
  on RED and the base arm was expected to, and did, draw RED twice.
* ⚠ **`git stash`, `git checkout .` and `git reset --hard` WERE NEVER USED.**
  `git add` **BY EXPLICIT PATH ONLY**.
* `~/.cache/ucsimt-tmp/wave15/` for every intermediate; nothing in `/tmp`.
* **CONTENT COMPARED, NOT A SELF-COMPUTED DIGEST**: `fz2_replay` is compared
  **field by field by name** and the comparator **refuses a zero-row
  population**; the `chain_lfsr` signatures are the tool's own; the WAVE 13/14
  reproduction is draw by draw over ten draws.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL**, reported first, and this wave
  caught **two** vacuous or confounded instruments with them (§2.3, §3.2).
* No Codex.  No nested subagent.
* **No figure in this wave is a receipt, a gate or a design Fmax.**
  `standing_gates.md` §A governs; one green build is not closure.
* **Record what was measured, not what was expected** — and §9's last four rows
  are four expectations that were wrong, left visible.

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
