import time
from math import gcd
from functools import reduce
n=6; NB=1<<n; FULLMASK=(1<<NB)-1
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
def swings_fast(ac):
    WIN=0
    for c in ac: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULLMASK
    return [bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
def antichains(n):
    masks=list(range(NB)); results=[]
    def rec(chosen,start):
        results.append(tuple(chosen))
        for idx in range(start,len(masks)):
            m=masks[idx]; ok=True
            for c in chosen:
                if (c&m)==c: ok=False; break
            if ok: chosen.append(m); rec(chosen,idx+1); chosen.pop()
    rec([],0); return results
target=tuple([1]+[2]*(n-1))
sols=[]
for ac in antichains(n):
    if not ac or 0 in ac: continue
    eta=swings_fast(ac)
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target: sols.append((ac,eta))
def fmt(ac):
    return sorted(sorted(j+1 for j in range(n) if (c>>j)&1) for c in ac)
pairs=[]; fours=[]
for ac,eta in sols:
    sz=tuple(sorted(bin(c).count('1') for c in ac))
    (pairs if sz==(2,2,2,2,2,2,2,2,3) else fours).append(ac)
print("=== FAMILY A: 8 pairs + 1 triple (2 examples) ===")
for ac in pairs[:2]:
    print("  ", fmt(ac))
print("=== FAMILY B: 7 four-sets (3 examples) ===")
for ac in fours[:3]:
    print("  ", fmt(ac))
