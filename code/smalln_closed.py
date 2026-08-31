"""Try closed-form constructions for n=8,10,11,12,15 via general construction."""
from ortools.sat.python import cp_model
from math import gcd
from functools import reduce

def construct(n, D, f, q):
    p=f-q; sp=n-1
    num=2*D*(n-4)+4*(n-1)-2*f
    if num%7!=0: return None
    c=num//7
    if c<=0: return None
    s=D+c//2-q
    if s<0 or s>n-1: return None
    if s<2*q: return None
    F=[]; idx=0
    for t in range(p):
        F.append((idx,idx+1,idx+2)); idx+=3
    for t in range(q):
        F.append((idx,idx+1,sp)); idx+=2
    if idx>n-1: return None
    target=[0]*n
    for i in range(idx): target[i]=D-1
    for i in range(idx,n-1): target[i]=D
    target[sp]=s
    G=set()
    for X in F:
        for i in range(3):
            for j in range(i+1,3): G.add(tuple(sorted((X[i],X[j]))))
    cur=[0]*n
    for a,b in G: cur[a]+=1; cur[b]+=1
    rem=[target[i]-cur[i] for i in range(n)]
    if any(r<0 for r in rem) or sum(rem)%2!=0: return None
    model=cp_model.CpModel()
    pairs=[(a,b) for a in range(n) for b in range(a+1,n) if tuple(sorted((a,b))) not in G]
    pe={(a,b):model.NewBoolVar(f'e{a}_{b}') for (a,b) in pairs}
    for i in range(n):
        model.Add(sum(pe[e] for e in pairs if i in e)==rem[i])
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=20
    if solver.Solve(model) not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    for (a,b),v in pe.items():
        if solver.Value(v)==1: G.add(tuple(sorted((a,b))))
    deg=[0]*n
    for a,b in G: deg[a]+=1; deg[b]+=1
    Gset=G; eta=[]
    for i in range(n):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(n-1))
    mono=all(tuple(sorted((X[a],X[b]))) in G for X in F for a in range(3) for b in range(a+1,3))
    return c,s,G,F,ok,mono

print("=== try closed-form for small n ===")
for n in (8,10,11,12,15):
    r=n%7
    # f from modular condition for D=3: f ≡ 5r mod 7
    f0=(5*r)%7
    found=None
    for f in (f0, f0+7):
        if f==0: continue
        for D in (2,3,4,5):
            for q in range(0, f+1):
                rr=construct(n,D,f,q)
                if rr is not None and rr[4]:
                    found=(D,f,q,rr[0],rr[1])
                    break
            if found: break
        if found: break
    if found:
        print(f"n={n} (≡{r}): CLOSED FORM D={found[0]} f={found[1]} q={found[2]} c={found[3]} s={found[4]}")
    else:
        print(f"n={n} (≡{r}): no closed form found in this family")
