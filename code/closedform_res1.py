"""Closed-form construction for n ≡ 1 (mod 7), n >= 57:
- 5 disjoint triangles (players 1..15) = F-triples = G-triangles (deg 2, r=1)
- R = players 16..n-1, degree 3
- special n, degree 5k+1
Verify swings via unified formula U."""
import networkx as nx
from math import gcd
from functools import reduce

def build(n):
    k=(n-1)//7
    c=10*k-4
    f=5
    # F-triples = triangles on 1..15 (0-indexed 0..14)
    tris=[(0,1,2),(3,4,5),(6,7,8),(9,10,11),(12,13,14)]
    # G = triangle edges + graph on R(15..n-2) ∪ special(n-1)
    G=[]
    for T in tris:
        for i in range(3):
            for j in range(i+1,3):
                G.append((T[i],T[j]))
    R=list(range(15,n-1))
    dspec=5*k+1
    if len(R) < dspec:
        return None, None, None, None, None
    seq=[3]*len(R)+[dspec]
    if not nx.is_graphical(seq):
        return None,None,None,None,None
    G2=nx.havel_hakimi_graph(seq)
    # relabel R ∪ {special} to actual indices
    verts=R+[n-1]
    for u,v in G2.edges():
        G.append((verts[u],verts[v]))
    return c, G, tris, dspec, len(G)

def verify(n):
    r=build(n)
    if r[0] is None:
        print(f"n={n}: construction infeasible"); return
    c,G,F,dspec,EG= r
    N=n
    Gset=set(tuple(sorted(e)) for e in G)
    deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(N):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(EG+(N-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok = sorted(x//g for x in eta)==sorted([1]+[2]*(N-1))
    print(f"n={n}: c={c} deg_special={dspec} |G|={EG} |F|={len(F)} swings_ok={ok} gcd={g}")

for n in (57, 64, 71, 78, 85, 92, 99, 113):
    verify(n)
