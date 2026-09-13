#!/usr/bin/env python3
"""WAVE 13 -- score one or more `quartus_gate --seeds N` distribution receipts.

It prints, per distribution, exactly the quantities the pre-registration's bars
N-1, N-2 and N-4 are written on, and NOTHING derived that the receipt does not
hold:

  N-1  verdict, per-seed Fmax / worst setup / ALMs, the `worst-of-N`, and
       whether every draw clears 32.0 MHz with positive setup and empty
       `tns_violations`.
  N-2  every per-seed `core_domain`: the measured k of each class, its nominal,
       and `off_class`.
  N-4  `E11_no_build_stamp` on the distribution AND on every per-seed receipt.

Also printed because a landing needs them: the DERIVED `configuration` string
(E-6), the `.rbf` sha256 of each draw (E-9), and the `input_manifest` id.

  usage: wave13_score.py DIST.json [DIST.json ...]
         wave13_score.py --delta A_DIST.json B_DIST.json   (N-3)
"""
import json, sys, os

BAR_FMAX = 32.0


def load(p):
    return json.loads(open(p).read())


def rbf_of(seed_rec):
    for n, h in (seed_rec.get("outputs") or {}).items():
        if n.endswith(".rbf"):
            return h
    return ""


def e11_of(rec):
    e = rec.get("E11_no_build_stamp")
    if e is None:
        return None
    return bool(e.get("pass")), e.get("files_scanned"), e.get("file_present"), \
        e.get("token_hits")


def report(path):
    d = load(path)
    print("=" * 78)
    print(f"{path}")
    print(f"  id                 {d['id'][:16]}…")
    print(f"  label              {d.get('label')}")
    print(f"  verdict            {d['verdict']}   rc={d['rc']}   {d['seconds']:.0f} s")
    print(f"  configuration      {d['configuration'].split(' -- ')[0]}")
    print(f"  DERIVED-from       {'DERIVED' if '-- DERIVED' in d['configuration'] else '*** NOT DERIVED ***'}")
    print(f"  input_manifest     {d['input_manifest']['sha256'][:16]}…  "
          f"({len(d['input_manifest']['files'])} files)")
    w = d["worst_of_n"]
    print(f"  WORST-OF-{w['n']}         {w['fmax_mhz']} MHz  (seed {w['seed']})   "
          f"quotable_as: {w['quotable_as']}")
    f = d["fmax"]
    print(f"  draws              {' · '.join(str(x) for x in f['sorted'])}"
          f"   median {f['median']}  spread {f['spread']}")

    e = e11_of(d)
    print(f"  E11 (distribution) {'PASS' if e and e[0] else '*** FAIL/ABSENT ***'}"
          f"   scanned={e[1] if e else '-'}  file_present={e[2] if e else '-'}"
          f"  token_hits={e[3] if e else '-'}")

    n1_fail, n2_fail, n4_fail = [], [], []
    print("  seed  Fmax    setup      ALMs                    core k(SAME/INTO/OUTOF)"
          "  off_class   E11   rbf")
    for s in d["per_seed"]:
        cd = s.get("core_domain") or {}
        km, kn = cd.get("k_measured"), cd.get("k_nominal")
        ks = f"meas {km} / nom {kn}"
        off = cd.get("off_class")
        sr = load(s["receipt"]) if os.path.exists(s.get("receipt", "")) else {}
        se = e11_of(sr)
        okE11 = se[0] if se else None
        print(f"  {s['seed']:>4}  {s['fmax_mhz']:>6}  {s['worst_setup_ns']:>+8.3f}"
              f"  {s['alms']:<22}  {ks:<22}"
              f"  {str(off):<10}  {'ok' if okE11 else '??'}   {rbf_of(s)[:12]}")
        if s["fmax_mhz"] < BAR_FMAX or s["worst_setup_ns"] <= 0 or s.get("tns_violations"):
            n1_fail.append(s["seed"])
        if off:
            n2_fail.append((s["seed"], off))
        if okE11 is not True:
            n4_fail.append(s["seed"])

    print(f"  N-1  every draw >= {BAR_FMAX} MHz, setup > 0, tns_violations empty : "
          f"{'PASS' if not n1_fail else '*** FAIL on seeds ' + str(n1_fail) + ' ***'}")
    print(f"  N-2  off_class EMPTY on every draw                        : "
          f"{'PASS' if not n2_fail else '*** ' + str(n2_fail) + ' ***'}")
    print(f"  N-4  E11 true on every per-seed receipt                   : "
          f"{'PASS' if not n4_fail else '*** FAIL on seeds ' + str(n4_fail) + ' ***'}")
    rbfs = [rbf_of(s) for s in d["per_seed"]]
    print(f"  E-9  .rbf distinct across draws                           : "
          f"{len(set(rbfs))} distinct of {len(rbfs)}"
          f"{'' if all(rbfs) else '   (some draws have no .rbf)'}")
    return d


def main():
    if sys.argv[1] == "--delta":
        a, b = report(sys.argv[2]), report(sys.argv[3])
        print("=" * 78)
        print("N-3  THE LIKE-FOR-LIKE DELTA")
        print(f"  A  {a.get('label')}   worst-of-{a['worst_of_n']['n']} = "
              f"{a['worst_of_n']['fmax_mhz']} MHz")
        print(f"  B  {b.get('label')}   worst-of-{b['worst_of_n']['n']} = "
              f"{b['worst_of_n']['fmax_mhz']} MHz")
        print(f"  B - A = {b['worst_of_n']['fmax_mhz'] - a['worst_of_n']['fmax_mhz']:+.2f} MHz")
        print(f"  seed sets: A {a['seeds']}  B {b['seeds']}  "
              f"{'SAME' if a['seeds'] == b['seeds'] else '*** DIFFERENT ***'}")
        return 0
    for p in sys.argv[1:]:
        report(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
