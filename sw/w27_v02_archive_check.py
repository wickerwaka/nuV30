#!/usr/bin/env python3
"""w27_v02_archive_check -- RET-3's live falsifier.

`tests/v30/v0.2/` is GONE (WAVE 27; `docs/notes/invalidation_ledger.md` RET-3)
and it was NOT in git, so no checkout restores it.  What survives is
`tests/v30/v02-unique-archive/` -- the 7,127 cases `tests/v30/v0.3`'s
first-1,000-per-form prefix does not reproduce.

This gate re-derives, against `v0.3` ALONE, every claim the archive makes that
can still be checked without `v0.2`:

  A  integrity      -- SHA256SUMS and the manifest's per-file digests hold, and
                       every archived record's own `hash` field recomputes.
  B  the SHIFTED set -- each of the 5,890 cases the manifest calls
                       "present in v0.3 at another index" IS in v0.3's 10,000,
                       at the index the manifest names, byte for byte.
  C  the ABSENT set  -- each of the 1,237 cases the manifest calls absent is in
                       NO index of v0.3's 10,000.
  D  arithmetic      -- the counts add up and match the manifest's headline.

POSITIVE CONTROL (always run, --no-control to skip): B and C are each made to
FAIL on a perturbed copy of the manifest.  A check that cannot fail is not a
check.

exit 0 PASS / 1 FAIL / 2 CANNOT MEASURE
"""
import gzip, json, hashlib, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCH = ROOT / "tests/v30/v02-unique-archive"
V03 = ROOT / "tests/v30/v0.3"


def sha1_of(r):
    return hashlib.sha1(json.dumps(
        [r["name"], r["bytes"], r["initial"], r["final"], r["cycles"]],
        separators=(",", ":")).encode()).hexdigest()


def load_v03(form):
    p = V03 / f"{form}.json.gz"
    if not p.exists():
        return None
    return json.load(gzip.open(p))


def run(man, arch_recs, quiet=False):
    """Return (list of violations, counts).  `man` may be perturbed."""
    bad, n_shift, n_abs = [], 0, 0
    for form, d in sorted(man["forms"].items()):
        recs = arch_recs[form]
        by_idx = {r["idx"]: r for r in recs}
        b = load_v03(form)
        if b is None:
            bad.append(f"{form}: no v0.3 form on disk")
            continue
        bh = {}
        for j, r in enumerate(b):
            bh.setdefault(r["hash"], []).append(j)
        for i_s, j in d["disposition"]["PRESENT_IN_v0.3_AT_ANOTHER_INDEX"].items():
            n_shift += 1
            r = by_idx.get(int(i_s))
            if r is None:
                bad.append(f"{form}/{i_s}: index not in the archive file")
                continue
            if j >= len(b) or b[j]["hash"] != r["hash"]:
                bad.append(f"{form}/{i_s}: v0.3[{j}] does not carry this case")
                continue
            if json.dumps([b[j][k] for k in ("name", "bytes", "initial", "final", "cycles")],
                          separators=(",", ":")) != \
               json.dumps([r[k] for k in ("name", "bytes", "initial", "final", "cycles")],
                          separators=(",", ":")):
                bad.append(f"{form}/{i_s}: hash equal but record differs")
        for i_s, info in d["disposition"]["ABSENT_FROM_v0.3"].items():
            n_abs += 1
            r = by_idx.get(int(i_s))
            if r is None:
                bad.append(f"{form}/{i_s}: index not in the archive file")
                continue
            if r["hash"] in bh:
                bad.append(f"{form}/{i_s}: claimed ABSENT but v0.3 has it at "
                           f"{bh[r['hash']][0]}")
    return bad, n_shift, n_abs


def main():
    control = "--no-control" not in sys.argv
    if not ARCH.is_dir():
        print(f"w27_v02_archive_check: CANNOT MEASURE -- {ARCH} is not on disk")
        return 2
    if not V03.is_dir() or not any(V03.glob("*.json.gz")):
        print("w27_v02_archive_check: CANNOT MEASURE -- tests/v30/v0.3 has no "
              "forms on disk (it is disk-only; see its .gitignore)")
        return 2
    man = json.load(open(ARCH / "manifest.json"))
    print("w27_v02_archive_check -- RET-3's live falsifier")
    print(f"  archive : {ARCH.relative_to(ROOT)}")
    print(f"  against : {V03.relative_to(ROOT)}  "
          f"({len(list(V03.glob('*.json.gz')))} forms on disk)")
    print()

    fail = []

    # ---- A  INTEGRITY ----------------------------------------------------
    sums = {}
    for ln in (ARCH / "SHA256SUMS").read_text().split("\n"):
        if ln.strip():
            h, n = ln.split("  ", 1)
            sums[n] = h
    arch_recs, nrec, nhash_bad = {}, 0, 0
    for form, d in sorted(man["forms"].items()):
        p = ARCH / d["archive_file"]
        got = hashlib.sha256(p.read_bytes()).hexdigest()
        if got != d["archive_sha256"]:
            fail.append(f"A: {p.name} sha256 != manifest")
        if sums.get(p.name) != got:
            fail.append(f"A: {p.name} sha256 != SHA256SUMS")
        recs = json.load(gzip.open(p))
        arch_recs[form] = recs
        nrec += len(recs)
        if len(recs) != d["n_differing"]:
            fail.append(f"A: {p.name} holds {len(recs)}, manifest says {d['n_differing']}")
        for r in recs:
            if sha1_of(r) != r["hash"]:
                nhash_bad += 1
    if nhash_bad:
        fail.append(f"A: {nhash_bad} archived record(s) whose own `hash` does not recompute")
    print(f"  A  INTEGRITY      {len(man['forms'])} form file(s), {nrec} record(s), "
          f"{nhash_bad} bad hash field(s)")

    # ---- B / C / D -------------------------------------------------------
    bad, n_shift, n_abs = run(man, arch_recs)
    print(f"  B  SHIFTED        {n_shift} claimed present in v0.3 elsewhere")
    print(f"  C  ABSENT         {n_abs} claimed absent from v0.3 entirely")
    for v in bad[:20]:
        print(f"       ! {v}")
    fail += bad

    hd = man["of_which"]
    if n_shift != hd["PRESENT_IN_v0.3_AT_ANOTHER_INDEX"]:
        fail.append("D: shifted count != manifest headline")
    if n_abs != hd["ABSENT_FROM_v0.3_ENTIRELY"]:
        fail.append("D: absent count != manifest headline")
    if n_shift + n_abs != man["not_reproduced"] != nrec:
        fail.append("D: shifted + absent != not_reproduced != records on disk")
    if hd["ABSENT_and_REJECTED_BY_v0.3s_GENERATOR"] + \
       hd["ABSENT_and_SAME_SEED_DIFFERENT_RECORD"] != n_abs:
        fail.append("D: the two ABSENT sub-classes do not sum to ABSENT")
    print(f"  D  ARITHMETIC     {n_shift} + {n_abs} = {n_shift + n_abs} "
          f"(manifest: {man['not_reproduced']}, on disk: {nrec})")

    # ---- THE POSITIVE CONTROL -------------------------------------------
    if control:
        print()
        print("  POSITIVE CONTROL -- each check made to fail on a perturbed manifest")
        pm = json.loads(json.dumps(man))
        # B: move one shifted case to a different v0.3 index.
        for form, d in sorted(pm["forms"].items()):
            s = d["disposition"]["PRESENT_IN_v0.3_AT_ANOTHER_INDEX"]
            if s:
                k = sorted(s)[0]
                s[k] = (s[k] + 1) % 10000
                break
        b1, _, _ = run(pm, arch_recs)
        print(f"      B fires on a moved index : {'YES' if b1 else 'NO'}")
        if not b1:
            fail.append("CONTROL: B did not fire -- it proves nothing")
        # C: relabel one SHIFTED case as ABSENT.  v0.3 has it, so C must fire.
        pm = json.loads(json.dumps(man))
        for form, d in sorted(pm["forms"].items()):
            s = d["disposition"]["PRESENT_IN_v0.3_AT_ANOTHER_INDEX"]
            if s:
                k = sorted(s)[0]
                del s[k]
                d["disposition"]["ABSENT_FROM_v0.3"][k] = {
                    "v02_seed_attempt": -1, "class": "CONTROL"}
                break
        b2, _, _ = run(pm, arch_recs)
        print(f"      C fires on a false ABSENT: {'YES' if b2 else 'NO'}")
        if not b2:
            fail.append("CONTROL: C did not fire -- it proves nothing")

    print()
    if fail:
        print(f"w27_v02_archive_check: FAIL -- {len(fail)} violation(s)")
        for f in fail[:20]:
            print(f"  - {f}")
        return 1
    print(f"w27_v02_archive_check: PASS -- {nrec} preserved v0.2 record(s); "
          f"{n_shift} re-found in v0.3 byte-identical, {n_abs} confirmed absent "
          f"from all {len(man['forms'])} v0.3 forms checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
