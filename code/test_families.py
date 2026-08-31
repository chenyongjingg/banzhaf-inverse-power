import sys
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

def report(name, ac, n):
    eta=swings(ac,n)
    g=reduce(gcd,eta)
    norm=sorted(e//g for e in eta)
    target=sorted([1]+[2]*(n-1))
    ok = (norm==target)
    print(f"{name}: swings={eta} total={sum(eta)} gcd={g} -> {'SOLUTION!' if ok else 'no'}")
    return eta

n=7
# variants
report("V1 (all pairs 3-5 to 6,7 + 67)", [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4,5],[3,6],[4,6],[5,6],[3,7],[4,7],[5,7],[6,7]], n)
report("V2 (pairs 3-5 to 6,7 no 67)", [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4,5],[3,6],[4,6],[5,6],[3,7],[4,7],[5,7]], n)
report("V3 (tail chain 3-5 to 6, then 67+37,47)", [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4,5],[3,6],[4,6],[5,6],[3,7],[4,7],[6,7]], n)
report("V4 (add 7 as 456? no, 367)", [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4,5],[3,6],[4,6],[5,6],[3,6,7],[4,7],[5,7]], n)
