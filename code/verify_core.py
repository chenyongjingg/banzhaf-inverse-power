"""Rigorous independent verification of the core theorems:
A) Theorem 1 (complement-of-edge), B) Proposition 8 formula (U), C) special cases."""
import random
from math import gcd
from functools import reduce

def swings_brute(G, F, n):
    """Direct swing count of v(G,F): |S|>=n-1, or (|S|=n-2, comp in G), or (|S|=n-3, comp in F)."""
    Gmask=[(1<<a)|(1<<b) for a,b in G]
    Fmask=[(1<<a)|(1<<b)|(1<<c) for a,b,c in F]
    def win(S):
        s=bin(S).count('1'); comp=((1<<n)-1)&~S
        if s>=n-1: return True
        if s==n-2: return comp in Gmask
        if s==n-3: return comp in Fmask
        return False
    return [sum(1 for S in range(1<<n) if not (S&(1<<i)) and (not win(S)) and win(S|(1<<i))) for i in range(n)]

def formulaU(G, F, n):
    Gset=set(tuple(sorted(e)) for e in G)
    deg=[0]*n
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(n):
        r=sum(1 for X in F if i in X)
        e=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*r+e)
    return eta

def mono(G,F):
    Gset=set(tuple(sorted(e)) for e in G)
    return all(tuple(sorted((X[a],X[b]))) in Gset for X in F for a in range(3) for b in range(a+1,3))

random.seed(2024)
trials=0; mism=0
for n in range(5,15):
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    tris=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    for t in range(25):
        # random monotone (G,F)
        G=random.sample(pairs, random.randint(0,len(pairs)))
        F=random.sample(tris, random.randint(0,min(8,len(tris))))
        if not mono(G,F): continue
        b=swings_brute(G,F,n); u=formulaU(G,F,n)
        trials+=1
        if b!=u:
            mism+=1
            if mism<=3: print(f"MISMATCH n={n} G={G} F={F}\n  brute={b}\n  U={u}")
print(f"Formula (U) verification: {trials} monotone random instances, {mism} mismatches")

# Special case A: F=empty -> Theorem 1 (complement-of-edge)
mism=0; tr=0
for n in range(4,13):
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    for t in range(30):
        G=random.sample(pairs, random.randint(1,len(pairs)))
        # ensure no isolated, not star (Thm1 conditions)
        deg=[0]*n
        for a,b in G: deg[a]+=1; deg[b]+=1
        if 0 in deg: continue
        if any(deg[v]==n-1 and len(G)==n-1 for v in range(n)): continue
        b=swings_brute(G,[],n); u=formulaU(G,[],n)
        tr+=1
        if b!=u:
            mism+=1
            print(f"A MISMATCH n={n} G={G}: brute={b} U={u}")
print(f"Theorem 1 (F=empty) check: {tr} instances, {mism} mismatches")

# Special case B: G = complement(E) -> Theorem 3 (threshold)
mism=0; tr=0
for n in range(5,12):
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    for t in range(20):
        E=random.sample(pairs, random.randint(0,len(pairs)))
        G=[e for e in pairs if e not in E]
        F=random.sample([(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)], random.randint(0,5))
        if not mono(G,F): continue
        b=swings_brute(G,F,n); u=formulaU(G,F,n)
        tr+=1
        if b!=u:
            mism+=1; print(f"B MISMATCH n={n}")
print(f"Theorem 3 (G=complement) check: {tr} instances, {mism} mismatches")
