#!/usr/bin/env python3
"""P-4(b): the SCORED CONTENT of an `fz2_replay --out` report, hashed.

The report carries three kinds of field: the SCORED CONTENT (`rows`, `tables`),
the ARTEFACT IDENTITY (`tb_sys_receipt`, `tb_sys_tree`, `git`, `era_report`,
`era_ok`) and the RUN's own metadata (`ts`).  An RTL edit MUST move the second
kind and MUST NOT move the first: that is the whole of P-4(b).  This prints the
sha256 of the first kind alone, so the two can be compared with one string.

Usage: phase_split_replay_sha.py A.json [B.json]
"""
import json, hashlib, sys

SCORED = ("rows", "tables")

def sha(p):
    d = json.loads(open(p).read())
    payload = {k: d[k] for k in SCORED}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
    ).hexdigest(), len(d["rows"]), d.get("tb_sys_receipt", "")

def main():
    out = [(p,) + sha(p) for p in sys.argv[1:]]
    for p, h, n, r in out:
        print(f"{p}\n  scored-content sha256 {h}\n  rows {n}   tb_sys receipt {r[:16]}…")
    if len(out) == 2:
        same = out[0][1] == out[1][1]
        print("\nSCORED CONTENT: %s" % ("IDENTICAL" if same else "*** DIFFERS ***"))
        print("tb_sys receipt: %s" % ("*** IDENTICAL -- the edit did not reach the binary ***"
                                      if out[0][3] == out[1][3] else "MOVED, as it must"))
        return 0 if same else 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
