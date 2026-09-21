import gzip,json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
V02=Path("tests/v30/v0.2"); V03=Path("tests/v30/v0.3")
def one(form):
    a=json.load(gzip.open(V02/f"{form}.json.gz")); b=json.load(gzip.open(V03/f"{form}.json.gz"))
    J=lambda x:json.dumps(x,sort_keys=True,separators=(",",":"))
    out={}
    out["hash"]=sum(1 for i in range(len(a)) if a[i]["hash"]!=b[i]["hash"])
    out["full+idx"]=sum(1 for i in range(len(a)) if J(a[i])!=J(b[i]))
    out["initial"]=sum(1 for i in range(len(a)) if J(a[i]["initial"])!=J(b[i]["initial"]))
    out["final"]=sum(1 for i in range(len(a)) if J(a[i]["final"])!=J(b[i]["final"]))
    out["cycles"]=sum(1 for i in range(len(a)) if J(a[i]["cycles"])!=J(b[i]["cycles"]))
    out["name+bytes"]=sum(1 for i in range(len(a)) if (a[i]["name"],a[i]["bytes"])!=(b[i]["name"],b[i]["bytes"]))
    out["nbi"]=sum(1 for i in range(len(a)) if J([a[i]["name"],a[i]["bytes"],a[i]["initial"]])!=J([b[i]["name"],b[i]["bytes"],b[i]["initial"]]))
    return out
if __name__=="__main__":
    forms=sorted(p.name[:-8] for p in V02.glob("*.json.gz"))
    tot={}
    with ProcessPoolExecutor(max_workers=8) as ex:
        for d in ex.map(one,forms):
            for k,v in d.items(): tot[k]=tot.get(k,0)+v
    for k,v in sorted(tot.items()): print(f"  {k:<14} {v}")
