# -*- coding: utf-8 -*-
"""DIRECT exhaustive verification of the SHARP mirror statement (M):
   For any weighted game with w_i >= w_j > w_s and eta_i == eta_j (both = 2c), both
     P([q-w_i, q-w_j)) = 0   and   P([q-w_s-w_i, q-w_s-w_j)) = 0
   where P counts subset sums of the remaining n-3 weights (N minus {i,j,s}).
   Tested on REAL random games: require eta_i == eta_j exactly, then check (M)."""
import random
def profile(weights):
    r = [0]
    for x in weights:
        r = r + [v + x for v in r]
    return r
def P(S, a, b):
    return sum(1 for s in S if a <= s < b)
def swings(weights, q):
    n = len(weights); N = 1 << n
    sw = [0]*N
    for mm in range(1, N):
        lb = mm & (-mm); sw[mm] = sw[mm ^ lb] + weights[lb.bit_length()-1]
    eta = [0]*n
    for i in range(n):
        for mm in range(N):
            if mm & (1 << i): continue
            if sw[mm] >= q - weights[i] and sw[mm] < q:
                eta[i] += 1
    return eta

random.seed(11)
hyp = viol = 0
for _ in range(300000):
    n = random.randint(3, 7)
    others = [random.randint(1, 20) for _ in range(n-3)]
    w_s = random.randint(1, 6)
    w_j = random.randint(w_s+1, 9)
    w_i = random.randint(w_j, 12)
    w = others + [w_i, w_j, w_s]
    q = random.randint(2, 3*sum(w)//2 + 3)
    eta = swings(w, q)
    if eta[-3] != eta[-2]:
        continue
    hyp += 1
    S = profile(others)
    p1 = P(S, q-w_i, q-w_j)
    p2 = P(S, q-w_s-w_i, q-w_s-w_j)
    if p1 or p2:
        viol += 1
        if viol <= 5:
            print(f"  NONEMPTY: others={others} w=({w_i},{w_j},{w_s}) q={q} p1={p1} p2={p2}")
print(f"real games with eta_i==eta_j: {hyp}; sharp (M) violations: {viol}")
