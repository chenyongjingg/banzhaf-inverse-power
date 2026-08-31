"""MILP for n=8: does a simple game exist with swings (2c,...,2c,c)?
Uses scipy.optimize.milp. Variables x[m] (m=0..255) winning indicators + c (scale)."""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix
import time

n = 8
NV = 257
c_idx = 256

I = []   # row indices
J = []   # column indices
V = []   # values
lb = []
ub = []

def add_constraint(d, lo, hi):
    """d: dict var->coeff, lo <= sum <= hi"""
    row = len(lb)
    for k, v in d.items():
        I.append(row); J.append(k); V.append(v)
    lb.append(lo); ub.append(hi)

# x[0]=0, x[255]=1
add_constraint({0: 1}, 0, 0)
add_constraint({255: 1}, 1, 1)

# monotonicity: x[m] - x[m|bit] <= 0
for m in range(1 << n):
    for i in range(n):
        bit = 1 << i
        if m & bit:
            continue
        add_constraint({m: 1, (m | bit): -1}, -np.inf, 0)

# swings: eta_i = sum_{m: bit i=0}(x[m|bit] - x[m]) ; eta_i = (2c if i!=n-1 else c)
for i in range(n):
    d = {}
    for m in range(1 << n):
        if m & (1 << i):
            continue
        d[m | (1 << i)] = d.get(m | (1 << i), 0) + 1
        d[m] = d.get(m, 0) - 1
    coeff = 2 if i != n - 1 else 1
    d[c_idx] = -coeff
    add_constraint(d, 0, 0)

# c >= 1
add_constraint({c_idx: 1}, 1, 1000)

m = csr_matrix((V, (I, J)), shape=(len(lb), NV))
cons = LinearConstraint(m, np.array(lb), np.array(ub))
integrality = np.ones(NV, dtype=int)
bounds = Bounds(np.zeros(NV), np.ones(NV))
bounds.lb[c_idx] = 1   # c >= 1
bounds.ub[c_idx] = 100

t0 = time.time()
res = milp(c=np.zeros(NV), constraints=cons, integrality=integrality, bounds=bounds,
           options={"time_limit": 300, "mip_rel_gap": 0})
print(f"time: {time.time()-t0:.1f}s  status: {res.status}  message: {res.message}")
if res.x is not None:
    x = res.x
    c = round(x[c_idx])
    print("c =", c)
    win = [round(x[m]) for m in range(1 << n)]
    # minimal winning coalitions
    ac = []
    for m in range(1 << n):
        if win[m]:
            ok = True
            for b in range(n):
                mm = m & ~(1 << b)
                if win[mm]:
                    ok = False; break
            if ok:
                ac.append(m)
    print("antichain (minimal winning):")
    for a in ac:
        print("  ", sorted(j + 1 for j in range(n) if (a >> j) & 1))
    def f(mm): return win[mm]
    eta = [0] * n
    for i in range(n):
        bit = 1 << i
        for mm in range(1 << n):
            if mm & bit: continue
            if (not f(mm)) and f(mm | bit): eta[i] += 1
    print("swings:", eta, " (should be", [2 * c] * (n - 1) + [c], ")")
