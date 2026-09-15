#!/bin/bash
# n=9 L1 optimal computation - FULL T sweep [9, 2304] = [Tmin, 9*2^8] to find the
# best L1 (candidate global optimum).  CPU-only, coexists with P1-PILOT (GPU1-bound).
# Self-guarded: waits for any prior n=9 L1 run to exit before starting.
cd "$(dirname "$0")" || exit 1

echo "guard: waiting for prior n=9 L1 runs to finish..."
while pgrep -f 'conj15_l1_range.py 9' >/dev/null; do sleep 30; done
echo "guard: clear. launching n=9 L1 full sweep (T in [9,2304], per-T 60s, 20 workers)"

python conj15_l1_range.py 9 9 2304 60 20 > l1_n9.log 2>&1
echo "exit=$?" >> l1_n9.log
