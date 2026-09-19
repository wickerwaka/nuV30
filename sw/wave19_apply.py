#!/usr/bin/env python3
"""WAVE 19 -- APPLY ARM-B, MECHANICALLY, AND PROVE THE RESULT IS THE MEASURED
ARTIFACT RATHER THAN SOMETHING I TYPED.

Two edits and no others:

  1. `hdl/rtl/ucore/v30u_eu.sv` <- `sw/testdata/wave19/armb_delta.diff`, the
     7-hunk one-file patch committed WITH the pre-registration.  The result is
     then required to be sha256 `31ff3a50f503da77...`, which is WAVE 15's ARM-B
     arm -- the tree that drew 34.48 / 34.41.  ⚠ A patch that applies is not a
     patch that applied CORRECTLY; the hash is what says so.

  2. `sw/ss_flop_whitelist_ucore.txt`, the `s1q` entry's JUSTIFICATION.  NO
     ENTRY IS ADDED.  The cone now reads an EIGHTH registered BIU view,
     `q_ripe`, and a justification that does not name it would be untrue.

`--check` verifies without writing; `--apply` writes.  Either way it REFUSES
rather than guesses, and it prints what it measured.
"""
import hashlib
import subprocess
import sys

EU = 'hdl/rtl/ucore/v30u_eu.sv'
WL = 'sw/ss_flop_whitelist_ucore.txt'
DELTA = 'sw/testdata/wave19/armb_delta.diff'

SHA_BEFORE = 'c70dee375f9b9df54aecddacff0382dc313184f032795387f9f567d7ae1961b1'
SHA_AFTER = '31ff3a50f503da773796a644308095e0af668a8b383cd85bb2bca10e8fb698c3'

WL_OLD = ("widened from 495 to 778 bits by the CUT SET (A-1)). It is STAGE 1 of "
          "the next-state cone -- a pure function of `ce`-committed registers, "
          "the EU's own and the seven REGISTERED BIU views the wire cone reads "
          "(eu_access_active / eu_opr_free / eu_rd_done_n / eu_slot_busy / "
          "eu_wr_done_n / eu_wr_eval / q_byte), ALL of which are SSA-mapped on "
          "their own side")

WL_NEW = ("widened from 495 to 778 bits by the CUT SET (A-1), and to 779 by "
          "WAVE 19's ARM-B, whose ONE added bit `qripe_pop` is the 1BL-lead "
          "select `q_pop && q_ripe && !q_flush` -- a WIDENING OF THIS ENTRY, "
          "NOT A NEW ONE). It is STAGE 1 of the next-state cone -- a pure "
          "function of `ce`-committed registers, the EU's own and the EIGHT "
          "REGISTERED BIU views the wire cone reads (eu_access_active / "
          "eu_opr_free / eu_rd_done_n / eu_slot_busy / eu_wr_done_n / "
          "eu_wr_eval / q_byte / q_ripe -- the eighth arrived with ARM-B and is "
          "`poppable != 4'd0` at v30u_biu.sv:848 over r_grn_ttl / r_q_cnt / "
          "r_grn_n, whose addresses are SSA_B_GRN_TTL / SSA_B_Q_CNT / "
          "SSA_B_GRN_N at v30u_biu.sv:2858-2860), ALL of which are SSA-mapped "
          "on their own side")


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    apply_ = '--apply' in sys.argv
    if not apply_ and '--check' not in sys.argv:
        print(__doc__)
        return 2

    eu = sha(EU)
    print(f'{EU}\n  sha256 now      {eu}')
    wl = open(WL).read()

    if eu == SHA_AFTER:
        print('  ALREADY ARM-B   (the delta is applied)')
        patched = True
    elif eu == SHA_BEFORE:
        print(f'  expected-before {SHA_BEFORE}   OK')
        patched = False
    else:
        print('  *** REFUSING: this file is NEITHER the pre-edit tree NOR ARM-B. ***')
        return 3

    hits = wl.count(WL_OLD)
    done = wl.count(WL_NEW)
    print(f'{WL}\n  old justification occurrences: {hits}   new: {done}')
    if hits + done != 1:
        print('  *** REFUSING: the `s1q` justification is neither the '
              'pre-edit text exactly once nor already amended exactly once. ***')
        return 3

    if not apply_:
        print('\n--check only; nothing written.')
        return 0

    if not patched:
        r = subprocess.run(['git', 'apply', DELTA], capture_output=True, text=True)
        if r.returncode:
            print('  *** git apply FAILED ***\n' + r.stderr)
            return 3
        got = sha(EU)
        print(f'  patched -> {got}')
        if got != SHA_AFTER:
            print(f'  *** REFUSING: expected {SHA_AFTER}.  The patch applied but '
                  'the bytes are not WAVE 15\'s ARM-B arm. ***')
            return 3
        print('  ✔ BYTE-IDENTICAL TO WAVE 15\'s ARM-B ARM')

    if hits == 1:
        open(WL, 'w').write(wl.replace(WL_OLD, WL_NEW))
        print('  ✔ `s1q` justification amended (NO ENTRY ADDED)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
