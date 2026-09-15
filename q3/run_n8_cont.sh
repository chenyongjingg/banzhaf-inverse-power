#!/bin/bash
# n=8 L1 continuation: sweep T in [201, 1024] to certify global optimality of the
# T=60 / 0.066667 finding.  Self-guarded: waits for the current n=8 sweep
# (l1_n8.log writer / conj15_l1.py 8 200 ...) to exit before starting.
cd "$(dirname "$0")" || exit 1

echo "guard: waiting for current n=8 sweep (T<=200) to finish..."
while pgrep -f 'conj15_l1.py 8 200' >/dev/null; do sleep 30; done
echo "guard: n=8 T<=200 sweep finished. launching continuation T in [201,1024]"

python conj15_l1_range.py 8 201 1024 90 10 > l1_n8_cont.log 2>&1
echo "exit=$?" >> l1_n8_cont.log
