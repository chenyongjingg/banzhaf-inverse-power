"""Reproduce all closed-form constructions for the paper. Outputs a results table."""
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

def build(n, edges):
    win=[sorted(set(range(1,n+1))-set(e)) for e in edges]
    return swings(win, n)

results = []
# n=6: C4(1-2-6-3-1) U K3(4,5,6)
results.append((6, [(1,2),(1,3),(2,6),(3,6),(4,5),(4,6),(5,6)], "C4 U K3"))
# n=7: C6 on 1..6 + star7
results.append((7, [(i,i+1) for i in range(1,6)]+[(6,1)]+[(i,7) for i in range(1,7)], "C6 + star7"))
# n=9: star9(1-4) + matching{5,6},{7,8}
results.append((9, [(i,9) for i in range(1,5)]+[(5,6),(7,8)], "star9 + matching"))
# n=13: star13(1-8) + matching + C4(9-12)
results.append((13, [(i,13) for i in range(1,9)]+[(1,2),(3,4),(5,6),(7,8)]+[(9,10),(10,11),(11,12),(12,9)], "star13+matching+C4"))
# n=14: C13 + chord{6,10} + star14(excl 6,10)
results.append((14, [(i,i+1) for i in range(1,13)]+[(13,1)]+[(6,10)]+[(i,14) for i in [1,2,3,4,5,7,8,9,11,12,13]], "C13+chord+star14"))
# n=16: star16(1-7) + matching
results.append((16, [(i,16) for i in range(1,8)]+[(8,9),(10,11),(12,13),(14,15)], "star16+matching"))
# n=17: star17(all) + C16 + matching(i,i+8)
results.append((17, [(i,17) for i in range(1,17)]+[(i,i+1) for i in range(1,16)]+[(16,1)]+[(i,i+8) for i in range(1,9)], "star17+C16+matching"))

print(f"{'n':>3} {'c':>3} {'swings':<55} OK")
print("-"*90)
for n, edges, name in results:
    eta = build(n, edges)
    g = reduce(gcd, eta)
    c = g
    ok = sorted(e//g for e in eta) == sorted([1]+[2]*(n-1))
    assert ok, f"FAIL n={n}"
    print(f"{n:>3} {c:>3} {str(eta):<55} OK ({name})")
print("ALL CLOSED-FORM CONSTRUCTIONS VERIFIED.")
