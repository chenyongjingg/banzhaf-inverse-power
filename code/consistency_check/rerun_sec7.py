"""Longer-budget rerun of the Section 7 MILP instances.

Section 7 reports that the general monotone MILP of `milp_verify.py` found realizing
games for n in {8, 10, 11, 12, 15}.  The benchmark of Section 10.4 runs the same
model under a common 300 s cap, where the n = 12 instance returns no verdict.  This
script re-runs the three instances that are in neither the benchmark set nor the
obstruction range (n = 11, 12, 15) with a per-instance budget of 3600 s, so that the
frontier reported in Section 10.4 can be compared against the budget Section 7 was
run under.

Measured on the same machine as the benchmark (Python 3.14.4, scipy 1.17.1,
HiGHS 1.12.0), 2026-09-14:

    n = 11   OPTIMAL   25.9 s   c = 14   (matches the appendix dataset)
    n = 12   see code/consistency_check/sec7_rerun.log
    n = 15   see code/consistency_check/sec7_rerun.log

Each instance is a separate process, so a solver that overruns its own time limit is
still bounded by an outer `timeout`.  The log is appended, not overwritten, so a
re-run is visible next to the previous one.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
LOG = HERE / "sec7_rerun.log"
BUDGET = 3600
OUTER = BUDGET + 300
NS = [11, 12, 15]

log = open(LOG, "a", encoding="utf-8")
print(f"writing to {LOG}", file=sys.stderr)
for n in NS:
    header = f"=== n={n}  budget={BUDGET}s  at {time.strftime('%Y-%m-%dT%H:%M:%S')} ==="
    print(header, file=log, flush=True)
    t0 = time.time()
    try:
        r = subprocess.run(
            [sys.executable, str(CODE / "milp_verify.py"), str(n), str(BUDGET)],
            capture_output=True, text=True, timeout=OUTER, cwd=str(CODE.parent),
        )
        out = (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        out = f"(killed at the outer {OUTER}s cap; the solver never returned)\n"
    print(out.rstrip(), file=log, flush=True)
    print(f"--- wall {time.time() - t0:.1f}s ---", file=log, flush=True)
log.close()
print("done", file=sys.stderr)
