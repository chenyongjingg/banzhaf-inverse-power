"""Re-run the benchmark's F2 configuration at one n, alone on the machine.

The §10.4 benchmark reports "no verdict" for F2 at n = 12 under a common 300 s cap,
with a measured wall time of 655 s.  A separate run of the general monotone model
(`milp_verify.py`, which differs in one respect: it bounds c <= 100000 where
`milp_n8.py` bounds c <= 100) returned a witness for the same n in 270.3 s.  Two
configurations of the same constraint system disagreeing by an order of magnitude
has to be explained rather than papered over, so this script re-runs the benchmark's
own configuration, through the benchmark's own patcher, on an otherwise idle machine.

Usage:

    python code/consistency_check/rerun_f2_config.py n [time_limit]

`_patch_milp_n8` is imported from `benchmark_formulations.py` rather than
re-implemented, so the model executed here is the one the benchmark executed.  The
log is appended to `code/consistency_check/f2_config_rerun.log`.
"""
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
ROOT = CODE.parent
sys.path.insert(0, str(CODE))

import benchmark_formulations as bf  # noqa: E402

LOG = HERE / "f2_config_rerun.log"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    n = int(sys.argv[1])
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 3600

    src, patched = bf._patch_milp_n8(n, budget)
    print(f"n = {n}, budget = {budget}s")
    print(f"c bound in the model: {bf.F2_C_BOUND if hasattr(bf, 'F2_C_BOUND') else 'as in milp_n8.py'}")

    log = open(LOG, "a", encoding="utf-8")
    print(f"=== n={n} budget={budget}s at {time.strftime('%Y-%m-%dT%H:%M:%S')} ===", file=log)
    t0 = time.time()
    row = bf.run_f2(n, budget)
    wall = time.time() - t0
    keep = {k: row.get(k) for k in
            ("n", "formulation", "outcome", "solve_time_s", "wall_time_s", "build_time_s",
             "num_variables", "num_constraints", "c", "solver_status", "solver", "c_bound_used")}
    print(json.dumps(keep, indent=1, default=str), file=log)
    print(f"--- wall {wall:.1f}s ---", file=log)
    log.close()
    print(json.dumps(keep, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
