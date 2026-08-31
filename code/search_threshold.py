"""Search the threshold+exceptions family for swings proportional to (2,...,2,1).
v(S)=1 iff |S|>=n-1 or (|S|=n-2, comp notin E) or (|S|=n-3, comp in F).
Uses formula: eta_i = C(n-1,2) + |F| - |E| + 2deg_E(i) - 2r_i + e_i."""
import random, time, sys
from math import gcd
from functools import reduce

def main():
    n=int(sys.argv[1])
    seed=int(sys.argv[2]) if len(sys.argv)>2 else 0
    trials=int(sys.argv[3]) if len(sys.argv)>3 else 200000
    random.seed(seed)
    Es=[(a,b) for a in range(n) for b in range(a+1,n)]
    Fs=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    target=tuple([1]+[2]*(n-1))
    C=(n-1)*(n-2)//2
    t0=time.time()
    for it in range(trials):
        E=random.sample(Es, random.randint(0,len(Es)))
        F=random.sample(Fs, random.randint(0,min(12,len(Fs))))
        Em=set(tuple(sorted(e)) for e in E)
        deg=[0]*n
        for a,b in E: deg[a]+=1; deg[b]+=1
        r=[0]*n; e=[0]*n
        for X in F:
            Xs=set(X)
            for i in X: r[i]+=1
            for i in X:
                pr=tuple(sorted(Xs-{i}))
                if pr in Em: e[i]+=1
        f=len(F); el=len(E)
        eta=[C+f-el+2*deg[i]-2*r[i]+e[i] for i in range(n)]
        if any(v<=0 for v in eta): continue
        g=reduce(gcd,eta)
        if tuple(sorted(v//g for v in eta))==target:
            print(f"FOUND n={n} it={it} in {time.time()-t0:.1f}s: swings={eta} gcd={g}")
            print("  E(edges):", E)
            print("  F(triples):", F)
            return
    print(f"n={n}: none in {trials} trials, {time.time()-t0:.1f}s")
main()
