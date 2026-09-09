# WAVE 8 — **THE FRONT END: ANATOMY, THEN ONE MEASURED LEVER.**  THE PRE-REGISTRATION.

Committed **BEFORE THE FIRST QUARTUS STAGE OF THIS WAVE**.  Instruments
`05211a1959`, committed before this document.

**MEASUREMENT ONLY.  NOTHING IS LANDED IN THE CORE.  NO RTL UNDER
`hdl/rtl/ucore/` IS EDITED.**  **OFFLINE ONLY — NO BOARD, NO FLASH, NO
BITSTREAM.**  No Codex consulted.  No nested subagent spawned.  This document
is **NOT A GATE**, it writes **no receipt**, and **no figure produced under it
may be quoted as a pass**; `docs/notes/standing_gates.md` §A governs every
timing figure — **one green build is not closure, and the same tree has drawn
19.42 and 45.91 MHz.**

---

## §0 WHERE THE CAMPAIGN STANDS, AND WHY THE TARGET MOVED

**USER RULING 2026-09-08, verbatim: *"I don't want custom sdc rules,
period."***  The no-exception build is the goal state.  It is not re-opened
here.

| | CONTROL | RETENTION |
|---|---:|---:|
| no-exception `worst-of-5`, after WAVE 7 | **28.32 MHz** | **28.90 MHz** |
| the bar | 32.0 | 32.0 |
| **the gap** | **3.68** | **3.10** |

The arc is **~35.3 ns** and must reach **~29.6**: **about 5.7 ns remain.**

**WAVE 7 MOVED THE BINDING STRUCTURE.**  The chain is no longer it.  On all
five no-exception CONTROL draws and both configurations the binding path
launches and lands inside the microcode ROM
(`chainflat_landing_results_2026-09-09.md` §6.1, §6.2).  **The front end has
never been attacked by any wave.**

### 0.1 THE METHOD THIS WAVE INHERITS, AND THE ONE IT REFUSES

* **A DIFFERENCE BETWEEN TWO IDENTICALLY-COMPILED BUILDS TRANSFERS.**  WAVE 6
  predicted **−9.431 ns** out of context; WAVE 7 realised **−9.413** in the
  design.  **Correction +0.018 ns = 0.2 %.**
* **A PARTITION PREDICTION DOES NOT.**  WAVE 5's uncut estimates mispredicted a
  realised downstream half by **+11.3 … +20.0 ns** and the loop by **+15.30**.

**So: a standalone A/B may be used for a DELTA.  It may NOT be used to predict
a SPLIT.**  Both figures are quoted verbatim beside every standalone number
this wave produces (bar H-4).

### 0.2 ⚠ **THE ROW TABLE IS NOT RE-TRIED, AND THIS SECTION IS THE STATEMENT THE BRIEF ASKS FOR**

WAVE 3 landed the registered ROW table, measured **+0.36 MHz**, and its own
registered bar **L-8 FIRED**: on 3 of 10 goal-state draws the worst
`ce → ce` path **ENDS AT `row_q`** — the new `upc → ucdecode → ucrom → row_q`
D-pin class **BINDS** (`l2_registered_row_results_2026-09-08.md` §5.1).  The
mechanism of the refutation is that **the two ROMs and the EU's chain are a
LOOP, not a series chain** (§5.2), so registering a table relocates the cut
without shortening the loop.

**THAT REFUTATION IS INDEPENDENT OF THE CHAIN AND SURVIVES WAVE 7**, because
the loop still closes: `row → front end → chain → upc_*_n → dec_addr_next →
ucdecode`.  WAVE 7 shortened one arm of the loop; it did not open it.
**THIS WAVE DOES NOT RE-TRY IT AND WILL NOT PROPOSE IT AS A CANDIDATE**, and
if the anatomy names a candidate whose mechanism is *"register a microcode
table output"* in any form, **it is declared REFUTED-BY-WAVE-3 and excluded
before it is ranked**, with the exclusion printed.

---

## §1 STEP 0 — **THE MARKER RULE, COMMITTED BEFORE THE TOOL IS RUN (H-2)**

`sw/sta_chain_anatomy.tcl` REFUSES on the landed tree at PC-3 (*`st_zero_ok`
pins in the netlist: 0*).  WAVE 7 deliberately did not pick a replacement,
recording that **choosing a marker after seeing the refusal is fitting-shaped.**

**THE RULE — the whole of it, in one sentence, and it is already in the tree at
`05211a1959`:**

> A base name is a **CHAIN-POSITION BOUNDARY MARKER** if and only if it is
> **(i)** READ by a chain position's ENTRY GUARD in the chain pass of
> `hdl/rtl/ucore/v30u_eu.sv`, **AND** **(ii)** ASSIGNED inside a chain ARM
> BODY.

Clause (i) is what makes it a boundary; clause (ii) is what makes it
**loop-carried** — a name a guard reads but no arm writes is an INPUT to the
whole pass, not a carrier between positions, and cannot separate two positions.
It is a rule about the SOURCE and it names no netlist node.

> ### ⚠ **THE RULE DOES NOT PICK A NEW MARKER.  IT PICKS THE SAME ONE TWICE.**
>
> Evaluated on the PRE-landing tree (`aba01feb07`) **and** on the landed tree it
> gives the identical set **`{st_n, stop}`** — WAVE 5's set **minus
> `st_zero_ok`**, which is a *function* no arm assigns and was therefore never a
> carrier.  **WAVE 7's refusal was a defect in PC-3's PIN SELECTION** (it forced
> its control path through an `st_zero_ok` pin specifically), **not in the
> segmentation.**

The repair is therefore to the CONTROL, and it is **WAVE 5's own PC-4 repair
pattern applied to PC-3**: try each marker's pins **ONE AT A TIME**, **NAME**
the pin that answered, and **PRINT EVERY MARKER'S PIN COUNT INCLUDING THE
ZEROS** — with `st_zero_ok` printed beside them as a named known-absent control,
so the WAVE 7 condition stays visible instead of becoming invisible.

### 1.1 THE RULE'S OWN CONTROLS — ALL PASS, AND THREE OF THEM MISSED FIRST

Run offline, no Quartus in the loop, against WAVE 7's **committed** pre-landing
artifacts (`sw/testdata/chainanat-wave7-prelanding/`).  Full text in
`sw/frontend_srcmap.py`; the misses are recorded in the code beside the lines
that fix them and in `05211a1959`'s message.

| control | bar | verdict |
|---|---|---|
| **PC-M0** | `chain_srcmap` still recovers 33 arms / 24 guarded / 9 == `st_zero_ok` | **PASS** |
| **PC-M1** | the rule gives `{st_n, stop}` on BOTH trees | **PASS** |
| **PC-M2a** | boundary COUNT identical to WAVE 5's marker set on **4 of 4** committed pre-landing draws | **PASS** |
| **PC-M2b** | with the `st_zero_ok` arrival points DELETED from the stream, the two marker sets give **byte-identical** segmentations | **PASS** |
| **PC-M2c** | ⚠ **THE ORIGINAL BAR, STILL COMPUTED AND STILL PRINTED**: raw-stream segmentations identical on **2 of 4**; max \|Δcut\| **1.135 ns**, which is exactly one `st_zero_ok` cell | **REPORTED** |
| **PC-M3** | a marker that does not exist gives **0** boundaries | **PASS** |
| **PC-S1** | the STAGE rule reproduces WAVE 5 §5(a)'s FRONT-END / CHAINABLE partition on 10 of 10 names — from the SOURCE where WAVE 5 got it from the NETLIST | **PASS** |
| **PC-S2** | an invented signal classifies `UNMAPPED` | **PASS** |
| **PC-S3** | the `BIU` / `ROMHEAD` / `OUTSIDE` hierarchy overrides fire | **PASS** |

⚠ **PC-M2's FIRST FORM WAS AUTHORED, RUN AND MISSED, BEFORE ANY QUARTUS STAGE
OF THIS WAVE EXISTED.**  It is restated as M2a/M2b/M2c and **the original form
is still computed and still printed on every run** — a bar that is replaced
silently is a bar that was softened.  The miss is diagnosed to ONE NAMED CELL
and the diagnosis is itself the M2b test.  **On the landed tree the question is
moot: `st_zero_ok` has 0 pins.**

---

## §2 STEP 1 — WHAT WILL BE MEASURED

**Configuration: NO-EXCEPTION** (the goal state).  The CE multicycle is deleted
from `hdl/nec_test.sdc` for the measurement fits only and restored by the
driver's `finally`; **no SDC change is landed and the USER RULING is not
re-opened.**  **3 CONTROL seeds + 1 RETENTION seed as a cross-check**, at
WAVE 7's HEAD (`8deb1e7d8e`).  **MAP ONCE PER CONFIGURATION, FIT ONCE PER
SEED.**

Registered deliverables:

* **A** — the worst `ce → ce` path, **segment by segment**, with the ROM head,
  the row decode, the operand / EA select and everything else the source-derived
  STAGE rule names, **named separately**.
* **B** — a **NET CENSUS OVER A POPULATION** of endpoint-diverse paths
  (`-nworst 1`, 400 per draw), not one path, reported **STRICT** and
  **CARRY-FORWARD**, with the **tree-property / draw-property split stated**
  (WAVE 5's E-2).
* **C** — **is the `q_cnt → q_ripe_lead_n` BIU ROUND TRIP still on the arc, and
  what is it worth now?**  WAVE 5 measured **2.70 – 2.89 ns on 2 of 4 draws**,
  pre-flattening.  Reported as: presence on the worst arc, presence RATE over
  the population, and mean/max span.
* **D** — **does `S_EA_CALC`'s 8-way `gpr_n` read still cost anything?**
  WAVE 6 folded six register-file reads into one; the survivor may or may not be
  on the path.  Reported as the `ARRAYMUX` class's presence rate and ns.

### 2.1 THE STAGE RULE (also committed at `05211a1959`)

First match wins: `|u_biu|` → **BIU**; `|u_ucrom|` → **ROMHEAD**; outside
`|u_eu|` → **OUTSIDE**; base name assigned in a chain arm file → **CHAIN**;
assigned in exactly one `//====` **BANNER SECTION** of `v30u_eu.sv` → that
section's own title; more than one → **AMBIG**; a `Ram<N>` → **ARRAYMUX**; a
Quartus synthesised name → **ANON**; otherwise **UNMAPPED**.

The banner sections are **the file's own declared structure**, written by the
authors long before this wave, so the partition is not this wave's invention and
cannot be tuned to a result.  A base name `B` is looked up as `B` **and** as
`B_n` — the module's own declared naming law (*"One `_n` per state register"*).

⚠ **40 – 46 % OF THE ARRIVAL POINTS ON WAVE 7's COMMITTED PRE-LANDING ARCS
CARRY NO RTL IDENTIFIER AT ALL.**  That is a real limit of the instrument.  The
STRICT census reports them as `ANON`; the CARRY-FORWARD census attributes each
to the next NAMED node downstream, **and is labelled a READING on every line it
appears on**, exactly as WAVE 5 labelled its "segment 0 read in two".

---

## §3 STEP 2 — HOW CANDIDATES WILL BE RANKED.  **REGISTERED BEFORE THE FIRST FIT.**

A candidate is admitted only if **all four** hold, and the admission test is
applied **before** any candidate is ranked:

1. it is a **single named RTL mechanism** in `hdl/rtl/ucore/`, not a net name
   (WAVE 1 §6 item 1: *a Quartus net name is not by itself an RTL seam*, and
   WAVE 2 REFUTED exactly that identification for `Decoder28#1`);
2. it is **not** *"register a microcode table output"* in any form (§0.2);
3. it is **not** a `ce`/`ce_half` phase split (WAVE 2 and WAVE 4, both RED;
   WAVE 5 §9.1 measured why);
4. it does not require a custom SDC rule (USER RULING 2026-09-08).

Admitted candidates are ranked by **MEASURED mean ns per path over the
population, on the CARRY-FORWARD census**, with the STRICT figure and the
per-draw min..max printed beside it as the uncertainty (H-4).  **Plausibility
is not a ranking key and is not a tie-break.**  Ties are broken by **presence
rate over the population** (a stage on 90 % of paths is a tree property; a stage
on 20 % is a draw property).

> ### **THE REGISTERED STOP CONDITION**
>
> **If no admitted candidate is worth ≥ 1.5 ns, the wave SAYS SO AND STOPS AT
> STEP 2.**  That is a real result, it is reported as one, and the user decides
> what follows.  **A candidate will not be promoted by lowering this number
> after seeing the table.**

---

## §4 STEP 3 — THE STANDALONE A/B, IF IT IS REACHED

WAVE 6's shape **exactly**, and no other:

* two arms — **REF**, a `diff -r`-verified byte-identical copy of
  `hdl/rtl/ucore/`, and **ARM**, the same tree with **ONE** substitution
  generated mechanically;
* **outside `hdl/rtl/ucore/`** (H-5), under `~/.cache/ucsimt-tmp/wave8/` with
  the artifacts copied to `sw/testdata/frontend/<label>/`;
* `v30u_eu` as its own top with virtual pins, same device `5CSEBA6U23I7`, same
  effort, **no `set_multicycle_path`**, `create_clock -period 31.250`;
* **MAP ONCE PER PROJECT, FIT ONCE PER SEED, ≥ 5 SEEDS**;
* an **EQUIVALENCE GATE** before any delay figure is quoted:
  `check_core --core ucore --opcodes all --cases 0` **169,000/169,000** on both
  arms and **four byte-identical `chain_lfsr_gate` signatures**;
* a **POSITIVE CONTROL THAT REPRODUCES A KNOWN IN-SITU FIGURE** before any
  comparison is quoted — registered here as: **the REF arm's mean worst
  reg → reg data delay must land within ±15 % of this wave's own in-situ
  no-exception `ce → ce` arc mean**, and the two figures are printed side by
  side.  A miss is reported as a miss and the comparison is not quoted.

The delta is reported **with its uncertainty** (per-seed spread on both arms)
and with **WAVE 6's 0.2 % and WAVE 5's +11.3 … +20.0 ns both quoted beside it**
(H-4).

⚠ **AT MOST ONE PROTOTYPE DELTA.  NOTHING IS LANDED IN THE CORE (H-6).**

---

## §5 THE BARS

| bar | statement |
|---|---|
| **H-1** | **EVERY CLASSIFIER CARRIES A POSITIVE CONTROL, REPORTED FIRST.  A MISS VOIDS THE WAVE.**  Bulk `-through` collections are the known trap (WAVE 5 §1.1): every `-through` is ONE PIN, the pin that answered is NAMED, and the bulk form is kept and PRINTED beside it as the known-wrong control. |
| **H-2** | The segmenter's marker rule is **COMMITTED BEFORE** the tool is run against the post-flattening netlist.  **MET at `05211a1959`, and this document restates it.** |
| **H-3** | The anatomy is reported over a **POPULATION** and **across seeds**, with the **tree-property / draw-property split stated**. |
| **H-4** | Every candidate's figure carries its **uncertainty** and, if it came from a standalone project, the **out-of-context caveat with WAVE 6's 0.2 % and WAVE 5's +11.3 … +20.0 ns both quoted**. |
| **H-5** | `git status --porcelain hdl/` shows **NO tracked modification at start and at end.**  Any SDC change for a measurement fit is reverted and never committed.  Standalone A/B arms live **OUTSIDE `hdl/rtl/ucore/`**. |
| **H-6** | **NOTHING IS LANDED IN THE CORE.**  The wave ends with a measured, ranked list and at most one prototype delta. |

### 5.1 THE CONFIGURATION CHECKS, WHICH ARE NOT OPTIONAL

* **The multicycle deletion must have reached the compiler**: `sta_truefmax_
  probe.tcl`'s `SAME` class must read **k = 1.0000** on every draw.  A draw whose
  `SAME` still reads 2.0 was fitted to the exception and answers a different
  question; it is discarded and said so.
* **The seed must have reached the fitter**, read back from Quartus's own
  *Fitter Initial Placement Seed* row.
* **The retention macro must be proved POSITIVELY**, not by the flag.

### 5.2 DISCIPLINE

Single-writer guard by EXACT binary name before every Quartus stage;
`hdl/nec_test_ucore.qsf` `git checkout --`'d between runs (the declared §70.7
exemption); `~/.cache/ucsimt-tmp/` for every intermediate, nothing large in
`/tmp`; `git add` by explicit path only and **never `git add -A`**; **there are
~18 pre-existing modified files in the working tree that are NOT this wave's
and not one of them is touched.**

---

## §6 THE DEBT THIS WAVE RECORDS AND DOES NOT DISCHARGE

⚠ **A FABRIC CONFIRMATION IS OWED AND UNPAID.**  WAVE 7 changed the EU's
decode and **nothing has been on a board**.  Every fabric figure in this repo
was taken on **FLASH #21 or earlier** and **may not be quoted against this
tree**.  The user has chosen to proceed to the front end first.  **Recorded, not
discharged.**

---

## §7 WHAT WOULD MAKE THIS WAVE'S ANSWER A NULL, WRITTEN BEFORE THE ANSWER

If the census puts the remaining nanoseconds in stages with **no single named
RTL mechanism** — a broad `ANON` mass, or one `AMBIG` class, or the ROM head's
own M10K clk→q, which is a device property and not an RTL one — then **there is
no lever ≥ 1.5 ns to take to STEP 3**, and this wave's deliverable is the ranked
table plus that sentence.  **The document will say that in those words.**
