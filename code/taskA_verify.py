"""Task A: construct explicit graphs for the new families and verify swings via formula + brute force."""
import networkx as nx
from math import gcd
from functools import reduce

def swings_formula(G, n):
    E = G.number_of_edges()
    deg = dict(G.degree())
    return [E + (n-1) - 2*deg[i] for i in range(n)]

def swings_brute(edge_list, n):
    ac=[(1<<n)-1 & ~((1<<a)|(1<<b)) for a,b in edge_list]
    def win(m): return any((m&c)==c for c in ac)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(1<<n):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

def build_and_check(n, d):
    num = d*(2*n-8) + 4*(n-1)
    if num%7!=0: return None
    c = num//7
    ds = d + c//2
    seq = [d]*(n-1) + [ds]
    if not nx.is_graphical(seq): return None
    G = nx.havel_hakimi_graph(seq)
    eta = swings_formula(G, n)
    g = reduce(gcd, eta)
    ok = sorted(e//g for e in eta) == sorted([1]+[2]*(n-1))
    return (G, c, eta, ok)

print("=== Verify new families (formula) ===")
print("n≡2 (mod 7), d=1:")
for n in (9, 16, 23, 37, 100):
    r = build_and_check(n, 1)
    if r:
        G, c, eta, ok = r
        print(f"  n={n}: c={c} swings_ok={ok}")
print("n≡3 (mod 7), d=4:")
for n in (17, 24, 31, 45, 94):
    r = build_and_check(n, 4)
    if r:
        G, c, eta, ok = r
        print(f"  n={n}: c={c} swings_ok={ok}")

print("\n=== Brute-force verify small new-family examples ===")
for n, d in [(16,1),(17,4),(23,1),(24,4)]:
    num = d*(2*n-8)+4*(n-1); c=num//7
    seq = [d]*(n-1)+[d+c//2]
    G = nx.havel_hakimi_graph(seq)
    edge_list = [(u,v) for u,v in G.edges()]
    eta_b = swings_brute(edge_list, n)
    g = reduce(gcd, eta_b)
    print(f"  n={n} d={d}: brute swings {eta_b} -> OK={sorted(e//g for e in eta_b)==sorted([1]+[2]*(n-1))}")
