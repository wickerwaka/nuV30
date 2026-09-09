# WAVE 8 -- THE FRONT-END ANATOMY.  MEASUREMENT ONLY; IT IS NOT A GATE AND
# WRITES NO RECEIPT.  No Fmax may be quoted from it.
#
# WAVE 7 flattened the EU's sevenfold chain unroll and the binding `ce -> ce`
# arc moved OUT of the chain and INTO the microcode ROM / front end on every
# draw of both configurations.  The front end has never been attacked.  This
# script measures where its nanoseconds are.
#
# args: {project revision OUTPREFIX npaths markerlist}
#   `markerlist` is a Tcl list of chain-boundary marker BASE NAMES.  IT IS NOT
#   CHOSEN HERE.  It is derived from the RTL by `sw/frontend_srcmap.py`'s
#   committed MARKER RULE and passed in, so this file cannot pick a convenient
#   marker after seeing a refusal (WAVE 8 bar H-2).  An empty list is REFUSED.
#
# ============================ WHAT CHANGED FROM WAVE 5 =====================
# `sw/sta_chain_anatomy.tcl` is WAVE 5's and is UNTOUCHED.  This is a separate
# file because two things had to move:
#
#  (a) PC-3's PIN SELECTION.  WAVE 5's PC-3 forced its control path through an
#      `st_zero_ok` pin SPECIFICALLY.  After the flattening there are none --
#      the nine `st_n == S_X` guards make the nine-way OR redundant and Quartus
#      deletes it -- so the control REFUSED (correctly: it said "0 pins",
#      not "0 boundaries").  Here every marker's pins are tried ONE AT A TIME
#      in the rule's own declared order, the pin that answered is NAMED, and
#      the pin count of EVERY marker is printed INCLUDING the names that have
#      none.  This is WAVE 5's own PC-4 repair pattern applied to PC-3.
#
#  (b) A POPULATION, not one path.  WAVE 1 §0 and every wave since: one arc is
#      one draw of a placement.  §I dumps an ENDPOINT-DIVERSE population
#      (`-nworst 1`, so one path per endpoint pair) to a machine-readable file
#      and `sw/frontend_anat_report.py` censuses it by source-derived STAGE.
#
# ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection
#   (WAVE 1 §0.2) -- `get_pins` is the resolver, and PC-1 re-demonstrates it
#   live rather than citing it.
# ⚠ A BULK `-through` COLLECTION IS THE KNOWN TRAP (WAVE 5 §1.1): it can be
#   accepted and ignored, returning the unconstrained worst path.  Every
#   `-through` here is ONE PIN, and the bulk form is kept and PRINTED beside it
#   as the known-wrong control.
# ⚠ `string match` on a name carrying a bus index FAILS (`[3]` is a character
#   class, WAVE 1 §3.0).  Every prefix test here is `string first ... == 0`.
project_open [lindex $quartus(args) 0] -revision [lindex $quartus(args) 1]
set PFX [lindex $quartus(args) 2]
set NP  [lindex $quartus(args) 3]
set MARKERS [lindex $quartus(args) 4]
if {$NP eq ""} { set NP 400 }
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
set PINISH {combout dataa datab datac datad datae dataf datag q d clk cin cout \
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

emit "=== sta_frontend_anatomy (WAVE 8) ==="
emit "  revision [lindex $quartus(args) 1]   npaths $NP"
emit "  MARKERS (source-derived, passed in, NOT chosen here): $MARKERS"
if {[llength $MARKERS] < 1} {
    emit "REFUSING: empty marker list." ; close $fh ; project_close ; exit 3
}

set v30u_regs [add_to_collection [get_registers -nowarn {*|v30u_eu:*|*}] \
                                 [get_registers -nowarn {*|v30u_biu:*|*}]]
set v30u_half [get_registers -nowarn {*|v30u_biu:*|t1_half2}]
set v30u_ce   [remove_from_collection $v30u_regs $v30u_half]
emit [format "  \$v30u_ce %d   \$v30u_half %d" \
          [get_collection_size $v30u_ce] [get_collection_size $v30u_half]]
if {[get_collection_size $v30u_ce] < 1000} {
    emit "CONTROL FAILED: \$v30u_ce implausibly short.  REFUSING." ; close $fh
    project_close ; exit 3
}

# --------------------------------------------------------------- the walker
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

# ------------------------------------------------------------- the segmenter
# Transliterated from sta_chain_anatomy.tcl and re-implemented independently in
# sw/frontend_srcmap.py, where PC-M2 compares the two marker sets on WAVE 7's
# committed artifacts with no Quartus in the loop.
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

# ==========================================================================
# §A  THE POSITIVE CONTROLS.  RUN FIRST.  THEY GATE EVERYTHING BELOW (H-1).
# ==========================================================================
emit ""
emit "=== A. POSITIVE CONTROLS (reported FIRST; a miss voids the wave) ==="
set CTL_OK 1

set W ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                             -npaths 1 -detail full_path] { set W $p }
if {$W eq ""} { emit "  PC: NO ce->ce PATH -- REFUSING" ; close $fh ; project_close ; exit 3 }
set wk [walk $W]
array set WK $wk

# --- PC-1 THE RESOLVER
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
        [get_timing_paths -from $v30u_ce -to $v30u_ce -through $cp -setup -npaths 1]] }
    if {$c_nodes > 0} { set n_nodes [get_collection_size \
        [get_timing_paths -from $v30u_ce -to $v30u_ce -through $cn -setup -npaths 1]] }
}
emit "  PC-1 RESOLVER   probe node: $probe"
emit [format "       get_pins  collection %d -> paths %d   (MUST be >= 1: the question can say YES)" $c_pins $n_pins]
emit [format "       get_nodes collection %d -> paths %d   (WAVE 1 §0.2: silently 0)" $c_nodes $n_nodes]
if {$n_pins < 1} { set CTL_OK 0 ; emit "       *** PC-1 FAILED ***" } else { emit "       PC-1 PASS" }

# --- PC-2 THE WALKER
set dd [get_path_info $W -data_delay]
set wd [expr {$WK(total) - $WK(launch)}]
emit [format "  PC-2 WALKER     state %d (MUST be 3)   data cells %d (MUST be >= 3)" \
          $WK(state) $WK(ncell)]
emit [format "                  walker data delay %.3f  vs Quartus -data_delay %s   diff %.3f (MUST be <= 0.01)" \
          $wd $dd [expr {abs($wd - $dd)}]]
if {$WK(state) != 3 || $WK(ncell) < 3 || abs($wd - $dd) > 0.01} {
    set CTL_OK 0 ; emit "       *** PC-2 FAILED ***" } else { emit "       PC-2 PASS" }

# --- PC-3 THE SEGMENTER, RE-BASED.
# EVERY marker's pin count is printed, INCLUDING zeros, and `st_zero_ok` --
# the name WAVE 5 cut on and WAVE 7's flattening deleted -- is printed beside
# them as a NAMED KNOWN-ABSENT control.  A marker set whose every name reads 0
# is the WAVE 7 refusal and is refused again, loudly.
emit "  PC-3 SEGMENTER  marker pin census (compatibility_mode: `*` must cross `|`)"
set best_pat "" ; set best_n 0
foreach mk [concat $MARKERS st_zero_ok] {
    set c1 [get_collection_size [get_pins -nowarn -compatibility_mode "*|u_eu|${mk}~*|combout"]]
    set c2 [get_collection_size [get_pins -nowarn -compatibility_mode "*|u_eu|${mk}\[*\]~*|combout"]]
    set tot [expr {$c1 + $c2}]
    set tag ""
    if {[lsearch -exact $MARKERS $mk] < 0} { set tag "   <- NOT a marker under the rule (WAVE 5 cut on it; WAVE 7 deleted it)" }
    emit [format "       %-16s pins %5d  (+%d indexed)%s" $mk $c1 $c2 $tag]
    if {[lsearch -exact $MARKERS $mk] >= 0 && $tot > $best_n} {
        set best_n $tot ; set best_pat $mk
    }
}
set nb_pos -1 ; set nb_neg -1 ; set pc3_pin "" ; set pc3_tries 0
foreach mk $MARKERS {
    if {$nb_pos >= 1} { break }
    foreach pat [list "*|u_eu|${mk}~*|combout" "*|u_eu|${mk}\[*\]~*|combout"] {
        if {$nb_pos >= 1} { break }
        set cand [get_pins -nowarn -compatibility_mode $pat]
        foreach_in_collection pin $cand {
            if {$pc3_tries >= 60 || $nb_pos >= 1} { break }
            incr pc3_tries
            set ps [get_timing_paths -from $v30u_ce -to $v30u_ce -through $pin \
                        -setup -npaths 1 -detail full_path]
            if {[get_collection_size $ps] == 0} { continue }
            foreach_in_collection Z $ps {
                array unset ZK ; array set ZK [walk $Z]
                if {!$ZK(ok)} { continue }
                array unset S1 ; array unset S0
                array set S1 [segment $ZK(pts) $MARKERS]
                array set S0 [segment $ZK(pts) {zzz_no_such_marker_XYZZY}]
                if {[llength $S1(cuts)] >= 1} {
                    set nb_pos [llength $S1(cuts)] ; set nb_neg [llength $S0(cuts)]
                    set pc3_pin [get_node_info $pin -name]
                }
            }
        }
    }
}
emit [format "       boundaries on a path forced through ONE NAMED MARKER PIN : %d  (MUST be >= 1)" $nb_pos]
emit "       the pin that answered : $pc3_pin   (single-pin tries: $pc3_tries)"
emit [format "       the SAME path under a marker that does not exist         : %d  (MUST be 0)" $nb_neg]
if {$nb_pos < 1 || $nb_neg != 0} { set CTL_OK 0 ; emit "       *** PC-3 FAILED ***" } \
    else { emit "       PC-3 PASS" }

# --- PC-4 THE BIU MATCHER (WAVE 5's repaired form, verbatim in shape)
set nbiu_pos -1 ; set nbiu_typ -1 ; set biu_pin "" ; set biu_tries 0
set nbiu_bulk -1
foreach pat {{*|u_biu|q_ripe_lead_n~*|combout} {*|u_biu|q_cnt~*|combout}
             {*|u_biu|*|combout}} {
    if {$nbiu_pos >= 1} { break }
    set cand [get_pins -nowarn -compatibility_mode $pat]
    foreach_in_collection pin $cand {
        if {$biu_tries >= 80 || $nbiu_pos >= 1} { break }
        incr biu_tries
        set ps [get_timing_paths -from $v30u_ce -to $v30u_ce -through $pin \
                    -setup -npaths 1 -detail full_path]
        if {[get_collection_size $ps] == 0} { continue }
        foreach_in_collection B $ps {
            array unset BK ; array set BK [walk $B]
            set a 0 ; set b 0
            foreach e $BK(pts) {
                foreach {nm cum inc ty} $e break
                if {[string first "|u_biu|" $nm] >= 0} { incr a }
                if {[string first "v30u_biu:" $nm] >= 0} { incr b }
            }
            if {$a >= 1} {
                set nbiu_pos $a ; set nbiu_typ $b
                set biu_pin [get_node_info $pin -name]
            }
        }
    }
}
set biup [get_pins -nowarn -compatibility_mode {*|u_biu|*|combout}]
emit [format "  PC-4 BIU        |u_biu| combout pins: %d   (single-pin tries: %d)" \
          [get_collection_size $biup] $biu_tries]
if {[get_collection_size $biup] > 0} {
    set BB ""
    foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce \
                                 -through $biup -setup -npaths 1 -detail full_path] { set BB $p }
    if {$BB ne ""} {
        array unset BQ ; array set BQ [walk $BB]
        set nbiu_bulk 0
        foreach e $BQ(pts) {
            foreach {nm cum inc ty} $e break
            if {[string first "|u_biu|" $nm] >= 0} { incr nbiu_bulk }
        }
    }
}
emit [format "       BIU nodes on a path forced through ONE NAMED PIN : %d  (MUST be >= 1)" $nbiu_pos]
emit "       the pin that answered : $biu_pin"
emit [format "       ...that same path under the TYPE prefix          : %d  (WAVE 4 §6.1: the wrong test)" $nbiu_typ]
emit [format "       ...and the BULK -through of %d pins yields        : %d  BIU nodes" \
          [get_collection_size $biup] $nbiu_bulk]
emit "       (a BULK figure BELOW the single-pin figure is `-through` being"
emit "        ACCEPTED AND IGNORED -- printed, never relied on)"
if {$nbiu_pos < 1} { set CTL_OK 0 ; emit "       *** PC-4 FAILED ***" } else { emit "       PC-4 PASS" }

# --- PC-5 THE ROM HEAD MATCHER.  Same shape, same trap, different hierarchy:
# force a path through ONE NAMED `|u_ucrom|` pin and require the counter to say
# YES; the bulk form is printed beside it.
set nrom_pos -1 ; set rom_pin "" ; set rom_tries 0 ; set nrom_bulk -1
set romp [get_pins -nowarn -compatibility_mode {*|u_ucrom|*|combout}]
foreach_in_collection pin $romp {
    if {$rom_tries >= 80 || $nrom_pos >= 1} { break }
    incr rom_tries
    set ps [get_timing_paths -from $v30u_ce -to $v30u_ce -through $pin \
                -setup -npaths 1 -detail full_path]
    if {[get_collection_size $ps] == 0} { continue }
    foreach_in_collection R $ps {
        array unset RK ; array set RK [walk $R]
        set a 0
        foreach e $RK(pts) {
            foreach {nm cum inc ty} $e break
            if {[string first "|u_ucrom|" $nm] >= 0} { incr a }
        }
        if {$a >= 1} { set nrom_pos $a ; set rom_pin [get_node_info $pin -name] }
    }
}
if {[get_collection_size $romp] > 0} {
    set RB ""
    foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce \
                                 -through $romp -setup -npaths 1 -detail full_path] { set RB $p }
    if {$RB ne ""} {
        array unset RQ ; array set RQ [walk $RB]
        set nrom_bulk 0
        foreach e $RQ(pts) {
            foreach {nm cum inc ty} $e break
            if {[string first "|u_ucrom|" $nm] >= 0} { incr nrom_bulk }
        }
    }
}
emit [format "  PC-5 ROMHEAD    |u_ucrom| combout pins: %d   (single-pin tries: %d)" \
          [get_collection_size $romp] $rom_tries]
emit [format "       ROM nodes on a path forced through ONE NAMED PIN : %d  (MUST be >= 1)" $nrom_pos]
emit "       the pin that answered : $rom_pin"
emit [format "       ...and the BULK -through of %d pins yields        : %d" \
          [get_collection_size $romp] $nrom_bulk]
if {$nrom_pos < 1} { set CTL_OK 0 ; emit "       *** PC-5 FAILED ***" } else { emit "       PC-5 PASS" }

emit ""
emit "  === CONTROLS: [expr {$CTL_OK ? {ALL PASS} : {*** FAILED -- NOTHING BELOW MAY BE QUOTED ***}}] ==="
if {!$CTL_OK} { close $fh ; project_close ; exit 4 }

# ==========================================================================
# §B  THE WORST `ce -> ce` ARC
# ==========================================================================
emit ""
emit "=== B. THE WORST ce->ce ARC ==="
emit "  from : $WK(from)"
emit "  to   : $WK(to)"
emit [format "  slack %+8.3f   logic levels %s   data delay %s   walked cells %d  combout %d" \
          [get_path_info $W -slack] [get_path_info $W -num_logic_levels] $dd \
          $WK(ncell) $WK(ncomb)]
set ap [open "${PFX}.arrivalpoints.txt" w]
foreach l $WK(dump) { puts $ap $l }
close $ap
emit "  arrival points -> ${PFX}.arrivalpoints.txt"

# ==========================================================================
# §C  THE PER-SEGMENT PROFILE ON THE WORST ARC
# ==========================================================================
array set SG [segment $WK(pts) $MARKERS]
set nseg [llength $SG(segs)]
emit ""
emit "=== C. THE PER-SEGMENT PROFILE (segments = chain positions' bodies) ==="
emit [format "  boundaries found: %d   segments: %d" [llength $SG(cuts)] $nseg]
emit "  seg |   from ns |     to ns |   span ns | cells | comb | first .. last combout base names"
set i 0
foreach s $SG(segs) {
    foreach {a b nc nb names} $s break
    emit [format "  %3d | %9.3f | %9.3f | %9.3f | %5d | %4d | %s .. %s" \
              $i [expr {$a - $WK(launch)}] [expr {$b - $WK(launch)}] \
              [expr {$b - $a}] $nc $nb [lindex $names 0] [lindex $names end]]
    incr i
}
emit ""
emit "=== C.2  SEGMENT CONTENTS (base names, in order) ==="
set i 0
foreach s $SG(segs) {
    foreach {a b nc nb names} $s break
    emit [format "  seg %d (%.3f ns): %s" $i [expr {$b - $a}] [join $names " "]]
    incr i
}

# ==========================================================================
# §D  THE BIU ROUND TRIP ON THE WORST ARC
# ==========================================================================
emit ""
emit "=== D. THE BIU ROUND TRIP (q_cnt -> q_ripe_lead_n), ON THE WORST ARC ==="
set nb_tot 0 ; set b_first -1.0 ; set b_last -1.0
foreach e $WK(pts) {
    foreach {nm cum inc ty} $e break
    if {[string first "|u_biu|" $nm] >= 0} {
        incr nb_tot
        if {$b_first < 0} { set b_first [expr {$cum - $inc}] }
        set b_last $cum
        emit [format "    %8.3f ns  %s" [expr {$cum - $WK(launch)}] $nm]
    }
}
emit "  BIU nodes on the worst ce->ce arc: $nb_tot"
if {$nb_tot == 0} { emit "    (none -- the binding arc is EU-internal on this draw)" } \
    else { emit [format "  SPAN: %.3f ns  (enters %.3f, leaves %.3f of a %.3f ns arc)" \
                    [expr {$b_last - $b_first}] [expr {$b_first - $WK(launch)}] \
                    [expr {$b_last - $WK(launch)}] $wd] }

# ==========================================================================
# §I  THE POPULATION.  Endpoint-diverse, machine-readable, censused by
#     sw/frontend_anat_report.py against the SOURCE-DERIVED stage map.
# ==========================================================================
emit ""
emit "=== I. THE POPULATION (endpoint-diverse, -nworst 1) ==="
set pop [open "${PFX}.population.txt" w]
puts $pop "# WAVE 8 population dump.  One block per path."
puts $pop "# P <idx> <slack> <data_delay> <levels> <nboundaries> <from> <to>"
puts $pop "# N <idx> <cum> <incr> <type> <name>"
set np_done 0
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                             -npaths $NP -nworst 1 -detail full_path] {
    array unset K ; array set K [walk $p]
    if {!$K(ok)} { continue }
    array unset S ; array set S [segment $K(pts) $MARKERS]
    set d [expr {$K(total) - $K(launch)}]
    puts $pop [format "P %d %s %.3f %s %d %s %s" $np_done [get_path_info $p -slack] \
                   $d [get_path_info $p -num_logic_levels] [llength $S(cuts)] \
                   $K(from) $K(to)]
    foreach e $K(pts) {
        foreach {nm cum inc ty} $e break
        puts $pop [format "N %d %.3f %.3f %s %s" $np_done \
                       [expr {$cum - $K(launch)}] $inc $ty $nm]
    }
    incr np_done
}
close $pop
emit "  paths dumped: $np_done  -> ${PFX}.population.txt"

close $fh
project_close
