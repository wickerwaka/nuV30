"""WAVE 24 B-1: THE COLLISION, SHOWN FROM THE BANKED CASE ALONE.

No engine, no regeneration -- arithmetic over the golden's own recorded
initial state.  Both cases are `idx % 2 == 1`, i.e. the PREFETCHED variant,
whose run image is `PRELOAD_BYTES * 2 + instr` with PC moved back 2*2 bytes
(sw/emit_suite.py::emit_case).  PRELOAD_BYTES is b"\\x63\\xc0".
"""
import gzip, json, sys
from pathlib import Path
SUITE = Path(__file__).resolve().parents[3] / "tests" / "v30" / "v0.3"
PRE = b"\x63\xc0"

CASES = [
    # form, idx, prose, the ModR/M-derived EA expression, EA
    ("0F1B", 3917, "clr1 imm word [bx+di],05h", "DS*16 + BW + IY"),
    ("83.5", 8683, "sub w,simm8 word [bx],01h", "DS*16 + BW"),
]

def ea_of(form, r):
    if form == "0F1B":                     # modrm 0x01 -> mod0 reg0 rm1 [BW+IY]
        return (r["bx"] + r["di"]) & 0xFFFF
    return r["bx"] & 0xFFFF                # modrm 0x2f -> mod0 reg5 rm7 [BW]

bad = 0
for form, idx, prose, expr in CASES:
    c = [t for t in json.load(gzip.open(SUITE / f"{form}.json.gz"))
         if t["idx"] == idx][0]
    r = c["initial"]["regs"]
    ram = {a & 0xFFFF: v for a, v in c["initial"]["ram"]}
    code_lin = ((r["cs"] << 4) + r["ip"]) & 0xFFFFF
    code_phys = code_lin & 0xFFFF
    n = 2                                   # preload repetitions, idx odd
    pl_lo = (code_phys - 2 * n) & 0xFFFF    # PC -= 2*n
    pl = PRE * n                            # 63 c0 63 c0
    ea = ea_of(form, r)
    op_phys = ((r["ds"] << 4) + ea) & 0xFFFF
    print(f"=== {form}/{idx}  {prose}   (idx odd -> PREFETCHED, {n} preloads)")
    print(f"    instruction  CS:IP {r['cs']:04x}:{r['ip']:04x}"
          f" -> linear {code_lin:05x}, phys(64K) {code_phys:04x}")
    print(f"    preload span {pl_lo:04x}..{(pl_lo+len(pl)-1)&0xFFFF:04x}"
          f"  = {' '.join(f'{b:02x}' for b in pl)}")
    print(f"    operand EA   {expr} = {op_phys:04x} (offset {ea:04x})")
    for k in range(2):
        p = (op_phys + k) & 0xFFFF
        inside = 0 <= ((p - pl_lo) & 0xFFFF) < len(pl)
        got = pl[(p - pl_lo) & 0xFFFF] if inside else None
        want = ram.get(p)
        flag = "COLLIDES" if inside and want is not None and got != want else \
               ("inside-preload" if inside else "clear")
        print(f"      operand byte {k}: phys {p:04x}  want "
              f"{'--' if want is None else f'{want:02x}'}  image holds "
              f"{'--' if got is None else f'{got:02x}'}   -> {flag}")
        if flag == "COLLIDES":
            bad += 1
print(f"\ncolliding operand bytes: {bad}")
sys.exit(0 if bad else 1)
