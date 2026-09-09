# WAVE 6 — THE CHAIN FLATTENING STUDY.  PRE-REGISTRATION.

**THIS IS A STUDY.  IT PROPOSES NO DESIGN FOR THE CORE AND LANDS NOTHING IN
IT.**  OFFLINE ONLY.  **NO BOARD.  NO FLASH.  NO BITSTREAM IS PROGRAMMED.**  No
Codex consulted.  No nested subagent spawned.  It is **NOT A GATE**, it writes
**no receipt**, and **no figure in it may be quoted as a pass**;
`docs/notes/standing_gates.md` §A governs every timing figure it produces.

Committed **before the first Quartus stage of this wave**.  Instruments
committed before this document.

---

## §0 THE QUESTION

> **Is the 7-copy unroll a MODELLING ARTIFACT or a real description of the
> die's decode — and would a FLATTENED composed cone be SHORTER?**

The die does one clock's decode in ONE combinational cone.  The RTL needs up to
seven serial copies of `step()` because the C++ model
(`sim/loader_impl.h`, `sim/exec_impl.h` — **the SPEC**) expresses that clock as
up to six sequential statement positions between `charge()` calls.

⚠ **THE HONEST RISK, STATED UP FRONT: COMPOSING SIX STEPS DOES NOT
AUTOMATICALLY REDUCE DEPTH.**  It wins only if the composition folds and shares.
**Five consecutive waves have had a predicted lever refuted by measurement.**
If the answer is "flattening does not get shorter", **that is this wave's most
valuable possible output and the document says so.**  DO NOT MANUFACTURE A YES.

⚠ **AND THE CAMPAIGN'S ANSWER IS ALREADY BOUNDED FROM ABOVE.**  WAVE 5
measured that deleting the ENTIRE folded chain **for free** leaves the `ce → ce`
arc at **29.490 ns mean against a 29.6 ns requirement**, over it on 2 of 4
draws.  **No chain change — flattening included — can close the −13.9 ns gap**,
and this wave is registered in the knowledge that it cannot.  What it can
answer is whether the unroll is an artifact, and how many nanoseconds and how
much area a flattened form finds.

---

## §1 WHAT IS ALREADY MEASURED AT THE TIME OF THIS REGISTRATION, AND WHAT IS NOT

**Stated plainly because a pre-registration that back-dates a measurement is
worth nothing.**

| leg | status at registration |
|---|---|
| **A(i)** the STATIC graph (`sw/chainflat_graph.py`) | **ALREADY RUN.**  Its three controls PC-A1/A2/A3 are reported as measured, non-vacuity included |
| **A(ii)** the DYNAMIC census (`sw/chainflat_probe.py`) | **ALREADY RUN** over the golden suite + 4 LFSR seeds.  Reported as measured |
| **B** the sequence census | **ALREADY RUN** (it is A(ii)'s output) |
| **C** the composition analysis (`sw/chainflat_compose.py`) | **ALREADY RUN.**  Reported as measured |
| **D**'s EQUIVALENCE GATE (**P-2**) | **ALREADY RUN, AND IT PASSED**, before this document was committed: the FLAT tree scores **169,000 / 169,000** and its four `tb_chain_lfsr` signatures are **byte-identical to REF's** (`1d01c9b269ffaa94 · b39b040a98b28e5d · 0997b773cd99c030 · d05b6c3c3d9fbe78`, depth 6 on both).  It is a pass/fail equivalence check with nothing to tune, and it is recorded here rather than presented as a prediction |
| **D** the SYNTHESIS EXPERIMENT | ⚠ **NOT RUN.  NOT ONE QUARTUS STAGE HAS BEEN EXECUTED FOR THIS WAVE.**  §3 below is registered ahead of it |
| **E** the verdict | not written |

A(i)–C are **source-and-simulation** measurements with their own falsifiers, and
each carries a NEGATIVE CONTROL that was demonstrated to fire.  §3's bars are
the ones this registration exists for.

---

## §2 THE INSTRUMENTS

| file | what it is |
|---|---|
| `sw/chainflat_graph.py` | the STATIC chain graph: path enumeration over the 33 arms of `v30u_eu_step.svh` (includes spliced), five DECLARED symbolic reductions, controls PC-A1/A2/A3 |
| `sw/chainflat_probe.py` | the DYNAMIC census driver.  Builds the `CHAIN_PROBE` binaries **into a scratch objdir** and never asks the artifact layer to promote one |
| `sw/chainflat_compose.py` | deliverable C: per-arm read/write sets, carried dependencies, dead writes, chain-invariant inputs |
| `sw/chainflat_proto.py` | generates the REF and FLAT scratch trees and their standalone Quartus projects; `--verify` scores both in Verilator |
| `sw/sta_chainflat.tcl` | the standalone-harness STA: walker, segmenter and copy census, with PC-1/PC-2/PC-3 |
| `sw/run_chainflat_synth.py` | the Quartus driver, single-writer guarded |

**THE ONE RTL EDIT, AND ITS TERMS.**  `hdl/rtl/ucore/v30u_eu.sv` gains a
SEQUENCE census strictly inside the existing `` `ifdef CHAIN_PROBE `` (off by
default, sim-only, no synthesis flow defines it).  It records the ORDERED tuple
of states occupying positions 0..N−1 of one CE edge, de-duplicates it in a
linear-probed table and counts it.  **The tuple is filled in the combinational
chain block and CENSUSED in the clocked observer**, which is the discipline
`stop` / `chain_used` / `chain_first` already use, and for the same reason: a
comb block re-evaluates many times per delta.

**F-3 IS THE TERM: no other tracked file under `hdl/` is modified, at the start
of this wave or at the end.**

---

## §3 THE SYNTHESIS EXPERIMENT — REGISTERED BEFORE THE FIRST COMPILE

### 3.1 WHAT IS BUILT

Two **standalone** projects, `v30u_eu` as its own top with virtual pins —
`ucore_provenance.md` §51.1's harness, the one whose baseline reproduced the
in-design cell count closely enough to attribute with.  Same device
(`5CSEBA6U23I7`), same optimisation mode, **NO `set_multicycle_path`** (the
USER RULING of 2026-09-08 makes the no-exception configuration the goal state).

* **REF** — a byte-identical copy of `hdl/rtl/ucore/`.  The 7-copy chain AS IT
  EXISTS.  **It is the positive control.**
* **FLAT** — the same tree with ONE substitution: the bounded
  `for (chain = 0; chain < CHAIN_MAX; ...)` loop, which is SEVEN full copies of
  a 33-arm `case`, replaced by *position 0's 33-arm case once, then the NINE
  chainable arms ONCE EACH in TOPOLOGICAL ORDER, each guarded by
  `st_n == S_X`*.

The substitution is exact **because the fall-through graph is a DAG over
exactly those nine states** (A(i)), so one edge's walk visits each at most once
and is a subsequence of any topological order.  **That is an argument.  The
gate is P-2.**

⚠ **NEITHER TREE IS PROPOSED FOR `hdl/rtl/ucore/`.**  FLAT exists to put a
number on the question and nothing more.

### 3.2 THE BARS

| bar | registered statement |
|---|---|
| **P-1 (= F-2) THE POSITIVE CONTROL.**  A MISS VOIDS DELIVERABLE D AND ITS FIGURES MAY NOT BE QUOTED | On **REF**, all three of: **(a)** the worst reg→reg arc carries **≥ 2** chain boundaries (the chain is on the binding arc, as WAVE 5 measured in situ); **(b)** **segment 0 is the largest single segment** (position 0 fat); **(c)** the copy census reads `st_n` **≥ 20** distinct cones, each of `rst_ctr_n` / `ld_dlo_n` / `ld_ripe_prev_n` **≤ 1**, and the negative control `zzz_no_such_signal` **== 0** (copies independent, and the census can say NO) |
| **P-1d** REPORTED, NOT VOIDING | the mean **per-folded-position** delay on REF, against WAVE 5's in-situ **5.359 ns** (band 2.993 – 7.945).  A registered band of **[2.0, 9.0] ns** is declared; **a miss is reported AS A MISS** and, because a standalone harness has no reason to reproduce an in-design absolute delay, it does not void (a)(b)(c) — this exemption is registered HERE, in advance, and may not be widened afterwards |
| **P-2 THE EQUIVALENCE GATE.  A MISS VOIDS DELIVERABLE D ENTIRELY** | FLAT scores **169,000 / 169,000** on `check_core --core ucore --opcodes all --cases 0` AND its four `tb_chain_lfsr` output signatures are **BYTE-IDENTICAL** to REF's, seed for seed.  A flattened form that computes a different function is not a comparison, it is a bug |
| **P-3 THE MEASUREMENT** | MAP ONCE PER PROJECT, FIT ONCE PER SEED, **3 seeds each**.  Reported for both: ALMs, combinational ALUTs, registers, worst reg→reg data delay, logic levels, boundary count, and the boundary-bucketed scan.  `map_errors == 0` and the `$readmemh` check **POSITIVE** (F44: a wrong `HEXDIR` gives an all-zero ROM and a compile that SUCCEEDS) |
| **P-4a THE AREA PREDICTION** | FLAT's **combinational ALUT** count falls by **≥ 25 %** against REF.  *Reasoning, registered: the fold removes five of six copies of the nine chainable arms and of the per-position 33-way decoder.*  **A smaller fall REFUTES it and is reported as a MISS** |
| **P-4b THE TIMING PREDICTION, AND IT IS DELIBERATELY TWO-SIDED** | FLAT's worst reg→reg data delay is **within ±15 %** of REF's.  *Reasoning, registered: deliverable C measures the composition's SERIAL dependency chain to be unchanged by flattening — the same registers are carried in the same order.*  **A fall of more than 15 % REFUTES this expectation and is reported as a refutation IN THE STUDY'S FAVOUR** (flattening finds nanoseconds).  A rise of more than 15 % is equally a refutation and is reported as one |
| **P-5 THE OUT-OF-CONTEXT CAVEAT (= F-4)** | every estimate carries its uncertainty AND the sentence *"a standalone-prototype figure is NOT a prediction for the core"*, with WAVE 5's measured mispredictions (**+11.3 to +20.0 ns** on a downstream half, **+15.30 ns** on the loop) quoted beside it |
| **P-6 THE VERDICT (= F-5)** | ARTIFACT or DESCRIPTION, stated plainly; and whether flattening finds nanoseconds, **with a NO reported as the result it is** |
| **P-7 DISCIPLINE (= F-3)** | `git status --porcelain hdl/` carries **no tracked modification other than the `ifdef CHAIN_PROBE` extension** at the start and at the end.  `git add -A hdl/` is never used.  The standing ladder is re-scored GREEN after the probe edit and the figures are printed |

### 3.3 WHAT WOULD MAKE THIS WAVE REPORT A NULL

Registered now, in the pre-registration, in the words the results document must
use if it comes out that way:

> *The unroll is an artifact of the model's control flow, and flattening it is
> an AREA change and not a TIMING one: the flattened arc measures within noise
> of the unrolled one, because the serial dependency the chain expresses is
> real and a composition cannot beat it.  There are no nanoseconds here.*

and, if the area prediction also fails:

> *Neither the area nor the delay moved.  Quartus was already recovering what
> the fold could recover, and the 7 copies cost less than the source suggests.*

**Either sentence is a legitimate outcome and neither is a failure of the
wave.**

---

## §4 WHAT IS DELIBERATELY NOT DONE

1. **NOTHING IS LANDED IN `hdl/rtl/ucore/`** beyond the sim-only probe.
2. **NO DESIGN-LEVEL BUILD.**  `hdl/nec_test.qsf` / `nec_test_ucore.qsf` /
   `nec_test.sdc` are never opened by this wave's driver, so WAVE 5's
   `git checkout --` dance has nothing to restore.
3. **NO Fmax CLAIM.**  Three seeds are not a distribution; the same tree has
   drawn 19.42 and 45.91 MHz (`ucore_provenance.md` §74.4).
4. **NO CLAIM ABOUT WHAT FLAT WOULD DO IN THE DESIGN.**  P-5.
5. **`CHAIN_MAX` IS NOT CHANGED.**

---

## §5 DISCIPLINE, DECLARED

* OFFLINE ONLY.  NO BOARD.  NO FLASH.  No Codex.  No nested subagent.
* Single-writer guard by EXACT binary name before every Quartus stage.
* `~/.cache/ucsimt-tmp/chainflat/` for every intermediate; nothing large in
  `/tmp`.
* **A number with no artifact id is not quotable.**  Artifacts under
  `sw/testdata/chainflat/`, named in the results document.
* Record what was measured, not what was expected.
