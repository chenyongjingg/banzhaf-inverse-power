"""Build remaining edges avoiding forbidden (base) edges, then verify n=18 closed form."""
import heapq
from math import gcd
from functools import reduce

def build_avoid_forbidden(rem, forbid):
    """Greedy: connect highest remaining-degree vertices, skip forbidden edges."""
    n=len(rem)
    rem=rem[:]
    edges=set()
    if sum(rem)%2!=0: return None
    # greedy matching of remaining degree
    while sum(rem)>0:
        # pick vertex with max positive rem
        v=max((i for i in range(n) if rem[i]>0), key=lambda i: rem[i])
        # pick neighbor with max rem, not forbidden, not v
        cand=[(rem[j], j) for j in range(n) if j!=v and rem[j]>0 and tuple(sorted((v,j))) not in forbid]
        if not cand: return None
        _,u=max(cand)
        edges.add(tuple(sorted((v,u))))
        rem[v]-=1; rem[u]-=1
    return edges

n=18; N=18; sp=17
F=[(0,1,17),(2,3,17),(4,5,17),(6,7,17),(8,9,10),(11,12,13)]
# base edges
G=set()
for X in F:
    for i in range(3):
        for j in range(i+1,3):
            G.add(tuple(sorted((X[i],X[j]))))
# target: 0-13 -> 4, 14-16 -> 5, special -> 15
target=[4]*14+[5]*3+[15]
cur=[0]*N
for a,b in G: cur[a]+=1; cur[b]+=1
rem=[target[i]-cur[i] for i in range(N)]
extra=build_avoid_forbidden(rem, G)
print('extra edges found:', extra is not None, 'count:', len(extra) if extra else 0)
if extra:
    G |= extra
    deg=[0]*N
    for a,b in G: deg[a]+=1; deg[b]+=1
    print('final degrees:', deg)
    print('match target:', deg==target)
    Gset=G; Fset=F
    eta=[]
    for i in range(N):
        ri=sum(1 for X in Fset if i in X)
        ei=sum(1 for X in Fset if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(N-1)+len(Fset)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    print(f'|G|={len(G)} |F|={len(F)} swings: {eta}')
    print('OK:', sorted(x//g for x in eta)==sorted([1]+[2]*(N-1)), 'gcd', g)
    print('e_i=0 all:', all(all(tuple(sorted(set(X)-{i})) in Gset for i in X) for X in F))
