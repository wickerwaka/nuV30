# WAVE 23 — RESULTS.  **THERE IS NO WEDGE AND NO MISSING MECHANISM: THE ucore ALREADY REPRODUCES SILICON'S STALE-EA WITNESSES, AND `0 / 128` IS A STIMULUS DEFECT OF THE TESTBENCH.  NOT ONE `hdl/` BYTE MOVED — AND THE WAVE FOUND A DIFFERENT, REAL SILICON DIVERGENCE ON THE WAY.**

Pre-registration `3818953ad2`
(`docs/notes/lea_mod3_prereg_2026-09-20.md`), committed **before the first
`hdl/` edit** — of which there were none.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

---

## §1  THE HEADLINE

| | |
|---|---|
| **the mechanism, in one sentence** | *At `mod == 3` the `8D` decode issues no EA calculation, so the row-1 `SIGMA -> R` transfer writes the register the ModR/M `reg` field names with whatever the address adder's two rails still hold — the retained EA lane and the ordinary scratch lane — and the instruction falls through.* |
| **does the ucore have a last-EA latch?** | **YES.**  `ea_residue` (`v30u_eu.sv:251`), with `ea_pair_rhs` / `ea_pair_valid` beside it, save-state addresses `0x177` / `0x178` / `0x179`, landed in the wrfuzz campaign and versioned in `v30u_ss_pkg.sv` at `SS_VERSION` 0x89 → 0x8A |
| **does the ucore wedge at `S_HALT`?** | **NO.**  Cycle rows **128 / 128** on all 128 goldens.  `v30u_eu.sv:832-845` says in as many words that `opr_starved` fires on `62`/`C4`/`C5`/`FE`/`FF /3`/`/5` at `mod == 3` **and not on `8D`** |
| **`mod3_illegal`, measured** | **`0 / 128 full (cycles 128, arch 0)` — UNCHANGED.  X-2 IS A REGISTERED MISS** |
| **RTL changed** | **NOTHING.**  107 synthesis inputs, sha256 identical before and after (`sw/testdata/wave23/synth-manifest-{before,after}.txt`) |
| **what fabric owes** | **NOTHING NEW.  FLASH #23 STILL COVERS THIS TREE.** |
| **what the wave found instead** | ⚠ **A REAL, SILICON-ANCHORED DIVERGENCE the briefing did not ask about**: on a **ModR/M** memory predecessor the ucore's retained EA lane does not hold what silicon's holds.  **BOOKED WITH ITS FALSIFIER, NOT FIXED** — §4 |

---

## §2  THE PROOF THAT THE ucore IS RIGHT

`sw/tb_bootrun.py`'s `+bootimg` mode drives the composed image **from RESET
with no backdoor injection at all**, so the image's own loader runs inside the
core exactly as it ran inside the chip.  TB receipt `5332bc26a38de4b2…`.

**THE TWO SILICON WITNESSES, REPRODUCED EXACTLY:**

| stimulus, body at `PS = 0x0000` | SILICON (`metadata.json::stale_ea_probe`) | **ucore** | |
|---|---:|---:|---|
| `MOV [1234h],AW ; LEA SI,DI(mod3)` | `0x1234` (`match: true`) | **`0x1234`** | **MATCH** |
| `MOV [BEEFh],AW ; LEA SI,DI(mod3)` | `0xBEEF` (`match: true`) | **`0xBEEF`** | **MATCH** |

**AND THE `0x0500` THE 128 GOLDENS EXPECT IS THE SAME MECHANISM.**
`sw/testimage.py::load_routine` — **byte-identical at the capture commit
`74942059cf` (2026-07-18) and today** — ends `BR PS:PC`.  With nothing before
the LEA:

| `PS` | `PC` | ucore writes | `PC + PS` |
|---:|---:|---:|---:|
| `0x0000` | `0x8100` | **`0x8100`** | `0x8100` |
| `0x0800` | `0x0100` | **`0x0900`** | `0x0900` |
| `0x0810` | `0x0000` | **`0x0810`** | `0x0810` |

and the sum is discriminated from a single latch: `MOV [1234h],AW` at
`PS = 0x0800` writes **`0x1A34` = `0x1234 + 0x0800`**, not `0x1234`.  Every one
of the 128 goldens sits at `PS = 0x0000`, `PC = 0x0500`, so the value silicon
wrote is `0x0500 + 0x0000` — **and the ucore writes it.**

---

## §3  WHY THE SCORER READS `0 / 128` ANYWAY

`hdl/tb/tb_v30_core.sv:1120` injects **the fourteen architectural registers**
and nothing else:

```
for (i = 0; i < 14; i++) bkd_regs[i*16 +: 16] = rv[i];
```

`ea_residue` therefore enters every golden case at its reset value `16'd0`,
where the chip entered carrying `0x0500`.  **The golden carries no field for
it.**  WAVE 22 wrote this first (`suite_scorer_results_2026-09-19.md` §5:
*"a property of what the chip did before the window"*); **it is now proved,
and the mechanism is named.**

> **A GOLDEN WHOSE OUTCOME DEPENDS ON PRE-WINDOW MICROARCHITECTURAL STATE IS
> UNSCOREABLE BY AN INJECTED ENGINE BY CONSTRUCTION.**  No RTL changes that.

**AND THE OBVIOUS "FIX" IS A STOP, NOT A FIX** — pre-registered as **S-4**.
Injecting `ea_residue = PC` through the backdoor would read 128/128 tomorrow.
It is refused because (a) it chooses an initial condition **after** seeing the
expected answer, (b) the goldens carry no such field, so the value is invented
stimulus, and (c) it is right only because these 128 all sit at `PS = 0x0000` —
the complete rule needs the scratch rail too, and **a rule that is right for
one population's constant is a fit.**  *Falsifier, if a future wave takes it:
compose a directed capture at `PS != 0` and show the injected pair reproduces
it.*

---

## §4  ⚠⚠ WHAT THE WAVE FOUND THAT IT WAS NOT LOOKING FOR — **A REAL SILICON DIVERGENCE, BOOKED AND NOT FIXED**

The suite's `stale_ea_probe` has **four** rows.  Two are `match: true` and are
§2's.  The other two are marked `match: false` — **and `match` records only
that the 2026-07-27 rig's hypothesis (*"the register receives the EA"*) failed
on them.  `si_loaded` is still a silicon measurement, and it is explained
exactly.**

| row (encoding INFERRED from the prose `pre`) | silicon `si_loaded` | decomposition | **ucore** | decomposition |
|---|---:|---|---:|---|
| `MOV [3010h],AH` → `88 26 10 30` | **`0x4121`** | `0x3010` (**the EA**) `+ 0x1111` (`AW`) | `0x9211` | `0x8100` (**the loader's PC**) `+ 0x1111` |
| `MOV CW,[4455h]` → `8B 0E 55 44` | **`0xD4E5`** | `0x4455` (**the EA**) `+ 0x9090` (the loaded word; the v1 composer filled the image with `0x90`) | `0x1190` | `0x8100` `+ 0x9090` (mod 2^16) |

**THE SCRATCH TERM AGREES BETWEEN THE TWO ENGINES ON BOTH ROWS — `0x1111` and
`0x9090`, identified independently of either engine — SO THE ATTRIBUTION IS
CLEAN: THE ONLY THING THAT DIFFERS IS THE RETAINED EA LANE.**  Silicon's holds
the effective address; the ucore's holds what the loader's branch left there,
i.e. it was never updated by the ModR/M access at all.

**Characterised further** (`89 xx` = `MOV [modrm],AW`, `PS = 0`, body at
`0x8100`, LEA result):

| ModR/M | `rm` | EA | ucore LEA result |
|---|---|---:|---:|
| `00` | `BW+IX` | `0xBBBB` | `0x8888` |
| `01` | `BW+IY` | `0xCCCC` | `0x9999` |
| `02` | `BP+IX` | `0xDDDD` | `0x8888` |
| `03` | `BP+IY` | `0xEEEE` | `0x9999` |
| `04` | `IX` | `0x7777` | `0x9211` |
| `05` | `IY` | `0x8888` | `0x9211` |
| `06 34 12` | direct | `0x1234` | `0x9211` |
| `06 78 56` | direct | `0x5678` | **`0x9211` — EA-INDEPENDENT** |
| `07` | `BW` | `0x4444` | `0x9211` |

⚠ **AND `v30u_eu.sv:247-250`'s OWN COMMENT DOES NOT DESCRIBE THIS**: it says
*"a ModR/M EA calculation instead leaves the **pre-displacement base** here"*,
and `v30u_eu_arm_ea_calc.svh:35` assigns `ea_residue_n = ea` **before**
`ea = ea + ld_disp_n`.  For `mod=00 rm=110` the pre-displacement base is
`16'd0`, so the comment predicts `0x0000 + 0x1111 = 0x1111`.  **The tree
produces `0x9211`.**  Something after `S_EA_CALC` restores the earlier value,
and this wave did not find what.

### §4.1  WHY IT IS **BOOKED AND NOT FIXED** — THREE REASONS, EACH SUFFICIENT

1. **THE EVIDENCE IS TWO ROWS, AND THEIR BYTES ARE INFERRED FROM PROSE.**
   `metadata.json` records `pre` as English (*"MOV[3010h],AH"*), not as bytes.
   §4's encodings are the obvious ones and are stated so they can be checked —
   **but an `hdl/rtl/ucore/` landing on an inferred encoding is exactly the
   fitting this repo forbids.**
2. **CLOSING IT NEEDS A DIRECTED SOCKET CAPTURE, AND `X-4` FORBIDS BOARD
   CONTACT IN THIS WAVE.**  The right instrument is `sw/char_mod3.py`'s
   stale-EA probe re-run over the ModR/M predecessor family with the bytes
   RECORDED.  **It cannot be closed here by construction.**
3. **IT IS A DIFFERENT MECHANISM FROM THE ONE THE WAVE WAS AUTHORISED FOR**,
   and it **does not move `mod3_illegal` by one case**: those 128 have no
   preceding instruction at all, so their residue is the loader's `PC` and the
   injected TB zeroes it either way.

> **FALSIFIER, REGISTERED**: a directed socket capture of `8D` at `mod == 3`
> preceded by each of the eight `mod=00` ModR/M forms, with the preceding
> instruction's BYTES recorded, in which the register does **not** receive
> `EA + scratch`.  Until that capture exists, the retained-EA-lane law is a
> two-point measurement and is quoted as one.

---

## §5  THE NEW GATE — `python3 sw/lea_mod3_gate.py`, AND **ITS NON-VACUITY IS MEASURED, NOT CLAIMED**

```
  L1  SILICON       2/2   (the `match: true` rows of mod3_illegal/metadata.json)
  L4  KNOWN-RED     2 of 2 ModR/M-predecessor silicon row(s) DIVERGE
  L2  ROUTING       64/64  (8 reg fields x 8 rm, confinement checked)
  L3  NON-VACUITY   3/3
  71 whole-program replays, from RESET, no backdoor injection      PASS, ~7 s
```

L1's expected values are **read out of the artifact**, never hard-coded.  L2
sweeps all 8 ModR/M `reg` fields x all 8 `rm` values and requires that the
named register takes the value and **no other GPR moves**.

**FIVE RTL PERTURBATIONS WERE BUILT AND RUN AGAINST IT**, each in an isolated
`git worktree` at `3818953ad2`, each with the unperturbed build as its own
control (control: **PASS**).  **THAT EACH PERTURBATION REACHED THE COMPILER IS
MEASURED, NOT ASSUMED**: the worktree's `verilator_binary.jsonl` gained **six
receipts, one per build** (control + five perturbations), and the first three
were inspected and carry **three DISTINCT binary sha256s**
(`26336242c79f12c9…`, `11fa2ef59866a67f…`, `d2003c98cecd839a…`) — so the
`.svh` is a declared input and a perturbation of it forces a rebuild.  ⚠ The
remaining three receipts were counted, **not hash-inspected**, and that is
stated rather than glossed:

| # | perturbation of `v30u_eu_arm_bind.svh` | gate |
|---|---|---|
| **P5** | `r_idx_n = rmreg` → `rmreg ^ 3'd1` | ⭐ **CAUGHT — L1 0/2, L2 0/64, L3 0/3** |
| P1 | delete the mod3 arm's `tmpa_n = ea_residue_n;` | **NOT CAUGHT** |
| P2 | `tmpa_n = ea_pair_rhs_n;` (wrong rail) | **NOT CAUGHT** |
| P4 | `modrm_reg_n = rmreg ^ 3'd1` | **NOT CAUGHT** |
| P6 | delete `if (ea_pair_valid_n) tmpb_n = ea_pair_rhs_n;` | **NOT CAUGHT** |

⚠ **AND THE REASON IS THE STIMULUS, NOT THE GATE'S SHAPE.**  On a
`MOV [imm16],AW` predecessor — the rig's own probe instruction, and the **only**
preceding form with a silicon reference — `ea_residue` and `tmpa` hold the same
value, so the arm's assignment is a no-op and the retained-rail plumbing is
invisible to any comparison.  P4 misses for a second reason: `modrm_reg_n` is
not the net that routes this destination; `r_idx_n` is.

> **THIS GATE FALSIFIES THE OBSERVABLE LAW — WHICH REGISTER RECEIVES WHAT —
> AGAINST SILICON.  IT DOES NOT COVER THE RETAINED-RAIL PLUMBING, AND THE
> DOCSTRING SAYS SO.**  A characterisation-lock leg over the pair-rail family
> was built, measured (§4's table) and **NOT SHIPPED**: with no silicon
> reference it would freeze the ucore's own answer, and the ucore's answer on
> that family is the one §4 has just called into question.  **Locking a value
> you suspect is wrong is worse than having no leg.**

---

## §6  THE LADDER — **ZERO-DELTA, AND BY CONSTRUCTION**

**P-5 MET, EXACTLY**: `sha256sum` over the **107 tracked files Quartus reads**
(`hdl/rtl/**`, `hdl/sys/**`, `nec_test.sv`, `nec_test.sdc`,
`nec_test_ucore.qsf`, `files_ucore.qip`) is **IDENTICAL before and after — 0
files moved**.  `sw/testdata/wave23/synth-manifest-{before,after}.txt`.
**The Verilated TB is therefore the same binary on both sides** (receipt
`5332bc26a38de4b2…`), which is why the legs below are a RE-REGISTRATION on this
tree and not a comparison of two trees.

<!-- WAVE23-LADDER-BEGIN -->
<!-- WAVE23-LADDER-END -->

---

## §7  G6 — SCORED

| bar | result |
|---|---|
| **G6-A** `hdl/nec_test.sdc` exception-free | **MET.**  Anchored `grep -cE '^[[:space:]]*(set_multicycle_path\|set_false_path\|set_max_delay)'` = **0**.  The unanchored count is **2** and both are the commented DO-NOT-RESTORE record at lines 237-238 — **which is why the anchor is the instrument** |
| **G6-B** `quartus_gate.py` PASS | **NOT OWED, AND NOT RUN.**  §6: not one synthesis input moved, so the compiler would be handed identical bytes.  WAVE 21 measured on this very tree that identical input yields a **byte-identical `.rbf`** (`e91a67badeef2c17…`, two builds).  **A Quartus compile measures a bitstream; this wave does not move one.**  `test_quartus_gate` **302/302** is green as the gate's own falsifier |
| **G6-C** no regression vs `worst-of-5` CONTROL 34.48 / RETENTION 34.41 | **NOT OWED, AND NOT RUN**, same reason.  **The floor was registered anyway and it did not bind**, because its trigger — *"if any synthesis input moves"* — did not fire.  **NOTHING IN THIS WAVE IS QUOTED AS AN Fmax FIGURE**; the live band remains WAVE 19's 34.48 / 34.41 |
| **G6-D** `cutset_lint` 81/0 and `phase_split_lint` 157/779/0 | **MET, BOTH EXACT** — `cutset_lint: PASS (81 members / 0 violations)`, `phase_split_lint: PASS (157 members / 779 bits / 0 violations)`.  **No stage-2 wire was asked for and the cut set was not widened** (S-3 did not fire) |

---

## §8  BARS X-1 … X-7

| bar | verdict |
|---|---|
| **X-1** pre-registration before the first `hdl/` edit | **MET** — `3818953ad2`, and there was no `hdl/` edit to be before |
| **X-2** `mod3_illegal` ARCH 0/128 → 128/128, POINT | ⚠ **MISSED, AND REGISTERED AS A MISS IN ADVANCE** (prereg P-1).  Measured **`0/128 full (cycles 128, arch 0)`**.  **Reported as registered, not restated**: the mechanism it would be testing is already correct, and the residue is the TB's stimulus (§3) |
| **X-3** ladder zero-delta both sides | **MET** — §6, and by construction: 107/107 synthesis inputs byte-identical.  **`ss_lint` DID NOT MOVE** (232 addresses / 229 flops / 4 whitelist / **0 UNMAPPED**); the permitted delta was not used because **no flop was added** |
| **X-4** no flash, no board contact | **MET — NO BOARD WAS TOUCHED.**  And the bitstream did not move, so **nothing new is owed to fabric and FLASH #23 still covers this tree** |
| **X-5** the user's uncommitted files | **MET** — no `git stash` / `checkout .` / `reset --hard`; every `git add` by explicit path; `sw/testdata/receipts/*.jsonl` NOT added |
| **X-6** nothing dies silently | **MET** — nothing was retired, so no ledger entry is owed.  `invalidation_ledger.md` gains no register |
| **X-7** doc discrepancies as a FLOOR with a disposition each | **MET** — §9, **5 hits, 5 dispositions, and the count is a FLOOR** |

---

## §9  DOCUMENTATION DISCREPANCIES — **FIVE FOUND, FIVE DISPOSITIONED, AND THE COUNT IS A FLOOR**

| # | where | what is wrong | disposition |
|---|---|---|---|
| **D-1** | `tests/v30/mod3_illegal/metadata.json`, `finding` | *"The core **WEDGES** at S_HALT on this - the bug."* — **FALSE for the ucore**, whose cycle rows are 128/128.  It describes the ARCHIVED FSM core, deleted 2026-09-19 (RET-2) | **LEFT WITH REASON.**  It is a frozen capture artifact under WAVE 22's committed sha256 manifest (`67161a0c409c7fc6…`) and editing it would invalidate that manifest.  **Erratum recorded here and in `standing_gates.md` §W22** |
| **D-2** | `hdl/rtl/ucore/v30u_eu.sv:247-250` | *"a ModR/M EA calculation instead leaves the pre-displacement base here"* — **the tree does not do that** on `mod=00 rm=110` (§4) | **LEFT WITH REASON, AND THE REASON IS LOAD-BEARING**: it is a **synthesis input**.  Editing a comment there moves the manifest, fails P-5, and puts a **10-draw Quartus sweep** on this wave's bill for a sentence.  Booked with §4 |
| **D-3** | the briefing itself | *"THE mod=3 LEA STALE-EA **WEDGE**"*, *"the FIRST `hdl/rtl/ucore/` edit in many waves"*, *"If it does not [have a latch], you are ADDING STATE"*, and **X-2** | **FIXED IN PLACE** — enumerated in the pre-registration §6 **before** the results were known |
| **D-4** | `CLAUDE.md` gate quick reference | *"mod3_illegal needs `--residue stale-ea`"* — that flag belongs to `ucsim_check`, which exits 2 naming RET-1.  The live scorer is `check_core --suite-dir … --opcodes goldens` | **FIXED** — the WAVE 23 banner added to `CLAUDE.md` states the live command and the live figure |
| **D-5** | `suite_scorer_results_2026-09-19.md` §5 | *"no injected engine can reproduce"* — **CORRECT, and now proved rather than asserted**; what it could not say is WHY, or that the ucore is right on the complete path | **MARKED-HISTORY** — §5 stands unedited and this document is its continuation, cross-referenced from `standing_gates.md` §W22 |

⚠ **THE COUNT IS A FLOOR AND THE METHOD SAYS SO** (WAVE 21's lesson): this is a
**manual** enumeration over the documents this wave had reason to open.  **No
gate enumerates claims about the ucore's undocumented-opcode behaviour**, and
D-2 was found only because a measurement contradicted it — not by any search.

---

## §9.1  ⚠ ERRATUM AGAINST THIS WAVE'S OWN PRE-REGISTRATION — **THREE CITATIONS IN IT ARE ONE LINE OFF, AND IT WAS NOT EDITED**

`3818953ad2` cites `v30u_eu_arm_bind.svh:79-85` (the block is **81-84**, and it
is **four** lines, not six) and `v30u_eu.sv:832-841` (the comment runs to
**845**, where the `opr_starved` wire itself is).  **The file was momentarily
corrected and then RESTORED TO ITS COMMITTED BYTES**: a pre-registration that
is edited after the results are known is not a pre-registration, and a typo in
a line number is not worth that.  **The corrected citations are the ones used
everywhere else in this document, in `CLAUDE.md` and in `standing_gates.md`.**
Nothing the prereg registered — no bar, no prediction, no STOP — depends on
them.

---

## §10  WHAT THIS WAVE DELIBERATELY DID NOT DO

* **It did not edit `hdl/`.**  The freeze the briefing lifted was **DECLINED AS
  UNNEEDED**, and the timing achievement it protects is untouched.
* **It did not inject `ea_residue` into the backdoor** to buy 128/128 (S-4).
* **It did not fix §4's ModR/M divergence** — two prose-inferred rows, and the
  capture that would settle it needs the board (§4.1).
* **It did not ship a characterisation-lock leg** over the pair-rail family
  (§5).
* **It did not run Quartus** (§7).
