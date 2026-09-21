WAVE 26 -- THE RETAINED EA LANE TAKES THE ADDRESS ADDER'S SECOND ADDEND.
Artifacts by value.

  synth-manifest-before.txt   sha256 of the 107 tracked files Quartus reads,
  synth-manifest-after.txt    before and after the landing.  FOUR MOVED, all
                              four in hdl/rtl/ucore/ -- so THE BITSTREAM
                              MOVED and FLASH #23 no longer covers the tree.

  b2b/8D.json.gz              the WAVE 26 directed SOCKET capture: WAVE 24's
  b2b/manifest.json           thirteen probes kept verbatim as reproduction
                              controls (13/13 REPRO) plus EIGHT mod=01/10
                              rows that close WAVE 24's declared reference
                              gap.  Full per-clock rows retained.  Divider
                              readback recorded per probe.  Rig:
                              sw/w26_ea_lane2.py, committed BEFORE contact.
  b2b/ucore_columns.json      the LANDED core against that capture: 21/21.
  b2b/ucore_columns_before.json   the PRE-landing core against it: 7/21.

  decomp.txt                  the read-only perturbation diagnostic that
  w26_decomp.py               located the defect without an RTL edit: one
                              register (or the body address) moved at a time,
                              whole-program replay, no backdoor injection.

  ladder/{before,after}/      every ladder leg's raw log, both sides, and
                              rc.txt with each leg's ${PIPESTATUS[0]}.
                              The AFTER side was measured in a git worktree
                              whose Verilator build_key is IDENTICAL to the
                              landed tree's (340b3a9b7bd64523...), which is
                              why the two columns are comparable.

  landed/confirm.log          the confirmation subset re-run on the LANDED
                              main tree.

  The G6 distributions are sw/testdata/g6dist/WAVE26 ea second-addend
  {CONTROL,RETENTION}/ -- five seeds each, worst-of-5 33.76 / 34.16 MHz.
