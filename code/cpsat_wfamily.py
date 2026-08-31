"""CP-SAT solver for the unified W(G,F) family: find (G,F) with Banzhaf = psi^n.
Usage: python cpsat_wfamily.py n [time_limit_sec]"""
import sys, time
from ortools.sat.python import cp_model

def main():
    n = int(sys.argv[1])
    tl = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    pairs = [(a,b) for a in range(n) for b in range(a+1,n)]
    triples = [(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    model = cp_model.CpModel()
    x = {}   # pair -> bool (edge in G)
    for e in pairs:
        x[e] = model.NewBoolVar(f"x{e}")
    y = {}   # triple -> bool (in F)
    for T in triples:
        y[T] = model.NewBoolVar(f"y{T}")
    z = {}   # (triple, pair) -> bool
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            z[(T,e)] = model.NewBoolVar(f"z{T}{e}")
    c = model.NewIntVar(1, 1000000, "c")
    # monotonicity: y[T] implies x[e] for e subset T
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            model.AddImplication(y[T], x[e])
    # z = y AND x
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            zt = z[(T,e)]
            model.AddImplication(zt, y[T])
            model.AddImplication(zt, x[e])
            model.AddBoolOr([y[T].Not(), x[e].Not(), zt])
    # swing equations
    # beta_i = sum_pairs x + (n-1) + sum_triples y - 2*sum_{e in i} x - sum_{T in i} y - sum_{T in i} z_{T,T\i}
    for i in range(n):
        expr = sum(x[e] for e in pairs) + (n-1) + sum(y[T] for T in triples)
        expr -= 2*sum(x[e] for e in pairs if i in e)
        expr -= sum(y[T] for T in triples if i in T)
        expr -= sum(z[(T, tuple(sorted(set(T)-{i})))] for T in triples if i in T)
        target = (2*c if i != n-1 else c)
        model.Add(expr == target)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = tl
    solver.parameters.num_search_workers = 8
    t0 = time.time()
    status = solver.Solve(model)
    print(f"n={n}: status={solver.StatusName(status)} time={time.time()-t0:.0f}s", flush=True)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        G = [e for e in pairs if solver.Value(x[e]) == 1]
        F = [T for T in triples if solver.Value(y[T]) == 1]
        print(f"  c={solver.Value(c)} |G|={len(G)} |F|={len(F)}", flush=True)
        return G, F, solver.Value(c)
    return None

if __name__ == "__main__":
    main()
