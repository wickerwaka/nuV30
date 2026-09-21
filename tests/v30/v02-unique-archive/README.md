# `v0.2` UNIQUE-CASE ARCHIVE — the 7,127 cases `v0.3`'s prefix does not reproduce

**WAVE 27, 2026-09-21.**  User directive: *"Remove v0.2, v0.3 supersedes it"*.
Ledger entry: `docs/notes/invalidation_ledger.md` **RET-3**.

**THIS DIRECTORY EXISTS BECAUSE `tests/v30/v0.2/` WAS NOT IN GIT.**  Exactly one
of its 351 files was tracked (`.gitignore`); the other 350 — 91,237,482 bytes of
socket captures taken from the user's uPD70116 on 2026-07-17 — were excluded by
that file's own `*` rule.  RET-1 (`sim/`) and RET-2 (`hdl/rtl/core/`) could say
*"nothing is destroyed, `git checkout <commit> -- <path>` restores it."*
**This retirement cannot say that.**  So everything `v0.3` does not already
carry was copied here, tracked, and committed **before the first deletion**.

## What is here

Twelve `<form>.json.gz` files: one JSON array per form of the **verbatim `v0.2`
records** that `v0.3`'s first 1,000 cases of that form do not reproduce at the
same index.  The schema is `v0.2`'s own — `name`, `bytes`, `initial`, `final`,
`cycles`, `hash`, `idx` — and **`idx` is the record's original `v0.2` output
index**, so any case here can be quoted by its historical coordinate.

`manifest.json` carries, per form: the differing indices, the counts, the
disposition of every index, the `sha256` of the archived file and of its
uncompressed content, and the `sha256` of the `v0.2` file the records came from.

## The measurement

Full 347-form positional scan, `v0.2` (1,000 cases/form) against `v0.3`'s first
1,000 (`v0.3` carries **10,000** per form).

| | |
|---|---:|
| `v0.2` total cases | **347,000** |
| `v0.2` forms, and forms of it **absent** from `v0.3` | **347**, and **0** |
| reproduced by `v0.3`'s prefix **at the same index, byte for byte** | **339,873** |
| **not** reproduced | **7,127  (2.0539 %)**, in **12 forms** |

**COMPARISON KEY**: the record's own `hash` field = `SHA1` of
`json.dumps([name,bytes,initial,final,cycles],separators=(",",":"))` — the whole
record except `idx`, which is a position label and not content.  *Positive
control*: at every position where the two hashes are equal the two records were
asserted byte-identical modulo `idx` — **0 violations in 339,873**.  Three other
keys (whole record including `idx`; `initial` alone; `name`+`bytes`+`initial`)
return **the same 7,127**.

## Are these cases `v0.3` REROLLED AWAY, or cases it drew differently?

**BOTH, AND THE SPLIT IS MEASURED.**  `emit_suite.py` draws case *i* of form *F*
from seed attempts *k = 0,1,2,…* in order, skipping any attempt it rerolls, and
each reroll is one line of `emit_log.txt`.  So `out_idx → seed attempt` is the
ordered attempts minus the rerolled set, and both suites ship the log.

> **POSITIVE CONTROL FOR THAT RECONSTRUCTION.**  `v0.3` also ships the true map
> per form (`XX.seeds.json`).  Rebuilding it from `v0.3`'s own `emit_log.txt`
> reproduces the committed map on **370 of 370 forms, exactly**, and the
> equality is **not trivial — 107 of the 370 maps are non-identity**.

| class | count | what it means |
|---|---:|---|
| **PRESENT IN `v0.3` AT ANOTHER INDEX** | **5,890** | `v0.3` holds this case **byte for byte**; a reroll earlier in the form shifted every later index.  **Nothing is lost.** |
| **ABSENT, `SAME_SEED_DIFFERENT_RECORD`** | **1,152** | `v0.3` *used* the same seed attempt and built a **different case** from it — the emitter's placement logic moved between the two emissions (flat-1 MB memory model; mirror-collision footprint-reject removed).  **A different draw, not a rejection.** |
| **ABSENT, `REJECTED_BY_v0.3`** | **85** | `v0.3`'s generator **rerolled this exact seed attempt away**.  These are the only cases whose *content* `v0.3` refused. |
| | **7,127** | |

**THE 85 REJECTED CASES ARE PRESERVED DELIBERATELY AND ARE FLAGGED AS SUCH.**
`v0.3`'s reroll reasons on these nine forms are dominated by
*"implausible final PSW"*, plus *"PC push bytes not contiguous"*, *"footprint
overlap (instr/stub/ivt collide)"* and *"test footprint intersects the reserved
page"*.  A case the later generator calls implausible is **evidence about the
generator**, and possibly about the part; it is not obviously ill-formed data,
and it is not this wave's business to adjudicate.  Every one of the 85 is
identified in `manifest.json` by form, index, its `v0.2` seed attempt and its
class.

⚠ **NO CLAIM IS MADE THAT THESE 7,127 COVER ANY BEHAVIOUR `v0.3` DOES NOT.**
All 347 `v0.2` forms exist in `v0.3` at **ten times the case count**.  Form-level
coverage does not drop by one form.  What is preserved here is 7,127 particular
draws of forms `v0.3` already covers 10,000 deep.

## Per form

| form | not reproduced | present in `v0.3` elsewhere | same seed, different record | **rejected by `v0.3`** |
|---|---:|---:|---:|---:|
| `HLT.INT` | 924 | 380 | 537 | 7 |
| `IE0.90` | 907 | 905 | 0 | 2 |
| `INT.8ED8` | 903 | 889 | 6 | 8 |
| `INT.9D` | 897 | 867 | 16 | 14 |
| `HLT.RES` | 813 | 244 | 566 | 3 |
| `INT.8ED0` | 776 | 759 | 4 | 13 |
| `INT.FB` | 727 | 714 | 0 | 13 |
| `INT.B8` | 609 | 583 | 13 | 13 |
| `INT.90` | 564 | 549 | 3 | 12 |
| `0F31` | 5 | 0 | 5 | 0 |
| `0F26` | 1 | 0 | 1 | 0 |
| `A6` | 1 | 0 | 1 | 0 |
| **total** | **7,127** | **5,890** | **1,152** | **85** |

**7,120 of the 7,127 are in the nine interrupt/HALT forms**, and they are
exactly the positions where the two emissions used a **different seed attempt**
(a reroll-history shift, measured independently: 7,120).  **The other seven —
`0F31` ×5, `0F26` ×1, `A6` ×1 — use the SAME seed attempt in both emissions**
and are therefore emitter-evolution alone, with no reroll involved.

## ⚠ The `7,127` vs `7,137` discrepancy — REPORTED, NOT RESOLVED

`tests/v30/v0.3/README.md` says **7,137**.  This tree measures **7,127** on four
independent content keys, and **no key tried reproduces 7,137**
(`cycles` alone gives 6,830, `name`+`bytes` 6,270; every whole-record key gives
7,127).  The `7,137` text was written at `24d6d78573`.

**It cannot be re-derived, and the reason is this entry's whole subject:
NEITHER SUITE IS IN GIT**, so no historical state of either can be checked out.
The most likely cause is that the figure was taken against a pre-re-emission
state of one of them — `v0.3/reemit.log` records five confined per-index
re-emissions, **two of them inside the compared prefix** (`36.6E` idx 517,
`F26F` idx 743), and `docs/notes/v0.2_reemission_worklist.md` records a
re-emission pass over `v0.2` itself.  **The ten-case gap is stated as
unexplained; 7,127 is what this tree measures and 7,127 is what is archived.**

## ⚠ WHAT `REJECTED_BY_v0.3` DOES AND DOES NOT MEAN — a scoping limit, and a refuted reading

**IT MEANS: `v0.3`'s generator rerolled that SEED ATTEMPT away.**  It does NOT
mean `v0.3` was handed this exact `v0.2` record and refused it.  The two
emissions build **different cases from the same seed** — that is precisely what
the 1,152 `SAME_SEED_DIFFERENT_RECORD` cases demonstrate — so the candidate
`v0.3` refused at seed *k* is its own candidate, not necessarily the record
`v0.2` banked at that index.  **The class is a statement about the seed, and
the archive preserves the `v0.2` record that sits behind it.**

`v0.3`'s own reroll reason for each of the 85:

| reason family, verbatim from `v0.3/emit_log.txt` | n |
|---|---:|
| `implausible final PSW <value>` — `0` ×37, plus 8 distinct non-zero values ×1 each | **45** |
| `pf assert before window (<offset>)` — `0`, −1, −2, −3, −4, −58, −59, −60, −70, −71 | **37** |
| `no F pop from close addr <addr>` | **3** |
| | **85** |

Regenerate with `python3 sw/testdata/wave27/w27_rejected_reasons.py` (runs from
the archive and `v0.3/emit_log.txt` alone; it exits non-zero if any of the 85
has no matching reroll line — measured **0**).  Frozen output:
`sw/testdata/wave27/z2_rejected_reasons.txt`.

⚠ **A READING THAT LOOKED OBVIOUS AND IS REFUTED BY ITS OWN CONTROL.**  Four
spot-checked rejected cases all carried **no `final.flags`**, which suggested
the 85 were `v0.2` captures with a defective final-PSW capture — the very thing
`v0.3/README.md` says it fixed.  **The control says otherwise**: `final.flags`
is absent from **all 7,127** archived records — 85 rejected, 1,152 same-seed,
5,890 shifted alike — because `final.regs` is sparse in this schema and these
pin-event forms do not list it.  **Absence of `final.flags` is not a
discriminator and the reading is withdrawn.**  What stands is the reason
histogram above, which is `v0.3`'s own log and needs no interpretation.

## `provenance/` — the suite's own records, and the only copies that exist

`v0.2`'s five non-case files, preserved verbatim (gzipped, `mtime=0`) with
their original `sha256` in `manifest.json`:

| file | bytes |
|---|---:|
| `metadata.json` | 638 |
| `run_manifest.json` | 638 |
| `emit_log.txt` | 431,633 |
| `emit_run.log` | 226,823 |
| `.gitignore` | 144 — *the one tracked file of the 352, and the reason the other 351 were not* |

⚠ **`emit_log.txt` IS THE ONLY SURVIVING RECORD OF `v0.2`'s REROLL HISTORY**, and
it is what the reroll-vs-different-draw classification above was derived from.
It was never in git.  Without it the 85/1,152 split cannot be re-derived by
anyone, ever.

## The falsifier

`python3 sw/w27_v02_archive_check.py` — needs only this directory and `v0.3`.
It re-derives every claim above that survives `v0.2`'s deletion, and it carries
a positive control that makes two of its four checks fail on a perturbed
manifest.
