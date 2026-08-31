# -*- coding: utf-8 -*-
"""n=9 L1 focused re-check with per-T STATUS classification (SOLVED/INFEASIBLE/UNKNOWN).
Decisive: distinguish timeout (UNKNOWN) from proven infeasible, so we know whether
the range sweep's 'best' claim is certified.  Reuses conj15_l1.solve_T.
Usage: python l1_n9_status.py [Tmin] [Tmax] [perT_timeout] [procs]
"""
import sys, time
from conj15_l1 import solve_T, build_swing_model
from ortools.sat.python import cp_model

N_GLOBAL = 9
W_GLOBAL = 1 << (N_GLOBAL - 1)
TIMEOUT_GLOBAL = 120


def work(T):
    r = solve_T(N_GLOBAL, W_GLOBAL, T, TIMEOUT_GLOBAL, sw=1)
    if r is None:
        # re-solve with FEASIBILITY check only to distinguish INFEASIBLE vs UNKNOWN
        m, w, q, eta = build_swing_model(N_GLOBAL, W_GLOBAL)
        m.Add(sum(eta) == T)
        s2 = cp_model.CpSolver()
        s2.parameters.max_time_in_seconds = TIMEOUT_GLOBAL
        s2.parameters.num_search_workers = 1
        st2 = s2.Solve(m)
        if st2 == cp_model.INFEASIBLE:
            return (T, "INFEASIBLE", None)
        if st2 == cp_model.UNKNOWN or st2 == cp_model.MODEL_INVALID:
            return (T, "UNKNOWN", None)
        return (T, f"FEASIBLE_NO_OBJ({st2})", None)
    l1, eta_v, w_v, q_v, opt = r
    return (T, f"SOLVED(opt={opt})", (l1, eta_v, w_v, q_v))


def main():
    import multiprocessing as mp
    global TIMEOUT_GLOBAL
    Tmin = int(sys.argv[1]); Tmax = int(sys.argv[2])
    TIMEOUT_GLOBAL = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    procs = int(sys.argv[4]) if len(sys.argv) > 4 else 20
    t0 = time.time()

    pool = mp.Pool(procs)
    res = pool.map(work, range(Tmin, Tmax + 1))
    pool.close(); pool.join()

    solved = [r for r in res if r[1].startswith("SOLVED")]
    infeas = [r for r in res if r[1] == "INFEASIBLE"]
    unknown = [r for r in res if r[1] == "UNKNOWN"]
    best = min(solved, key=lambda r: r[2][0]) if solved else None
    print(f"n=9 STATUS[{Tmin},{Tmax}] {time.time()-t0:.0f}s: "
          f"solved={len(solved)} infeasible={len(infeas)} UNKNOWN={len(unknown)}")
    if unknown:
        print(f"  UNKNOWN T values (certification gaps): {[r[0] for r in unknown]}")
    if best:
        l1, eta_v, w_v, q_v = best[2]
        print(f"  best among solved: l1={l1:.8f} @T={best[0]} n*L1={9*l1:.6f} eta={eta_v} w={w_v} q={q_v}")
    else:
        print("  no solved T in range")
    print("  all-ones baseline: l1=0.104575 @T=9 n*L1=0.941176")

if __name__ == "__main__":
    main()
