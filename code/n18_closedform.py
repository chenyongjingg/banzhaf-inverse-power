"""Explicit closed-form construction for n=18 (≡4): deg_G(i)+r_i = D=5 for non-special.
F: 4 special triples {n,1,2},{n,3,4},{n,5,6},{n,7,8} + 2 pure triangles {9,10,11},{12,13,14}.
Non-special 1-14: r=1, deg 4. 15,16,17: r=0, deg 5. Special n=18: r_n=4, deg 15."""
import networkx as nx
from math import gcd
from functools import reduce

n=18
N=18; sp=17
F=[(0,1,17),(2,3,17),(4,5,17),(6,7,17),(8,9,10),(11,12,13)]
# base edges from F-triples (all pairs)
G=set()
for X in F:
    for i in range(3):
        for j in range(i+1,3):
            G.add(tuple(sorted((X[i],X[j]))))
# remaining degrees
cur=[0]*N
for a,b in G: cur[a]+=1; cur[b]+=1
target=[0]*N
for i in range(N-1): target[i]=4 if i<14 else 5   # players 0-13 (1-14) deg4, 14-16 deg5
target[sp]=15
rem=[target[i]-cur[i] for i in range(N)]
assert all(r>=0 for r in rem), rem
seq=rem
assert sum(seq)%2==0, sum(seq)
# build remaining edges via Havel-Hakimi on the remaining degree sequence
G2=nx.havel_hakimi_graph(seq)
for u,v in G2.edges(): G.add(tuple(sorted((u,v))))
# verify degrees
deg=[0]*N
for a,b in G: deg[a]+=1; deg[b]+=1
Gset=set(G); Fset=F
eta=[]
for i in range(N):
    ri=sum(1 for X in Fset if i in X)
    ei=sum(1 for X in Fset if i in X and tuple(sorted(set(X)-{i})) not in Gset)
    eta.append(len(G)+(N-1)+len(Fset)-2*deg[i]-2*ri+ei)
g=reduce(gcd,eta)
print(f"n=18: |G|={len(G)} |F|={len(F)} degs={sorted(deg)}")
print(f"swings: {eta}, gcd={g}, OK:", sorted(x//g for x in eta)==sorted([1]+[2]*(N-1)))
# check e_i=0 and monotonicity
for i in range(N):
    for X in Fset:
        if i in X:
            pr=tuple(sorted(set(X)-{i}))
            if pr not in Gset:
                print(f"  e_i>0 at player {i+1} triple {[x+1 for x in X]}")
print("e_i=0 check done; monotone:", all(tuple(sorted((X[a],X[b]))) in Gset for X in F for a in range(3) for b in range(a+1,3)))
