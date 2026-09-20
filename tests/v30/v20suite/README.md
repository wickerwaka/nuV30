# V20 SingleStepTests data (local cache)

Gzipped JSON test files from https://github.com/SingleStepTests/v20
(branch `main`, suite v1.0.3, MIT license), used by `sw/pilot_v20.py`
for architectural cross-validation of the real V30 — including the
mission 12 unmasked-flags comparison (docs/facts/undefined_flags.md).

The `.json.gz` files are not committed (re-fetchable); `metadata.json`
(opcode status/flags-mask database) is. To restore the working set:

    cd tests/v30/v20suite
    for f in 00 27 37 B8 D2.4 F6.4 F6.6; do
      curl -sfO "https://raw.githubusercontent.com/SingleStepTests/v20/main/v1_native/$f.json.gz"
    done

Fetched 2026-07-10 (00/37/B8/metadata) and 2026-07-11 (27/D2.4/F6.4/F6.6).

## ⚠ WAVE 22, 2026-09-19 — THIS README IS STALE IN THREE WAYS, MEASURED

Recorded here rather than rewritten, because the restore recipe above is the
only record of how the first seven forms arrived.

1. **THE WORKING SET IS NO LONGER SEVEN FORMS.**  Measured on disk:
   **360 forms, 3,125,000 cases** (plus an `iords/` sidecar directory).  The
   `for f in 00 27 37 B8 D2.4 F6.4 F6.6` loop restores 7 of them.  Whoever
   expanded it did not update this file; the expansion is untracked working
   data, exactly as `.gitignore` intends.
2. **THE VERSIONS DISAGREE.**  This file says upstream *suite v1.0.3*;
   `metadata.json` says `"version": "1.0.2"`.  Unresolved — it is a question
   about which upstream snapshot is on disk, and WAVE 22 did not answer it.
3. **`sw/pilot_v20.py` IS NO LONGER THE ONLY CONSUMER.**  Since 2026-09-19 the
   suite is scored against the ucore by
   `python3 sw/check_core.py --core ucore --suite-dir tests/v30/v20suite
   --opcodes all --cases 0 --arch-only` — **`--arch-only` is required**: it is a
   µPD70108 (V20, 8-bit bus) capture, so the per-cycle rows are not comparable
   with a V30 core and only the architectural result is.  Without the flag the
   suite scores 0.  See `docs/notes/suite_scorer_prereg_2026-09-19.md`.

## ⚠ `metadata.toml` IS PRESENT ON DISK AND UNTRACKED — NOT A DIVERGENCE

It is upstream SingleStepTests' native manifest form; `metadata.json` (tracked)
is the converted copy the scorers read.  WAVE 22 parsed both without modifying
either: **the same 8 header keys with byte-equal values, the same 282 opcode
entries, 0 keys present in only one, 0 entries differing.**  There is nothing to
decide between them.  Whether to track the `.toml` is the repository owner's
call and WAVE 22 deliberately did not make it.
