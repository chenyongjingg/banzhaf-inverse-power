"""Background search for n=8 over complement-antichains H (pairs + triples)."""
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
pairs=[(1<<a)|(1<<b) for a in range(n) for b in range(a+1,n)]
triples=[(1<<a)|(1<<b)|(1<<c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
random.seed(999)
t0=time.time(); found=0
for it in range(20000000):
    H=[]
    # random triples (0..3)
    for tr in random.sample(triples, random.randint(0,3)):
        H.append(tr)
    # pairs avoiding triples (antichain: pair not subset of any triple)
    covered=set()
    for tr in H:
        for a in range(n):
            for b in range(a+1,n):
                p=(1<<a)|(1<<b)
                if (p&~tr)==0: covered.add(p)
    avail=[p for p in pairs if p not in covered]
    for p in random.sample(avail, random.randint(0,6)):
        H.append(p)
    if not H: continue
    # complement antichain -> winning sets
    win_sets=[((1<<n)-1)&~x for x in H]
    WIN=0
    for c in win_sets: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULL
    eta=[bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        found+=1
        print(f"FOUND it={it}: swings={eta} gcd={g}", flush=True)
        print("  H(complements):", sorted(sorted(j+1 for j in range(n) if (x>>j)&1) for x in H), flush=True)
        print("  winning sets:", sorted(sorted(j+1 for j in range(n) if ((((1<<n)-1)&~x)>>j)&1) for x in H), flush=True)
        if found>=3: break
    if it%2000000==0:
        print(f"  iter {it}, {time.time()-t0:.0f}s, found={found}", flush=True)
print(f"DONE {it+1} trials, found={found}, {time.time()-t0:.0f}s", flush=True)
