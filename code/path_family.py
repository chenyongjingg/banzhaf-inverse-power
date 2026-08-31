from math import gcd
from functools import reduce
def swings(ac_sets, n):
    ac=[sum(1<<(x-1) for x in c) for c in ac_sets]
    def win(m): return any((m&c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta
def report(n, extra):
    ac=[[1,2],[1,3],[1,4],[2,3],[2,4],[3,4,5]]+extra
    eta=swings(ac,n)
    g=reduce(gcd,eta)
    ok = sorted(e//g for e in eta)==sorted([1]+[2]*(n-1))
    print(f"n={n} extra={extra}: swings={eta} gcd={g} {'OK' if ok else ''}")
# pure path
for n in (6,7,8):
    extra=[[i,i+1] for i in range(5,n)]
    report(n, extra)
# path + {3,6},{4,6}
for n in (6,7,8):
    extra=[[3,6],[4,6]]+[[i,i+1] for i in range(5,n)]
    report(n, extra)
# path + {3,j},{4,j} for j=6..n
for n in (7,8):
    extra=[[3,j],[4,j] for j in range(6,n+1)]+[[i,i+1] for i in range(5,n)]
    report(n, extra)
