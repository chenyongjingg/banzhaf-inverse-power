"""From n=8 MILP solution, reconstruct the threshold-family (E,F)."""
n=8
# minimal winning coalitions from MILP (0-indexed)
mw=[[0,1,2,4,5],[0,1,2,3,6],[0,2,3,4,5,6],[1,2,3,4,5,6],[0,1,3,4,5,7],
    [1,2,3,4,6,7],[0,2,3,5,6,7],[0,1,4,5,6,7],[0,3,4,5,6,7],[1,3,4,5,6,7],[2,3,4,5,6,7]]
def mkset(c): return set(c)
# full winning set = upward closure
full=set()
for c in mw:
    c=set(c)
    # all supersets
    for m in range(1<<n):
        S=set(j for j in range(n) if (m>>j)&1)
        if c<=S: full.add(frozenset(S))
# histogram
from collections import Counter
sizes=Counter(len(s) for s in full)
print('winning sizes:', dict(sizes))
# threshold structure: all |S|>=n-1 winning? check 7,8
sevens=[s for s in full if len(s)==7]
print('7-sets winning:', len(sevens), 'of', 8)
# losing 6-sets -> E
losing6=[frozenset(j for j in range(n) if not (m>>j)&1) for m in range(1<<n) if bin(m).count('1')==6]
E=set()
for L in losing6:
    if frozenset(L) not in full:
        comp=frozenset(j for j in range(n) if j not in L)
        E.add(tuple(sorted(comp)))
print('E edges (losing 6-sets):', sorted(E), len(E))
# winning 5-sets -> F
win5=[s for s in full if len(s)==5]
F=[tuple(sorted(set(range(n))-s)) for s in win5]
print('F triples (winning 5-sets comps):', sorted(F), len(F))
# monotonicity check E ∩ Pairs(F)
Pairs=set()
for X in F:
    for i in range(3):
        for j in range(i+1,3):
            Pairs.add(tuple(sorted((X[i],X[j]))))
print('E ∩ Pairs(F):', set(E)&Pairs)
