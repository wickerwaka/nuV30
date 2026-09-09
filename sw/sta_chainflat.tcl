# WAVE 6 -- THE CHAIN FLATTENING STUDY.  STANDALONE-HARNESS STA.
# MEASUREMENT ONLY; NOT A GATE; IT WRITES NO RECEIPT AND NO Fmax QUOTED FROM IT
# IS A DESIGN FIGURE.  The project is `v30u_eu` AS ITS OWN TOP with virtual
# pins (ucore_provenance.md sec.51.1's harness), compiled for the same device
# and the same optimisation mode as the design, so that the 7-copy chain and
# the flattened one are compared to EACH OTHER and to nothing else.
#
# args: {project revision OUTPREFIX ?npaths?}
#
# The walker, the segmenter and `basename2` are WAVE 5's
# (`sw/sta_chain_anatomy.tcl`), reproduced here because that script collects
# registers by the DESIGN's hierarchy (`*|v30u_eu:*|*`) and refuses below 1,000
# of them -- neither of which is true of a standalone `v30u_eu`.
#
# ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection
#   (WAVE 1 sec.0.2): PC-1 re-demonstrates that live on THIS netlist.
# ⚠ `string match` on a name carrying a bus index FAILS -- every prefix test
#   here is `string first ... == 0`.
project_open [lindex $quartus(args) 0] -revision [lindex $quartus(args) 1]
set PFX [lindex $quartus(args) 2]
set NP  [lindex $quartus(args) 3]
if {$NP eq ""} { set NP 200 }
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
set PINISH {combout dataa datab datac datad datae dataf q d clk cin cout \
            sumout shareout o i inclk outclk regout datain}
proc basename2 {name} {
    global PINISH
    set segs [split [norm $name] "|"]
    if {[llength $segs] > 1 && [lsearch -exact $PINISH [lindex $segs end]] >= 0} {
        set segs [lrange $segs 0 end-1]
    }
    set last [lindex $segs end]
    set t [string first "~" $last]
    if {$t >= 0} { set last [string range $last 0 [expr {$t-1}]] }
    set b [string first "\[" $last]
    if {$b >= 0} { set last [string range $last 0 [expr {$b-1}]] }
    return $last
}

proc walk {p} {
    set from [get_node_info [get_path_info $p -from] -name]
    set to   [get_node_info [get_path_info $p -to] -name]
    set fn [norm $from] ; set tn [norm $to]
    set state 0 ; set cum 0.0 ; set launch 0.0
    set pts {} ; set dump {} ; set ncell 0 ; set ncomb 0
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
        set tag CLK
        if {$state == 1} { set tag LAUNCH } elseif {$state == 2} { set tag DATA } \
            elseif {$state == 3} { set tag DEST }
        if {$state == 2} {
            lappend pts [list $nm $cum $inc $ty]
            if {$ty eq "cell"} { incr ncell }
            if {[string first "|combout" $nm] >= 0} { incr ncomb }
        }
        lappend dump [format "%8.3f %8.3f %-6s %-5s %s" $inc $cum $ty $tag $nm]
    }
    return [list ok 1 pts $pts dump $dump total $cum launch $launch \
                from $from to $to ncell $ncell ncomb $ncomb state $state]
}

proc segment {pts markers} {
    set segs {} ; set cuts {} ; set names {}
    set start -1.0 ; set nc 0 ; set nb 0 ; set inmark 0 ; set pend 0.0
    foreach e $pts {
        foreach {nm cum inc ty} $e break
        if {$start < 0} { set start [expr {$cum - $inc}] }
        set b [basename2 $nm]
        set ismark [expr {[lsearch -exact $markers $b] >= 0}]
        if {$ismark} {
            set inmark 1
            set pend $cum
        } else {
            if {$inmark} {
                lappend segs [list $start $pend $nc $nb $names]
                lappend cuts $pend
                set start $pend ; set nc 0 ; set nb 0 ; set names {}
                set inmark 0
            }
            if {$ty eq "cell"} { incr nc }
            if {[string first "|combout" $nm] >= 0} { incr nb ; lappend names [basename2 $nm] }
        }
    }
    if {$inmark} { lappend segs [list $start $pend $nc $nb $names] ; lappend cuts $pend
                   set start $pend ; set nc 0 ; set nb 0 ; set names {} }
    lappend segs [list $start [lindex [lindex $pts end] 1] $nc $nb $names]
    return [list segs $segs cuts $cuts]
}

emit "=== sta_chainflat (WAVE 6) ==="
emit "  revision [lindex $quartus(args) 1]   npaths $NP"

set REGS [get_registers -nowarn {*}]
emit [format "  registers in the netlist: %d" [get_collection_size $REGS]]
if {[get_collection_size $REGS] < 200} {
    emit "CONTROL FAILED: implausibly few registers.  REFUSING." ; close $fh
    project_close ; exit 3
}

# =========================================================================
# A.  THE POSITIVE CONTROLS.  REPORTED FIRST.
# =========================================================================
emit ""
emit "=== A. POSITIVE CONTROLS ==="
set CTL_OK 1
set W ""
foreach_in_collection p [get_timing_paths -from $REGS -to $REGS -setup \
                             -npaths 1 -detail full_path] { set W $p }
if {$W eq ""} { emit "  NO reg->reg PATH -- REFUSING" ; close $fh
                project_close ; exit 3 }
array set WK [walk $W]

set probe ""
foreach e $WK(pts) {
    foreach {nm cum inc ty} $e break
    if {[string first "|combout" $nm] >= 0} { set probe $nm ; break }
}
set n_pins 0 ; set n_nodes 0 ; set c_pins 0 ; set c_nodes 0
if {$probe ne ""} {
    set cp [get_pins -nowarn $probe] ; set cn [get_nodes -nowarn $probe]
    set c_pins [get_collection_size $cp] ; set c_nodes [get_collection_size $cn]
    if {$c_pins > 0} { set n_pins [get_collection_size \
        [get_timing_paths -from $REGS -to $REGS -through $cp -setup -npaths 1]] }
    if {$c_nodes > 0} { set n_nodes [get_collection_size \
        [get_timing_paths -from $REGS -to $REGS -through $cn -setup -npaths 1]] }
}
emit "  PC-1 RESOLVER   probe node: $probe"
emit [format "       get_pins  collection %d -> paths %d   (MUST be >= 1)" $c_pins $n_pins]
emit [format "       get_nodes collection %d -> paths %d   (WAVE 1: silently 0)" $c_nodes $n_nodes]
if {$n_pins < 1} { set CTL_OK 0 ; emit "       *** PC-1 FAILED ***" } else { emit "       PC-1 PASS" }

set dd [get_path_info $W -data_delay]
set wd [expr {$WK(total) - $WK(launch)}]
emit [format "  PC-2 WALKER     state %d (MUST be 3)   data cells %d (MUST be >= 3)" \
          $WK(state) $WK(ncell)]
emit [format "                  walker %.3f vs Quartus -data_delay %s  diff %.3f (MUST be <= 0.01)" \
          $wd $dd [expr {abs($wd - $dd)}]]
if {$WK(state) != 3 || $WK(ncell) < 3 || abs($wd - $dd) > 0.01} {
    set CTL_OK 0 ; emit "       *** PC-2 FAILED ***" } else { emit "       PC-2 PASS" }

# PC-3 THE SEGMENTER.  Forced through an `st_n` pin -- a boundary crossing BY
# CONSTRUCTION -- the segmenter must report >= 1 boundary; the SAME path under
# a marker name that does not exist must report 0.
set stp [get_pins -nowarn -compatibility_mode {*st_n~*|combout}]
emit [format "  PC-3 SEGMENTER  st_n combout pins in the netlist: %d" [get_collection_size $stp]]
set nb_pos -1 ; set nb_neg -1 ; set forced_pin ""
set tries 0
foreach_in_collection pin $stp {
    if {$nb_pos >= 1 || $tries >= 40} { break }
    incr tries
    set ps [get_timing_paths -from $REGS -to $REGS -through $pin -setup \
                -npaths 1 -detail full_path]
    if {[get_collection_size $ps] == 0} { continue }
    foreach_in_collection Z $ps {
        array unset ZK ; array set ZK [walk $Z]
        array unset S1 ; array set S1 [segment $ZK(pts) {st_n stop st_zero_ok}]
        array unset S0 ; array set S0 [segment $ZK(pts) {XYZZY_NO_SUCH_NET}]
        set nb_pos [llength $S1(cuts)] ; set nb_neg [llength $S0(cuts)]
        set forced_pin [get_node_info $pin -name]
    }
}
emit "       the pin that answered: $forced_pin   (single-pin tries $tries)"
emit [format "       boundaries, real markers : %d  (MUST be >= 1)" $nb_pos]
emit [format "       boundaries, fake marker  : %d  (MUST be 0)" $nb_neg]
if {$nb_pos < 1 || $nb_neg != 0} { set CTL_OK 0 ; emit "       *** PC-3 FAILED ***" } \
    else { emit "       PC-3 PASS" }
emit ""
emit [format "  CONTROLS: %s" [expr {$CTL_OK ? "ALL PASS" : "*** A CONTROL FAILED ***"}]]

# =========================================================================
# B.  THE WORST reg -> reg ARC, SEGMENTED
# =========================================================================
emit ""
emit "=== B. THE WORST reg -> reg ARC ==="
set sl [get_path_info $W -slack]
emit [format "  slack        %.3f" $sl]
emit [format "  data delay   %.3f" $dd]
emit [format "  levels       %d cells / %d combout" $WK(ncell) $WK(ncomb)]
emit "  from         $WK(from)"
emit "  to           $WK(to)"
array set SG [segment $WK(pts) {st_n stop st_zero_ok}]
emit [format "  boundaries   %d" [llength $SG(cuts)]]
set i 0
foreach s $SG(segs) {
    foreach {a b nc nb nms} $s break
    emit [format "    seg %d  %8.3f -> %8.3f  = %7.3f  cells %2d  luts %2d  %s" \
              $i $a $b [expr {$b - $a}] $nc $nb [lrange $nms 0 8]]
    incr i
}
set dfh [open "${PFX}.arrivalpoints.txt" w]
foreach l $WK(dump) { puts $dfh $l }
close $dfh

# =========================================================================
# C.  THE ENDPOINT-DIVERSE SCAN -- worst arc by number of chain boundaries
# =========================================================================
emit ""
emit "=== C. BOUNDARY-BUCKETED SCAN (npaths $NP) ==="
array set BUCK {}
array set BCNT {}
set n 0
foreach_in_collection p [get_timing_paths -from $REGS -to $REGS -setup \
                             -npaths $NP -detail full_path] {
    incr n
    array unset PK ; array set PK [walk $p]
    if {![info exists PK(pts)] || [llength $PK(pts)] == 0} { continue }
    array unset SS ; array set SS [segment $PK(pts) {st_n stop st_zero_ok}]
    set nb [llength $SS(cuts)]
    set d [expr {$PK(total) - $PK(launch)}]
    if {![info exists BUCK($nb)] || $d > $BUCK($nb)} { set BUCK($nb) $d }
    if {![info exists BCNT($nb)]} { set BCNT($nb) 0 }
    incr BCNT($nb)
}
emit [format "  paths walked %d" $n]
foreach k [lsort -integer [array names BUCK]] {
    emit [format "  boundaries %2d : worst data delay %8.3f   count %d" \
              $k $BUCK($k) $BCNT($k)]
}

# =========================================================================
# D.  THE COPY CENSUS -- how many distinct cones carry each RTL base name
# =========================================================================
emit ""
emit "=== D. COPY CENSUS (distinct combout cones per RTL base name) ==="
array set CENS {}
set allc [get_pins -nowarn -compatibility_mode {*|combout}]
set ncones 0
foreach_in_collection q $allc {
    incr ncones
    set b [basename2 [get_node_info $q -name]]
    if {![info exists CENS($b)]} { set CENS($b) 0 }
    incr CENS($b)
}
emit [format "  combout cones in the netlist: %d" $ncones]
foreach nmz {st_n stop st_zero_ok ld_b_n pv opc_base m_kind seg_override_n
             sigma s1_val it_val rst_ctr_n ld_dlo_n ld_ripe_prev_n
             nmi_latch_n rloop_n_n zzz_no_such_signal} {
    set v 0
    if {[info exists CENS($nmz)]} { set v $CENS($nmz) }
    emit [format "  %-22s %d" $nmz $v]
}
set tfh [open "${PFX}.census.txt" w]
foreach k [lsort [array names CENS]] { puts $tfh [format "%-40s %d" $k $CENS($k)] }
close $tfh

emit ""
emit [format "RESULT controls=%s" [expr {$CTL_OK ? "PASS" : "FAIL"}]]
close $fh
project_close
if {!$CTL_OK} { exit 4 }
exit 0
