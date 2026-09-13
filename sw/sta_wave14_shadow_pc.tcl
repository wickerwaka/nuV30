# WAVE 14 -- THE POSITIVE CONTROL `sta_cutset_diag.tcl`'s STAGE ROWS NEVER HAD.
#
# WHY IT EXISTS.  On this wave's ARM netlists `sta_cutset_diag.tcl` reported
#   "STAGE 1 (anything -> s1q), worst: ... to : ...|u_eu|v1~24_OTERM7145"
# -- a destination whose name does NOT contain `s1q`, so it cannot be in the
# `-to` collection the query was given.  On the BASE netlists the same query
# returned `s1q[730]` and `s1q[738]~DUPLICATE`, which are.  Either `-to` was
# honoured and the netlist holds a shadow register under another name, or `-to`
# was SILENTLY IGNORED -- the WAVE 1 sec.0.2 family, which has now bitten this
# campaign with `-through` (get_nodes), with `-through` in bulk (PC-W4, 14 of 34
# draws) and possibly here.  A STAGE figure taken under an ignored constraint is
# the whole `ce -> ce` worst path wearing a stage's label.
#
# THE ONE THING THIS FILE DOES: ask, on the netlist as it stands, whether
# `-to <register collection>` is honoured -- and prove the question can say YES.
#
#   PC-S1  the collection is non-empty and its members are NAMED.
#   PC-S2  FORCE `-to` to ONE register taken from that collection, BY NODE
#          OBJECT (no name to spell -- WAVE 10 sec.1.1 item 4).  The returned
#          path's destination MUST be that register.  If this fails, `-to` is
#          not honoured at all and NO stage figure on this netlist is readable.
#   PC-S3  the FREE query `-from $v30u_ce -to $shadow`: report the top 5
#          destinations and whether each is IN the collection, tested by
#          COLLECTION MEMBERSHIP (get_node_info -name compared against the
#          collection's own names), never by eyeballing a string.
#   PC-S4  the KNOWN-WRONG form, printed beside it: the same query with the
#          collection passed as `get_nodes`, which WAVE 1 sec.0.2 says is
#          silently ignored.
#
# args: {project revision OUTFILE}
project_open [lindex $quartus(args) 0] -revision [lindex $quartus(args) 1]
create_timing_netlist -model slow
read_sdc
update_timing_netlist

set fh [open [lindex $quartus(args) 2] w]
proc emit {s} { global fh ; puts $fh $s ; puts $s }

emit "=== sta_wave14_shadow_pc ==="

set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] \
                                 [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
set shadow    [get_registers -nowarn {*|v30u_eu:*|s1q*}]

set snames {}
foreach_in_collection r $shadow { lappend snames [get_node_info -name $r] }
emit [format "  PC-S1  \$v30u_ce %d   \$shadow %d" \
          [get_collection_size $v30u_ce] [llength $snames]]
emit "         first three shadow names:"
foreach n [lrange $snames 0 2] { emit "           $n" }
if {[llength $snames] < 1} { emit "  *** PC-S1 FAILED ***" ; close $fh ; project_close ; return }

# --- PC-S2: force -to ONE register, BY NODE OBJECT.
set one ""
foreach_in_collection r $shadow { set one $r ; break }
set onename [get_node_info -name $one]
set got ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $one -setup -npaths 1] {
    set got [get_node_info [get_path_info $p -to] -name]
}
emit "  PC-S2  forced -to ONE register (node object): $onename"
emit "         path returned, destination            : [expr {$got eq "" ? "*** NONE ***" : $got}]"
emit [format "         VERDICT: %s" [expr {$got eq $onename ? "PASS -- `-to` IS honoured" : "*** FAIL -- `-to` IS NOT HONOURED ON THIS NETLIST ***"}]]

# --- PC-S3: the free query, membership-tested.
emit "  PC-S3  the free query `-from \$v30u_ce -to \$shadow`, top 5:"
set i 0 ; set nin 0 ; set nout 0
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $shadow -setup -npaths 5 -detail full_path] {
    incr i
    set t [get_node_info [get_path_info $p -to] -name]
    set inc [expr {[lsearch -exact $snames $t] >= 0 ? "IN" : "*** NOT IN ***"}]
    if {[lsearch -exact $snames $t] >= 0} { incr nin } else { incr nout }
    emit [format "         %d  %-14s slack %+8.3f  data %s  to %s" \
              $i $inc [get_path_info $p -slack] [get_path_info $p -data_delay] $t]
}
emit [format "         %d of %d destinations are IN the collection" $nin $i]

# --- PC-S4: the KNOWN-WRONG form, printed and never relied on.
set sn [get_nodes -nowarn {*|v30u_eu:*|s1q*}]
set n4 [get_collection_size [get_timing_paths -from $v30u_ce -to $sn -setup -npaths 1]]
emit [format "  PC-S4  the same query with get_nodes (%d nodes) returns %d path(s)" \
          [get_collection_size $sn] $n4]
emit "         (printed as the KNOWN-WRONG resolver form, never relied on)"

# --- and the same three rows sta_cutset_diag prints, with membership shown.
foreach {tag from to} [list "STAGE 1 (* -> s1q)" $v30u_ce $shadow \
                            "STAGE 2 (s1q -> *)" $shadow $v30u_ce] {
    foreach_in_collection p [get_timing_paths -from $from -to $to -setup -npaths 1 -detail full_path] {
        set f [get_node_info [get_path_info $p -from] -name]
        set t [get_node_info [get_path_info $p -to] -name]
        emit "  $tag worst:"
        emit "    from : $f   [expr {[lsearch -exact $snames $f] >= 0 ? "(IN shadow)" : "(not in shadow)"}]"
        emit "    to   : $t   [expr {[lsearch -exact $snames $t] >= 0 ? "(IN shadow)" : "(not in shadow)"}]"
        emit [format "    slack %+8.3f   levels %s   data delay %s" \
                  [get_path_info $p -slack] [get_path_info $p -num_logic_levels] \
                  [get_path_info $p -data_delay]]
    }
}
close $fh
project_close
