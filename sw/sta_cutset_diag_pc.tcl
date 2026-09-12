# WAVE 9 -- J-3(b)'s POSITIVE CONTROLS, AND THE REPAIR OF ONE THAT COULD NOT
# SAY YES.
#
# `sw/sta_cutset_diag.tcl` reported its own `-through` positive control as
# **"resolves 0 pin(s)"** on this netlist (WAVE 4's read 1).  An instrument
# whose control cannot say YES cannot be trusted when it says NO, so the NO it
# reported -- C-3(b)/J-3(b)'s "0 arrival points name |s1q" -- is not quotable
# until a control passes.  THIS FILE IS THAT CONTROL, and it does not change the
# measurement: the diag's own count is re-derived here and must agree.
#
# THE CAUSE, MEASURED AND NOT GUESSED: the binding path's LAST arrival point is
# `...|upc_page[0]|asdata`, not `|d`.  `upc_page[0]` is loaded through its
# SECONDARY DATA port (a synchronous-load register), so the pattern
# `"${to}|d*"` names a pin that does not exist on this destination.  WAVE 4's
# destination (`opc_base[3]`) was a plain `d`-loaded flop and its control passed
# for that reason and not because the probe was general.
#
# ⚠ THE KNOWN-WRONG FORM IS KEPT AND PRINTED BESIDE THE REPAIRED ONE, per the
# campaign's standing rule about bulk / mis-shaped collections.
#
# args: {project revision outfile}.  ⚠ The comment is on its own line: Tcl has
# no trailing `#`.
project_open nec_test -revision nec_test_ucore
create_timing_netlist -model slow
read_sdc
update_timing_netlist
set fh [open [lindex $quartus(args) 2] w]
proc emit {fh s} { puts $fh $s ; puts $s }

set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] \
                                 [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
set shadow    [get_registers -nowarn {*|v30u_eu:*|s1q*}]

emit $fh "=== sta_cutset_diag_pc (WAVE 9) -- THE CONTROLS ==="
emit $fh [format "  \$v30u_ce %d   shadow registers %d" \
              [get_collection_size $v30u_ce] [get_collection_size $shadow]]

# ---------------------------------------------------------------- PC-1
# THE CLASSIFIER MUST BE ABLE TO SAY YES.  Run the IDENTICAL arrival-point scan
# -- the same `string first "|s1q"` test, on the same kind of collection -- over
# the worst path that LAUNCHES FROM the shadow.  That path names `|s1q` at its
# launch by construction, so a scan reading 0 here would be a broken scan and
# not a finding.  THIS IS THE CONTROL THE `-through` PROBE FAILED TO PROVIDE.
proc scan_s1q {p} {
    set n 0 ; set tot 0
    if {![catch {set pts [get_path_info $p -arrival_points]}]} {
        foreach_in_collection pt $pts {
            set nd [lindex [get_point_info $pt -node] 0]
            if {$nd eq ""} { continue }
            incr tot
            if {[string first "|s1q" [get_node_info $nd -name]] >= 0} { incr n }
        }
    }
    return [list $n $tot]
}
foreach_in_collection p [get_timing_paths -from $shadow -to $v30u_ce -setup -npaths 1 -detail full_path] {
    set r [scan_s1q $p]
    emit $fh [format "  PC-1  the SAME scan on a path that LAUNCHES FROM the shadow: %d of %d name |s1q" \
                  [lindex $r 0] [lindex $r 1]]
    emit $fh "        (MUST be > 0.  0 here means the scan is broken, not that the shadow is absent.)"
    emit $fh "        from : [get_node_info [get_path_info $p -from] -name]"
    emit $fh "        to   : [get_node_info [get_path_info $p -to] -name]"
}
# ---------------------------------------------------------------- PC-2
# ...and the mirror: a path that LANDS ON the shadow.
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $shadow -setup -npaths 1 -detail full_path] {
    set r [scan_s1q $p]
    emit $fh [format "  PC-2  the SAME scan on a path that LANDS ON the shadow: %d of %d name |s1q" \
                  [lindex $r 0] [lindex $r 1]]
    emit $fh "        (MUST be > 0.)"
}

# ---------------------------------------------------------------- PC-3
# THE `-through` CONTROL, BOTH FORMS, ON THE ACTUAL BINDING DESTINATION.
set to ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 1 -detail path_only] {
    set to [get_node_info [get_path_info $p -to] -name]
}
emit $fh "  the binding destination : $to"
foreach pat {d asdata} {
    set pins [get_pins -nowarn -compatibility_mode "${to}|${pat}*"]
    set np [get_collection_size $pins]
    set npaths "n/a"
    if {$np > 0} {
        set npaths [get_collection_size [get_timing_paths -from $v30u_ce -to $v30u_ce -through $pins -setup -npaths 1]]
    }
    emit $fh [format "  PC-3  -through {%s|%s*} resolves %d pin(s), paths returned %s" \
                  $to $pat $np $npaths]
}
emit $fh "        (WAVE 4's diag asks ONLY the `d` form.  On THIS destination it"
emit $fh "         resolves 0 and the control silently could not say YES.)"

# ---------------------------------------------------------------- PC-4
# THE `-through` CONTROL ON A DESTINATION WHOSE `d` PIN DOES EXIST, so the
# original form is shown WORKING on this same netlist -- i.e. the failure above
# is a property of the DESTINATION, not of the netlist or of Quartus.
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $shadow -setup -npaths 1 -detail path_only] {
    set st [get_node_info [get_path_info $p -to] -name]
    set pins [get_pins -nowarn -compatibility_mode "${st}|d*"]
    set np [get_collection_size $pins]
    set npaths "n/a"
    if {$np > 0} {
        set npaths [get_collection_size [get_timing_paths -from $v30u_ce -to $shadow -through $pins -setup -npaths 1]]
    }
    emit $fh [format "  PC-4  the ORIGINAL `d` form on %s : %d pin(s), paths returned %s" $st $np $npaths]
}

# ---------------------------------------------------------------- J-3(b)
# THE MEASUREMENT, RE-DERIVED HERE so it is reported by an instrument whose
# controls passed.  Top 200 `ce -> ce`, counting how many name the shadow ANYWHERE
# on the path -- a strictly WEAKER question than "launches from / lands on", so a
# 0 here is the strongest available form of the answer.
set nany 0 ; set ntot 0
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 200 -detail full_path] {
    incr ntot
    set r [scan_s1q $p]
    if {[lindex $r 0] > 0} { incr nany }
}
emit $fh [format "  J-3(b)  of the top %d ce->ce paths, %d name |s1q ANYWHERE on the path" $ntot $nany]

close $fh
project_close
