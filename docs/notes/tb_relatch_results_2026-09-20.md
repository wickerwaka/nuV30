# WAVE 25 — RESULTS.  **THE `v20suite` RESIDUE WAS ONE LINE OF TESTBENCH.  3,124,992 → 3,125,000 / 3,125,000, EXACTLY EIGHT CASES MOVED, AND NOTHING ELSE IN 7.85 M MOVED AT ALL.**

Pre-registration `935e8fed21`
(`docs/notes/tb_relatch_prereg_2026-09-20.md`), with its §0 erratum declared in
advance.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

**`hdl/rtl/` WAS NOT TOUCHED.  NO QUARTUS RUN WAS MADE AND NONE IS OWED.
NOTHING WAS FLASHED.  THE BOARD STILL CARRIES FLASH #23.**

---

## §1  THE HEADLINE

| | |
|---|---|
| **the fix, in one sentence** | *The settle window's re-latch fires **exactly once** — on the first clock after the window-closing F pop at which the EU's outstanding work has drained — and then the window closes; it no longer re-arms on every later `dbg_pend` pulse.* |
| **the edit** | **ONE LINE OF CODE**: `fin_wait <= 5'd0;` in `hdl/tb/tb_v30_core.sv`'s re-latch arm (plus 49 lines of comment) |
| **P-1, the POINT prediction** | ⭐ **MET EXACTLY.  `v20suite --arch-only` 3,124,992 → 3,125,000 / 3,125,000 ARCH** |
| **P-2, the wave's own falsifier** | ⭐ **MET EXACTLY.  8 cases moved, all 8 inside WAVE 24's 2,284-case predicate; 0 of the other 3,122,716 moved in either direction** — and the proof is a `diff` of the two 360-form logs whose ONLY differing lines are the eight failures and the TOTAL |
| **the rest of the ladder** | ⭐ **31 briefed legs + 11 extra legs: ZERO-DELTA, MEASURED BOTH SIDES.**  Every scored line byte-identical; the only textual differences anywhere are the printed **receipt id**, a Verilator **walltime** banner and a **random temp directory name** |
| **`v0.3`** | **3,699,998 / 3,699,998**, and its 355-form log is **byte-identical on both sides AND byte-identical to WAVE 24's registered run** (`644a11c5e09f38ed…`) |
| **`hdl/rtl/`** | **107 synthesis inputs, sha256 IDENTICAL before and after — and identical to WAVE 23's after-manifest.  The bitstream cannot have moved.** |

---

## §2  THE DEFECT, RE-DERIVED — **VERIFIED, NOT INHERITED**

WAVE 24's directed control was **reproduced on the pristine tree before
anything was edited**, cell for cell:

| variant | injection | **WAVE 24** | **re-measured here (pristine)** |
|---|---|---|---|
| `base` | none | 20 / 20 | **20 / 20** |
| `inj0` | `FF CC` (`DEC SP`) at `end+0` | **0 / 20** | **0 / 20** |
| `inj2` | at `end+2` | **0 / 20** | **0 / 20** |
| `inj4` | at `end+4` | 20 / 20 | **20 / 20** |
| `far64` | at `end+64` | 20 / 20 | **20 / 20** |

And the eight `v20suite` failures are **the same eight cases, by index**:
`03/2019 (sp,flags)` · `0F1D/4712 (bx,flags)` · `29/9262 (sp,bp)` ·
`62/1229 (dx)` · `85/4717 (cx,flags)` · `86/9919 (dx)` · `E8/216 (sp)` ·
`E9/7762 (sp)`.  **NOT ONE `ip`, 8 of 8.**  The predicate was re-derived from
the suite with no engine: **2,284 of 3,125,000, all eight inside**
(`sw/testdata/wave25/predicate-census.txt`, `w25_predicate.py`).

### §2.1  WHAT THE INSTRUMENT ACTUALLY SHOWED — **AND IT REFUTES THE TEMPTING FIX**

A temporary `+gdbg` dump of the settle window (`fin_wait`, `dbg_pend`,
`fin_ghost`, `sp`, `ds`, `ip`, `flags` on every CPU cycle) was read on form
`03` case 0.  Three findings, in order of importance:

> **(a) THE WINDOW IS LOAD-BEARING FOR ORDINARY INSTRUCTIONS.  DELETING IT IS
> NOT THE FIX.**  At the window-closing F pop `dbg_regs.flags` still reads the
> case's **INITIAL `0xf8c3`**; the golden's final is **`0xf017`** and the core
> writes it **on that very edge**, so `fin_regs <= dbg_regs` captures the
> pre-edge, stale value.  The block's comment — *"ghost loads (POP-to-reg data
> still in flight …)"* — **understates its own job**: this case has no ghost
> load and needs the re-latch anyway.

> **(b) `dbg_pend` PULSES ONCE PER INSTRUCTION, AND THAT IS THE BUG.**
> `assign dbg_pend = (rd_pending != 2'd0) || (rdq_n != 2'd0) || poste;`
> (`v30u_eu.sv:2671`) — and `poste` is the post-`E`-row debt, raised for
> **every** instruction.  The dump shows `pend` alternating on a **three-CPU-
> cycle period for the whole 16-cycle window**, and the old code re-latched on
> **every falling edge — five times on this one case**.  The FIRST re-latch is
> the instruction under test's own commit; the rest are whatever retired next.
> On `inj0`, re-latch #1 captured `sp = 0x978f` (correct) and re-latch #2
> captured `sp = 0x978e` — the injected `DEC SP`.

> **(c) `ip` IS EXCLUDED BECAUSE IT CANNOT BE SEPARATED IN TIME.**  On the same
> edge on which the instruction under test commits its flags, the FOLLOWING
> instruction commits its `ip` (`3323 → 3324`).  `3323` is right and is what
> the close already latched — F9 (`ucore_provenance.md` §18) says why: at the
> closing pop the live `pc` IS the retired IP.  **The hand-excluded `ip` was
> the tell that the author knew later instructions retire inside the window;
> every other field they write went straight into the captured final state.**

---

## §3  THE FIX

```diff
             else if (fin_ghost) begin
                 fin_ghost <= 0;
+                fin_wait  <= 5'd0;   // captured: the window is CLOSED
                 fin_regs[191:0]   <= dbg_regs[191:0];
                 fin_regs[223:208] <= dbg_regs[223:208];
             end
```

**WHY IT IS THE MINIMAL ONE.**  No new signal, no new hierarchical reference
into the core, no field list, no per-opcode rule, no distance constant, no
change to what is latched or to `ip`'s exclusion — and nothing under
`hdl/rtl/`.  It deletes a re-arm; it adds no policy.  The other 49 changed
lines are comment.

**THE SECOND LINE WAS WRITTEN, MEASURED AND DELIBERATELY NOT LANDED.**  The
pre-registration registered a **Fix-B** carrying `fin_ghost <= 0;` at the
window-closing latch, against a **cross-case leak**: `fin_ghost` is never
cleared at a case boundary, so a case whose `dbg_pend` never fell could arm the
next one.  A temporary counter at the closing pop measured it:
**0 over 3,644,883 cases** — v0.1 169,000, v0.2 347,000, v20suite 3,125,000,
the four HLT sweeps, three `evt` cells — with **0 wait-overlaps** as well.
**The positive control is structural**: the probe sits in the same statement
that assigns `fin_regs`, so if it were not reached once per case every case
would fail — and every one of those suites scored its registered figure on that
same binary.  **A line with a measured effect of zero is not landed.**  The
measurement and the reasoning are written into the block's own comment, so the
next reader does not have to re-ask.  `sw/testdata/wave25/leak-probe-results.txt`.

**FIX-A AND FIX-B ARE INDISTINGUISHABLE WHERE BOTH WERE SCORED** — the eleven
directed-control variants (20/20 each) and the eight `v20suite` forms
(80,000 / 80,000).  Fix-A is the one in the tree.

---

## §4  P-1 — **THE POINT PREDICTION, MET EXACTLY**

```
python3 sw/check_core.py --core ucore --suite-dir tests/v30/v20suite \
        --opcodes all --cases 0 --arch-only
BEFORE  TOTAL ARCH: 3124992/3125000     (binary sha256 6c447277d3a8b546…)
AFTER   TOTAL ARCH: 3125000/3125000     (binary sha256 ca31aeac8d390307…)
```

**THE ATTRIBUTION IS A `diff`, NOT AN ARGUMENT.**  The two 360-form logs differ
in **38 lines and no others**: the eight failure blocks (24 detail lines + 8
per-form lines) collapsing to eight `ARCH 10000/10000` lines, and the TOTAL.
**Every other per-form line in both logs is byte-identical.**
`sw/testdata/wave25/ladder/{before,after}/v20suite.log`.

### §4.1  V-4 — THE INSIDE / OUTSIDE SPLIT

| population | size | **moved** |
|---|---:|---:|
| inside WAVE 24's predicate (*continuation point has a recorded non-`0x90` byte within 4*) | **2,284** | **8** (all fail → pass) |
| outside it | **3,122,716** | **0** |
| | **3,125,000** | **8** |

**No case moved outside the predicate, in either direction.  The fix has no
second effect on this population.**  And the predicate is **necessary, not
sufficient** — 2,276 of its members were passing before and pass after, exactly
as WAVE 24's distance sweep predicts: the injected instruction must also land
inside the re-latch's reach, which the sweep measures at **`+2` yes, `+4` no**.

### §4.2  THE DIRECTED CONTROL, BOTH SIDES, ON THE LANDED BINARY

| variant | `end+0` | `+2` | `+4` | `+6` | `+8` | `+10` | `+12` | `+16` | `+64` | `90 90 @ +0` | base |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **BEFORE** | **0/20** | **0/20** | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |
| **AFTER** | **20/20** | **20/20** | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 | 20/20 |

⚠ `null90` is **VACUOUS BY CONSTRUCTION AND WAVE 24 SAID SO** — the TB already
fills with `0x90`.  `far64` is the real negative control and it is 20/20 on
both sides, which is what says the effect is LOCAL and not "any change anywhere
in the image".  `base` 20/20 on both sides says the slice itself is clean.

---

## §5  THE LADDER — **BOTH SIDES, 31 BRIEFED LEGS, ZERO MOVED**

`RC` captured with `${PIPESTATUS[0]}`, never `tail`'s.  Raw logs by value at
`sw/testdata/wave25/ladder/{before,after}/`.

<!-- WAVE25-LADDER-BEGIN -->

| leg | command | **BEFORE** | **AFTER** | |
|---|---|---|---|---|
| `check_core` | `--core ucore --opcodes all --cases 0 --ce-div 4` | 169,000 / 169,000 | **169,000 / 169,000** | log byte-identical |
| `check_core` | `… --ce-div 2` | 169,000 / 169,000 | **169,000 / 169,000** | byte-identical |
| `check_core` | `… --ce-div 3` | 169,000 / 169,000 | **169,000 / 169,000** | byte-identical |
| `check_core` | `… --ce-div 8` | 169,000 / 169,000 | **169,000 / 169,000** | byte-identical |
| `check_core` | `… --ce-div 1` | **exit 2**, clause C-a named | **exit 2**, clause C-a named | byte-identical |
| HLT sweep `s10-w0` | `--waits 0` | 97 / 97 | **97 / 97** | byte-identical |
| HLT sweep `s10-w1` | `--waits 1` | 93 / 95, `(10, busstat)`×2 | **93 / 95, `(10, busstat)`×2** | byte-identical |
| HLT sweep `s13-w2` | `--waits 2` | 45 / 46, `(12, busstat)` | **45 / 46, `(12, busstat)`** | byte-identical |
| HLT sweep `s13-w3` | `--waits 3` | 44 / 45, `(14, busstat)` | **44 / 45, `(14, busstat)`** | byte-identical |
| *the four sweeps* | | **279 / 283** | **279 / 283** | the same four survivors |
| `v0.2` | `--suite-dir tests/v30/v0.2 --opcodes all --cases 0` | 347,000 / 347,000 | **347,000 / 347,000** | byte-identical |
| `v0.3` | `--suite-dir tests/v30/v0.3 --opcodes all --cases 0` | 3,699,998 / 3,699,998 [2 excluded] | **3,699,998 / 3,699,998 [2 excluded]** | ⭐ byte-identical, sha256 `644a11c5e09f38ed…` — **the same bytes as WAVE 24's registered run** |
| **`v20suite`** | `… --arch-only` | **3,124,992 / 3,125,000** | ⭐ **3,125,000 / 3,125,000** | **THE ONLY LEG THAT MOVED** |
| `check_boot` | `220` | MATCH over 220 rows | **MATCH over 220 rows** | only the printed receipt id differs |
| `check_boot` | `400` | MATCH over 400 rows | **MATCH over 400 rows** | only the printed receipt id differs |
| `check_ab_sim` | `--core ucore` | MATCH over 187 rows | **MATCH over 187 rows** | byte-identical |
| `ghost_launch_law` | `score` | 200 / 200 = 100.0 % | **200 / 200 = 100.0 %** | byte-identical |
| `lea_mod3_gate` | | PASS, 71 whole-program replays | **PASS, 71 whole-program replays** | only the printed receipt id differs |
| `chain_lfsr_gate` | | PASS, four signatures `1d01c9b269ffaa94` / `b39b040a98b28e5d` / `0997b773cd99c030` / `d05b6c3c3d9fbe78` | **PASS, the four signatures BYTE-IDENTICAL** | byte-identical |
| `chainflat_relocation_check` | | PASS — 9 arms | **PASS — 9 arms** | byte-identical |
| `demux_off_gate` | | PASS — 3 legs | **PASS — 3 legs** | only the Verilator walltime banner differs |
| `r7_lint` | | PASS — 0 carriers, 0 unresolved, 41 `stop` sites, 0 violations | **PASS, identical** | byte-identical |
| `ss_lint --core ucore` | | PASS — **232** (109×2 BIU + 122×2 EU + tag), **229** flops, **4** whitelist, **0 UNMAPPED** | **PASS, identical** | byte-identical |
| `cutset_lint` | | PASS — 81 members / 0 violations | **PASS, identical** | byte-identical |
| `phase_split_lint` | | PASS — 157 members / 779 bits / 0 violations | **PASS, identical** | byte-identical |
| `test_artifact` | | 45 / 45, NON-VACUOUS | **45 / 45, NON-VACUOUS** | only the random self-test temp dir differs |
| `test_quartus_gate` | | **302 / 302**, PASS | **302 / 302**, PASS | byte-identical |
| `qsf_lint --check` | | CANONICAL | **CANONICAL** | byte-identical |
| `core_portlist_lint` | | PASS — 4 configurations | **PASS — 4 configurations** | byte-identical |
| `ucrom_mif_check` | | PASS | **PASS** | byte-identical |
| `check_ucore_tables` (G0) | | PASS — **9,988** entries | **PASS — 9,988** | byte-identical |
| `pla3_check` | | OK — 21 checks | **OK — 21 checks** | byte-identical |

**31 LEGS · 1 MOVED (as predicted, to the case) · 30 ZERO-DELTA.**

### §5.1  ELEVEN EXTRA LEGS — **NOT IN THE BRIEF, RUN BECAUSE THEY GO THROUGH THIS TESTBENCH**

Every one **byte-identical** before and after:

`v0.1-w1` **1,200 / 1,200** · `v0.1-w3` **1,200 / 1,200** ·
`v0.1-w1 --opcodes EB` **200 / 200** · `v0.1-w0evt` **200 / 200** ·
`v0.1-w1evt` **1,200 / 1,200** · `v0.1-w2evt` **200 / 200** ·
`v0.1-w3evt` **1,200 / 1,200** · `v0.1-w1evt-biased` **1,200 / 1,200** ·
`f4a_boundary` **160 / 160** · `f0lock_tranche` **400 / 400** ·
`mod3_illegal` **cycles 128 / 128, ARCH 0 / 128 (KNOWN-RED, WAVE 23 §3,
UNMOVED)**.

⚠ **`enter_nesting` IS NOT A `check_core` SUITE** — it raises
`KeyError: 'initial'` on **both** sides, identically.  Reported, not counted,
and not a WAVE 25 casualty.

**ARCHITECTURAL CASES RE-SCORED THIS WAVE: (169,000 × 4 + 347,000 + 3,699,998 +
3,125,000 + 283 + 7,288) × 2 SIDES = 7,855,569 × 2 = 15,711,138**, plus the
directed control (100 cases BEFORE, 220 AFTER) and the 3,644,883-case leak
probe.

---

## §6  V-5 / V-6 — **THE BITSTREAM DID NOT MOVE, AND NOTHING WAS FLASHED**

| | |
|---|---|
| `git diff --stat -- hdl/rtl/` | **EMPTY**, throughout and at the landing |
| `git diff --stat -- hdl/` | `hdl/tb/tb_v30_core.sv` **only**, 50 insertions / 3 deletions |
| the 107 files Quartus reads | **sha256 IDENTICAL before and after** — and **identical to WAVE 23's after-manifest**, so the RTL has not moved since 2026-09-20 morning.  `sw/testdata/wave25/synth-manifest-{before,after}.txt` |
| Quartus | ⛔ **NOT RUN.  NONE IS OWED.**  A testbench is not a synthesis input; `hdl/tb/` appears in no `.qsf`, no `.qip` and no manifest row |
| **FLASH #23** | ⭐ **STILL COVERS THIS TREE.**  `sw/testdata/flash_log.jsonl` is **26 entries**, sha256 `13a81a43f30c380a…`, and is **not in `git status`** — untouched |
| board contact | **NONE.**  No `ssh`, no probe, no CFG write, no divider command, not even a liveness check |

---

## §7  V-8 — **WHAT CLOSING THE EIGHT DOES AND DOES NOT ESTABLISH**

The `v20suite` goldens were captured from a **uPD70108 (V20)**; this core
models the **uPD70116 (V30)**.  The parts differ — most obviously in the
external data bus and the prefetch queue depth (4 bytes against 6), which is
exactly why the leg must be run `--arch-only` with the final queue MASKED.

**WHAT IS ESTABLISHED:** *on 3,125,000 V20-captured architectural cases, once
the testbench stops letting the NEXT instruction write the captured final
state, this V30 core's architectural result agrees with the V20's — with no
exceptions and no exemption list.*  And, narrowly and certainly: **the
comparator was wrong, and WAVE 22's prefetch-depth reading of the eight is
refuted a second way** — the fix names no queue, no opcode and no part.

**WHAT IS NOT ESTABLISHED:** that the two parts agree architecturally in
general.  This suite exercises what it exercises; a V20/V30 difference that no
captured case reaches is not disproved by 3,125,000 that do not reach it.  It
is also **not** a cycle claim — `--arch-only` skips the cycle-row diff entirely,
by design, because the two parts' bus cycles genuinely differ.  And it says
nothing about `8D`/mod=3, whose goldens are unscoreable by an injected engine
(WAVE 23 §3) and whose `0 / 128` is **unmoved here**.

> **A residue would have been evidence of a part difference.  Its absence is
> evidence the instrument was the difference — which is a smaller claim than
> "the parts agree", and it is the one this wave makes.**

---

## §8  THE ARTIFACTS

| what | id |
|---|---|
| BEFORE testbench | `hdl/tb/tb_v30_core.sv` sha256 **`a02d5d4abc662ee1…`** |
| BEFORE binary | build_key **`8e9de77c32e8716d…`**, `Vtb_v30_core` sha256 **`6c447277d3a8b546…`** |
| AFTER testbench | `hdl/tb/tb_v30_core.sv` sha256 **`6cf556080f391d50…`** |
| AFTER binary | build_key **`8e89ec2581298522…`**, `Vtb_v30_core` sha256 **`ca31aeac8d390307…`**, receipt **`fc8baf0cf95cac30…`** |
| synthesis manifest | **`0b642908e820ed57…`** (both sides, 107 files) |
| `v0.3` log | **`644a11c5e09f38ed…`** (both sides; = WAVE 24's) |

Every rebuild in this wave was **deliberate** — `python3 sw/check_core.py
--build --core ucore`.  `check_core.build()` calls `artifact.ensure()`
(build-if-needed), which is why the rebuild is expected and why the receipt id
in `check_boot` / `lea_mod3_gate` output moves; nothing scored against a stale
binary at any point, because `ensure` requires after it builds.

---

## §9  BARS V-1 … V-9

| bar | verdict |
|---|---|
| **V-1** | ⚠ **MET ONLY IN PART, AND THE SHORTFALL WAS DECLARED IN ADVANCE, NOT DISCOVERED.**  The pre-registration `935e8fed21` was committed before the LANDING edit but **after** an exploratory diagnostic + candidate pass on `hdl/tb/`, which its own §0 states, along with what that costs: the eight forms' 80,000 cases are a CONFIRMATION, the other 3,045,000 and the whole ladder were registered blind.  Every exploratory edit was reverted and the tree proved byte-identical before a single BEFORE figure was taken |
| **V-2** | ⭐ **MET EXACTLY — 3,125,000 / 3,125,000.**  A POINT prediction, hit on the point |
| **V-3** | ⭐ **MET — 31 briefed legs + 11 extras, BOTH SIDES, every scored line byte-identical.**  The four legs whose logs differ at all differ only in a receipt id, a walltime banner and a random temp dir; all four verdict lines identical |
| **V-4** | ⭐ **MET — 8 inside / 0 outside**, proved by `diff` over the full 360-form logs rather than by inference (§4.1) |
| **V-5** | ⭐ **MET — `git diff --stat -- hdl/rtl/` EMPTY; 107 synthesis inputs sha256-identical; no Quartus run made and none owed** (§6) |
| **V-6** | ⭐ **MET — no board contact of any kind; `flash_log.jsonl` 26 entries, untouched.  FLASH #23 intact** |
| **V-7** | ⭐ **MET — no `git stash`, no `git checkout .`, no `git reset --hard` at any point.**  The one `git checkout --` was by explicit single path on `hdl/tb/tb_v30_core.sv`, a file this session alone had modified and which was clean in the opening `git status`.  Every `git add` by explicit path; `sw/testdata/receipts/*.jsonl` never staged; the user's 21 modified and 16 untracked files untouched |
| **V-8** | ⭐ **MET — §7, stated as a narrowing and not as a part-agreement claim** |
| **V-9** | **MET — §10, reported as a FLOOR with a disposition each** |

---

## §10  DOCUMENTATION DISCREPANCIES — **REPORTED AS A FLOOR**

| # | where | what is wrong | disposition |
|---|---|---|---|
| **X-1** | `hdl/tb/tb_v30_core.sv:481-483` (the block's own comment) | *"ghost loads (POP-to-reg data still in flight at the closing F) complete within the settle window; re-latch everything except the retired IP (**the following NOPs keep retiring**)"* — three claims, two of them false.  The window is needed for instructions with **no** ghost load (§2.1a); and *"the following NOPs"* is an ASSUMPTION about the image that the V20 captures violate, stated as if it were a property of the core | **FIXED — this wave's edit.**  The replacement states the mechanism, the measurement, and the falsifier |
| **X-2** | `docs/notes/standing_gates.md` §B (WAVE 24 addendum) and the gate table | *"DISPOSITION PROPOSED, NOT TAKEN — `3,124,992 / 3,125,000 ARCH` stays the quotable figure"* | **FIXED — updated in place**, both the table row and the addendum, with the WAVE 25 figure and this document named |
| **X-3** | `CLAUDE.md`'s WAVE 24 banner | same sentence | **FIXED — a WAVE 25 banner added above it; the WAVE 24 text is kept verbatim as history**, because a ratchet is only readable against its own history |
| **X-4** | `docs/notes/suite_divergence_results_2026-09-20.md` §4b | *"THE DISPOSITION IS PROPOSED AND NOT TAKEN … (a) is the one that fixes something"* | **SUPERSEDED HERE, NOT EDITED.**  It is a results document of a wave that deliberately did not land; route **(a)** is what this wave took, exactly as written.  Editing it would erase the proposal that was right |
| **X-5** | `docs/notes/invalidation_ledger.md` §A (the RET-1 replacement table) | carries `v20suite` **3,124,992 / 3,125,000** as a current measured figure | **MARKED — one footnote row added naming WAVE 25**; the table itself is labelled *"ucore, WAVE 22"* and stays as that wave's measurement |
| **X-6** | `docs/notes/suite_scorer_results_2026-09-19.md` §7 and `lea_mod3_results_2026-09-20.md` §6 | both quote 3,124,992 as current | **LEFT WITH REASON** — historical results documents of waves that measured it truthfully on their own trees.  Recorded here instead |
| **X-7** | `sw/check_core.py:326-331` (`compose_batch`'s `arch_only` comment) | *"V20 traces END one F-pop earlier than our v0.1 convention … So to dump the register file at the RETIREMENT point … close one F-pop later"* — true, and **it is the reason the defect is `v20suite`-visible and our-suites-invisible**, but it does not say so, and nothing links it to the settle window it hands the problem to | **LEFT WITH REASON, RECORDED HERE.**  The explanation now lives in the testbench block that owns the behaviour; duplicating it in the composer would put the same claim in two places that can drift apart |

⚠ **THE COUNT IS A FLOOR AND THE METHOD SAYS SO.**  X-1 and X-7 were found by
**reading the code the measurement pointed at**; X-2, X-3, X-5 and X-6 by a
`grep` for the superseded figure.  **No gate enumerates claims of this kind**,
and a sentence that is wrong in a way no number contradicts would not appear
here.

---

## §11  WHAT THIS WAVE DELIBERATELY DID NOT DO

* **No `hdl/rtl/` edit** — including the `ea_pair_valid` qualifier that WAVE 24
  §6.3 books and that the user's *"do both fixes, tb first"* names as the
  second.  **It is a separate wave and was not touched.**
* **No Quartus, no flash, no board contact, no Codex, no nested subagent.**
* **No second testbench line landed** on a measured-zero effect (§3).
* **No suite edited.  No golden moved.  No exemption added or retired.**  The
  eight cases were closed by fixing the comparator, not by excusing them — the
  disposition WAVE 24 called *"(b) only stops counting it"* was not taken.
* **No document deleted**; two fixed in place, one marked, three left with
  reasons, one superseded by reference.
