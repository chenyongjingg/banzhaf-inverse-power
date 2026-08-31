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

def swing_vector(ac, n):
    eta = [0]*n
    for m in range(1 << n):
        win = any((m & c) == c for c in ac)
        if win:
            for i in range(n):
                mm = m & ~(1 << i)
                if not any((mm & c) == c for c in ac): eta[i] += 1
        else:
            for i in range(n):
                mm = m | (1 << i)
                if any((mm & c) == c for c in ac): eta[i] += 1
    return eta

def check(ac, n):
    # f(empty)=0 : no antichain element empty
    if 0 in ac: return None
    if not ac: return None
    eta = swing_vector(ac, n)
    g = reduce(gcd, eta)
    norm = tuple(sorted(e//g for e in eta))
    if norm == tuple([1] + [2]*(n-1)):
        return eta
    return None

if __name__ == "__main__":
    n = int(sys.argv[1])
    # sanity: unanimity and dictator
    full = (1<<n)-1
    print("unanimity swings:", swing_vector([full], n))
    print("dictator{0} swings:", swing_vector([1], n))
    t0=time.time()
    sols=[]
    cnt=0
    for ac in antichains(n):
        cnt+=1
        r = check(ac, n)
        if r: sols.append((ac, r))
    print(f"n={n}: {len(sols)} solutions out of {cnt} antichains in {time.time()-t0:.1f}s")
    for ac, eta in sols[:10]:
        print("  antichain:", ac, " swings:", eta)
