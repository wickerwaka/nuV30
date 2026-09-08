# sta_l2_rowq_probe.tcl -- L-8: THE NEW D-PIN CLASS L2 CREATES, AND WHETHER IT BINDS.
#
# L2 registers the microcode ROW table on the `ce` edge that makes its address.
# Its address is `{dec_bank_next, upc_loc_sel[1:0]}` and `dec_bank_next` is the
# COMBINATIONAL `ucdecode` output, so `row_q`'s D pin carries BOTH ROMS IN
# SERIES -- the chain L1 broke on the Q side.  That was REGISTERED IN ADVANCE
# as a trap (`l2_registered_row_prereg_2026-09-08.md` §1.4) and this script is
# what measures it: if the new class BINDS, L2 in this form is REFUTED.
#
# It answers four questions and nothing else:
#   §E  the collections it used            (a silently-short collection reads
#                                          as a reassuring result)
#   §1  the worst `ce -> ce` path ENDING at `row_q`   (the NEW class)
#   §2  the worst `ce -> ce` path LAUNCHING at `row_q` (what L2 was for)
#   §3  the worst `ce -> ce` path anywhere            (what actually binds)
# and prints §1 as a fraction of §3, which is the L-8 verdict.
#
# ⚠ IT IS NOT A GATE AND IT WRITES NO RECEIPT.  Quotable Fmax comes from
# `sw/quartus_gate.py`.
#
# ⚠ THE TWO RECORDED TRAPS OF THIS TREE'S STA SCRIPTS ARE OBEYED HERE TOO:
#   * `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection
#     (`sta_phase_split_scan.tcl` header).  This script uses no `-through`.
#   * `string match` on a register name carrying a BUS INDEX fails, because
#     `[3]` is a character class.  This script does no name matching at all --
#     it uses `get_registers` globs, whose `[*]` is a Quartus wildcard, and it
#     PRINTS the collection sizes so a glob that matched nothing is visible.
#
#   quartus_sta -t sw/sta_l2_rowq_probe.tcl <proj> <rev> <out>

set proj [lindex $quartus(args) 0]
set rev  [lindex $quartus(args) 1]
set out  [lindex $quartus(args) 2]

project_open $proj -revision $rev
create_timing_netlist -model slow -speed 7 -temperature 100 -voltage 1100
read_sdc
update_timing_netlist

set fh [open "$out.rowq.txt" w]
proc emit {s} { global fh ; puts $fh $s ; puts $s }

emit "=== sta_l2_rowq_probe: $proj / $rev ==="

# The SDC's own collections, reproduced exactly as sta_truefmax_probe.tcl and
# sta_phase_split_scan.tcl do.
set v30u_regs [add_to_collection \
                   [get_registers -nowarn {*|v30u_eu:*|*}] \
                   [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]

# `row_q` INCLUDING the fitter's `~DUPLICATE` forms.  The distribution gate's
# §6 records an exact-name collection SILENTLY missing duplicated registers,
# and this campaign's binding path has ended in one before.
set rowq [get_registers -nowarn {*|v30u_eu:*|row_q[*]}]
set rowq [add_to_collection $rowq [get_registers -nowarn {*|v30u_eu:*|row_q[*]~*}]]
set decq [get_registers -nowarn {*|v30u_eu:*|dec_q[*]}]
set decq [add_to_collection $decq [get_registers -nowarn {*|v30u_eu:*|dec_q[*]~*}]]

emit ""
emit "=== E. COLLECTION SIZES ==="
emit [format "  \$v30u_ce                : %d" [get_collection_size $v30u_ce]]
emit [format "  row_q (incl ~DUPLICATE) : %d" [get_collection_size $rowq]]
emit [format "  dec_q (incl ~DUPLICATE) : %d" [get_collection_size $decq]]

if {[get_collection_size $rowq] == 0} {
    emit ""
    emit "CONTROL FAILED: the row_q collection is EMPTY.  Either this netlist"
    emit "predates L2, or every row_q bit was optimised away, or the glob is"
    emit "wrong.  NO L-8 RESULT IS EMITTED -- an empty collection returns no"
    emit "path, and 'no path' would read as 'the class does not bind'."
    close $fh ; project_close ; exit 3
}

proc report {label paths} {
    global fh
    if {[get_collection_size $paths] == 0} {
        emit "  $label: NO PATH RETURNED"
        return -1
    }
    set worst 1e9
    foreach_in_collection p $paths {
        set slack [get_path_info $p -slack]
        set lv    [get_path_info $p -num_logic_levels]
        set dd    [get_path_info $p -data_delay]
        set from  [get_node_info [get_path_info $p -from] -name]
        set to    [get_node_info [get_path_info $p -to] -name]
        emit "  $label"
        emit "    from        : $from"
        emit "    to          : $to"
        emit [format "    slack       : %8.3f ns" $slack]
        emit [format "    data delay  : %8.3f ns" $dd]
        emit [format "    logic levels: %d" $lv]
        if {$slack < $worst} { set worst $slack }
    }
    return $worst
}

emit ""
emit "=== 1. THE NEW CLASS -- worst \$v30u_ce -> row_q ==="
set s_to [report "worst -> row_q" \
              [get_timing_paths -setup -npaths 1 -from $v30u_ce -to $rowq]]

emit ""
emit "=== 2. WHAT L2 WAS FOR -- worst row_q -> \$v30u_ce ==="
set s_from [report "worst row_q ->" \
                [get_timing_paths -setup -npaths 1 -from $rowq -to $v30u_ce]]

emit ""
emit "=== 2b. FOR CONTEXT -- worst \$v30u_ce -> dec_q, and worst dec_q -> \$v30u_ce ==="
report "worst -> dec_q" [get_timing_paths -setup -npaths 1 -from $v30u_ce -to $decq]
report "worst dec_q ->" [get_timing_paths -setup -npaths 1 -from $decq -to $v30u_ce]

emit ""
emit "=== 3. WHAT ACTUALLY BINDS -- worst \$v30u_ce -> \$v30u_ce ==="
set s_all [report "worst ce -> ce" \
               [get_timing_paths -setup -npaths 1 -from $v30u_ce -to $v30u_ce]]

emit ""
emit "=== L-8 VERDICT ==="
if {$s_to < 0 || $s_all < 0} { } ;# slacks may legitimately be negative
emit [format "  worst slack INTO row_q : %8.3f ns" $s_to]
emit [format "  worst slack ce -> ce   : %8.3f ns" $s_all]
if {abs($s_to - $s_all) < 1e-6} {
    emit "  >>> THE NEW CLASS **BINDS** (it IS the worst ce -> ce path)."
    emit "  >>> L2 IN THIS FORM IS REFUTED BY ITS OWN REGISTERED BAR (L-8)."
} else {
    emit [format "  >>> the new class is %.3f ns BEHIND the binding arc -- it does NOT bind." \
              [expr {$s_to - $s_all}]]
}

emit ""
emit "=== 4. THE TOP 10 ce -> ce PATHS, endpoint only (is row_q anywhere near?) ==="
set i 0
foreach_in_collection p [get_timing_paths -setup -npaths 10 -from $v30u_ce -to $v30u_ce] {
    incr i
    emit [format "  %2d  slack %8.3f  levels %3d   %s\n         -> %s" $i \
              [get_path_info $p -slack] [get_path_info $p -num_logic_levels] \
              [get_node_info [get_path_info $p -from] -name] \
              [get_node_info [get_path_info $p -to] -name]]
}

close $fh
project_close
