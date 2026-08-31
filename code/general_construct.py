"""General construction with special-triples: f triples, q of them contain special.
p=f-q pure triangles. 2q special-triple players + 3p pure players, degree 2, r=1.
R players degree 3. Special degree s=(c+6)/2 - q.
Valid when s-2q <= |R| (special's R-edges fit), |R|=n-1-3f+q."""
import networkx as nx
from math import gcd
from functools import reduce

def construct(n, f, q):
    c=(10*(n-1)-2*f-18)//7
    if c<=0: return None
    s=(c+6)//2 - q
    p=f-q
    Rcount=(n-1)-3*f+q
    if s<0 or s-2*q > Rcount: return None
    # edges among F-players (pure triangles + partner edges in special triples)
    G=[]; F=[]
    # pure triangles: players 0..3p-1
    idx=0
    for t in range(p):
        a,b,cc=idx,idx+1,idx+2; idx+=3
        F.append((a,b,cc)); G.append((a,b)); G.append((a,cc)); G.append((b,cc))
    # special triples: players idx..idx+2q-1, plus special
    st_players=[]
    for t in range(q):
        a,b=idx,idx+1; idx+=2
        st_players.append((a,b))
        F.append((a,b,n-1)); G.append((a,b)); G.append((a,n-1)); G.append((b,n-1))
    # R players: idx..n-2, special = n-1. R-edges: special connects to (s-2q) R players,
    # R players degree 3.
    R=list(range(idx, n-1))
    seq=[3]*len(R)+[s-2*q]
    if not nx.is_graphical(seq): return None
    G2=nx.havel_hakimi_graph(seq)
    verts=R+[n-1]
    for u,v in G2.edges(): G.append((verts[u],verts[v]))
    return c,s,G,F

def verify(n,f,q):
    r=construct(n,f,q)
    if r is None:
        print(f"n={n} f={f} q={q}: infeasible"); return
    c,s,G,F=r
    N=n; Gset=set(tuple(sorted(e)) for e in G); deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(N):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(N-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(N-1))
    print(f"n={n} f={f} q={q}: c={c} s={s} |G|={len(G)} |F|={len(F)} OK={ok}")

# small hard-residue n: find feasible (f,q)
print("=== smaller hard-residue n ===")
for n in (22,29,36,43,50, 25,32,39,46,53,60, 26,33,40,47,54,61):
    r=n%7
    f={(1):5,(4):6,(5):4}[r]
    found=False
    for q in range(0,f+1):
        rr=construct(n,f,q)
        if rr is not None:
            verify(n,f,q); found=True; break
    if not found:
        # try larger f
        for f2 in (f+7, f+14):
            for q in range(0,f2+1):
                rr=construct(n,f2,q)
                if rr is not None:
                    verify(n,f2,q); found=True; break
            if found: break
        if not found: print(f"n={n}: no construction found")
