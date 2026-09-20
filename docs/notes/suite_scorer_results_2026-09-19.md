# WAVE 22 — RESULTS.  THE FOUR SUITES HAVE REAL TOTALS.

Scored against **`sw/check_core.py --core ucore`**, offline, no board, no flash,
no Quartus, **no `hdl/` edit of any kind**.  Pre-registration: `d2b1faaba0`,
`docs/notes/suite_scorer_prereg_2026-09-19.md`, committed before the first `sw/`
edit and the first scored run.  Adapter and cleanup: `946bcea689`.

Every raw per-form line and per-form JSONL is committed by value under
`sw/testdata/wave22/`.

---

## §1  THE HEADLINE

| suite | cases | **ucore** | rate | never scored before? |
|---|---:|---:|---:|---|
| `v0.1` **(the control)** | 169,000 | **169,000 / 169,000 full** | 100.0000 % | no — the standing gate |
| `v0.2` | 347,000 | **347,000 / 347,000 full** | **100.0000 %** | **YES — "cannot be run at all"** |
| `v0.2` `--raw-flags` | 347,000 | **347,000 / 347,000 full** | **100.0000 %** | YES |
| `v0.3` (list DISABLED) | 3,700,000 | **3,699,998 / 3,700,000 full** | **99.99995 %** | **YES — full suite, first time** |
| `v0.3` (list applied) | 3,699,997 | **3,699,997 / 3,699,997 full** | **100.0000 %** | YES |
| `v20suite` `--arch-only` | 3,125,000 | **3,124,992 / 3,125,000 ARCH** | **99.99974 %** | **YES — first time** |
| `mod3_illegal` | 128 | **cycles 128 / 128 · ARCH 0 / 128** | see §5 | **YES — it had NO live scorer** |

**TEN FAILING CASES IN 7,172,000, ACROSS THREE SUITES NEVER SCORED BEFORE**
(`v0.2` 347,000 + `v0.3` 3,700,000 + `v20suite` 3,125,000), **plus a fourth,
`mod3_illegal`, whose 128 are §5.**
Each of the ten is characterised in §4–§6.  Nothing was tuned to reach these
numbers; the two `v0.3` failures are the two cases a pre-existing list already
named, and the eight `v20suite` failures are reported exactly as measured.

⚠ **`mod3_illegal` IS 0 / 128 ARCHITECTURALLY AND THAT IS THE EXPECTED RESULT**,
pre-registered as such (§2, W-3 row 6).  It is a directed cell whose whole
subject is a residue no injected engine can reproduce.  **What it proves is in
§5, and it is a POSITIVE result.**

---

## §2  W-1 … W-8, SCORED

| bar | verdict | evidence |
|---|---|---|
| **W-1** pre-registration before the first `sw/` edit and first scored run | **MET** | `git log`: prereg `d2b1faaba0`, first `sw/` edit `946bcea689` |
| **W-2** `v0.1` ZERO-DELTA across the adapter | **MET, TWO WAYS** | §3 |
| **W-3** four real totals with failure taxonomies | **MET** | §1, §4, §5, §6 |
| **W-3b** `v0.3` runtime plan, registered before the run | **MET — and the pre-registered estimate held** | registered **≈ 50 min** from a 7-form timing (5.55–10.42 s, mean 8.0 s/form) against a 2.5 h budget. **Measured, all six legs launched together on 8 cores: `v0.3` 43.3 min · `v20suite` 33.8 min · `v0.2` 4.6 min each leg · `v0.1` 2.6 min · `mod3_illegal` 7 s.** **Every leg ran in FULL; no slice was substituted for a whole** |
| **W-4** the adapter DECLARES each dialect, no per-suite/per-opcode case | **MET** | `sw/suitemeta.py --selfcheck` **PASS, 17 checks, 3 dialects reached, 0 skipped**, non-vacuity fires (16 of 347 `v0.2` masks move when the delegation target is emptied) |
| **W-5** the live ladder is ZERO-DELTA | **MET with TWO REGISTERED DISCREPANCIES IN THE BAR ITSELF** | §7 |
| **W-6** nothing in `hdl/` edited | **MET** | `git diff -- hdl/` empty; verified at each commit |
| **W-7** the user's 21 files untouched, receipts unstaged | **MET** | no `git stash` / `checkout .` / `reset --hard` was run at any point; every `git add` by explicit path; `sw/testdata/receipts/*.jsonl` still shows `M` and is not in any WAVE 22 commit |
| **W-8** no gate dies silently | **MET** | §8 — five gate resurrections/re-attributions, each recorded |

---

## §3  W-2 — THE CONTROL, PROVED TWO WAYS

**(a) THE ADAPTER IS A PURE-FUNCTION NO-OP WHERE THE OLD CODE COULD REACH.**
The pre-WAVE-22 inline expression from `check_core.py:878` was re-implemented
verbatim and compared against `suitemeta.SuiteMeta.flags_mask` over every form
of every suite the old code could resolve:

```
v0.1             347 forms, 0 differ, 16 carry a real mask (non-vacuous)
v20suite         360 forms, 0 differ, 99 carry a real mask (non-vacuous)
v0.1-w1/-w3/-w1evt/f4a_boundary/f0lock_tranche   26 forms, 0 differ
W-2 PART A: 733 forms compared, 0 DIFFER
```

**(b) END TO END, BEFORE AND AFTER.**
`check_core --core ucore --suite-dir tests/v30/v0.1 --opcodes all --cases 0`:

```
BEFORE  TOTAL: 169000/169000 full (cycles 169000, arch 169000)
AFTER   TOTAL: 169000/169000 full (cycles 169000, arch 169000)
351 per-form lines compared, 0 differ
sha256 of the per-form line set, BOTH SIDES: d6b4ef4ab73c0822fa84d5a5ee427829…
```

⚠ **BINARY IDENTITY, STATED RATHER THAN ASSUMED.**  The two runs executed
binaries with **different receipt ids** — `7ef59cb4b5b33366…` and
`5332bc26a38de4b2…` — and the **same `build_key` `8e9de77c32e8716d…`** over 29
declared `hdl/` inputs and **zero `sw/` inputs**.  The ids differ because
`check_core.build()` passes `args.build` **as `force`**, so `--build` is an
unconditional rebuild; the `build_key` is what the artifact is a function of,
and it did not move.  Recorded because a control whose two legs ran different
bytes is not a control, and "the RTL did not change" is a claim that has to be
carried by something.

---

## §4  `v0.2` — 347,000 / 347,000, AND THE MASK POLICY DOES NOT MOVE IT

The suite `ucore_gaps_2026-08-04.md` §F.2 recorded as **"never runnable through
this checker, for either core"** scores **100.0 %** the first time it is run.

**BOTH MASK LEGS AGREE TO THE CASE.**  Primary (delegated `v0.1` masks, of which
**16 of 347 forms carry a real non-`0xFFFF` mask**) and control (`--raw-flags`,
`0xFFFF` everywhere, **0 forms masked**) both score **347,000 / 347,000**.

> **So on these 347,000 cases the ucore computes every V20/V30-undefined flag
> bit exactly as the socketed chip did.**  The masks were not load-bearing here.
> That is a RESULT, not a tautology: the gap document's suggested `0xFFFF`
> fallback and the delegation this wave implemented would have produced the same
> number, and now that is measured instead of argued.

**NO TAXONOMY IS OWED** — there are no failures to classify.

⚠ **AND THE SUITE IS LARGELY REDUNDANT.**  `tests/v30/v0.3/README.md`:
*"supersedes v0.2 outright … v0.3 uses the same seed scheme as v0.2 (base
`v30-v0.2`), so its first 1,000 cases per form are prefix-identical to v0.2
wherever the reroll history agrees … 2.1 % of prefix cases (7,137 of 347,000)
differ."*  **The independently distinct population here is ≈ 7,137 cases, not
347,000**, and the "7.17 M" headline double-counts by that much.  Quantifying
the exact distinct remainder is **booked, not taken**.

---

## §5  `mod3_illegal` — 0 / 128 ARCHITECTURALLY, AND THE CONFINEMENT CLAIM IS NOW PROVED AGAINST THE ucore

It had **no live scorer**: `sw/check_mod3_illegal.py` exits **2** with the RET-2
FSM banner, and `--residue stale-ea` is `sw/ucsim_check.py`'s flag, reachable
only through the RET-1 refusal.  It shares `v0.2`'s metadata dialect exactly, so
`check_core` died on it with the same `KeyError` — **a fact no version of the gap
document, `standing_gates.md`, `CLAUDE.md` or this wave's own briefing recorded.**

```
python3 sw/check_core.py --core ucore --suite-dir tests/v30/mod3_illegal \
                         --opcodes goldens --cases 0
TOTAL: 0/128 full (cycles 128, arch 0)
```

**THE TAXONOMY IS THE RESULT, AND IT IS EXACT:**

| measured over all 128 | value |
|---|---|
| cycle rows | **128 / 128 PERFECT** |
| cases whose divergence is a SINGLE register | **128 / 128** |
| RAM differences | **0 / 128** (`ram=[]` on every case) |
| queue check | **`q_ok=True` on 128 / 128** |
| distinct diverging registers | **8, at exactly 16 cases each** |

And the eight registers pair with the ModR/M `reg` field **8 for 8**:

```
/0 ax   /1 cx   /2 dx   /3 bx   /4 sp   /5 bp   /6 si   /7 di
```

> **`tests/v30/mod3_illegal/metadata.json`'s claim — *"LEA reg,rm (mod3) loads
> the EU stale effective-address latch (last computed EA), independent of rm"* —
> IS CONFIRMED AGAINST THE ucore, for the first time.**  The divergence is
> confined to the destination register the `reg` field names, on every one of
> the 128, with cycle rows and RAM identical.  The ucore writes `0000` where the
> chip writes its pre-window address latch, which no injected engine can
> reproduce because the value is a property of what the chip did **before** the
> window.
>
> **The `reg`-field pairing is the classifier's own positive control**: an
> instrument that merely reported "one register differs" would not have to
> produce the right one, and it produces the right one 8 times out of 8.

**`0 / 128` is the honest architectural number and it is reported as the
headline.**  A `--residue`-style confinement gate would score this 128/128, and
building one is **booked, not taken** — choosing a scorer after seeing a result
is what this repo's own discipline forbids.

---

## §6  `v0.3` — AND `known_divergences.json` IS NOT WHAT IT SAID IT WAS

### §6.1  The totals, both ways

```
--no-known-divergences   TOTAL: 3699998/3700000 full (cycles 3699998, arch 3699998)
list applied             TOTAL: 3699997/3699997 full            [3 excluded]
```

⚠ **`3,699,998` IS NOT THE NUMBER THE DOCUMENTS HAVE BEEN CARRYING, EVEN THOUGH
IT IS THE SAME DIGITS.**  In `CLAUDE.md`, `standing_gates.md`, the gap document
and RET-1 it is the **MODEL's architectural DENOMINATOR** (`3,700,000` minus the
two `VOID` entries, because `ucsim_check` read the list **by class** and excluded
`VOID` but not the arch-clean `EDGE`).  Here it is the **ucore's PASS COUNT out
of 3,700,000**.  Two quantities, one string.  **`check_core` is a cycle-row
checker and excludes all three, so the ucore's list-applied denominator is
`3,699,997`.**

### §6.2  THE PROVENANCE — READ BEFORE ANY EXEMPTION IS INHERITED

One such file exists in the whole `tests/` tree, 970 bytes, **three entries**.
Its own `_doc` establishes them against commits **`8fd94df` / `4508e08`**
(2026-07-25).  **`git ls-tree 4508e08 hdl/rtl/` lists `core` and NO `ucore`.**

> **IT IS THE ARCHIVED FSM CORE'S ACCEPTED-RESIDUE LIST** — not the C++ model's,
> as the briefing suspected, but the same disease under a different name: a
> residue list written against an implementation WAVE 21 deleted (`RET-2`),
> inherited by the ucore and never re-tested against it.  `ucore_gaps` §F.3's
> `229,999 / 229,999` block-I/O figure carries one of these three as
> *"1 documented pre-existing excluded"*, inherited the same way.

### §6.3  SCORED BOTH WAYS — AND THE THREE ENTRIES DO NOT HAVE THE SAME FATE

| entry | class | on the ucore | disposition |
|---|---|---|---|
| `0F1B` / 3917 | VOID | **FAILS**, first divergence row 9 `bus` | **claim CONFIRMED, independently** |
| `83.5` / 8683 | VOID | **FAILS**, first divergence row 7 `bus` | **claim CONFIRMED, independently** |
| `646F` / 8988 | EDGE | ✅ **PASSES 10000 / 10000** | ⚠ **OBSOLETE — the ucore does not have that cycle edge** |

**THE TWO `VOID` ENTRIES ARE RE-DERIVED FROM THE DIVERGENCE DATA ITSELF, NOT
INHERITED.**  `v03_divergence_ledger.md` F4bc says the `63 C0` PRELOAD bytes
landed on the operand EA in the 64K-mirrored image, so *"the golden encoded the
chip reading code, not the operand"*.  The measured rows say exactly that:

```
0F1B/3917   row 9  data: exp 25536 (= 0x63C0)  got  4489 (= 0x1189)
83.5/8683   row 7  data: exp 25536 (= 0x63C0)  got 42944 (= 0xA7C0)
```

**The EXPECTED value is literally `0x63C0` — the preload bytes — on both.**  The
ucore reads the modelled operand.  The VOID claim is a property of the CAPTURE,
it is engine-independent, and it now has a second engine's confirmation three
generations later.  **They stay excluded, and for the first time that exclusion
is measured rather than asserted.**

**THE `EDGE` ENTRY IS A DIFFERENT MATTER.**  It claims a *"known pre-existing
1/10000 cycle edge, repnc OUTSW cx=13 (REP OUTS loop timing, rows 28-32)"* — an
**ENGINE** claim about a core that no longer exists.  The ucore scores that form
**10,000 / 10,000**.  **The exemption excuses a case that passes.**

**IT IS NOT DELETED BY THIS WAVE.**  The list is unedited and the entry is
unremoved; one wave's reading is not grounds to retire another's record, and
removing it would change `v0.3`'s denominator on the authority of a single
sitting.  **Booked, with the measurement on the record**, and
`check_core --no-known-divergences` exists so the question can be asked by
anyone at any time.

### §6.4  Taxonomy

**Two failing cases in 3,700,000.**  Both are the `VOID` pair above.  **Every
one of the other 368 forms is 10,000 / 10,000 on cycles AND arch** — including
all 23 block-I/O (INM/OUTM) forms, which is where `ucore_gaps` §F.3's figure
came from, and including the whole `v0.3` OUTS/INS prefetch-ordering family
(29,892 cases) that `v03_divergence_ledger.md` booked as the **primary
BIU-ordering intake** against the FSM core.  **That intake is closed in this
engine.**

---

## §7  `v20suite` — 3,124,992 / 3,125,000 ARCH, AND THE EIGHT HAVE A SHAPE

It needs **`--arch-only`** — its own `--help` says *"For the V20 suite"* — because
it is a µPD70108 (V20, 8-bit bus) capture and its per-cycle rows are not
comparable with a V30 core.  Without the flag it scores 0.  **This was true
before WAVE 22 and needed no adapter; the suite was never blocked, only never
run.**

```
python3 sw/check_core.py --core ucore --suite-dir tests/v30/v20suite \
                         --opcodes all --cases 0 --arch-only
TOTAL ARCH: 3124992/3125000          360 forms, 8 failures
```

**THE TAXONOMY — 8 FORMS, EXACTLY ONE CASE EACH:**

| form | idx | disassembly | diverging registers |
|---|---|---|---|
| `03` | 2019 | `add bp, word [ds:bp+di-30h]` | `sp` (0ccf→0cce), `flags` |
| `0F1D` | 4712 | `set1 word [ss:bp+si], FFF7h` | `bx`, `flags` |
| `29` | 9262 | `sub word [cs:si-21FCh], bx` | `sp`, `bp` (5fa4 → **9090**) |
| `62` | 1229 | `bound cx, word [ss:bp+4Ah]` | `dx` |
| `85` | 4717 | `test word [cs:bp+si+16h], ax` | `cx`, `flags` |
| `86` | 9919 | `xchg dl, byte [ss:bx-3Bh]` | `dx` (7cb6 → **90b6**) |
| `E8` | 216 | `call 0002h` | `sp` (0a89→0a87) |
| `E9` | 7762 | `jmp 0002h` | `sp` (95ed→95eb) |

**WHAT THE EIGHT HAVE IN COMMON — stated as an observation, with its attribution
labelled UNPROVEN:**

1. **`sp` MOVES ON FOUR INSTRUCTIONS THAT DO NOT TOUCH `sp`** (`03`, `29`, `E8`
   `call 0002h`, `E9` `jmp 0002h`), and on `E8`/`E9` the target is **`0002h`** —
   inside the interrupt-vector table.  A wild jump into the vector area executes
   whatever is in the image, so the scored window runs past the instruction under
   test and the two parts diverge on what they execute NEXT, not on the
   instruction.
2. **`0x90` — the image fill byte — APPEARS IN TWO GOT VALUES** (`29`'s `bp` is
   `9090`, `86`'s `dx` high byte is `90`).  That is the signature of a read
   landing on fill, i.e. the same instrument class as `v0.3`'s `VOID` pair.
3. **SIX OF THE EIGHT CARRY A SEGMENT OVERRIDE** on the memory operand
   (`ds:`/`ss:`/`cs:`), and **two touch memory THROUGH `cs:`** — `29` WRITES
   through it (self-modifying code) and `85` READS through it — outcomes that
   depend on how much has already been prefetched.  ⚠ **`--arch-only` masks the final QUEUE (V20 4-byte
   vs V30 6-byte) but it CANNOT mask the ARCHITECTURAL CONSEQUENCE of a different
   prefetch depth**, and a V30 fetching two bytes further ahead than a V20 is
   exactly what would make a `cs:`-override write land differently.

> **ONE MECHANISM WOULD ACCOUNT FOR ALL EIGHT — the two parts' queues are
> different depths, so a case that reaches past its own instruction (by a wild
> jump, or by writing into the code it is about to execute) is not a comparable
> case.**  That is a hypothesis, it is not established here, and it is written
> this way deliberately: **eight per-case explanations would be the many-cased
> rule the simplicity principle names as a signal of misunderstanding.**
> **BOOKED.**  The falsifier is cheap and is registered for whoever takes it:
> re-score the eight with the window truncated at the instruction's own
> retirement; if the mechanism is right, all eight become non-comparable rather
> than failing.

**NOTHING HERE IS EXCUSED.**  The eight are in the numerator and the
denominator; `3,124,992 / 3,125,000` is the quotable figure.

---

## §8  W-5 — THE LIVE LADDER, MEASURED, WITH TWO DISCREPANCIES IN THE BAR

| leg | briefed | **measured** | |
|---|---|---|---|
| `check_core --opcodes all --cases 0` `--ce-div 2` | 169,000 | **169,000 / 169,000** | ✓ |
| … `--ce-div 3` | 169,000 | **169,000 / 169,000** | ✓ |
| … `--ce-div 4` (default) | 169,000 | **169,000 / 169,000** | ✓ |
| … `--ce-div 8` | 169,000 | **169,000 / 169,000** | ✓ |
| … `--ce-div 1` | REFUSED | **REFUSED, exit 2, clause cited** | ✓ |
| HLT sweeps `--waits 0/1/2/3` | 279/283 | **97 + 93 + 45 + 44 = 279 / 283** | ✓ |
| `ss_lint` | 232 / 229 / 4 / 0x8F / 0x8FE8 | **232 (109×2 BIU + 122×2 EU + tag) · 229 flops · 4 whitelist · 0 UNMAPPED** | ✓ ⚠ see (a) |
| `cutset_lint` | PASS 81/0 | **PASS, 81 members / 0 violations** | ✓ |
| `phase_split_lint` | 157/779/0 | **PASS, 157 members / 779 bits / 0 violations** | ✓ |
| `r7_lint` | PASS | **PASS, 0 undeclared carriers / 0 unresolved / 0 `stop` sites** | ✓ |
| `qsf_lint --check` | PASS | **PASS — `nec_test_ucore.qsf` is CANONICAL** | ✓ |
| `core_portlist_lint` | PASS 4 configs | **PASS, 4 configurations** | ✓ |
| `test_quartus_gate` | 302/302 | **302 / 302 checks pass, PASS** | ✓ |
| `test_artifact` | 45/45 | **45 / 45** | ✓ |
| `chainflat_relocation_check` | 9/9 | **PASS — 9 arms, one copy each, byte-identical to `aba01feb07`** | ✓ |
| `chain_lfsr_gate` | 4 signatures byte-identical | **PASS**, `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78` — **BYTE-IDENTICAL** to the registry, depth 6, 0 overflows | ✓ |
| `demux_off_gate` | PASS | **PASS** | ✓ |
| `check_ucore_tables` (G0) | PASS 9,988 | **PASS — 1028 rows + 8192 micro-addresses + 768 PLA entries = 9,988** | ✓ |
| `check_boot` 220 / 400 | MATCH | **MATCH over 220 rows** / **MATCH over 400 rows** | ✓ |
| `check_ab_sim --core ucore` | 187 | **MATCHES CHIP BOOT over 187 rows** | ✓ |
| `ghost_launch_law` | 200/200 | **ALL THREE POPULATIONS 200/200 = 100.0 %** | ✓ ⚠ see (b) |
| `check_fuzz_bank` | PASS 621 | ⚠ **REFUSES — `FsmCoreRetired`, exit 1** | ✗ see (c) |

**(a) `ss_lint` DOES NOT PRINT `SS_VERSION` OR `SS_TAG`.**  It prints
*"109×2 BIU + 122×2 EU + tag = 232; constants OK"* and the flop census.  The
briefed `0x8F` / `0x8FE8` are **in the RTL, not in the tool's output**, and were
read directly from `hdl/rtl/ucore/v30u_ss_pkg.sv:136,151`: `SS_VERSION = 8'h8F`,
`SS_COUNT = 1 + 109 + 122 = 232`, `SS_TAG = {8'h8F, 8'd232}` = **0x8FE8**.
Confirmed — but the bar as written attributes two figures to a tool that does not
report them.

**(b) `ghost_launch_law` TAKES A SUBCOMMAND.**  Bare, it exits **2**:
*"the following arguments are required: cmd"*.  The 200/200 leg is
`ghost_launch_law.py score`.  The bar as written names an invocation that
cannot run.

**(c) ⚠⚠ `check_fuzz_bank` IS ON THE BRIEFED LADDER AND WAVE 21 RETIRED IT ONE
COMMIT EARLIER.**  `docs/notes/fsm_removal_results_2026-09-19.md:330`:
*"**`check_fuzz_bank`** | PASS \| 621 \| stable 621 … | **REFUSES —
`FsmCoreRetired`** | ⚠ **FORMALLY RETIRED**, RET-2, replaced by NOTHING"*.
Measured here: **exit 1** through the `check_seq` pin.  **The figure `PASS 621`
is its LAST REGISTERED figure, not a current one**, and quoting it as a live
ladder leg is exactly the stale-precedence pattern this wave was sent to find.
⚠ It exits via a **traceback**, not through `fsmcore.refuse()`'s clean banner —
noted, not changed: WAVE 21 owns that tool's refusal shape.

**ZERO-DELTA VERDICT: every leg that can run is UNMOVED.  21 legs SAME, 0 MOVED,
2 bars mis-stated, 1 bar naming a retired gate.**

---

## §9  THE ADAPTER

**ONE SENTENCE:** *a suite's opcode map comes from its own `metadata.json` when
that file has one, and from `v0.1`'s otherwise.*

**THREE dialects, not the briefing's four.**  `v0.2` and `mod3_illegal` are the
**same** dialect — both say *"metadata, but no opcode map"* — and the briefing's
table splits them and omits `mod3_illegal` entirely.

| dialect | predicate | suites | opcode map |
|---|---|---|---|
| `sst` | `metadata.json` exists AND has `opcodes` | `v0.1`, `v20suite` | its own |
| `emitter` | `metadata.json` exists, no `opcodes` | `v0.2`, `mod3_illegal` | **delegates to `v0.1`** |
| `absent` | no `metadata.json` | `v0.3`, every `v0.1-w*`/`*evt`/derived tranche | **delegates to `v0.1`** |

One predicate each, one delegation target shared by two, **no per-suite branch
and no per-opcode case anywhere in `sw/suitemeta.py`**.

**THE POSITIVE CONTROL** (`--selfcheck`, **PASS / 17 checks**): every dialect
REACHED by a real suite on disk; delegation ANNOUNCED, never silent; a delegated
`flags_mask` equal to `v0.1`'s form for form over 724 forms; and a **NON-VACUITY**
leg that empties the delegation target and **requires** the equality to break —
it fires, 16 of 347 `v0.2` forms move.

⚠ **THE PRECEDENCE INVERSION, AND IT IS WHY THIS WAS NEVER FIXED.**  The whole
rule already existed — in **`sw/ucsim_check.py::load_meta`, the C++ model's
scorer**, whose CLI has refused since WAVE 20 (`RET-1`).  It implemented **both**
halves; `check_core` implemented only the file-absent half.  And
`sw/timed_gate.py`, `sw/timed_probe.py` and `sw/uarch.py` all **imported it** to
get the rule.  *The dead model's scorer was the live tree's metadata authority.*
Nothing was ported: the rule moved out, and `ucsim_check` keeps
`load_meta` / `flags_mask_of` / `dont_care_spec` as **thin forwarders** so no
caller's line had to change.

Its one behavioural read of the delegated dict — `meta.get("cpu")` → `bus8` —
is now `meta.raw.get(...)`, and the equivalence was **swept over every suite
directory in `tests/v30/`: 0 disagreements.**

---

## §10  THE `--core sim` CLEANUP — A DISPOSITION PER HIT, AND THE COUNT IS A FLOOR

**ENUMERATED, NOT ESTIMATED.**  `sw/testdata/wave22/core_sim_control.py`:

| quantity | before | after |
|---|---|---|
| real `--core` declarations in `sw/` | 42 | 42 |
| **offering `"sim"` in `choices`** | **24** | **0** |
| DEFAULTING to `"sim"` | 13 | **13 — KEPT DELIBERATELY** |
| carrying `type=simbin.core_choice{,_optional}` | 0 | **24** |

The briefing estimated *"~40 `--core` option lists"*.  A looser one-line
instrument said **45** and was over-counting three non-`--core` flags
(`--golden-args`, `--core-solve`, `--cores`); the paren-balanced instrument says
**42**, and its own first form said **43** by counting `simbin.py`'s explanatory
comment as a declaration.  **WAVE 21's finding firing on this wave's own
instrument: a token in an enumeration is not a token that was dispositioned.**

### §10.1  WAVE 21's STATED BLOCKER DISSOLVED ON A MEASURED FACT

`fsm_removal_results_2026-09-19.md:482` booked this item with a reason:
*"Removing the `sim` half means changing ~15 measurement tools' DEFAULTS from
`sim` to `ucore`, which silently changes WHAT A BARE INVOCATION MEASURES in a
wave that cannot re-measure them."*

**That risk is real and it was not accepted — it was removed.  `argparse` applies
`type=` to a STRING DEFAULT.**  Measured:

```
ap.add_argument("--core", default="sim", type=simbin.core_choice)
ap.parse_args([])      ->  SystemExit 2, the RET-1 banner
```

So `default="sim"` now refuses **on omission** exactly as on `--core sim`, and
**cannot** silently become `ucore`.  **No default was re-pointed and no
consumption point was edited** — one line per site, 24 sites.  The first design's
`core_required()` helper was written and then **deleted as unnecessary**, and the
measurement that killed it is recorded in `sw/simbin.py` beside where it stood.

### §10.2  DISPOSITIONS — every hit, individually

| disposition | n | what |
|---|---|---|
| **FIXED** — `choices` dropped, `type=simbin.core_choice` added | **24** | the full enumerated set, in 20 files; table in `sw/testdata/wave22/core_sim_dispositions.txt` |
| **DELIBERATELY LEFT, with reason** | **13** | the `default="sim"` strings.  Removing them would require choosing a replacement default; keeping them makes omission refuse by name. The refusal is proved by control check (3) |
| **DELIBERATELY LEFT, with reason** | **1** | `sm3_nmigeom`'s `--core ""` — a real third **STATE** ("report the chip axis, run no engine leg"), not a third engine. `core_choice_optional` preserves it |
| **CHANGED MEANING, named** | **2** | `--core both` in `wrfuzz_wr1_guard` / `wrfuzz_w7_gap_guard` meant `sim`+`ucore`; with one engine the word is a lie, so `both` is now refused by name rather than quietly meaning one leg |
| **NOT TOUCHED — a different token** | — | `"sim"` as a board-capture **LEG KEY** (`fz2_a2_replay.py`: `LEG = {"real": "socket (use_core=0)", "sim": "fabric core (use_core=1)"}`), so `j["sim"]` in `f21_wt1.py`, `ie_pinfall_cell.py`, `tf0f_cell.py` means **the FPGA core**, not the model |
| **NOT TOUCHED — history** | — | every `--core sim` figure in a dated `sm3_*` / `wrfuzz_*` pre-registration or results document. Those record measurements made when the model existed; a ratchet is only readable against its own history |

**⚠ THE COUNT IS A FLOOR.**  A mechanical enumeration plus a manual disposition
gives a lower bound, not a total.  **No gate was built for this** — WAVE 21 booked
that deliberately on the grounds that a gate's first green in the sitting that
needs it is unfalsifiable, and that reasoning is adopted unchanged.

---

## §11  ⚠⚠ FIVE MORE EAGER PRECONDITIONS.  WAVE 20 FOUND SIX AND THIS IS A CLASS IT COULD NOT SEE

WAVE 20 repaired six unconditional `simbin.ensure()` calls and wrote
***"An eager precondition is a coupling."***  **All six sat AFTER `parse_args()`,
where a `--core` test could be written.**  These five sit **BEFORE** it — so they
refused for the retired model's sake before the flag that selects the engine had
even been read:

| tool | what it was | repair | **what the repair revealed** |
|---|---|---|---|
| `sw/timed_wvec_gate.py` | unconditional, pre-`parse_args` | moved behind `args.core == "sim"` | reaches its own `gen_seq._v1_anchor_stop` refusal — **the v1-anchor casualty exists on `master` too, and its blocker is the ANCHOR, not the model** |
| `sw/timed_enter_replay.py` | " | " | same; registered ratchet `--core ucore` **154/154 ×5** is anchor-blocked, not model-blocked |
| `sw/timed_ins_replay.py` | " | " | `FileNotFoundError: sw/case31_all_exts.txt` — **confirming `CLAUDE.md`'s own staleness erratum §(a) on the ucore leg**, where the model's refusal had been masking it |
| `sw/uscope.py` | `--core` default `ucore`, **no `sim` option has ever existed** | **DELETED** | **`uscope 00 0` → rc=0.  A DEAD TOOL IS ALIVE.** |
| `sw/wrfuzz_smoke.py` | `--core choices=("ucore",)`, **UCORE-ONLY** | **DELETED** | reaches its OWN defect, `KeyError: 'brkem_pairs'`. **Reported, not fixed** — a different mechanism, and fixing it in the sitting that found it is how a finding becomes a guess |

**Three registered ratchets (`timed_wvec_gate` 88/88, `timed_enter_replay`
154×5, `timed_ins_replay` 1,312 / 2,624) are now correctly attributed**: they are
blocked by the v1 image anchor and by an uncommitted input file, **not** by the
retired model, and that distinction was invisible while the model's refusal fired
first.

Also found, by RUNNING the tools rather than reading them: `sm3_s16_score` and
`sm3_famb_survey` carried **function-local `import simbin`**, which makes the
name local for the whole function — so `type=simbin.core_choice` in the same
function raised `UnboundLocalError`.  Promoted to module level;
`sm3_s16_score --core ucore` prints `{'busstat_other': 24, 'ARCH': 27}`, its
registered figures.

---

## §12  ⚠ WHAT A SCORER IS NOT — THE EXPOSURE THIS WAVE FOUND AND DID NOT CLOSE

| suite | files on disk | **tracked in git** | tracked `*.json.gz` |
|---|---:|---:|---:|
| `v0.1` | 350 | 350 | **347** |
| `v0.2` | 351 | **1** (`.gitignore`) | **0** |
| `v0.3` | 746 | 3 | **0** |
| `v20suite` | 364 | 3 | **0** |
| `mod3_illegal` | 2 | 2 | 1 |

Deliberate, and documented in each suite's own `.gitignore`: `v0.2`
*"superseded by v0.3; kept disk-only … Whole suite untracked"*; `v0.3`
*"disk-only for now (916 MB); storage/versioning decided at the
upstream-contribution stage (task #17)"*; `v20suite` the upstream cache its
README calls *"not committed (re-fetchable)"*.

> **7,172,000 of the 7,341,128 cases scored above live only on this machine.**
> Giving them a scorer does **not** give them a repo-reproducible GATE, and this
> wave does not claim one.  Mitigation, not closure: every leg is recorded beside
> its suite's **per-file sha256 manifest digest**, committed at
> `sw/testdata/wave22/manifest-*.txt`:
>
> ```
> v0.1          350 files  af07d949a38c166d…
> v0.2          351 files  cbc0fde9d9586996…
> v0.3          745 files  6abe383d34ac0fa5…
> v20suite      363 files  67b8c7d7c83e8af5…
> mod3_illegal    2 files  67161a0c409c7fc6…
> ```
>
> **Deciding whether these suites should be in the repository is the owner's
> call and WAVE 22 deliberately did not make it.**

---

## §13  `tests/v30/v20suite/metadata.toml` — MEASURED, UNDECIDED, UNTOUCHED

It is **the user's untracked file**, sitting beside the tracked `metadata.json`
the scorers read.  Both were parsed **without modifying either**:

* the **same 8 header keys** with byte-equal values (`version` 1.0.2, `cpu` V20,
  `generator` arduino8088 v1.1, `date` 2024/05/25, …)
* the **same 282 opcode entries**
* **0 keys present in only one side · 0 entries differing**

**THEY ARE SEMANTICALLY IDENTICAL.**  The `.toml` is upstream SingleStepTests'
native manifest form; the `.json` is the converted copy.  **There is nothing to
decide between them, and WAVE 22 decides nothing**: not edited, not `git add`ed,
not resolved.  One adjacent discrepancy is reported and also not resolved — the
suite's README cites upstream *"suite v1.0.3"* while both manifests say **1.0.2**.

---

## §14  DOCUMENTATION DISCREPANCIES — FOUND AND RESOLVED

**Reported as a FLOOR.**  The enumeration was mechanical; the disposition was
manual; and a swept token is not a dispositioned token.

| # | claim | where | disposition |
|---|---|---|---|
| 1 | *"`v0.2` cannot be run … `KeyError: 'opcodes'` at `check_core.py:709`"* | `ucore_gaps` §F.2 ×3, `CLAUDE.md` ×2, `standing_gates.md`, ledger RET-1 | **FIXED** — the line is **878**, and the cause is a dialect mismatch, not a defect |
| 2 | *"three of the four golden suites have never been run"* framed as one blockage | same | **FIXED** — `v0.3` and `v20suite` were **never blocked, only never run**; both scored on the unmodified tree |
| 3 | `mod3_illegal` shares the blocking dialect | **nowhere** | **FIXED** — added; it had no live scorer at all |
| 4 | `3,699,998` presented as the suite's size | `CLAUDE.md`, `standing_gates.md`, gaps, RET-1 | **FIXED** — it is the MODEL's arch denominator (3,700,000 − 2 `VOID`); the suite is **3,700,000** and the ucore's cycle denominator is 3,699,997 |
| 5 | *"7.17 M architectural cases"* | same four | **FIXED** — it **double-counts**; `v0.3` *"supersedes v0.2 outright"* by `v0.3/README.md`, same seed base, 2.1 % of the prefix differing |
| 6 | the live **Functional** recipe names `sw/ucsim_check.py` and `--residue stale-ea` | `CLAUDE.md` | **FIXED** — both are behind the RET-1 refusal; replaced with the live `check_core` recipe |
| 7 | `known_divergences.json` inherited without provenance | `ucore_gaps` §F.3's 229,999/229,999 | **FIXED** — annotated: FSM-provenanced (`8fd94df`/`4508e08`, no `ucore` in that tree), and re-measured in §6 |
| 8 | *"The v0.1 / v0.3 / f4a / f0lock suites … are still swept against the ucore by `check_core` (the standing ladder)"* | `sw/t30_sweep.sh`'s retirement note | **FIXED** — **`v0.3` was NOT on the standing ladder and had never been run against the ucore at all.** A retirement note that over-claims its successor is how a gate dies silently |
| 9 | the v20suite restore recipe (`for f in 00 27 37 B8 D2.4 F6.4 F6.6`) | `tests/v30/v20suite/README.md` | **FIXED (annotated)** — the working set is **360 forms / 3,125,000 cases**, not 7 |
| 10 | README *"suite v1.0.3"* vs metadata `1.0.2` | same | **RECORDED, NOT RESOLVED** — a question about which upstream snapshot is on disk |
| 11 | README names `pilot_v20.py` as the consumer | same | **FIXED** — `check_core … --arch-only` is now a consumer, and `--arch-only` is **required** |
| 12 | `ss_lint` credited with printing `SS_VERSION` / `SS_TAG` | this wave's briefing | **RECORDED** — it prints neither; read from `v30u_ss_pkg.sv` and confirmed (§8a) |
| 13 | `ghost_launch_law` quoted as a bare invocation | this wave's briefing | **RECORDED** — it requires a subcommand; the leg is `ghost_launch_law score` (§8b) |
| 14 | `check_fuzz_bank` PASS 621 on a live ladder | this wave's briefing | **RECORDED** — WAVE 21 **formally retired it** (RET-2) one commit earlier; 621 is its last registered figure (§8c) |
| 15 | *"~40 `--core` option lists still offer `sim`"* | this wave's briefing | **FIXED** — **24 declarations of 42**, in 20 files (§10) |
| 16 | the metadata table lists **four** dialects | this wave's briefing | **FIXED** — **three**; `v0.2` and `mod3_illegal` are one, and `mod3_illegal` is absent from the table (§9) |
| 17 | *"Removing the `sim` half means changing ~15 DEFAULTS"* | `fsm_removal_results` §booked | **DISSOLVED** — argparse applies `type=` to a string default; no default was changed (§10.1) |
| 18 | WAVE 20's six eager preconditions presented as the set | `CLAUDE.md`, WAVE 20 results | **FIXED** — **five more**, of a class the six could not reveal (§11) |

**18 found, 15 fixed, 3 recorded-not-resolved** (10, 12, 13 — plus 14, which is
recorded here and belongs to whoever re-registers the ladder).

---

## §15  WHAT THIS WAVE DELIBERATELY DID NOT DO

* **No `hdl/` edit.**  `git diff -- hdl/` empty throughout.
* **No board, no flash, no Quartus, no Codex, no nested subagent.**
* **No harness tuning.**  Not one line was changed after seeing a failing total.
* **`known_divergences.json` is UNEDITED** — the obsolete `EDGE` entry is
  measured and booked, not deleted, because one sitting's reading is not grounds
  to change another's denominator.
* **No confinement gate for `mod3_illegal`** — `0/128` is the honest
  architectural number; building the scorer that would make it 128/128 after
  seeing 0/128 is choosing a comparator after seeing a result.
* **No re-derivation of `v0.2`'s genuinely distinct remainder** (≈ 7,137 cases).
* **No decision on `metadata.toml`, or on whether the three suites belong in
  git.**  Both are the owner's.
* **No gate built for the `--core` sweep**, per WAVE 21's booked reasoning.
* **`sw/wrfuzz_smoke.py`'s `KeyError: 'brkem_pairs'` is reported, not fixed.**
