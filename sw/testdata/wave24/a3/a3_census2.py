"""WAVE 24 A-3, the SINGLE predicate: does the case's CONTINUATION point (where
execution goes after the instruction under test retires) have a recorded
non-0x90 byte within REACH bytes?"""
import gzip, json, sys
from pathlib import Path
S = Path('/home/wickerwaka/src/nec_test/tests/v30/v20suite')
EIGHT = {('03',2019),('0F1D',4712),('29',9262),('62',1229),
         ('85',4717),('86',9919),('E8',216),('E9',7762)}
REACH = int(sys.argv[1]) if len(sys.argv) > 1 else 4
tot = 0; hit = []
for fn in sorted(S.glob('*.json.gz')):
    form = fn.name[:-8]
    for c in json.load(gzip.open(fn)):
        tot += 1
        r = c['initial']['regs']; f = c['final']['regs']
        cs = f.get('cs', r['cs']); ip = f.get('ip', r['ip'])
        cont = ((cs << 4) + ip) & 0xFFFFF
        img = {}
        for a, v in c['initial']['ram']: img[a & 0xFFFFF] = v
        for a, v in c['final']['ram']:   img[a & 0xFFFFF] = v
        if any(img.get((cont + d) & 0xFFFFF, 0x90) != 0x90 for d in range(REACH)):
            hit.append((form, c['idx']))
H = set(hit)
print(f"REACH={REACH}  total {tot}")
print(f"CONT-NONFILL : {len(hit)}")
print(f"the EIGHT inside: {len(EIGHT & H)} of 8  -> {sorted(f'{a}/{b}' for a,b in (EIGHT & H))}")
print(f"members not in the EIGHT ({len(H - EIGHT)}): {sorted(f'{a}/{b}' for a,b in (H - EIGHT))[:40]}")
