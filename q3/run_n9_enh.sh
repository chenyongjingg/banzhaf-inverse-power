#!/bin/bash
# n=9 exact-feasibility via ENHANCED model (conj15_feas2.py, 6x faster).  Self-guarded:
# waits for the current standard-model batch3 n=9 run (conj15_feas.py 9 256 7200)
# to exit before starting, to avoid CPU contention.
cd "$(dirname "$0")" || exit 1

echo "guard: waiting for batch3 standard n=9 run to finish..."
while pgrep -f 'conj15_feas.py 9 256 7200' >/dev/null; do sleep 30; done
echo "guard: standard n=9 done. launching enhanced model (2h budget)"

timeout 7500 python conj15_feas2.py 9 256 7200 > conj15_feas2_n9.log 2>&1
echo "exit=$?" >> conj15_feas2_n9.log
