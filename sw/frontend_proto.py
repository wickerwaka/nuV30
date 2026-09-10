#!/usr/bin/env python3
"""WAVE 8 -- THE STANDALONE A/B HARNESS.  MEASUREMENT ONLY, NO GATE.

WAVE 6's `sw/chainflat_proto.py` + `sw/run_chainflat_synth.py` in one file,
generalised from ONE hard-coded substitution to a NAMED ARM, so the arm this
wave measures is chosen by the ANATOMY and not by this file.

**IT TOUCHES NOTHING UNDER `hdl/`** (WAVE 8 bar H-5).  Both trees and both
Quartus projects live under `~/.cache/ucsimt-tmp/wave8/`; `hdl/nec_test.qsf`,
`hdl/nec_test_ucore.qsf` and `hdl/nec_test.sdc` are never opened, never patched
and never restored, because they are never used -- and the driver CHECKS that
by refusing on a tracked-dirty `hdl/` at the start and re-checking at the end.

⚠ **NO FIGURE HERE IS A DESIGN Fmax.**  `standing_gates.md` §A governs.
**WHAT THE COMPARISON IS FOR IS THE DIFFERENCE** between two forms compiled the
same way: WAVE 6 predicted **-9.431 ns** out of context and WAVE 7 realised
**-9.413** in the design -- a **0.2 %** correction -- while WAVE 5's
out-of-context PARTITION predictions mispredicted by **+11.3 ... +20.0 ns**.
**A DIFFERENCE TRANSFERS; A PARTITION PREDICTION DOES NOT.**  Both figures are
printed by this tool on every comparison it emits.

Usage:
    python3 sw/frontend_proto.py --gen --arm <name> [--qsf]
    python3 sw/frontend_proto.py --verify --arm <name>
    python3 sw/frontend_proto.py --synth --arm <name> --seeds 1,2,3,4,5
"""
import argparse, json, os, re, shutil, subprocess, sys, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
UC = os.path.join(ROOT, 'hdl/rtl/ucore')
TB = os.path.join(ROOT, 'hdl/tb')
SW = os.path.join(ROOT, 'sw')
SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/wave8')
QB = os.path.expanduser('~/intelFPGA_lite/17.1/quartus/bin')


def sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)


def guard():
    for b in ('quartus_map', 'quartus_fit', 'quartus_sta', 'quartus_asm', 'quartus_sh'):
        if sh(f'pgrep -x {b}').returncode == 0:
            print(f'REFUSING: {b} is running -- two writers on one db')
            return False
    return True


def run(argv, cwd, log):
    t0 = time.time()
    print('  $ ' + ' '.join(argv), flush=True)
    r = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
    open(log, 'a').write(r.stdout + r.stderr)
    print(f'    exit {r.returncode}  {time.time()-t0:.0f}s', flush=True)
    return r


# ===========================================================================
#  THE ARMS.  Each is ONE substitution, applied mechanically to a copy of
#  `hdl/rtl/ucore/`.  An arm that cannot make its edit RAISES -- it never
#  silently produces a tree identical to REF, because a null edit measured
#  against REF would report a delta of zero and read like a refutation.
# ===========================================================================
def _sub(path, old, new, n=1):
    t = open(path).read()
    c = t.count(old)
    if c != n:
        raise SystemExit(f'REFUSING: anchor occurs {c} times (expected {n}) '
                         f'in {os.path.basename(path)}:\n---\n{old}\n---')
    open(path, 'w').write(t.replace(old, new, n))
    return c


ARMS = {}


def arm(name):
    def deco(fn):
        ARMS[name] = fn
        return fn
    return deco


# ===========================================================================
#  ARM `ucflat` -- THE TOP CANDIDATE OF THE WAVE 8 ANATOMY.
#
#  MEASURED: `ucrom` -- the 612-LUT COMBINATIONAL microcode ROM read -- is
#  3.805 ns per path (3.386 .. 4.357) on 100 % of 1,600 endpoint-diverse paths
#  across four draws, the largest NAMED contributor in the census by 1.6x, and
#  the whole ROM head is 5.232 ns = 17.0 % of the arc.
#
#  THE ASYMMETRY THE MEASUREMENT HANDS OVER, and it is one sentence:
#      `ucdecode` is 8192 x 12 = 98,304 bits and costs 1.046 ns, because it is
#      in M10K with a REGISTERED ADDRESS.
#      `ucrom` is 1028 x 29 = 29,812 bits and costs 3.805 ns, because it is in
#      LUTs -- and it is in LUTs because its address `{dec_bank, upc_loc[1:0]}`
#      is not available until 1.046 ns into the clock, `dec_bank` being the
#      other table's output.  THE TWO LOOKUPS ARE IN SERIES INSIDE ONE CLOCK.
#
#  THE SUBSTITUTION: compose them at BUILD time into ONE table indexed by the
#  full 15-bit micro-address `{upc_page, upc_opc, upc_loc}`, read through the
#  SAME single register that exists today.  U0 already flattened the die's
#  MATCH PLA into a build-time table (finding F1); this flattens one composition
#  further, and it is the same function -- proved, not argued, by the
#  equivalence gate.
#
#  ⚠⚠ IT IS **NOT** WAVE 3's REFUTED MOVE, AND THE DIFFERENCE IS COUNTABLE.
#  WAVE 3 (`l2_registered_row_results_2026-09-08.md`) ADDED a second register,
#  `row_q`, beside the existing `dec_q`, and its own bar L-8 fired because the
#  NEW `upc -> ucdecode -> ucrom -> row_q` D-pin class BOUND on 3 of 10 draws.
#  This arm ADDS NO REGISTER: `flat_q` REPLACES `dec_q` one-for-one, so the
#  loop still contains exactly ONE register and exactly ONE new D-pin class
#  cannot appear -- the one that exists (`dec_addr_next` -> the ucdecode M10K
#  address register) becomes `uaddr_next` -> the ucflat M10K address register,
#  two bits wider and otherwise identical.  WAVE 8's pre-registration §0.2
#  excludes "register a microcode table output"; this registers nothing new.
#
#  ⚠ AND THE CORRECTNESS ARGUMENT IS L1's OWN, EXTENDED FROM TWO BITS TO FOUR.
#  `v30u_eu.sv`'s MICRO-ROW header says the decode of the micro-address the
#  bank is ABOUT TO COMMIT may be read on the edge that commits it, because
#  `dec_addr_next` is character for character the selection the bank applies to
#  `upc_*`.  `uaddr_next` is the same selection over all four bits of
#  `upc_loc` instead of its top two.  The `srst` mirroring arm is carried over
#  verbatim, including its falsifier.
#
#  ⚠ THE COST IS MEMORY: 32768 x 30 = 983,040 bits against 98,304 + 612 LUTs.
#  That is real and it is REPORTED, not hidden.  Whether it fits the design's
#  M10K budget is a LANDING question and this wave lands nothing.
# ===========================================================================
UCROM_FLAT = """
// WAVE 8 ARM `ucflat` -- generated by sw/frontend_proto.py.  NOT the design.
// The two build-time tables composed into ONE, read through ONE registered
// address.  See the arm's own header in sw/frontend_proto.py.
// ⚠ THE SIMULATION `HEXDIR` IS THIS ARM'S OWN TREE, not `hdl/rtl/ucore/`.
// `ucflat.hex` is generated INTO the arm tree and `hdl/` is never written
// (WAVE 8 bar H-5).  The SYNTHESIS default is unchanged and resolves through
// the project's `rtl -> tree` symlink exactly as the reference arm's does.
// F44's probe below is what said so: the first form of this module kept the
// shipped default, could not find the table, and $fatal'd instead of running
// with an all-zero ROM.
module v30u_ucrom #(
`ifdef SYNTHESIS
    parameter string HEXDIR = "rtl/ucore/"
`else
    parameter string HEXDIR = "@TREE@/"
`endif
) (
    // {page[2:0], opc[7:0], loc[3:0]}
    input      [14:0] flat_addr,
    output     [29:0] flat_word
);
reg [29:0] ucflat [0:32767];
initial begin
    $readmemh({HEXDIR, "ucflat.hex"}, ucflat);
end
`ifndef SYNTHESIS
// F44 -- THE SILENT-EMPTY FAILURE MODE.  A wrong HEXDIR yields an all-zero
// table and a run that COMPLETES NORMALLY.  Probe the table after the load.
initial begin
    #0;
    if (ucflat[15'h0000] === 30'd0 || (^ucflat[15'h0000]) === 1'bx)
        $fatal(1, "v30u_ucrom(ucflat): ucflat.hex did not load from '%s' (F44)", HEXDIR);
    // 0x790C is the flat index of `ucdecode`'s LAST VALID entry (0x1E43),
    // which is where the original probe looked for a SHORT file.
    if (ucflat[15'h790C] === 30'd0 || (^ucflat[15'h790C]) === 1'bx)
        $fatal(1, "v30u_ucrom(ucflat): ucflat.hex is SHORT from '%s' (F44)", HEXDIR);
end
`endif
assign flat_word = ucflat[flat_addr];
endmodule
"""


def _gen_flat_hex(tree):
    """Compose ucdecode.hex x ucrom.hex into ucflat.hex, 32768 x 30.

    word = {dec_valid, ucrom[{dec_bank, loc[1:0]}]}, and where the decode is
    INVALID the row word is left 0 -- exactly what `row_nop = !dec_valid`
    already makes the EU ignore.  THE COMPOSITION IS CHECKED, NOT ASSERTED:
    every one of the 8,192 decode entries is re-read back out of the flat
    table for all four `loc[1:0]` values and compared.
    """
    dec = [int(l.strip(), 16) for l in open(os.path.join(tree, 'ucdecode.hex'))
           if l.strip()]
    rom = [int(l.strip(), 16) for l in open(os.path.join(tree, 'ucrom.hex'))
           if l.strip()]
    assert len(dec) == 8192, len(dec)
    assert len(rom) == 1028, len(rom)
    flat = [0] * 32768
    for a in range(8192):
        w = dec[a] & 0x3FF
        valid = (w >> 9) & 1
        bank = w & 0x1FF
        page = (a >> 10) & 0x7
        opc = (a >> 2) & 0xFF
        grp = a & 0x3
        for lo in range(4):
            ra = (bank << 2) | lo
            rw = rom[ra] if (valid and ra < len(rom)) else 0
            flat[(page << 12) | (opc << 4) | (grp << 2) | lo] = (valid << 29) | (rw & 0x1FFFFFFF)
    # --- THE CHECK, and it is DELIBERATELY NOT THE SAME LOOP.  It walks
    # (page, opc, loc) -- the machine's own coordinates -- and derives BOTH
    # indices from them independently, so an error in the write loop's index
    # arithmetic cannot reproduce itself in the read.
    bad = 0
    nz_valid = 0
    for page in range(8):
        for opc in range(256):
            for loc in range(16):
                da = (page << 10) | (opc << 2) | (loc >> 2)
                w = dec[da] & 0x3FF
                valid = (w >> 9) & 1
                bank = w & 0x1FF
                ra = (bank << 2) | (loc & 3)
                want = (valid << 29) | ((rom[ra] if (valid and ra < len(rom)) else 0)
                                        & 0x1FFFFFFF)
                got = flat[(page << 12) | (opc << 4) | loc]
                if got != want:
                    bad += 1
                if valid:
                    nz_valid += 1
    if bad:
        raise SystemExit(f'REFUSING: flat composition self-check failed on {bad} entries')
    with open(os.path.join(tree, 'ucflat.hex'), 'w') as fh:
        for v in flat:
            fh.write('%08X\n' % v)
    nz = sum(1 for v in flat if v)
    distinct_rows = len({v & 0x1FFFFFFF for v in flat if v >> 29})
    return {'entries': 32768, 'nonzero': nz,
            'valid_decodes': sum(1 for a in range(8192) if (dec[a] >> 9) & 1),
            'valid_flat_entries': nz_valid,
            'distinct_row_words': distinct_rows,
            'selfcheck_entries': 32768, 'selfcheck_bad': bad}


@arm('ucflat')
def _arm_ucflat(tree):
    meta = {'hex': _gen_flat_hex(tree)}
    open(os.path.join(tree, 'v30u_ucrom.sv'), 'w').write(
        UCROM_FLAT.replace('@TREE@', tree))
    eu = os.path.join(tree, 'v30u_eu.sv')

    # (1) the declarations + the instance
    _sub(eu, """wire [12:0] dec_addr_next;          // assigned beside THE COMMIT, below
wire        dec_valid_next;
wire  [8:0] dec_bank_next;
reg   [9:0] dec_q;
wire        dec_valid = dec_q[9];
wire  [8:0] dec_bank  = dec_q[8:0];
wire [28:0] row;

v30u_ucrom u_ucrom (
    .dec_addr (dec_addr_next),
    .dec_valid(dec_valid_next),
    .dec_bank (dec_bank_next),
    .rom_addr ({dec_bank, upc_loc[1:0]}),
    .rom_word (row)
);""",
         """// WAVE 8 ARM `ucflat`: ONE table, ONE register, ONE lookup.
wire [14:0] uaddr_next;             // assigned beside THE COMMIT, below
wire [29:0] flat_word;
reg  [29:0] flat_q;
wire        dec_valid = flat_q[29];
wire [28:0] row       = flat_q[28:0];

v30u_ucrom u_ucrom (
    .flat_addr (uaddr_next),
    .flat_word (flat_word)
);""")

    # (2) the address expression -- L1's `srst` mirroring, all four loc bits
    _sub(eu, """assign dec_addr_next = (srst && !ss_we)
        ? {upc_page_r, upc_opc_r, upc_loc_r[3:2]}
        : {upc_page_n, upc_opc_n, upc_loc_n[3:2]};""",
         """assign uaddr_next = (srst && !ss_we)
        ? {upc_page_r, upc_opc_r, upc_loc_r}
        : {upc_page_n, upc_opc_n, upc_loc_n};""")

    # (3) the commit
    _sub(eu, "        dec_q <= {dec_valid_next, dec_bank_next};",
             "        flat_q <= flat_word;")
    return meta


# ===========================================================================
def gen(armname):
    os.makedirs(SCRATCH, exist_ok=True)
    out = {}
    for kind in ('ref', armname):
        d = os.path.join(SCRATCH, 'tree_' + kind)
        if os.path.exists(d):
            shutil.rmtree(d)
        shutil.copytree(UC, d)
        out[kind] = d
    meta = ARMS[armname](out[armname])
    r = subprocess.run(['diff', '-r', UC, out['ref']], capture_output=True, text=True)
    meta['ref_identical'] = (r.returncode == 0)
    d = subprocess.run(['diff', '-u', os.path.join(UC, 'v30u_eu.sv'),
                        os.path.join(out[armname], 'v30u_eu.sv')],
                       capture_output=True, text=True).stdout
    meta['arm_diff'] = d
    meta['arm_diff_lines'] = len([l for l in d.split('\n')
                                  if l[:1] in '+-' and l[:3] not in ('+++', '---')])
    meta['trees'] = out
    print('REF  %s   byte-identical to hdl/rtl/ucore: %s'
          % (out['ref'], meta['ref_identical']))
    print('ARM  %s   %d changed source lines'
          % (out[armname], meta['arm_diff_lines']))
    if meta['arm_diff_lines'] == 0:
        raise SystemExit('REFUSING: the arm made no edit.')
    return meta


# --------------------------------------------------------------------------
WARN = ['-Wall', '-Wno-UNUSEDSIGNAL', '-Wno-VARHIDDEN', '-Wno-TIMESCALEMOD',
        '-Wno-WIDTHEXPAND', '-Wno-BLKSEQ', '-Wno-DECLFILENAME', '-Wno-UNUSEDPARAM']
RTL = ['v30u_ss_pkg.sv', 'v30_core.sv', 'v30u_biu.sv', 'v30u_ucrom.sv', 'v30u_eu.sv']


def vbuild(tree, top, objdir):
    if top == 'tb_v30_core':
        srcs = ([os.path.join(tree, 'v30u_ss_pkg.sv'),
                 os.path.join(TB, 'tb_v30_core.sv')]
                + [os.path.join(tree, f) for f in RTL[1:]])
        extra = ['-DV30_BACKDOOR', '-DV30_PFX_ASSERT', '--assert', '-DV30_UCORE']
    else:
        srcs = ([os.path.join(TB, top + '.sv')] + [os.path.join(tree, f) for f in RTL])
        extra = ['-Wno-MULTIDRIVEN', '-Wno-UNOPTFLAT', '-Wno-CASEINCOMPLETE']
    cmd = (['verilator', '--binary', '--timing', '-DV30_MUXED_AD'] + extra
           + WARN + ['--top-module', top, '-I' + tree, '-Mdir', objdir] + srcs)
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    binp = os.path.join(objdir, 'V' + top)
    if p.returncode != 0 or not os.path.exists(binp):
        sys.stderr.write((p.stdout + p.stderr)[-6000:])
        raise SystemExit('frontend_proto: BUILD FAILED %s / %s' % (tree, top))
    return binp


def verify(armname, golden_args='--core ucore --opcodes all --cases 0',
           seeds=('1', '2', '3', '4'), clocks=400000):
    """THE EQUIVALENCE GATE.  No delay figure may be quoted until it passes."""
    res = {}
    for kind in ('ref', armname):
        tree = os.path.join(SCRATCH, 'tree_' + kind)
        obj = os.path.join(SCRATCH, 'vobj_' + kind)
        core = vbuild(tree, 'tb_v30_core', obj + '_core')
        lf = vbuild(tree, 'tb_chain_lfsr', obj + '_lfsr')
        code = ('import sys, pathlib\n'
                f'sys.path.insert(0, {SW!r})\n'
                'import check_core as cc\n'
                f'cc.core_objdir = lambda c: pathlib.Path({obj + "_core"!r})\n'
                'cc.build = lambda *a, **k: None\n'
                f'sys.argv = ["check_core"] + {golden_args.split()!r}\n'
                'sys.exit(cc.main())\n')
        p = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                           capture_output=True, text=True, timeout=14400)
        m = re.search(r'TOTAL:\s+(\d+)/(\d+)', p.stdout)
        sigs, depths = [], []
        for s in seeds:
            q = subprocess.run([lf, '+chaindepth', f'+seed={s}', f'+clocks={clocks}'],
                               cwd=ROOT, capture_output=True, text=True, timeout=7200)
            o = q.stdout + q.stderr
            sg = re.search(r'LFSR_SIG\s+([0-9a-f]+)', o)
            sigs.append(sg.group(1) if sg else 'MISSING')
            d = [int(x) for x in re.findall(r'CHAIN_DEPTH_MAX\s+(\d+)', o)]
            depths.append(max(d) if d else 0)
            if 'RESULT OK' not in o:
                sigs[-1] = 'NOT-OK'
        res[kind] = {'golden': m.group(0) if m else 'MISSING',
                     'golden_rc': p.returncode, 'lfsr_sigs': sigs,
                     'lfsr_depths': depths, 'tail': p.stdout[-400:]}
        print('[%s] %s  rc=%d  LFSR sigs %s  depths %s'
              % (kind, res[kind]['golden'], p.returncode, sigs, depths), flush=True)
    ok = (res['ref']['golden'] == res[armname]['golden']
          and res['ref']['golden'] == 'TOTAL: 169000/169000'
          and res['ref']['lfsr_sigs'] == res[armname]['lfsr_sigs']
          and 'MISSING' not in res[armname]['lfsr_sigs']
          and 'NOT-OK' not in res[armname]['lfsr_sigs']
          and res['ref']['golden_rc'] == 0 and res[armname]['golden_rc'] == 0)
    print()
    print('PC-E0  the ARM tree computes the SAME function as REF           '
          ': %s' % ('PASS' if ok else 'FAIL'))
    print('       golden  REF %s   ARM %s' % (res['ref']['golden'], res[armname]['golden']))
    print('       LFSR    REF %s' % ' '.join(res['ref']['lfsr_sigs']))
    print('               ARM %s' % ' '.join(res[armname]['lfsr_sigs']))
    res['PC-E0'] = ok
    return ok, res


# --------------------------------------------------------------------------
PORT_RE = re.compile(r'^\s*(input|output|inout)\s+(?:wire\s+|reg\s+|logic\s+)?'
                     r'(?:\[[^\]]*\]\s*)?([A-Za-z_][A-Za-z0-9_]*)')


def ports(tree):
    txt = open(os.path.join(tree, 'v30u_eu.sv')).read()
    m = re.search(r'^module\s+v30u_eu\s*\((.*?)^\);', txt, re.S | re.M)
    out = []
    for line in m.group(1).split('\n'):
        line = line.split('//')[0]
        mm = PORT_RE.match(line)
        if mm:
            out.append(mm.group(2))
    return out


QSF = """# WAVE 8 -- STANDALONE `v30u_eu` PROJECT.  GENERATED by sw/frontend_proto.py.
# It is NOT the design; it is ucore_provenance.md sec.51.1's harness (`v30u_eu`
# as its own top with virtual pins), used here so two forms are compiled ALONE
# and compared TO EACH OTHER.  NO Fmax quoted from it is a design figure, and
# only the DIFFERENCE between the two arms is offered as evidence.
set_global_assignment -name FAMILY "Cyclone V"
set_global_assignment -name DEVICE 5CSEBA6U23I7
set_global_assignment -name TOP_LEVEL_ENTITY v30u_eu
set_global_assignment -name LAST_QUARTUS_VERSION "17.1.0 Lite Edition"
set_global_assignment -name OPTIMIZATION_MODE "HIGH PERFORMANCE EFFORT"
set_global_assignment -name NUM_PARALLEL_PROCESSORS ALL
set_global_assignment -name PROJECT_OUTPUT_DIRECTORY output
set_global_assignment -name SEARCH_PATH "{tree}"
set_global_assignment -name SDC_FILE cf.sdc
set_global_assignment -name SYSTEMVERILOG_FILE "{tree}/v30u_ss_pkg.sv"
set_global_assignment -name SYSTEMVERILOG_FILE "{tree}/v30u_ucrom.sv"
set_global_assignment -name SYSTEMVERILOG_FILE "{tree}/v30u_eu.sv"
set_global_assignment -name VERILOG_MACRO "SYNTHESIS=1"
set_global_assignment -name VERILOG_MACRO "V30_MUXED_AD=1"
{vpins}
"""

SDC = """# WAVE 8 -- the standalone harness's SDC.  NO `set_multicycle_path`: the
# USER RULING of 2026-09-08 makes the NO-EXCEPTION configuration the goal state.
create_clock -name clk -period 31.250 [get_ports clk]
derive_clock_uncertainty
set_false_path -from [get_ports *]
set_false_path -to   [get_ports *]
"""


def qsf(kind):
    tree = os.path.join(SCRATCH, 'tree_' + kind)
    proj = os.path.join(SCRATCH, 'proj_' + kind)
    os.makedirs(proj, exist_ok=True)
    ps = [p for p in ports(tree) if p != 'clk']
    vp = '\n'.join('set_instance_assignment -name VIRTUAL_PIN ON -to %s' % p for p in ps)
    open(os.path.join(proj, 'cf.qsf'), 'w').write(QSF.format(tree=tree, vpins=vp))
    open(os.path.join(proj, 'cf.sdc'), 'w').write(SDC)
    open(os.path.join(proj, 'cf.qpf'), 'w').write(
        'QUARTUS_VERSION = "17.1"\nDATE = "00:00:00  January 01, 2026"\n'
        'PROJECT_REVISION = "cf"\n')
    # F44: `HEXDIR` defaults to "rtl/ucore/" under SYNTHESIS, relative to cwd.
    link = os.path.join(proj, 'rtl')
    if os.path.islink(link):
        os.remove(link)
    elif os.path.exists(link):
        shutil.rmtree(link)
    os.makedirs(link)
    os.symlink(tree, os.path.join(link, 'ucore'))
    print('[qsf] %s   %d virtual pins' % (proj, len(ps)))
    return proj


FIT_ALM = re.compile(r'Logic utilization \(in ALMs\)\s*;\s*([\d,]+)')
FIT_COMB = re.compile(r'Combinational ALUTs?\s*;\s*([\d,]+)')
FIT_REG = re.compile(r'Total registers\s*;\s*([\d,]+)')
FIT_SEED = re.compile(r'Fitter Initial Placement Seed\s*;\s*(\d+)')
MAP_ERR = re.compile(r'Error \(\d+\)')


def parse_reports(proj):
    out = {}
    p = os.path.join(proj, 'output', 'cf.fit.rpt')
    if os.path.exists(p):
        t = open(p, errors='replace').read()
        for rx, key in ((FIT_ALM, 'alms'), (FIT_COMB, 'comb_aluts'),
                        (FIT_REG, 'registers'), (FIT_SEED, 'seed')):
            m = rx.search(t)
            if m:
                out[key] = m.group(1)
    p = os.path.join(proj, 'output', 'cf.map.rpt')
    if os.path.exists(p):
        t = open(p, errors='replace').read()
        out['map_errors'] = len(MAP_ERR.findall(t))
        # F44 POSITIVE check: a WRONG HEXDIR gives an all-zero ROM and a
        # compile that SUCCEEDS.  The `ucrom.hex(1)` truncation warning is
        # what PROVES the table was read.
        out['hex_loaded'] = ('ucrom.hex' in t)
        out['hexdir_missing'] = len(re.findall(r"can't find.*\.hex", t))
    return out


def synth(armname, seeds, npaths, outdir, skip_map=False, kinds=None):
    dirty = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    if dirty:
        print('REFUSING: hdl/ carries tracked changes:\n' + dirty)
        return 2, {}
    outdir = os.path.join(ROOT, outdir)
    os.makedirs(outdir, exist_ok=True)
    log = os.path.join(outdir, 'synth.log')
    open(log, 'a').write('=== frontend_proto --synth ===\n')
    res = {}
    for kind in (kinds or ['ref', armname]):
        proj = os.path.join(SCRATCH, 'proj_' + kind)
        if not os.path.exists(os.path.join(proj, 'cf.qsf')):
            print('REFUSING: no project at ' + proj)
            return 2, {}
        if not guard():
            return 2, {}
        if skip_map:
            print(f'\n=== MAP: {kind} SKIPPED ===', flush=True)
        else:
            print(f'\n=== MAP: {kind} ===', flush=True)
            if run([f'{QB}/quartus_map', 'cf', '-c', 'cf'], proj, log).returncode:
                print('MAP FAILED for ' + kind)
                return 1, res
        for sd in seeds:
            if not guard():
                return 2, res
            print(f'\n=== FIT: {kind} seed {sd} ===', flush=True)
            if run([f'{QB}/quartus_fit', f'--seed={sd}', '--recompile=off',
                    'cf', '-c', 'cf'], proj, log).returncode:
                print('FIT FAILED')
                return 1, res
            stem = os.path.join(outdir, f'{kind}_seed{sd}')
            run([f'{QB}/quartus_sta', '-t', f'{ROOT}/sw/sta_chainflat.tcl',
                 'cf', 'cf', stem, npaths], proj, log)
            r = parse_reports(proj)
            r['sta_exists'] = os.path.exists(stem + '.txt')
            res[f'{kind}_seed{sd}'] = r
            print('    ' + json.dumps(r))
    left = sh("git status --porcelain hdl/ | grep -v '^??'").stdout.strip()
    print('\nhdl/ at end: %s' % (left or 'CLEAN'))
    return 0, res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--gen', action='store_true')
    ap.add_argument('--qsf', action='store_true')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--synth', action='store_true')
    ap.add_argument('--seeds', default='1,2,3,4,5')
    ap.add_argument('--kinds', default=None)
    ap.add_argument('--npaths', default='400')
    ap.add_argument('--clocks', type=int, default=400000)
    ap.add_argument('--skip-map', action='store_true')
    ap.add_argument('--outdir', default=None)
    a = ap.parse_args()
    if a.arm not in ARMS:
        print('unknown arm %r; known: %s' % (a.arm, ' '.join(sorted(ARMS))))
        return 2
    outdir = a.outdir or ('sw/testdata/frontend/' + a.arm)
    meta = {}
    if a.gen:
        meta = gen(a.arm)
    if a.qsf:
        meta['projects'] = {k: qsf(k) for k in ('ref', a.arm)}
    ok = True
    if a.verify:
        ok, v = verify(a.arm, clocks=a.clocks)
        meta['verify'] = v
    if a.synth:
        rc, r = synth(a.arm, [s for s in a.seeds.split(',') if s.strip()],
                      a.npaths, outdir, a.skip_map,
                      a.kinds.split(',') if a.kinds else None)
        meta['synth'] = r
        ok &= (rc == 0)
    if meta:
        os.makedirs(os.path.join(ROOT, outdir), exist_ok=True)
        p = os.path.join(ROOT, outdir, 'proto.json')
        old = {}
        if os.path.exists(p):
            try:
                old = json.load(open(p))
            except Exception:
                old = {}
        old.update(meta)
        json.dump(old, open(p, 'w'), indent=1, default=str)
        print('wrote %s' % p)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
