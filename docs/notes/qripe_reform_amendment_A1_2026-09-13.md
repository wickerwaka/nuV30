# WAVE 15 — **AMENDMENT A-1: Q-3 IS THREE COLUMNS, NOT ONE.  REGISTERED BEFORE THE FIRST QUARTUS STAGE AND BEFORE ANY ARM NETLIST EXISTS.**

The pre-registration (`qripe_reform_prereg_2026-09-13.md` §2.1) wrote Q-3 as a
single count: *`q_ripe_lead_n*` BY NAME on 0 of 200 arm paths against 200 of 200
on the base*.  Building the classifier against **WAVE 14's own committed rows**
— before this wave had a netlist of its own — showed that one column cannot
carry the question.  **This amendment is written from a CONTROL, not from a
result.**

## A-1.1 WHAT THE CONTROL SHOWED

`python3 sw/wave15_q3.py --selftest`, reading
`sw/testdata/wave14/w14-{base,tie,hold}/roundtrip_{control,retention}.rows.txt`:

| leg | Q-3a by name | Q-3b **EU→BIU→EU via `ripe`** | Q-3c **EU→BIU→EU, ANY BIU node** |
|---|---:|---:|---:|
| `w14-base` / control | **200** | **200** | 200 |
| `w14-base` / retention | **200** | **200** | 200 |
| `w14-tie` / control | 0 | 0 | ⚠ **115** |
| `w14-tie` / retention | 0 | 0 | 0 |
| `w14-hold` / control | 0 | 0 | 0 |
| `w14-hold` / retention | 0 | 0 | 6 → **0 as a round trip** (all six launch outside the EU) |

> ### ⚠ **`w14-tie`'s CONTROL NETLIST STILL CARRIES 115 OF 200 EU → BIU → EU ROUND TRIPS WITH `q_ripe_lead_n` ON NONE OF THEM.**  A bar written as *"no round trip"* would therefore have been **unmeetable by any mechanism, including WAVE 14's own behaviour-breaking probe**, and a bar written only as *"not by that name"* can be met by renaming a node.  Neither is the question.

## A-1.2 THE THREE COLUMNS, AND WHICH ONE IS THE BAR

* **Q-3a — BY NAME.** The unedited WAVE 14/WAVE 10 instrument's own `<ripe>`
  column.  ⚠ Its matcher is `string first "q_ripe_lead_n"`, a **SUBSTRING**
  test, so it matches this wave's `q_ripe_lead_n0` / `q_ripe_lead_n1` as well —
  **the mechanism cannot pass Q-3a by renaming the node.**  **BAR: arm 0,
  base 200.**
* **Q-3b — THE ROUND TRIP THROUGH THIS MECHANISM.** The path LAUNCHES in
  `u_eu`, ENDS in `u_eu`, carries a BIU node in its DATA SECTION **and** carries
  `q_ripe_lead_n*`.  This is the shape C1 claims to convert into a
  BIU-register-launched path.  **BAR: arm 0, base 200.**
* **Q-3c — THE RESIDUAL.** EU→BIU→EU through **any** BIU node.
  **REPORTED, EXPLICITLY NOT GATED**, and its base and arm figures quoted
  side by side.  A nonzero arm reading is a *finding about the tree*, not a
  failure of this mechanism, and WAVE 14's `w14-tie` control is the precedent
  that says so.

**THE POSITIVE CONTROL IS MANDATORY AND IS PRINTED FIRST**: the BASE arm's rows,
scored by the same classifier in the same invocation, must read **200/200 on
Q-3a AND Q-3b** or nothing below may be quoted (the tool exits 4).

## A-1.3 THE INSTRUMENT IS POST-PROCESSING ONLY

`sw/wave15_q3.py` **runs no STA and edits no `.tcl`.**  It reads the
`*.rows.txt` that `sw/sta_biu_roundtrip.tcl` — **WAVE 10's, unedited** — writes,
and derives Q-3a/b/c from the columns already in it (`<ripe>`, `<biu_data>`,
`<from>`, `<to>`).  That is the WAVE 14 precedent obeyed: *changing an
instrument in the wave that measures with it is how a result gets chosen.*

## A-1.4 TWO NON-VACUITY DEMONSTRATIONS OF THE RTL FALSIFIER, AND ONE THAT DID NOT FIRE

The mechanism's own falsifier (`v30u_biu.sv`, `ifndef SYNTHESIS`, two clauses,
checked at every `ce`) is demonstrated able to fail:

| perturbation | clause | result |
|---|---|---|
| `--nonvacuity` — one term of `q_ripe_lead_n1` moved from `grn_ttl == 1` to `grn_ttl == 2` | **(1) the identity** | **FIRES** on `FA` at 4,685,000: *"composed=0 reference=1 (pop_eff=1 q_cnt=2 q_cnt_np=3 grn_n=2 grn_ttl=1)"* |
| `--nonvacuity3` — `pop_eff` armed from `q_pop` alone | **(2) the select** | **FIRES** on `FA` at 85,000: *"pop_eff=1 but q_pop=1 q_ripe=0 q_flush=0"* |
| `--nonvacuity2` — the flush's `pop_eff = 1'b0` deleted | (either) | ⚠ **DID NOT FIRE — `check_core --opcodes all` reads 169,000/169,000 with the term removed.**  **The pop/flush coincidence is NOT REACHED by the 169,000-case golden population.**  Recorded as measured.  The `!q_flush` term is kept because the flush provably overwrites the count; it is simply not exercised there. |

**A falsifier that cannot fail is not a falsifier, and the third row is
reported because it is what was measured, not what was expected.**

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
