# WAVE 24 — RESULTS.  **THE SUITE DIVERGENCES ARE THREE INSTRUMENTS AND ONE REAL SILICON LAW — AND THE ONE REPAIR THE USER AUTHORISED IS BLOCKED BY A FOURTH.**

Pre-registration `6703bd93af`
(`docs/notes/suite_divergence_prereg_2026-09-20.md`), committed **before the
first `tests/` edit and before the first board probe**; the B-2 rig
`6cfd3d0cfd`, committed **before first board contact**.  Session
`https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

**`hdl/` WAS NOT EDITED.  NOTHING WAS FLASHED.  THE BOARD STILL CARRIES FLASH #23.**

---

## §1  THE HEADLINE

| what was asked | what was measured |
|---|---|
| **A-1** the seven `v0.2` cases | ⭐ **ALL SEVEN PASS.**  `INT.90` · `INT.9D` · `INT.FB` = **1000 / 1000 each, 3000 / 3000** |
| **A-2** the `v0.3` ledger's 62 | ⭐ **EXACTLY TWO FAILURES IN 170,000**, and they are the `F4bc` `VOID` pair.  `FF.3/7685`, the *"DEFINITIVE segment-offset-wrap"*, **PASSES** |
| **A-3** the `v20suite` eight | ⭐ **ONE MECHANISM, AND IT IS NOT THE ONE WAVE 22 OFFERED.**  WAVE 22's *V20-4-byte-queue vs V30-6-byte-queue* reading is **REFUTED**: the mechanism is `tb_v30_core.sv`'s own **16-cycle ghost-load re-latch**, proved by a directed control **20 / 20** and by a fingerprint that holds **8 of 8** |
| **B-1** re-capture the two `VOID` goldens | ⚠ **COLLISION PROVED, RE-CAPTURE TAKEN, AND THE REPLACEMENT REFUSED.**  The emitter and the scorer are in different image eras (§5); the suite was **RESTORED BYTE-IDENTICAL** and the exemptions stay.  **REGISTERED MISS** |
| **B-2** the ModR/M retained-EA lane | ⭐ **CAPTURED FROM SILICON WITH CONSTRUCTED BYTES, 13 / 13.**  The controls reproduce the 2026-07-27 rows EXACTLY.  **A REAL DIVERGENCE, 6 of 13 — and WAVE 23's own reading of it is REFINED BY ITS OWN FALSIFIER** |
| **B-3** `mod3_illegal` | route costed, **NOT TAKEN** (§7) |
| ladder | **31 legs SAME, 0 MOVED, 0 NEW** — §8 |

**FOUR OF THE FIVE "KNOWN DIVERGENCES" ARE INSTRUMENTS.  THE ONE THAT IS NOT IS
NEW, AND IT IS THE ONE NOBODY HAD ASKED FOR.**

---

## §2  THE DATE CHECK (bar Y-2) — **EVERY SUITE DOCUMENT PREDATES THE ENGINE, NOT MERELY THE ARCHIVE**

`hdl/rtl/ucore/` first appears at **`0bfea2bfd0`, 2026-08-03**.

| document | dated | vs the ucore's first commit | verdict | the measurement that settles it |
|---|---|---|---|---|
| `v02_suspected_divergences.md` | **2026-07-18** | **−16 days** | **FSM-ERA** | 3000 / 3000 — §3 |
| `v03_divergence_ledger.md` | **2026-07-19 … 07-23** | **−11 days** | **FSM-ERA** | 169,998 / 170,000 — §4 |
| `v0.3/known_divergences.json` | **2026-07-25** | **−9 days** | **FSM-ERA** (ledger §D, 2026-09-19) | the two `VOID` claims re-derived, §5 |
| `mod3_illegal/metadata.json` | **2026-07-27** | **−7 days** | **FSM-ERA** (WAVE 23 D-1) | its `stale_ea_probe` re-taken from silicon, §6 |
| `tests/v30/v20suite/` | upstream **2024-05-25** | **a DIFFERENT PART** (µPD70108 V20) | not an engine claim at all | §4b |

**BOTH IN-REPO DOCUMENTS ARE NOW MARKED IN PLACE AND NEITHER IS DELETED** — a
quoted WAVE 24 header at the top of each, carrying the date arithmetic and the
measurement.

---

## §3  A-1 — THE SEVEN `v0.2` CASES, BY NAME.  **P-A1 MET.**

```
python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.2 \
                         --opcodes INT.90,INT.9D,INT.FB --cases 0
INT.90: 1000/1000 full   INT.9D: 1000/1000 full   INT.FB: 1000/1000 full
TOTAL: 3000/3000 full (cycles 3000, arch 3000)
```

`sw/testdata/wave24/a1_v02.log`.  The seven — `INT.90/239`, `INT.9D/44`,
`INT.9D/62`, `INT.9D/954`, `INT.FB/142`, `INT.FB/368`, `INT.FB/730` — are
contained by construction: **a form that scores 1000 / 1000 has no failing
index in it.**

**AND THE DOCUMENT ALREADY SAID WHY, IN ITS OWN LAST SECTION.**  The seven are
the `final.flags` **store-stub capture convention**, closed under task #21 by
re-deriving 269 `v0.2` pin-event goldens host-side.  **The SUITE was edited, not
the RTL.**  What was never done is the thing this wave did: **check whether the
escalation was still live against the engine that exists.**  It is not.

---

## §4  A-2 — THE `v0.3` LEDGER.  **P-A2 MET, EXACTLY.**

Nine forms carrying the ledger's 62 cases, plus the whole Family-5/7
string-I/O prefetch-ordering intake (~44,935 cases) the ledger calls *"the
primary BIU-ordering intake"* — **exemptions OFF**:

```
python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.3 \
  --opcodes 0F31,0F26,0F22,0F20,HLT.RES,IE0.90,0F1B,83.5,FF.3,\
            6E,6F,36.6E,26.6E,2E.6F,646F,6C,6D --cases 0 --no-known-divergences
TOTAL: 169998/170000 full (cycles 169998, arch 169998)
```

| ledger family | forms | cases claimed | **measured on the ucore** |
|---|---|---:|---|
| F1 `0F31` INS, *"cyc-only, offset=0 ∧ width=15, exact 25/25"* | 1 | 25 | **10,000 / 10,000 — 0 failures** |
| F2 BCD-4S, *"V30-specific Z/P, RTL implements the V20 result"* | 3 | 24 | **30,000 / 30,000 — 0 failures** |
| F3 pin-event, *"CAPTURE ARTIFACT"* | 2 | 10 | **20,000 / 20,000 — 0 failures** |
| F4a `FF.3/7685`, *"DEFINITIVE segment-offset-wrap"* | 1 | 1 | **10,000 / 10,000 — 0 failures** |
| F4bc `0F1B/3917`, `83.5/8683`, **VOID** | 2 | 2 | **2 failures — the ONLY ones** |
| Family 5 / 5a / 7, the string-I/O ordering intake | 8 | ~44,935 | **80,000 / 80,000 — 0 failures** |

**THE ENTIRE 2026-07 INTAKE IS CLOSED IN THIS ENGINE EXCEPT THE TWO CASES THAT
WERE NEVER THE ENGINE'S.**  `sw/testdata/wave24/a2_v03_ledger.log`.

### §4b  A-3 — THE `v20suite` EIGHT.  **WAVE 22's HYPOTHESIS IS REFUTED, AND THE REPLACEMENT IS ONE LINE OF TESTBENCH.**

WAVE 22 offered, labelled UNPROVEN: *the V20's 4-byte prefetch queue against the
V30's 6-byte one … `--arch-only` masks the queue but not the architectural
consequence of a different prefetch depth.*

> **H-W, REGISTERED BEFORE THE CONTROL WAS RUN**: *the scored window's register
> sample is not frozen at the closing F pop.*  `hdl/tb/tb_v30_core.sv:477`
> latches `fin_regs` at the close; **`:483-491` then keeps a 16-CPU-cycle
> `fin_wait` window in which, if a load is pending, the WHOLE register file
> except the retired IP is RE-LATCHED later** — on the comment's own words,
> *"the following NOPs keep retiring"*.  The V20 goldens are external captures
> that put **non-`0x90` bytes immediately after the instruction under test**;
> this repo's own emitted suites cannot, because
> `emit_suite._operand_abuts_code` (margin 8) rejects such placements.

**THE DIRECTED CONTROL — form `03`, 20 PASSING cases, `FF CC` = `DEC SP`
written at the retirement point** (`sw/testdata/wave24/a3/`):

| variant | injection | **ARCH** | |
|---|---|---|---|
| `base` | none | **20 / 20** | the slice is clean |
| **`inj0`** | `FF CC` at `end+0` | **0 / 20** | ⭐ **ALL 20, each with `sp == exp − 1`** — the registered bar was ≥ 16 / 20 |
| **`inj2`** | `FF CC` at `end+2` | **0 / 20** | two NOPs then `DEC SP` still reaches |
| `inj4` … `inj16` | `FF CC` at `end+4 … +16` | **20 / 20 each** | out of reach |
| `far64` | `FF CC` at `end+64` | **20 / 20** | the REAL negative control — the effect is LOCAL |
| `null90` | `90 90` at `end+0` | 20 / 20 | ⚠ **VACUOUS BY CONSTRUCTION AND SAID SO** — the TB already fills with `0x90`, so the registered C-NULL writes nothing.  `far64` replaces it and the replacement is declared, not quietly substituted |

**AND THE FINGERPRINT IS THE MECHANISM'S OWN.**  `:489-490` re-latches
`fin_regs[191:0]` and `fin_regs[223:208]` — **every architectural register
EXCEPT index 12, which `check_core.REGS[12]` says is `ip`.**  Every one of the
20 injected failures moved **`sp` AND `flags` AND NOT `ip`**.  And the eight
real failures:

```
03 sp,flags | 0F1D bx,flags | 29 sp,bp | 62 dx | 85 cx,flags | 86 dx | E8 sp | E9 sp
```

**NOT ONE `ip`.  EIGHT OF EIGHT.**

**THE CENSUS — ONE PREDICATE, NO PER-CASE RULE** (`a3_census2.py`): *the case's
CONTINUATION point (`final.cs:final.ip`, which is the branch target or the trap
handler where there is one) has a recorded non-`0x90` byte within 4 bytes.*
**2,284 of 3,125,000 — and ALL EIGHT failures are inside it.**  The predicate
is NECESSARY and not sufficient, and the directed control says exactly why:
the injected instruction must also land inside the re-latch's reach, which the
distance sweep measures at **`+2` yes, `+4` no**.

**WHAT EACH OF THE EIGHT ACTUALLY EXECUTED** — read off the case's own bytes,
no engine:

| case | bytes at the continuation | the extra instruction | the divergence |
|---|---|---|---|
| `03`/2019 | `FF CC` at `end+0` | **`DEC SP`** | `sp` 0ccf→0cce, flags |
| `85`/4717 | `41` at `end+3` | **`INC CX`** | `cx` e893→e894, flags |
| `62`/1229 | `B6 43` at the **BOUND trap handler** `2465:9FFA` | **`MOV DH,43h`** | `dx` |
| `E8`/216, `E9`/7762 | `FE FF` — the branch targets **its own encoding** | — | `sp` |
| `29`/9262, `0F1D`/4712, `86`/9919 | the instruction's own **write or operand lands in its prefetch shadow** | — | `sp,bp` / `bx,flags` / `dx` |

> **ONE MECHANISM, AND IT IS THE INSTRUMENT.**  It is not a part difference: the
> control reproduces the entire signature on a `add ax, bx` case with no memory
> operand and no queue-depth question anywhere in it.  **The V20-vs-V30 prefetch
> depth is not needed to explain any of the eight, and a hypothesis that is not
> needed is not evidence.**

**THE DISPOSITION IS PROPOSED AND NOT TAKEN**, as the brief requires.  The
eight stay in the numerator and denominator; **`3,124,992 / 3,125,000 ARCH` is
the quotable figure**.  The two routes, for a later wave to choose between:
**(a)** re-latch only the fields a ghost load can write instead of all thirteen
(an `hdl/` edit — frozen here), or **(b)** exclude the eight as
instrument-failure, the same class as `v0.3`'s `VOID` pair.  **(a) is the one
that fixes something**; (b) only stops counting it.

---

## §5  B-1 — THE COLLISION IS REAL, THE RE-CAPTURE WAS TAKEN, AND THE REPLACEMENT WAS REFUSED

**THE COLLISION, FROM THE BANKED CASE ALONE, NO ENGINE**
(`sw/testdata/wave24/b1_collision_proof.py`, exit 0):

```
0F1B/3917  code phys dc33   preload span dc2f..dc32 = 63 c0 63 c0
           operand EA = DS*16+BW+IY = dc30  want 89 -> image holds c0  COLLIDES
                                     dc31  want 11 -> image holds 63  COLLIDES
83.5/8683  code phys 979b   preload span 9797..979a = 63 c0 63 c0
           operand EA = DS*16+BW    = 9799  want a7 -> image holds 63  COLLIDES
                                     979a  want a4 -> image holds c0  COLLIDES
```

**P-B1a MET, BYTE FOR BYTE** against `v03_divergence_ledger.md` F4bc
(`dc30 / 89 / C0`, `9799 / A7 / 63`) and against WAVE 22's measured
`exp 0x63C0` rows.  **The `VOID` claim now has three independent derivations
and the exemptions are earned.**

**THEN THE RE-CAPTURE WAS TAKEN FROM SILICON — AND BOTH REPLACEMENTS CAME BACK
`neither`**, the emitter's own flat-validity verdict for *neither a flat nor a
64K-mirrored replay reproduces this golden*.  **The control says that is not
about these two cases**: five of seven ARBITRARY `v0.3` indices re-captured
today are `neither` too, while **18 of 18 BANKED cases replay `flat`**.

> **THE EMITTER AND THE BATCH SCORER ARE IN DIFFERENT IMAGE ERAS.**  The
> fuzz-v2 composer fills with **`0xCC`** (`testimage.CODE_FILL`); the batch
> testbench fills with **`8'h90`**, an unconditional literal at
> `tb_v30_core.sv:1072`.  The failing rows' diverging column **is the fill
> word** — `0x9090` in the 2026-07 goldens, `0xCCCC` in one captured today.

> ⭐ **AND B-2 CORROBORATES IT FROM A COMPLETELY DIFFERENT INSTRUMENT.**  The
> frozen 2026-07-27 silicon row `MOV CW,[4455h]` reads **`0xD4E5 = 0x4455 +
> 0x9090`**; the SAME instruction, captured from the socket today, reads
> **`0x1121 = 0x4455 + 0xCCCC`** (§6.1).  *One term changed, and it is the
> image fill byte, measured on silicon, with the law holding either side of it.*
> **Two instruments, one fact: the composer's fill went `0x90` → `0xCC` and the
> testbench's did not.**

**THE SUITE WAS RESTORED BYTE-IDENTICAL** (`7e1f444cb318…` / `8e7824acc4e3…`,
before and after) and **the two exemptions stay**.  Shipping the replacements
would have traded a documented, thrice-derived golden defect for an
undocumented instrument failure and moved `v0.3`'s published figure on a
capture the scorer cannot read.  **P-B1b and P-B1c are REGISTERED MISSES and are
reported as registered**: `v0.3` stays **3,699,998 / 3,699,998 [2 excluded]**,
not the predicted 3,700,000 / 3,700,000.

**NOTHING WAS DESTROYED.**  Originals archived byte-identical
(`sw/testdata/wave24/void-archive/*.orig`, `SHA256-BEFORE.txt`,
`SHA256-AFTER-RESTORE.txt`, `original-cases.json`); **the two re-captures are
true silicon and are RETAINED** with their full per-clock rows, divider readback
and truth stamp at `recaptured-2026-09-20.json`.  Full entry:
`invalidation_ledger.md` **§E**, filed explicitly as **none of the five
registers** with its reasons.

---

## §6  B-2 — THE ModR/M RETAINED-EA LANE.  **THIRTEEN CONSTRUCTED PROBES, AND WAVE 23's FALSIFIER FIRED.**

⚠ **DECLARED AS A COORDINATOR EXTENSION OF THE AUTHORISED BOARD SESSION**, and
it exists because WAVE 23 §4.1 could not close the divergence it found: the two
silicon rows' bytes were **inferred from a prose field**, and the committed
`sw/char_mod3.py`'s own probe list **does not contain those rows** (the freeze's
`rig` says *"char_mod3.py **+ inline freeze**"*).  **The bytes are not
recoverable from any artifact.**

Every probe is `<predecessor> 8D F7` — `LEA SI, DI` at `mod == 3` — body at
`PS=0x0000 PC=0x8100`, `char_mod3.SETUPS[0]` registers, `AW = 0x1111`.  Socket
capture `sw/b2_ea_lane.py` (13/13, divider readback **`div=8 (4 MHz), commanded
by this connection`**); ucore leg `sw/b2_ea_lane_ucore.py`, whole-program replay
from RESET with **no backdoor injection**, through WAVE 23's own `Runner`.

```
tag  predecessor bytes prose                  EA   pred  SILICON   ucore  verdict
C1   a3 34 12       MOV [1234h],AW       1234   1234     1234    1234  MATCH
C2   a3 ef be       MOV [BEEFh],AW       beef   beef     beef    beef  MATCH
C3   90             NOP (no EA)             -      -     2222    2222  MATCH
R1   88 26 10 30    MOV [3010h],AH       3010   4121     4121    9211  DIVERGE
R2   8b 0e 55 44    MOV CW,[4455h]       4455      -     1121    4dcc  DIVERGE
M0   89 00          MOV [BW+IX],AW       bbbb   cccc     8888    8888  MATCH
M1   89 01          MOV [BW+IY],AW       cccc   dddd     9999    9999  MATCH
M2   89 02          MOV [BP+IX],AW       dddd   eeee     8888    8888  MATCH
M3   89 03          MOV [BP+IY],AW       eeee   ffff     9999    9999  MATCH
M4   89 04          MOV [IX],AW          7777   8888     1111    9211  DIVERGE
M5   89 05          MOV [IY],AW          8888   9999     1111    9211  DIVERGE
M6   89 06 34 12    MOV [1234h],AW       1234   2345     2345    9211  DIVERGE
M7   89 07          MOV [BW],AW          4444   5555     1111    9211  DIVERGE

MATCH 7 / 13   DIVERGE 6 / 13
```

### §6.1  **P-B2a MET — THE CONTROLS REPRODUCE THE 2026-07-27 SILICON EXACTLY**

`C1 = 0x1234` and `C2 = 0xBEEF`, the frozen `stale_ea_probe`'s two `match: true`
rows, **to the bit**.  And **`R1 = 0x4121` reproduces the frozen `si_loaded`
`16673` exactly** — so **WAVE 23's INFERRED encoding `88 26 10 30` for
*"MOV[3010h],AH"* was CORRECT**, and that is now established by construction
rather than by reading English.

**`R2` REPRODUCES TOO, AND ITS ARITHMETIC IS THE PROOF THAT THE OLD ROW WAS
READ RIGHT.**  The frozen row is `0xD4E5 = 0x4455 + 0x9090`, where `0x9090` was
the v1 composer's NOP fill.  Today's composer fills with `0xCC`, and silicon
gives **`0x1121 = 0x4455 + 0xCCCC`**.  *Same law, same instruction, the one term
that changed is the one the image changed.*

### §6.2  ⚠ **P-B2b MISSED — AND THE MISS IS THE RESULT**

Registered: *the retained EA lane holds the **completed** effective address*, so
`M0 CCCC · M1 DDDD · M2 EEEE · M3 FFFF · M4 8888 · M5 9999 · M6 2345 · M7 5555`.
**Measured: `8888 · 9999 · 8888 · 9999 · 1111 · 1111 · 2345 · 1111`.  One of
eight.**

> **WHAT SILICON ACTUALLY RETAINS, IN ONE SENTENCE:** *the lane holds the
> address adder's **SECOND addend** on the last EA calculation — the index
> register for a two-register form, the displacement for a displacement form,
> and **ZERO** when there is nothing to add.*

Checked term by term against `AW = 0x1111`:

| form | EA | second addend | + scratch | **silicon** |
|---|---|---|---|---|
| `89 00` `[BW+IX]` | `BBBB` | `IX` = `7777` | `8888` | **`8888`** |
| `89 01` `[BW+IY]` | `CCCC` | `IY` = `8888` | `9999` | **`9999`** |
| `89 02` `[BP+IX]` | `DDDD` | `IX` | `8888` | **`8888`** |
| `89 03` `[BP+IY]` | `EEEE` | `IY` | `9999` | **`9999`** |
| `89 04` `[IX]` | `7777` | **none → 0** | `1111` | **`1111`** |
| `89 05` `[IY]` | `8888` | **none → 0** | `1111` | **`1111`** |
| `89 07` `[BW]` | `4444` | **none → 0** | `1111` | **`1111`** |
| `89 06` `[1234h]` | `1234` | `disp` = `1234` | `2345` | **`2345`** |

**THEREFORE WAVE 23's REGISTERED FALSIFIER FIRED, IN THE USEFUL DIRECTION.**  It
asked for *"a directed socket capture … in which the register does not receive
`EA + scratch`"*.  **Silicon does not receive `EA + scratch` on three of the
eight `mod=00` forms.**  WAVE 23's two-point reading — *"silicon's lane holds
the effective address"* — was true of both witnesses it had **because both were
displacement-only forms, where the last addend IS the address**.  It is
withdrawn as a general law and replaced by the sentence above, which is right on
all thirteen rows.

### §6.3  ⚠ **AND THE ucore IS RIGHT ON HALF OF IT** — which is what makes the defect one predicate

The ucore agrees with silicon on **every two-register form** (`M0`–`M3`) and
disagrees on **every single-addend form** (`M4`, `M5`, `M7`, `M6`, `R1`, `R2`),
where it keeps a **stale** value — `0x8100`, the loader's own `PC`
(`0x9211 = 0x8100 + 0x1111`; `0x4dcc = 0x8100 + 0xCCCC`).  **The scratch term
agrees on every row, so the attribution is clean: the only thing that differs is
the retained lane.**

> **THE DEFECT IS ONE QUALIFIER.**  `v30u_eu.sv:251`'s `ea_residue` is written
> under `ea_pair_valid` — *when there is a pair*.  Silicon writes it on **every**
> EA calculation, with zero when there is no second addend.  **That is one
> predicate, not a table, and it is exactly what the simplicity principle
> predicts of 80s silicon: the rail is loaded because it is always loaded.**

⚠ **`hdl/` WAS NOT EDITED AND THIS IS BOOKED, NOT FIXED.**  **FALSIFIER,
REGISTERED FOR THE LANDING WAVE**: after the change, re-run
`sw/b2_ea_lane_ucore.py` — all thirteen rows must read MATCH, **and the four
that already MATCH (`M0`–`M3`) must not move**; and `sw/lea_mod3_gate.py` must
stay PASS with `mod3_illegal` unmoved at `0/128`, since those 128 have no
ModR/M predecessor at all.

⚠ **AND ONE THING THIS WAVE DID NOT PROBE**: `mod=01`/`mod=10` forms, where a
base+index **and** a displacement are both present.  The sentence above predicts
the **displacement** (the last addend).  **Not measured, and not claimed.**

---

## §7  B-3 — `mod3_illegal`: THE ROUTE, COSTED AND NOT TAKEN

WAVE 23 established that the 128 are **unscoreable by an injected engine by
construction** — the outcome depends on pre-window `ea_residue` (`0x0500`
= `PC + PS`, left by the capture harness's own terminal `BR PS:PC`), and
`tb_v30_core.sv:1120` injects fourteen architectural registers and nothing else.
Injecting the value is **STOP S-4** and remains forbidden.

**WHAT A RE-CAPTURE WITH A DECLARED PREDECESSOR WOULD COST**

* **Board**: 128 socket captures ≈ **2 minutes**, plus the same again for a
  second register setup.  Trivial.
* **Emitter**: the probe body becomes `<declared predecessor> <8D modrm>`, which
  is `sw/b2_ea_lane.py`'s shape — and B-2 has already paid the one real cost:
  `emit_case`'s cycle window is **one instruction wide**, so `next_ip` must name
  the predecessor's end and **the golden's cycle rows then cover the predecessor,
  not the LEA**.  A 128-case tranche captured that way is an **architectural**
  tranche only.
* **The real cost — `tests/v30/mod3_illegal/` is a FROZEN artifact under WAVE
  22's committed sha256 manifest `67161a0c409c7fc6…`**, and replacing its
  goldens invalidates that manifest and every figure keyed to it, WAVE 23's
  `lea_mod3_gate` L1/L4 legs included (they read their expected values **out of
  `metadata.json`**).

**WHAT IT WOULD BUY**

* `mod3_illegal` becomes **scoreable**: with a declared predecessor the residue
  is a function of the case's own recorded stimulus, so `0 / 128` becomes a real
  number instead of a structural one.
* It would cover the gap §6.3 names — `mod=01`/`mod=10` — on the same run.

**WHAT IT WOULD NOT BUY**: **nothing about the ucore's correctness that §6 has
not already settled more cheaply.**  §6's thirteen rows isolate the mechanism to
one qualifier with silicon on both sides of it; 128 more rows of the *same*
predecessor-free stimulus would add cases, not information.

> **RECOMMENDATION, NOT A DECISION: do it as part of the RTL landing wave that
> fixes §6.3, as that landing's silicon bar — not before.**  Re-capturing a
> frozen artifact to make a number look better, with no mechanism waiting on it,
> is how a gate loses its meaning.

---

## §8  THE LADDER

**Every leg below was RUN on this tree in this wave.  `RC` is the process exit
code, captured with `${PIPESTATUS[0]}`, never `tail`'s.**  Raw logs by value at
`sw/testdata/wave24/ladder/`.

| leg | command | registered | **measured** | |
|---|---|---|---|---|
| `check_core` | `--core ucore --opcodes all --cases 0 --ce-div 4` | 169,000 | **169,000 / 169,000 full** | SAME |
| `check_core` | `… --ce-div 2` | 169,000 | **169,000 / 169,000 full** | SAME |
| `check_core` | `… --ce-div 3` | 169,000 | **169,000 / 169,000 full** | SAME |
| `check_core` | `… --ce-div 8` | 169,000 | **169,000 / 169,000 full** | SAME |
| `check_core` | `… --ce-div 1` | **REFUSED** | **exit 2**, clause **C-a** cited by name | SAME |
| HLT sweep `s10-w0` | `--waits 0` | 97 | **97 / 97** | SAME |
| HLT sweep `s10-w1` | `--waits 1` | 93 | **93 / 95**, the survivor at `(10, 'busstat')` | SAME |
| HLT sweep `s13-w2` | `--waits 2` | 45 | **45 / 46**, `(12, 'busstat')` | SAME |
| HLT sweep `s13-w3` | `--waits 3` | 44 | **44 / 45**, `(14, 'busstat')` | SAME |
| *the four sweeps* | | **279 / 283** | **279 / 283** | SAME |
| `v0.2` | `--suite-dir tests/v30/v0.2 --opcodes all --cases 0` | 347,000 | **347,000 / 347,000 full** | SAME |
| **`v0.3`** | `--suite-dir tests/v30/v0.3 --opcodes all --cases 0` | 3,699,998 [2 excluded] | **3,699,998 / 3,699,998 full  [2 documented pre-existing excluded]** | ⚠ **SAME — and the REGISTERED 3,700,000 / 3,700,000 IS A MISS (§5)** |
| `v20suite` | `… --arch-only` | 3,124,992 / 3,125,000 | **3,124,992 / 3,125,000 ARCH**, the SAME eight forms, one case each | SAME |
| `ss_lint --core ucore` | | 232 / 229 flops / 4 whitelist / 0 UNMAPPED | **PASS — 232 (109×2 BIU + 122×2 EU + tag); 229 flops; 4 whitelisted; 0 UNMAPPED** | SAME |
| `cutset_lint` | | 81 / 0 | **PASS (81 members / 0 violations)** | SAME |
| `phase_split_lint` | | 157 / 779 / 0 | **PASS (157 members / 779 bits / 0 violations)** | SAME |
| `r7_lint` | | PASS | **PASS — 0 undeclared carriers, 0 undeclared unresolved, 41 `stop` sites, 0 violations** | SAME |
| `qsf_lint --check` | | CANONICAL | **CANONICAL** (0 materialised assignments, one file list, one output directory) | SAME |
| `core_portlist_lint` | | 4 configurations | **PASS — 4 configuration(s)** | SAME |
| `test_quartus_gate` | | 302 / 302 | **302 / 302, PASS** | SAME |
| `test_artifact` | | 45 / 45 | **45 / 45, NON-VACUOUS** | SAME |
| `lea_mod3_gate` | | PASS | **PASS — L1 2/2 · L2 64/64 · L3 3/3 · L4 2 of 2 KNOWN-RED**, 71 replays | SAME |
| `chainflat_relocation_check` | | 9 / 9 | **PASS — 9 arms, one copy each, byte-identical to `aba01feb07`, reconstruction exact** | SAME |
| `chain_lfsr_gate` | | four signatures byte-identical | **PASS** — CHAIN_MAX 7, observed depth [6], 0 overflows, 4 seeds × 400,000 clocks | SAME |
| `demux_off_gate` | | PASS | **PASS — 3 legs** | SAME |
| `check_boot` | `220` | MATCH | **MATCHES over 220 rows from RESET release** | SAME |
| `check_boot` | `400` | MATCH | **MATCHES over 400 rows** | SAME |
| `check_ab_sim` | `--core ucore` | 187 | **AB SIM MATCHES CHIP BOOT over 187 rows** | SAME |
| `ghost_launch_law` | `score` | 200 / 200 | **ALL THREE POPULATIONS: 200/200 = 100.0 %** | SAME |
| `check_ucore_tables` (G0) | | 9,988 | **PASS — 1028 rows + 8192 micro-addresses + 768 PLA entries = 9,988 byte-identical on both legs** | SAME |
| `pla3_check` | | 21 checks | **OK (21 checks passed)** | SAME |
| `ucrom_mif_check` | | PASS | **PASS — every emitted table matches its `.hex` word for word** | SAME |

**31 LEGS SAME · 0 MOVED · 0 NEW.**  Architectural cases re-scored this wave:
**169,000 × 4 + 347,000 + 3,699,998 + 3,125,000 + 283 = 7,848,281**, plus the
**170,000** of §4, the **80,000** of §4b's eight forms and the **3,000** of §3.

> ⭐ **AND THE `v0.3` LEG IS BYTE-IDENTICAL TO THE RUN THAT REGISTERED IT.**
> This wave's 355-form log has sha256 **`644a11c5e09f38ed…`** — **the same
> file, byte for byte**, as `sw/testdata/edge-removal/v03_confirm.log`, the
> confirming run `invalidation_ledger.md` §D.1 recorded earlier the same day.
> **That is also the strongest available proof that §5's restore worked**: a
> single changed golden anywhere in 3,700,000 would have changed a per-form
> line, and none did.

---

## §9  BOARD HYGIENE

| | |
|---|---|
| single-writer | `pgrep -x ssh` → **none**; `pgrep -x python3` → **none** but this session's own |
| `use_core` | **`False`, explicit on every probe** — `emit_suite.EMIT_USE_CORE` is `False` and **asserted at the top of both rigs** |
| divider | **`div=8 (4 MHz), commanded by this connection`** on **every** probe — **0 UNPINNED**.  STOP S-1 did not fire |
| probes taken | **13** (B-2) **+ 7** (B-1 control) **+ 2** (B-1 re-emit) **+ 2** (B-1 retain) **+ 800 rows** (closing chip proof) **+ 1** (`board_idle`) |
| closing chip proof | `check_ab_hw chip 800` → **`chip-vs-golden: MATCH over 800 rows`** |
| `board_idle()` | **run and clean** (NOP image, `use_core=False` explicit) |
| flashing | **NONE.**  `sw/testdata/flash_log.jsonl` is **26 entries** before and after; last entry `2026-09-19T23:48:27Z`, sha256 `0f4fcfa5cd55bc32…`.  **FLASH #23 IS INTACT** |
| ⚠ erratum | **declared in the pre-registration §0**: a read-only `ssh 'uname -a; uptime'` liveness check was run **before** the pre-registration was committed.  No CFG written, no capture, no core selected, no divider touched |

---

## §10  BARS Y-1 … Y-9

| bar | verdict |
|---|---|
| **Y-1** | **MET, with its own erratum declared in advance** — prereg `6703bd93af` and rig `6cfd3d0cfd` both before the first board **probe** and before the first `tests/` edit; the `uname` liveness check is §0 and §9 |
| **Y-2** | **MET** — §2, every document by DATE against the ucore's first commit, A-1 and A-2 each with the measurement |
| **Y-3** | **MET — ONE MECHANISM, and WAVE 22's is REFUTED** (§4b): a two-sided directed control at 20/20 and a fingerprint that holds 8/8 |
| **Y-4** | ⚠ **PARTIAL, AND THE SHORTFALL IS THE RESULT.**  Collision **shown** (three derivations), case **regenerated**, **re-captured from silicon** — and the exemption **NOT retired**, because the replacement is unreadable by the scorer (§5).  Original archived byte-identical, ledger entry **§E** written |
| **Y-5** | **MET** — 13/13 captured with CONSTRUCTED encodings, mechanism reported (§6.2), `hdl/` untouched, falsifier registered (§6.3) |
| **Y-6** | **MET — 31 legs SAME, 0 MOVED, 0 NEW**, and `v0.3` did NOT move because §5's replacement was refused, which is the one deviation P-B1c registered in advance.  The `v0.3` leg's log is **byte-identical** to the run that registered the figure |
| **Y-7** | **MET — `git diff -- hdl/` EMPTY throughout** |
| **Y-8** | **MET** — no `git stash` / `checkout .` / `reset --hard` at any point; every `git add` by explicit path; `sw/testdata/receipts/*.jsonl` never staged; the user's 21 modified and 16 untracked files untouched |
| **Y-9** | **MET** — §11, reported as a FLOOR with a disposition each |

---

## §11  DOCUMENTATION DISCREPANCIES — **REPORTED AS A FLOOR**

| # | where | what is wrong | disposition |
|---|---|---|---|
| **W-1** | `v02_suspected_divergences.md` | escalates seven cases as *"a genuine chip-vs-RTL disagreement"* against an engine that did not exist | **MARKED-HISTORY** — quoted WAVE 24 header with the date arithmetic and 3000/3000 |
| **W-2** | `v03_divergence_ledger.md` | 62 cases, five families, each with a *"fix locus"*, all against the archived FSM core | **MARKED-HISTORY** — header with 169,998/170,000 and the per-family table |
| **W-3** | `suite_scorer_results_2026-09-19.md` §7 | the `v20suite` eight attributed to *"the two parts' queues are different depths"*, labelled UNPROVEN | **SUPERSEDED HERE, NOT EDITED** — §4b refutes it with a directed control.  WAVE 22 labelled it a hypothesis and said so; that is why it could be refuted rather than inherited |
| **W-4** | `lea_mod3_results_2026-09-20.md` §4 (WAVE 23) | *"the retained EA lane holds the EA on silicon"* — true of both its witnesses, **false as a general law** | **REFINED HERE, NOT EDITED** — §6.2, by WAVE 23's own registered falsifier.  Its §4 table of ucore values is **confirmed** row for row |
| **W-5** | `sw/char_mod3.py` docstring | *"the four memory-operand-REQUIRED opcodes that **wedge v30_core at S_HALT**"* — describes the deleted FSM core (WAVE 23 proved the ucore does not wedge) | **LEFT WITH REASON** — it is the rig that froze the 2026-07-27 artifact, and its probe list already disagrees with the artifact it froze (§6).  Editing its prose would make it look like the rig that took those rows.  Recorded here and in §6 |
| **W-6** | `tests/v30/v0.3/README.md` | *"every case is reproducible from seed `f\"{base}/{opcode}/{n}\"`"* — **not true today**: `0F1B`'s index 3917 came from seed-attempt **3919** (7,321 of 10,000 indices have `idx != seed`), and re-composing either VOID case's recorded seed today yields a **different instruction encoding and a different `CS:IP`** | **LEFT UNTOUCHED — IT IS THE USER'S OWN MODIFIED FILE** (`git status`: ` M`).  Recorded here instead |
| **W-7** | `emit_suite.cmd_reemit` docstring | *"only valid for forms whose current file has `idx == seed`"* — and `_emit_one_index` **always** starts from `.../{idx}`, so on a form where they differ a re-emit silently produces a different lineage.  `cmd_reemit` also does **not** update `XX.seeds.json`, whose `[idx, seed]` map cannot express a within-index reroll `.../{idx}/{r}` at all | **RECORDED, NOT FIXED** — a wave that could not ship its re-emission should not also rewrite the re-emitter |

| **W-8** | `sw/lea_mod3_gate.py`, leg **L1b/L4** | prints the frozen `si_loaded=0xd4e5` for `MOV CW,[4455h]` as *the* silicon value.  **It is FILL-DEPENDENT**: the same instruction on the same part reads **`0x1121`** today, because the composer's fill moved `0x90` → `0xCC` (§5, §6.1).  The gate is not wrong — it reads the artifact, and L4 is REPORTED, not a bar — but the number is not reproducible on the current rig and nothing says so | **RECORDED, NOT FIXED** — the gate is WAVE 23's and its L4 is explicitly not a bar; changing what it prints in the wave that found the reason would make the two waves' outputs incomparable |

⚠ **THE COUNT IS A FLOOR AND THE METHOD SAYS SO.**  This is a manual
enumeration over the documents this wave had reason to open.  **W-3, W-4 and
W-7 were each found by a MEASUREMENT contradicting a sentence, not by any
search**, and no gate enumerates claims of this kind.

---

## §12  WHAT THIS WAVE DELIBERATELY DID NOT DO

* **No `hdl/` edit** — including the one-qualifier fix §6.3 names and the
  one-line testbench fix §4b names.  Both are BOOKED with falsifiers.
* **No Quartus, no flash, no Codex, no nested subagent.**
* **No replacement shipped into `v0.3`** — restored byte-identical instead (§5).
* **No disposition TAKEN on the `v20suite` eight** — proposed only.
* **No `mod3_illegal` re-capture** and no `ea_residue` injection (STOP S-4).
* **No document deleted.**  Two marked, three superseded-in-place-by-reference,
  two left with reasons.
* **No edit to `emit_suite`'s re-emitter**, whose two defects are §11 W-7.
