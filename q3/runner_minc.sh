#!/bin/bash
# Parallel minimal-c certification sweep (max 4 concurrent CP-SAT tasks, 8 workers each)
cd "$(dirname "$0")" || exit 1
jobs=( "9 4" "9 2" "10 8" "11 12" "12 14" "15 20" )
rm -f minc_*.log
for j in "${jobs[@]}"; do
  set -- $j
  n=$1; c=$2
  python min_c_sweep.py "$n" "$c" 900 > "minc_${n}_${c}.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 4 ]; do wait -n; done
done
wait
echo "=== summary ==="
cat minc_*.log
