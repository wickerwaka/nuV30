"""WAVE 24 A-3 census: how many v20suite cases place a non-0x90 recorded byte
inside the retirement point's reach, or transfer control away from it."""
import gzip, json
from pathlib import Path
S = Path('/home/wickerwaka/src/nec_test/tests/v30/v20suite')
EIGHT = {('03',2019),('0F1D',4712),('29',9262),('62',1229),
         ('85',4717),('86',9919),('E8',216),('E9',7762)}
REACH = 4
tot = near = xfer = both = 0
hits = set(); xfers = set()
for fn in sorted(S.glob('*.json.gz')):
    form = fn.name[:-8]
    for c in json.load(gzip.open(fn)):
        tot += 1
        r = c['initial']['regs']; f = c['final']['regs']
        lin = ((r['cs'] << 4) + r['ip']) & 0xFFFFF
        end = (lin + len(c['bytes'])) & 0xFFFFF
        img = {}
        for a, v in c['initial']['ram']: img[a & 0xFFFFF] = v
        for a, v in c['final']['ram']:   img[a & 0xFFFFF] = v
        n = any(img.get((end + d) & 0xFFFFF, 0x90) != 0x90 for d in range(REACH))
        x = (f.get('ip', r['ip']) != (r['ip'] + len(c['bytes'])) & 0xFFFF) or \
            ('cs' in f and f['cs'] != r['cs'])
        if n: near += 1; hits.add((form, c['idx']))
        if x: xfer += 1; xfers.add((form, c['idx']))
        if n and x: both += 1
print(f"total {tot}")
print(f"NEAR  (non-0x90 recorded byte in [end, end+{REACH}))  : {near}")
print(f"XFER  (control transfer away from ip+len)             : {xfer}")
print(f"both                                                  : {both}")
print(f"union                                                 : {len(hits | xfers)}")
print(f"the EIGHT inside NEAR : {sorted(f'{a}/{b}' for a,b in (EIGHT & hits))}")
print(f"the EIGHT inside XFER : {sorted(f'{a}/{b}' for a,b in (EIGHT & xfers))}")
print(f"the EIGHT inside UNION: {len(EIGHT & (hits | xfers))} of 8")
