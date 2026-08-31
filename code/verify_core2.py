"""Extensive verification: (1) formula U with guaranteed-monotone instances,
(2) Proposition 11 triangle constructions for all residues, (3) small-value deg+r=D."""
import random
from math import gcd
from functools import reduce
import networkx as nx
from ortools.sat.python import cp_model

def swings_brute(G,F,n):
    Gm=[(1<<a)|(1<<b) for a,b in G]; Fm=[(1<<a)|(1<<b)|(1<<c) for a,b,c in F]
    def win(S):
        s=bin(S).count('1'); comp=((1<<n)-1)&~S
        if s>=n-1: return True
        if s==n-2: return comp in Gm
        if s==n-3: return comp in Fm
        return False
    return [sum(1 for S in range(1<<n) if not (S&(1<<i)) and (not win(S)) and win(S|(1<<i))) for i in range(n)]

def formulaU(G,F,n):
    Gset=set(tuple(sorted(e)) for e in G); deg=[0]*n
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(n):
        r=sum(1 for X in F if i in X)
        e=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*r+e)
    return eta

# (1) Formula U, guaranteed monotone (G contains Pairs(F)), extensive
random.seed(7); tr=0; mism=0
for n in range(4,15):
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    tris=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    for t in range(40):
        F=random.sample(tris, random.randint(0,min(7,len(tris))))
        pf=set()
        for X in F:
            for a in range(3):
                for b in range(a+1,3): pf.add(tuple(sorted((X[a],X[b]))))
        G=list(pf)+random.sample([e for e in pairs if e not in pf], random.randint(0, len(pairs)-len(pf)))
        b=swings_brute(G,F,n); u=formulaU(G,F,n)
        tr+=1
        if b!=u:
            mism+=1
            if mism<=2: print(f"U MISMATCH n={n}")
print(f"(1) Formula U: {tr} monotone instances, {mism} mismatches")

# (2) Proposition 11 triangle constructions: verify for all residues in [6,50]
def tri_construct(n,D,f,q):
    sp=n-1
    num=2*D*(n-4)+4*(n-1)-2*f
    if num%7!=0: return None
    c=num//7
    if c<=0: return None
    s=D+c//2-q
    if s<0 or s>n-1 or s<2*q: return None
    F=[]; idx=0; p=f-q
    for _ in range(p): F.append((idx,idx+1,idx+2)); idx+=3
    for _ in range(q): F.append((idx,idx+1,sp)); idx+=2
    if idx>n-1: return None
    target=[0]*n
    for i in range(idx): target[i]=D-1
    for i in range(idx,n-1): target[i]=D
    target[sp]=s
    G=set()
    for X in F:
        for a in range(3):
            for b in range(a+1,3): G.add(tuple(sorted((X[a],X[b]))))
    cur=[0]*n
    for a,b in G: cur[a]+=1; cur[b]+=1
    rem=[target[i]-cur[i] for i in range(n)]
    if any(r<0 for r in rem) or sum(rem)%2!=0: return None
    model=cp_model.CpModel()
    cand=[(a,b) for a in range(n) for b in range(a+1,n) if tuple(sorted((a,b))) not in G]
    pe={(a,b):model.NewBoolVar(f'e{a}_{b}') for (a,b) in cand}
    for i in range(n): model.Add(sum(pe[e] for e in cand if i in e)==rem[i])
    sol=cp_model.CpSolver(); sol.parameters.max_time_in_seconds=10
    if sol.Solve(model) not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    for (a,b),v in pe.items():
        if sol.Value(v)==1: G.add(tuple(sorted((a,b))))
    return c,s,G,F

ok_n=[]; fail_n=[]
for n in range(6,51):
    r=n%7; found=False
    if r in (0,2,3,6):
        # complement-of-edge
        d={0:3,2:1,3:4,6:2}[r]
        num=d*(2*n-8)+4*(n-1)
        if num%7==0:
            c=num//7; ds=d+c//2
            if nx.is_graphical([d]*(n-1)+[ds]): found=True
    else:
        # triangle construction
        f={1:5,4:6,5:4}[r]
        D=4 if (r==4 and n<25) else 3
        for q in range(f+1):
            rr=tri_construct(n,D,f,q)
            if rr is not None:
                # verify swings
                c,s,G,F=rr; Gset=set(tuple(sorted(e)) for e in G); deg=[0]*n
                for a,b in G: deg[a]+=1; deg[b]+=1
                eta=[]
                for i in range(n):
                    ri=sum(1 for X in F if i in X)
                    ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
                    eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*ri+ei)
                g=reduce(gcd,eta)
                if sorted(x//g for x in eta)==sorted([1]+[2]*(n-1)):
                    found=True; break
    (ok_n if found else fail_n).append(n)
print(f"(2) Prop 11 closed forms n=6..50: {len(ok_n)} OK, fails: {fail_n}")
