# WAVE 8 -- NODE IDENTIFICATION.  MEASUREMENT ONLY; NOT A GATE, NO RECEIPT.
#
# `sw/frontend_anat_report.py` §8 attributes an ANONYMOUS Quartus cone
# (`Add57`, `Mux358`, `always6`) to its nearest NAMED neighbours on a path.
# That is an ATTRIBUTION and it says so.  This is the IDENTIFICATION: it asks
# the netlist itself for the cone's FANIN and FANOUT, so `Add57` stops being
# "the thing between `v1` and `stop`" and becomes a named set of RTL signals.
#
# args: {project revision OUTPREFIX pattern ?pattern ...?}
#   each pattern is a leaf base name; every `*|u_eu|<name>~*|combout` pin is
#   collected and its immediate fanin / fanout leaf names are censused.
#
# ⚠ THE POSITIVE CONTROL IS PC-N1 AND IT IS REPORTED FIRST: a name that DOES
# exist must return a non-empty collection with non-empty fanin, and the
# invented name `zzz_no_such_node` must return ZERO.  Without the negative leg
# an empty census reads exactly like "this cone has no inputs".
# ⚠ `get_fanins` on a PIN wants `-through`-free plain collections; the names
# are normalised the same way the anatomy normalises them (`string first`, never
# `string match` -- a bus index is a character class, WAVE 1 §3.0).
project_open [lindex $quartus(args) 0] -revision [lindex $quartus(args) 1]
set PFX [lindex $quartus(args) 2]
set PATS [lrange $quartus(args) 3 end]
create_timing_netlist -model slow
read_sdc
update_timing_netlist

set fh [open "${PFX}.nodeid.txt" w]
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

proc census {pat} {
    # every LUT of this cone, its fanin leaf names and its fanout leaf names
    array set FI {} ; array set FO {}
    set n 0
    # ⚠ PC-N1 CAUGHT THIS FORM BEING WRONG AND REFUSED RATHER THAN REPORTING
    # "no fanin": the first version asked only for `*|u_eu|<name>~*|combout`,
    # which cannot reach a node one level deeper -- and `ucrom`'s LUTs live at
    # `...|u_eu|u_ucrom|ucrom~157|combout`.  It read 0 LUTs for a name with 613
    # of them.  Both depths are asked for now, and the control is what said so.
    # ⚠ AND A SECOND DEFECT THE SAME CONTROL FOUND: a CARRY CHAIN's output pin
    # is `cout` / `sumout`, not `combout`.  `Add57` read 0 LUTs for a cone the
    # arrival points show eight cells of.  All three output-pin kinds are asked
    # for.
    set forms {}
    foreach pin {combout cout sumout} {
        lappend forms "*|u_eu|${pat}~*|$pin" "*|u_eu|${pat}\[*\]~*|$pin" \
                      "*|u_eu|*|${pat}~*|$pin" "*|u_eu|*|${pat}\[*\]~*|$pin"
    }
    foreach form $forms {
        foreach_in_collection p [get_pins -nowarn -compatibility_mode $form] {
            incr n
            set nm [get_node_info $p -name]
            foreach_in_collection f [get_fanins -no_logic $nm] {
                set b [basename2 [get_node_info $f -name]]
                if {![info exists FI($b)]} { set FI($b) 0 }
                incr FI($b)
            }
            foreach_in_collection f [get_fanouts -no_logic $nm] {
                set b [basename2 [get_node_info $f -name]]
                if {![info exists FO($b)]} { set FO($b) 0 }
                incr FO($b)
            }
        }
    }
    return [list n $n fi [array get FI] fo [array get FO]]
}

proc top {arr k} {
    array set A $arr
    set l {}
    foreach {a b} [array get A] { lappend l [list $b $a] }
    set l [lsort -integer -index 0 -decreasing $l]
    set o {}
    foreach e [lrange $l 0 [expr {$k-1}]] {
        lappend o "[lindex $e 1]([lindex $e 0])"
    }
    return [join $o " "]
}

emit "=== sta_node_id (WAVE 8) ==="
emit "  revision [lindex $quartus(args) 1]"
emit ""
emit "=== PC-N1  THE POSITIVE CONTROL, REPORTED FIRST ==="
set CTL 1
array set C0 [census [lindex $PATS 0]]
array set CZ [census zzz_no_such_node]
emit [format "  a name that DOES exist  (%s) : %d LUTs, %d distinct fanin names   (MUST be >= 1 and >= 1)" \
          [lindex $PATS 0] $C0(n) [expr {[llength $C0(fi)]/2}]]
emit [format "  the invented name       (zzz_no_such_node) : %d LUTs   (MUST be 0)" $CZ(n)]
if {$C0(n) < 1 || [llength $C0(fi)] < 2 || $CZ(n) != 0} {
    set CTL 0 ; emit "  *** PC-N1 FAILED -- NOTHING BELOW MAY BE QUOTED ***"
} else { emit "  PC-N1 PASS" }
emit ""
if {!$CTL} { close $fh ; project_close ; exit 4 }

emit "=== THE CENSUS ==="
foreach pat $PATS {
    array unset C ; array set C [census $pat]
    emit ""
    emit [format "--- %s : %d LUTs in v30u_eu" $pat $C(n)]
    emit "    FANIN  (what it reads) : [top $C(fi) 14]"
    emit "    FANOUT (what reads it) : [top $C(fo) 14]"
}
close $fh
project_close
