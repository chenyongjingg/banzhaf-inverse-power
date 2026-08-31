"""Threshold-family search WITH monotonicity (E ∩ Pairs(F) = empty)."""
import random, time, sys
from math import gcd
from functools import reduce

def main():
    n=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 0
    trials=int(sys.argv[3]) if len(sys.argv)>3 else 300000
    random.seed(seed)
    Es=[(a,b) for a in range(n) for b in range(a+1,n)]
    Fs=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    target=tuple([1]+[2]*(n-1))
    C=(n-1)*(n-2)//2
    t0=time.time()
    for it in range(trials):
        F=random.sample(Fs, random.randint(0,min(10,len(Fs))))
        # pairs within F-triples (forbidden in E)
        forb=set()
        for X in F:
            for i in range(3):
                for j in range(i+1,3):
                    forb.add(tuple(sorted((X[i],X[j]))))
        avail=[e for e in Es if e not in forb]
        E=random.sample(avail, random.randint(0,len(avail)))
        Em=set(E)
        deg=[0]*n
        for a,b in E: deg[a]+=1; deg[b]+=1
        r=[0]*n; e=[0]*n
        for X in F:
            Xs=set(X)
            for i in X: r[i]+=1
            for i in X:
                if tuple(sorted(Xs-{i})) in Em: e[i]+=1
        f=len(F); el=len(E)
        eta=[C+f-el+2*deg[i]-2*r[i]+e[i] for i in range(n)]
        if any(v<=0 for v in eta): continue
        g=reduce(gcd,eta)
        if tuple(sorted(v//g for v in eta))==target:
            print(f"FOUND n={n} it={it} in {time.time()-t0:.1f}s: swings={eta} gcd={g}")
            print("  E:", sorted(E)); print("  F:", sorted(F))
            return
    print(f"n={n}: none in {trials} trials ({time.time()-t0:.1f}s)")
main()
