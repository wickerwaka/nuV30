# WAVE 4 DIAGNOSIS -- C-3(b) AND C-8.  DOES THE BINDING ARC CROSS THE SHADOW,
# AND IS THERE A `ce -> ce` ARC THAT TOUCHES NEITHER STAGE?
#
# WAVE 2's answer to the first question was **ZERO of 103 arrival points** and
# that is why it failed (`phase_split_landing_results_2026-09-08.md` §11.6).
# The third class -- an arc that neither ENDS at the shadow nor LAUNCHES from it
# -- IS WAVE 2's FAILURE SIGNATURE, and C-8 asks for it by name: "The third must
# not exist; if it does, name it -- that is the next cut."
#
# ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection in
# Quartus 17.1 (WAVE 1 §0.2).  `get_pins` is the resolver, and the POSITIVE
# CONTROL below is what makes a NO mean anything.
# ⚠ `string match` on a register name carrying a bus index FAILS (`[3]` is a
# character class, WAVE 1 §3.0).  Every test here is `string first`.
project_open nec_test -revision nec_test_ucore
create_timing_netlist -model slow
read_sdc
update_timing_netlist

set fh [open [lindex $quartus(args) 2] w]   # 2, not 0 -- args are {proj rev out}
proc emit {fh s} { puts $fh $s ; puts $s }

emit $fh "=== sta_cutset_diag (WAVE 4) ==="

set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] \
                                 [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
set shadow    [get_registers -nowarn {*|v30u_eu:*|s1q*}]

emit $fh [format "  \$v30u_ce %d   shadow registers matching |s1q* : %d" \
              [get_collection_size $v30u_ce] [get_collection_size $shadow]]

# ---------------------------------------------------------------- the worst
set to "" ; set from ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 1 -detail full_path] {
    set from [get_node_info [get_path_info $p -from] -name]
    set to   [get_node_info [get_path_info $p -to] -name]
    emit $fh "  worst ce->ce"
    emit $fh "    from  : $from"
    emit $fh "    to    : $to"
    emit $fh [format "    slack : %+8.3f   logic levels %s   data delay %s" \
                  [get_path_info $p -slack] [get_path_info $p -num_logic_levels] \
                  [get_path_info $p -data_delay]]
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
    emit $fh "    arrival points: $ncells   of which name |s1q : $nsh    <<<< C-3(b)"
}
if {$to eq ""} { emit $fh "  NO ce->ce PATH -- cannot diagnose" ; close $fh ; project_close ; return }

# --------------------------------------------- POSITIVE CONTROL (WAVE 1 §0.2)
set dpin [get_pins -nowarn -compatibility_mode "${to}|d*"]
emit $fh [format "  positive control: -through the destination's own D pin resolves %d pin(s)" \
              [get_collection_size $dpin]]
if {[get_collection_size $dpin] > 0} {
    set n [get_collection_size [get_timing_paths -from $v30u_ce -to $v30u_ce -through $dpin -setup -npaths 1]]
    emit $fh "    -> paths returned: $n   (MUST be 1; 0 means the question cannot say YES)"
}

# ------------------------------------------------------------------ C-8
# Classify the top 200 `ce -> ce` paths.  A path ENDS at the shadow (STAGE 1),
# LAUNCHES from it (STAGE 2), or does NEITHER -- and the third class is WAVE 2's
# failure signature.
set n1 0 ; set n2 0 ; set n0 0
set w1 "" ; set w2 "" ; set w0 ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 200 -detail path_only] {
    set f [get_node_info [get_path_info $p -from] -name]
    set t [get_node_info [get_path_info $p -to] -name]
    set s [get_path_info $p -slack]
    set l [get_path_info $p -num_logic_levels]
    set d [get_path_info $p -data_delay]
    set row [format "%+8.3f  levels %-3s  data %-8s  %s  ->  %s" $s $l $d $f $t]
    set isf [expr {[string first "|s1q" $f] >= 0}]
    set ist [expr {[string first "|s1q" $t] >= 0}]
    if {$ist} { incr n1 ; if {$w1 eq ""} { set w1 $row }
    } elseif {$isf} { incr n2 ; if {$w2 eq ""} { set w2 $row }
    } else { incr n0 ; if {$w0 eq ""} { set w0 $row } }
}
emit $fh "  --- C-8: the top 200 ce->ce paths, classified ---"
emit $fh "    STAGE 1  (* -> s1q)       count $n1"
emit $fh "      worst: $w1"
emit $fh "    STAGE 2  (s1q -> *)       count $n2"
emit $fh "      worst: $w2"
emit $fh "    NEITHER  (WAVE 2's signature)  count $n0"
emit $fh "      worst: $w0"

# ---------------------------------- the two stages' own worst, full detail
foreach_in_collection p1 [get_timing_paths -from $v30u_ce -to $shadow -setup -npaths 1 -detail full_path] {
    emit $fh "  STAGE 1 (anything -> s1q), worst:"
    emit $fh "    from  : [get_node_info [get_path_info $p1 -from] -name]"
    emit $fh "    to    : [get_node_info [get_path_info $p1 -to] -name]"
    emit $fh [format "    slack : %+8.3f   logic levels %s   data delay %s" \
                  [get_path_info $p1 -slack] [get_path_info $p1 -num_logic_levels] \
                  [get_path_info $p1 -data_delay]]
}
foreach_in_collection p2 [get_timing_paths -from $shadow -to $v30u_ce -setup -npaths 1 -detail full_path] {
    emit $fh "  STAGE 2 (s1q -> anything), worst:"
    emit $fh "    from  : [get_node_info [get_path_info $p2 -from] -name]"
    emit $fh "    to    : [get_node_info [get_path_info $p2 -to] -name]"
    emit $fh [format "    slack : %+8.3f   logic levels %s   data delay %s" \
                  [get_path_info $p2 -slack] [get_path_info $p2 -num_logic_levels] \
                  [get_path_info $p2 -data_delay]]
}
close $fh
project_close
