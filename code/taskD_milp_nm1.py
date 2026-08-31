"""MILP test: is 'all (n-1)-sets winning' NECESSARY? Add constraint x(N\{1})=0, see if feasible."""
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix
import sys, time

def test(n, force_losing_nm1=True):
    NV=(1<<n)+1; c_idx=1<<n; full=(1<<n)-1
    I=[];J=[];V=[];lb=[];ub=[]
    def add(d,lo,hi):
        for k,v in d.items(): I.append(len(lb));J.append(k);V.append(v)
        lb.append(lo);ub.append(hi)
    add({0:1},0,0); add({full:1},1,1)
    for m in range(1<<n):
        for i in range(n):
            bit=1<<i
            if m&bit: continue
            add({m:1,(m|bit):-1},-np.inf,0)
    for i in range(n):
        d={}
        for m in range(1<<n):
            if m&(1<<i): continue
            d[m|(1<<i)]=d.get(m|(1<<i),0)+1
            d[m]=d.get(m,0)-1
        d[c_idx]=-(2 if i!=n-1 else 1)
        add(d,0,0)
    add({c_idx:1},1,1000)
    # symmetry break
    for i in range(1,n-1):
        add({full&~(1<<(i-1)):1, full&~(1<<i):-1},-np.inf,0)
    if force_losing_nm1:
        # force N\{0} losing
        add({full&~(1<<0):1},0,0)
    M=csr_matrix((V,(I,J)),shape=(len(lb),NV))
    cons=LinearConstraint(M,np.array(lb),np.array(ub))
    b=Bounds(np.zeros(NV),np.ones(NV)); b.lb[c_idx]=1; b.ub[c_idx]=1000
    t0=time.time()
    res=milp(c=np.zeros(NV),constraints=cons,integrality=np.ones(NV),bounds=b,options={"time_limit":60})
    return res.status, time.time()-t0

for n in (7,8):
    st1,t1=test(n, force_losing_nm1=False)
    st2,t2=test(n, force_losing_nm1=True)
    print(f"n={n}: unconstrained feasible={st1==0} ({t1:.0f}s); WITH losing (n-1)-set feasible={st2==0} ({t2:.0f}s)")
    if st2==0:
        print(f"  -> COUNTEREXAMPLE EXISTS: all-(n-1)-winning NOT necessary")
    else:
        print(f"  -> infeasible: all (n-1)-sets winning IS necessary (MILP evidence)")
