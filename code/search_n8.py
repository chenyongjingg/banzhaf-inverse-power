"""Search n=8 solutions via 'complement antichain' family: winning = complements of an antichain H
of 2-sets and 3-sets. Structured random + targeted."""
import random, time
from math import gcd
from functools import reduce

n=8
NB=1<<n; FULL=(1<<NB)-1
# precompute
def swings_from_complements(H):
    # winning coalitions = N \ X for X in H, antichain H assumed
    win_sets=[]
    for X in H:
        m = ((1<<n)-1) & ~X
        win_sets.append(m)
    def win(m): return any((m&c)==c for c in win_sets)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(NB):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

pairs=[(1<<a)|(1<<b) for a in range(n) for b in range(a+1,n)]
triples=[(1<<a)|(1<<b)|(1<<c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
quads=[(1<<a)|(1<<b)|(1<<c)|(1<<d) for a in range(n) for b in range(a+1,n) for c in range(b+1,n) for d in range(c+1,n)]
target=tuple([1]+[2]*(n-1))
random.seed(42)
t0=time.time()
trials=600000
for it in range(trials):
    # build antichain H: random triples, then random pairs avoiding triples, then maybe quads
    H=[]
    # random subset of triples
    for tr in random.sample(triples, random.randint(0,3)):
        H.append(tr)
    # pairs not contained in any triple of H
    covered=set()
    for tr in H:
        # submasks of tr of size 2
        for a in range(n):
            for b in range(a+1,n):
                p=(1<<a)|(1<<b)
                if (p & ~tr)==0: covered.add(p)
    avail_pairs=[p for p in pairs if p not in covered]
    # random subset of pairs
    for p in random.sample(avail_pairs, min(len(avail_pairs), random.randint(0,5))):
        H.append(p)
    # random quads that don't contain/are contained... just add 0-2 quads, ensure antichain
    H2=[]
    for h in H:
        if not any((h & h2)==h2 and h!=h2 for h2 in H):
            H2.append(h)
    # also add a quad if it doesn't contain/contained in existing
    for q in random.sample(quads, random.randint(0,1)):
        if not any((q & h2)==h2 or (h2 & q)==q for h2 in H2):
            H2.append(q)
    if not H2: continue
    eta=swings_from_complements(H2)
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        print(f"FOUND at {it} in {time.time()-t0:.1f}s")
        comps=sorted(sorted(j+1 for j in range(n) if (x>>j)&1) for x in H2)
        print("  complement-antichain:", comps)
        print("  winning sets:", sorted(sorted(j+1 for j in range(n) if (((1<<n)-1)&~x)>>j&1) for x in H2))
        print("  swings:", eta, "gcd:", g)
        break
else:
    print(f"none in {trials} trials, {time.time()-t0:.1f}s")
