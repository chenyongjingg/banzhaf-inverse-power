"""MILP verify: for given n, does a simple game exist with swings (2c,...,2c,c)?
Usage: python milp_verify.py n [time_limit]
Prints c and minimal winning coalitions."""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix
import sys, time

n = int(sys.argv[1])
tl = int(sys.argv[2]) if len(sys.argv) > 2 else 300
NV = (1 << n) + 1
c_idx = 1 << n

I=[]; J=[]; V=[]; lb=[]; ub=[]
def add(d, lo, hi):
    for k, v in d.items():
        I.append(len(lb)); J.append(k); V.append(v)
    lb.append(lo); ub.append(hi)

add({0: 1}, 0, 0)                    # empty losing
add({(1 << n) - 1: 1}, 1, 1)         # full winning
for m in range(1 << n):
    for i in range(n):
        bit = 1 << i
        if m & bit: continue
        add({m: 1, (m | bit): -1}, -np.inf, 0)   # monotone
for i in range(n):
    d = {}
    for m in range(1 << n):
        if m & (1 << i): continue
        d[m | (1 << i)] = d.get(m | (1 << i), 0) + 1
        d[m] = d.get(m, 0) - 1
    d[c_idx] = -(2 if i != n - 1 else 1)
    add(d, 0, 0)                     # swing equation
add({c_idx: 1}, 1, 100000)

M = csr_matrix((V, (I, J)), shape=(len(lb), NV))
cons = LinearConstraint(M, np.array(lb), np.array(ub))
bounds = Bounds(np.zeros(NV), np.ones(NV))
bounds.lb[c_idx] = 1; bounds.ub[c_idx] = 100000

t0 = time.time()
res = milp(c=np.zeros(NV), constraints=cons, integrality=np.ones(NV), bounds=bounds,
           options={"time_limit": tl, "mip_rel_gap": 0})
print(f"n={n}: status={res.status} msg={res.message} time={time.time()-t0:.1f}s")
if res.x is not None:
    x = res.x
    c = round(x[c_idx])
    win = [round(x[m]) for m in range(1 << n)]
    ac = []
    for m in range(1 << n):
        if not win[m]: continue
        minimal = True
        for b in range(n):
            if (m >> b) & 1 and win[m & ~(1 << b)]:
                minimal = False; break
        if minimal: ac.append(m)
    print(f"  c={c}")
    for a in ac:
        print("   ", sorted(j + 1 for j in range(n) if (a >> j) & 1))
