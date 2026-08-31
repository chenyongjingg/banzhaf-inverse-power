"""Generate explicit (G,F) closed-form constructions for all n in a range, verified.
Uses: complement-of-edge (≡0,2,3,6), triangle construction (≡1,4,5), deg+r=D for small values."""
import networkx as nx
from ortools.sat.python import cp_model
from math import gcd
from functools import reduce
import json

def comp_edge(n, d):
    """Complement-of-edge: G graph, F empty. Returns (G_edges, F_triples)."""
    num=d*(2*n-8)+4*(n-1)
    if num%7: return None
    c=num//7; ds=d+c//2
    seq=[d]*(n-1)+[ds]
    if not nx.is_graphical(seq): return None
    G=nx.havel_hakimi_graph(seq)
    return [(int(u),int(v)) for u,v in G.edges()], [], c

def triangle_construct(n, D, f, q):
    """Triangle construction with special triples. Returns (G, F, c)."""
    sp=n-1
    num=2*D*(n-4)+4*(n-1)-2*f
    if num%7!=0: return None
    c=num//7
    if c<=0: return None
    s=D+c//2-q
    if s<0 or s>n-1: return None
    if s<2*q: return None
    F=[]; idx=0
    p=f-q
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
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=15
    if solver.Solve(model) not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    for (a,b),v in pe.items():
        if solver.Value(v)==1: G.add(tuple(sorted((a,b))))
    return list(G), F, c

def verify(n, G, F):
    Gset=set(tuple(sorted(e)) for e in G); deg=[0]*n
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(n):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(n-1))
    mono=all(tuple(sorted((X[a],X[b]))) in Gset for X in F for a in range(3) for b in range(a+1,3))
    return ok and mono

# small-value explicit (G,F) from earlier CP-SAT (D-structure) - we'll search if needed
small_D = {8:(4,2), 10:(3,1), 11:(6,6), 12:(5,6), 15:(4,6), 18:(4,6)}
def small_construct(n):
    """deg+r=D construction for small values via CP-SAT."""
    sp=n-1; D=fcap=small_D[n][0]
    model=cp_model.CpModel()
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    triples=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    xe={e:model.NewBoolVar(f"x{e}") for e in pairs}
    y={T:model.NewBoolVar(f"y{T}") for T in triples}
    c2=model.NewIntVar(1,500,"c2")
    for i in range(n-1):
        model.Add(sum(xe[e] for e in pairs if i in e)+sum(y[T] for T in triples if i in T)==D)
    model.Add(sum(xe[e] for e in pairs if sp in e)+sum(y[T] for T in triples if sp in T)==D+c2)
    for i in range(n):
        model.Add(sum(y[T] for T in triples if i in T)<=3)
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            model.AddImplication(y[T], xe[e])
    for i in range(n):
        expr=sum(xe[e] for e in pairs)+(n-1)+sum(y[T] for T in triples)-2*sum(xe[e] for e in pairs if i in e)-2*sum(y[T] for T in triples if i in T)
        model.Add(expr==(4*c2 if i!=sp else 2*c2))
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=20
    if solver.Solve(model) not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    G=[e for e in pairs if solver.Value(xe[e])==1]
    F=[T for T in triples if solver.Value(y[T])==1]
    return G,F,2*solver.Value(c2)

# main: generate for n=6..40
print("Generating appendix (G,F) for n=6..40 ...")
results={}
for n in range(6,41):
    r=n%7
    sol=None
    if n in small_D:
        sol=small_construct(n)
        method="deg+r=D"
    elif r in (0,2,3,6):
        d={0:3,2:1,3:4,6:2}[r]
        rr=comp_edge(n,d)
        if rr: sol=(rr[0],rr[1],rr[2]); method="complement-edge"
        else:
            # fallback D=3
            sol=triangle_construct(n,3,{(0):0,(2):3,(3):1,(6):2}[r],0) if False else None
    elif r==1:
        # triangle, D=3 f=5, find q
        for q in range(6):
            s=triangle_construct(n,3,5,q)
            if s: sol=(s[0],s[1],s[2]); method=f"triangle(D3,f5,q{q})"; break
        if sol is None:
            s=small_construct(n) if n in small_D else None
            if s: sol=s; method="deg+r=D"
    elif r==4:
        D=4 if n<25 else 3
        for q in range(7):
            s=triangle_construct(n,D,6,q)
            if s: sol=(s[0],s[1],s[2]); method=f"triangle(D{D},f6,q{q})"; break
    elif r==5:
        D=3
        for q in range(5):
            s=triangle_construct(n,D,4,q)
            if s: sol=(s[0],s[1],s[2]); method=f"triangle(D3,f4,q{q})"; break
    if sol is None:
        # final fallback: deg+r=D search
        s=small_construct(n) if n in small_D else None
        if s: sol=s; method="deg+r=D"
    if sol and verify(n, sol[0], sol[1]):
        results[n]={'c':sol[2],'G':[list(map(int,e)) for e in sol[0]],'F':[list(map(int,X)) for X in sol[1]],'method':method}
        print(f"n={n}: c={sol[2]} |G|={len(sol[0])} |F|={len(sol[1])} ({method})")
    else:
        print(f"n={n}: NO CONSTRUCTION")
json.dump(results, open(r'data/appendix-data.json','w'), indent=1)
print(f"\nSaved {len(results)} constructions to appendix-data.json")
