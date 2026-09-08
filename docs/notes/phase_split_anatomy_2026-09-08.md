# THE ce/ce_half PHASE-SPLIT ANATOMY — WAVE 1

**MEASUREMENT ONLY. OFFLINE ONLY. NO BOARD. NO FLASH. NO BITSTREAM PROGRAMMED.**

**NOTHING UNDER `hdl/rtl/` OR `hdl/nec_test.sdc` IS TOUCHED BY THIS WAVE.**
`git status --porcelain hdl/` showed **0** tracked modifications at the start
and **0 at the end**, and `git diff c0633d7685..HEAD -- hdl/` is **EMPTY**:
`hdl/` is byte-identical to the tree the wave measured. (Untracked
`hdl/quartus_gate_*.log` files predate the wave and no new untracked file was
left under `hdl/`.)

⚠ **ONE FILE UNDER `hdl/` DID MOVE DURING THE RUN AND WAS RESTORED:
`hdl/nec_test_ucore.qsf`.** Quartus rewrites the revision `.qsf` it compiles,
appending ~182 lines of pin assignments — this is the DECLARED §70.7 exemption,
the same one `sw/testdata/g6dist/…/distribution.json`'s `E7_input_stability`
bar names as its single permitted mover. It was restored with
`git checkout -- hdl/nec_test_ucore.qsf` after the last draw. Recorded because
a file that moves and is put back is still a file that moved.

**THIS IS NOT A GATE AND IT PRODUCES NO RECEIPT.** It may not be quoted as a
pass. The quotable Fmax numbers come from `sw/quartus_gate.py`, and
`docs/notes/standing_gates.md` §A governs every timing figure in it.

| | |
|---|---|
| **Tree** | `c0633d7685` (`master`), instrument at `ce9caea6b0` |
| **Instrument** | `sw/sta_phase_split_scan.tcl` (fixed at `c2a4f42eef` — §3.0), driver `sw/run_phase_split_anatomy.sh`, attribution `sw/sta_phase_split_frontier.tcl` |
| **Tool** | Quartus 17.1.0 Lite Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` 31.250 ns |
| **Artifacts** | `sw/testdata/phasesplit/ctl/` (seeds 1-3), `sw/testdata/phasesplit/ret/` (seed 1), `sw/testdata/phasesplit/ctl-DEFECTIVE-WALKER/` (retained, quoted nowhere), `sw/testdata/phasesplit/devrun-stale-f688db385b/` (declared, §1.0) |

---

## §0 HEADLINE

**THE CUT EXISTS, AND IT IS NOT MARGINAL: 96 % OF THE BINDING `ce -> ce` CONE
IS PHASE-STABLE.** On the worst path of every draw, pin-dependence enters only
in the last 2–3 combinational cells, at 89.7–96.8 % of the data delay. On one
CONTROL draw **20 of the top 50 paths carry no pin-dependent node at all.**

**AND THE FRONTIER HAS EXACTLY ONE OWNER, MEASURED TWICE INDEPENDENTLY: the
RESET pin.** Every pin-dependent node in the whole cone is a `dec_addr_next[*]`
bit — the microcode decode address — and the only live register that reaches
any of them is **`c_reset_q`**. Not `READY`, not `INT`, not `NMI`, not the read
data. (`sw/testdata/phasesplit/ctl/seed1.frontier.txt`,
`.../ret/seed1.frontier.txt`.)

| bar | verdict | |
|---|---|---|
| **A-1** positive control 100 % pin-dependent, 4 of 4 draws | **MET** | 26/26 · 25/25 · 26/26 · 25/25, both live sets, 0 REG-ONLY, 0 UNRESOLVED |
| **A-2** binding class is `SAME` at k = 2 on every CONTROL draw | **MET** | 40.09 · 38.99 · 40.83 MHz, k = 2.0000, `SAME` the minimum of the three core classes on all three |
| **A-3** worst `ce -> ce` path 100 % REG-ONLY on ≥ 3 of 4 draws | **MISSED, 0 of 4** | 48/50 · 48/49 · 47/49 · 39/41 REG-ONLY — every draw carries 1–2 pin-dependent cells, and they are the `dec_addr_next` tail |
| **A-4** a balanced REG-ONLY cut exists | **MET, 4 of 4** | 8 · 9 · 8 · 7 candidates on the strict MAX split; **three nets qualify on all four draws** |
| **A-5** worst `live -> core` ≤ 26.0 ns | **MET, 4 of 4** | 23.436 · 20.876 · 23.060 · 22.504 ns, identical under both live sets |

**THE NAMED CUT: `Decoder28#1`, the entry to the EU chain loop's first unrolled
position — measured split 46 % / 54 %, and it is one of only three nets that
clear A-4 on all four draws (`st_n#1`, `Decoder28#1`, `ld_b_n#1`).** §5.

⚠ **AN INSTRUMENT DEFECT WAS FOUND BY THIS WAVE'S OWN OUTPUT AND ALL FOUR DRAWS
WERE RE-TAKEN.** The first CONTROL run's walker used `string match` on register
names carrying a bus index, where `[3]` is a character class, and **reported 19
of 50 walker failures as the result "this path has no pin-dependent node"**.
Retained and named at `sw/testdata/phasesplit/ctl-DEFECTIVE-WALKER/`; nothing is
quoted from it. §3.0.

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
  **if it does, that is a finding.** It did not: `SAME` binds at k = 2 on the
  retention draw exactly as on the three CONTROL draws (38.78 MHz against
  40.09 / 38.99 / 40.83), the frontier has the same owner, and the same three
  nets clear A-4. **No finding.**

**EVERY FIT USED THE SEED IT WAS GIVEN**, read back from the fitter's own
report (`seed*.seedecho.txt`): `Fitter Initial Placement Seed` = 1 · 2 · 3 on
CONTROL and 1 on RETENTION.

**ALL FOUR DRAWS WERE TAKEN TWICE.** The first set is
`sw/testdata/phasesplit/ctl-DEFECTIVE-WALKER/` and is quoted nowhere (§3.0);
every number in this document comes from the re-run with the fixed instrument.
One `quartus_map` + one `quartus_fit --seed=S --recompile=off` per seed, per
configuration, through `sw/run_phase_split_anatomy.sh` with its single-writer
guard by exact binary name.

**THE FIVE SDC EXCEPTION CLASSES, PER DRAW** (`sta_truefmax_probe.tcl`, each
class with its own measured k — a slack is not an Fmax, `standing_gates.md` §A):

| class | k | CONTROL s1 | CONTROL s2 | CONTROL s3 | RETENTION s1 |
|---|---:|---:|---:|---:|---:|
| DEFAULT (whole design) | 1.0 | 41.57 | 41.32 | 41.73 | 41.59 |
| **SAME `ce -> ce`** | **2.0** | **40.09** | **38.99** | **40.83** | **38.78** |
| INTO `ce -> t1_half2` | 1.0 | 63.01 | 61.68 | 58.50 | 67.12 |
| OUTOF `t1_half2 -> ce` | 1.0 | 84.52 | 87.65 | 75.78 | 78.66 |
| ENABLE `-> t1_half2` | 1.0 | 130.99 | 94.32 | 112.97 | 142.73 |

**A-2 IS MET**: `SAME` is the minimum of the three core-domain classes on every
draw and measures **k = 2.0000** on every draw, reproducing the CLASS of
`sw/testdata/g6dist/rep-int-term-control-20260820/` (which read `SAME`, k = 2.0,
`worst-of-5` 38.25 MHz, `t_min_ns` 24.73–26.14). ⚠ **The numbers are NOT
expected to agree and are not the bar** — that sweep is at `f688db385b`, two
`v30u_eu.sv` commits behind. **These figures are NOT a G6 result and are not
quotable as Fmax**: they are one `sta_truefmax_probe` row per draw off an
anatomy driver that writes no receipt.

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

CONTROL seed 1, `sw/testdata/phasesplit/ctl/seed1.phasesplit.txt` §D path 1.
Data delay **48.245 ns over 50 combinational cells, 38 logic levels**, launch
`v30u_ucrom|…|ram_block1a6~PORT_A_WRITE_ENABLE_REG`, latch
`v30u_ucrom|…|ram_block1a2~porta_address_reg4`.

**Both endpoints are the microcode ROM's own M10K.** The binding arc is the
microcode ADDRESS FEEDBACK LOOP: read the row, decide the next state, compute
the next decode address, present it to the ROM. All cumulative figures below
are DATA delay, measured from the launch register's output pin (the ~9.2 ns
clock-network arrival is excluded).

| segment | from → to | ns | cells |
|---|---|---:|---:|
| ucrom M10K read + ROM row decode | `portadataout[0]` → `ucrom~90` | 5.33 | 3 |
| operand / queue-state select | `Selector671` · `Equal28` · `opr_free_now` · `rd_done_cnt_n` · `rdq0_n` · `opr_n` · `v1` | 9.34 | 9 |
| **`Add57` EA carry chain** | `Add57~17` → `Add57~5\|sumout` | **1.94** | 12 |
| row compare / state mux into the chain | `Equal243` · `Mux358` · `Mux359` → `Decoder28` | 5.69 | 4 |
| **chain position 1** | `Decoder28` → `st_n~14` | 3.53 | 3 |
| **chain position 2** | `Decoder30` → `ld_b_n~17` → `Ram15` ×2 → `p~6` → `st_n~62` | 8.08 | 8 |
| **chain position 3** | `Decoder34` → `ld_b_n~38` → `Ram21` ×2 → `p~9` → `st_n~99` | 7.70 | 8 |
| **chain position 4 (tail)** | `Decoder38` → `dec_addr_next[8]` → `dec_addr_next[4]` | 2.95 | 3 |
| routing + M10K address-register setup | | 3.68 | — |

**FOUR unrolled chain positions stand in series on one path** (`CHAIN_MAX` is 7;
measured maximum occupancy is 6), marked unambiguously by their four separate
`Decoder*` cones, and they are **22.3 ns of the 48.2 — 46 % of the whole arc.**
Each position is the same source line: `v30u_eu.sv`'s
`for (chain = 0; chain < CHAIN_MAX; chain = chain + 4'd1)` around
`` `include "v30u_eu_step.svh" ``.

⚠ Two things worth recording because they are NOT where the delay is:

* **The EA adder is 1.94 ns of 48.245 — 4 %** — twelve carry cells, most of them
  at 0.000 ns increment. The carry chain is not the problem.
* **`Ram15` and `Ram21` are the register-file read** (`gpr [0:7]` /
  `sreg [0:3]`, `v30u_eu.sv:236-237`), and there is **one per chain position**:
  each unrolled step reads the file again.

---

## §3 THE PIN-DEPENDENCE SCAN — CONTROL FIRST

### §3.1 THE POSITIVE CONTROL — **PASSED ON 4 OF 4 DRAWS. A-1 IS MET.**

| draw | control path | data delay | data cells | PIN-DEP | REG-ONLY | UNRESOLVED | excluded by rule |
|---|---|---:|---:|---:|---:|---:|---|
| CONTROL s1 | `c_int_q` → `v30u_eu\|row_posted` | 23.436 | 26 | **26** | 0 | 0 | 5 clock + 5 dest |
| CONTROL s2 | `c_int_q` → `v30u_eu\|row_posted` | 20.876 | 25 | **25** | 0 | 0 | 5 clock + 5 dest |
| CONTROL s3 | `c_int_q` → `v30u_eu\|row_posted` | 23.060 | 26 | **26** | 0 | 0 | 5 clock + 5 dest |
| RETENTION s1 | `c_int_q` → `v30u_eu\|row_posted` | 22.504 | 25 | **25** | 0 | 0 | 5 clock + 5 dest |

**Every non-excluded node came back pin-dependent, on every draw, under BOTH
`LIVE_NARROW` and `LIVE_WIDE` — the two sets returned the identical path and
the identical count on all four draws.** The classifier can say YES, so its
NOs in §3.2 mean something. Resolver census: **every node resolved by
`get_pins`** — 112 · 120 · 149 · 117 distinct nodes, `get_nets` 0, UNRESOLVED 0.

### §3.0 ⚠ THE FIRST RUN OF THIS SCAN WAS DEFECTIVE, AND ITS OWN OUTPUT IS WHAT SAID SO

The instrument as committed at `ce9caea6b0` located the launch and destination
registers with `string match "${from_name}*" $node_name`. A Quartus register
name carrying a **bus index** — `opc_base[3]`, `tmpb[4]` — is a `string match`
PATTERN in which `[3]` is a **character class**, so the pattern fails to match
its own name. On that run's `seed2` the walker never entered its DATA phase on
**19 of 50 paths**; they reported `cells 0 / regO 0 / pinD 0`, contributed
nothing to the census, and their printed "data delay" still carried the 9.3 ns
clock-network arrival — which is why that draw showed a 58.794 ns worst data
delay against 49.6 ns on every path actually walked.

**And the failures were printed as a result**: they were absorbed into the
`merge point UNDEFINED` count, so *"the walker could not find this path"* was
reported as *"this path has no pin-dependent node on it"*. **The positive
control did not catch it** — the control's own path launches from `c_int_q`,
which has no bus index, so its `nc < 3` guard never fired. That is the
vacuous-gate pattern one layer in from where the control was watching.

Fixed at `c2a4f42eef` in three parts (literal `hasprefix` prefix tests; WALKER
FAILURES counted in a class of their own and printed by path number; a
walker-failed path may not set the worst data delay), the defective run retained
and named at `sw/testdata/phasesplit/ctl-DEFECTIVE-WALKER/`, **and all four
draws re-taken**. On the re-run **WALKER FAILURES reads 0 of 50 on every
draw**, and seed 2's `merge point UNDEFINED` reads **20** — a real 20, not the
19 failures plus one.

### §3.2 THE SCAN — WHERE PIN-DEPENDENCE ENTERS

| draw | `$v30u_ce` | worst `ce→ce` data delay | worst path REG-ONLY / PIN-DEP | pinDep per path (min…max) | merge point, mean | as % of mean data delay | no pin-dep at all | walker failures |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| CONTROL s1 | 2,109 | 48.245 | **48 / 2** | 2 … 2 | 43.200 | **89.7 %** | 0 / 50 | **0 / 50** |
| CONTROL s2 | 2,096 | 50.580 | **48 / 1** | 0 … 4 | 48.243 | **96.8 %** | **20 / 50** | **0 / 50** |
| CONTROL s3 | 2,101 | 48.191 | **47 / 2** | 2 … 2 | 43.726 | **91.9 %** | 0 / 50 | **0 / 50** |
| RETENTION s1 | 2,084 | 50.841 | **39 / 2** | 0 … 2 | 45.538 | **91.0 %** | 8 / 50 | **0 / 50** |

**A-3 IS MISSED, 0 OF 4, AND IT IS REPORTED AS REGISTERED.** No draw's worst
path is 100 % REG-ONLY: each carries 1–2 pin-dependent cells. **The miss is
real and it is also small** — those cells are the last 1.5–5 ns of a 48–51 ns
arc, downstream of every cut candidate in §4, so **A-3's miss does not
constrain the cut.** It constrains STAGE 2, which must contain them.

### §3.3 WHAT THE PIN-DEPENDENT NODES ARE

Identical in kind on all four draws: **`dec_addr_next[*]`** — the microcode
DECODE ADDRESS — with `opc_base` (CONTROL s2) and `modrm_reg[2]`
(RETENTION s1) joining it in the same tail. Nothing else in the cone is
pin-dependent on any draw.

### §3.4 ⚠ THE FRONTIER HAS ONE OWNER, AND IT IS `RESET`

`sw/sta_phase_split_frontier.tcl`, run on a CONTROL seed-1 fit and on the
RETENTION seed-1 fit, asking the same `-through` question once per live
register:

| draw | node | live sources reaching it | which |
|---|---|---:|---|
| CONTROL s1 | `dec_addr_next[8]~24\|combout` | **1 of 22** | `c_reset_q` |
| CONTROL s1 | `dec_addr_next[4]~35\|combout` | **1 of 22** | `c_reset_q` |
| RETENTION s1 | `dec_addr_next[2]~21\|combout` | **1 of 45** | `c_reset_q` |
| RETENTION s1 | `dec_addr_next[2]~22\|combout` | **1 of 45** | `c_reset_q` |

Positive control on both: the first data node of the worst `live -> $v30u_ce`
path is reached by 1 of the live registers (`c_int_q`, its own launch), so the
per-register question can return YES.

**`READY`, `INT`, `NMI`, `POLL_N` and the AD read word reach NOTHING in the
binding `ce -> ce` cone.** The one live term is `RESET`, which enters through
`core_reset = c_reset_q | ~cfg_use_core` (`system_large.sv:384`).

⚠ **THIS IS AN ATTRIBUTION, NOT A DISPOSITION.** It says which pin owns the
frontier. It does **not** say the frontier can be moved, and nothing here
proposes touching the reset path. What it does establish is that the theorem's
constraint on stage 1 is bounded by a single, well-understood signal rather
than by the data or control pins the campaign was worried about.

---

## §4 THE CUT-POINT CENSUS

Occurrence-indexed (`net#N`), scored on the strict MAX split, 60 % bar computed
per draw from that draw's own worst `ce -> ce` data delay.

| draw | worst data delay | 60 % bar | A-4 candidates (MAX) | A-4 |
|---|---:|---:|---:|---|
| CONTROL s1 | 48.245 | 28.947 | 8 | **MET** |
| CONTROL s2 | 50.580 | 30.348 | 9 | **MET** |
| CONTROL s3 | 48.191 | 28.915 | 8 | **MET** |
| RETENTION s1 | 50.841 | 30.505 | 7 | **MET** |

**THREE NETS CLEAR A-4 ON ALL FOUR DRAWS.** Everything else on the candidate
lists is a one-draw or two-draw name (`Mux358` / `Mux359` / `Mux360` / `Mux350`,
`Ram12` / `Ram14` / `Ram15` / `Ram17`, `p`, `Decoder30`) — the fitter renames
the same structure per draw, which is exactly why a cut must be chosen on the
intersection and not on one draw's best number.

| net | CONTROL s1 up / dn | CONTROL s2 | CONTROL s3 | RETENTION s1 | paths |
|---|---:|---:|---:|---:|---:|
| **`Decoder28#1`** | 22.779 / 25.949 | 25.168 / 25.412 | 22.232 / 25.959 | 23.506 / 27.487 | 100 · 100 · 78 · 100 % |
| **`ld_b_n#1`** | 26.949 / 21.317 | 25.784 / 24.796 | 26.301 / 25.583 | 27.814 / 23.027 | 100 % on all four |
| **`st_n#1`** | 23.796 / 24.571 | 30.044 / 20.536 | 27.728 / 24.182 | 25.215 / 26.004 | 100 % on all four |

(MAX split, ns. Every cell is REG-ONLY on every path the net appears on, on
every draw — that is a precondition of appearing in this table at all.)

**`Decoder28#1` is the most consistently balanced of the three**: 46.8 / 53.2,
49.8 / 50.2, 46.1 / 53.9, 46.1 / 53.9 per cent. `st_n#1` is the best on one
draw (49.2 / 50.8) and the worst on another (59.4 / 40.6, within the bar by
0.30 ns). `ld_b_n#1` sits between them and is always slightly upstream-heavy.

---

## §5 WHAT THE ANATOMY SAYS THE DESIGN IS

### §5.1 THE MEASUREMENT FIRST, AND WHAT IT DOES *NOT* CONSTRAIN

The pin-dependence frontier sits at **89.7–96.8 % of the binding arc**. The
theorem therefore admits a stage-1 capture **essentially anywhere in the first
43–48 ns of a 48–51 ns cone**, and on one CONTROL draw on 20 of 50 paths it
admits one anywhere at all. **The theorem is not what picks the cut. RTL
expressibility is.** A cut is only real if the source can say it, and a Quartus
net name is not by itself an RTL seam.

### §5.2 THE ONE SEAM THE EVIDENCE ACTUALLY SUPPORTS

`v30u_eu.sv` builds the EU's next state as a **bounded, UNROLLED loop**:

```
    for (chain = 0; chain < CHAIN_MAX; chain = chain + 4'd1)
        if (!stop) begin
            if ((chain != 4'd0) && !st_zero_ok(st_n)) stop = 1'b1;
            else `include "v30u_eu_step.svh"
        end
```

Every position is a fresh copy of one source line, and §2 measures **four of
them standing in series on the worst path, 22.3 ns of the 48.2**. That loop is
the only place in this cone where the RTL has a boundary the netlist also has:
the four separate `Decoder*` cones are the four copies' state decoders, and
`Decoder28` is the first of them.

**THE NAMED CUT: `Decoder28#1` — the ENTRY to the chain loop.**
**Stage 1** = the microcode row read, the operand / queue-state select, the EA
add, and the row-compare/state mux that produce the loop's inputs.
**Stage 2** = the whole unrolled loop and the `dec_addr_next` tail.
**Measured split, worst-case over each draw: 46.8 / 53.2 · 49.8 / 50.2 ·
46.1 / 53.9 · 46.1 / 53.9 per cent** — the only candidate that is within
±4 points of balanced on all four draws.

**THE RTL CONSTRUCT** is to peel the loop: evaluate stage 1 in one
`always_comb`, capture its outputs in a register enabled by `ce_half`, and let
the `for` loop read that register instead of the live combinational value. It
needs **no new contract clause** — `S-1` already guarantees a `ce_half` between
consecutive `ce`s and is already asserted in `v30_core.sv` — and a stage-1
capture is idempotent, so extra `ce_half`s stay harmless exactly as they are
today for `t1_half2`.

### §5.3 THE TWO ALTERNATIVES, NAMED SO THEY ARE NOT RE-DISCOVERED

* **`st_n#1`** — peel *after* the first chain position instead of before it.
  Same register width (the loop-carried set is the same set), one position's
  delay moved from stage 2 to stage 1. Its split is the best on CONTROL s1
  (49.2 / 50.8) and the worst on CONTROL s2 (59.4 / 40.6, inside the bar by
  0.30 ns), so it trades balance for draw-sensitivity.
* **`ld_b_n#1`** — peel inside the second position. Consistently
  upstream-heavy, no structural advantage over the other two, listed because it
  is the third net that survives all four draws.

**Nothing else in §4 is proposed as a cut.** The best-balanced net on any single
draw is usually a `Ram*` or `Mux3*` occurrence *inside* one unrolled copy, and
the RTL cannot cut inside one copy without cutting inside all of them — they are
the same source line.

---

## §6 WHAT IS **NOT** MEASURED HERE

1. **THE POST-CUT DELAYS. THE SPLIT IS AN ESTIMATE, NOT A PREDICTION.** Every
   number in §4 is read off the **uncut** netlist, where Quartus has merged
   logic freely across the prospective boundary — §2's worst path shows
   `st_zero_ok` and three separate `st_n~*` LUTs folded across a position
   boundary. After a real cut both stages are re-synthesised and the numbers
   move. **This anatomy bounds the shape of the cut. It does not predict an
   Fmax, and no Fmax may be quoted from it.** The quotable numbers come from
   `sw/quartus_gate.py`.
2. **THE WIDTH OF THE PHASE REGISTER.** The crossing set is the loop-carried
   variable set — every `*_n` written before the cut and read after it. This
   anatomy measures DELAY, not that set, and its cardinality (and hence the ALM
   and flop cost, and whether `ss_lint`'s map must grow) is unmeasured. It is
   derivable from the RTL and is wave 2's first job.
3. **BEHAVIOUR.** Nothing was simulated. The bit-exactness argument is the
   theorem plus §3's measurement that the prefix is register-only; no
   `check_core`, `ulockstep`, `tb_sys` or fuzz leg was run, and none is claimed.
4. **THE SDC.** Whether deleting `set_multicycle_path -setup 2 -hold 1` actually
   closes at k = 1 after the cut is the whole point of the campaign and is **not
   tested here.**
5. **`RESET`'s disposition.** §3.4 attributes the frontier to `c_reset_q`. It
   does not establish that a stage-1 register may ignore it, that the reset path
   may be changed, or that the `dec_addr_next` tail fits in stage 2's window.
6. **THE DRAW POPULATION IS 3 + 1.** Three CONTROL draws is not a distribution,
   and `standing_gates.md` §A governs: the same tree has drawn 19.42 and
   45.91 MHz. The RETENTION draw is a cross-check and was not the source of the
   choice; it agreed with CONTROL on every structural finding — the same
   control result, the same frontier owner, the same three A-4 nets — which is
   what was expected of a core-internal class and is therefore **not** a
   finding.
7. **THE TOP-50 POPULATION.** The scan sorts by slack, and §2 notes that data
   delay and slack do not order identically under clock skew. Paths outside the
   top 50 by slack are not measured.

---

## §6.1 THREE THINGS THE WAVE MEASURED THAT NOBODY ASKED FOR

* **THE MULTICYCLE COVERS 2,084–2,109 REGISTERS, NOT 2,200, AND THE COUNT MOVES
  WITH THE DRAW.** The brief's 2,200 is the stale `hdl/db` at `f688db385b`. At
  HEAD `nec_test.sdc` reports `CE multicycle 2/1 applied to 2109 / 2096 / 2101 /
  2084 ce-gated v30u core registers` on the four draws.
* **`t1_half2` IS DUPLICATED BY THE FITTER ON SOME DRAWS, AND THE SDC's
  EXACT-NAME COLLECTION CATCHES THE DUPLICATE.** `$v30u_half` measured **1** on
  CONTROL s1 and RETENTION s1 and **2** on CONTROL s2 and s3
  (`t1_half2~DUPLICATE`). `nec_test.sdc:178-179` states the opposite — *"`set
  v30u_half` matches by EXACT NAME, so a fitter-created `t1_half2~DUPLICATE`
  falls into `$v30u_ce`"* — and the sta log agrees with the measurement, not the
  comment (`2 ce_half-gated register(s) kept OUT of the CE multicycle`).
  **The comment is stale; the behaviour is the one it wanted.** Recorded, not
  acted on: no SDC edit is in scope for this wave.
* **THE BRIEF'S LIVE COLLECTION NAMED THE WRONG REGISTERS.** It named "the 36
  `nec_bus|ad_in_q[*]` read-data bits"; `ad_in_q` is 20 bits (`nec_bus.sv:196`)
  and does not drive a core port — it feeds `ad_drive`, a register inside
  `nec_bus`. The core's asynchronous inputs are the `c_*_q` registers of
  `system_large.sv` (`LIVE_NARROW` = 22 · 21 · 23 · 47). This did not change any
  verdict: `LIVE_WIDE`, which needs no name list and is a superset of both
  readings, returned the identical control path and count on all four draws.

---

## §7 THE REGISTERED BARS

**Pre-registered here, BEFORE the first draw of this wave** (commit
`5ba6008a7d`, ancestor of every draw). **They are scored as registered and
reported as registered even where they miss — the scoring is §0's table, and
A-3 MISSED on 0 of 4.**

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

