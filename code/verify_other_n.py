"""Verify complement-of-edge constructions for n=13,14,16,17."""
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

def build(n, edges):
    win=[sorted(set(range(1,n+1))-set(e)) for e in edges]
    eta=swings_antichain(win,n)
    g=reduce(gcd,eta)
    ok = sorted(e//g for e in eta)==sorted([1]+[2]*(n-1))
    print(f"n={n}: edges={len(edges)} swings={eta} gcd={g} -> {'OK' if ok else 'FAIL'}")
    return ok

# n=13: special=13 deg 8, non-special deg 2
E13=[(i,13) for i in range(1,9)] + [(1,2),(3,4),(5,6),(7,8)] + [(9,10),(10,11),(11,12),(12,9)]
build(13,E13)

# n=14: d=3, c=16, special deg 11, |E|=25. 13 non-special deg 3, special deg 11.
# 11 star edges special->{1..11}. remaining non-special {1..11} need 2 more, {12,13} need 3.
# total extra needed: 11*2 + 2*3 = 22+6=28?? but |E|=25, star=11, extra=14. check: 28/2=14 ✓
# Construct: 
E14=[(i,14) for i in range(1,12)]
# {1..11} need 2 more edges each, {12,13} need 3 each -> total extra edges = (11*2+2*3)/2 = 14
# use C11 on {1..11}? that gives 2 each for {1..11} (11 edges) + 3 each for {12,13}: {12,13} connect to 3 of {1..11} each -> but that adds degree to {1..11} too. Let me instead:
# {12,13} each degree 3: edges {12,13},{12,x},{13,y} -> {12,13} share edge, x,y in {1..11}. That gives x,y +1. 
# Let me do: C11 on {1..11}: edges (i,i+1) for i in 1..10, (11,1): 11 edges. Now {1..11} have degree 2 (from cycle) + 1 (star) = 3 ✓. {12,13}: need degree 3, 0 so far. Add edges {12,13},{12,a},{13,b} where a,b ∈ {1..11} and a≠b. That adds +1 to a and b. So a,b go to 4. Bad.
# Instead: make {12,13} degree 3 via edges to each other and 2 more: {12,13},{12,a},{12,b}? then 12 has 3, 13 has 1. 
# Let me be systematic: total extra edges 14. {1..11} currently degree 1 (star) + need to reach 3: need 2 each = 22 incidences. {12,13} need 3 each = 6. Total 28 incidences /2 = 14 edges ✓.
# C11 on {1..11} uses 11 edges, 22 incidences on {1..11} ✓ reaches degree 3 (1 star + 2 cycle). 
# Remaining: {12,13} need 6 incidences = 3 edges. But only 3 edges among {12,13,?}: {12,13},{12,?},{13,?} would touch others. 
# Use: {12,13},{12,13} no. Trio: {12,13} plus both connect to vertex 1: {12,1},{13,1}: edges {12,13},{12,1},{13,1}. Degrees: 12:2,13:2, 1:+2 (now 1 has 3+2=5). Bad.
# Alternative: {12,13} connect to each other and each to a distinct: {12,13},{12,1},{13,2}: 12:2,13:2,1:+1,2:+1. 12,13 need 1 more each. Add {12,13}? already have. Hmm.
# Let me just construct via degree sequence and verify.
print()
