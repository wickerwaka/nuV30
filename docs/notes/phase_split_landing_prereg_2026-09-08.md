# THE ce/ce_half PHASE-SPLIT LANDING — WAVE 2.  PRE-REGISTRATION.

**COMMITTED BEFORE THE FIRST EDIT UNDER `hdl/`.**  `git status --porcelain
hdl/` shows **0 tracked modifications** at the moment of this commit (the
twelve untracked `hdl/quartus_gate_*.log` files predate this wave and predate
WAVE 1).

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM IS TO BE PROGRAMMED.**
A fabric confirmation is a later wave's debt and is recorded as owed.
No Codex consultation.  No nested subagent spawning.

| | |
|---|---|
| **Tree at entry** | `a21195f38f` (`master`) |
| **Wave 1** | `docs/notes/phase_split_anatomy_2026-09-08.md` (`c89d0bde0c`, `a21195f38f`) |
| **Precedent landing** | `docs/notes/adcone_l1_results_2026-08-13.md` (L1) |
| **Results go in** | `docs/notes/phase_split_landing_results_2026-09-08.md` (SEPARATE document) |

---

## §0 STANDING DESIGN PRINCIPLE (verbatim, user directive 2026-08-01)

> SIMPLICITY: this is 80's era hardware — nothing on the die is wasted.
> Complex or confusing observed behavior is likely simple systems interacting
> in ways not yet understood. A large fitted table, a many-cased rule, or a
> per-opcode special case is a signal of misunderstanding, not a deliverable.

---

## §1 WHAT IS BEING LANDED

WAVE 1 measured that the binding `ce -> ce` cone is **96 % phase-stable** and
named the cut: **`Decoder28#1`, the ENTRY to `v30u_eu.sv`'s unrolled
`for (chain = 0; chain < CHAIN_MAX; ...)` loop**, splitting 46.8/53.2 ·
49.8/50.2 · 46.1/53.9 · 46.1/53.9 per cent over four draws.

**THE THEOREM THE LANDING RESTS ON:**

> A node in the `ce -> ce` cone that is outside every input pin's fanout
> depends only on registers that commit on `ce`.  Its value is therefore
> CONSTANT ACROSS THE WHOLE CPU CYCLE — identical at `ce_half(n)` and at
> `ce(n+1)`.  Capturing it on `ce_half` and consuming it on `ce` is bit-exact
> by construction and moves no pin on any clock.

**THE DESIGN — PEEL THE LOOP.**

* **STAGE 1** (evaluated `ce -> ce_half`, captured on `ce_half`): the microcode
  row read, the row-field decode, the operand / queue-state select, the EA add,
  and whatever else feeds the loop's entry.
* **STAGE 2** (evaluated `ce_half -> ce`, captured on `ce`): the whole unrolled
  chain loop and the `dec_addr_next` tail.
* Then **DELETE the CE multicycle from `hdl/nec_test.sdc`**.  That is the
  wave's purpose.  Both stages become default single-cycle checks.

**SCOPE IS THE SPLIT ALONE** (USER RULING 3).  The `ucrom` registration (the L2
lever) is NOT bundled.  One mechanism, measured on its own; a bundle's benefit
is not evidence for any member of it.

---

## §2 THE SHADOW REGISTER'S WIDTH — MEASURED BEFORE THE DESIGN WAS COMMITTED TO

WAVE 1 §6 item 2 declares this unmeasured and names it wave 2's first job.
**MEASURED: 490 BITS over 63 named signals**, against the coordinator's
"stop if implausibly large (say > 600 bits)" threshold.  **UNDER THE
THRESHOLD; the wave proceeds.**

Method (`sw/phase_split_width.py`, committed with this document): expand every
`` `include `` inside `v30u_eu.sv`'s next-state `always @*`; take the set of
names ASSIGNED in the pre-loop region (the `else` arm of `if (ss_we)`, i.e.
blocks (a)–(f), EXCLUDING the preload, which assigns every `_n` from its own
flop and therefore crosses nothing); intersect it with every identifier
MENTIONED at or after the loop (a deliberately conservative read set — a name
mentioned only as an assignment target after the cut is still counted, so the
figure is an UPPER BOUND); drop `ifndef SYNTHESIS` trace-only names; sum the
declared widths.

* **UPPER BOUND ON THE CUT'S CROSSING SET: 490 bits / 63 names.**
* **THE WHOLE `_n` SET, for scale: 828 bits / 138 names** (plus `brk_p_n`,
  whose declared width is the `BRK_FLOOR` parameter and is 4 at its landed
  default, which the script prints as unparsed rather than guessing).  A shadow
  that simply captured all of stage 1's variable state would be ~832 bits and
  would be OVER the threshold; the crossing set is 59 % of it.
* The five widest members are `gpr_n` 128, `sreg_n` 64, and then sixteen
  16-bit members (`pc_n`, `psw_n`, `tmpa_n`, `tmpb_n`, `tmpc_n`, `opr_n`,
  `ind_n`, `count_n`, `stat_n`, `ea_residue_n`, `rdq0_n`, `rdq1_n`, and the
  scratch pair `v1`/`v2`).

⚠ **THIS IS A WIDTH, NOT AN ALM COST.**  What it costs in area is measured by
G6 and reported there, not predicted here.

---

## §3 THE THREE USER RULINGS THAT GOVERN THIS WAVE

**RULING 1 (2026-09-08) — THE SAVE-STATE FREEZE CLAUSE IS EXTENDED TO
`CE_HALF`.**  `v30_core.sv` already carries, unconditionally:

```
if (SS_WE && CE)    $error("SS_WE asserted while CE high (core not frozen)");
if (SS_WE && RESET) $error("SS_WE asserted during RESET");
if (CE && ss_we_q)  $error("CE resumed with SS command staging undrained ...");
```

Add the `CE_HALF` counterparts (`SS_WE && CE_HALF`, `CE_HALF && ss_we_q`).
⚠ `CE_HALF` currently exists only under `V30_MUXED_AD`, and that block's own
comment records that the ce/ce_half clauses had to move under the define while
the SS block could not follow them.  See RULING 3 — after the port move this
constraint may no longer apply.  Get the `ifdef` structure right and say in the
comment why it is where it is.

**RULING 2 — THE SHADOW IS DERIVED STATE AND IS NOT MAPPED.**  It goes on the
DERIVED class of `sw/ss_flop_whitelist_ucore.txt`, beside L1's `dec_q`, with a
justification that names the place the derivation is checkable by eye.
**`SS_COUNT` and `SS_VERSION` MUST NOT MOVE.**

⚠ A `ce_half`-gated shadow does not satisfy the DERIVED class's current wording
literally ("recomputed ... under the SAME commit condition ... so a save-state
restore ... reconstructs it ON THAT VERY EDGE").  Two honest ways to meet it;
**one must be picked, STATED, and justified in the RTL and in the results**:

  (i) give the shadow the commit condition `(ss_we || srst || ce_half)` with
      its input expression mirroring the `(srst && !ss_we)` selection exactly
      as `dec_addr_next` does — then it IS reconstructed on that very edge and
      the existing rule is met verbatim, no widening; or
  (ii) leave it `ce_half`-gated and WIDEN the DERIVED rule, in that file, from
      "on that very edge" to "no later than the first `ce_half` after the
      restore, which S-1 guarantees falls before the next `ce`".

(i) is the coordinator's recommendation because it changes no rule.  Whichever
is picked, the FIRST `ce` after reset must ALSO be handled: `ce_half_since_ce`
starts asserted so a run's first `CE` is not an S-1 violation, which means the
shadow may never have been captured at that point.  Say how it is handled.

**RULING 3 — SCOPE IS THE SPLIT ALONE.**  Do NOT bundle the `ucrom`
registration (the L2 lever).

---

## §4 THE STRUCTURAL PROBLEM AND ITS PRE-REGISTERED ANSWER

**`CE_HALF` DOES NOT EXIST IN A `V30_MUXED_AD`-OFF BUILD.**  It is declared
inside the `ifdef` as muxed-bus machinery, and `sw/demux_off_gate.py` is a
STANDING GATE that the define-OFF configuration builds and runs.  If the EU
needs `ce_half`, a de-muxed build has no enable for stage 1.

**PRE-REGISTERED INTERFACE CHANGE: `CE_HALF` MOVES OUT OF THE `ifdef` AND
BECOMES AN UNCONDITIONAL INPUT PORT OF `v30_core`.**  The rationale, to be
stated in the RTL: `V30_MUXED_AD` governs the BUS SHAPE, and once the EU is
phase-split `ce_half` is a CORE CLOCKING input, orthogonal to bus shape — which
is exactly what the module header already says the define is not about.  `AD`,
`AD_OE` and `DATA_I` stay exactly as they are.

**`sw/demux_off_gate.py` MUST PASS.**  Its "GONE" leg currently asserts that
splicing `.CE_HALF` back in FAILS naming the pin; after this change `CE_HALF`
IS a port of every configuration, so that one leg's premise is refuted by the
landing itself.  **The gate's `AD` and `AD_OE` legs are unchanged and must
still fail naming their pins**; the `CE_HALF` leg is re-registered to the new
interface and the change is reported, not hidden.

If a reason is found that the port move cannot work, the wave STOPS and
reports rather than inventing a second core.

---

## §5 THE BARS.  THESE ARE THE COORDINATOR'S AND ARE CARRIED VERBATIM.

  P-1  THE LANDING BAR. With the CE multicycle DELETED from `nec_test.sdc`,
       `sw/quartus_gate.py --seeds 5` PASSES E1-E5 on EVERY draw (Fmax >= 32.0
       MHz, worst setup > 0, TNS 0.000 setup AND hold on every domain, 0
       errors, 0 latches, 0 lpm_divide), on BOTH configurations (CONTROL and
       --retention). A single failing draw fails P-1.
  P-2  THE EXCEPTION IS GONE, AND THAT IS CHECKED, NOT ASSERTED. `nec_test.sdc`
       emits no "CE multicycle" info line, and every receipt's `core_domain`
       reports k = 1 with an EMPTY `off_class`. A receipt still showing k = 2
       fails P-2 however good its Fmax.
  P-3  THE COST, REGISTERED AS A PREDICTION SO A MISS IS VISIBLE EITHER WAY.
       CONTROL `worst-of-5@seeds{1..5}` lands in [34.0, 40.0] MHz. Wave 1's
       shape estimate is ~36 MHz and the pre-split HEAD figure is 38.99
       (worst of Wave 1's three CONTROL draws). Report the measured number
       against this interval whatever it is; a value OUTSIDE the interval is
       reported as a REFUTED PREDICTION, not re-derived.
  P-4  PIN IDENTITY — THE PROOF THAT NOTHING MOVED. All of:
         (a) `sw/chain_lfsr_gate.py` — the four per-seed signatures
             BYTE-IDENTICAL to the pre-edit run, with CHAIN_DEPTH_MAX,
             entry_st, coincide and every gap count identical too. **This is
             the load-bearing gate for this wave**: its CE train is built to
             the contract and nothing narrower, so it exercises the ADJACENT
             `ce`/`ce_half` case the split's worst budget assumes.
         (b) `sw/fz2_replay.py` scored-content sha256 IDENTICAL pre- and
             post-edit (the `tb_sys` binary receipt is the one field that may
             move, and must).
         (c) the full golden ladder at its registered values, listed in P-6.
  P-5  SAVE STATE DOES NOT MOVE. `sw/ss_lint.py --core ucore` exits 0 with
       `SS_COUNT` and `SS_VERSION` and `SS_TAG` UNCHANGED from HEAD, 0
       UNMAPPED, and the whitelist grown by exactly the shadow's entry.
  P-6  THE LADDER, EVERY LEG AT ITS REGISTERED VALUE:
         `r7_lint` PASS, 0 violations
         `check_core --opcodes all --cases 0`        169,000/169,000
         `check_core --opcodes 8F.0 --cases 0`       500/500
         HLT sweeps ⚠ WITH `--waits 0/1/2/3`         97 · 93 · 45 · 44 = 279/283
         `v0.1-w1` / `-w3`                           1,200 / 1,200
         `v0.1-w1 --opcodes EB`                      200
         the four evt cells w0/w1/w2/w3              200 / 1,200 / 200 / 1,200
         `v0.1-w1evt-biased`                         1,200
         `ulockstep --golden all --cases 50`         17,350/17,350 ALL LOCKSTEP
         `ghost_launch_law score`                    200/200
         `check_boot --core ucore`                   220 and 400
         `check_ab_sim --core ucore`                 MATCH over 187 rows
         `sm3_s16_score --core ucore`                1,320/1,371
         `sw/demux_off_gate.py`                      PASS, 3 legs
         `sw/test_artifact.py`                       45/45
         `sw/test_quartus_gate.py`                   254/254 (255 with a build tree)
         `sw/ucrom_mif_check.py`                     PASS
       ⚠ VERIFY EACH FIGURE AGAINST `standing_gates.md` BEFORE YOU RUN, not
       against this list — if the two disagree, `standing_gates.md` governs and
       the disagreement is itself a finding to report.
  P-7  DIVISOR INDEPENDENCE. `check_core --opcodes all --cases 0` is
       169,000/169,000 at `--ce-div 2, 3, 4 AND 8`. The split makes S-1
       load-bearing for the EU, not just the BIU, so this is no longer a
       cross-check — it is the bar that the core works on every contract-legal
       train. `--ce-div 1` must still be REFUSED.
  P-8  NON-VACUITY, DEMONSTRATED AND RECORDED, on all four of:
         (a) each NEW `$error` clause of RULING 1 fires when its condition is
             constructed;
         (b) S-1's `$fatal` still fires, and its message now names the EU's
             dependence, not only `t1_half2`/`ad_oe_data`;
         (c) the shadow register is LOAD-BEARING: perturbing one bit of it
             breaks a named gate leg (a shadow nothing depends on would pass
             every identity bar for the wrong reason);
         (d) the multicycle's deletion is what changes the timing: a control
             build with the multicycle RESTORED reports k = 2 again.
  P-9  THE REVERT CONDITION. If P-1 fails, or P-2 fails, or ANY leg of P-4/P-5/
       P-6/P-7 moves, THE LANDING DOES NOT HAPPEN. Revert the RTL and the SDC,
       report what was measured, and keep the pre-registration and the results
       document. A wave that reports "the split does not close" has done its
       job. **DO NOT soften a bar to make a landing possible, and do not
       re-scope the cut after seeing a result.**

---

## §6 BARS ADDED BY THIS DOCUMENT (permitted: "You may ADD bars")

  P-10 **THE PHASE-STABILITY PREMISE IS ASSERTED AT RUNTIME, NOT ARGUED.**
       The theorem's precondition is that every stage-1 output is unchanged
       between `ce_half(n)` and `ce(n+1)`.  An `ifndef SYNTHESIS` clause in
       `v30u_eu.sv` shall RE-EVALUATE stage 1 at every `ce` and `$fatal` if the
       shadow disagrees with it.  This turns the theorem into a per-clock
       falsifier over every golden case, every `ulockstep` scenario and all
       4 x 400,000 `chain_lfsr` clocks — the SIMPLE instrument, and the one
       that makes P-4's byte-identity mean "the premise held", not "no test
       reached the difference".  **It must be demonstrated non-vacuous.**
  P-11 **THE PIN READS MUST BE ON THE `ce` SIDE, AND THAT IS AUDITED, NOT
       ASSUMED.**  `pin_int`, `pin_nmi`, `pin_poll_n`, `eu_rd_edge`,
       `eu_rd_edge_d`, `eu_slot_busy_n` and `q_ripe_lead_n` — the module's live
       inputs and `r7_lint`'s one declared exception plus its two declared
       unresolved carriers — shall appear NOWHERE in stage 1.  Recorded as a
       grep with its result, before and after.
  P-12 **THE INTERFACE CHANGE IS REPORTED IN BOTH DIRECTIONS.**  `CE_HALF` is a
       port of `v30_core` in EVERY configuration after this wave.  The
       `demux_off_gate` "GONE" leg's `CE_HALF` clause is therefore
       re-registered; its `AD` and `AD_OE` clauses are NOT and must still fail
       naming their pins.  Any downstream integrator that instantiated the
       de-muxed core without `CE_HALF` will now fail to elaborate, **and that
       is the intended, surfaced consequence** — the same shape as the
       `SYNTHESIS`-without-`V30_MUXED_AD` refusal `demux_bus_prereg` §E-6
       records.

---

## §7 ORDER OF WORK, PRE-REGISTERED

 1. Verify HEAD, verify `git status --porcelain hdl/` shows no tracked
    modification.  **DONE — `a21195f38f`, clean.**
 2. **MEASURE THE SHADOW WIDTH.**  **DONE — §2, 490 bits.**
 3. Commit this pre-registration.  **Nothing under `hdl/` may be edited first.**
 4. Take the BEFORE side of every P-4 identity leg and every P-6 ladder leg on
    the UNEDITED tree, so the A/B is real.  Save the artifacts.
 5. The edits, as SEPARATE COMMITS in this order:
      (a) `CE_HALF` out of the `ifdef` + the RULING 1 assertion clauses
          + the S-1 message update.  Ladder must still be green here.
      (b) the peel itself + the whitelist entry.
      (c) the SDC deletion.
 6. The full ladder, then G6 on both configurations.
 7. The results document, scored as registered.

**DISCIPLINE**: single-writer guard by EXACT binary name before any Quartus
stage; `~/.cache/ucsimt-tmp` for big intermediates, never `/tmp`; receipted
binaries rebuilt with `python3 sw/check_core.py --build --core ucore`; a number
with no artifact id is not quotable; record what was measured, not what was
expected.
