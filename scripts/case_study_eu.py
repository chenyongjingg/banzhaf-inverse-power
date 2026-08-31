# -*- coding: utf-8 -*-
"""EJOR case study: exact Banzhaf of historical EU Council weighted bodies,
and their L1-distance to the egalitarian target psi^n.

All bodies in the certified range n in {6,...,10} are exactly certified by the
paper's CP-SAT machinery; n=12,15 are shown as scaling context only (Tier 3).

Weights follow the official QMV tables (Treaty of Rome / accession treaties).
"""
from itertools import combinations
from fractions import Fraction

def banzhaf_swings(weights, quota):
    """Exact Banzhaf swing counts via subset enumeration. n<=15 trivial."""
    n = len(weights)
    swings = [0] * n
    for r in range(n):
        for T in combinations(range(n), r):
            S = set(T)
            W = sum(weights[i] for i in T)
            for i in range(n):
                if i in S:
                    continue
                # S losing, S+{i} winning  => swing for i
                if W < quota <= W + weights[i]:
                    swings[i] += 1
    return swings

def norm_bz(swings):
    tot = sum(swings)
    return [Fraction(s, tot) for s in swings]

def psi(n, special):
    return [Fraction(2, 2 * n - 1) if i != special else Fraction(1, 2 * n - 1)
            for i in range(n)]

def l1_to_psi(bz, n):
    """min over special-player position of sum_i |bz_i - psi^n_i|."""
    best = None
    for s in range(n):
        d = sum(abs(bz[i] - psi(n, s)[i]) for i in range(n))
        if best is None or d < best:
            best = d
    return best

def report(name, weights, quota, certified):
    swings = banzhaf_swings(weights, quota)
    bz = norm_bz(swings)
    n = len(weights)
    d = l1_to_psi(bz, n)
    pct = [str(round(float(f) * 100, 2)) + "%" for f in bz]
    print(f"--- {name} (n={n}, certified={certified}) ---")
    print(f"  weights={weights}, quota={quota}")
    print(f"  swings={swings}, total={sum(swings)}")
    print(f"  Bz(norm)={pct}")
    print(f"  min L1 to psi^{n} = {d} = {float(d):.6f}")
    # most-powerful vs least-powerful spread
    mn, mx = min(bz), max(bz)
    nulls = sum(1 for s in swings if s == 0)
    if mn == 0:
        print(f"  power spread: max={float(mx):.4f}, {nulls} null player(s) (0 power)")
    else:
        print(f"  power spread max/min = {float(mx):.4f}/{float(mn):.4f} = {float(mx/mn):.2f}x")
    print()
    return swings, bz, d

if __name__ == "__main__":
    # Real bodies in the paper's EXACT-certified range (n<=10):
    report("EEC-6 (Rome 1958-1973)", [4,4,4,2,2,1], 12, True)
    report("EEC-9 (1973-1981)",     [10,10,10,10,5,5,3,3,2], 41, True)
    report("EEC-10 (1981-1986)",    [10,10,10,10,5,5,5,3,3,2], 45, True)
    # Scaling context (n>10, Tier-3 heuristic only, exact infeasibility NOT certified):
    report("EEC-12 (1986-1995)",    [10,10,10,10,8,5,5,5,5,3,3,2], 54, False)
    report("EU-15 (1995-2004)",     [10,10,10,10,8,5,5,5,5,4,4,4,3,3,2], 62, False)

    # The certified global L1-optimum from the paper for n=6 (weights (3,1,3,3,3,1), q=11)
    print("=== reference: paper's certified L1-optimum for n=6 ===")
    w = [3,1,3,3,3,1]; q = 11
    sw = banzhaf_swings(w, q)
    bz = norm_bz(sw)
    print(f"  swings={sw}, Bz(norm)={[str(round(float(x)*100,2))+'%' for x in bz]}")
    print(f"  L1 to psi^6 = {l1_to_psi(bz, 6)} = {float(l1_to_psi(bz,6)):.6f}  (certified global min)")
