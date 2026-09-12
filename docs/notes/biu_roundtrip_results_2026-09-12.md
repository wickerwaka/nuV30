# WAVE 10 — **THE CONTRADICTION IS A COIN.  THE ROUND TRIP IS WORTH 0.5 ns WHERE IT MATTERS AND 6.6 ns WHERE IT DOES NOT.**  RESULTS, SCORED AS REGISTERED.

Pre-registration `docs/notes/biu_roundtrip_prereg_2026-09-12.md`, committed at
`294839a428` **before the first Quartus stage**.
**MEASUREMENT ONLY.  NOTHING IS LANDED IN THE CORE.**  OFFLINE ONLY — no board,
no flash, no bitstream.  `git status --porcelain hdl/` carried **0 tracked
modifications** at the start and carries 0 at the end (**K-6**).

---

## §0 THE HEADLINE, IN FOUR SENTENCES

> **1. THE TWO INSTRUMENTS ASKED THE SAME QUESTION.**  Over every one of the
> **109,876 arrival points** in both waves' committed artifacts the two
> predicates select the **identical node set, 0 disagreements**.  They differ in
> POPULATION and in SPAN CONVENTION, and neither difference can turn 0.000 into
> 2.786.
>
> **2. THE CONTRADICTION IS A PLACEMENT LOTTERY, AND BOTH WAVES DREW HONESTLY.**
> On the UNCUT tree, one instrument over **13 draws** finds the round trip on
> the binding class **5 times** — CONTROL **4 of 10**, RETENTION **1 of 3**.
> WAVE 8 drew three CONTROLs and got three tails; WAVE 9 drew one CUT-tree
> CONTROL and got a head.  **On the CUT tree it is 6 of 6.**  P-1 and P-3 are
> both **MISSED, and the misses ARE the resolution.**
>
> **3. THE CENSUS OVERSTATED IT 5.3×, AND WAVE 8's RULE HELD ON A MECHANISM
> WAVE 8 NEVER TOUCHED.**  Measured by a 10-seed paired A/B against a
> BEHAVIOUR-BREAKING probe, the round trip is worth **+0.527 ns, 95 % CI
> [−0.185, +1.239]** on the arc of today's tree — against the census's
> **2.786 ns**.  WAVE 8 measured **5.9×** on `ucrom`; this is **5.3×**.
>
> **4. IT DOES NOT CLOSE THE GAP, AND THE REASON IS AMDAHL.**  Today's tree
> needs **−4.06 ns** and the round trip yields **0.53** — **not even the top of
> its confidence interval reaches a quarter of the gap.**  On WAVE 9's CUT tree
> the *same* edit is worth **+6.629 ns** of arc, because there the split had
> already shortened everything longer.  **THE MECHANISM DID NOT CHANGE VALUE;
> WHAT ELSE WAS ON THE ARC DID.**

---

## §1 K-1 — **THE POSITIVE CONTROLS.  REPORTED FIRST.  ALL PASS ON ALL 34 DRAWS.**

`sw/testdata/wave10/report.txt` carries the full table.  Every draw:

| control | what it demands | every draw |
|---|---|---|
| **PC-W1** RESOLVER | `-through` a `get_pins` collection returns ≥ 1 path; the same name as `get_nodes` returns 0 (WAVE 1 §0.2), demonstrated LIVE | `get_pins 1 → 1`, `get_nodes 1 → 0` on **34 of 34** |
| **PC-W2** MATCHER | forced through ONE NAMED `q_ripe_lead_n` / `q_cnt` pin the counter must find BIU nodes | **6 … 29** on 34 of 34 |
| **PC-W3** WRONG FORMS | the `v30u_biu:` TYPE prefix in the DATA SECTION, and an instance that does not exist, must read 0 | **0 / 0** on 34 of 34 |
| **PC-W4** BULK | the bulk `-through` printed and never relied on | fired as documented — see §1.2 |
| **PC-W5a/b** DESTINATION | a path forced to ONE named destination, and BOTH write-pin forms handled | PASS on 34 of 34 |
| **AX-1 / AX-2 live** | both predicates agree, and the data section equals all points, ON EVERY POPULATION OF EVERY DRAW | PASS on 34 of 34 |
| **PC-C2** | the multicycle deletion reached the compiler: core `SAME` class **k = 1.0000** | **34 of 34** |

### 1.1 ⚠⚠ **FOUR CONTROLS MISSED FIRST.  EVERY ONE WAS FIXED AS AN INSTRUMENT DEFECT AND NOT ONE BY WIDENING A BAR.**

This campaign's tally of instruments that produced confident wrong answers was
**eight**.  This wave adds four near-misses, all caught before any figure was
quoted, and each is a commit of its own:

1. **PC-W5, form 1** (`a054bfa935`) — it tried `|d`, `|asdata` and `|datain`,
   and the uncut tree's binding path ends at an **M10K PORT REGISTER**
   (`ram_block1a6~porta_address_reg7`) whose input pin is none of the three.
   K-1 named the `|d`/`|asdata` trap; the design had a third form.
2. **PC-W5, form 2** (`9a6266288b`) — it stopped guessing and asked the netlist
   for `<dest>|*`, **and got 0 pins: an M10K port register exposes no pin
   objects at all.**  A pin-based destination control cannot be the whole of
   this one, on any list.  Split into W5a (`get_registers`/`get_keepers`/node
   object, whichever answers, NAMED) and W5b (both write-pin forms, exercised on
   `upc_page` — the very register WAVE 9 §5.1 died on, which answered BOTH).
3. **PC-W3** (`5db3b26fd8`) — it gated on ALL POINTS and therefore **FAILED on
   this wave's own ceiling-probe arm**, whose entire content is that it ADDS a
   BIU register, and a REGISTER's name *does* carry the type prefix.  The clause
   is a DATA-SECTION clause and always was; the all-points count is now
   REPORTED, where a nonzero reading is a **free positive control that the arm
   reached the compiler.**
4. **PC-W5a** again (`80bbe99dc2`) — it failed on
   `...|u_eu|eff_op[2]~2_OTERM2473`, a physical-synthesis duplicate whose name
   `get_registers` will not match even with the brackets escaped.
   **A CONTROL THAT CAN ONLY ADDRESS THE REGISTERS WHOSE NAMES IT CAN SPELL IS A
   CONTROL THAT WILL FAIL ON THE NEXT NAME SHAPE.**  It now falls through to the
   NODE OBJECT, which needs no name, and prints which form answered.

### 1.2 **PC-W4 FIRED ON 14 OF 34 DRAWS AND THAT IS THE TRAP, CAUGHT LIVE**

On 14 draws the BULK `-through` of **1,157–1,223** `|u_biu|` pins returned a
path carrying **0** BIU nodes while the SINGLE-PIN form on the same netlist
returned **6–29**.  That is `get_timing_paths -through` **accepted and ignored**,
happening in front of the instrument, on the machine, this week.  It is printed
on every draw and **no figure in this wave rests on a bulk form.**

### 1.3 THE OFFLINE RECONCILIATION'S OWN CONTROLS

`sw/biu_predicate_reconcile.py`: **PC-R0** names and line-counts every artifact
it reads; **PC-R1** shows each predicate saying YES on the *other* wave's
artifact (8 / 8 / 2,400 / 2,400 points) with the known-wrong type-prefix form at
**0**; **PC-R2** a nonexistent instance reads **0**.  **ALL PASS.**

---

## §2 K-2 — **THE PREDICATE RECONCILIATION.  THE WAVE'S FIRST ANSWER.**

Run over both waves' **own committed artifacts**, no Quartus in the loop, so it
is a deterministic re-read of committed bytes.  **It compares CONTENT — counts
of lines in named files — and never a digest it computed itself.**

| axis | WAVE 8 asked | WAVE 9 asked | same question? |
|---|---|---|---|
| **AX-1** the MATCH | `'\|u_biu\|' in norm(name)` — type prefixes STRIPPED | `string first "\|u_biu\|"` on the RAW name | **YES** |
| **AX-2** the SECTION | the DATA section only (`state == 2`) | EVERY arrival point, clock network included | **YES on this design** |
| **AX-3** the POPULATION | `-npaths 400 -nworst 1` | `-npaths 200`, no diversity constraint | **NO** |
| **AX-4** the SPAN | `last.cum − (first.cum − first.incr)` | `last.total − first.total` | **NO** |

**AX-1, MEASURED**: over `27,777 + 30,682 + 26,166 + 25,172 + 79 = 109,876`
arrival points the two predicates disagree on **0**.  ⚠ That is an agreement on
these artifacts, not an identity of the tests — WAVE 8's would also match a BIU
*register*; no BIU register appears in the data section of a `ce → ce` path,
which is why the sets coincide.  (And it is exactly that latent difference that
made PC-W3 fire on the arm, §1.1 item 3.)

**AX-2, MEASURED**: 0 BIU points anywhere before the launch register.

**AX-3 IS A REAL DIFFERENCE OF QUESTION AND IS *NOT* THE RESOLUTION.**
WAVE 8's 400 paths are **400 distinct endpoint pairs**; WAVE 9's top-200 hold,
measured over this wave's own 34 draws, **5 to 37 distinct pairs, median 14**.  Those are different
questions — *"is it on an endpoint-diverse spread?"* against *"is it on the
binding class?"*.  **But the WORST PATH BELONGS TO BOTH POPULATIONS BY
CONSTRUCTION**, and on all three of WAVE 8's CONTROL draws it carries **0** BIU
nodes while WAVE 9's carries **8**.

**AX-4** is worth **+0.274 … +0.300 ns** (WAVE 8's convention is the larger).
It cannot turn 0.000 into 2.786.  It *is* a reason never to diff the two waves'
ns figures without naming the convention.

> ### **VERDICT: THE TWO INSTRUMENTS AGREE ABOUT WHAT TO LOOK FOR AND DISAGREED ABOUT WHAT THEY FOUND.  WHAT WAS LEFT WAS THREE CONFOUNDS IN THE DESIGN — TREE, CONFIGURATION, DRAW — AND §3 MEASURED ALL THREE WITH ONE INSTRUMENT.**

⚠ **AX-3 IS LIVE IN DEGREE EVEN WHERE IT IS NOT LIVE IN PRESENCE**, and this
wave measured a case: `uncut_control` seed 3 reads **POP-A 46.5 % against POP-B
4.8 %** — the round trip is on the worst cone and almost nowhere else.  On the
`cutarm` cell the two populations disagree the *other* way on every draw
(POP-A 0–28 %, POP-B 36–53 %).  **Quote the population with the number.**

---

## §3 K-3 — **ONE INSTRUMENT, SIX CELLS, 34 DRAWS.  THE ANSWER IS A COIN.**

No-exception configuration on every draw (`SAME` k = 1.0000, 34 of 34).
MAP ONCE PER CONFIGURATION, FIT ONCE PER SEED, clean db before every map.

### 3.1 PRESENCE — `k` = draws whose POP-A carries the round trip on ≥ 90 % of paths

| cell | tree | config | **k** | per-draw POP-A fraction |
|---|---|---|---|---|
| **U-C** | UNCUT (HEAD `de3fd2896a`) | CONTROL | **4 of 10** | 0 · 100 · **46** · 100 · 0 · 0 · 0 · 100 · 0 · 100 % |
| **U-R** | UNCUT | RETENTION | **1 of 3** | 0 · 0 · 100 % |
| **C-C** | CUT (`bacf7f9fd9`) | CONTROL | **3 of 3** | 100 · 100 · 100 % |
| **C-R** | CUT | RETENTION | **3 of 3** | 100 · 100 · 100 % |
| **ARM** `qripe_reg` | UNCUT + probe | CONTROL | **0 of 10** | 0 % ×10 |
| **CUTARM** | CUT + probe | CONTROL | **0 of 5** | 28 · 11 · 0 · 0 · 27 % |

### 3.2 THE BARS, SCORED

| bar | registered | measured | verdict |
|---|---|---|---|
| **P-1** WAVE 8 reproduces | `k(U-C) ≤ 1 of 5` | **4 of 10** (2 of the first 5) | ⚠ **MISSED** |
| **P-2** WAVE 9 reproduces | `k(C-C) ≥ 2 of 3` | **3 of 3** | **MET** |
| **P-3** the configuration axis | `k(U-R) ≥ 2 of 3` | **1 of 3** | ⚠ **MISSED** |
| **P-4** a split cell is a DRAW EFFECT and forbids attribution | — | **U-C and U-R BOTH SPLIT** | **FIRED** |
| **P-5** the populations compared within each draw | — | 0 draws disagree on PRESENCE; 1 disagrees sharply in DEGREE | **AX-3 harmless in presence, live in degree** |

> ### **P-1 AND P-3 ARE MISSED AND THE MISSES ARE THE FINDING.  ON THE UNCUT TREE THE ROUND TRIP'S PRESENCE ON THE BINDING CLASS IS A PLACEMENT OUTCOME — 5 OF 13 DRAWS — AND NEITHER WAVE 8's 0-OF-3 NOR WAVE 9's 1-OF-1 WAS EVER A PROPERTY OF A TREE.**
>
> **P-4 IS THEREFORE OBEYED: NO CONFIGURATION ATTRIBUTION IS MADE.**  WAVE 8's
> reading that its single RETENTION draw *might* be a configuration effect is
> **refuted** — retention splits too, and WAVE 5's all-or-nothing shape
> (2 of 4, pre-flattening) is the third independent sighting of the same coin.

**THE ONE ATTRIBUTION THAT SURVIVES IS A TREE EFFECT, AND IT IS THE OPPOSITE OF
A NUISANCE**: **6 of 6 on the CUT tree against 5 of 13 on the UNCUT one.**  The
phase split shortened everything it could reach, so the arc it could not reach
became the binding one on every draw — which is WAVE 9 §5.5's own sentence,
now measured over a population instead of one draw.

### 3.3 ⚠ **WAVE 9 REPRODUCES TO THE DIGIT.  WAVE 8 DOES NOT.  BOTH FACTS ARE RECORDED AND NEITHER IS EXPLAINED.**

`cut_control` seed 2, through a **different instrument and a different driver**,
reads **T_min 33.262 ns = 30.06 MHz, worst arc 31.959 ns, round trip 200/200,
mean span 2.786 ns** — WAVE 9 §5.3/§5.4's four headline numbers, every one of
them, to the thousandth.

**PC-C0**, a control nobody registered: `uncut_control` seed 1 draws
**T_min 35.867 ns / 27.88 MHz, `$v30u_ce` 1,918** where WAVE 8 drew **34.220 /
29.22 / 2,154** on the SAME SEED and a tree that is **byte-identical**
(`git diff 0267e48a2c HEAD -- hdl/` is EMPTY; no `.sv`, `.v`, `.qsf`, `.sdc`,
`.hex` or `.mif` changed anywhere in the repo).  This wave's pipeline is
**deterministic** — 35.867 came back on a dirty db, on a clean db, and again
from a **fresh map** three hours later, and the arm's seed 1 likewise reproduced
33.485 exactly — so the difference is not this wave's instability.
**RECORDED, NOT EXPLAINED.  `standing_gates.md` §A governs.**
Its practical consequence is stated and obeyed: **every comparison in §4 is
internal to this wave's own 34 draws**, and WAVE 8's absolute figures are quoted
only as history.

### 3.4 THE ARC AND THE BAND, PER CELL

| cell | n | worst arc ns, mean (min..max) | T_min mean | MHz mean | **worst-of-n** |
|---|---:|---|---:|---:|---:|
| **uncut CONTROL** | 10 | **34.486** (33.551..35.174) | 35.779 | 27.95 | **27.42** |
| uncut RETENTION | 3 | 34.234 (33.659..35.305) | 35.807 | 27.94 | 27.05 |
| cut CONTROL | 3 | 31.640 (31.023..31.959) | 32.846 | 30.45 | **30.06** |
| cut RETENTION | 3 | 30.131 (29.939..30.397) | 31.647 | 31.60 | **31.52** |
| **ARM `qripe_reg`** ⚠ | 10 | **33.959** (32.458..35.722) | 35.379 | 28.29 | 27.02 |
| **CUTARM** ⚠ | 5 | **25.249** (23.653..26.209) | 25.629 | 39.05 | **37.86** |

⚠ The last two rows are **BEHAVIOUR-BREAKING PROBES**.  See §4.

The measured span, where the round trip is present (POP-A mean, WAVE 9
convention): uncut CONTROL **2.229 ns** (1.769..3.046, n=5), uncut RETENTION
1.774, cut CONTROL **2.926** (2.285..3.706), cut RETENTION **2.892**.

---

## §4 K-4 / K-5 — **THE CEILING.  MEASURED, NOT ATTRIBUTED.**

### 4.1 ⚠⚠ **THE ARM IS BEHAVIOUR-BREAKING BY CONSTRUCTION AND NO EQUIVALENCE IS CLAIMED FOR IT**

**`qripe_reg`** registers `q_ripe_lead_n` inside `v30u_biu.sv`, severing
`q_cnt → poppable_n → q_ripe_lead_n → the EU chain`.  The EU is contracted (F7)
to read the BIU's NEXT level there; the arm hands it the PREVIOUS one.

* **IT IS NOT A DESIGN AND IS NOT PROPOSED AS ONE.**  A real mechanism is a
  later wave's problem.
* **IT IS NEVER LANDED.**  It lives in a scratch git worktree; the main tree's
  `hdl/` is never written.
* **IT WOULD ALSO BREAK `ss_lint`** — it adds a flop with no save-state address.
  Not run; recorded.

**K-4a, THE ANTI-EQUIVALENCE GATE — MET, AND REPORTED AS A FAILURE:**

| | REF | **ARM `qripe_reg`** |
|---|---|---|
| `check_core --core ucore --opcodes all --cases 0` | 169,000 / 169,000 | **168,819 / 169,000, exit 1** |

**181 cases fail.**  *A probe that still passes has not cut anything*, so this
is the evidence the path is really severed — and the STA agrees independently:
the arm carries the round trip on **0 of 10** draws where the reference carries
it on 4.

### 4.2 PC-C1 — **THE POSITIVE CONTROL, REPORTED BEFORE THE DELTA.  MET.**

The REF arm is the design itself.  Registered: its worst no-exception `ce → ce`
arc, meaned over its draws, must land within **±15 %** of WAVE 8 §3.1's
**32.969 ns**.

| | ns |
|---|---:|
| WAVE 8 §3.1, 4 draws | **32.969** |
| **this wave's REF**, 10 draws | **34.486** |
| difference | **+4.6 %** — inside ±15 %, **MET** |

### 4.3 **THE CEILING ON TODAY'S TREE — `+0.527 ns`, AND ITS INTERVAL INCLUDES ZERO**

Full design, both arms identically compiled, same driver, same SDC patch, same
instrument, clean db, map-once/fit-once, **10 seeds each, paired on the seed**.

| statistic | worst `ce → ce` ARC | whole-design T_min |
|---|---:|---:|
| paired mean over 10 seeds | **+0.527 ns** | +0.400 ns |
| sd | 0.995 | 1.112 |
| standard error | 0.315 | 0.351 |
| **95 % CI** | **[−0.185, +1.239]** | [−0.395, +1.195] |
| t | +1.68 | +1.14 |

per seed (ns): `s1 +2.120 · s2 +1.461 · s3 −0.262 · s4 +1.275 · s5 −0.759 ·
s6 −0.550 · s7 +1.107 · s8 +1.033 · s9 −0.385 · s10 +0.233`

> ### **THE SIZE IS `+0.527 ns` AND IT IS NOT DISTINGUISHABLE FROM ZERO AT n = 10.  THE CENSUS SAID `2.786`.  THAT IS A `5.3×` OVERSTATEMENT, AGAINST WAVE 8's MEASURED `5.9×` ON `ucrom` — A RULE THAT HAS NOW HELD TWICE, ON TWO UNRELATED MECHANISMS, IN TWO CONSECUTIVE WAVES.**
>
> **K-5 IS MET: the size carries its interval, and WAVE 8's 5.9 × is quoted
> beside it.**

**AND THE CONDITIONAL, WHICH IS THE FAIREST FORM OF THE QUESTION.**  Splitting
the 10 paired deltas by whether the round trip was on the REFERENCE's arc at
all:

| REF draws | n | mean Δ |
|---|---:|---:|
| **round trip ON the binding arc** | 4 | **+1.000 ns** |
| round trip NOT on it | 6 | +0.212 ns |

Even conditioned on being present, it is worth **1.000 ns against a census
figure of 2.786** — still **2.8× overstated**, and still a quarter of the gap.

### 4.4 ⚠ **BONUS, REPORTED SEPARATELY AS REQUIRED: THE CUT TREE, WHERE THE SAME EDIT IS WORTH 12× MORE**

| statistic | ARC | T_min |
|---|---:|---:|
| paired mean over 3 seeds (`cut_control` → `cutarm_control`) | **+6.629 ns** | **+7.464 ns** |
| sd / SE | 0.819 / 0.473 | 0.588 / 0.339 |
| 95 % CI | [+4.595, +8.663] | [+6.004, +8.924] |
| per seed | +7.370 · +5.750 · +6.767 | +8.017 · +6.847 · +7.528 |

`cutarm_control` measures **worst-of-5 = 37.86 MHz** (best draw 41.17), against
`cut_control`'s worst-of-3 **30.06**.

⚠⚠ **THIS IS TWO BEHAVIOUR-BREAKING CHANGES STACKED AND IT OVER-ANSWERS THE
QUESTION.**  WAVE 9's split ceiling was `max(STAGE 1 20.235, STAGE 2 27.922)` =
**27.922 ns**; the CUTARM arc is **25.249 ns**, *below* it.  The arm is
therefore not merely removing the round trip on that tree — **its new register
subdivides STAGE 2**, making a three-stage machine out of a two-stage one.
**`+6.629 ns` IS NOT THE ROUND TRIP'S SIZE.  IT IS THE SIZE OF "SEVER THE ROUND
TRIP *AND* ADD A THIRD PIPELINE STAGE INSIDE STAGE 2".**  It is quoted as a
BONUS and never as the ceiling.

### 4.5 **AND THE TWO NUMBERS TOGETHER ARE THE WAVE'S SECOND FINDING**

> **THE SAME ONE-LINE EDIT IS WORTH `0.527 ns` ON ONE TREE AND `6.629 ns` ON
> ANOTHER.  THE MECHANISM DID NOT CHANGE.  WHAT ELSE WAS ON THE ARC DID.**
>
> On the uncut tree the microcode-ROM loop binds and the round trip is on the
> arc 4 times in 10 — so removing it recovers almost nothing.  On the cut tree
> the split had already shortened everything longer, the round trip binds 6
> times in 6, and removing it recovers a great deal.  **A CANDIDATE'S VALUE IS
> NOT A PROPERTY OF THE CANDIDATE.**  That is Amdahl, it is the simplest
> possible reading, and it is what the standing design principle predicts: no
> exotic mechanism is needed to explain either number.

---

## §5 K-7 — **THE ENDGAME ARITHMETIC, WITH ITS NUMBERS**

The bar is **32.0 MHz**, i.e. **T_min ≤ 31.250 ns**, no exception.
The standing scoreboard for today's tree is WAVE 7's own no-exception
`worst-of-5`: **CONTROL 28.32 MHz (T_min 35.311 ns) / RETENTION 28.90 MHz
(34.602 ns)** — gaps **4.061 ns / 3.352 ns**.
*(This wave's own 10 CONTROL draws read worst-of-10 27.42 MHz / 36.466 ns.
They are consistent with each other and slower than WAVE 7's; §3.3 governs, and
the arithmetic below uses the STANDING figure, which is the friendlier one.)*

### 5.1 WHAT THE ROUND TRIP IS WORTH

**+0.527 ns**, 95 % CI **[−0.185, +1.239]**; **+1.000 ns** conditioned on it
being on the arc at all.  Census figure **2.786 ns**, overstated **5.3×**.

### 5.2 **DOES THE ROUND TRIP ALONE CLEAR 32.0 ON THE UNCUT TREE?  NO — IT COVERS AT MOST A THIRD OF THE GAP.**

| | CONTROL | RETENTION |
|---|---:|---:|
| standing T_min | 35.311 | 34.602 |
| − the measured ceiling **0.527** | **34.784 → 28.75 MHz** | **34.075 → 29.35 MHz** |
| − the TOP of the 95 % CI **1.239** | 34.072 → 29.35 MHz | 33.363 → 29.97 MHz |
| **remaining gap to 31.250 ns** | **3.53 ns** (2.82 at the CI top) | **2.83 ns** (2.11) |

**WAVE 9's estimate said "~31.5 MHz — short".  It was right that it is short,
and generous by about 2.7 MHz.**  Its own text called that figure *"a POINTER,
not a prediction"* and wrote the caveat that has now been measured:
**an ATTRIBUTED SHARE of an uncut arc is not a difference and does not
transfer.**

### 5.3 **DOES ROUND TRIP + THE PHASE SPLIT CLEAR IT?  ON THE MEASURED PROBE, YES — AND THE PROBE IS NOT A DESIGN.**

* WAVE 9's split ALONE: `worst-of-5` **CONTROL 30.06 / RETENTION 31.17** — RED,
  which is why J-11 fired and the split was reverted at `cbb556a097`.
  Reproduced here: cut CONTROL worst-of-3 **30.06**, cut RETENTION **31.52**.
* Split **+** the round-trip probe: `cutarm_control` **worst-of-5 37.86 MHz**,
  clearing 32.0 by **5.86 MHz**.
* ⚠ **BUT §4.4: the probe on that tree adds a THIRD pipeline stage inside
  STAGE 2, so it buys more than the round trip is.**  Taking instead WAVE 9's
  own two-stage ceiling `max(STAGE 1, STAGE 2) = 27.922 ns` of arc — the most a
  *two-stage* split can give once the third class is gone — and adding the
  cut tree's measured arc→T_min offset of **+1.205 ns** (mean of the three cut
  CONTROL draws) gives **T_min ≈ 29.13 ns = 34.33 MHz.**  **That clears 32.0.**
* ⚠ And subtracting only the honest ceiling from the cut tree's binding arc
  instead — `33.262 − 0.527 = 32.735 ns = 30.55 MHz` — **does NOT.**
  **The two readings disagree, and the disagreement is exactly the question of
  whether a REAL mechanism at that arc behaves like the probe or like the uncut
  measurement.  THIS WAVE DOES NOT SETTLE IT AND DOES NOT PRETEND TO.**

### 5.4 ⚠ **THE CUTTING PENALTY, CARRIED AS REQUIRED**

Any arithmetic involving a FUTURE cut must carry **~15.2 ns**: WAVE 4 measured
**+15.295** on a 43.485 ns arc and WAVE 9 **+15.188** on a 32.969 ns arc — the
same to **0.11 ns**, across a tree change that moved the arc by 10.5 ns.
**THE CUTTING PENALTY IS A CONSTANT OF THIS DESIGN, NOT A FRACTION OF THE ARC**,
so halving an arc of length *L* by a cut buys `L − (L/2 + 15.2)` only while
`L > 30.4 ns`.  **Today's uncut arc is 34.486 ns**, which leaves *L/2 + 15.2 =
32.44 ns* — **a cut of today's binding arc, taken alone, would still be over the
31.250 ns budget.**  The margin for this class of move is 2.0 ns wide and
shrinking as the arc shortens.

### 5.5 **THE SENTENCE THE WAVE OWES**

> **THE BIU ROUND TRIP IS NOT THE REMAINING GAP AND SHOULD NOT BE THE NEXT
> WAVE.**  It is worth **0.53 ns** on the tree that exists, its interval
> includes zero, and it is on the binding class only **5 draws in 13**.  The
> gap is **4.06 ns**.  What binds today's tree is the arc that launches inside
> the **microcode ROM** and lands in the **ROM's own address register** —
> **10 of 10 uncut CONTROL draws and 3 of 3 uncut RETENTION draws launch there
> and land there, and so do 6 of 6 on the cut tree** (5 of 6 landing in the ROM
> address register) — the loop WAVE 8 measured at `ucrom` **3.805 ns/path**
> and then showed recovers only **0.644** when built out.  **BOTH OF THIS
> CAMPAIGN'S LAST TWO CANDIDATES HAVE NOW BEEN SIZED AND BOTH CAME BACK ~5-6×
> SMALLER THAN THEIR CENSUS.  THE NEXT WAVE SHOULD SIZE BEFORE IT BUILDS, AND
> SHOULD EXPECT THE GAP TO NEED SEVERAL MECHANISMS RATHER THAN ONE.**

---

## §6 THE BARS, SCORED

| bar | verdict |
|---|---|
| **K-1** every classifier carries a positive control, reported first; a miss voids the wave | **MET.**  PC-W1..PC-W5, AX-1/AX-2 live and PC-C2 PASS on **34 of 34** draws; PC-R0..PC-R2 PASS offline.  **FOUR controls missed first and all four were fixed as instrument defects, none by widening a bar** (§1.1).  Every `-through` is ONE PIN; the bulk form is printed and **fired on 12 of 34 draws** (§1.2). |
| **K-2** the predicate reconciliation stated explicitly | **MET and it is the headline.**  §2 — same MATCH (0 disagreements over 109,876 points), same SECTION, different POPULATION and SPAN, and **the difference in question is not the resolution.** |
| **K-3** one instrument across both trees and both configurations, ≥ 3 draws each | **MET.**  6 cells, **34 draws**: U-C 10, U-R 3, C-C 3, C-R 3, ARM 10, CUTARM 5.  §3. |
| **K-4** the probe labelled BEHAVIOUR-BREAKING everywhere, no equivalence claimed, `check_core` reported FAILING | **MET.**  **168,819 / 169,000, exit 1.**  §4.1. |
| **K-5** the size carries its uncertainty and quotes WAVE 8's 5.9× beside it | **MET.**  `+0.527 ns`, 95 % CI `[−0.185, +1.239]`, census overstatement **5.3×** against WAVE 8's **5.9×**.  §4.3. |
| **K-6** `git status --porcelain hdl/` clean at start and end; probes in a scratch worktree; nothing landed | **MET.**  §8. |
| **K-7** the endgame arithmetic stated with its numbers | **MET.**  §5. |
| **P-1** | ⚠ **MISSED** — `k(U-C)` = 4 of 10.  **The miss is the resolution.** |
| **P-2** | **MET** — `k(C-C)` = 3 of 3, and seed 2 reproduces WAVE 9 to the thousandth. |
| **P-3** | ⚠ **MISSED** — `k(U-R)` = 1 of 3. |
| **P-4** | **FIRED on both uncut cells.  No configuration attribution is made.** |
| **P-5** | **MET** — 0 presence disagreements, 1 sharp DEGREE disagreement, reported. |
| **P-6** the ceiling is < 2.786 ns | **MET** — 0.527 ns. |
| **PC-C1** | **MET** — REF 34.486 vs WAVE 8's 32.969, **+4.6 %**, inside ±15 %. |
| **PC-C2** | **MET** — `SAME` k = 1.0000 on 34 of 34. |
| **PC-C0** | ⚠ **RECORDED, NOT EXPLAINED** — §3.3. |

---

## §7 WHAT IS OWED

1. ⚠⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND IS STILL OWED.**
   The chain flattening changed the EU's decode; **a fabric figure taken on
   FLASH #21 or earlier may not be quoted against this tree.**  Nothing was
   flashed by this wave and **it is not this wave's debt to discharge.**
2. **PC-C0 IS OPEN.**  A byte-identical tree at the same seed draws 1.65 ns
   slower here than in WAVE 8, with 236 fewer post-fit registers in the
   `v30u_*` collection, reproducibly.  It does not affect any conclusion above
   (every comparison is internal to this wave's 34 draws) but it means **WAVE 8's
   and this wave's absolute figures may not be diffed.**
3. **`qripe_tie`** — the second, more optimistic probe arm — is **implemented
   and NOT RUN**.  Booked, not taken.
4. **THE CUT-TREE CEILING IS NOT A CLEAN MEASUREMENT OF THIS MECHANISM** (§4.4)
   and §5.3's two readings disagree by ~4 MHz.  Settling it needs a probe on the
   cut tree that severs the round trip **without** subdividing STAGE 2.
5. **NOTHING IS LANDED.**  WAVE 9's split remains reverted; the standing tree is
   WAVE 7's.

---

## §8 DISCIPLINE, DECLARED

* **OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM.**
* **`git status --porcelain hdl/` carried 0 tracked modifications at the start
  of the wave and carries 0 at the end.**  Every driver run printed
  `hdl restored: CLEAN` for the main tree.  The two probe arms and the cut tree
  live in **scratch git worktrees** under `~/.cache/ucsimt-tmp/wave10/`;
  `--allow-arm-dirty` is itself **REFUSED outside that directory**.
* **NOTHING IS LANDED IN THE CORE.**  No file under `hdl/` is modified by any
  commit of this wave.
* Single-writer guard (`pgrep -x`, EXACT binary name) before every Quartus stage;
  `hdl/nec_test_ucore.qsf` `git checkout --`'d after every stage.
* `git add` BY EXPLICIT PATH ONLY; the ~18 pre-existing modified files in the
  working tree were not touched.
* `~/.cache/ucsimt-tmp/`, never `/tmp`.
* **CONTENT COMPARED, NOT A SELF-COMPUTED DIGEST**: every count in §2 is a count
  of lines in a named committed file, and every timing figure is quoted from the
  artifact that produced it, under `sw/testdata/wave10/`.
* No Codex.  No nested subagents.
* **No figure in this wave is a receipt, a gate or a design Fmax.**
  `standing_gates.md` §A governs; one green build is not closure.
