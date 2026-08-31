#!/bin/bash
# Complete the n=10 minimality certification: c=8 already INFEASIBLE (57s).
# Serial, 8 workers: safe.
cd "$(dirname "$0")" || exit 1
for c in 2 4 6; do
  echo "--- n=10 c=$c ---"
  python min_c_sweep.py 10 "$c" 300 | tee "minc_10_${c}.log"
done
echo "n=10 c in {2,4,6} done" | tee n10_minc.flag
