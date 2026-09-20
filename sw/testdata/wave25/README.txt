WAVE 25 -- THE TESTBENCH RE-LATCH DEFECT.  Artifacts by value.

  synth-manifest-before.txt  sha256 of the 107 tracked files Quartus reads,
  synth-manifest-after.txt   before and after the landing.  IDENTICAL, and
                             IDENTICAL to WAVE 23's after-manifest -- so the
                             bitstream does not move and FLASH #23 still
                             covers the tree.

  w25_predicate.py           dumps WAVE 24's A-3 predicate (the case's
                             continuation point has a recorded non-0x90 byte
                             within 4) to JSON.  Re-derived here: 2,284 of
                             3,125,000, all eight failures inside.

  w25_leakprobe_driver.py    the driver used with a TEMPORARY in-TB counter to
                             measure the cross-case `fin_ghost` leak.  The
                             counter is NOT in the landed testbench; the
                             measurement is 0 over 3,644,883 cases and is
                             recorded in the block's own comment.

  ladder/                    every leg's raw log, both sides.

  The directed control itself is WAVE 24's and is unchanged:
  sw/testdata/wave24/a3/a3_build.py.
