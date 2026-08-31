"""Verify the swing formula for the threshold+exceptions family:
v(S)=1 iff |S|>=n-1, OR (|S|=n-2 and N\S notin E), OR (|S|=n-3 and N\S in F).
Claimed: eta_i = C(n-1,2) + |F| - 2*r_i + e_i,  e_i = #{X in F: i in X, X\{i} in E}."""
import random
from itertools import combinations
from math import gcd
from functools import reduce

def swings_brute(E, F, n):
    Emasks=[(1<<a)|(1<<b) for a,b in E]
    Fmasks=[(1<<a)|(1<<b)|(1<<c) for a,b,c in F]
    def win(S):
        s=bin(S).count('1')
        if s>=n-1: return True
        comp=((1<<n)-1)&~S
        if s==n-2: return (comp not in Emasks)
        if s==n-3: return (comp in Fmasks)
        return False
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for S in range(1<<n):
            if S&bit: continue
            if (not win(S)) and win(S|bit): eta[i]+=1
    return eta

def formula(E, F, n):
    Fsets=[set(f) for f in F]
    C= (n-1)*(n-2)//2
    f=len(F)
    eta=[]
    for i in range(n):
        r=sum(1 for X in Fsets if i in X)
        e=sum(1 for X in Fsets if i in X and tuple(sorted(X-{i})) in [tuple(sorted(e2)) for e2 in E])
        eta.append(C + f - 2*r + e)
    return eta

random.seed(1)
for n in (8,10,12):
    for trial in range(5):
        Es=[(a,b) for a in range(n) for b in range(a+1,n)]
        Fs=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
        E=random.sample(Es, random.randint(0,len(Es)))
        F=random.sample(Fs, random.randint(0,min(10,len(Fs))))
        b=swings_brute(E,F,n); fml=formula(E,F,n)
        assert b==fml, (n,E,F,b,fml)
print("FORMULA VERIFIED on random (E,F) for n=8,10,12")
