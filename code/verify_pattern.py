"""Verify conjectured general construction: winning (n-2)-sets = complements of edges of G_n.
G_6 = C4(1-2-6-3-1) U K3(4-5-6);  G_n (n>=7) = C_{n-1} on {1..n-1} U star at n."""
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

def edges_to_winning_sets(edges, n):
    """winning (n-2)-sets = complements of edges"""
    win=[]
    for a,b in edges:
        S=set(range(1,n+1))-{a,b}
        win.append(sorted(S))
    return win

cases = {}
# n=6
cases[6] = [(1,2),(1,3),(2,6),(3,6),(4,5),(4,6),(5,6)]  # C4 U K3
# n=7: C6 on 1..6 + star at 7
E7=[(1,2),(2,3),(3,4),(4,5),(5,6),(6,1)]+[(i,7) for i in range(1,7)]
cases[7]=E7
# n=8: C7 on 1..7 + star at 8
E8=[(i,i+1) for i in range(1,7)]+[(7,1)]+[(i,8) for i in range(1,8)]
cases[8]=E8
# n=9,10
for n in (9,10):
    E=[(i,i+1) for i in range(1,n-1)]+[(n-1,1)]+[(i,n) for i in range(1,n)]
    cases[n]=E

for n in (6,7,8,9,10):
    win=edges_to_winning_sets(cases[n], n)
    eta=swings_antichain(win, n)
    g=reduce(gcd,eta)
    norm=sorted(e//g for e in eta)
    print(f"n={n}: edges={len(cases[n])} antichain={len(win)} swings={eta} gcd={g} target={sorted([1]+[2]*(n-1))} -> {'OK' if norm==sorted([1]+[2]*(n-1)) else 'FAIL'}")
