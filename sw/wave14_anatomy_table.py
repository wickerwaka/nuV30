#!/usr/bin/env python3
"""WAVE 14 -- assemble the STA anatomy of every arm into ONE table.

It reads the artifacts the driver left beside each sweep and reports, per
(arm, configuration):

  * the worst `ce -> ce` arc: slack, logic levels, DATA DELAY (the ns figure
    WAVE 9's 20.235 / 27.922 / 31.959 are in), and whether it is an EU -> BIU ->
    EU round trip with the first and last BIU node NAMED;
  * **STAGE 1 (`* -> s1q`) and STAGE 2 (`s1q -> *`) worst data delay** -- P-3's
    evidence.  A STAGE BOUNDARY IS A REGISTER: the arms add none, so no stage
    can be subdivided, and these two rows are the measurement that says so;
  * the top-200 classification STAGE 1 / STAGE 2 / NEITHER;
  * POPULATION A's round-trip fraction and mean span (WAVE 10's census);
  * **every positive control's verdict, printed FIRST** (P-1).

⚠ IT PARSES COMMITTED ARTIFACT TEXT.  It computes no digest of its own and it
re-runs no analysis: every number below is a line of a named file.

⚠ `sta_cutset_diag.tcl`'s OWN "-through the destination's D pin" control reads
**0 pins** on this design, and that is NOT a new defect: the binding path ends
in an **M10K PORT REGISTER, which exposes no pin objects at all** (WAVE 10 §1.1
item 2, which is why WAVE 10 split that control into W5a/W5b).  Its STAGE 1 /
STAGE 2 / classification figures come from `-from`/`-to` REGISTER COLLECTIONS
and do not use `-through` at all, so they do not rest on it -- and the REPAIRED
control (PC-W5a via `get_registers`, PC-W5b on both write-pin forms) runs on the
SAME netlist in `sta_biu_roundtrip.tcl` and is reported here beside it.

usage: wave14_anatomy_table.py DIR [DIR ...]      (each DIR = one arm's outdir)
"""
import os
import re
import sys


def grab(path):
    if not os.path.exists(path):
        return None
    return open(path, errors="replace").read()


def diag(txt):
    o = {}
    m = re.search(r"\$v30u_ce (\d+)\s+shadow registers matching \|s1q\* : (\d+)", txt)
    if m:
        o["v30u_ce"], o["shadow"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"worst ce->ce.*?slack :\s*([-+0-9.]+)\s+logic levels (\d+)\s+"
                  r"data delay ([0-9.]+)", txt, re.S)
    if m:
        o["worst_slack"], o["worst_lv"], o["worst_ns"] = \
            float(m.group(1)), int(m.group(2)), float(m.group(3))
    m = re.search(r"arrival points: (\d+)\s+of which name \|s1q : (\d+)", txt)
    if m:
        o["points"], o["s1q_on_worst"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"live in v30u_biu : (\d+)\s+v30u_eu : (\d+)\s+elsewhere : (\d+)", txt)
    if m:
        o["biu_on_worst"] = int(m.group(1))
    o["roundtrip_on_worst"] = "COMBINATIONAL ROUND TRIP" in txt
    m = re.search(r"first BIU node : (\S+)", txt)
    if m:
        o["first_biu"] = m.group(1)
    m = re.search(r"last  BIU node : (\S+)", txt)
    if m:
        o["last_biu"] = m.group(1)
    m = re.search(r"positive control: -through the destination's own D pin "
                  r"resolves (\d+) pin", txt)
    if m:
        o["diag_pc_pins"] = int(m.group(1))
    for tag, key in (("STAGE 1  \\(\\* -> s1q\\)", "n1"),
                     ("STAGE 2  \\(s1q -> \\*\\)", "n2"),
                     ("NEITHER  \\(WAVE 2's signature\\)", "n0")):
        m = re.search(tag + r"\s+count (\d+)", txt)
        if m:
            o[key] = int(m.group(1))
    for tag, key in (("STAGE 1 \\(anything -> s1q\\), worst:", "s1"),
                     ("STAGE 2 \\(s1q -> anything\\), worst:", "s2")):
        m = re.search(tag + r".*?slack :\s*([-+0-9.]+)\s+logic levels (\d+)\s+"
                      r"data delay ([0-9.]+)", txt, re.S)
        o[key] = (float(m.group(1)), int(m.group(2)), float(m.group(3))) if m else None
    return o


def rt(txt):
    o = {}
    o["controls"] = "=== CONTROLS: ALL PASS ===" in txt
    o["ax"] = "AX CONTROLS: ALL PASS" in txt
    m = re.search(r"PC-W1 RESOLVER.*?get_pins\s+(\d+) -> paths (\d+).*?"
                  r"get_nodes (\d+) -> paths (\d+)", txt, re.S)
    if m:
        o["pcw1"] = tuple(int(x) for x in m.groups())
    m = re.search(r"BIU nodes on a path forced through ONE NAMED PIN : (\d+)", txt)
    if m:
        o["pcw2"] = int(m.group(1))
    m = re.search(r"the pin that answered : (\S+)", txt)
    if m:
        o["pcw2_pin"] = m.group(1)
    m = re.search(r"PC-W4 BULK\s+the BULK -through of (\d+) pins yields : (-?\d+)", txt)
    if m:
        o["pcw4"] = (int(m.group(1)), int(m.group(2)))
    m = re.search(r"=== B\. THE WORST ce->ce ARC ===.*?slack\s+([-+0-9.]+)\s+levels (\d+)\s+"
                  r"data delay ([0-9.]+).*?BIU nodes \(all points\) (\d+)\s+"
                  r"\(data section\) (\d+)\s+q_ripe_lead_n points (\d+)", txt, re.S)
    if m:
        o["worst"] = (float(m.group(1)), int(m.group(2)), float(m.group(3)),
                      int(m.group(4)), int(m.group(5)), int(m.group(6)))
    m = re.search(r"--- POPULATION A_topN ---\s*\n\s*paths scanned\s+: (\d+).*?"
                  r"carrying the round trip \(all points\)\s+: (\d+).*?"
                  r"mean span, WAVE 9 convention \(ns\)\s+: ([0-9.]+)", txt, re.S)
    if m:
        o["popA"] = (int(m.group(1)), int(m.group(2)), float(m.group(3)))
    return o


def main():
    print("=" * 100)
    print("P-1  THE POSITIVE CONTROLS, REPORTED FIRST")
    print("  leg                     sta_biu_roundtrip controls   AX   PC-W1 pins->paths / "
          "nodes->paths   PC-W2   PC-W4 bulk")
    legs = []
    for d in sys.argv[1:]:
        for cfg in ("control", "retention"):
            td = grab(os.path.join(d, f"cutset_diag_{cfg}.txt"))
            tr = grab(os.path.join(d, f"roundtrip_{cfg}.txt"))
            if td is None and tr is None:
                continue
            legs.append((os.path.basename(d.rstrip("/")), cfg,
                         diag(td) if td else {}, rt(tr) if tr else {}))
    for name, cfg, D, R in legs:
        w1 = R.get("pcw1")
        print(f"  {name+'/'+cfg:<22}  {'ALL PASS' if R.get('controls') else '*** NOT ALL PASS ***':<26} "
              f"{'PASS' if R.get('ax') else '****':<4} "
              f"{(str(w1[0])+'->'+str(w1[1])+' / '+str(w1[2])+'->'+str(w1[3])) if w1 else '-':<28} "
              f"{str(R.get('pcw2')):<7} {str(R.get('pcw4'))}")
    print("  ⚠ PC-W4 is the KNOWN-WRONG bulk form, printed and never relied on: a bulk figure")
    print("    BELOW PC-W2's single-pin figure is `-through` accepted-and-ignored.")
    print("  ⚠ sta_cutset_diag's OWN D-pin control reads: " +
          ", ".join(f"{n}/{c} {D.get('diag_pc_pins')}" for n, c, D, _ in legs))
    print("    0 is the M10K PORT REGISTER finding (WAVE 10 §1.1 item 2), not a new defect;")
    print("    its STAGE figures use -from/-to collections and no -through at all.")

    print("=" * 100)
    print("P-3  THE ANATOMY.  A STAGE BOUNDARY IS A REGISTER; NO ARM ADDS ONE.")
    print("  leg                     $v30u_ce  s1q   worst ce->ce ns (lv)   RT?  BIU   "
          "STAGE1 ns (lv)   STAGE2 ns (lv)   top200 S1/S2/NEITHER   POP-A rt/n  span")
    for name, cfg, D, R in legs:
        s1, s2 = D.get("s1"), D.get("s2")
        pa = R.get("popA")
        print(f"  {name+'/'+cfg:<22}  {str(D.get('v30u_ce')):>8}  {str(D.get('shadow')):>4}   "
              f"{str(D.get('worst_ns')):>7} ({str(D.get('worst_lv')):>2})        "
              f"{'YES' if D.get('roundtrip_on_worst') else 'no ':<4} "
              f"{str(D.get('biu_on_worst')):>3}   "
              f"{(f'{s1[2]:7.3f} ({s1[1]:2d})' if s1 else '      -    '):<16} "
              f"{(f'{s2[2]:7.3f} ({s2[1]:2d})' if s2 else '      -    '):<16} "
              f"{str(D.get('n1'))+'/'+str(D.get('n2'))+'/'+str(D.get('n0')):>18}   "
              f"{(str(pa[1])+'/'+str(pa[0])) if pa else '-':>9}  "
              f"{(f'{pa[2]:.3f}' if pa else '-'):>6}")
    print("  RT? = the worst ce->ce arc is an EU -> BIU -> EU combinational round trip")
    print("  first/last BIU node on the worst arc:")
    for name, cfg, D, R in legs:
        if D.get("first_biu"):
            print(f"    {name+'/'+cfg:<22} {D['first_biu']}  ->  {D['last_biu']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
