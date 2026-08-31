"""Search uniform-k antichains for n voters with swings proportional to (2,...,2,1)."""
import sys, time
from itertools import combinations
from math import gcd
from functools import reduce

def swings_for(antichain, n):
    full=(1<<n)-1
    # winning mask
    W=0
    for c in antichain:
        # all supersets of c
        rem = (~c) & full
        sub = rem
        while True:
            W |= (c | sub)
            if sub==0: break
            sub = (sub-1) & rem
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        cnt=0
        for m in range(1<<n):
            if m & bit: continue
            if ((W>>m)&1)==0 and ((W>>(m|bit))&1)==1: cnt+=1
        eta[i]=cnt
    return eta

def main():
    n=int(sys.argv[1])
    target=tuple([1]+[2]*(n-1))
    allsubs={}
    for k in range(1,n):
        combs=[sum(1<<(x-1) for x in c) for c in combinations(range(1,n+1),k)]
        allsubs[k]=combs
    t0=time.time()
    found=0
    for k in range(2,n):
        combs=allsubs[k]
        num=1<<len(combs)
        # iterate all subsets of combs as antichains (uniform => any collection of distinct k-sets)
        for s in range(num):
            ac=[]
            x=s; idx=0
            while x:
                if x&1: ac.append(combs[idx])
                x>>=1; idx+=1
            if not ac: continue
            eta=swings_for(ac,n)
            if any(e==0 for e in eta): continue
            g=reduce(gcd,eta)
            if tuple(sorted(e//g for e in eta))==target:
                found+=1
                if found<=6:
                    print(f"  k={k} antichain:", sorted([sorted([j+1 for j in range(n) if (m>>j)&1]) for m in ac]), "swings:", eta)
        print(f"k={k}: done in {time.time()-t0:.1f}s (cumulative)")
    print(f"TOTAL uniform solutions for n={n}: {found}")

main()
