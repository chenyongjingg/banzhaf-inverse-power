#!/bin/bash
# Serial downward sweep for n=15 minimal c (c=20 already certified FEASIBLE).
# Stop at the first INFEASIBLE: then minimal c = that value + 2 (even).
# Serial + 8 workers only: no CPU oversubscription, safe alongside StrongREJECT.
cd "$(dirname "$0")" || exit 1
for c in 18 16 14 12 10 8 6 4 2; do
  echo "--- testing c=$c ---"
  python min_c_sweep.py 15 "$c" 600 | tee "minc_15_${c}.log"
  if grep -q INFEASIBLE "minc_15_${c}.log"; then
    echo "n=15 minimal c certified: $((c + 2))  (c=$c infeasible)" | tee minc_15_result.txt
    exit 0
  fi
done
echo "all of 2..18 feasible?? (should not happen)" | tee minc_15_result.txt
