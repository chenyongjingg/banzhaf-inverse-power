"""n=8 search seeded with n=7 structure (C6+star7), varying player 8's connections."""
import time
from itertools import combinations
from math import gcd
from functools import reduce

n=8
NB=1<<n; FULL=(1<<NB)-1
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

def swings(win_sets):
    WIN=0
    for c in win_sets: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULL
    return [bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]

def S(*xs): return sum(1<<(x-1) for x in xs)
# C6 edges on {1..6} + star7 to all + star8 to S
C6=[S(1,2),S(2,3),S(3,4),S(4,5),S(5,6),S(6,1)]
star7=[S(i,7) for i in range(1,7)]
target=tuple([1]+[2]*(n-1))
t0=time.time()
for mask in range(128):  # star8 subset S of {1..7}
    star8=[S(8,i+1) for i in range(7) if mask>>i&1]
    # winning = complements of all edges
    edges=C6+star7+star8
    win=[((1<<n)-1)&~e for e in edges]
    eta=swings(win)
    if any(e==0 for e in eta): continue
    g=reduce(gcd,eta)
    if tuple(sorted(e//g for e in eta))==target:
        print(f"FOUND star8 mask={mask}: swings={eta}")
print(f"C6+star7+star8 variants done in {time.time()-t0:.1f}s")

# also try: winning = complements of edges + complements of triples (mixed)
# vary one triple added
triples=[S(a,b,c) for a in range(1,n+1) for b in range(a+1,n+1) for c in range(b+1,n+1)]
t0=time.time()
found=0
for mask in range(128):
    star8=[S(8,i+1) for i in range(7) if mask>>i&1]
    edges=C6+star7+star8
    # add up to 2 triples
    for t1 in range(len(triples)):
        H=set(edges)|{triples[t1]}
        # antichain: triple must not contain edge? triple doesn't contain 2-edge; edge{...} subset of triple possible
        if any((triples[t1]&e)==e for e in edges): continue
        win=[((1<<n)-1)&~x for x in H]
        eta=swings(win)
        if any(e==0 for e in eta): continue
        g=reduce(gcd,eta)
        if tuple(sorted(e//g for e in eta))==target:
            found+=1
            print(f"FOUND mask={mask} triple={sorted(j+1 for j in range(n) if triples[t1]>>j&1)}: swings={eta}")
            if found>3: break
    if found>3: break
print(f"mixed (edge+triple) done in {time.time()-t0:.1f}s found={found}")
