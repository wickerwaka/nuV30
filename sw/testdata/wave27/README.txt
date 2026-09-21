WAVE 27 -- REMOVE THE `v0.2` SUITE.  Artifacts by value.
User directive 2026-09-21: "Remove v0.2, v0.3 supersedes it".
Ledger: docs/notes/invalidation_ledger.md RET-3.

  z1_scan.txt          the full 347-form positional scan of tests/v30/v0.2
                       against tests/v30/v0.3's first-1,000-per-form prefix.
                       347,000 cases; 7,127 not reproduced, in 12 forms; the
                       shifted/absent split; and the KEY POSITIVE CONTROL (0
                       equal-hash pairs that are not byte-identical).
                       PRODUCED BEFORE THE DELETION -- it cannot be re-run.

  z1_keys.txt          the same diff under SEVEN comparison keys.  Every
                       whole-record key returns 7,127.  NO key returns the
                       7,137 that tests/v30/v0.3/README.md quotes.

  z2_reproduction.txt  Z-2.  Per form, the sha256 of the ordered `i:hash` list
                       AND of the ordered RECORD BODIES over the reproduced
                       positions, computed on BOTH sides.  347/347 forms agree
                       on both digests; 339,873 cases reproduced byte for byte
                       at the same index.

  z2_reroll_class.txt  reroll-vs-different-draw, with its own positive control:
                       v0.3's committed XX.seeds.json maps are reconstructed
                       from v0.3's OWN emit_log on 370/370 forms (107 of them
                       non-identity, so the equality is not trivial).  Of the
                       1,237 cases absent from v0.3 entirely: 1,152 are the SAME
                       seed attempt drawn differently, 85 are seed attempts
                       v0.3's generator REROLLED AWAY.

  w27_prefix_scan.py   the three instruments, kept by value.  THEY CANNOT RUN
  w27_reroll_class.py  ON THIS TREE ANY MORE -- tests/v30/v0.2/ is gone and was
  w27_keys.py          not in git.  They are the method, recorded.

  The LIVE falsifier is `python3 sw/w27_v02_archive_check.py`, which needs only
  the archive and v0.3.
