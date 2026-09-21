WAVE 28 / FLASH #24 -- artifacts by value.
USER AUTHORISATION 2026-09-21: "Flash it".
Pre-registration  docs/notes/flash24_prereg_2026-09-21.md   (eb3be735a1)
Results           docs/notes/flash24_results_2026-09-21.md

THE BITSTREAM
  nec_test_ucore.sof 3066d40a558486c61becf490c451d351a5c3da8156109f6fbedd2927f0ae1833
  nec_test_ucore.rbf 44cfd64791781752e89f1a86be9cafd85471dc32fb1aa9ce17ee4ae8023418c7
  RETENTION (X1_AD_RETENTION=1) draw@seed1, receipt 8077ba94656880ef…
  G6 records: sw/testdata/g6dist/FLASH#24 {CONTROL,RETENTION} draw@seed1/

OFFLINE, BEFORE THE BOARD
  g6_control_seed1.log          the CONTROL build (34.35 MHz, rbf aa931892f7a69668…)
  g6_retention_seed1.log        the RETENTION build (34.59 MHz, rbf 44cfd64791781752…)
  e6_envvar_refusal.txt         E-6: X1_AD_RETENTION=1 in the ENVIRONMENT exits 2
  era_guard_preflash.txt        the fabric era guard REFUSING at HEAD, naming the
                                six moved declared inputs.  A guard that passes
                                before a flash is a guard that is not working.
  ucore_verilator_recheck.{log,json}
                                the Verilator ucore EA column re-measured at HEAD
                                BEFORE the pre-registration was committed: 21/21.
  tbsys_build.log               the landed tree's tb_sys (ret), receipt 03c861175b6313d5…
  w28_replay_prediction.{json,log}
                                THE NULL, DERIVED: fz2_replay run PREDICTIVELY on
                                this tree against the F23 ledger (era guard
                                deliberately bypassed and said so).  252 seeds,
                                6 closers named, 0 entrants among 150 sampled
                                passes.  This is what the prereg registered.

THE EA-LANE LAW IN FABRIC  (sw/w28_ea_lane_fabric.py)
  ea_fabric_preflash/           --expect before, on the RESIDENT FLASH #23
  ea_fabric_preflash.log        bitstream.  PAIRWISE 7/21, core column
                                value-for-value = the pre-landing Verilator
                                column, 21/21.  THE NON-VACUITY CONTROL.
  ea_fabric_postflash/          --expect after, on FLASH #24.  PAIRWISE 21/21,
  ea_fabric_postflash.log       socket positive control REPRO 21/21.
                                Each directory holds 8D_socket.json.gz,
                                8D_core.json.gz (FULL per-clock rows) and a
                                manifest naming each leg's use_core, its sha256
                                and the divider readback.

THE FLASH AND THE BOARD
  safe_flash.log                VERIFY ok, TRY 1.  flash_log 26 -> 27.
  first_light.log               check_ab_hw all 800 -> MATCH 800 x3
  fz2_lint.log fz2_control.log fz2_preflight.log fz2_capture.log
  fz2_ledger.log fz2_bars.log   the corpus legs
  closing_chip_proof.log        check_ab_hw chip 800 -> MATCH, after everything
  board_idle.log                board_idle, LAST
  w28_replay_closing.{json,log} the closing control, era guard PASSING with no
                                bypass at 98/98: 247/247 = 100.0 %
  fz2_immaterial_falsify.log    MEASURED, NOT REGISTERED.  G1-G5,G8 PASS,
                                G6/G7 FAIL on inherited document staleness --
                                the same state FLASH #23 registered as C-16c.

THE A/B THAT ATTRIBUTES THE MOVEMENT   (a git worktree at 56bdf8d851, the tree
immediately BEFORE the landing; its tb_sys receipt 3ca720bf73bf3ed8…; scored
against the SAME regenerated images and the SAME banked socket rows)
  prelanding_tbsys_build.log
  prelanding_ab_closers.{json,log}   the six closers FAIL 6/6 there,
                                     first_bad IDENTICAL -- and PASS 6/6 on the
                                     landed tree.
  prelanding_ab_entrant.{json,log}   fz2e/527035 scores bad 0 there, and 753 /
                                     first_bad 431 on the landed tree, which is
                                     what fabric reads.  THE ONE UNREGISTERED
                                     ENTRANT IS THE FIX'S COST.  NET +5.
  The worktree was removed with `git worktree remove` once these were kept.

THE LADDER
  w28_ladder.sh                 the driver; every RC via ${PIPESTATUS[0]}
  ladder/                       one log per leg + rc.txt
  w28_ladder_cmp.py             THE FALSIFIER: leg-by-leg scored-line comparison
                                against sw/testdata/wave27/ladder.  This wave
                                edits no hdl/, so the expectation is
                                SAME on every leg, 0 MOVED, 0 GONE, 0 NEW.
