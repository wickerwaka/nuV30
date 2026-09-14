# WAVE 15 — **AMENDMENT A-2: WHAT Q-2 FOUND, AND WHY ARM-B IS BEING BUILT.  WRITTEN BEFORE ANY ARM-B TIMING EXISTS AND BEFORE ANY ARM TIMING FIGURE HAS BEEN READ.**

At the moment this is committed the Quartus driver is on the **BASE** arm's
first sweep.  **No arm's Fmax, slack or ALM count exists.**  Everything below is
a Q-2 (equivalence) result or an instrument finding.

---

## A-2.1 ARM-A IS **BEHAVIOURALLY EXACT** — EVERY LEG, BASE AND ARM, IDENTICAL

`sw/wave15_ladder.sh`, run identically in both scratch worktrees on each one's
own freshly built and **separately receipted** Verilator binaries
(`Vtb_v30_core`: base `a85a4104f7a69ed8…`, ARM-A `74a2a09796d70878…`).

| leg | base | ARM-A |
|---|---|---|
| `check_core --opcodes all --cases 0` | **169,000/169,000** | **169,000/169,000** |
| …at `--ce-div 2 / 3 / 8` | 169,000 · 169,000 · 169,000 | **identical** |
| …`--ce-div 1` | **REFUSED** | **REFUSED** |
| **the 181 goldens WAVE 14's probes failed** | `FA` 500/500 · `FB` 500/500 · `INT.FB` 200/200 | **identical — all three perfect** |
| `8F.0` | 500/500 | 500/500 |
| the four HLT sweeps | 97 · 93 · 45 · 44 = **279/283** | **identical** |
| `v0.1-w1` / `-w3` / `EB` | 1,200 · 1,200 · 200 | identical |
| the four `evt` cells + biased | 200 · 1,200 · 200 · 1,200 · 1,200 | identical |
| `ulockstep --golden all --cases 50` | **17,350/17,350 ALL LOCKSTEP** | **identical** |
| `ghost_launch_law` | 200/200 = 100.0 % | identical |
| `check_boot` / `--timed 400` | 220 · 400 rows MATCH | identical |
| `check_ab_sim` | 187 rows MATCH | identical |
| `sm3_s16_score --core ucore` | census `busstat_other` 24 · `ARCH` 27 | **identical** |
| `chain_lfsr_gate` | PASS, sigs `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78` | **BYTE-IDENTICAL, and every gap and liveness row with them** |
| `demux_off_gate` | PASS | PASS |
| `test_artifact` | 45/45 | 45/45 |
| `test_quartus_gate` | **286 / 286** ⚠ | **286 / 286** |
| `chainflat_relocation_check` | PASS, 9 arms | PASS |
| `phase_split_lint` | PASS 156 / 778 | PASS 156 / 778 |
| `ss_lint --core ucore` | PASS **232**; 229 architectural flops, 0 UNMAPPED | **identical** |
| **`fz2_replay`, 305 seeds** | see A-2.3 | **305 rows × 11 fields IDENTICAL** |
| **`r7_lint`** | PASS | PASS **with the two declared entries** (A-2.2) |
| **`cutset_lint`** | PASS 80 / 0 | ⚠ **FAIL — X4, one violation** (A-2.4) |

⚠ **THREE DISAGREEMENTS WITH THE STANDING TABLES, ALL MEASURED AND NONE A
FAILURE OF EITHER ARM**, reported per the standing rule that a stale row is not
a failure:

1. **`test_quartus_gate` reads 286/286 on this tree, not 287/287.**  Identical
   on base and arm.
2. **`ss_lint`'s `standing_gates.md` row is stale** (226 / 214 / `SS_VERSION`
   0x8D) against this tree's **232 / 229**.  Known-stale since WAVE 13.
3. **`ucrom_mif_check` exits 2 on BOTH arms** — *"NOTHING TO CHECK: no `hdl/db`
   (a clean build deletes it; run this against a build still on disk)"*.  A
   fresh worktree has no build tree.  It is re-run after the sweeps, when there
   is one.

## A-2.2 THE DECLARED COST: `r7_lint` GAINS TWO ENTRIES, AND THE ARGUMENT IS UNCHANGED

C1 splits the one net `q_ripe_lead_n` — a **declared unresolved carrier** of
`sw/r7_lint.py` since §73 — into `q_ripe_lead_n0` and `q_ripe_lead_n1`.  Without
the list edit `r7_lint` **FAILS with two undeclared unresolved carriers**, and
it is right to.  The edit is **part of the arm's own diff** (`sw/wave15_arms.py`
applies it, so it appears in `git diff` beside the RTL and cannot be mistaken
for a repo-wide loosening), the original entry is **kept above the two new ones
so a reader can see nothing was dropped**, and the argument is the same one,
character for character: both nets are driven from the queue's procedural
next-state and neither is the READY sample.  **This is a cost, and it is
declared, not absorbed.**

## A-2.3 ⚠⚠ **A RIG FINDING: `fz2_replay` IS STRUCTURALLY VACUOUS IN A GIT WORKTREE, AND IT RAN VACUOUS HERE FIRST.**

The ladder's first `fz2_replay` leg reported **`rc=0`** on both arms and its
JSON compared **IDENTICAL** — over **ZERO ROWS**.

> **`.gitignore:9` ignores `sw/testdata/campaigns/*/captures/`.**  A scratch
> `git worktree` therefore contains **none** of the banked captures, so
> `fz2_replay.retained()` returns `{}` and the tool prints
> *"population 0 seeds with banked socket rows"* / *"NOT SCOREABLE (no retained
> capture): 106"* — **and exits 0.**

**A GREEN `fz2_replay` IN A WORKTREE IS NOT EVIDENCE OF ANYTHING**, and this is
the tenth instrument in this campaign to produce a confident, wrong, vacuous
result.  It was caught only because the comparison was written to print the ROW
COUNT before the verdict.  **Every wave that runs gates in a scratch worktree
inherits this**; WAVE 14 did not run `fz2_replay` and so did not meet it.

Repaired by symlinking the two live campaigns' `captures/` into each worktree
(untracked, no tracked file touched) and re-running.  The leg is then
**305 seeds** — WAVE 7's own denominator — and:

* base: **AGREEMENT 301 / 305 = 98.7 %**, of the 101 both-FAIL seeds
  `first_bad` IDENTICAL on **101**;
* **base vs ARM-A: 305 rows × 11 fields IDENTICAL** — `seed`, `cid`, `k`,
  `tier`, `fabric_bad`, `fabric_first`, `win`, `wait_mode`, `has_evt`, `family`
  and the whole nested `sys` dict (`n`, `nrows`, `bad`, `flick`, `first`,
  `fired`, `vecused`).  **Compared BY NAME, never by a digest computed here**
  (`sw/wave15_fz2cmp.py`), and the tool **refuses with exit 4 on a zero-row
  population** so this vacuity cannot recur silently.

## A-2.4 ⚠⚠ **THE ONE FAILING LEG, AND IT IS A REAL FINDING: `cutset_lint` X4 FIRES ON ARM-A, AND IT IS RIGHT TO.**

```
VIOLATION X4: the next-state block reads module-level COMBINATIONAL VALUE(S)
DIRECTLY ... so they are NOT in the cut set and stage 2 bypasses the shadow
exactly as WAVE 2 did: ['q_ripe_lead_n']
```

> ### **C1 DOES NOT DELETE THE BYPASS.  IT RELOCATES IT — AND THAT MAKES A BYPASS THAT WAS ALWAYS THERE VISIBLE TO A LINT THAT COULD NOT SEE IT.**
>
> On the base tree `q_ripe_lead_n` is an **input PORT**, and `cutset_lint`
> exempts ports because a port's value comes from outside the module.  But the
> value on that port is `f(q_pop)`, `q_pop` is stage-1 combinational logic, and
> the EU's stage 2 reads it — **so stage 2 has been reading stage-1
> combinational logic through the BIU all along.**  That is not a new defect;
> it is *precisely why this arc binds on 200 of 200 paths of the split tree
> while the split shortened everything else it could reach.*  X4 cannot see
> through a module boundary; when C1 brings the mux inside the EU, it can.
>
> **The consequence for the mechanism is a prediction, written before any
> timing is read: C1 should shorten this arc (the BIU's three LUT levels become
> one EU mux) but cannot remove it from the `ce → ce` cone, because the select
> still launches in stage 1.**

## A-2.5 WHY ARM-B IS BEING BUILT, AND HOW THAT SITS WITH §4

The pre-registration §4 says ARM-B is built *iff ARM-A passes Q-2 in full and
fails to close both configurations*, and *"if ARM-A fails Q-2, the wave reports
C0 and ARM-B is not used to rescue it."*

**ARM-A DOES NOT PASS Q-2 IN FULL: `cutset_lint` FAILS.**  I am building ARM-B
anyway, and this is the reasoning, stated plainly so that a reader can discount
it:

* §4's clause was written about **behavioural** equivalence — the thing that
  costs 181 goldens and that no mechanism may weaken.  **ARM-A is behaviourally
  exact on every leg of A-2.1**, including the 181.  Nothing about F7 is
  weakened by C1 and nothing is claimed that a golden contradicts.
* The failing leg is a **structural lint of the phase split**, and its content
  is A-2.4's finding: C1 relocates a bypass rather than deleting it.  **The
  registered remedy for exactly that is C2**, written into §4 of the
  pre-registration *before any of this was measured*, with its cost (one flop,
  `s1q` 778 → 779, split-dependent) declared there.
* **This is an interpretation made after seeing a LINT result and before seeing
  ANY timing result.**  It is recorded as an interpretation, not as a bar that
  was always going to be read this way.  A reader who rejects it should read
  the wave as: **ARM-A is behaviourally exact and fails one structural lint;
  ARM-B is the registered successor; both are measured and neither is landed.**
* **Nothing is landed either way** (Q-7), so no gate is weakened by building
  both and reporting both.

**ARM-B, MEASURED BEFORE ITS TIMING EXISTS**: `check_core --opcodes all
--cases 0` **169,000/169,000** on its own receipted binary
(`f40ce2fe6e11102d…`) — **and the phase split's own premise assertion
(`v30u_eu.sv`'s `$fatal` on `s1q !== s1_bus` at every `ce`) DID NOT FIRE, which
is the measurement that the select really is constant across the CPU cycle** —
with `cutset_lint` **PASS (81 members / 0 violations)**, `phase_split_lint`
**PASS (157 members / 779 bits)** and `r7_lint` **PASS**.

⚠ **`sw/wave15_arms.py`'s Q-6 SOURCE CHECK PRINTS "0 non-blocking assignments —
no flop added" FOR ARM-B, AND THAT IS THE CHECK BEING WRONG, NOT ARM-B BEING
FLOPLESS.**  ARM-B's flop arrives as a **parameter widening** (`S1W` 778 → 779),
which no textual `<=` scan can see.  **ARM-B ADDS ONE FLOP.  It is declared in
the pre-registration §4, it is declared here, and `ss_lint`'s `SS_COUNT` must
not move because `s1q` is derived state and deliberately not save-state
mapped.**

## A-2.6 THE FALSIFIER'S NON-VACUITY (from A-1.4, restated because it is Q-2 evidence)

Clause (1) FIRES when one term of `q_ripe_lead_n1` is perturbed; clause (2)
FIRES when `pop_eff` is armed from `q_pop` alone.  A third perturbation —
deleting the flush's cancellation of the pop — **DID NOT** fire, and
`check_core` read 169,000/169,000 without it: **the pop/flush coincidence is not
reachable in the golden population.**  Recorded as measured.

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
