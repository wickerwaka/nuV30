RETAINED AND NAMED -- TAKEN ON A DEFECTIVE INSTRUMENT.  NOTHING IS QUOTED FROM
THIS DIRECTORY, AND NO BAR IS SCORED ON IT.

The three CONTROL draws of 2026-09-08 taken with `sw/sta_phase_split_scan.tcl`
AS COMMITTED AT `ce9caea6b0`.  Its path walker located the launch and
destination registers with

        string match "${from_name}*" $node_name

and a Quartus register name carrying a BUS INDEX -- `opc_base[3]`, `tmpb[4]` --
is a `string match` PATTERN in which `[3]` is a CHARACTER CLASS.  The pattern
therefore FAILS TO MATCH ITS OWN NAME.  Demonstrated:

    set fn "…|opc_base\[3\]" ; set nn "…|opc_base\[3\]|q"
    string match "${fn}*" $nn                -> 0    <-- WRONG
    expr {[string first $fn $nn] == 0}       -> 1    <-- correct

CONSEQUENCE, MEASURED IN THIS DIRECTORY: on `seed2` the walker never entered
its DATA phase on **19 of 50 paths**.  Those paths report `cells 0`,
`regO 0`, `pinD 0`, contribute NOTHING to the cut-point census, and their
printed `dataDly` is not a data delay at all -- it still carries the ~9.3 ns
clock-network arrival, which is why `seed2` shows a 58.794 ns "worst
$v30u_ce -> $v30u_ce data delay" against 49.6 ns on every path the walker
actually walked.  Worse, **the 19 failures were absorbed into the
`merge point UNDEFINED` count**, so a WALKER FAILURE was printed as the
RESULT "this path has no pin-dependent node".  That is the vacuous-gate
pattern: an instrument reporting its own silence as an answer.

`seed1` and `seed3` show `merge point UNDEFINED: 0 of 50`, so their walks did
not fail -- but they are discarded from the gate set anyway, because a document
must quote ONE instrument, and the fixed instrument is a different one.

FIXED at the commit that created this directory: the prefix tests are literal
(`hasprefix`), and the scan now counts WALKER FAILURES in a class of their own,
refuses to let one set the worst data delay, and prints the offending path
numbers.  On the re-run the count must read 0.
