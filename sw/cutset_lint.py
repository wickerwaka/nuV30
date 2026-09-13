#!/usr/bin/env python3
"""cutset_lint -- THE CUT SET'S OWN FALSIFIER  (WAVE 4, 2026-09-08).

WHY IT EXISTS
-------------
WAVE 2 built a `ce_half` shadow of the EU's loop-carried `_n` set, landed it
bit-exact, deleted the SDC exception -- and came back RED at 22.78 MHz with
**103 arrival points on the binding path of which ZERO named the shadow**
(`docs/notes/phase_split_landing_results_2026-09-08.md` §11.6).  The reason was
in the SOURCE, not in the netlist: `row` and its field decodes are module-level
WIRES, and the chain body read them LIVE.  The register was placed BESIDE the
loop, not ACROSS it.  **IT WAS NOT A CUT SET.**

A cut set is a claim about what stage 2 CANNOT REACH, and that claim is exactly
the kind a comment cannot hold -- `sw/r7_lint.py` exists for the same reason and
is this file's model.  So:

    THE INVARIANT.  The EU's next-state block -- and every file it includes --
    references NO module-level combinational wire of `v30u_eu.sv`.  Everything
    it used to read that way is now a `reg` whose ONLY assignment before THE
    CUT is `<x> = s1w_<x>`, and which crosses to stage 2 through the shadow.

That is the complete-by-construction proof.  A stage-2 read of a pre-cut value
has to name an `s1w_` wire, and clause X2 forbids it; a NEW module-level wire
read by the block trips X4 even if nobody thought about the phase split.

CHECKS (exit 0 PASS / 1 violation / 2 could-not-run):

  X1  the split is present: the pack, the unpack and `S1W` exist.  If not,
      exit 2 -- a lint that passes on a tree without the mechanism passes
      VACUOUSLY, and this file says so instead.
  X2  NO `s1w_` identifier appears anywhere in the next-state block -- NOR IN
      ANY `.svh` IT INCLUDES -- except on the alias lines at the head of
      STAGE 1.  ⚠ The include half was added 2026-09-09: without it a bypass
      spliced into `v30u_eu_step.svh`, which is where the chain body lives and
      where WAVE 2's defect was, was invisible to X2 and only X4 caught it.
  X3  every aliased name is aliased EXACTLY ONCE, and every alias stands
      BEFORE THE CUT (`s1_bus = {`).
  X4  **COMPLETENESS.**  The block, plus every `.svh` it includes, names ZERO
      MODULE-LEVEL COMBINATIONAL VALUES of `v30u_eu.sv`.  This is the clause
      that fires on a re-introduced bypass.
      ⚠ **"COMBINATIONAL VALUE" IS NOT "WIRE", AND THE DIFFERENCE COST WAVE 4
      ITS FIRST CUT.**  This clause used to read *"continuous-assignment
      targets"*, i.e. `wire x = ...` and `assign x = ...`.  `v30u_eu.sv` has SIX
      OTHER combinational `always @*` blocks -- the ALU, the BCD unit, the
      iterative stepper, the Source1 and Source2 selects and the reset function
      -- and every one of them drives module-level `reg`s that are exactly as
      combinational and exactly as pre-cut as a wire.  The first landed cut set
      shadowed the 70 wires, PASSED this clause, and the netlist then showed the
      binding arc running `modrm_reg -> opc_sel -> ... -> s1_val/it_val -> v1 ->
      the chain -> opc_base` with **107 arrival points and ZERO naming the
      shadow** -- WAVE 2's signature, one layer in.  The set is now BOTH kinds.
      A name the preload assigns is the block's OWN scratch, not a pre-cut
      value, and is excluded by that rule and not by a list.
  X5  every aliased name is a member of the pack list (so it actually crosses).
  X6  no aliased wire's cone reaches a LIVE input -- `r7_lint`'s own set: the
      three asynchronous pins, the declared live-`READY` carrier and its data
      twin, and the two declared UNRESOLVED carriers.  A pin may not be
      captured on `ce_half`.

WHAT IT DOES **NOT** ESTABLISH
-----------------------------
It is a STRUCTURAL check.  It says the cut set is complete; it says NOTHING
about whether the two stages are balanced or whether the design closes timing.
Only Quartus can say that (`sw/quartus_gate.py`, G6).
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UC = ROOT / "hdl/rtl/ucore"
EU = UC / "v30u_eu.sv"

LIVE = {"pin_int", "pin_nmi", "pin_poll_n",
        "eu_rd_edge", "eu_rd_edge_d",
        "eu_slot_busy_n", "q_ripe_lead_n"}

# ⚠ 2026-09-09 (WAVE 9) -- THE INCLUDE LIST IS NO LONGER A LIST.
# It was a HARD-CODED nine names, and WAVE 7 then moved the nine chain-arm
# bodies into `v30u_eu_arm_<state>.svh` -- files this list did not name, i.e.
# X2 and X4 would have scanned RIGHT PAST the chain body on the flattened
# tree and passed VACUOUSLY.  That is A-1's failure shape exactly (a set
# derived from a list instead of from the RTL), so the list is DERIVED: the
# TRANSITIVE CLOSURE of the next-state block's own `` `include ``s, computed
# by `block_includes()` below.  A file that appears tomorrow is scanned
# tomorrow, with nobody having to remember.
def block_includes(block_text, uc):
    """transitive closure of `` `include "x" `` starting from block_text"""
    seen, out = set(), []
    frontier = re.findall(r'`include\s+"([^"]+)"', block_text)
    while frontier:
        f = frontier.pop(0)
        if f in seen:
            continue
        seen.add(f)
        pth = uc / f
        if not pth.exists():
            continue
        out.append(f)
        t = nocomment(pth.read_text())
        frontier += re.findall(r'`include\s+"([^"]+)"', t)
    return out

KEYWORDS = set("""begin end if else case endcase for while default posedge negedge
wire reg logic assign always always_comb always_ff input output inout module
endmodule function endfunction task endtask automatic localparam parameter
integer genvar signed unsigned int bit byte return void typedef enum struct
packed const import package endpackage generate endgenerate initial final
disable fork join unique priority inside with this super null static""".split())


def nocomment(t):
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)
    return re.sub(r"//[^\n]*", "", t)


def idents(t):
    return {m.group(1) for m in re.finditer(r"(?<![\w'`$.])([A-Za-z_]\w*)", t)
            if m.group(1) not in KEYWORDS}


def main():
    raw = EU.read_text()
    lines = raw.split("\n")
    src = nocomment(raw)
    bad = []

    # --- X1 ---------------------------------------------------------------
    if "s1_bus = {" not in src or "= s1q;" not in src or "S1W" not in src:
        print("  the phase split is NOT IN THIS TREE -- no `s1_bus = {...}`, no\n"
              "  `{...} = s1q`.  This lint has nothing to check and says so rather\n"
              "  than passing: **exit 2, COULD NOT RUN**, never exit 0.")
        print("\n=== cutset_lint: COULD NOT RUN (the split is absent)")
        return 2

    # --- locate the next-state block --------------------------------------
    starts = [i for i, l in enumerate(lines) if l.startswith("always @* begin")]
    # ⚠ 2026-09-09 (WAVE 9): the anchor was `for (chain = 0;`, which WAVE 7
    # DELETED -- and which survives on this tree ONLY AS A COMMENT, so an
    # anchor that searched the raw text would have silently keyed on prose.
    # The anchor is now the chain pass's own entry, and its absence is a
    # REFUSAL and never a pass.
    anch = [i for i, l in enumerate(lines)
            if 'include "v30u_eu_step.svh"' in nocomment(l)]
    if not anch:
        print("  cutset_lint: COULD NOT RUN -- no `include \"v30u_eu_step.svh\"` "
              "in v30u_eu.sv; the next-state block cannot be located.")
        return 2
    b0 = max(s for s in starts if s < anch[0])
    b1 = next(i for i in range(b0 + 1, len(lines)) if lines[i].rstrip() == "end")
    block_raw = "\n".join(lines[b0:b1 + 1])
    block = nocomment(block_raw)
    cut = block.index("s1_bus = {")
    INCLUDES = block_includes(block, UC)
    print("  includes closed : %d  %s" % (len(INCLUDES), sorted(INCLUDES)))

    # --- the aliases -------------------------------------------------------
    alias = re.findall(r"^\s*(\w+)\s*=\s*s1w_(\w+)\s*;\s*$", block, re.M)
    names = []
    for lhs, rhs in alias:
        if lhs != rhs:
            bad.append("X3: alias `%s = s1w_%s;` -- the two names must be the "
                       "same name, or the cut set is not checkable by eye" % (lhs, rhs))
        names.append(lhs)
    if len(set(names)) != len(names):
        dup = sorted({n for n in names if names.count(n) > 1})
        bad.append("X3: aliased more than once: %s" % dup)
    for m in re.finditer(r"^\s*(\w+)\s*=\s*s1w_(\w+)\s*;\s*$", block, re.M):
        if m.start() > cut:
            bad.append("X3: the alias for `%s` stands AFTER THE CUT" % m.group(1))
    print("  cut-set members : %d" % len(names))

    # --- X2 ----------------------------------------------------------------
    stray = []
    for i, l in enumerate(lines[b0:b1 + 1], start=b0 + 1):
        code = nocomment(l)
        if "s1w_" not in code:
            continue
        if re.match(r"^\s*\w+\s*=\s*s1w_\w+\s*;\s*$", code):
            continue
        stray.append((i, l.strip()[:90]))
    # ...AND THE INCLUDES, WHICH IS WHERE THE CHAIN BODY ACTUALLY LIVES.
    # X2 used to scan only `v30u_eu.sv`'s own lines, so a bypass spliced into
    # `v30u_eu_step.svh` -- the most likely place for one, and the file WAVE 2's
    # defect was in -- was invisible to it and only X4 caught it.  MEASURED by
    # C-9 case B, which reported X2 "DID NOT FIRE" on exactly that probe.
    # No `.svh` may name `s1w_` at all: the aliases are in `v30u_eu.sv`.
    for inc in INCLUDES:
        pth = UC / inc
        if not pth.exists():
            continue
        for i, l in enumerate(nocomment(pth.read_text()).split("\n"), start=1):
            if "s1w_" in l:
                stray.append(("%s:%d" % (inc, i), l.strip()[:90]))
    if stray:
        for i, l in stray[:12]:
            bad.append("X2: `s1w_` named inside the next-state block at %s: %s" % (i, l))
    print("  s1w_ in block   : %d (must be 0 outside the alias lines)" % len(stray))

    # --- module-level COMBINATIONAL VALUES ---------------------------------
    # (a) continuous assignments, and (b) the module-level `reg`s driven by the
    # OTHER combinational `always @*` blocks.  (b) is not a refinement: it is
    # where WAVE 4's first cut set leaked (see X4's note above).
    stmts, cur = [], []
    for ch in src:
        cur.append(ch)
        if ch == ';':
            stmts.append("".join(cur)); cur = []
    decls, deps = {}, {}
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
            decls[m.group(3)] = m.group(4)
            continue
        m = re.match(r"^(?:.*\b)?assign\s+([A-Za-z_]\w*)\s*=\s*(.*);$", s3)
        if m and m.group(1) in decls:
            decls[m.group(1)] = m.group(2)
    deps = {n: idents(e or "") for n, e in decls.items()}

    # (b) -- every module-level `reg` assigned in a combinational `always @*`
    # block OTHER than the next-state one.  A name the PRELOAD assigns is the
    # next-state block's own mirror or scratch and is NOT a pre-cut value; that
    # is the rule that excludes `rep_chained`, and it is a rule and not a list.
    modregs = {}
    for m in re.finditer(r"^reg\s+(?:signed\s+)?(\[[^\]]*\]\s*)?(.*?);", src, re.M):
        for nm in m.group(2).split(","):
            mm = re.match(r"\s*(\w+)", nm)
            if mm:
                modregs[mm.group(1)] = True
    preload_assigned = set()
    pp = UC / "v30u_eu_preload.svh"
    if pp.exists():
        for m in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*=(?!=)",
                             nocomment(pp.read_text())):
            preload_assigned.add(m.group(1))
    comb_starts = [i for i, l in enumerate(lines) if l.startswith("always @* begin")]
    for st in comb_starts:
        if st == b0:
            continue
        en = next(i for i in range(st + 1, len(lines)) if lines[i].rstrip() == "end")
        body = nocomment("\n".join(lines[st:en + 1]))
        for m in re.finditer(r"(?<![\w.])([A-Za-z_]\w*)\s*(?:\[[^\]]*\])?\s*=(?!=)", body):
            n = m.group(1)
            if n in modregs and n not in preload_assigned and n not in decls:
                decls[n] = None
                deps[n] = set()

    # --- X4 : COMPLETENESS -------------------------------------------------
    # THE ALIAS LINES ARE THE ONE PLACE THE CUT IS ALLOWED TO NAME THE WIRE,
    # and they are excluded HERE rather than by a name pattern: X2 has already
    # proved that every `s1w_` in the block is on one of them.
    region = "\n".join(l for l in block.split("\n")
                       if not re.match(r"^\s*\w+\s*=\s*s1w_\w+\s*;\s*$", l))
    for inc in INCLUDES:
        p = UC / inc
        if p.exists():
            region += "\n" + nocomment(p.read_text())
    read = idents(region)
    leaked = sorted(n for n in decls if n in read)
    print("  module combinational values the block names : %d (must be 0)" % len(leaked))
    if leaked:
        bad.append("X4: the next-state block reads module-level COMBINATIONAL "
                   "VALUE(S) DIRECTLY -- a wire, or a `reg` driven by one of the "
                   "module's other `always @*` blocks -- "
                   "so they are NOT in the cut set and stage 2 bypasses the shadow "
                   "exactly as WAVE 2 did: %s" % leaked[:12])

    # --- X5 ----------------------------------------------------------------
    pack = re.search(r"s1_bus\s*=\s*\{(.*?)\};", src, re.S)
    members = {m.strip() for m in pack.group(1).split(",") if m.strip()}
    missing = [n for n in names if n not in members]
    if missing:
        bad.append("X5: aliased but NOT in the pack list (so it never crosses): %s" % missing)

    # --- X6 ----------------------------------------------------------------
    tainted = set()
    changed = True
    while changed:
        changed = False
        for n, d in deps.items():
            if n not in tainted and (d & (LIVE | tainted)):
                tainted.add(n); changed = True
    hot = [n for n in names if ("s1w_" + n) in tainted]
    print("  live-tainted members : %s" % (hot or "none"))
    if hot:
        bad.append("X6: the cone of %s reaches a LIVE input.  A pin may not be "
                   "captured on `ce_half` -- move the term to stage 2 (block (g)), "
                   "as `poll_pipe_n` was." % hot)

    for b in bad:
        print("  VIOLATION " + b)
    ok = not bad
    print("\n=== cutset_lint: %s   (%d members / %d violations)"
          % ("PASS" if ok else "FAIL", len(names), len(bad)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
