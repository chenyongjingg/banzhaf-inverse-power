# -*- coding: utf-8 -*-
"""Conjecture 15 exact-feasibility, ENHANCED model (fallback for n=9+).
Same as conj15_feas.py but additionally imposes the SHARP mirror constraints (M'):
for every pair of non-special voters i,j with w_i >= w_j (w_s strictly minimal, Cor 19),
  |{T subseteq N\\{i,j,s} : q - w_i <= W(T) < q - w_j}| = 0,
  |{T subseteq N\\{i,j,s} : q - w_s - w_i <= W(T) < q - w_s - w_j}| = 0.
These are consequences of the exact hypothesis eta=(2c,...,2c,c) (Cor 20), so they are
valid pruning constraints for the feasibility model.  Usage:
  python conj15_feas2.py [n] [W] [timeout_s]
"""
import sys, time
from ortools.sat.python import cp_model

def model_exists(n, W, timeout):
    t0 = time.time()
    m = cp_model.CpModel()
    N = 1 << n
    w = [m.NewIntVar(1, W, f"w{i}") for i in range(n)]
    for i in range(n-1):
        m.Add(w[i] > w[n-1])
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
    for i in range(n):
        acc = []
        for mm in range(N):
            if mm & (1 << i): continue
            d = m.NewBoolVar(f"d{i}_{mm}")
            b1 = m.NewBoolVar(f"b1{i}_{mm}")
            b2 = m.NewBoolVar(f"b2{i}_{mm}")
            m.Add(SW[mm] + w[i] >= q).OnlyEnforceIf(b1)
            m.Add(SW[mm] + w[i] <= q - 1).OnlyEnforceIf(b1.Not())
            m.Add(SW[mm] <= q - 1).OnlyEnforceIf(b2)
            m.Add(SW[mm] >= q).OnlyEnforceIf(b2.Not())
            m.AddBoolAnd([b1, b2]).OnlyEnforceIf(d)
            m.AddBoolOr([b1.Not(), b2.Not()]).OnlyEnforceIf(d.Not())
            acc.append(d)
        m.Add(eta[i] == sum(acc))
    for i in range(n-1):
        m.Add(eta[i] == 2*c)
    m.Add(eta[n-1] == c)
    # ---- (M') sharp mirror constraints: window [q-w_j, q-w_i) sum-free over N\{i,j,s} ----
    # for each pair i<j of non-special players the symmetry break gives w[j] >= w[i], so the
    # HEAVIER player is j; Cor 20 (M') says the window [q-w_{heavier}, q-w_{lighter}) and its
    # translate by w_s are both free of subset sums of N\{i,j,s}:
    #   P([q-w_j, q-w_i)) = 0  and  P([q-w_s-w_j, q-w_s-w_i)) = 0.
    pairs = [(i, j) for i in range(n-2) for j in range(i+1, n-1)]
    n_mirror = 0
    for (i, j) in pairs:
        rest = [k for k in range(n) if k not in (i, j, n-1)]
        for mask in range(1 << len(rest)):
            T = 0
            for k, r in enumerate(rest):
                if mask & (1 << k):
                    T |= (1 << r)
            # forbid SW[T] in [q-w_j, q-w_i): NOT( SW >= q-w_j AND SW <= q-w_i-1 )
            lo1 = m.NewBoolVar(f"lo_{i}_{j}_{T}")
            m.Add(SW[T] >= q - w[j]).OnlyEnforceIf(lo1)
            m.Add(SW[T] <= q - w[j] - 1).OnlyEnforceIf(lo1.Not())
            hi1 = m.NewBoolVar(f"hi_{i}_{j}_{T}")
            m.Add(SW[T] <= q - w[i] - 1).OnlyEnforceIf(hi1)
            m.Add(SW[T] >= q - w[i]).OnlyEnforceIf(hi1.Not())
            m.AddBoolOr([lo1.Not(), hi1.Not()])     # window 1 sum-free
            # forbid SW[T] in [q-w_s-w_j, q-w_s-w_i)
            lo2 = m.NewBoolVar(f"lo2_{i}_{j}_{T}")
            m.Add(SW[T] >= q - w[n-1] - w[j]).OnlyEnforceIf(lo2)
            m.Add(SW[T] <= q - w[n-1] - w[j] - 1).OnlyEnforceIf(lo2.Not())
            hi2 = m.NewBoolVar(f"hi2_{i}_{j}_{T}")
            m.Add(SW[T] <= q - w[n-1] - w[i] - 1).OnlyEnforceIf(hi2)
            m.Add(SW[T] >= q - w[n-1] - w[i]).OnlyEnforceIf(hi2.Not())
            m.AddBoolOr([lo2.Not(), hi2.Not()])     # window 2 sum-free
            n_mirror += 2
    m.Minimize(sum(w) + q)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = 8
    status = solver.Solve(m)
    el = time.time()-t0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print(f"n={n} W={W}: FEASIBLE! c={solver.Value(c)} q={solver.Value(q)} "
              f"w={[solver.Value(wi) for wi in w]} eta={[solver.Value(e) for e in eta]} "
              f"[{el:.1f}s] ({n_mirror} mirror constraints)", flush=True)
        return True
    elif status == cp_model.INFEASIBLE:
        print(f"n={n} W={W}: INFEASIBLE [{el:.1f}s] ({n_mirror} mirror constraints)", flush=True)
        return False
    else:
        print(f"n={n} W={W}: UNKNOWN (status={status}) [{el:.1f}s] ({n_mirror} mirror constraints)", flush=True)
        return None

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    W = int(sys.argv[2]) if len(sys.argv) > 2 else (1 << (n-1))
    timeout = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    model_exists(n, W, timeout)
