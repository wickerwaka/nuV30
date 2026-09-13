# WAVE 12 — **REMOVE `build_id.v` ENTIRELY.**  PRE-REGISTRATION, COMMITTED BEFORE THE FIRST EDIT.

**A LANDING.  OFFLINE ONLY — NO BOARD, NO FLASH.**  ⚠ **THIS CHANGE MOVES THE
BITSTREAM.**  It deletes a ~26-character element from `CONF_STR`, and WAVE 11
measured exactly what that is worth: **1.647 ns / 1.34 MHz at one seed.**  Every
figure taken after this wave is comparable to every other one in a way no figure
before it was, and no figure before it is comparable to one after it.

---

## §0 THE USER'S INSTRUCTION, VERBATIM (2026-09-12)

> **"Change the project so build_id.v isn't generated and isn't used."**

That is the whole scope.  It is not extended into other timing work.

## §1 WHY — WAVE 11's MEASUREMENT

`docs/notes/pcc0_settle_results_2026-09-12.md`.  `hdl/build_id.v` is a `%y%m%d`
date stamp written by the MiSTer `PRE_FLOW` script, `.gitignore`d, untracked, a
**declared exclusion** from `quartus_gate`'s `input_manifest`, and consumed at
`hdl/nec_test.sv:229` as the last element of `CONF_STR`.  Same tree, same seed,
`--clean-db` in all three arms, **two ASCII characters the only difference**:

| stamp | `$v30u_ce` | `T_min` | MHz |
|---|---:|---:|---:|
| `"260909"` | 2,154 | 34.220 | 29.22 |
| `"260910"` (a null, never used by any wave) | 1,936 | 34.773 | 28.76 |
| `"260912"` | 1,918 | 35.867 | 27.88 |

The core leaves Analysis & Synthesis with **1,181 ce-gated registers under every
stamp**.  The stamp moves **91 logic cells of OSD byte-mux, entirely outside the
core**; the fitter then places a different design and timing-driven physical
synthesis duplicates a different number of registers on the microcode ROM's read
loop.  **Three stamps at one seed span 1.647 ns; WAVE 7's five seeds at one stamp
spanned 0.603 ns.  The stamp is the larger dimension and it was unlabelled**, and
the campaign is now deciding at 0.34–0.83 MHz margins.

## §2 THE CONSUMER MAP, AS VERIFIED IN THIS TREE BEFORE ANY EDIT

| file | what it does |
|---|---|
| `hdl/nec_test.sv:200` | `` `include "build_id.v" `` |
| `hdl/nec_test.sv:229` | `` "V,v",`BUILD_DATE `` — the last `CONF_STR` element |
| `hdl/sys/build_id.tcl` | `generateBuildID_Verilog` (the stamp) **and `generateCDF` (`jtag.cdf`) — two unrelated things in one vendored script** |
| `hdl/sys/sys.tcl:211` | `PRE_FLOW_SCRIPT_FILE "quartus_sh:sys/build_id.tcl"` — the only hook.  **Neither `.qsf` carries one** |
| `hdl/.gitignore:32` | `build_id.v` |
| `sw/run_adcone_anatomy.sh:29`, `sw/run_adcone_census.sh:26`, `sw/run_phase_split_anatomy.sh:54`, `sw/run_intcone_anatomy.sh:32` | `quartus_sh -t sys/build_id.tcl preflow …` — run **only** because a direct `quartus_map` does not honour `PRE_FLOW` and A&S would die at `Error (10054)` |
| `sw/run_biu_roundtrip.py:109-127` | copies `hdl/build_id.v` from the main tree into a scratch worktree, for the same reason |
| `sw/quartus_gate.py` | `preflow_command()`, `build_id_state()`, the prepended `preflow` stage, and the `build_id` receipt field |
| `sw/test_quartus_gate.py` | Q1 and Q9 assert that stage |

⚠ `hdl/quartus_gate_*.log` and `sw/testdata/**` hits are **RECORDS of builds
that were taken under a stamp.  They are true, they are left alone, and this
wave does not edit one of them.**

## §3 ⚠ THE QUESTION ANSWERED BEFORE EDITING — **IS `CONF_STR`'s `V` ELEMENT REQUIRED?**

**IT IS OPTIONAL.  NOTHING IN THE RTL PARSES `CONF_STR` AT ALL.**  Evidence,
from the vendored framework itself:

* `hdl/sys/hps_io.sv:30` — `CONF_STR` is a module **parameter**, and
  `STRLEN = $size(CONF_STR)>>3` is derived from it.  There is no fixed layout.
* `hdl/sys/hps_io.sv:243` (and `confstr_rom` at `:1027` for the BRAM variant) —
  the string is served to the HPS **byte by byte, positionally**, indexed by
  `byte_cnt`.  **No element is located, named, counted or decoded in hardware.**
* `hdl/sys/hps_io.sv:393` — `'h14: if(byte_cnt <= STRLEN) io_dout[7:0] <= conf_byte;`
  — past the end the HPS reads **0**, which is the terminator.  A shorter string
  terminates one byte earlier and by the same mechanism.
* `hps_io` is the **only** consumer of `CONF_STR` in `hdl/sys/`.

The `V` element is a **MiSTer *Main* (ARM userland) convention** that supplies the
version text shown at the bottom of the OSD menu.  Its absence costs that text
and nothing else; no gate, no measurement and no capture in this repository goes
through the OSD.  **So it is deleted, which is the user's instruction exactly.**
Had it been structurally required this wave would have STOPPED and reported — a
fixed literal is a different thing from *"isn't used"* and would have been the
user's call.

## §4 THE CHANGE, AS IT WILL BE MADE

1. `hdl/nec_test.sv` — the `` `include `` and the `"V,v",`BUILD_DATE ` element go;
   `"v,0;"` becomes the last element and loses its trailing comma.
2. `hdl/sys/build_id.tcl` → **`hdl/sys/gen_cdf.tcl`** by `git mv`, with
   `generateBuildID_Verilog` **deleted** and **`generateCDF` kept byte-for-byte**.
   ⚠ **`generateCDF` is not this wave's business**: it writes `jtag.cdf`, which
   `sys.tcl:213` names as `CDF_FILE`.  Removing it would be a SECOND change to
   the build, outside the instruction.  The rename is what takes the token
   `build_id` off the build path; the CDF behaviour is unchanged.
3. `hdl/sys/sys.tcl:211` — the hook points at `sys/gen_cdf.tcl`.
4. `hdl/.gitignore:32` — the `build_id.v` entry is **REMOVED**, deliberately: an
   ignored file that came back would be invisible to `git status`, and the whole
   lesson of PC-C0 is that an unlabelled build input hides.
5. The four shell drivers lose their explicit `preflow` line, and
   `sw/run_biu_roundtrip.py` loses the copy block — **their only purpose was the
   stamp**.
6. `sw/quartus_gate.py` — `preflow_command()`, `build_id_state()` and the
   prepended stage are deleted.  ⚠ **THIS RESTORES THE RECORDED FOUR-STAGE
   `--retention` RECIPE** (`map`, `fit`, `asm`, `sta`); the fifth stage existed
   only to write `build_id.v`.
7. `hdl/build_id.v` is deleted from the working tree.

## §5 THE BARS, REGISTERED NOW.  VERBATIM.

* **M-1  IT IS NOT GENERATED.**  A full clean compile from a tree with no
  `hdl/build_id.v` produces none.  **Demonstrated, not asserted.**
* **M-2  IT IS NOT USED.**  `BUILD_DATE` and `build_id` appear in no RTL, no
  `.qsf`, no `.tcl` on any build path, and no driver.  (Historical
  `hdl/quartus_gate_*.log` files and `sw/testdata/` artifacts are RECORDS —
  they are left alone and said so.)
* **M-3  THE FALSIFIER, AND IT IS THE POINT OF THE WAVE.**  Reproduce WAVE 11's
  experiment on the changed tree: take the two conditions that previously gave
  **34.220** and **35.867** at the same seed and show they now give **the SAME
  answer** — same `$v30u_ce`, same `T_min`, and ideally a byte-identical `.rbf`.
  **The nondeterminism must be measurably GONE, not argued gone.**  If a residue
  remains, report its size.
* **M-4  G6 PASSES** on BOTH configurations, `--seeds 5`, with the tree's current
  SDC (the CE multicycle is present; this wave does not touch it).  Report
  `worst-of-5` against WAVE 7's 41.06 — **this is the first stamp-free baseline
  the project has and it is recorded as such.**
* **M-5  THE FULL LADDER IS ZERO-DELTA.**  `nec_test.sv` is RTL.  The BEFORE side
  is taken first: `r7_lint` · `ss_lint` · `check_core --opcodes all --cases 0`
  169,000 · `8F.0` 500 · HLT sweeps ⚠ WITH `--waits 0/1/2/3` 279/283 ·
  `ulockstep` 17,350 · `check_boot` 220 and 400 · `check_ab_sim` 187 ·
  `sm3_s16_score` 1,320/1,371 · `demux_off_gate` · `test_artifact` 45/45 ·
  `ucrom_mif_check` · `chain_lfsr_gate` with its four signatures BYTE-IDENTICAL.
  ⚠ Each is verified against `standing_gates.md` first; two rows there are known
  stale — **measure, report the disagreement, never treat a stale row as a
  failure.**
* **M-6  THE GATE THAT KEEPS IT REMOVED.**  `quartus_gate.py` must RECORD the
  absence and **REFUSE** (non-zero exit, reason named) if `build_id.v` reappears
  or if `BUILD_DATE` re-enters the RTL — because `hdl/sys/` is **vendored** and a
  future framework update would silently bring it back.  `sw/test_quartus_gate.py`
  is extended accordingly and **the new clause is demonstrated FIRING**
  (non-vacuous).  **This is the gate whose absence let PC-C0 hide: two waves were
  compared across it and nothing objected.**
* **M-7  THE REVERT CONDITION.**  If M-4 fails, or any leg of M-5 moves, the
  landing does not happen: revert, report, keep both documents.  **No bar is
  softened.**

### 5.1 HOW M-3 IS RUN, REGISTERED BEFORE IT IS RUN

WAVE 11's own pipeline, unchanged: `sw/run_biu_roundtrip.py --clean-db
--control-seeds 1 --retention-seeds ''`, the no-exception SDC patch from the one
shared anchor, single-writer guard, `.qsf` restored after every stage.  **Two
arms, and the ONLY difference between them is the file WAVE 11 proved was
worth 1.647 ns:**

| arm | `hdl/build_id.v` on disk | |
|---|---|---|
| **W12-A** | present, `` `define BUILD_DATE "260909" `` (sha256 `11e55ef99ab705c5…`, the value a COMMITTED RECEIPT records) | WAVE 11's E-1 condition |
| **W12-B** | present, `` `define BUILD_DATE "260912" `` (sha256 `5b4d6ad10ee2a48f…`) | WAVE 11's PC-11 condition |

**REGISTERED PREDICTION**: the two arms return the **SAME** `$v30u_ce`, the
**SAME** `T_min` to the thousandth, and **byte-identical** `truefmax` artifacts.
**WHAT FALSIFIES IT**: any difference at all.  **The residue, if any, is reported
as a number, not as a hedge.**
⚠ The file is *created by hand* in each arm because nothing generates it any
more; that it is present and inert is the whole point.  Its bytes and `sha256`
are printed for each arm.  It is removed at the end.
⚠ **A third arm is NOT run.**  Two arms is what WAVE 11's demonstration used and
what the prediction is written against; adding arms after seeing a result is
fitting.

### 5.2 WHAT M-4 IS AND IS NOT

`python3 sw/quartus_gate.py --seeds 5` and `--retention --seeds 5`, tree's own
SDC, one map and five fits each.  The quotable figure is
`worst-of-5@seeds{1,2,3,4,5}`.  ⚠ **It is scored against the G6 PASS bars
(Fmax ≥ 32 MHz, worst setup > 0, setup AND hold TNS 0.000), not against 41.06.**
WAVE 7's 41.06 was drawn at stamp **260909** and this tree has no stamp, so the
comparison is **REPORTED AND NOT SCORED** — `standing_gates.md` §A governs, and
one green build is not closure.

---

## §6 DISCIPLINE

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.**  ⚠ **A FABRIC CONFIRMATION HAS BEEN
  OWED SINCE WAVE 7 AND IS STILL OWED**; this wave records it and **it is not
  this wave's to discharge.**  ⚠ **THIS CHANGE MOVES THE BITSTREAM**: a fabric
  figure taken on FLASH #21 or earlier may not be quoted against this tree, and
  now for a second, independent reason.
* No Codex.  No nested subagents.
* Single-writer guard (`pgrep -x`, EXACT binary name) before every Quartus stage.
* `hdl/nec_test_ucore.qsf` `git checkout --`'d between Quartus runs.
* **`git add` BY EXPLICIT PATH ONLY** — ~21 pre-existing modified files in the
  working tree are **not this wave's** and not one of them is touched.
* `~/.cache/ucsimt-tmp/`, never `/tmp`.
* **CONTENT COMPARED, NOT A DIGEST COMPUTED HERE**: artifacts are `diff`ed whole.
* ⚠ Verilator `$stop`s on the first `$error`; each clause gets its own probe.
* **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL.**  Nine instruments in this
  campaign have produced confident, wrong, vacuous results.
* Truthful commit messages; a gate that is not met is never asserted.
* **Record what was measured, not what was expected.**
