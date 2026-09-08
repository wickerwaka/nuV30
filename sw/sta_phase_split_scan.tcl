# sta_phase_split_scan.tcl -- CAN THE BINDING `ce -> ce` CONE BE CUT IN TWO
# ACROSS THE TWO CLOCK-ENABLE PHASES?
#
# THE QUESTION.  The ucore does all its work on `ce`; `ce_half` has exactly one
# consumer (`v30u_biu|t1_half2`).  Closing timing therefore needs
# `set_multicycle_path -setup 2 -hold 1` on ~2,200 core registers, which every
# downstream integrator must re-derive (`m72_downstream_timing_2026-08-12.md`
# §1).  IF the binding cone could be split -- stage 1 evaluated in the
# `ce -> ce_half` window and captured on `ce_half`, stage 2 evaluated in the
# `ce_half -> ce` window and captured on `ce` -- one 2-period arc becomes two
# 1-period arcs and the exception is DELETED.
#
# THE THEOREM THE CAMPAIGN RESTS ON.  A node in the `ce -> ce` cone that is
# outside every LIVE source's combinational fanout depends only on registers
# that commit on `ce`.  Its value is therefore CONSTANT ACROSS THE WHOLE CPU
# CYCLE -- identical at `ce_half(n)` and at `ce(n+1)` -- so capturing it on
# `ce_half` and consuming it on `ce` is bit-exact by construction and moves no
# pin on any clock.  (This is L1's argument -- `v30u_eu.sv` "L1 -- THE DECODE
# IS TAKEN ON THE EDGE THAT MAKES ITS ADDRESS", `adcone_l1_results_2026-08-13.md`
# -- one PHASE over instead of one CLOCK early.)  So the measurement this
# script takes is: WHERE, ALONG THE BINDING PATHS, DOES PIN-DEPENDENCE ENTER?
#
# ⚠⚠ THE INSTRUMENT TRAP THIS SCRIPT CARRIES A PERMANENT CONTROL AGAINST.
# `get_timing_paths -through` SILENTLY IGNORES a collection produced by
# `get_nodes` in Quartus 17.1 -- it returns "no path" for EVERY node, including
# nodes that demonstrably ARE on a path.  Measured on
# `emu|system_large|u_core|u_biu|ann_kill~0|combout` with a -from/-to pair known
# to have a path through it:
#       get_nodes   -> collection size 1 -> paths 0     <-- WRONG, and SILENT
#       get_pins    -> collection size 1 -> paths 1     <-- correct
#       get_nets    -> collection size 1 -> paths 1     <-- correct
#       get_cells   -> collection size 1 -> paths 1     <-- correct
#       bare string                      -> paths 1     <-- correct
# The first version of this scan used `get_nodes` and reported "all 50 nodes are
# register-only".  IT WAS ENTIRELY VACUOUS.  §A below re-asks the SAME question
# of the nodes on a path that is BY CONSTRUCTION pin-dependent end to end; if
# any of them comes back register-only the instrument is broken and the script
# REFUSES TO EMIT A SCAN RESULT.
#
# ⚠ THIS IS NOT A GATE AND IT WRITES NO RECEIPT.  The quotable Fmax numbers come
# from `sw/quartus_gate.py`.
#
# WHAT IT EMITS, in order:
#   §E  the collection sizes it used            (a silently-short collection
#       reads as a reassuring result -- `timing50_distribution_2026-08-13.md` §6)
#   §A  THE POSITIVE CONTROL -- and it GATES everything below it
#   §B  the pin-dependence scan over the top-N `ce -> ce` setup paths
#   §C  the cut-point census, sorted by |upstream - downstream|
#   §D  the worst three paths node by node
#
#   quartus_sta -t sw/sta_phase_split_scan.tcl <proj> <rev> <out> [npaths]

set proj [lindex $quartus(args) 0]
set rev  [lindex $quartus(args) 1]
set out  [lindex $quartus(args) 2]
set np   [lindex $quartus(args) 3]
if {$np eq ""} { set np 50 }

project_open $proj -revision $rev
create_timing_netlist -model slow -speed 7 -temperature 100 -voltage 1100
read_sdc
update_timing_netlist

set fh [open "$out.phasesplit.txt" w]
proc emit {s} { global fh ; puts $fh $s ; puts $s }

emit "=== sta_phase_split_scan: $proj / $rev ==="
emit "npaths requested = $np"

set T0 0.0
set divclk_name ""
foreach_in_collection c [get_clocks] {
    if {[string match "*gpll~PLL_OUTPUT_COUNTER|divclk" [get_clock_info $c -name]] &&
        [string match "emu|pll*" [get_clock_info $c -name]]} {
        set T0 [get_clock_info $c -period]
        set divclk_name [get_clock_info $c -name]
    }
}
emit [format "T0 = %.3f ns   (clock %s)" $T0 $divclk_name]

# ---------------------------------------------------------------------------
# NAME NORMALISATION.
# Quartus names the same object two ways: post-fit REGISTER nodes carry the
# `type:instance` form (`emu:emu|system_large:system_large|...|c_int_q`) while
# post-fit COMBINATIONAL pins carry the instance alone
# (`emu|system_large|u_core|u_biu|ann_kill~0|combout`).  `norm` strips the
# `type:` prefixes so the two forms compare.  `basenet` additionally drops the
# trailing PIN segment and the Quartus synthetic `~N` / `~DUPLICATE` /
# `~0_OTERM…DUPLICATE` suffix, which is what folds `Mux67~0_OTERM3150DUPLICATE`
# and `Mux67~1` onto the RTL net `Mux67`.  The `~DUPLICATE` fold is not
# cosmetic: `timing50_distribution_2026-08-13.md` §6 records an exact-name
# collection SILENTLY missing duplicated registers, and the binding path this
# campaign was aimed at ENDS in a `~DUPLICATE` node.
# ---------------------------------------------------------------------------
proc norm {name} {
    set segs [split $name "|"]
    set o {}
    foreach s $segs {
        set c [string first ":" $s]
        if {$c >= 0} { set s [string range $s [expr {$c+1}] end] }
        lappend o $s
    }
    return [join $o "|"]
}
proc basenet {name} {
    set segs [split [norm $name] "|"]
    if {[llength $segs] > 1} { set segs [lrange $segs 0 end-1] }
    set last [lindex $segs end]
    set t [string first "~" $last]
    if {$t >= 0} { set last [string range $last 0 [expr {$t-1}]] }
    set segs [lreplace $segs end end $last]
    return [join $segs "|"]
}

# ---------------------------------------------------------------------------
# §E. THE COLLECTIONS.
# ---------------------------------------------------------------------------
# The SDC's own collections, reproduced exactly as `sta_truefmax_probe.tcl`
# does.  The `*|v30u_eu:*|*` / `*|v30u_biu:*|*` globs already admit the
# `~DUPLICATE` register forms (the tilde is inside the leaf segment).
set v30u_regs [add_to_collection \
                   [get_registers -nowarn {*|v30u_eu:*|*}] \
                   [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
set allreg    [get_registers *]

# LIVE_NARROW -- the registers that DRIVE THE CORE'S ASYNCHRONOUS INPUT PORTS,
# read off `hdl/rtl/system_large.sv`: READY/INT/NMI/POLL_N/RESET are
# `c_*_q` (line ~371), and the read word arrives on the shared AD pads as
# `core_ad[15:0] = c_addrv_q ? c_rdata_q : 16'hzzzz` (line 491).  In a RETENTION
# build `core_ad_hold` is a second AD driver and is included; in CONTROL that
# collection is empty and the line is a no-op.
set live_narrow [get_registers -nowarn {*system_large*|c_ready_q}]
foreach pat {
    {*system_large*|c_int_q} {*system_large*|c_nmi_q} {*system_large*|c_polln_q}
    {*system_large*|c_reset_q} {*system_large*|c_rdata_q[*]}
    {*system_large*|c_addrv_q} {*system_large*|core_ad_hold[*]}
    {*system_large*|c_ready_q~*} {*system_large*|c_int_q~*}
    {*system_large*|c_nmi_q~*} {*system_large*|c_polln_q~*}
    {*system_large*|c_reset_q~*} {*system_large*|c_rdata_q[*]~*}
    {*system_large*|c_addrv_q~*} {*system_large*|core_ad_hold[*]~*}
} {
    set live_narrow [add_to_collection $live_narrow [get_registers -nowarn $pat]]
}

# LIVE_WIDE -- EVERY register that is not in `$v30u_ce`.  This is the
# CONSERVATIVE reading of the theorem and it needs no name list: a register
# outside `$v30u_ce` is, as far as STA can know, free to change between `ce(n)`
# and `ce(n+1)`.  It admits `t1_half2` itself, which LIVE_NARROW does not and
# which a name-list instrument would MISS -- `t1_half2` is by construction a
# mid-cycle changer, so a `ce` register combinationally downstream of it is NOT
# phase-stable either.
set live_wide [remove_from_collection $allreg $v30u_ce]

emit ""
emit "=== E. COLLECTION SIZES (a silently-short collection reads as a result) ==="
emit [format "  all registers                 : %d" [get_collection_size $allreg]]
emit [format "  \$v30u_regs (eu + biu)         : %d" [get_collection_size $v30u_regs]]
emit [format "  \$v30u_half (t1_half2)         : %d" [get_collection_size $v30u_half]]
emit [format "  \$v30u_ce                      : %d" [get_collection_size $v30u_ce]]
emit [format "  LIVE_NARROW (core input drvrs): %d" [get_collection_size $live_narrow]]
emit [format "  LIVE_WIDE   (not \$v30u_ce)    : %d" [get_collection_size $live_wide]]
foreach_in_collection h $v30u_half {
    emit "    t1_half2 member: [get_node_info $h -name]"
}
if {[get_collection_size $v30u_ce] < 1000 || [get_collection_size $v30u_half] < 1 ||
    [get_collection_size $live_narrow] < 4} {
    emit ""
    emit "CONTROL FAILED: a collection is implausibly short.  REFUSING to scan."
    close $fh ; project_close ; exit 3
}

# ---------------------------------------------------------------------------
# THE CLASSIFIER.
# `-through` is given a `get_pins` collection.  `get_nodes` IS SILENTLY IGNORED
# (see the header).  Falls back to `get_nets`, then to the bare string, and
# records which resolver answered so the answer is never anonymous.
# ---------------------------------------------------------------------------
array set THRU_KIND {}
proc thru_collection {node} {
    global THRU_KIND
    set c [get_pins -nowarn $node]
    if {[get_collection_size $c] > 0} { set THRU_KIND($node) pins ; return $c }
    set c [get_nets -nowarn $node]
    if {[get_collection_size $c] > 0} { set THRU_KIND($node) nets ; return $c }
    set THRU_KIND($node) UNRESOLVED
    return ""
}

array set PDN {}   ;# node -> 1 pin-dep / 0 reg-only  (LIVE_NARROW)
array set PDW {}   ;# node -> 1 pin-dep / 0 reg-only  (LIVE_WIDE)
set n_unresolved 0
set unresolved_list {}

proc pindep {node which} {
    global PDN PDW live_narrow live_wide v30u_ce n_unresolved unresolved_list
    if {$which eq "N"} {
        if {[info exists PDN($node)]} { return $PDN($node) }
    } else {
        if {[info exists PDW($node)]} { return $PDW($node) }
    }
    set c [thru_collection $node]
    if {$c eq ""} {
        incr n_unresolved
        lappend unresolved_list $node
        if {$which eq "N"} { set PDN($node) -1 } else { set PDW($node) -1 }
        return -1
    }
    if {$which eq "N"} { set src $live_narrow } else { set src $live_wide }
    set ps [get_timing_paths -setup -npaths 1 -from $src -through $c -to $v30u_ce]
    set r [expr {[get_collection_size $ps] > 0 ? 1 : 0}]
    if {$which eq "N"} { set PDN($node) $r } else { set PDW($node) $r }
    return $r
}

# ---------------------------------------------------------------------------
# PATH WALKER.
# Splits a path's arrival points into three STRUCTURAL phases -- clock network,
# launch register, data path -- by NAME MATCH against the path's own -from and
# -to, not by pattern-matching PLL names.  The clock network is EVERYTHING at or
# before the launch register, and the destination register is everything at or
# after the -to node; those two classes are the only legitimate exclusions and
# they are excluded BY RULE.
# Returns a dict: cells (list of {name cum incr}), total_cum, launch_cum,
#                 nclock, ndest, to_name
# ---------------------------------------------------------------------------
proc walk {p} {
    set from [get_node_info [get_path_info $p -from] -name]
    set to   [get_node_info [get_path_info $p -to] -name]
    set fn [norm $from]
    set tn [norm $to]
    set state 0
    set cum 0.0
    set launch_cum 0.0
    set cells {}
    set nclock 0
    set ndest 0
    set alldump {}
    if {[catch {set pts [get_path_info $p -arrival_points]} err]} {
        return [list cells {} total 0.0 launch 0.0 nclock 0 ndest 0 to $to from $from dump {} err $err]
    }
    foreach_in_collection pt $pts {
        set nd [get_point_info $pt -node]
        if {$nd eq ""} { continue }
        set nm  [get_node_info $nd -name]
        set inc [get_point_info $pt -incr]
        set ty  [get_point_info $pt -type]
        if {$inc eq ""} { set inc 0.0 }
        set cum [expr {$cum + $inc}]
        set nn [norm $nm]
        if {$state == 0} {
            if {[string match "${fn}*" $nn]} { set state 1 } else {
                if {$ty eq "cell"} { incr nclock }
            }
        }
        if {$state == 1} {
            if {[string match "${fn}*" $nn]} {
                set launch_cum $cum
            } else { set state 2 }
        }
        if {$state == 2 && [string match "${tn}*" $nn]} { set state 3 }
        set tag ""
        if {$state == 0} { set tag CLK } elseif {$state == 1} { set tag LAUNCH } \
            elseif {$state == 2} { set tag DATA } else { set tag DEST }
        if {$state == 2 && $ty eq "cell"} {
            lappend cells [list $nm $cum $inc]
        }
        if {$state == 3 && $ty eq "cell"} { incr ndest }
        lappend alldump [list [format "%8.3f %8.3f %-6s %-6s %s" $inc $cum $ty $tag $nm] $nm]
    }
    return [list cells $cells total $cum launch $launch_cum nclock $nclock \
                ndest $ndest to $to from $from dump $alldump err ""]
}

# ---------------------------------------------------------------------------
# §A. THE POSITIVE CONTROL.  RUN FIRST, AND IT GATES EVERYTHING BELOW.
# Take the worst `LIVE -> $v30u_ce` path -- pin-dependent end to end BY
# CONSTRUCTION -- walk its own data nodes, and re-ask the classifier the same
# `-through` question of each.  Every one MUST come back pin-dependent.
# ---------------------------------------------------------------------------
emit ""
emit "=== A. THE POSITIVE CONTROL (gates everything below) ==="
set control_ok 1
set control_rows {}
foreach which {N W} {
    if {$which eq "N"} { set src $live_narrow ; set lbl "LIVE_NARROW" } \
        else { set src $live_wide ; set lbl "LIVE_WIDE" }
    set cps [get_timing_paths -setup -npaths 1 -detail full_path -from $src -to $v30u_ce]
    if {[get_collection_size $cps] == 0} {
        emit "  $lbl: NO PATH -- the control cannot run.  CONTROL FAILED."
        set control_ok 0
        continue
    }
    foreach_in_collection p $cps {
        array set W [walk $p]
        set nc [llength $W(cells)]
        set ok 0 ; set bad 0 ; set unr 0
        set badlist {}
        foreach c $W(cells) {
            set nm [lindex $c 0]
            set r [pindep $nm $which]
            if {$r == 1} { incr ok } elseif {$r == 0} { incr bad ; lappend badlist $nm } \
                else { incr unr ; lappend badlist "UNRESOLVED:$nm" }
        }
        emit ""
        emit "  --- $lbl ---"
        emit "  worst path : $W(from)"
        emit "            -> $W(to)"
        emit [format "  data delay (launch reg output -> dest) : %8.3f ns" \
                  [expr {$W(total) - $W(launch)}]]
        emit [format "  total arrival (from clock source)      : %8.3f ns" $W(total)]
        emit [format "  data-path combinational cells          : %d" $nc]
        emit [format "  EXCLUDED BY RULE: clock-network cells %d, destination-register cells %d" \
                  $W(nclock) $W(ndest)]
        emit [format "  PIN-DEPENDENT %d / %d      REG-ONLY %d      UNRESOLVED %d" \
                  $ok $nc $bad $unr]
        if {$nc < 3} {
            set control_ok 0
            emit "  ⚠ THE WALKER FOUND FEWER THAN 3 DATA-PATH CELLS ON THIS PATH."
            emit "    A control with nothing to classify passes vacuously; it does not."
        }
        if {$bad > 0 || $unr > 0} {
            set control_ok 0
            emit "  ⚠ THE FOLLOWING SHOULD HAVE BEEN PIN-DEPENDENT AND WERE NOT:"
            foreach b $badlist { emit "      $b" }
        }
        lappend control_rows [list $lbl $ok $nc $bad $unr]
        array unset W
    }
}
emit ""
if {!$control_ok} {
    emit "CONTROL FAILED"
    emit "The `-through` classifier did not reproduce pin-dependence on a path"
    emit "that is pin-dependent by construction.  No scan result is emitted."
    close $fh
    project_close
    exit 4
}
emit "CONTROL PASSED -- 100% pin-dependent on every non-excluded node, both live sets."

# ---------------------------------------------------------------------------
# §B. THE SCAN.
# ---------------------------------------------------------------------------
emit ""
emit "=== B. THE PIN-DEPENDENCE SCAN over the top-$np \$v30u_ce -> \$v30u_ce paths ==="
set paths [get_timing_paths -setup -npaths $np -detail full_path -from $v30u_ce -to $v30u_ce]
emit [format "paths returned: %d" [get_collection_size $paths]]

array set netcount {}     ;# base net -> #paths it appears on
array set netcum {}       ;# base net -> sum of (cum - launch) at it
array set netcummax {}    ;# base net -> max of (cum - launch)
array set netrem {}       ;# base net -> sum of (total - cum)
array set netremmax {}
array set netregonly {}   ;# base net -> 1 while REG-ONLY on every path so far
array set netpaths {}

set npath 0
set n_nomerge 0
set worst_data 0.0
set worst_desc ""
set dumps {}
set rows {}
foreach_in_collection p $paths {
    incr npath
    array set W [walk $p]
    set slack [get_path_info $p -slack]
    set lv    [get_path_info $p -num_logic_levels]
    set data  [expr {$W(total) - $W(launch)}]
    if {$npath <= 3} { lappend dumps [list $npath $W(from) $W(to) $W(dump)] }
    if {$data > $worst_data} { set worst_data $data ; set worst_desc "$W(from) -> $W(to)" }

    set npd 0 ; set nro 0 ; set nun 0 ; set merge -1 ; set merge_idx -1
    set idx 0
    array set seen {}
    array set occ {}
    foreach c $W(cells) {
        set nm  [lindex $c 0]
        set cum [lindex $c 1]
        set rel [expr {$cum - $W(launch)}]
        set r   [pindep $nm N]
        if {$r == 1} {
            incr npd
            if {$merge < 0} { set merge $rel ; set merge_idx $idx }
        } elseif {$r == 0} { incr nro } else {
            incr nun
            if {$merge < 0} { set merge $rel ; set merge_idx $idx }
        }
        # ⚠ OCCURRENCE-INDEXED.  `st_n`, `ld_b_n`, `always6` and `Ram*` each
        # appear SEVERAL TIMES on one path -- the EU's chain loop is UNROLLED
        # (`v30u_eu.sv`'s `for (chain = 0; chain < CHAIN_MAX; ...)`) and every
        # position is a fresh copy of the same source line, so a first-
        # occurrence-only census would report ONE cut where the netlist has
        # three and would report the FIRST one's split for all of them.  The
        # census key is therefore `net#occurrence`.
        set braw [basenet $nm]
        if {[info exists occ($braw)]} { incr occ($braw) } else { set occ($braw) 1 }
        set b "$braw#$occ($braw)"
        if {![info exists seen($b)]} {
            set seen($b) 1
            if {![info exists netcount($b)]} {
                set netcount($b) 0 ; set netcum($b) 0.0 ; set netrem($b) 0.0
                set netregonly($b) 1 ; set netcummax($b) 0.0 ; set netremmax($b) 0.0
                set netpaths($b) {}
            }
            incr netcount($b)
            lappend netpaths($b) $npath
            set netcum($b) [expr {$netcum($b) + $rel}]
            set netrem($b) [expr {$netrem($b) + ($W(total) - $cum)}]
            if {$rel > $netcummax($b)} { set netcummax($b) $rel }
            if {($W(total) - $cum) > $netremmax($b)} { set netremmax($b) [expr {$W(total)-$cum}] }
        }
        # an UNRESOLVED node is NOT evidence of register-only-ness
        if {$r != 0} { set netregonly($b) 0 }
        incr idx
    }
    array unset seen ; array unset occ
    if {$merge < 0} { incr n_nomerge }
    lappend rows [list $npath $slack $lv $data [llength $W(cells)] $nro $npd $merge $merge_idx $W(from) $W(to) $nun]
    array unset W
}

emit ""
emit [format "%4s %8s %5s %9s %6s %6s %6s %5s %10s %7s" \
          "#" "slack" "lvls" "dataDly" "cells" "regO" "pinD" "unres" "mergeNs" "mergeIx"]
foreach r $rows {
    set mg [lindex $r 7]
    set mi [lindex $r 8]
    if {$mg < 0} { set mgs "     none" ; set mis "   n/a" } \
        else { set mgs [format "%10.3f" $mg] ; set mis [format "%7d" $mi] }
    emit [format "%4d %8.3f %5s %9.3f %6d %6d %6d %5d %s %s" \
              [lindex $r 0] [lindex $r 1] [lindex $r 2] [lindex $r 3] \
              [lindex $r 4] [lindex $r 5] [lindex $r 6] [lindex $r 11] $mgs $mis]
}
emit ""
emit "  (mergeNs = cumulative DATA delay, measured from the launch register's"
emit "   output pin, at which the FIRST pin-dependent node appears.  mergeIx is"
emit "   that node's index in the path's combinational cell list, so mergeIx IS"
emit "   the REG-ONLY prefix depth and cells-mergeIx the PIN-DEP suffix depth.)"
emit ""
emit [format "  paths with NO pin-dependent node at all (merge point UNDEFINED): %d of %d" \
          $n_nomerge $npath]
emit "  -- reported as its own class; it is NOT folded into 0 and NOT into the total."
emit ""
emit [format "  worst \$v30u_ce -> \$v30u_ce DATA delay in this population: %.3f ns" $worst_data]
emit "     $worst_desc"
if {$n_unresolved > 0} {
    emit ""
    emit [format "  ⚠ UNRESOLVED nodes (neither get_pins nor get_nets answered): %d" $n_unresolved]
    foreach u [lsort -unique $unresolved_list] { emit "      $u" }
}

# per-path detail: worst path's own prefix/suffix
set r0 [lindex $rows 0]
emit ""
emit "  THE WORST PATH'S SPLIT:"
emit [format "    data delay %.3f ns over %d combinational cells" [lindex $r0 3] [lindex $r0 4]]
emit [format "    REG-ONLY %d   PIN-DEP %d" [lindex $r0 5] [lindex $r0 6]]

# ---------------------------------------------------------------------------
# §C. THE CUT-POINT CENSUS.  This is what picks the design.
# ---------------------------------------------------------------------------
emit ""
emit "=== C. CUT-POINT CENSUS -- nets on >= 25% of the $npath paths ==="
emit "  A cut is USABLE only if the net is REG-ONLY on every path it appears on"
emit "  (so stage 1 is phase-stable by the theorem) AND its (upstream,"
emit "  downstream) split is balanced.  Sorted by |up - down| on the MEAN."
emit ""
emit [format "%5s %7s %9s %9s %9s %9s  %-8s %s" \
          "paths" "%pop" "up.mean" "dn.mean" "up.max" "dn.max" "REGONLY" "net"]
set crows {}
foreach n [array names netcount] {
    if {$netcount($n) * 4 < $npath} { continue }
    set up [expr {$netcum($n)/$netcount($n)}]
    set dn [expr {$netrem($n)/$netcount($n)}]
    lappend crows [list [expr {abs($up-$dn)}] $netcount($n) $up $dn \
                       $netcummax($n) $netremmax($n) $netregonly($n) $n]
}
foreach r [lsort -real -increasing -index 0 $crows] {
    emit [format "%5d %6.1f%% %9.3f %9.3f %9.3f %9.3f  %-8s %s" \
              [lindex $r 1] [expr {100.0*[lindex $r 1]/$npath}] \
              [lindex $r 2] [lindex $r 3] [lindex $r 4] [lindex $r 5] \
              [expr {[lindex $r 6] ? "yes" : "NO"}] [lindex $r 7]]
}

# The A-4 existence question, scored here so it is not scored by eye.
emit ""
emit "=== C.2  THE A-4 EXISTENCE QUESTION ==="
emit [format "  bar: a net REG-ONLY on every path it appears on, present on >= 50%% of the"]
emit [format "       %d paths, whose upstream AND downstream halves are each <= 60%% of the" $npath]
emit [format "       worst \$v30u_ce -> \$v30u_ce data delay (%.3f ns) => <= %.3f ns" \
          $worst_data [expr {0.60*$worst_data}]]
set lim [expr {0.60*$worst_data}]
set a4_mean {} ; set a4_max {}
foreach r $crows {
    if {[lindex $r 6] != 1} { continue }
    if {[lindex $r 1] * 2 < $npath} { continue }
    if {[lindex $r 2] <= $lim && [lindex $r 3] <= $lim} { lappend a4_mean [lindex $r 7] }
    if {[lindex $r 4] <= $lim && [lindex $r 5] <= $lim} { lappend a4_max [lindex $r 7] }
}
emit [format "  candidates on the MEAN split : %d" [llength $a4_mean]]
foreach c $a4_mean { emit "      $c" }
emit [format "  candidates on the MAX  split : %d   <-- A-4 is scored on THIS, the strict reading" \
          [llength $a4_max]]
foreach c $a4_max { emit "      $c" }
if {[llength $a4_max] > 0} { emit "  A-4: MET" } else { emit "  A-4: MISSED" }

# ---------------------------------------------------------------------------
# §D. THE WORST THREE PATHS, NODE BY NODE.
# ---------------------------------------------------------------------------
emit ""
emit "=== D. THE WORST THREE PATHS, NODE BY NODE ==="
emit "  (PD column: 1 = pin-dependent under LIVE_NARROW, 0 = register-only,"
emit "   '.' = not a data-path combinational cell)"
foreach d $dumps {
    emit ""
    emit [format "  --- path %d ---" [lindex $d 0]]
    emit "  from: [lindex $d 1]"
    emit "  to  : [lindex $d 2]"
    emit [format "  %2s %8s %8s %-6s %-6s %s" "PD" "incr" "cum" "type" "phase" "node"]
    foreach ent [lindex $d 3] {
        set line [lindex $ent 0]
        set nm   [lindex $ent 1]
        set pd "."
        if {[info exists PDN($nm)]} { set pd [expr {$PDN($nm) == 1 ? "1" : ($PDN($nm) == 0 ? "0" : "?")}] }
        emit "  $pd $line"
    }
}

emit ""
emit "=== RESOLVER CENSUS (which collection command answered) ==="
array set kc {}
foreach n [array names THRU_KIND] {
    set k $THRU_KIND($n)
    if {[info exists kc($k)]} { incr kc($k) } else { set kc($k) 1 }
}
foreach k [lsort [array names kc]] { emit [format "  %-12s %d" $k $kc($k)] }
emit [format "  distinct nodes classified (LIVE_NARROW): %d" [array size PDN]]
emit [format "  distinct nodes classified (LIVE_WIDE)  : %d" [array size PDW]]

close $fh
puts "wrote $out.phasesplit.txt"
project_close
