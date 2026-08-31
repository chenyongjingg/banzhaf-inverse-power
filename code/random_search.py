"""Random search for n=7: simple games with swings proportional to (2,...,2,1)."""
import sys, time, random
from math import gcd
from functools import reduce

def make_tables(n):
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
    return SUP, MaskZ, MaskO, twoi, FULLMASK

def main():
    random.seed(int(sys.argv[2]) if len(sys.argv)>2 else 1)
    n=int(sys.argv[1])
    SUP,MaskZ,MaskO,twoi,FULLMASK=make_tables(n)
    target=tuple([1]+[2]*(n-1))
    pool=[c for c in range(1,(1<<n)-1) if bin(c).count('1')>=2]  # size>=2
    trials=int(sys.argv[3]) if len(sys.argv)>3 else 200000
    t0=time.time()
    for it in range(trials):
        # random antichain: pick subset then minimize
        k=random.randint(3,7)
        chosen=random.sample(pool,k)
        # keep minimal elements
        ac=[]
        for m in chosen:
            if not any((c&m)==m and c!=m for c in chosen):  # m minimal among chosen (no other chosen proper subset of m)
                ac.append(m)
        if not ac: continue
        WIN=0
        for c in ac: WIN|=SUP[c]
        NOTWIN=(~WIN)&FULLMASK
        eta=[bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
        if any(e==0 for e in eta): continue
        g=reduce(gcd,eta)
        if tuple(sorted(e//g for e in eta))==target:
            print(f"FOUND at iter {it} in {time.time()-t0:.1f}s")
            print("  antichain:", sorted(sorted(j+1 for j in range(n) if (c>>j)&1) for c in ac))
            print("  swings:", eta, "gcd:", g)
            return
    print(f"no solution in {trials} trials ({time.time()-t0:.1f}s)")
main()
