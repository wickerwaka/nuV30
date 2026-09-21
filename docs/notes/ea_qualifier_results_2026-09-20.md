# WAVE 26 — RESULTS.  **ONE QUALIFIER, ONE MUX, AND THE RETAINED EA LANE IS SILICON-EXACT: `stale_ea_probe` 7 / 13 → 13 / 13, AND 21 / 21 WITH THE EIGHT `mod=01/10` ROWS THAT DID NOT SELECT THE RULE.**

Pre-registration `86b33eeebb`
(`docs/notes/ea_qualifier_prereg_2026-09-20.md`), committed **before the first
`hdl/` edit**; board addendum + rig `a1e1d7a4d6`
(`docs/notes/ea_qualifier_board_prereg_2026-09-20.md`), committed **before the
first board contact**.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

**THIS EDIT MOVES THE BITSTREAM.  NOTHING WAS FLASHED.  A RE-FLASH IS OWED —
§9.**

---

## §1  THE HEADLINE

| | |
|---|---|
| **the rule, in one sentence** | *The address adder's B rail is loaded on EVERY EA calculation with the SECOND ADDEND — the index register where the form has one and nothing is added after it, the displacement otherwise, and ZERO where there is nothing to add.* |
| **the edit** | **ONE MUX AND ONE CONSTANT** in `hdl/rtl/ucore/v30u_eu_arm_ea_calc.svh`: `ea_pair_valid_n = 1'b1;` and a single conditional expression replacing a three-branch `if` chain.  **No new flop, no new save-state address, no opcode named, no `mod`-specific branch, no table.** |
| **W-2, the POINT prediction** | ⭐ **MET EXACTLY.  `sw/b2_ea_lane_ucore.py` 7 / 13 → 13 / 13**, and the four rows that already matched (`M0`–`M3`) **did not move** |
| **the silicon bar** | ⭐ **21 / 21 ON A FRESH DIRECTED SOCKET CAPTURE**, thirteen WAVE 24 controls **all REPRO** plus **eight `mod=01/10` rows that did not select the rule** — every one hit on the point |
| **an unplanned second silicon reference** | ⭐ **`lea_mod3_gate`'s L4 went `2 of 2 DIVERGE` → `0 of 2`**: the fixed core now reproduces the **FROZEN 2026-07-27** `stale_ea_probe` rows `0x4121` and `0xD4E5` exactly — a different rig, a different date, an artifact nobody touched |
| **G6-A** | **MET** — anchored SDC exception count **0**.  **No exception was added, considered or needed** |
| **G6-D** | **MET, BOTH EXACT** — `cutset_lint` **81 / 0**, `phase_split_lint` **157 / 779 / 0**.  **S-3 did not fire: no pre-cut wire was wanted** |
| **G6-E** | **MET, AND THE DECLARED DELTA WAS NOT USED** — `ss_lint` **232 / 229 flops / 4 whitelist / 0 UNMAPPED, UNMOVED**, no `SS_VERSION` bump |
| **`mod3_illegal`** | **UNMOVED — ARCH 0 / 128, cycles 128 / 128**, exactly as P-4 registered.  **NOT re-captured** (§7) |
| **fabric** | ⚠ **FLASH #23 NO LONGER COVERS THIS TREE.  A RE-FLASH IS OWED AND WAS NOT TAKEN.** |

---

## §2  THE DEFECT, RE-DERIVED FROM THE TREE — **VERIFIED, NOT INHERITED**

⚠ **THE BRIEF'S OWN SENTENCE IS NOT WHAT THE TREE SAYS, AND THE USER RULING OF
2026-09-19 IS WHY IT WAS CHECKED.**  The brief (quoting
`suite_divergence_results_2026-09-20.md` §6.3) says *"`ea_residue` … **is
written under `ea_pair_valid`**"*.  It is not: `v30u_eu_arm_ea_calc.svh:35`
assigns `ea_residue_n = ea` **unconditionally**, and `ea_pair_valid` guards a
DIFFERENT rail.  **The mechanism is one qualifier, as the brief says, but it is
the qualifier on the OTHER rail.**

**WHAT THE TREE ACTUALLY DID, DERIVED READ-ONLY** — whole-program replays with
ONE register (or the body address) perturbed at a time, no RTL edit, no
backdoor injection (`sw/testdata/wave26/decomp.txt`):

| probe | base | `AW+1` | `BW+1` | `IX+1` | `IY+1` | `BP+1` | body `PC+0x10` |
|---|---|---|---|---|---|---|---|
| `C3` `90` | `2222` | **+2** | 0 | 0 | 0 | 0 | 0 |
| `M0` `89 00` | `8888` | **+1** | 0 | **+1** | 0 | 0 | 0 |
| `M4` `89 04` | `9211` | **+1** | 0 | 0 | 0 | 0 | **+16** |
| `M6` `89 06 34 12` | `9211` | **+1** | 0 | 0 | 0 | 0 | **+16** |
| `M7` `89 07` | `9211` | **+1** | 0 | 0 | 0 | 0 | **+16** |

Read against `v30u_eu_arm_bind.svh`'s mod-3 arm (`tmpa_n = ea_residue_n;
if (ea_pair_valid_n) tmpb_n = ea_pair_rhs_n;`):

* **the `0x8100` in every diverging row is `tmpb`, NOT `ea_residue`** — it is
  the loader's own branch target, still standing in the ordinary scratch latch
  because the predecessor never wrote `tmpb`, and it **tracks the body address
  exactly** (`+16` for `PC+0x10`).  `ea_residue` carries `AW` on every one of
  these rows, which is why `AW+1` moves them all by exactly one;
* **on the two-register forms the ucore's sum was RIGHT WITH THE ROLES
  SWAPPED**: silicon holds the index on the retained rail and the moved datum
  on the scratch; the ucore held the datum on the retained rail (ordinary
  `tmpa` writes refresh it, `v30u_eu_step.svh:399`) and the index on
  `ea_pair_rhs`.  **Two wrongs summing to the right number is why `M0`–`M3`
  passed and why the defect survived.**

> **THE SIMPLE SYSTEM UNDERNEATH, WHICH IS WHY ONE MUX IS ENOUGH**: there is no
> special "retained EA lane".  There is **the address adder, which is the ALU**,
> and its two operand latches.  An EA calculation loads them and adds; `8D` at
> `mod == 3` issues no EA calculation, so its row-1 `SIGMA -> R` adds **whatever
> the adder was last given**.  `ea_residue` and `ea_pair_rhs` are the model's
> names for those two inputs, and the only thing the tree had wrong was **what
> the B input is loaded with, and when.**

---

## §3  THE EDIT

```diff
-    // Only the four two-register address forms select a distinct RHS rail.
-    // Remember both that select and the index value; a later unary EA clears
-    // the select but leaves tmpb itself to evolve exactly as before.
-    ea_pair_valid_n = (rmrm <= 3'd3);
-    if ((rmrm == 3'd0) || (rmrm == 3'd2))
-        ea_pair_rhs_n = gpr_n[R_IX];
-    else if ((rmrm == 3'd1) || (rmrm == 3'd3))
-        ea_pair_rhs_n = gpr_n[R_IY];
+    ea_pair_valid_n = 1'b1;
+    ea_pair_rhs_n = ((rmmod == 2'd0) && (rmrm <= 3'd3))
+                  ? (rmrm[0] ? gpr_n[R_IY] : gpr_n[R_IX])
+                  : ld_disp_n;
```

**WHY THAT IS THE WHOLE RULE AND NOT A THREE-WAY CASE.**  `ld_disp_n` is
**zero on any form that carries no displacement** (`v30u_eu_step.svh:157`
clears it at the ModR/M take and only the three displacement paths write it),
so *"the displacement, and zero when there is none"* is **one operand, not
two branches**.  The only genuine choice left is *"index, or the thing added
after it"* — and `mod == 0` with `rm <= 3` is exactly the case where no
displacement follows the index.  **One select, one mux.**

⚠ **`mod == 3` NEVER REACHES THIS ARM** — `v30u_eu_step.svh:165` routes it
straight to `S_BIND` — so the `rmmod` term has three live values and the
expression is complete over them.

**`ea_pair_valid` CHANGES MEANING AND THE COMMENTS SAY SO.**  It no longer
means *"the EA had a register pair"*; it means *"the rail still holds what the
EA calculation put there — no `tmpb` write has replaced it since"*, which is
what the clear beside every `tmpb` write (`v30u_eu_step.svh:368` / `:400`,
`v30u_eu.sv:3822`) already implemented.  **It is still a real flop**: with it
forced high, `C3` (`NOP`, which writes `tmpb` itself) would read the stale
rail instead of `tmpb` and would be wrong.

**THE DIFF**, `git diff --stat` at the landing:

```
 hdl/rtl/ucore/v30u_eu.sv              | 27 +++++++++++++++++-------
 hdl/rtl/ucore/v30u_eu_arm_bind.svh    | 13 ++++++++-----
 hdl/rtl/ucore/v30u_eu_arm_ea_calc.svh | 25 ++++++++++++++--------
 hdl/rtl/ucore/v30u_eu_step.svh        |  7 ++++---
```

**Of those, exactly SEVEN lines are code** — the five above plus the two
`v30u_eu_arm_ea_calc.svh` lines they replace.  **Everything else is comment**,
and three of the four files are comment-only: they carry the sentences silicon
has now refuted (§8, D-1 and D-2), which WAVE 23 booked and declined to fix
**because a comment edit costs a Quartus sweep** — and this wave is paying for
one anyway.

---

## §4  W-2 — THE POINT PREDICTION, MET EXACTLY

```
sw/b2_ea_lane_ucore.py         BEFORE  MATCH  7 / 13   DIVERGE 6 / 13
                               AFTER   MATCH 13 / 13   DIVERGE 0 / 13
```

| tag | predecessor | form | **silicon** | before | **after** |
|---|---|---|---:|---:|---:|
| `C1` `A3 34 12` | `MOV [1234h],AW` | no ModR/M | `1234` | `1234` | **`1234`** |
| `C2` `A3 EF BE` | `MOV [BEEFh],AW` | no ModR/M | `BEEF` | `BEEF` | **`BEEF`** |
| `C3` `90` | `NOP` | no EA | `2222` | `2222` | **`2222`** |
| `R1` `88 26 10 30` | `MOV [3010h],AH` | `mod=00 rm=110` | `4121` | `9211` ✗ | ⭐ **`4121`** |
| `R2` `8B 0E 55 44` | `MOV CW,[4455h]` | `mod=00 rm=110` | `1121` | `4DCC` ✗ | ⭐ **`1121`** |
| `M0`–`M3` `89 00…03` | two-register | `mod=00 rm<=3` | `8888` `9999` `8888` `9999` | same | **same — UNMOVED** |
| `M4` `89 04` | `[IX]` | `mod=00 rm=100` | `1111` | `9211` ✗ | ⭐ **`1111`** |
| `M5` `89 05` | `[IY]` | `mod=00 rm=101` | `1111` | `9211` ✗ | ⭐ **`1111`** |
| `M6` `89 06 34 12` | `[1234h]` | `mod=00 rm=110` | `2345` | `9211` ✗ | ⭐ **`2345`** |
| `M7` `89 07` | `[BW]` | `mod=00 rm=111` | `1111` | `9211` ✗ | ⭐ **`1111`** |

**WAVE 24 §6.3's REGISTERED FALSIFIER IS DISCHARGED IN BOTH OF ITS CLAUSES**:
*"all thirteen rows must read MATCH, and the four that already MATCH must not
move."*  **13 / 13, and `M0`–`M3` byte-identical.**

---

## §5  THE SILICON BAR — **21 / 21, AND THE EIGHT NEW ROWS DID NOT SELECT THE RULE**

`sw/w26_ea_lane2.py`, socket capture 2026-09-20, `8D.json.gz` sha256
**`d0fea3a937fa83fb…`**, manifest **`1f246035b04407c5…`**, divider readback
**`div=8 (4 MHz), commanded by this connection`** on every probe.

**THE THIRTEEN CONTROLS ALL REPRO**, against WAVE 24's capture read out of the
artifact rather than hard-coded: `C1 1234 · C2 BEEF · C3 2222 · R1 4121 ·
R2 1121 · M0 8888 · M1 9999 · M2 8888 · M3 9999 · M4 1111 · M5 1111 ·
M6 2345 · M7 1111` — **13 of 13, no row moved.**  (`R2` reads `1121`, so the
composer's fill is still `0xCC`; had it read `D4E5` that would have been a
finding about the composer, and it was registered as one in advance.)

**THE EIGHT GAP-CLOSING ROWS — `mod = 01` AND `mod = 10`, PREDICTED IN
`a1e1d7a4d6` BEFORE THE SOCKET WAS TOUCHED:**

| tag | predecessor | form | **predicted** | **SILICON** | ucore | the reading it REFUTES |
|---|---|---|---:|---:|---:|---|
| `P0` | `89 40 10` | `[BW+IX+10h]` | `1121` | **`1121`** | `1121` | *B = the index* → `8888` |
| `P1` | `89 40 00` | `[BW+IX+0]` | `1111` | **`1111`** | `1111` | ⭐ *B = the index when the displacement is ZERO* → `8888` |
| `P2` | `89 46 10` | `[BP+10h]` | `1121` | **`1121`** | `1121` | *B = 0 on a one-register form* → `1111` |
| `P3` | `89 84 34 12` | `[IX+1234h]` | `2345` | **`2345`** | `2345` | *B = 0 on a one-register form* → `1111` |
| `P4` | `89 81 34 12` | `[BW+IY+1234h]` | `2345` | **`2345`** | `2345` | *B = the index* → `9999` |
| `P5` | `89 45 20` | `[IY+20h]` | `1131` | **`1131`** | `1131` | *B = 0* → `1111` |
| `P6` | `89 87 34 12` | `[BW+1234h]` | `2345` | **`2345`** | `2345` | *B = 0* → `1111` |
| `P7` | `89 44 F0` | `[IX−10h]` | `1101` | **`1101`** | `1101` | *B = 0* → `1111`; *B = the UNSIGNED disp8* → `1201` |

⭐ **`P1` IS THE ROW THAT MATTERS.**  A `mod = 01` form whose displacement is
**zero**: *"the form carries a displacement"* predicts `1111`, *"the
displacement is non-zero"* predicts `8888`, and **silicon says `1111`.**  The
RTL implements the former, and it was written that way **before** the probe
existed, for the structural reason (the adder is given the displacement
because the form has one), not because a measurement chose it.

⭐ **`P7` PINS THE SIGN.**  A negative `disp8` reaches the rail
**sign-extended** (`FFF0`, giving `1101`), not as the raw unsigned byte
(`1201`).

> **THE WHOLE POINT OF THESE EIGHT IS THAT THEY WERE NOT USED TO PICK THE
> RULE.**  The rule was fixed by WAVE 24's thirteen `mod = 00` rows; the RTL
> was written and built against those thirteen; only then were the eight
> composed, their values registered, and the socket touched.
> **`CLAUDE.md`'s standing rule — *a refuted key's REPLACEMENT must be
> validated on data that was not used to select it* — is satisfied, and it is
> satisfied on the point, 8 of 8.**

⚠ **WHAT IS STILL NOT MEASURED**: `mod = 01`/`mod = 10` at `rm = 110`
(`[BP+disp]`) is measured (`P2`), but nothing here probes a form with a
**segment override**, a **byte** displacement on a two-register form other
than `P0`/`P1`, or a `mod = 10` two-register form other than `P4`.  Those are
predicted by the same one sentence and are **not claimed as measured.**

### §5.1  ⭐ THE UNPLANNED THIRD REFERENCE — **`lea_mod3_gate`'s L4, AGAINST AN ARTIFACT NOBODY TOUCHED**

WAVE 23 built `sw/lea_mod3_gate.py` with an L4 leg that replays the two
ModR/M-predecessor rows of the **FROZEN 2026-07-27** `stale_ea_probe`,
reproducing that era's image fill through `compose(ram=…)` so the stimulus is
the capture's.  It has read **`2 of 2 … DIVERGE`** since the day it was
written.

```
  L4  MOV[3010h],AH   silicon 0x4121   ucore 0x4121  MATCH   (REPORTED, NOT A BAR)
  L4  MOV CW,[4455h]  silicon 0xd4e5   ucore 0xd4e5  MATCH   (REPORTED, NOT A BAR)
  L4  KNOWN-RED  0 of 2 ModR/M-predecessor silicon row(s) DIVERGE
```

**A DIFFERENT RIG, A DIFFERENT DATE, A DIFFERENT IMAGE FILL, AND AN ARTIFACT
THIS WAVE DID NOT TOUCH — AND BOTH ROWS CLOSE.**  `0xD4E5 = 0x4455 + 0x9090`
where `0x9090` is the v1 composer's fill; the same instruction on today's
`0xCC` fill reads `0x1121` on the same silicon and on the fixed core.  *The
law holds across the one term that moved.*

**THIS IS A LADDER LEG THAT MOVED**, and it is attributed here rather than
folded into the "zero-delta" claim.  The gate's **exit status is unchanged
(PASS)**; L4 is explicitly not a bar.

---

## §6  THE LADDER — **BOTH SIDES MEASURED, 36 LEGS, ONE MOVED AND IT IS THE ONE THAT SHOULD HAVE**

`RC` captured with `${PIPESTATUS[0]}`, never `tail`'s.  Raw logs by value at
`sw/testdata/wave26/ladder/{before,after}/`.

⚠ **HOW THE AFTER COLUMN WAS TAKEN, STATED PLAINLY.**  The AFTER side was run
in a `git worktree` while the BEFORE side ran on the main tree, so the two
columns are wall-clock parallel.  **That is legitimate here because the
Verilator `build_key` — the hash of the declared input set — is IDENTICAL on
the two trees, `340b3a9b7bd64523…`**, measured after the landing.  Same
declared inputs, same goldens, same scorer.  The confirmation subset was
additionally re-run on the LANDED main tree
(`sw/testdata/wave26/landed/confirm.log`).

| leg | command | **BEFORE** | **AFTER** | |
|---|---|---|---|---|
| `check_core` | `--core ucore --opcodes all --cases 0 --ce-div 4` | 169,000 / 169,000 | **169,000 / 169,000** | log byte-identical |
| `check_core` | `… --ce-div 2` | 169,000 / 169,000 | **169,000 / 169,000** | byte-identical |
| `check_core` | `… --ce-div 3` | 169,000 / 169,000 | **169,000 / 169,000** | byte-identical |
| `check_core` | `… --ce-div 8` | 169,000 / 169,000 | **169,000 / 169,000** | byte-identical |
| `check_core` | `… --ce-div 1` | **exit 2**, clause C-a named | **exit 2**, clause C-a named | byte-identical |
| HLT sweep `s10-w0` | `--waits 0` | 97 / 97 | **97 / 97** | byte-identical |
| HLT sweep `s10-w1` | `--waits 1` | 93 / 95 | **93 / 95** | byte-identical |
| HLT sweep `s13-w2` | `--waits 2` | 45 / 46 | **45 / 46** | byte-identical |
| HLT sweep `s13-w3` | `--waits 3` | 44 / 45 | **44 / 45** | byte-identical |
| *the four sweeps* | | **279 / 283** | **279 / 283** | the same four survivors |
| `v0.2` | `--suite-dir tests/v30/v0.2 --opcodes all --cases 0` | 347,000 / 347,000 | **347,000 / 347,000** | byte-identical |
| **`v0.3`** | `--suite-dir tests/v30/v0.3 --opcodes all --cases 0` | 3,699,998 / 3,699,998 [2 excluded] | **3,699,998 / 3,699,998 [2 excluded]** | ⭐ byte-identical, sha256 `644a11c5e09f38ed…` — **the same bytes as WAVE 24's registered run AND as WAVE 25's** |
| `v20suite` | `… --arch-only` | **3,125,000 / 3,125,000 ARCH** | **3,125,000 / 3,125,000 ARCH** | byte-identical (WAVE 25's figure, re-registered here) |
| `mod3_illegal` | `--suite-dir … --opcodes all` | 0 / 128 full (cycles 128, **arch 0**) | **0 / 128 (cycles 128, arch 0)** | byte-identical — **P-4 MET** |
| `v0.1-w1` | `--waits 1` | 1,200 / 1,200 | **1,200 / 1,200** | byte-identical |
| `v0.1-w3` | `--waits 3` | 1,200 / 1,200 | **1,200 / 1,200** | byte-identical |
| `v0.1-w1 --opcodes EB` | | 200 / 200 | **200 / 200** | byte-identical |
| `f4a_boundary` | | 160 / 160 | **160 / 160** | byte-identical |
| `f0lock_tranche` | | 400 / 400 | **400 / 400** | byte-identical |
| `check_boot` | `220` | MATCH over 220 rows | **MATCH over 220 rows** | only the receipt id differs |
| `check_boot` | `400` | MATCH over 400 rows | **MATCH over 400 rows** | only the receipt id differs |
| `check_ab_sim` | `--core ucore` | MATCH over 187 rows | **MATCH over 187 rows** | only a rebuild banner + receipt id |
| `ghost_launch_law` | `score` | 200 / 200 = 100.0 % | **200 / 200 = 100.0 %** | byte-identical |
| **`lea_mod3_gate`** | | **PASS**, L1 2/2 · L2 64/64 · L3 3/3 · **L4 `2 of 2` DIVERGE** | **PASS**, L1 2/2 · L2 64/64 · L3 3/3 · ⭐ **L4 `0 of 2`** | ⭐ **THE ONE LEG THAT MOVED — §5.1** |
| `chain_lfsr_gate` | | PASS, sigs `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78` | **PASS, ALL FOUR BYTE-IDENTICAL**, and every `ce_clocks` / `g0` / `coincide` count with them | ⭐ the chain walks the same states on the same clocks |
| **`chainflat_relocation_check`** | | PASS (9 arms byte-identical to `aba01feb07`) | ⚠ **FAIL with the WAVE 25 gate; PASS with the repair** | ⚠ **AN UNREGISTERED MISS — §6.1** |
| `demux_off_gate` | | PASS — 3 legs | **PASS — 3 legs** | only paths and walltime differ |
| `r7_lint` | | PASS — 41 `stop` sites, 0 violations | **PASS, identical** | byte-identical |
| **`ss_lint --core ucore`** | | PASS — **232** (109×2 BIU + 122×2 EU + tag), **229** flops, **4** whitelist, **0 UNMAPPED** | **PASS, IDENTICAL** | ⭐ **byte-identical — the ONE permitted delta WAS NOT USED** |
| `cutset_lint` | | PASS — 81 members / 0 violations | **PASS, identical** | byte-identical |
| `phase_split_lint` | | PASS — 157 members / 779 bits / 0 violations | **PASS, identical** | byte-identical |
| `test_artifact` | | 45 / 45, NON-VACUOUS | **45 / 45, NON-VACUOUS** | only the random self-test temp dir |
| `test_quartus_gate` | | **302 / 302**, PASS | **302 / 302**, PASS | byte-identical |
| `qsf_lint --check` | | CANONICAL | **CANONICAL** | byte-identical |
| `core_portlist_lint` | | PASS — 4 configurations | **PASS — 4 configurations** | byte-identical |
| `ucrom_mif_check` | | PASS | **PASS** | only the emitted-into path differs |
| `check_ucore_tables` (G0) | | PASS — **9,988** entries | **PASS — 9,988** | byte-identical |
| `pla3_check` | | OK — 21 checks | **OK — 21 checks** | byte-identical |

**36 LEGS · 1 MOVED (`lea_mod3_gate`'s L4, in the intended direction) · 1
UNREGISTERED MISS (`chainflat_relocation_check`, §6.1) · 34 ZERO-DELTA.**

**ARCHITECTURAL CASES RE-SCORED THIS WAVE: (169,000 × 4 + 347,000 + 3,699,998
+ 3,125,000 + 283 + 128 + 2,600 + 560) × 2 SIDES = 7,851,569 × 2 =
15,703,138**, plus the 21 directed socket probes, their 21 ucore replays on
each side, and 71 more inside `lea_mod3_gate`.

### §6.1  ⚠ THE UNREGISTERED MISS — **A STANDING GATE FROZE THE EU's `case (st_n)`, AND WAVE 26 IS THE FIRST WAVE TO EDIT IT**

`sw/chainflat_relocation_check.py`'s **G-12** required every one of the nine
arm bodies, and the whole reconstructed `case (st_n)`, to be **byte-identical
to `aba01feb07`** — WAVE 7's pre-flattening tree.  It is a *relocation*
falsifier and it did its job perfectly for four waves, because **no wave since
WAVE 7 had changed an EU arm.**  This one does, so the gate went RED:

```
  - G-12 S_EA_CALC: the carved body DIFFERS from aba01feb07
  - G-12 S_BIND:    the carved body DIFFERS from aba01feb07
  - G-12: the reconstruction does NOT match aba01feb07
```

**I DID NOT PREDICT THIS AND IT IS REPORTED AS AN UNREGISTERED MISS.**  The
pre-registration listed `chainflat_relocation_check` among the zero-delta
legs; that was wrong, and it was wrong for a reason worth writing down: *a
gate that pins a file to a historical commit forbids all future work on that
file, and nothing in the gate said so.*

**THE REPAIR KEEPS THE FALSIFIER LIVE RATHER THAN WIDENING IT.**

* **G-11 is unchanged in meaning** and now derives the nine bodies from the
  **CURRENT** arm files, so *"exactly one copy in `hdl/`"* keeps being checked
  however the bodies evolve.  It never needed the frozen reference.
* **G-12 still diffs the reconstruction against `aba01feb07`.**  What changed
  is that a deviation is permitted only if it is **DECLARED in the source and
  matches `DEVIATION['digest']` — the sha256 of the unified diff itself**.
  **One further edited character anywhere in the EU's `case (st_n)` moves that
  digest and the gate FAILS.**
* The declaration names its wave, its arms, its reason and its **code-hunk
  count (1 — the other two hunks are comment-only)**, and prints all of it on
  every run.

**THREE CONTROLS, ALL MEASURED:**

| control | result |
|---|---|
| the declared deviation in force on the landed tree | **PASS**, 7 arms byte-identical + 2 declared |
| a synthetic line spliced into `S_ENTER`'s body | digest `abb6954fe1a7…` → `139da5f0a5b2…`, **CAUGHT** |
| the same declaration against the **PRE-edit** tree | **FAIL — `STALE DECLARATION, remove it`** |

**LEDGERED** as `invalidation_ledger.md` **DEV-1**, a per-gate *declared
deviation* — no defect alleged, nothing retired, and the previous claim
(*"9 arms byte-identical to `aba01feb07`"*) is preserved as what it now is: a
claim about **seven** of them plus a pinned diff.

---

## §7  `mod3_illegal` — **UNMOVED AT `0 / 128`, AND DELIBERATELY NOT RE-CAPTURED**

```
check_core --core ucore --suite-dir tests/v30/mod3_illegal --opcodes all --cases 0
BEFORE  0/128 full (cycles 128, arch 0)
AFTER   0/128 full (cycles 128, arch 0)        -- logs BYTE-IDENTICAL
```

**P-4 MET.**  WAVE 23 §3 established why and this wave does not disturb it:
the 128 goldens have **no ModR/M predecessor at all**, so their outcome
depends on pre-window `ea_residue` (`0x0500` = `PC + PS`, left by the capture
harness's own terminal `BR PS:PC`), and `tb_v30_core.sv:1120` injects fourteen
architectural registers and nothing else.  **A golden whose outcome depends on
pre-window microarchitectural state is unscoreable by an injected engine by
construction**, and this fix — which changes the adder's **B** rail — cannot
reach it.

**THE BRIEF NAMED `B-3`, THE RE-CAPTURE, AS THIS WAVE'S SILICON BAR.  IT WAS
NOT TAKEN, AND THE REASONS WERE REGISTERED IN `a1e1d7a4d6` BEFORE THE
ALTERNATIVE WAS RUN:**

1. the suite is a **FROZEN artifact under WAVE 22's committed sha256 manifest
   `67161a0c409c7fc6…`**, and `sw/lea_mod3_gate.py`'s L1 and L4 legs read
   their expected values **out of its `metadata.json`** — replacing its
   goldens moves a frozen input to a live gate;
2. a declared-predecessor re-capture is **a different suite**, so `0 / 128`
   and the new figure would not be comparable and **the ratchet would be
   broken, not raised**;
3. the information it would buy is exactly what §5's eight rows bought, at
   ~30 s of board time, **with the frozen suite untouched** — and WAVE 24
   itself wrote that 128 more rows *"would add cases, not information"*;
4. **WAVE 24 §5's precedent** refused exactly this trade.

⚠ **THIS IS A DEVIATION FROM THE BRIEF AND IT IS THE COORDINATOR'S TO
REVERSE.**  Nothing is destroyed by not taking it; the route stays costed in
`suite_divergence_results_2026-09-20.md` §7, and §5.1 above shows the frozen
artifact's own two rows now close **without** re-capturing anything.

---

## §8  G6 — **SCORED, FIVE SEEDS PER CONFIGURATION, 10 OF 10 PASS**

| bar | result |
|---|---|
| **G6-A** `hdl/nec_test.sdc` exception-free | ⭐ **MET.**  Anchored `grep -cE '^[[:space:]]*(set_multicycle_path\|set_false_path\|set_max_delay)'` = **0**; the unanchored count is **2** and both are the commented DO-NOT-RESTORE record, **which is why the anchor is the instrument**.  `nec_test.sdc` is **byte-untouched** — it is not in the 4-file diff.  **No exception was added, considered or needed; S-2 never came close to firing** |
| **G6-B** `quartus_gate.py` PASSES | ⭐ **MET on all ten draws.**  Fmax ≥ 32 on 10 of 10 (min **33.76**), worst setup positive on 10 of 10 (min **+1.633 ns**), **TNS 0.000 setup AND hold on all four domains of all ten draws**, 0 error lines, 0 latches, 0 `lpm_divide`, E1 `qsf_lint --check` **CANONICAL**, E7 input stability with the one declared `.qsf` exemption, E11 build stamp ABSENT |
| **G6-C** no regression vs the no-exception baseline | ⚠ **MET AS REGISTERED, AND THE BASELINE COMPARISON IS REPORTED, NOT EXPLAINED** — see below |
| **G6-D** `cutset_lint` 81/0, `phase_split_lint` 157/779/0 | ⭐ **MET, BOTH EXACT**, byte-identical before and after.  **S-3 did not fire: the mechanism wanted no pre-cut wire, and the cut set was not widened** |
| **G6-E** `ss_lint` | ⭐ **MET, AND THE DECLARED DELTA WAS NOT USED.**  **232 addresses / 229 flops / 4 whitelist / 0 UNMAPPED**, byte-identical; **no `SS_VERSION` bump**; `v30u_ss_pkg.sv` untouched.  The edit changes what an existing rail is loaded with, and adds no state |

**THE PAIR, AS `standing_gates.md` §A REQUIRES IT:**

| | draws (seeds 1…5) | **`worst-of-5`** | ALMs | baseline (WAVE 19 / FLASH #23) | Δ |
|---|---|---:|---|---:|---:|
| **CONTROL** | 34.35 · 33.81 · 35.43 · **33.76** · 34.60 | **33.76 MHz** | 8,431 – 8,468 (20 %) | 34.48 | **−0.72** |
| **RETENTION** | 34.59 · 34.87 · **34.16** · 34.58 · 34.33 | **34.16 MHz** | 8,495 – 8,528 (20 %) | 34.41 | **−0.25** |

**THE FLOOR WAS REGISTERED AT 33.00 MHz BOTH CONFIGURATIONS, BEFORE THE SWEEP
(`86b33eeebb` P-7), AND BOTH CLEAR IT.**  Records
`sw/testdata/g6dist/WAVE26 ea second-addend {CONTROL,RETENTION}/`, ids
`d9da5f5bea833e45…` and `bbd1b0800a95a831…`; configuration **DERIVED from the
reports** as `CONTROL/DEFAULT (no X1_AD_RETENTION)` and
`RETENTION (X1_AD_RETENTION=1)` respectively (E-6), with **different `.rbf`s**
(`aa931892f7a69668…` vs `44cfd64791781752…`, E-9).

⚠ **THE MINUS SIGNS ARE REPORTED AND NOT EXPLAINED AWAY, AND ONE FACT BEARS ON
THEM**: **the binding cone is the MICROCODE ROM on all ten draws of both
configurations** —
`v30u_ucrom|altsyncram|…ram_block1a3~PORT_A_WRITE_ENABLE_REG →
…ram_block1a1~porta_address_reg4`, at `k = 1.0`, `off_class` SAME on every
reading.  **It is not the EU cone this edit touched**, and WAVE 7 already
recorded that the ROM became the binding structure.  The CONTROL spread on
this one netlist is **1.67 MHz over five seeds**, which is more than twice the
CONTROL delta; `standing_gates.md` §A governs and **one green build is not
closure.**  ⚠ ALMs rose ~20–70 on both configurations (CONTROL 8,413 → 8,431–
8,468).  **Recorded, not explained**; §74.4a says combinational counts are not
reproducible run to run.

---

## §9  W-5 — **THE FABRIC DEBT, PLAINLY**

| | |
|---|---|
| `git diff --stat -- hdl/` at the landing | **four files, all in `hdl/rtl/ucore/`** |
| the 107 files Quartus reads | **4 MOVED**: `v30u_eu.sv`, `v30u_eu_arm_bind.svh`, `v30u_eu_arm_ea_calc.svh`, `v30u_eu_step.svh`.  `sw/testdata/wave26/synth-manifest-{before,after}.txt`; the BEFORE manifest is byte-identical to WAVE 25's and WAVE 23's after-manifest |
| **FLASH #23** | ⛔ **NO LONGER COVERS THIS TREE.  A RE-FLASH IS OWED AND WAS NOT TAKEN.**  **NO FABRIC FIGURE TAKEN ON FLASH #23 OR EARLIER MAY BE QUOTED AGAINST THE LANDED TREE** |
| the board itself | **still carries FLASH #23**: `sw/testdata/flash_log.jsonl` **26 entries, sha256 `13a81a43f30c380a…`**, verified before AND after the board session, and **not in `git status`** |
| what a re-flash would need | a RETENTION build from this tree (the gate can make one: `sw/quartus_gate.py --retention`, exercised here for the first time on a landing), its own pre-registration, and a null population — **none of which is this wave's** |

⚠ **THE SOCKET LEG OF §5 IS UNAFFECTED BY THE DEBT** — its truth source is the
chip in the socket, not the FPGA core — and the ucore leg is Verilated from
the landed tree.  **No FPGA-side figure was taken in this session.**

---

## §10  BOARD HYGIENE

| | |
|---|---|
| authorisation | **CAPTURE ONLY.  NOTHING WAS FLASHED** |
| single-writer | `pgrep -x ssh` → **none** before first contact |
| `use_core` | **`False`, explicit** — `emit_suite.EMIT_USE_CORE` is `False`, the rig **REFUSES to start otherwise**, and the truth stamp recorded in the manifest reads `SOCKET (real chip, use_core=False)` |
| divider | `div_guard()` on every probe; readback **`div=8 (4 MHz), commanded by this connection`** — **22 probes, 0 UNPINNED.  STOP S-5 did not fire** |
| probes taken | **21** (the directed capture) **+ 800 rows** (closing chip proof) **+ 1** (`board_idle`) |
| retention | full per-clock rows retained, `8D.json.gz` sha256 **`d0fea3a937fa83fb…`**, manifest **`1f246035b04407c5…`** |
| closing chip proof | `check_ab_hw chip 800` → **`chip-vs-golden: MATCH over 800 rows`** |
| `board_idle()` | **run and clean** — NOP image, `use_core=False` explicit, divider left PINNED at the corpus frequency |
| transport errors | **0** |
| **FLASH #23** | **26 entries / `13a81a43f30c380a…` before and after — INTACT.  STOP S-6 did not fire** |

---

## §11  BARS W-1 … W-8

| bar | verdict |
|---|---|
| **W-1** | ⭐ **MET.**  `86b33eeebb` committed **before the first `hdl/` edit** — `git diff -- hdl/` was EMPTY at that commit — and `a1e1d7a4d6` (addendum + rig) **before the first board contact**.  The read-only diagnostic that preceded the prereg is **declared in its own §0**, not discovered afterwards.  The rule, the POINT prediction (13/13), the G6-C floor (33.00), the `ss_lint` declaration and seven STOPs are all in the committed text |
| **W-2** | ⭐ **MET EXACTLY — 13 / 13**, and `M0`–`M3` did not move.  Both clauses of WAVE 24 §6.3's registered falsifier discharged.  **Plus 21 / 21 on a capture that did not exist when the RTL was written** |
| **W-3** | ⚠ **MET WITH ONE MOVED LEG AND ONE UNREGISTERED MISS, BOTH ATTRIBUTED.**  36 legs both sides; 34 zero-delta with the scored lines byte-identical; `lea_mod3_gate`'s L4 moved **2 of 2 DIVERGE → 0 of 2** (§5.1, the fix's own effect on an independent silicon reference); `chainflat_relocation_check` is the unregistered miss and its repair is §6.1.  `ss_lint` **did not move** |
| **W-4** | ⭐ **MET — `0 / 128` arch, `128 / 128` cycles, logs byte-identical**, and the reason is structural (§7).  **`ea_residue` was NOT injected into the TB** (STOP S-4, carried forward verbatim from WAVE 23).  **NOT re-captured**, with four reasons registered in advance |
| **W-5** | ⭐ **MET — §9**, and in `CLAUDE.md`'s banner and `standing_gates.md` |
| **W-6** | ⭐ **MET.**  No `git stash`, no `git checkout .`, no `git reset --hard` at any point.  The only `git checkout --` was by explicit single path on `hdl/nec_test_ucore.qsf` **inside the worktree**, between Quartus runs, as the brief requires.  Every `git add` by explicit path; **`sw/testdata/receipts/*.jsonl` never staged** (they are appended to by every Verilator build and remain the user's uncommitted work); the user's 21 modified and 20 untracked files untouched |
| **W-7** | ⚠ **MET, AND ONE GATE NEEDED IT.**  Nothing was retired.  `chainflat_relocation_check` went RED, **did not die silently**, and is ledgered as **DEV-1** with its last measured figure (*"9 arms, one copy each, byte-identical to `aba01feb07`, reconstruction exact"*) and what replaces it (*"7 byte-identical + 2 declared, pinned by digest `abb6954fe1a73655…`"*) |
| **W-8** | ⭐ **MET — §12, reported as a FLOOR with a disposition each** |

---

## §12  DOCUMENTATION DISCREPANCIES — **REPORTED AS A FLOOR**

| # | where | what is wrong | disposition |
|---|---|---|---|
| **D-1** | `hdl/rtl/ucore/v30u_eu.sv:252-256` | *"A two-register EA also leaves its index input selected on the adder's other rail.  **Unary EA forms do not select that rail**"* — **refuted by silicon** on `M4`/`M5`/`M7` (the rail reads **0**, not the stale scratch) | **FIXED — this wave's edit.**  The replacement states the two rails, what each takes, what `_valid` now means, and names the capture |
| **D-2** | `hdl/rtl/ucore/v30u_eu.sv:247-250` | *"a ModR/M EA calculation instead leaves the **pre-displacement base** here"* — **WAVE 23's own booked D-2**, left unfixed then because *"editing a comment there … puts a 10-draw Quartus sweep on this wave's bill for a sentence"* | **FIXED — this wave paid for the sweep anyway.**  The replacement says the A rail takes the first addend and that **ordinary `tmpa` writes then refresh it**, which is what the tree does and what silicon does |
| **D-3** | `hdl/rtl/ucore/v30u_eu_arm_bind.svh:75-80` | *"unary forms instead expose the ordinary tmpb rail"* — same refuted claim at the observation site | **FIXED — comment-only hunk** |
| **D-4** | `hdl/rtl/ucore/v30u_eu_step.svh` (the `S_ROW` residue block) | *"replaces the retained **two-register** EA selection"* — the selection is no longer two-register-only | **FIXED — comment-only hunk** |
| **D-5** | the briefing, quoting `suite_divergence_results_2026-09-20.md` §6.3 | *"`ea_residue` … **is written under `ea_pair_valid`**"* — it is not; `ea_residue_n = ea` is unconditional and `ea_pair_valid` guards the **other** rail.  The conclusion (*"the defect is one qualifier"*) is right; the location is not | **RECORDED HERE, THE SOURCE NOT EDITED.**  `suite_divergence_results_…` is a results document of a wave that measured truthfully and booked honestly; §2 above is its continuation.  **It is exactly what the 2026-09-19 user ruling is for, and checking it is why this wave found the real rail** |
| **D-6** | `CLAUDE.md` gate quick reference | *"`sw/check_boot.py --timed 220`"* is listed as a standing gate.  **`--timed` is the RETIRED C++ model leg** and exits 1 naming RET-1; the live RTL legs are `check_boot.py 220` / `400`, which the tool's own refusal message says | ⚠ **RECORDED, AND IT COST THIS WAVE TWO LEGS.**  The ladder ran the `--timed` spelling on **both** sides, both exited 1, and both were re-run with the live spelling (`rc.txt` says so in place).  **FIXED in `CLAUDE.md`'s WAVE 26 banner**, which states the live command |
| **D-7** | `sw/chainflat_relocation_check.py` docstring | *"`--ref REV` … so this keeps working as a standing check long after the landing"* — it does **not**: it freezes the EU's `case (st_n)` and fails the first wave that edits an arm | **FIXED — §6.1**, with the reason written into the docstring so the next reader does not re-derive it |
| **D-8** | `sw/lea_mod3_gate.py` L4's label, and WAVE 24 §11 W-8 | the leg is named **`KNOWN-RED`** and its two rows are no longer red | **LEFT WITH REASON, RECORDED HERE.**  The label is WAVE 23's and the leg is explicitly *not a bar*; renaming it in the wave that closed it would make the two waves' outputs incomparable — the same reason WAVE 24 gave for not touching it.  **The count printed beside it is derived (`0 of 2`), not the label, so the output is truthful as it stands** |

⚠ **THE COUNT IS A FLOOR AND THE METHOD SAYS SO.**  D-1 … D-4 were found by a
**measurement contradicting a sentence**; D-5 by checking the brief against the
tree under the 2026-09-19 ruling; D-6 and D-7 by **a gate exiting non-zero**;
D-8 by reading the output of a leg that moved.  **No gate enumerates claims of
this kind**, and a sentence that is wrong in a way no number contradicts would
not appear here.

---

## §10  WHAT THIS WAVE DELIBERATELY DID NOT DO

* **No flash.**  The bitstream moved and the debt is stated (§9).
* **No SDC edit.**  G6-A was met without one, and S-2 never came close to
  firing.
* **No cut-set widening** (S-3), **no backdoor injection of `ea_residue`**
  (S-4, carried forward verbatim from WAVE 23).
* **No re-capture of `tests/v30/mod3_illegal/`** — §7, registered in advance.
* **No new standing gate.**  `sw/w26_consumer_census.py` is a one-shot
  structural argument with its own positive control, not a ratchet, and it is
  not proposed as one.
* **No `git stash`, `git checkout .` or `git reset --hard`**; every `git add`
  by explicit path; `sw/testdata/receipts/*.jsonl` never staged.
* **No Codex, no nested subagent.**
