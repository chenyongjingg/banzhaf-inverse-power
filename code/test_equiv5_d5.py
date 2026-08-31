"""Test D=5 construction for ≡5 mod 7, allowing r=2 players.
Structure: f=6 triples, special in r_n triples; F-players with r=1 or 2; some r=0.
Uses CP-SAT to build (G,F) with the deg+r=D=5 pattern."""
from ortools.sat.python import cp_model
from math import gcd
from functools import reduce

def construct(n, D, f, r_n, r1, r2):
    """r1 players with r=1 (deg D-1), r2 players with r=2 (deg D-2),
    rest non-special r=0 (deg D). r_n = special's F-count."""
    sp=n-1
    Nf = r1 + r2   # non-special players in F
    # check incidence consistency: 2*r2 + r1 (non-special incidences) + r_n = 3f
    if 2*r2 + r1 + r_n != 3*f: return None
    if Nf > n-1: return None
    c = (2*D*(n-4)+4*(n-1)-2*f)//7
    if c<=0: return None
    s = D + c//2 - r_n
    if s<0 or s>n-1: return None
    # degrees: r2 players D-2, r1 players D-1, r0 players D, special s
    target=[]
    for i in range(r2): target.append(D-2)
    for i in range(r2, r2+r1): target.append(D-1)
    for i in range(r2+r1, n-1): target.append(D)
    target.append(s)
    assert len(target)==n
    # F-triples: build via CP-SAT too (need r_i = 1 or 2, r_n = r_n, pairs subset G)
    # Simpler: use full CP-SAT with deg+r=D constraint. Let's just verify via existing solutions approach.
    # Use a CP-SAT model for (G, F) directly with deg constraint.
    model=cp_model.CpModel()
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    triples=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    xe={e:model.NewBoolVar(f"x{e}") for e in pairs}
    y={T:model.NewBoolVar(f"y{T}") for T in triples}
    # deg_i = D - r_i for non-special, s for special
    for i in range(n):
        deg_i = sum(xe[e] for e in pairs if i in e)
        model.Add(deg_i == target[i])
    # F-count: r_i for non-special (0,1,2), r_n for special
    for i in range(n-1):
        ri = sum(y[T] for T in triples if i in T)
        if i < r2:
            model.Add(ri==2)
        elif i < r2+r1:
            model.Add(ri==1)
        else:
            model.Add(ri==0)
    rn = sum(y[T] for T in triples if sp in T)
    model.Add(rn==r_n)
    # monotonicity: y_T implies x_e for e subset T
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            model.AddImplication(y[T], xe[e])
    # swings
    for i in range(n):
        expr = sum(xe[e] for e in pairs) + (n-1) + sum(y[T] for T in triples)
        expr -= 2*sum(xe[e] for e in pairs if i in e)
        expr -= 2*sum(y[T] for T in triples if i in T)
        expr += sum(y[T] for T in triples if i in T and tuple(sorted(set(T)-{i})) not in pairs and False)
        # e_i via z linearization
        # (skip e_i for simplicity - assume e_i=0 by forcing pairs in G)
    # e_i=0: for X in F, all pairs in G. Enforce via: y[T] -> x[e] for all pairs in T (done above).
    # swings with e=0: beta = g + (n-1) + f - 2deg - 2r
    for i in range(n):
        g = sum(xe[e] for e in pairs)
        fterm = sum(y[T] for T in triples)
        expr = g + (n-1) + fterm - 2*sum(xe[e] for e in pairs if i in e) - 2*sum(y[T] for T in triples if i in T)
        target_v = (2*c if i != sp else c)
        model.Add(expr == target_v)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=40
    status=solver.Solve(model)
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    G=[e for e in pairs if solver.Value(xe[e])==1]
    F=[T for T in triples if solver.Value(y[T])==1]
    return c, s, G, F

print("=== ≡5, D=5, f=6: try for n=12,19,26,33,40 ===")
for n in (12,19,26,33,40):
    found=None
    for r2 in range(0,8):
        for r1 in range(0,12):
            # 2r2 + r1 + r_n = 18, so r_n = 18 - 2r2 - r1
            rn = 18 - 2*r2 - r1
            if rn<0 or rn>6: continue
            if r2+r1 > n-1: continue
            r=construct(n,5,6,rn,r1,r2)
            if r is not None:
                c,s,G,F=r
                # verify swings
                N=n; Gset=set(tuple(sorted(e)) for e in G); deg=[0]*N
                for a,b in G: deg[a]+=1; deg[b]+=1
                eta=[]
                for i in range(N):
                    ri=sum(1 for X in F if i in X)
                    ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
                    eta.append(len(G)+(N-1)+len(F)-2*deg[i]-2*ri+ei)
                from math import gcd
                from functools import reduce
                g=reduce(gcd,eta)
                if sorted(x//g for x in eta)==sorted([1]+[2]*(N-1)):
                    found=(r2,r1,rn,c,s)
                    break
        if found: break
    print(f"n={n} (≡5): found={found}")
