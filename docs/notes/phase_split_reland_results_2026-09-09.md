# WAVE 9 — **THE PHASE SPLIT, RE-MEASURED ON THE FLATTENED TREE.**  RESULTS, SCORED AS REGISTERED.

Pre-registration **`6c7d2e4285`**
(`docs/notes/phase_split_reland_prereg_2026-09-09.md`), committed **BEFORE THE
FIRST EDIT UNDER `hdl/`**.  Its bars **J-1 … J-11 are quoted verbatim below and
not one of them was softened, re-derived or re-scoped after a result was seen.**

**OFFLINE ONLY.  NO BOARD.  NO FLASH.  NO BITSTREAM WAS PROGRAMMED.**
No Codex consulted.  No nested subagent spawned.

| | |
|---|---|
| **Tree at entry** | `cf43e65cb3` (`master`), `git status --porcelain hdl/` clean of tracked modifications |
| **The instruments** | `451bbf26c5` (the three cut-set instruments, ported to the flattened tree) |
| **The edits** | (a) `6e822bf750` · (b) `5cf3254104` · **(c) `bacf7f9fd9`** |
| **Artifacts** | `sw/testdata/wave9/{before,after}/`, `sw/testdata/wave9/diag_*`, `sw/testdata/g6dist/wave9-cutset-{WITHEXC,NOEXC}-{control,retention}-n5/` |
| **Tool** | Verilator 5.032; Quartus 17.1.0 Build 590, 5CSEBA6U23I7, Slow 1100 mV 100 C, `divclk` **31.250 ns** |

⚠ **THIS WAVE WAS RUN IN TWO SITTINGS BY TWO AGENTS.**  The first was killed
mid-flight by a rate limit after committing the instruments, the
pre-registration and edits (a) and (b), and after taking the BEFORE ladder, the
AFTER ladder and J-8.  **The identity legs (J-4 · J-5 · J-6 · J-7 · J-8) were
independently re-verified from the committed artifacts by the coordinator and
again here from those same artifacts; they are attributed as
COORDINATOR-VERIFIED throughout and the re-verification is described, not
asserted.**  Edit (c), J-1, J-2, J-3, J-9, J-10 and this document are the
second sitting's own measurements.

---

## §2 J-4 / J-5 / J-6 / J-7 — **THE LADDER AND PIN IDENTITY.  COORDINATOR-VERIFIED, AND RE-VERIFIED HERE FROM THE SAME ARTIFACTS.**

`sw/phase_split_ladder.sh` on the UNEDITED tree (`sw/testdata/wave9/before/`)
and on the CUT tree (`sw/testdata/wave9/after/`), diffed leg by leg by
`sw/phase_split_ladder_diff.py`.

> ### **`=== ladder diff: 29 SAME / 2 MOVED / 0 MISSING`**

⚠ **A METHOD NOTE, BECAUSE IT ALMOST PRODUCED A FALSE ALARM.**  Diffing the raw
`before`/`after` log TEXT reports every leg as DIFFERING — the logs carry
timestamps, paths, durations and artifact receipts.  A regex sweep for
16-hex-character strings sweeps up receipts and tree hashes with the
signatures.  **The comparison is of the SCORED QUANTITIES, queried by name,
which is what `phase_split_ladder_diff.py` does.**

Both movers are registered in advance and neither is a measurement:

* **`ss_lint`** — `ss_flopcensus` **228 → 229** architectural flops, whitelist
  **3 → 4**.  That is J-6's *"grown by exactly the shadow's entry"*, and the
  entry is `s1q` on the **DERIVED** class beside `dec_q`.
* **`demux_off_gate`** — its own summary line, *"three muxed ports"* →
  *"two"*.  Edit (a)'s registered J-5 / §2.3 wording change.

| leg | registered | before | **after (the cut tree)** |
|---|---|---|---|
| `r7_lint` | PASS | PASS — 0 undeclared carriers / 0 undeclared unresolved / 0 `stop` sites | **SAME** |
| `check_core --opcodes all --cases 0` | 169,000 | 169,000/169,000 | **SAME** |
| `8F.0` | 500 | 500/500 | **SAME** |
| HLT sweeps `--waits 0/1/2/3` | 97 · 93 · 45 · 44 = 279/283 | 97 · 93 · 45 · 44 | **SAME** |
| `v0.1-w1` / `-w3` | 1,200 / 1,200 | 1,200 / 1,200 | **SAME** |
| `v0.1-w1 --opcodes EB` | 200 | 200 | **SAME** |
| the four `evt` cells | 200 / 1,200 / 200 / 1,200 | same | **SAME** |
| `v0.1-w1evt-biased` | 1,200 | 1,200 | **SAME** |
| `ulockstep --golden all --cases 50` | 17,350 ALL LOCKSTEP | ALL CASES LOCKSTEP | **SAME** |
| `ghost_launch_law score` | 200/200 | 200/200 = 100.0 % | **SAME** |
| `check_boot --core ucore` | 220 and 400 | MATCH 220, MATCH 400 | **SAME** |
| `check_ab_sim --core ucore` | 187 | MATCH over 187 rows | **SAME** |
| `sm3_s16_score --core ucore` | 1,320/1,371 | 1,320/1,371 | **SAME** |
| `demux_off_gate` | PASS | PASS | **PASS** (the registered wording move) |
| `test_artifact` | 45/45 | 45/45 | **SAME** |
| `test_quartus_gate` | 254 / **255 with a build tree** | **255/255** | **SAME** |
| `ucrom_mif_check` | PASS | PASS | **SAME** |
| **J-7** `--ce-div 2 / 3 / 8` | 169,000 each | 169,000/169,000 each | **SAME** |
| **J-7** `--ce-div 1` | REFUSED | REFUSED, clause cited (exit 2) | **SAME** |

**J-4(a) `chain_lfsr_gate` — BYTE-IDENTICAL, 4 OF 4.**  4 seeds × 400,000
fabric clocks: `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` ·
`d05b6c3c3d9fbe78`, with `CHAIN_DEPTH_MAX` **6** · `entry_st` **25** ·
`coincide` **0** on every seed of both runs.

**J-4(b) `fz2_replay` — SCORED-CONTENT sha256 IDENTICAL over 305 rows.**

⚠ **ERRATUM AGAINST THE COORDINATOR'S OWN HANDOFF, MEASURED HERE.**  The
handoff quotes the scored-content sha256 as
`d8f71943225e83425058042ea86072b062c75b5d23262f84462ba9c72f2c2c2f`.
Re-run on the committed artifacts with the repo's own
`sw/phase_split_replay_sha.py`, **both sides read
`de949fd373ed77de7f7d980a1728538de1b6ddaf6e200a9e61ba69bd1a8b2942`** — which is
the value `CLAUDE.md` already registers for WAVE 7 and WAVE 4 quotes for its own
three runs.  **The CONCLUSION is unchanged and is the one that matters (the two
sides are IDENTICAL); the quoted digest in the handoff is wrong and is corrected
here rather than repeated.**  The `tb_sys` receipt moved
`16f66ab3c23e3f52…` → `9e4910d317a34d48…`, **which is NOT quoted as evidence of
anything** — a Verilator receipt moves across rebuilds of a byte-identical tree
(prereg §5, WAVE 3 §6 item 9).

**J-6 — SAVE STATE DID NOT MOVE.**  `ss_lint` exits 0;
`SS_VERSION` **0x8F** / `SS_COUNT` **232** (109×2 BIU + 122×2 EU + tag) /
`SS_TAG` **0x8FE8**, **ALL UNCHANGED**; **0 UNMAPPED** on both sides;
`hdl/rtl/ucore/v30u_ss_pkg.sv` is **untouched by every commit of this wave**.
The census moves 228 → 229 flops and the whitelist 3 → 4 — **exactly the
shadow's one entry, and nothing else.**

---

## §3 J-8 — **NO REGRESSION WITH THE EXCEPTION.  10 OF 10 PASS, AND THE BAND ROSE.**

Measured on the CUT tree **BEFORE** edit (c), which is §4 step 7 of the
pre-registration and is the order that makes it interpretable: with the
exception still in the SDC, the cut must not have cost anything.

| | `worst-of-5@seeds{1,2,3,4,5}` | draws | ALMs | record |
|---|---:|---|---:|---|
| **CONTROL** | **41.69 MHz** (seed 4) | 42.72 · 42.97 · 42.04 · **41.69** · 44.65 | 7,940–7,966 (19 %) | `9d6fe1ba48918e81…` |
| **RETENTION** | **42.38 MHz** (seed 4) | 43.01 · 44.34 · 45.19 · **42.38** · 43.34 | 7,991–8,040 (19 %) | `872d210583d40382…` |

**Against WAVE 7's `worst-of-5` of 41.06 on both configurations: +0.63
(CONTROL) and +1.32 (RETENTION).  J-8 IS MET — there is no regression.**
Every draw PASS, E7 `n_moved` 1 / `moved_offending` 0 (the declared §70.7
exemption, `hdl/nec_test_ucore.qsf`), E8 5/5 seeds honoured, E10 N = 5, TNS
0.000 setup AND hold on every domain, `tns_violations` empty on all ten.
`off_class` **EMPTY** on all ten with **`SAME` measured k = 2.0 against a
nominal of 2.0** — which is the check that the exception was still in force
for this leg, i.e. that J-8 measured what it says it measured.
`input_manifest` **`9f52ae11123b93fb…` / 99 files, IDENTICAL between the two
configurations**, which is the check that they differ by the
`--verilog_macro` and nothing else.

⚠ **AND THE AREA MOVED THE WRONG WAY FOR THE SECOND WAVE RUNNING, WHICH IS
RECORDED AND NOT EXPLAINED.**  The split adds **778 bits of flop** and the
fitted design is **SMALLER**: 7,940–8,040 ALMs against WAVE 7's 8,079–8,149.
WAVE 4 §3.2 recorded the same shape.  `standing_gates.md` §A governs and A&S
combinational counts are not reproducible run to run (§74.4a).

⚠ **THE BINDING PATH WITH THE EXCEPTION IS THE MICROCODE ROM ON 9 OF 10 DRAWS**
— an M10K's own `PORT_A_WRITE_ENABLE_REG` or a front-end term
(`opc_sel[0]`, `rowq[0]`, `opc_from_modrm`) to another M10K's
`porta_address_reg`.  **The chain is not on it, and neither is the shadow.**
That is WAVE 7's finding reproduced on the cut tree, and it is the reading that
matters for §5.

---

## §4 J-1 / J-2 — **THE REQUIREMENT.  `--seeds 5`, BOTH CONFIGURATIONS, NO EXCEPTION.**

Driver: `sw/quartus_gate.py --seeds 5` twice, `--retention` on the second,
`hdl/nec_test_ucore.qsf` `git checkout --`'d before and after each sweep, the
single-writer guard by EXACT binary name before every stage.  Logs
`sw/testdata/wave9/g6_noexc_{control,retention}_n5.log`.

### 4.1 ⚠ **J-1 IS FAILED.  TEN OF TEN DRAWS ARE `RED`, AND THE GAP IS THE SMALLEST THIS CAMPAIGN HAS MEASURED.**

**CONTROL — record `37671cea92a6ce01…`, distribution `a085cff58fc8b343…`,
`worst-of-5@seeds{1,2,3,4,5}` = 30.06 MHz**

| seed | Fmax | worst setup | core `SAME` T_min | ALMs | binding cone |
|---|---:|---:|---:|---:|---|
| 1 | 30.95 | −1.059 | 32.309 | 8,142 (19 %) | `ram_block1a3~PORT_A_WRITE_ENABLE_REG → ram_block1a2~porta_address_reg10` |
| **2** | **30.06** | **−2.012** | **33.262** | 8,147 | `ram_block1a6~PORT_A_WRITE_ENABLE_REG → upc_page[0]` |
| 3 | 30.33 | −1.716 | 32.966 | 8,152 | `ram_block1a5~PORT_A_WRITE_ENABLE_REG → ram_block1a0~porta_address_reg5` |
| 4 | 30.48 | −1.554 | 32.804 | 8,136 | `ram_block1a0~PORT_A_WRITE_ENABLE_REG → ram_block1a4~porta_address_reg2` |
| 5 | 30.57 | −1.459 | 32.709 | 8,113 | `ram_block1a5~PORT_A_WRITE_ENABLE_REG → ram_block1a7~porta_address_reg2` |

> worst **30.06** · median 30.48 · best 30.95 · **spread 0.89**

**RETENTION — record `384a3606d47993ed…`, distribution `ca1ded8ad010892a…`,
`worst-of-5` = 31.17 MHz**

| seed | Fmax | worst setup | core `SAME` T_min | ALMs | binding cone |
|---|---:|---:|---:|---:|---|
| 1 | 31.66 | **−0.340** | 31.590 | 8,236 (20 %) | `ram_block1a0~PORT_A_WRITE_ENABLE_REG → ram_block1a2~porta_address_reg8` |
| 2 | 31.52 | −0.479 | 31.729 | 8,218 | `ram_block1a5~… → ram_block1a2~porta_address_reg12` |
| 3 | 31.62 | −0.371 | 31.621 | 8,243 | `ram_block1a7~… → ram_block1a3~porta_address_reg2` |
| 4 | 31.21 | −0.787 | 32.037 | 8,228 | `ram_block1a1~… → ram_block1a3~porta_address_reg2` |
| **5** | **31.17** | **−0.834** | **32.084** | 8,223 | `ram_block1a5~… → ram_block1a6~porta_address_reg4` |

> worst **31.17** · median 31.52 · best 31.66 · **spread 0.49**

E2 (0 errors, every stage Successful) **PASSES on all ten**; E3, E4 and E5 fail
together on all ten, which is one failure reported three ways and not three.
E7 `n_moved` 1 / `moved_offending` 0, E8 5/5 seeds honoured, E10 N = 5 on both.
`input_manifest` **`2d9117d4fcd7d218…` / 99 files, IDENTICAL between the two
configurations** and **DIFFERENT from J-8's `9f52ae11123b93fb…`** — which is the
check that edit (c) reached the compiler and that the two configurations differ
by the `--verilog_macro` and nothing else.

### 4.2 **THE SCOREBOARD — THE GAP FELL BY HALF AGAIN, AND IT IS STILL A GAP**

> | | WAVE 7 (the flat chain alone) | **WAVE 9 (+ the phase split)** | move | **GAP to 32.0** |
> |---|---:|---:|---:|---:|
> | **CONTROL, no exception, `worst-of-5`** | 28.32 | **30.06** | **+1.74** | 3.68 → **1.94** |
> | **RETENTION, no exception, `worst-of-5`** | 28.90 | **31.17** | **+2.27** | 3.10 → **0.83** |
>
> **AND THE WHOLE ARC OF THE CAMPAIGN**, against WAVE 3 / L2's pre-flattening
> no-exception baseline of **22.18 / 22.16**: **+7.88 MHz (CONTROL) and
> +9.01 MHz (RETENTION)**, gap **9.82 → 1.94** and **9.84 → 0.83**.
>
> **RETENTION seed 1 misses the bar by 0.340 ns of setup.**  It is still a MISS.

⚠ **AND IT IS A MISS ON EVERY DRAW OF BOTH CONFIGURATIONS, WHICH IS WHAT J-1
ASKED.**  `standing_gates.md` §A governs: one green build is not closure, and
the converse is also true — ten red draws on two configurations, with a spread
of 0.89 and 0.49, is a distribution that does not reach 32.0, not a run of bad
luck.  **No bar was softened and the cut was not re-scoped after the result.**

### 4.3 J-2 — **THE EXCEPTION IS GONE AND IT IS CHECKED, THREE WAYS, ON ALL TEN DRAWS.  MET.**

1. **`hdl/nec_test.sdc` carries ZERO uncommented `set_multicycle_path` and ZERO
   `set_false_path`.**  Two matches survive in the file and both are inside the
   deletion banner's historical quotation of the lines that were removed.
2. **No *"CE multicycle"* info line.**  The `post_message` now reads
   *"NO ce->ce exception — N ce-gated v30u core registers are checked
   SINGLE-CYCLE"*, and it is in every one of the ten fitter logs.
3. **Every receipt's `core_domain` reports `SAME` at k = 1.0 against a nominal
   of 1.0, with an EMPTY `off_class`, on 10 of 10.**  The nominal fell with the
   constraint (edit (c) moves `nominal["SAME"]` 2.0 → 1.0), so a draw still
   fitted to the exception would land in `off_class` and be reported.  None did.
   J-8's ten draws read the mirror image — `SAME` k = 2.0 against a nominal of
   2.0, `off_class` empty — which is how the same field distinguishes the two
   legs rather than merely decorating both.

⚠ **THE POLARITY DIFFERS FROM WAVE 7's AND THAT IS DELIBERATE.**  WAVE 7 deleted
the exception TEMPORARILY and left the nominal at 2.0, so its proof was
`off_class == ['SAME']` at k = 1.0.  This is a landing attempt, so the nominal
falls with the constraint and a conforming draw reports EMPTY.  **The two forms
carry the same information in opposite polarity; a reader comparing the two
`off_class` fields across waves without reading the nominal will draw the
opposite conclusion from the right data.**

---

## §5 J-3(b) / J-9 — **THE DIAGNOSIS.  THE CUT WORKS, BOTH STAGES FIT, AND WHAT BINDS IS AN ARC THAT LEAVES THE MODULE THE CUT SET IS DEFINED ON.**

A fresh CONTROL map + fit at the **worst CONTROL draw, seed 2** (`--recompile=off`,
its own `quartus_map`, `hdl/nec_test_ucore.qsf` restored either side), then
`sw/sta_cutset_diag.tcl`, `sw/sta_cutset_dump.tcl` and two new probes.
Artifacts `sw/testdata/wave9/diag_ctl_seed2.{txt,arrivalpoints.txt,controls.txt,biucensus.txt}`.

⚠ **IT IS A PROBE AND NOT A GATE**: it writes no receipt and **no Fmax is quoted
from it.**  The quotable figures are §4's.

### 5.1 ⚠⚠ **THE STOCK DIAGNOSTIC'S OWN POSITIVE CONTROL FAILED, AND THE FAILURE IS DIAGNOSED TO THE PIN**

`sta_cutset_diag.tcl` printed

```
  positive control: -through the destination's own D pin resolves 0 pin(s)
```

WAVE 4's read *"paths returned: 1"*.  **An instrument whose control cannot say
YES cannot be trusted when it says NO**, so the NO it reported — J-3(b)'s count
— was **not quotable until a control passed.**  `sw/sta_cutset_diag_pc.tcl`
(new) supplies four, and the cause is measured rather than guessed:

| control | reads | must read |
|---|---|---|
| **PC-1** the SAME `string first "\|s1q"` scan on a path that **LAUNCHES FROM** the shadow | **4 of 69** name `\|s1q` | **> 0** |
| **PC-2** …on a path that **LANDS ON** the shadow | **2 of 49** | **> 0** |
| **PC-3a** `-through {…\|upc_page[0]\|d*}` — WAVE 4's form | **0 pin(s)** | — |
| **PC-3b** `-through {…\|upc_page[0]\|asdata*}` | **2 pin(s), 1 path** | **1** |
| **PC-4** WAVE 4's `d` form on a destination that has one (`s1q[726]`), SAME netlist | **1 pin, 1 path** | **1** |

> **THE CAUSE: the binding path's last arrival point is `…\|upc_page[0]\|asdata`,
> not `\|d`.  `upc_page[0]` is a SYNCHRONOUS-LOAD register and is written through
> its SECONDARY DATA port, so the pattern `"${to}\|d*"` names a pin that does not
> exist on this destination.**  WAVE 4's destination (`opc_base[3]`) was a plain
> `d`-loaded flop and its control passed **for that reason and not because the
> probe was general** — PC-4 shows the same form still working on this netlist.
> **The instrument was destination-shaped and nobody knew.**  It is the same
> family as WAVE 4 §6.1's three: an instrument that can only say NO.

**With PC-1 and PC-2 passing, the classifier is demonstrated able to say YES,
and the NO below is a finding.**

### 5.2 **J-3(b) — MISSED, AND IT IS 0 OF 200 WHOLE PATHS, NOT 0 OF 79 ARRIVAL POINTS**

| | WAVE 2 | WAVE 4 (first) | WAVE 4 (A-1) | **WAVE 9** |
|---|---:|---:|---:|---:|
| arrival points on the binding path naming `\|s1q` | 0 of 103 | 0 of 107 | 0 of 107 | **0 of 79** |
| top-200 `ce → ce` paths naming `\|s1q` **anywhere** | — | — | — | **0 of 200** |

**J-3(b) IS MISSED FOR THE THIRD TIME**, and this wave measured it on a
strictly WEAKER question than the registered one — *does the shadow appear
ANYWHERE on the path*, not *is it an endpoint* — with the classifier's ability
to say YES demonstrated twice.  **0 of 200 is the strongest available form of
the answer.**

### 5.3 ⚠⚠ **AND THE REASON IS NOT WAVE 4's.  BOTH STAGES FIT.**

| | WAVE 4 + A-1 | **WAVE 9** | budget |
|---|---:|---:|---:|
| `\$v30u_ce` | 2,512 | **2,792** | |
| shadow bits surviving synthesis | 668 of 778 | **633 of 778** | |
| **STAGE 1** (`* → s1q`) worst | +8.071, 19 lv, **21.556 ns** | **+9.357, 16 lv, 20.235 ns** (T_min 21.893 → **45.68 MHz**) | 31.25 ns |
| **STAGE 2** (`s1q → *`) worst | **−6.633, 40 lv, 37.224 ns** | **+2.670, 26 lv, 27.922 ns** (T_min 28.580 → **34.99 MHz**) | 31.25 ns |
| **worst `ce → ce`** | −11.309, 45 lv, 41.302 ns | **−2.012, 31 lv, 31.959 ns** (T_min 33.262 → 30.06 MHz) | |
| top-200: STAGE 1 / STAGE 2 / **NEITHER** | 0 / 0 / **200** | 0 / 0 / **200** | |

> ### **WAVE 4's ANSWER WAS *"THE DOWNSTREAM HALF IS 6.0 ns OVER BUDGET BY ITSELF — 26.86 MHz — SO NO CHOICE OF CROSSING SET CAN CLOSE THIS DESIGN."*  ON THIS TREE STAGE 2 IS `+2.670 ns OF SLACK` AND `34.99 MHz`.  **THAT SENTENCE IS RETIRED BY MEASUREMENT.**  WAVE 7's chain flattening fixed precisely the thing WAVE 4 named as unfixable, and the phase split's OWN CEILING on this tree — `max(STAGE 1, STAGE 2)` — is **34.99 MHz, ABOVE THE 32.0 BAR.**

**THE MECHANISM WOULD NOW DELIVER.  IT IS BLOCKED BY AN ARC IT DOES NOT TOUCH.**

### 5.4 **J-9's THIRD CLASS EXISTS, AND THIS TIME IT IS THE WHOLE POPULATION**

J-9 registered the third class — a `ce → ce` path that neither ends at the
shadow nor launches from it — as *"it must not exist; if it does, name it."*
**It exists, it is 200 of 200, and the arrival-point dump names it to the node**
(`sw/testdata/wave9/diag_ctl_seed2.arrivalpoints.txt`, 79 lines):

```
  ucdecode M10K ~PORT_A_WRITE_ENABLE_REG        9.238
    -> portadataout[0] -> ucrom~796/461/114/118 -> r_farjmp~0
    -> s1_bus[207]~25 -> comb~19 -> Mux277~12/3/7 -> ind_now[0]~25
    -> s1_bus[111]~59 -> s1_bus[103]                              20.792
    -> u_biu|q_cnt~2 -> u_biu|Add46~0                                       <<< LEAVES THE EU
    -> u_biu|q_ripe_lead_n~0 -> u_biu|q_ripe_lead_n~5              24.045
    -> Mux354~9 -> Mux358~12 -> always6~63 -> stop~3                        <<< AND COMES BACK
    -> st_n~14 -> ld_b_n~7 -> Ram9~5 -> st_n~17_Duplicate x2
    -> ld_hasrm_n~2_Duplicate -> always6~30_Duplicate -> st_n~19_Duplicate
    -> dec_addr_next[10]~66/~69 -> upc_page[0]|asdata              41.197
```

**`sw/sta_cutset_biu_census.tcl` (new) asks the whole population, with the
known-wrong type-prefix form printed beside the instance-name form as its
negative control:**

| | |
|---|---:|
| **PC-A** `\|u_biu\|` nodes on the binding path (must be > 0) | **1** ✓ |
| **PC-B** the KNOWN-WRONG `v30u_biu:` type-prefix form, same path (must be 0) | **0** ✓ |
| paths scanned | 200 |
| **…launching inside the microcode ROM** | **200 / 200** |
| **…carrying the EU → BIU → EU combinational round trip** | **200 / 200** |
| **…carrying `q_ripe_lead_n` BY NAME** | **200 / 200** |
| …naming the shadow `\|s1q` anywhere | **0 / 200** |
| **mean span of the round trip when present** | **2.786 ns** |

> ### **THE BINDING CLASS IS ONE SHAPE, ON 200 OF 200 PATHS: `ucdecode M10K → the EU's stage-1 logic → the EU's LIVE combinational output → the BIU's `q_cnt` / `q_ripe_lead_n` cone → back into the EU's chain → `dec_addr_next` → the ROM's own address register.`**
>
> **A CUT SET INSIDE `v30u_eu.sv` CANNOT DIVIDE IT, BECAUSE ITS MIDPOINT IS
> OUTSIDE `v30u_eu`** — and no lint about `v30u_eu.sv`'s own names can see it.
> It is `r7_lint`'s own **DECLARED UNRESOLVED CARRIER `q_ripe_lead_n`**, declared
> and known since §73, and **WAVE 4 §4.1 named this exact arc as "the next cut"**
> — then measured that cutting it would not have been enough, because STAGE 2 was
> 37.224 ns.  **STAGE 2 IS NOW 27.922 ns, SO THE SAME ARC IS NOW THE WHOLE
> REMAINING GAP.**

**AND THE ARITHMETIC SAYS IT COVERS THE GAP.**  CONTROL's worst draw misses by
**2.012 ns** (T_min 33.262 against the 31.250 ns budget); RETENTION's by
**0.834 ns**.  **The round trip is 2.786 ns.**  Nothing here says removing it
recovers its own span — WAVE 5's law is that a cut GROWS an arc, and WAVE 8 §7.6
measured that an ATTRIBUTED SHARE of an uncut arc is not a difference and does
not transfer (5.9× overstatement there).  **This is a POINTER, not a prediction,
and it is written as one.**

⚠ **AND IT CONTRADICTS WAVE 8 §4, LOUDLY, AND THIS WAVE DOES NOT EXPLAIN IT.**
WAVE 8 measured this same round trip at **0.000 ns on 0 of 1,200 CONTROL
endpoint-diverse paths** and concluded *"it is not a candidate"* — while its ONE
RETENTION draw carried it on 400 of 400 at 1.894 ns, and it called that
all-or-nothing pattern a placement outcome it could not attribute with one draw.
**Here it is on 200 of 200 CONTROL paths at 2.786 ns.**  Two differences are
confounded — WAVE 8 measured the UNCUT tree and this is the CUT tree, and this
is ONE seed against WAVE 8's three — so **no attribution is made.  It is
recorded, it is the strongest pointer the wave has, and the confound is stated
rather than resolved.**

### 5.5 **THE GROWTH — WAVE 5's LAW REPRODUCED TO 0.11 ns ACROSS A TREE CHANGE THAT MOVED THE ARC BY 10.5 ns**

WAVE 5 established that **a cut does not divide an arc, it GROWS it.**  J-9
registered the arithmetic to be reported whatever the outcome.

| | uncut arc | STAGE 1 | STAGE 2 | Σ stages | **GROWTH** |
|---|---:|---:|---:|---:|---:|
| **WAVE 4** (unrolled chain) | 43.485 | 21.556 | 37.224 | 58.780 | **+15.295 ns (+35.2 %)** |
| **WAVE 9** (flattened chain) | **32.969** ⧉ | **20.235** | **27.922** | **48.157** | **+15.188 ns (+46.1 %)** |

⧉ WAVE 8 §3.1, mean of 4 draws (32.549 · 33.669 · 32.744 · 32.916, spread 1.120).

> ### **THE ABSOLUTE GROWTH IS +15.19 ns HERE AND +15.30 ns THERE — 0.11 ns APART — ACROSS A TREE CHANGE THAT SHORTENED THE UNCUT ARC BY 10.5 ns AND A CHAIN REWRITE THAT DELETED SEVEN COPIES OF A 33-ARM CASE.**
>
> **THE CUTTING PENALTY IS A CONSTANT OF THIS DESIGN, NOT A FRACTION OF THE
> ARC.**  That is a transferable finding and it is the thing a future wave should
> budget with: **halving an arc of length *L* by this cut buys
> `L − (L/2 + 15.2)` only while `L > 30.4 ns`,** and *L* is now 33.0.

⚠ **AND THE THIRD CLASS DID NOT GROW.**  The binding `ce → ce` arc measures
**31.959 ns** against WAVE 8's uncut **32.969** — it is the SAME LOOP, essentially
unmoved (−1.01 ns), because the cut set does not lie on it.  **That is the whole
story of this wave in one comparison: the cut divided everything it could reach,
and what binds is what it could not.**

---

## §6 J-10 — NON-VACUITY

`sw/cutset_nonvacuity.py` on the cut tree.  Each case constructs its condition by
a temporary patch, rebuilds where it must, runs the thing that must complain, and
reverts with `git checkout --`.  **`hdl/ restored: CLEAN`.**

| case | probe | result |
|---|---|---|
| **A** the shadow is LOAD-BEARING | `} = s1q ^ 778'd1` in front of `check_core --opcodes 90 --cases 5` | ⚠ **DID NOT FIRE — 5/5.**  **Reported as a MISS, not replaced.**  The concatenation's LSB is its LAST member and that is `it_writes_tmpa`; **`90` is a NOP and exercises no iterative step**, so the bit is genuinely dead on that leg.  **WAVE 4 measured the identical miss for the identical reason** and this wave re-measured rather than inherited it |
| **A2** the SAME one bit, wider population | the same perturbation in front of `check_core --opcodes all --cases 0` | **FIRED** (`first-div:`).  A NAMED GATE LEG — the 169,000-case ratchet — breaks on one perturbed bit of 778 |
| **B** the lint fires on a re-introduced bypass | `s1w_row_bus` spliced back into `v30u_eu_step.svh` — WAVE 2's exact defect | **X2 AND X4 FIRE**, `cutset_lint: FAIL` |
| **B2** …on a bypass no `s1w_` prefix betrays | a read of `sigma`, a module wire never in the cut set | **X4 FIRES** — X2 cannot, by construction, which is what shows X4 is not a restatement of X2 |
| **B3** ⚠ **WAVE 9's OWN — …on a bypass in an ARM FILE** | `sigma` spliced into `v30u_eu_arm_decode2.svh` | **X4 FIRES**, `cutset_lint: FAIL` |
| **C** S-1's `$fatal` names the EU | `ce_half <= 1'b0` in the TB | **FIRES**, and the message contains **"STAGE-1 capture edge"** |

**ALL THREE OF J-10's REGISTERED CLAUSES ARE MET**: the lint fires on a
re-introduced bypass (B, B2, **B3**), the shadow is load-bearing — perturbing one
bit breaks a named gate leg (**A2**) — and S-1's `$fatal` fires naming the EU's
dependence (**C**).  **The suite's own exit code is 1 because case A missed**,
and that is reported here exactly as it is: a narrower probe of a clause another
probe satisfies, whose miss has a measured structural cause.

### 6.1 ⚠⚠ **B3 IS THE CASE THAT MATTERED, AND WITHOUT IT THIS WAVE'S LINT WOULD HAVE PASSED VACUOUSLY**

`cutset_lint`'s include set was **NINE HARD-CODED FILENAMES** in WAVE 4.  **WAVE 7
moved the nine chainable arm bodies out of `v30u_eu_step.svh` into
`v30u_eu_arm_<state>.svh`** — files that list does not name.  On the flattened
tree, X2 and X4 would have **scanned right past the chain body** and returned
`PASS — 0 violations` while the chain could name any pre-cut wire it liked.  The
port (`451bbf26c5`, committed before the pre-registration) makes the set the
**transitive closure of the block's own `` `include ``s** — it now closes **19
files** — and **B3 is that port's own falsifier.**  It is the eleventh
incarnation of the vacuous-gate pattern this repo has caught, and it was caught
by asking the instrument to say NO.

---

## §7 THE VERDICT TABLE, SCORED AS REGISTERED

| bar | verdict |
|---|---|
| **J-1** the requirement (`--seeds 5`, E1-E5 every draw, BOTH configurations, no exception) | **FAILED — `RED` on 10 of 10 draws.**  CONTROL `worst-of-5` **30.06**, RETENTION **31.17**.  §4 |
| **J-2** the exception is GONE and it is CHECKED | **MET** — zero uncommented `set_multicycle_path` / `set_false_path`, no *"CE multicycle"* info line, and **every one of the ten receipts reports `SAME` at k = 1.0 against a nominal of 1.0 with an EMPTY `off_class`**.  §4.3 |
| **J-3(a)** the cut set is complete BY CONSTRUCTION; lint passes and is demonstrated FIRING | **MET** — `cutset_lint: PASS (80 members / 0 violations)`, `phase_split_lint: PASS (156 members / 778 bits / 0 violations)`, and **three different kinds of re-introduced bypass make it FAIL** (§6, B / B2 / **B3**) |
| **J-3(b)** on a no-exception fit the binding path's arrival points DO name the shadow | **MISSED — 0 of 79 arrival points, and 0 of the top 200 paths name it ANYWHERE**, against WAVE 4's 0 of 107 (twice) and WAVE 2's 0 of 103.  **Measured with the classifier demonstrated able to say YES (PC-1 4 of 69, PC-2 2 of 49), after the stock control was found unable to.**  §5.1-5.2 |
| **J-4** pin identity | **MET** — `chain_lfsr_gate` 4 of 4 signatures and every census BYTE-IDENTICAL; `fz2_replay` scored-content sha256 IDENTICAL over 305 rows.  COORDINATOR-VERIFIED, re-verified here.  ⚠ one ERRATUM against the handoff's quoted digest, §2 |
| **J-5** the ladder at its registered values | **MET** — **29 SAME / 2 MOVED / 0 MISSING**, both movers registered in advance and neither a measurement.  COORDINATOR-VERIFIED, re-verified here.  §2 |
| **J-6** save state does not move | **MET** — `SS_VERSION` 0x8F / `SS_COUNT` 232 / `SS_TAG` 0x8FE8 / 0 UNMAPPED, ALL UNCHANGED; `v30u_ss_pkg.sv` untouched; whitelist 3 → **4**, grown by **exactly the shadow's one entry** |
| **J-7** divisor independence | **MET** — 169,000/169,000 at `--ce-div` 2, 3, 4 and 8; `--ce-div 1` REFUSED, clause cited |
| **J-8** no regression WITH the exception | **MET** — 10 of 10 PASS, `worst-of-5` CONTROL **41.69** / RETENTION **42.38** against WAVE 7's **41.06**.  §3 |
| **J-9** the arithmetic, reported whatever the outcome | **DELIVERED, AND IT IS THE WAVE'S PRODUCT.**  STAGE 1 **20.235**, STAGE 2 **27.922**, the third class **31.959** and **200 of 200**; growth **+15.188 ns** against WAVE 4's **+15.295**.  §5 |
| **J-10** non-vacuity | **MET on all three registered clauses** (A2 · B/B2/B3 · C).  **A MISSED and is reported as MISSED**, as WAVE 4's did, for the same measured reason.  §6 |
| **J-11** the revert condition | **TRIGGERED.**  §8 |

---

## §8 J-11 — **THE REVERT, AND THE GAP**

J-11 is unambiguous: *"If J-1 fails … THE LANDING DOES NOT HAPPEN.  Revert,
report, keep both documents.  Do not soften a bar to make a landing possible and
do not re-scope the cut after seeing a result.  Report the GAP to 32.0
explicitly either way."*

> ### **THE GAP IS 1.94 MHz (CONTROL) AND 0.83 MHz (RETENTION).**
>
> **RETENTION's best draw misses the bar by 0.340 ns of setup.**

**No bar was softened.  The cut was not re-scoped after a result.  Nothing was
flashed and no board was touched.**  Edits (a) `6e822bf750`, (b) `5cf3254104`
and (c) `bacf7f9fd9` are reverted; both documents are kept; every artifact is
retained.

### 8.1 WHAT THIS WAVE ESTABLISHED, AND IT IS NOT NOTHING

1. **WAVE 4's REFUTATION IS RETIRED BY MEASUREMENT.**  It said the downstream
   half was **37.224 ns = 26.86 MHz**, 6.0 ns over budget by itself, and that
   *"a `ce`/`ce_half` split cannot deliver 32 MHz on this design however the
   crossing set is drawn."*  On the flattened tree **STAGE 2 is 27.922 ns with
   +2.670 ns of slack**, and **the split's own ceiling is 34.99 MHz — above the
   bar.**  The mechanism is no longer the wall.
2. **THE WALL IS NAMED, TO THE NODE, ON 200 OF 200 PATHS**: the EU → BIU → EU
   combinational round trip through `q_cnt` → **`q_ripe_lead_n`**, `r7_lint`'s
   own declared UNRESOLVED carrier, **2.786 ns**, against a shortfall of
   **2.012 ns (CONTROL) / 0.834 ns (RETENTION)**.  **A cut set inside
   `v30u_eu.sv` cannot divide it because its midpoint is outside `v30u_eu`.**
3. **THE CUTTING PENALTY IS A CONSTANT OF THIS DESIGN**: **+15.19 ns** here,
   **+15.30 ns** in WAVE 4, across a tree change that shortened the uncut arc by
   10.5 ns.  A future wave can budget with that number.
4. **THE SPLIT IS BIT-EXACT AT 778 BITS** over 169,000 goldens at four divisors,
   17,350 `ulockstep` scenarios, 1.6 M `chain_lfsr` clocks byte-identical, 305
   `fz2_replay` rows sha256-identical — **with the phase-stability premise
   `$fatal`-asserted every `ce` and never once violated**, and `SS_COUNT`,
   `SS_VERSION` and `SS_TAG` unmoved.
5. **TWO MORE INSTRUMENTS WERE MADE TO SAY NO** — `cutset_lint`'s hard-coded
   include list (would have passed VACUOUSLY on every tree from WAVE 7 onward;
   ported before the pre-registration, falsified by **B3**) and
   `sta_cutset_diag.tcl`'s destination-shaped `-through` positive control
   (**diagnosed to the `asdata` pin**, repaired in a new file with the wrong form
   kept printed beside it).  **That is eight and nine in this campaign's running
   count, and every one was caught by a positive control.**

### 8.2 THE NUMBERS THAT MAY BE QUOTED FROM THIS WAVE

**CONTROL no-exception `worst-of-5` 30.06 MHz** (`37671cea92a6ce01…`),
**RETENTION 31.17** (`384a3606d47993ed…`), **J-8's 41.69 / 42.38**
(`9d6fe1ba48918e81…` / `872d210583d40382…`), **STAGE 1 20.235 ns**, **STAGE 2
27.922 ns**, **the round trip 2.786 ns on 200 of 200**.

⚠ **AND THE ONE THAT MAY NOT.**  `standing_gates.md` §A governs every timing
figure: the same tree has drawn 19.42 and 45.91 MHz, and **one green build is
not closure — which cuts both ways, so these ten RED draws are not a proof that
no phase split can close, only that these did not on these draws.**  What makes
them strong is not the count but §5.3-5.4: **both stages' lengths and endpoints
are structural, the binding class is one shape on 200 of 200 paths, and the BIU
is on it by counting rather than by reading.**

### 8.3 WHAT IS OWED

1. ⚠ **A FABRIC CONFIRMATION HAS BEEN OWED SINCE WAVE 7 AND IS NOT DISCHARGED.**
   WAVE 7 changed the EU's decode and nothing since has been on a board.
   **NO FABRIC FIGURE TAKEN ON FLASH #21 OR EARLIER MAY BE QUOTED AGAINST THIS
   TREE.**  This wave reverts, so nothing new is owed *for it*.
2. **THE NEXT MECHANISM IS NAMED AND IT IS NOT A PHASE SPLIT**: break the
   EU → BIU → EU combinational round trip through `q_ripe_lead_n`.  WAVE 4 §4.1
   named it and measured that closing it would not have been enough; **that is no
   longer true.**  Its declared-unresolved status in `r7_lint` is the place to
   start, and **`sw/sta_cutset_biu_census.tcl` is the instrument that scores it.**
3. **`sw/sta_cutset_diag.tcl`'s `-through` control is still destination-shaped
   in the file itself** — `sw/sta_cutset_diag_pc.tcl` supplies the repaired form
   beside it rather than editing a reverted wave's retained instrument.
   **BOOKED**, and named so the next reader does not lose an hour.
4. **`standing_gates.md` §B still carries two stale ucore rows** (`test_quartus_gate`
   at line 494, and an `ss_lint` row that is `fuzz-v2-on-relanding`'s and not
   `master`'s).  WAVE 2, WAVE 3 and WAVE 4 each booked this.  **BOOKED for the
   fourth time**, and the repetition is itself worth noticing.
5. **`check_core --ss-sweep` IS STILL NOT ON ANY REGISTERED LADDER.**  Booked by
   WAVE 2, WAVE 3 and WAVE 4; **not run here either.**  The resume path is the one
   place the shadow's derivation is not covered by the runtime assert, which
   excludes `ss_we` by construction.  **BOOKED for the fourth time.**

### 8.4 THE REVERT IS MEASURED, NOT ASSERTED — `cbb556a097`

* **`git diff cf43e65cb3 -- hdl/` is EMPTY.**  `hdl/` is BYTE-IDENTICAL to the
  tree this wave entered on; `hdl/rtl/ucore/v30u_eu_preload.svh` is deleted.
  The same diff over `sw/quartus_gate.py`, `sw/sta_truefmax_probe.tcl`,
  `sw/test_quartus_gate.py`, `sw/demux_off_gate.py` and
  `sw/ss_flop_whitelist_ucore.txt` is **EMPTY** too.
* **THE THREE INSTRUMENTS OF `451bbf26c5` ARE DELIBERATELY NOT REVERTED** —
  `sw/cutset_census.py`, `sw/cutset_lint.py`, `sw/phase_split_width.py`.  They
  are the ONLY files still differing from `cf43e65cb3`, they touch no `hdl/`
  file, and the include-list repair they carry is what stopped `cutset_lint`
  passing vacuously on every tree from WAVE 7 onward (§6.1).
  `sw/sta_cutset_diag_pc.tcl` and `sw/sta_cutset_biu_census.tcl` are kept for the
  same reason — **the second is the instrument that scores the next mechanism.**
* **BOTH LINTS REFUSE**: `sw/cutset_lint.py` and `sw/phase_split_lint.py` each
  exit **2, COULD NOT RUN**, naming the absent mechanism.  Neither is registered
  in `standing_gates.md`, for the reason WAVE 2 and WAVE 4 gave: **a lint that
  PASSED here would pass vacuously.**
* **MEASURED BACK AT THEIR REGISTERED VALUES ON THE REVERTED TREE**: `r7_lint`
  **PASS** (0 undeclared carriers / 0 undeclared unresolved / 0 `stop` sites) ·
  `ss_lint` **PASS**, `ss_flopcensus` **228** architectural flops and **3**
  whitelist entries — *the shadow's entry is gone and it is the only one that
  went* · `test_quartus_gate` **255 / 255**.  **The functional ladder is not
  re-run**: `hdl/` is byte-identical to `cf43e65cb3`, which is a stronger
  statement than re-measuring it, and `sw/testdata/wave9/before/` already holds
  that tree's column leg for leg.
* `sw/cutset_nonvacuity.py` on the reverted tree: **A / A2 / B / B2 / B3
  SKIPPED**, said to be, and said WHY (*"probe a mechanism that is not here"*);
  **C FIRES on `REQUIREMENT VIOLATED (S-1)`** and **DOES NOT** contain
  *"STAGE-1 capture edge"* — ⚠ **correctly**, because that wording came with
  edit (a) and went with it, and on a tree with no phase split the EU has no
  stage-1 dependence to name.  **WAVE 4 measured the identical behaviour on its
  own reverted tree and this reproduces it.**  `hdl/ restored: CLEAN`.
* **`git add -A` WAS NEVER USED.**  The ~18 pre-existing modified files (a
  repo-wide hard-coded-path rename in flight, plus the three **append-only**
  ledgers under `sw/testdata/receipts/`) are untouched, and the twelve
  pre-existing untracked `hdl/quartus_gate_*.log` files are still untracked.
  ⚠ **This wave adds two more of that same class** —
  `hdl/quartus_gate_w9_noexc_{control,retention}.log` — **left untracked, like
  the twelve, and named here rather than left to be discovered.**
  ⚠ **The receipt ledgers carry this wave's appends and are DELIBERATELY LEFT
  UNCOMMITTED**, because they were already modified at entry; every receipt id
  quoted above is also present in the committed per-seed receipts under
  `sw/testdata/g6dist/`, so nothing is unquotable for want of them.
* `hdl/nec_test_ucore.qsf` moved during every Quartus run — the declared §70.7
  exemption, E7's single permitted mover — and was restored with
  `git checkout --` after each.  **Recorded because a file that moves and is put
  back is still a file that moved**, and because failing to put it back cost
  WAVE 4 a whole sweep.


Claude-Session: https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5
