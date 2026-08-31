"""Task A verify: formula-based for all n (checking Thm1 conditions), brute-force bit-trick for small n."""
import networkx as nx
from math import gcd
from functools import reduce

def swings_formula(G, n):
    E = G.number_of_edges()
    deg = dict(G.degree())
    return [E + (n-1) - 2*deg[i] for i in range(n)]

def brute_swings_bit(edge_list, n):
    NB=1<<n; FULL=(1<<NB)-1
    # build winning = complements of edges, minimal antichain
    win_masks=set()
    for a,b in edge_list:
        comp = ((1<<n)-1) & ~((1<<a)|(1<<b))
        win_masks.add(comp)
    # swings via bit trick on WIN integer
    # build WIN (bit m set iff coalition m winning = superset of some comp)
    # Actually simpler: count directly (small n)
    def win(m): return any((m&c)==c for c in win_masks)
    eta=[0]*n
    for i in range(n):
        bit=1<<i
        for m in range(NB):
            if m&bit: continue
            if (not win(m)) and win(m|bit): eta[i]+=1
    return eta

def build(n, d):
    num = d*(2*n-8) + 4*(n-1)
    if num%7!=0: return None
    c = num//7
    ds = d + c//2
    seq = [d]*(n-1) + [ds]
    if not nx.is_graphical(seq): return None
    G = nx.havel_hakimi_graph(seq)
    degs = sorted(dict(G.degree()).values())
    no_iso = (degs[0] >= 1)
    # not a star: no vertex covers all edges
    edges = set(G.edges())
    not_star = not any(all(e[0]==v or e[1]==v for e in edges) for v in range(n))
    eta = swings_formula(G, n)
    g = reduce(gcd, eta)
    ok = sorted(e//g for e in eta) == sorted([1]+[2]*(n-1))
    return (G, c, ds, no_iso, not_star, ok)

print("=== formula-based check for new families (with Thm1 conditions) ===")
fam = {'n≡2 mod7 d=1': [(9,1),(16,1),(23,1),(30,1),(37,1),(44,1),(58,1),(72,1),(100,1)],
       'n≡3 mod7 d=4': [(17,4),(24,4),(31,4),(38,4),(52,4),(66,4),(94,4)],
       'n≡0 mod7 d=3': [(7,3),(14,3),(21,3),(35,3),(56,3),(98,3)],
       'n≡6 mod7 d=2': [(6,2),(13,2),(20,2),(34,2),(48,2),(90,2)]}
for name, items in fam.items():
    print(f"{name}:")
    allok=True
    for n,d in items:
        r = build(n,d)
        if r is None:
            print(f"  n={n}: NO GRAPHICAL"); allok=False; continue
        G,c,ds,no_iso,not_star,ok = r
        if not (no_iso and not_star and ok): allok=False
        print(f"  n={n}: c={c} deg_special={ds} Thm1conds(noIso={no_iso},notStar={not_star}) formula_ok={ok}")
    print(f"  -> all OK: {allok}")

print("\n=== brute-force cross-check (bit, n<=14) ===")
for n,d in [(9,1),(13,2),(14,3),(17,4)]:
    r=build(n,d)
    if r is None: continue
    G,c,_,_,_,_ = r
    el=[(u,v) for u,v in G.edges()]
    eta_f = swings_formula(G,n)
    eta_b = brute_swings_bit(el, n)
    print(f"  n={n} d={d}: formula={eta_f} brute={eta_b} match={eta_f==eta_b}")
