# -*- coding: utf-8 -*-
"""Exact certification of Observation 10 over ALL simple games (not only weighted ones).

Observation 10 of the manuscript says: if v is a simple game with Bz(v) = psi^n, then every
(n-1)-element coalition is winning.  The evidence recorded for it was (i) exhaustive enumeration
for n = 6 and (ii) a floating-point MILP with a 60 s time limit for n = 7, 8, which reported the
model infeasible once the constraint "some (n-1)-set is losing" was added.  Two things are weaker
there than the heading "verified for n <= 8" suggests:

  * the MILP is scipy/HiGHS in double precision under a time limit, so its INFEASIBLE is a
    solver verdict rather than a certificate;
  * the constraint pinned ONE (n-1)-set (N \\ {0}) as losing.  The symmetry group of the problem
    permutes {0..n-2} only, because the special player's swing count is c and everyone else's is
    2c, so "some (n-1)-set is losing" has exactly TWO inequivalent cases, and only one was tested.

This script decides both cases exactly, in integer arithmetic, with CP-SAT -- the same instrument
the manuscript already uses for the certification of Section 9.  Variables are one Boolean per
coalition, so the model ranges over every monotone Boolean function, not over weighted games.

  Case A: N \\ {j} losing for a NON-special j   (all such j are equivalent by symmetry)
  Case B: N \\ {s} losing for the special player s = n-1

If both are INFEASIBLE then Observation 10 holds for that n as a finite statement about all simple
games on n voters.  UNKNOWN is reported as UNKNOWN: a time limit is not a proof.

Usage: python certify_obs10.py [nmin] [nmax] [timeout_s] [workers]
"""
import sys
import time

from ortools.sat.python import cp_model


def decide(n, case, timeout, workers, seed=None, symmetry_break=True):
    """Return (verdict, c_value, seconds).  verdict is 'INFEASIBLE', 'FEASIBLE' or 'UNKNOWN'."""
    model = cp_model.CpModel()
    N = 1 << n
    full = N - 1
    special = n - 1
    x = [model.NewBoolVar("x%d" % m) for m in range(N)]
    model.Add(x[0] == 0)
    model.Add(x[full] == 1)
    # v is a simple game: monotone Boolean function
    for m in range(N):
        for i in range(n):
            if not (m >> i) & 1:
                model.Add(x[m] <= x[m | (1 << i)])
    # swing counts proportional to (2,...,2,1)
    c = model.NewIntVar(1, N, "c")
    for i in range(n):
        terms = [x[m | (1 << i)] - x[m] for m in range(N) if not (m >> i) & 1]
        model.Add(sum(terms) == (c if i == special else 2 * c))
    # (a run with case="none" keeps only this block, and is the positive control: the model must be
    #  feasible there, since the manuscript exhibits simple games with Bz(v) proportional to psi^n)
    # the losing (n-1)-set whose existence the observation denies
    j = 0 if case == "A" else special
    if case != "none":
        model.Add(x[full & ~(1 << j)] == 0)
    # Symmetry break: the Banzhaf coefficients of the non-special players are all equal, so the
    # group permuting {0..n-2} is a symmetry of the whole model for both cases, and the (n-1)-sets
    # that omit a non-special player may be taken in this order.  In case A it is applied after
    # fixing x(N\\{0}) = 0, whose stabiliser still permutes {1..n-2} freely.
    # The break is a convenience, not part of the claim: every run is repeated with it switched off
    # (`--no-break`), and an infeasibility that survives without it is an infeasibility of the
    # unbroken model.  Removing a valid symmetry break can only slow the search down.
    if symmetry_break:
        for i in range(n - 2):
            model.Add(x[full & ~(1 << i)] <= x[full & ~(1 << (i + 1))])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = float(timeout)
    solver.parameters.num_search_workers = workers
    if seed is not None:
        solver.parameters.random_seed = seed
    t0 = time.time()
    status = solver.Solve(model)
    dt = time.time() - t0
    if status == cp_model.INFEASIBLE:
        return "INFEASIBLE", None, dt
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return "FEASIBLE", solver.Value(c), dt
    return "UNKNOWN", None, dt


def main():
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 3600
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    brk = "--no-break" not in sys.argv
    print("CONFIG n = %d..%d, timeout = %ds, workers = %d, symmetry break %s"
          % (nmin, nmax, timeout, workers, "on" if brk else "OFF"))
    all_certified = True
    for n in range(nmin, nmax + 1):
        row = []
        for case in ("A", "B"):
            verdict, cv, dt = decide(n, case, timeout, workers, symmetry_break=brk)
            if verdict != "INFEASIBLE":
                all_certified = False
            row.append("%s: %s (%.1fs%s)" % (case, verdict, dt,
                                             "" if cv is None else ", c = %d" % cv))
        print("n = %2d  %s" % (n, "   ".join(row)))
        sys.stdout.flush()
    print("OBS10 CERTIFICATION: %s" % ("both cases infeasible for every n tested -- "
                                       "Observation 10 holds for n = %d..%d over all simple games"
                                       % (nmin, nmax) if all_certified else
                                       "NOT CERTIFIED for every n tested -- see the rows above"))


if __name__ == "__main__":
    main()
