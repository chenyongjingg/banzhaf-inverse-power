"""Test structured complement-of-triples H candidates for n=8."""
from itertools import combinations
from math import gcd
from functools import reduce

def swings_comp(H, n):
    # winning = complements of H
    win=[((1<<n)-1)&~x for x in H]
    acm=set()
    for m in win:
        if not any((m&w)==m and w!=m for w in win): acm.add(m)  # minimal
    def winf(mm): return any((mm&c)==c for c in acm)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for mm in range(1<<n):
            if mm&bit: continue
            if (not winf(mm)) and winf(mm|bit): eta[i]+=1
    return eta

n=8
def S(*xs): return sum(1<<(x-1) for x in xs)
triples=[S(a,b,c) for a in range(1,n+1) for b in range(a+1,n+1) for c in range(b+1,n+1)]
target=sorted([1]+[2]*(n-1))

def report(name, H):
    eta=swings_comp(H,n)
    if any(e==0 for e in eta): 
        print(f"{name}: has null players"); return
    g=reduce(gcd,eta)
    ok = sorted(e//g for e in eta)==target
    print(f"{name}: swings={eta} gcd={g} {'OK' if ok else ''}")

report("all triples", triples)
report("triples containing 8", [t for t in triples if t & (1<<7)])
report("triples NOT containing 8", [t for t in triples if not (t & (1<<7))])
# H = all triples containing at least 2 of {1,2}
report("triples containing {1,2}", [t for t in triples if (t&3)==3])
# H = triples of form {8,a,b}
report("triples {8,a,b} all", [S(8,a,b) for a in range(1,8) for b in range(a+1,8)])
