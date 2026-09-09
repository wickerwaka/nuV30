#!/usr/bin/env python3
"""WAVE 8 (THE FRONT END) -- THE SOURCE-DERIVED MARKER RULE AND STAGE MAP.

MEASUREMENT ONLY.  It is NOT a gate, it writes no receipt, and no Fmax may be
quoted from it.

=============================================================================
WHY THIS FILE EXISTS
=============================================================================
WAVE 5's segmenter (`sw/sta_chain_anatomy.tcl`) cuts a timing arc into chain
positions by finding netlist pins named after a MARKER SET, hard-coded there as
`{st_n stop st_zero_ok}`.  WAVE 7's flattening deleted `st_zero_ok` from the
netlist (the nine `st_n == S_X` guards make the nine-way OR redundant and
Quartus removes it), the tool's own control PC-3 REFUSED, and WAVE 7 recorded
-- correctly -- that *choosing a replacement marker after seeing the refusal is
fitting-shaped*.

So the marker set is not chosen here.  It is DERIVED BY A RULE, the rule is
committed before the tool is run against the post-flattening netlist (WAVE 8
bar H-2), and the rule is validated by requiring it to REPRODUCE WAVE 5's OWN
PUBLISHED SEGMENTATION on WAVE 7's committed pre-landing artifacts.

=============================================================================
THE MARKER RULE  (committed before any WAVE 8 fit; bar H-2)
=============================================================================
    A base name is a CHAIN-POSITION BOUNDARY MARKER if and only if it is
      (i)  READ by a chain position's ENTRY GUARD in the chain pass of
           `hdl/rtl/ucore/v30u_eu.sv`, AND
      (ii) ASSIGNED inside a chain ARM BODY.

Clause (i) is what makes it a boundary -- crossing it is how the netlist gets
from one position to the next.  Clause (ii) is what makes it LOOP-CARRIED: a
name a guard reads but no arm writes is an INPUT to the whole pass, not a
carrier between positions, and cannot separate two positions.

It is a rule about the SOURCE, evaluated on whatever revision it is handed, and
it names no netlist node.  On BOTH trees it yields exactly

    {st_n, stop}

  * PRE-landing (`aba01feb07`), the guard is
        if (!stop) ... if ((chain != 4'd0) && !st_zero_ok(st_n)) stop = 1'b1;
    reading {stop, chain, st_zero_ok, st_n}; of those, `stop` and `st_n` are
    assigned by arm bodies, `st_zero_ok` is a FUNCTION (never assigned) and
    `chain` is the position label (assigned by the pass, not by an arm).
  * POST-landing (`8deb1e7d8e`), the guards are
        if (!stop && (st_n == S_X))
    reading {stop, st_n} plus the nine `S_*` state constants, which are
    localparams and are assigned by nothing.

⚠ SO THE RULE DOES NOT PICK A NEW MARKER AT ALL.  It says WAVE 5's set was
`{st_n, stop}` PLUS ONE NAME THAT WAS NEVER LOAD-BEARING, and that WAVE 7's
refusal was a defect in PC-3's PIN SELECTION -- the control forced its path
through an `st_zero_ok` pin specifically -- and not in the segmentation.  The
repair is therefore to the CONTROL (try each marker's pins in the rule's own
declared order and NAME the one that answered, exactly as WAVE 5 repaired its
own vacuous PC-4), not to the marker set.

⚠ AND THAT CLAIM IS FALSIFIABLE, WHICH IS PC-M2 BELOW: on WAVE 7's committed
PRE-LANDING arrival points, segmenting with `{st_n, stop}` must reproduce the
published `{st_n, stop, st_zero_ok}` segmentation EXACTLY -- same boundary
count, same spans to the thousandth.  If it does not, the rule is REFUSED and
nothing downstream may quote it.

=============================================================================
THE STAGE RULE  (also committed before any WAVE 8 fit)
=============================================================================
    A netlist node's STAGE is decided in this order, first match wins:

      1. the node's HIERARCHICAL name contains `|u_biu|`            -> BIU
      2. ...contains `|u_ucrom|` (the two microcode tables)         -> ROMHEAD
      3. ...is outside `|u_eu|`                                     -> OUTSIDE
      4. its BASE NAME is assigned in a chain ARM file or in
         `v30u_eu_step.svh`'s cone                                  -> CHAIN
      5. its BASE NAME is assigned in exactly one `//====` BANNER
         SECTION of `v30u_eu.sv`                -> that section's TITLE
      6. its BASE NAME is assigned in more than one section         -> AMBIG
      7. otherwise                                                  -> UNMAPPED

The `//====`-banner sections of `hdl/rtl/ucore/v30u_eu.sv` are the file's own
declared structure -- `THE MICRO-ROW STANDING ON upc`, `THE ROW'S DEMANDS`,
`SOURCE / DESTINATION MUXES`, `THE ALU`, `STALLS`, ... -- written by the
authors long before this wave, so the partition is not this wave's invention
and cannot be tuned to a result.  `AMBIG` and `UNMAPPED` are REPORTED, never
resolved to a convenient section.

Quartus's own synthesised names (`MuxNNN`, `SelectorNNN`, `DecoderNNN`,
`EqualNNN`, `AddNNN`, `RamNNN`, `always6`, `comb`) have no RTL base name and
land in `UNMAPPED` by construction.  THAT IS A REAL LIMIT OF THE INSTRUMENT AND
IT IS REPORTED AS A PERCENTAGE OF EVERY CENSUS, never hidden.
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
UC = os.path.join(ROOT, 'hdl/rtl/ucore')
EU = 'v30u_eu.sv'
STEP = 'v30u_eu_step.svh'
ARM_GLOB = 'v30u_eu_arm_'

INC_RE = re.compile(r'^\s*`include\s+"([^"]+)"')
IDENT_RE = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')
# an assignment target: `name` or `name[...]` at the head of a statement
ASSIGN_RE = re.compile(r'(?:^|[;\)]\s*|\bbegin\b\s*|\belse\b\s*|\bdo\b\s*)'
                       r'([A-Za-z_][A-Za-z0-9_]*)\s*(?:\[[^\]=]*\])?\s*(?:<?=)(?!=)',
                       re.M)
# ⚠ `chain_srcmap.py`'s ASSIGN_RE (inherited above) matches PROCEDURAL targets
# only.  `v30u_eu.sv`'s front end is mostly CONTINUOUS -- `wire [15:0] sigma =
# ...` and `assign x = ...` -- and neither form has a `;`, `begin` or `)` in
# front of the target, so both were invisible to it.  MEASURED by PC-S1, which
# reported `sigma` UNMAPPED before this line existed.
DECL_ASSIGN_RE = re.compile(
    r'^\s*(?:wire|reg|logic|bit)\s+(?:signed\s+)?(?:\[[^\]]*\]\s*)?'
    r'([A-Za-z_][A-Za-z0-9_]*)\s*=', re.M)
CONT_ASSIGN_RE = re.compile(r'^\s*assign\s+([A-Za-z_][A-Za-z0-9_]*)', re.M)


def all_targets(text):
    """Every identifier assigned in `text`: procedural, declaration-with-
    initialiser, and continuous."""
    return ({m.group(1) for m in ASSIGN_RE.finditer(text)} |
            {m.group(1) for m in DECL_ASSIGN_RE.finditer(text)} |
            {m.group(1) for m in CONT_ASSIGN_RE.finditer(text)})
BANNER_RE = re.compile(r'^//=+\s*$')

SV_KEYWORDS = {
    'if', 'else', 'begin', 'end', 'case', 'endcase', 'default', 'for', 'while',
    'assign', 'wire', 'reg', 'logic', 'always', 'posedge', 'negedge', 'or',
    'and', 'not', 'function', 'endfunction', 'automatic', 'input', 'output',
    'localparam', 'parameter', 'bit', 'integer', 'return', 'module',
    'endmodule', 'signed', 'unsigned', 'do', 'break', 'continue',
}


def strip_comments(text):
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    return '\n'.join(l.split('//')[0] for l in text.split('\n'))


def rev_text(rev, path):
    """The text of `path` at git revision `rev`; rev=None means the worktree."""
    if rev is None:
        return open(os.path.join(ROOT, path)).read()
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f'git show {rev}:{path} failed: {r.stderr.strip()}')
    return r.stdout


def rev_ls(rev, prefix):
    if rev is None:
        return sorted(f for f in os.listdir(UC) if f.startswith(prefix))
    r = subprocess.run(['git', 'ls-tree', '--name-only', rev, 'hdl/rtl/ucore/'],
                       cwd=ROOT, capture_output=True, text=True)
    return sorted(os.path.basename(l) for l in r.stdout.split()
                  if os.path.basename(l).startswith(prefix))


# ===========================================================================
#  THE CHAIN PASS -- located by its own banner, not by a line number
# ===========================================================================
PASS_START = re.compile(r'THE ZERO-COST CHAIN|for \(chain\s*=\s*0')
PASS_END = re.compile(r'CHAIN OVERFLOW and the depth tracker')


def chain_pass_text(eu_text):
    """The chain pass region of v30u_eu.sv, comments STRIPPED.

    Located between the pass's own opening comment / `for` header and the
    closing comment both forms carry verbatim.  Refuses rather than guessing.
    """
    lines = eu_text.split('\n')
    a = b = None
    for i, l in enumerate(lines):
        if a is None and PASS_START.search(l):
            a = i
        if a is not None and PASS_END.search(l):
            b = i
            break
    if a is None or b is None:
        raise SystemExit('REFUSING: cannot locate the chain pass in v30u_eu.sv')
    return strip_comments('\n'.join(lines[a:b])), a, b


GUARD_RE = re.compile(r'\bif\s*\(')


def guard_idents(pass_text):
    """Identifiers READ by the pass's `if (...)` conditions.

    Every `if` in the pass region is a position entry guard or the fail-safe;
    both are entry conditions and both are taken.  Balanced-paren scan, so a
    nested call like `st_zero_ok(st_n)` is inside the condition, not truncated.
    """
    out = set()
    for m in GUARD_RE.finditer(pass_text):
        i = m.end() - 1
        depth = 0
        j = i
        while j < len(pass_text):
            if pass_text[j] == '(':
                depth += 1
            elif pass_text[j] == ')':
                depth -= 1
                if depth == 0:
                    break
            j += 1
        cond = pass_text[i + 1:j]
        for t in IDENT_RE.findall(cond):
            if t in SV_KEYWORDS or t[0].isdigit():
                continue
            out.add(t)
    return out


def arm_files(rev):
    """The chain ARM bodies: the nine arm includes plus the step case's cone."""
    return [f for f in rev_ls(rev, ARM_GLOB)] + [STEP]


def expand_text(rev, fn, seen=None):
    seen = seen or set()
    if fn in seen:
        return ''
    seen = seen | {fn}
    out = []
    for line in strip_comments(rev_text(rev, f'hdl/rtl/ucore/{fn}')).split('\n'):
        m = INC_RE.match(line)
        if m:
            try:
                out.append(expand_text(rev, m.group(1), seen))
                continue
            except SystemExit:
                pass
        out.append(line)
    return '\n'.join(out)


def arm_assigned(rev):
    """Every identifier assigned inside a chain arm body (includes spliced)."""
    out = set()
    for fn in arm_files(rev):
        txt = expand_text(rev, fn)
        out |= all_targets(txt)
    return out


def derive_markers(rev=None, verbose=False):
    """THE MARKER RULE.  Returns (markers, derivation dict)."""
    eu = rev_text(rev, f'hdl/rtl/ucore/{EU}')
    pt, a, b = chain_pass_text(eu)
    read = guard_idents(pt)
    assigned = arm_assigned(rev)
    markers = sorted(read & assigned)
    d = {
        'rev': rev or 'WORKTREE',
        'pass_lines': [a + 1, b + 1],
        'guard_idents': sorted(read),
        'guard_read_but_not_arm_assigned': sorted(read - assigned),
        'markers': markers,
    }
    if verbose:
        print(f"  rev {d['rev']}  chain pass at v30u_eu.sv:{a+1}-{b+1}")
        print(f"  (i)  identifiers READ by the pass's entry guards : "
              f"{' '.join(d['guard_idents'])}")
        print(f"  (ii) ...of those, ASSIGNED in a chain arm body   : "
              f"{' '.join(markers)}")
        print(f"       ...read but never arm-assigned (EXCLUDED)   : "
              f"{' '.join(d['guard_read_but_not_arm_assigned'])}")
    return markers, d


# ===========================================================================
#  THE SEGMENTER, re-implemented in Python EXACTLY as sta_chain_anatomy.tcl
#  has it, so PC-M2 can compare two marker sets on a COMMITTED artifact with
#  no Quartus in the loop.
# ===========================================================================
PINISH = {'combout', 'dataa', 'datab', 'datac', 'datad', 'datae', 'dataf',
          'datag', 'q', 'd', 'clk', 'cin', 'cout', 'sumout', 'shareout', 'o',
          'i', 'inclk', 'outclk', 'regout', 'datain'}


def norm(name):
    return '|'.join(s.split(':', 1)[1] if ':' in s else s for s in name.split('|'))


def basename2(name):
    segs = norm(name).split('|')
    if len(segs) > 1 and segs[-1] in PINISH:
        segs = segs[:-1]
    last = segs[-1]
    for ch in ('~', '['):
        k = last.find(ch)
        if k >= 0:
            last = last[:k]
    return last


def read_arrivalpoints(path):
    """-> (pts, launch, total, from, to).  `pts` are the DATA points only."""
    pts, launch, total = [], 0.0, 0.0
    frm = to = ''
    for line in open(path):
        f = line.split(None, 4)
        if len(f) < 5:
            continue
        inc, cum, ty, tag, nm = f[0], f[1], f[2], f[3], f[4].strip()
        try:
            inc, cum = float(inc), float(cum)
        except ValueError:
            continue
        total = cum
        if tag == 'LAUNCH':
            launch = cum
            frm = nm
        elif tag == 'DATA':
            pts.append((nm, cum, inc, ty))
        elif tag == 'DEST' and not to:
            to = nm
    return pts, launch, total, frm, to


def segment(pts, markers):
    """The Tcl `segment` proc, transliterated.  -> (segs, cuts)."""
    markers = set(markers)
    segs, cuts, names = [], [], []
    start, nc, nb, inmark, pend = -1.0, 0, 0, 0, 0.0
    for nm, cum, inc, ty in pts:
        if start < 0:
            start = cum - inc
        ismark = basename2(nm) in markers
        if ismark:
            inmark = 1
            pend = cum
        else:
            if inmark:
                segs.append((start, pend, nc, nb, names))
                cuts.append(pend)
                start, nc, nb, names, inmark = pend, 0, 0, [], 0
            if ty == 'cell':
                nc += 1
            if '|combout' in nm:
                nb += 1
                names.append(basename2(nm))
    if inmark:
        segs.append((start, pend, nc, nb, names))
        cuts.append(pend)
        start, nc, nb, names = pend, 0, 0, []
    segs.append((start, pts[-1][1], nc, nb, names))
    return segs, cuts


# ===========================================================================
#  THE STAGE MAP
# ===========================================================================
def banner_sections(text):
    """[(title, body)] for each `//====` banner section of a file.

    A section is `//====` / `// TITLE` / `//====` followed by everything up to
    the next such banner.  Anything before the first is `PROLOGUE`.
    """
    lines = text.split('\n')
    marks = []
    for i in range(len(lines) - 2):
        if (BANNER_RE.match(lines[i].strip()) and
                lines[i + 1].strip().startswith('//') and
                BANNER_RE.match(lines[i + 2].strip())):
            marks.append((i, lines[i + 1].strip().lstrip('/').strip()))
    out = []
    if not marks:
        return [('PROLOGUE', text)]
    if marks[0][0] > 0:
        out.append(('PROLOGUE', '\n'.join(lines[:marks[0][0]])))
    for k, (i, title) in enumerate(marks):
        j = marks[k + 1][0] if k + 1 < len(marks) else len(lines)
        out.append((title, '\n'.join(lines[i + 3:j])))
    return out


def build_stagemap(rev=None):
    eu = rev_text(rev, f'hdl/rtl/ucore/{EU}')
    sig2sec = {}
    for title, body in banner_sections(eu):
        for t in all_targets(strip_comments(body)):
            sig2sec.setdefault(t, set()).add(title)
    chain = arm_assigned(rev)
    return sig2sec, chain


# ⚠ THE `_n` SHADOW IS THE MODULE'S OWN DECLARED NAMING LAW, NOT A PATCH.
# `v30u_eu.sv`'s banner section *THE NEXT-STATE SHADOW* says verbatim: "One
# `_n` per state register".  The chain writes `opc_base_n`; the FLOP is
# `opc_base`; and Quartus names the flop's D-pin cone after the FLOP
# (`opc_base[3]~11|combout`).  So a netlist base name `B` is looked up as `B`
# AND as `B_n`, or the whole chain would classify as its own destination
# section.  MEASURED by PC-S1, which reported `opc_base` and `m_kind` in the
# pin-pipeline section before this clause existed.
def _lookup(b, sig2sec, chain):
    for cand in (b, b + '_n'):
        if cand in chain:
            return 'CHAIN'
    secs = set()
    for cand in (b, b + '_n'):
        secs |= sig2sec.get(cand, set())
    if not secs:
        return 'UNMAPPED'
    if len(secs) == 1:
        return next(iter(secs))
    return 'AMBIG'


# Quartus's own synthesised leaf names.  `Ram<N>` is separated from the rest
# because `v30u_eu` contains exactly NINE arrays -- `gpr`, `sreg`, `tmps`,
# `tmps_lat`, `gpr_r`, `sreg_r`, `gpr_n`, `sreg_n` and the sim-only `cp_seq` --
# so a `Ram<N>` inside `|u_eu|` is an ARRAY READ MUX and nothing else, and the
# brief asks specifically about one of them (`S_EA_CALC`'s eight-way `gpr_n`
# read).  The others carry no RTL identity at all and are ANON.
ANON_RE = re.compile(r'^(Mux|Selector|Decoder|Equal|Add|Sub|Mult|Div|LessThan|'
                     r'comb|always|process|WideOr|WideNor|WideXor|nx|_)\w*$')
RAM_RE = re.compile(r'^Ram\d*$')


def classify(node, sig2sec, chain):
    """THE STAGE RULE, first match wins.  `node` is a full hierarchical name."""
    n = norm(node)
    if '|u_biu|' in n:
        return 'BIU'
    if '|u_ucrom|' in n:
        return 'ROMHEAD'
    if '|u_eu|' not in n:
        return 'OUTSIDE'
    b = basename2(node)
    r = _lookup(b, sig2sec, chain)
    if r != 'UNMAPPED':
        return r
    if RAM_RE.match(b):
        return 'ARRAYMUX'
    if ANON_RE.match(b):
        return 'ANON'
    return 'UNMAPPED'


# ⚠ A READING, LABELLED AS ONE -- NOT A MEASUREMENT.
# 40-46 % of the arrival points on WAVE 7's committed pre-landing arcs are
# `ANON`: Quartus names a LUT after the OPERATION it implements (`Mux277`,
# `Selector1552`) and there is no RTL identifier to look up.  An anonymous cone
# exists in order to PRODUCE a named signal, so this reading attributes each
# ANON point to the stage of the next NAMED point DOWNSTREAM of it on the same
# path.  It is offered BESIDE the strict census, never instead of it, and every
# figure derived from it says CARRY-FORWARD.
def carry_forward(stages):
    """stages: the per-arrival-point stage list, in path order."""
    out = list(stages)
    nxt = 'TAIL-ANON'
    for i in range(len(out) - 1, -1, -1):
        if out[i] in ('ANON', 'UNMAPPED'):
            out[i] = nxt
        else:
            nxt = out[i]
    return out


# ===========================================================================
#  THE POSITIVE CONTROLS.  REPORTED FIRST.  A MISS VOIDS THE WAVE (H-1).
# ===========================================================================
PRELAND = os.path.join(ROOT, 'sw/testdata/chainanat-wave7-prelanding')
WAVE5_MARKERS = ['st_n', 'stop', 'st_zero_ok']
PRE_REV = 'aba01feb07'
# WAVE 5's published FRONT-END / CHAINABLE partition (chain_anatomy_results
# §5(a)), used as an independent reproduction target for the STAGE rule.
W5_FRONTEND = ['sigma', 's1_val', 'it_val']
W5_CHAINABLE = ['st_n', 'stop', 'ld_b_n', 'pv', 'opc_base', 'm_kind',
                'seg_override_n']


def controls(verbose=True):
    ok = True
    P = print if verbose else (lambda *a, **k: None)
    P("=== WAVE 8 SOURCE-MAP POSITIVE CONTROLS (reported FIRST; a miss voids "
      "the wave) ===")

    # ---- PC-M0: chain_srcmap's own control still recovers the file structure
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'sw/chain_srcmap.py'),
                        '--control'], capture_output=True, text=True, cwd=ROOT)
    m0 = (r.returncode == 0 and 'CONTROL: PASS' in r.stdout)
    P(f"  PC-M0 chain_srcmap structure   : {'PASS' if m0 else 'FAIL'}  "
      f"(33 arms / 24 guarded / 9 == st_zero_ok)")
    ok &= m0

    # ---- PC-M1: THE RULE, evaluated on BOTH trees, yields the SAME set
    mk_post, d_post = derive_markers(None)
    mk_pre, d_pre = derive_markers(PRE_REV)
    P(f"  PC-M1 the marker RULE")
    P(f"        POST-landing (worktree)  guards read "
      f"{' '.join(d_post['guard_idents'])}")
    P(f"                                 -> markers {' '.join(mk_post)}")
    P(f"        PRE-landing  ({PRE_REV})  guards read "
      f"{' '.join(d_pre['guard_idents'])}")
    P(f"                                 -> markers {' '.join(mk_pre)}")
    m1 = (mk_post == mk_pre == ['st_n', 'stop'])
    P(f"        the rule gives the SAME set on both trees, and it is "
      f"{{st_n, stop}} : {'PASS' if m1 else 'FAIL'}")
    ok &= m1

    # ---- PC-M2: on WAVE 7's COMMITTED pre-landing arrival points, the
    #      rule's set must reproduce WAVE 5's published segmentation.
    #
    # ⚠⚠ THE FIRST FORM OF THIS CONTROL WAS `IDENTICAL TO THE THOUSANDTH ON
    # THE RAW STREAM`, IT WAS RUN, AND IT MISSED ON 2 OF THE 4 DRAWS -- BEFORE
    # ANY WAVE 8 QUARTUS STAGE EXISTED.  It is restated here, and the ORIGINAL
    # FORM IS STILL COMPUTED AND STILL PRINTED (PC-M2c), because a bar that is
    # replaced silently is a bar that was softened.
    #
    # WHAT THE MISS WAS, EXACTLY: on CONTROL seeds 2 and 3 an `st_zero_ok` cell
    # sits IMMEDIATELY AFTER the last `st_n` cell of a marker run
    # (`st_n~85|combout` 44.585 -> `st_zero_ok~6|combout` 45.267 on seed 2).
    # WAVE 5's set swallows it into the run and cuts at 45.267; the rule's set
    # ends the run at 44.585 and the `st_zero_ok` cell becomes the first cell of
    # the downstream segment.  THE BOUNDARY COUNT DOES NOT MOVE; ONE BOUNDARY'S
    # TIME MOVES BY THAT ONE CELL.  So the two sets differ in the PLACEMENT OF
    # THE `st_zero_ok` CELLS THEMSELVES AND IN NOTHING ELSE -- which is
    # testable exactly, and is PC-M2b.
    #
    #   PC-M2a  the BOUNDARY COUNT is identical on every draw          MUST
    #   PC-M2b  with the `st_zero_ok` points DELETED from the stream,
    #           the two sets give byte-identical segmentations          MUST
    #   PC-M2c  max |delta cut| on the raw stream, and the cell that
    #           explains it                                          REPORTED
    #
    # ⚠ AND ON THE LANDED TREE THE QUESTION IS MOOT: WAVE 7 measured
    # `st_zero_ok` pins in the netlist = 0.  There is nothing for the two sets
    # to disagree about.
    P("  PC-M2 the rule reproduces WAVE 5's own segmentation on WAVE 7's")
    P("        committed PRE-LANDING artifacts (no Quartus in the loop)")
    n_cmp = 0
    m2a = m2b = True
    worst_d = 0.0
    worst_why = ''
    raw_identical = 0
    for f in sorted(os.listdir(PRELAND)):
        if not f.endswith('.arrivalpoints.txt'):
            continue
        pts, launch, total, frm, to = read_arrivalpoints(os.path.join(PRELAND, f))
        s5, c5 = segment(pts, WAVE5_MARKERS)
        s8, c8 = segment(pts, mk_pre)
        cnt_ok = (len(c5) == len(c8))
        m2a &= cnt_ok
        # PC-M2b: delete every `st_zero_ok` arrival point and re-segment
        pz = [q for q in pts if basename2(q[0]) != 'st_zero_ok']
        z5, k5 = segment(pz, WAVE5_MARKERS)
        z8, k8 = segment(pz, mk_pre)
        same_z = (len(k5) == len(k8) and
                  all(abs(x - y) < 1e-6 for x, y in zip(k5, k8)) and
                  len(z5) == len(z8) and
                  all(abs(x[0] - y[0]) < 1e-6 and abs(x[1] - y[1]) < 1e-6
                      for x, y in zip(z5, z8)))
        m2b &= same_z
        d = max([abs(x - y) for x, y in zip(c5, c8)] or [0.0])
        if d > worst_d:
            worst_d = d
            worst_why = f
        raw_identical += 1 if d < 1e-6 else 0
        spans = ' * '.join(f'{b - a:.3f}' for a, b, *_ in s8)
        P(f"        {f.replace('.arrivalpoints.txt',''):18s} "
          f"bnds W5 {len(c5)} / rule {len(c8)}  "
          f"{'COUNT-SAME' if cnt_ok else '*** COUNT DIFFERS ***'}  "
          f"{'z-IDENTICAL' if same_z else '*** z-DIFFERS ***'}  "
          f"max|dcut| {d:.3f}   spans {spans}")
        n_cmp += 1
    m2a &= (n_cmp >= 4)
    P(f"        PC-M2a boundary COUNT identical on {n_cmp} draws "
      f"(MUST be >= 4) : {'PASS' if m2a else 'FAIL'}")
    P(f"        PC-M2b with `st_zero_ok` points deleted, segmentations "
      f"byte-identical : {'PASS' if m2b else 'FAIL'}")
    P(f"        PC-M2c THE ORIGINAL BAR, STILL COMPUTED: raw-stream "
      f"segmentations identical on {raw_identical} of {n_cmp} draws;")
    P(f"               max |delta cut| = {worst_d:.3f} ns ({worst_why}), which "
      f"is one `st_zero_ok` cell")
    ok &= (m2a and m2b)

    # ---- PC-M3: the segmenter can say NO -- a marker that does not exist
    pts, *_ = read_arrivalpoints(os.path.join(PRELAND, 'control_seed1.arrivalpoints.txt'))
    _, c_neg = segment(pts, ['zzz_no_such_marker'])
    m3 = (len(c_neg) == 0)
    P(f"  PC-M3 NEGATIVE control: a marker that does not exist gives "
      f"{len(c_neg)} boundaries (MUST be 0) : {'PASS' if m3 else 'FAIL'}")
    ok &= m3

    # ---- PC-S1: the STAGE rule reproduces WAVE 5's FRONT-END / CHAINABLE
    #      partition, which WAVE 5 derived from the NETLIST copy census and
    #      this derives from the SOURCE.  Two routes, one answer.
    sig2sec, chain = build_stagemap(None)
    P("  PC-S1 the STAGE rule reproduces WAVE 5 §5(a)'s FRONT-END / CHAINABLE")
    P("        partition, derived here from the SOURCE and there from the")
    P("        NETLIST copy census")
    s1 = True
    for nm in W5_CHAINABLE:
        st = classify(f'emu|system_large|u_core|u_eu|{nm}~7|combout', sig2sec, chain)
        good = (st == 'CHAIN')
        s1 &= good
        P(f"        CHAINABLE {nm:18s} -> {st:34s} {'ok' if good else '*** FAIL ***'}")
    for nm in W5_FRONTEND:
        st = classify(f'emu|system_large|u_core|u_eu|{nm}~7|combout', sig2sec, chain)
        good = (st not in ('CHAIN', 'UNMAPPED'))
        s1 &= good
        P(f"        FRONT-END {nm:18s} -> {st:34s} {'ok' if good else '*** FAIL ***'}")
    P(f"        PC-S1 : {'PASS' if s1 else 'FAIL'}")
    ok &= s1

    # ---- PC-S2: the stage map can say NO
    st = classify('emu|system_large|u_core|u_eu|zzz_no_such_signal~3|combout',
                  sig2sec, chain)
    s2 = (st == 'UNMAPPED')
    P(f"  PC-S2 NEGATIVE control: an invented signal classifies {st} "
      f"(MUST be UNMAPPED) : {'PASS' if s2 else 'FAIL'}")
    ok &= s2

    # ---- PC-S3: the hierarchy overrides fire
    s3 = (classify('emu|system_large|u_core|u_biu|q_ripe_lead_n~4|combout',
                   sig2sec, chain) == 'BIU' and
          classify('emu|system_large|u_core|u_eu|u_ucrom|ucrom~754|combout',
                   sig2sec, chain) == 'ROMHEAD' and
          classify('emu|system_large|nec_bus|ad_in_q[3]', sig2sec, chain)
          == 'OUTSIDE')
    P(f"  PC-S3 hierarchy overrides (BIU / ROMHEAD / OUTSIDE) : "
      f"{'PASS' if s3 else 'FAIL'}")
    ok &= s3

    P("")
    P(f"  === SOURCE-MAP CONTROLS: "
      f"{'ALL PASS' if ok else '*** FAILED -- NOTHING MAY BE QUOTED ***'} ===")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('cmd', choices=['controls', 'markers', 'stages', 'dump'])
    ap.add_argument('--rev', default=None)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    if a.cmd == 'controls':
        return 0 if controls() else 3
    if a.cmd == 'markers':
        mk, d = derive_markers(a.rev, verbose=True)
        print(' '.join(mk))
        return 0
    if a.cmd == 'stages':
        sig2sec, chain = build_stagemap(a.rev)
        secs = {}
        for s, v in sig2sec.items():
            for t in v:
                secs.setdefault(t, []).append(s)
        for t in sorted(secs):
            print(f"{len(secs[t]):5d}  {t}")
        print(f"{len(chain):5d}  CHAIN (arm bodies)")
        return 0
    if a.cmd == 'dump':
        if not controls():
            return 3
        mk, d = derive_markers(None)
        sig2sec, chain = build_stagemap(None)
        json.dump({'markers': mk, 'derivation': d,
                   'sig2sec': {k: sorted(v) for k, v in sig2sec.items()},
                   'chain_assigned': sorted(chain)},
                  open(a.out, 'w'), indent=1)
        print(f"\n  written to {a.out}")
        return 0


if __name__ == '__main__':
    sys.exit(main())
