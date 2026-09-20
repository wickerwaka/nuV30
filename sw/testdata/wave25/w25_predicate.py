"""WAVE 25 -- dump WAVE 24's A-3 predicate membership (the 2,284) to JSON.
Identical predicate to sw/testdata/wave24/a3/a3_census2.py, REACH=4."""
import gzip, json, sys
from pathlib import Path
S = Path('/home/wickerwaka/src/nec_test/tests/v30/v20suite')
REACH = 4
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
            hit.append([form, c['idx']])
json.dump({"total": tot, "reach": REACH, "members": hit},
          open(sys.argv[1], "w"), separators=(",", ":"))
print(f"total {tot}  members {len(hit)}")
