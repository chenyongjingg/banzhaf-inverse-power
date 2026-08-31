"""CP-SAT W-family that SAVES the (G,F) solution. Usage: python cpsat_save.py n [tl]"""
import sys, time, json
from ortools.sat.python import cp_model
def main():
    n=int(sys.argv[1]); tl=int(sys.argv[2]) if len(sys.argv)>2 else 120
    pairs=[(a,b) for a in range(n) for b in range(a+1,n)]
    triples=[(a,b,c) for a in range(n) for b in range(a+1,n) for c in range(b+1,n)]
    model=cp_model.CpModel()
    x={e:model.NewBoolVar(f"x{e}") for e in pairs}
    y={T:model.NewBoolVar(f"y{T}") for T in triples}
    z={(T,e):model.NewBoolVar(f"z{T}{e}") for T in triples for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]}
    c=model.NewIntVar(1,1000000,"c")
    for T in triples:
        for e in [(T[0],T[1]),(T[0],T[2]),(T[1],T[2])]:
            model.AddImplication(y[T], x[e])
            zt=z[(T,e)]
            model.AddImplication(zt, y[T]); model.AddImplication(zt, x[e])
            model.AddBoolOr([y[T].Not(), x[e].Not(), zt])
    for i in range(n):
        expr=sum(x[e] for e in pairs)+(n-1)+sum(y[T] for T in triples)
        expr-=2*sum(x[e] for e in pairs if i in e)
        expr-=sum(y[T] for T in triples if i in T)
        expr-=sum(z[(T,tuple(sorted(set(T)-{i})))] for T in triples if i in T)
        target=(2*c if i!=n-1 else c)
        model.Add(expr==target)
    solver=cp_model.CpSolver(); solver.parameters.max_time_in_seconds=tl; solver.parameters.num_search_workers=8
    t0=time.time(); status=solver.Solve(model)
    print(f"n={n}: {solver.StatusName(status)} time={time.time()-t0:.0f}s", flush=True)
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        G=[e for e in pairs if solver.Value(x[e])==1]; F=[T for T in triples if solver.Value(y[T])==1]
        cval=solver.Value(c)
        out={'n':n,'c':cval,'G':G,'F':F}
        json.dump(out, open(f'paper-raw/sol_{n}.json','w'))
        print(f"  c={cval} |G|={len(G)} |F|={len(F)} saved", flush=True)
main()
