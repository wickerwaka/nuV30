#!/usr/bin/env python3
"""THE PHASE SPLIT'S OWN FALSIFIER  (WAVE 2, 2026-09-08).

`v30u_eu.sv` carries the shadow's membership list TWICE -- once as the pack
`s1_bus = { ... };` at THE CUT and once as the unpack `{ ... } = s1q;` that
opens STAGE 2.  The whole of the correctness argument is that those two lists
are the SAME LIST, and the whole of `ss_flop_whitelist_ucore.txt`'s DERIVED
bar is that the derivation is CHECKABLE BY EYE IN ONE PLACE.  A comment is not
a gate, so this is the gate.

CHECKS (exit 0 PASS / 1 violation / 2 could-not-run):

  L1  the pack list and the unpack list exist, exactly once each.
  L2  they are CHARACTER-IDENTICAL after whitespace normalisation.
  L3  their summed DECLARED widths equal `S1W` in the same file.
  L4  every member is declared in `v30u_eu.sv` (no typo silently widening a
      concatenation with an implicit net).
  L5  `v30u_eu_preload.svh` is included EXACTLY TWICE -- once at the head of
      the next-state block and once at the head of its `ss_we` arm, which is
      what makes that arm byte-identical to the pre-split one -- and the
      second inclusion stands IMMEDIATELY BEFORE the `ss_write` include.
  L6  the shadow's commit condition is `(ss_we || srst || ce_half)`: `ce_half`
      because that is the capture edge, `srst` because it is what makes the
      shadow current at a run's FIRST `ce`, and `ss_we` because the resume
      drain edge is where it is re-derived from the restored register file.
  L7  NO LIVE INPUT IS IN STAGE 1 (P-11).  `pin_int`, `pin_nmi`, `pin_poll_n`,
      `eu_rd_edge`, `eu_rd_edge_d`, `eu_slot_busy_n` and `q_ripe_lead_n` --
      the module's asynchronous inputs plus `r7_lint`'s one declared exception
      and its two declared unresolved carriers -- may not appear anywhere
      between the preload and THE CUT.
"""
import re, sys, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
EU   = os.path.join(ROOT, 'hdl', 'rtl', 'ucore', 'v30u_eu.sv')

LIVE = ["pin_int", "pin_nmi", "pin_poll_n", "eu_rd_edge", "eu_rd_edge_d",
        "eu_slot_busy_n", "q_ripe_lead_n"]

def norm(t):
    return re.sub(r'\s+', ' ', t).strip()

def main():
    src = open(EU).read()
    bad = []

    # --- L1 -----------------------------------------------------------------
    packs   = re.findall(r's1_bus\s*=\s*\{(.*?)\};', src, re.S)
    unpacks = re.findall(r'\{([^{}]*?)\}\s*=\s*s1q\s*;', src, re.S)
    print("  pack sites   : %d" % len(packs))
    print("  unpack sites : %d" % len(unpacks))
    if len(packs) != 1:
        bad.append("L1: expected exactly 1 `s1_bus = {...};`, found %d" % len(packs))
    if len(unpacks) != 1:
        bad.append("L1: expected exactly 1 `{...} = s1q;`, found %d" % len(unpacks))
    if bad:
        for b in bad: print("  VIOLATION", b)
        print("\n=== phase_split_lint: FAIL")
        return 1

    p, u = norm(packs[0]), norm(unpacks[0])
    # --- L2 -----------------------------------------------------------------
    if p != u:
        bad.append("L2: the pack and unpack lists DIFFER.\n    pack   %s\n    unpack %s" % (p, u))
    members = [m.strip() for m in p.split(',') if m.strip()]
    print("  members      : %d" % len(members))

    # --- widths -------------------------------------------------------------
    w = {}
    for l in src.split('\n'):
        m = re.match(r'^\s*(?:reg|logic)\s*(?:signed\s*)?(\[([^\]]+)\])?\s+(.*?);', l)
        if not m:
            continue
        rng = m.group(2)
        base = 1
        if rng:
            mm = re.match(r'\s*(\d+)\s*:\s*(\d+)\s*$', rng)
            if not mm:
                continue
            base = abs(int(mm.group(1)) - int(mm.group(2))) + 1
        for n in m.group(3).split(','):
            n = n.strip()
            am = re.match(r'(\w+)\s*\[\s*\d+\s*:\s*\d+\s*\]$', n)
            nm = (am.group(1) if am else (re.match(r'(\w+)', n).group(1)
                                          if re.match(r'(\w+)', n) else None))
            if nm:
                w[nm] = base

    total = 0
    for mem in members:
        base = re.match(r'(\w+)', mem).group(1)
        if base not in w:
            bad.append("L4: member `%s` is not declared in v30u_eu.sv" % mem)
            continue
        total += w[base]
    sm = re.search(r'localparam\s+int\s+S1W\s*=\s*(\d+)\s*;', src)
    if not sm:
        bad.append("L3: no `localparam int S1W = <n>;` in v30u_eu.sv")
    else:
        s1w = int(sm.group(1))
        print("  summed width : %d   S1W = %d" % (total, s1w))
        if total != s1w:
            bad.append("L3: the member list sums to %d bits, S1W says %d" % (total, s1w))

    # --- L5 -----------------------------------------------------------------
    inc = [m.start() for m in re.finditer(r'`include "v30u_eu_preload\.svh"', src)]
    print("  preload incl : %d" % len(inc))
    if len(inc) != 2:
        bad.append("L5: `v30u_eu_preload.svh` must be included EXACTLY twice, found %d" % len(inc))
    else:
        tail = src[inc[1]:inc[1] + 400]
        if not re.match(r'`include "v30u_eu_preload\.svh"\s*\n\s*`include "v30u_eu_ss_write\.svh"', tail):
            bad.append("L5: the second preload include must stand IMMEDIATELY BEFORE "
                       "the ss_write include (it is what undoes stage 1 in the ss_we arm)")

    # --- L6 -----------------------------------------------------------------
    if not re.search(r'if\s*\(\s*ss_we\s*\|\|\s*srst\s*\|\|\s*ce_half\s*\)\s*s1q\s*<=\s*s1_bus\s*;', src):
        bad.append("L6: the shadow's commit condition is not `if (ss_we || srst || ce_half) s1q <= s1_bus;`")

    # --- L7 -----------------------------------------------------------------
    hi = src.index('`include "v30u_eu_preload.svh"')
    ci = src.index('s1_bus = {')
    stage1 = re.sub(r'//[^\n]*', '', src[hi:ci])
    hits = [s for s in LIVE if re.search(r'(?<![\w.])%s(?![\w])' % s, stage1)]
    print("  live-in-stage1: %s" % (hits or 'none'))
    if hits:
        bad.append("L7: LIVE input(s) %s appear in STAGE 1.  A pin may not be "
                   "captured on ce_half -- move the term to stage 2 (block (g)), "
                   "as `poll_pipe_n` was.  P-11." % hits)

    for b in bad:
        print("  VIOLATION " + b)
    ok = not bad
    print("\n=== phase_split_lint: %s   (%d members / %d bits / %d violations)"
          % ("PASS" if ok else "FAIL", len(members), total, len(bad)))
    return 0 if ok else 1

if __name__ == '__main__':
    sys.exit(main())
