#!/bin/bash
# Re-run of the minimal-scale certification sweeps quoted in Paper A ("minimality is
# certified for n = 8 (c = 8, with c in {2,4,6} infeasible), n = 9 (c = 6, c in {2,4}
# infeasible) and n = 10 (c = 10, c in {2,4,6,8} infeasible)"), plus the n = 15, c = 18
# downward sweep Paper A reports as not terminating within a 600 s solver budget.
#
# Logs land in q3/recheck/ with names that say what they are. Nothing is deleted.
#
# Usage:   ./rerun_minc_20260922.sh [budget]      re-run the sweeps and print the summary
#          ./rerun_minc_20260922.sh --summary-only  print the summary from logs already on disk
#
# `--summary-only` exists because the summary loop globs this directory, so if the caller
# redirects the script's own stdout into it (e.g. `> recheck/rerun_minc_driver.log`) the loop
# reaches its own output file and reads it half-written. The first driver log was produced that
# way and its last line was an artefact of exactly that: `tail -1` on the partially flushed file
# returned the previous row's text. The glob below skips the driver log by name, and
# `--summary-only` regenerates the summary from the per-case logs without re-solving anything.
cd "$(dirname "$0")" || exit 1
OUT=recheck
mkdir -p "$OUT"
DRIVER="$OUT/rerun_minc_driver.log"

summary() {
  echo "=== summary ==="
  for f in "$OUT"/rerun_minc_*.log; do
    [ "$f" = "$DRIVER" ] && continue
    printf '%-34s %s\n' "$(basename "$f")" "$(tail -1 "$f")"
  done
}

if [ "$1" = "--summary-only" ]; then
  summary
  exit 0
fi

BUDGET=${1:-900}

jobs=( "8 2" "8 4" "8 6" "9 2" "9 4" "10 2" "10 4" "10 6" "10 8" )
for j in "${jobs[@]}"; do
  set -- $j
  n=$1; c=$2
  python min_c_sweep.py "$n" "$c" "$BUDGET" > "$OUT/rerun_minc_${n}_${c}.log" 2>&1 &
  while [ "$(jobs -r | wc -l)" -ge 3 ]; do wait -n; done
done
# n = 15 at the c = 18 bound Paper A names, under that paper's own 600 s budget.
python min_c_sweep.py 15 18 600 > "$OUT/rerun_minc_15_18.log" 2>&1
wait
summary
