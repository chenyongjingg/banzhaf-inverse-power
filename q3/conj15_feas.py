# -*- coding: utf-8 -*-
"""Conjecture 15 exact-feasibility: does there exist a weighted majority game [q;w]
whose Banzhaf swings are exactly (2c,...,2c,c) (= psi^n, special player = n)?
Uses OR-Tools CP-SAT. Usage: python conj15_feas.py [n] [W] [timeout_s]
Weight bound: minimal integer reps have w_i <= 2^(n-1) (classical), so W=2^(n-1) is conclusive.
"""
import sys, time
from ortools.sat.python import cp_model

def model_exists(n, W, timeout):
    t0 = time.time()
    m = cp_model.CpModel()
    N = 1 << n
    w = [m.NewIntVar(1, W, f"w{i}") for i in range(n)]
    # special player n-1 strictly minimal (Corollary 19)
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
    solver.parameters.num_search_workers = 8
    status = solver.Solve(m)
    el = time.time()-t0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"n={n} W={W}: FEASIBLE (a weighted game realizes psi^n!) c={solver.Value(c)} "
              f"q={solver.Value(q)} w={[solver.Value(wi) for wi in w]} "
              f"eta={[solver.Value(e) for e in eta]} [{el:.1f}s]", flush=True)
        return True
    elif status == cp_model.INFEASIBLE:
        print(f"n={n} W={W}: INFEASIBLE - no weighted game realizes psi^n [{el:.1f}s]", flush=True)
        return False
    else:
        print(f"n={n} W={W}: UNKNOWN (status={status}) [{el:.1f}s]", flush=True)
        return None

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    W = int(sys.argv[2]) if len(sys.argv) > 2 else (1 << (n-1))
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    model_exists(n, W, timeout)
