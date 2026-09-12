# WAVE 9 -- THE CENSUS THAT MAKES J-9's THIRD CLASS ACTIONABLE.
#
# The binding `ce -> ce` path touches NEITHER stage, and its arrival points name
# the EU -> BIU -> EU combinational round trip through `q_cnt` -> `q_ripe_lead_n`
# (`r7_lint`'s own DECLARED UNRESOLVED carrier).  ONE path is an anecdote.  This
# asks the whole population: of the top N `ce -> ce` paths, how many carry it?
#
# ⚠ MATCH `|u_biu|`, THE INSTANCE NAME, NOT `v30u_biu:`, THE TYPE PREFIX.
# Quartus prints the type prefix on REGISTER names and omits it on COMBINATIONAL
# node names, so a `v30u_biu:` test finds every BIU flop and NOT ONE BIU LUT --
# and it is the LUTs that make a round trip.  WAVE 4 §6.1 item 1.
#
# POSITIVE CONTROLS, REPORTED FIRST:
#   PC-A  the `|u_biu|` test on the binding path must read > 0 (the diag already
#         read 8; if this reads 0 the test is broken, not the finding).
#   PC-B  the KNOWN-WRONG `v30u_biu:` type-prefix form printed beside it, which
#         must read 0 on the same paths -- that is what shows PC-A is not
#         matching by accident.
# args: {project revision outfile}.
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

emit $fh "=== sta_cutset_biu_census (WAVE 9) ==="
set n 0 ; set nbiu 0 ; set nripe 0 ; set nshadow 0 ; set nucrom_launch 0
set first 1
set sum_biu 0.0
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup -npaths 200 -detail full_path] {
    incr n
    set f [get_node_info [get_path_info $p -from] -name]
    if {[string first "u_ucrom" $f] >= 0} { incr nucrom_launch }
    set hb 0 ; set hr 0 ; set hs 0 ; set hbt 0
    set tin -1.0 ; set tout -1.0
    if {![catch {set pts [get_path_info $p -arrival_points]}]} {
        foreach_in_collection pt $pts {
            set nd [lindex [get_point_info $pt -node] 0]
            if {$nd eq ""} { continue }
            set nm [get_node_info $nd -name]
            set t  [get_point_info $pt -total]
            if {[string first "|u_biu|" $nm] >= 0} {
                set hb 1
                if {$tin < 0.0} { set tin $t }
                set tout $t
            }
            if {[string first "q_ripe_lead_n" $nm] >= 0} { set hr 1 }
            if {[string first "|s1q" $nm] >= 0} { set hs 1 }
            if {[string first "v30u_biu:" $nm] >= 0} { set hbt 1 }
        }
    }
    incr nbiu $hb ; incr nripe $hr ; incr nshadow $hs
    if {$hb && $tout > $tin} { set sum_biu [expr {$sum_biu + ($tout - $tin)}] }
    if {$first} {
        emit $fh [format "  PC-A  the binding path: |u_biu| nodes present = %d   (MUST be 1)" $hb]
        emit $fh [format "  PC-B  the KNOWN-WRONG `v30u_biu:` type-prefix form on the SAME path = %d   (MUST be 0)" $hbt]
        set first 0
    }
}
emit $fh [format "  paths scanned                                   : %d" $n]
emit $fh [format "  ...launching inside the microcode ROM           : %d" $nucrom_launch]
emit $fh [format "  ...carrying the EU -> BIU -> EU round trip      : %d" $nbiu]
emit $fh [format "  ...carrying `q_ripe_lead_n` by name             : %d" $nripe]
emit $fh [format "  ...naming the shadow |s1q anywhere              : %d" $nshadow]
if {$nbiu > 0} {
    emit $fh [format "  mean span of the round trip when present (ns)   : %.3f" [expr {$sum_biu / $nbiu}]]
}
close $fh
project_close
