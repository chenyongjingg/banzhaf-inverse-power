# -*- coding: utf-8 -*-
"""Minimal-scale certification for Conjecture 16: given n and a scale c, decide whether
there exists a simple game v on n voters with Banzhaf index Bz(v) = psi^n (i.e. swings
(2c,...,2c,c)) up to normalization.

Model (Section 7 of the manuscript): variables x(S) in {0,1} for the winning status of
each coalition S, monotonicity x(S) <= x(T) for S subset T, normalization x(empty)=0,
x(N)=1, and the swing equations
    sum_{S notni i} ( x(S u {i}) - x(S) ) = 2c   (i != special)
    sum_{S notni s} ( x(S u {s}) - x(S) ) = c    (s = special, fixed to voter n-1)
Using the swap sum_{S notni i} x(S u {i}) = sum_{S ni i} x(S), each equation becomes a
plain linear sum of the x-variables:
    sum_{S ni i} x(S) - sum_{S notni i} x(S) = 2c   (and = c for the special voter).

Since c is even (Corollary 18), the sweep runs over even c.  CP-SAT (ortools) is exact:
FEASIBLE means a certified existence, INFEASIBLE means a certified non-existence.

Usage:  python min_c_sweep.py <n> <c> [timeout_s]
prints  FEASIBLE / INFEASIBLE / UNKNOWN(timeout), and on FEASIBLE dumps the winning
coalitions as the x(S)=1 mask list.
"""
import sys, time
from ortools.sat.python import cp_model


def decide(n, c, timeout):
    t0 = time.time()
    m = cp_model.CpModel()
    N = 1 << n
    spec = n - 1  # special voter (unique minimal swing c); others 2c

    x = [m.NewBoolVar(f"x{mask}") for mask in range(N)]
    m.Add(x[0] == 0)
    m.Add(x[N - 1] == 1)

    # Monotonicity: x(S) <= x(S u {i})
    for mask in range(N):
        for i in range(n):
            if not (mask & (1 << i)):
                m.Add(x[mask] <= x[mask | (1 << i)])

    # Swing equations via the swap-sum linearization
    for i in range(n):
        tgt = c if i == spec else 2 * c
        in_sum = sum(x[mask] for mask in range(N) if mask & (1 << i))
        out_sum = sum(x[mask] for mask in range(N) if not (mask & (1 << i)))
        m.Add(in_sum - out_sum == tgt)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = 8
    status = solver.Solve(m)
    dt = time.time() - t0
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        wins = [mask for mask in range(N) if solver.Value(x[mask]) == 1]
        print(f"n={n} c={c}  FEASIBLE  ({dt:.1f}s)  #winning={len(wins)}")
        print("winning_masks=" + " ".join(map(str, wins)))
        return True
    if status == cp_model.INFEASIBLE:
        print(f"n={n} c={c}  INFEASIBLE  ({dt:.1f}s)")
        return False
    print(f"n={n} c={c}  UNKNOWN(timeout {timeout}s, {dt:.1f}s)")
    return None


if __name__ == "__main__":
    n = int(sys.argv[1])
    c = int(sys.argv[2])
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 300
    decide(n, c, timeout)
