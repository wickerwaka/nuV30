"""WAVE 24 B-1 CONTROL: is 'neither' special to the two VOID indices, or is it
what TODAY'S emitter produces for ANY v0.3 index?  Emits in memory only --
nothing is written to tests/."""
import sys
sys.path.insert(0, '/home/wickerwaka/src/nec_test/sw')
import emit_suite as es, suitemeta
from pathlib import Path

HOST = "root@mister-nec"
BASE = "v30-v0.2"
OUT = Path('/home/wickerwaka/src/nec_test/tests/v30/v0.3')
meta = suitemeta.load(OUT, delegate_to=es.DEFAULT_OUT)
TARGETS = [("88", 100), ("01", 200), ("8B", 300), ("83.5", 100), ("0F1B", 100),
           ("88", 101), ("01", 201)]
res = {}
for op, idx in TARGETS:
    spec = es.OPCODES[op]
    fm = meta.flags_mask(op)
    try:
        t = es._emit_one_index(spec, False, op, idx, HOST, BASE, -1, 0,
                               validate=True, flags_mask=fm, relog=None)
        d = t.get("flatvalidity", "flat-or-mirror-resolved")
        res[f"{op}/{idx}"] = d
    except Exception as e:
        res[f"{op}/{idx}"] = f"EXC {type(e).__name__}: {str(e)[:90]}"
    print(f"  {op}/{idx}: {res[f'{op}/{idx}']}", flush=True)
print("\nSUMMARY", res)
