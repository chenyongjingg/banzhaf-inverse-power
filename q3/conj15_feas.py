# -*- coding: utf-8 -*-
"""Conjecture 15 exact-feasibility: does there exist a weighted majority game [q;w]
whose Banzhaf swings are exactly (2c,...,2c,c) (= psi^n, special player = n)?
Uses OR-Tools CP-SAT. Usage: python conj15_feas.py [n] [W] [timeout_s] [workers] [seed]
Weight bound: Muroga (1971, proof of Thm 9.3.2.1) gives an integer representation with
0 <= w_i <= alpha_n, alpha_n = the largest determinant of an n x n 0-1 matrix, and
alpha_n = 9, 32, 56, 144, 320 for n = 6..10 -- each <= 2^(n-1).  So W = 2^(n-1) is
conclusive for n <= 10, the range the paper claims.  It is NOT conclusive at n = 11
(alpha_11 = 1458 > 2^10 = 1024), which is why verdicts there are budgeted and are
labelled Tier 3 in the manuscript.
The last two arguments are optional and default to 8 workers and CP-SAT's own default
seed, the configuration behind the published n <= 10 verdicts; larger worker counts
let a bigger machine run the same model at n = 11 and beyond, and the seed is exposed
so two machines can be compared without sharing a search path.  The verdict line
prints the configuration, so a log carries its own provenance.
"""
import sys, time
from ortools.sat.python import cp_model

def model_exists(n, W, timeout, workers=8, seed=None):
    t0 = time.time()
    m = cp_model.CpModel()
    N = 1 << n
    w = [m.NewIntVar(1, W, f"w{i}") for i in range(n)]
    # special player n-1 strictly minimal (Corollary 6 of the manuscript)
    for i in range(n-1):
        m.Add(w[i] > w[n-1])
    # symmetry break: all non-special players have equal target swing (2c), so relabel
    # them in nondecreasing weight order (any solution can be relabeled to satisfy this)
    for i in range(n-2):
        m.Add(w[i] <= w[i+1])
    q = m.NewIntVar(1, n*W, "q")
    c = m.NewIntVar(1, n*W, "c")
    SW = [None]*N
    SW[0] = m.NewIntVar(0, n*W, "SW0")
    m.Add(SW[0] == 0)
    for mm in range(1, N):
        lb = mm & (-mm)
        i = lb.bit_length()-1
        SW[mm] = m.NewIntVar(0, n*W, f"SW{mm}")
        m.Add(SW[mm] == SW[mm ^ lb] + w[i])
    eta = [m.NewIntVar(0, N, f"eta{i}") for i in range(n)]
    # swing indicators
    for i in range(n):
        acc = []
        for mm in range(N):
            if mm & (1 << i): continue
            d = m.NewBoolVar(f"d{i}_{mm}")
            b1 = m.NewBoolVar(f"b1{i}_{mm}")
            b2 = m.NewBoolVar(f"b2{i}_{mm}")
            # b1: SW >= q - w[i]  i.e. SW + w[i] - q >= 0
            m.Add(SW[mm] + w[i] >= q).OnlyEnforceIf(b1)
            m.Add(SW[mm] + w[i] <= q - 1).OnlyEnforceIf(b1.Not())
            # b2: SW <= q - 1
            m.Add(SW[mm] <= q - 1).OnlyEnforceIf(b2)
            m.Add(SW[mm] >= q).OnlyEnforceIf(b2.Not())
            m.AddBoolAnd([b1, b2]).OnlyEnforceIf(d)
            m.AddBoolOr([b1.Not(), b2.Not()]).OnlyEnforceIf(d.Not())
            acc.append(d)
        m.Add(eta[i] == sum(acc))
    for i in range(n-1):
        m.Add(eta[i] == 2*c)
    m.Add(eta[n-1] == c)
    # objective: none (feasibility). give solver a hint toward small weights via a dummy objective
    m.Minimize(sum(w) + q)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = workers
    if seed is not None:
        solver.parameters.random_seed = seed
    status = solver.Solve(m)
    el = time.time()-t0
    cfg = f"{workers} workers, seed {seed}"
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"n={n} W={W}: FEASIBLE (a weighted game realizes psi^n!) c={solver.Value(c)} "
              f"q={solver.Value(q)} w={[solver.Value(wi) for wi in w]} "
              f"eta={[solver.Value(e) for e in eta]} [{el:.1f}s] ({cfg})", flush=True)
        return True
    elif status == cp_model.INFEASIBLE:
        print(f"n={n} W={W}: INFEASIBLE - no weighted game realizes psi^n [{el:.1f}s] ({cfg})",
              flush=True)
        return False
    else:
        print(f"n={n} W={W}: UNKNOWN (status={status}) [{el:.1f}s] ({cfg})", flush=True)
        return None

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    W = int(sys.argv[2]) if len(sys.argv) > 2 else (1 << (n-1))
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    seed = int(sys.argv[5]) if len(sys.argv) > 5 else None
    model_exists(n, W, timeout, workers, seed)
