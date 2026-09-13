#!/usr/bin/env python3
"""WAVE 14 -- THE ARMS FOR THE SPLIT-TREE CEILING PROBE.

⚠⚠ **EVERY ARM BELOW IS BEHAVIOUR-BREAKING BY CONSTRUCTION.  NO EQUIVALENCE IS
CLAIMED FOR ANY OF THEM.  NONE IS PROPOSED AS A DESIGN.  NOTHING IS LANDED.**

THE BASE IS THE **SPLIT** TREE (`850ef46559`, WAVE 13's three edits applied).
WAVE 10 sized this mechanism on the UNSPLIT tree and its cut-tree arm
OVER-ANSWERED: that arm inserted a REGISTER and therefore SUBDIVIDED STAGE 2
(its 25.249 ns arc is BELOW WAVE 9's two-stage ceiling of 27.922).  **THE
DEFINING CONSTRAINT HERE IS THAT NEITHER ARM ADDS A FLOP**, so no new pipeline
stage can exist and the arms answer the question actually asked.

  ARM-T `qripe_tie`   -- WAVE 10's booked-and-never-run probe, verbatim from
                         `sw/biu_ceiling_proto.py`: `q_ripe_lead_n = 1'b1`.
                         ⚠ It OVER-ANSWERS BY PRUNING: a constant lets the
                         compiler delete the `poppable_n` cone AND constant-fold
                         every EU consumer.  The optimistic bound.
  ARM-H `qripe_hold`  -- the SAME function off the REGISTERS that already exist
                         (`poppable`, v30u_biu.sv:842, already drives `q_ripe`).
                         Adds no flop AND prunes nothing: `q_ripe_lead_n` stays
                         live with its whole fanout.  The tighter bound.

Registered in `docs/notes/qripe_split_ceiling_prereg_2026-09-13.md` §1 BEFORE
either was generated, together with the rule that the quoted ceiling is
`min(Δ_T, Δ_H)` -- so the answer cannot be chosen after it is seen.

usage:
    python3 sw/wave14_arms.py --gen --arm base|qripe_tie|qripe_hold
    python3 sw/wave14_arms.py --equiv --arm qripe_tie        # MUST FAIL (P-2)
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
from biu_ceiling_proto import _sub, CONTRACT, BIU, sh   # noqa: E402  one anchor

ROOT = os.path.abspath(os.path.join(HERE, '..'))
SCRATCH = os.path.expanduser('~/.cache/ucsimt-tmp/wave14')
BASE_COMMIT = '850ef46559'

# the REGISTER-sourced form, verbatim from v30u_biu.sv:842 -- it already exists
# and already drives `q_ripe`, which is why ARM-H adds no logic and no flop.
POPPABLE_REG = ("wire [3:0] poppable = (r_grn_ttl != 2'd0) ? "
                "(r_q_cnt - {2'b0, r_grn_n}) : r_q_cnt;")


def arm_qripe_tie(wt):
    """WAVE 10's `qripe_tie`, character for character from biu_ceiling_proto."""
    from biu_ceiling_proto import ARMS
    ARMS['qripe_tie'](wt)


def arm_qripe_hold(wt):
    p = os.path.join(wt, BIU)
    t = open(p).read()
    if t.count(POPPABLE_REG) != 1:
        raise SystemExit('REFUSING: the register-form `poppable` anchor is not '
                         'unique in ' + p)
    _sub(p, CONTRACT, """wire [3:0] poppable_n = (grn_ttl != 2'd0) ? (q_cnt - {2'b0, grn_n}) : q_cnt;
// ⚠⚠ WAVE 14 CEILING PROBE `qripe_hold` -- BEHAVIOUR-BREAKING BY CONSTRUCTION.
// NOT A DESIGN, NOT AN EQUIVALENCE, NEVER LANDED.  It severs the EU -> BIU -> EU
// combinational round trip by sourcing the SAME function from the REGISTERS
// that already exist (`poppable`, above, which already drives `q_ripe`) instead
// of from the procedural next-state view.  The EU is contracted (F7) to read
// the NEXT level here; this gives it the PREVIOUS one.
// ⚠ IT ADDS NO FLOP -- that is the whole point.  WAVE 10's cut-tree arm added
// one and thereby SUBDIVIDED STAGE 2, which is what made its +6.629 ns not the
// round trip's size.  A stage boundary is a register; no register is added
// here, so no stage can be subdivided.
wire q_ripe_lead_unused_n = (poppable_n != 4'd0) ||
                        ((grn_ttl == 2'd1) && (q_cnt != 4'd0));
assign q_ripe_lead_n  = (poppable != 4'd0) ||
                        ((r_grn_ttl == 2'd1) && (r_q_cnt != 4'd0));""")


ARMS = {'qripe_tie': arm_qripe_tie, 'qripe_hold': arm_qripe_hold}


def wt_of(name):
    return os.path.join(SCRATCH, 'wt_' + name)


def gen(name, base):
    if sh("git status --porcelain hdl/ | grep -v '^??'", ROOT).stdout.strip():
        raise SystemExit("REFUSING: the main tree's hdl/ carries tracked changes.")
    os.makedirs(SCRATCH, exist_ok=True)
    wt = wt_of(name)
    if os.path.exists(wt):
        sh(f'git worktree remove --force {wt}', ROOT)
        shutil.rmtree(wt, ignore_errors=True)
    r = sh(f'git worktree add --detach {wt} {base}', ROOT)
    if r.returncode:
        raise SystemExit('worktree add failed:\n' + r.stdout + r.stderr)
    head = sh('git rev-parse HEAD', wt).stdout.strip()
    print(f'worktree {wt}\n  at {head}  (base {base})')
    if name != 'base':
        ARMS[name](wt)
    d = sh(f'git diff --stat -- {BIU}', wt).stdout.strip()
    # ⚠ WAVE 10's counter reads `l[:1] in '+-'`, and in Python `'' in '+-'` is
    # TRUE -- an EMPTY diff splits to [''] and counts as ONE changed line, so a
    # clean reference worktree is refused as dirty.  Measured here, 2026-09-13,
    # the first time this wave asked for an unmodified arm.  `l` must be
    # non-empty before its first character is classified.
    n = len([l for l in sh(f'git diff -- {BIU}', wt).stdout.split('\n')
             if l and l[0] in '+-' and l[:3] not in ('+++', '---')])
    print(f'  arm edit: {n} changed source lines\n  {d}')
    print(sh(f'git diff -- {BIU}', wt).stdout)
    if name != 'base' and n == 0:
        raise SystemExit('REFUSING: the arm made no edit.')
    if name == 'base' and n != 0:
        raise SystemExit('REFUSING: the BASE worktree is not clean.')
    # ⚠ P-3's FIRST CHECK, AT THE SOURCE: no arm may introduce a flop.  A
    # non-blocking assignment inside the BIU's commit block is what WAVE 10's
    # arm added; this refuses one textually before a single fit is spent.
    dif = sh(f'git diff -- {BIU}', wt).stdout
    added = [l for l in dif.split('\n') if l.startswith('+') and not l.startswith('+++')]
    bad = [l for l in added if '<=' in l and not l.lstrip('+').lstrip().startswith('//')]
    print(f'  P-3 source check: {len(added)} added lines, '
          f'{len(bad)} carrying a non-blocking assignment  '
          f'({"OK -- no flop added" if not bad else "*** A FLOP MAY HAVE BEEN ADDED ***"})')
    for l in bad:
        print('    ' + l)
    return wt


def equiv(name):
    """P-2, THE ANTI-EQUIVALENCE GATE.  A PROBE THAT STILL PASSES HAS NOT CUT
    ANYTHING, so `check_core` FAILING is the evidence the path is really
    severed -- and it is REPORTED AS A FAILURE, never excused.  On the BASE arm
    the SAME instrument is the POSITIVE CONTROL and must read 169,000/169,000."""
    wt = wt_of(name)
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
    print(f'  P-2  {name}:  {tot}   exit {r.returncode}')
    if name == 'base':
        ok = bool(m) and m.group(1) == m.group(2)
        print('       POSITIVE CONTROL verdict: %s' %
              ('PASSES -- the instrument says 169,000/169,000 on the unprobed '
               'split tree' if ok else '*** THE CONTROL FAILED -- NO ARM RESULT '
               'IS READABLE ***'))
        return ok, tot
    broke = bool(m) and m.group(1) != m.group(2)
    print('       verdict: %s' % ('FAILS as required -- the path really is severed'
                                  if broke else
                                  '*** STILL PASSES -- THE PROBE CUT NOTHING ***'))
    return broke, tot


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', required=True)
    ap.add_argument('--base', default=BASE_COMMIT)
    ap.add_argument('--gen', action='store_true')
    ap.add_argument('--equiv', action='store_true')
    a = ap.parse_args()
    if a.arm != 'base' and a.arm not in ARMS:
        print('unknown arm %r; known: base %s' % (a.arm, ' '.join(sorted(ARMS))))
        return 2
    if a.gen:
        gen(a.arm, a.base)
    if a.equiv:
        equiv(a.arm)
    return 0


if __name__ == '__main__':
    sys.exit(main())
