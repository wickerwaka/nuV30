# THE ce/ce_half PHASE-SPLIT ANATOMY — WAVE 1

**MEASUREMENT ONLY. OFFLINE ONLY. NO BOARD. NO FLASH. NO BITSTREAM PROGRAMMED.**

**NOTHING UNDER `hdl/rtl/` OR `hdl/nec_test.sdc` IS TOUCHED BY THIS WAVE.**
`git status --porcelain hdl/` showed **0** tracked modifications at the start
and must show 0 at the end. (Untracked `hdl/quartus_gate_*.log` files predate
the wave.)

**THIS IS NOT A GATE AND IT PRODUCES NO RECEIPT.** It may not be quoted as a
pass. The quotable Fmax numbers come from `sw/quartus_gate.py`, and
`docs/notes/standing_gates.md` §A governs every timing figure in it.

| | |
|---|---|
| **Tree** | `c0633d7685` (`master`), instrument at `ce9caea6b0` |
| **Instrument** | `sw/sta_phase_split_scan.tcl`, driver `sw/run_phase_split_anatomy.sh` |
| **Tool** | Quartus 17.1.0 Lite Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns |
| **Artifacts** | `sw/testdata/phasesplit/<label>/` |

---

## §0 HEADLINE

*(filled in after the run — this document is committed as a PRE-REGISTRATION
before the draws are taken, and the results sections are appended to it.)*

---

## §0.1 THE QUESTION, AND THE THEOREM IT RESTS ON

The V30 ucore has two clock-enable phases, `ce` and `ce_half`, and does all its
work on `ce`. `ce_half` has **exactly one** consumer, `v30u_biu|t1_half2`.
Closing timing therefore needs a `set_multicycle_path -setup 2 -hold 1` on
2,200 core registers (`hdl/nec_test.sdc`), and every downstream integrator must
re-derive and copy it — `docs/notes/m72_downstream_timing_2026-08-12.md` §1 is
the measured cost of that.

The campaign's hypothesis is that the binding `ce -> ce` cone can be **SPLIT
ACROSS THE TWO PHASES**: a first stage evaluated in the `ce -> ce_half` window
and captured on `ce_half`, a second stage evaluated in the `ce_half -> ce`
window and captured on `ce`. One 2-period arc becomes two 1-period arcs and the
multicycle exception is **DELETED**, at unchanged Fmax and unchanged behaviour.

> **THE THEOREM.** A node in the `ce -> ce` cone that is outside every input
> pin's combinational fanout depends only on registers that commit on `ce`. Its
> value is therefore CONSTANT ACROSS THE WHOLE CPU CYCLE — identical at
> `ce_half(n)` and at `ce(n+1)`. Capturing it on `ce_half` and consuming it on
> `ce` is bit-exact by construction and moves no pin on any clock.

This is L1's argument (`hdl/rtl/ucore/v30u_eu.sv`, "L1 — THE DECODE IS TAKEN ON
THE EDGE THAT MAKES ITS ADDRESS", and `docs/notes/adcone_l1_results_2026-08-13.md`)
**one PHASE over instead of one CLOCK early**. It needs **no new contract
clause**: `S-1` (*at least one `ce_half` falls between consecutive `ce`s*) is
already asserted in `hdl/rtl/ucore/v30_core.sv` and is already load-bearing for
`t1_half2`, and a stage-1 capture is idempotent for exactly the reason extra
`ce_half`s are harmless today.

**WAVE 1's JOB IS TO MEASURE WHETHER A CUT THAT DOES THAT EXISTS, AND IF SO
WHERE.** It chooses no design and writes no RTL.

---

## §0.2 THE INSTRUMENT TRAP THIS INSTRUMENT CARRIES A PERMANENT CONTROL AGAINST

`get_timing_paths -through` **SILENTLY IGNORES a collection produced by
`get_nodes`** in Quartus 17.1. It returns *no path* for every node, including
nodes that demonstrably ARE on a path. Measured on this tree, on the node
`emu|system_large|u_core|u_biu|ann_kill~0|combout` with a `-from`/`-to` pair
known to have a path through it:

| resolver | collection size | paths returned |
|---|---:|---:|
| `get_nodes` | 1 | **0** ← WRONG, and SILENT |
| `get_pins` | 1 | 1 |
| `get_nets` | **0** for this name | — |
| `get_cells` | **0** for this name | — |

The coordinator's first version of the scan used `get_nodes` and reported *"all
50 nodes are register-only"*. **IT WAS ENTIRELY VACUOUS.** This is the vacuous-gate
pattern (`standing_gates.md`, *Meta-finding: the vacuous-gate pattern*) in its
purest form: an instrument that cannot say NO.

⚠ Note the second half of the table, which the coordinator's report did not
carry and which matters for the resolver ladder: on **this** node name
`get_nets` and `get_cells` return an EMPTY collection, not a working one. The
brief's "falling back to `get_nets`" is therefore a fallback that will rarely
fire; `get_pins` is the resolver, and every node whose classification is used is
recorded with the resolver that answered it (§3's RESOLVER CENSUS).

The instrument's answer is **§A, THE POSITIVE CONTROL, WHICH GATES EVERYTHING
ELSE**: take the worst `live -> $v30u_ce` path — pin-dependent end to end BY
CONSTRUCTION — walk its own data nodes, and re-ask the classifier the same
`-through` question of each. Every one must come back pin-dependent. **If it
does not, the script prints `CONTROL FAILED` and REFUSES to emit any scan
result** (exit 4).

The two legitimate exclusions are **the clock network** and **the destination
register**, and they are excluded **BY RULE, not by fiddling until the number is
clean**: the walker splits each path's arrival points into CLK / LAUNCH / DATA /
DEST phases by matching against the path's OWN `-from` and `-to` names, so the
clock network is *everything at or before the launch register* and the
destination is *everything at or after the `-to` node*. A path on which the
walker finds fewer than 3 data cells FAILS THE CONTROL — a control with nothing
to classify passes vacuously, and it does not.

---

## §0.3 TWO INSTRUMENT DECISIONS THAT ARE FINDINGS IN THEMSELVES

**(a) THE CENSUS IS OCCURRENCE-INDEXED (`net#N`).** `st_n`, `ld_b_n`, `always6`
and `Ram*` each appear SEVERAL times on one path: the EU's chain loop is
UNROLLED (`v30u_eu.sv`'s `for (chain = 0; chain < CHAIN_MAX; ...)`, `CHAIN_MAX`
= 7, measured maximum occupancy 6) and every position is a fresh copy of the
same source line. A first-occurrence-only census would report ONE cut where the
netlist has three, and would report the FIRST one's split for all of them.

**(b) LIVE IS MEASURED TWO WAYS AND BOTH ARE PRINTED.**

* **`LIVE_NARROW`** — the registers that drive the core's asynchronous input
  ports, read off `hdl/rtl/system_large.sv`: `c_ready_q` / `c_int_q` / `c_nmi_q`
  / `c_polln_q` / `c_reset_q` (line ~371) and the read word, which arrives on
  the shared pads as `core_ad[15:0] = c_addrv_q ? c_rdata_q : 16'hzzzz`
  (line 491), plus `core_ad_hold` in a RETENTION build. **Note this differs from
  the coordinator's stated collection**, which named "the 36
  `nec_bus|ad_in_q[*]` read-data bits". `ad_in_q` is 20 bits wide
  (`nec_bus.sv:196`) and it does **not** drive a core port: it feeds
  `ad_drive`, which is a REGISTER inside `nec_bus`, so `ad_in_q` reaches the
  core only through `c_rdata_q` and is register-to-register. The named-driver
  set is the one that matches the RTL.
* **`LIVE_WIDE`** — **every register not in `$v30u_ce`**. This needs no name
  list at all, which is the SIMPLICITY answer, and it admits **`t1_half2`
  itself** — by construction a mid-cycle changer, so a `ce` register
  combinationally downstream of it is not phase-stable either. **A name-list
  instrument MISSES that**, and the control is run on both sets so the
  difference is visible rather than assumed.

---

## §1 THE DRAWS

Re-mapped at HEAD. The `hdl/db` on disk before this wave was built at
`f688db385b`, **two commits behind** `c0633d7685`, and both intervening commits
touch `v30u_eu.sv` (the REP CL==0 ALU-width fix `e61f2e0988` and the
REP-termination fix `c59d205479`). **Every figure in the coordinator's brief is
therefore indicative and not this tree's**, and this wave re-measures all of it.

* **CONTROL, seeds 1, 2 and 3** — the source of the choice.
* **RETENTION, seed 1** — **A CROSS-CHECK ONLY, NOT THE SOURCE OF THE CHOICE.**
  The `SAME` class is core-internal, so retention is not expected to move it;
  **if it does, that is a finding.**

### §1.0 THE DEVELOPMENT RUN, DECLARED

⚠ **A DEVELOPMENT RUN OF THE INSTRUMENT WAS TAKEN ON THE STALE `hdl/db`
(`f688db385b`) BEFORE THESE BARS WERE COMMITTED, AND IT SAW THE ANSWER.** It is
declared here rather than omitted, because omitting it would leave a reader
unable to tell fitting from pre-registration. Two things make it not a fit:

1. **The bars A-1…A-5 are the coordinator's, given verbatim in the wave brief
   before any run.** Nothing in them was chosen by the agent that ran the scan.
2. The development run's purpose was to (i) prove `get_pins` resolves and
   `get_nodes` does not, (ii) time the scan, and (iii) find the
   first-occurrence-census defect of §0.3(a) — which it did, and which is why
   the committed instrument is occurrence-indexed.

The development run's outputs are retained at
`sw/testdata/phasesplit/devrun-stale-f688db385b/` and are **NOT** scored against
any bar and **MAY NOT BE QUOTED** as a result of this tree.

---

## §2 WHERE THE DELAY IS ON THE WORST PATH

*(filled in after the run)*

---

## §3 THE PIN-DEPENDENCE SCAN — CONTROL FIRST

*(filled in after the run; the control's result is stated before anything else)*

---

## §4 THE CUT-POINT CENSUS

*(filled in after the run)*

---

## §5 WHAT THE ANATOMY SAYS THE DESIGN IS

*(filled in after the run)*

---

## §6 WHAT IS **NOT** MEASURED HERE

*(filled in after the run)*

---

## §7 THE REGISTERED BARS

**Pre-registered here, BEFORE the first draw of this wave. They are scored as
registered and reported as registered even where they miss.**

| bar | statement |
|---|---|
| **A-1** | The positive control reads **100 % pin-dependent on every non-excluded node, on 4 of 4 draws**. **A MISS HERE VOIDS THE WAVE** — report it and stop. |
| **A-2** | The binding class on each CONTROL draw is `ce -> ce` (**SAME**) at **k = 2**, reproducing `sw/testdata/g6dist/rep-int-term-control-20260820/`. ⚠ **It is at a DIFFERENT COMMIT, so exact agreement is NOT expected and is NOT the bar; the bar is that the CLASS is the same class.** |
| **A-3** | On **≥ 3 of the 4 draws**, the worst `ce -> ce` path is **100 % REG-ONLY** (0 pin-dependent nodes). |
| **A-4** | There EXISTS at least one **named net, REG-ONLY on every path it appears on and present on ≥ 50 % of the top-50 paths, whose upstream and downstream halves are each ≤ 60 % of that draw's worst `ce -> ce` data delay.** This is the cut's existence bar. |
| **A-5** | The worst `live -> core` path is **≤ 26.0 ns on every draw** (it bounds stage 2 no matter where the cut goes). |

> **A-4 MAY LEGITIMATELY MISS, AND A MISS IS A REAL AND VALUABLE RESULT.** The
> RTL's natural seams (block boundaries, chain positions) need not line up with
> the pin-dependence frontier. **A YES IS NOT TO BE MANUFACTURED.** If no
> balanced REG-ONLY cut exists, this document says so, says what the best
> available cut is and what it would cost, and stops. A wave that reports *"the
> cut does not exist where we hoped"* has done its job.

**DEFINITIONS, fixed here so they are not chosen after seeing a number:**

* **DATA DELAY** = arrival at the destination register **minus** arrival at the
  launch register's output pin. It EXCLUDES the ~9.2 ns clock-network arrival.
  Both are printed; every split in §4 and every A-4 verdict is on the DATA
  delay.
* **UPSTREAM** of a cut = data delay from the launch register's output to that
  net. **DOWNSTREAM** = the remainder to the destination register.
* **A-4 is scored on the MAX split over the paths a net appears on**, the strict
  reading; the MEAN split is printed beside it.
* **REG-ONLY** means the classifier found **no path** `live -> through(node) ->
  $v30u_ce` under `LIVE_NARROW`. An **UNRESOLVED** node (neither `get_pins` nor
  `get_nets` answered) is counted as **PIN-DEPENDENT**, never as register-only —
  an instrument's silence is not evidence.

