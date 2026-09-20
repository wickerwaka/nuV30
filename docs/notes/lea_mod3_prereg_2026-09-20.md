# WAVE 23 — PRE-REGISTRATION.  **THE MECHANISM IS ALREADY IN THE TREE, IT ALREADY MATCHES SILICON, AND THE PREDICTED `mod3_illegal` FIGURE IS THEREFORE `0 / 128` — A REGISTERED MISS AGAINST THE BRIEF'S POINT PREDICTION.**

Committed **before the first `hdl/` edit** and before the first scored run of
this wave's new instrument.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

⚠ **THIS DOCUMENT REGISTERS A REFUTATION OF ITS OWN BRIEFING'S CENTRAL
PREMISE.**  The briefing is authorised to lift the `hdl/rtl/ucore/` freeze for
*"the mod=3 LEA stale-EA wedge"*.  **There is no wedge and there is no missing
mechanism.**  §0 records what was measured before this file was written, in the
WAVE 22 form (*"six of the briefing's own premises are wrong and the
measurements are in §0"*), because the briefing's own instruction is to *treat
the documentation as hearsay until proven otherwise* and the proving had to
happen first.

---

## §0  WHAT WAS ALREADY MEASURED WHEN THIS FILE WAS WRITTEN

Diagnostic reads and runs only — **no `hdl/` file has been touched and no
scored gate of this wave has been run.**

| # | measured | value |
|---|---|---|
| 0.1 | `check_core --core ucore --suite-dir tests/v30/mod3_illegal --opcodes goldens --cases 0` | `TOTAL: 0/128 full (cycles 128, arch 0)`; every case `exp 0500 got 0000` |
| 0.2 | the 128 goldens' expected value | **1280 = `0x0500` on all 128**, in the register the ModR/M `reg` field names, and `0x0500` **is the goldens' own initial `ip`** (`Counter({1280: 128})` over `initial.regs.ip`) |
| 0.3 | does the ucore have a last-EA latch? | **YES — `ea_residue`, `hdl/rtl/ucore/v30u_eu.sv:251`**, with `ea_pair_rhs` / `ea_pair_valid` beside it, **SS-mapped at `0x177` / `0x178` / `0x179`** and versioned in `v30u_ss_pkg.sv` (*"WRFUZZ LEA residue: 0x88 -> 0x89"*, *"WRFUZZ LEA pair rail: 0x89 -> 0x8A"*) |
| 0.4 | is the `8D` / `mod == 3` path implemented? | **YES — `hdl/rtl/ucore/v30u_eu_arm_bind.svh:79-85`**, `if (!ld_ext_n && (ld_b_n == 8'h8D) && (rmmod == 2'd3)) begin tmpa_n = ea_residue_n; if (ea_pair_valid_n) tmpb_n = ea_pair_rhs_n; end` |
| 0.5 | does the ucore WEDGE, as `tests/v30/mod3_illegal/metadata.json` says? | **NO.** Cycle rows are **128 / 128** on all 128 goldens, and `v30u_eu.sv:832-841` states in as many words that `opr_starved` fires on `62`/`C4`/`C5`/`FE`/`FF /3`/`/5` at `mod == 3` **and not on `8D`** |

**0.6 — THE DECISIVE DIAGNOSTIC.**  Driven through `sw/tb_bootrun.py`'s
`+bootimg` mode — **from RESET, with NO backdoor injection at all**, so the
image's own loader runs inside the core exactly as it ran inside the chip
(TB receipt `5332bc26a38de4b2…`):

| stimulus (body at `PS = 0x0000`) | SILICON, `metadata.json::stale_ea_probe` | **ucore** | |
|---|---:|---:|---|
| `MOV [1234h],AW ; LEA SI,DI(mod3)` | `0x1234` (`match: true`) | **`0x1234`** | **MATCH** |
| `MOV [BEEFh],AW ; LEA SI,DI(mod3)` | `0xBEEF` (`match: true`) | **`0xBEEF`** | **MATCH** |

**THE ucore REPRODUCES BOTH OF SILICON'S POSITIVE STALE-EA WITNESSES EXACTLY,
WITH NO EDIT OF ANY KIND.**

**0.7 — AND THE `0x0500` THE 128 GOLDENS EXPECT IS THE SAME MECHANISM.**
`sw/testimage.py::load_routine` — byte-identical at the capture commit
(`74942059cf`, 2026-07-18) and today — ends **`BR PS:PC`**.  Measured on the
same from-reset path, with no instruction before the LEA:

| `PS` | `PC` | ucore writes | `PC + PS` |
|---:|---:|---:|---:|
| `0x0000` | `0x8100` | `0x8100` | `0x8100` |
| `0x0800` | `0x0100` | `0x0900` | `0x0900` |
| `0x0810` | `0x0000` | `0x0810` | `0x0810` |

and, discriminating the sum from a single latch, `MOV [1234h],AW` at
`PS = 0x0800` writes **`0x1A34` = `0x1234 + 0x0800`**, not `0x1234`.

> **THE DECOMPOSITION IS MEASURED, NOT ASSUMED**: the register receives
> `ea_residue + tmpb`, the terminal `BR PS:PC` of the capture harness's loader
> leaves **`PC` on the EA rail and `PS` on the scratch rail**, and the 128
> goldens are all captured at `PS = 0x0000`, `PC = 0x0500` — so their expected
> value is `0x0500 + 0x0000`.  **The ucore produces it.**

---

## §1  THE MECHANISM, IN ONE SENTENCE

> **At `mod == 3` the `8D` decode issues no EA calculation, so the row-1
> `SIGMA -> R` transfer writes the register the ModR/M `reg` field names with
> whatever the address adder's two rails still hold — the retained EA lane and
> the ordinary scratch lane — and the instruction falls through.**

**IT IS ALREADY THE TREE'S SENTENCE.**  It is implemented in six lines of
`v30u_eu_arm_bind.svh`, it names no opcode table, it costs no flop that is not
already there, and it is SS-mapped.  **NO RTL RULE IS ADDED BY THIS WAVE.**

---

## §2  WHY `0 / 128` IS NOT AN RTL DEFECT

`hdl/tb/tb_v30_core.sv` injects **the fourteen architectural registers**
through the `V30_BACKDOOR` port while the core is held in reset
(`for (i = 0; i < 14; i++) bkd_regs[i*16 +: 16] = rv[i];`) and **nothing
else**.  `ea_residue` therefore enters every golden case at its RESET value,
`16'd0`, while the chip entered the identical window carrying `0x0500` from
the loader's own terminal branch.

**The golden carries no field for it**, so the injected leg is scoring the
ucore against a stimulus the ucore was never given.  WAVE 22 wrote exactly
this (`suite_scorer_results_2026-09-19.md` §5: *"a property of what the chip
did **before** the window"*) — **this wave proves it, and proves the ucore
right on the path where the stimulus is complete.**

---

## §3  WHAT THIS WAVE WILL DO

1. **NO `hdl/rtl/ucore/` EDIT.  NO `hdl/` EDIT OF ANY KIND.**  The freeze
   stands; the briefing's lifting of it is **DECLINED AS UNNEEDED**.
2. Build **`sw/lea_mod3_gate.py`**, a standing always-on falsifier for the
   mechanism on the path where it is scoreable — the from-reset whole-program
   replay — anchored on the metadata's own SILICON rows, with positive
   controls and a non-vacuity leg.
3. Record the erratum against `tests/v30/mod3_illegal/metadata.json` **without
   editing that file** (it is a frozen capture artifact under WAVE 22's sha256
   manifest `67161a0c409c7fc6…`).

---

## §4  PRE-REGISTERED PREDICTIONS

| id | prediction | how it is scored |
|---|---|---|
| **P-1** | `check_core --core ucore --suite-dir tests/v30/mod3_illegal --opcodes goldens --cases 0` reads **`0/128 full (cycles 128, arch 0)`, UNCHANGED** | the brief's **X-2 is registered as a MISS** and is reported as registered, not restated |
| **P-2** | `sw/lea_mod3_gate.py` **L1 SILICON = 2 / 2** — the two `match: true` `stale_ea_probe` rows, read out of `metadata.json` and not hard-coded | point |
| **P-3** | **L2 ROUTING = 64 / 64** — all 8 ModR/M `reg` fields x all 8 `rm` values receive the preceding EA and **no other GPR moves**, i.e. the value is `reg`-selected and `rm`-independent | point |
| **P-4** | **L3 NON-VACUITY fires on 3 of 3 controls** — a different preceding EA gives a different value; a `mod != 3` LEA gives the real EA and not the residue; and a stimulus with the LEA removed leaves the register at its loaded value | point |
| **P-5** | **THE LADDER IS ZERO-DELTA**, and trivially so: **not one file reachable from `hdl/files_ucore.qip` changes**, proved by sha256 before and after | per-leg |
| **P-6** | **G6-A anchored `grep` = 0** live `set_multicycle_path` / `set_false_path` / `set_max_delay` in `hdl/nec_test.sdc`; **G6-D `cutset_lint` 81/0** and **`phase_split_lint` 157/779/0** | point |

### §4.1  G6-B AND G6-C ARE PRE-REGISTERED AS **NOT OWED**, WITH THE REASON

**A Quartus compile measures a bitstream.  This wave does not move one.**
If P-5 holds — **no file in the synthesis manifest changes by a single byte** —
then the compiler is handed identical input, and WAVE 21 measured on this very
tree that identical input yields a **byte-identical `.rbf`** (`standing_gates.md`
§A: two builds, both `e91a67badeef2c17…`).  **Ten Quartus draws would
re-measure `34.48 / 34.41` on an unchanged tree.**

> **THE FLOOR IS REGISTERED ANYWAY, AND IT BINDS IF P-5 FAILS**: if any
> synthesis input moves, **G6-C `worst-of-5` >= 34.48 CONTROL and >= 34.41
> RETENTION**, 5 seeds each, and a five-draw sweep is run before anything is
> called landed.

---

## §5  WHAT IS A **STOP**

* **S-1** Any need to add a second rule, an opcode table, or a per-form case to
  make the mechanism match — **STOP AND REPORT** (briefing, verbatim).
* **S-2** Any need for a `set_multicycle_path` / `set_false_path` /
  `set_max_delay` in `hdl/nec_test.sdc` — **automatic STOP**.
* **S-3** Any need for stage 2 of the phase split to name a pre-cut wire, i.e.
  any widening of `cutset_lint`'s cut set — **STOP AND REPORT**.
* **S-4** **Injecting `ea_residue` through the backdoor to turn `0/128` into
  `128/128` IS A STOP IN THIS WAVE.**  It is choosing an initial condition
  after seeing the expected answer; the goldens carry no such field; and the
  value would be right only because these 128 all sit at `PS = 0x0000`.  It is
  **BOOKED, NOT TAKEN**, with its own falsifier in the results.
* **S-5** Any edit to `tests/v30/mod3_illegal/metadata.json` or
  `goldens.json.gz` — they are frozen capture artifacts under a committed
  sha256 manifest.
* **S-6** Any board contact.  **X-4: no flash, no socket, nothing.**

---

## §6  WHAT THE BRIEFING GOT WRONG, ENUMERATED IN ADVANCE OF THE RESULTS

| briefing clause | measured |
|---|---|
| *"THE mod=3 LEA STALE-EA **WEDGE**"* / *"The core **WEDGES** at S_HALT on this — the bug"* | **REFUTED for the ucore.** Cycle rows 128/128; `opr_starved` explicitly excludes `8D`.  The wedge is the **ARCHIVED FSM core's**, and that core was deleted 2026-09-19 (RET-2) |
| *"This is the FIRST `hdl/rtl/ucore/` edit in many waves"* | **THERE IS NO EDIT.**  The mechanism landed in the wrfuzz campaign and has been SS-mapped since `SS_VERSION` 0x89 |
| *"If it does not [have a last-EA latch], you are ADDING STATE"* | **It has one**, and it has the pair rail too |
| **X-2** *"`mod3_illegal` ARCH 0/128 -> 128/128 … as a POINT prediction"* | **REGISTERED AS A MISS** — see P-1.  The injected TB cannot present pre-window microarchitectural state, and the thing it would be testing is already right |
