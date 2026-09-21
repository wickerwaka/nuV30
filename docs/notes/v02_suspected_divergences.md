> # ⚠⚠ WAVE 27 HEADER, 2026-09-21 — **THE SUITE THIS DOCUMENT IS ABOUT NO LONGER EXISTS.**
>
> `tests/v30/v0.2/` was DELETED on user instruction (*"Remove v0.2, v0.3
> supersedes it"*), `docs/notes/invalidation_ledger.md` **RET-3**.  **It was not
> in git and it is not recoverable.**  Every case coordinate below (`INT.90/239`,
> `INT.9D/44,62,954`, `INT.FB/142,368,730`) names an index in a suite that is
> gone; the WAVE 24 re-measurement that closed them is unaffected, because a form
> that scored 1000/1000 had no failing index in it and the same three forms are
> scored 10,000 deep in `v0.3`.  **THE DOCUMENT IS RETAINED AND UNEDITED BELOW
> THIS LINE.**
>
> ---
>
> # ⚠ WAVE 24 HEADER, 2026-09-20 — **THIS DOCUMENT IS FSM-ERA HISTORY. RETAINED, NOT DELETED.**
>
> **DATED 2026-07-18.**  `hdl/rtl/ucore/` — the only implementation this repo
> now has — **first appears at `0bfea2bfd0`, 2026-08-03**, sixteen days later.
> The trace-fitted FSM core this document was written against was archived
> 2026-08-04 (`80d9cc8228`) and REMOVED 2026-09-19
> (`docs/notes/invalidation_ledger.md` **RET-2**).  **Nothing below is evidence
> about the ucore** (USER RULING 2026-09-19: *"treat the documentation as
> hearsay until proven otherwise"*).
>
> **RE-MEASURED AGAINST THE ucore, 2026-09-20 — ALL SEVEN PASS.**  The seven
> cases this document escalated as *"a genuine chip-vs-RTL disagreement"*
> (`INT.90/239`, `INT.9D/44,62,954`, `INT.FB/142,368,730`) are scored by
> whole-form inclusion:
>
> ```
> python3 sw/check_core.py --core ucore --suite-dir tests/v30/v0.2 \
>                          --opcodes INT.90,INT.9D,INT.FB --cases 0
> INT.90: 1000/1000 full   INT.9D: 1000/1000 full   INT.FB: 1000/1000 full
> TOTAL: 3000/3000 full (cycles 3000, arch 3000)
> ```
>
> **The document's own closing section already said why** — the seven are the
> `final.flags` store-stub CAPTURE CONVENTION, closed under task #21 by
> re-deriving 269 v0.2 pin-event goldens host-side.  **The SUITE was edited, not
> the RTL**, and the suite on disk carries that fix.  The escalation stands as
> history and is not a live lead.  `docs/notes/suite_divergence_results_2026-09-20.md`.

# v0.2 suspected real divergences (KEEP + escalated) — 2026-07-18

Found during the flat-validity three-way discrimination of the collision re-emission.
These 7 cases fail BOTH memory models (got(flat) == got(mirror) != chip golden) -> NOT
mirror-dependent; a genuine chip-vs-RTL disagreement. Per the escalation rule they are
KEPT in v0.2 (never rerolled away) and flagged as an RTL lead.

All are pin-event (interrupt) cases; the divergence is in the FINAL FLAGS after the
instruction + interrupt entry + handler. Memory-model-independent.

  form     idx   exp_flags got(flat=mirror)  xor(diff bits)
  INT.90   239   f086      f856              08d0  (AC,Z,S,OF)
  INT.9D    44   f407      f0c6              04c1  (CY,Z,S,DF)
  INT.9D    62   f816      fc17              0401  (CY,DF)
  INT.9D   954   f403      f853              0c50  (AC,Z,DF,OF)
  INT.FB   142   f083      f852              08d1  (CY,AC,Z,S,OF)
  INT.FB   368   f857      f806              0051  (CY,AC,Z)
  INT.FB   730   f083      f0c3              0040  (Z)

INT.90 = nop <int>, INT.9D = pop psw <int>, INT.FB = ei <int>, all with various int
delays (d=1..8). Hypothesis: interrupt-boundary flag handling / the exact cycle the INT
is sampled relative to instruction retirement (pin-event timing sensitivity), or a real
interrupt-entry flag-masking bug. v0.1 pin-event goldens (w0) passed 169000/169000, so
these specific seed/delay combinations expose behavior v0.1's cases did not. NEEDS RTL
investigation - reported to coordinator, not fixed here.

## INVESTIGATION UPDATE (2026-07-18) — NOT an RTL execution bug; pin-event capture convention

Probe (before any RTL change): for all 7, the SIM's CYCLE trace matches the chip golden
EXACTLY (cycles_ok=True) - including the INTA position, i.e. the STI/POPF interrupt-
acceptance inhibit-shadow is honored correctly by our RTL. The divergence is ONLY in the
extracted final.flags. So this is NOT the inhibit-shadow hypothesis and NOT a timing bug.

Discrimination against the interrupt-PUSHED PSW (in final.ram, the true architectural
result) normalized (IE/BRK cleared):
  INT.90/239, INT.FB/142,368,730 (4): SIM == pushed_norm (ARCH-CORRECT); golden != it.
    -> CAPTURE ARTIFACT. The golden's final.flags (store-stub PUSH PSW, captured AFTER the
       handler) is contaminated with an architecturally-impossible value (EI/nop+interrupt
       cannot change arithmetic flags). OUR RTL IS CORRECT.
  INT.9D/44,62,954 (3, pop psw <int>): NEITHER SIM nor golden == pushed_norm. The pushed
    PSW itself is un-normalized (e.g. 0xec92, reserved bit12=0). More complex - POP PSW's
    own inhibit-shadow + interrupt + reserved-bit normalization. OPEN: needs deeper analysis;
    could be capture OR a real pop-psw/shadow interaction.

WHY w0 passed pin-event forms: passing cases have final.flags == initial (sparse final.regs
OMITS unchanged flags); the contamination only surfaces when the store-stub capture records
a CHANGED value, which is rare (3/1000/form) and specific. So the w0 gate for pin-event
forms was testing final.flags-when-changed, which its 200 cases/form rarely exercised in a
contaminating way.

PROPOSED (instrument, pre-registered gate to follow): extract pin-event final.flags from the
interrupt-PUSHED PSW (architectural result), not the post-handler store-stub PUSH PSW; re-
validate ALL pin-event goldens in v0.1 + v0.2. Hold for coordinator direction on the INT.9D
sub-case first.

## OPEN QUESTION — 0F31/0F26 same-seed re-capture non-determinism (logged, not chased)
Re-emitting some 0F31 (INS/EXT bit-field) and 0F26 (CMP4S) cases at the SAME seed produced
a DIFFERENT golden than the file (the three-way re-emit's attempt-0 classified them differently
than the file golden had). Emission non-determinism on these ops is itself a lead - possibly
state-dependent / uninitialized-input behavior. Recorded for later; not investigated now.

## RESOLUTION (2026-07-18) — ALL 7 are the store-stub final.flags convention artifact; NO RTL bug

Direction (b) dig into INT.9D (pop psw) REVERSED my earlier "3 open" read and RESOLVED it:
my initial pushed-PSW read used the wrong stack offset (POP PSW increments SP; the bit12=0
"novel silicon" observation was me misreading the CS push as the PSW push). Correct read
(interrupt-push MEMW data, robust via sim recs):

  INT.9D idx44/62/954: chip interrupt-pushed PSW = f607 / 17fe / f603; OUR RTL's interrupt
  push MATCHES EXACTLY (f607 / 17fe / f603). So our RTL correctly commits the popped flags
  and pushes the right PSW. The golden final.flags (f407=f607&~0x300 etc) is CORRECT; the
  SIM's store-stub final.flags (f0c6) is the contaminated field. Under the correct convention
  (final.flags = interrupt-pushed PSW & ~0x300) both sides agree -> passes.

So ALL 7 (INT.90, INT.FB x3, INT.9D x3) are the SAME artifact: the `final.flags` field, when
present, is the POST-HANDLER store-stub PUSH PSW, which is UNRELIABLE for pin-event forms
(contaminated case-dependently on EITHER side). The interrupt-PUSHED PSW (in the trace /
recoverable from final.ram) is the reliable architectural result and MATCHES chip<->RTL for
all 7. NO RTL DIVERGENCE. The 7 fail only because chip and RTL contaminated the store-stub
field differently for those specific cases.

CONVENTION FIX (approved): pin-event final.flags := interrupt-pushed PSW & ~0x300 (IE/BRK
cleared). Note: an exposure scan needs a ROBUST interrupt-PSW-push extraction (a naive
golden-cycle col-6/T1 read mis-picks odd-address byte-split and non-PSW writes; the sim-recs
extraction used for the 7 is correct). w0 passes today because chip and RTL agree on the
contaminated store-stub value for all v0.1 cases; only 7 v0.2 cases diverge.

## TASK #21 CLOSED (2026-07-18) — instrument fix landed, gate green

Convention: pin-event/trap `final.flags` := interrupt-pushed PSW & ~0x300 (recoverable
from each case's final.ram at SS:(dumped_sp+4); POP-PSW pushes that leave memory unchanged
fall back to initial ram). Applied:
- check_core: pin-event/handler-close cases compare the DERIVED pushed-PSW on both sides
  (validated via the cycle-trace push), not the store-stub field; guarded to fired-interrupt
  cases only (valid PSW reserved bits 15:12=1) so masked/no-fire pin-events (IE0.90) keep the
  normal comparison. v0.1 byte-untouched.
- v0.2: 269 contaminated pin-event cases re-derived host-side (final.flags <- pushed PSW),
  hashes updated. 4000 no-fire cases (IE0.90 etc.) correctly untouched.
- emit_evt_case + emit_case: handler-close final.flags derived from the pushed PSW for all
  future emission (10k).
GATE (green): 7 artifacts pass; v0.2 pin-event 15000/15000; v0.1 pin-event 3000/3000; w0
169000/169000. NO RTL change (RTL was correct all along).
