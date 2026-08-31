"""Verify n=9 construction: star at 9 (edges to 1-4) + matching {5,6},{7,8}.
Game: winning (n-2)=7-sets = complements of edges."""
from math import gcd
from functools import reduce

def swings_antichain(ac_sets, n):
    ac=[sum(1<<(x-1) for x in c) for c in ac_sets]
    def win(m): return any((m&c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

n=9
edges=[(1,9),(2,9),(3,9),(4,9),(5,6),(7,8)]
win=[]
for a,b in edges:
    win.append(sorted(set(range(1,n+1))-{a,b}))
eta=swings_antichain(win,n)
g=reduce(gcd,eta)
print("edges:", edges)
print("swings:", eta, "total:", sum(eta))
print("gcd:", g, "normalized:", sorted(e//g for e in eta))
print("target (2,..,2,1):", sorted([1]+[2]*(n-1)))
print("OK!" if sorted(e//g for e in eta)==sorted([1]+[2]*(n-1)) else "FAIL")
