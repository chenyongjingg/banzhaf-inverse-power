"""Random search for n=8 with hub-structured antichains (special player n in many coalitions)."""
import random, time
from math import gcd
from functools import reduce

n=8
NB=1<<n; FULL=(1<<NB)-1
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
target=tuple([1]+[2]*(n-1))
pbit=1<<(n-1)
# pool: coalitions containing player n (hub), sizes 2..6; and non-hub coalitions sizes 2..6
hub_pool=[c for c in range(1,NB-1) if (c&pbit) and 2<=bin(c).count('1')<=6]
oth_pool=[c for c in range(1,NB-1) if not (c&pbit) and 2<=bin(c).count('1')<=6]
random.seed(777)
t0=time.time(); found=0
for it in range(3000000):
    ac=[]
    # sample hub coalitions
    for m in random.sample(hub_pool, random.randint(2,6)):
        ac.append(m)
    for m in random.sample(oth_pool, random.randint(0,4)):
        ac.append(m)
    # minimize to antichain
    ac2=[]
    for m in ac:
        if not any((c&m)==m and c!=m for c in ac):
            ac2.append(m)
    if not ac2 or 0 in ac2: continue
    WIN=0
    for c in ac2: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULL
    eta=[bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        found+=1
        print(f"  FOUND it={it}: swings={eta} gcd={g}")
        print("   antichain:", sorted(sorted(j+1 for j in range(n) if (c>>j)&1) for c in ac2))
        if found>=5: break
    if it%1000000==0: print(f"  iter {it}, {time.time()-t0:.0f}s")
print(f"done, found={found}, {time.time()-t0:.0f}s")
