#!/usr/bin/env python3
"""WAVE 10 -- THE CEILING PROBE FOR THE EU -> BIU -> EU ROUND TRIP.

⚠⚠ **EVERY ARM BELOW IS BEHAVIOUR-BREAKING BY CONSTRUCTION.  NO EQUIVALENCE IS
CLAIMED FOR ANY OF THEM.  NONE IS PROPOSED AS A DESIGN.  NOTHING IS LANDED.**
They answer exactly one question -- *what is the MOST this mechanism could ever
be worth?* -- and a real mechanism is a later wave's problem.

WHY A PROBE AND NOT A CENSUS.  WAVE 8 sec.7.6 established the rule the hard way:
its census attributed **3.805 ns** to `ucrom`, and building the substitution out
recovered **0.644** -- **5.9x overstated**, because a per-name ns figure includes
the interconnect INTO those cells and interconnect is INHERITED by whatever
replaces them.  **A CENSUS RANKS CANDIDATES; IT DOES NOT SIZE THEM.**  WAVE 9's
**2.786 ns** for this round trip is therefore a RANKING, not a size.

THE METHOD THAT HAS EARNED ITS CREDIBILITY: two arms compiled IDENTICALLY,
map-once / fit-once, >= 5 seeds, and the DIFFERENCE quoted -- never a partition
attribution.  WAVE 6 predicted **-9.431 ns** that way and WAVE 7 realised
**-9.413** (a 0.2 % correction), while WAVE 5's out-of-context PARTITION
predictions mispredicted by **+11.3 .. +20.0 ns**.

⚠ AND THIS ONE GOES FURTHER THAN WAVE 6/8's STANDALONE HARNESS: the round trip
LEAVES `v30u_eu`, so a `v30u_eu`-only project cannot contain it (`q_ripe_lead_n`
is an input port there and ports are false-pathed).  The arms are therefore
compiled **IN THE FULL DESIGN**, in a SCRATCH GIT WORKTREE, with the same
driver, the same SDC patch and the same instrument as the reference -- so no
out-of-context transfer is needed at all and the positive control is the
strongest available: **the REF arm IS the design, and must reproduce the
scoreboard.**

WAVE 10 bar K-6: `hdl/` in the MAIN tree is never written.  Everything lives in
`~/.cache/ucsimt-tmp/wave10/`.

usage:
    python3 sw/biu_ceiling_proto.py --gen  --arm qripe_reg
    python3 sw/biu_ceiling_proto.py --equiv --arm qripe_reg     # MUST FAIL (K-4)
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/wave10')
BIU = 'hdl/rtl/ucore/v30u_biu.sv'


def sh(c, cwd=None):
    return subprocess.run(c, shell=True, capture_output=True, text=True, cwd=cwd)


def _sub(path, old, new, n=1):
    t = open(path).read()
    c = t.count(old)
    if c != n:
        raise SystemExit(f'REFUSING: anchor occurs {c} times (expected {n}) in {path}:\n'
                         f'---\n{old}\n---')
    open(path, 'w').write(t.replace(old, new, n))


ARMS = {}


def arm(name):
    def deco(fn):
        ARMS[name] = fn
        return fn
    return deco


# --------------------------------------------------------------------------- #
# THE ANCHOR, verbatim from `hdl/rtl/ucore/v30u_biu.sv`'s THE EU CONTRACT block.
CONTRACT = """wire [3:0] poppable_n = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
assign q_ripe_lead_n  = (poppable_n != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt != 4'd0));"""

COMMIT_ANCHOR = "    r_grn_ttl <= (srst && !ss_we) ? grn_ttl_rst : grn_ttl;"


@arm('qripe_reg')
def _arm_qripe_reg(root):
    """SEVER the round trip by REGISTERING `q_ripe_lead_n`.

    ⚠ BEHAVIOUR-BREAKING.  The EU's clocked step is contracted (F7) to read the
    BIU's NEXT level `_n`; this hands it LAST clock's level instead.  It is the
    HONEST ceiling because it keeps every gate -- the whole `poppable_n` cone,
    its fanin and its fanout all survive -- and moves only the register
    boundary.  What it buys is therefore an upper bound on what a REAL
    reformulation of this arc could buy, minus whatever a real one would have
    to add back.
    """
    p = os.path.join(root, BIU)
    _sub(p, CONTRACT, """wire [3:0] poppable_n = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
// ⚠⚠ WAVE 10 CEILING PROBE `qripe_reg` -- BEHAVIOUR-BREAKING BY CONSTRUCTION.
// NOT A DESIGN, NOT AN EQUIVALENCE, NEVER LANDED.  It severs the EU -> BIU -> EU
// combinational round trip so the arc can be MEASURED without it.  The EU is
// contracted (F7) to read the NEXT level here; this gives it the PREVIOUS one.
wire q_ripe_lead_comb = (poppable_n != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt != 4'd0));
reg  r_q_ripe_lead_probe;
assign q_ripe_lead_n  = r_q_ripe_lead_probe;""")
    _sub(p, COMMIT_ANCHOR, COMMIT_ANCHOR +
         "\n    r_q_ripe_lead_probe <= q_ripe_lead_comb;   // WAVE 10 CEILING PROBE")


@arm('qripe_tie')
def _arm_qripe_tie(root):
    """DELETE the mechanism outright -- the ABSOLUTE upper bound.

    ⚠ BEHAVIOUR-BREAKING, AND MORE OPTIMISTIC THAN `qripe_reg` BY CONSTRUCTION:
    tying the output lets the compiler PRUNE the `poppable_n` cone entirely, so
    the delta it reports includes area no real mechanism gets to delete.  It is
    reported SEPARATELY and never as the ceiling.
    """
    p = os.path.join(root, BIU)
    _sub(p, CONTRACT, """wire [3:0] poppable_n = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
// ⚠⚠ WAVE 10 CEILING PROBE `qripe_tie` -- BEHAVIOUR-BREAKING BY CONSTRUCTION.
// The mechanism is DELETED, not moved.  The absolute upper bound and nothing
// else.  NOT A DESIGN, NOT AN EQUIVALENCE, NEVER LANDED.
wire q_ripe_lead_unused = (poppable_n != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt != 4'd0));
assign q_ripe_lead_n  = 1'b1;""")


# --------------------------------------------------------------------------- #
def gen(name, base):
    if sh("git status --porcelain hdl/ | grep -v '^??'", ROOT).stdout.strip():
        raise SystemExit('REFUSING: the main tree\'s hdl/ carries tracked changes.')
    os.makedirs(SCRATCH, exist_ok=True)
    wt = os.path.join(SCRATCH, 'wt_' + name)
    if os.path.exists(wt):
        sh(f'git worktree remove --force {wt}', ROOT)
        shutil.rmtree(wt, ignore_errors=True)
    r = sh(f'git worktree add --detach {wt} {base}', ROOT)
    if r.returncode:
        raise SystemExit('worktree add failed:\n' + r.stdout + r.stderr)
    head = sh('git rev-parse HEAD', wt).stdout.strip()
    print(f'worktree {wt}\n  at {head}')
    if name != 'ref':
        ARMS[name](wt)
    d = sh(f'git diff --stat -- {BIU}', wt).stdout.strip()
    n = len([l for l in sh(f'git diff -- {BIU}', wt).stdout.split('\n')
             if l[:1] in '+-' and l[:3] not in ('+++', '---')])
    print(f'  arm edit: {n} changed source lines\n  {d}')
    if name != 'ref' and n == 0:
        raise SystemExit('REFUSING: the arm made no edit.')
    if name == 'ref' and n != 0:
        raise SystemExit('REFUSING: the REF worktree is not clean.')
    return wt


def equiv(name):
    """THE ANTI-EQUIVALENCE GATE (K-4).  A PROBE THAT STILL PASSES HAS NOT CUT
    ANYTHING, so `check_core` FAILING is the evidence the path is really
    severed -- and it is REPORTED AS A FAILURE, never excused."""
    wt = os.path.join(SCRATCH, 'wt_' + name)
    if not os.path.isdir(wt):
        raise SystemExit('no worktree ' + wt)
    print(f'=== BUILD: {wt} ===', flush=True)
    r = subprocess.run([sys.executable, 'sw/check_core.py', '--build',
                        '--core', 'ucore'], cwd=wt, capture_output=True, text=True)
    print((r.stdout + r.stderr)[-2500:])
    if r.returncode:
        raise SystemExit('BUILD FAILED -- the probe does not even elaborate.')
    print(f'=== check_core --core ucore --opcodes all --cases 0 on {name} ===', flush=True)
    r = subprocess.run([sys.executable, 'sw/check_core.py', '--core', 'ucore',
                        '--opcodes', 'all', '--cases', '0'],
                       cwd=wt, capture_output=True, text=True, timeout=21600)
    tail = (r.stdout + r.stderr)[-3000:]
    print(tail)
    m = re.search(r'TOTAL:\s+(\d+)/(\d+)', r.stdout)
    tot = m.group(0) if m else 'MISSING'
    print()
    print('  K-4  the probe is BEHAVIOUR-BREAKING and check_core must FAIL')
    print(f'       {tot}   exit {r.returncode}')
    broke = bool(m) and m.group(1) != m.group(2)
    print('       verdict: %s' % ('FAILS as required -- the path really is severed'
                                  if broke else
                                  '*** STILL PASSES -- THE PROBE CUT NOTHING ***'))
    return broke, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--base', default='HEAD')
    ap.add_argument('--gen', action='store_true')
    ap.add_argument('--equiv', action='store_true')
    a = ap.parse_args()
    if a.arm != 'ref' and a.arm not in ARMS:
        print('unknown arm %r; known: ref %s' % (a.arm, ' '.join(sorted(ARMS))))
        return 2
    if a.gen:
        gen(a.arm, a.base)
    if a.equiv:
        equiv(a.arm)
    return 0


if __name__ == '__main__':
    sys.exit(main())
