# THE INVALIDATION LEDGER

**Opened 2026-08-04, session SM1, by the user directive of that date**
(`CLAUDE.md` § "Correctness target"):

> Where the rig or a golden is found defective, fix the rig and RE-CAPTURE;
> goldens invalidated by rig defects are DISCARDED from all gate sets —
> archived by rename with an invalidation ledger entry (the w1evt-biased
> precedent; raw captures stay retained, nothing gates on them).

This file is the register the directive names. It did not exist before this
session; **no invalidation had ever been recorded in this project.**

## What an entry must carry

| field | meaning |
|---|---|
| **WHAT** | the artifact or population, by path, with its size |
| **WHY** | what is false about it — stated as a property of the artifact, not of anyone's opinion of it |
| **WHICH RIG DEFECT** | the named finding, and whether the defect is fixed |
| **WHAT REPLACES IT** | the interim gate, the re-capture that closes it, or "nothing" |
| **THE ARCHIVE** | where the raw data went. **Nothing is ever deleted.** |
| **GATE STATUS** | every standing figure that moved, and the new status of each gate |

**This file carries a SECOND register, opened 2026-08-09: § SUPERSEDED
POPULATIONS — NOT INVALIDATIONS (`SUP-n`).** A supersession is filed there and
never here, because *nothing is wrong with a superseded artifact*: its **WHICH
RIG DEFECT** field reads **NONE**, no capture is false, and it is retired from
the DEFAULT population by a `status` key in its own manifest rather than
discarded from every gate set. Do not read a `SUP-n` entry as evidence of a
defect, and do not file a defect as a `SUP-n`.

**It carries a THIRD register, § EXCLUDED SEEDS (`EXC-n`), a FOURTH — opened
2026-08-11 — § ERRATA AGAINST DERIVED COLUMNS (`ERR-n`), and a FIFTH, opened
2026-09-19: § RETIRED INSTRUMENTS (`RET-n`). The first four are about DATA;
`RET-n` is the only one about an INSTRUMENT this repo deleted, and its
load-bearing field is the enumeration of every gate that died with it.** The first
three are all about **CAPTURES**. `ERR-n` is the only one about a **DERIVED
COLUMN** — something this tree *computed* from a capture and stored beside it,
which can be wrong while every capture behind it is true. Its **WHICH RIG
DEFECT** field also reads **NONE**, and it carries a field none of the others
has: a named **INSTRUMENT** defect with its fix commit. Its disposition is
neither discard nor retire nor drop — the column is **RECOMPUTED IN PLACE** and
every movement is reported. Read its six preconditions before filing one; it is
not a licence to edit data that disagrees with a gate.

## A caution about the precedent this directive cites

**The w1evt-biased event is an ARCHIVE-BY-RENAME, not an invalidation**, and
reading it as one will produce the wrong mechanics. `ucsim_t_provenance.md`
§24.4 / §24.7: `tests/v30/v0.1-w1evt` was renamed to `v0.1-w1evt-biased` because
its case generation was BIASED (706 rerolls), a fresh tranche was emitted on the
same committed path, and **both** were re-scored at 1,200/1,200. §24.7's own
words: *"the old suite is **not retracted** — it was a true statement about the
1,200 cases it contained."* The biased suite is a **live standing gate to this
day** (`standing_gates.md` §B).

So the precedent supplies the *habit* — rename, never delete; keep the evidence
with the artifact; land it as its own commit; report both numbers — and not the
*disposition*. **INV-1 below is the project's first artifact that is actually
invalid**, and it is invalid in a specific way the precedent has no case for:
the captured data is TRUE and its LABEL is FALSE.

---

## INV-1 — THE EVT-SCORED FUZZ POPULATION, AS A GATE

**Opened 2026-08-04 (SM1). CLOSED 2026-08-04 (SM2) by re-capture.
Status: **CLOSED — the population is REBUILT and back in the gate.**
The rig defect is FIXED in RTL, in the host tool, in the bitstream (FLASH #4)
and on the board.  The closure record is §CLOSURE below and
`ucore_provenance.md` §59.7.3-§59.7.7.**

### WHAT

Not a file and not a directory — a **population selection** and the two standing
figures computed over it:

| | |
|---|---|
| the seeds | **760** banked fuzz seeds carrying `evt.hold = 300`: `tests/v30/fuzz_bank/mc1/seeds/*.json.gz` (**369**) and `tests/v30/fuzz_bank/mc2/seeds/*.json.gz` (**391**) |
| measured, this session | all 760 are inside the **1,008-seed scored EVT population**; the other 248 scored EVT seeds carry `hold = 2`. (The remaining 157 armed-but-unscored seeds are `OPEN_BUS` and all carry `hold = 2`. 760 + 248 + 157 = 1,165 = every `evt`-armed banked seed.) |
| the figures | `timed_fuzz --evt-replay`'s **EVT** and **COMBINED** columns: ucore **EVT 192/1,008**, **COMBINED 1,675/2,710**; sim **EVT 709/1,008**, **COMBINED 1,981/2,710** |
| **NOT** invalidated | the **REGISTERED** column. Its 1,702 seeds are by definition the ones with no `evt` axis. **ucore 1,483/1,702 and sim 1,272/1,702 are untouched**, and were re-run this session at exactly those values. |

### WHY

**F46.** `hdl/rtl/hps_axi_slave.sv` stored the pin-event hold in an **8-bit**
register (`evt_hold <= wdata[23:16]`), carried as `input [7:0] evt_hold` into
`hdl/rtl/nec_bus.sv`'s scheduler. A banked hold of 300 reached the socket as
`300 & 0xFF` = **44** clocks. The truncation was **silent**.

The captures are not corrupt. `chip_rows` in all 760 files is **true silicon** —
it is exactly what the part did with INT asserted for 44 clocks. What is false
is the **`evt.hold` label**, and therefore the DIRECTIVE the harness hands an
engine when it replays the seed.

That distinction decides everything about the disposition, and it is why the
invalidation is of a GATE and not of a capture:

* a **replaying** engine (`sim` under `--evt-replay`) is HANDED the capture's
  acknowledge positions, so it barely notices: **565/760 cycle-exact**;
* a **predicting** engine (any RTL core) computes its own recognition from the
  directive, is told 300 where the part got 44, and re-enters the handler two to
  four times where the socket entered once: **22/760 cycle-exact**.

A number that separates two engines by **543 seeds** on the strength of a
directive **neither engine's silicon ever received** is not a measurement of
either engine. It also made the EVT column read as a large ucore deficit (547
ucore-only non-exact seeds, `ucore_gaps_2026-08-04.md` §T.5) that is an artifact
of the rig.

The corrected sub-population points the other way, which is the strongest single
argument that the poison was doing the work — measured this session over the
248 un-poisoned EVT seeds:

| engine | poisoned 760 | **un-poisoned 248** | as banked, 1,008 |
|---|---|---|---|
| ucore | 22 | **170 (68.5 %)** | 192 |
| sim | 565 | **144 (58.1 %)** | 709 |

**On the EVT seeds whose directive the rig actually applied, the ucore beats the
model by 26 seeds.** As banked it "loses" by 517.

### WHICH RIG DEFECT, AND IS IT FIXED

**F46 / `ucore_gaps_2026-08-04.md` gap R1. FIXED in this session's commit:**

* `hps_axi_slave.sv` — `evt_hold` is **12 bits**, packed `{wdata[30:27],
  wdata[23:16]}` into `EVT_CFG (0x20)`'s only free space. `evt_pin[26:24]` and
  `evt_arm[31]` do not move, and a host writing zeros in `[30:27]` gets exactly
  the old behaviour.
* `nec_bus.sv` — `input [11:0] evt_hold`, `ev_hold_cnt` widened to match.
* `system_large.sv` — the wire.
* `sw/v30ctl.py` — `RIG_EVT_HOLD_BITS = 12`, one place, with the RTL named as
  the authority; and `set_event` now **RAISES** on an out-of-range hold instead
  of truncating. *The root cause of INV-1 is not the width. It is that the rig
  silently applied a directive other than the one it was handed.*
* `sw/fuzz_campaign.py` — every new capture banks `evt.hold_bits` and
  `evt.hold_applied` beside `evt.hold`, so a seed says which rig took it rather
  than leaving it to be re-derived from whatever the RTL says later.

**No bitstream carries the fix.** `sw/testdata/flash_log.jsonl` ends at FLASH #3
(`924c4a61e0…`, 2026-08-04). Every flashed bitstream is 8-bit-hold silicon, so
the re-capture needs a fourth flash. That is SM2's.

### WHAT REPLACES IT

1. **Interim gate, available today** — the un-poisoned EVT sub-population:
   **248 seeds**, ucore **170/248**, sim **144/248**. Registered in
   `standing_gates.md` §B as the EVT figure, with its denominator stated.
2. **The closing measurement** — re-capture the 760 on a bitstream carrying the
   12-bit hold, at the hold the bank asks for. Then `evt.hold_bits = 12` is
   banked with the capture, `f46_invalidated` returns False by arithmetic, and
   the seeds re-enter the gate without anyone editing a list.

### THE ARCHIVE — and why it is NOT a rename

**Nothing was moved and nothing was deleted.** All 760 files are where they
were, with their `chip_rows` intact, and they are still read by
`check_fuzz_bank` (the 3,242-seed replay-regression control cited for the U5
comparator change) and by `s15_census --rmw`. Moving them would have silently
changed both of those corpora, which is a second falsehood introduced to record
the first.

The directive's *rename* mechanism assumes the invalid artifact IS a directory —
which is true of a golden suite (`v0.1-w1evt` → `-biased`) and false here: the
invalid thing is a **selection inside a shared directory**. A rename cannot
express it. So the exclusion is **DERIVED FROM THE RECORD**, in code, at
`sw/timed_fuzz.py::f46_invalidated`:

```python
h    = int(e.get("hold", 0))
bits = int(e.get("hold_bits", 8))   # no field => the 8-bit rig, by date
if h != (h & ((1 << bits) - 1)):                        # (a) REPRESENTABILITY
    return True
if "hold_applied" in e and int(e["hold_applied"]) != h:  # (b) APPLICATION
    return True
return False
```

**Limb (b) was added 2026-08-04 (SM3 sitting 5, `ucore_provenance.md` §64.3)
after a Codex review found that the predicate implemented only the one defect
we had found, not the property this entry claims.** Limb (a) asks whether the
rig *could* hold the number; limb (b) asks whether it *did*. (a) derives (b) for
F46 and for nothing else: a representable-but-mis-applied directive — a
scheduler that clamps, a host that rounds, a register widened again later —
passes (a) and would have stayed silently SCORED. **The root cause named above
is "the rig silently applied a directive other than the one it was handed", and
limb (b) is that sentence as a predicate.**

*Proof that no current record is mis-applied*: `timed_fuzz --core sim
--evt-replay --pop evt` under `--rig-hold banked` and `--rig-hold applied`
produces **byte-identical** reports (EVT 780/1,008 both, no `INVALIDATED` line
on either). If any banked record disagreed with itself the two modes would hand
the engine different directives and part.

A derivation is strictly stronger than a rename here, and the reason is the
project's own standing lesson about vacuous gates: **a list can drift away from
what it describes and a rename can be undone silently; a predicate computed from
the artifact cannot.** It also self-heals on re-capture.

`timed_fuzz` prints the excluded population on its own **`INVALIDATED`** line
with its count and, for reference only, its cycle-exact figure. It is not
summed into any gate.

### GATE STATUS — every figure that moved

| gate | before | **after** | status |
|---|---|---|---|
| `timed_fuzz --core ucore --evt-replay` **REGISTERED** | 1,483/1,702 | **1,483/1,702** | **UNCHANGED.** Re-run this session. |
| `timed_fuzz --core sim` **REGISTERED** | 1,272/1,702 | **1,272/1,702** | **UNCHANGED.** Re-run this session. |
| **EVT**, ucore | 192/1,008 | **170/248** | **RE-REGISTERED** on the un-poisoned sub-population. The 1,008 figure is STRUCK. |
| **EVT**, sim | 709/1,008 | **144/248** | **RE-REGISTERED**, same. |
| **COMBINED**, ucore | 1,675/2,710 | **1,653/1,950** | **RE-REGISTERED** (denominator 2,710 → 1,950). |
| **COMBINED**, sim | 1,981/2,710 | **1,416/1,950** | **RE-REGISTERED**, same. |
| the **full 1,008-seed EVT column** as a gate | a standing ratchet | — | **SUSPENDED pending an SM2 re-capture.** |

**A contradiction this closes.** `standing_gates.md` registered `EVT 192/1,008`
as a standing ratchet on the same day `ucore_gaps_2026-08-04.md` §T.5 said of
the same number *"the EVT column is RIG-POISONED and is not a gate."* Both were
current. The gaps report was right and the gate list had not caught up.

*Falsifier for this entry*: a capture in the 760 whose acknowledge pattern is
consistent with a hold longer than 255 clocks — i.e. evidence the truncation did
not actually happen on the wire.

### §CLOSURE — SM2, 2026-08-04.  THE RE-CAPTURE

**The bitstream INV-1 was waiting for exists**: `FLASH #4`,
`nec_test_ucore.sof 67ddd59413d58934716260966cfc981f4f0d7065e90b8a8e655010e7687e4320`,
built from HEAD with the 12-bit `evt_hold`.  The board's own host tool was
replaced with the repo's 12-bit copy in the same step — a 12-bit bitstream
driven by an 8-bit host is still an 8-bit rig, and the old copy is preserved on
the board as `v30ctl.py.pre-sm2.bak`.

**THE WIRE WAS PROVED BEFORE THE POPULATION WAS TOUCHED**, in the two halves the
falsifier asks for.  `EVT_CFG` round-trips 8/8 including 256, 300 and 4,095
(`hold = 300` packs to `0x882C0000`: `[23:16] = 44` — the exact value F46
truncated to — plus `[30:27] = 1`).  And on the PIN, one seed, one image, five
directives differing only in `hold`, INTA T1 rows counted: **2 at `hold=44`, 6
at 300, 12 at 600**, against **2** in that seed's old banked capture.  The part
entered its handler ONCE under what the rig applied and THREE times under what
the bank asked for.

**THE RE-CAPTURE.**  All 760, socket (`use_core=False`), divider PINNED, each
seed's image hash-checked against its banked `image_sha256` first:
**760 new, 0 errors, 0 GEN-DRIFT, `evt_fired` 760/760.**

**WHAT THE PART DOES UNDER A TRUE 300-CLOCK LEVEL** — registered as a
measurement, never as a bar, because it had never been observed:

| INTA T1 rows | 0 | 2 | 4 | 6 | 8 | 10 |
|---|---|---|---|---|---|---|
| OLD (44 applied) | 28 | **732** | 0 | 0 | 0 | 0 |
| **NEW (300 applied)** | 21 | 1 | 40 | 125 | **265** | **308** |

### THE ARCHIVE, AND THE MECHANISM THAT KEEPS BOTH

`sw/testdata/inv1-archive/{mc1,mc2}/seeds/` — **760 byte-identical copies** of
the entries as they stood before the re-capture, with `SHA256SUMS`
(sha256 `6f79283222d169fdf1f7a8e599c403faacdd0d8d8801abb55c567d89a392355a`) and
a manifest.  **Deliberately OUTSIDE `tests/v30/fuzz_bank/`**: `check_fuzz_bank`
globs `*/seeds/*.json.gz` under that root, so an archive placed inside it would
have silently grown the 3,242-seed corpus — the same reasoning that kept the
originals from being moved in the first place.  (They are also in git history at
`64641a5644`; the copy exists so the guarantee does not depend on that.)

The entries themselves were **rewritten IN PLACE**, which is this entry's own
stated closure — *"a re-capture on the widened rig banks `hold_bits = 12`, and
the seed leaves this set by arithmetic… the seeds re-enter the gate without
anyone editing a list."*  Each carries a `recapture` block naming the bitstream,
the flash, the prior `chip_rows` sha256, the prior `banked_ts`, the prior
`replay_verdict` and the archive path.

`replay_verdict` was **recomputed and the movement REPORTED**, because leaving
it stale would have made `check_fuzz_bank` cry 700 spurious regressions and
recomputing it silently would have made that gate vacuous on these seeds:

| banked → re-captured | seeds |
|---|---|
| `FUNCTIONAL` → **`TIMING`** | **372** |
| `FUNCTIONAL` → `FUNCTIONAL` | 348 |
| `FUNCTIONAL` → **`KNOWN_ACCEPTED`** | **18** |
| `TIMING` → `TIMING` | 20 |
| `KNOWN_ACCEPTED` → `KNOWN_ACCEPTED` | 2 |
| **worse** | **0** |

### THE CLOSURE BARS (`ucore_provenance.md` §59.2, pre-registered) — ALL MET

| bar | result |
|---|---|
| every `hold=300` entry banks `hold_bits = 12` and `hold_applied = 300` | **760/760 MET** |
| `f46_invalidated` True anywhere in the bank | **0 MET** |
| the originals archived | **760 MET** |
| `timed_fuzz`'s `INVALIDATED` line | **gone, both engines** — the derivation self-healed |

### GATE STATUS — the second movement, and the sign flip

| gate | SM1 (INV-1 as opened) | **SM2 (re-captured)** |
|---|---|---|
| `timed_fuzz --core ucore` **REGISTERED** | 1,483/1,702 | **1,483/1,702 — UNCHANGED, to the seed** |
| `timed_fuzz --core sim` **REGISTERED** | 1,272/1,702 | **1,272/1,702 — UNCHANGED** |
| **EVT**, ucore | 170/248 (interim sub-gate) | **468 / 1,008 (46.4 %)** |
| **EVT**, sim | 144/248 | **363 / 1,008 (36.0 %)** |
| **COMBINED**, ucore | 1,653/1,950 | **1,951 / 2,710 (72.0 %)** |
| **COMBINED**, sim | 1,416/1,950 | **1,635 / 2,710 (60.3 %)** |
| the full 1,008-seed EVT column | **SUSPENDED** | **UN-SUSPENDED.  It is a gate again.** |

**The decomposition is the control**, and it is why the new number can be
trusted:

| sub-population | ucore | sim |
|---|---|---|
| the **248** never poisoned | **170/248** | **144/248** — *identical to SM1, seed for seed* |
| the **760** re-captured | **298/760** (was 22) | **219/760** (was 565) |
| total | **468/1,008** | **363/1,008** |

**THE SIGN FLIPPED.**  As banked, this column said the ucore lost to the model
by **517** seeds.  On captures taken under the directive the bank actually
records, **the ucore beats the model by 105.**  SM1 predicted the sign from the
un-poisoned 248 alone (a 26-seed margin) and the corrected full column
reproduces it and widens it.  §T.5's "547 ucore-only non-exact seeds" were the
rig, and are gone.

*The falsifier this entry registered* — *a capture in the 760 whose acknowledge
pattern is consistent with a hold longer than 255 clocks* — was **not** met by
any of the 760 old captures (732 of them show a single handler entry), and its
mirror image was demonstrated directly on the pin.  **INV-1 is closed as
diagnosed.**

---

## INV-2 — THE T12 fuzz-v2 CORPUS CAPTURE, AS A GATE

**Opened 2026-08-09.  Status: OPEN — archived by rename, re-capture in the same
sitting.**  The rig defect is FIXED in `sw/fuzz_campaign.py` at `c32b8cbb9d`
(amendment A-3, `fz2_corpus_prereg_2026-08-08.md` §13), committed before any
board contact of that sitting.

### WHAT

| | |
|---|---|
| the artifact | the **first fuzz-v2 corpus capture**, 3,840 seeds, taken 2026-08-09 on FLASH #12 in 10.8 minutes of board time |
| the banks | `sw/testdata/campaigns/fz2c/` (960 result lines, 552 retained captures) and `sw/testdata/campaigns/fz2e/` (2,880 lines, 374 captures) — **74 MB, 926 full per-clock capture files** |
| the scorings | `sw/testdata/fz2/fz2_bars.json`, `fz2_capture.json`, `fz2_c9.json`, `fz2_preflight.json`, `fz2_idle.json` |
| sha256, before the move | `results.jsonl` fz2c `f67b496c56a39707…`, fz2e `b95cb470c91a28aa…`; `fz2_bars.json` `e3fc9cfe5da0aa75…`; `fz2_capture.json` `01e0ed2192d23a54…`; `fz2_c9.json` `817566da12e86d24…` |

### WHY

Not because the rows are false.  **They are true silicon** and they are
retained.  What is false is what they can be scored AGAINST: every one of the
3,840 seeds was handed a terminating-NMI delay computed by a budget that left
**7 rows of tail slack at w0 and 1 at w3**, so on 1,048 seeds the terminator
fired, was intercepted, and the dump ran off the end of the 4,096-record
capture.  A capture whose termination is decided by the instrument's own
arithmetic error cannot measure a containment bar.  Stated as a property of the
artifact: **`(anchor + tail) / scale` over the 194 fully-observable completions
is PINNED at 461.1 against a reserve of 462.0** — the distribution is
right-censored at the budget, and no value above it exists in the data because
none could be recorded.

### WHICH RIG DEFECT

**O-2a**, named in §12.3 of the pre-registration and diagnosed in §13.2:
`ANCHOR_W0` was a post-RESET row number subtracted from a `CAP_ROWS` that counts
from record 0 (a 35-row coordinate error), `DUMP_W0` carried a 21-clock
*estimate* for an NMI entry that measures 53 minimum and 463 maximum, and the
NMI acceptance latency was in no term of the formula at all.  **FIXED** at
`c32b8cbb9d`: `ANCHOR_W0` 145→180, `DUMP_W0` 240→219, new measured term
`ENTRY_MAX` = 463, `TERM_MARGIN` and `TERM_FLOOR` unchanged.  The instrument
that diagnosed it, `sw/fz2_termcost.py`, reads only banked captures and
re-derives every number offline.

### WHAT REPLACES IT

A **re-capture of the same 3,840 seeds** — `SEED_LIST_SHA256`
`45d25f31a325c496…` is unchanged, so it is the same corpus, seed for seed —
against the **unchanged** bars C-1 … C-11.  Nothing gates on the archived
capture in the interim; it was never a ratchet (§8.2: *"a first registration is
not a ratchet"*), so no standing figure moves and none is suspended.

### THE ARCHIVE

**Renamed, never deleted, and nothing was rewritten:**

| from | to |
|---|---|
| `sw/testdata/campaigns/fz2c/` | `sw/testdata/campaigns/fz2c-INV2-archive/` |
| `sw/testdata/campaigns/fz2e/` | `sw/testdata/campaigns/fz2e-INV2-archive/` |
| `sw/testdata/fz2/fz2_{bars,capture,c9,preflight,idle}.json` | `sw/testdata/fz2/inv2-archive/` |

All 926 retained per-clock captures moved with their banks.  The precedent is
INV-1's (archive by rename, raw captures retained, nothing deleted) and the
w1evt-biased habit; the *disposition* is INV-1's, not the biased suite's,
because here the label is what is false.

**THE ARCHIVE IS LOAD-BEARING AND MUST NOT BE PRUNED.**  It is the only evidence
of the un-repaired rig, it is the population A-3's three constants were measured
on, and it is what makes the repair attributable: without it the improvement is
unverifiable and the before/after cannot be audited.  `sw/fz2_termcost.py` reads
the archive names first, by design.

### GATE STATUS

| figure | before | after |
|---|---|---|
| every standing gate in `standing_gates.md` | — | **UNMOVED.**  No standing gate reads `sw/testdata/campaigns/` |
| the fuzz-v2 bars C-1 … C-11 | 6 MET / 3 MISSED / 2 NOT SCOREABLE (§12.1) | **VOID pending the re-capture** — not restated, not carried forward |
| the census/enriched decompositions | 94.9 % / 72.08 % and 94.34 % / 69.72 % | **VOID pending the re-capture** |
| `SEEDS_SHA256` | `386c65fd641b84a1…` | `48a0f01176fd31b7…` (`TERM_CLOCKS` is derived from the constants) |
| `SEED_LIST_SHA256` | `45d25f31a325c496…` | **UNCHANGED** — the same 3,840 seeds |

### THE FALSIFIER, registered with the entry

If the re-capture's UNDISPOSITIONED count does **not** fall, the diagnosis is
wrong and O-2a is not a budget defect.  If the residue that survives is **not**
dominated by §13.5's stopped-CPU class (O-2d), the partition drawn off the
banked captures is wrong.  Either outcome is reported as registered.

---

## INV-3 — THE `rep_cl0` DERIVATION CELL, AS A GATE

**Opened 2026-08-17.**  Pre-registration `0dc40e51dc`, amendments
`bb37f154f2` (A-1) and `5fd01af2c0` (A-2); results
`docs/notes/rep_cl0_silicon_results_2026-08-17.md`.

### WHAT

`tests/v30/rep_cl0-INV3-archive/` — 24 socket captures (12 `F3A4` + 12 `F3A5`),
full per-clock rows, taken 2026-08-17 to ask silicon what `REP MOVSB` does at
`CX = 0x0100`.  **It has never gated anything and it never will.**

### WHY

**A-1 R-2, registered before the run, reads: *"THE SEED IS NEVER REROLLED ON A
CAPTURE-LENGTH FAILURE … A rerolled seed in this cell invalidates the cell."*
Eight seeds were rerolled** — one on `F3A4` (index 11), seven on `F3A5` — and
the emit log records each.

The reroll is not uniform, which is what makes it false rather than merely
untidy: **six of the seven `F3A5` quarantines are precisely the doubly-odd
images** (odd `SI` **and** odd `DI`), which split every word access into two
byte cycles and so exceed the 4,096-record ceiling.  Every surviving `F3A5`
case has at most one odd operand.  A whole alignment class was therefore
excluded **from inside `P-3`, the cell's own gating control** — and a control
with a systematically missing stratum is not a control.

⚠ **The direction of the bias runs OPPOSITE to the observation** (rerolling
selects for SHORT traces, and short is `H-SILICON`'s signature), and the four
`F3A4` `CX=256` cases carrying the headline are **first-choice, un-rerolled**
images.  **Both facts are recorded as reasoning and NEITHER is a waiver.**
R-2 invalidates on the artifact, not on the persuasiveness of the residue;
choosing the un-rerolled subset *after* seeing the result is the fitting this
register exists to prevent.

### WHICH RIG DEFECT

**NAMED, and NOT yet fixed at the time of filing.**  Two instrument paths, both
in `sw/emit_suite.py`:

1. **The ceiling.**  `EMIT_CAP = 2048`, `EMIT_CAP_RETRY = 4096`, and
   `EMIT_CAP = min(4096, EMIT_CAP * (1 + waits))` (`:197-198`, `:2548`).  A
   doubly-odd `F3A5` at these counts exceeds 4,096 and **has no larger retry to
   fall to**, so the case dies and the seed is rerolled.
2. **A second failure mode with NO retry path at all.**  *"only N register words
   before the done marker"* does not match the retry predicate, so it rerolls
   straight from 2,048 without ever trying 4,096.  This is the `F3A4` index-11
   reroll.

A-1 R-2 was written assuming a capture-length failure always ends in a
successful retry.  **That assumption is false, and the assumption is the
defect** — the reroll is `cmd_emit` behaving as designed on an error the
registration did not anticipate.

### WHAT REPLACES IT

**A RE-CAPTURE**, under its own pre-registration, after the ceiling is raised so
that no case in the cell can reroll.  Until that capture exists:

* **no figure in `rep_cl0_silicon_results_2026-08-17.md` may be quoted as a
  gate**, and
* the finding it points to — that silicon executes the loop where both engines
  skip it — **stands as an OBSERVATION with its instrument named, not as a
  certified result.**

The validation cell (A-2 §A-2.2, 72 disjoint-form cases) is **not** captured
until the re-capture certifies, and **no width rule may be quoted as validated**
until it is.

### THE ARCHIVE

**Renamed, never deleted, nothing rewritten:**

| from | to |
|---|---|
| `tests/v30/rep_cl0/` | `tests/v30/rep_cl0-INV3-archive/` |

The precedent is INV-2's (archive by rename; the invalid thing IS a directory,
so a rename can express it — unlike INV-1, where it was a selection inside a
shared directory).  All 24 per-clock captures moved with it, with the
`seeds.json` maps and `emit_log.txt` that **record the rerolls** and are the
only evidence of the un-repaired instrument.  **THE ARCHIVE IS LOAD-BEARING AND
MUST NOT BE PRUNED**: it is the before-column that makes the re-capture's repair
attributable.

### GATE STATUS

**No standing figure moves.**  The cell was new, gated nothing, and entered no
ratchet — the ladder is untouched and `P-6` was MET (`git diff --stat` over
`v0.1`/`v0.2`/`v0.3`/`v20suite` EMPTY, verified).  Nothing in
`docs/notes/standing_gates.md` changes.

⚠ **What does NOT change either: the REP `CL == 0` defect in both engines is
still measured, still reproducible offline, and still un-fixed.**  INV-3
invalidates a CAPTURE, not the offline finding — `sw/testdata/rep_cl0/`'s two
drivers reproduce the engine behaviour with no board in the loop.

### THE FALSIFIER, registered with the entry

The re-capture must complete the full 24-case cell with **ZERO rerolls** and
`emit_log.txt` carrying **no `reroll:` line**.  If it rerolls even once, the
ceiling fix is insufficient and the disposition is re-opened rather than
re-argued.  If the re-captured cell then reads anything other than
`H-ENGINE`, **this entry's WHY is wrong** and the bias analysis above must be
retracted rather than defended.

---

# SUPERSEDED POPULATIONS — **NOT** INVALIDATIONS

**Opened 2026-08-09.** This register was opened for artifacts that are FALSE.
The entries below are for artifacts that are TRUE and no longer USED. They are
filed here because they change what a gate measures and that must be findable in
one place — and they are filed under their own heading because filing a
retirement as an invalidation would say something about the data that is not so.

| | an INVALIDATION (INV-n) | a SUPERSESSION (SUP-n) |
|---|---|---|
| what is wrong with the capture | something — it was scored against a directive it never saw, or its label is false | **nothing** |
| the named rig defect | required | **NONE — and that field must read NONE** |
| the predicate | `timed_fuzz.f46_invalidated`, over the record | `bank_status.is_superseded`, over the manifest |
| the disposition | out of every gate set, permanently | out of the DEFAULT population; back with one flag |
| what it says | this measurement was not of what we thought | a better instrument exists |

**The two are independent.** A seed can be neither, either or both, and neither
predicate is computed from the other. `f46_invalidated` is **0 bank-wide** and
stays 0 — SUP-1 does not touch it and alleges nothing.

---

## SUP-1 — THE v1 FUZZ CORPUS, AS A REPLAYED POPULATION

**Opened 2026-08-09, branch `fuzz-v2-on-relanding`. Status: RETIRED BY STATUS.
No rig defect. Nothing moved, renamed or deleted.**

### WHAT

| | |
|---|---|
| the artifact | the **v1 fuzz bank** — four campaigns, **3,242 banked seeds**, captured 2026-07-28 |
| the cids | `mc1` **1,295** · `mc2` **1,294** · `t30-raw` **568** · `t30-brkem` **85** |
| where it is | `tests/v30/fuzz_bank/{mc1,mc2,t30-raw,t30-brkem}/` — **exactly where it has always been, byte for byte** |
| what changed in it | four `manifest.json` files gained `status`, `superseded_by`, `as_of_commit`, `superseded_ledger`, `superseded_note`. **No seed file, sig index, result shard or `chip_rows` was touched.** |
| the tree it was set on | `as_of_commit` `c07fbc0169ed31ca27b94be7a5759c085fb83d0d` |

### WHY — superseded, **not false**

The user directive of this campaign is *"I do not care about the old fuzz data,
discard it, move on"*, and the fuzz-v2 corpus was captured, scored and banked to
replace it. Until this entry the v1 seeds were still replayed **on every
`check_fuzz_bank` run** — 3,242 of the 3,865 seeds in the gate, for **+19.2 %
wall time and zero information about the population the project now develops
against** (`fz2_corpus_prereg_2026-08-08.md` §21.4).

**Nothing is alleged about the captures.** They are true silicon; they were taken
from the socket; they will remain true. Every figure ever quoted off them stays
true *of them*. What ended is their standing as the population a landing is
developed and scored against.

This also **RESOLVES C-11's third clause**, which §21.4 reported and did not
resolve. *"Standing bank ≤ 3,500"* was scored as `fz2c + fz2e` = **623** while
§2.1 justifies the number with *"every banked seed is replayed on every gate
run"* — a population of **3,865**, breaching the ceiling by 365.
**COORDINATOR RULING, 2026-08-09: §2.1's reading is correct** — gate wall time is
the cost the number exists to bound. The repair is not to shrink `fz2`; it is to
stop replaying a corpus that was discarded. The two readings now agree at **623**
and `fz2_w1.cmd_bars` computes **the §2.1 one** (`replayed`), recording both.

### WHICH RIG DEFECT

# **NONE.**

No rig defect is alleged, none is diagnosed, and none is fixed by this entry.
No capture is false, no directive was mis-applied, no label is wrong.
`f46_invalidated` is **0** across the whole bank before and after. If this entry
is ever read as evidence that something was wrong with the v1 captures, it is
being read wrongly.

### WHAT REPLACES IT

The **fuzz-v2 corpus**, `fz2c` **480** + `fz2e` **143** = **623** banked seeds
(`fz2_corpus_prereg_2026-08-08.md` §21), promoted 2026-08-09 and replaying
**623 stable / 0 improved / 0 worse / 0 GEN-DRIFT / 0 errors**.

It is a better instrument on the axes this campaign cares about, and it is
**measured, not asserted** (census over the banked records):

| axis | v1, 3,242 seeds | v2, 623 seeds |
|---|---|---|
| per-access WAIT VECTOR (task #38) | **0** — the axis did not exist | **169** `wvec-uni` (+454 flat) |
| `PSW.TF` / single-step | **0** seeds carry `has_tf` | **22** |
| census promotion rule | divergence-driven quota (a selection artefact) | **480 by the FROZEN rule**, `census_exact` true — population rates are population rates |
| `evt` pin events | 1,165 armed (760 at hold 300) | 295 armed (108 at hold 300) |
| 8080 / BRKEM | 50 seeds with BRKEM positions + the 85-seed `t30-brkem` bank | **0** — every v2 seed is `no8080` |

### THE ARCHIVE — there is none, because **nothing moved**

**This is the whole point of the mechanism.** INV-1's own words:

> a list can drift away from what it describes and a rename can be undone
> silently; a predicate computed from the artifact cannot.

INV-1 archived by rename because its captures had to leave a gate set
permanently. A supersession does not: the population must stay **reachable on
request**, so a historical figure can be re-derived. So it is a **STATUS**, in
each campaign's own `manifest.json`, and the population is a predicate over the
manifests — `sw/bank_status.py`, a leaf module with no engine behind it:

```
python3 sw/bank_status.py                       # the replayed population
python3 sw/bank_status.py --include-superseded  # everything banked
```

A bank with **no** `status` key is `ACTIVE`, so no existing bank and no future
promotion has to be edited to keep meaning what it means. Every consumer that
excludes a bank **says so on its own line**; a consumer that dropped 3,242 seeds
silently would defeat the mechanism.

### GATE STATUS — every figure that moved, and every one that did not

| gate | before | after |
|---|---|---|
| `check_fuzz_bank` **population** | **3,865** seeds | **623** seeds |
| `check_fuzz_bank` **verdict** | **FAIL** — see §"THE BEFORE WAS RED" below | **PASS** — `623 banked seeds \| stable 623 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0` |
| `check_fuzz_bank` **wall time** | **1,580 s** (26 m 20 s) | **266 s** (4 m 26 s) — **−83.2 %** |
| `check_fuzz_bank --include-superseded` | — | **3,865 seeds selected — the pre-SUP-1 population exactly, path for path** (proved: `bank_status.seed_paths(include_superseded=True)` is set- and order-identical to the historical `BANK.glob("*/seeds/*.json.gz")`). It still FAILS, for the reason below, which is not SUP-1's |
| `timed_fuzz --core ucore --evt-replay` | REGISTERED 1,564/1,702 · EVT 937/1,008 · COMBINED 2,501/2,710 | **NOT MEASURABLE ON THIS BRANCH, with or without the flag** — see §"THE BEFORE WAS RED". Without it: 0 seeds. With it: 3,242 seeds, **all `GEN_DRIFT`** (measured: `--bank mc1 --limit 40` → `GEN_DRIFT=40  SCORED 0`) |
| `timed_fuzz --core sim --evt-replay` | REGISTERED 1,343/1,702 · EVT 802/1,008 · COMBINED 2,145/2,710 | **NOT MEASURABLE ON THIS BRANCH**, same cause, same evidence |
| `timed_fuzz --seeddir …/b2-tranche/seeds` | 182/188 (ucore), 161/188 (sim) | **UNTOUCHED** — `--seeddir` does not read the bank |
| FZ2 bars | 8/11 MET, NOT MET C-1, C-3, C-6 | **8/11 MET, NOT MET C-1, C-3, C-6.** Only C-11's `measured` moved (gains `replayed` 623, `all_banked_incl_superseded` 3,865, `superseded_cids`); no other bar's `measured` changed by one character |
| C-11, §4.3's reading (`fz2c + fz2e`) | 623 ≤ 3,500 **MET** | 623 ≤ 3,500 **MET** |
| C-11, §2.1's reading (replayed) | 3,865 ≤ 3,500 **BREACHED by 365** | **623 ≤ 3,500 MET** — and this is the one the scorer computes |
| `f46_invalidated`, bank-wide | **0** | **0** |
| every other standing gate | — | **UNMOVED.** No other gate reads the bank glob |

### THE BEFORE WAS RED, AND THE WHOLE RED WAS THE v1 CORPUS

**This was not in the brief and it is not what anyone expected. It is measured,
and it corrects the framing of the finding this entry acts on.** §21.4 costed
the v1 corpus at *"+19.2 % wall time and zero information"*. The true cost was
higher: **on branch `fuzz-v2-on-relanding`, `check_fuzz_bank` over the 3,865-seed
population FAILS**, and every failing seed is a v1 seed —

```
check_fuzz_bank: FAIL | 3865 banked seeds | stable 623 improved 0 worse 0
                      | gen_drift 3157 regen_err 85 | float-floor 0
                      | new-sig TIMING 0                        (1,580 s)
```

`mc1` **1,295** + `mc2` **1,294** + `t30-raw` **568** = **3,157 GEN-DRIFT**, and
all **85** `t30-brkem` seeds raise
`brkem_high: refused -- fuzz-v2 eliminates 8080 entry unconditionally (plan D9)`.
The **623** fz2 seeds are the only stable ones in the tree.

**THE CAUSE IS fuzz-v2's OWN PLAN D9, AND IT LANDED LONG BEFORE THIS ENTRY**
(`sw/fuzz_campaign.py`, commits `e45772e4e0` … `b155b6166b`): the `0F` scrub is
now **unconditional** at all three build sites, so every v1 image regenerates to
a different sha256; and `brkem_high` is **refused outright**, so the BRKEM bank
cannot be composed at all. Both are deliberate, registered and correct. Their
side effect is that **the v1 corpus stopped being replayable on this branch the
day D9 landed** — GEN-DRIFT is the gate's designed report for exactly this: *a
generator change silently moved the seed*.

Three consequences, stated so no one has to rediscover them:

1. **SUP-1 takes `check_fuzz_bank` from FAIL to PASS.** That is a real
   improvement and it must not be quoted as a repair — nothing was repaired.
   A corpus the generator no longer builds stopped being replayed.
2. **`timed_fuzz`'s two v1 fuzz-bank ratchets were already unmeasurable on this
   branch**, before SUP-1 and independently of it: `--include-superseded`
   selects all 3,242 and every one categorises `GEN_DRIFT` (`--bank mc1
   --limit 40` → `GEN_DRIFT=40  SCORED 0`). Honouring status in
   `timed_fuzz.seeds_of` therefore costs those ratchets **nothing D9 had not
   already taken**. They are re-derivable only on a tree whose generator
   predates fuzz-v2 — merge-base `7e949925b7`, or `master`.
3. **"Reachable on request" means the SEEDS, not the REPLAY.** The flag returns
   the population path for path; it cannot return a replay the generator can no
   longer produce. This entry claims the first and does not claim the second.

### WHAT IS LOST — stated plainly, because retirement has a cost

1. **The 532 `OPEN_BUS` seeds.** The v1 bank is 3,242 seeds of which 2,710 are
   scoreable and **532 are `OPEN_BUS`-excused**. That excused population was a
   standing reservoir — every landing that shrank it did so by moving seeds out
   of it, and several were quoted that way (SM3 sitting 25's *"plus 51
   `OPEN_BUS`"*). Off the default population, that reservoir stops being watched.
2. **The 8080 / BRKEM class, and the `t30-brkem` bank entirely.** 85 banked seeds
   and 50 seeds carrying BRKEM positions. **The v2 corpus has ZERO of them** —
   every fz2 seed is `no8080`. This class is DEFERRED BY USER DECISION
   (2026-08-05) and structurally unreachable in the ucore, so nothing was gating
   on it; but the coverage is gone, not merely idle, and a future 8080 campaign
   must re-capture rather than re-read.
3. **INV-1's 760 re-captured EVT seeds.** All 760 live in `mc1`/`mc2`. They cost
   a board session, a 12-bit `evt_hold` in RTL, in flash and on the pin, and a
   closure with its own bars. They remain byte-identical and reachable; they are
   no longer replayed. **INV-1's own tooling (`sw/inv1_recapture.py`) reads them
   explicitly and is unaffected** — its predicate is `f46_invalidated`, not
   status, and it passes `include_superseded=True` deliberately.
4. **Re-scoring any pre-v2 landing on the population it was developed against —
   and this one was ALREADY lost, by D9, not by SUP-1.** Every ucore landing
   from H1 through the take-clock leg was measured on these 3,242 seeds, seed
   for seed, and their *"N gained, ZERO lost over all 3,242"* claims are
   statements about this corpus. **On this branch those claims cannot be
   re-derived at all**: the seeds are reachable with the flag, but the generator
   that built their images is gone, so every one of them scores `GEN_DRIFT`.
   Reproducing them needs a tree whose `sw/fuzz_campaign.py` predates fuzz-v2
   (merge-base `7e949925b7` or `master`) — a checkout, not a flag. **That is the
   standing hazard of this entry, and `standing_gates.md` says it in each row.**
5. **The wait-class mix.** v1 carries 1,765 `wrand` and 1,477 fixed-wait seeds
   across w0/w1/w2/w3; v2's 623 are 454 flat + 169 `wvec-uni`. The v2 corpus is
   better on the per-access axis and **thinner in absolute seed count by 5.2×**.
   Fewer seeds see fewer things; this is a real reduction in incidental coverage
   that no axis table shows.

### THE FALSIFIER, registered with the entry

The claim is **"nothing moved, status only"**, and the falsifier is about the
POPULATION, not about any figure's value — because D9 already took the replay
and this entry must not be credited with something it did not do.

**FALSIFIED IF** `bank_status.seed_paths(include_superseded=True)` is ever not
set- and order-identical to the historical `tests/v30/fuzz_bank/*/seeds/*.json.gz`
glob, or if `python3 sw/bank_status.py --include-superseded` prints anything but
**3865**, or if any file under `tests/v30/fuzz_bank/*/seeds/` differs by one byte
from its pre-SUP-1 content. All three were checked when this entry was written;
the first is an equality test anyone can re-run in a second.

**ALSO FALSIFIED IF** any consumer of that glob is found excluding superseded
seeds **without printing the exclusion**. A silently smaller denominator is how
a gate goes vacuous without anyone noticing, which is why `check_fuzz_bank`
returns **1**, not 0, if every bank in the tree is ever retired at once.

If any consumer of `tests/v30/fuzz_bank/*/seeds/*.json.gz` is found excluding
superseded seeds **without printing the exclusion**, the mechanism is defective
regardless of the arithmetic: a silently smaller denominator is how a gate goes
vacuous without anyone noticing.

---

# EXCLUDED SEEDS — **NOT** INVALIDATIONS AND **NOT** SUPERSESSIONS

**Opened 2026-08-09.** A third class, opened because filing it as either of the
two above would say something untrue. An excluded seed's capture is **true
silicon** (so it is not an INV) and **no better instrument replaced it** (so it
is not a SUP). It is a true capture **of a feature this project has deferred**,
and therefore not a member of the population any rate is computed over.

| | INVALIDATION (INV-n) | SUPERSESSION (SUP-n) | **EXCLUSION (EXC-n)** |
|---|---|---|---|
| what is wrong with the capture | something | nothing | **nothing** |
| named rig defect | required | NONE | **NONE** |
| the predicate | `timed_fuzz.f46_invalidated` | `bank_status.is_superseded` | **`bank_status.excluded_of`, over the manifest** |
| granularity | per capture | per campaign | **per seed** |
| the disposition | out of every gate set, permanently | out of the DEFAULT replayed population; back with `--include-superseded` | **out of every scored rate's NUMERATOR AND DENOMINATOR, and out of the replayed bank; back with `--include-excluded`** |
| what it says | this measurement was not of what we thought | a better instrument exists | **this is a true measurement of something we are not scoring** |

## EXC-1 — THE TWO RUNTIME 8080 ENTRIES IN `fz2e`

**Opened 2026-08-09, branch `fuzz-v2-on-relanding`. Status: EXCLUDED BY STATUS.
No rig defect. Nothing moved, renamed or deleted.**

| | |
|---|---|
| the seeds | **`fz2e/509069`** (soup, `FUNCTIONAL`, `sig 8cb79b8ba571898b`, 1,126 divergent rows) and **`fz2e/521059`** (raw, `KNOWN_ACCEPTED/open_bus`, 2,814 divergent rows) |
| the files | `tests/v30/fuzz_bank/fz2e/seeds/soup_509069_e6e5f2c9b2ec.json.gz` and `raw_521059_17de21d60cf3.json.gz` — **exactly where they have always been, byte for byte** |
| what changed | `tests/v30/fuzz_bank/fz2e/manifest.json` gained an `excluded_seeds` list. **No seed file, sig index, result shard, `chip_rows` or `results.jsonl` line was touched.** |
| the argument | `fz2_corpus_prereg_2026-08-08.md` **§31** (AMENDMENT A-12), the coordinator's ruling on §29.7 |
| the tree it was set on | `as_of_commit` `20816b9462` |

### WHY

Both seeds entered **8080 mode at RUNTIME** — a `MEMW` into the code region
manufactured a `0F xx` pair after the compose-time scrub had run (§29.1), and
`fuzz_campaign._ps3_8080` detected it on both. **8080/BRKEM is DEFERRED BY USER
DECISION 2026-08-05**, *not to be tested or considered until a later campaign*.
A capture in which the part entered a deferred mode is evidence about neither
side of the ledger: it is not a success and it is not a failure, **it is not a
member**. Scoring one — in a numerator, in a denominator, or in a regression
bank that fails a future landing on a deferred feature's divergence — is what
this entry stops.

### WHICH RIG DEFECT

# **NONE.**

The captures are true silicon, taken from the socket, and they stay true. Every
row in them remains readable and re-scoreable; `--include-excluded` replays them
in full.

### THE FALSIFIER

**FALSIFIED IF** a `ps3_8080` seed is ever found inside a scored rate or inside
the replayed bank while this entry stands — which is exactly what C-3's **R3′b**
computes, in both directions, on every `fz2_w1 bars` run: every `ps3_8080` seed
with a banked file must be named in `excluded_seeds`, **and** no banked file may
be excluded that the campaign results do not show `ps3_8080` for. A list that
drifts away from the artifact it describes fails, loudly.

**ALSO FALSIFIED IF** any consumer drops an excluded seed **without printing the
exclusion**.

### ADDENDUM, 2026-08-10 — THE ERA THIS ENTRY IS ABOUT, AND WHAT A-13 CHANGES

**Nothing above is retracted or rewritten.** This addendum states the era the
entry was always about, because a re-capture has since made it matter.

The two seeds are excluded on the strength of **their banked captures** —
`tests/v30/fuzz_bank/fz2e/seeds/{soup_509069_e6e5f2c9b2ec,raw_521059_17de21d60cf3}.json.gz`,
promoted 2026-08-09T18:09–18:10Z from the **F12-era** corpus, and byte-identical
since. Recomputing `fuzz_campaign._ps3_8080` over the `chip_rows` those two files
carry fires on **both**, and over **all 623 banked captures it fires on those two
and nothing else** (`prereg §34.3`). **EXC-1 is exactly right about the bank,
seed for seed.**

`0ac4c2a83a` then re-captured the corpus on FLASH #13 **without re-promoting the
bank**, and on that capture `fz2e/521059` **does not** enter 8080 mode while
`fz2c/408029` and `fz2e/523042` do (prereg §33). All three are `raw` tier with
identical `image_sha256` across the eras: **a runtime 8080 entry is a property of
the capture, not of the seed**, on a tier whose socket leg is not reproducible
(`0ac4c2a83a` bar C1). **This is not a defect in these captures and not a
retraction of this entry.**

**AMENDMENT A-13** (`fz2_corpus_prereg_2026-08-08.md` §34) therefore re-registers
C-3's **R3′b** to justify a *bank* exclusion against **the banked capture's own
rows, recomputed**, rather than against a campaign result line that may now be a
different capture. The falsifier below is unchanged in force and stronger in
form: it no longer trusts a stored column in another file, it decompresses every
banked seed and recomputes the predicate over the exact rows `check_fuzz_bank`
replays.

---

## EXC-2 — THE THREE RUNTIME 8080 ENTRIES IN THE **FLASH #13** CORPUS

**Opened 2026-08-10, branch `fuzz-v2-on-relanding`. Status: EXCLUDED BY STATUS.
No rig defect. Nothing moved, renamed or deleted.**

| | |
|---|---|
| the seeds | **`fz2c/408029`** (raw, stratum 8, `KNOWN_ACCEPTED/open_bus`, `sig dcc39a8e7bf43c1f`, 3,074 divergent rows), **`fz2e/509069`** (soup, stratum 21, `FUNCTIONAL/func:R@94`, `sig 8cb79b8ba571898b`, 1,126 rows — **also EXC-1**, and identical leaf for leaf across the re-capture) and **`fz2e/523042`** (raw, stratum 35, `KNOWN_ACCEPTED/open_bus`, `sig 626ef279e6b4d248`, 2,789 rows) |
| the artifact | `sw/testdata/campaigns/{fz2c,fz2e}/results.jsonl`, the **FLASH #13** re-capture of `0ac4c2a83a` (2026-08-10T00:51:09–01:02:21Z, 3,840 seeds, 0 halts) |
| what changed | **NOTHING IN ANY MANIFEST.** The exclusion is by arithmetic: `fz2_w1.py bars` filters a `ps3_8080` line out of its tier's numerator **and** denominator and prints the count (C-1 `excluded_ps3_8080`: `census/soup` 0 · `census/raw` 1 · `enriched/soup` 1 · `enriched/raw` 1, total **3**) |
| the argument | `fz2_corpus_prereg_2026-08-08.md` **§31** (A-12, what *discarded* means) and **§34** (A-13, which artifact justifies which half) |
| the tree it was set on | `as_of_commit` `db80e00596` |

### WHY

Same mechanism as EXC-1: a `MEMW` into the code region manufactured a `0F xx`
pair after the compose-time scrub had run, and the part entered 8080 mode at
runtime. **8080/BRKEM is DEFERRED BY USER DECISION 2026-08-05.** A capture in
which the part entered a deferred mode is not a member of the scored population.

### WHY NO MANIFEST RECORD IS WRITTEN — AND WHY WRITING ONE WOULD BE WRONG

**`fz2c/408029` and `fz2e/523042` have no file under
`tests/v30/fuzz_bank/<cid>/seeds/`.** The bank was promoted from the F12-era
corpus, in which neither seed diverged at all (`SUCCESS`). An `excluded_seeds`
record for a file that is not in the bank is itself a **failure** of C-3's R3′b
(*"excluded record names a file that is not in the bank"*), and it would be a
record about nothing: an exclusion is a statement about a replayed capture, and
there is no replayed capture to make it about.

`fz2e/509069` **is** banked, and its record already exists — **EXC-1's**. It is
not duplicated here.

### WHICH RIG DEFECT

# **NONE.**

The captures are true silicon, taken from the socket on FLASH #13, and they stay
true. They are retained in full in `sw/testdata/campaigns/{fz2c,fz2e}/captures/`.

### WHAT THIS ENTRY IS FOR

**A future promotion.** The bank was deliberately **not** re-promoted from this
corpus (prereg §34.5, with the numbers that move: the replayed population would
go **621 → 622**, `fz2e` banking 144 rather than 143). If it ever is, these
seeds' captures become banked files, and each one must then carry an
`excluded_seeds` record with a reason — which R3′b will demand, loudly, in its
A-13 form.

### THE FALSIFIER

**FALSIFIED IF** a `ps3_8080` line in the current corpus is ever found inside a
scored rate's numerator or denominator — which C-3's **R3′a** recomputes from
`sel_all` a second way on every `bars` run — or inside the replayed bank without
an `excluded_seeds` record, which **R3′b** recomputes off the banked rows
themselves.

**ALSO FALSIFIED IF** the exclusion is ever dropped **without being printed**
(R3′c).

# ERRATA AGAINST DERIVED COLUMNS — **NOT** INVALIDATIONS, **NOT** SUPERSESSIONS, **NOT** EXCLUSIONS

**Opened 2026-08-11.** A fourth register, opened for the same reason the third
was: filing this as any of the other three would say something untrue.

The three registers above are all about **CAPTURES** — data the rig produced.
This one is about a **DERIVED COLUMN**: something the tree *computes* from a
capture and stores beside it. A derived column can be wrong while every capture
it was computed from is perfectly true, and when it is, none of the three
dispositions applies — there is nothing to discard (INV), nothing to retire
(SUP) and nothing to drop from a rate (EXC). What there is, is **a wrong number
that must be recomputed with every movement reported.**

| | INVALIDATION (INV-n) | SUPERSESSION (SUP-n) | EXCLUSION (EXC-n) | **ERRATUM (ERR-n)** |
|---|---|---|---|---|
| what is wrong with the **capture** | something | nothing | nothing | **nothing** |
| what is wrong with the **derived column** | — | — | — | **it was computed by an instrument since found defective** |
| named **rig** defect | required | NONE | NONE | **NONE — and that field must read NONE** |
| named **instrument** defect | — | — | — | **required, with its fix commit** |
| granularity | per capture | per campaign | per seed | **per derived column, bank-wide** |
| the disposition | out of every gate set, permanently | out of the DEFAULT population; back with `--include-superseded` | out of every scored rate's numerator AND denominator; back with `--include-excluded` | **RECOMPUTED IN PLACE by the corrected instrument; nothing leaves any population** |
| how the gate returns green | re-capture | not applicable | not applicable | **by arithmetic — banker and checker compute the same corrected function — with NO list edited and NO seed excused** |
| what it says | this measurement was not of what we thought | a better instrument exists | this is a true measurement of something we are not scoring | **the measurement is true; the label we computed beside it was wrong** |

**AN `ERR-n` IS NOT A LICENCE TO EDIT DATA THAT DISAGREES WITH A GATE.** Its
preconditions are strict, all of them must be met, and each must be stated in
the entry:

1. the column is **DERIVED** — computed by this tree, never measured by the rig;
2. the **instrument defect is named and already fixed**, in its own commit;
3. the movement is **fully attributed BEFORE the rewrite**, seed by seed, in a
   document committed before it;
4. the originals are **archived byte-identical before a byte is touched**;
5. every rewritten entry is **PRINTED** and carries a provenance block naming
   what it replaced;
6. the untouchable fields are **proved untouched mechanically**, not asserted.

If any of those is missing, the honest disposition is a RED gate, not an ERR-n.
`cfb_tier_prereg_2026-08-11.md` §R.6 is the worked example of choosing the RED:
the same 90 seeds were left failing for a day rather than rewritten behind an
instrument fix that had no pre-registration of its own.

---

## ERR-1 — THE BANKED `replay_verdict` COLUMN OF THE 621-SEED fuzz-v2 BANK

**Opened AND CLOSED 2026-08-11, branch `fuzz-v2-on-relanding`, by
re-derivation. No rig defect. Nothing moved, renamed or deleted.**

### WHAT

| | |
|---|---|
| the artifact | the **derived replay columns** of the fuzz-v2 bank — `replay_verdict`, `replay_sig`, `replay_sub` on each entry, plus the **replay** contribution to `tests/v30/fuzz_bank/sig_ledger.json` |
| the population | `fz2c` 480 + `fz2e` 143 = 623 banked files, **− 2 EXC-1 = 621 replayed** (296 `soup` + 325 `raw`) |
| where it is | `tests/v30/fuzz_bank/{fz2c,fz2e}/seeds/*.json.gz` — **exactly where it has always been** |
| what changed in it | **three fields per entry** plus a new `rederive` provenance block, and the ledger's replay-sig keys. **No `chip_rows`, `chip_arch`, `image_sha256`, discovery `verdict`/`sub`/`sig`, `manifest.json`, sig index or result shard was touched** — proved mechanically, see THE MECHANICS |
| the tree it was set on | `921e756534` |
| the commits | prereg `537c6697c5` · archive `77ecf565d9` · tool `32fd811ed7` · rewrite `a54cc27454` |

### WHY — the column, not the capture

`sw/fuzz_bank.py:261` (`_write_bank`) computes the banked `replay_verdict` by
calling **`check_fuzz_bank.replay_classify` itself**. Until `09ec85e4bb` that
call site built `fc.Ctx(tier=entry["tier"])` with the banked config literal
`"soup"`/`"raw"`, while `Ctx.tier`'s declared domain is `'A'`/`'B'` — so every
tier branch in the classifier was silently False, **the arch-dump comparison
among them**. The banked column IS that defect's output.

Because the **same defective function was both the banker and the checker**,
`check_fuzz_bank` read `stable 621 / worse 0` for as long as the defect stood:
the round-trip compared the defect against itself. That green was a statement
about the determinism of an instrument, not about the bank
(`cfb_tier_prereg_2026-08-11.md` §2).

**Nothing is alleged about any capture.** `chip_rows` are true silicon, taken
from the socket, and they stay true — measured, not assumed: `gen_drift 0` and
`regen_err 0` on the full 621 in both the RED run and the green one, every image
still regenerating to its banked `sha256`, and the live bank's `chip_rows`
hashing **identical to the archive** after the rewrite. What was wrong was a
**label this tree computed and stored beside them.**

### WHICH RIG DEFECT

# **NONE.**

No rig defect is alleged, none is diagnosed, and none is fixed by this entry.
No capture is false, no directive was mis-applied, no board was touched, no
bitstream is implicated. **The defect is an INSTRUMENT defect and it is named**:
`check_fuzz_bank.replay_classify`'s tier-domain mismatch, **FIXED at
`09ec85e4bb`** by `fuzz_campaign.ctx_tier`, the one home of the mapping, which
**raises** outside its domain. Its own falsifier — 9 board-free checks, proved
non-vacuous — is `sw/test_fuzz_classify._tier_domain_falsifier()`.

### WHAT REPLACES IT

The same column, recomputed by the corrected instrument:
**`python3 sw/cfb_rederive.py --apply`**. Not a re-capture, not a re-bank, not a
re-promotion — the identical `(chip, sim)` row pairs read by a classifier
finally inside its own domain.

### THE ARCHIVE

`sw/testdata/cfb-tier-archive/{fz2c,fz2e}/seeds/` — **621 byte-identical
copies** of the entries as they stood at `921e756534`, plus a byte-identical
`sig_ledger.json`, `SHA256SUMS` (622 files; sha256 of `SHA256SUMS` itself
`4c2162cd6f2a6785ca722b01211696859a55580d75bfe9a69de635a5e15075ac`) and a
manifest, committed at `77ecf565d9` **before a byte of the bank was written**.

**Deliberately OUTSIDE `tests/v30/fuzz_bank/`**, for INV-1's own reason:
`bank_status.seed_paths()` globs `*/seeds/*.json.gz` under that root, so an
archive placed inside it would have silently grown the replayed corpus. (The
originals are also in git history at `921e756534`; the copy exists so the
guarantee does not depend on that.)

### THE MECHANICS — how "untouched" is proved rather than asserted

`sw/cfb_rederive.py` may write **four keys and no others**
(`replay_verdict`, `replay_sig`, `replay_sub`, `rederive`). For every entry it
hashes the canonical JSON of **every other key**, before and after, and
**aborts the whole run on a single mismatch** — `621/621 identical`. A
GEN-DRIFT is a STOP, not a repair. A negative ledger count is a STOP. `--limit`
is refused with `--apply`, because a partial rewrite is a truncated bank.

An **independent check that does not use the tool's own hash function**
compared the live bank against the archive key by key: **621/621 identical, 0
differing**, and `chip_rows` alone hash to
`5b93d459a9d21425fa9bc7386e705b732ddf8d163cce1d5e2be794b9c5a5b395` on **both**.

**Printed, never silent**: one line per entry (moved or not), one line per
ledger key added or removed. Each entry now carries a `rederive` block naming
its prior `replay_verdict`/`replay_sig`/`replay_sub`, its prior `banked_ts`, the
fix commit and the archive path — **faithful on 621/621 against the archive** —
so the movement stays derivable from the artifact, not only from a document.

### GATE STATUS — the movement, reported

| | RED (`921e756534`, mapped classifier vs defective column) | **GREEN (`a54cc27454`, re-derived)** |
|---|---|---|
| `check_fuzz_bank` | `FAIL \| 621 \| stable 531 improved 0 worse 90` | **`PASS \| 621 \| stable 621 improved 0 worse 0`** |
| `gen_drift` / `regen_err` | 0 / 0 | **0 / 0** |
| `float-floor` | 35 | **0** |
| `new-sig TIMING` | 148 | **0** |

**THE 90 ARE NOT ERASED BY THE GREEN.** They are, and stay, a finding about the
bank's derived column, itemized seed by seed in
`cfb_tier_prereg_2026-08-11.md` §R.2 and recorded in each entry's own
`rederive` block: **55 `soup`** where `done_mismatch` came alive
(`fuzz_classify.py:586`; 33 `TIMING`→`FUNCTIONAL`, 22
`KNOWN_ACCEPTED`→`FUNCTIONAL`) and **35 `raw`** where tier B's fixed 4,000-row
window came alive (`:562`; `SUCCESS` → 25 `TIMING` + 10 `KNOWN_ACCEPTED`, which
is `float-floor 35` seed for seed). **Nothing about the RTL, the model, the TB
binary or the silicon moved in either direction.**

Both registered clauses were scored on a **full dry run before `--apply`** and
again on the applied record:

* the **90 movers land EXACTLY on §R.2's committed after-column** — mover set
  equal seed for seed, **0 extra and 0 missing**, both mechanism splits exact —
  and, cross-checked independently against the RED run's own 90 `WORSE` lines,
  **90/90 agree on verdict AND sub**;
* the **531 non-movers' verdicts are byte-identical, 0 moved**, and their subs
  byte-identical on **521**, the 10 exceptions being exactly the sub-only class
  §R.5 measured and this sitting's §P-4 registered **in advance**.

The ledger moved **12,303 → 12,384** signatures (**+354, −273**), every key
printed, no count negative — the arithmetic registered at §P-6 before the run.

### WHAT IS **NOT** CLOSED BY THIS ENTRY

**The SUPERSEDED v1 banks still carry the defective column.** `mc1` · `mc2` ·
`t30-raw` · `t30-brkem` — **3,242 seeds** — were banked through the same
defective call site and are **NOT re-derived**, because on this branch they
**cannot** be: plan D9 makes the `0F` scrub unconditional, so every v1 image
regenerates to a different `sha256` and `replay_classify` STOPs at GEN-DRIFT
before it classifies (`3,157 GEN-DRIFT + 85 refused, 0 scored`). Re-deriving
them needs a checkout of a pre-fuzz-v2 generator. **Their `replay_verdict` is
the defective instrument's output and must not be quoted as anything else**;
`--include-superseded` still selects them and still fails, for D9's reason.

### THE FALSIFIER

**FALSIFIED IF** `check_fuzz_bank` and `cfb_rederive` ever disagree on a banked
seed's `replay_verdict` on an unchanged tree — that is the round-trip this
entry restored, and it is checked on every gate run by construction, because
the two call the same `replay_classify`.

**ALSO FALSIFIED IF** any live banked entry's non-mutable fields ever differ
from `sw/testdata/cfb-tier-archive/`'s copy of it. The archive is the standing
control on the claim *"only the derived columns moved"*, and the comparison is
four lines of Python over 621 files.

**ALSO FALSIFIED IF** a future sitting makes this gate green by editing a list,
excusing a seed, or narrowing the population. This entry's green came from
arithmetic; anything that comes from a list is a different thing wearing its
name.

---

---

# RETIRED INSTRUMENTS — **NOT** INVALIDATIONS, **NOT** SUPERSESSIONS, **NOT** EXCLUSIONS, **NOT** ERRATA

**Opened 2026-09-19 (WAVE 20).** The first four registers are about **DATA** —
a capture that is false (`INV-n`), a population that is true and no longer used
(`SUP-n`), a seed dropped from a rate (`EXC-n`), a derived column this tree
computed wrongly (`ERR-n`). **`RET-n` is the only one about an INSTRUMENT**: a
piece of this repo that MEASURES, deleted from the tree, taking its gates with
it.

Filing an instrument retirement as a supersession would say the population
moved, which it did not. Filing it as an invalidation would say the instrument
was wrong, which — on the day it went — it was not. So it gets its own heading,
and it carries a field none of the others has:

| field | meaning |
|---|---|
| **WHAT WENT** | the artifact, by path, with its size, measured |
| **WHY** | why it stopped earning its maintenance — as a property of the tree |
| **WHICH RIG DEFECT** | **NONE** must be the answer, or this is an `INV-n` |
| **EVERY GATE THAT DIED** | ⚠ **the load-bearing field.** Each gate by command, with its LAST REGISTERED FIGURE and whether that figure was GREEN when the instrument went. A retirement that does not enumerate its casualties is a silent gate death, which is this repo's oldest failure mode |
| **WHAT REPLACED IT** | per gate: a substitute, or **nothing** — and "nothing" must be written |
| **HOW TO RECOVER IT** | the exact commands. `git rm` keeps history; **nothing is destroyed** and the entry must say so |
| **THE FALSIFIER** | as everywhere else |

---

## RET-1 — THE C++ REFERENCE MODEL `sim/`

**Retired 2026-09-19, branch `master`, WAVE 20. No rig defect. Nothing was
destroyed — `git rm` keeps every byte in history, and the recovery command is
in this entry.**

### THE AUTHORITY

**USER DIRECTIVE, 2026-09-19, verbatim:**

> *"A lot of stale data and systems have accumulated over all these campaigns.
> Do an audit and determine what is no longer relevant and should be removed.
> **The old C model has not been maintained, remove it.**"*

### WHAT WENT — measured, not estimated

| | |
|---|---|
| the artifact | `sim/` — the C++20 microcode-driven V30 model (`ucsim`, closed 2026-08-01; `ucsim-t` timed mode, closed 2026-08-02) |
| tracked payload | **39 files, 491,759 bytes, 10,089 lines of C++ in 36 sources** (`git ls-files sim/`). The "1.7 MB" on disk was 33 gitignored `.o`/`.d` files plus the built binary |
| the binary every scorer ran | `sim/build/v30sim`, receipt `54cb8188bf7bff16…` (`sw/simbin.py --id`, taken before the removal) |
| reachable consumers in `sw/` | **134 modules — 37 that name the model directly, 97 that reach it by import.** Method and its limits in `docs/notes/staleness_audit_2026-09-19.md` §1 |
| **NOT retired with it** | `docs/V20BITS.TXT`, `docs/V20UC.TXT`, `docs/V20UCDIS.PAS`, `docs/pla3_outputs.txt` and every other normative source. They are the **ROM**, not the model, and `hdl/rtl/ucore/`'s whole table generator reads them |
| **ARCHIVED BY RENAME**, not deleted | `sim/README.md` → `docs/notes/ucsim_model_README_archived_2026-09-19.md`; `sim/coverage_report.txt` → `docs/notes/ucsim_coverage_report_archived_2026-09-19.txt` (**912 / 1028 micro-rows executed**, the only surviving statement of the ROM's coverage) |

### WHY — and the evidence is one commit

The model was the project's SPEC until 2026-08-04, when the correctness target
became **SILICON MATCH** and `CLAUDE.md` recorded *"matching the model is no
longer acceptable."* From that day the model was an instrument, not a
reference. What ended its usefulness is measurable and it is not an opinion:

1. **THE LAST SOURCE CHANGE IS `be4eb2c32f`, 2026-08-17** — 33 days before this
   entry. There were **75 commits to `sim/*.cpp` / `sim/*.h` in August 2026 and
   none since.**
2. **THE ucore TOOK A FUNCTIONAL FIX THE MODEL NEVER GOT.** `c59d205479`
   (2026-08-20, *"Fix REP termination before interrupt withdrawal"*) touches
   `hdl/rtl/ucore/v30u_eu_cond.svh` and **no file under `sim/`**. From that
   commit the two engines disagree on silicon-referenced behaviour, with the
   RTL right. **That commit is the measured end of `ulockstep`'s stated
   governance** — *"the model is the SPEC. A divergence reported here is a bug
   in the RTL"* — which was already formally superseded on 2026-08-04 and was
   still printed at the head of the file on the day it went.
3. **IT WAS NOT BROKEN, AND THAT IS NOT THE SAME THING.** Measured in this
   session, on the tree that carried it: `timed_gate --suite tests/v30/v0.1
   --forms all` = **169,000 / 169,000, row-diffs 0**; `ulockstep --golden all
   --cases 50` = **17,350 / 17,350 ALL LOCKSTEP**. **The model was GREEN on the
   day it was retired.** It is retired for being unmaintained and superseded as
   a reference, not for being wrong, and nothing in this entry says otherwise.

### WHICH RIG DEFECT

# **NONE.**

No rig defect is alleged, none is diagnosed, and none is fixed by this entry.
No capture is false. Every figure ever scored against the model stays true *of
the model*, and the receipt that identifies the bytes that produced it
(`54cb8188bf7bff16…`) is recorded here so those figures keep their artifact id.

### EVERY GATE THAT DIED — enumerated, with its last registered figure

⚠ **This is the field that makes the retirement honest.** Every row below was
run after the removal and its behaviour recorded (`§Y-2 DEMONSTRATED`).
**STATUS** is the gate's state at the moment it went, not its state today.

**A. STANDING-SET LEGS — gone, with nothing replacing them**

| gate | last registered figure | status when it went | replaced by |
|---|---|---|---|
| `python3 sw/simbin.py --disasm` (§A row 1, ⧉) | disasm byte-exact vs `V20UC.TXT`, **1,285 rows** | GREEN (run this session) | **NOTHING.** The ROM's disassembly has no second implementation in this tree |
| `python3 sw/ulockstep.py --golden all --cases 50` | **17,350 / 17,350 ALL LOCKSTEP** | **GREEN — measured this session at `975ecd0187` before the removal** | **NOTHING.** It was the only model-vs-RTL clock-for-clock comparator, and its governing premise had been superseded for six weeks |
| `python3 sw/timed_gate.py --suite … --forms all` | `v0.1` **169,000/169,000** · `-w1`/`-w3` 1,200 each · `EB` 200 · the four `evt` cells 200/1,200/200/1,200 · `w1evt-biased` 1,200 · the four HLT sweeps **283/283** | **GREEN on `v0.1` — measured this session, row-diffs 0** | **NOTHING for the model.** The same goldens are scored against the RTL by `check_core`, which is unmoved at 169,000 and 279/283 |
| `python3 sw/ucsim_check.py --suite …` | the architectural ladder, **7,341,126 cases** (v0.1 169,000 + v0.2 347,000 + v0.3 3,699,998 + v20suite 3,125,000 + mod3_illegal 128) | not re-measured this session | ✅ **REPLACED 2026-09-19 (WAVE 22) by `python3 sw/check_core.py --core ucore --suite-dir tests/v30/<suite> --opcodes all --cases 0`** — `v20suite` needs `--arch-only`, `mod3_illegal` needs `--opcodes goldens`, and the metadata dialects are adapted by `sw/suitemeta.py`. `docs/notes/suite_scorer_prereg_2026-09-19.md` / `..._results_2026-09-19.md` carry the four measured totals and their taxonomies. ⚠ **THE REPLACEMENT IS NOT EQUAL TO WHAT WENT**: `check_core` scores the **RTL**, `ucsim_check` scored the **model**, and the two were never one measurement. ⚠ **AND THIS ROW OWED THREE CORRECTIONS, EACH MEASURED IN WAVE 22**: (a) **`v0.3` and `v20suite` were never BLOCKED — only never RUN**; (b) the `KeyError` also hit `mod3_illegal`, unnamed here; (c) **the 7.17 M double-counts** — `v0.3` *"supersedes v0.2 outright"* (`v0.3/README.md`), same seed base, 2.1 % of the 347,000 prefix cases differing. ⚠ **STILL TRUE**: `v0.2`/`v0.3`/`v20suite` are **NOT IN GIT** (per each suite's own `.gitignore`), so a scorer is not a repo-reproducible gate. *The original text: "NOTHING — and this is the single largest loss in this entry."* |
| `python3 sw/ucsim_fuzz.py --bank …` | the S3 sequence gauntlet, **2,125 / 2,125** architectural dumps | not re-measured | **NOTHING** |
| `python3 sw/check_boot.py --timed 220` | **220 / 220** rows from RESET release | not re-measured | the RTL legs `check_boot 220` and `400`, **which are PRESERVED and measured unmoved** — they had been killed by an unconditional `simbin.ensure()` and this wave made it conditional |
| `python3 sw/qdepth_probe.py` | `rdq_ ≤ 2`, `rd_done_q_ ≤ 1` — the regime in which `timed_fuzz`'s `BOUND WARNINGS` is a theorem | not re-measured | **NOTHING.** The bound is still asserted as a hard failure inside `check_core`, where it is a theorem; what is gone is the instrument that PROVED the regime |
| `python3 sw/timed_fuzz.py --core sim --evt-replay` | REGISTERED **1,339/1,702** · EVT **799/1,008** · COMBINED **2,138/2,710** · `--seeddir …/b2-tranche` **161/188** | not re-measured | **NOTHING for the model leg.** ⚠ **The `--core ucore` leg is PRESERVED** (REGISTERED 1,559/1,702 · EVT 934/1,008 · COMBINED 2,493/2,710 · b2 181/188) — it too was about to die to an unconditional `ensure()`, and this wave gated it |
| `python3 sw/sm3_s16_score.py --core sim` | **1,305 / 1,371** | not re-measured | **NOTHING for the model leg**; the `--core ucore` leg (**1,320/1,371**) was already conditional and is unmoved |
| `python3 sw/sm3_tf_floor_cell.py score --core sim` | **121,890 rows, 0 row-diffs at floor 3** | not re-measured | **NOTHING for the model leg.** ⚠ **The `--core ucore` leg is PRESERVED and MEASURED: 121,890 rows, 0 row-diffs, EXACT, surviving floors `[4]` over 22 cells** — it was dying to an **IMPORT-TIME** `simbin.ensure()`, which this wave moved onto the sim leg |
| `python3 sw/timed_lawcards.py` | **8 GREEN / 0 RED / 3 UNRESOLVED** (C6, C7, C11) | **ALREADY DOWN** — `V1AnchorStop`, measured this session | nothing; it was already unrunnable |

**B. GATES THAT WERE ALREADY DOWN AND NOW HAVE A SECOND CAUSE.** Each of these
is a v1-anchor casualty (`staleness_audit_2026-09-19.md` §4) *and* a model
consumer. Retiring the model does not make them worse and does not close them.

| gate | last registered figure | it was already down because |
|---|---|---|
| `sw/timed_wvec_gate.py` | **88/88, +0.0 %** | `V1AnchorStop` (confirmed this session) |
| `sw/timed_enter_replay.py` | **154/154 ×5** | its own v1-anchor refusal (confirmed) |
| `sw/timed_ins_replay.py --raw` | rails **1,312/1,312**, vs-chip **2,624/2,624** | ⚠ **NOT the anchor** — `FileNotFoundError: sw/case31_all_exts.txt`, a file that **has never been committed to this repository** (`git log -- ` it: empty). Measured this session |
| `sw/timed_scenario.py` | **18 PASS / 0 FAIL / 9 SKIP** | ⚠ **IT WAS NOT DOWN.** `CLAUDE.md` says it dies in `gen_seq._v1_anchor_stop`; **measured this session on `master` it RAN AND PASSED at exactly its registered figure.** It is a genuine casualty of this entry, and the `CLAUDE.md` claim is an erratum recorded in the audit |

**C. MEASUREMENT TOOLS — never gates, and `CLAUDE.md` says so.** All die:
`sw/s14_census.py`, `sw/s14_dstar.py`, `sw/uscope.py`, `sw/ucsim_smoke.py`,
`sw/ucsim_coverage_report.py`, `sw/sm3_famb_survey.py`, `sw/sm3_tf_law.py`,
`sw/qcensus.py` / `q1census.py` / `q1diff.py` / `repcensus.py` / `wchain.py`
(model legs), `sw/wrfuzz_smoke.py`, and the `--core sim` legs of
`sw/s15_census.py` (its **`--core ucore`** leg is PRESERVED, gated by this
wave), `sw/wrfuzz_w7_gap_guard.py`, `sw/w33_take_cell.py`,
`sw/w33_poste_cell.py` and `sw/w34_grant.py` (their **`--core ucore`** legs are
PRESERVED, all three gated by this wave off an IMPORT-TIME `ensure()`).
`sw/s13_board.py`'s model leg goes; **the board CLI itself is PRESERVED** — it
was about to die whole, and SM2's rig-integrity finding is that nothing notices
an s10/s13 probe is broken until a board sitting needs it.

**D. THE ONE THAT WAS LOAD-BEARING, AND IT IS PRESERVED — GATE G0.**

`sw/check_ucore_tables.py` diffed `hdl/rtl/ucore/ucrom.hex`, `ucdecode.hex` and
`pla3_tables.svh` against **`sim/v30sim dump-tables`**. That is the microcode
ROM — the ucore's entire architecture — and the model was its INDEPENDENT
reference.

**IT IS PRESERVED BY SNAPSHOT, AND THE INDEPENDENCE SURVIVES INTACT**, because
the independence was never in the model being *runnable*: it was in the model
being a **SECOND IMPLEMENTATION**, 10,089 lines of C++ transliterated from
`docs/V20UCDIS.PAS`. Freezing its output preserves exactly that, for exactly
the ROM it was taken from.

* the reference: **`sw/testdata/g0-tables/v30sim_dump_tables.txt`**, 9,992
  lines, sha256 **`23d0025bc72eff93…`**, produced by receipt
  `54cb8188bf7bff16…` at tree `975ecd0187`, with `manifest.json` beside it.
* **the gate REFUSES rather than scoring if the ROM moves.** The manifest pins
  `docs/V20BITS.TXT` (`ecd09bf03a886840…`) and `docs/pla3_outputs.txt`
  (`d4eab9e854fb59c6…`); either moving makes the snapshot a statement about a
  ROM this tree no longer has, and the engine that could re-derive it is gone.
  `check_ucore_tables` then exits **2, CANNOT MEASURE — never PASS, never
  FAIL**, and prints the commands to restore the model and re-take the
  snapshot.
* **G0 still reports the same 9,988 entries identical on BOTH legs** — Leg A's
  own independent parser and Leg B's emitted artifacts — measured before and
  after the removal.
* **FIVE POSITIVE CONTROLS, all fired** (the classifier does not get to be
  trusted): a one-nibble edit to the snapshot with the manifest NOT re-hashed →
  **exit 2**, *"does not match its own manifest"*; the same edit WITH the
  manifest re-hashed → **exit 1**, *"ucrom rows: 1 MISMATCH of 1028"* and
  *"ucrom.hex: 1 MISMATCH of 1028"* (the comparison is live, not a
  tautology); one byte appended to `docs/V20BITS.TXT` → **exit 2** naming it;
  one byte appended to `docs/pla3_outputs.txt` → **exit 2** naming it; one bit
  flipped in `hdl/rtl/ucore/ucrom.hex` → **exit 1**, LEG B and LEG C both
  failing. All five files restored and verified byte-identical afterwards, two
  independent ways (sha256 against a pre-image copy, and `git status` clean).

### WHAT ELSE IS PRESERVED, AND HOW — the mechanism, stated once

**`sw/simbin.py` IS NOT DELETED. IT IS THE RETIREMENT DECLARATION.** It was the
SINGLE DECLARATION of what the model was a function of, and **134 modules reach
it by import** — four of them (`check_fuzz_bank`, `fz2_replay`, `fz2_w1`,
`ghost_launch_law`) are LIVE STANDING GATES that never touch the model and
would have died at `import` for a reason unrelated to what they measure.

So the declaration outlives the artifact and now declares its retirement. Every
verb — `ensure()`, `require_bin()`, `recipe()`, `receipt_id()`, `disasm_gate()`
— raises **`ModelRetired`**, one banner naming the directive, this entry, and
the recovery command. `simbin.SIM` stays a path constant, because six modules
bind it at import time and a module-level `__getattr__` that raised would kill
`ghost_launch_law`. `simbin.retired()` exists for the handful of tools that
resolved the binary by bare path.

**THE RULE: NO GATE DIES SILENTLY AND NONE DIES WITH A `FileNotFoundError`.**
Verified by running every module in `sw/` (376 of them) under `import`: **0
model consumers raise a file error.** The three that do
(`fit_class5`, `t33_scattertest`, `t33_traj`) fail on `/tmp/class5_data.json`
and `testdata/campaigns/mc1/results.jsonl` — relative-path bugs that predate
this entry and have nothing to do with the model.

⚠ **FIVE FILES WERE DELIBERATELY NOT REPAIRED, AND THEY WILL RAISE
`FileNotFoundError`**: `sw/t7_sim_ab.py`, `sw/t7_sim_proof.py`,
`sw/testdata/rep_cl0/modeldrive.py`, `sw/testdata/rep_cl0/rep_cl0_repro.py`,
`sw/testdata/rep_cl0/repdrive.py`. **All five are the USER'S OWN UNCOMMITTED
WORK** in this working tree, and this wave's standing instruction forbids
touching it (`git stash` swept it once already, WAVE 12). They resolve
`sim/build/v30sim` by bare path; none is a gate; all five are closed-campaign
one-shots. **The fix is one line each — `simbin.retired("…")` before the first
`subprocess.run`** — and it belongs to whoever owns those edits.

### HOW TO RECOVER IT — nothing was destroyed

```sh
git checkout be4eb2c32f930e12575da5a6359b4fead3c28f96 -- sim/
git checkout <the commit before this entry> -- sw/simbin.py
python3 sw/simbin.py --build
```

`be4eb2c32f` (2026-08-17) is the model's last source commit. The `git rm` in
this wave removes the files from the WORKING TREE only; every byte, every
revision and every one of the 75 August commits remains in history. The
pre-retirement `sw/simbin.py` — the receipt-layer declaration with its §A-§C
reasoning — is in that same history and should be read there rather than
reconstructed.

⚠ **One thing recovery does NOT restore**: `sw/gen_ucore_tables.py` and
`sw/ucore_tables.py` describe themselves as *"a line-for-line transliteration
of `sim/ucrom.cpp`"* and cite `sim/pla3_table.h`, `sim/ucrom.h`,
`sim/state.h` and `sim/exec_impl.h:796` by path. **Those citations now point
into history.** They were left standing deliberately: they are the ucore's
provenance and deleting them would delete the provenance, not the dangle. Read
them against `be4eb2c32f`.

### GATE STATUS — what moved, and what did not

| | before | after |
|---|---|---|
| `check_core --opcodes all --cases 0`, `--ce-div` 2 / 3 / 4 / 8 | 169,000 ×4 | **169,000 ×4 — UNMOVED** |
| `--ce-div 1` | REFUSED, exit 2 | **REFUSED, exit 2 — UNMOVED** |
| `FA` / `FB` / `INT.FB` (the exact 181's population) | 1,200/1,200 | **1,200/1,200 — UNMOVED** |
| the four HLT sweeps at `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = **279/283** | **279/283 — UNMOVED** |
| `check_boot` 220 / 400 (RTL) | MATCH / MATCH | **MATCH / MATCH — UNMOVED** (⚠ they would have DIED; see above) |
| `check_ab_sim` | 187 rows MATCH | **187 rows MATCH — UNMOVED** |
| `ss_lint` | 232 / 229 flops / 4 whitelist / 0 UNMAPPED | **UNMOVED** |
| `r7_lint` · `cutset_lint` (81/0) · `phase_split_lint` (157/779/0) · `core_portlist_lint` · `chainflat_relocation_check` (9/9) · `ucrom_mif_check` · `demux_off_gate` | PASS | **PASS — UNMOVED** |
| `chain_lfsr_gate` | 4 signatures `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78` | **BYTE-IDENTICAL — UNMOVED** |
| `test_artifact` · `test_quartus_gate` | 45/45 · 287/287 | **UNMOVED** |
| `check_fuzz_bank` | PASS 621 | **PASS 621 — UNMOVED** (it imports `timed_fuzz`, which imports `simbin`) |
| `gen_ucore_qsf --check` · `pla3_check` | PASS · 21 checks | **UNMOVED** |
| `check_ucore_tables` (G0) | PASS, 9,988 entries | **PASS, 9,988 entries — on the frozen reference** |
| `ghost_launch_law score` | 200/200 = 100.0 % | **200/200 — UNMOVED** |
| `sm3_tf_floor_cell score --floors 4 --core ucore` | 121,890 rows, 0 row-diffs, EXACT | **UNMOVED** |
| `simbin --disasm` | PASS, 1,285 rows | **RETIRED — exit 2, naming this entry** |
| every gate in §A / §B / §C above | see the table | **RETIRED, exit non-zero, naming this entry** |

### THE FALSIFIER, registered with the entry

The claim is **"no gate died silently, and G0's independence survives"**, and
it has three falsifiers, each cheap:

1. **FALSIFIED IF** any module under `sw/` that consumed the model raises
   `FileNotFoundError`, `ImportError` or `ModuleNotFoundError` instead of
   `ModelRetired`, on the five declared exceptions above excepted. The test is
   the import sweep in `staleness_audit_2026-09-19.md` §B and it is four lines
   of Python.
2. **FALSIFIED IF** `check_ucore_tables` ever reports **PASS** on a tree whose
   `docs/V20BITS.TXT` or `docs/pla3_outputs.txt` differs from the manifest's
   sha256. That is the whole content of the snapshot's honesty, and the five
   positive controls above are its standing demonstration.
3. **FALSIFIED IF** a future sitting restores a retired gate to green by
   pointing it at the RTL and keeping the model's registered figure. Those
   figures are the MODEL's; an RTL leg that inherits them is a different
   measurement wearing their name. Re-register, never re-label.

---

---

---

---

## RET-2 — THE ARCHIVED FSM CORE `hdl/rtl/core/`, AND THE FSM QUARTUS REVISION

**Retired 2026-09-19, branch `master`, WAVE 21.  No rig defect.  Nothing was
destroyed — `git rm` keeps every byte in history, and the recovery commands are
in this entry.**

### THE AUTHORITY

**USER INSTRUCTION, 2026-09-19, verbatim:**

> *"Remove the FSM core, fix whatever dependencies exist"*

**USER RULING, 2026-09-19, verbatim, which widened it from a deletion to a
re-basing:**

> *"These are the kinds of discrepancies I am asking you to audit and resolve.
> There have been a lot of iterations in this project and you need to treat the
> documentation as hearsay until proven otherwise.  Ucore is the only valid
> implementation in this code base, if it has dependencies on any other
> implementations those need to be removed.  Documentation that gives those
> other implementations precedence is suspect."*

⚠ **THIS OVERRIDES WAVE 20's AUDIT RECOMMENDATION.**
`staleness_audit_2026-09-19.md` §2 recommended **"KEEP THE RTL, RETIRE FOUR OF
ITS TEN GATES"**.  The user's instruction is the removal; the audit's
recommendation is recorded as what it was, and is not retracted as an argument —
it is overruled as a decision.

### WHAT WENT — measured, not estimated

| | |
|---|---|
| the artifact | `hdl/rtl/core/` — the cycle-accurate, **trace-fitted** V30 core (campaigns 3 and 4, first light 2026-07-13; ARCHIVED 2026-08-04, `docs/notes/fsm_core_archive_2026-08-04.md`) |
| tracked payload | **6 files, 467,184 bytes** — `v30_eu.sv` 292,906 · `v30_biu.sv` 111,724 · `v30_ss_pkg.sv` 25,826 · `v30_core.sv` 16,799 · `race_law.svh` 14,809 (GENERATED) · `int9d_race.hex` 5,120 |
| its Verilator binary | `hdl/tb/obj_dir/Vtb_v30_core`, receipt **`6ef5e51f32e75735…`**, built and receipted in this session immediately before the removal |
| the Quartus side | `hdl/files.qip` (the FSM file list, 1,058 bytes) · `hdl/nec_test.qsf` (the FSM revision) · `PROJECT_REVISION = "nec_test"` in `hdl/nec_test.qpf` · `sw/gen_ucore_qsf.py` (the derivation and bar **E1**) |
| also gone | `sw/race_law_equiv_tb.sv` — the FSM-only Verilator harness `check_race_law` built |
| **ARCHIVED BY RENAME, not deleted** | `hdl/rtl/core/int9d_race.hex` → **`docs/facts/int9d_race_contract_archived_2026-09-19.hex`**.  ⚠ **IT IS A MEASURED CONTRACT, NOT RTL** — `sw/exp_race.py:8` calls it *"the measured contract: bit=1 → class B"* for the POP-PSW/INT race, and `race_law.svh` was GENERATED from it.  The RET-1 precedent (`sim/README.md` → `docs/notes/…`).  `docs/facts/int9d_race_table.json.gz` holds the same table in the facts tree |
| **NOT retired with it** | `sw/gen_race_law.py` — the generator survives as a REFUSAL, because it is the provenance of the archived contract |

### WHY — and the ruling is the reason, not a measurement

The archive of 2026-08-04 already recorded the evidence (`fsm_core_archive_
2026-08-04.md` §3: 59/178 vs 176/178 in fabric on the priority tranche; a
**104-seed silent regression** no gate saw; the unfixed F51 HALT pad-drive
defect; the rail forest the SIMPLICITY directive names).  WAVE 20 added the
maintenance measurement: **two authorised changes since the archive, both pure
port-list maintenance forced by ucore landings** (§6a's `AD_OE`, §6b's
`ADDR_O`/`DATA_O`/`STATUS_O`), **five weeks unreachable by its own documented
procedure**, and **one whole wave (18) spent so that a gate could elaborate**,
which produced a permanent standing gate whose only job was to keep the two
port lists equal.

**AND IT WAS GREEN ON THE DAY IT WENT, WHICH IS NOT A DEFENCE.**  Measured in
this session, on the tree that carried it (`6c3de357d9`):

| leg | measured 2026-09-20, immediately before the removal |
|---|---|
| `check_core --core fsm --opcodes all --cases 0` | **169,000 / 169,000** (cycles 169,000, arch 169,000) |
| the four HLT sweeps, `--waits 0/1/2/3` | **87/97 · 82/95 · 30/46 · 27/45 = 226 / 283** |
| `ss_lint --core fsm` | **PASS — 203 addresses (82×2 BIU + 120×2 EU + tag), 181 architectural flops, 0 UNMAPPED** |
| `check_ab_sim --core fsm` | **MATCH over 187 rows from RESET release** |
| `check_race_law` | **PASS (2/2 sub-checks)** |
| `prefix_clear_lint` | **PASS (20 `S_FIRST` sites, 4 PFX-KEEP, single source, no drift)** |
| `ea_step_lint` | **PASS** |

⚠ **AND THAT CONFIRMS WAVE 18's ERRATUM AND REFUTES THE ARCHIVE'S OWN §5.**
`fsm_core_archive_2026-08-04.md` §5 registers **168,400 / 169,000** and
**16 / 283** on *"the corrected comparator"*.  Measured on this tree the same
commands give **169,000 / 169,000** and **226 / 283**.  Nothing in
`hdl/rtl/core/` changed; the COMPARATOR did, at `0254d9f23e`, whose own message
says *"it moves NOTHING"* and quotes the **ucore** leg.  **Both figures are that
instrument's, and any FSM figure must name which comparator produced it.**

### WHICH RIG DEFECT

# **NONE.**

No rig defect is alleged, none is diagnosed, and none is fixed by this entry.
No capture is false.  Every figure ever scored against this core stays true *of
this core*, and the receipt that identifies the bytes that produced the final
set (`6ef5e51f32e75735…`) is recorded here so those figures keep their artifact
id.

### EVERY GATE THAT DIED — enumerated, with its last registered figure

⚠ **This is the field that makes the retirement honest.**  Every row was run
AFTER the removal and its behaviour recorded (the results document's §Z-3
table).  **STATUS** is the gate's state at the moment it went, not today's.

**A. `standing_gates.md` §C — THE TEN ON-DEMAND FSM GATES.  §C IS NOW EMPTY.**

| gate | last registered figure | status when it went | replaced by |
|---|---|---|---|
| `python3 sw/check_core.py --core fsm --opcodes all --cases 0` | **169,000 / 169,000** (⚠ §5 of the archive says 168,400 — different comparator) | **GREEN, measured this session** | **NOTHING for this core.** The same goldens are scored against the ucore by `check_core` with no flag, unmoved at 169,000 |
| the four HLT sweeps, `--core fsm` | **226 / 283** (87·82·30·27) | **RED as registered, measured this session** | **NOTHING.** The ucore's own sweeps are 279/283 and are UNMOVED |
| `python3 sw/ss_lint.py --core fsm` | **PASS, 203 addresses / 181 flops / 0 UNMAPPED** | **GREEN, measured this session** | **NOTHING.** The ucore leg (232 / 229 / 4 whitelist / 0 UNMAPPED, `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8) is the default and is UNMOVED. ⚠ **The two maps were never stream-compatible** |
| `python3 sw/ss_flopcensus.py --core fsm` | **PASS, 181 flops, 0 whitelist** | **GREEN, measured this session** | **NOTHING** |
| `python3 sw/check_ab_sim.py --core fsm` | **MATCH over 187 rows** | **GREEN, measured this session** | **NOTHING for this core.** The `--core ucore` leg is the default, also 187 rows MATCH, UNMOVED |
| `python3 sw/check_race_law.py` | **PASS (2/2)** — `race_law.svh` exhaustively matches `int9d_race.hex` AND regenerates byte-for-byte | **GREEN, measured this session** | **NOTHING.** The POP-PSW/INT race law has no ucore equivalent: the ucore does not carry a race table. ⚠ **The measured contract is PRESERVED** (`docs/facts/int9d_race_contract_archived_2026-09-19.hex`) and `sw/gen_race_law.py` survives as its provenance |
| `python3 sw/prefix_clear_lint.py` | **PASS (20 `S_FIRST` sites, 4 PFX-KEEP, single source, no drift)** — RR4 | **GREEN, measured this session** | **NOTHING.** It greps `hdl/rtl/core/v30_eu.sv`; the ucore has no `clear_prefixes()` |
| `python3 sw/ea_step_lint.py` | **PASS** — every operand EA step wraps via `ea_step2` (F4a) | **GREEN, measured this session** | **NOTHING.** It greps `hdl/rtl/core/v30_eu.sv` |
| `python3 sw/check_ff_t4.py` | `SLOT_FF_T4` non-vacuous | **ALREADY DOWN — `V1AnchorStop`, confirmed this session.** ⚠ It also carried one of WAVE 18's two booked STALE-BINARY hazards (`:34`, raw `check_seq.BIN`, no artifact assertion) — **that hazard dies with it** | nothing; it was already unrunnable |
| `python3 sw/check_mod3_illegal.py` | LEA mod=11 executes chip-exact (task #30) | **ALREADY DOWN — `ComposeError: body [0500,0502) is not inside the code region [8000,c000)`, confirmed this session** | nothing; a v1-anchor casualty (`staleness_audit_2026-09-19.md` §4) |
| `python3 sw/check_lc6_gate.py` | the Family-5 strio-single uline-1 veto is intact | **ALREADY DOWN — `ComposeError: body [0500,0517) …`, confirmed this session** | nothing; a v1-anchor casualty |
| `python3 sw/check_enter_nesting.py` | ENTER walk == chip (task #31) | **ALREADY RED, AND ENGINE-INDEPENDENTLY SO — `check_enter_nesting: FAIL`, confirmed this session.** The identical instrument with `check_seq.CORE = "ucore"` fails the same 512: it composes a v2 image and scores it against v1 goldens. **A LOUD RED CAN BE AS FALSE AS A SILENT GREEN** | nothing; a v1-anchor casualty |
| `python3 sw/check_fuzz_bank.py [--strict]` | **`PASS \| 621 banked seeds \| stable 621 improved 0 worse 0 \| gen_drift 0 regen_err 0 \| float-floor 0 \| new-sig TIMING 0`** (⚠ and `--strict` exits 0 since SM3 sitting 7) | see the dedicated section below | **NOTHING, and it is NOT re-pointed.  See below.** |
| `sw/t30_sweep.sh` | *"any non-full suite total or failed gate = regression"*, read against 169,000 and 226/283 | **RED as registered** (three legs are v1-anchor casualties; the script was only made capable of reporting RED at `becaf81e89`, 2026-09-19) | **NOTHING as an aggregate.** Its v0.1 / v0.3 / f4a_boundary / f0lock_tranche legs are swept against the ucore by `sw/check_core.py` on the standing ladder |
| `python3 sw/r7_lint.py --core fsm` | **INFORMATIONAL ONLY — never a gate.** Measured this session: **`WOULD FAIL`** | not a gate, so not a casualty | nothing; the ucore leg is the gate and is PASS |

**B. THE QUARTUS A/B, AND THE ONE GUARANTEE THAT DIES WITH NOTHING REPLACING IT**

| gate | last registered figure | status | replaced by |
|---|---|---|---|
| `python3 sw/gen_ucore_qsf.py --check` — bar **E1** of `quartus_gate.py`, receipt key `E1_gen_ucore_qsf`, bar text *"hdl/nec_test_ucore.qsf is a faithful derivative of hdl/nec_test.qsf"* | **PASS** — measured this session, and PASS on FLASH #23's own CONTROL receipt | **GREEN** | ⚠ **SPLIT IN TWO.**  (a) The half with a surviving referent — *the revision file the compiler reads has not drifted from what the tree declares, i.e. no previous build's in-place Quartus rewrite was left in it* — is **REPLACED by `sw/qsf_lint.py --check`**, receipt key **`E1_qsf_canonical`**, a CANONICAL-FORM bar.  (b) The half the bar was named for — ***"the two A/B bitstreams differ by the CORE and nothing else"*** — **IS RETIRED AND NOTHING REPLACES IT.  There is no second core and no second revision for it to be about.**  Every A/B claim resting on it is HISTORY as of this entry |
| the FSM A/B bitstream | `nec_test.sof` **`a4533dfef09b896ebb08763658b053e7cfb0946877b1ce43831fbd7b89f500e2`** (FLASH #2, 2026-08-04T04:06:15Z) — **the last FSM bitstream built from a then-HEAD, and it was NEVER on the board after FLASH #3** | not on the board; `flash_log.jsonl` keeps its entry | **NOTHING.** No FSM bitstream can be built from this tree. ⚠ **The A/B experiment is CLOSED, not paused** — reproducing it requires the recovery below AND a board session, and `fsm_core_archive_2026-08-04.md` §5's standing warning (build and flash BOTH cores from ONE HEAD) still governs anyone who does |
| `sw/receipt_diff.py`'s *"FSM vs ucore bitstream: `files_ucore.qip` ↔ `files.qip` + the cores"* row | a documented comparison mode | it names a file list that no longer exists | **NOTHING.** The row is corrected to say so |

**C. TOOLS, NOT GATES — `CLAUDE.md` and `standing_gates.md` never listed these
as gates and this entry does not promote them.**  All refuse by name through
`sw/fsmcore.py`: `sw/biu_law_mutation.py`, `sw/biu_law_lc3_gadget.py`,
`sw/biu_law_lc3_seedsearch.py`, `sw/biu_law_lc6_gadget.py`,
`sw/biu_law_gatesearch.py` (all five mutate `hdl/rtl/core/v30_biu.sv`),
`sw/gen_race_law.py`, `sw/exp_race.py`, `sw/sweep_popa.py` (and through it
`sweep_farjmp` / `sweep_loop` / `sweep_push` / `sweep_regea` / `sweep_swint`),
`sw/sweep_dispphase.py`.  Refusing through **`check_seq`'s retired pin**:
`sw/causal_wrand.py`'s `run_tb_internal` and its ~20 `class5_*` readers,
`sw/dumpeu.py`, `sw/exact_predict.py`, `sw/f7a_arbitrate.py`,
`sw/exp_iret.py`, `sw/pi1a_trace.py`.

**D. THE PIN THAT MADE MOST OF C POSSIBLE — `sw/check_seq.py`.**
`CORE = "fsm"` was the single declaration that decided which engine every
`check_seq.run_tb()` caller got when it named none, and `BIN` was the FSM
`obj_dir` path.  **`CORE` IS NOW `None` AND BOTH REFUSE BY NAME.**  A caller
that means the ucore must say so (`core="ucore"`) — which `fz2_replay`,
`emit_suite`, `fz2_a1_rescore`, `fz2_c1_rescore`, `fz2_c2_rescore`, `fz2_m10`,
`fz2_p2_probe` and `fz2_undoc_probe` already did, and which is why **no live
standing gate moved.**

### ⚠ `check_fuzz_bank` — RETIRED, NOT RE-POINTED, AND WHY

`sw/check_fuzz_bank.py:76` replays every banked seed through
`check_seq.run_tb(...)` **with no `core=`** — i.e. through `check_seq.CORE`,
which was `"fsm"`. Its registered figure is therefore **an FSM figure**.

**IT IS NOT RE-POINTED TO THE ucore, AND THAT IS A DECISION WITH A REASON.**
`sw/fuzz_bank.py:261` computed each entry's banked `replay_verdict` **by calling
this same function** — on the FSM TB.  A ucore replay would compare a ucore
verdict against an FSM-derived column: a guaranteed FAIL that measures the
engine swap and nothing else.  And RET-1's falsifier #3 forbids the alternative:
*a re-pointed leg may not inherit the retired leg's figure.*

**BOOKED, NOT TAKEN**: re-deriving the banked `replay_verdict` column on a ucore
replay, under the `ERR-1` / `sw/cfb_rederive.py` pre-registration pattern
(archive the column byte-identical first, score a full dry run, register the
movers in advance).  Until then the gate has **NO** replacement.

⚠ **WHAT IS LOST WITH IT, stated plainly**: it was the load-bearing control for
the U5 comparator change (**3,242 banked seeds replayed and re-classified,
worse 0** — `ucore_provenance.md` §57.2) and for the SM3 sitting 6 `IOW` fix.
**Those measurements remain true and citable; the instrument that could repeat
them does not exist on this tree.**

### WHAT ELSE CHANGED, AND IT IS NOT A RETIREMENT

* **`sw/core_portlist_lint.py` — RE-POINTED, and its old claim retired.**
  WAVE 18's gate compared the TWO cores' port lists; with one core that has no
  second operand and **nothing replaces it.**  It now checks, per
  CONFIGURATION, that **every `.NAME(...)` named connection to `v30_core` is a
  port the module declares under the same define set** — the same defect class
  (`%Error-PINNOTFOUND`; Quartus's accept-and-ignore Critical Warning) with the
  operand that still exists, and it now covers the **FABRIC** configuration
  (`SYNTHESIS` + `V30_MUXED_AD`) that no Verilator run exercises.  **Measured:
  PASS in 4 configurations** — `tb_v30_core` (34 ports / 34 connections),
  `system_large` under Verilator and under `SYNTHESIS` (24 / 24 each),
  `tb_demux_min` (23 / 23).
  ⚠ **AND IT WAS CARRYING A SILENT BUG.**  WAVE 18's `_strip_comments`
  stripped `/* … */` with a regex over the RAW text; `hdl/tb/tb_v30_core.sv:40`
  is a LINE comment containing `hdl/rtl/core/*.sv`, so the regex matched from
  there to line 254's `*/` and **deleted 200 lines including the `v30_core dut (`
  instantiation.**  It never showed because WAVE 18 only ever fed it the two
  `v30_core.sv` files.  Found the first time the function was pointed at the TB,
  and it presented as **exit 2 CANNOT MEASURE** — which is the only reason it
  was not a silent wrong answer.  Replaced by a scanner.
* **`sw/check_core.py`'s `BIN` / `OBJ` / `RTL` — RE-POINTED to the ucore, and
  five tools change engine.**  `:180` declared them *"pinned to the FSM layout
  and both with NO consumers anywhere in the tree (checked 2026-08-04)"*.
  **MEASURED FALSE: `BIN` has five consumers and `OBJ` two** —
  `sw/emit_suite.py:2258`, `sw/f4a_boundary_battery.py:73`,
  `sw/char_divergence.py:26`, `sw/validate_strio_sim.py:158`,
  `sw/class5_hext.py:58`; `sw/pi1a_trace.py:29` and `sw/repro_segleak.py:33`.
  ⚠ **`emit_suite.py` calls `CC.build()` — which builds the DEFAULT ucore into
  `obj_dir_ucore` — and then executes `CC.BIN`, the ARCHIVED core's binary in
  the unsuffixed `obj_dir`.**  The trap the comment warned about was already
  sprung.  **This is a CHANGE OF ENGINE and it is declared: no registered figure
  is inherited across it**, and none of the seven tools carries a figure on any
  standing ladder (`f4a_boundary` 160/160 and `f0lock_tranche` 400/400 are taken
  through `check_core --suite-dir`, not through `f4a_boundary_battery.py`).
* **`sw/check_boot.py` — A LIVE COUPLING TO RET-1'S MODEL, FIXED HERE.**
  RET-1 §A claims the `check_boot` RTL legs *"had been killed by an
  unconditional `simbin.ensure()` and this wave made it conditional"*.
  **MEASURED: the condition it landed is `if timed:` — and `--timed` is the
  MODEL leg (`run_timed()` runs `$SIM timed-boot`).**  So
  `sw/check_boot.py --timed 220`, the command `CLAUDE.md`'s quick reference
  still prints under *"Timed, whole-program"*, **dies with `ModelRetired`**, and
  the live RTL legs are `check_boot.py 220` / `check_boot.py 400` — **measured
  MATCH over 220 and 400 rows this session.**  The `--timed` leg is therefore a
  RET-1 casualty that RET-1's own GATE STATUS table records as *"UNMOVED"*.
  Corrected in both documents.

### HOW TO RECOVER IT — nothing was destroyed

```sh
git checkout fb9365c01c -- hdl/rtl/core/ hdl/files.qip hdl/nec_test.qsf
git checkout fb9365c01c -- sw/gen_ucore_qsf.py sw/race_law_equiv_tb.sv
git checkout fb9365c01c -- sw/check_core.py sw/check_seq.py sw/check_ab_sim.py
git checkout fb9365c01c -- sw/ss_lint.py sw/ss_flopcensus.py sw/r7_lint.py
git checkout fb9365c01c -- sw/core_portlist_lint.py sw/quartus_gate.py
git checkout fb9365c01c -- sw/t30_sweep.sh sw/check_race_law.py sw/gen_race_law.py
#   ...and `PROJECT_REVISION = "nec_test"` back into hdl/nec_test.qpf
python3 sw/check_core.py --build --core fsm
```

`fb9365c01c` (2026-09-19) is WAVE 20's tip, the last commit with the FSM core in
the working tree.  The `git rm` in this wave removes the files from the WORKING
TREE only; **every byte, every revision and the whole of campaigns 3 and 4
remain in history.**  `docs/notes/fsm_core_archive_2026-08-04.md` keeps its
record of what the core achieved and why it was archived, and is now a HISTORY
document rather than a description of the tree.

⚠ **One thing recovery does NOT restore**: the ucore's own RTL comments cite
`hdl/rtl/core/` by path (`hdl/rtl/ucore/v30_core.sv:5`, `v30u_biu.sv:100`,
`v30u_ss_pkg.sv:7`) and are **LEFT STANDING DELIBERATELY** — they are the
ucore's provenance, and deleting them would delete the provenance rather than
the dangle.  `hdl/rtl/ucore/` was not edited in this wave (bar **Z-6**).  Read
them against `fb9365c01c`.

### GATE STATUS — what moved, and what did not

The full BEFORE/AFTER table is `docs/notes/fsm_removal_results_2026-09-19.md`
§Z-5, with both logs committed at `sw/testdata/wave21/{before,after}_ladder.txt`.

**THE LIVE LADDER IS ZERO-DELTA: 23 legs SAME, 0 MOVED.**  `check_core
--opcodes all --cases 0` **169,000 / 169,000** at `--ce-div` 2, 3, 4 **and** 8
with div 1 still refused · the exact 181 (`FA` **500** · `FB` **500** ·
`INT.FB` **200**) · the four HLT sweeps at `--waits 0/1/2/3`
**97 · 93 · 45 · 44 = 279 / 283** · `r7_lint` PASS · `ss_lint` **232 / 229
flops / 4 whitelist / 0 UNMAPPED, `SS_VERSION` 0x8F, `SS_TAG` 0x8FE8** ·
`cutset_lint` **PASS 81 / 0** · `phase_split_lint` **157 / 779 / 0** ·
`demux_off_gate` PASS · `test_artifact` **45 / 45** · `ucrom_mif_check` PASS ·
`check_ucore_tables` (G0) **PASS, 9,988 entries** · `chain_lfsr_gate` **PASS
with its four signatures BYTE-IDENTICAL** (`1d01c9b269ffaa94` ·
`b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78`, and every
`ce_clocks`/`g0` count with them) · `chainflat_relocation_check` **9 / 9** ·
`check_boot` **220 and 400 MATCH** · `check_ab_sim --core ucore` **187 rows
MATCH** · `ghost_launch_law score` **200 / 200**.

**FOUR LEGS CHANGED AND ALL FOUR ARE THIS ENTRY'S OWN BUSINESS**:
`check_fuzz_bank` (RETIRED, replaced by nothing), **E1** (RETIRED, half
replaced), `core_portlist_lint` (RE-POINTED, 2 → 4 configurations), and
`test_quartus_gate` **287 → 302 / 302** (+15: Q18, the new bar's falsifier,
pre-registered as a possible rise).

⚠ **`check_boot --timed 220`/`400` was DEAD ON BOTH SIDES** — a RET-1 casualty
this entry's §"WHAT ELSE CHANGED" documents, and the reason the rows above name
`check_boot.py 220` / `400` instead.

### THE FALSIFIER, registered with the entry

The claim is **"no gate died silently, the live ladder is unmoved, and the
removal is bitstream-neutral"**, and it has four falsifiers:

1. **FALSIFIED IF** any tool that bound the archived core raises
   `FileNotFoundError`, `ImportError`, `ModuleNotFoundError` or a bare Verilator
   `%Error-PINNOTFOUND` instead of `FsmCoreRetired` — with the five RET-1
   exceptions (the user's own uncommitted files) excepted.  The test is the
   run-them-all sweep in the results document §Z-3.
2. **FALSIFIED IF** the CONTROL `.rbf` built after the removal differs from
   FLASH #23's CONTROL draw
   (`e91a67badeef2c17262b5239e0700672f3be69eeb44e749e5c9d53ae1302a613`).  That
   would mean the FSM core, or the `.qsf` re-basing, was reaching the ucore
   bitstream.  **Scored as TWO builds so a difference names its own cause.**
3. **FALSIFIED IF** `core_portlist_lint` ever reports PASS on a tree where a
   `.NAME(...)` connection to `v30_core` names an undeclared port.  Its positive
   controls are in the results document.
4. **FALSIFIED IF** a future sitting restores a retired gate to green by
   pointing it at the ucore and keeping the FSM's registered figure.  Those
   figures are the FSM core's; an RTL leg that inherits them is a different
   measurement wearing their name.  **Re-register, never re-label.**

## AUDITED AND **NOT** INVALIDATED

Recorded because an unexamined suspicion is indistinguishable from an
unexamined artifact. Each of these was checked this session and cleared.

| candidate | verdict | the evidence that clears it |
|---|---|---|
| **every `tests/v30` golden suite** | **CLEAN of F46** | The golden emitter's `EVT(...)` spec table (`sw/emit_suite.py:632-657`) declares a max hold of **6**, across all 15 forms. Measured over every suite, `evt.hold` ∈ {0, 2, 6} — always ≤ 255. `hold = 300` is injected ONLY by `fuzz_campaign.py`'s `has_halt` branch, which no golden path takes. |
| the four `v0.1-w*evt` cells and `w1evt-biased` | **CLEAN** | holds 0 and 2 only |
| the four `s10`/`s13` HLT sweeps | **CLEAN** | hold 0 |
| the **b2 victory tranche** (171/188) | **CLEAN** | all 216 seeds carry `evt: none` |
| the **b3 priority tranche** (176/178) and **b4** (435/449) | **CLEAN of F46** | zero cells carry an `evt` axis. X3's issue is bitstream vintage, not hold — and it is a **declared** deviation (§55.2), with the F51 change proved inert on that population offline. **No standing gate consumes either directory** (`sw/u4_tranche.py` is the only reader, and it is not in `standing_gates.md`), so nothing needs suspending. |
| **the sticky-divider era** | **CLOSED, nothing in a gate set** | `ucsim_t_provenance.md` §21.1: two readings were produced at `div = 4` and **retracted before landing**; *"Nothing in the banked corpus is retracted"* — `v0.1`, `-w1`, `-w3` carry the correct display status in their stored rows, so they were emitted at 4 MHz and their provenance is recoverable from their content. The uncorrected emission was preserved-not-deleted at `sw/testdata/s10/s1-instrument/`, and §22.6 pinned the rig (`DIV_OF_RECORD = 8`, stamped into every `emit_log.txt`; `div_guard` readback `PINNED`). |
| **the composed-AD mask** (F51 / U5) | **poisons no golden** | It was a defect in the **comparator** (`hdl/tb/tb_v30_core.sv`), not in any emission. No golden in the tree was emitted from a TB — every `emit_log.txt` opens `# TRUTH SOURCE: SOCKET (real chip, use_core=False)`, and the four suites predating that header carry the equivalent in `metadata.json`. The load-bearing control is §57.2: replaying all **3,242** banked seeds through the corrected comparator moved **no** seed's verdict — *worse 0*. What the mask did poison were **FSM-core scores**, and that is already booked (168,400/169,000 and 16/283, `standing_gates.md` §C). |
| **R6 — the s10/s13 per-repetition rows** | **a retention GAP, not poison** | Both manifests bank every per-rep `raw_sha` and `evt_fired`; only the per-rep *rows* are missing, so `HLT.INT_w2_d0`'s `stable_identical: false` cannot be **verified** as the same pad artefact as `HLT.INT_w0_d0`. Nothing captured is wrong; a verification is unavailable and needs the board. Standing caveat retained: `stable_key` changed at §26.1 and keys stored before it are internally valid and **not comparable across the change**. |
| the campaign result logs (`sw/testdata/campaigns/*/results.jsonl`, 3,005 records asking `hold=300`) | **metadata only, no gate** | no standing gate reads `sw/testdata/campaigns/` |
| the campaign raw capture archives (13,252 files) | **CLEAN** | schema is `{"real": [rows]}`; they carry no `evt` axis at all |

---

# ⚠ WAVE 22 ADDENDUM, 2026-09-19 — GATES THAT MOVED, AND WHY NONE DIED SILENTLY

**This is not a new register.**  Nothing here is an `INV`, `SUP`, `EXC`, `ERR`
or `RET`: no capture is false, no population moved, no seed left a rate, no
derived column was recomputed, and **no instrument was deleted**.  It is the
W-8 record of WAVE 22 (`docs/notes/suite_scorer_prereg_2026-09-19.md` /
`..._results_2026-09-19.md`), filed here because this is where a reader looks
for "what happened to that gate".

## A — WHAT `RET-1` SAID WAS LOST, AND WHAT IT COSTS NOW

RET-1's load-bearing row called `ucsim_check`'s 7,341,126-case architectural
ladder *"the single largest loss in this entry … now scored by nothing"*.  That
row is updated in place above.  **Its replacement is not equal to what went**:
`check_core --suite-dir` scores the **RTL**; `ucsim_check` scored the **model**.
The measured replacement figures are:

| suite | **ucore, WAVE 22** |
|---|---|
| `v0.1` | 169,000 / 169,000 |
| `v0.2` | **347,000 / 347,000** (and identically under `--raw-flags`) |
| `v0.3` | **3,699,998 / 3,700,000** (list disabled) · **3,699,997 / 3,699,997** (list applied) |
| `v20suite` | **3,124,992 / 3,125,000** ARCH — ⚠ **`3,125,000 / 3,125,000` SINCE WAVE 25**, 2026-09-20: the eight were the testbench's settle-window re-latch, not the engine (`tb_relatch_results_2026-09-20.md`).  The WAVE 22 figure stands as WAVE 22's measurement |
| `mod3_illegal` | cycles **128/128** · ARCH **0/128**, confinement CONFIRMED |

⚠ **AND THE REPLACEMENT IS NOT A GATE.**  `v0.2`, `v0.3` and `v20suite` are NOT
IN GIT (per each suite's own `.gitignore`), so **7,172,000 of those cases exist
only on the machine that measured them.**  Recorded with per-suite sha256
manifests; deciding whether they belong in the repository is the owner's call.

## B — FIVE EAGER PRECONDITIONS REPAIRED (a WAVE 20 class, not a WAVE 20 miss)

WAVE 20 repaired six unconditional `simbin.ensure()` calls and wrote *"An eager
precondition is a coupling."*  **All six sat AFTER `parse_args()`.**  These five
sat BEFORE it, so they refused for the retired model's sake before the flag that
selects the engine had been read:

| tool | last state | now | replaced by |
|---|---|---|---|
| `sw/timed_wvec_gate.py` | refused: `ModelRetired` on EVERY invocation | `ensure` behind `--core sim` | its OWN `gen_seq._v1_anchor_stop` refusal — **the v1-anchor casualty is on `master` too, and the blocker is the ANCHOR, not the model.**  Its registered `--core ucore` **88/88, +0.0 %** is anchor-blocked |
| `sw/timed_enter_replay.py` | " | " | same; registered `--core ucore` **154/154 ×5** is anchor-blocked |
| `sw/timed_ins_replay.py` | " | " | `FileNotFoundError: sw/case31_all_exts.txt`, **a file never committed to this repo** — confirming `CLAUDE.md`'s own staleness erratum §(a).  Registered `--core ucore` **1,312/1,312** and **2,624/2,624** are input-blocked |
| `sw/uscope.py` | " (and it has NO `sim` option, ever) | `ensure` **DELETED** | **NOTHING — it works.**  `uscope 00 0` exits 0 |
| `sw/wrfuzz_smoke.py` | " (`--core choices=("ucore",)`) | `ensure` **DELETED** | its OWN defect, `KeyError: 'brkem_pairs'`.  **Reported, NOT fixed** — a different mechanism |

**Nothing was retired and nothing was replaced by nothing.**  Three ratchets
that appeared model-blocked are now correctly attributed to an image anchor and
an uncommitted input file; two tools that could never have run the model are
alive.

## C — `check_fuzz_bank` — AN ERRATUM AGAINST A LIVE LADDER, NOT A NEW DEATH

WAVE 22's own briefing listed `check_fuzz_bank` **PASS 621** as a live
zero-delta leg.  Measured: it **exits 1** through the `check_seq` pin with
`FsmCoreRetired`.  **That is not a WAVE 22 casualty** — `RET-2` /
`fsm_removal_results_2026-09-19.md:330` already records it as **FORMALLY
RETIRED, replaced by NOTHING**, with `PASS | 621 | stable 621 …` as its LAST
REGISTERED figure.  Recorded here so the figure is not quoted as current again.
⚠ It refuses via a **traceback** rather than `fsmcore.refuse()`'s banner; noted,
not changed.

## D.1 — THE `EDGE` ENTRY IS REMOVED, 2026-09-20, USER-AUTHORISED

§D measured the file and deliberately did not edit it.  **The USER then ruled:
*"Remove the stale EDGE entry"*.**  Done, and the measurement that authorises it
was re-taken by the coordinator first rather than inherited from §D.

**WHAT WENT**: `646F` → `8988`, *"EDGE: known pre-existing 1/10000 cycle edge,
repnc OUTSW cx=13 (REP OUTS loop timing, rows 28-32) … arch-CLEAN
(cycle-only)"*.  **The `EDGE` CLASS IS NOW EMPTY**; the two `VOID` entries
(`0F1B`/3917, `83.5`/8683) are untouched and still fail on their merits.

**WHY**: the entry excused a case that PASSES.  Measured 2026-09-20, both legs,
on form `646F` (10,000 cases):

| leg | result |
|---|---|
| exemptions **OFF** (`--no-known-divergences`) | **10,000 / 10,000 full** |
| exemptions **ON**, entry present | 9,999 / 9,999 `[1 documented pre-existing excluded]` |
| exemptions **ON**, entry REMOVED | **10,000 / 10,000 full**, no exclusion note |

**The first two lines are each other's POSITIVE CONTROL** — they prove
`--no-known-divergences` is live and not accepted-and-ignored, which is the
check this campaign has had to add fifteen times.  The third is the edit's own
effect.

**PROVENANCE, AND IT IS THE REASON THIS CLASS WAS SUSPECT**: the file's `_doc`
cites `8fd94df` / `4508e08`, and **`git ls-tree 4508e08 hdl/rtl/` lists `core`
and NO `ucore`** — every classification in it was established against the
**ARCHIVED FSM CORE** (removed 2026-09-19, **RET-2**), not against the ucore and
not against the C++ model.  Under the USER's 2026-09-19 ruling (*"treat the
documentation as hearsay until proven otherwise"*) an exemption inherited from a
deleted implementation is exactly the artifact to re-ask, and re-asking it
retired one of the three.

**NOTHING IS DESTROYED**: the file is TRACKED, so `git show HEAD~1 --
tests/v30/v0.3/known_divergences.json` restores the entry verbatim, and its text
is quoted above.  The suspect provenance note is RETAINED in `_doc` as history
rather than rewritten.

⚠ **THE SUITE'S REGISTERED FIGURE MOVES, AND IT MOVES UP BY ONE CASE IN BOTH
TERMS**: `v0.3` list-on was **3,699,997 / 3,699,997**; the denominator gains the
un-exempted case and the numerator gains it too, so the figure is
**3,699,998 / 3,699,998**.  **REGISTERED AS A PREDICTION BEFORE the confirming
full-suite run** (commit `d639509ad6`, which deliberately declined to quote it as
measured), derived from §D's own list-off measurement (3,699,998 / 3,700,000, the
two VOIDs the only failures).

✅ **CONFIRMED 2026-09-20 — THE PREDICTION HELD TO THE CASE.**  Full-suite run,
**355 forms, 0 errors**:

```
TOTAL: 3699998/3699998 full (cycles 3699998, arch 3699998)  [2 documented pre-existing excluded]
```

The bracket reads **2**, not 3 — the two `VOID` entries and nothing else, which
is the removal's own falsifier: had the `EDGE` entry survived the edit it would
read 3, and had the un-exempted case regressed the numerator would be 3,699,997.
Log retained at `sw/testdata/edge-removal/v03_confirm.log`, sha256 `644a11c5e09f38ed…`.
**This figure is now MEASURED and quotable with that artifact.**

## E — ⚠⚠ THE EMITTER AND THE SCORER ARE IN DIFFERENT IMAGE ERAS, AND NO GATE SEES IT (WAVE 24, 2026-09-20)

**THIS IS NOT ONE OF THE FIVE REGISTERS AND IT DOES NOT PRETEND TO BE.**  It is
not an **INV** — no rig defect is alleged and no capture is false; not a **SUP**
— no population is superseded and nothing came back with a flag; not an **EXC**
— no seed leaves any numerator; not an **ERR** — no derived column is wrong; not
a **RET** — nothing is retired.  **What it records is a CAPABILITY that is gone
and that nothing measured until it was needed.**

### WHAT WAS ATTEMPTED

WAVE 24 was authorised by the user to **re-capture the two `VOID` goldens of
§D from silicon** — `0F1B`/3917 and `83.5`/8683 — with a non-colliding layout,
and retire the exemptions.  The collision was first **re-derived from the banked
cases alone, with no engine** (`sw/testdata/wave24/b1_collision_proof.py`), and
it reproduces `v03_divergence_ledger.md` F4bc byte for byte:

```
0F1B/3917  code phys dc33, preload span dc2f..dc32 = 63 c0 63 c0
           operand EA = DS*16+BW+IY = dc30   want 89 -> image holds c0   COLLIDES
                                      dc31   want 11 -> image holds 63   COLLIDES
83.5/8683  code phys 979b, preload span 9797..979a = 63 c0 63 c0
           operand EA = DS*16+BW    = 9799   want a7 -> image holds 63   COLLIDES
                                      979a   want a4 -> image holds c0   COLLIDES
```

**THE CLAIM IS CONFIRMED THREE TIMES OVER** — the 2026-07 ledger text, WAVE 22's
measured `exp 0x63C0` rows, and now this arithmetic.

Both indices were then re-emitted from the **socket** (`emit_suite reemit
--validate`, `EMIT_USE_CORE` False, divider readback `div=8 (4 MHz), commanded
by this connection`).  Both came back **`neither`** — the emitter's own
flat-validity gate saying *neither a flat nor a 64K-mirrored replay reproduces
this golden*.

### WHAT THE CONTROL SAID — **`neither` IS NOT ABOUT THESE TWO CASES**

`sw/testdata/wave24/b1_control.py`, seven ARBITRARY v0.3 indices, emitted in
memory and **never written into the suite**:

```
88/100  neither   01/200  neither   8B/300  resolved
83.5/100 neither  0F1B/100 neither  88/101  neither   01/201 resolved
```

**FIVE OF SEVEN ORDINARY INDICES ARE UNREPLAYABLE TOO.**  And the other
direction, offline, no board (`sw/testdata/wave24/b1_era.py`):

```
_flat_mirror_check on 18 BANKED v0.3 cases (88, 01, 8B)   ->  {'flat': 18}
```

**18 of 18 banked cases replay perfectly; 5 of 7 freshly captured ones cannot.**
The difference is not the case.  **It is the era of the image the case was
captured in.**

### THE ERA SIGNATURE, IN THE ARTIFACTS THEMSELVES

```
banked 88   : cases carrying a 0xCC byte    88/10000   carrying a 0x90 byte 10000/10000
banked 01   :                              131/10000                        10000/10000
banked 8B   :                              123/10000                        10000/10000
banked 0F1B :                              107/10000                         9999/10000
banked 83.5 :                              138/10000                         9999/10000

0F1B/3917  banked 2026-07: has 0x90, no 0xCC   captured today: has 0xCC, no 0x90
83.5/8683  banked 2026-07: has 0x90, no 0xCC   captured today: has 0xCC, no 0x90
```

and in the failing rows themselves — the diverging column **is the fill word**:

```
83.5/8683 banked  row 0  ... data 37008 = 0x9090 ...   (PASV Ti, retained bus)
83.5/8683 today   row 0  ... data 52428 = 0xCCCC ...
```

### THE NAMED CANDIDATE CAUSE — **stated as a candidate, with its falsifier**

* `sw/testimage.py:63` — **`CODE_FILL = 0xCC`** (INT3).  The fuzz-v2 composer
  fills the image with INT3 so a runaway traps to the terminator; the v1
  composer the v0.3 suite was emitted under used **`0x90`** (NOP) and a
  fall-through store stub.
* `hdl/tb/tb_v30_core.sv:1072` — the batch scorer's memory is
  **`for (i = 0; i < 1048576; i++) mem[i] = 8'h90;`**, an unconditional
  literal.  The `+scr` script path has a `fill` token (`:934`); **the `+batch`
  path, which every golden suite is scored through, has none.**

> **A GOLDEN CAPTURED TODAY IS SCORED AGAINST A DIFFERENTLY-FILLED MEMORY.**
> Every byte the chip touched inside the window is recorded in the case, so the
> case is not wrong; what is not recorded is the **pre-window retained bus** and
> the fill the part saw around the window, and those are 0xCC on the board and
> 0x90 in the testbench.

**FALSIFIER, REGISTERED**: change the `+batch` path's fill to `8'hCC` (an `hdl/`
edit, forbidden in WAVE 24) and re-run both legs.  If the cause is named
correctly the two fresh captures replay **`flat`** and the 18 banked ones stop
replaying.  Until that is run, the cause is a CANDIDATE and is quoted as one.

### THE DISPOSITION TAKEN

**THE SUITE WAS RESTORED BYTE-IDENTICAL AND THE TWO EXEMPTIONS STAY.**

```
sha256 BEFORE  7e1f444cb318...  tests/v30/v0.3/0F1B.json.gz
               8e7824acc4e3...  tests/v30/v0.3/83.5.json.gz
sha256 AFTER   7e1f444cb318...  /  8e7824acc4e3...      IDENTICAL
```

Shipping the replacements would have swapped a **documented, understood,
independently re-derived** golden defect for an **undocumented failure caused by
the instrument**, and would have moved `v0.3`'s published figure on the strength
of a capture the scorer cannot read.  **`v0.3` stays `3,699,998 / 3,699,998
[2 documented pre-existing excluded]`**, and WAVE 24's registered prediction of
`3,700,000 / 3,700,000` is a **REGISTERED MISS, reported as registered**
(`docs/notes/suite_divergence_prereg_2026-09-20.md` P-B1b/c).

**NOTHING IS DESTROYED.**  The originals are archived byte-identical at
`sw/testdata/wave24/void-archive/` (`*.json.gz.orig`, on disk beside a suite
that is itself disk-only, with `SHA256-BEFORE.txt` and
`SHA256-AFTER-RESTORE.txt` committed), the two original cases are committed in
full as `original-cases.json`, and **the two re-captures are true silicon and
are RETAINED** at `recaptured-2026-09-20.json` — outside the suite, with their
full per-clock rows, their divider readback and their truth-source stamp.

### WHAT THIS COSTS, STATED PLAINLY

**`tests/v30/v0.3` (3,700,000 cases) and `tests/v30/v0.2` (347,000) CAN NO
LONGER BE EXTENDED, REPAIRED OR RE-EMITTED** while the two eras disagree.  The
suites still score, because the cases on disk were captured in the era the
scorer implements.  **A capability that only fails when it is used is a
capability nothing gates**, and this one had been gone for an unknown length of
time before a wave needed it.

## D — `tests/v30/v0.3/known_divergences.json` — MEASURED, NOT EDITED

Its three entries were established against **`8fd94df` / `4508e08`** (2026-07-25);
`git ls-tree 4508e08 hdl/rtl/` lists `core` and **no `ucore`**.  **It is the
ARCHIVED FSM CORE's accepted-residue list**, inherited by the ucore and never
re-tested — including by `ucore_gaps_2026-08-04.md` §F.3.

| entry | class | measured on the ucore |
|---|---|---|
| `0F1B`/3917 | VOID | **FAILS** — and its expected data is literally `0x63C0`, the PRELOAD bytes.  **The VOID claim is INDEPENDENTLY RE-DERIVED** |
| `83.5`/8683 | VOID | **FAILS**, same signature.  Claim re-derived |
| `646F`/8988 | EDGE | ✅ **PASSES 10,000/10,000 — THE EXEMPTION IS OBSOLETE** |

**THE FILE IS UNEDITED AND NO ENTRY IS REMOVED.**  One sitting's reading is not
grounds to change another's denominator, and removing the `EDGE` entry would
move `v0.3`'s published denominator on a single wave's authority.
`sw/check_core.py --no-known-divergences` exists so the question can be re-asked
by anyone, at any time, without editing a list.
