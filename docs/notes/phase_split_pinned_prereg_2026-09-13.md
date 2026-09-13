# WAVE 13 — **THE PHASE SPLIT, RE-MEASURED LIKE-FOR-LIKE ON THE STAMP-FREE TREE.**  PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST `hdl/` EDIT.**  Results go in a SEPARATE
`docs/notes/phase_split_pinned_results_2026-09-13.md`.

**THIS IS A MEASUREMENT THAT BECOMES A LANDING IF IT CLEARS THE BAR.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM MAY BE PROGRAMMED BY THIS
WAVE.**  No Codex.  No nested subagent.  `docs/notes/standing_gates.md` §A
governs every timing figure — **one green build is not closure.**

---

## §0 THE STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood.  A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

## §0.1 THE STANDING REQUIREMENT (USER RULING 2026-09-08, verbatim)

> **"I don't want custom sdc rules, period."**

**It is not re-opened.**  The NO-EXCEPTION build is the goal state and this wave
measures it.

---

## §1 WHY THIS WAVE EXISTS — **EVERY PHASE-SPLIT FIGURE THIS CAMPAIGN HAS EVER QUOTED IS CROSS-STAMP**

WAVE 11 (`docs/notes/pcc0_settle_results_2026-09-12.md`) proved that
`hdl/build_id.v` — a **gitignored two-character-varying `%y%m%d` date stamp**
embedded in the OSD `CONF_STR`, which the CPU never sees — was an **unlabelled
extra fitter seed worth 1.647 ns / 1.34 MHz at one seed**, against WAVE 7's
**0.603 ns** span over five fitter seeds.  **The uncontrolled dimension was
larger than the controlled one.**

WAVE 12 (`docs/notes/buildid_removal_results_2026-09-12.md`, landing
`04efdc8d47`) **removed it**, gated it (`quartus_gate` bar **E11**, exit 2 with
the reason named, no quiet path), and measured the nondeterminism gone:
**Δ = 0.000 ns where WAVE 11 measured 1.647**, with whole 390,761-byte Quartus
transcripts differing in one progress timestamp.  **The tree's Quartus figures
are comparable to each other for the first time.**

### 1.1 WAVE 9's HEADLINE IS CONTAMINATED IN A KNOWN DIRECTION

WAVE 9 (`docs/notes/phase_split_reland_results_2026-09-09.md`) landed the three
edits, measured **CONTROL `worst-of-5` 30.06 / RETENTION 31.17** with no
exception, called J-1 **FAILED** and **reverted at `cbb556a097`**.  Its
scoreboard read **+1.74 / +2.27** against WAVE 7's 28.32 / 28.90.

* WAVE 9's no-exception split draws were compiled at stamp **`260912`** — the
  **SLOW** one (WAVE 11 measured `260912` at 35.867 ns against `260909`'s
  34.220 at the same seed on the same tree).
* The WAVE 7 baseline it improved on was compiled at stamp **`260909`** — the
  **FAST** one.

**SO WAVE 9's +1.74 / +2.27 UNDERSTATES THE MECHANISM, AND THE GAP TO 32.0 IS
SMALLER THAN THE 1.94 / 0.83 MHz IT REPORTED.  BY HOW MUCH IS UNKNOWN AND THAT
IS WHAT THIS WAVE MEASURES.**

⚠ **DO NOT ASSUME IT CLEARS.  DO NOT ASSUME IT MISSES.**  Both arms are drawn on
THIS tree, by ONE driver, at the SAME seeds.  **A number carried over from any
earlier wave is not a baseline** — WAVE 7's 28.32 / 28.90 and WAVE 12's
with-exception 40.62 / 41.63 are **HISTORY, NOT THIS WAVE'S CONTROL**, and
WAVE 12 §8 already registers the boundary as a hard one: a pre-WAVE-12 Quartus
figure may not be differenced against a post-WAVE-12 one.

---

## §2 WHAT IS BUILT

**WAVE 9's THREE EDITS, ON TODAY'S HEAD (`5f8128b88b`).**  Nothing is
re-derived that does not have to be.

| commit | edit |
|---|---|
| `6e822bf750` | **(a)** `CE_HALF` becomes an UNCONDITIONAL port of `v30_core` + RULING 1's two SS freeze clauses move down with it |
| `5cf3254104` | **(b)** the cut set — `v30u_eu_preload.svh`, the **778-bit** `s1q` shadow |
| `bacf7f9fd9` | **(c)** DELETE the CE multicycle from `hdl/nec_test.sdc` (+ the `nominal["SAME"]` 2.0 → 1.0 check, the probe labels, and `test_quartus_gate`'s era assertion) |

WAVE 12 touched `hdl/nec_test.sv`, `hdl/sys/sys.tcl`, `hdl/.gitignore`, deleted
`hdl/sys/build_id.tcl`, added `hdl/sys/gen_cdf.tcl`, and rewrote
`sw/quartus_gate.py` / `sw/test_quartus_gate.py` for bar E11.  **It did NOT
touch `hdl/rtl/ucore/`.**

⚠ **APPLICABILITY IS MEASURED, NOT ASSUMED, AND IT IS MEASURED IN THIS
DOCUMENT.**  `git diff <commit>^ <commit> | git apply --check --3way` on today's
HEAD, one commit at a time:

```
=== 6e822bf750 ===  v30_core.sv cleanly · tb_demux_min.sv cleanly · demux_off_gate.py cleanly
=== 5cf3254104 ===  v30_core.sv cleanly · v30u_eu.sv cleanly · (new file, direct) · cutset_lint.py cleanly · ss_flop_whitelist_ucore.txt cleanly
=== bacf7f9fd9 ===  nec_test.sdc cleanly · quartus_gate.py cleanly · sta_truefmax_probe.tcl cleanly · test_quartus_gate.py cleanly
```

**ALL THREE APPLY CLEAN AGAINST HEAD, INCLUDING EDIT (c)'s TWO HUNKS IN THE
FILES WAVE 12 REWROTE.**  The results document reports whether the actual
sequenced pick fuzzed, conflicted or applied, **and says so either way**.  If
any hunk is re-derived, **the results document says it was re-derived** and
what changed.

⚠ **EDIT (a) IS AN INTERFACE CHANGE.**  `CE_HALF` leaves `ifdef V30_MUXED_AD`
and becomes an unconditional port; a de-muxed downstream integrator that did not
connect it will fail to elaborate — the intended, SURFACED consequence.  It has
been built and reverted twice (WAVE 4, WAVE 9).  **`demux_off_gate` MUST PASS.**

---

## §3 THE BARS.  **VERBATIM, AND THEY ARE NOT NEGOTIABLE AFTER A RESULT IS SEEN.**

**N-1  THE REQUIREMENT.**  With the CE multicycle deleted, `quartus_gate.py
--seeds 5` PASSES E1-E5 on EVERY draw (Fmax ≥ 32.0, worst setup > 0, TNS 0.000
setup AND hold, 0 errors / 0 latches / 0 `lpm_divide`), **BOTH**
configurations.  **This is the campaign's success condition.**

**N-2**  The exception is gone and CHECKED: no `set_multicycle_path`, no "CE
multicycle" info line, every receipt's `core_domain` k = 1.

**N-3  THE LIKE-FOR-LIKE DELTA — THE WAVE'S SCIENTIFIC PRODUCT, DUE WHATEVER
N-1 SAYS.**  Draw the UNSPLIT no-exception arm on THIS tree, `--seeds 5`, both
configurations, with the SAME driver and the SAME seed set as the split arm.
Report the two `worst-of-5` figures and their difference.  **This is the first
stamp-free measurement of the phase split's benefit and it is the number every
earlier wave got wrong.**

**N-4  BAR E11 IS TRUE ON EVERY RECEIPT** — no `%y%m%d` stamp on any build path,
on all 20 draws.  This is what makes N-3 like-for-like, so **a single false E11
voids N-3.**

**N-5  PIN IDENTITY**, taken BEFORE side on the unedited tree first:
`chain_lfsr_gate`'s four signatures BYTE-IDENTICAL with every gap count;
`fz2_replay` scored-content IDENTICAL — **compare the named fields directly, NOT
a digest computed by this wave**; and the full ladder of N-6.  ⚠ The split was
zero-delta at WAVE 9 and WAVE 12 was zero-delta, but **the COMBINATION is new
and unmeasured.**

**N-6  THE LADDER, EVERY LEG AT ITS REGISTERED VALUE**: `r7_lint` ·
`check_core --opcodes all --cases 0` 169,000 · `8F.0` 500 · HLT sweeps ⚠ WITH
`--waits 0/1/2/3` 279/283 · `v0.1-w1`/`-w3` 1,200 · `EB` 200 · the four evt
cells 200/1,200/200/1,200 · `v0.1-w1evt-biased` 1,200 · `ulockstep` 17,350 ALL
LOCKSTEP · `ghost_launch_law` 200/200 · `check_boot` 220 and 400 ·
`check_ab_sim` 187 · `sm3_s16_score` 1,320/1,371 · **`demux_off_gate` PASS** ·
`test_artifact` 45/45 · `test_quartus_gate` **287/287** · `ucrom_mif_check`
PASS.  ⚠ Verify each against `standing_gates.md` first; its `ss_lint` row
(226 / 214 / 0x8D) is **KNOWN STALE** against the tree's 232 / 228 / 0x8F —
**measure, report the disagreement, never treat a stale row as a failure.**

**N-7**  `ss_lint` exits 0, `SS_COUNT` / `SS_VERSION` / `SS_TAG` UNCHANGED, 0
UNMAPPED, whitelist grown by **exactly the shadow's entry**.

**N-8**  `check_core --opcodes all --cases 0` = 169,000 at `--ce-div 2, 3, 4 AND
8`; `--ce-div 1` still REFUSED.

**N-9  THE DISPOSITION.**

* **If N-1 PASSES and N-5 / N-6 / N-7 / N-8 hold — THE SPLIT LANDS.**  Say so
  plainly; it is the requirement met after thirteen waves.
* **If N-1 FAILS — revert all three edits, report the GAP to 32.0 explicitly,
  and N-3 is still delivered.**  A wave that reports *"still N MHz short,
  measured cleanly for the first time"* has done its job.

**Do not soften a bar to make a landing possible and do not re-scope after
seeing a result.**

---

## §4 THE ORDER OF OPERATIONS, REGISTERED SO IT CANNOT BE CHOSEN AFTERWARDS

1. the **BEFORE ladder** on the UNEDITED tree — `sw/testdata/wave13/before/`,
   started before this document was written and touching no `hdl/` file;
2. **this document**;
3. **edit (c) FIRST, ALONE** — the SDC deletion and the driver's `nominal`
   change;
4. **N-3's UNSPLIT ARM**: `quartus_gate.py --seeds 5` and
   `--retention --seeds 5`, on the UNSPLIT RTL with NO exception;
5. edit (a), the interface change;
6. edit (b), the cut set;
7. the **AFTER ladder**, `ss_lint`, `demux_off_gate`, the divisor sweep —
   N-5 / N-6 / N-7 / N-8;
8. **N-1's SPLIT ARM**: `quartus_gate.py --seeds 5` and
   `--retention --seeds 5`, same driver, same seed set `{1,2,3,4,5}`;
9. the verdict, and **N-9 if the revert triggers**.

### 4.1 ⚠ WHY EDIT (c) COMES FIRST HERE AND CAME LAST IN WAVE 9 — REGISTERED IN ADVANCE

WAVE 9 ordered (a) · (b) · (c) so that J-8 — *no regression WITH the exception*
— could be measured on the cut tree before the exception went away.  **THIS WAVE
IS NOT ASKING J-8's QUESTION.**  It is asking N-3's: *what is the split worth,
measured like-for-like?*  That needs the UNSPLIT arm compiled under **the same
SDC and the same driver** as the split arm, which is edit (c) applied to the
unsplit RTL.

**Applying (c) first is FUNCTIONALLY INERT and OVER-CONSTRAINING, never
under-constraining**: an SDC with no exception asks the compiler for a
single-cycle check on an arc the RTL still walks in two periods.  That is the
PESSIMISTIC direction — the intermediate tree is a **correct design measured
against a budget it does not need**, which is exactly what makes it the right
control for N-3.  **No Verilator gate can see an SDC**, so the functional ladder
is untouched by step 3, and the ladder that governs the landing is step 7's, on
the tree with all three edits.

⚠ **THE INTERMEDIATE COMMIT IS EXPECTED TO DRAW RED AND THAT IS NOT A RESULT
AGAINST THE DESIGN.**  It is N-3's baseline arm and is quoted only as such.

---

## §5 DISCIPLINE, DECLARED IN ADVANCE

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.**  ⚠ **A FABRIC CONFIRMATION HAS BEEN
  OWED SINCE WAVE 7** (the EU's decode changed) **AND WAVE 12 ADDED A SECOND
  REASON** (the bitstream moved again).  It is **RECORDED, NOT DISCHARGED**, and
  **no fabric figure taken on FLASH #21 or earlier may be quoted against this
  tree.**
* **Single-writer guard before any Quartus stage** — `pgrep -x`, EXACT binary
  name, **ONE PATTERN PER CALL** (`pgrep -x a b` is an ERROR and its failure
  branch reads as *"idle"*).
* ⚠ **NEVER `git stash`, `git checkout .`, `git reset --hard`, or anything that
  touches the working tree wholesale.**  There are **21 pre-existing modified
  files that are the USER'S OWN UNCOMMITTED WORK** plus 14 untracked
  `hdl/quartus_gate_*.log` files.  **`git add` BY EXPLICIT PATH ONLY.**
* ⚠ `hdl/nec_test_ucore.qsf` is `git checkout -- <that exact path>`'d between
  Quartus runs — the declared §70.7 exemption, E7's single permitted mover.
  **Never a bare `git checkout`.**
* `~/.cache/ucsimt-tmp` for every intermediate; nothing large in `/tmp`.
* ⚠ **COMPARE CONTENT, NOT A DIGEST COMPUTED BY THIS WAVE.**  *A number with no
  artifact id is not quotable.*
* ⚠ Verilator `$stop`s on the first `$error`; each clause gets its own probe.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  Nine instruments in this
  campaign have produced confident, wrong, vacuous results.
* ⚠ **A Verilator artifact receipt is NOT reproducible across rebuilds of a
  byte-identical tree** — *"the receipt moved, so the edit reached the binary"*
  is INVALID.
* Truthful commit messages; **never assert a gate that is not met**.
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
