# -*- coding: utf-8 -*-
"""Probe 2 (Conjecture 15): for small n, the optimal L1 distance ||Bz(v) - psi^n||_1
over (a) ALL simple games vs (b) WEIGHTED majority games. psi^n = (2,...,2,1)/(2n-1)."""
import numpy as np
from scipy.optimize import linprog

def monotone_games(n):
    """Yield all simple games (v(0)=0, v(N)=1) as dicts mask->0/1, in increasing-size order."""
    N = 1 << n
    masks = sorted(range(N), key=lambda m: (bin(m).count("1"), m))
    # precompute subsets per mask (only need: any subset set to 1?)
    sub = [None]*N
    for m in masks:
        s = []
        sub_m = m
        while True:
            sub_m = (sub_m-1) & m
            if sub_m == 0: break
            s.append(sub_m)
        sub[m] = s
    vals = {}
    def rec(idx):
        if idx == N:
            if vals[0] == 0 and vals[N-1] == 1:
                yield dict(vals)
            return
        m = masks[idx]
        if m == 0:
            vals[m] = 0; yield from rec(idx+1)
            return
        if m == N-1:
            vals[m] = 1; yield from rec(idx+1)
            return
        # any subset already 1? then v(m) forced to 1
        forced1 = any(vals.get(t, 0) for t in sub[m])
        if forced1:
            vals[m] = 1; yield from rec(idx+1)
        else:
            vals[m] = 0; yield from rec(idx+1)
            vals[m] = 1; yield from rec(idx+1)
        del vals[m]
    yield from rec(0)

def banzhaf(vals, n):
    eta = np.zeros(n, dtype=int)
    N = 1 << n
    for i in range(n):
        bit = 1 << i
        for m in range(N):
            if m & bit: continue
            if vals.get(m, 0) == 0 and vals.get(m | bit, 0) == 1:
                eta[i] += 1
    return eta

def is_weighted(vals, n):
    """LP feasibility: exists integer weights w_i, quota q realizing the game."""
    minimal_win = []; maximal_lose = []
    N = 1 << n
    for m in range(1, N-1):
        v = vals.get(m, 0)
        if v == 1:
            # minimal winning if all proper subsets losing
            if all(vals.get(t, 0) == 0 for t in range(1, N-1) if (t & ~m) == 0 and t != m and (m & ~t) != 0):
                minimal_win.append(m)
        else:
            if all(vals.get(t, 0) == 1 for t in range(1, N-1) if (t & ~m) == 0 and t != m and (m & ~t) != 0):
                maximal_lose.append(m)
    if not minimal_win:  # empty game shouldn't happen since v(N)=1 -> at least one MWC
        return False
    # variables: w[0..n-1], q
    A_ub = []; b_ub = []
    for S in minimal_win:   # w(S) >= q  -> -w(S) + q <= 0
        row = [0.0]*(n+1)
        for i in range(n):
            if S >> i & 1: row[i] = -1.0
        row[n] = 1.0
        A_ub.append(row); b_ub.append(0.0)
    for T in maximal_lose:  # w(T) <= q-1 -> w(T) - q <= -1
        row = [0.0]*(n+1)
        for i in range(n):
            if T >> i & 1: row[i] = 1.0
        row[n] = -1.0
        A_ub.append(row); b_ub.append(-1.0)
    res = linprog(np.zeros(n+1), A_ub=np.array(A_ub), b_ub=np.array(b_ub),
                  bounds=[(0, None)]*(n) + [(0, None)], method="highs")
    return res.status == 0

def dist_psi(eta, n):
    bz = eta / eta.sum()
    psi = np.array([2/(2*n-1)]*(n-1) + [1/(2*n-1)])
    return np.abs(bz - psi).sum()

for n in [3, 4, 5]:
    best_all = 1e9; best_weighted = 1e9; ng = 0; nw = 0; nexact = 0
    for vals in monotone_games(n):
        ng += 1
        eta = banzhaf(vals, n)
        d = dist_psi(eta, n)
        if d < best_all: best_all = d
        if d < 1e-12: nexact += 1
        if is_weighted(vals, n):
            nw += 1
            if d < best_weighted: best_weighted = d
    print(f"n={n}: #simple_games={ng}  #weighted={nw}  #exact(==psi)={nexact}  "
          f"minL1_all={best_all:.8f}  minL1_weighted={best_weighted:.8f}")
