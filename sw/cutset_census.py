#!/usr/bin/env python3
"""cutset_census -- WAVE 4's FIRST JOB, DONE FIRST AND BEFORE THE DESIGN.

Derives, FROM THE SOURCE, the two candidate crossing sets of the ce/ce_half
PHASE SPLIT DONE AS A CUT SET:

  (A) shadow `row` itself and re-do the row decode in stage 2;
  (B) shadow every module-level combinational wire of `v30u_eu` that the
      NEXT-STATE BLOCK reads and that is PHASE-STABLE (i.e. whose cone does not
      reach one of the module's live inputs), PLUS wave 2's loop-carried `_n`
      crossing set.

It reports the WIDTH of each, and the LIVE-TAINTED wires the next-state block
reads (which CANNOT be shadowed and therefore stay live -- they are stage-2
sources, and the lint must not demand they be shadowed).

THE LIVE SET is r7_lint's, not a guess: the three asynchronous pins plus the
ONE declared live-READY carrier (and its data twin) plus the TWO declared
UNRESOLVED carriers.

Usage: python3 sw/cutset_census.py [--verbose]
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UC = ROOT / "hdl/rtl/ucore"
EU = UC / "v30u_eu.sv"

# r7_lint's own two lists plus the module's asynchronous pins.
LIVE = {"pin_int", "pin_nmi", "pin_poll_n",
        "eu_rd_edge", "eu_rd_edge_d",
        "eu_slot_busy_n", "q_ripe_lead_n"}

KEYWORDS = set("""begin end if else case endcase for while default posedge negedge
wire reg logic assign always always_comb always_ff input output inout module
endmodule function endfunction task endtask automatic localparam parameter
integer genvar signed unsigned int bit byte return void typedef enum struct
packed const import package endpackage generate endgenerate initial final
disable fork join unique priority inside with this super null static
""".split())

def strip_comments(txt):
    txt = re.sub(r"/\*.*?\*/", " ", txt, flags=re.S)
    txt = re.sub(r"//[^\n]*", "", txt)
    return txt

def idents(expr):
    out = set()
    for m in re.finditer(r"(?<![\w'`$.])([A-Za-z_]\w*)", expr):
        n = m.group(1)
        if n in KEYWORDS:
            continue
        out.add(n)
    return out

def main():
    verbose = "--verbose" in sys.argv
    raw = EU.read_text()
    src = strip_comments(raw)
    lines_raw = raw.split("\n")

    # ---- 1. module-level continuous assignments -------------------------
    # `wire [a:b] name = expr;`  /  `assign name = expr;`  /  `wire [a:b] name;`
    body = src
    decls = {}      # name -> (width, expr or None)
    order = []
    # join continuations: statements end at ';'
    stmts = []
    depth_par = 0
    cur = []
    for ch in body:
        cur.append(ch)
        if ch == ';':
            stmts.append("".join(cur)); cur = []
    for s in stmts:
        s2 = " ".join(s.split())
        # ⚠ STRIP THE BLOCK-CLOSING KEYWORDS FIRST.  Statements are split on
        # `;`, so the FIRST declaration after an `always`/`case`/`function`
        # block begins with that block's `end` / `endcase` tokens, and a bare
        # `startswith("wire")` test drops it.  `sigma` -- the ALU's own result
        # rail, the first `wire` after the iterative stepper's `endcase end` --
        # was invisible to this parser for exactly that reason (measured
        # 2026-09-09; see the WAVE 4 results document).
        s3 = re.sub(r"^(?:\s*\b(?:end|endcase|endfunction|endtask|endgenerate|"
                    r"begin|else|endmodule)\b)+\s*", "", s2)
        m = re.match(r"^(?:.*\b)?(wire|logic)\s*(\[[^\]]*\])?\s+([A-Za-z_]\w*)\s*(?:=\s*(.*))?;$", s3)
        if m and s3.lstrip().startswith(("wire", "logic")):
            w = m.group(2); nm = m.group(3); ex = m.group(4)
            decls[nm] = (w, ex)
            order.append(nm)
            continue
        m = re.match(r"^(?:.*\b)?assign\s+([A-Za-z_]\w*)\s*=\s*(.*);$", s3)
        if m:
            nm, ex = m.group(1), m.group(2)
            if nm in decls:
                decls[nm] = (decls[nm][0], ex)
            continue

    # ---- 2. widths ------------------------------------------------------
    LP = {}
    for m in re.finditer(r"localparam\s+(?:\w+\s+)?([A-Za-z_]\w*)\s*=\s*([^,;]+)", src):
        LP[m.group(1)] = m.group(2).strip()
    def width(w):
        if w is None:
            return 1
        m = re.match(r"\[\s*([^:]+):\s*([^\]]+)\]", w)
        if not m: return 1
        def ev(e):
            e = e.strip()
            for k, v in LP.items():
                e = re.sub(r"\b" + k + r"\b", "(" + v + ")", e)
            e = re.sub(r"\b\d+'[dhb]?([0-9a-fA-F]+)", r"\1", e)
            try: return int(eval(e))
            except Exception: return None
        a, b = ev(m.group(1)), ev(m.group(2))
        if a is None or b is None: return None
        return abs(a - b) + 1

    # ---- 3. taint closure ----------------------------------------------
    deps = {n: (idents(e) if e else set()) for n, (w, e) in decls.items()}
    tainted = set()
    changed = True
    while changed:
        changed = False
        for n, d in deps.items():
            if n in tainted: continue
            if d & (LIVE | tainted):
                tainted.add(n); changed = True

    # ---- 4. what the NEXT-STATE BLOCK reads -----------------------------
    # region: the `always @* begin` whose body contains `for (chain`
    ai = None
    for i, l in enumerate(lines_raw):
        if l.startswith("always @* begin"):
            ai = i
    # find the one containing the chain loop
    starts = [i for i, l in enumerate(lines_raw) if l.startswith("always @* begin")]
    chain_line = [i for i, l in enumerate(lines_raw) if "for (chain = 0;" in l][0]
    start = max(s for s in starts if s < chain_line)
    # end = first line == "end" at column 0 after start
    end = next(i for i in range(start + 1, len(lines_raw)) if lines_raw[i].rstrip() == "end")
    region = strip_comments("\n".join(lines_raw[start:end + 1]))
    for inc in ["v30u_eu_step.svh", "v30u_eu_row.svh", "v30u_eu_cond.svh",
                "v30u_eu_1bl.svh", "v30u_eu_wd1.svh", "v30u_eu_poste.svh",
                "v30u_eu_iend_late.svh"]:
        region += "\n" + strip_comments((UC / inc).read_text())
    read = idents(region)

    # ⚠ AND THE MODULE-LEVEL `reg`s DRIVEN BY THE *OTHER* COMBINATIONAL
    # `always @*` BLOCKS.  They are exactly as combinational and exactly as
    # pre-cut as a wire, and WAVE 4's first cut set leaked through them: the
    # ALU (`sigma`/`ev_*`), the iterative stepper (`it_val`, `it_flags`, ...)
    # and the Source1 / Source2 selects (`s1_val`, `s2_val`, ...) are all of
    # this kind.  A name the PRELOAD assigns is the next-state block's own
    # mirror or scratch and is NOT a pre-cut value -- that rule, and not a
    # list, is what excludes `rep_chained`.
    modregs = {}
    for m in re.finditer(r"^reg\s+(?:signed\s+)?(\[[^\]]*\]\s*)?(.*?);", src, re.M):
        w = m.group(1)
        for nm in m.group(2).split(","):
            mm = re.match(r"\s*(\w+)", nm)
            if mm:
                modregs[mm.group(1)] = (w.strip() if w else None)
    preload_assigned = set()
    pp = UC / "v30u_eu_preload.svh"
    if pp.exists():
        for m in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*=(?!=)",
                             strip_comments(pp.read_text())):
            preload_assigned.add(m.group(1))
    for st in starts:
        if st == start:
            continue
        en = next(i for i in range(st + 1, len(lines_raw)) if lines_raw[i].rstrip() == "end")
        body = strip_comments("\n".join(lines_raw[st:en + 1]))
        for m in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*=(?!=)", body):
            n = m.group(1)
            if n in modregs and n not in preload_assigned and n not in decls:
                decls[n] = (modregs[n], None)
                deps[n] = set()
                order.append(n)

    ss_write = idents(strip_comments((UC / "v30u_eu_ss_write.svh").read_text()))

    clean = [n for n in order if n in read and n not in tainted]
    dirty = [n for n in order if n in read and n in tainted]

    tot = 0; unk = []
    for n in clean:
        w = width(decls[n][0])
        if w is None: unk.append(n)
        else: tot += w
    print(f"module-level wires declared      : {len(decls)}")
    print(f"  ...LIVE-TAINTED                : {len(tainted)}")
    print(f"read by the NEXT-STATE BLOCK     : {len([n for n in order if n in read])}")
    print()
    print(f"SHAPE (B) crossing wires (clean) : {len(clean)} names / {tot} bits"
          + (f"   [{len(unk)} width UNKNOWN: {unk}]" if unk else ""))
    print(f"SHAPE (B) + wave 2's `_n` set    : {tot} + 495 = {tot + 495} bits")
    print()
    rowd = decls.get('row') or decls.get('s1w_row')
    if rowd:
        print(f"SHAPE (A) `row` only             : {width(rowd[0])} bits"
              f"  (+ wave 2's 495 = {width(rowd[0]) + 495})")
    else:
        print("SHAPE (A) `row` only             : (no `row` net -- the cut is landed)")
    print()
    print(f"LIVE-TAINTED wires the block reads (STAGE-2 SOURCES, not shadowable): {len(dirty)}")
    for n in dirty:
        print(f"    {n:26s} <- {sorted((deps[n] & (LIVE|tainted)))[:6]}")
    if verbose:
        print("\nCLEAN crossing wires:")
        for n in clean:
            print(f"    {n:26s} {width(decls[n][0])}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
