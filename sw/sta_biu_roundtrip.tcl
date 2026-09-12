# WAVE 10 -- THE UNIFIED BIU ROUND-TRIP CENSUS.  MEASUREMENT ONLY; NOT A GATE,
# NO RECEIPT, NO Fmax MAY BE QUOTED FROM IT.
#
# WAVE 8 sec.4 and WAVE 9 sec.5.4 measured the EU -> BIU -> EU combinational round
# trip `q_cnt -> poppable_n -> q_ripe_lead_n` and disagreed 0-of-1,200 against
# 200-of-200.  `sw/biu_predicate_reconcile.py` established OFFLINE, on both
# waves' own committed artifacts, that their MATCH selects the identical node
# set (AX-1) and their SECTION selects the same points on a `ce -> ce` path
# (AX-2), and that they differ only in POPULATION (AX-3: endpoint-diverse
# `-nworst 1` against top-N-by-slack) and in SPAN CONVENTION (AX-4: WAVE 8
# includes the interconnect INTO the first BIU node, WAVE 9 does not).
#
# **THIS FILE ASKS BOTH POPULATION QUESTIONS IN ONE STA SESSION AND REPORTS BOTH
# SPAN CONVENTIONS SIDE BY SIDE, SO A DRAW CANNOT ANSWER ONE AND NOT THE OTHER.**
#
# args: {project revision OUTPREFIX NA NB}
#   NA  paths for POPULATION A -- `-npaths NA`, no diversity constraint (WAVE 9)
#   NB  paths for POPULATION B -- `-npaths NB -nworst 1` (WAVE 8)
#
# POSITIVE CONTROLS, REPORTED FIRST.  A MISS VOIDS THE DRAW (WAVE 10 bar K-1).
#   PC-W1  THE RESOLVER.  `-through` a `get_pins` collection returns paths;
#          `-through` the same name as `get_nodes` silently returns none
#          (WAVE 1 sec.0.2).  Demonstrated live, not cited.
#   PC-W2  THE MATCHER CAN SAY YES.  Forced through ONE NAMED `q_ripe_lead_n`
#          combout pin, the counter must find BIU nodes -- so a 0 on the free
#          population is a measurement and not a broken test.
#   PC-W3  THE KNOWN-WRONG FORMS, printed beside PC-W2 and required to read 0:
#          the `v30u_biu:` TYPE prefix (WAVE 4 sec.6.1 item 1) and an instance
#          name that does not exist.
#   PC-W4  THE BULK `-through`, printed and never relied on.  A bulk figure
#          BELOW the single-pin figure is `-through` accepted-and-ignored.
#   PC-W5  BOTH DESTINATION PIN FORMS.  WAVE 9's own diagnostic control failed
#          because `upc_page[0]` is a SYNCHRONOUS-LOAD register written through
#          `|asdata`, not `|d`.  This forces a path to a named register through
#          `|d` AND through `|asdata` and reports which answered.  At least one
#          must.
#
# EVERY `-through` IS ONE PIN AT A TIME (`get_pins`, never `get_nodes`).
# `string match` on a name with a bus index FAILS (`[3]` is a character class),
# so every test here is `string first`.
project_open [lindex $quartus(args) 0] -revision [lindex $quartus(args) 1]
set PFX [lindex $quartus(args) 2]
set NA  [lindex $quartus(args) 3]
set NB  [lindex $quartus(args) 4]
if {$NA eq ""} { set NA 200 }
if {$NB eq ""} { set NB 400 }
create_timing_netlist -model slow
read_sdc
update_timing_netlist

set fh [open "${PFX}.txt" w]
proc emit {s} { global fh ; puts $fh $s ; puts $s }

proc norm {name} {
    set o {}
    foreach s [split $name "|"] {
        set c [string first ":" $s]
        if {$c >= 0} { set s [string range $s [expr {$c+1}] end] }
        lappend o $s
    }
    return [join $o "|"]
}
proc hasprefix {s p} { return [expr {[string first $p $s] == 0}] }

# --- THE PREDICATES, both of them, transcribed from the two instruments.
proc p9 {nm}  { return [expr {[string first "|u_biu|" $nm] >= 0}] }
proc p8 {nm}  { return [expr {[string first "|u_biu|" [norm $nm]] >= 0}] }
proc pkw {nm} { return [expr {[string first "v30u_biu:" $nm] >= 0}] }
proc pabs {nm} { return [expr {[string first "|u_no_such_instance|" $nm] >= 0}] }
proc prip {nm} { return [expr {[string first "q_ripe_lead_n" $nm] >= 0}] }

emit "=== sta_biu_roundtrip (WAVE 10) ==="
emit "  revision [lindex $quartus(args) 1]   NA $NA (no -nworst)   NB $NB (-nworst 1)"

set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] \
                                 [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
emit [format "  \$v30u_ce %d   \$v30u_half %d" \
          [get_collection_size $v30u_ce] [get_collection_size $v30u_half]]
if {[get_collection_size $v30u_ce] < 1000} {
    emit "CONTROL FAILED: \$v30u_ce implausibly short.  REFUSING."
    close $fh ; project_close ; exit 3
}

# --------------------------------------------------------------------- walker
# Returns, for one path: the FULL arrival-point list and the index at which the
# DATA section begins/ends, so AX-2 (data-only vs all-points) is measured LIVE
# on every draw rather than assumed from WAVE 8's artifacts.
proc walk {p} {
    set from [get_node_info [get_path_info $p -from] -name]
    set to   [get_node_info [get_path_info $p -to] -name]
    set fn [norm $from] ; set tn [norm $to]
    set state 0 ; set cum 0.0 ; set launch 0.0
    set pts {} ; set dump {}
    if {[catch {set ap [get_path_info $p -arrival_points]} err]} {
        return [list ok 0 err $err]
    }
    foreach_in_collection q $ap {
        set nd [get_point_info $q -node]
        if {$nd eq ""} { continue }
        set nm [get_node_info $nd -name]
        set inc [get_point_info $q -incr]
        set ty  [get_point_info $q -type]
        if {$inc eq ""} { set inc 0.0 }
        set cum [expr {$cum + $inc}]
        set nn [norm $nm]
        if {$state == 0} { if {[hasprefix $nn $fn]} { set state 1 } }
        if {$state == 1} {
            if {[hasprefix $nn $fn]} { set launch $cum } else { set state 2 }
        }
        if {$state == 2 && [hasprefix $nn $tn]} { set state 3 }
        # sec = 1 while inside the DATA section (WAVE 8's `pts`), 0 otherwise.
        set sec [expr {$state == 2 ? 1 : 0}]
        lappend pts [list $nm $cum $inc $ty $sec]
        lappend dump [format "%8.3f %8.3f %-6s %d %s" $inc $cum $ty $sec $nm]
    }
    return [list ok 1 pts $pts dump $dump total $cum launch $launch \
                from $from to $to state $state]
}

# Census ONE path.  Returns a flat list of the eight quantities the report
# needs, computed under BOTH sections and BOTH span conventions.
proc census1 {pts} {
    set n9_all 0 ; set n9_dat 0 ; set n8_dat 0 ; set nkw 0 ; set nabs 0 ; set nrip 0
    set f_tot -1.0 ; set f_pre -1.0 ; set l_tot -1.0
    set fd_tot -1.0 ; set fd_pre -1.0 ; set ld_tot -1.0
    foreach e $pts {
        foreach {nm cum inc ty sec} $e break
        if {[pkw  $nm]} { incr nkw }
        if {[pabs $nm]} { incr nabs }
        if {[prip $nm] && $sec} { incr nrip }
        if {[p9 $nm]} {
            incr n9_all
            if {$f_tot < 0.0} { set f_tot $cum ; set f_pre [expr {$cum - $inc}] }
            set l_tot $cum
            if {$sec} {
                incr n9_dat
                if {$fd_tot < 0.0} { set fd_tot $cum ; set fd_pre [expr {$cum - $inc}] }
                set ld_tot $cum
            }
        }
        if {[p8 $nm] && $sec} { incr n8_dat }
    }
    # WAVE 9's span: all points, last.total - first.total.
    set s9 0.0
    if {$n9_all > 0 && $l_tot > $f_tot} { set s9 [expr {$l_tot - $f_tot}] }
    # WAVE 8's span: data section, last.total - (first.total - first.incr).
    set s8 0.0
    if {$n9_dat > 0 && $ld_tot > $fd_pre} { set s8 [expr {$ld_tot - $fd_pre}] }
    return [list $n9_all $n9_dat $n8_dat $nkw $nabs $nrip $s9 $s8]
}

# ==========================================================================
# A.  THE POSITIVE CONTROLS.  RUN FIRST.  THEY GATE EVERYTHING BELOW (K-1).
# ==========================================================================
emit ""
emit "=== A. POSITIVE CONTROLS (reported FIRST; a miss voids the draw) ==="
set CTL_OK 1

set W ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                             -npaths 1 -detail full_path] { set W $p }
if {$W eq ""} { emit "  NO ce->ce PATH -- REFUSING" ; close $fh ; project_close ; exit 3 }
array set WK [walk $W]

# --- PC-W1 THE RESOLVER, demonstrated live on a pin that is really on a path.
set probe ""
foreach e $WK(pts) {
    foreach {nm cum inc ty sec} $e break
    if {$sec && [string first "|combout" $nm] >= 0} { set probe $nm ; break }
}
set c_pins 0 ; set c_nodes 0 ; set n_pins 0 ; set n_nodes 0
if {$probe ne ""} {
    set cp [get_pins -nowarn $probe] ; set cn [get_nodes -nowarn $probe]
    set c_pins [get_collection_size $cp] ; set c_nodes [get_collection_size $cn]
    if {$c_pins > 0} { set n_pins [get_collection_size \
        [get_timing_paths -from $v30u_ce -to $v30u_ce -through $cp -setup -npaths 1]] }
    if {$c_nodes > 0} { set n_nodes [get_collection_size \
        [get_timing_paths -from $v30u_ce -to $v30u_ce -through $cn -setup -npaths 1]] }
}
emit "  PC-W1 RESOLVER   probe: $probe"
emit [format "        get_pins  %d -> paths %d   (MUST be >= 1)" $c_pins $n_pins]
emit [format "        get_nodes %d -> paths %d   (WAVE 1 sec.0.2: silently 0)" $c_nodes $n_nodes]
if {$n_pins < 1} { set CTL_OK 0 ; emit "        *** PC-W1 FAILED ***" } else { emit "        PC-W1 PASS" }

# --- PC-W2 / PC-W3  THE MATCHER CAN SAY YES, AND THE WRONG FORMS SAY NO.
set biu_pos -1 ; set biu_kw -1 ; set biu_abs -1 ; set biu_pin "" ; set tries 0
set biu_p8 -1
foreach pat {{*|u_biu|q_ripe_lead_n~*|combout} {*|u_biu|q_cnt~*|combout}
             {*|u_biu|*|combout}} {
    if {$biu_pos >= 1} { break }
    foreach_in_collection pin [get_pins -nowarn -compatibility_mode $pat] {
        if {$tries >= 80 || $biu_pos >= 1} { break }
        incr tries
        set ps [get_timing_paths -from $v30u_ce -to $v30u_ce -through $pin \
                    -setup -npaths 1 -detail full_path]
        if {[get_collection_size $ps] == 0} { continue }
        foreach_in_collection B $ps {
            array unset BK ; array set BK [walk $B]
            if {!$BK(ok)} { continue }
            set c [census1 $BK(pts)]
            if {[lindex $c 0] >= 1} {
                set biu_pos [lindex $c 0] ; set biu_p8 [lindex $c 2]
                set biu_kw [lindex $c 3] ; set biu_abs [lindex $c 4]
                set biu_pin [get_node_info $pin -name]
            }
        }
    }
}
set biup [get_pins -nowarn -compatibility_mode {*|u_biu|*|combout}]
set biu_bulk -1
if {[get_collection_size $biup] > 0} {
    set BB ""
    foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce \
                                 -through $biup -setup -npaths 1 -detail full_path] { set BB $p }
    if {$BB ne ""} {
        array unset BQ ; array set BQ [walk $BB]
        set biu_bulk [lindex [census1 $BQ(pts)] 0]
    }
}
emit [format "  PC-W2 MATCHER    |u_biu| combout pins in the netlist: %d  (single-pin tries %d)" \
          [get_collection_size $biup] $tries]
emit [format "        BIU nodes on a path forced through ONE NAMED PIN : %d  (MUST be >= 1)" $biu_pos]
emit "        the pin that answered : $biu_pin"
emit [format "  PC-W3 WRONG FORMS  ...the `v30u_biu:` TYPE prefix, same path : %d  (MUST be 0)" $biu_kw]
emit [format "                     ...an instance that does not exist        : %d  (MUST be 0)" $biu_abs]
emit [format "        (AX-1 live: WAVE 8's normalising predicate on the same path: %d)" $biu_p8]
emit [format "  PC-W4 BULK       the BULK -through of %d pins yields : %d BIU nodes" \
          [get_collection_size $biup] $biu_bulk]
emit "        (a BULK figure BELOW the single-pin figure is `-through` being"
emit "         ACCEPTED AND IGNORED -- printed, never relied on)"
if {$biu_pos < 1 || $biu_kw != 0 || $biu_abs != 0} {
    set CTL_OK 0 ; emit "        *** PC-W2/W3 FAILED ***" } else { emit "        PC-W2/W3 PASS" }

# --- PC-W5  BOTH DESTINATION PIN FORMS.  WAVE 9 sec.5.1: `upc_page[0]` is a
#     SYNCHRONOUS-LOAD register written through `|asdata`, not `|d`.
set pc5_d 0 ; set pc5_as 0 ; set pc5_name ""
set dreg [get_node_info [get_path_info $W -to] -name]
set pc5_name $dreg
foreach {tag pat} [list d "${dreg}|d" asdata "${dreg}|asdata" datain "${dreg}|datain"] {
    set cp [get_pins -nowarn -compatibility_mode $pat]
    set k 0
    if {[get_collection_size $cp] > 0} {
        set k [get_collection_size [get_timing_paths -from $v30u_ce -to $v30u_ce \
                                        -through $cp -setup -npaths 1]]
    }
    emit [format "  PC-W5 PINFORM    %-8s pins %d -> paths %d" $tag [get_collection_size $cp] $k]
    if {$tag eq "d"} { set pc5_d $k } elseif {$tag eq "asdata"} { set pc5_as $k }
}
emit "        destination register : $pc5_name"
emit [format "        at least one form must answer : %s" \
          [expr {($pc5_d + $pc5_as) >= 1 ? {YES} : {*** NO ***}}]]
if {($pc5_d + $pc5_as) < 1} { set CTL_OK 0 ; emit "        *** PC-W5 FAILED ***" } \
    else { emit "        PC-W5 PASS" }

emit ""
emit "  === CONTROLS: [expr {$CTL_OK ? {ALL PASS} : {*** FAILED -- NOTHING BELOW MAY BE QUOTED ***}}] ==="
if {!$CTL_OK} { close $fh ; project_close ; exit 4 }

# ==========================================================================
# B.  THE WORST ARC, DUMPED
# ==========================================================================
set wc [census1 $WK(pts)]
emit ""
emit "=== B. THE WORST ce->ce ARC ==="
emit "  from : $WK(from)"
emit "  to   : $WK(to)"
emit [format "  slack %+8.3f   levels %s   data delay %s" \
          [get_path_info $W -slack] [get_path_info $W -num_logic_levels] \
          [get_path_info $W -data_delay]]
emit [format "  BIU nodes (all points) %d   (data section) %d   q_ripe_lead_n points %d" \
          [lindex $wc 0] [lindex $wc 1] [lindex $wc 5]]
emit [format "  span WAVE 9 convention %.3f ns   span WAVE 8 convention %.3f ns" \
          [lindex $wc 6] [lindex $wc 7]]
set ap [open "${PFX}.arrivalpoints.txt" w]
puts $ap "# incr cum type in_data_section name"
foreach l $WK(dump) { puts $ap $l }
close $ap

# ==========================================================================
# C.  THE TWO POPULATIONS, ONE PREDICATE.
# ==========================================================================
proc population {tag paths outfh} {
    global fh
    set n 0 ; set c9 0 ; set c9d 0 ; set c8 0 ; set crip 0 ; set ckw 0 ; set cabs 0
    set s9sum 0.0 ; set s8sum 0.0 ; set s9max 0.0
    set pairs [list]
    foreach_in_collection p $paths {
        array unset K ; array set K [walk $p]
        if {!$K(ok)} { continue }
        incr n
        set c [census1 $K(pts)]
        foreach {n9a n9d n8d nkw nabs nrip s9 s8} $c break
        if {$n9a > 0} { incr c9 ; set s9sum [expr {$s9sum + $s9}]
                        if {$s9 > $s9max} { set s9max $s9 } }
        if {$n9d > 0} { incr c9d ; set s8sum [expr {$s8sum + $s8}] }
        if {$n8d > 0} { incr c8 }
        if {$nrip > 0} { incr crip }
        if {$nkw  > 0} { incr ckw }
        if {$nabs > 0} { incr cabs }
        lappend pairs "$K(from)\t$K(to)"
        puts $outfh [format "R %s %d %s %s %d %d %d %d %.3f %.3f %s %s" $tag $n \
                         [get_path_info $p -slack] [get_path_info $p -data_delay] \
                         $n9a $n9d $nrip $nkw $s9 $s8 $K(from) $K(to)]
    }
    set uniq [llength [lsort -unique $pairs]]
    emit ""
    emit "  --- POPULATION $tag ---"
    emit [format "    paths scanned                                : %d" $n]
    emit [format "    DISTINCT (from,to) endpoint pairs            : %d" $uniq]
    emit [format "    ...carrying the round trip (all points)      : %d" $c9]
    emit [format "    ...carrying it in the DATA SECTION           : %d   (AX-2 control: must equal the line above)" $c9d]
    emit [format "    ...under WAVE 8's normalising predicate      : %d   (AX-1 control: must equal it too)" $c8]
    emit [format "    ...carrying `q_ripe_lead_n` BY NAME          : %d" $crip]
    emit [format "    ...matching the KNOWN-WRONG type prefix      : %d   (MUST be 0)" $ckw]
    emit [format "    ...matching an instance that does not exist  : %d   (MUST be 0)" $cabs]
    if {$c9 > 0} {
        emit [format "    mean span, WAVE 9 convention (ns)            : %.3f" [expr {$s9sum / $c9}]]
        emit [format "    max  span, WAVE 9 convention (ns)            : %.3f" $s9max]
    }
    if {$c9d > 0} {
        emit [format "    mean span, WAVE 8 convention (ns)            : %.3f" [expr {$s8sum / $c9d}]]
    }
    return [list $n $c9 $c9d $c8 $ckw $cabs]
}

emit ""
emit "=== C. THE TWO POPULATIONS, ONE PREDICATE ==="
set rows [open "${PFX}.rows.txt" w]
puts $rows "# R <pop> <idx> <slack> <data_delay> <biu_all> <biu_data> <ripe> <typeprefix> <span9> <span8> <from> <to>"
set A [population "A_topN" [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                                -npaths $NA -detail full_path] $rows]
set B [population "B_nworst1" [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                                   -npaths $NB -nworst 1 -detail full_path] $rows]
close $rows

emit ""
emit "=== D. THE AX CONTROLS, SCORED ON THIS DRAW ==="
set ax_ok 1
foreach {tag R} [list A_topN $A B_nworst1 $B] {
    foreach {n c9 c9d c8 ckw cabs} $R break
    set a1 [expr {$c9 == $c8}]
    set a2 [expr {$c9 == $c9d}]
    emit [format "  %-10s AX-1 (both predicates agree) %s    AX-2 (data section == all points) %s    wrong forms %s" \
              $tag [expr {$a1 ? {PASS} : {*** FAIL ***}}] \
              [expr {$a2 ? {PASS} : {*** FAIL ***}}] \
              [expr {($ckw == 0 && $cabs == 0) ? {PASS} : {*** FAIL ***}}]]
    if {!($a1 && $a2 && $ckw == 0 && $cabs == 0)} { set ax_ok 0 }
}
emit [format "  AX CONTROLS: %s" [expr {$ax_ok ? {ALL PASS} : {*** FAILED ***}}]]

close $fh
project_close
