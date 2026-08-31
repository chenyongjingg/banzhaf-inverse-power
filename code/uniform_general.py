"""Search uniform-k antichains for n voters with swings proportional to (2,...,2,1). Optimized."""
import sys, time
from itertools import combinations
from math import gcd
from functools import reduce

def main():
    n=int(sys.argv[1]); k=int(sys.argv[2])
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
    t0=time.time(); found=0; total=1<<len(combs)
    for s in range(total):
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
            found+=1
            if found<=5:
                print("  antichain:", sorted(sorted(j+1 for j in range(n) if (c>>j)&1) for c in ac), "swings:", eta)
        if s % 500000 == 0 and s>0:
            print(f"  progress {s}/{total} ({time.time()-t0:.0f}s)")
    print(f"n={n} k={k}: {found} solutions in {time.time()-t0:.1f}s")
main()
