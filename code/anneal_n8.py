"""Simulated annealing for n=8: find antichain with swings proportional to (2,...,2,1)."""
import random, time, math
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

def swings(ac):
    WIN=0
    for c in ac: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULL
    return [bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]

def antichain_ok(ac):
    ac=sorted(set(ac))
    for i in range(len(ac)):
        for j in range(len(ac)):
            if i!=j and (ac[i]&ac[j])==ac[j]:  # ac[j] subset of ac[i]
                return False
    return True

# target swings for scale c
def loss(eta, c):
    target=[2*c]*(n-1)+[c]
    return sum(abs(eta[i]-target[i]) for i in range(n))

random.seed(2024)
pool=[c for c in range(1,NB-1) if 2<=bin(c).count('1')<=6]
best=None; bestloss=10**9
t0=time.time()
for restart in range(60):
    # random start antichain
    ac=[]
    for m in random.sample(pool, random.randint(4,9)):
        if not any((c&m)==m and c!=m for c in ac): ac.append(m)
    if not ac: continue
    c0=2  # try small scale
    # estimate best c: total swings
    T=10**9
    for it in range(4000):
        T = 5.0 * (1 - it/4000) + 0.01
        eta=swings(ac)
        # pick c nearest ratio
        total=sum(eta)
        # target total = c(2n-1) = 15c
        c=max(1, round(total/15))
        L=loss(eta,c)
        if L<bestloss:
            bestloss=L; best=list(ac)
            if L==0:
                print(f"SOLUTION! restart={restart} iter={it} time={time.time()-t0:.0f}s")
                print("  antichain:", sorted(sorted(j+1 for j in range(n) if (x>>j)&1) for x in ac))
                print("  swings:", eta, "c:", c)
                raise SystemExit
        # mutate
        ac2=list(ac)
        op=random.random()
        if op<0.4 and len(ac2)<12:
            ac2.append(random.choice(pool))
        elif op<0.8 and ac2:
            ac2.pop(random.randrange(len(ac2)))
        else:
            ac2[random.randrange(len(ac2))]=random.choice(pool)
        ac2=sorted(set(ac2))
        # keep antichain (minimal elements)
        ac2=[m for m in ac2 if not any((x&m)==m and x!=m for x in ac2)]
        if not ac2: continue
        eta2=swings(ac2)
        total2=sum(eta2)
        c2=max(1, round(total2/15))
        L2=loss(eta2,c2)
        if L2<=L or random.random() < math.exp((L-L2)/T):
            ac=ac2
print(f"annealing done. best loss={bestloss} in {time.time()-t0:.0f}s")
if best:
    print("best antichain:", sorted(sorted(j+1 for j in range(n) if (x>>j)&1) for x in best))
    print("best swings:", swings(best))
