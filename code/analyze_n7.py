"""Analyze complement-graph structure of all n=7 uniform-5 solutions."""
import sys, time
from itertools import combinations
from math import gcd
from functools import reduce

n=7; k=5
NB=1<<n; FULLMASK=(1<<NB)-1
SUP=[0]*NB
for c in range(NB):
    rem=(~c)&(NB-1); sub=rem; s=0
    while True:
        s|=1<<(c|sub)
        if sub==0: break
        sub=(sub-1)&rem
    SUP[c]=s
MaskZ=[0]*n; MaskO=[0]*n; twoi=[1<<i for i in range(n)]
for i in range(n):
    z=o=0
    for m in range(NB):
        if (m>>i)&1: o|=1<<m
        else: z|=1<<m
    MaskZ[i]=z; MaskO[i]=o
combs=[sum(1<<(x-1) for x in c) for c in combinations(range(1,n+1),k)]
target=tuple([1]+[2]*(n-1))

def complement_graph(ac):
    # each winning k-set complement is a 2-set (edge)
    edges=set()
    for c in ac:
        comp = ((1<<n)-1) & ~c
        # comp should be size 2
        a,b=[j for j in range(n) if comp>>j&1]
        edges.add((min(a,b),max(a,b)))
    return edges

t0=time.time()
graphs=set()
rep=None
for s in range(1<<len(combs)):
    ac=[]; x=s; idx=0
    while x:
        if x&1: ac.append(combs[idx])
        x>>=1; idx+=1
    if not ac: continue
    WIN=0
    for c in ac: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULLMASK
    eta=[bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        edges=complement_graph(ac)
        # canonical: degree sequence
        degs=tuple(sorted([len([e for e in edges if i in e]) for i in range(n)]))
        graphs.add((frozenset(edges), degs))
        if rep is None: rep=edges
print("num distinct complement graphs:", len(graphs), " time:", round(time.time()-t0,1),"s")
from collections import Counter
degdist=Counter(d for _,d in graphs)
print("degree sequences of complement graphs:")
for d,c in degdist.most_common(10):
    print("  ", d, "count:", c)
print("example edges:", sorted(sorted((a+1,b+1) for a,b in rep)))
