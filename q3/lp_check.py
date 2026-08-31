# -*- coding: utf-8 -*-
"""DECISIVE independent check for the minimal-c certification via LP relaxation.

Variables x(S) in [0,1] for each coalition S.  Constraints: normalization, monotonicity
x(S) <= x(S u {i}), and the swing equations.  If the LP relaxation is infeasible then the
integer (0/1) feasibility problem is CERTAINLY infeasible (relaxation enlarges the
feasible set).  This is structurally independent of the CP-SAT swap-sum model and uses the
same solver family (HiGHS) that Section 7 of the manuscript cites.

Usage: python lp_check.py <n> <c>
"""
import sys, time
import numpy as np
from scipy.optimize import linprog


def lp_status(n, c):
    t0 = time.time()
    N = 1 << n
    spec = n - 1
    # variable order: x[mask] for mask in 0..N-1
    def var(mask):
        return mask

    # Equality rows: swing equations + normalization.  Represent as A_eq row (len N), b_eq scalar.
    Aeq, beq = [], []
    for i in range(n):
        tgt = c if i == spec else 2 * c
        row = np.zeros(N)
        for mask in range(N):
            if mask & (1 << i):
                row[mask] += 1.0
            else:
                row[mask] -= 1.0
        Aeq.append(row); beq.append(tgt)
    row0 = np.zeros(N); row0[0] = 1.0
    rowf = np.zeros(N); rowf[N - 1] = 1.0
    Aeq.append(row0); beq.append(0.0)
    Aeq.append(rowf); beq.append(1.0)

    # Inequality rows: x(S) - x(S u {i}) <= 0
    Aub, bub = [], []
    for mask in range(N):
        for i in range(n):
            if mask & (1 << i):
                continue
            row = np.zeros(N)
            row[mask] = 1.0
            row[mask | (1 << i)] = -1.0
            Aub.append(row); bub.append(0.0)

    res = linprog(np.zeros(N), A_ub=np.array(Aub), b_ub=np.array(bub),
                  A_eq=np.array(Aeq), b_eq=np.array(beq),
                  bounds=[(0, 1)] * N, method="highs")
    dt = time.time() - t0
    tag = "INFEASIBLE" if res.status == 2 else ("OPTIMAL(FEASIBLE)" if res.status == 0 else f"OTHER({res.status})")
    print(f"[lp/highs] n={n} c={c}  {tag}  ({dt:.1f}s, {len(Aub)} monotone rows, {len(Aeq)} eq rows)")
    if res.status != 2:
        print(f"  message: {res.message}")
    return res.status


if __name__ == "__main__":
    n = int(sys.argv[1]); c = int(sys.argv[2])
    lp_status(n, c)
