"""WAVE 24 A-3 controls: build scratch v20suite slices with a directed byte
injection after the instruction under test."""
import gzip, json, shutil, sys
from pathlib import Path

SUITE = Path('/home/wickerwaka/src/nec_test/tests/v30/v20suite')
OUT   = Path('/home/wickerwaka/.cache/ucsimt-tmp/w24/a3')
FORM  = '03'
N     = 20

cases = json.load(gzip.open(SUITE / f'{FORM}.json.gz'))
sel = []
for c in cases:
    if c['idx'] == 2019:        # the known failure -- excluded from the control
        continue
    r = c['initial']['regs']
    lin = ((r['cs'] << 4) + r['ip']) & 0xFFFFF
    end = (lin + len(c['bytes'])) & 0xFFFFF
    recorded = {a & 0xFFFFF for a, _ in c['initial']['ram']} | \
               {a & 0xFFFFF for a, _ in c['final']['ram']}
    # the whole injection reach must be free of recorded bytes, so no variant
    # of this experiment can disturb an operand the golden records
    reach = {(end + d) & 0xFFFFF for d in range(0, 20)}
    if reach & recorded:
        continue
    sel.append((c['idx'], end))
    if len(sel) >= N:
        break

print(f"selected {len(sel)} cases of form {FORM}: idx {[i for i,_ in sel]}")
idxs = {i for i, _ in sel}
ends = dict(sel)

def variant(name, patch):
    d = OUT / name
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(SUITE / 'metadata.json', d / 'metadata.json')
    out = []
    for c in cases:
        if c['idx'] not in idxs:
            continue
        c = json.loads(json.dumps(c))
        for a, v in patch(ends[c['idx']]):
            c['initial']['ram'].append([a & 0xFFFFF, v])
        out.append(c)
    with gzip.open(d / f'{FORM}.json.gz', 'wt') as f:
        json.dump(out, f, separators=(',', ':'))
    print(f"  wrote {name}: {len(out)} cases")

variant('base',   lambda e: [])
variant('inj0',   lambda e: [(e, 0xFF), (e + 1, 0xCC)])        # DEC SP at +0
variant('null90', lambda e: [(e, 0x90), (e + 1, 0x90)])        # registered C-NULL
variant('far64',  lambda e: [(e + 64, 0xFF), (e + 65, 0xCC)])  # C-FAR
for off in (2, 4, 6, 8, 10, 12, 16):
    variant(f'inj{off}', (lambda o: (lambda e: [(e + o, 0xFF), (e + o + 1, 0xCC)]))(off))
