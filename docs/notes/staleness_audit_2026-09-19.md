# THE STALENESS AUDIT — 2026-09-19 (WAVE 20)

**Written against the tree at `975ecd0187` (`master`).  Every figure below was
MEASURED in this session unless the row says otherwise, and where a figure is
quoted from a document rather than measured it says so and names the
document.**

**USER DIRECTIVE, verbatim:**

> *"A lot of stale data and systems have accumulated over all these campaigns.
> Do an audit and determine what is no longer relevant and should be removed.
> **The old C model has not been maintained, remove it.**"*

**This document is the AUDIT.  Only ONE of its items was EXECUTED** — the C++
model, which the directive authorises by name (`invalidation_ledger.md`
**RET-1**).  **Everything else is a RECOMMENDATION and nothing else was
touched**: no branch deleted, nothing pushed, no `sw/testdata/` tree removed,
the FSM core's RTL not edited, `hdl/rtl/ucore/` and `hdl/nec_test.sdc` not
opened.

---

## §0 THE HEADLINE, IN FOUR SENTENCES

1. **THE BIGGEST SINGLE CLUSTER OF DEAD GATES IS ONE ROOT CAUSE, AND IT IS
   ALREADY WRITTEN DOWN IN THE CODE.** Seven of the nine tools in the
   "v1-anchor casualty family" die because **fuzz-v2 task T2 moved the test
   image's code region from `0x0500` to `[0x8000,0xC000)` and `gen_seq` plus
   the v1-anchored composers were deliberately left unported** — the decision,
   its reasoning and its consequences are in `sw/gen_seq._v1_anchor_stop`, in
   full, written at the time.  **It is not eight findings. It is one, with
   three different exit paths** (a raise, a different raise, and a silent RED).
2. **TWO OF THE NINE ARE NOT THAT, AND `CLAUDE.md` IS WRONG ABOUT BOTH.**
   `timed_scenario` **RUNS AND PASSES at its registered 18/0/9**;
   `timed_ins_replay` dies on **`sw/case31_all_exts.txt`, a data file that has
   never been committed to this repository.**
3. **THE C++ MODEL WAS NOT BROKEN — IT WAS UNMAINTAINED AND SUPERSEDED.** It
   scored **169,000/169,000** and **17,350/17,350 ALL LOCKSTEP** in this
   session, on the day it was removed.  What justifies removing it is one
   commit: `c59d205479` (2026-08-20) fixed REP termination in
   `hdl/rtl/ucore/` **and in no file under `sim/`**, so the RTL has been ahead
   of the "spec" for a month.
4. **THE ARCHIVED FSM CORE IS NOT EARNING ITS MAINTENANCE, BUT IT CANNOT BE
   REMOVED TODAY** — `sw/gen_ucore_qsf.py --check`, a STANDING gate, derives
   the ucore's Quartus revision **from the FSM revision**, and
   `sw/check_ab_sim.py --core fsm` / `sw/core_portlist_lint.py` are built on
   the two cores being drop-in alternatives.  The recommendation is therefore
   **KEEP THE RTL, RETIRE FOUR OF ITS TEN GATES**, not remove the core.

---

## §1 THE C++ MODEL `sim/` — **EXECUTED.  See `invalidation_ledger.md` RET-1.**

### What it is, measured

| | |
|---|---|
| tracked payload | **39 files, 491,759 bytes, 10,089 lines of C++ in 36 sources** |
| on disk | 1.7 MB — the difference is 33 gitignored `.o`/`.d` files and the built binary |
| last source change | **`be4eb2c32f`, 2026-08-17.  75 commits to `sim/*.cpp` / `*.h` in August 2026 and NONE since.** |
| its binary | `sim/build/v30sim`, receipt `54cb8188bf7bff16…` |

### The evidence that it is stale — three facts, none of them an opinion

1. **THE CORRECTNESS TARGET MOVED OUT FROM UNDER IT ON 2026-08-04.**
   `CLAUDE.md`: *"SILICON MATCH is the only correctness bar. Matching the model
   is no longer acceptable."*  From that date the model is an instrument, not a
   reference — yet `sw/ulockstep.py`'s header still reads *"the model is the
   SPEC. A divergence reported here is a bug in the RTL"*, and that sentence
   was still in the tree on the day the model went.
2. **THE RTL IS AHEAD OF IT ON SILICON-REFERENCED BEHAVIOUR.** `c59d205479`
   (2026-08-20, *"Fix REP termination before interrupt withdrawal"*) touches
   `hdl/rtl/ucore/v30u_eu_cond.svh` and **no `sim/` file**.  `be4eb2c32f`
   (the REP `CL==0` fix) landed in BOTH on 2026-08-17; three days later the
   pairing stopped.
3. **IT IS GREEN, AND THAT IS NOT A DEFENCE.** Measured this session before
   the removal: `timed_gate --suite tests/v30/v0.1 --forms all` =
   **169,000/169,000, row-diffs 0**; `ulockstep --golden all --cases 50` =
   **17,350/17,350 ALL LOCKSTEP**.  A green instrument that no longer defines
   correctness and is a month behind the artifact it measures is exactly what
   *stale* means here.

### The consumer enumeration — **Y-1**, with its method AND its limits

**METHOD.** (a) A regex sweep of every `*.py` under `sw/` for `simbin`,
`v30sim`, `sim/build` → **37 files** that name the model directly.  (b) An
import graph built by AST over all 376 modules, plus `import_module("…")`
string forms → **97 further modules** that reach one of the 37 by import.
(c) An AST pass that distinguishes calls in **module scope** from calls in
function scope, to find the tools that touch the model at **import** time →
**6**.  (d) A grep over `*.sh`, `*.sv`, `*.svh`, `Makefile`, `*.json` and
`tests/` for the same names.

**LIMITS, stated because a method with no limits is a method nobody checked.**
The import graph is textual: a module reached only through `getattr`, a
`subprocess` call assembled from string fragments, or a shell wrapper naming
`v30sim` in a variable would be missed.  The `*.sh` sweep found the name only
in comments.  `hdl/tb/tb_v30_core.sv:1027` names `v30sim` in a **comment**.
**No `Makefile`, no `.qip`, no `.sdc`, no `tests/` data file builds or runs the
model.**  The backstop against a missed consumer is not the sweep: it is that
`sw/simbin.py` survives as a refusal, so anything that reaches the model dies
**by name** rather than by `FileNotFoundError` — and that was verified by
importing all 376 modules.

**RECOMMENDATION: REMOVE — DONE.**  Cost of keeping: a 10,089-line C++ engine
that no longer defines correctness, is a month behind the RTL, and whose
`ulockstep` leg invites a reader to treat model agreement as a bar.  Cost of
removing: enumerated gate-by-gate in RET-1; the largest single item is the
**7.17 M-case architectural ladder outside `v0.1`** (`v0.2` 347,000 + `v0.3`
3,699,998 + `v20suite` 3,125,000), which now has **no scorer at all**.

---

## §2 THE ARCHIVED FSM CORE `hdl/rtl/core/` — **RECOMMEND: KEEP THE RTL, RETIRE FOUR GATES**

### What it is, measured

| | |
|---|---|
| size | **476 KB, 6 files** (`v30_eu.sv` 293 KB, `v30_biu.sv` 112 KB, `v30_core.sv` 17 KB, `v30_ss_pkg.sv` 26 KB, `race_law.svh`, `int9d_race.hex`) |
| archived | 2026-08-04, `docs/notes/fsm_core_archive_2026-08-04.md` |
| substantive change since | **NONE.** `git log --since=2026-08-04 -- hdl/rtl/core/` returns **one** commit, `9ccc6d0177` (WAVE 18), and it adds three output ports tied to zero |

### The evidence that it is costing more than it returns

* **TWO AUTHORISED CHANGES SINCE THE ARCHIVE, BOTH PURE PORT-LIST
  MAINTENANCE FORCED BY ucore LANDINGS** — §6a's `AD_OE` (2026-08-04) and
  §6b's `ADDR_O`/`DATA_O`/`STATUS_O` (2026-09-19).  Neither is about the FSM
  core; both exist because the two cores share `hdl/tb/tb_v30_core.sv` and
  `hdl/rtl/system_large.sv`.
* **IT WAS UNREACHABLE BY ITS OWN DOCUMENTED PROCEDURE FOR FIVE WEEKS.**  The
  de-muxed bus landing (`b7083b45a5`, 2026-08-14) killed `check_core --core
  fsm` — the archive's §6 re-activation command — plus `check_fuzz_bank`,
  `check_enter_nesting`, `check_ab_sim --core fsm` and `t30_sweep.sh`, at
  `%Error-PINNOTFOUND`, **before the first seed and without printing a
  verdict** (`standing_gates.md` §C, WAVE 18).
* **ITS REGISTERED FIGURES WERE STALE BY A FACTOR OF FOURTEEN.**  §C carried
  **168,400/169,000** and **16/283**; re-measured 2026-09-19 they are
  **169,000/169,000** and **226/283**.  Nothing about the core changed — the
  COMPARATOR did, at `0254d9f23e` on 2026-08-05, whose own message says *"it
  moves NOTHING"* and quotes the **ucore** leg.
* **ONE WHOLE WAVE (18) WAS SPENT SO A GATE COULD ELABORATE**, and it produced
  a **new permanent standing gate**, `sw/core_portlist_lint.py`, whose entire
  purpose is to keep the two port lists equal.  That gate is now maintenance
  the ucore pays for the archive.

### Why it CANNOT simply be removed — measured, and this is the load-bearing part

* **`sw/gen_ucore_qsf.py --check` IS A STANDING GATE (§A) AND IT DERIVES THE
  ucore REVISION FROM THE FSM ONE.**  `hdl/nec_test.qsf` + `hdl/files.qip` IS
  the FSM revision (`files.qip:9-12` names all four `rtl/core/*.sv`), and
  `hdl/nec_test_ucore.qsf` is *"this file with one line changed"*.  Deleting
  `hdl/rtl/core/` breaks the A/B derivation the gate exists to protect.
* `sw/check_ab_sim.py --core fsm` (**187 rows MATCH**) and
  `sw/core_portlist_lint.py` both rest on the two cores being drop-in
  alternatives with identical port lists.
* The archive's §5 keeps a real asset: *the falsifier-generator value* — a
  second, independently-derived implementation of the same part, in the tree.

### The ten on-demand gates, measured 2026-09-19

| gate | measured | root cause |
|---|---|---|
| `check_race_law` · `prefix_clear_lint` · `ea_step_lint` · `ss_lint --core fsm` · `check_fuzz_bank` | **RUN** | — |
| `check_enter_nesting` | **RUNS, RED, engine-independent** (the same 512 fail with `check_seq.CORE="ucore"`) | **v1 anchor** — composes a v2 image, compares to v1 goldens |
| `check_ff_t4` | **DOWN — `V1AnchorStop`** | **v1 anchor** |
| `check_mod3_illegal` | **DOWN — `ComposeError: body [0500,0502) is not inside the code region [8000,c000)`** | **v1 anchor** |
| `check_lc6_gate` | **DOWN — `ComposeError: body [0500,0517) …`** | **v1 anchor** |

**⚠ NOT ONE OF THE FOUR FAILURES IS THE FSM CORE'S FAULT.**  All four are §4's
single root cause, and `check_enter_nesting` fails identically on the **ucore**.
The FSM core is being blamed for a fuzz-v2 casualty.

**RECOMMENDATION — three parts, for the coordinator and the user:**

1. **KEEP `hdl/rtl/core/`.**  Removing it breaks a standing gate and costs the
   only independent implementation left in the tree.  ARCHIVE-BY-RENAME buys
   nothing here — the files are already declared archived and `files.qip`
   needs them where they are.
2. **FORMALLY RETIRE the four down gates as `RET-2` (the v1-anchor family)**,
   or re-anchor them — which is board work and a user decision (§4).  They
   have carried green rows in §C while being unrunnable; **that is the exact
   failure WAVE 18 named, and it is still live for four of ten.**
3. **RE-REGISTER §C's FSM figures as 169,000/169,000 and 226/283 with the
   comparator named**, and record in the archive that `t30_sweep.sh`'s
   *"any non-full suite total = regression"* rule must be read against them.
   (§6b already states this; §C's table still shows the old pair as the live
   one in one place and the new pair in another.)

---

## §3 THE v1 FUZZ BANKS — **RECOMMEND: KEEP, AS THEY ARE.  DO NOT DELETE.**

| | |
|---|---|
| what | `tests/v30/fuzz_bank/{mc1,mc2,t30-raw,t30-brkem}` — **3,242 banked seeds**, 103 MB with the v2 banks |
| status | **SUPERSEDED** by `SUP-1` (2026-08-09) — a status key in four `manifest.json` files; **nothing was moved, renamed or deleted** |
| replayable? | **NO, and not because of SUP-1.**  Plan **D9** made the `0F` scrub unconditional, so every v1 image regenerates to a different sha256: **3,157 GEN-DRIFT + 85 refused, 0 scored** |

**THE EVIDENCE IT IS "STALE" IS ALSO THE EVIDENCE IT MUST BE KEPT.**  SUP-1's
own **WHAT IS LOST** section already enumerates the cost, and two of its five
items are irreplaceable: the **532 `OPEN_BUS`-excused seeds** and the **8080 /
BRKEM class** (85 seeds plus 50 BRKEM positions), of which **the v2 corpus has
exactly zero**.  These are TRUE SILICON CAPTURES from the socket.  The project
directive is *archive by rename with a ledger entry, nothing is ever deleted*,
and here even the rename was unnecessary.

**RECOMMENDATION: KEEP.**  Cost of keeping: **103 MB and nothing else** — no
gate replays them, `--include-superseded` returns the seeds on request, and
every consumer prints the exclusion on its own line.  Cost of removing:
permanent loss of the only 8080-mode silicon in the repo, for 103 MB.  **There
is no case for removal.**

**ONE THING WORTH DOING, CHEAPLY**: `standing_gates.md` and `CLAUDE.md` still
print the v1-bank ratchets (`timed_fuzz --core ucore` 1,559/1,702 etc. over
3,242 seeds) beside the live ones with a ⚠ rather than in a retired block.
Those figures are **not derivable on this tree**, and a reader who skips the ⚠
will quote them.  Consider moving them under one heading that says so once.

---

## §4 ⭐ THE v1-ANCHOR CASUALTY FAMILY — **ONE ROOT CAUSE, AND IT IS ALREADY DOCUMENTED IN THE CODE**

### The answer to the brief's question: **YES, and it is worth more than eight rows.**

**THE ROOT CAUSE, IN ONE SENTENCE**: *fuzz-v2 task **T2** moved the test
image's code region from the v1 anchor `PC0 = 0x0500` to `[0x8000, 0xC000)`,
`testimage.compose` now rejects any body outside it, and `sw/gen_seq.py` — plus
every tool that composes a v1-anchored body directly — was **deliberately left
unported** (plan finding **F6**).*

**IT IS NOT AN OVERSIGHT AND IT IS NOT A BUG.**  `sw/gen_seq._v1_anchor_stop`'s
own docstring names the gates, the measurement, and the reason:

> *"Moving PC0 into the code region is two lines and it is the WRONG TWO LINES
> to write unreviewed, because it RE-BASES every `fz<seed>` image.  Those
> standing gates score against SILICON baselines frozen at the v1 anchor …
> a green produced that way would be a fabricated green — the gate would pass
> while measuring something nobody has ever captured on the part.  Re-basing
> therefore requires a RE-CAPTURE, which is board work and a user decision, not
> a code fix."*

And the same campaign already built the mechanism for it: **`sw/retired_v1.py`**
(fuzz-v2 T12, 2026-08-08) retires **23 tools** for the same reason, with the
same reasoning, raising `RetiredTool` rather than a confusing `TypeError`.
`gen_seq` is the one thing T12 chose to STOP at rather than retire, because
stopping is reversible and retiring the gates was not its call.

### The nine tools, MEASURED 2026-09-19 on `master`

| tool | registered figure | measured behaviour | same root cause? |
|---|---|---|---|
| `timed_wvec_gate` | 88/88, +0.0 % | **`V1AnchorStop`** | ✔ |
| `timed_lawcards` | 8 GREEN / 0 RED / 3 UNRESOLVED | **`V1AnchorStop`** | ✔ |
| `check_ff_t4` (archived) | `SLOT_FF_T4` non-vacuous | **`V1AnchorStop`** | ✔ |
| `timed_enter_replay` | 154/154 ×5 | **its own v1-anchor refusal**, different text, same decision | ✔ |
| `check_mod3_illegal` (archived) | chip-exact | **`ComposeError: body [0500,0502) not in [8000,c000)`** | ✔ (composes directly; does not route through `gen_seq`) |
| `check_lc6_gate` (archived) | LC6 veto intact | **`ComposeError: body [0500,0517) …`** | ✔ |
| `check_enter_nesting` (archived) | ENTER walk == chip | **RUNS, 100 % divergence, RED — and RED identically with `CORE="ucore"`** | ✔ — *a v2 image scored against v1 goldens.*  **A LOUD RED CAN BE AS FALSE AS A SILENT GREEN** |
| **`timed_scenario`** | 18/0/9 | ⚠ **RAN AND PASSED: `18 PASS, 0 FAIL, 9 SKIP`** | ✘ **NOT A CASUALTY.  `CLAUDE.md` is wrong.** |
| **`timed_ins_replay`** | 1,312/1,312 · 2,624/2,624 | ⚠ **`FileNotFoundError: sw/case31_all_exts.txt`** | ✘ **A DIFFERENT CAUSE ENTIRELY** |

### The two errata this audit raises

**ERRATUM 1 — `timed_scenario` IS NOT DOWN.**  `CLAUDE.md`'s
`fuzz-v2-on-relanding` banner says *"FOUR RATCHETS IN THIS FILE CANNOT RUN HERE
AT ALL — `timed_scenario`, `timed_ins_replay`, `timed_wvec_gate`,
`timed_enter_replay`.  They die in `image_of(seed)` on
`gen_seq._v1_anchor_stop`."*  On `master` — which **is** a descendant of
`fuzz-v2-on-relanding` (merge-base `82d7561c4b`) — `timed_scenario` runs to
completion at its registered figure.  It is a model consumer and therefore a
genuine casualty of **RET-1**, which is a different thing from being a v1-anchor
casualty, and the two must not be merged.

**ERRATUM 2 — `timed_ins_replay` DIES ON AN UNCOMMITTED DATA FILE.**
`sw/case31_all_exts.txt` is **not tracked, not ignored, and absent**;
`git log -- sw/case31_all_exts.txt` is empty, so it has never been in this
repository.  Three further tools read it: `sw/biu_case165_ins_split_write_
factorial.py`, `sw/biu_case249_new_ins_factorial.py`,
`sw/biu_case253_rtl_ins_deadline_validate.py`.  **A standing ratchet
(1,312/1,312 and 2,624/2,624) has been unrunnable from a clean checkout for an
unknown period, and no gate saw it** — the same class of finding as WAVE 18's,
one level down.

### What the family costs, and what closing it costs

**RECOMMENDATION.**

1. **FILE THE FAMILY AS ONE LEDGER ENTRY, `RET-2` or `SUP-2`** — seven gates,
   one cause, one decision, one falsifier.  Eight separate rows in
   `standing_gates.md` invite eight separate repairs, and six of the seven
   would be *fabricated greens* if repaired without a re-capture.
2. **THE ONLY REAL FIX IS A BOARD SESSION**: re-capture the frozen v1 baselines
   (`biu_rebuild_wvec_baseline.json`, the lawcards chip captures, the INS
   replay rails, the ENTER socket digests) at the v2 anchor.  **That is a USER
   DECISION and this audit does not make it.**  Note it would also need
   `gen_seq.far_int_support()`'s vector 3, which fuzz-v2 reserves for the
   terminator — *the port is two mechanisms deep, not one.*
3. **`timed_ins_replay` IS THE CHEAP ONE AND IT IS NOT IN THE FAMILY**: commit
   `sw/case31_all_exts.txt`, or make the four readers refuse by name.  It may
   be a one-line fix to a standing ratchet.

---

## §5 STALE GIT STATE — **RECOMMEND: REPORT ONLY.  NOTHING WAS DELETED OR PUSHED.**

### Measured

| item | measured | recommendation |
|---|---|---|
| `worktree-agent-*` branches | **42.  41 of them contain NO commit that is not already in `master`** (`git rev-list --count master..$b` = 0); the exception is `worktree-agent-a235820721ac7b80a`, **1 unique commit** | **REMOVE the 41, AFTER the push below.**  Check the 1 first.  ⚠ **NOT DONE — branch deletion is the coordinator's call** |
| other local branches | 12 (`biu-arb-qcnt`, `biu-rebuild`, `fuzz-v2`, `fuzz-v2-on-relanding`, `savestate-v2`, `spike-r0b`, `ucore-relanding`, `ucsim`, `v20-arch-oracle`, `w4-eubiu-landed`, `w7-ghost-retention`, `master`) | **KEEP** — several are cited by name in the ledger as the only trees where a historical figure is re-derivable (SUP-1 names `7e949925b7` and `master`) |
| ⚠ **`origin/master`** | **`c0633d7685`, 2026-08-27.  `master` is 126 COMMITS AHEAD.** | **PUSH — user's call.  NOT DONE.**  Six waves, two flashes (#22, #23) and the whole no-SDC campaign's answer exist only on this machine |
| registered worktrees | 4, all under `~/.cache/ucsimt-tmp/wave{16,17,19}/`; wave 16's two are for a landed wave | `git worktree prune` after checking; **NOT DONE** |
| `hdl/tb/obj_dir*` | **994 MB in 10 directories.**  `obj_dir_harness` **162 MB, untouched since 2026-07-13**; `obj_dir_sys.stale-0704` and `obj_dir_sys_ret.stale-0705` are **explicitly named `stale`** and total 6.7 MB | **REMOVE `obj_dir_harness` and the two `.stale-*`.**  All are rebuildable; the receipt layer refuses a stale binary, so nothing can score off them.  ⚠ **NOT DONE** |
| `hdl/quartus_gate_*.log` | **14 untracked logs, 6,119,080 bytes**, from Aug 11 – Sep 12 | The repo's own convention is the last commit's: *"commit the orphaned G6 driver logs, **gzipped** per convention"*.  **Either gzip-and-commit them or delete them** — an untracked 6 MB log is neither evidence nor housekeeping.  ⚠ **NOT DONE** |
| `sw/testdata/` | **34,274 tracked files; 6,265 untracked/ignored.**  Largest trees: `campaigns` 1.4 GB (37 readers), `chipcache` 176 MB (4), `sm3-s13cell` 116 MB (**0 readers**), `t4` 85 MB (7), `sm3-s11cell` 21 MB (**0 readers**) | **KEEP ALL OF IT.**  These are silicon captures and the ledger's first rule is that nothing is deleted.  ⚠ The two **0-reader** trees (137 MB) are worth a coordinator glance, but *"no reader"* is not *"no value"* — `sw/testdata/campaigns` had no reader either when INV-1 needed it |
| repo size | working tree **5.4 GB**, `.git` **764 MB** | no action |

---

## §6 DOCUMENTATION MASS — **RECOMMEND: FIX FOUR THINGS THAT ARE *WRONG*.  CHANGE NOTHING ELSE.**

**THE LAYERING IS DELIBERATE AND THIS AUDIT DEFENDS IT.**  *"A ratchet is only
readable against its own history"* is the reason `CLAUDE.md` (1,358 lines) and
`standing_gates.md` (3,243 lines) carry superseded blocks, and every one of
them is labelled.  `docs/notes/` is **292 files, 139,029 lines, 9.4 MB**, and
its size is the record of nineteen waves.  **Do not compress it.**

**Recommended ONLY where a section is WRONG — i.e. it makes a false statement
about the tree as it is today:**

| # | where | what is wrong | evidence |
|---|---|---|---|
| **W-1** | `CLAUDE.md`, the `fuzz-v2-on-relanding` banner | *"FOUR RATCHETS … CANNOT RUN HERE AT ALL"* naming `timed_scenario` and `timed_ins_replay` | **measured**: `timed_scenario` ran and passed 18/0/9; `timed_ins_replay` dies on a missing untracked file, not the anchor (§4) |
| **W-2** | `CLAUDE.md`, the `ss_lint` row of the Gate quick reference | presents **`SS_VERSION` 0x8D / `SS_COUNT` 226 / `SS_TAG` 0x8DE2 / 214 flops** as **CURRENT** | **measured**: **232 / 229 flops / 4 whitelist / 0 UNMAPPED, 0x8F, 0x8FE8**.  ⚠ `standing_gates.md` §B line 1497 is **already correct** — so the handoff's §10 item 2 (*"its stale `ss_lint` row"*) is itself discharged, and CLAUDE.md is the one left |
| **W-3** | `CLAUDE.md`, the WAVE 7 banner | *"`ss_lint` **232 / 228 flops** / 0 UNMAPPED"* | **measured 229** — ARM-B's one declared flop.  One digit, in the banner a reader trusts most |
| **W-4** | `docs/notes/timing_campaign_handoff_2026-09-14.md` §2, §4, §10 | *"the phase split … **reverted**"*, *"ARM-A vs ARM-B … **the only thing blocking a landing plan**"*, *"`test_quartus_gate` **286**"* | **all three are closed**: WAVE 17 landed the split, ARM-B is in silicon at FLASH #23, and `test_quartus_gate` measures **287/287**.  The handoff is a **snapshot of 2026-09-14** and should say so in its title line, or it will be read as state |

**Not recommended, deliberately**: the superseded G6 bands, the superseded
FLASH lines, the struck EVT comparisons, the `168,400 / 16/283` FSM history.
Every one is labelled as history and each is load-bearing for reading the
ratchet it supersedes.

---

## §7 EVERYTHING ELSE THE SWEEP FOUND

| finding | measured | recommendation |
|---|---|---|
| **`sw/case31_all_exts.txt` was never committed** | not tracked, not ignored, absent; `git log --` empty.  Breaks **4 tools**, one of them a standing ratchet | **commit it, or refuse by name.**  §4 erratum 2 |
| **`sw/sm3_tf_law.py` prints a full rollup over ZERO seeds** | `== rollup 0 seeds` followed by nine empty `Counter()`s and *"rejected 4/6 pairs (arch): 0"* — a confident-looking report from an empty population | a measurement tool, not a gate; but it is the **vacuous-instrument pattern in its purest form**.  Give it a non-empty-population assertion |
| **`sw/t30_sweep.sh` now correctly reports FAILED** | it was repaired at `becaf81e89`; three of its legs are §4 casualties | the sweep cannot go green until §4 is dispositioned.  **Do not "fix" it by dropping the legs** |
| **two latent stale-binary hazards, still open** | `sw/check_ff_t4.py:34` and `sw/causal_wrand.py:715` use `check_seq.BIN` **with no artifact assertion** — a STALE binary would score | booked by WAVE 18, not repaired, still true.  Cheap to close once §4 is dispositioned |
| **`sw/retired_v1.py` already exists and is the right pattern** | 23 tools use it | **use it (or `simbin.retired`) for §4's family** rather than inventing a third mechanism |
| **`fz2_replay` refuses with ERA MISMATCH on this tree** | 4 files MOVED vs the flashed manifest, incl. `hdl/sys/build_id.tcl`, `hdl/sys/sys.tcl` | pre-existing, unrelated to this wave, and **the guard working as designed**.  It is the fabric debt showing through an instrument |
| **`sw/ucore_tables.py` / `sw/gen_ucore_tables.py` cite `sim/` by path** | *"a line-for-line transliteration of `sim/ucrom.cpp`"*, plus `sim/pla3_table.h`, `sim/ucrom.h`, `sim/state.h`, `sim/exec_impl.h:796` | **LEFT STANDING DELIBERATELY.**  They are the ucore's provenance; deleting them deletes the provenance, not the dangle.  RET-1 records that they now point into history at `be4eb2c32f` |

---

## §8 WHAT THIS WAVE DID **NOT** DO — the list, so nobody has to infer it

* **Did not push.**  `origin/master` is 126 commits behind.
* **Did not delete a branch**, a worktree, an `obj_dir`, a Quartus log, or one
  byte of `sw/testdata/` or `tests/`.
* **Did not touch `hdl/rtl/ucore/` or `hdl/nec_test.sdc`.**  No Quartus build
  was run and none was needed.
* **Did not touch `hdl/rtl/core/`** — the FSM core is untouched.
* **Did not touch the user's 21 uncommitted files.**  Five of them consume the
  model by bare path and will raise `FileNotFoundError`; they are named in
  RET-1 with their one-line fix, and repairing them is the owner's call.
* **Did not run the board.**  FLASH #23 stands.
