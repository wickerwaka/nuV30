# WAVE 15 — **THE SPEC DERIVATION AND THE CANDIDATE ENUMERATION.  COMMITTED BEFORE A CANDIDATE IS CHOSEN AND BEFORE THE FIRST `hdl/` EDIT.**

This document is bar **Q-1** and nothing else.  **It names no winner.**  The
choice, with its reason, is the SEPARATE commit that follows
(`qripe_reform_prereg_2026-09-13.md`), and that commit is also before the first
`hdl/` edit.  This is the anatomy-first discipline that produced WAVES 6 and 7
and that WAVES 2, 3 and 4 each skipped and were refuted for.

**MEASUREMENT AND MECHANISM-FINDING ONLY.  THIS WAVE LANDS NOTHING.**
**OFFLINE ONLY — NO BOARD, NO FLASH.**

---

## §1 WHAT `q_ripe_lead_n` MEANS, FROM THE SPEC

### 1.1 THE SPEC IS FIVE LINES OF C++

`sim/biu_timed.cpp:1307`:

```c++
void BiuTimed::wait_retire_lead() {
    if (brk_pending_) return;
    int guard = 0;
    while ((q_.empty() || q_.front().ready > clk_ + 1) && ++guard < 4096) tick();
}
```

Its **one** caller is `sim/loader_impl.h:334`, inside the `ONE_BYTE_LOGIC`
(pre-decode-executed) arm, between the HALT early-out and the flag write:

```c++
        biu.wait_retire_lead();
        switch (pla3::bl1_op(v)) { ... }      // DI / EI / STC / CLC / CMC / ...
        m.set_flags(m.psw);
        biu.charge(1);   // pre-decode-executed forms retire in 2 clocks
```

So the quantity is: **"the queue's front byte is ready by `clk_ + 1`"** —
*not* "is ready now".  It is a **ONE-CLOCK LEAD** on ripeness, and it is asked
**after** the instruction's own opcode pop has already happened, because the
pop is what got us into the decode.

### 1.2 THE RTL RENDERING, AND THE TWO VIEWS

`hdl/rtl/ucore/v30u_biu.sv:922`, inside **THE EU CONTRACT (F7)** block:

```systemverilog
wire [3:0] poppable_n = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
assign q_ripe_lead_n  = (poppable_n != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt != 4'd0));
```

`q_cnt`, `grn_n` and `grn_ttl` here are the **procedural next-state** variables
— the `_n` view, "the level the register takes at this edge" — *not* the
registers `r_q_cnt` / `r_grn_n` / `r_grn_ttl`.  The register-view twin one
block up (`v30u_biu.sv:842`) is `poppable`, and it drives `q_ripe`, the
**NOW** answer the combinational act decode reads.

Two disjunctive terms, and they are the two ways the front byte can be ready by
the clock after next:

| term | meaning |
|---|---|
| `poppable_n != 0` | the front byte is **already** past its green window at `c+1` — ripe NOW, in the clock the step is stepping into |
| `(grn_ttl == 1) && (q_cnt != 0)` | the green window has exactly **one clock left to run** at `c+1`, so a byte that exists becomes poppable at `c+2` |

which is `q_.front().ready <= clk_ + 1` evaluated at `clk_ = c+1`, term for term.

### 1.3 THE TWO CONSUMERS.  BOTH ARE IN THE CLOCKED STEP.  THERE ARE NO OTHERS.

`grep -rn q_ripe_lead_n hdl/rtl/ucore/` finds exactly two *reads*:

1. **`v30u_eu_arm_decode2.svh:126`** — `if (q_ripe_lead_n || brk_seen)`: the
   1BL execute strobe is taken on THIS edge (`S_1BL_CHG`) or deferred to a pure
   wait state (`S_1BL_LEAD`).
2. **`v30u_eu_step.svh:135`** — `S_1BL_LEAD: if (!q_ripe_lead_n) stop = 1'b1;`
   — the wait itself.

Both are inside the EU's **clocked step**, which is stage 2 of the phase split.
Neither is in the combinational act decode.  That is F7's rule applied:
*the step produces the EU's state for the clock this edge OPENS, so it must see
the BIU as it will then be.*

### 1.4 **WHAT F7 REQUIRES, IN ONE SENTENCE**

> **The value the step reads must be the BIU's queue level for the clock the
> edge opens — WHICH INCLUDES THE EFFECT OF THE EU'S OWN POP ON THIS CLOCK.**

That is the whole contract, and it is why the excursion exists.  Since the
chain flattening (WAVE 7) a single clock can walk
`S_EPOP · S_TAIL · S_INSTR_END · S_TAKE_OPC · S_DECODE · S_DECODE2`, so the
opcode pop (`q_pop` asserted, `S_TAKE_OPC`) and the 1BL decode
(`S_DECODE2`, reading `q_ripe_lead_n`) happen **in the same clock**.  The decode
must see the queue **after** the pop it is itself making.

### 1.5 WHAT BREAKING IT COSTS — **181 GOLDENS, AND THEY ARE ONE FAMILY**

WAVE 14's two probe arms both scored `168,819 / 169,000` on
`check_core --core ucore --opcodes all --cases 0`
(`sw/testdata/wave14/logs/p2_equiv.log.gz`).  The 181 are:

| suite | failing | first divergence |
|---|---:|---|
| `FA` (`di`) | **74** of 500 | `(1, 'bus')` |
| `FB` (`ei`) | **68** of 500 | `(1, 'bus')` |
| `INT.FB` (`ei <int d=n>`) | **39** of 200 | `(1, 'bus')` |
| | **181** | |

**Every one of them is a `ONE_BYTE_LOGIC` form, which is `wait_retire_lead`'s
only caller.**  Nothing else in 169,000 cases moves.  `FA` and `FB` fail in
OPPOSITE directions on the same row (`exp 430224 got 168080` and
`exp 168080 got 430224`) — the flag write lands one clock early or one clock
late depending on which way the severed value happened to read.  The arch dumps
survive on 154 of the 181 (`arch 168973`), which is the signature of a pure
TIMING displacement of the write, not a wrong value.

**This is the exact set any behaviour-preserving reformulation must keep at
169,000 / 169,000, and it is the reason F7 may not be weakened to make a
mechanism work.**

---

## §2 THE LOOP, TERM BY TERM

### 2.1 WHICH TERMS DEPEND ON THE EU'S OWN ACT AND WHICH DO NOT

Walking `v30u_biu.sv`'s next-state block (`always @*`, lines 1640–2580) for every
write to the three operands of `q_ripe_lead_n`:

| # | line | write | depends on an EU act? |
|---|---|---|---|
| 1 | 1679–1681 | `q_cnt = r_q_cnt; grn_n = r_grn_n; grn_ttl = r_grn_ttl;` | **no** — registers |
| 2 | 1919 | `if (pop_l) q_cnt = q_cnt - 4'd1;` where `pop_l = pop_now = q_pop && q_ripe` and `q_ripe = (poppable != 0)` is a **pure register function** | **YES — `q_pop`, ONE BIT** |
| 3 | 2064 | `if (q_flush) begin q_cnt = 0; grn_n = 0; grn_ttl = 0; end` | **YES — `q_flush`, ONE BIT** |
| 4 | 2183–2184 | `if (run && ts==T4 && cur_fetch && cur_pn!=0) begin q_cnt += cur_pn; grn_n = cur_pn; set_grn = 1; end` | **no** — `run`/`ts`/`cur_*` are the cycle registers |
| 5 | 2573–2574 | `if (set_grn) grn_ttl = new_ttl; else if (grn_ttl != 0) grn_ttl--;` | **no** |
| 6 | 1792–1794 | the `ss_we` decode | **no** |

**THE PARTITION IS THEREFORE EXACTLY TWO BITS**:

> `q_ripe_lead_n = f(BIU registers, q_pop, q_flush)`
>
> and because a flush **overwrites** `q_cnt` after the pop has decremented it,
> the two do not interact: **on a flush the pop is irrelevant.**  There are
> three distinct levels, not four:
>
> ```
> q_ripe_lead_n = q_flush ? L_flush : ( (q_pop && q_ripe) ? L_pop : L_none )
> ```
>
> where `L_flush`, `L_pop` and `L_none` are **pure functions of BIU registers**
> and `q_ripe` is **already a BIU register output the EU is already given**.

`grn_n` and `grn_ttl` are touched by `q_flush` **only**; `q_pop` reaches
`q_ripe_lead_n` through the single 4-bit decrement at line 1919 and nowhere
else.  (`pop_l` also advances `q_head` and, through `pop_now`, gates `qs_e_now`
→ `e_pend`; neither reaches the three operands.)

`q_cnt` is READ, after the pop and before the end, at exactly four places:
`occ` at T3 (2142), `qi` at T4 (2173), the push (2183) and the eval's `occ`
(2305) — plus the register commit (2632) and the `+utrace` display (2960).
**Any reformulation that moves the decrement must compensate all of them, and
that list is the whole of it.**  ⚠ `qi = q_head + q_cnt` is provably
**pop-invariant** (the pop advances the head and decrements the count, and the
tail index is their sum) but the code computes it from the *post-pop* pair, so
a moved decrement must be compensated there too or the mod-6 reduction differs.

### 2.2 **THE MEASURED FACT: ON THE SPLIT TREE THE BINDING ROUND TRIP IS THE `q_pop` ONE, NOT THE `q_flush` ONE.**

From WAVE 14's own committed base netlists
(`sw/testdata/wave14/w14-base/roundtrip_{control,retention}.arrivalpoints.txt.gz`),
the binding `ce → ce` path's data section contains **exactly one EU node
before the BIU excursion**, and it is the same node on both configurations:

```
 …|u_eu|s1_bus[103]|combout        20.732
 …|u_biu|q_cnt~3|datae             21.003     <- the excursion begins
 …|u_biu|q_cnt~6|combout           22.076
 …|u_biu|q_ripe_lead_n~3|combout   22.509     <- and ends, 1.777 ns later
 …|u_eu|Mux358~11|datac            23.195
```

**`s1_bus[103]` is `bnd_fire`**, derived from the pack list at
`v30u_eu.sv:3852` by counting widths from the LSB
(`it_writes_tmpa` 0 · `it_fmask` 1–16 · `it_flags` 17–32 · `it_tmpa` 33–48 ·
`it_val` 49–64 · `s2_wbyte` 65 · `s2_val` 66–81 · `s1_wbyte` 82 · `s1_byte` 83 ·
`s1_val` 84–99 · `inta_first` 100 · `row_pre_wait` 101 · `q_bnd_pop` 102 ·
**`bnd_fire` 103**).  `bnd_fire` appears in the EU's act decode in exactly one
place — **`q_demand`**, `v30u_eu.sv:2205`
(`((st == S_OPC_POP) && !s1w_bnd_fire)` and the deferred-pop arm) — and
`assign q_pop = q_demand`.

> **THE ROUND TRIP THAT BINDS IS `EU bnd_fire → q_pop → q_cnt → q_ripe_lead_n →
> EU chain`.  `q_flush` IS NOT ON IT.**  The excursion itself is
> **3 LUT levels and 1.777 ns** (`span8`) / **1.506 ns** (`span9`) on
> CONTROL; the mean POP-A span is 2.149 (CONTROL) / 2.562 (RETENTION).
> ⚠ **AND THAT IS A CENSUS FIGURE, WHICH DOES NOT SIZE ANYTHING IN EITHER
> DIRECTION** — WAVE 14 measured the census 2.3× / 1.7× LOW on this very
> mechanism.  It is quoted here as ANATOMY, not as a prediction.

### 2.3 WHY THE PHASE SPLIT CANNOT CUT IT — AND WHY IT BINDS *BECAUSE* OF THE SPLIT

`q_pop` is computed in the EU's **stage 1** (it reads `st`, the register file
and `s1w_*`, all stage-1 quantities), and `q_ripe_lead_n` is consumed in the
EU's **stage 2**.  Stage 1's output is supposed to reach stage 2 only through
the `s1q` shadow register captured at `ce_half`.  **This one value escapes to
the BIU and comes back combinationally, bypassing the cut.**  That is exactly
why WAVE 14 found it on **200 of 200** binding paths of the split tree while
WAVE 10 found it on only 5 of 13 draws of the unsplit one: the split shortened
everything it could reach, and this is what it could not.

---

## §3 THE CANDIDATE ENUMERATION.  **NO CANDIDATE IS CHOSEN IN THIS DOCUMENT.**

Eight candidates, each with what it would do, what it costs, and the test that
would refute it.  ⚠ Several are listed **in order to be refuted**; a list that
contains only survivors is not an enumeration.

### C0 — **DO NOTHING; DECLARE NO LEGAL MECHANISM EXISTS**
The Q-8 outcome.  Legitimate, and it is a real result: it retires the last
named mechanism of this campaign.  It is the default if every other candidate
below fails equivalence or fails to recover ≥ 23.9 % (CONTROL) / 18.2 %
(RETENTION) of WAVE 14's ceiling.

### C1 — **PRE-COMPUTE BOTH ANSWERS; THE EU SELECTS WITH ITS OWN POP BIT**
The BIU publishes two levels, each a pure function of BIU registers (and
`q_flush`), neither depending on `q_pop`:
`q_ripe_lead_n0` = the level if the EU does not pop, `q_ripe_lead_n1` = the
level if it does.  The EU muxes locally with
`q_pop && q_ripe && !q_flush`, all three of which are either its own outputs or
a BIU **register** port it already has.
*Cost*: two ports instead of one; one duplicated 4-bit compare in the BIU; one
AND + one MUX in the EU.  **No flop.**
*Why it is legal*: §2.1's partition — the dependence on `q_pop` is ONE BIT
entering at ONE place.
*Refuted by*: any of §1.5's 181 goldens moving; or the identity
`published == original` failing on any simulated clock.

### C1′ — **THE SAME MUX, BUT LEFT IN THE BIU**
`assign q_ripe_lead_n = pop_eff ? lead1 : lead0;` with `lead0`/`lead1` pure
register functions.  Same logical depth reduction, **no new port**, and
`q_ripe_lead_n` keeps its name (so `r7_lint`'s declared-unresolved entry is
untouched).  But the value still leaves the EU and comes back, so **Q-3's
detector will still read `q_ripe_lead_n` on 200 of 200 paths** and the wave
could not distinguish a real win from a re-labelled one.

### C2 — **C1 PLUS: TAKE THE SELECT OFF THE `s1q` SHADOW**
`q_pop` is a stage-1 quantity, so it is constant from `ce_half` to `ce` (the
phase-split premise, which `v30u_eu.sv:4206` `$fatal`s on).  Adding the select
bit to `s1_bus`/`s1q` would make stage 2's read of it come off a **flop**, so
the `ce → ce` cone would contain **no** EU-stage-1 logic at all on this path —
the launch would move from the microcode ROM to a register.
*Cost*: **one flop** (`s1q` 778 → 779), a `phase_split_lint` membership entry,
and it is **split-dependent**: it is meaningless on a tree without the cut, and
the split does not currently land (WAVE 13 N-1 failed).
*Free falsifier*: the split's own premise assertion already checks it.

### C3 — **PUBLISH THE COUNT, NOT THE PREDICATE**
Export `poppable_n`/`q_cnt`/`grn_ttl` and let the EU do the whole comparison.
More wires, the same depth, and it moves BIU bookkeeping into the EU — the
opposite of the direction F31 and F7 established.  **Expected to be refuted on
simplicity grounds, not on correctness.**

### C4 — **RE-TIME: MAKE THE 1BL ARM READ THE *REGISTER* VIEW ONE CLOCK LATER**
Give `S_DECODE2`'s 1BL arm the `q_ripe` (NOW) view and add a state.
This is WAVE 14's `qripe_hold` with a compensating state, i.e. it changes WHEN
the strobe is taken.  **It adds a clock to the 1BL forms and the 181 goldens
say what that costs.**  Listed to be refuted: `charge(1)` is already the whole
budget of these forms.

### C5 — **HOIST THE DECREMENT TO THE END OF THE NEXT-STATE BLOCK**
Rather than publish two levels, restructure so `q_cnt`'s cone is pop-free until
one final decrementer, then publish from the pre-decrement value.  This is the
*implementation* C1 needs (§2.1's four compensation sites), not an alternative
to it; it is listed separately because it can also be done **without** the
second port, in which case it is C1′.

### C6 — **MOVE THE 1BL WAIT INTO THE BIU**
Let the BIU own the whole `wait_retire_lead` predicate including the strobe.
Refuted on the spec: the wait is the loader's, the flag write is the EU's, and
the BIU has no notion of `bl1_op`.  It would put a decode in the bus unit.

### C7 — **AN SDC EXCEPTION ON THE ARC**
**FORBIDDEN.  USER RULING 2026-09-08, verbatim: *"I don't want custom sdc
rules, period."***  Listed so that the enumeration is complete and so that the
ruling is visible in it.  **Not to be re-opened.**

---

## §4 WHAT THE NEXT COMMIT MUST DO

Choose from §3 **with a reason**, register the bars **Q-1 … Q-8**, and only
then touch `hdl/`.  ⚠ `git status --porcelain hdl/` carries **0 tracked
modifications** as this document is committed, and the choice commit will carry
0 as well.

Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
