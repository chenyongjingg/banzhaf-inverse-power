"""Search for simple games on n voters whose Banzhaf swing vector is proportional to
(2,2,...,2,1) [Kurz Conjecture 16 target psi^n]. Uses forced structure:
the unique 1-swing player p appears in exactly one minimal winning coalition {p} U T
(T losing), and F = antichain of minimal winning coalitions inside {1..n-1}.
"""
import sys, time
from math import gcd
from functools import reduce

def antichains(m):
    masks = list(range(1 << m))
    res = []
    def rec(chosen, start):
        res.append(tuple(chosen))
        for idx in range(start, len(masks)):
            mm = masks[idx]
            if any((c & mm) == c for c in chosen):
                continue
            chosen.append(mm); rec(chosen, idx + 1); chosen.pop()
    rec([], 0)
    return res

def swings_of(pT, F, n):
    pbit = 1 << (n - 1)
    def win(m):
        if (m & pbit) == pbit and (m & pT) == pT:
            return True
        for f in F:
            if (m & f) == f:
                return True
        return False
    eta = [0] * n
    for i in range(n):
        bit = 1 << i
        for mm in range(1 << n):
            if mm & bit:
                continue
            if (not win(mm)) and win(mm | bit):
                eta[i] += 1
    return eta

def normalized(eta):
    g = reduce(gcd, eta)
    return tuple(sorted(e // g for e in eta))

def main():
    n = int(sys.argv[1])
    m = n - 1
    target = tuple([1] + [2] * (n - 1))
    Flist = antichains(m)
    t0 = time.time(); sols = []
    for F in Flist:
        if not F:
            continue
        for T in range(1 << m):
            if any((f & T) == f for f in F):
                continue  # T winning
            pT = T | (1 << (n - 1))
            eta = swings_of(pT, F, n)
            if normalized(eta) == target:
                sols.append((F, T, eta))
    print(f"n={n}: found {len(sols)} solutions in {time.time()-t0:.1f}s")
    for F, T, eta in sols[:8]:
        fmtF = [sorted([j + 1 for j in range(n - 1) if f >> j & 1]) for f in F]
        fmtT = [j + 1 for j in range(n - 1) if T >> j & 1]
        print("  F:", fmtF, " T:", fmtT, " swings:", eta)

if __name__ == "__main__":
    main()
