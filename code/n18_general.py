"""General construction for n=18 (≡4): base D, f triples, q special triples.
Builds G with degree targets, avoiding forbidden F-edges, via CP-SAT for the extra edges."""
from ortools.sat.python import cp_model
from math import gcd
from functools import reduce

def construct(n, D, f, q):
    p=f-q
    c=(2*D*(n-4)+4*(n-1)-2*f)//7
    if c<=0 or (2*D*(n-4)+4*(n-1)-2*f)%7!=0: return None
    s=D + c//2 - q   # special degree
    # F-triples: q special {n,..}, p pure
    F=[]; sp=n-1
    # pure triangles first (players 0..3p-1), then special triples (3p..3p+2q-1)
    F=[]; idx=0
    for t in range(p):
        F.append((idx,idx+1,idx+2)); idx+=3
    st=[]
    for t in range(q):
        F.append((idx,idx+1,sp)); st.append((idx,idx+1)); idx+=2
    # target degrees: F-players D-1 (r=1), non-F D (r=0), special s
    Np=idx  # number of non-special in F
    if Np>n-1: return None
    target=[0]*n
    for i in range(Np): target[i]=D-1
    for i in range(Np, n-1): target[i]=D
    target[sp]=s
    # base edges (F-triple pairs)
    G=set()
    for X in F:
        for i in range(3):
            for j in range(i+1,3): G.add(tuple(sorted((X[i],X[j]))))
    cur=[0]*n
    for a,b in G: cur[a]+=1; cur[b]+=1
    rem=[target[i]-cur[i] for i in range(n)]
    if any(r<0 for r in rem) or sum(rem)%2!=0:
        return None
    # CP-SAT: find extra edges with degree rem avoiding forbidden G
    model=cp_model.CpModel()
    pairs=[(a,b) for a in range(n) for b in range(a+1,n) if tuple(sorted((a,b))) not in G]
    pe={(a,b):model.NewBoolVar(f'e{a}_{b}') for (a,b) in pairs}
    for i in range(n):
        model.Add(sum(pe[e] for e in pairs if i in e)==rem[i])
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=30
    status=solver.Solve(model)
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    for (a,b),v in pe.items():
        if solver.Value(v)==1: G.add(tuple(sorted((a,b))))
    # verify
    deg=[0]*n
    for a,b in G: deg[a]+=1; deg[b]+=1
    Gset=G
    eta=[]
    for i in range(n):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(n-1))
    return c, s, G, F, deg, eta, ok

# try several (D,f,q) for n=18
n=18
for D in (3,4,5):
    for f in (6,13):
        for q in range(0,f+1):
            r=construct(n,D,f,q)
            if r is not None:
                c,s,G,F,deg,eta,ok=r
                print(f"n=18 D={D} f={f} q={q}: c={c} s={s} |G|={len(G)} |F|={len(F)} OK={ok}")
                if ok:
                    print(f"   F={F}")  # closed form found!
                    break
            if r is not None and r[-1]: break
