WAVE 24 -- the B-1 archive.  2026-09-20.

`0F1B.json.gz.orig` and `83.5.json.gz.orig` are the BYTE-IDENTICAL pre-edit
copies of `tests/v30/v0.3/{0F1B,83.5}.json.gz`, taken before the re-emission
and used to RESTORE them afterwards.  They are 3.0 MB each and they are
DELIBERATELY NOT COMMITTED: `tests/v30/v0.3` is itself disk-only by its own
`.gitignore` ("916 MB; storage/versioning decided at the upstream-contribution
stage"), so an archive of two of its forms has exactly the same status as the
thing it archives.  What IS committed is everything that makes the archive
checkable and the finding quotable:

  SHA256-BEFORE.txt         the suite files and the archive copies, before
  SHA256-AFTER-RESTORE.txt  the suite files after the restore -- IDENTICAL
  original-cases.json       the two ORIGINAL cases in full, by value
  recaptured-2026-09-20.json  the two RE-CAPTURES in full (true silicon,
                            retained outside the suite; full per-clock rows,
                            divider readback, truth-source stamp)

The seeds maps (`*.seeds.json.orig`, 136 KB each) are copies of files that were
never modified; they are kept beside the rest for the same reason.

See docs/notes/invalidation_ledger.md section E.
