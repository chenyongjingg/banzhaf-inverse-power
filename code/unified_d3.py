"""UNIFIED construction with base degree d=3 for ALL residues:
f = smallest non-negative integer with f ≡ 5*(n mod 7) (mod 7).
f triangles (F-triples = G-triangles), special degree s=(c+6)/2.
c = (10(n-1) - 2f - 18)/7. Valid when s <= n-1-3f."""
import networkx as nx
from math import gcd
from functools import reduce

def unified(n):
    r=n%7
    # smallest f >= 0 with f ≡ 5r (mod 7)
    f=(5*r)%7
    c=(10*(n-1)-2*f-18)//7
    if c<=0: return None
    s=(c+6)//2
    Rcount=(n-1)-3*f
    if s>Rcount: return None
    seq=[3]*Rcount+[s]
    if not nx.is_graphical(seq): return None
    # build
    F=[]; G=[]
    for t in range(f):
        a,b,cc=3*t,3*t+1,3*t+2
        F.append((a,b,cc)); G.append((a,b)); G.append((a,cc)); G.append((b,cc))
    R=list(range(3*f,n-1))
    G2=nx.havel_hakimi_graph(seq)
    verts=R+[n-1]
    for u,v in G2.edges(): G.append((verts[u],verts[v]))
    return c,s,f,G,F

def verify(n):
    r=unified(n)
    if r is None:
        print(f"n={n} (≡{n%7}): infeasible"); return
    c,s,f,G,F=r
    N=n; Gset=set(tuple(sorted(e)) for e in G); deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(N):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(N-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(N-1))
    print(f"n={n} (≡{n%7}) f={f}: c={c} s={s} OK={ok}")

print("=== Unified d=3 construction, n in [67,110] all residues ===")
ok_all=True
for n in range(67,111):
    r=unified(n)
    if r is None: ok_all=False
print("all [67,110] feasible:", ok_all)
print("\n=== sample verification ===")
for n in (67,68,70,71,72,73,74,75,76,77,78,79,80,85,90,95,100,105,110):
    verify(n)
