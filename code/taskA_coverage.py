"""Task A: maximize complement-of-edge coverage. For each n, solve 7c=d(2n-8)+4(n-1),
check degree sequence (d x (n-1), d+c/2) is graphical via Erdős-Gallai, construct via Havel-Hakimi."""
import networkx as nx
from math import gcd
from functools import reduce

def solve(n):
    sols = []
    for d in range(1, n):  # non-special degree, >=1 (no isolated)
        num = d*(2*n-8) + 4*(n-1)
        if num <= 0 or num % 7 != 0:
            continue
        c = num // 7
        if c < 1 or c % 2 != 0:   # c positive even (deg_special = d + c/2 integer)
            continue
        ds = d + c//2
        if ds > n-1:
            continue
        if (n*d + c//2) % 2 != 0:  # |E| = (nd + c/2)/2 integer
            continue
        # degree sequence: n-1 copies of d, one of ds
        seq = [d]*(n-1) + [ds]
        if nx.is_graphical(seq):
            sols.append((d, c, ds))
    return sols

def havel_construct(n, d, c):
    ds = d + c//2
    seq = [d]*(n-1) + [ds]
    G = nx.havel_hakimi_graph(seq)
    return G

def swings_formula(G):
    E = G.number_of_edges()
    deg = dict(G.degree())
    return [E + (n-1) - 2*deg[i] for i in range(n)]

# Main sweep
print("n : (d, c, deg_special) solutions")
covered = []
for n in range(6, 151):
    sols = solve(n)
    if sols:
        covered.append(n)
        if n <= 40 or n >= 140:
            print(f"n={n:>3}: {sols}")
# residue class analysis
print("\ncovered n up to 150:", covered)
print("\nUncovered n up to 60:", [n for n in range(6,61) if n not in covered])
# find residue classes mod 7 / mod 14 that are ALWAYS covered in a range
from collections import defaultdict
cov_by_res7 = defaultdict(list)
for n in range(6, 101):
    if n in covered:
        cov_by_res7[n % 7].append(n)
for r in sorted(cov_by_res7):
    vals = cov_by_res7[r]
    if len(vals) >= 8:  # many values
        print(f"n≡{r} (mod 7): covered values = {vals[:8]}... (count {len(vals)} of 14)")
