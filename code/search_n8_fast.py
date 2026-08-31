"""Optimized random search for n=8 using bit-trick swings."""
import random, time
from math import gcd
from functools import reduce

n=8
NB=1<<n; FULL=(1<<NB)-1
# tables
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
pool=[c for c in range(1,NB-1) if 2<=bin(c).count('1')<=6]
random.seed(int(__import__('sys').argv[1]) if len(__import__('sys').argv)>1 else 123)
t0=time.time(); found=0
TRIALS=2000000
for it in range(TRIALS):
    k=random.randint(4,9)
    chosen=random.sample(pool,k)
    ac=[]
    for m in chosen:
        if not any((c&m)==m and c!=m for c in chosen):
            ac.append(m)
    if not ac or 0 in ac: continue
    WIN=0
    for c in ac: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULL
    eta=[bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        found+=1
        if found<=3:
            print(f"  FOUND it={it}: swings={eta} gcd={g}")
            print("   antichain:", sorted(sorted(j+1 for j in range(n) if (c>>j)&1) for c in ac))
    if found>=5: break
    if it%500000==0: print(f"  iter {it}, {time.time()-t0:.0f}s")
print(f"done {TRIALS} trials in {time.time()-t0:.0f}s, found={found}")
