"""Task D: necessary conditions. Analyze the 360 n=6 solutions for common structural features."""
import time
from math import gcd
from functools import reduce

n=6
NB=1<<n; FULLMASK=(1<<NB)-1
SUP=[0]*NB
for c in range(NB):
    rem=(~c)&(NB-1); sub=rem; s=0
    while True:
        s|=1<<(c|sub)
        if sub==0: break
        sub=(sub-1)&rem
    SUP[c]=s
MaskZ=[0]*n; MaskO=[0]*n; twoi=[1<<i for i in range(n)]
for i in range(n):
    z=o=0
    for m in range(NB):
        if (m>>i)&1: o|=1<<m
        else: z|=1<<m
    MaskZ[i]=z; MaskO[i]=o
def swings_fast(ac):
    WIN=0
    for c in ac: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULLMASK
    return [bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]
def antichains(n):
    masks=list(range(NB)); results=[]
    def rec(chosen,start):
        results.append(tuple(chosen))
        for idx in range(start,len(masks)):
            m=masks[idx]; ok=True
            for c in chosen:
                if (c&m)==c: ok=False; break
            if ok: chosen.append(m); rec(chosen,idx+1); chosen.pop()
    rec([],0); return results

target=tuple([1]+[2]*(n-1))
sols=[]
for ac in antichains(n):
    if not ac or 0 in ac: continue
    eta=swings_fast(ac)
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        sols.append(ac)
print(f"n=6: {len(sols)} solutions")

from collections import Counter
# Feature 1: minimal winning coalition sizes
print("\nMinimal winning coalition size multisets:")
print(Counter(tuple(sorted(bin(c).count('1') for c in ac)) for ac in sols))

# Feature 2: proper / strong / decisive
def is_proper(ac):
    for c in ac:
        comp=((1<<n)-1)&~c
        if any((comp&d)==d for d in ac): return False
    return True
def is_strong(ac):
    for m in range(1<<n):
        comp=((1<<n)-1)&~m
        wm = any((m&d)==d for d in ac)
        wc = any((comp&d)==d for d in ac)
        if not wm and not wc: return False
    return True
proper = sum(1 for ac in sols if is_proper(ac))
strong = sum(1 for ac in sols if is_strong(ac))
decisive = sum(1 for ac in sols if is_proper(ac) and is_strong(ac))
print(f"\nproper: {proper}, strong: {strong}, decisive: {decisive}")

# Feature 3: winning coalitions by size (histogram)
print("\nWinning-coalition size histograms (top patterns):")
hists=Counter()
for ac in sols:
    win=set()
    for c in ac:
        rem=(~c)&((1<<n)-1); sub=rem
        while True:
            win.add(c|sub)
            if sub==0: break
            sub=(sub-1)&rem
    h=tuple(len([m for m in win if bin(m).count('1')==k]) for k in range(n+1))
    hists[h]+=1
for h,cnt in hists.most_common(5):
    print(f"  {h}  count={cnt}")
