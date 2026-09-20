import sys, random, json, gzip
sys.path.insert(0, '/home/wickerwaka/src/nec_test/sw')
import emit_suite as es, testimage

BASE = "v30-v0.2"
targets = [("0F1B", 3917), ("83.5", 8683)]

def compose_for(op, idx, seedsuffix=""):
    spec = es.OPCODES[op]
    pn = 2 if idx % 2 == 1 else 0
    sd = f"{BASE}/{op}/{idx}" + seedsuffix
    rng = random.Random(sd)
    case = es.gen_case(spec, rng)
    nec_regs = {es.INTEL2NEC[k]: v for k, v in case["regs"].items()}
    instr = case["instr"]
    ram = list(case["ram"]); ivt = case["ivt"]
    if pn:
        nec_regs["PC"] = (nec_regs["PC"] - 2*pn) & 0xFFFF
        run_instr = es.PRELOAD_BYTES * pn + instr
    else:
        run_instr = instr
    next_ip = case.get("next_ip")
    if next_ip is None:
        next_ip = (case["regs"]["ip"] + len(instr)) & 0xFFFF
    next_cs = case.get("next_cs")
    cont_cs = next_cs if next_cs is not None else case["regs"]["cs"]
    cont_linear = ((cont_cs << 4) + next_ip) & 0xFFFF
    if ivt:
        h = bytes([0xEA, cont_linear & 0xFF, cont_linear >> 8, 0x00, 0x00])
        ram += [(es.HANDLER_OFF + k, b) for k, b in enumerate(h)]
    image, meta = testimage.compose(regs=nec_regs, instr=run_instr, ram=ram, ivt=ivt)
    bad = es._operand_survives(image, ram)
    spans = meta.get("spans") if isinstance(meta, dict) else None
    return case, image, meta, ram, bad, sd, pn

for op, idx in targets:
    print("="*70)
    banked = [t for t in json.load(gzip.open(f"tests/v30/{ 'v0.3' }/{op}.json.gz")) if t["idx"] == idx][0]
    for suf in ["", "/1", "/2"]:
        try:
            case, image, meta, ram, bad, sd, pn = compose_for(op, idx, suf)
        except Exception as e:
            print(f"{op}/{idx} seed={BASE}/{op}/{idx}{suf}: EXC {type(e).__name__}: {e}")
            continue
        regs = case["regs"]
        same = (regs["cs"] == banked["initial"]["regs"]["cs"] and
                regs["ip"] == banked["initial"]["regs"]["ip"] and
                list(case["instr"]) == list(banked["bytes"]))
        print(f"{op}/{idx} seed='{sd}' preload_n={pn} matches_banked_initial={same}")
        print(f"   instr={[hex(b) for b in case['instr']]} cs={regs['cs']:04x} ip={regs['ip']:04x}")
        print(f"   _operand_survives -> {bad if bad is None else ('phys %04x want %02x got %02x' % bad)}")
