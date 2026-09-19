# WAVE 18 — PRE-REGISTRATION: `check_fuzz_bank` CANNOT RUN, AND NEITHER CAN ITS SIBLINGS

**Committed BEFORE the first edit to `hdl/`, `sw/` or any document this wave
changes.**  Offline only.  No board.  No flash.  No Codex.

---

## 1. THE FINDING AS RECEIVED, AND WHAT IS ALREADY MEASURED

`sw/check_fuzz_bank.py` is unrunnable.  Measured on this tree (`f89f4e6978`)
before any edit:

```
$ python3 sw/check_fuzz_bank.py           ; EXIT=1
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:255:6: Pin not found: 'ADDR_O'
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:256:6: Pin not found: 'DATA_O'
%Error-PINNOTFOUND: hdl/tb/tb_v30_core.sv:257:6: Pin not found: 'STATUS_O'
%Error: Exiting due to 3 error(s)
artifact.ArtifactError: ARTIFACT LAYER -- BUILD FAILED -- hdl/tb/obj_dir/Vtb_v30_core
  recipe   verilator_binary/tb_v30_core/fsm
```

**AND IT IS BIGGER THAN THE TB.**  `hdl/rtl/system_large.sv:542-544` connects
the same three pins UNCONDITIONALLY, so:

```
$ python3 sw/check_ab_sim.py --core fsm   ; EXIT=1
%Error-PINNOTFOUND: hdl/rtl/system_large.sv:542:6: Pin not found: 'ADDR_O'
```

`hdl/files.qip` (the `nec_test` FSM Quartus revision) compiles that same
`system_large.sv`, so the FSM **bitstream** path is implicated by the same
three lines.  That is a claim, and §4 registers how it is tested.

## 2. THE INVARIANT THAT WAS BROKEN, IN THE ARCHIVE'S OWN WORDS

`docs/notes/fsm_core_archive_2026-08-04.md` §6a, the only authorised change to
the archived core since the archive, states the rule it was made to satisfy:

> the two cores are DROP-IN alternatives with the same module name and the same
> port list … A port list that differed between them would make the A/B
> uncontrolled in exactly the way §51.8b warns about.

`hdl/rtl/ucore/v30_core.sv`'s own header makes the same claim in the present
tense — *"same module name, same port list"* — and since `b7083b45a5`
(2026-08-14) **that sentence has been false**.  This wave is not a new decision;
it is the restoration of a rule the archive already carries.

## 3. THE DISPOSITION, REGISTERED BEFORE IT IS TAKEN

**(b) REPAIR THE ARCHIVED CORE**, under §6a's precedent and for §6a's stated
reason, scope limited to **THREE OUTPUT PORTS AND THREE TIE-OFFS**:

```
    output     [19:0] ADDR_O,
    output     [15:0] DATA_O,
    output      [3:0] STATUS_O,
...
assign ADDR_O = '0;  assign DATA_O = '0;  assign STATUS_O = '0;
```

**NOT IMPLEMENTED, AND DECLARED SO.**  The archived core publishes the
MULTIPLEXED view only; it is not re-derived, no BIU or EU line is touched, no
flop is added, no behaviour changes.  Every instantiation of the FSM core in the
tree leaves all three UNCONNECTED (`tb_v30_core.sv:255-257`,
`system_large.sv:542-544`), so nothing in the tree reads the zeros.

**WHAT THE ALTERNATIVES COST, registered before the measurement:**

* **(a) make the TB's three pins conditional.**  Fixes the `tb_v30_core` gates
  and NOT `system_large`, so `check_ab_sim --core fsm` and the FSM Quartus
  revision stay broken — 2 of the 4 breakage sites.  It also requires
  parameterising `tb_v30_core.sv` on the engine, which
  `hdl/rtl/ucore/v30_core.sv`'s header explicitly forbids (*"hdl/tb/tb_v30_core.sv
  is not parameterised on the engine"*), and it would leave the §6a port-list
  invariant broken while hiding the symptom.
* **(c) formally retire `check_fuzz_bank`.**  Retires ONE gate and repairs
  nothing: `check_ab_sim --core fsm`, `t30_sweep.sh` and the FSM bitstream path
  are not that gate, and §6's re-activation procedure (*"All of it works on this
  tree today"*) would become false with nothing written to say so.  A
  retirement is a legitimate outcome for a gate whose SUBJECT is dead; the
  subject here is alive and the PORT LIST is what died.

## 4. THE BARS — pre-registered, numeric, monotone

| id | bar |
|---|---|
| **W18-1** | `python3 sw/check_fuzz_bank.py` RUNS to a verdict and prints a `PASS`/`FAIL` line.  ⚠ **The verdict itself is NOT pre-registered as PASS.**  The last figure on record is `PASS \| 621 \| stable 621 \| worse 0` at `399ba6729d` (2026-08-10) and **five weeks of landings sit between**; whatever it reads is REPORTED, not scored. |
| **W18-2** | `python3 sw/check_ab_sim.py --core fsm` = **MATCH over 187 rows** (the archive §6a figure, re-derived on this tree). |
| **W18-3** | `python3 sw/check_core.py --core fsm --suite-dir tests/v30/v0.1 --opcodes all --cases 0 --waits 0` = **168,400 / 169,000** — the archive §5 corrected-comparator figure, UNMOVED.  Any other value fails this wave. |
| **W18-4** | `python3 sw/ss_lint.py --core fsm` rc 0, **203 addresses, 181 flops, 0 UNMAPPED** — an output port is not a flop. |
| **W18-5** | **NON-VACUITY.**  Deleting ONE of the three new ports from the archived core makes `check_fuzz_bank` FAIL, naming that pin.  Demonstrated, then reverted. |
| **W18-6** | **A GATE SEES IT NEXT TIME.**  A new lint, `sw/core_portlist_lint.py`, compares the two `v30_core` port lists under `V30_MUXED_AD` and exits non-zero naming any port present in one and absent from the other.  It must FAIL on the pre-repair archived core (positive control, run against the pre-edit file) and PASS after. |
| **W18-7** | **THE ucore LADDER IS ZERO-DELTA** (U-5): `check_core --opcodes all --cases 0` **169,000/169,000** · `ulockstep --golden all --cases 50` **17,350/17,350** · `chain_lfsr_gate` PASS with its four signatures byte-identical · `r7_lint` PASS · `ss_lint` PASS at `SS_VERSION` 0x8F / 232 / 228 flops · `demux_off_gate` PASS. |
| **W18-8** | **THE SIBLING INVENTORY.**  Every gate in `standing_gates.md` §C is invoked on this tree and its status recorded as RUNS / DOWN-with-reason, **before and after** the repair.  The inventory is reported whatever it shows. |

**W18-9 — THE FSM QUARTUS CLAIM.**  §1 claims `system_large.sv:542-544` breaks
the FSM Quartus revision.  It is registered here as a CLAIM.  It is tested by
running `quartus_map` on the `nec_test` revision (analysis only, no fit, no
bitstream, single-writer check first) BEFORE the repair — the prediction is an
analysis ERROR naming `ADDR_O` — and again AFTER.  **If the stage is not run,
the claim is reported as DERIVED-NOT-MEASURED and never as a measurement.**

## 5. WHAT IS NOT DONE HERE

* **No board, no flash.**  FLASH #22 stands.
* **`standing_gates.md` and `CLAUDE.md` are NOT EDITED** — the coordinator is
  registering the backlog in parallel.  §7 of the results document lists what
  needs registering.
* **The archived core's two open findings are not touched** (§3.2's 104-seed
  regression, §3.3's one-line F51 HALT fix).  Neither is started, exactly as the
  archive leaves them.
* **`t30_sweep.sh`'s v0.3 leg (3.7 M cases) is not run.**  The sweep's status is
  reported from its shared blocker and its cheap legs, and labelled as such.

---

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
