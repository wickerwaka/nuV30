# WAVE 9 — **THE PHASE SPLIT, RE-MEASURED ON THE FLATTENED TREE.**  PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST `hdl/` EDIT.**  Results go in a SEPARATE
`docs/notes/phase_split_reland_results_2026-09-09.md`.

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

**It is not re-opened.**  The SCOREBOARD is the no-exception `worst-of-5`:
**CONTROL 28.32 / RETENTION 28.90** against **32.0**
(`chainflat_landing_results_2026-09-09.md` §6.2).  The arc is **33.0 ns**
(`frontend_anatomy_results_2026-09-09.md` §3.1, mean 32.969 over 4 draws) and
must reach **~29.6 ns**.  **Gap ~3.4 ns.**

---

## §1 WHY THIS WAVE EXISTS — **THE REFUTATION WAS MEASURED ON A TREE THAT IS GONE**

WAVE 4 (`phase_split_cutset_results_2026-09-08.md`) cut the EU across
`ce`/`ce_half` with a **complete 778-bit cut set** and came back **RED on 20 of
20 draws**, `worst-of-5` CONTROL **23.50** / RETENTION **23.57**.  Its diagnosis
was not the Fmax but §0.1:

> **STAGE 1 = 21.556 ns / 19 levels (fits).  STAGE 2 = 37.224 ns / 40 levels =
> 26.86 MHz — the EU's UNROLLED CHAIN ALONE, BIU-free, 6.0 ns over budget by
> itself.**

**WAVE 7 DELETED THAT UNROLL** (`2ceb8c3ba3`).  The seven copies of the 33-arm
step case are one copy per arm; the arc fell **43.485 → 33.0 ns**; the `CHAIN`
bucket is **9.395 ns** on 100 % of 1,600 paths (WAVE 8 §3.2); and WAVE 8 §4
measured the BIU round trip at **0.000 ns on 0 of 1,200 CONTROL paths**.

**THE SPECIFIC STRUCTURE THAT MADE STAGE 2 37.2 ns NO LONGER EXISTS.**  That is
why this is being re-measured.  **IT IS NOT A REASON TO ASSUME IT WORKS.**

### 1.1 ⚠ THE PENALTY THAT KILLED IT IS STILL REAL AND THIS WAVE MUST MEASURE IT

WAVE 5 (`chain_anatomy_results_2026-09-09.md` §3.1) established that **a cut
does not divide an arc, it GROWS it**: its uncut profile predicted a downstream
half of **17.2–22.1 ns** and WAVE 4 realised **37.224** — an error of
**+11.3 … +20.0 ns** — and the whole loop grew **+15.30 ns (+35 %)**.  Uncut,
Quartus merges logic freely across the prospective boundary; after the cut both
halves are re-synthesised and cannot.  WAVE 8 §7.6 measured the same thing in a
second vocabulary: **an ATTRIBUTED SHARE of an uncut arc is not a difference and
does not transfer** (5.9× overstatement there).

**WHETHER 33.0 ns HALVED PLUS THAT PENALTY CLEARS 29.6 IS EXACTLY WHAT THIS
WAVE MEASURES AND NOBODY KNOWS.  No estimate in this document is a prediction,
and §7's arithmetic is registered to be reported WHATEVER THE OUTCOME.**

---

## §2 WHAT IS BUILT

WAVE 4's cut set, **RE-DERIVED FOR THE FLATTENED TREE**.  WAVE 4's commits are
read as a GUIDE, not applied as a patch:

| commit | what it was |
|---|---|
| `c46004eba1` | edit (a) — `CE_HALF` unconditional + the two SS freeze clauses moving down with it |
| `3e0a4dfc3b` | edit (b) — the cut set |
| `a0e45d8076` | **A-1**, which COMPLETED the cut set (the ten module `reg`s the OTHER `always @*` blocks drive) |
| `742b52f643` | edit (c) — the SDC deletion |
| `133de40fe7` | the revert |

⚠ **WAVE 4's FIRST CUT SET WAS INCOMPLETE AND ITS OWN LINT COULD NOT SEE IT.**
This wave does not repeat that: **the crossing set is derived from the RTL, not
from a list**, and the derivation is the ported `sw/cutset_census.py` /
`sw/cutset_lint.py` (`451bbf26c5`, committed **before this document**), whose
include set is now the **transitive closure** of the next-state block's own
`` `include ``s rather than nine hard-coded names.

### 2.1 THE RULE THAT DECIDES IT

The cut must be a **CUT SET PROVEN BY CONSTRUCTION** — stage 2 structurally
unable to NAME a pre-cut wire — **enforced by a lint**, not asserted.

### 2.2 ⚠ THE SHADOW WIDTH, MEASURED **BEFORE** THE PEEL IS COMMITTED TO

Registered STOP threshold: **900 bits — report and stop if exceeded.**

| | |
|---|---:|
| loop-carried `_n` set (WAVE 2's peel, WAVE 4's 76 pack members, re-summed on THIS tree) | **495 bits** |
| the wire cone (`cutset_census.py` on this tree: 81 names / 284 bits, **minus `rep_chained`**, which the preload assigns and which the census only reports because `v30u_eu_preload.svh` does not exist yet) | **283 bits** |
| **`S1W`** | **778 bits** |

**IDENTICAL TO WAVE 4's 778.**  The wire cone is WAVE 4's 80 names **name for
name** (`comm` over the two sorted lists is EMPTY both ways once `rep_chained`
is excluded by its own rule).  **UNDER THE STOP.  THE WAVE PROCEEDS.**

The loop-carried set is WAVE 4's 76-member list, which is a **SUPERSET** of what
`phase_split_width.py` derives on this tree (62 names / 489 bits) by four names
— `first_pop_seen_n` (1), `poll_pipe_n` (3), `rd_age0_n` (1), `rdh_byte` (1) =
6 bits.  **Over-inclusion is safe by construction** (a member the unpack writes
with the shadow value is equal to the live value by the phase-stability premise,
which is `$fatal`-asserted every `ce`), and taking WAVE 4's list verbatim is
what makes this wave's 778 comparable to WAVE 4's 778 bit for bit.  **The
difference is reported here, in advance, rather than discovered in the results.**

### 2.3 `CE_HALF` BECOMES AN UNCONDITIONAL PORT AGAIN — **AN INTERFACE CHANGE, PRE-REGISTERED AS ONE**

`CE_HALF` currently lives under `ifdef V30_MUXED_AD`.  A `V30_MUXED_AD`-off
build therefore has no half-cycle enable at all, and a phase-split EU cannot be
enabled in that configuration — `sw/demux_off_gate.py` breaks.  So:

> **`input CE_HALF` MOVES OUT OF THE `ifdef` AND BECOMES AN UNCONDITIONAL PORT
> OF `v30_core`.  THIS IS A CHANGE TO THE MODULE'S PORT LIST.  A DE-MUXED
> DOWNSTREAM INTEGRATOR THAT DID NOT CONNECT IT WILL FAIL TO ELABORATE — the
> intended, SURFACED consequence, the same shape as the
> `SYNTHESIS`-without-`V30_MUXED_AD` refusal E-6 records.**

The two USER-RULING-1 save-state freeze clauses (`SS_WE && CE_HALF`,
`CE_HALF && ss_we_q`) move DOWN out of the `ifdef` with it, into the
bus-shape-independent SS block, so they are asserted in EVERY configuration.
`sw/demux_off_gate.py` LOSES its `CE_HALF` GONE-clause (asserting it would
assert something false) and its summary line reads *"the two muxed ports are
GONE"*; the `AD` and `AD_OE` clauses are untouched and still REFUSE naming their
pins, which is what keeps that leg non-vacuous.  **`demux_off_gate` MUST PASS.**

### 2.4 SAVE STATE — USER RULING 2026-09-08, STANDING

The shadow is **DERIVED** and goes on the **DERIVED** class of
`sw/ss_flop_whitelist_ucore.txt`.  **`SS_COUNT` / `SS_VERSION` / `SS_TAG` MUST
NOT MOVE.**  RULING 2's **option (i)** is re-used verbatim: the commit condition
is `(ss_we || srst || ce_half)` with the `ss_we` arm re-running the preload so
the shadow is reconstructed on that very edge, exactly as `dec_addr_next` does
it.  **NO RULE IS WIDENED.**

---

## §3 THE BARS.  **VERBATIM, AND THEY ARE NOT NEGOTIABLE AFTER A RESULT IS SEEN.**

**J-1  THE REQUIREMENT.**  With the CE multicycle DELETED, `quartus_gate.py
--seeds 5` PASSES E1-E5 on EVERY draw (Fmax >= 32.0, worst setup > 0, TNS 0.000
setup AND hold, 0 errors / 0 latches / 0 lpm_divide), BOTH configurations.
**This is the campaign's success condition.**

**J-2**  The exception is gone and CHECKED: no `set_multicycle_path`, no "CE
multicycle" info line, every receipt's `core_domain` k = 1.

**J-3  THE CUT SET IS COMPLETE, PROVEN TWO WAYS.**  (a) the lint passes and is
demonstrated FIRING on a deliberately re-introduced bypass; (b) on a
no-exception fit the worst `ce -> ce` path's arrival points **DO** name the
shadow — **report the count against WAVE 4's 0 of 107.**

**J-4  PIN IDENTITY**: `chain_lfsr_gate`'s four signatures BYTE-IDENTICAL with
every gap count and census; `fz2_replay` scored-content sha256 IDENTICAL; the
full ladder of J-5.  BEFORE side on the unedited tree.

**J-5  THE LADDER, EVERY LEG AT ITS REGISTERED VALUE**: `r7_lint` ·
`check_core --opcodes all --cases 0` 169,000 · `8F.0` 500 · HLT sweeps ⚠ WITH
`--waits 0/1/2/3` 279/283 · `v0.1-w1`/`-w3` 1,200 · `EB` 200 · the four evt
cells 200/1,200/200/1,200 · `v0.1-w1evt-biased` 1,200 · `ulockstep` 17,350 ALL
LOCKSTEP · `ghost_launch_law` 200/200 · `check_boot` 220 and 400 ·
`check_ab_sim` 187 · `sm3_s16_score` 1,320/1,371 · `demux_off_gate` PASS ·
`test_artifact` 45/45 · `test_quartus_gate` · `ucrom_mif_check` PASS ·
`chain_lfsr_gate` PASS.  ⚠ Verify each against `standing_gates.md`; **two rows
there are known stale — measure, report the disagreement, never treat it as a
failure.**

**J-6**  `ss_lint` exits 0, `SS_COUNT`/`SS_VERSION`/`SS_TAG` UNCHANGED, 0
UNMAPPED, whitelist grown by exactly the shadow's entry.

**J-7**  `check_core --opcodes all --cases 0` = 169,000 at `--ce-div 2, 3, 4 AND
8`; `--ce-div 1` still REFUSED.  The split makes S-1 load-bearing for the EU, so
this is a correctness bar.

**J-8  NO REGRESSION WITH the exception**: `--seeds 5` on the tree's current SDC
PASSES both configurations, `worst-of-5` not below WAVE 7's **41.06**.  A
regression here fails J-8.

**J-9  THE ARITHMETIC, REPORTED WHATEVER THE OUTCOME — this is the wave's
scientific product.**  On a no-exception fit: worst `* -> shadow`, worst
`shadow -> *`, and the worst `ce -> ce` path touching NEITHER (WAVE 4's failure
signature — it must not exist; if it does, name it).  **Then the GROWTH: the two
stages against the 33.0 ns uncut arc.**  WAVE 4's equivalent growth was
+11.3 to +20.0 ns on the downstream half.

**J-10  NON-VACUITY**: the lint fires on a re-introduced bypass; the shadow is
load-bearing (perturbing one bit breaks a named gate leg); S-1's `$fatal` fires.

**J-11  THE REVERT CONDITION.**  If J-1 fails, or any leg of J-4/J-5/J-6/J-7
moves, or J-8 regresses, **THE LANDING DOES NOT HAPPEN.**  Revert, report, keep
both documents.  **Do not soften a bar to make a landing possible and do not
re-scope the cut after seeing a result.**  Report the GAP to 32.0 explicitly
either way.

---

## §4 THE ORDER OF OPERATIONS, REGISTERED SO IT CANNOT BE CHOSEN AFTERWARDS

1. the BEFORE ladder, on the UNEDITED tree — **already taken**,
   `sw/testdata/wave9/before/`;
2. the shadow width — **already taken**, §2.2, under the STOP;
3. **this document**;
4. edit (a), the interface change;
5. edit (b), the cut set + A-1's ten in ONE edit (A-1 is not re-discovered: it
   is part of the derivation from the start);
6. the AFTER ladder, the lints, `ss_lint`, the divisor sweep — J-4/J-5/J-6/J-7;
7. **J-8, WITH the exception, on the CUT tree** — it must be measured before
   edit (c) removes the exception;
8. edit (c), the SDC deletion;
9. **J-1**, `--seeds 5`, both configurations, no exception;
10. **J-3(b) / J-9**, the diagnosis fit;
11. **J-10**, non-vacuity;
12. the verdict, and **J-11 if it triggers**.

## §5 DISCIPLINE, DECLARED IN ADVANCE

* OFFLINE ONLY.  **NO BOARD.  NO FLASH.**  ⚠ **A FABRIC CONFIRMATION IS OWED
  SINCE WAVE 7** and is not this wave's to discharge; it is recorded, and **no
  fabric figure from FLASH #21 or earlier may be quoted against this tree.**
* Single-writer guard by EXACT binary name before any Quartus stage.
* ⚠ `hdl/nec_test_ucore.qsf` `git checkout --`'d between Quartus runs (the
  declared §70.7 exemption: `quartus_map` rewrites it; WAVE 4 lost a sweep to
  not doing it).
* ⚠ **`git add` BY EXPLICIT PATH ONLY.**  ~18 pre-existing modified files in the
  working tree are NOT this wave's; every one is left alone.  `git add -A` is
  never used.
* `~/.cache/ucsimt-tmp` for every intermediate; nothing large in `/tmp`.
* ⚠ `get_timing_paths -through` ignores a `get_nodes` collection — `get_pins`,
  ONE PIN AT A TIME, with any bulk form printed beside it as a known-wrong
  control.  ⚠ `string match` on a name with a bus index FAILS.
* ⚠ Verilator `$stop`s on the first `$error`; each clause gets its own probe.
* ⚠ **A Verilator artifact receipt is NOT reproducible across rebuilds of a
  byte-identical tree** — "the receipt moved, so the edit reached the binary" is
  INVALID.  Reach is proved another way.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**
* Truthful commit messages; **a number with no artifact id is not quotable**.
* **Record what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01GNePHdAnFPZZjwActogQsm
