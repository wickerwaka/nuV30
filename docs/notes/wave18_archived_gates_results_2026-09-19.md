# WAVE 18 — RESULTS: THE ARCHIVED FSM CORE'S PORT LIST, AND THE FULL INVENTORY OF WHAT THAT BROKE

Pre-registration: `docs/notes/wave18_archived_gates_prereg_2026-09-19.md`
(`71a757cf30`, committed before the first edit).  Landing `9ccc6d0177`.
Tree at start: `f89f4e6978`.  **Offline only.  No board.  No flash.  No Codex.**

---

## 1. THE DIAGNOSIS, FROM THE ARTIFACT

**WHAT FAILS, AND AT WHICH STAGE.**  `sw/check_fuzz_bank.py` dies at
`check_fuzz_bank.py:112` — `print(f"check_fuzz_bank: TB leg {check_seq.tb_bin()}")`
— which is the FIRST thing `check()` does, before the seed loop.  That call is
`check_seq.py:87`, `artifact.ensure(check_core.recipe("fsm"))`, which builds
because the content key moved and then FAILS the build:

```
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:255:6: Pin not found: 'ADDR_O'
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:256:6: Pin not found: 'DATA_O'
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:257:6: Pin not found: 'STATUS_O'
%Error: Exiting due to 3 error(s)
artifact.ArtifactError: ARTIFACT LAYER -- BUILD FAILED -- hdl/tb/obj_dir/Vtb_v30_core
  recipe   verilator_binary/tb_v30_core/fsm
  NOTHING WAS PROMOTED.  The previous artifact and its receipt are untouched.
```

Exit 1.  **The gate never reached a seed and never printed a verdict.**

**WHICH CORE IT BINDS, AND HOW.**  `check_seq.py:69` pins `CORE = "fsm"`
DELIBERATELY (`check_seq.py` §60-63), and `check_fuzz_bank` calls
`check_seq.run_tb` / `check_seq.tb_bin()` with no `core=` argument, so it gets
the module pin.  `check_core.recipe("fsm")` builds
`hdl/rtl/core/{v30_ss_pkg,v30_core,v30_biu,v30_eu}.sv` together with the SHARED
`hdl/tb/tb_v30_core.sv` into `hdl/tb/obj_dir/`.

**SINCE WHICH COMMIT.**  `git log -S'ADDR_O' -- hdl/tb/tb_v30_core.sv` returns
exactly one commit: **`b7083b45a5`, 2026-08-14 09:40:34 -0700**, *"LAND: the
de-muxed bus interface — ADDR_O / DATA_O / STATUS_O, V30_MUXED_AD"*.  The
corroborating artifact is the binary itself: `hdl/tb/obj_dir/Vtb_v30_core` and
its receipt were dated **2026-08-13 21:41**, i.e. **twelve hours before that
landing** — the last moment the FSM leg could be built.

**⚠ AND IT IS NOT ONLY THE TESTBENCH.**  `hdl/rtl/system_large.sv:542-544`
carries the same three pins **unconditionally** (they sit outside the
surrounding `ifdef V30_MUXED_AD` / `ifdef SYNTHESIS` blocks), so the FSM leg of
the A/B integration harness fails identically:

```
$ python3 sw/check_ab_sim.py --core fsm          ; EXIT=1
%Error-PINNOTFOUND: hdl/rtl/system_large.sv:542:6: Pin not found: 'ADDR_O'
```

**THE INVARIANT BROKEN IS THE ARCHIVE'S OWN.**
`fsm_core_archive_2026-08-04.md` §6a authorised the ONLY previous change to the
archived core — `AD_OE` — with this reason, verbatim: *"the two cores are
DROP-IN alternatives with the same module name and the same port list … A port
list that differed between them would make the A/B uncontrolled in exactly the
way §51.8b warns about."*  `hdl/rtl/ucore/v30_core.sv`'s header still states
*"same module name, same port list"* in the present tense.  **That sentence had
been false for five weeks.**

### 1a. ⚠ THE FINDING THE PRE-REGISTRATION GOT WRONG — **W18-9 IS REFUTED, AND THE REFUTATION IS WORTH MORE THAN THE CLAIM**

§1 of the pre-registration CLAIMED that `system_large.sv:542-544` breaks the FSM
**Quartus** revision too.  **It does not.**  Measured, `quartus_map
--analysis_and_elaboration nec_test -c nec_test`, single-writer checked, on the
**pre-repair** tree:

```
Info: Quartus Prime Analysis & Elaboration was successful. 0 errors, 52 warnings
```

Not one of the 52 warnings names any of the three pins.  They appear **only**
inside the Port Connectivity Checks folder of `hdl/output_files/nec_test.map.rpt`:

```
; ADDR_O   ; Unknown ; Critical Warning ; Named port was not declared by the instantiated entity ;
; DATA_O   ; Unknown ; Critical Warning ; Named port was not declared by the instantiated entity ;
; STATUS_O ; Unknown ; Critical Warning ; Named port was not declared by the instantiated entity ;
```

summarised on the console as the single line *"10 hierarchies have connectivity
warnings — see the Connectivity Checks report folder"*.

**SO THE TWO COMPILERS DISAGREE ABOUT A DEFECT, AND THE DISAGREEMENT IS THE
FINDING.**  Verilator REFUSES; Quartus 17.1 ACCEPTS AND IGNORES, with zero
errors and no console evidence.  `sw/quartus_gate.py` scores errors, latches and
`lpm_divide` and does not read the connectivity folder, so **an FSM bitstream
carrying three silently-dropped port connections would have built, passed G6 and
been flashable.**  This is the accepted-and-ignored class (E-6) inside the
compiler rather than inside a tool, and it is why `sw/core_portlist_lint.py`
exists rather than "just build it".

After the repair the same stage reads **0 errors, 52 warnings** and the three
rows become `Info ; Explicitly unconnected` — which is the positive proof that
the repair reached the compiler, and is the same phrase the de-mux results
document records for the ucore.

---

## 2. THE SIBLING INVENTORY — Job 3, reported whatever it shows

Every gate in `standing_gates.md` §C, invoked on this tree.  **BEFORE** = the
pre-repair tree (`f89f4e6978`); **AFTER** = the landing (`9ccc6d0177`).

| gate | BEFORE | AFTER | binding / stage that decides |
|---|---|---|---|
| `check_race_law` | **RUNS — PASS** (2/2 sub-checks) | RUNS — PASS | pure regeneration of `race_law.svh` / `int9d_race.hex`; never touches a binary |
| `prefix_clear_lint` | **RUNS — PASS** (20 S_FIRST sites, 4 PFX-KEEP) | RUNS — PASS | greps `rtl/core/v30_eu.sv` |
| `ea_step_lint` | **RUNS — PASS** | RUNS — PASS | greps `rtl/core/v30_eu.sv` |
| `ss_lint --core fsm` | **RUNS — PASS**, 203 addresses / 181 flops / 0 UNMAPPED | RUNS — PASS, **identical** | text + flop census, no binary |
| `check_fuzz_bank` | **DOWN** — `ArtifactError`, `PINNOTFOUND` ×3, rc 1 | **RUNS — `PASS \| 621 banked seeds \| stable 621 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0`**, rc 0 | `check_seq.tb_bin()` → the FSM TB build |
| `check_enter_nesting` | **DOWN** — same `PINNOTFOUND`, rc 1 | **RUNS — and it is RED.**  `MASK` FAIL 512/512 walk-mismatches; `WAITED` FAIL 154/154 walk-stream, 110 unexpected cycle divergences.  rc 1 | `check_seq.run_tb` → the FSM TB build |
| `check_ff_t4` | **DOWN — for a DIFFERENT reason.**  `gen_seq.V1AnchorStop`, raised before any binary is touched | unchanged — still DOWN | `gen_seq._v1_anchor_stop`: fuzz-v2 moved the code region and this gate's goldens are frozen at the v1 anchor.  **Already registered** (`CLAUDE.md`'s four-ratchet note names it) |
| `check_mod3_illegal` | **DOWN — for a DIFFERENT reason.**  `testimage.ComposeError: body [0500,0502) is not inside the code region [8000,c000)` | unchanged — still DOWN | the fuzz-v2 code-region relocation, raised in `testimage.compose` before the TB |
| `check_lc6_gate` | **DOWN — for a DIFFERENT reason.**  `testimage.ComposeError: body [0500,0517) …` | unchanged — still DOWN | same relocation, via `biu_law_lc6_gadget.build_image` |
| `sw/t30_sweep.sh` | **DOWN in 8 of its 14 legs** | **RUNS in 12 of 14** | shares every blocker above |

**AND TWO THAT ARE NOT IN §C BUT ARE IN THE SAME STATE** — this is the part the
listed set does not cover:

| | BEFORE | AFTER |
|---|---|---|
| `check_ab_sim.py --core fsm` (archive §5 names it as live: *"still 187 rows MATCH"*) | **DOWN** — `PINNOTFOUND` on `system_large.sv:542-544` | **RUNS — AB SIM MATCHES CHIP BOOT over 187 rows**, artifact `5c2db0f1c06034ba…` |
| `check_core.py --core fsm` — the archive §6 re-activation command itself | **DOWN** — the build fails | **RUNS** |

### 2a. `t30_sweep.sh`, leg by leg (it has no single verdict, so it gets a table)

| leg | status |
|---|---|
| `ss_lint --core fsm` | PASS |
| `prefix_clear_lint` | PASS |
| `ea_step_lint` | PASS |
| `check_race_law` | PASS |
| `optable --selfcheck` | **PASS — rc 0**, 0 errors, 255 one-byte ops / 26 `F0_WHITELIST` forms |
| `fuzz_campaign lint` | **PASS — rc 0**.  `LINT PASS: soup hits=0 compose_err=0; raw hits=0 compose_err=0; wvec hits=0; bias hits=0; handler hits=0` — raw 100,000 seeds in 1,456.8 s, wvec 200 × 2 × 5 in 36.6 s, and **its own four planted controls A/B/C/D all FIRE** |
| `check_ff_t4` | **DOWN** — V1 anchor |
| `check_mod3_illegal` | **DOWN** — code region |
| the six `check_core --core fsm` suite legs | **all six blocked BEFORE; all six build AFTER.**  `v0.1` measured (§3); the other five not run in this wave, `v0.3` (3.7 M cases) deliberately not run |

### 2b. ⚠ TWO LATENT STALE-BINARY HAZARDS FOUND WHILE TAKING THE INVENTORY

Neither can fire today, because both gates die earlier — but both are the
**incarnation** pattern and neither has an artifact-layer assertion:

* **`sw/check_ff_t4.py:34`** keeps its own `BIN = hdl/tb/obj_dir/Vtb_v30_core`
  and its only guard is `if not BIN.exists(): return 2`.  A **STALE** binary is
  not a missing one: it would run and it would print PASS.  For five weeks that
  path pointed at a binary built 12 hours before the demux landing.
* **`sw/causal_wrand.py:715`** does `from check_seq import BIN` — the raw path
  constant, never `tb_bin()` — and `check_lc6_gate` reaches the TB only through
  it.  Same exposure, plus every census tool that calls `run_tb_internal`.

`check_seq.py:65` already annotates `BIN` as *"ONLY a path — ask `tb_bin()` for
a binary you intend to RUN"*.  **Two consumers do not.**  Not repaired in this
wave (both gates are down for unrelated reasons, so a repair could not be shown
non-vacuous); registered in §7.

---

## 3. THE BARS, SCORED AS REGISTERED

| bar | registered | measured | verdict |
|---|---|---|---|
| **W18-1** | `check_fuzz_bank` RUNS to a verdict; the verdict itself NOT pre-registered | `PASS \| 621 banked seeds \| stable 621 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0`, rc 0, TB leg `hdl/tb/obj_dir/Vtb_v30_core` | **MET** |
| **W18-2** | `check_ab_sim --core fsm` MATCH over 187 rows | **MATCH over 187 rows**, artifact `5c2db0f1c06034ba…` | **MET** |
| **W18-3** | `check_core --core fsm` v0.1 = **168,400 / 169,000** | **169,000 / 169,000** | **⚠ MISSED — see §4** |
| **W18-4** | `ss_lint --core fsm` rc 0, 203 / 181 / 0 UNMAPPED | **rc 0, 203 addresses, 181 flops, 0 UNMAPPED** (identical before and after the edit) | **MET** |
| **W18-5** | deleting ONE new port makes `check_fuzz_bank` FAIL naming that pin | `STATUS_O` deleted → `core_portlist_lint` rc 1 naming `STATUS_O`; `check_fuzz_bank` rc 1 at `%Error-PINNOTFOUND: tb_v30_core.sv:257:6: Pin not found: 'STATUS_O'`, *"NOTHING WAS PROMOTED"*; file restored byte-identical (`git status` clean) and `check_core.require_bin('fsm')` still passes | **MET** |
| **W18-6** | a new lint FAILS on the pre-repair core and PASSES after | pre-repair copy → **rc 1**, all three ports named, both configurations; repaired tree → **rc 0**, 24 and 34 ports MATCH; unparseable file → **rc 2 CANNOT MEASURE**, never PASS | **MET** |
| **W18-7** | the ucore ladder zero-delta | see §5 | **MET** |
| **W18-8** | the full sibling inventory | §2 | **MET** |
| **W18-9** | the FSM Quartus claim is TESTED | tested, and the claim is **REFUTED** — §1a | **MET as a bar, REFUTED as a claim** |

---

## 4. ⚠ W18-3 IS A MISS, AND THE MISS IS A FINDING: TWO REGISTERED FSM FIGURES ARE STALE

The archive §5 registers, *on the corrected comparator (the TB's composed-AD
mask removed at U5)*:

| leg | §5 | **measured 2026-09-19** |
|---|---|---|
| `check_core --core fsm --opcodes all --cases 0` | 168,400 / 169,000 | **169,000 / 169,000** |
| the four HLT delay sweeps | 0/97 · 4/95 · 5/46 · 7/45 = **16 / 283** | **87/97 · 82/95 · 30/46 · 27/45 = 226 / 283** |

**THE MOVE IS THE COMPARATOR'S, NOT THE CORE'S.**  `0254d9f23e` (2026-08-05,
SM3 sitting 20, F55 part 2) replaced `tb_v30_core.sv`'s protocol-inferred
composer with an **`AD_OE`-keyed one carrying float retention**:

```
wire [15:0] eff_lo = (dut_ad_oe[0] || mem_drive) ? AD[15:0]  : hold[15:0];
wire  [3:0] eff_hi =  dut_ad_oe[16]              ? AD[19:16] : hold[19:16];
```

The archived core's `ad_oe_ps` explicitly excludes `K_HALT` (archive §3.3), so
on a HALT display `dut_ad_oe[16]` is 0 and `eff_hi` takes `hold` — the RETAINED
nibble, which is the previous CS fetch's PS, which is the value the goldens
carry.  **F51 is present, unfixed, and invisible on `tb_v30_core` again** — by a
different mechanism from the mask U5 removed, and this time the retention is a
deliberate physical model rather than a substitution.

**WHY NOBODY SAW IT.**  `0254d9f23e`'s own message says *"it moves NOTHING"* and
the receipt quoted in the testbench beside the change lists `check_core
--opcodes all` **169,000/169,000** — **that is the ucore leg**.  The FSM leg was
never re-measured, and nine days later `b7083b45a5` made it unmeasurable.

**NOTHING IS RETRACTED.**  §5's figures are that comparator's and remain true of
it.  What must change is that *"the corrected comparator"* now names a **third**
instrument, and no FSM figure is quotable without saying which.  Adjudicating
whether the retention model is right for a HALT display is **not this wave's
work** and is not started.

---

## 5. THE ucore LADDER — ZERO-DELTA (U-5 / W18-7)

Measured on the landing, **on this tree** (nothing carried from another):

| leg | measured |
|---|---|
| `check_core.py --opcodes all --cases 0` | **169,000 / 169,000** full (cycles 169,000, arch 169,000) |
| `ulockstep.py --golden all --cases 50` | **17,350 / 17,350 — ALL CASES LOCKSTEP** |
| `chain_lfsr_gate.py` | **PASS** — CHAIN_MAX 7, observed depth [6], 0 overflows, 4 seeds × 400,000 clocks; signatures **`1d01c9b269ffaa94 · b39b040a98b28e5d · 0997b773cd99c030 · d05b6c3c3d9fbe78`** — **byte-identical** to the registered set |
| `r7_lint.py` | **PASS** — 0 undeclared carriers, 0 undeclared unresolved, 0 `stop` sites |
| `ss_lint.py` (ucore) | **PASS** — 109×2 BIU + 122×2 EU + tag = **232**; **229** architectural flops, 4 whitelisted, **0 UNMAPPED** — exactly the `flash22_results_2026-09-19.md` row |
| `demux_off_gate.py` | **PASS** — the de-muxed core builds and runs, the two muxed ports are GONE, and the define is what removes them |

The edit is confined to `hdl/rtl/core/v30_core.sv`, which is not an input of
`check_core.recipe("ucore")`, so the ucore binary did not even rebuild — the
ladder is a confirmation, not a re-derivation.

---

## 6. `check_enter_nesting` IS RED, AND THAT IS REPORTED, NOT EXPLAINED

It could not run for five weeks and now it does, and it reports
**MASK 512/512 walk-mismatches** and **WAITED 154/154 walk-stream FAIL** with
110 unexpected cycle divergences — total, not marginal.

**THIS IS THE FIRST MEASUREMENT SINCE 2026-08-14 AND POSSIBLY SINCE LONG
BEFORE.**  The archive (2026-08-04) states these gates *"still pass"*; nothing
between then and now re-measured this one.  It is **NOT** caused by this wave's
edit — the three added ports have no reader inside the core and cannot reach
`AD` — and it is **NOT** diagnosed here.  The two candidate classes, neither
tested to a conclusion in this wave:

* **the instrument/era class.**  `check_enter_nesting.check_mask` composes its
  images with `testimage.compose(...)`, whose code region moved to
  `[8000,C000)` under fuzz-v2 (plan D9), while the goldens in
  `tests/v30/enter_nesting/` are v1-anchored captures.  This is the same family
  that takes down `check_ff_t4`, `check_mod3_illegal` and `check_lc6_gate` — the
  difference being that those three RAISE and this one silently compares.
* **the archived core's own drift** — archive §3.2's undiagnosed 104-seed
  regression is in this family of *"a reference that can silently regress"*.

**THE DISCRIMINATOR WAS REGISTERED AND THEN RUN, AND IT ANSWERS**: the identical
instrument with the identical goldens, `check_seq.CORE` monkey-patched to
`"ucore"` and nothing else changed —

```
=== ENGINE ucore ===
  MASK (w0, nesting 0..255 x2): FAIL | 512 goldens | max stack pushes 256 (nest=255=>256) | walk-mismatches 512
```

**THE ucore FAILS THE SAME 512.**  The RED is **ENGINE-INDEPENDENT**, so it is
the instrument/era and NOT the archived core: `check_enter_nesting` is a
**fourth casualty of the fuzz-v2 code-region relocation**, alongside
`check_ff_t4`, `check_mod3_illegal` and `check_lc6_gate` — and the only one of
the four that does not RAISE.  The other three announce the era mismatch and
refuse; this one composes an image the goldens were never captured from and
compares it, so it prints a 100 % divergence that reads like a core regression.

⚠ **THAT IS THE DANGEROUS MEMBER OF THE FAMILY** and it is worth its own line in
the vacuous-gate meta-finding: **a loud RED can be as false as a silent GREEN**,
and the thing that separates them is whether the instrument checks its own era.
`gen_seq._v1_anchor_stop` is exactly that check, and `testimage.compose` (which
this gate uses instead) only raises when the ADDRESS is out of region, which for
the ENTER tranche it is not — the stack walk at `[2000,3FFF)` is composable at
either anchor.

**NOTHING IS CONCLUDED ABOUT THE ARCHIVED CORE FROM THIS RED**, and the archive's
2026-08-04 *"they still pass"* is neither confirmed nor refuted by it.  Deciding
whether to re-anchor the tranche or re-capture it is board work and a USER
DECISION, exactly as `gen_seq._v1_anchor_stop` says of its own four.

---

## 7. WHAT NEEDS REGISTERING IN `standing_gates.md` — **NOT EDITED HERE** (U-7)

1. **§C header**: the FSM-specific gates bind `hdl/tb/tb_v30_core.sv` AND
   `hdl/rtl/system_large.sv`, both SHARED with the ucore.  **An edit to either
   that adds a port breaks every one of them, and the standing set does not see
   it.**  `b7083b45a5` did exactly that on 2026-08-14 and it went unnoticed for
   five weeks; it surfaced only because FLASH #22 copied a `PASS 621` row across
   trees.
2. **A NEW GATE**: `python3 sw/core_portlist_lint.py` (0.1 s, offline, exit
   0/1/2) — the two `v30_core` port lists must agree under `V30_MUXED_AD`, with
   and without `V30_BACKDOOR`.  Non-vacuous three ways (§3, W18-6).  It belongs
   in the **standing** set, not in §C: it protects the UCORE's shared files as
   much as the archive's.
3. **§C's `check_fuzz_bank` row**: the gate ran on 2026-09-19 at `9ccc6d0177` —
   `PASS | 621 | stable 621 | improved 0 | worse 0 | gen_drift 0 | regen_err 0 |
   float-floor 0 | new-sig TIMING 0`.  ⚠ **And a note that FLASH #22's identical
   row was COPIED and could not have been measured**: the gate had been
   unrunnable since 2026-08-14.  The figure is right; the row was unearned when
   it was written and is earned now.
4. **§C's `check_enter_nesting` row**: **RED as of 2026-09-19** — MASK 512/512
   walk-mismatch, WAITED 154/154 — first measurement since 2026-08-14.  **The
   engine control was run and the RED is ENGINE-INDEPENDENT** (the ucore fails
   the identical 512), so it is a **fourth v1-anchor/code-region casualty**, not
   an FSM regression, and it belongs beside `check_ff_t4`,
   `check_mod3_illegal` and `check_lc6_gate` rather than in the archive's
   defect list.  ⚠ It is the only one of the four that does **not** raise: it
   composes a v2-anchored image, compares it to v1-anchored goldens and prints
   100 % divergence.  **A loud RED can be as false as a silent GREEN.**
5. **§C's `check_ff_t4`, `check_mod3_illegal`, `check_lc6_gate` rows**: all
   three **DOWN for the fuzz-v2 code-region / v1-anchor reason**, independently
   of the demux break.  `check_ff_t4` is already covered by `CLAUDE.md`'s
   four-ratchet note; the other two are not.
6. **The archive's FSM figures (§5, and the note in `t30_sweep.sh`)**: the
   *"read against 168,400, not 169,000"* rule is **stale**.  On the current
   comparator the archived core is **169,000/169,000** and **226/283**.  §4
   above has the mechanism and `fsm_core_archive_2026-08-04.md` §6b carries it.
7. **`sw/t30_sweep.sh` DISCARDS EVERY LEG'S EXIT CODE** — each leg is
   `… 2>&1 | tail -1`, so the sweep prints verdict lines and aggregates
   nothing.  A failing leg does not fail the sweep, and the reader is the only
   check.  (Found because this document's first draft made the same mistake
   when scoring two of those legs; corrected before anything was quoted.)
8. **§C's two latent stale-binary hazards** (§2b): `check_ff_t4.py:34` and
   `causal_wrand.py:715` both use the raw `check_seq.BIN` path with no
   artifact-layer assertion.  A stale binary would score.
9. **A meta-finding for the vacuous-gate list** — this one is the mirror image
   of the five already there.  **Those five were GREEN while blind.  This one
   could not run at all, and the ledger still carried its green row**, because
   the row was copied rather than measured.  *A gate's registered row and the
   gate's ability to run are two different facts, and only one of them is
   checked.*  Related: **Quartus accepted the same defect with 0 errors** (§1a),
   so "the bitstream built" is not evidence that a port list is intact.

---

## 8. DISCIPLINE

Offline only; no board contact and no flash — FLASH #22 stands.  No Codex, no
nested subagents.  Single-writer `pgrep -x quartus_map` / `-x quartus_sh` before
each Quartus stage (both clean, both times).  No `git stash`, `git checkout .`
or `git reset --hard`; every `git add` by explicit path and no
`sw/testdata/receipts/*.jsonl` staged.  Temporaries under
`~/.cache/ucsimt-tmp/wave18/`.  Every figure above was measured on this tree;
nothing was carried from another.

⚠ **A SECOND TRAP, AND THIS ONE CAUGHT THIS DOCUMENT'S OWN FIRST DRAFT.**  The
two `t30_sweep.sh` lint legs above were first run as `cmd 2>&1 | tail -1; rc=$?`
— which captures **`tail`'s** exit code, not the tool's, and prints `rc=0`
whatever the tool did.  `t30_sweep.sh` itself is written in exactly that shape
(`… 2>&1 | tail -1` on every leg), so **the sweep's own legs report their
verdict LINE and discard their EXIT CODE**; it has `set -uo pipefail` but no
aggregation, so a failing leg does not fail the sweep.  Both legs were
re-measured with the real exit code captured (`REAL_EXIT=0` on each) before
anything was scored here.  *An instrument that cannot fail is not measuring* —
this is the eleven-instruments rule landing on the reporter rather than on the
subject.

⚠ **ONE TRAP FOUND BY WALKING INTO IT, AND WORTH REGISTERING.**  Running
`quartus_map … nec_test -c nec_test` **REWRITES `hdl/nec_test.qsf` AND
`hdl/nec_test.qpf` IN PLACE** — the `.qsf` is expanded from its 126-line
hand-maintained form to 307 lines of fully-enumerated assignments, and the
`.qpf` swaps its two `PROJECT_REVISION` lines and re-stamps `DATE`.  Left there
it would have made `hdl/nec_test_ucore.qsf` stop looking like a derivative of
its parent.  **Both files were restored to `HEAD` by explicit path** (never
`git checkout .`) and `python3 sw/gen_ucore_qsf.py --check` re-verified:
*"nec_test_ucore.qsf is up to date"*.  Anyone running a Quartus stage on the
**FSM** revision must check `git status hdl/nec_test.qsf hdl/nec_test.qpf`
afterwards.

---

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
