WAVE 29 -- THE PROVENANCE STAMP IS ONE DERIVATION AND IT CAN REFUSE
===================================================================
Results document: docs/notes/truth_stamp_results_2026-09-21.md
Ledger entry:     docs/notes/invalidation_ledger.md  PRV-1  (a SEVENTH register,
                  disposition ANNOTATE NEVER REWRITE)
Landing:          40642891fb

  truth_stamp_lint.log          the new standing gate, PASS 23/23
  truth_stamp_nonvacuity.log    its OWN two non-vacuity controls, both FAILING
                                as registered (NV-1 a spliced second literal;
                                NV-2 the derivation reverted to the WAVE 28
                                behaviour) and then restored to PASS 23/23
  s12_regold_prv1_writer.log    PRV-1's own writer, MEASURED: 0/49 goldens
                                re-derived.  PRE-EXISTING (WAVE 24 ledger-E
                                class), and the reason the BANKED REPLAY stamp
                                could not be exercised end-to-end.  Retained
                                because a caveat with no artifact is not a
                                caveat
  w29_ladder.sh                 WAVE 28's ladder verbatim + ONE new leg
  w29_ladder_cmp.py             the zero-delta comparison against wave28/ladder
  ladder/                       39 legs, one log each, rc.txt
  ladder_cmp.txt                the comparison's output

NO hdl/.  NO Quartus.  NO board.  NO flash -- FLASH #24 stands, flash_log.jsonl
27 entries, sha256 7496b4be2d1771c9...
