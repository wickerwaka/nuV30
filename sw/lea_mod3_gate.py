#!/usr/bin/env python3
"""lea_mod3_gate -- the standing falsifier for the undocumented `8D` / mod=3
STALE-EA mechanism, scored against SILICON, on the path where the stimulus is
COMPLETE.

WHY THIS GATE EXISTS, AND WHY IT IS NOT `check_core --suite-dir`
----------------------------------------------------------------
`tests/v30/mod3_illegal` is 128 socket-captured goldens of `8D` at `mod == 3`
(`truth_source: SOCKET (use_core=False)`, 2026-07-27).  Scored through
`check_core`'s backdoor-injection TB the ucore reads **ARCH 0 / 128** with
**cycles 128 / 128**, every case differing in exactly the register the ModR/M
`reg` field names, `exp 0500 got 0000`.

**THAT IS A STIMULUS DEFECT OF THE TESTBENCH, NOT A DEFECT OF THE CORE.**
`hdl/tb/tb_v30_core.sv` injects the FOURTEEN ARCHITECTURAL REGISTERS through
the `V30_BACKDOOR` port while the core is held in reset, and nothing else --
so the EU's retained EA rail (`ea_residue`, `hdl/rtl/ucore/v30u_eu.sv:251`,
save-state address `0x177`) enters every case at its reset value `16'd0`,
while the chip entered the identical window carrying the value its own
pre-window history had left there.  The golden carries no field for it.  A
golden whose outcome depends on pre-window MICROARCHITECTURAL state is
unscoreable by an injected engine BY CONSTRUCTION, and no amount of RTL is
going to change that (`docs/notes/suite_scorer_results_2026-09-19.md` §5 said
so first; `docs/notes/lea_mod3_results_2026-09-20.md` proves it).

So this gate scores the same mechanism where the stimulus IS complete: the
WHOLE-PROGRAM replay, `sw/tb_bootrun.py`'s `+bootimg` mode, **from RESET, with
NO backdoor injection at all**, so the composed image's own loader runs inside
the core exactly as it ran inside the chip.

THE MECHANISM, IN ONE SENTENCE
------------------------------
    At `mod == 3` the `8D` decode issues no EA calculation, so the row-1
    SIGMA -> R transfer writes the register the ModR/M `reg` field names with
    whatever the address adder's two rails still hold -- the retained EA lane
    (`ea_residue`) and the ordinary scratch lane (`tmpb`) -- and the
    instruction falls through.

`hdl/rtl/ucore/v30u_eu_arm_bind.svh:81-84` is the whole of it.  It names no
opcode table and costs no flop this core did not already have.

THE LEGS
--------
  L1  SILICON, REGISTERED.  The `match: true` rows of the suite's own
      `metadata.json::stale_ea_probe` -- read OUT of that file, never
      hard-coded -- replayed at the capture rig's own `PS = 0x0000`.  2 / 2.
  L1b SILICON, OBSERVATIONAL AND NOT A BAR.  The `match: false` rows.  Their
      `si_loaded` is still a silicon measurement; `match` records only that the
      RIG's 2026-07-27 hypothesis ("the register receives the EA") failed on
      them, which is exactly what a SUM of two rails predicts.  Reported, never
      scored, because nothing about the encoding of a prose `pre` field is
      certain enough to gate on.
  L2  ROUTING.  All 8 ModR/M `reg` fields x all 8 `rm` values, one preceding
      EA: the named register takes it, **no other GPR moves**, and the value
      does not depend on `rm`.  64 / 64.  This is the `reg`-field pairing WAVE
      22 found on the injected leg, re-derived on the complete one.
  L3  NON-VACUITY, 3 controls, each of which MUST fail its L1/L2 shape:
      C1 the same image with the LEA REMOVED leaves the register loaded;
      C2 a DIFFERENT preceding EA gives a DIFFERENT value (so L1/L2 cannot
         pass by writing a constant);
      C3 a different `reg` field moves a different register and leaves the
         first one loaded.
  L4  ⚠ **KNOWN-RED, REPORTED, AND DELIBERATELY NOT A BAR.**  The suite's two
      OTHER silicon rows, whose `pre` is a ModR/M memory form.  **THE ucore
      DIVERGES FROM SILICON ON BOTH**, and the divergence is in the retained
      EA lane alone.  It is not a bar because the reference population is TWO
      rows whose byte encoding is INFERRED FROM A PROSE FIELD, and closing it
      needs a directed socket capture.  `docs/notes/lea_mod3_results_2026-09-20.md`
      §4 carries the derivation and the falsifier.

  Offline, no board, ~70 whole-program replays, ~7 s.  Exit 0 PASS / 1 FAIL /
  2 CANNOT MEASURE.

⚠⚠ WHAT THIS GATE DOES AND DOES NOT FALSIFY -- **MEASURED, NOT ASSUMED**
-----------------------------------------------------------------------
Five perturbations of `hdl/rtl/ucore/v30u_eu_arm_bind.svh` were BUILT AND RUN
against it, each in an isolated worktree, each with the unperturbed build as
its own control (`docs/notes/lea_mod3_results_2026-09-20.md` §5):

  * **P5** `r_idx_n = rmreg` -> `rmreg ^ 3'd1` (the ModR/M `reg` operand
    index): **CAUGHT -- L1 0/2, L2 0/64, L3 0/3.**
  * **P1** deleting the mod3 arm's `tmpa_n = ea_residue_n;`: **NOT CAUGHT.**
  * **P2** `tmpa_n = ea_pair_rhs_n;` (wrong rail): **NOT CAUGHT.**
  * **P4** `modrm_reg_n = rmreg ^ 3'd1`: **NOT CAUGHT** (that net does not
    route this destination; `r_idx_n` does).
  * **P6** deleting `if (ea_pair_valid_n) tmpb_n = ea_pair_rhs_n;`:
    **NOT CAUGHT.**

**AND THE REASON IS THE STIMULUS, NOT THE GATE'S SHAPE**: on a `MOV [imm16],AW`
predecessor -- the rig's own probe instruction, and the only preceding form with
a SILICON reference -- `ea_residue` and `tmpa` HOLD THE SAME VALUE, so the arm's
assignment is a no-op and the retained-rail plumbing is invisible to any
comparison.  **This gate falsifies the OBSERVABLE LAW -- which register receives
what -- against silicon.  IT DOES NOT COVER THE RETAINED-RAIL PLUMBING, and
saying so is worth more than a green claim that does not hold.**

⚠ THE GATE IS PS-SENSITIVE ON PURPOSE.  The register receives
`ea_residue + tmpb`, and the capture harness's loader ends `BR PS:PC`, which
leaves PC on the EA rail and **PS on the scratch rail**.  Every silicon row
this gate scores was captured at `PS = 0x0000`, so every leg here composes at
`PS = 0x0000` too.  Composing at any other `PS` shifts every expected value by
`PS` -- measured, and the reason `--ps-sweep` exists below.
"""
import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

SW = Path(__file__).resolve().parent
sys.path.insert(0, str(SW))
ROOT = SW.parent

import testimage as ti                                       # noqa: E402
import fuzz_classify as fc                                   # noqa: E402
from tb_bootrun import run_boot                              # noqa: E402

SUITE = ROOT / "tests" / "v30" / "mod3_illegal"

# The rig's own register setup (sw/char_mod3.py::SETUPS[0]), in V30 names.
# `cs`/`ip` are NOT taken from it: the body address is this gate's to choose
# and is stated per leg.
BASE = {"AW": 0x1111, "CW": 0x2222, "DW": 0x3333, "BW": 0x4444, "SP": 0x3F00,
        "BP": 0x6666, "IX": 0x7777, "IY": 0x8888, "DS0": 0x1000,
        "DS1": 0x2000, "SS": 0x3000, "PSW": 0xF002}

# ModR/M `reg` field -> the STORE_ORDER name of the register it selects.
REGF = {0: "AW", 1: "CW", 2: "DW", 3: "BW", 4: "SP", 5: "BP", 6: "IX",
        7: "IY"}
GPRS = ["AW", "CW", "DW", "BW", "SP", "BP", "IX", "IY"]

CLOCKS = 4200
BODY_PS = 0x0000
BODY_PC = ti.CODE_LO + 0x0100        # 0x8100, inside the v2 code region


def mov_direct_aw(ea):
    """`A3 imm16` -- MOV [imm16],AW.  The rig's own stale-EA probe instruction
    (sw/char_mod3.py: "A3 imm16 = MOV [imm16],AW (EA latch = imm16)")."""
    return bytes([0xA3, ea & 0xFF, (ea >> 8) & 0xFF])


def lea_mod3(reg, rm):
    """`8D` with mod=11."""
    return bytes([0x8D, 0xC0 | (reg << 3) | rm])


class Fail(Exception):
    pass


class Runner:
    def __init__(self, td):
        self.td = td
        self.n = 0

    def dump(self, body, ps=BODY_PS, pc=BODY_PC, ram=None):
        """Compose, replay from RESET, return the 15-word architectural dump."""
        regs = dict(BASE)
        regs["PS"], regs["PC"] = ps, pc
        img, _ = ti.compose(regs=regs, instr=body, ram=ram or [])
        rows = run_boot(bytes(img), CLOCKS, self.td, waits=0)
        self.n += 1
        d = fc.arch_dump(rows, len(rows))
        if d is None:
            raise Fail(f"no architectural dump from body {body.hex()} "
                       f"at {ps:04x}:{pc:04x} ({len(rows)} rows)")
        return d


# --------------------------------------------------------------------------- #
#  L1 / L1b -- the suite's own SILICON rows
# --------------------------------------------------------------------------- #
_PRE_RE = re.compile(r"^MOV\s*\[([0-9A-Fa-f]+)h\]\s*,\s*AW$")


def silicon_rows():
    """The `stale_ea_probe` rows of the suite's metadata, split into the ones
    this gate can ENCODE UNAMBIGUOUSLY (`MOV [imm16],AW`, the rig's own probe
    instruction) and the rest.

    The expected value is read out of the artifact.  Nothing here is a
    literal."""
    meta = json.loads((SUITE / "metadata.json").read_text())
    enc, unenc = [], []
    for row in meta.get("stale_ea_probe", []):
        m = _PRE_RE.match(row["pre"].replace(" ", "").replace(",", " , ")
                          .replace(" , ", ",").replace("MOV", "MOV "))
        if m and int(m.group(1), 16) == row["ea"]:
            enc.append(row)
        else:
            unenc.append(row)
    return meta, enc, unenc


def leg_l1(r, enc, verbose):
    """REGISTERED.  The `match: true` encodable rows, scored to the value."""
    rows = [x for x in enc if x.get("match")]
    if not rows:
        raise Fail("no `match: true` encodable stale_ea_probe row in metadata")
    ok = 0
    for row in rows:
        d = r.dump(mov_direct_aw(row["ea"]) + lea_mod3(6, 7))
        got = d["IX"]
        good = (got == row["si_loaded"] == row["ea"])
        ok += good
        if verbose or not good:
            print(f"  L1  {row['pre']:22s} silicon {row['si_loaded']:#06x}"
                  f"   ucore {got:#06x}   {'MATCH' if good else 'DIFF'}")
    return ok, len(rows)


def leg_l1b(r, unenc, verbose):
    """OBSERVATIONAL, NOT A BAR.  See the module docstring."""
    out = []
    for row in unenc:
        out.append((row["pre"], row["ea"], row["si_loaded"], row.get("match")))
        if verbose:
            print(f"  L1b {row['pre']:22s} silicon si_loaded "
                  f"{row['si_loaded']:#06x}  match={row.get('match')}  "
                  f"(NOT SCORED -- prose `pre`, no certain encoding)")
    return out


# --------------------------------------------------------------------------- #
#  L4 -- the ModR/M-predecessor rows.  KNOWN-RED.  REPORTED, NOT SCORED.
# --------------------------------------------------------------------------- #
#  Encodings INFERRED from the metadata's prose `pre` field, stated here so the
#  inference is reviewable and not buried:
#     "MOV[3010h],AH"  -> 88 26 10 30   (MOV r/m8,r8; mod=00 reg=100 rm=110)
#     "MOV CW,[4455h]" -> 8B 0E 55 44   (MOV r16,r/m16; mod=00 reg=001 rm=110)
#  The load's datum is the image fill the v1 composer laid down everywhere
#  (`fill=0x90`), reproduced here through `compose(ram=...)` so the stimulus is
#  the capture's and not this image's 0xCC code fill.
L4_ROWS = {
    0x3010: (bytes([0x88, 0x26, 0x10, 0x30]), None),
    0x4455: (bytes([0x8B, 0x0E, 0x55, 0x44]), [(0x4455, 0x90), (0x4456, 0x90)]),
}


def leg_l4(r, unenc):
    """Print silicon vs ucore for the rows whose predecessor is a ModR/M form.
    NEVER contributes to the exit status."""
    out = []
    for row in unenc:
        enc = L4_ROWS.get(row["ea"])
        if enc is None:
            out.append((row["pre"], row["si_loaded"], None))
            continue
        d = r.dump(enc[0] + lea_mod3(6, 7), ram=enc[1])
        out.append((row["pre"], row["si_loaded"], d["IX"]))
    for pre, sil, got in out:
        g = "not encodable" if got is None else f"{got:#06x}"
        v = "" if got is None else ("  MATCH" if got == sil else "  ⚠ DIVERGES")
        print(f"  L4  {pre:22s} silicon {sil:#06x}   ucore {g}{v}"
              f"   (REPORTED, NOT A BAR)")
    return out


# --------------------------------------------------------------------------- #
#  L2 -- routing: reg selects, rm does not
# --------------------------------------------------------------------------- #
L2_EA = 0x1234


def leg_l2(r, verbose):
    ok, tot, notes = 0, 0, []
    for reg in range(8):
        name = REGF[reg]
        for rm in range(8):
            tot += 1
            d = r.dump(mov_direct_aw(L2_EA) + lea_mod3(reg, rm))
            moved = {g: d[g] for g in GPRS if d[g] != BASE[g]}
            good = (d[name] == L2_EA and set(moved) <= {name})
            ok += good
            if not good:
                notes.append(f"reg=/{reg}({name}) rm={rm}: {name}="
                             f"{d[name]:#06x} moved={ {k: hex(v) for k, v in moved.items()} }")
            if verbose:
                print(f"  L2  /{reg}({name}) rm{rm}  {name}={d[name]:#06x}  "
                      f"moved={sorted(moved)}  {'ok' if good else 'DIFF'}")
    return ok, tot, notes


# --------------------------------------------------------------------------- #
#  L3 -- non-vacuity
# --------------------------------------------------------------------------- #
def leg_l3(r, verbose):
    res = []

    d = r.dump(mov_direct_aw(L2_EA))                       # C1: no LEA at all
    res.append(("C1 LEA removed -> IX stays loaded",
                d["IX"] == BASE["IX"], f"IX={d['IX']:#06x}"))

    d = r.dump(mov_direct_aw(0xBEEF) + lea_mod3(6, 7))     # C2: different EA
    res.append(("C2 different preceding EA -> different value",
                d["IX"] == 0xBEEF and d["IX"] != L2_EA, f"IX={d['IX']:#06x}"))

    d = r.dump(mov_direct_aw(L2_EA) + lea_mod3(2, 7))      # C3: different reg
    res.append(("C3 /2 moves DW and leaves IX loaded",
                d["DW"] == L2_EA and d["IX"] == BASE["IX"],
                f"DW={d['DW']:#06x} IX={d['IX']:#06x}"))

    for nm, good, detail in res:
        if verbose or not good:
            print(f"  L3  {nm:44s} {detail:28s} {'ok' if good else 'FAIL'}")
    return sum(1 for _, g, _ in res if g), len(res), res


# --------------------------------------------------------------------------- #
def ps_sweep(r):
    """NOT A BAR.  The measurement that makes the PS-sensitivity above a
    statement about the artifact rather than a warning: with no instruction
    before it, the register receives `PC + PS`, because the loader's terminal
    `BR PS:PC` leaves PC on the EA rail and PS on the scratch rail."""
    print("  PS/PC sweep (no preceding EA; NOT a bar):")
    for ps, pc in ((0x0000, ti.CODE_LO + 0x0100), (0x0800, 0x0100),
                   (0x0810, 0x0000)):
        d = r.dump(lea_mod3(6, 7), ps=ps, pc=pc)
        print(f"    PS={ps:#06x} PC={pc:#06x} -> IX={d['IX']:#06x}"
              f"   (PC+PS = {(pc + ps) & 0xFFFF:#06x})"
              f"   {'agrees' if d['IX'] == ((pc + ps) & 0xFFFF) else 'DIFFERS'}")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--ps-sweep", action="store_true",
                    help="also print the PC+PS derivation (not a bar)")
    ap.add_argument("--quick", action="store_true",
                    help="L1 + L3 only (skip the 64-cell routing leg)")
    a = ap.parse_args()

    if not (SUITE / "metadata.json").exists():
        print(f"CANNOT MEASURE: {SUITE}/metadata.json is not on this machine")
        return 2
    try:
        meta, enc, unenc = silicon_rows()
    except Exception as e:                                    # noqa: BLE001
        print(f"CANNOT MEASURE: {e}")
        return 2

    td = tempfile.mkdtemp(prefix="lea_mod3_",
                          dir=str(Path.home() / ".cache" / "ucsimt-tmp"))
    r = Runner(td)
    bad = []
    try:
        l1_ok, l1_n = leg_l1(r, enc, a.verbose)
        if l1_ok != l1_n:
            bad.append(f"L1 SILICON {l1_ok}/{l1_n}")
        l1b = leg_l1b(r, unenc, True)
        l4 = leg_l4(r, unenc)

        if a.quick:
            l2_ok = l2_n = 0
            l2_notes = []
        else:
            l2_ok, l2_n, l2_notes = leg_l2(r, a.verbose)
            if l2_ok != l2_n:
                bad.append(f"L2 ROUTING {l2_ok}/{l2_n}")

        l3_ok, l3_n, _ = leg_l3(r, a.verbose)
        if l3_ok != l3_n:
            bad.append(f"L3 NON-VACUITY {l3_ok}/{l3_n}")

        if a.ps_sweep:
            ps_sweep(r)
    except Fail as e:
        print(f"FAIL: {e}")
        return 1

    print(f"\n  L1  SILICON       {l1_ok}/{l1_n}   "
          f"(the `match: true` rows of {SUITE.name}/metadata.json)")
    print(f"  L1b OBSERVED      {len(l1b)} unscored row(s): "
          + "; ".join(f"{p} si_loaded={s:#06x} match={m}"
                      for p, _, s, m in l1b))
    nd = sum(1 for _, sil, got in l4 if got is not None and got != sil)
    print(f"  L4  KNOWN-RED     {nd} of {len(l4)} ModR/M-predecessor silicon "
          f"row(s) DIVERGE -- REPORTED, NOT A BAR (results doc §4)")
    if not a.quick:
        print(f"  L2  ROUTING       {l2_ok}/{l2_n}   "
              f"(8 reg fields x 8 rm, confinement checked)")
        for n in l2_notes[:8]:
            print(f"        {n}")
    print(f"  L3  NON-VACUITY   {l3_ok}/{l3_n}")
    print(f"  {r.n} whole-program replays, from RESET, no backdoor injection")

    if bad:
        print("FAIL: " + " / ".join(bad))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
