from math import gcd
from functools import reduce

def swings_antichain(ac_sets, n):
    ac=[sum(1<<(x-1) for x in c) for c in ac_sets]
    def win(m): return any((m&c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

def build(n, edges, name):
    win=[sorted(set(range(1,n+1))-set(e)) for e in edges]
    eta=swings_antichain(win,n)
    g=reduce(gcd,eta)
    ok = sorted(e//g for e in eta)==sorted([1]+[2]*(n-1))
    print(f"n={n} {name}: edges={len(edges)} swings={eta} gcd={g} -> {'OK' if ok else 'FAIL'}")

# n=14: C13 + chord{6,10} + star 14->{1,2,3,4,5,7,8,9,11,12,13}
E14=[(i,i+1) for i in range(1,13)] + [(13,1)] + [(6,10)] + [(i,14) for i in [1,2,3,4,5,7,8,9,11,12,13]]
build(14,E14,"C13+chord+star")

# n=16: star 16->{1..7} + matching {8,9},{10,11},{12,13},{14,15}
E16=[(i,16) for i in range(1,8)] + [(8,9),(10,11),(12,13),(14,15)]
build(16,E16,"star7+matching4")

# n=17: star 17->all 16 + C16 + perfect matching {i,i+8}
E17=[(i,17) for i in range(1,17)] + [(i,i+1) for i in range(1,16)] + [(16,1)] + [(i,i+8) for i in range(1,9)]
build(17,E17,"star16+C16+matching")
