"""MILP over the unified W(G,F) family: O(n^3) variables instead of 2^n.
Finds (G,F) with Banzhaf = psi^n. Usage: python milp_ufamily.py n [tl]"""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix
import sys, time

def main():
    n = int(sys.argv[1])
    tl = int(sys.argv[2]) if len(sys.argv)>2 else 300
    pairs = [(a,b) for a in range(n) for b in range(a+1,n)]
    triples = [(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    E_idx = {e:i for i,e in enumerate(pairs)}
    # variables: x[pair] (0..E-1), y[triple] (E..E+T-1), z[triple,pair in triple] (rest), c (last)
    ne=len(pairs); nt=len(triples)
    z_list=[]  # (triple_idx, pair)
    for ti,tr in enumerate(triples):
        for pair in [(tr[0],tr[1]),(tr[0],tr[2]),(tr[1],tr[2])]:
            z_list.append((ti, pair))
    nz=len(z_list)
    c_var = ne+nt+nz
    NV = c_var+1
    I=[];J=[];V=[];lb=[];ub=[]
    def add(d,lo,hi):
        for k,v in d.items(): I.append(len(lb));J.append(k);V.append(v)
        lb.append(lo);ub.append(hi)
    # monotonicity: y_T <= x_e for pair e subset T
    for ti,tr in enumerate(triples):
        for pair in [(tr[0],tr[1]),(tr[0],tr[2]),(tr[1],tr[2])]:
            add({ne+ti:1, E_idx[pair]:-1}, -np.inf, 0)
    # linearization: z_{T,e} = y_T * x_e
    for zi,(ti,pair) in enumerate(z_list):
        ve=ne+nt+zi; vy=ne+ti; vx=E_idx[pair]
        add({ve:1, vy:-1}, -np.inf, 0)         # z <= y
        add({ve:1, vx:-1}, -np.inf, 0)         # z <= x
        add({ve:1, vy:-1, vx:-1}, -1, np.inf)  # z >= y+x-1
    # swing equations: beta_i = 2c (i<n-1), beta_n = c.
    # beta_i = |G| + (n-1) + |F| - 2*deg_G(i) - r_i - sum_{T in i} z_{T,T\i}
    # ->  |G| + |F| - 2*deg - r_i - sum z = target - (n-1)   [constant moved to RHS]
    for i in range(n):
        d={}
        for e in pairs: d[E_idx[e]] = d.get(E_idx[e],0)+1
        for ti,tr in enumerate(triples):
            d[ne+ti] = d.get(ne+ti,0)+1
            if i in tr:
                d[ne+ti] = d.get(ne+ti,0)-1
        for e in pairs:
            if i in e: d[E_idx[e]] = d.get(E_idx[e],0)-2
        for ti,tr in enumerate(triples):
            if i in tr:
                pr = tuple(sorted(set(tr)-{i}))
                zi = z_list.index((ti, pr))
                d[ne+nt+zi] = d.get(ne+nt+zi,0)-1
        d[ne+nt+nz] = -(2 if i != n-1 else 1)
        # RHS = target - (n-1); move to: expression - target = -(n-1)
        rhs = -(n-1)
        add(d, rhs, rhs)
    # c >= 1
    add({c_var:1},1,10000)
    # sum |G|, |F| positive-ish (optional: force some structure)
    M = csr_matrix((V,(I,J)), shape=(len(lb),NV))
    cons = LinearConstraint(M, np.array(lb), np.array(ub))
    bounds = Bounds(np.zeros(NV), np.ones(NV))
    bounds.lb[c_var]=1; bounds.ub[c_var]=10000
    t0=time.time()
    res = milp(c=np.zeros(NV), constraints=cons, integrality=np.ones(NV), bounds=bounds,
               options={"time_limit":tl})
    print(f"n={n}: status={res.status} msg={res.message} time={time.time()-t0:.1f}s", flush=True)
    if res.x is not None:
        x=res.x
        c=round(x[c_var])
        G=[pairs[i] for i in range(ne) if x[i]>0.5]
        F=[triples[i] for i in range(nt) if x[ne+i]>0.5]
        print(f"  c={c}, |G|={len(G)}, |F|={len(F)}", flush=True)
        print(f"  G edges: {G}", flush=True)
        print(f"  F triples: {F}", flush=True)
main()
