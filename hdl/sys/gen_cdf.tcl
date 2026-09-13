
# Build CDF file
# Sorgelig - 17/2/2018
#
# ⚠ THIS FILE WAS `sys/build_id.tcl` UNTIL WAVE 12 (2026-09-12), AND IT DID TWO
# UNRELATED THINGS.  `generateBuildID_Verilog` wrote `hdl/build_id.v`, a
# `%y%m%d` date stamp that `nec_test.sv` `include`d into the last element of
# `CONF_STR`.  It was `.gitignore`d, untracked, and a DECLARED EXCLUSION from
# `quartus_gate`'s `input_manifest` -- and WAVE 11 measured what that cost: on a
# BYTE-IDENTICAL tree at ONE fitter seed, two ASCII characters of the stamp moved
# `$v30u_ce` 2,154 -> 1,918 and T_min 34.220 -> 35.867 ns.  1.647 ns / 1.34 MHz,
# against 0.603 ns for WAVE 7's FIVE FITTER SEEDS.  The stamp was the larger
# dimension of the two and nothing labelled it; two waves were differenced across
# it and no gate objected.
#
# USER INSTRUCTION 2026-09-12: *"Change the project so build_id.v isn't generated
# and isn't used."*  The generator is DELETED and the file renamed for what it
# still does.  `generateCDF` is UNTOUCHED, byte for byte: it writes `jtag.cdf`,
# which `sys/sys.tcl` names as `CDF_FILE`, and it has nothing to do with the
# stamp.
#
# ⚠ `hdl/sys/` IS VENDORED MiSTer FRAMEWORK CODE.  A future `sys/` update will
# restore `sys/build_id.tcl` and re-point `PRE_FLOW_SCRIPT_FILE` at it, and the
# stamp will be back with no edit anyone made.  `sw/quartus_gate.py`'s bar
# **E11** is what refuses that build; `python3 sw/test_quartus_gate.py` is E11's
# own falsifier.
proc generateCDF {revision device outpath} {

	set outputFileName "jtag.cdf"
	set outputFile [open $outputFileName "w"]

	puts $outputFile "JedecChain;"
	puts $outputFile "	FileRevision(JESD32A);"
	puts $outputFile "	DefaultMfr(6E);"
	puts $outputFile ""
	puts $outputFile "	P ActionCode(Ign)"
	puts $outputFile "		Device PartName(SOCVHPS) MfrSpec(OpMask(0));"
	puts $outputFile "	P ActionCode(Cfg)"
	puts $outputFile "		Device PartName($device) Path(\"$outpath/\") File(\"$revision.sof\") MfrSpec(OpMask(1));"
	puts $outputFile "ChainEnd;"
	puts $outputFile ""
	puts $outputFile "AlteraBegin;"
	puts $outputFile "	ChainType(JTAG);"
	puts $outputFile "AlteraEnd;"
}

set project_name [lindex $quartus(args) 1]
set revision [lindex $quartus(args) 2]

if {[project_exists $project_name]} {
    if {[string equal "" $revision]} {
        project_open $project_name -revision [get_current_revision $project_name]
    } else {
        project_open $project_name -revision $revision
    }
} else {
    post_message -type error "Project $project_name does not exist"
    exit
}

set device  [get_global_assignment -name DEVICE]
set outpath [get_global_assignment -name PROJECT_OUTPUT_DIRECTORY]

if [is_project_open] {
    project_close
}

generateCDF $revision $device $outpath
