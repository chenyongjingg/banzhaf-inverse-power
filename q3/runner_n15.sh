#!/bin/bash
# Sweep n=15 downward from c=18 to find the true minimum (c=20 already FEASIBLE).
cd "$(dirname "$0")" || exit 1
for c in 18 16 14 12 10 8 6 4 2; do
  python min_c_sweep.py 15 "$c" 600 > "minc_15_${c}.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 4 ]; do wait -n; done
done
wait
echo "=== n=15 downward sweep done ==="
cat minc_15_1*.log minc_15_1[2468].log minc_15_2.log minc_15_4.log minc_15_6.log minc_15_8.log 2>/dev/null
