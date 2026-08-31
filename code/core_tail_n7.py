"""Exhaustive core+tail search for n=7: core {12,13,14,23,24,345} + subset of tail pool."""
import time
from math import gcd
from functools import reduce

def swings_antichain(ac, n):
    def win(m): return any((m&c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

n=7
def S(*xs): return sum(1<<(x-1) for x in xs)
core=[S(1,2),S(1,3),S(1,4),S(2,3),S(2,4),S(3,4,5)]
pool_names={}
pool=[]
def add(*xs): pool.append(S(*xs))
add(3,6); add(4,6); add(5,6); add(3,7); add(4,7); add(5,7); add(6,7)
add(3,4,6); add(3,4,7); add(3,5,6); add(3,5,7); add(4,5,6); add(4,5,7); add(3,6,7); add(4,6,7); add(5,6,7)
target=tuple([1]+[2]*(n-1))
t0=time.time(); found=0
for mask in range(1<<len(pool)):
    ac=list(core)
    ok=True
    for i,p in enumerate(pool):
        if mask>>i&1:
            # check antichain: p not superset/subset of existing
            if any((p&c)==p or (c&p)==c for c in ac):
                ok=False; break
            ac.append(p)
    if not ok: continue
    eta=swings_antichain(ac,n)
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        found+=1
        if found<=6:
            extra=[sorted(j+1 for j in range(n) if (p>>j)&1) for i,p in enumerate(pool) if mask>>i&1]
            print(f"  extra tail: {extra}  swings: {eta} gcd:{g}")
print(f"total with this core: {found} in {time.time()-t0:.1f}s")
