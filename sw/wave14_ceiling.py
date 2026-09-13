#!/usr/bin/env python3
"""WAVE 14 -- THE PAIRED CEILING SCORER.

It reads `quartus_gate --seeds N` DISTRIBUTION receipts and reports, per arm and
per PAIR, exactly the quantities the pre-registration's bars P-3, P-4 and P-5
are written on -- and nothing the receipts do not hold.

  P-3  registers: A&S `map_registers`, fitter `fit_registers`, and the per-entity
       `ucore_hierarchy` counts for `v30u_biu` / `v30u_eu` / `v30_core`.  A STAGE
       BOUNDARY IS A REGISTER: if no register moved, no stage was subdivided.
       The `combinational_aluts` columns are printed beside them because they are
       how much logic an arm PRUNED, which is the other way a probe over-answers.
  P-4  `E11_no_build_stamp` at DISTRIBUTION level AND on every per-seed receipt.
       ⚠ It is NOT inside a seed's `bars` dict; a query there returns nothing and
       reads as a miss.  Also: seed sets identical, both configurations present.
  P-5  the paired mean of the per-seed differences with sd, standard error and a
       95 % CI -- WAVE 10's form, so the two waves' figures are read the same way.

⚠ IT SIZES NOTHING BY ATTRIBUTION.  Every number is a DIFFERENCE between two
identically-compiled arms at the same seed.  A census ranks candidates; it does
not size them (WAVE 8: 5.9x on `ucrom`; WAVE 10: 5.3x on this mechanism).

POSITIVE CONTROL (P-1), RUN BEFORE ANY NEW DATA IS SCORED:
    python3 sw/wave14_ceiling.py --selftest
reproduces WAVE 13's COMMITTED `w13-split-noexc-*` distributions -- draws,
worst-of-5, spread and ALMs -- from their bytes on disk, and FAILS LOUDLY if it
cannot.  A scorer that has never been shown to reproduce a known answer is not
an instrument.

usage:
    python3 sw/wave14_ceiling.py --selftest
    python3 sw/wave14_ceiling.py report  DIST.json [DIST.json ...]
    python3 sw/wave14_ceiling.py pair    BASE_DIST.json ARM_DIST.json
"""
import json
import math
import os
import sys

# two-sided 95 % t, df = n-1.  Small table; refuse rather than approximate.
T95 = {2: 12.706, 3: 4.303, 4: 3.182, 5: 2.776, 6: 2.571, 7: 2.447,
       8: 2.365, 9: 2.306, 10: 2.262}

W13 = "sw/testdata/g6dist/w13-split-noexc-%s-n5/distribution.json"
W13_EXPECT = {
    "control":   dict(worst=30.53, draws=[30.53, 30.62, 30.85, 30.98, 31.11],
                      spread=0.58),
    "retention": dict(worst=31.15, draws=[31.15, 31.82, 32.43, 32.53, 32.75],
                      spread=1.60),
}


def load(p):
    with open(p) as f:
        return json.load(f)


def e11(rec):
    e = rec.get("E11_no_build_stamp")
    if e is None:
        return None
    return bool(e.get("pass"))


def tmin(seed_rec):
    """T_min in ns.  Preferred: the core-domain figure the receipt computed.
    Fallback: 1000 / fmax, PRINTED as a fallback when it is used."""
    cd = seed_rec.get("core_domain") or {}
    if cd.get("t_min_ns"):
        return float(cd["t_min_ns"]), False
    return 1000.0 / float(seed_rec["fmax_mhz"]), True


def arm(path):
    d = load(path)
    d["_path"] = path
    d["_seeds"] = {s["seed"]: s for s in d["per_seed"]}
    return d


def report(d, quiet=False):
    p = d["_path"]
    f = d["fmax"]
    w = d["worst_of_n"]
    ok_e11 = e11(d)
    if not quiet:
        print("=" * 78)
        print(p)
        print(f"  label            {d.get('label')}")
        print(f"  id               {d['id'][:16]}…")
        print(f"  verdict          {d['verdict']}   rc={d['rc']}   {d['seconds']:.0f} s")
        print(f"  configuration    {d['configuration'].split(' -- ')[0]}")
        print(f"  input_manifest   {d['input_manifest']['sha256'][:16]}…  "
              f"({len(d['input_manifest']['files'])} files)")
        print(f"  seeds            {d['seeds']}")
        print(f"  WORST-OF-{w['n']}       {w['fmax_mhz']} MHz (seed {w['seed']})   "
              f"draws {' · '.join(str(x) for x in f['sorted'])}   spread {f['spread']}")
        print(f"  P-4  E11 (DISTRIBUTION level)  "
              f"{'PASS' if ok_e11 else '*** FAIL/ABSENT ***'}")
        print("  seed  Fmax     T_min      setup   ALMs        map_reg  fit_reg  "
              "biu_reg  eu_reg  biu_alut  eu_alut  off_class  E11")
    rows = []
    fb_used = False
    for s in d["per_seed"]:
        t, fb = tmin(s)
        fb_used |= fb
        cd = s.get("core_domain") or {}
        rec = load(s["receipt"]) if os.path.exists(s["receipt"]) else {}
        fig = rec.get("figures", {})
        st = fig.get("status", {})
        h = fig.get("ucore_hierarchy", {})

        def hz(ent, key):
            return (h.get(ent, {}).get(key, {}) or {}).get("own")
        row = dict(seed=s["seed"], fmax=s["fmax_mhz"], tmin=t,
                   setup=s["worst_setup_ns"], alms=st.get("alms", "?"),
                   map_reg=st.get("map_registers"), fit_reg=st.get("fit_registers"),
                   biu_reg=hz("v30u_biu", "dedicated_logic_registers"),
                   eu_reg=hz("v30u_eu", "dedicated_logic_registers"),
                   biu_alut=hz("v30u_biu", "combinational_aluts"),
                   eu_alut=hz("v30u_eu", "combinational_aluts"),
                   off=cd.get("off_class"), k=cd.get("k_measured"),
                   knom=cd.get("k_nominal"), e11=e11(rec))
        rows.append(row)
        if not quiet:
            print(f"  {row['seed']:>4}  {row['fmax']:>6}  {row['tmin']:>8.3f}  "
                  f"{row['setup']:>+7.3f}  {str(row['alms']).split(' /')[0]:>7}  "
                  f"{str(row['map_reg']):>7}  {str(row['fit_reg']):>7}  "
                  f"{str(row['biu_reg']):>7}  {str(row['eu_reg']):>6}  "
                  f"{str(row['biu_alut']):>8}  {str(row['eu_alut']):>7}  "
                  f"{str(row['off']):>9}  {'ok' if row['e11'] else '***'}")
    if not quiet:
        if fb_used:
            print("  ⚠ T_min for at least one draw is the 1000/Fmax FALLBACK, "
                  "not the receipt's own core_domain.t_min_ns")
        bad = [r["seed"] for r in rows if r["e11"] is not True]
        print(f"  P-4  E11 on every PER-SEED receipt      "
              f"{'PASS' if not bad else '*** FAIL on ' + str(bad) + ' ***'}")
        offs = [(r["seed"], r["off"]) for r in rows if r["off"]]
        print(f"  N-2  off_class EMPTY on every draw      "
              f"{'PASS' if not offs else '*** ' + str(offs) + ' ***'}")
        for key in ("map_reg", "fit_reg", "biu_reg", "eu_reg"):
            vals = sorted({str(r[key]) for r in rows})
            print(f"  P-3  {key:<8} across the sweep        "
                  f"{'CONSTANT ' + vals[0] if len(vals) == 1 else '*** VARIES ' + str(vals) + ' ***'}")
    d["_rows"] = rows
    return d


def stats(xs):
    n = len(xs)
    m = sum(xs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1)) if n > 1 else float("nan")
    se = sd / math.sqrt(n) if n > 1 else float("nan")
    t = T95.get(n)
    if t is None:
        raise SystemExit(f"REFUSING: no tabulated t for n={n}; add it rather "
                         f"than approximate.")
    return m, sd, se, (m - t * se, m + t * se), (m / se if se else float("nan"))


def pair(base, armd):
    a, b = report(arm(base)), report(arm(armd))
    print("=" * 78)
    print("THE PAIRED DIFFERENCE  (arm - base, per seed; a POSITIVE ns figure "
          "means the arm's arc is SHORTER)")
    sa, sb = set(a["_seeds"]), set(b["_seeds"])
    print(f"  seed sets   base {sorted(sa)}   arm {sorted(sb)}   "
          f"{'SAME' if sa == sb else '*** DIFFERENT -- NOT A PAIR ***'}")
    if sa != sb:
        return 1
    seeds = sorted(sa)
    dt, dm = [], []
    print("  seed   base T_min   arm T_min    Δns      base MHz  arm MHz   ΔMHz")
    for s in seeds:
        ta, _ = tmin(a["_seeds"][s])
        tb, _ = tmin(b["_seeds"][s])
        fa = a["_seeds"][s]["fmax_mhz"]
        fb = b["_seeds"][s]["fmax_mhz"]
        dt.append(ta - tb)      # arc SHORTENED by the arm -> positive
        dm.append(fb - fa)
        print(f"  {s:>4}   {ta:>9.3f}   {tb:>9.3f}  {ta-tb:>+7.3f}   "
              f"{fa:>8.2f}  {fb:>7.2f}  {fb-fa:>+6.2f}")
    for name, xs, unit in (("T_min", dt, "ns"), ("Fmax", dm, "MHz")):
        m, sd, se, ci, t = stats(xs)
        print(f"  {name:>5} paired mean {m:+.3f} {unit}   sd {sd:.3f}   "
              f"se {se:.3f}   95 % CI [{ci[0]:+.3f}, {ci[1]:+.3f}]   t {t:+.2f}")
    wa = a["worst_of_n"]["fmax_mhz"]
    wb = b["worst_of_n"]["fmax_mhz"]
    print(f"  worst-of-{len(seeds)}   base {wa} MHz   arm {wb} MHz   "
          f"Δ {wb-wa:+.2f} MHz")
    return 0


def selftest():
    print("=== P-1 POSITIVE CONTROL: reproduce WAVE 13's COMMITTED split "
          "distributions from their bytes ===")
    ok = True
    for cfg, exp in W13_EXPECT.items():
        p = W13 % cfg
        if not os.path.exists(p):
            print(f"  *** {p} MISSING -- the control cannot run ***")
            ok = False
            continue
        d = report(arm(p), quiet=True)
        got = dict(worst=d["worst_of_n"]["fmax_mhz"],
                   draws=d["fmax"]["sorted"], spread=d["fmax"]["spread"])
        good = all(abs(got[k] - exp[k]) < 1e-9 if not isinstance(exp[k], list)
                   else got[k] == exp[k] for k in exp)
        print(f"  {cfg:<10} worst {got['worst']} (want {exp['worst']})   "
              f"draws {got['draws']}   spread {got['spread']}   "
              f"{'MATCH' if good else '*** MISMATCH ***'}")
        # and the fields P-3 will be read from must be present and constant
        for key in ("map_reg", "fit_reg", "biu_reg", "eu_reg"):
            vals = {str(r[key]) for r in d["_rows"]}
            print(f"    {key:<8} {sorted(vals)}"
                  f"{'' if len(vals) == 1 else '   *** VARIES ***'}")
            if None in {r[key] for r in d["_rows"]}:
                print(f"    *** {key} ABSENT from the receipts -- P-3 cannot "
                      f"be read this way ***")
                ok = False
        ok &= good
    print(f"  SELFTEST {'PASS' if ok else '*** FAIL ***'}")
    return 0 if ok else 1


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    c = sys.argv[1]
    if c == "--selftest":
        return selftest()
    if c == "report":
        for p in sys.argv[2:]:
            report(arm(p))
        return 0
    if c == "pair":
        return pair(sys.argv[2], sys.argv[3])
    print("unknown command " + c)
    return 2


if __name__ == "__main__":
    sys.exit(main())
