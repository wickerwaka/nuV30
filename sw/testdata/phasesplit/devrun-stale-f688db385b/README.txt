DEVELOPMENT RUN OF sw/sta_phase_split_scan.tcl -- NOT A RESULT OF THIS TREE.

Taken on the `hdl/db` that was already on disk, which was fitted at
`f688db385b` -- TWO COMMITS BEHIND the tree this wave measures (`c0633d7685`),
and both intervening commits touch `hdl/rtl/ucore/v30u_eu.sv` (`e61f2e0988`
the REP CL==0 ALU-width fix, `c59d205479` the REP-termination fix).  Its seed
is whatever the on-disk fit used and was not recorded by this driver.

⚠ THESE NUMBERS ARE SCORED AGAINST NO BAR AND MAY NOT BE QUOTED AS A RESULT.
They are retained because the run happened BEFORE the wave's bars were
committed and saw the answer; declaring it is what lets a reader tell fitting
from pre-registration (`phase_split_anatomy_2026-09-08.md` §1.0).

What it was FOR, and what it found:
  * proved `get_pins` resolves a node name and `get_nodes` is silently ignored
    by `get_timing_paths -through` (the §0.2 table);
  * timed the scan (~20 s of quartus_sta wall time for 50 paths);
  * FOUND the first-occurrence-census defect -- `st_n`, `ld_b_n`, `always6` and
    `Ram*` appear several times on one path because the EU chain loop is
    unrolled -- which is why the committed instrument is occurrence-indexed.

`dev2.phasesplit.txt` was produced by the instrument AS COMMITTED at
`ce9caea6b0`.  An earlier, pre-occurrence-index output is NOT retained: it was
produced by a version of the script that does not exist in any commit.
