# -*- coding: utf-8 -*-
"""W-family generator: closed-form constructions (G, F) realizing psi^n for every
6 <= n <= 80, with a brute-force swing verification against the definition.

W-family (Proposition 8 / threshold-with-exceptions family, formula (4) of the manuscript):
  v(G,F)(S) = 1  iff  |S| >= n-1  or  (|S| = n-2 and N\\S in G)  or  (|S| = n-3 and N\\S in F)
where G is a set of pairs and F a set of triples of [n].  psi^n has Banzhaf swings
(2c,...,2c,c) for a special voter s (index n-1 here).

Constructions:
  * complement-of-edges (Prop 5): n in {0,2,3,6} mod 7, d constant per residue,
    G = graph with degree seq (d,...,d, d+c/2), F = empty.
  * triangle construction (Prop 11): n in {1,4,5} mod 7, f disjoint triangles,
    q of them special (containing the special voter), p ordinary; G carries the triangle
    edges plus a matching on the residual degree, F = the triangles.

Verification is brute-force and structure-free: swing(i) =
    (n-1) - deg_G(i)                                   [|S| = n-2 swings]
  + #{ {x,y} subset N\\{i} : {x,y} in G and {x,y,i} not in F }   [|S| = n-3 swings]
and we require swing(s) = c, swing(i) = 2c for all i != s, and Pairs(F) subseteq G.

Usage: python wfamily_gen.py [nmin] [nmax]   (default 6 80)
"""
import sys


def erdos_gallai(deg):
    d = sorted(deg, reverse=True)
    n = len(d)
    if sum(d) % 2:
        return False
    s = 0
    for k in range(1, n + 1):
        s += d[k - 1]
        rhs = k * (k - 1) + sum(min(d[j], k) for j in range(k, n))
        if s > rhs:
            return False
    return True


def hh_construct(deg, forbidden=()):
    """Havel-Hakimi on the residual degree list; returns edge list of the residual graph.
    forbidden is a set of frozenset edges to avoid (already present)."""
    n = len(deg)
    adj = [[] for _ in range(n)]
    rem = list(deg)
    nodes = list(range(n))
    while True:
        nodes.sort(key=lambda v: rem[v], reverse=True)
        while nodes and rem[nodes[0]] == 0:
            nodes.pop(0)
        if not nodes:
            break
        v = nodes[0]
        if rem[v] > len(nodes) - 1:
            return None
        for u in nodes[1:rem[v] + 1]:
            if frozenset((v, u)) in forbidden:
                return None
            adj[v].append(u)
            adj[u].append(v)
            rem[v] -= 1
            rem[u] -= 1
        if rem[v] != 0:
            return None
    if any(r != 0 for r in rem):
        return None
    return adj


def complement_edge(n):
    """Prop 5: constant d per residue class; solve Corollary 2 equation 7c=d(2n-8)+4(n-1)."""
    r = n % 7
    d_by_r = {0: 3, 2: 1, 3: 4, 6: 2}
    if r not in d_by_r:
        return None
    d = d_by_r[r]
    num = d * (2 * n - 8) + 4 * (n - 1)
    if num % 7:
        return None
    c = num // 7
    if c <= 0 or c % 2 != 0:
        return None
    if not (1 <= d <= n - 2 and d + c / 2 <= n - 1):
        return None
    seq = [d] * (n - 1) + [d + c // 2]
    if not erdos_gallai(seq):
        return None
    adj = hh_construct(seq)
    if adj is None:
        return None
    G = [frozenset((i, j)) for i in range(n) for j in range(i + 1, n) if j in adj[i]]
    return G, [], c, "complement-edge"


def triangle(n):
    """Prop 11 closed form for hard residues n in {1,4,5} mod 7."""
    r = n % 7
    params = {1: (5, 28), 4: (6, 30), 5: (4, 26)}  # residue -> (f, offset) with c=(10(n-1)-offset)/7
    if r not in params:
        return None
    f, off = params[r]
    c = (10 * (n - 1) - off) // 7
    if 10 * (n - 1) - off != 7 * c or c <= 0 or c % 2:
        return None
    for q in range(0, f + 1):
        s = (c + 6) // 2 - q
        # degree sequence: special deg s, (3f-q) triangle non-special deg 2, rest deg 3
        tri_others = 3 * f - q
        rest = n - 1 - tri_others
        if rest < 0:
            continue
        seq = [s] + [2] * tri_others + [3] * rest
        if not erdos_gallai(seq):
            continue
        # build G: triangle edges first, then residual HH on special + ordinary players
        F = []
        Gset = set()
        # ordinary triangles p = f - q on ordinary vertices
        ord_players = [n - 1 - tri_others + k for k in range(rest)]  # indices beyond triangles? careful
        # label layout: vertex 0..n-1, special = n-1
        # ordinary (deg-3) vertices: pick first 'rest' non-special vertices not used by triangles
        spec = n - 1
        used = set()
        tri_spec = []  # special-triangle partners (deg 2)
        tri_ord = []   # ordinary-triangle players (deg 2)
        idx = 0
        # ordinary triangles
        for _ in range(p := f - q):
            while idx in used or idx == spec:
                idx += 1
            a = idx; idx += 1
            while idx in used or idx == spec:
                idx += 1
            b = idx; idx += 1
            while idx in used or idx == spec:
                idx += 1
            e = idx; idx += 1
            F.append((a, b, e))
            for x, y in ((a, b), (b, e), (a, e)):
                Gset.add(frozenset((x, y)))
            used.add(a); used.add(b); used.add(e)
            tri_ord += [a, b, e]
        # special triangles
        for _ in range(q):
            while idx in used or idx == spec:
                idx += 1
            a = idx; idx += 1
            while idx in used or idx == spec:
                idx += 1
            b = idx; idx += 1
            F.append((spec, a, b))
            for x, y in ((spec, a), (spec, b), (a, b)):
                Gset.add(frozenset((x, y)))
            used.add(a); used.add(b)
            tri_spec += [a, b]
        # ordinary (deg 3) residual players
        ord_players = [v for v in range(n) if v != spec and v not in used]
        if len(ord_players) != rest:
            continue
        # residual needs: special needs s - 2q extra, ord_players each need 3
        need = {}
        need[spec] = s - 2 * q
        for v in ord_players:
            need[v] = 3
        forbidden = set(Gset)
        # residual HH over the graph induced on spec + ord_players
        verts = [spec] + ord_players
        rem = {v: need[v] for v in verts}
        while True:
            verts.sort(key=lambda v: rem[v], reverse=True)
            verts = [v for v in verts if rem[v] > 0]
            if not verts:
                break
            v = verts[0]
            if rem[v] > len(verts) - 1:
                break  # fail
            for u in verts[1:rem[v] + 1]:
                e = frozenset((v, u))
                if e in forbidden:
                    break
                Gset.add(e)
                rem[v] -= 1
                rem[u] -= 1
            else:
                continue
            break  # inner break -> fail
        if any(rem.get(v, 0) != 0 for v in verts) and any(rem.values()):
            continue
        if any(rem.values()):
            continue
        G = list(Gset)
        return G, F, c, f"triangle(D3,f{f},q{q})"
    return None


def verify(n, G, F, c):
    """Brute-force swing check against definition + monotonicity Pairs(F) subset G."""
    Gset = {frozenset(e) for e in G}
    Fset = {frozenset(t) for t in F}
    # monotonicity: every pair of an F-triple is a G-edge
    for t in Fset:
        t = tuple(t)
        for x, y in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
            if frozenset((x, y)) not in Gset:
                return False, "pairs(F) not subset G"
    deg = [0] * n
    for e in Gset:
        a, b = tuple(e)
        deg[a] += 1
        deg[b] += 1
    spec = n - 1
    # |S|=n-4 swings: S u {i} is an (n-3)-set winning iff N\(S u {i}) in F, and S is losing
    # (|S|=n-4 < n-3).  Count = # of F-triples not containing i = f - r_i.
    f_in = len(Fset)
    swings = []
    for i in range(n):
        sw = (n - 1) - deg[i]
        for x in range(n):
            if x == i:
                continue
            for y in range(x + 1, n):
                if y == i:
                    continue
                if frozenset((x, y)) in Gset and frozenset((x, y, i)) not in Fset:
                    sw += 1
        sw += sum(1 for t in Fset if i not in t)
        swings.append(sw)
    ok = all(swings[i] == c if i == spec else swings[i] == 2 * c for i in range(n))
    if not ok:
        return False, f"swings wrong: {swings} (want special {c}, others {2*c})"
    return True, f"swings={swings[0]},{swings[1]}.. special={swings[spec]}, |G|={len(G)}, |F|={len(F)}"


def main():
    nmin = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    nmax = int(sys.argv[2]) if len(sys.argv) > 2 else 80
    rows = []
    for n in range(nmin, nmax + 1):
        r = n % 7
        res = None
        if r in (0, 2, 3, 6):
            res = complement_edge(n)
        if res is None and r in (1, 4, 5):
            res = triangle(n)
        if res is None:
            print(f"n={n}: NO CLOSED FORM")
            rows.append((n, None, None, None, None, "MISSING"))
            continue
        G, F, c, method = res
        ok, msg = verify(n, G, F, c)
        status = "OK" if ok else "FAIL"
        print(f"n={n} (r{r}) c={c} |G|={len(G)} |F|={len(F)} {method} {status}  {msg}" if ok
              else f"n={n} c={c} {method} {status}  {msg}")
        rows.append((n, r, c, len(G), len(F), method))


if __name__ == "__main__":
    main()
