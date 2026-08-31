"""UNIFIED closed-form construction for hard residues (n ≡ 1,4,5 mod 7).
f triangles (F-triples = G-triangles, 3f players deg 2, r=1);
R = n-1-3f players deg 3; special deg s=(c+6)/2, not in F.
c = (10(n-1) - 2f - 18)/7.  f=5 (n≡1), 6 (n≡4), 4 (n≡5)."""
import networkx as nx
from math import gcd
from functools import reduce

def build(n, f):
    c=(10*(n-1)-2*f-18)//7
    s=(c+6)//2
    Rcount = (n-1) - 3*f
    if s > Rcount:  # special degree exceeds available R players
        return None, None, None, None
    # triangle players: 0..3f-1, partition into f triangles
    F=[]
    G=[]
    for t in range(f):
        a,b,cc = 3*t, 3*t+1, 3*t+2
        F.append((a,b,cc))
        G.append((a,b)); G.append((a,cc)); G.append((b,cc))
    # R = 3f .. n-2, special = n-1
    R=list(range(3*f, n-1))
    seq=[3]*Rcount+[s]
    if not nx.is_graphical(seq):
        return None,None,None,None
    G2=nx.havel_hakimi_graph(seq)
    verts=R+[n-1]
    for u,v in G2.edges():
        G.append((verts[u],verts[v]))
    return c, G, F, s

def verify(n, f):
    r=build(n,f)
    if r[0] is None:
        print(f"n={n}: infeasible"); return
    c,G,F,s = r
    N=n
    Gset=set(tuple(sorted(e)) for e in G)
    deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(N):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(N-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok = sorted(x//g for x in eta)==sorted([1]+[2]*(N-1))
    print(f"n={n} (≡{n%7}) f={f}: c={c} s={s} |G|={len(G)} |F|={len(F)} OK={ok}")

# n ≡ 1 (f=5), n>=57
for n in (57,64,71,78,85,92,99,106,113): verify(n,5)
# n ≡ 4 (f=6), n>=67
for n in (67,74,81,88,95,102,109,116): verify(n,6)
# n ≡ 5 (f=4), n>=47
for n in (47,54,61,68,75,82,89,96,103,110): verify(n,4)
