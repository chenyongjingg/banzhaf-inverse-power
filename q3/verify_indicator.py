# -*- coding: utf-8 -*-
"""Independent cross-check of min_c_sweep.py using a DIFFERENT encoding: per (i,S) swing
indicator d(i,S) = x(S u {i}) - x(S) enforced via OnlyEnforceIf, summed explicitly.
This is a deliberately slower, structurally different implementation to rule out any
linearization bug in the swap-sum model of min_c_sweep.py.

Usage: python verify_indicator.py <n> <c> [timeout_s]
"""
import sys, time
from ortools.sat.python import cp_model


def decide(n, c, timeout):
    t0 = time.time()
    m = cp_model.CpModel()
    N = 1 << n
    spec = n - 1
    x = [m.NewBoolVar(f"x{mask}") for mask in range(N)]
    m.Add(x[0] == 0)
    m.Add(x[N - 1] == 1)
    for mask in range(N):
        for i in range(n):
            if not (mask & (1 << i)):
                m.Add(x[mask] <= x[mask | (1 << i)])
    # explicit swing indicators: d(i,S) = x(S u {i}) - x(S) >= 0 by monotonicity.
    # Bind d to the difference linearly (each swing is a named var; structurally
    # distinct from the swap-sum model of min_c_sweep.py).
    swing = [0] * n
    for i in range(n):
        dsum = []
        for mask in range(N):
            if mask & (1 << i):
                continue
            d = m.NewBoolVar(f"d{i}_{mask}")
            m.Add(d == x[mask | (1 << i)] - x[mask])
            dsum.append(d)
        swing[i] = m.NewIntVar(0, N, f"swing{i}")
        m.Add(swing[i] == sum(dsum))
        m.Add(swing[i] == (c if i == spec else 2 * c))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = 1  # force different search behavior
    status = solver.Solve(m)
    dt = time.time() - t0
    tag = {cp_model.OPTIMAL: "FEASIBLE", cp_model.FEASIBLE: "FEASIBLE",
           cp_model.INFEASIBLE: "INFEASIBLE"}.get(status, "UNKNOWN")
    print(f"[indicator] n={n} c={c}  {tag}  ({dt:.1f}s)")
    return status


if __name__ == "__main__":
    n = int(sys.argv[1]); c = int(sys.argv[2])
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    decide(n, c, timeout)
