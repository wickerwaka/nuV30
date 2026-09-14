#!/usr/bin/env python3
"""WAVE 15 -- THE ARMS FOR THE `q_ripe_lead_n` REFORMULATION.

**UNLIKE WAVE 14's, ARM-A IS CLAIMED TO BE BEHAVIOUR-PRESERVING**, and Q-2 is
the gate that decides whether the claim survives.  Nothing here is landed.

THE BASE IS THE **SPLIT** TREE (`850ef46559`), the same base WAVES 13 and 14
measured on -- so this wave's base arm is a free control against both.

  ARM-A `qripe_presel`  -- C1 of `qripe_reform_derivation_2026-09-13.md` §3,
                           chosen in `qripe_reform_prereg_2026-09-13.md` §1
                           BEFORE this file was written.  The BIU publishes the
                           ripe-lead level for each of the two things the EU can
                           do to the queue this clock (pop / not) and the EU
                           picks the one it is doing.  NO FLOP.
  ARM-B `qripe_s1q`     -- C2, the CONDITIONAL second arm registered in §4:
                           ARM-A plus the select taken off the `s1q` shadow.
                           ONE flop.  Built only under §4's condition.

usage:
    python3 sw/wave15_arms.py --gen --arm base|qripe_presel|qripe_s1q
    python3 sw/wave15_arms.py --gen --arm qripe_presel --nonvacuity
"""
import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/wave15')
BASE_COMMIT = '850ef46559'

R7 = 'sw/r7_lint.py'
BIU = 'hdl/rtl/ucore/v30u_biu.sv'
EU = 'hdl/rtl/ucore/v30u_eu.sv'
CORE = 'hdl/rtl/ucore/v30_core.sv'


def sh(cmd, cwd=ROOT):
    return subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)


def _sub(path, old, new, count=1):
    """Exact, unique textual substitution.  REFUSES on anything but `count`
    occurrences -- a silent no-op edit is how an arm gets measured against
    itself."""
    t = open(path).read()
    n = t.count(old)
    if n != count:
        raise SystemExit(f'REFUSING: anchor occurs {n} times (want {count}) in '
                         f'{path}:\n---\n{old}\n---')
    open(path, 'w').write(t.replace(old, new))


# --------------------------------------------------------------------------- #
# THE ANCHORS.  Every one is verbatim from the base tree; `_sub` refuses if any
# is not unique, which is the check that the edit reached the file it meant.
# --------------------------------------------------------------------------- #
A_POP = """        if (pop_l) begin
            q_head = (q_head == 3'd5) ? 3'd0 : q_head + 3'd1;
            q_cnt  = q_cnt - 4'd1;
        end"""

B_POP = """        if (pop_l) begin
            q_head = (q_head == 3'd5) ? 3'd0 : q_head + 3'd1;
            // WAVE 15 C1 -- THE DECREMENT IS APPLIED AT THE END OF THIS BLOCK,
            // NOT HERE.  `q_cnt`'s cone is then POP-FREE all the way to the
            // publish, which is what lets THE EU CONTRACT below hand the EU two
            // pure-register levels instead of one level that depends on the
            // EU's own act.  The four places that READ `q_cnt` between here and
            // the end are compensated with `pop_eff`, and they are the whole
            // list (`occ` twice, `qi`, and the publish).  VALUE-IDENTICAL: the
            // block's own falsifier below `$fatal`s on the first clock it is
            // not.
            pop_eff = 1'b1;
        end"""

A_FLUSH = "            q_cnt = 4'd0; q_head = 3'd0; grn_n = 2'd0; grn_ttl = 2'd0;"
B_FLUSH = ("            q_cnt = 4'd0; q_head = 3'd0; grn_n = 2'd0; grn_ttl = 2'd0;\n"
           "            pop_eff = 1'b0;   // WAVE 15 C1: the flush OVERWRITES the\n"
           "                              // count, so the pop's decrement is gone\n"
           "                              // with it.  This is the one interaction\n"
           "                              // between the two EU acts and it is\n"
           "                              // `q_flush` wins.")

A_OCC1 = """                occ = {1'b0, q_cnt}
                    + (cur_fetch ? {3'b0, cur_pn} : 5'd0)"""
B_OCC1 = """                occ = {1'b0, q_cnt} - {4'b0, pop_eff}   // WAVE 15 C1
                    + (cur_fetch ? {3'b0, cur_pn} : 5'd0)"""

A_QI = "                    qi = {1'b0, q_head} + q_cnt;"
B_QI = ("                    qi = {1'b0, q_head} + q_cnt - {3'b0, pop_eff};"
        "  // WAVE 15 C1")

A_OCC2 = """            occ = {1'b0, q_cnt}
                + ((run && cur_fetch) ? {3'b0, cur_pn} : 5'd0)"""
B_OCC2 = """            occ = {1'b0, q_cnt} - {4'b0, pop_eff}   // WAVE 15 C1
                + ((run && cur_fetch) ? {3'b0, cur_pn} : 5'd0)"""

A_TAIL = """        if (run && evald && (sev != 2'd3) && !evi_l) sev = sev + 2'd1;

    end
end"""
B_TAIL = """        if (run && evald && (sev != 2'd3) && !evi_l) sev = sev + 2'd1;

    end

    //======================================================================
    // WAVE 15 C1 -- THE POP, APPLIED LAST.
    //======================================================================
    // `q_cnt_np` is the queue count this edge would take IF THE EU DID NOT POP
    // -- flush and landing included, pop excluded.  It is the basis THE EU
    // CONTRACT publishes both levels from, and it depends on NO EU act except
    // `q_flush`.  `q_cnt` itself keeps its exact former value, so the register
    // commit, `+utrace` and every other consumer below are unchanged.
    //
    // `pop_eff` is 0 on an `ss_we` clock by initialisation, so this arm is
    // vacuous there, exactly as the in-place decrement was.
    q_cnt_np = q_cnt;
    if (pop_eff) q_cnt = q_cnt - 4'd1;
end"""

A_DECL = """reg  [3:0] q_cnt;
reg  [1:0] grn_n;         // newest bytes not yet POPPABLE"""
B_DECL = """reg  [3:0] q_cnt;
reg  [3:0] q_cnt_np;      // WAVE 15 C1: ...before the EU's own pop this clock
reg  [1:0] grn_n;         // newest bytes not yet POPPABLE"""

A_TEMPS = "reg        ne_now, kill_l, evi_l, hfree_l, pop_l, qse_l;"
B_TEMPS = ("reg        ne_now, kill_l, evi_l, hfree_l, pop_l, qse_l;\n"
           "reg        pop_eff;    // WAVE 15 C1: `pop_l` AND the flush did not "
           "wipe it")

A_TINIT = "    hfree_l = 1'b0; pop_l = 1'b0; qse_l = 1'b0; sev_now = 2'd0;"
B_TINIT = ("    hfree_l = 1'b0; pop_l = 1'b0; qse_l = 1'b0; sev_now = 2'd0;\n"
           "    pop_eff = 1'b0; q_cnt_np = 4'd0;")

A_PORT = "    output            q_ripe_lead_n, // ...or will be on the NEXT one (1BL lead)"
B_PORT = """    // WAVE 15 C1 -- THE 1BL LEAD IS PUBLISHED AS TWO LEVELS, ONE FOR EACH
    // THING THE EU CAN DO TO THE QUEUE THIS CLOCK.  Neither depends on `q_pop`;
    // the EU selects with its own act.  See THE EU CONTRACT below.
    output            q_ripe_lead_n0, // ...will be ripe NEXT clock if NO pop
    output            q_ripe_lead_n1, // ...and if the EU DOES pop this clock"""

A_PUB = """wire [3:0] poppable_n = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
assign q_ripe_lead_n  = (poppable_n != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt != 4'd0));"""

B_PUB = """//
// WAVE 15 C1 -- AND IT IS PUBLISHED AS TWO LEVELS, BECAUSE THE ANSWER DEPENDS
// ON WHETHER THE EU POPS AND THE EU IS THE ONE WHO KNOWS.
//
// Walking every write to the three operands of this predicate, the dependence
// on the EU is exactly TWO BITS: `q_pop` (the decrement, ONE place) and
// `q_flush` (the zeroing).  A flush OVERWRITES the count, so on a flush the pop
// is irrelevant and there are THREE levels, not four -- and `q_flush` is not on
// the binding arc, so only the pop is split here.
//
// `q_cnt_np` is the count WITHOUT the pop, so both levels below are pure
// functions of the BIU's own registers (and `q_flush`).  It is the SAME
// function against two thresholds: "at least one" and "at least two".  The EU
// selects with `q_pop && q_ripe && !q_flush` -- two of its own outputs and a
// BIU REGISTER port it already has -- so its pop never leaves the EU, and the
// EU -> BIU -> EU combinational excursion this predicate used to make is gone.
//
// F7 IS UNCHANGED AND IS THE REASON THIS IS SHAPED SO: the step must see the
// queue AS IT WILL BE, pop included.  Severing that costs 181 goldens
// (`FA` 74 + `FB` 68 + `INT.FB` 39, all ONE_BYTE_LOGIC forms, which is
// `wait_retire_lead`'s only caller).  Nothing here severs it; it re-associates
// which side of the module boundary the selection happens on.
wire [3:0] q_cnt_np1  = q_cnt_np - 4'd1;
wire [3:0] poppable_n0 = (grn_ttl != 2'd0) ? (q_cnt_np  - {2'b0, grn_n}) : q_cnt_np;
wire [3:0] poppable_n1 = (grn_ttl != 2'd0) ? (q_cnt_np1 - {2'b0, grn_n}) : q_cnt_np1;
assign q_ripe_lead_n0 = (poppable_n0 != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt_np  != 4'd0));
assign q_ripe_lead_n1 = (poppable_n1 != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt_np1 != 4'd0));

`ifndef SYNTHESIS
//--------------------------------------------------------------------------
// THE FALSIFIER.  The ORIGINAL expression is kept VERBATIM as a reference and
// compared every clock the EU samples -- the `V30_MUXED_AD` precedent, where
// the historical nine-way mux is kept as a sim-only reference compared every
// fabric clock.  Clause (1) is the identity itself; clause (2) is what makes
// the EU's local select formula sound, because the EU cannot see `pop_eff`.
//--------------------------------------------------------------------------
wire [3:0] poppable_n_ref = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
wire q_ripe_lead_n_ref = (poppable_n_ref != 4'd0) ||
                         ((grn_ttl == 2'd1) && (q_cnt != 4'd0));
wire q_ripe_lead_n_comp = pop_eff ? q_ripe_lead_n1 : q_ripe_lead_n0;
always @(posedge clk) if (ce && !srst && !ss_we) begin
    if (q_ripe_lead_n_comp !== q_ripe_lead_n_ref)
        $fatal(1, "v30u_biu: WAVE 15 C1 IDENTITY VIOLATED at %0t -- composed=%b reference=%b  (pop_eff=%b q_cnt=%0d q_cnt_np=%0d grn_n=%0d grn_ttl=%0d)",
               $time, q_ripe_lead_n_comp, q_ripe_lead_n_ref,
               pop_eff, q_cnt, q_cnt_np, grn_n, grn_ttl);
    if (pop_eff !== (q_pop && q_ripe && !q_flush))
        $fatal(1, "v30u_biu: WAVE 15 C1 SELECT VIOLATED at %0t -- pop_eff=%b but q_pop=%b q_ripe=%b q_flush=%b.  The EU composes the select from those three, so they must agree.",
               $time, pop_eff, q_pop, q_ripe, q_flush);
end
`endif"""

# ---- the EU side ---------------------------------------------------------- #
A_EUPORT = "    input             q_ripe_lead_n, // ...and it will be ripe NEXT clock"
B_EUPORT = """    input             q_ripe_lead_n0, // ...ripe NEXT clock if NO pop
    input             q_ripe_lead_n1, // ...and if this clock's own pop happens"""

A_EUSEL = "assign q_pop   = q_demand;"
B_EUSEL = """assign q_pop   = q_demand;

// WAVE 15 C1 -- THE SELECTION HAPPENS HERE, NOT IN THE BIU.
//
// The BIU publishes the 1BL retire lead for each of the two things this module
// can do to the queue on this clock, both off ITS OWN REGISTERS.  The EU's pop
// is a one-bit fact this module already owns, and `q_ripe` is a BIU REGISTER
// port, so the select costs one AND and one MUX HERE and the value the clocked
// step reads no longer makes a combinational excursion into the BIU and back.
//
// `!q_flush` is a term because the flush OVERWRITES the queue count after the
// pop has decremented it, so on a flush clock the published no-pop level is the
// right one.  The BIU `$fatal`s (`ifndef SYNTHESIS`) if this expression ever
// disagrees with its own `pop_eff`, and again if the composed value ever
// differs from the original predicate -- so the two consumer sites below
// (`v30u_eu_step.svh`, `v30u_eu_arm_decode2.svh`) are BYTE-UNCHANGED and read
// exactly what F7 promises them.
wire q_ripe_lead_n = (q_pop && q_ripe && !q_flush) ? q_ripe_lead_n1
                                                   : q_ripe_lead_n0;"""

# ---- the top ------------------------------------------------------------- #
A_CWIRE = "wire        q_ripe, q_ripe_lead_n;"
B_CWIRE = "wire        q_ripe, q_ripe_lead_n0, q_ripe_lead_n1;   // WAVE 15 C1"

A_CMAP = "    .q_ripe_lead_n(q_ripe_lead_n),"
B_CMAP = ("    .q_ripe_lead_n0(q_ripe_lead_n0),\n"
          "    .q_ripe_lead_n1(q_ripe_lead_n1),")


def arm_qripe_presel(wt, nonvacuity=False, nonvacuity2=False, nonvacuity3=False):
    biu = os.path.join(wt, BIU)
    eu = os.path.join(wt, EU)
    core = os.path.join(wt, CORE)
    _sub(biu, A_DECL, B_DECL)
    _sub(biu, A_TEMPS, B_TEMPS)
    _sub(biu, A_TINIT, B_TINIT)
    _sub(biu, A_PORT, B_PORT)
    _sub(biu, A_POP, B_POP)
    _sub(biu, A_FLUSH, B_FLUSH)
    _sub(biu, A_OCC1, B_OCC1)
    _sub(biu, A_QI, B_QI)
    _sub(biu, A_OCC2, B_OCC2)
    _sub(biu, A_TAIL, B_TAIL)
    _sub(biu, A_PUB, B_PUB)
    _sub(eu, A_EUPORT, B_EUPORT)
    _sub(eu, A_EUSEL, B_EUSEL)
    _sub(core, A_CWIRE, B_CWIRE)
    _sub(core, A_CMAP, B_CMAP, count=2)
    # THE DECLARED COST: `r7_lint`'s unresolved list must name the two nets the
    # one it declares was split into.  Declared here, in the arm, so that it is
    # visible in the arm's own diff and cannot be mistaken for a repo-wide
    # loosening.
    _sub(os.path.join(wt, R7), A_R7, B_R7)
    if nonvacuity:
        # ⚠ THE NON-VACUITY DEMONSTRATION.  Perturb ONE term of the published
        # pair and the falsifier must fire.  A falsifier that cannot fail is
        # not a falsifier -- nine instruments in this campaign have produced
        # confident, wrong, vacuous results.
        _sub(biu, "((grn_ttl == 2'd1) && (q_cnt_np1 != 4'd0));",
                  "((grn_ttl == 2'd2) && (q_cnt_np1 != 4'd0));  // PERTURBED")
    if nonvacuity2:
        # THE SECOND CLAUSE'S OWN NON-VACUITY: drop the flush's cancellation of
        # the pop.  `pop_eff` then no longer equals `q_pop && q_ripe && !q_flush`
        # -- the formula the EU composes its select from -- so clause (2) must
        # fire.  It also proves the flush/pop interaction is REACHABLE and not a
        # term written for a case that never happens.
        _sub(biu, "            pop_eff = 1'b0;   // WAVE 15 C1: the flush",
                  "            // PERTURBED (nonvacuity2): pop_eff NOT cleared\n"
                  "            // WAVE 15 C1: the flush")
    if nonvacuity3:
        # CLAUSE (2)'s NON-VACUITY.  Arm `pop_eff` from `q_pop` alone, so it no
        # longer equals `q_pop && q_ripe && !q_flush` -- the formula the EU
        # composes its select from and the only thing that makes the EU's local
        # mux sound.  Clause (2) must fire.
        _sub(biu, "    pop_eff = 1'b0; q_cnt_np = 4'd0;",
                  "    pop_eff = q_pop; q_cnt_np = 4'd0;   // PERTURBED (nonvacuity3)")


A_R7 = """    "q_ripe_lead_n":
        "§73's own list of REGISTER-ONLY EU inputs.  Driven from `poppable_n` "
        "off the queue's procedural next-state (`q_cnt`, `grn_ttl`, `grn_n`), "
        "which is the queue's own bookkeeping and not the READY sample.",
}"""

B_R7 = """    "q_ripe_lead_n":
        "§73's own list of REGISTER-ONLY EU inputs.  Driven from `poppable_n` "
        "off the queue's procedural next-state (`q_cnt`, `grn_ttl`, `grn_n`), "
        "which is the queue's own bookkeeping and not the READY sample.",
    # ⚠ WAVE 15 C1 SPLIT THE NET ABOVE IN TWO, AND THE TWO ENTRIES BELOW ARE
    # PART OF THE MECHANISM'S DECLARED COST -- not a silent widening.  The
    # ARGUMENT IS UNCHANGED, character for character: both are driven from the
    # queue's procedural next-state (`q_cnt_np`, `grn_ttl`, `grn_n`) and neither
    # is the READY sample.  What changed is that the predicate is now published
    # once per value of the EU's own pop, so that the EU's act does not have to
    # travel into this module and back to be answered.  The entry the two
    # replace is kept above so that a reader can see the list did not grow by
    # forgetting anything.
    "q_ripe_lead_n0":
        "§73's own list of REGISTER-ONLY EU inputs, WAVE 15 C1's no-pop half.  "
        "Driven from `poppable_n0` off the queue's procedural next-state "
        "(`q_cnt_np`, `grn_ttl`, `grn_n`), which is the queue's own bookkeeping "
        "and not the READY sample.",
    "q_ripe_lead_n1":
        "§73's own list of REGISTER-ONLY EU inputs, WAVE 15 C1's pop half.  "
        "Driven from `poppable_n1` off the same procedural next-state minus the "
        "EU's own pop, which is the queue's own bookkeeping and not the READY "
        "sample.",
}"""


# --------------------------------------------------------------------------- #
# ARM-B `qripe_s1q` -- C2, the CONDITIONAL second arm of the pre-registration
# §4.  ARM-A plus: the mux SELECT is taken off the phase split's own `s1q`
# shadow instead of live stage-1 logic, so stage 2's cone for this value
# launches at a REGISTER on both of its inputs.  ⚠ IT ADDS ONE FLOP, `s1q`
# 778 -> 779, and it is SPLIT-DEPENDENT.
# --------------------------------------------------------------------------- #
A_S1Q_EUSEL = """wire q_ripe_lead_n = (q_pop && q_ripe && !q_flush) ? q_ripe_lead_n1
                                                   : q_ripe_lead_n0;"""
B_S1Q_EUSEL = """// WAVE 15 C2 -- ...AND THE SELECT RIDES THE PHASE SPLIT'S OWN SHADOW.
// `q_pop`, `q_ripe` and `q_flush` are all constant across the CPU cycle
// (`q_ripe` is a BIU REGISTER; the other two are stage-1 quantities), so this
// one bit belongs in `s1_bus` like every other stage-1 output -- and the
// split's OWN premise assertion `$fatal`s if it is not constant, which is this
// arm's free falsifier.  With the select shadowed, stage 2 reads THREE
// registers -- the two published levels and this bit -- and the `ce -> ce` cone
// no longer contains any of stage 1's logic on this path.
wire s1w_qripe_pop = q_pop && q_ripe && !q_flush;"""

A_S1Q_DECL = """reg            row_flush;"""
B_S1Q_DECL = """reg            qripe_pop;      // WAVE 15 C2: the shadowed 1BL-lead select
reg            q_ripe_lead_n;  // ...and the level it selects, stage 2 only
reg            row_flush;"""

A_S1Q_ALIAS = "    q_bnd_pop              = s1w_q_bnd_pop;"
B_S1Q_ALIAS = ("    q_bnd_pop              = s1w_q_bnd_pop;\n"
               "    qripe_pop              = s1w_qripe_pop;")

A_S1Q_PACK = """        it_writes_tmpa
        };"""
B_S1Q_PACK = """        it_writes_tmpa, qripe_pop
        };"""

A_S1Q_UNPACK = """        it_writes_tmpa
        } = s1q;"""
B_S1Q_UNPACK = """        it_writes_tmpa, qripe_pop
        } = s1q;"""

A_S1Q_W = "localparam int S1W = 778;   // 495 loop-carried + 283 wire cone.  RE-DERIVED"
B_S1Q_W = ("localparam int S1W = 779;   // WAVE 15 C2: 778 + `qripe_pop`, THE ONE FLOP\n"
           "                           // THIS ARM ADDS AND THE ONLY ONE.  `s1q` is\n"
           "                           // DERIVED state and is deliberately NOT\n"
           "                           // save-state mapped, so `SS_COUNT` does not\n"
           "                           // move -- see THE PHASE SPLIT below.\n"
           "                            // 495 loop-carried + 283 wire cone.  RE-DERIVED")

A_S1Q_SSWE = """            `include "v30u_eu_preload.svh"
            `include "v30u_eu_ss_write.svh"
        end else begin"""
B_S1Q_SSWE = """            `include "v30u_eu_preload.svh"
            `include "v30u_eu_ss_write.svh"
            // WAVE 15 C2: `q_ripe_lead_n` is a stage-2 value and this arm never
            // reads it, but an `always @*` reg must be written on every path or
            // it infers a LATCH -- and G6 gates on 0 latches.
            q_ripe_lead_n = q_ripe_lead_n0;
        end else begin"""

A_S1Q_STOP = """        } = s1q;


        stop = 1'b0;"""
B_S1Q_STOP = """        } = s1q;

        // WAVE 15 C2 -- THE SELECTION, OFF THE SHADOW.  Both inputs are BIU
        // register cones and `qripe_pop` is a flop, so nothing in this
        // expression launches in stage 1.
        q_ripe_lead_n = qripe_pop ? q_ripe_lead_n1 : q_ripe_lead_n0;

        stop = 1'b0;"""


def arm_qripe_s1q(wt, nonvacuity=False, nonvacuity2=False, nonvacuity3=False):
    arm_qripe_presel(wt)
    eu = os.path.join(wt, EU)
    _sub(eu, A_S1Q_EUSEL, B_S1Q_EUSEL)
    _sub(eu, A_S1Q_DECL, B_S1Q_DECL)
    _sub(eu, A_S1Q_ALIAS, B_S1Q_ALIAS)
    _sub(eu, A_S1Q_PACK, B_S1Q_PACK)
    _sub(eu, A_S1Q_UNPACK, B_S1Q_UNPACK)
    _sub(eu, A_S1Q_W, B_S1Q_W)
    _sub(eu, A_S1Q_SSWE, B_S1Q_SSWE)
    _sub(eu, A_S1Q_STOP, B_S1Q_STOP)


ARMS = {'qripe_presel': arm_qripe_presel, 'qripe_s1q': arm_qripe_s1q}


def wt_of(name):
    return os.path.join(SCRATCH, 'wt_' + name)


def gen(name, base, nonvacuity=False, nonvacuity2=False, nonvacuity3=False):
    if sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip():
        raise SystemExit("REFUSING: the main tree's hdl/ carries tracked changes.")
    os.makedirs(SCRATCH, exist_ok=True)
    sfx = ('_nv' if nonvacuity else '_nv2' if nonvacuity2
           else '_nv3' if nonvacuity3 else '')
    wt = wt_of(name + sfx)
    if os.path.exists(wt):
        sh(f'git worktree remove --force {wt}')
        shutil.rmtree(wt, ignore_errors=True)
    r = sh(f'git worktree add --detach {wt} {base}')
    if r.returncode:
        raise SystemExit('worktree add failed:\n' + r.stdout + r.stderr)
    print(f'worktree {wt}\n  at {sh("git rev-parse HEAD", wt).stdout.strip()}  (base {base})')
    if name != 'base':
        ARMS[name](wt, nonvacuity=nonvacuity, nonvacuity2=nonvacuity2,
               nonvacuity3=nonvacuity3)
    files = f'{BIU} {EU} {CORE} {R7}'
    dif = sh(f'git diff -- {files}', wt).stdout
    n = len([l for l in dif.split('\n')
             if l and l[0] in '+-' and l[:3] not in ('+++', '---')])
    print(sh(f'git diff --stat -- {files}', wt).stdout)
    print(f'  arm edit: {n} changed source lines')
    if name != 'base' and n == 0:
        raise SystemExit('REFUSING: the arm made no edit.')
    if name == 'base' and n != 0:
        raise SystemExit('REFUSING: the BASE worktree is not clean.')
    # THE FLOP CHECK AT THE SOURCE, inherited from WAVE 14 P-3: no arm may
    # introduce a non-blocking assignment.  A pipeline stage boundary IS a
    # register; refusing one textually costs nothing and a fit costs an hour.
    added = [l for l in dif.split('\n') if l.startswith('+') and not l.startswith('+++')]
    bad = [l for l in added if '<=' in l and not l.lstrip('+').lstrip().startswith('//')]
    print(f'  Q-6 source check: {len(added)} added lines, {len(bad)} carrying a '
          f'non-blocking assignment  '
          f'({"OK -- no flop added" if not bad else "*** A FLOP MAY HAVE BEEN ADDED ***"})')
    for l in bad:
        print('    ' + l)
    # ...and the whole tree must be otherwise untouched.
    other = [l for l in sh('git status --porcelain', wt).stdout.split('\n')
             if l and not l.startswith('??')
             and l.split()[-1] not in (BIU, EU, CORE, R7)]
    print(f'  tree check: {len(other)} other tracked modification(s)')
    for l in other:
        print('    ' + l)
    if other:
        raise SystemExit('REFUSING: the arm touched something else.')
    return wt


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--gen', action='store_true')
    ap.add_argument('--arm', required=True)
    ap.add_argument('--base', default=BASE_COMMIT)
    ap.add_argument('--nonvacuity', action='store_true')
    ap.add_argument('--nonvacuity2', action='store_true')
    ap.add_argument('--nonvacuity3', action='store_true')
    a = ap.parse_args()
    if a.gen:
        gen(a.arm, a.base, a.nonvacuity, a.nonvacuity2, a.nonvacuity3)
    else:
        ap.error('nothing to do')
