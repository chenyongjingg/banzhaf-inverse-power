"""W-family MILP with c FIXED to a candidate. Usage: python milp_ufixed.py n c [tl]"""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix
import sys, time

def main():
    n=int(sys.argv[1]); c_fix=int(sys.argv[2])
    tl=int(sys.argv[3]) if len(sys.argv)>3 else 200
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    triples=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    E_idx={e:i for i,e in enumerate(pairs)}
    ne=len(pairs); nt=len(triples)
    z_list=[(ti,pair) for ti,tr in enumerate(triples) for pair in [(tr[0],tr[1]),(tr[0],tr[2]),(tr[1],tr[2])]]
    nz=len(z_list); c_var=ne+nt+nz; NV=c_var+1
    I=[];J=[];V=[];lb=[];ub=[]
    def add(d,lo,hi):
        for k,v in d.items(): I.append(len(lb));J.append(k);V.append(v)
        lb.append(lo);ub.append(hi)
    for ti,tr in enumerate(triples):
        for pair in [(tr[0],tr[1]),(tr[0],tr[2]),(tr[1],tr[2])]:
            add({ne+ti:1, E_idx[pair]:-1}, -np.inf, 0)   # monotonicity
    for zi,(ti,pair) in enumerate(z_list):
        ve=ne+nt+zi; vy=ne+ti; vx=E_idx[pair]
        add({ve:1, vy:-1}, -np.inf, 0)
        add({ve:1, vx:-1}, -np.inf, 0)
        add({ve:1, vy:-1, vx:-1}, -1, np.inf)
    for i in range(n):
        d={}
        for e in pairs: d[E_idx[e]]=d.get(E_idx[e],0)+1
        for ti,tr in enumerate(triples):
            d[ne+ti]=d.get(ne+ti,0)+1
            if i in tr: d[ne+ti]=d.get(ne+ti,0)-1
        for e in pairs:
            if i in e: d[E_idx[e]]=d.get(E_idx[e],0)-2
        for ti,tr in enumerate(triples):
            if i in tr:
                pr=tuple(sorted(set(tr)-{i}))
                d[ne+nt+z_list.index((ti,pr))]=d.get(ne+nt+z_list.index((ti,pr)),0)-1
        target = (2*c_fix if i!=n-1 else c_fix)
        add(d, target-(n-1), target-(n-1))
    # fix c = c_fix
    add({c_var:1}, c_fix, c_fix)
    M=csr_matrix((V,(I,J)),shape=(len(lb),NV))
    cons=LinearConstraint(M,np.array(lb),np.array(ub))
    b=Bounds(np.zeros(NV),np.ones(NV)); b.lb[c_var]=c_fix; b.ub[c_var]=c_fix
    t0=time.time()
    res=milp(c=np.zeros(NV),constraints=cons,integrality=np.ones(NV),bounds=b,options={"time_limit":tl})
    print(f"n={n} c={c_fix}: status={res.status} time={time.time()-t0:.0f}s msg={res.message}", flush=True)
    if res.x is not None:
        x=res.x
        G=[pairs[i] for i in range(ne) if x[i]>0.5]
        F=[triples[i] for i in range(nt) if x[ne+i]>0.5]
        print(f"  |G|={len(G)} |F|={len(F)}", flush=True)
main()
