# WAVE 2 DIAGNOSIS -- DOES THE BINDING ARC CROSS THE SHADOW?
#
# The landing's G6 came back RED and the binding class is `SAME` at k = 1.  The
# question this answers is the only one that matters for the NEXT wave: after
# the cut, does the worst `ce -> ce` path pass THROUGH `v30u_eu|s1q`, or does it
# run from the microcode ROM to a committed register WITHOUT touching the
# shadow at all?  The second means the cut divided nothing on that arc.
#
# ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection in
# Quartus 17.1 (WAVE 1 §0.2).  `get_pins` is the resolver, and the POSITIVE
# CONTROL below is what makes a NO mean anything: a `-through` on the path's own
# destination register pin must return the path.
project_open nec_test -revision nec_test_ucore
create_timing_netlist -model slow
read_sdc
update_timing_netlist

set fh [open [lindex $quartus(args) 0] w]
proc emit {fh s} { puts $fh $s ; puts $s }

emit $fh "=== sta_phase_split_diag ==="

set core "*v30_core:u_core*"
set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] \
                                 [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
set shadow    [get_registers -nowarn {*|v30u_eu:*|s1q*}]

emit $fh [format "  \$v30u_ce %d   shadow registers matching |s1q* : %d" \
              [get_collection_size $v30u_ce] [get_collection_size $shadow]]

# the worst ce -> ce path
set to ""
set from ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 1 -detail full_path] {
    set from [get_node_info [get_path_info $p -from] -name]
    set to   [get_node_info [get_path_info $p -to] -name]
    emit $fh "  worst ce->ce"
    emit $fh "    from  : $from"
    emit $fh "    to    : $to"
    emit $fh [format "    slack : %+8.3f   logic levels %s" \
                  [get_path_info $p -slack] [get_path_info $p -num_logic_levels]]
    # WALK THE ARRIVAL POINTS AND LOOK FOR THE SHADOW BY NAME.  This is the
    # whole diagnosis: if `s1q` appears on this path, the cut divided it; if it
    # does not, the cut divided something else.
    set nsh 0 ; set ncells 0
    if {![catch {set pts [get_path_info $p -arrival_points]}]} {
        foreach_in_collection pt $pts {
            set nd [lindex [get_point_info $pt -node] 0]
            if {$nd eq ""} { continue }
            set nm [get_node_info $nd -name]
            incr ncells
            if {[string first "|s1q" $nm] >= 0} { incr nsh }
        }
    }
    emit $fh "    arrival points: $ncells   of which name |s1q : $nsh"
}
if {$to eq ""} { emit $fh "  NO ce->ce PATH -- cannot diagnose" ; close $fh ; project_close ; return }

# --- POSITIVE CONTROL: -through the destination register's own D pin ---
set dpin [get_pins -nowarn -compatibility_mode "${to}|d*"]
emit $fh [format "  positive control: -through the destination's own D pin resolves %d pin(s)" \
              [get_collection_size $dpin]]
if {[get_collection_size $dpin] > 0} {
    set n [get_collection_size [get_timing_paths -from $v30u_ce -to $v30u_ce -through $dpin -setup -npaths 1]]
    emit $fh "    -> paths returned: $n   (MUST be 1; 0 means the question cannot say YES)"
}

# --- THE QUESTION: does ANY worst-class path go through the shadow? ---
set nsh 0
foreach_in_collection r $shadow {
    set rn [get_node_info -name $r]
    set qp [get_pins -nowarn -compatibility_mode "${rn}|q*"]
    if {[get_collection_size $qp] == 0} { continue }
    set n [get_collection_size [get_timing_paths -from $v30u_ce -to $to -through $qp -setup -npaths 1]]
    if {$n > 0} { incr nsh }
}
emit $fh "  shadow bits whose Q pin lies on a path INTO the binding destination: $nsh"

# --- and how long is the arc that ENDS at the shadow? (stage 1's own worst) ---
foreach_in_collection p1 [get_timing_paths -from $v30u_ce -to $shadow -setup -npaths 1 -detail full_path] {
    emit $fh "  STAGE 1 (anything -> s1q), worst:"
    emit $fh "    from  : [get_node_info [get_path_info $p1 -from] -name]"
    emit $fh "    to    : [get_node_info [get_path_info $p1 -to] -name]"
    emit $fh [format "    slack : %+8.3f   logic levels %s" \
                  [get_path_info $p1 -slack] [get_path_info $p1 -num_logic_levels]]
}
foreach_in_collection p2 [get_timing_paths -from $shadow -to $v30u_ce -setup -npaths 1 -detail full_path] {
    emit $fh "  STAGE 2 (s1q -> anything), worst:"
    emit $fh "    from  : [get_node_info [get_path_info $p2 -from] -name]"
    emit $fh "    to    : [get_node_info [get_path_info $p2 -to] -name]"
    emit $fh [format "    slack : %+8.3f   logic levels %s" \
                  [get_path_info $p2 -slack] [get_path_info $p2 -num_logic_levels]]
}
close $fh
project_close
