# -*- coding: utf-8 -*-
"""Wide-range test: under eta_i = eta_j (single-pair hypothesis), is the window
[q-w_i, q-w_j) ALWAYS empty of subset sums? (Both [q-w_i,q-w_j) and its w_s-translate
[q-w_s-w_i,q-w_s-w_j) measured.) Wider weights/values to rule out small-parameter artifact."""
import random
def P(S, a, b):
    return sum(1 for s in S if a <= s < b)
def subsets(arr):
    r = [0]
    for x in arr: r = r + [v+x for v in r]
    return r

random.seed(7)
cnt = nonempty = 0
for _ in range(400000):
    nv = random.randint(1, 4)
    vals = [random.randint(1, 60) for _ in range(nv)]
    S = subsets(vals)
    w_i = random.randint(2, 30)
    w_j = random.randint(1, w_i-1)           # strict
    w_s = random.randint(1, w_j)             # w_s <= w_j (Cor 19 gives w_s < w_i; w_s<=w_j WLOG pair choice)
    q = random.randint(2, 120)
    lhsA = P(S, q-w_i, q-w_s) + P(S, q-w_i-w_j, q-w_s-w_j)
    lhsB = P(S, q-w_j, q-w_s) + P(S, q-w_i-w_j, q-w_s-w_i)
    if lhsA != lhsB: continue
    cnt += 1
    m1 = P(S, q-w_i, q-w_j)
    m2 = P(S, q-w_s-w_i, q-w_s-w_j)
    if m1 > 0 or m2 > 0:
        nonempty += 1
        if nonempty <= 5:
            print(f"  NONEMPTY: vals={vals} w=({w_i},{w_j},{w_s}) q={q} P1={m1} P2={m2}")
print(f"hyp-met={cnt}, with nonempty mirror windows: {nonempty}")
