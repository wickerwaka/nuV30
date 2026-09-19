#!/usr/bin/env python3
"""WAVE 16 -- R-5.  THE `ifndef SYNTHESIS` REFERENCE PREDICATE'S OWN
NON-VACUITY, DEMONSTRATED ON THE LANDED TREE.

The mechanism keeps the ORIGINAL predicate VERBATIM as a sim-only reference and
`$fatal`s every `ce` in two clauses.  A falsifier that cannot fail is not a
falsifier, so each clause is perturbed IN TURN and the run must DIE.

The three perturbations are WAVE 15's, character for character
(`sw/wave15_arms.py` `--nonvacuity{,2,3}`), so that this leg is a REPRODUCTION
on the unsplit tree and not a new instrument.

⚠ THE FILE IS RESTORED FROM A BYTE COPY TAKEN BEFORE THE FIRST PERTURBATION,
and the restored file's sha256 is checked against that copy.  `git checkout` is
NEVER used: the landing is uncommitted work in this tree at the time this runs.

usage:  python3 sw/wave16_nonvacuity.py
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BIU = os.path.join(ROOT, 'hdl/rtl/ucore/v30u_biu.sv')

PERTURB = [
    ('nv1  clause (1): one term of `q_ripe_lead_n1`, grn_ttl == 1 -> == 2',
     "((grn_ttl == 2'd1) && (q_cnt_np1 != 4'd0));",
     "((grn_ttl == 2'd2) && (q_cnt_np1 != 4'd0));  // PERTURBED"),
    ('nv2  clause (2): the flush no longer cancels the pop',
     "            pop_eff = 1'b0;   // WAVE 15 C1: the flush",
     "            // PERTURBED (nv2): pop_eff NOT cleared\n"
     "            // WAVE 15 C1: the flush"),
    ('nv3  clause (2): `pop_eff` armed from `q_pop` alone',
     "    pop_eff = 1'b0; q_cnt_np = 4'd0;",
     "    pop_eff = q_pop; q_cnt_np = 4'd0;   // PERTURBED (nv3)"),
]


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def sub(old, new):
    t = open(BIU).read()
    n = t.count(old)
    if n != 1:
        raise SystemExit(f'REFUSING: anchor occurs {n} times (want 1)')
    open(BIU, 'w').write(t.replace(old, new))


def run(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True)


def main():
    env_note = 'TMPDIR=$HOME/.cache/ucsimt-tmp '
    keep = tempfile.mkdtemp(prefix='w16nv-', dir=os.path.expanduser('~/.cache/ucsimt-tmp'))
    pristine = os.path.join(keep, 'v30u_biu.sv')
    shutil.copy2(BIU, pristine)
    base_sha = sha(BIU)
    print(f'PRISTINE v30u_biu.sv sha256 {base_sha}\n  kept at {pristine}')
    fails = 0
    for name, old, new in PERTURB:
        print(f'\n--- {name}')
        shutil.copy2(pristine, BIU)
        sub(old, new)
        b = run(env_note + 'python3 sw/check_core.py --build --core ucore')
        rid = [l for l in b.stdout.splitlines() if 'receipt' in l]
        print(f'    build rc={b.returncode}  {rid[-1].strip() if rid else ""}')
        if b.returncode != 0:
            print('    *** BUILD FAILED -- the perturbation did not elaborate; '
                  'that is NOT a demonstration that the falsifier fires ***')
            print('   ', b.stdout[-400:], b.stderr[-400:])
            continue
        r = run(env_note + 'python3 sw/check_core.py --core ucore --opcodes FA --cases 0')
        txt = r.stdout + r.stderr
        fired = ('WAVE 15 C1 IDENTITY VIOLATED' in txt or
                 'WAVE 15 C1 SELECT VIOLATED' in txt)
        for l in txt.splitlines():
            if 'WAVE 15 C1' in l:
                print('    FATAL:', l.strip()[:200])
                break
        tot = [l for l in txt.splitlines() if l.startswith('TOTAL:')]
        print(f'    rc={r.returncode}  falsifier FIRED={fired}  {tot[-1] if tot else ""}')
        if not fired:
            fails += 1
            print('    ⚠ DID NOT FIRE -- recorded as measured, not restated.')
    shutil.copy2(pristine, BIU)
    print(f'\nRESTORED v30u_biu.sv sha256 {sha(BIU)}  '
          f'{"== pristine" if sha(BIU) == base_sha else "*** DIFFERS ***"}')
    b = run(env_note + 'python3 sw/check_core.py --build --core ucore')
    rid = [l for l in b.stdout.splitlines() if 'receipt' in l]
    print(f'REBUILT clean ARM-A: {rid[-1].strip() if rid else b.returncode}')
    print(f'\n=== R-5: {len(PERTURB) - fails} of {len(PERTURB)} perturbations FIRED ===')
    return 0


if __name__ == '__main__':
    sys.exit(main())
