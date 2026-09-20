import sys, subprocess, gzip, json, tempfile, os
sys.path.insert(0,'sw')
import check_core as cc
from pathlib import Path
suite=Path(sys.argv[1]); waits=sys.argv[2] if len(sys.argv)>2 else "0"
arch = "--arch" in sys.argv
tot_g=tot_w=0; ncase=0
tmp=Path(os.path.expanduser("~/.cache/ucsimt-tmp/w25/lp")); tmp.mkdir(exist_ok=True)
for fn in sorted(suite.glob("*.json.gz")):
    cases=json.load(gzip.open(fn))
    b=tmp/"b.txt"; o=tmp/"o.txt"
    cc.compose_batch(cases,b,arch_only=arch)
    r=subprocess.run([str(cc.core_bin("ucore")),f"+batch={b}",f"+out={o}",
                      f"+waits={waits}","+ce_div=4"],capture_output=True,text=True)
    for ln in r.stdout.splitlines():
        if ln.startswith("W25LEAK"):
            p=ln.split(); tot_g+=int(p[1].split("=")[1]); tot_w+=int(p[2].split("=")[1])
    ncase+=len(cases)
print(f"{suite.name}: cases {ncase}  ghost-leak {tot_g}  wait-overlap {tot_w}")
