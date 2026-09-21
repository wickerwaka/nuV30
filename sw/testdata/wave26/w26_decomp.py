#!/usr/bin/env python3
"""WAVE 26 read-only diagnostic: decompose the ucore's mod3-LEA result by
perturbing ONE register / ONE address at a time.  No RTL edit."""
import sys, tempfile
from pathlib import Path
SW = Path("/home/wickerwaka/src/nec_test/sw")
sys.path.insert(0, str(SW))
import lea_mod3_gate as g
import testimage as ti, fuzz_classify as fc
from tb_bootrun import run_boot

LEA = bytes([0x8D, 0xF7])

class R2(g.Runner):
    def dump2(self, body, overrides=None, pc=None):
        regs = dict(g.BASE); regs.update(overrides or {})
        regs["PS"] = 0x0000
        regs["PC"] = g.BODY_PC if pc is None else pc
        img, _ = ti.compose(regs=regs, instr=body, ram=[])
        rows = run_boot(bytes(img), g.CLOCKS, self.td, waits=0)
        d = fc.arch_dump(rows, len(rows))
        if d is None: raise g.Fail("no dump")
        return d

PRE = {
 "C3": bytes([0x90]),
 "M0": bytes([0x89,0x00]),
 "M4": bytes([0x89,0x04]),
 "M6": bytes([0x89,0x06,0x34,0x12]),
 "M7": bytes([0x89,0x07]),
}
VARY = [
 ("base",   {},               None),
 ("AW+1",   {"AW":0x1112},    None),
 ("BW+1",   {"BW":0x4445},    None),
 ("IX+1",   {"IX":0x7778},    None),
 ("IY+1",   {"IY":0x8889},    None),
 ("BP+1",   {"BP":0x6667},    None),
 ("PC+0x10",{},               g.BODY_PC+0x10),
]

with tempfile.TemporaryDirectory(dir=str(Path.home()/".cache"/"ucsimt-tmp")) as td:
    r = R2(td)
    print("%-4s " % "tag" + " ".join("%10s"%v[0] for v in VARY))
    for tag, pre in PRE.items():
        vals=[]
        for name, ov, pc in VARY:
            d = r.dump2(pre+LEA, ov, pc)
            vals.append(d["IX"])
        base=vals[0]
        print("%-4s " % tag + " ".join("%10s"%("%04x"%v + ("" if i==0 else "(%+d)"%((v-base)&0xFFFF if (v-base)&0xFFFF<0x8000 else ((v-base)&0xFFFF)-0x10000))) for i,v in enumerate(vals)))
