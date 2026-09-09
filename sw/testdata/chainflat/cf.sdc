# WAVE 6 -- the standalone harness's SDC.  NO `set_multicycle_path`: the
# USER RULING of 2026-09-08 makes the NO-EXCEPTION configuration the goal state,
# and the whole point of the measurement is the `ce -> ce` arc under it.
create_clock -name clk -period 31.250 [get_ports clk]
derive_clock_uncertainty
set_false_path -from [get_ports *]
set_false_path -to   [get_ports *]
