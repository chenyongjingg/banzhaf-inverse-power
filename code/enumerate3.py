from itertools import combinations
import sys, time
from math import gcd
from functools import reduce

def antichains(n):
    masks = list(range(1 << n))
    results = []
    def rec(chosen, start):
        results.append(tuple(chosen))
        for idx in range(start, len(masks)):
            m = masks[idx]
            if any((c & m) == c for c in chosen): continue
            chosen.append(m); rec(chosen, idx+1); chosen.pop()
    rec([], 0)
    return results

def swings(ac, n):
    """Standard Banzhaf swing counts. f(m)=winning iff some antichain element c: c subset of m."""
    def win(m): return any((m & c) == c for c in ac)
    eta = [0]*n
    for i in range(n):
        bit = 1 << i
        for m in range(1 << n):
            if m & bit: continue        # i not in S
            if (not win(m)) and win(m | bit):
                eta[i] += 1
    return eta

def check(ac, n):
    if 0 in ac or not ac: return None
    eta = swings(ac, n)
    g = reduce(gcd, eta)
    norm = tuple(sorted(e//g for e in eta))
    if norm == tuple([1] + [2]*(n-1)):
        return eta
    return None

if __name__ == "__main__":
    n = int(sys.argv[1])
    full = (1<<n)-1
    print("unanimity swings:", swings([full], n))      # expect [1]*n
    print("dictator{0} swings:", swings([1], n))       # expect [2^(n-1), 0, ..., 0]
    print("majority(quota2):", swings([c for c in combinations(range(n),2) and 0], n) if False else "skip")
    t0=time.time(); sols=[]; cnt=0
    for ac in antichains(n):
        cnt+=1
        r = check(ac, n)
        if r: sols.append((ac, r))
    print(f"n={n}: {len(sols)} solutions out of {cnt} antichains in {time.time()-t0:.1f}s")
    for ac, eta in sols[:12]:
        print("  antichain:", ac, " swings:", eta)
