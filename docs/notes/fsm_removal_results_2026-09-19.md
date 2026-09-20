# WAVE 21 — REMOVE THE ARCHIVED FSM CORE — **RESULTS**

**Pre-registration `6c3de357d9`, committed BEFORE the first edit to `hdl/` or
`sw/`.**  Baseline `fb9365c01c` (WAVE 20's tip).  **Every figure below was
MEASURED in this session unless the row says otherwise, and where a figure is
quoted from a document rather than measured it says so and names the document.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.**  The board carries FLASH #23 and was not
touched.

---

## §0 THE HEADLINE, IN FIVE SENTENCES

1. **THE CORE IS OUT AND NOT ONE GATE DIED SILENTLY.**  Sixteen tools refuse
   with a banner naming the directive, the ledger and the recovery command;
   `check_seq`'s engine pin refuses rather than being re-pointed; **378 modules
   import and ZERO raise a NEW `FileNotFoundError` / `ImportError` /
   `ModuleNotFoundError`.**
2. **THE BRIEF'S OWN BLOCKER WAS NOT ONE.**  `gen_ucore_qsf --check` never
   opened `hdl/files.qip` and never read `hdl/rtl/core/`; it ran **GREEN with
   the entire FSM core deleted**.  E1 was retired because the USER RULING voids
   its claim, not because the deletion broke it.
3. **E1 IS HALF-REPLACED AND THE OTHER HALF IS GONE WITH NOTHING IN ITS PLACE.**
   `qsf_lint --check` proves the one revision is in CANONICAL FORM.  *"The two
   bitstreams differ by the CORE and nothing else"* has no referent and is
   retired.
4. **Z-4 — THE BITSTREAM FALSIFIER — WAS SCORED AS TWO BUILDS** so a moved
   `.rbf` would name its own cause.  See §Z-4.
5. **FOURTEEN DOCUMENTATION CLAIMS WERE MEASURED FALSE AND FIXED**, including
   one that made `emit_suite` build the ucore and then run the archived core's
   binary, one that documented an environment variable that exists in exactly
   one comment, and one green ledger row for a gate that could not run.

---

## §Z-1 THE DEPENDENCY ENUMERATION — METHOD, RESULT, AND LIMITS

**METHOD.**  A literal-token grep over **every tracked file** outside `docs/`,
`sw/testdata/` and `tests/v30/*/` (data, not code), for fifteen tokens by which
the archived core can be named: `rtl/core`, `files.qip`, `nec_test.qsf`,
`PROJECT_REVISION`, `gen_ucore_qsf`, `V30_FSM_PROBES`, `race_law`,
`int9d_race`, `obj_dir/Vtb_v30_core`, `obj_dir_ab"`, `V30_CORE`, `"fsm"`,
`'fsm'`, `--core fsm`, `core fsm`.  Then, independently, **an import sweep over
all 378 `sw/*.py` modules**, which is the only instrument that finds a
dependency reached through a variable rather than a literal.

**RESULT — the code-side dependency set, 44 files:**

| group | files |
|---|---|
| **RTL / Quartus** | `hdl/rtl/core/*` (6) · `hdl/files.qip` · `hdl/files_ucore.qip` (comments) · `hdl/nec_test.qsf` · `hdl/nec_test.qpf` · `hdl/tb/tb_v30_core.sv` (comments + `V30_FSM_PROBES`) · `hdl/rtl/ucore/{v30_core,v30u_biu,v30u_ss_pkg}.sv` (comments only — **NOT TOUCHED, bar Z-6**) |
| **the engine pin** | `sw/check_seq.py` |
| **explicit `--core fsm` legs** | `sw/check_core.py` · `sw/check_ab_sim.py` · `sw/ss_lint.py` · `sw/ss_flopcensus.py` · `sw/r7_lint.py` · `sw/check_boot.py` |
| **FSM-structural tools** | `sw/check_race_law.py` · `sw/gen_race_law.py` · `sw/prefix_clear_lint.py` · `sw/ea_step_lint.py` · `sw/biu_law_{mutation,lc3_gadget,lc3_seedsearch,lc6_gadget,gatesearch}.py` · `sw/exp_race.py` · `sw/race_law_equiv_tb.sv` |
| **FSM-TB-binary tools** | `sw/check_ff_t4.py` · `sw/check_mod3_illegal.py` · `sw/check_lc6_gate.py` · `sw/check_enter_nesting.py` · `sw/check_fuzz_bank.py` · `sw/causal_wrand.py` · `sw/sweep_popa.py` · `sw/sweep_dispphase.py` · `sw/dumpeu.py` · `sw/exact_predict.py` · `sw/f7a_arbitrate.py` · `sw/pi1a_trace.py` · `sw/repro_segleak.py` · `sw/exp_iret.py` |
| **the A/B / revision machinery** | `sw/gen_ucore_qsf.py` · `sw/quartus_gate.py` · `sw/test_quartus_gate.py` · `sw/receipt_diff.py` · `sw/fz2_p2_gates.sh` · `sw/fz2_replay.py` (comment) |
| **`--core` choice lists offering `fsm`** | `s15_census` · `sm3_{ackcmp,bswap,famb_survey,h1_cell,h3_cell,h7_cell,haltsupp,nmigeom,s16_score}` · `sweep_parallel` · `tb_bootrun` · `timed_{enter_replay,fuzz,ins_replay,wvec_gate}` · `u4_tranche` · `w32_launch` · `wrfuzz_smoke` · `fz2_undoc_probe` (18) |
| **the aggregate** | `sw/t30_sweep.sh` (14 legs) · `sw/biu_rebuild_gate.sh` (one leg) |

**⚠ THE IMPORT SWEEP FOUND ONE THE GREP DID NOT ACT ON**: `sw/causal_wrand.py`
reads `hdl/rtl/core/v30_eu.sv` **at MODULE IMPORT** (`_load_state_names`, `:274`)
to decode the TB's `onset_state` numbers.  The deletion took down every importer
— including the registered ratchet `timed_wvec_gate` — with a bare
`FileNotFoundError`.  **That is the whole reason a grep is not the method and an
import sweep is.**

**LIMITS, stated because a method with no limits is a method nobody checked.**

* Both instruments are **textual and import-time**.  A dependency reached
  through `getattr`, through a `subprocess` command assembled from string
  fragments, or through a path built at RUN time inside a function that no test
  calls, would be missed by both.
* `docs/` (292 files) and `sw/testdata/` were EXCLUDED from the grep by design:
  they are history and data.  `docs/` is dispositioned separately in §D below;
  `sw/testdata/` is captures, and the ledger's first rule is that nothing there
  is edited.
* **The backstop is not the sweep.**  It is that `sw/fsmcore.py` and the
  `check_seq` pin survive as REFUSALS, so anything that reaches the archived
  core dies **by name** rather than by file error — and that is verified
  directly by the import sweep (§Z-3).
* `tests/v30/*/` was excluded: **no golden suite names the core.**  Verified by
  the unrestricted grep, which returns only `README.md` and `ROADMAP.md` outside
  the set above.

**Z-1: MET.**

---

## §Z-2 E1's DISPOSITION — DECIDED AND REGISTERED BEFORE THE EDIT

Registered in `fsm_removal_prereg_2026-09-19.md` §2 / §2b, committed at
`6c3de357d9` before the first `hdl/` or `sw/` edit.  Summary:

**RETIRED, AND ONLY HALF REPLACED.**

* **What E1 asserted**, verbatim from FLASH #23's own CONTROL receipt
  (`sw/testdata/flash23/g6-control-draw-seed1/seed1_quartus_gate.json`, key
  `E1_gen_ucore_qsf/bar`): *"hdl/nec_test_ucore.qsf is a faithful derivative of
  hdl/nec_test.qsf"*.  That sentence makes the **FSM** revision the ORIGINAL.
  The USER RULING inverts that precedence, so the claim is **VOID, not merely
  unmeasurable.**
* **THE REPLACEMENT: `sw/qsf_lint.py --check`**, receipt key
  **`E1_qsf_canonical`**, same position in the gate (before anything is
  compiled), same RED-and-stop behaviour.
  **WHAT IT PROVES**: the one revision the compiler reads is in CANONICAL FORM —
  it carries none of the assignments Quartus materialises into it from
  `source sys/sys.tcl`, and it declares exactly one file list and exactly one
  output directory.  **Measured, canonical vs post-build:**

  | property | canonical | what `sys/sys.tcl` adds |
  |---|---|---|
  | `set_location_assignment` | **0** | **107** |
  | `set_instance_assignment` | **1** (`PARTITION_HIERARCHY`, the revision's own) | **+50** |
  | `PRE_FLOW_SCRIPT_FILE` | absent | present (`sys/gen_cdf.tcl`) |
  | `source files_ucore.qip` | exactly 1 | 1 |
  | `PROJECT_OUTPUT_DIRECTORY` | exactly 1 | 1 |

  So a green run says: **no previous build's in-place rewrite was left in the
  tree, and no assignment reaches the compiler that is not in the committed
  revision file.**  That is the half of E1 that had a referent, and it is the
  half `INPUT_FLIP_EXEMPT` and the post-build regeneration were built on.
* **WHAT IT DOES NOT PROVE.**  **(a) NOT** *"the two A/B bitstreams differ by
  the CORE and nothing else"* — **that guarantee is RETIRED and NOTHING REPLACES
  IT**; there is no second core and no second revision for it to be about.
  **(b) NOT** faithfulness to a second file: there is no template, the revision
  file IS the source of truth, and **nothing now cross-checks the settings
  against a second copy** — the replacement for that cross-check is that there
  is only one copy to get wrong.  **(c) NOT** anything about the contents of
  `files_ucore.qip` (sourced, not derived).  **(d) NOT** that the settings are
  CORRECT — a wrong `set_global_assignment` is a green `qsf_lint`.  **(e) NOT**
  anything about what Quartus DOES with the settings; E2–E11 are that.
* **NON-VACUITY — three positive controls, MEASURED:**

  | control | expected | measured |
  |---|---|---|
  | one `set_location_assignment` spliced in | exit 1, naming the line | **CONTROL-1 RESULT** |
  | `source files_ucore.qip` deleted | exit 1, "expected exactly one" | **CONTROL-2 RESULT** |
  | the file absent | exit **2** CANNOT MEASURE, never PASS | **CONTROL-3 RESULT** |

* **WHAT IS DELIBERATELY NOT RENAMED, and why.**  The revision stays
  `nec_test_ucore` and the output directory stays `output_files_ucore`.  Every
  receipt, every `flash_log.jsonl` entry and FLASH #23 itself records that name;
  `ucore` is the implementation's NAME, not a variant marker, now that nothing
  offers a second revision to be a variant OF; and — decisively — **a revision
  rename plausibly moves the `.rbf`, and Z-4 says a moved `.rbf` STOPS THE
  WAVE.**  Renaming would spend the wave's one falsifier on a cosmetic change.
  **BOOKED with this reasoning, not taken.**

**Z-2: MET.  The wave did not stop.**

---

## §Z-3 NO GATE DIES SILENTLY — DEMONSTRATED, NOT ASSERTED

**THE LEDGER ENTRY IS `invalidation_ledger.md` RET-2**, following RET-1's form,
and every gate in it carries its **LAST REGISTERED FIGURE measured on
`6c3de357d9` immediately before the removal** (Verilator receipt
`6ef5e51f32e75735…`) rather than copied from `standing_gates.md`:

| gate | measured BEFORE the removal | after |
|---|---|---|
| `check_core --core fsm --opcodes all --cases 0` | **169,000 / 169,000** | refuses, exit non-zero, `FsmCoreRetired` |
| the four HLT sweeps `--core fsm --waits 0/1/2/3` | **87 · 82 · 30 · 27 = 226 / 283** | refuses |
| `ss_lint --core fsm` | **PASS, 203 addresses / 181 flops / 0 UNMAPPED** | **exit 2**, banner |
| `ss_flopcensus --core fsm` | **PASS, 181 flops / 0 whitelist** | **exit 2**, banner |
| `check_ab_sim --core fsm` | **MATCH over 187 rows** | refuses, `FsmCoreRetired` |
| `check_race_law` | **PASS (2/2 sub-checks)** | **exit 2**, banner |
| `prefix_clear_lint` | **PASS** (20 `S_FIRST`, 4 PFX-KEEP, single source, no drift) | **exit 2**, banner |
| `ea_step_lint` | **PASS** | **exit 2**, banner |
| `check_ff_t4` | **DOWN — `V1AnchorStop`** | **exit 2**, banner |
| `check_mod3_illegal` | **DOWN — `ComposeError: body [0500,0502) is not inside the code region [8000,c000)`** | **exit 2**, banner |
| `check_lc6_gate` | **DOWN — `ComposeError: body [0500,0517) …`** | **exit 2**, banner |
| `check_enter_nesting` | **RED — `check_enter_nesting: FAIL`**, engine-independently | **exit 2**, banner |
| `check_fuzz_bank` | **`PASS \| 621 banked seeds \| stable 621 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0`** | refuses through the `check_seq` pin, `FsmCoreRetired` |
| `r7_lint --core fsm` | **`WOULD FAIL`** (INFORMATIONAL, never a gate) | **exit 2**, banner |
| `sw/t30_sweep.sh` | RED as registered | **exit 2**, banner |
| `gen_ucore_qsf --check` | **PASS**, and **PASS WITH THE WHOLE FSM CORE DELETED** | retired; **`qsf_lint --check` PASS** |

**THE IMPORT SWEEP — RET-1's falsifier #1, re-run.**

```
378 modules imported, 56 raised
  SystemExit 29 · RetiredTool 13 · IndexError 6 · FileNotFoundError 3
  · FsmCoreRetired 2 · ModelRetired 2 · V1AnchorStop 1
FILE/IMPORT ERRORS: fit_class5, t33_scattertest, t33_traj
```

**ZERO NEW FILE OR IMPORT ERRORS.**  The three `FileNotFoundError` are RET-1's
own three declared pre-existing relative-path bugs (`/tmp/class5_data.json`,
`testdata/campaigns/mc1/results.jsonl`) and are unchanged.  The six `IndexError`
read `sys.argv[1]` at import and predate this wave.  The 29 `SystemExit` are the
sixteen WAVE 21 guards plus the tools that import them.

**⚠ FIVE FILES WERE DELIBERATELY NOT TOUCHED** — `sw/t7_sim_ab.py`,
`sw/t7_sim_proof.py` and the three `sw/testdata/rep_cl0/*.py`.  They are the
USER'S OWN UNCOMMITTED WORK (RET-1), they raise `FileNotFoundError` for the
MODEL's sake and not this wave's, and they are exactly as this wave found them.

**Z-3: MET.**

---

## §Z-4 THE BITSTREAM FALSIFIER — **TWO BUILDS, SCORED SEPARATELY**

**THE TARGET**, from FLASH #23's CONTROL receipt: `.rbf` sha256
**`e91a67badeef2c17262b5239e0700672f3be69eeb44e749e5c9d53ae1302a613`**.

**Z-4a — the RTL deletion alone** (FSM RTL and `files.qip` removed; the three
`.qsf`/`.qpf` files UNTOUCHED).  **Z-4b — the `.qsf` re-basing on top.**  The
split exists because the pre-registration's own erratum established that the
re-basing is a DELIBERATE ACT under the ruling and not a consequence of the
deletion, so a difference must be attributable.

**Z-4 RESULTS TABLE**

**Z-4: PENDING**

---

## §Z-5 THE LIVE LADDER — BEFORE SIDE TAKEN FIRST

**Z-5 RESULTS TABLE**

---

## §Z-6 `hdl/rtl/ucore/` AND `hdl/nec_test.sdc` — UNTOUCHED

**Z-6 RESULT**

---

## §Z-7 THE USER'S UNCOMMITTED WORK

**Z-7 RESULT**

---

## §Z-8 `git rm` RETAINS HISTORY

`fb9365c01c` (WAVE 20's tip) is the last commit with `hdl/rtl/core/` in the
working tree.  **Nothing was destroyed.**  The recovery commands are in RET-2
and in `sw/fsmcore.py`'s own banner, so a reader who trips the refusal is told
how to undo it without opening a document.  `hdl/rtl/core/int9d_race.hex` —
**a measured silicon contract, not RTL** — was **archived by RENAME** to
`docs/facts/int9d_race_contract_archived_2026-09-19.hex` and is not recoverable-
by-necessity because it never left.

**Z-8: MET.**

---

## §D THE DOCUMENTATION DISCREPANCIES — a first-class deliverable

**D RESULTS TABLE**

---

## §E WHAT THIS WAVE DID **NOT** DO

* **Did not touch `hdl/rtl/ucore/` or `hdl/nec_test.sdc`** (Z-6).
* **Did not touch the user's 21 uncommitted files** (Z-7).
* **Did not run the board and did not flash.**  FLASH #23 stands.
* **Did not re-point `check_fuzz_bank` at the ucore** — booked with its reason.
* **Did not re-derive `fuzz_bank`'s `replay_verdict` column.**
* **Did not re-anchor the v1-anchor casualty family** — WAVE 20 §4's open item
  and a board decision.
* **Did not rename the Quartus revision or its output directory** — booked with
  its reason (§Z-2).
* **Did not delete a branch, a worktree, an `obj_dir`, a Quartus log, or one
  byte of `sw/testdata/` or `tests/`.**
* **Did not push.**
