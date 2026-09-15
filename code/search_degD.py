"""Search deg+r=D structure for n in (8,11,15). F-players can have r=0,1,2,3.
CP-SAT finds (G,F) with deg_i + r_i = D for non-special."""
from ortools.sat.python import cp_model
from math import gcd
from functools import reduce

def try_D(n, D, maxr=3, tl=40):
    """Find (G,F) with deg+r=D for non-special, deg+r_n = D+c/2 for special."""
    sp=n-1
    model=cp_model.CpModel()
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    triples=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    xe={e:model.NewBoolVar(f"x{e}") for e in pairs}
    y={T:model.NewBoolVar(f"y{T}") for T in triples}
    # c2 = c/2 (c even). special: deg + r_n = D + c2.
    c2=model.NewIntVar(1,500,"c2")
    for i in range(n-1):
        model.Add(sum(xe[e] for e in pairs if i in e) + sum(y[T] for T in triples if i in T) == D)
    model.Add(sum(xe[e] for e in pairs if sp in e) + sum(y[T] for T in triples if sp in T) == D + c2)
    # cap r_i
    for i in range(n):
        model.Add(sum(y[T] for T in triples if i in T) <= maxr)
    # monotonicity
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            model.AddImplication(y[T], xe[e])
    # swings (assume e_i=0 enforced by monotonicity -> X\{i} in G)
    # beta_i = g + (n-1) + f - 2deg - 2r = g+(n-1)+f-2D for non-special, g+(n-1)+f-2(D+c/2) for special
    for i in range(n):
        expr = sum(xe[e] for e in pairs) + (n-1) + sum(y[T] for T in triples) \
               - 2*sum(xe[e] for e in pairs if i in e) - 2*sum(y[T] for T in triples if i in T)
        target = (4*c2 if i!=sp else 2*c2)
        model.Add(expr == target)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=tl
    status=solver.Solve(model)
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL): return None
    G=[e for e in pairs if solver.Value(xe[e])==1]
    F=[T for T in triples if solver.Value(y[T])==1]
    cv=2*solver.Value(c2)
    # verify
    Gset=set(tuple(sorted(e)) for e in G); deg=[0]*n
    for a,b in G: deg[a]+=1; deg[b]+=1
    eta=[]
    for i in range(n):
        ri=sum(1 for X in F if i in X)
        ei=sum(1 for X in F if i in X and tuple(sorted(set(X)-{i})) not in Gset)
        eta.append(len(G)+(n-1)+len(F)-2*deg[i]-2*ri+ei)
    g=reduce(gcd,eta)
    ok=sorted(x//g for x in eta)==sorted([1]+[2]*(n-1))
    return cv, G, F, ok

print("=== search deg+r=D for n=8,11,15 ===")
for n in (8,11,15):
    found=None
    for D in range(2,9):
        r=try_D(n,D)
        if r is not None and r[3]:
            found=(D, r[0], len(r[1]), len(r[2]))
            break
    print(f"n={n}: {'FOUND D='+str(found[0])+' c='+str(found[1])+' |G|='+str(found[2])+' |F|='+str(found[3]) if found else 'not found'}")
