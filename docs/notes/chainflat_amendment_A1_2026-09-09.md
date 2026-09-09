# WAVE 6 — AMENDMENT A-1.  **P-1(c) MISSED, AND ITS REPLACEMENT IS REGISTERED HERE BEFORE THE DATA THAT WILL SCORE IT EXISTS.**

Amends `docs/notes/chainflat_prereg_2026-09-09.md` (`39e201aa6c`).
Committed **before the REF/FLAT seed 4, 5, 6 fits are started**.

---

## §1 THE MISS, REPORTED AS REGISTERED AND NOT RESTATED

P-1(c) asked, on **REF**:

> the copy census reads `st_n` **≥ 20** distinct cones, each of `rst_ctr_n` /
> `ld_dlo_n` / `ld_ripe_prev_n` **≤ 1**, and the negative control
> `zzz_no_such_signal` **== 0**

**MEASURED, three CONTROL draws, `sw/testdata/chainflat/ref_seed{1,2,3}.txt`:**

| clause | seed 1 | seed 2 | seed 3 | asked | |
|---|---:|---:|---:|---|---|
| `st_n` | 129 | 131 | 129 | ≥ 20 | MET |
| `rst_ctr_n` | 0 | 0 | 0 | ≤ 1 | MET |
| `ld_dlo_n` | 0 | 0 | 0 | ≤ 1 | MET |
| **`ld_ripe_prev_n`** | **3** | **3** | **3** | ≤ 1 | **MISSED** |
| `zzz_no_such_signal` | 0 | 0 | 0 | == 0 | MET |

> ## **P-1(c) IS MISSED, ON ALL THREE DRAWS, AND THEREFORE P-1 IS MISSED.  BY THE PRE-REGISTRATION THAT VOIDS DELIVERABLE D, AND DELIVERABLE D IS NOT QUOTED ON THE STRENGTH OF THE ORIGINAL BAR.**
>
> **THE BAR IS NOT WIDENED.**  It stays as written and it stays missed.
> Recognising, after seeing a 3, that the number should have been different is
> exactly what pre-registration exists to prevent.

## §2 THE ERRATUM — WHY THE BAR WAS WRONG **FOR THE HARNESS**, MECHANISM FIRST

The threshold was carried over from WAVE 5's **in-design** census, where
`ld_ripe_prev_n` reads **0** on every draw.  It does not survive the change of
harness, and the reason is structural rather than numeric:

* In the design, `q_ripe` comes out of `v30u_biu` and the cone that computes
  `ld_ripe_prev_n = q_ripe` folds into its driver.
* In this study's harness, **`v30u_eu` is its own top and `q_ripe` is a VIRTUAL
  INPUT PIN.**  `ld_ripe_prev_n` is then a next-state signal sitting directly on
  a pin with nothing to fold into, and Quartus keeps it and duplicates it for
  fanout.  It reads **3 on FLAT as well as on REF** — identical on both arms,
  on all six draws — which is what a harness artefact looks like and is not
  what a chain property looks like.

**AN ABSOLUTE COUNT WAS THE WRONG SHAPE FOR THE CLAIM.**  What "copies
independent" asserts is that the census *discriminates*: a name a chainable arm
writes carries many cones, a name only a position-0 arm writes carries few, and
a name that does not exist carries none.  That is a RATIO and a negative
control, not a threshold on one name.

## §3 THE REPLACEMENT, AND IT IS VALIDATED ON DATA THAT DID NOT SELECT IT

⚠ **THE ORDER MATTERS AND IS DECLARED: this section is written and committed
BEFORE the seed 4, 5, 6 fits exist.**  Seeds 1 – 3 are the draws that exposed
the miss and they may not score the replacement (`ucore_provenance.md` §64.1).

### P-1′(c) — THE REFERENCE'S DISCRIMINATION CONTROL

On **REF**, on **each** of seeds 4, 5, 6:

```
   min( st_n, ld_b_n, pv, opc_base )   >=   10 x
   max( rst_ctr_n, ld_dlo_n, ld_ripe_prev_n, nmi_latch_n, rloop_n_n )
   AND  zzz_no_such_signal == 0
```

⚠ **THE FACTOR 10 IS DECLARED AS PARTLY POST-HOC.**  It is "an order of
magnitude", chosen for the mechanism (a chainable name has up to six copies plus
Quartus's fanout duplication; a position-0-only name has one or none) — but it
was written after seeing seeds 1 – 3, where the same expression evaluates to
58 / 3 ≈ 19.  **It is therefore registered as a bar to be scored on seeds
4, 5, 6 ONLY**, and the seeds 1 – 3 value is quoted as history, never as its
score.

### P-1″ — THE SPECIFICITY CONTROL, WHICH NEEDS NO THRESHOLD AT ALL

Between **REF** and **FLAT**, on seeds 4, 5, 6:

* **every** CHAINABLE base name (`st_n`, `stop`, `st_zero_ok`, `ld_b_n`, `pv`,
  `opc_base`, `m_kind`, `seg_override_n`) has **FEWER** cones on FLAT than on
  REF; **and**
* **no** FRONT-END base name (`sigma`, `s1_val`, `it_val`) has fewer.

This says the substitution removed chain copies **and nothing else**, and it is
a two-sided statement with no number in it.

### WHAT THE REPLACEMENT DOES AND DOES NOT BUY

* **If P-1′(c) and P-1″ are MET on seeds 4 – 6**, deliverable D's figures may be
  quoted **as scored on that basis**, with **P-1(c)'s miss carried beside them
  in every quotation**.
* **P-1(a)** (≥ 2 chain boundaries on the worst arc) and **P-1(b)** (segment 0
  the largest single segment) were **MET on seeds 1 – 3 as registered** and are
  unaffected; they are re-reported on seeds 4 – 6 as a confirmation.
* **P-4a and P-4b STAY SCORED ON SEEDS 1 – 3**, where they were registered.
  Seeds 4 – 6 are reported beside them as an additional draw set and are **NOT**
  used to re-score them.
* **MAP ONCE PER PROJECT is preserved**: the seed 4 – 6 fits run with
  `--skip-map` on the db seeds 1 – 3 were fitted from, so all six draws are
  draws of one map.  A second `quartus_map` would also re-roll the A&S
  combinational count, which is not reproducible run to run
  (`ucore_provenance.md` §74.4a).

## §4 WHAT IS **NOT** AMENDED

P-2, P-3, P-4a, P-4b, P-5, P-6 and P-7 are unchanged.  Nothing about the
verdict's wording is changed.  §3.3's two registered null sentences stand.
