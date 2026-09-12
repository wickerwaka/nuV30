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
#   PC-W3  THE KNOWN-WRONG FORMS, printed beside PC-W2: the `v30u_biu:` TYPE
#          prefix (WAVE 4 sec.6.1 item 1) and an instance name that does not
#          exist, both required to read 0 IN THE DATA SECTION.
#          ⚠ THE TYPE-PREFIX CLAUSE IS A DATA-SECTION CLAUSE AND ALWAYS WAS, and
#          WAVE 10's first form gated on ALL POINTS and therefore FAILED on its
#          own ceiling-probe arm -- which ADDS A BIU REGISTER, and a REGISTER's
#          name DOES carry the type prefix.  The all-points count is now
#          REPORTED beside the gated one, where a nonzero reading is a free
#          positive control that the arm reached the compiler.
#   PC-W4  THE BULK `-through`, printed and never relied on.  A bulk figure
#          BELOW the single-pin figure is `-through` accepted-and-ignored.
#   PC-W5  THE DESTINATION PIN FORM, ENUMERATED FROM THE NETLIST.  WAVE 9's own
#          diagnostic control failed because `upc_page[0]` is a
#          SYNCHRONOUS-LOAD register written through `|asdata`, not `|d`; WAVE
#          10's first form of THIS control failed one step further out, on an
#          M10K PORT REGISTER whose input pin is neither.  The pin list is
#          therefore ASKED OF THE NETLIST and tried ONE AT A TIME, and `|d`,
#          `|asdata` and `|datain` are printed beside it as NAMED KNOWN-ABSENT
#          controls.
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
    set n9_all 0 ; set n9_dat 0 ; set n8_dat 0 ; set nkw 0 ; set nkwa 0 ; set nabs 0 ; set nrip 0
    set f_tot -1.0 ; set f_pre -1.0 ; set l_tot -1.0
    set fd_tot -1.0 ; set fd_pre -1.0 ; set ld_tot -1.0
    foreach e $pts {
        foreach {nm cum inc ty sec} $e break
        # ⚠ THE TYPE-PREFIX CONTROL IS A DATA-SECTION CONTROL AND ALWAYS WAS.
        # Quartus prints `v30u_biu:` on REGISTER names and omits it on
        # COMBINATIONAL ones (WAVE 4 sec.6.1 item 1), so a nonzero reading in the
        # DATA SECTION means the raw `|u_biu|` match is picking up registers.
        # At an ENDPOINT it means something else entirely -- the path launches
        # from or lands in a BIU register -- which is IMPOSSIBLE on the shipped
        # design and is EXACTLY WHAT THE CEILING PROBE ARM CREATES.  Counted
        # separately; the data-section count gates, the all-points count is
        # REPORTED and is a free positive control that the arm reached the
        # compiler.
        if {[pkw  $nm]} { incr nkwa ; if {$sec} { incr nkw } }
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
    return [list $n9_all $n9_dat $n8_dat $nkw $nabs $nrip $s9 $s8 $nkwa]
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
set biu_pos -1 ; set biu_kw -1 ; set biu_kwa -1 ; set biu_abs -1 ; set biu_pin "" ; set tries 0
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
                set biu_kwa [lindex $c 8]
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
emit [format "  PC-W3 WRONG FORMS  ...the `v30u_biu:` TYPE prefix IN THE DATA SECTION : %d  (MUST be 0)" $biu_kw]
emit [format "                     ...the same form over ALL points of that path  : %d  (REPORTED: > 0 means the path ENDS AT or LAUNCHES FROM a BIU register, which the shipped design has not got and the CEILING PROBE ARM has by construction)" $biu_kwa]
emit [format "                     ...an instance that does not exist        : %d  (MUST be 0)" $biu_abs]
emit [format "        (AX-1 live: WAVE 8's normalising predicate on the same path: %d)" $biu_p8]
emit [format "  PC-W4 BULK       the BULK -through of %d pins yields : %d BIU nodes" \
          [get_collection_size $biup] $biu_bulk]
emit "        (a BULK figure BELOW the single-pin figure is `-through` being"
emit "         ACCEPTED AND IGNORED -- printed, never relied on)"
if {$biu_pos < 1 || $biu_kw != 0 || $biu_abs != 0} {
    set CTL_OK 0 ; emit "        *** PC-W2/W3 FAILED ***" } else { emit "        PC-W2/W3 PASS" }

# --- PC-W5  THE DESTINATION SIDE.  TWO CLAUSES, AND THE SECOND ONE IS K-1's.
#
# ⚠⚠ THIS CONTROL HAS NOW FAILED TWICE AND BOTH FAILURES ARE THE INSTRUMENT.
#   (i)  WAVE 9 sec.5.1: its diagnostic forced through `|d` and `upc_page[0]` is
#        a SYNCHRONOUS-LOAD register written through `|asdata`.
#   (ii) WAVE 10's first form tried `|d`, `|asdata` AND `|datain`; the UNCUT
#        tree's binding path ends at an M10K PORT REGISTER
#        (`ram_block1a6~porta_address_reg7`) whose input pin is none of the
#        three.  Its SECOND form asked the netlist for `<dest>|*` instead of
#        guessing -- **and that returned 0 PINS, because an M10K port register
#        EXPOSES NO PIN OBJECTS AT ALL.**  Printed below, because it is the
#        reason a pin-based destination control cannot be the whole of this one.
#
# So the control is split into the two things it was actually for:
#   W5a  THE CENSUS'S OWN REQUIREMENT -- a path can be forced to ONE NAMED
#        DESTINATION REGISTER.  `get_registers`, not `get_pins`, so it holds for
#        every register kind including an M10K port register.
#   W5b  K-1's REQUIREMENT -- BOTH WRITE-PIN FORMS ARE HANDLED.  The netlist is
#        searched for a `v30u_eu` register carrying a `|d` pin and one carrying
#        an `|asdata` pin, a path is forced through ONE NAMED PIN of each, and
#        BOTH are reported.  `upc_page` is named explicitly, because it is the
#        register WAVE 9's control died on.
set dreg [get_node_info [get_path_info $W -to] -name]
set desc $dreg
regsub -all {\[} $desc {\\[} desc
regsub -all {\]} $desc {\\]} desc
emit "  PC-W5 DESTINATION : $dreg"
foreach {tag pat} [list d "${desc}|d" asdata "${desc}|asdata" datain "${desc}|datain" \
                        any "${desc}|*"] {
    emit [format "        pins named `%-8s` on THAT register : %d" $tag \
              [get_collection_size [get_pins -nowarn -compatibility_mode $pat]]]
}
emit "        (all four reading 0 is an M10K PORT REGISTER, which exposes no pin"
emit "         objects -- the finding that voided this control's first two forms)"
# ⚠ W5a MUST NOT DEPEND ON RESOLVING A NAME.  Its first form did, and it FAILED
# on `...|u_eu|eff_op[2]~2_OTERM2473` -- a physical-synthesis DUPLICATE whose
# name carries `~` and `_OTERM` and which `get_registers` would not match even
# with the brackets escaped.  A control that can only address the registers
# whose names it can spell is a control that will fail on the next name shape.
# Three forms are tried IN ORDER and the one that answered is NAMED; the NODE
# OBJECT, which needs no name at all, is last and cannot miss.
set w5a 0 ; set w5a_how ""
foreach {how col} [list get_registers [get_registers -nowarn $desc] \
                        get_keepers   [get_keepers   -nowarn $desc] \
                        node_object   [get_path_info $W -to]] {
    if {$w5a >= 1} { break }
    if {[catch {set sz [get_collection_size $col]}]} { set sz "n/a(node)" }
    if {[catch {set k [get_collection_size [get_timing_paths -from $v30u_ce \
                           -to $col -setup -npaths 1]]}]} { set k 0 }
    emit [format "  PC-W5a  -to via %-13s collection %-9s -> paths %d" $how $sz $k]
    if {$k >= 1} { set w5a $k ; set w5a_how $how }
}
emit [format "  PC-W5a  a path forced TO that ONE DESTINATION : %d  via %s  (MUST be >= 1)" \
          $w5a $w5a_how]

set w5b_d 0 ; set w5b_as 0 ; set w5b_dpin "" ; set w5b_aspin ""
foreach {tag pats} [list d   {{*|u_eu|upc_page*|d} {*|u_eu|*|d}} \
                         as  {{*|u_eu|upc_page*|asdata} {*|u_eu|*|asdata}}] {
    set got 0 ; set gotpin "" ; set tries 0
    foreach pat $pats {
        if {$got} { break }
        foreach_in_collection pin [get_pins -nowarn -compatibility_mode $pat] {
            if {$tries >= 40 || $got} { break }
            incr tries
            set k [get_collection_size [get_timing_paths -from $v30u_ce -to $v30u_ce \
                                            -through $pin -setup -npaths 1]]
            if {$k >= 1} { set got 1 ; set gotpin [get_node_info $pin -name] }
        }
    }
    emit [format "  PC-W5b  `|%s` write-pin form : %s   %s" \
              [expr {$tag eq "d" ? "d" : "asdata"}] \
              [expr {$got ? {ANSWERED} : {*** NO PATH ***}}] $gotpin]
    if {$tag eq "d"} { set w5b_d $got } else { set w5b_as $got }
}
if {$w5a < 1 || !$w5b_d || !$w5b_as} {
    set CTL_OK 0 ; emit "        *** PC-W5 FAILED ***" } else { emit "        PC-W5 PASS" }

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
    set n 0 ; set c9 0 ; set c9d 0 ; set c8 0 ; set crip 0 ; set ckw 0 ; set ckwa 0 ; set cabs 0
    set s9sum 0.0 ; set s8sum 0.0 ; set s9max 0.0
    set pairs [list]
    foreach_in_collection p $paths {
        array unset K ; array set K [walk $p]
        if {!$K(ok)} { continue }
        incr n
        set c [census1 $K(pts)]
        foreach {n9a n9d n8d nkw nabs nrip s9 s8 nkwa} $c break
        if {$n9a > 0} { incr c9 ; set s9sum [expr {$s9sum + $s9}]
                        if {$s9 > $s9max} { set s9max $s9 } }
        if {$n9d > 0} { incr c9d ; set s8sum [expr {$s8sum + $s8}] }
        if {$n8d > 0} { incr c8 }
        if {$nrip > 0} { incr crip }
        if {$nkw  > 0} { incr ckw }
        if {$nkwa > 0} { incr ckwa }
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
    emit [format "    ...KNOWN-WRONG type prefix IN THE DATA SECTION: %d   (MUST be 0)" $ckw]
    emit [format "    ...the same form at ANY point (endpoints too) : %d   (REPORTED, not gated -- a BIU REGISTER ENDPOINT, which only an arm that adds one can have)" $ckwa]
    emit [format "    ...matching an instance that does not exist  : %d   (MUST be 0)" $cabs]
    if {$c9 > 0} {
        emit [format "    mean span, WAVE 9 convention (ns)            : %.3f" [expr {$s9sum / $c9}]]
        emit [format "    max  span, WAVE 9 convention (ns)            : %.3f" $s9max]
    }
    if {$c9d > 0} {
        emit [format "    mean span, WAVE 8 convention (ns)            : %.3f" [expr {$s8sum / $c9d}]]
    }
    return [list $n $c9 $c9d $c8 $ckw $cabs $ckwa]
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
    foreach {n c9 c9d c8 ckw cabs ckwa} $R break
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
