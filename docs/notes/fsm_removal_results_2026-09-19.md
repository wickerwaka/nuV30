# WAVE 21 — REMOVE THE ARCHIVED FSM CORE — **RESULTS**

**Pre-registration `6c3de357d9`, committed BEFORE the first edit to `hdl/` or
`sw/`.**  Baseline `fb9365c01c` (WAVE 20's tip).  **Every figure below was
MEASURED in this session unless the row says otherwise, and where a figure is
quoted from a document rather than measured it says so and names the document.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.**  The board carries FLASH #23 and was not
touched.

---

## §0 THE HEADLINE, IN FIVE SENTENCES

1. **THE CORE IS OUT AND NOT ONE GATE DIED SILENTLY.**  **Eighteen files refuse
   by name** — sixteen tools carrying an explicit `sw/fsmcore.py` guard, plus
   `sw/t30_sweep.sh` and `sw/gen_ucore_qsf.py` — each with a banner naming the
   directive, the ledger and the recovery command; and `check_seq`'s engine pin
   refuses rather than being silently re-pointed, which is what carries the
   refusal to everything downstream of it.  **378 modules import and ZERO raise
   a NEW `FileNotFoundError` / `ImportError` / `ModuleNotFoundError`.**
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
5. **SEVENTEEN DOCUMENTATION CLAIMS WERE MEASURED FALSE AND FIXED**, including
   one that made `emit_suite` build the ucore and then run the archived core's
   binary, one that documented an environment variable that exists in exactly
   one comment, one green ledger row for a gate that could not run — and
   **`CLAUDE.md`'s DEFINITION OF THE PROMOTION GATE ITSELF**, which named the
   retired tool as E1 for the length of this wave (§D-15).

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
* **NON-VACUITY — SIX POSITIVE CONTROLS, MEASURED, AND THEY ARE A STANDING
  FALSIFIER RATHER THAN A ONE-OFF.**  They live in `sw/test_quartus_gate.py` as
  **Q18**, so the new bar cannot quietly stop firing:

  | control | expected | measured |
  |---|---|---|
  | the real tree (the POSITIVE CONTROL, reported first) | exit 0, "CANONICAL" | **PASS** |
  | one `set_location_assignment` spliced in | exit 1, the line NAMED | **exit 1, `PIN_AA1` and `MATERIALISED` both printed, plus the `git checkout --` restore command** |
  | `source files_ucore.qip` deleted | exit 1, "expected exactly one" | **exit 1, "found 0"** |
  | a second `PROJECT_OUTPUT_DIRECTORY` | exit 1 | **exit 1** |
  | the file absent | exit **2** CANNOT MEASURE, never PASS | **exit 2, "CANNOT MEASURE"** |
  | the file EMPTY | exit **2** | **exit 2** |
  | ⚠ a COMMENTED-OUT `set_location_assignment` | **exit 0** — a lint that fired on every build is a lint nobody reads | **exit 0** |

  Q18 also asserts the GATE IS WIRED, not just that the lint works:
  `quartus_gate.py` calls `sw/qsf_lint.py`, the receipt key is
  `E1_qsf_canonical`, and `gen_ucore_qsf.py` is **no longer invoked**.
  **`test_quartus_gate` 287 → 302 / 302**, a rise of 15, pre-registered as a
  possible move and itemised here.

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

**Z-4 RESULTS — BOTH LEGS MET.  THE `.rbf` IS BYTE-IDENTICAL, TWICE.**

| | FLASH #23 CONTROL | **Z-4a** — FSM RTL + `files.qip` removed, `.qsf`/`.qpf` untouched | **Z-4b** — the `.qsf` re-basing on top |
|---|---|---|---|
| verdict | PASS | **PASS** | **PASS** |
| **`.rbf` sha256** | `e91a67badeef2c17…` | **`e91a67badeef2c17…` — IDENTICAL** | **`e91a67badeef2c17…` — IDENTICAL** |
| `.sta.summary` sha256 | `3d951d451a4d51f7…` | **IDENTICAL** | **IDENTICAL** |
| Fmax (`divclk`) | 34.68 MHz | **34.68** | **34.68** |
| worst setup | +2.419 ns | **+2.419** | **+2.419** |
| ALMs | — | 8,434 / 41,910 (20 %) | 8,434 / 41,910 (20 %) |
| TNS setup+hold, every domain | 0.000 | **0.000** | **0.000** |
| errors / latches / `lpm_divide` | 0 / 0 / 0 | **0 / 0 / 0** | **0 / 0 / 0** |
| `input_manifest` | `ee6a4eff46e483d3…`, **99** files | `ee6a4eff46e483d3…`, **99 — IDENTICAL** | `5fedcfccf841f604…`, **98** |
| E1 | `E1_gen_ucore_qsf` PASS | `E1_gen_ucore_qsf` **PASS** | **`E1_qsf_canonical` PASS** |
| receipt | `sw/testdata/flash23/…` | **`cf468aa4fc361a6a…`** | **`3dbde6847d004851…`** |

Both receipts are committed at `sw/testdata/wave21/z4{a,b}_quartus_gate.json`.

**WHAT Z-4a PROVES, and it is the strong one.**  Deleting `hdl/rtl/core/` (6
files, 467,184 bytes) and `hdl/files.qip` left the CONTROL bitstream
**byte-identical** AND the 99-file input manifest **hash-identical**.  The FSM
core was not reaching the ucore revision by any route — not through the file
list, not through the search path, not through a stale `db/`.  **The removal is
bitstream-neutral, measured rather than argued.**

**WHAT Z-4b PROVES.**  Deleting `hdl/nec_test.qsf`, dropping the `nec_test`
revision from the `.qpf`, authoring the revision file's header and rewriting
`files_ucore.qip`'s comments **also** left the `.rbf` byte-identical.  The
manifest moved exactly as registered: **99 → 98**, the one file removed is
`hdl/nec_test.qsf`, and the two whose content moved are `hdl/files_ucore.qip`
and `hdl/nec_test_ucore.qsf` — **comment-only edits in both, which is why the
compiler's output does not move.**  Nothing else in the 98 changed.

⚠ **TWO THINGS MEASURED HERE THAT NOBODY ASKED FOR, RECORDED BECAUSE THEY ARE
TRUE.**

1. **THE `.sof` DIFFERS ON EVERY BUILD AND THE `.rbf` DOES NOT.**  Three builds
   of the identical configuration give three `.sof` hashes (`d6d3a6d3c2c85159…`,
   `130dbabfa706e70b…`, `8316d0b62fa47d1d…`) and ONE `.rbf` hash.  **The `.sof`
   is not a byte-identity instrument and must not be used as one**; the `.rbf`
   is.  `sw/quartus_gate.py` hashes both and this wave is the first to notice
   they disagree about reproducibility.
2. ⚠ **QUARTUS DID NOT REWRITE THE REVISION `.qsf` ON THIS FLOW.**  The new
   post-build restore reported `{"restored": false, "why": "unchanged by the
   build"}`, and **E7 reported `n_moved: 0` with `moved_exempt: []` on BOTH
   builds** — so the `INPUT_FLIP_EXEMPT` entry that exists for §70.7's rewrite
   was VACUOUS on these runs.  The rewrite is real for other invocations (it is
   why the exemption and the post-build regeneration were built at all) and
   `quartus_sh --flow compile` with the gate's own stage flags did not trigger
   it here.  **RECORDED, NOT EXPLAINED.**  `qsf_lint`'s bar is unaffected: it
   checks canonical form whether or not anything rewrote the file.

**Z-4: MET on both legs.  The wave did not stop.**

**THEREFORE, AND CONDITIONALLY: THIS REMOVAL INCURS NO NEW FABRIC DEBT.**  The
CONTROL bitstream this tree builds is byte-identical to the one FLASH #23's
campaign built, so the board's contents are unaffected by construction.  **That
statement is CONDITIONAL ON Z-4 and on nothing else** — it would be withdrawn
the moment a `.rbf` moved.  **NOTHING WAS FLASHED.  FLASH #23 STANDS.**  The
FLASH #21 (v)/(vi) debt and every other pre-existing fabric debt are unchanged.


---

## §Z-5 THE LIVE LADDER — BEFORE SIDE TAKEN FIRST

**BOTH SIDES MEASURED IN THIS SESSION.  BEFORE at `6c3de357d9` (the
pre-registration commit, the FSM core still in the tree); AFTER at `a09f34defd`
(the core, the FSM Quartus revision and the TB's probe block all gone).  Both
logs are committed at `sw/testdata/wave21/{before,after}_ladder.txt`.**

| leg | BEFORE | AFTER | |
|---|---|---|---|
| `check_core --opcodes all --cases 0 --ce-div 4` | 169,000 / 169,000 | **169,000 / 169,000** | SAME |
| ` … --ce-div 2` | 169,000 / 169,000 | **169,000 / 169,000** | SAME |
| ` … --ce-div 3` | 169,000 / 169,000 | **169,000 / 169,000** | SAME |
| ` … --ce-div 8` | 169,000 / 169,000 | **169,000 / 169,000** | SAME |
| ` … --ce-div 1` | REFUSED, exit 2, clause cited | **REFUSED, exit 2** | SAME |
| **the exact 181** — `FA` | 500 / 500 | **500 / 500** | SAME |
| ` ` `FB` | 500 / 500 | **500 / 500** | SAME |
| ` ` `INT.FB` | 200 / 200 | **200 / 200** | SAME |
| the four HLT sweeps, `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = **279 / 283** | **97 · 93 · 45 · 44 = 279 / 283** | SAME |
| `r7_lint` | PASS — 0 carriers / 0 unresolved / 0 `stop` sites | **PASS, identical** | SAME |
| `ss_lint` | PASS — 109×2 BIU + 122×2 EU + tag = **232**, 229 flops, 4 whitelist, 0 UNMAPPED, `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8 | **identical** | SAME |
| `cutset_lint` | PASS — 81 members / 0 violations | **PASS 81 / 0** | SAME |
| `phase_split_lint` | PASS — 157 members / 779 bits / 0 violations | **PASS 157 / 779 / 0** | SAME |
| `demux_off_gate` | PASS | **PASS** | SAME |
| `test_artifact` | 45 / 45, NON-VACUOUS | **45 / 45** | SAME |
| `ucrom_mif_check` | PASS | **PASS** | SAME |
| **`check_ucore_tables` (G0)** | PASS — **9,988 entries** byte-identical on both legs | **PASS, 9,988** | SAME |
| `chain_lfsr_gate` | PASS — `CHAIN_MAX` 7, depth [6], 0 overflows, sigs `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78` | **PASS, and ALL FOUR SIGNATURES BYTE-IDENTICAL**, with every `ce_clocks` and `g0` count identical too | SAME |
| `chainflat_relocation_check` | PASS — 9 arms, one copy each | **PASS 9 / 9** | SAME |
| `check_boot 220` (the RTL leg) | MATCH over 220 rows | **MATCH over 220 rows** | SAME ⚠ |
| `check_boot 400` (the RTL leg) | MATCH over 400 rows | **MATCH over 400 rows** | SAME ⚠ |
| `check_ab_sim --core ucore` | MATCH over 187 rows | **MATCH over 187 rows** | SAME |
| `ghost_launch_law score` | 200 / 200 = 100.0 % on all three populations | **200 / 200** | SAME |
| `core_portlist_lint` | PASS — the two cores' port lists agree in 2 configurations | **PASS — every named connection is a declared port, in 4 configurations** | ⚠ **RE-POINTED**, §D-12 / RET-2 |
| `test_quartus_gate` | 287 / 287 | **302 / 302** | ⚠ **+15, PRE-REGISTERED** — Q18 is the new E1's falsifier |
| E1 | `gen_ucore_qsf --check` PASS | **`qsf_lint --check` PASS** | ⚠ **RETIRED AND REPLACED**, §Z-2 |
| **`check_fuzz_bank`** | **PASS \| 621 \| stable 621 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0** | **REFUSES — `FsmCoreRetired`** | ⚠ **FORMALLY RETIRED**, RET-2, replaced by NOTHING |
| `check_boot --timed 220` / `400` | **already DEAD — `simbin.ModelRetired`** | **`ModelRetired`** | ⚠ a RET-1 casualty that RET-1 recorded as green — §D-5 |

**THE LIVE LADDER IS ZERO-DELTA.  Twenty-three legs SAME, ZERO moved, and the
only four that changed are the four this wave formally disposes of** — two
retirements (`check_fuzz_bank`, E1), one re-pointing (`core_portlist_lint`) and
one deliberate rise (`test_quartus_gate` 287 → 302, the new bar's falsifier).

⚠ **THE TWO `check_boot` ROWS CARRY A ⚠ FOR A REASON THAT IS NOT THIS WAVE'S.**
The BEFORE column for them was measured on `check_boot.py 220` / `400`, the RTL
legs — **not** on `check_boot.py --timed 220`, which is what `CLAUDE.md`'s quick
reference printed and which was DEAD on both sides.  Measuring the registered
spelling would have scored **two REDs on the BEFORE side**, and the first
instrument this wave pointed at that row found it.  §D-5.

⚠ **AND THE HLT SWEEPS' `--waits` TRAP IS STILL LIVE AND WAS OBEYED.**  Run
without `--waits 1/2/3` the three waited suites read `0 / 0 / 0` and look like a
catastrophic regression with every failure at `(1, 'seg')`
(`ghost8f_read_results_2026-08-09.md` §10.2).  Both columns above pass
`--waits 0/1/2/3`.

**Z-5: MET.**

---

## §Z-6 `hdl/rtl/ucore/` AND `hdl/nec_test.sdc` — UNTOUCHED

**MEASURED, and it is a two-line check anyone can repeat:**

```
$ git diff --stat fb9365c01c..HEAD -- hdl/rtl/ucore hdl/nec_test.sdc
$ git log --oneline fb9365c01c..HEAD -- hdl/rtl/ucore hdl/nec_test.sdc | wc -l
0
```

**EMPTY DIFF, ZERO COMMITS.**  Not one byte of `hdl/rtl/ucore/` or
`hdl/nec_test.sdc` was edited by this wave.  The requirement they carry is met
and in silicon at FLASH #23, and the removal never needed to touch either.

⚠ **THE ucore's OWN COMMENTS STILL CITE `hdl/rtl/core/` BY PATH** —
`v30_core.sv:5`, `v30u_biu.sv:100`, `v30u_ss_pkg.sv:7` — and they are **LEFT
STANDING DELIBERATELY, under Z-6 and on RET-1's precedent for
`gen_ucore_tables.py`**: they are the ucore's provenance, and deleting them
would delete the provenance rather than the dangle.  They now point into
history at `fb9365c01c`.

⚠ `hdl/tb/tb_v30_core.sv` and `hdl/rtl/system_large.sv` are NOT under Z-6's
protection and `tb_v30_core.sv` WAS edited — the `V30_FSM_PROBES` block, see
§D.  `system_large.sv` was not touched.

**Z-6: MET.**

---

## §Z-7 THE USER'S UNCOMMITTED WORK

**MEASURED.**  The 21 files the brief names were found `M`-unstaged and were
left `M`-unstaged.  **No `git stash`, no `git checkout .`, no `git reset
--hard`** was run in this wave (`git stash list` is empty); every `git add` in
every commit named explicit paths.

| | |
|---|---|
| the 18 non-receipt files | **18 of 18 still `" M "` unstaged, none staged, none edited** |
| `sw/testdata/receipts/*.jsonl` (3) | **still `" M "` unstaged, and NOT staged in any commit of this wave** |

⚠ **ONE THING THIS WAVE DID TO THEM, AND IT IS THE GATE'S OWN BEHAVIOUR, NOT AN
EDIT.**  `sw/testdata/receipts/quartus_bitstream.jsonl` and
`quartus_distribution.jsonl` are the gate's APPEND-ONLY receipt history, and the
two Z-4 builds appended to them exactly as every G6 build does.  That is not a
modification of the user's work — it is the instrument recording itself — and
the lines are **left UNSTAGED** so the owner of those edits decides.  The wave's
own copies of both receipts are committed separately at
`sw/testdata/wave21/z4{a,b}_quartus_gate.json`, so nothing in the results
document depends on those files being committed.

**Z-7: MET.**

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

**SEVENTEEN CLAIMS WERE CHECKED AGAINST THE ARTIFACT AND FOUND FALSE.  ALL
SEVENTEEN ARE FIXED IN THIS WAVE.**  Under the user ruling, documentation is
hearsay until proved in the artifact, and where a doc and the code disagreed the
code won.

| # | where | what it asserted | what the artifact says | disposition |
|---|---|---|---|---|
| **D-1** | `hdl/files_ucore.qip:10-11` | the file list is *"Selected by the `V30_CORE` environment variable, read in nec_test.qsf"*, with `V30_CORE=ucore quartus_sh --flow compile nec_test` as the build command | **`V30_CORE` occurred EXACTLY ONCE IN THE WHOLE TREE — in that comment.**  Nothing read it and nothing could: the `.qsf` is read by a restricted settings parser with no `if` (Error 125048), which is why two revisions existed at all.  **Following the documented command built the FSM core and reported success** — accepted-and-ignored, class E-6, inside a build instruction | **FIXED** — the erratum is now that file's header |
| **D-2** | `sw/check_core.py:180` | `BIN` and `RTL` have *"NO consumers anywhere in the tree (checked 2026-08-04)"* | **SEVEN.**  `emit_suite.py:2258`, `f4a_boundary_battery.py:73`, `char_divergence.py:26`, `validate_strio_sim.py:158`, `class5_hext.py:58` take `CC.BIN`; `pi1a_trace.py:29`, `repro_segleak.py:33` take `CC.OBJ`.  ⚠ **`emit_suite` calls `CC.build()` — which builds the DEFAULT ucore into `obj_dir_ucore` — and then executed `CC.BIN`, the ARCHIVED core's binary.**  The trap the comment warned about was already sprung | **FIXED** — re-pointed at the ucore, and the engine change DECLARED in RET-2 |
| **D-3** | `sw/ss_lint.py:28` | *"`--core fsm` (default) is the standing gate"* | the default has been `ucore` since 2026-08-04 (`:175`) | **FIXED** |
| **D-4** | this wave's brief; `staleness_audit_2026-09-19.md` §2 | `gen_ucore_qsf --check` *"DERIVES THE ucore REVISION FROM THE FSM ONE"*, and deleting `hdl/rtl/core/` *"breaks the A/B derivation"* — **named as THE BLOCKER** | `derive()` is text substitution on ONE settings file.  It never opens `files.qip`, never reads `hdl/rtl/core/`, and **ran GREEN with the whole FSM core deleted** (§Z-4a) | **FIXED** — the audit records it |
| **D-5** | `CLAUDE.md` quick reference; `invalidation_ledger.md` **RET-1**'s own GATE STATUS table | *"Timed, whole-program: `sw/check_boot.py --timed 220`"*, and RET-1: the RTL legs *"had been killed by an unconditional `simbin.ensure()` and this wave made it conditional"*, status **"MATCH / MATCH — UNMOVED"** | the condition WAVE 20 landed is `if timed:` — **and `--timed` IS THE MODEL LEG** (`run_timed()` runs `$SIM timed-boot`; `run_sim()` is the Verilator TB).  It protected the leg it meant to retire and retired the leg it meant to protect.  **Measured: `--timed 220`/`400` raise `ModelRetired`; `check_boot.py 220`/`400` MATCH** | **FIXED in the code and in both documents** |
| **D-6** | `CLAUDE.md`, the `fuzz-v2-on-relanding` banner (WAVE 20 item W-1) | *"FOUR RATCHETS … CANNOT RUN HERE AT ALL — `timed_scenario`, `timed_ins_replay`, `timed_wvec_gate`, `timed_enter_replay`.  They die in `image_of(seed)` on `gen_seq._v1_anchor_stop`"* | WAVE 20 measured it false for two of the four.  **Measured again 2026-09-20: all four now raise `simbin.ModelRetired` FIRST** — they are RET-1 casualties before they are anything else | **FIXED** |
| **D-7** | `CLAUDE.md`, the `ss_lint` row (WAVE 20 item W-2) | **`SS_VERSION` 0x8D / `SS_COUNT` 226 / `SS_TAG` 0x8DE2 / 214 flops**, in bold, labelled **"CURRENT"** | **0x8F / 232 / 0x8FE8 / 229 flops / 4 whitelist / 0 UNMAPPED.**  Five map bumps stale, while `standing_gates.md` §B was already right | **FIXED** |
| **D-8** | `CLAUDE.md`, the WAVE 7 banner (WAVE 20 item W-3) | `ss_lint` **"232 / 228 flops"** | **229** — ARM-B's one declared flop.  One digit, in the banner a reader trusts most | **FIXED** |
| **D-9** | `CLAUDE.md` | *"the FSM core … `--core fsm` still builds and runs"*; the *"ARCHIVED — on demand"* pointer; and a paragraph instructing the reader to **quote 168,400 / 169,000 and 16 / 283** | the core is gone and `--core fsm` refuses.  **There are THREE comparators in this repo's history and they disagree**; measured on the day of the removal the same commands give **169,000 / 169,000** and **226 / 283** | **FIXED** — all three instruments now named |
| **D-10** | `fsm_core_archive_2026-08-04.md` §5, §6, §6a/§6b | the corrected-comparator figures, a re-activation procedure, and *"`gen_ucore_qsf.py --check` still gates that the two bitstreams differ by the core and nothing else"* | none of it describes this tree | **FIXED** — the document is banner-marked HISTORY, with §2 and §3 explicitly **not** retracted |
| **D-11** | `standing_gates.md` §C | ten gates presented as ON-DEMAND runnable | all ten are retired; four of them could not run before the removal either | **FIXED** — §C is now an empty section that says so |
| **D-12** | `sw/core_portlist_lint.py`'s `_strip_comments` | (implicitly) that it strips comments | ⚠ **IT RAN THE BLOCK-COMMENT REGEX OVER THE RAW TEXT.**  `tb_v30_core.sv:40` is a LINE comment containing `hdl/rtl/core/*.sv`, so it matched from there to line 254's `*/` and **deleted 200 lines including the `v30_core dut (` instantiation**.  Never showed because WAVE 18 only ever fed it the two `v30_core.sv` files.  **It presented as exit 2 CANNOT MEASURE — the only reason it was not a silent wrong answer** | **FIXED** — replaced by a scanner |
| **D-13** | `sw/receipt_diff.py:5-13` | *"`gen_ucore_qsf.py --check` already proves one A/B claim"*, and lists **"FSM vs ucore bitstream"** as a legitimate pair | no two-core comparison can be made on this tree | **FIXED** — the row is retired by name and kept as history so pre-2026-09-19 receipts stay readable |
| **D-14** | `docs/notes/artifact_receipt_layer.md:111` | the receipt schema's specimen environment variable is `{"V30_CORE": "ucore"}` | see D-1 — it perpetuated the fiction in the schema document | **FIXED** — the specimen is now `X1_AD_RETENTION`, which is real |

| **D-15** | `CLAUDE.md:64` — **the RTL-promotion rule, i.e. THE DEFINITION OF THE PROMOTION GATE** | *"G6: `gen_ucore_qsf --check`, one clean CONTROL build, Fmax ≥ 32 MHz, …"* | that tool is RETIRED BY THIS WAVE.  ⚠ **AND THIS WAVE MISSED IT FOR ITS WHOLE LENGTH.**  §Z-1's token grep DID list `CLAUDE.md` under the `gen_ucore_qsf` token; only the *Gate quick reference* copies were dispositioned, and the one sentence that tells a future agent **what G6 IS** was left naming a tool that exits 2.  **A token appearing in an enumeration is not a token that was dispositioned** — the enumeration found it and the fix pass did not consume it | **FIXED** — E1 is now `qsf_lint --check` with the A/B retirement stated inline |
| **D-16** | `CLAUDE.md`, the ratchet list's **LEAD** bullet | *"**ROM/PLA**: `python3 sw/simbin.py --disasm` (disasm byte-exact, 1,285 rows …)"*, with `make -C sim test` beside it | both are RET-1 casualties and `--disasm` raises `ModelRetired`.  WAVE 20's banner lists them as retired 500 lines above; the bullet itself carried no marker, and it is the FIRST ratchet a reader meets | **FIXED** — marked retired with its last figure, G0's frozen snapshot named as the surviving independent reference, and the row's live half (`pla3_check`, 21 checks) called out |
| **D-17** | `CLAUDE.md`, the ce/ce_half contract banner | *"⚠ `check_core --core fsm` therefore runs with NO enable enforcement — the ARCHIVED core was not touched"* | moot: that core is gone, so **every core this tree can build inherits the assert** | **FIXED** |

**AND FIVE MORE, SMALLER, FIXED IN PASSING**: `sw/check_ab_sim.py:59`
(*"must stay a subset of hdl/files.qip's"*), `standing_gates.md` §D (it repeats
D-2's "no consumers" claim), `sw/quartus_gate.py`'s SIGNALTAP comment (it
justified the placement BY THE A/B), `sw/timed_fuzz.py`'s `tb_bin` docstring
(*"the FSM core is `obj_dir`"*), and the five tools whose comments said
`check_seq.CORE` **is** pinned to the archived core (`fuzz_campaign`,
`wrfuzz_smoke`, `emit_suite`, `fz2_undoc_probe`, and `check_seq` itself); plus
WAVE 20's own two-part errata bullet in `CLAUDE.md`, whose *"this file is not
[correct]"* is **now discharged** and says so; the `ss_lint` history block's
*"the `--core fsm` leg is unchanged"*; and the receipt-layer bullet's
`python3 sw/simbin.py --build`, which is a record of a recipe rather than one.

### ⚠ THE METHOD FINDING THIS SECTION OWES ITSELF

**D-15 WAS FOUND AFTER THE WAVE BELIEVED ITSELF FINISHED**, by re-reading
`CLAUDE.md` end to end rather than by any instrument.  §Z-1's grep had already
named the file; what failed was the step between *enumerated* and
*dispositioned*, and nothing in this wave measured that step.  **The honest
statement is that the doc-discrepancy count is a FLOOR, not a total** — the
enumeration is mechanical and complete, the disposition of each hit was manual
and is not gated.  A future wave that wants the total should gate it: a check
that no live-recipe form (`python3 sw/<retired tool>`) appears in `CLAUDE.md`
or `standing_gates.md` outside a marked-history block.  **BOOKED, not built** —
building it in the sitting that needed it would make its first green
unfalsifiable.

### ⚠ THE BACKLOG — booked with evidence, NOT fixed here

| item | evidence | why not here |
|---|---|---|
| **~40 `--core` choice lists still offer `sim`** | the RET-1 model is gone; `--core sim` raises `ModelRetired` by name, which is RET-1's own chosen mechanism and its falsifier #1 | **The `fsm` half IS removed here** (18 files).  Removing the `sim` half means changing ~15 measurement tools' DEFAULTS from `sim` to `ucore`, which silently changes WHAT A BARE INVOCATION MEASURES in a wave that cannot re-measure them.  The one `sim` coupling that was a LIVE STANDING GATE — `check_boot --timed` — **is fixed here** (D-5) |
| `sw/run_chainflat_synth.py`, `sw/frontend_proto.py` headers | both say *"`hdl/nec_test.qsf`, `hdl/nec_test_ucore.qsf` and `hdl/nec_test.sdc` are never opened"* | the SENTENCE IS STILL TRUE (a file that does not exist is certainly never opened) and both are closed-wave drivers.  One-word items |
| `sw/t30_sweep.sh`'s body below its refusal | still carries the *"168,400/169,000"* rule and the fourteen legs | unreachable — the refusal `exec`s before it.  Kept as the record of what the sweep was |
| `sw/case31_all_exts.txt` was never committed | WAVE 20 §4 erratum 2; breaks four tools including a standing ratchet | not this wave's subject; unchanged, and `timed_ins_replay` now hits `ModelRetired` first anyway |
| the v1-anchor casualty family | `staleness_audit_2026-09-19.md` §4 | **a board decision** — re-basing needs a RE-CAPTURE, and a green produced without one would be a fabricated green |
| `check_fuzz_bank` re-pointed at the ucore | RET-2, and the `ERR-1`/`cfb_rederive` pattern | the banked `replay_verdict` column was computed on the FSM TB; re-pointing without re-deriving it measures the engine swap and nothing else |

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
