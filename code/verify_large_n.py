from math import gcd
from functools import reduce
import time

def make_tables(n):
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
    return SUP,MaskZ,MaskO,twoi,FULLMASK

def swings_fast(ac, SUP,MaskZ,MaskO,twoi,FULLMASK,n):
    WIN=0
    for c in ac: WIN|=SUP[c]
    NOTWIN=(~WIN)&FULLMASK
    return [bin(MaskZ[i]&NOTWIN&((MaskO[i]&WIN)>>twoi[i])).count("1") for i in range(n)]

# n=20 (6 mod 7): d=2, special deg 12
n=20
E20=[(i,20) for i in range(1,13)]+[(1,2),(3,4),(5,6),(7,8),(9,10),(11,12)]+[(13,14),(14,15),(15,16),(16,17),(17,18),(18,19),(19,13)]
SUP,MaskZ,MaskO,twoi,FULLMASK=make_tables(n)
ac=[((1<<n)-1)&~(1<<(a-1))&~(1<<(b-1)) for a,b in E20]
t0=time.time()
eta=swings_fast(ac,SUP,MaskZ,MaskO,twoi,FULLMASK,n)
g=reduce(gcd,eta)
print(f"n=20: swings={eta} gcd={g} OK={sorted(e//g for e in eta)==sorted([1]+[2]*19)} ({time.time()-t0:.1f}s)")

# n=21 (0 mod 7): d=3, special deg 16
n=21
E21=[(i,21) for i in range(1,17)]+[(i,i+1) for i in range(1,16)]+[(16,1)]+[(i,i+8) for i in range(1,9)]+[(17,18),(18,19),(19,20),(20,21),(21,17)]
SUP,MaskZ,MaskO,twoi,FULLMASK=make_tables(n)
ac=[((1<<n)-1)&~(1<<(a-1))&~(1<<(b-1)) for a,b in E21]
t0=time.time()
eta=swings_fast(ac,SUP,MaskZ,MaskO,twoi,FULLMASK,n)
g=reduce(gcd,eta)
print(f"n=21: swings={eta} gcd={g} OK={sorted(e//g for e in eta)==sorted([1]+[2]*20)} ({time.time()-t0:.1f}s)")
