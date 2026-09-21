# WAVE 27 — RESULTS.  **`tests/v30/v0.2` IS REMOVED, AND IT IS THE FIRST THING THIS REPO HAS DELETED THAT `git checkout` CANNOT BRING BACK.**

**USER INSTRUCTION 2026-09-21, verbatim: *"Remove v0.2, v0.3 supersedes it"***.

Offline.  **No `hdl/` edit of any kind.  No Quartus.  No board.  No flash.**
The tree's WAVE 26 re-flash debt is unchanged and undischarged.
Session `https://claude.ai/code/session_01AZih22iifLegfB9mxcLZA5`.

**THE REGISTER ENTRY IS `docs/notes/invalidation_ledger.md` RET-3 AND IT OWNS
EVERY MEASUREMENT.**  This document is the index and the scorecard; where a
number appears in both, RET-3 is the authority.

---

## §1  THE HEADLINE

| | |
|---|---|
| **what went** | `tests/v30/v0.2/` — **352 files, 91,237,482 bytes**, the 1,000-cases × 347-form socket emission of 2026-07-17 |
| ⚠ **what was in git** | **ONE file, 144 bytes** — `.gitignore`, whose whole content is `*` plus `!.gitignore`.  **The other 351 files, 91,237,338 bytes, were in no commit, branch or reflog and are GONE** |
| **what `v0.3` reproduces** | **339,873 of the 347,000 BYTE FOR BYTE at the same index** |
| **what it does not** | **7,127 (2.0539 %) in 12 forms** — **preserved, tracked, committed BEFORE the first deletion** |
| **reroll or different draw?** | **BOTH, MEASURED**: **5,890** are elsewhere in `v0.3` byte-identical · **1,152** are the same seed attempt drawn differently · **85** are seed attempts `v0.3`'s generator rerolled away |
| **form coverage** | **UNCHANGED.  All 347 `v0.2` forms exist in `v0.3` at ten times the case count.**  Not one form was lost |
| **gates that died** | **two ladder legs** (`v0.2` and `v0.2 --raw-flags`), enumerated in RET-3 with their last figures.  ⚠ **One is replaced by NOTHING** |
| **gates that broke** | **one — `suitemeta --selfcheck`** — and the grep did not find it.  §4 |
| ⚠ **unresolved** | `v0.3/README.md` says **7,137**; four independent keys say **7,127**, and the difference **cannot be re-derived because neither suite was ever in git** |

---

## §2  Z-1 … Z-8, SCORED

| bar | verdict | evidence |
|---|---|---|
| **Z-1** preserve the unique rows, tracked and committed, **before the first deletion** | **MET** | `f6bd939011` (7,127 records) and `d060ee28b7` (the five provenance files), both ancestors of the deletion commit `ad4bfb5ecf`.  `tests/v30/v02-unique-archive/`, 19 files, ~3.1 MB, `SHA256SUMS` + `manifest.json`.  ⚠ The 85 rejected are preserved **and flagged in the manifest**, as the bar requires |
| **Z-2** prove the rest is reproduced, by content hash, form by form, key stated | **MET** | `sw/testdata/wave27/z2_reproduction.txt` — **347/347 forms agree on BOTH a hash-list digest and a record-body digest**, computed on both sides; 339,873 reproduced.  Key: the record's own `hash` (§3) |
| **Z-3** remove the suite; report exact byte and file counts | **MET** | §1.  `git rm` took the one tracked file; `rm -rf` the rest.  Counted before deletion, not estimated |
| **Z-4** RET-3, in RET-1/RET-2's form, with the not-in-git fact stated plainly; leg removed from `standing_gates.md` and `CLAUDE.md` | **MET** | `invalidation_ledger.md` RET-3 (its § HOW TO RECOVER IT reads **YOU CANNOT**); `standing_gates.md` §W22 struck row; `CLAUDE.md` WAVE 27 banner |
| **Z-5** every consumer found and dispositioned, as a FLOOR | **MET — AND THE FLOOR WAS REAL** | `sw/testdata/wave27/z5_consumers.md`.  Every executable hit was **RUN on both sides of the deletion**.  §4 is what the grep missed |
| **Z-6** the ladder is zero-delta except the removed leg | **MET** | §5 |
| **Z-7** nothing in `hdl/`; no Quartus, board or flash | **MET** | `git diff --stat HEAD -- hdl/` **EMPTY**, verified at each commit |
| **Z-8** the user's 21 modified + untracked files untouched; no `stash`/`checkout .`/`reset --hard`; `git add` by explicit path; receipts unstaged | **MET** | None of those three commands was run at any point.  `git status` still shows the same **21 `M`** entries including `sw/testdata/receipts/*.jsonl` and **`tests/v30/v0.3/README.md`, which was NOT touched** |

---

## §3  THE MEASUREMENT, AND ITS COMPARISON KEY

**KEY**: the record's own `hash` field = `SHA1` of
`json.dumps([name,bytes,initial,final,cycles],separators=(",",":"))` — the whole
record except `idx`, which is a position label and not content.

**POSITIVE CONTROL**: at every one of the 339,873 positions where the two hashes
are equal, the two records were asserted **byte-identical modulo `idx`** —
**0 violations**.  Had the key not been a content key, that assertion fires.

**FOUR INDEPENDENT KEYS AGREE** (`sw/testdata/wave27/z1_keys.txt`): `hash`,
whole-record-including-`idx`, `initial` alone, and `name`+`bytes`+`initial` all
return **7,127**.  (`cycles` alone gives 6,830 and `name`+`bytes` 6,270; neither
is a whole-record key.)

### Reroll, or a different draw?

`emit_suite.py` draws case *i* of form *F* from seed attempts *k = 0,1,2,…* in
order, skipping any it rerolls and logging each.  So `out_idx → seed attempt` is
the ordered attempts minus the rerolled set, and both suites shipped the log.

> **POSITIVE CONTROL FOR THE RECONSTRUCTION.**  `v0.3` also ships the true map
> per form (`XX.seeds.json`).  Rebuilding it from `v0.3`'s **own** `emit_log`
> reproduces the committed map on **370 of 370 forms exactly**, and **107 of the
> 370 are non-identity maps**, so the equality is not trivial.

| class | n | meaning |
|---|---:|---|
| PRESENT IN `v0.3` AT ANOTHER INDEX | **5,890** | `v0.3` holds it byte for byte; a reroll shifted the index |
| ABSENT, `SAME_SEED_DIFFERENT_RECORD` | **1,152** | same seed attempt, different case — the emitter's placement logic moved |
| ABSENT, `REJECTED_BY_v0.3` | **85** | `v0.3`'s generator rerolled that seed attempt away |

**7,120 of the 7,127 lie in the nine interrupt/HALT forms** and are exactly the
positions where the two emissions used a **different seed attempt** (measured
independently on a seed-attempt key: **7,120**).  The other seven — `0F31` ×5,
`0F26`, `A6` — use the **same** attempt in both, so they are emitter evolution
with no reroll at all.

`v0.3`'s own reasons for the 85 (`z2_rejected_reasons.txt`, regenerable from the
archive alone, **exits non-zero if any of the 85 lacks a matching reroll line —
measured 0**): **`implausible final PSW` 45 · `pf assert before window` 37 ·
`no F pop from close addr` 3**.

⚠ **A SCOPING LIMIT**: `REJECTED_BY_v0.3` means *the SEED ATTEMPT was refused*,
not *this record was refused* — the two emissions build different cases from the
same seed, which the 1,152 demonstrate.

⚠ **AND A READING THIS WAVE REFUTED WITH ITS OWN CONTROL.**  Four spot-checked
rejected cases carried no `final.flags`, which looked like the store-stub
final-PSW capture defect `v0.3/README.md` says it fixed.  **The control kills
it**: `final.flags` is absent from **all 7,127** — rejected, same-seed and
shifted alike — because `final.regs` is sparse in this schema.  **Withdrawn, in
writing, in the archive README and in RET-3.**

### ⚠ The `7,127` vs `7,137` erratum — REPORTED, NOT RESOLVED

`v0.3/README.md` (written at `24d6d78573`) says **7,137**; no key tried
reproduces it.  **It cannot be re-derived, for this wave's own reason: neither
suite was ever in git.**  `v0.3/reemit.log` records five confined per-index
re-emissions, **two inside the compared prefix** (`36.6E` idx 517, `F26F` idx
743), and `v0.2_reemission_worklist.md` records a re-emission pass over `v0.2`;
either would move the figure by a few cases.
**RULED OUT: any drift between WAVE 22 and the deletion** — all 347 form files
and all four provenance files hash **identically** to WAVE 22's frozen manifest
`sw/testdata/wave22/manifest-v0.2.txt`, **347/347 and 4/4**.
⚠ `tests/v30/v0.3/README.md` is one of the **user's own modified files and was
not touched**; the erratum lives in RET-3.

---

## §4  Z-5 — **WHAT THE GREP MISSED, AND WHAT FOUND IT**

The mechanical pass found `sw/suitemeta.py`'s `("v0.2", EMITTER)` row, and the
obvious disposition — *delete it, `mod3_illegal` still reaches the `EMITTER`
dialect* — is **correct and not sufficient.**

`selfcheck`'s check (4) is the non-vacuity control: empty the delegation target
and demand that some mask MOVE.  It chose its probe as *the first delegating
suite in `CONTROL_SUITES` with forms on disk*.  That was `v0.2`, which happens
to carry **16 real (non-`0xFFFF`) masks**.  With the row gone the probe fell to
`mod3_illegal`, **whose single mask IS `0xFFFF`**, so emptying the target
changed nothing and the gate went **RED**:

```
NON-VACUOUS CONTROL DID NOT FIRE: an EMPTY delegation target left every
mod3_illegal mask equal to v0.1's, so check (3) proves nothing
suitemeta --selfcheck: FAIL -- 1 violation(s), 13 check(s) passed
```

**Nothing in the grep output pointed at check (4).  RUNNING THE TOOL AFTER THE
EDIT did**, which is why every executable hit in `z5_consumers.md` was run on
both sides rather than read.

**THE REPAIR STATES THE REQUIREMENT INSTEAD OF RELYING ON LIST ORDER**: the probe
is *a delegating suite with at least one non-`0xFFFF` mask*, and **if none is on
disk the gate records a violation rather than passing**.  Probe is now `v0.3`,
firing **16 of 370**.  **NEGATIVE CONTROL RUN**: restricted to `v0.1` +
`mod3_illegal` the selfcheck **exits 1**.

`suitemeta --selfcheck` now reads **PASS — 14 checks, 3 dialects reached, 0
skipped** (it was **17**; three were `v0.2`'s own rows).  **The `EMITTER` dialect
is NOT retired with the suite** and the dialect table is not edited.

**One other consumer would have lied quietly**: `sw/w26_consumer_census.py`
returns `(0, 0)` for a missing suite, so left alone it would have printed
`v0.2  8D cases 0  mod==3 0` — *"checked, and empty"* for a suite that does not
exist.  The drop is now **PRINTED** and the denominator reads 3.

---

## §5  Z-6 — THE LADDER

`sw/wave27_ladder.sh` — WAVE 26's leg set with the dead `v02` leg removed and
two added (`suitemeta`, `w27_archive`).  Compared leg by leg against
`sw/testdata/wave26/ladder/after/` by `sw/testdata/wave27/w27_ladder_cmp.py`,
which strips Verilator chatter, absolute paths, receipts and timings and
compares the **scored lines**.

**RESULT: 36 SAME · 0 MOVED · 1 GONE · 2 NEW.**  The one GONE is `v02` and
nothing else; the two NEW are `suitemeta` and `w27_archive`.
`sw/testdata/wave27/ladder_cmp.txt`, and every leg's raw log plus `rc.txt` (each
leg's own exit code, captured with no pipe between tool and capture) under
`sw/testdata/wave27/ladder/`.

| leg | measured | vs WAVE 26 |
|---|---|---|
| `v0.1` `--ce-div 4` / `2` / `3` / `8` | **169,000 / 169,000 full** on all four | SAME, 348 scored lines each |
| `v0.1` `--ce-div 1` | **REFUSED**, RC=2, citing **C-a** | SAME |
| HLT sweeps `--waits 0/1/2/3` | **97 · 93 · 45 · 44 = 279 / 283** | SAME |
| `v0.3` | **3,699,998 / 3,699,998 full [2 documented pre-existing excluded]** | SAME, 372 scored lines |
| `v20suite --arch-only` | **TOTAL ARCH: 3,125,000 / 3,125,000** | SAME, 361 scored lines |
| `mod3_illegal --opcodes goldens` | **0 / 128 full (cycles 128, arch 0)** — KNOWN-RED, expected | SAME |
| `v0.1-w1` / `-w3` / `w1 EB` / `f4a_boundary` / `f0lock_tranche` | **1,200 · 1,200 · 200 · 160 · 400** | SAME |
| `check_boot --core ucore` 220 / 400 | **MATCHES over 220 / 400 rows** | SAME |
| `check_ab_sim --core ucore` | **MATCHES CHIP BOOT over 187 rows** | SAME |
| `ghost_launch_law score` | **ALL THREE POPULATIONS 200/200 = 100.0 %** | SAME |
| `lea_mod3_gate` | **PASS** | SAME |
| `chainflat_relocation_check` | **PASS — 9 arms, one copy each, 7 byte-identical to `aba01feb07`, 2 DECLARED DEVIATIONS pinned by digest** (the **DEV-1** pin) | SAME |
| `chain_lfsr_gate` | **PASS — CHAIN_MAX 7, depth [6], 0 overflows**, and the **four signatures BYTE-IDENTICAL**: `1d01c9b269ffaa94` · `b39b040a98b28e5d` · `0997b773cd99c030` · `d05b6c3c3d9fbe78`, with every gap count and liveness row | SAME (whole log identical with build chatter stripped) |
| `demux_off_gate` | **PASS** | SAME |
| `r7_lint` | **PASS — 0 carriers, 0 unresolved, 0 `stop` sites** | SAME |
| `ss_lint --core ucore` | **PASS — 109×2 BIU + 122×2 EU + tag = 232**; census **229 flops, 4 whitelist, 0 UNMAPPED** | SAME |
| `cutset_lint` | **PASS — 81 members / 0 violations** | SAME |
| `phase_split_lint` | **PASS — 157 members / 779 bits / 0 violations** | SAME |
| `test_artifact` | **45 / 45** | SAME |
| `test_quartus_gate` | **302 / 302** | SAME |
| `qsf_lint --check` | **CANONICAL** | SAME |
| `core_portlist_lint` | **PASS, 4 configurations** | SAME |
| `ucrom_mif_check` | **PASS** | SAME |
| `check_ucore_tables` (G0) | **PASS — 9,988 entries byte-identical to the frozen reference, both legs** | SAME |
| `pla3_check` | **OK (21 checks)** | SAME |
| ~~`v0.2`~~ | — | ⚠ **GONE.  It was `347,000 / 347,000 full` and it is the leg this wave removed** |
| `suitemeta --selfcheck` | **PASS — 14 checks, 3 dialects reached, 0 skipped** | **NEW to the ladder** (it was 17 checks before the removal; §4) |
| `w27_v02_archive_check` | **PASS — 7,127 preserved records; 5,890 re-found in `v0.3` byte-identical; 1,237 confirmed absent**, both positive controls fire | **NEW** — RET-3's falsifier |

⚠ **`check_fuzz_bank` IS RETIRED (RET-2), exits 1, and is NOT a ladder leg** — it
was not run and is not counted.

---

## §6  ARTIFACTS

```
tests/v30/v02-unique-archive/      the 7,127 + v0.2's five provenance files
  README.md manifest.json SHA256SUMS
  <12 forms>.json.gz               the records, verbatim, `idx` = v0.2's index
  provenance/                      metadata.json run_manifest.json
                                   emit_log.txt emit_run.log .gitignore
sw/w27_v02_archive_check.py        RET-3's LIVE falsifier (archive + v0.3 only)
sw/wave27_ladder.sh                the ladder
sw/testdata/wave27/
  z1_scan.txt z1_keys.txt          the scan, and seven comparison keys
  z2_reproduction.txt              per-form reproduction, both digests
  z2_reroll_class.txt              reroll-vs-draw, with its own control
  z2_rejected_reasons.txt          the 85, by v0.3's own reason, + the control
  z5_consumers.md                  every consumer, with its disposition
  w27_*.py                         the instruments, by value
  ladder/                          every leg's raw log + rc.txt
docs/notes/invalidation_ledger.md  RET-3
```

⚠ **THE THREE `w27_*.py` SCANNERS IN `sw/testdata/wave27/` CANNOT RUN ON THIS
TREE ANY MORE** — they read `tests/v30/v0.2/`, and there is no
`tests/v30/v0.2/`.  They are the method, recorded.  **The live falsifiers are
`sw/w27_v02_archive_check.py` and `sw/testdata/wave27/w27_rejected_reasons.py`,
both of which need only the archive and `v0.3`.**

---

## §7  WHAT IS OWED

1. ⚠ **`--raw-flags` IS A GATE WITH NO SUCCESSOR.**  `v0.2 --raw-flags` scored
   **347,000 / 347,000** and `v0.3` **has never been run under that flag**.  The
   flag still exists (`sw/check_core.py --raw-flags`).  Booked, not taken —
   running it was outside this wave's brief.
2. ⚠ **`tests/v30/v0.3` AND `tests/v30/v20suite` ARE STILL NOT IN GIT** — 3
   tracked files of 746 and 3 of 364, 916 MB between them.  **The sentence that
   just came true about `v0.2` is true of both of them today**, and `v0.3` is
   now the sole holder of 339,873 `v0.2` captures as well as its own.
3. `hdl/tb/tb_v30_core.sv:523` still quotes the `7.17 M` arithmetic including
   `v0.2`.  **Z-7 forbade the edit**; booked for whoever next opens that file.
4. The **7,127 vs 7,137** erratum stays open and, absent a checkout that does
   not exist, is probably permanent.
