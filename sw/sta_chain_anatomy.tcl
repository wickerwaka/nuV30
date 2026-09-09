# WAVE 5 -- THE CHAIN ANATOMY.  MEASUREMENT ONLY; IT IS NOT A GATE AND WRITES
# NO RECEIPT.  No Fmax may be quoted from it.
#
# WAVE 4 measured that the EU's UNROLLED CHAIN ALONE is 37.224 ns / 40 levels,
# BIU-free, against a 31.25 ns budget -- so the chain is the whole problem and
# nobody has measured INSIDE it.  This script answers Q1 (the per-position
# profile), Q2 (the cumulative profile over every position boundary), Q3 (what
# dominates inside a position), Q4 (shared vs independent copies), Q5 (the
# floor) and Q6 (where the BIU round trip enters).
#
# args: {project revision OUTPREFIX ?npaths?}
#
# ============================ THE SEGMENTER ================================
# The chain is `for (chain = 0; chain < CHAIN_MAX; ...)` around
# `v30u_eu_step.svh`.  Its LOOP-CARRIED STATE is `st_n` and `stop`, and every
# position >= 1 is ENTERED through `st_zero_ok(st_n)`:
#     if ((chain != 4'd0) && !st_zero_ok(st_n)) stop = 1'b1; else <the step>
# `st_zero_ok` SURVIVES SYNTHESIS AS A NAMED NODE -- measured on this design
# before this script was written (`sw/testdata/cutset/diag_ctl_seed3.arrival
# points.txt` carries `st_zero_ok~14` and `st_zero_ok~16`).  So a maximal
# consecutive RUN of arrival points whose base name is `st_n`, `stop` or
# `st_zero_ok` is ONE POSITION BOUNDARY, and the segments between the runs are
# the positions' bodies.
#
# ⚠ WHAT THIS IS AND IS NOT.  It is a topological segmentation of ONE PATH; the
# order along a path IS the position order, because the only way from one `st_n`
# value to a later one is through a position's body.  It is NOT a claim that
# boundary i is chain position i: Quartus may fold a position whose body this
# path does not enter, and a single position may assign `st_n` more than once
# (`S_MODRM` does).  So the count is a LOWER BOUND on positions crossed, it is
# reported as SEGMENTS and not as positions, and CHAIN_MAX = 7 bounds it.
#
# ⚠ `get_timing_paths -through` SILENTLY IGNORES a `get_nodes` collection
#   (WAVE 1 §0.2) -- `get_pins` is the resolver, and PC-1 re-demonstrates it
#   live rather than citing it.
# ⚠ `string match` on a name carrying a bus index FAILS (`[3]` is a character
#   class, WAVE 1 §3.0).  Every prefix test here is `string first ... == 0`.
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
# leaf name with the Quartus `~N` suffix AND any bus index removed:
#   `...|u_eu|opc_base[4]~11|combout` -> `opc_base`
#   `...|u_eu|st_zero_ok~14|combout`  -> `st_zero_ok`
# ⚠ THE LAST SEGMENT IS ONLY DROPPED WHEN IT IS A PIN.  WAVE 1's `basenet`
# dropped it unconditionally, which is right for an arrival point
# (`...|st_n~44|combout`) and WRONG for a register name
# (`...|u_eu|opc_base[3]~DUPLICATE`), where it returns the INSTANCE `u_eu` and
# the signal disappears.  Measured on the smoke run: §F's rows read
# `auto_generated -> u_eu`.
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

emit "=== sta_chain_anatomy (WAVE 5) ==="
emit "  revision [lindex $quartus(args) 1]   npaths $NP"

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
# Splits a path's arrival points into CLK / LAUNCH / DATA / DEST by name match
# against the path's OWN -from and -to.  Returns every DATA point (not only
# cells) with its cumulative arrival, because the segmenter needs the ORDER.
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
# `markers` is the marker BASE-NAME list.  Returns a list of segments, each
# {startcum endcum ncell ncomb names}, plus the boundary cut times.
proc segment {pts markers} {
    set segs {} ; set cuts {} ; set names {}
    set start -1.0 ; set nc 0 ; set nb 0 ; set inmark 0
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
                # the marker run just ended -- close a segment at its end
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
# §A  THE POSITIVE CONTROLS.  RUN FIRST.  THEY GATE EVERYTHING BELOW.
# ==========================================================================
emit ""
emit "=== A. POSITIVE CONTROLS (reported FIRST; a miss voids the wave) ==="
set CTL_OK 1

# --- the worst ce->ce path, needed by PC-1 and PC-2
set W ""
foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                             -npaths 1 -detail full_path] { set W $p }
if {$W eq ""} { emit "  PC: NO ce->ce PATH -- REFUSING" ; close $fh ; project_close ; exit 3 }
set wk [walk $W]
array set WK $wk

# PC-1 THE RESOLVER.  `-through` must return a path for a get_pins collection
# and ZERO for the get_nodes collection of the SAME node.  This is WAVE 1 §0.2
# re-demonstrated live on this netlist rather than cited.
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

# PC-2 THE WALKER.  On a path whose endpoints Quartus itself names, the walker
# must reach the DEST phase (state 3) and find >= 3 data cells; and its own
# (total - launch) must reproduce Quartus's `-data_delay` to 0.01 ns.
set dd [get_path_info $W -data_delay]
set wd [expr {$WK(total) - $WK(launch)}]
emit [format "  PC-2 WALKER     state %d (MUST be 3)   data cells %d (MUST be >= 3)" \
          $WK(state) $WK(ncell)]
emit [format "                  walker data delay %.3f  vs Quartus -data_delay %s   diff %.3f (MUST be <= 0.01)" \
          $wd $dd [expr {abs($wd - $dd)}]]
if {$WK(state) != 3 || $WK(ncell) < 3 || abs($wd - $dd) > 0.01} {
    set CTL_OK 0 ; emit "       *** PC-2 FAILED ***" } else { emit "       PC-2 PASS" }

# PC-3 THE SEGMENTER.  Take a path FORCED through an `st_zero_ok` pin -- a case
# known to be YES BY CONSTRUCTION -- and require the segmenter to report >= 1
# boundary on it.  The NEGATIVE control is the SAME path segmented on a marker
# name that does not exist: it must report 0.
# ⚠ `get_pins` WITHOUT `-compatibility_mode` DOES NOT LET `*` CROSS A `|`
# HIERARCHY SEPARATOR, so `*|u_eu|st_zero_ok~*|*` resolves to ZERO on a name
# with six segments -- MEASURED on this design (0 plain, 72 in compatibility
# mode) before this line was written.  A zero collection here would have made
# PC-3 unrunnable and looked like "the marker is not in the netlist".
set zok [get_pins -nowarn -compatibility_mode {*|u_eu|st_zero_ok~*|combout}]
emit [format "  PC-3 SEGMENTER  st_zero_ok pins in the netlist: %d" [get_collection_size $zok]]
set nb_pos -1 ; set nb_neg -1
if {[get_collection_size $zok] > 0} {
    set Z ""
    foreach_in_collection p [get_timing_paths -from $v30u_ce -to $v30u_ce \
                                 -through $zok -setup -npaths 1 -detail full_path] { set Z $p }
    if {$Z ne ""} {
        array set ZK [walk $Z]
        array set S1 [segment $ZK(pts) {st_n stop st_zero_ok}]
        array set S0 [segment $ZK(pts) {st_zero_ok_XYZZY_NO_SUCH_NET}]
        set nb_pos [llength $S1(cuts)] ; set nb_neg [llength $S0(cuts)]
        emit "       forced path: [get_node_info [get_path_info $Z -from] -name]"
        emit "                 -> [get_node_info [get_path_info $Z -to] -name]"
    }
}
emit [format "       boundaries on the FORCED path, real markers : %d  (MUST be >= 1)" $nb_pos]
emit [format "       boundaries on the SAME path, a fake marker  : %d  (MUST be 0)" $nb_neg]
if {$nb_pos < 1 || $nb_neg != 0} { set CTL_OK 0 ; emit "       *** PC-3 FAILED ***" } \
    else { emit "       PC-3 PASS" }

# PC-4 THE BIU MATCHER.  `|u_biu|` is the INSTANCE name; `v30u_biu:` is the TYPE
# prefix Quartus prints on REGISTERS ONLY and omits on combinational nodes, so a
# type-prefix test finds no BIU LUT at all (WAVE 4 §6.1 item 1 -- it reported 0
# on a path carrying eight).  The control forces a path through a BIU pin and
# requires the counter to say YES.
#
# ⚠⚠ AND THE FIRST FORM OF THIS CONTROL WAS ITSELF VACUOUS, WHICH IS WHY IT IS
# WRITTEN THIS WAY.  It passed a `get_pins` collection of **1,176** BIU pins to
# `-through` and got back a path with **ZERO** BIU nodes on it -- i.e. the
# `-through` was ACCEPTED AND IGNORED and the collection simply returned the
# unconstrained worst `ce -> ce` path.  On the development netlist that read
# "8 BIU nodes" and PASSED, because THAT netlist's worst arc happened to carry
# the round trip: the control agreed for the wrong reason.  MEASURED on this
# tree, 2026-09-09.  **A `-through` is therefore given ONE PIN AT A TIME**, and
# the pin that answered is NAMED in the output so the YES is never anonymous.
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
# ...and the BULK form, kept and PRINTED as the known-wrong control, so the
# vacuity that was found here cannot come back silently.
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
# §C / §D  Q1 THE PER-SEGMENT PROFILE, Q2 THE CUMULATIVE PROFILE
# ==========================================================================
array set SG [segment $WK(pts) {st_n stop st_zero_ok}]
set nseg [llength $SG(segs)]
emit ""
emit "=== C. Q1 -- THE PER-SEGMENT PROFILE (segments = chain positions' bodies) ==="
emit [format "  boundaries found: %d   segments: %d   (CHAIN_MAX = 7 bounds it)" \
          [llength $SG(cuts)] $nseg]
emit "  seg |   from ns |     to ns |   span ns | cells | comb | first .. last combout base names"
set i 0
foreach s $SG(segs) {
    foreach {a b nc nb names} $s break
    set f [lindex $names 0] ; set l [lindex $names end]
    emit [format "  %3d | %9.3f | %9.3f | %9.3f | %5d | %4d | %s .. %s" \
              $i [expr {$a - $WK(launch)}] [expr {$b - $WK(launch)}] \
              [expr {$b - $a}] $nc $nb $f $l]
    incr i
}
emit ""
emit "=== D. Q2 -- THE CUMULATIVE PROFILE OVER EVERY BOUNDARY ==="
emit "  (upstream = launch pin -> the boundary; downstream = the boundary -> destination)"
emit "  ⚠ THESE ARE UNCUT-NETLIST ESTIMATES.  WAVE 1 §6 item 1: after a real cut"
emit "     both halves are re-synthesised and the numbers move."
emit "   k |  upstream ns | downstream ns | worse half | both <= 29.6 ?"
set k 0
foreach c $SG(cuts) {
    set up [expr {$c - $WK(launch)}]
    set dn [expr {$WK(total) - $c}]
    set w [expr {$up > $dn ? $up : $dn}]
    emit [format "  %2d | %12.3f | %13.3f | %10.3f | %s" $k $up $dn $w \
              [expr {$w <= 29.6 ? {YES} : {no}}]]
    incr k
}

# ==========================================================================
# §E  Q3/Q4 -- THE SEGMENTS' NODE NAMES, AND WHETHER THE COPIES SHARE
# ==========================================================================
emit ""
emit "=== E. Q3/Q4 -- SEGMENT CONTENTS (base names, in order) ==="
set i 0
foreach s $SG(segs) {
    foreach {a b nc nb names} $s break
    emit [format "  seg %d (%.3f ns): %s" $i [expr {$b - $a}] [join $names " "]]
    incr i
}
# Q4: do two segments carry the SAME base names at DIFFERENT node instances?
emit ""
emit "  --- Q4: base-name overlap between segments (same name, different ~N = INDEPENDENT COPIES) ---"
set i 0
foreach s $SG(segs) {
    foreach {a b nc nb names} $s break
    set L($i) $names ; incr i
}
for {set x 0} {$x < $nseg} {incr x} {
    for {set y [expr {$x+1}]} {$y < $nseg} {incr y} {
        set common {}
        foreach n $L($x) { if {[lsearch -exact $L($y) $n] >= 0 &&
                               [lsearch -exact $common $n] < 0} { lappend common $n } }
        if {[llength $common] > 0} {
            emit "    seg $x ∩ seg $y : [join $common { }]"
        }
    }
}

# ==========================================================================
# §F  Q5 -- THE FLOOR, and the top-N segment-count census
# ==========================================================================
emit ""
emit "=== F. Q5 -- THE FLOOR (worst ce->ce arc by number of chain boundaries) ==="
# TWO SCANS, because they answer different questions and the first alone is
# degenerate: the top-N BY SLACK are near-copies of one arc (measured: 200 of
# 200 crossed exactly 3 boundaries), so `-nworst 1` -- ONE path per endpoint
# pair -- is what spreads the population over the design and lets a 0- or
# 1-boundary arc appear at all.
foreach SCAN {SLACK ENDPOINT} {
array unset BEST ; array unset BESTROW ; array unset HIST
array set BEST {}
array set BESTROW {}
array set HIST {}
set nscan 0
if {$SCAN eq "SLACK"} {
    set PATHS [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                   -npaths $NP -detail full_path]
} else {
    set PATHS [get_timing_paths -from $v30u_ce -to $v30u_ce -setup \
                   -npaths $NP -nworst 1 -detail full_path]
}
foreach_in_collection p $PATHS {
    incr nscan
    array set K [walk $p]
    if {!$K(ok)} { continue }
    array set S [segment $K(pts) {st_n stop st_zero_ok}]
    set nb [llength $S(cuts)]
    set d [expr {$K(total) - $K(launch)}]
    if {![info exists HIST($nb)]} { set HIST($nb) 0 }
    incr HIST($nb)
    if {![info exists BEST($nb)] || $d > $BEST($nb)} {
        set BEST($nb) $d
        set BESTROW($nb) [format "%9.3f ns  levels %-3s  %s -> %s" $d \
                              [get_path_info $p -num_logic_levels] \
                              [basename2 $K(from)] [basename2 $K(to)]]
    }
    array unset S ; array unset K
}
emit ""
emit "  --- scan $SCAN: scanned $nscan paths ---"
emit "  boundaries | n paths | worst DATA delay among paths with that many boundaries"
foreach nb [lsort -integer [array names BEST]] {
    emit [format "  %10d | %6d | %s" $nb $HIST($nb) $BESTROW($nb)]
}
}
# THE ARITHMETIC FLOOR, on the worst arc itself: subtract every segment and
# every boundary run that is NOT the first segment or the last.  This is the
# `if positions 1..N-1 were free` reading and it is an APPROXIMATION -- after a
# real change both halves are re-synthesised (WAVE 1 §6 item 1).
set s0 [lindex $SG(segs) 0] ; set sN [lindex $SG(segs) end]
set span0 [expr {[lindex $s0 1] - [lindex $s0 0]}]
set spanN [expr {[lindex $sN 1] - [lindex $sN 0]}]
emit ""
emit [format "  ARITHMETIC FLOOR on THIS arc: seg 0 (%.3f) + seg %d (%.3f) = %.3f ns" \
          $span0 [expr {$nseg-1}] $spanN [expr {$span0 + $spanN}]]
emit [format "     (against the whole arc's %.3f ns; the %d intermediate segments and" \
          [expr {$WK(total) - $WK(launch)}] [expr {$nseg-2}]]
emit  "      every boundary run are what it removes.  APPROXIMATION, labelled.)"
emit ""
emit "  ⚠ APPROXIMATION, LABELLED AS ONE.  The 0- and 1-boundary rows are the"
emit "     closest thing this netlist has to 'the arc with the folded positions"
emit "     removed'.  They are paths that HAPPEN not to cross more boundaries,"
emit "     not the same design with positions 1-6 deleted."

# ==========================================================================
# §G  Q6 -- THE BIU ROUND TRIP, PLACED IN THE SEGMENTATION
# ==========================================================================
emit ""
emit "=== G. Q6 -- THE BIU ROUND TRIP ==="
set i 0 ; set nb_tot 0
foreach s $SG(segs) {
    foreach {a b nc nb names} $s break
    set SEGA($i) $a ; set SEGB($i) $b ; incr i
}
set biurows {}
foreach e $WK(pts) {
    foreach {nm cum inc ty} $e break
    if {[string first "|u_biu|" $nm] >= 0} {
        incr nb_tot
        set seg -1
        for {set x 0} {$x < $nseg} {incr x} {
            if {$cum > $SEGA($x) && $cum <= $SEGB($x)} { set seg $x ; break }
        }
        lappend biurows [format "    seg %-3d  %8.3f ns  %s" $seg [expr {$cum - $WK(launch)}] $nm]
    }
}
emit "  BIU nodes on the worst ce->ce arc: $nb_tot"
foreach r $biurows { emit $r }
if {$nb_tot == 0} { emit "    (none -- the binding arc is EU-internal on this draw)" }

# ==========================================================================
# §H  Q4 -- THE COPY CENSUS.  Chain-carried signals should have MANY netlist
# cones; a signal only a position-0-only arm writes should have FEW.
# ==========================================================================
emit ""
emit "=== H. Q4 -- THE COPY CENSUS (distinct combout nodes per RTL base name) ==="
emit "  signal              | class            | combout nodes in v30u_eu"
foreach pair {
    {st_n CHAINABLE} {stop CHAINABLE} {st_zero_ok CHAINABLE} {ld_b_n CHAINABLE}
    {pv CHAINABLE} {opc_base CHAINABLE} {m_kind CHAINABLE} {seg_override_n CHAINABLE}
    {rst_ctr_n POS0-ONLY} {ld_dlo_n POS0-ONLY} {nmi_latch_n POS0-ONLY}
    {rloop_n_n POS0-ONLY} {ld_ripe_prev_n POS0-ONLY}
    {sigma FRONT-END} {s1_val FRONT-END} {it_val FRONT-END}
    {zzz_no_such_signal NEGATIVE-CONTROL}
} {
    set nmx [lindex $pair 0] ; set cls [lindex $pair 1]
    set c [get_collection_size [get_nodes -nowarn "*|u_eu|${nmx}~*|combout"]]
    set c2 [get_collection_size [get_nodes -nowarn "*|u_eu|${nmx}\[*\]~*|combout"]]
    emit [format "  %-19s | %-16s | %d  (+%d indexed)" $nmx $cls $c $c2]
}

close $fh
project_close
