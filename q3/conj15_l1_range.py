# -*- coding: utf-8 -*-
"""Conjecture 15 L1-optimal computation over a RANGE of T (continuation for n=8).
Sweeps T in [Tmin, Tmax], reports the global best over the range.  Uses the model
from conj15_l1.py (imported), weight bound 2^(n-1) conclusive, sw=1 per worker.

Usage: python conj15_l1_range.py [n] [Tmin] [Tmax] [perT_timeout] [procs]
"""
import sys, time
from conj15_l1 import solve_T_wrap

def main():
    import multiprocessing as mp
    n = int(sys.argv[1]); Tmin = int(sys.argv[2]); Tmax = int(sys.argv[3])
    timeout = int(sys.argv[4]) if len(sys.argv) > 4 else 90
    procs = int(sys.argv[5]) if len(sys.argv) > 5 else 10
    W = 1 << (n - 1); k = 2 * n - 1
    best = None; t0 = time.time()
    jobs = [(n, W, T, timeout, 1) for T in range(Tmin, Tmax + 1)]
    pool = mp.Pool(procs)
    done = 0
    for T, r in pool.imap_unordered(solve_T_wrap, jobs):
        done += 1
        if r is None:
            if done % 40 == 0:
                print(f"  ...{done}/{len(jobs)} done (T in [{Tmin},{Tmax}]), "
                      f"{time.time()-t0:.0f}s, best={best[0] if best else None} at T={best[1] if best else None}",
                      flush=True)
            continue
        l1, eta, w, q, opt = r
        if best is None or l1 < best[0]:
            best = (l1, T, eta, w, q, opt)
            print(f"  T={T}: l1={l1:.6f} opt={opt} eta={eta} w={w} q={q}  [best in range]", flush=True)
        if done % 40 == 0:
            print(f"  ...{done}/{len(jobs)} done (T in [{Tmin},{Tmax}]), "
                  f"{time.time()-t0:.0f}s, best={best[0] if best else None:.6f} at T={best[1] if best else None}",
                  flush=True)
    pool.close(); pool.join()
    if best:
        l1, T, eta, w, q, opt = best
        print(f"n={n} RANGE[{Tmin},{Tmax}] RESULT: best L1 = {l1:.8f} at T={T} (opt={opt})  n*L1={n*l1:.6f}")
        print(f"  eta={eta} w={w} q={q}")
        print(f"  NOTE: re-run 'python conj15_l1.py confirm {n} {T} 600' to certify the winning T as OPTIMAL")
    else:
        print(f"n={n} RANGE[{Tmin},{Tmax}]: no feasible T (all UNKNOWN/INFEASIBLE within {timeout}s each)")

if __name__ == "__main__":
    main()
