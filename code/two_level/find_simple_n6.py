"""Search (CP-SAT) for a simple game on n voters with
eta(v) proportional to (2,...,2,1), i.e. Bz(v) = psi^n.

Variables x_S = v(S); monotonicity; and eta_i = sum_{S not containing i}
(x_{S+i} - x_S).  A common scale lambda is fixed in turn.  Existence is
known for 6 <= n <= 18 (Kurz & Napel 2014); no weighted game exists for
any n, which is the theorem of the accompanying note.
"""
from ortools.sat.python import cp_model

import verify_witness_n6


def solve(n, lam, time_limit=300):
    model = cp_model.CpModel()
    masks = list(range(1 << n))
    x = {m: model.NewBoolVar(f"x{m}") for m in masks}
    model.Add(x[0] == 0)
    model.Add(x[(1 << n) - 1] == 1)
    for m in masks:
        for i in range(n):
            if not (m >> i) & 1:
                model.Add(x[m] <= x[m | (1 << i)])
    for i in range(n):
        target = 2 if i < n - 1 else 1
        terms = []
        for m in masks:
            if not (m >> i) & 1:
                terms.append(x[m | (1 << i)])
                terms.append(-x[m])
        model.Add(sum(terms) == lam * target)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 8
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return solver.StatusName(status), None
    winning = [m for m in masks if solver.Value(x[m]) == 1]
    minimal = [m for m in winning
               if not any((m >> i) & 1 and (m ^ (1 << i)) in winning
                          for i in range(n))]
    return solver.StatusName(status), [tuple(i + 1 for i in range(n) if (m >> i) & 1)
                                       for m in sorted(minimal)]


if __name__ == "__main__":
    for n in range(6, 10):
        for lam in range(1, 9):
            status, coalitions = solve(n, lam, 120)
            if coalitions:
                print(f"n={n} lambda={lam}: {status}, {len(coalitions)} minimal winning coalitions")
                print("   ", coalitions)
                eta, complete = verify_witness_n6.check(coalitions)
                print("   verified:", eta, "complete:", complete)
                break
        else:
            print(f"n={n}: no solution with lambda <= 8")
