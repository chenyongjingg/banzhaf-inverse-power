# -*- coding: utf-8 -*-
"""Probe 6: rigorous check of the core identity
   eta_i - eta_j = 2 * #{T subset of N\\{i,j} : q-w_i <= W(T) < q-w_j}   for w_i >= w_j
on random weighted majority games, n up to 12."""
import random, sys
from itertools import combinations

def subset_sums(w):
    sums = {0: 1}  # count via dict is fine for verification
    res = [0]
    for wi in w:
        res = res + [x + wi for x in res]
    return res

def swings(w, q):
    n = len(w)
    sums = subset_sums(w)
    eta = [0]*n
    for i in range(n):
        for m in range(1 << n):
            if m >> i & 1: continue
            s = 0
            mm = m
            k = 0
            while mm:
                if mm & 1: s += w[k]
                mm >>= 1; k += 1
            if s < q <= s + w[i]:
                eta[i] += 1
    return eta

def identity_terms(w, q, i, j):
    """Compute both sides of the identity for w_i >= w_j."""
    n = len(w)
    eta = swings(w, q)
    # RHS: count T subset of N\{i,j} with q-w_i <= W(T) < q-w_j
    other = [w[k] for k in range(n) if k not in (i, j)]
    cnt = 0
    for r in range(len(other)+1):
        for T in combinations(range(len(other)), r):
            s = sum(other[k] for k in T)
            if q-w[i] <= s < q-w[j]:
                cnt += 1
    lhs = eta[i] - eta[j]
    return lhs, 2*cnt

random.seed(42)
fails = 0
tests = 0
for trial in range(2000):
    n = random.randint(3, 12)
    w = [random.randint(1, 30) for _ in range(n)]
    # ensure at least two distinct weights for a meaningful test
    if len(set(w)) < 2: continue
    smax = sum(w)
    for _q in range(3):
        q = random.randint(1, smax)
        pairs = [(i,j) for i in range(n) for j in range(n) if w[i] > w[j]]
        if not pairs: continue
        for (i, j) in random.sample(pairs, min(2, len(pairs))):
            tests += 1
            lhs, rhs = identity_terms(w, q, i, j)
            if lhs != rhs:
                fails += 1
                if fails <= 5:
                    print(f"FAIL n={n} w={w} q={q} i={i} j={j}: eta_i-eta_j={lhs}, 2*cnt={rhs}")
print(f"checked {tests} pairs across random weighted games: {fails} failures")

# also check the corollary: special player must be minimal weight if eta special < others
# and eta_i - eta_s even
print("\n--- corollary check: if eta has ratio 2:1 with special s, then w_s minimal & c even ---")
random.seed(7)
for trial in range(50):
    n = random.randint(3, 8)
    w = [random.randint(1, 25) for _ in range(n)]
    if len(set(w)) < 2: continue
    q = random.randint(1, sum(w))
    eta = swings(w, q)
    # find special player s with minimal swing count
    s = eta.index(min(eta))
    others = [k for k in range(n) if k != s]
    # is special weight minimal?
    wmin_ok = all(w[s] <= w[k] for k in others)
    print(f"  n={n} w={w} q={q} eta={eta} s={s} (min-swing), w_s={w[s]} minimal={wmin_ok}")
