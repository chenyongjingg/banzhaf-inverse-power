"""Determine smallest feasible n for each hard residue with general construction."""
import networkx as nx
from math import gcd
from functools import reduce

def construct(n,f,q):
    c=(10*(n-1)-2*f-18)//7
    if c<=0: return None
    s=(c+6)//2 - q
    Rcount=(n-1)-3*f+q
    if s<0 or s-2*q>Rcount: return None
    G=[];F=[];idx=0
    p=f-q
    for t in range(p):
        a,b,cc=idx,idx+1,idx+2; idx+=3
        F.append((a,b,cc)); G+= [(a,b),(a,cc),(b,cc)]
    for t in range(q):
        a,b=idx,idx+1; idx+=2
        F.append((a,b,n-1)); G+= [(a,b),(a,n-1),(b,n-1)]
    R=list(range(idx,n-1))
    seq=[3]*len(R)+[s-2*q]
    if not nx.is_graphical(seq): return None
    G2=nx.havel_hakimi_graph(seq); verts=R+[n-1]
    for u,v in G2.edges(): G.append((verts[u],verts[v]))
    return c,s,G,F

def verify(n,f,q):
    r=construct(n,f,q)
    if r is None: return False
    c,s,G,F=r; N=n
    Gset=set(tuple(sorted(e)) for e in G); deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(N):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(N-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    return sorted(x//g for x in eta)==sorted([1]+[2]*(N-1))

# test specific small n
print("=== edge small n ===")
for n in (15,18,19,22,25,26):
    r=n%7
    for f0 in (5,6,4):
        if f0!={(1):5,(4):6,(5):4}[r]: continue
        found=None
        for q in range(0,f0+1):
            if verify(n,f0,q): found=q; break
        # try larger f
        if found is None:
            for f2 in (f0+7,):
                for q in range(0,f2+1):
                    if verify(n,f2,q): found=q; f0=f2; break
                if found is not None: break
        print(f"n={n} (≡{r}): smallest feasible q={found} (f={f0})")

# smallest feasible n per residue
print()
print("=== smallest feasible n per hard residue ===")
for r,f0 in [(1,5),(4,6),(5,4)]:
    for n in range(6,100):
        if n%7!=r: continue
        ok=False
        for q in range(0,f0+1):
            if verify(n,f0,q): ok=True; break
        if not ok:
            for f2 in (f0+7,):
                for q in range(0,f2+1):
                    if verify(n,f2,q): ok=True; break
        if ok:
            print(f"  n≡{r}: smallest = {n}")
            break
