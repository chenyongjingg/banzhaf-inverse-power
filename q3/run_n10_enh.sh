#!/bin/bash
# n=10 exact-feasibility via ENHANCED model (conj15_feas2.py with (M') mirror constraints).
# Self-guarded: waits for batch3 standard n=10 (conj15_feas.py 10 512 7200) to exit before
# starting, to avoid CPU contention.  Solver budget 14400s (4h) - n=9 took 1562s, expect
# several hours at n=10.
cd "$(dirname "$0")" || exit 1

echo "guard: waiting for batch3 standard n=10 run to finish..."
while pgrep -f "conj15_feas.py 10 512" >/dev/null; do sleep 30; done
echo "guard: standard n=10 done. launching enhanced model (4h budget)"

timeout 15000 python conj15_feas2.py 10 512 14400 > conj15_feas2_n10.log 2>&1
echo "exit=$?" >> conj15_feas2_n10.log
