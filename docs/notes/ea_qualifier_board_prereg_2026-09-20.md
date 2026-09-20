# WAVE 26 — BOARD PRE-REGISTRATION (ADDENDUM TO `ea_qualifier_prereg_2026-09-20.md`).  **COMMITTED BEFORE THE FIRST BOARD CONTACT.**

The wave's pre-registration is `86b33eeebb`.  This addendum registers the
**silicon bar** and its POINT predictions, and it is committed **before the
socket is touched**.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

---

## §1  WHAT IS CAPTURED, AND WHY IT IS THIS AND NOT `mod3_illegal`

**THE RIG IS `sw/w26_ea_lane2.py`**, committed in the same commit as this
document and **before board contact**.  It is `sw/b2_ea_lane.py` extended:

* **THE THIRTEEN WAVE 24 PROBES ARE KEPT VERBATIM AS REPRODUCTION CONTROLS.**
  Their expected values are read **out of WAVE 24's own capture**
  (`sw/testdata/wave24/b2/8D.json.gz`), never hard-coded.  A control that does
  not reproduce is a **rig finding**, not a result.
* **EIGHT NEW ROWS CLOSE THE REFERENCE GAP WAVE 24 DECLARED** — `mod = 01` and
  `mod = 10`, where a base/index sum **and** a displacement are both present
  and WAVE 24 probed neither (`suite_divergence_results_2026-09-20.md` §6.3's
  final ⚠).

⚠ **THE BRIEF NAMED `B-3` — THE `mod3_illegal` RE-CAPTURE — AS THIS WAVE'S
SILICON BAR, AND I AM DELIBERATELY NOT TAKING IT.  THE REASONS ARE REGISTERED
HERE, BEFORE THE ALTERNATIVE IS RUN, SO THEY CANNOT BE A POST-HOC EXCUSE:**

1. `tests/v30/mod3_illegal/` is a **FROZEN artifact under WAVE 22's committed
   sha256 manifest `67161a0c409c7fc6…`**, and `sw/lea_mod3_gate.py`'s **L1 and
   L4 legs read their expected values out of its `metadata.json`**.  Replacing
   its goldens moves a frozen input to a live gate.
2. A re-capture with a declared predecessor is **a different suite**, not a
   re-measurement of the old one: `0 / 128` and the new figure would not be
   comparable, so the ratchet would be **broken, not raised**.
3. **The information it would buy is exactly what §2's eight rows buy**, at
   ~30 seconds of board time, **with the frozen suite left untouched** — and
   WAVE 24 itself wrote that 128 more rows *"would add cases, not
   information."*
4. **WAVE 24 §5's precedent is directly on point**: it refused to ship a
   re-capture into a frozen suite when the trade trained a documented state
   into an undocumented one.

**IF THIS IS THE WRONG CALL IT IS THE COORDINATOR'S TO REVERSE** — nothing is
destroyed by not taking it, and the route stays costed in
`suite_divergence_results_2026-09-20.md` §7.

---

## §2  THE POINT PREDICTIONS — **REGISTERED BEFORE THE SOCKET IS TOUCHED**

Every probe is `<predecessor> 8D F7`, body `PS=0x0000 PC=0x8100`,
`char_mod3.SETUPS[0]` with `AW = 0x1111`.

**THE RULE UNDER TEST** (landed in the RTL before this capture, and NOT
adjustable after it): *the address adder's B rail is loaded on every EA
calculation with the SECOND ADDEND — the index register where the form has
one and nothing is added after it, the displacement otherwise, and ZERO where
there is nothing to add.*

**THE `mod = 01` / `mod = 10` ROWS ARE THE VALIDATION POPULATION AND THEY DID
NOT SELECT THE RULE**: the rule was fixed by WAVE 24's thirteen `mod = 00`
rows, the RTL was written and built against those thirteen, and **only then**
were these eight composed.  The ucore's column below was measured OFFLINE on
the landed RTL **before** this document was committed and is quoted here as
the prediction, not as a result.

| tag | predecessor | form | EA | **PREDICTED silicon `SI`** | the reading it refutes if the prediction holds |
|---|---|---|---:|---:|---|
| `P0` | `89 40 10` | `mod=01 rm=000` `[BW+IX+10h]` | `BBCB` | **`1121`** | *B = the index* → `8888` |
| `P1` | `89 40 00` | `mod=01 rm=000` `[BW+IX+0]` | `BBBB` | **`1111`** | ⭐ *B = the index when the displacement is ZERO* → `8888`.  **THE SHARPEST ROW IN THE SET**: it separates *"the form carries a displacement"* from *"the displacement is non-zero"*, and the RTL implements the former |
| `P2` | `89 46 10` | `mod=01 rm=110` `[BP+10h]` | `6676` | **`1121`** | *B = 0 on a one-register form* → `1111` |
| `P3` | `89 84 34 12` | `mod=10 rm=100` `[IX+1234h]` | `89AB` | **`2345`** | *B = 0 on a one-register form* → `1111` |
| `P4` | `89 81 34 12` | `mod=10 rm=001` `[BW+IY+1234h]` | `DF00` | **`2345`** | *B = the index* → `9999` |
| `P5` | `89 45 20` | `mod=01 rm=101` `[IY+20h]` | `88A8` | **`1131`** | *B = 0* → `1111` |
| `P6` | `89 87 34 12` | `mod=10 rm=111` `[BW+1234h]` | `5678` | **`2345`** | *B = 0* → `1111` |
| `P7` | `89 44 F0` | `mod=01 rm=100` `[IX−10h]` | `7767` | **`1101`** | *B = 0* → `1111`; *B = the UNSIGNED disp8* → `1201` |

**AND THE THIRTEEN CONTROLS ARE PREDICTED TO REPRODUCE WAVE 24's SILICON
COLUMN EXACTLY**: `C1 1234 · C2 BEEF · C3 2222 · R1 4121 · R2 1121 ·
M0 8888 · M1 9999 · M2 8888 · M3 9999 · M4 1111 · M5 1111 · M6 2345 ·
M7 1111`.  ⚠ `R2`'s value is **image-fill dependent** (`0x4455 + 0xCCCC`,
`suite_divergence_results_2026-09-20.md` §6.1) and reproduces only because the
composer's fill has not moved since; if it reads `D4E5` the fill went back to
`0x90` and that is a finding about the composer, not about the core.

**SCORING**: **21 / 21 is the POINT prediction.**  A control that moves is a
rig finding and **STOPS** the run.  A `P` row that misses is a **REGISTERED
MISS on the validation population** — it does not retract the thirteen
anchored rows, and it is reported as registered, with the refuted reading
named.

---

## §3  BOARD DISCIPLINE — THE SESSION'S OWN BARS

| | |
|---|---|
| authorisation | **CAPTURE ONLY.  NO FLASH.** |
| socket | `use_core=False`, **passed explicitly on every probe** — the CFG is STICKY.  `emit_suite.EMIT_USE_CORE is not False` → the rig **REFUSES to start** |
| divider | `div_guard()` on every probe; the readback is recorded in the manifest.  **An UNPINNED readback is STOP S-5, a HARD STOP** |
| retention | full per-clock rows + sha256, `8D.json.gz` + `manifest.json` by value under `sw/testdata/wave26/b2b/` |
| single-writer | `pgrep -x ssh` before first contact |
| closing | `board_idle()` and a `use_core=0` chip proof (`check_ab_hw chip 800`) |
| **FLASH #23** | `sw/testdata/flash_log.jsonl` **MUST still read 26 entries, sha256 `13a81a43f30c380a…`** at the end — **STOP S-6** |

⚠ **NOTHING IN THIS WAVE IS FLASHED, SO THE BOARD IS RUNNING FLASH #23 WHILE
THE TREE NO LONGER MATCHES IT.  THE SOCKET LEG IS UNAFFECTED BY THAT** — the
truth source is the chip in the socket, not the FPGA core — and the ucore leg
is Verilated from the landed tree.  **No FPGA-side figure is taken in this
session.**
