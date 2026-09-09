# WAVE 4 -- THE ARRIVAL-POINT DUMP.  A PROBE, NOT A GATE.
#
# `sw/sta_cutset_diag.tcl` COUNTS the arrival points of the binding `ce -> ce`
# path; this prints them, one per line, with the cumulative arrival time.  It
# exists because a COUNT can be wrong for a reason a count cannot show -- the
# diag's own BIU clause matched the TYPE prefix `v30u_biu:`, which Quartus puts
# on register names and omits on combinational node names, and reported
# `v30u_biu : 0` on a path carrying EIGHT BIU LUTs.  The dump is what found
# that, and it is what named both of this wave's leaks to the node.
#
# args: {project revision outfile}.  ⚠ The comment is on its own line: Tcl has
# no trailing `#`.
project_open nec_test -revision nec_test_ucore
create_timing_netlist -model slow
read_sdc
update_timing_netlist
set fh [open [lindex $quartus(args) 2] w]
set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 1 -detail full_path] {
    foreach_in_collection pt [get_path_info $p -arrival_points] {
        set nd [lindex [get_point_info $pt -node] 0]
        if {$nd eq ""} { continue }
        puts $fh [format "%9.3f  %s" [get_point_info $pt -total] [get_node_info $nd -name]]
    }
}
close $fh
project_close
