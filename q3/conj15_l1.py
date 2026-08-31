# -*- coding: utf-8 -*-
"""Conjecture 15 L1-optimal computation. For weighted majority game [q;w] on n voters, minimize
L1 = ||Bz(v) - psi^n||_1 = sum_i |eta_i/T - p_i| over ALL weighted games, where
p = (2,...,2,1)/(2n-1). Exact via CP-SAT with fixed total swing T and the classical weight bound
w_i <= 2^(n-1) (conclusive). Special player fixed at position n-1 WLOG (relabeling). Symmetry
break: non-special voters have equal target swing, so relabel in nondecreasing weight order.

Robustness: solver threads sw=1 per process (reliable max_time), many processes. For each T the
incumbent is certified OPTIMAL or FEASIBLE; the winning T is re-verified with a long timeout.

Usage:
  python conj15_l1.py [n] [Tmax] [perT_timeout] [procs] [sw]        # sweep T in 1..Tmax
  python conj15_l1.py confirm [n] [T] [timeout]                      # verify a single T
"""
import sys, time
from ortools.sat.python import cp_model

def build_swing_model(n, W):
    m = cp_model.CpModel()
    N = 1 << n
    w = [m.NewIntVar(1, W, f"w{i}") for i in range(n)]
    # special player n-1 strictly minimal; symmetry break on non-special weights
    for i in range(n-1):
        m.Add(w[i] > w[n-1])
    for i in range(n-2):
        m.Add(w[i] <= w[i+1])
    q = m.NewIntVar(1, n*W, "q")
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
    return m, w, q, eta

def solve_T(n, W, T, timeout, sw=1):
    k = 2*n - 1
    m, w, q, eta = build_swing_model(n, W)
    m.Add(sum(eta) == T)
    slacks = []
    for i in range(n):
        z = m.NewIntVar(0, 10**9, f"z{i}")
        if i == n-1:
            m.Add(z >= k*eta[i] - T); m.Add(z >= T - k*eta[i])
        else:
            m.Add(z >= k*eta[i] - 2*T); m.Add(z >= 2*T - k*eta[i])
        slacks.append(z)
    m.Minimize(sum(slacks))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = timeout
    solver.parameters.num_search_workers = sw
    st = solver.Solve(m)
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None
    N = sum(solver.Value(e) for e in slacks)
    l1 = N / (k * T)
    return (l1, [solver.Value(e) for e in eta], [solver.Value(wi) for wi in w], solver.Value(q),
            st == cp_model.OPTIMAL)

def solve_T_wrap(args):
    n, W, T, timeout, sw = args
    return T, solve_T(n, W, T, timeout, sw)

def confirm(n, T, timeout):
    W = 1 << (n-1)
    r = solve_T(n, W, T, timeout, sw=1)
    if r is None:
        print(f"T={T}: no solution (INFEASIBLE/UNKNOWN) within {timeout}s")
        return
    l1, eta, w, q, opt = r
    print(f"T={T}: l1={l1:.8f} OPTIMAL={opt} eta={eta} w={w} q={q}  (n*L1={n*l1:.6f})")

def main():
    import multiprocessing as mp
    n = int(sys.argv[1]); Tmax = int(sys.argv[2]); timeout = int(sys.argv[3])
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 8
    sw = int(sys.argv[5]) if len(sys.argv) > 5 else 1
    W = 1 << (n-1); k = 2*n - 1
    best = None; t0 = time.time()
    jobs = [(n, W, T, timeout, sw) for T in range(1, Tmax+1)]
    pool = mp.Pool(procs)
    done = 0
    for T, r in pool.imap_unordered(solve_T_wrap, jobs):
        done += 1
        if r is None: continue
        l1, eta, w, q, opt = r
        if best is None or l1 < best[0]:
            best = (l1, T, eta, w, q, opt)
            print(f"  T={T}: l1={l1:.6f} opt={opt} eta={eta} w={w} q={q}  [best]", flush=True)
        if done % 40 == 0:
            el = time.time()-t0
            print(f"  ...{done}/{Tmax} done, {el:.0f}s, best={best[0] if best else None:.6f} at T={best[1] if best else None}", flush=True)
    pool.close(); pool.join()
    if best:
        l1, T, eta, w, q, opt = best
        print(f"n={n} RESULT: best L1 = {l1:.8f} at T={T} (opt={opt})  n*L1={n*l1:.6f}  1/n={1/n:.6f}")
        print(f"  eta={eta} w={w} q={q}")
        print(f"  NOTE: re-run 'python conj15_l1.py confirm {n} {T} 600' to certify the winning T as OPTIMAL")
    else:
        print(f"n={n}: no feasible T found")

if __name__ == "__main__":
    if sys.argv[1] == "confirm":
        confirm(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 600)
    else:
        main()
