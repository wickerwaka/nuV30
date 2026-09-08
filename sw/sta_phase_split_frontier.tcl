# sta_phase_split_frontier.tcl -- WHICH LIVE SOURCE OWNS THE PIN-DEPENDENCE
# FRONTIER?
#
# `sta_phase_split_scan.tcl` measures WHERE pin-dependence enters the binding
# `ce -> ce` cone.  On every draw of the 2026-09-08 anatomy it entered at the
# very END, on a handful of nodes.  This script asks WHICH live register makes
# them pin-dependent -- one `-through` question per (node, live register) pair,
# using the SAME `get_pins` resolver the scan uses and carrying the SAME
# positive control, because the trap it guards against (`get_timing_paths
# -through` silently ignoring a `get_nodes` collection) would answer "nobody"
# for every pair and read as a reassuring result.
#
# ⚠ NOT A GATE, NO RECEIPT.  An attribution, run on an already-fitted `db`.
#
#   quartus_sta -t sw/sta_phase_split_frontier.tcl <proj> <rev> <out> <node> [<node> ...]

set proj  [lindex $quartus(args) 0]
set rev   [lindex $quartus(args) 1]
set out   [lindex $quartus(args) 2]
set nodes [lrange $quartus(args) 3 end]

project_open $proj -revision $rev
create_timing_netlist -model slow -speed 7 -temperature 100 -voltage 1100
read_sdc
update_timing_netlist

set fh [open "$out.frontier.txt" w]
proc emit {s} { global fh ; puts $fh $s ; puts $s }

set v30u_regs [add_to_collection \
                   [get_registers -nowarn {*|v30u_eu:*|*}] \
                   [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]

# the same LIVE_NARROW membership the scan builds, but enumerated one register
# at a time so the answer names a REGISTER and not a collection
set pats {
    {*system_large*|c_ready_q}  {*system_large*|c_int_q}
    {*system_large*|c_nmi_q}    {*system_large*|c_polln_q}
    {*system_large*|c_reset_q}  {*system_large*|c_rdata_q[*]}
    {*system_large*|c_addrv_q}  {*system_large*|core_ad_hold[*]}
    {*system_large*|c_ready_q~*} {*system_large*|c_int_q~*}
    {*system_large*|c_nmi_q~*}  {*system_large*|c_polln_q~*}
    {*system_large*|c_reset_q~*} {*system_large*|c_rdata_q[*]~*}
    {*system_large*|c_addrv_q~*} {*system_large*|core_ad_hold[*]~*}
}
set live {}
foreach p $pats {
    foreach_in_collection r [get_registers -nowarn $p] {
        lappend live [get_node_info $r -name]
    }
}
set live [lsort -unique $live]
emit "=== sta_phase_split_frontier: $proj / $rev ==="
emit "\$v30u_ce [get_collection_size $v30u_ce]   LIVE_NARROW registers [llength $live]"
if {[llength $live] < 4 || [get_collection_size $v30u_ce] < 1000} {
    emit "CONTROL FAILED: a collection is implausibly short.  REFUSING."
    close $fh ; project_close ; exit 3
}

# POSITIVE CONTROL: the worst LIVE -> $v30u_ce path's own FIRST data node must
# be attributable to at least one live register, or the per-register question
# is being asked with an instrument that cannot answer YES.
set allive [get_registers -nowarn {*system_large*|c_ready_q}]
foreach p $pats { set allive [add_to_collection $allive [get_registers -nowarn $p]] }
# ⚠ THE LEAF TEST IS LITERAL, NEVER `string match`.  A register named with a
# bus index is a `string match` PATTERN in which `[3]` is a CHARACTER CLASS,
# so the pattern silently fails to match its own name -- the defect measured on
# `sta_phase_split_scan.tcl` on 2026-09-08 (19 of 50 paths on one draw walked
# as though they had no data path at all).
set cps [get_timing_paths -setup -npaths 1 -detail full_path -from $allive -to $v30u_ce]
set ctlnode ""
foreach_in_collection p $cps {
    set fn   [get_node_info [get_path_info $p -from] -name]
    set leaf [string range $fn [expr {[string last "|" $fn]+1}] end]
    set seen 0
    foreach_in_collection pt [get_path_info $p -arrival_points] {
        set nd [get_point_info $pt -node]
        if {$nd eq ""} continue
        set nm [get_node_info $nd -name]
        if {[string first $leaf $nm] >= 0} { set seen 1 ; continue }
        if {$seen && [get_point_info $pt -type] eq "cell"} { set ctlnode $nm ; break }
    }
}
set ctl_hits 0
if {$ctlnode ne ""} {
    set c [get_pins -nowarn $ctlnode]
    foreach l $live {
        set ps [get_timing_paths -setup -npaths 1 -from [get_registers $l] -through $c -to $v30u_ce]
        if {[get_collection_size $ps] > 0} { incr ctl_hits }
    }
}
emit ""
emit "--- POSITIVE CONTROL ---"
emit "  node: $ctlnode"
emit "  live registers that reach it: $ctl_hits of [llength $live]"
if {$ctlnode eq "" || $ctl_hits == 0} {
    emit "CONTROL FAILED -- the per-register question cannot return YES."
    close $fh ; project_close ; exit 4
}
emit "CONTROL PASSED"

emit ""
emit "=== ATTRIBUTION ==="
foreach node $nodes {
    set c [get_pins -nowarn $node]
    if {[get_collection_size $c] == 0} {
        emit "  $node : UNRESOLVED by get_pins -- no answer, and that is not a NO"
        continue
    }
    set hits {}
    foreach l $live {
        set ps [get_timing_paths -setup -npaths 1 -from [get_registers $l] -through $c -to $v30u_ce]
        if {[get_collection_size $ps] > 0} { lappend hits $l }
    }
    emit ""
    emit "  node: $node"
    emit "    live sources reaching it: [llength $hits] of [llength $live]"
    foreach h $hits { emit "      $h" }
}
close $fh
puts "wrote $out.frontier.txt"
project_close
