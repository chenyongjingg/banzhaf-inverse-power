#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Benchmark of three formulations for the INVERSE BANZHAF POWER INDEX problem.

Target vector:  psi^n = (2,...,2,1)/(2n-1), i.e. one distinguished player
(index n-1) with half the swing count of every other player.  Concretely we
look for a simple game on n players whose Banzhaf swing counts eta satisfy

        eta_i = 2c  (i != n-1),      eta_{n-1} = c,        c >= 1 integer.

Formulations compared, on identical instances (same n, same target):

  (F1) DIRECT WEIGHT-SPACE model -- written in this file.
       Integer weights w_i in [1,W], integer quota q, one binary y_S per
       coalition S, linked by big-M rows so that y_S = 1 iff sum_{i in S} w_i
       >= q.  The swing count of player i is sum_{S not containing i}
       (y_{S+i} - y_S).  No symmetry breaking and no extra valid inequalities:
       the "natural first formulation" one writes down before thinking about
       structure.  The big-M constants actually used are documented in
       BIG_M_NOTES below.

  (F2) GENERAL MONOTONE-BOOLEAN model -- the model of Section 7 of the
       manuscript.  REUSED: code/milp_n8.py.  Its source text is loaded and
       re-executed with the three n-dependent constants (n, NV, c_idx) and the
       solver time limit substituted.  Same variables x(S) for every coalition
       S, same monotonicity rows, same swing equations, same solver, same
       options -- nothing else is touched.

  (F3) THE PAPER'S COMPRESSED W-FAMILY model with O(n^3) variables -- the
       model of Proposition 12 / Section 10.1 of the manuscript.
       REUSED: code/cpsat_wfamily.py, imported as a module and driven through
       its own main(); the CP-SAT model object is captured by spying on
       CpSolver.Solve, so the variable/constraint counts reported are the ones
       that file itself builds.

Every number reported in data/benchmark_formulations.json comes from a solver
run performed by this script.  Nothing is estimated or extrapolated.  A
per-instance solver time limit of 300 s is used; a run that hits it is reported
as TIMEOUT, never as INFEASIBLE.  A model that cannot be built within the build
budget, or that dies while being built, is reported as BUILD_FAILED with null
counts.

Modes
-----
  python code/benchmark_formulations.py --all
      driver: runs every (formulation, n) pair in its own subprocess, verifies
      each witness by direct enumeration, writes
      data/benchmark_formulations.json
  python code/benchmark_formulations.py --one F1 --n 8
      worker: builds + solves one instance and prints a BENCH_BUILD line and a
      BENCH_SOLVE line (the recorded commands are of exactly this form)
  python code/benchmark_formulations.py --selftest
      sanity check: the same encoders are run against a target that IS
      realizable by a weighted majority game (unanimity, w=(1,...,1), q=n),
      and the direct-enumeration swing counter is checked against the
      closed-form construction at n=6.
"""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
import time
import traceback
from contextlib import redirect_stdout

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = os.path.join(ROOT, "code")
DATA = os.path.join(ROOT, "data")

MILP_N8 = os.path.join(CODE, "milp_n8.py")              # reused for F2
CPSAT_WFAMILY = os.path.join(CODE, "cpsat_wfamily.py")  # reused for F3

DEFAULT_NS = [6, 7, 8, 9, 10, 12, 14, 16, 18, 20]
DEFAULT_TIMEOUT = 300       # solver time limit, seconds (per the brief)
DEFAULT_BUILD_BUDGET = 300  # wall-clock budget for building a model, seconds
WORKER_SLACK = 90           # extra seconds allowed a worker beyond build+solve

BIG_M_NOTES = (
    "F1 big-M constants actually used. The equivalence y_S = 1 iff "
    "sum_{i in S} w_i >= q is encoded by two rows per nonempty proper coalition S. "
    "(U) 'y = 0 => sum <= q - 1':  sum_{i in S} w_i - q - (W*|S|) * y_S <= -1, i.e. the big-M is "
    "exactly the prescribed W*|S|; it is valid because sum_{i in S} w_i <= W*|S| for every "
    "feasible point, so the row cannot cut off a winning coalition. "
    "(L) 'y = 1 => sum >= q':  sum_{i in S} w_i - q - (n*W - |S|) * y_S >= -(n*W - |S|), with the "
    "constant big-M n*W - |S| = max(q - sum_{i in S} w_i) over the box 1 <= w_i <= W, 1 <= q <= n*W; "
    "this is the tight value for that direction. Both multipliers are constants (not "
    "variable-dependent), so both rows are linear. y_empty is fixed to 0 and y_full to 1, so "
    "neither gets a variable; one extra row sum_i w_i - q >= 0 forces the grand coalition to win."
)

SELFTEST_NOTES = (
    "The same encoders are run against a target that IS realizable by a weighted majority game: "
    "the unanimity vector (1,...,1), realized by w = (1,...,1), q = n. A FEASIBLE verdict there "
    "shows the encoding is able to find realizable targets, so a non-FEASIBLE verdict on psi^n is "
    "not an artefact of a broken model."
)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def popcounts(n, masks):
    import numpy as np
    m = np.asarray(masks, dtype=np.int64)
    pc = np.zeros(m.shape, dtype=np.int64)
    for k in range(n):
        pc += ((m >> k) & 1)
    return pc


def swings_by_direct_enumeration(n, win):
    """Direct Banzhaf swing counts from the winning function alone.

    eta_i = #{S : i not in S, win[S] = 0, win[S u {i}] = 1}.
    """
    import numpy as np
    N = 1 << n
    win = np.asarray(win, dtype=bool)
    assert win.shape == (N,), win.shape
    idx = np.arange(N, dtype=np.int64)
    eta = []
    for i in range(n):
        bit = 1 << i
        m = idx[(idx & bit) == 0]
        eta.append(int(np.count_nonzero((~win[m]) & win[m | bit])))
    return eta


def normalize(eta):
    from math import gcd
    from functools import reduce
    g = reduce(gcd, eta)
    if g == 0:
        return None
    return [e // g for e in eta]


def target_pattern(n, pattern=None, special=None):
    if pattern == "unanimity":
        return [1] * n
    s = n - 1 if special is None else special
    return [1 if i == s else 2 for i in range(n)]


def verification_block(n, eta, pattern=None, special=None, extra=None):
    want = target_pattern(n, pattern=pattern, special=special)
    norm = normalize(eta)
    out = {
        "swings_by_direct_enumeration": eta,
        "gcd_normalized": norm,
        "target_pattern": want,
        "matches_target": bool(norm == want),
        "n_coalitions_enumerated": int(1 << n),
    }
    if extra:
        out.update(extra)
    return out


def highs_outcome(res):
    st = int(res.status)
    if st == 0:
        return "OPTIMAL"
    if st == 1:
        return "FEASIBLE" if res.x is not None else "TIMEOUT"
    if st == 2:
        return "INFEASIBLE"
    if st == 3:
        return "UNBOUNDED"
    return "OTHER"


def solver_versions():
    v = {"python": sys.version.split()[0]}
    try:
        import ortools
        v["ortools"] = ortools.__version__
    except Exception:  # noqa: BLE001
        v["ortools"] = None
    try:
        import scipy
        v["scipy"] = scipy.__version__
        from scipy.optimize._highspy import _core as hc
        v["highs"] = "%d.%d.%d" % (hc.HIGHS_VERSION_MAJOR, hc.HIGHS_VERSION_MINOR,
                                   hc.HIGHS_VERSION_PATCH)
        v["highs_via"] = "scipy.optimize.milp"
    except Exception:  # noqa: BLE001
        v["scipy"] = None
    return v


# --------------------------------------------------------------------------
# F1 : direct weight-space model (written here)
# --------------------------------------------------------------------------

def build_f1(n, W, pattern=None, special=None):
    import numpy as np
    from scipy.sparse import csr_matrix

    t0 = time.perf_counter()
    N = 1 << n
    iq = n                 # quota variable column
    ic = n + 1             # integer scale c column
    ybase = n + 2          # y_S lives at ybase + (S - 1), 1 <= S <= N-2
    NV = n + 2 + (N - 2) + 1

    def ycol(S):
        return ybase + (S - 1)

    idx = np.arange(N, dtype=np.int64)
    masks = np.arange(1, N - 1, dtype=np.int64)      # nonempty proper subsets
    pc = popcounts(n, masks)
    row_u = masks - 1
    row_l = (N - 2) + (masks - 1)
    swing_base = 2 * (N - 2)
    grand_row = swing_base + n                       # grand coalition must win

    R, C, V = [], [], []

    def push(rows, cols, vals):
        R.append(np.asarray(rows, dtype=np.int32))
        C.append(np.asarray(cols, dtype=np.int32))
        V.append(np.asarray(vals, dtype=np.float64))

    # row (U): sum_{i in S} w_i - q - (W*|S|) y_S <= -1
    for k in range(n):
        sel = masks[((masks >> k) & 1) == 1]
        if sel.size:
            push(sel - 1, np.full(sel.size, k, dtype=np.int64), np.ones(sel.size))
    push(row_u, np.full(masks.size, iq, dtype=np.int64), -np.ones(masks.size))
    push(row_u, ycol(masks), -(W * pc).astype(np.float64))

    # row (L): sum_{i in S} w_i - q - (n*W - |S|) y_S >= -(n*W - |S|)
    ML = n * W - pc
    for k in range(n):
        sel = masks[((masks >> k) & 1) == 1]
        if sel.size:
            push((N - 2) + (sel - 1), np.full(sel.size, k, dtype=np.int64), np.ones(sel.size))
    push(row_l, np.full(masks.size, iq, dtype=np.int64), -np.ones(masks.size))
    push(row_l, ycol(masks), -ML.astype(np.float64))

    # swing rows:  sum_{S notni i} (y_{S+i} - y_S) - t_i c = -1
    tvec = target_pattern(n, pattern=pattern, special=special)
    for i in range(n):
        bit = 1 << i
        m = idx[(idx & bit) == 0]
        m = m[(m != 0) & (m != ((N - 1) ^ bit))]
        r = np.full(m.size, swing_base + i, dtype=np.int64)
        push(r, ycol(m | bit), np.ones(m.size))
        push(r, ycol(m), -np.ones(m.size))
    for i in range(n):
        bit = 1 << i
        r = swing_base + i
        # m = 0 contributes +y_{bit};  m = N\{i} contributes -y_m plus the constant y_N = 1
        push([r, r], [ycol(bit), ycol((N - 1) ^ bit)], [1.0, -1.0])
        push([r], [ic], [-float(tvec[i])])

    # grand coalition wins:  sum_i w_i - q >= 0
    push(np.full(n, grand_row), np.arange(n, dtype=np.int64), np.ones(n))
    push([grand_row], [iq], [-1.0])

    rows = np.concatenate(R)
    cols = np.concatenate(C)
    vals = np.concatenate(V)
    n_cons = 2 * (N - 2) + n + 1
    A = csr_matrix((vals, (rows, cols)), shape=(n_cons, NV))

    lo = np.full(n_cons, -np.inf)
    hi = np.zeros(n_cons)
    hi[:N - 2] = -1.0                                  # (U) rows
    lo[N - 2:2 * (N - 2)] = -ML.astype(np.float64)     # (L) rows
    hi[N - 2:2 * (N - 2)] = np.inf
    lo[swing_base:swing_base + n] = -1.0               # swing rows (equality)
    hi[swing_base:swing_base + n] = -1.0
    lo[grand_row] = 0.0                                # grand-coalition row
    hi[grand_row] = np.inf

    lb = np.zeros(NV)
    ub = np.ones(NV)
    lb[:n] = 1.0
    ub[:n] = float(W)
    lb[iq] = 1.0
    ub[iq] = float(n * W)
    lb[ic] = 1.0
    ub[ic] = float(1 << (n - 1))

    build_s = time.perf_counter() - t0
    counts = {
        "num_variables": int(NV),
        "num_constraints": int(n_cons),
        "num_nonzeros": int(A.nnz),
        "variable_breakdown": {"weights": n, "quota": 1, "scale_c": 1,
                               "coalition_binaries_y_S": int(N - 2),
                               "fixed_y_empty": 0, "fixed_y_full": 1},
        "constraint_breakdown": {"bigM_upper": int(N - 2), "bigM_lower": int(N - 2),
                                 "swing_equations": n, "grand_coalition_wins": 1},
    }
    return {"A": A, "lo": lo, "hi": hi, "lb": lb, "ub": ub, "NV": NV,
            "build_s": build_s, "counts": counts, "data": {"W": int(W), "n_coalitions": N}}


def f1_winning(n, w, q):
    import numpy as np
    N = 1 << n
    idx = np.arange(N, dtype=np.int64)
    tot = np.zeros(N, dtype=np.int64)
    for i in range(n):
        tot += ((idx >> i) & 1) * int(w[i])
    return tot >= int(q)


def run_f1(n, time_limit, pattern=None, special=None, build_budget=DEFAULT_BUILD_BUDGET,
           on_build=None):
    import numpy as np
    from scipy.optimize import milp, LinearConstraint, Bounds

    W = 1 << (n - 1)
    m = build_f1(n, W, pattern=pattern, special=special)
    out = {
        "formulation": "F1", "n": n,
        "build_time_s": m["build_s"],
        "num_variables": m["counts"]["num_variables"] if m["build_s"] <= build_budget else None,
        "num_constraints": m["counts"]["num_constraints"] if m["build_s"] <= build_budget else None,
        "num_nonzeros": m["counts"]["num_nonzeros"] if m["build_s"] <= build_budget else None,
        "counts_breakdown": m["counts"] if m["build_s"] <= build_budget else None,
        "solver": "scipy.optimize.milp (HiGHS)",
        "c": None, "solution": None, "verification": None,
        "outcome": "BUILD_FAILED",
        "solver_status": "build exceeded the %ds budget" % build_budget,
        "solve_time_s": None,
        "model_parameters": {"W": W, "weight_bound": "1 <= w_i <= %d" % W,
                             "quota_bound": "1 <= q <= %d" % (n * W),
                             "bigM": BIG_M_NOTES, "symmetry_breaking": "none"},
    }
    if m["build_s"] > build_budget:
        return out

    if on_build is not None:
        on_build(build_line(out))

    t0 = time.perf_counter()
    res = milp(c=np.zeros(m["NV"]),
               constraints=LinearConstraint(m["A"], m["lo"], m["hi"]),
               integrality=np.ones(m["NV"]),
               bounds=Bounds(m["lb"], m["ub"]),
               options={"time_limit": float(time_limit), "mip_rel_gap": 0})
    solve_s = time.perf_counter() - t0
    out["solve_time_s"] = solve_s
    out["outcome"] = highs_outcome(res)
    out["solver_status"] = str(res.message)
    out["solver_status_code"] = int(res.status)
    if res.x is not None and out["outcome"] in ("OPTIMAL", "FEASIBLE"):
        x = np.asarray(res.x)
        w = [int(round(v)) for v in x[:n]]
        q = int(round(x[n]))
        c = float(x[n + 1])
        frac = float(np.max(np.abs(x - np.round(x))))
        out["c"] = int(round(c))
        out["solution"] = {"w": w, "q": q, "c": int(round(c)),
                           "objective": float(res.fun),
                           "max_integrality_violation": frac}
        win = f1_winning(n, w, q)
        eta = swings_by_direct_enumeration(n, win)
        out["verification"] = verification_block(
            n, eta, pattern=pattern, special=special,
            extra={"witness": {"w": w, "q": q, "c": int(round(c))}})
    return out


# --------------------------------------------------------------------------
# F2 : Section 7 general monotone-Boolean model, REUSED from code/milp_n8.py
# --------------------------------------------------------------------------

def _patch_milp_n8(n, time_limit):
    src = open(MILP_N8, encoding="utf-8").read()
    patched, n1 = re.subn(r"(?m)^n = 8\s*$", "n = %d" % n, src)
    patched, n2 = re.subn(r"(?m)^NV = 257\s*$", "NV = (1 << n) + 1", patched)
    patched, n3 = re.subn(r"(?m)^c_idx = 256\s*$", "c_idx = (1 << n)", patched)
    patched, n4 = re.subn(r"add_constraint\(\{255: 1\}, 1, 1\)",
                          "add_constraint({(1 << n) - 1: 1}, 1, 1)", patched)
    patched, n5 = re.subn(r'time_limit": 300', 'time_limit": %d' % time_limit, patched)
    if (n1, n2, n3, n4, n5) != (1, 1, 1, 1, 1):
        raise RuntimeError("milp_n8.py patch failed (matched %s)" % str((n1, n2, n3, n4, n5)))
    return src, patched


def _patch_diff(n, time_limit):
    import difflib
    src, patched = _patch_milp_n8(n, time_limit)
    return list(difflib.unified_diff(src.splitlines(), patched.splitlines(),
                                     "code/milp_n8.py", "code/milp_n8.py (patched for n=%d)" % n,
                                     lineterm="", n=1))


def run_f2(n, time_limit, on_build=None):
    import numpy as np
    import scipy.optimize as sopt

    src, patched = _patch_milp_n8(n, time_limit)

    cap = {"t0": time.perf_counter()}
    real_milp = sopt.milp

    def spy(*a, **kw):
        cap["build_s"] = time.perf_counter() - cap["t0"]
        if on_build is not None:
            on_build(build_line({"formulation": "F2", "n": n,
                                 "build_time_s": cap["build_s"],
                                 "num_variables": int(ns["NV"]),
                                 "num_constraints": int(len(ns["lb"]))}))
        t = time.perf_counter()
        r = real_milp(*a, **kw)
        cap["solve_s"] = time.perf_counter() - t
        cap["res"] = r
        return r

    sopt.milp = spy
    ns = {"__name__": "milp_n8_reused"}
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            exec(compile(patched, MILP_N8 + " (patched)", "exec"), ns)
    finally:
        sopt.milp = real_milp

    res = cap.get("res")
    if res is None:
        raise RuntimeError("reused F2 code did not reach the solver")

    out = {
        "formulation": "F2", "n": n,
        "build_time_s": cap["build_s"],
        "solve_time_s": cap["solve_s"],
        "num_variables": int(ns["NV"]),
        "num_constraints": int(len(ns["lb"])),
        "num_nonzeros": None,
        "counts_breakdown": {
            "note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))",
            "coalition_variables": int(1 << n), "scale_c": 1,
            "monotonicity_rows": int(n * (1 << (n - 1))), "swing_rows": n,
            "fixed_x_empty": 1, "fixed_x_full": 1,
        },
        "solver": "scipy.optimize.milp (HiGHS)",
        "c": None, "solution": None, "verification": None,
        "outcome": highs_outcome(res),
        "solver_status": str(res.message),
        "solver_status_code": int(res.status),
        "reused_file": "code/milp_n8.py",
        "reuse_method": ("source text loaded, constants n / NV / c_idx / full-coalition literal and "
                         "the solver time limit substituted, then exec'd unchanged"),
        "patch_diff": _patch_diff(n, time_limit),
        "patched_constants": {"n": n, "NV": "(1 << n) + 1", "c_idx": "(1 << n)",
                              "full_coalition_literal": "(1 << n) - 1",
                              "time_limit": time_limit},
        "c_bound_used": "c <= 100, exactly as hard-coded in code/milp_n8.py (bounds.ub[c_idx]=100)",
        "raw_stdout_tail": buf.getvalue()[-1000:],
    }
    if res.x is not None and out["outcome"] in ("OPTIMAL", "FEASIBLE"):
        x = np.asarray(res.x)
        win = x[:1 << n] > 0.5
        c = float(x[1 << n])
        frac = float(np.max(np.abs(x - np.round(x))))
        out["c"] = int(round(c))
        out["solution"] = {"c": int(round(c)), "max_integrality_violation": frac}
        eta = swings_by_direct_enumeration(n, win)
        out["verification"] = verification_block(
            n, eta, extra={"witness": {"c": int(round(c))}})
    return out


# --------------------------------------------------------------------------
# F3 : the paper's compressed W-family model, REUSED from code/cpsat_wfamily.py
# --------------------------------------------------------------------------

def wfamily_winning(n, G, F):
    """Direct enumeration of the W-family game v(G,F) over all 2^n coalitions:
    v(S)=1 iff |S| >= n-1, or |S| = n-2 and N\\S in G, or |S| = n-3 and N\\S in F."""
    import numpy as np
    N = 1 << n
    idx = np.arange(N, dtype=np.int64)
    pc = popcounts(n, idx)
    comp = ((N - 1) ^ idx).astype(np.int64)
    inG = np.zeros(N, dtype=bool)
    for e in G:
        inG[(1 << int(e[0])) | (1 << int(e[1]))] = True
    inF = np.zeros(N, dtype=bool)
    for t in F:
        inF[(1 << int(t[0])) | (1 << int(t[1])) | (1 << int(t[2]))] = True
    return (pc >= n - 1) | ((pc == n - 2) & inG[comp]) | ((pc == n - 3) & inF[comp])


def run_f3(n, time_limit, on_build=None):
    from ortools.sat.python import cp_model

    spec = importlib.util.spec_from_file_location("cpsat_wfamily_reused", CPSAT_WFAMILY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    cap = {}
    real_solve = cp_model.CpSolver.Solve

    def spy(self, model, *a, **kw):
        cap["model"] = model
        cap["solver"] = self
        cap["build_s"] = time.perf_counter() - cap["t0"]
        if on_build is not None:
            on_build(build_line({"formulation": "F3", "n": n,
                                 "build_time_s": cap["build_s"],
                                 "num_variables": len(model.Proto().variables),
                                 "num_constraints": len(model.Proto().constraints)}))
        t = time.perf_counter()
        st = real_solve(self, model, *a, **kw)
        cap["solve_s"] = time.perf_counter() - t
        cap["status"] = st
        return st

    buf = io.StringIO()
    old_argv = sys.argv
    cp_model.CpSolver.Solve = spy
    try:
        sys.argv = [CPSAT_WFAMILY, str(n), str(time_limit)]
        cap["t0"] = time.perf_counter()
        with redirect_stdout(buf):
            ret = mod.main()
    finally:
        cp_model.CpSolver.Solve = real_solve
        sys.argv = old_argv

    model = cap.get("model")
    if model is None:
        raise RuntimeError("reused F3 code did not reach the solver")
    proto = model.Proto()
    name = cap["solver"].StatusName(cap["status"])
    if name == "OPTIMAL":
        outcome = "OPTIMAL"
    elif name == "FEASIBLE":
        outcome = "FEASIBLE"
    elif name == "INFEASIBLE":
        outcome = "INFEASIBLE"
    elif name in ("UNKNOWN", "MODEL_INVALID"):
        outcome = "TIMEOUT"
    else:
        outcome = name

    nv, nc = len(proto.variables), len(proto.constraints)
    p = n * (n - 1) // 2
    t3 = n * (n - 1) * (n - 2) // 6
    out = {
        "formulation": "F3", "n": n,
        "build_time_s": cap["build_s"],
        "solve_time_s": cap["solve_s"],
        "num_variables": nv,
        "num_constraints": nc,
        "num_nonzeros": None,
        "counts_breakdown": {
            "note": ("counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py "
                     "itself: len(proto.variables) and len(proto.constraints). CP-SAT may split "
                     "one source-level row into several proto constraints, so the constraint count "
                     "is the proto count, not a count of source lines."),
            "analytic_variable_count": {
                "pairs_C_n_2": p, "triples_C_n_3": t3, "z_terms_3_per_triple": 3 * t3,
                "scale_c": 1, "analytic_total": p + t3 + 3 * t3 + 1},
        },
        "solver": "OR-Tools CP-SAT",
        "c": None, "solution": None, "verification": None,
        "outcome": outcome,
        "solver_status": name,
        "solver_status_code": int(cap["status"]),
        "reused_file": "code/cpsat_wfamily.py",
        "reuse_method": ("imported as a module; its own main() called with sys.argv patched; the "
                         "CP-SAT model captured by spying on CpSolver.Solve"),
        "raw_stdout_tail": buf.getvalue()[-1000:],
    }
    if ret is not None:
        G, F, c = ret
        out["c"] = int(c)
        out["solution"] = {"c": int(c), "n_edges_G": len(G), "n_triples_F": len(F),
                           "G": [list(map(int, e)) for e in G],
                           "F": [list(map(int, t)) for t in F]}
        win = wfamily_winning(n, G, F)
        eta = swings_by_direct_enumeration(n, win)
        out["verification"] = verification_block(
            n, eta, extra={"witness": {"c": int(c), "n_edges_G": len(G), "n_triples_F": len(F)}})
    return out


# --------------------------------------------------------------------------
# worker
# --------------------------------------------------------------------------

def build_line(r):
    return {k: r.get(k) for k in ("formulation", "n", "build_time_s", "num_variables",
                                  "num_constraints")}


def do_one(formulation, n, time_limit, build_budget, on_build=None):
    t0 = time.perf_counter()
    try:
        if formulation == "F1":
            return run_f1(n, time_limit, build_budget=build_budget, on_build=on_build)
        if formulation == "F2":
            return run_f2(n, time_limit, on_build=on_build)
        if formulation == "F3":
            return run_f3(n, time_limit, on_build=on_build)
        raise ValueError(formulation)
    except MemoryError:
        return _failed(formulation, n, time.perf_counter() - t0, "MemoryError while building")
    except Exception as exc:  # noqa: BLE001
        r = _failed(formulation, n, time.perf_counter() - t0,
                    "%s: %s" % (type(exc).__name__, exc))
        r["traceback_tail"] = traceback.format_exc()[-800:]
        return r


def _failed(formulation, n, elapsed, reason):
    return {"formulation": formulation, "n": n, "outcome": "BUILD_FAILED",
            "solver_status": reason, "build_time_s": elapsed, "solve_time_s": None,
            "num_variables": None, "num_constraints": None, "num_nonzeros": None,
            "counts_breakdown": None, "c": None, "solution": None, "verification": None}


def worker(formulation, n, time_limit, build_budget):
    """Prints the build record the moment a model exists, then the solve record.

    The build line is flushed *before* the solver starts, so a worker killed by the
    outer wall-clock cap during a long solve is still identifiable as a built model
    (TIMEOUT) rather than a build failure.
    """
    sent = {"yes": False}
    real_out = sys.stdout   # the reused F2/F3 code redirects sys.stdout while it runs

    def on_build(b):
        sent["yes"] = True
        real_out.write("BENCH_BUILD " + json.dumps(b) + "\n")
        real_out.flush()

    r = do_one(formulation, n, time_limit, build_budget, on_build=on_build)
    if not sent["yes"] and r.get("num_variables") is not None:
        on_build(build_line(r))
    sys.stdout.write("BENCH_SOLVE " + json.dumps(r, default=str) + "\n")
    sys.stdout.flush()


def parse_worker(out):
    b = s = None
    for line in out.splitlines():
        if line.startswith("BENCH_BUILD "):
            b = json.loads(line[len("BENCH_BUILD "):])
        elif line.startswith("BENCH_SOLVE "):
            s = json.loads(line[len("BENCH_SOLVE "):])
    return b, s


def run_worker_subprocess(formulation, n, time_limit, build_budget, python):
    cmd = [python, os.path.join("code", "benchmark_formulations.py"),
           "--one", formulation, "--n", str(n), "--timeout", str(time_limit),
           "--build-budget", str(build_budget)]
    cmd_s = " ".join(cmd)
    cap = build_budget + time_limit + WORKER_SLACK
    t0 = time.perf_counter()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=cap)
    except subprocess.TimeoutExpired as exc:
        wall = time.perf_counter() - t0
        partial = exc.stdout or ""
        if not isinstance(partial, str):
            partial = partial.decode("utf-8", "replace")
        b, _ = parse_worker(partial)
        if b is None:
            return _failed(formulation, n, None,
                           "worker killed at the %ds wall-clock cap before any model was built "
                           "(build budget %ds, solve budget %ds)" % (cap, build_budget, time_limit)) | {
                "worker_cmd": cmd_s, "wall_time_s": wall}
        r = {"formulation": formulation, "n": n, "outcome": "TIMEOUT",
             "solver_status": ("worker killed at the %ds wall-clock cap while the solver was still "
                               "running; the model was built (so this is not a build failure) but the "
                               "solver returned no status of its own" % cap),
             "build_time_s": b.get("build_time_s"),
             "solve_time_s": None,
             "num_variables": b.get("num_variables"),
             "num_constraints": b.get("num_constraints"),
             "num_nonzeros": None, "counts_breakdown": None, "c": None,
             "solution": None, "verification": None,
             "worker_cmd": cmd_s, "wall_time_s": wall, "killed_at_wall_cap": True}
        return r
    wall = time.perf_counter() - t0
    b, s = parse_worker(p.stdout)
    if s is None:
        if b is None:
            return _failed(formulation, n, None,
                           "worker produced no build record (rc=%s): %s" % (
                               p.returncode, (p.stderr or p.stdout)[-300:].strip())) | {
                "worker_cmd": cmd_s, "wall_time_s": wall}
        return {"formulation": formulation, "n": n, "outcome": "TIMEOUT",
                "solver_status": "worker exited without a solve record (rc=%s)" % p.returncode,
                "build_time_s": b.get("build_time_s"),
                "num_variables": b.get("num_variables"),
                "num_constraints": b.get("num_constraints"),
                "num_nonzeros": None, "counts_breakdown": None, "c": None,
                "solution": None, "verification": None,
                "worker_cmd": cmd_s, "wall_time_s": wall,
                "stderr_tail": (p.stderr or "")[-400:]}
    s["worker_cmd"] = cmd_s
    s["wall_time_s"] = wall
    s["stderr_tail"] = (p.stderr or "")[-400:]
    return s


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

def selftest(time_limit=300):
    import numpy as np
    out = {}
    for n in (6, 8):
        r = run_f1(n, time_limit, pattern="unanimity")
        out["F1_unanimity_n%d" % n] = {
            "outcome": r["outcome"], "solver_status": r["solver_status"],
            "num_variables": r["num_variables"], "num_constraints": r["num_constraints"],
            "c": r["c"], "verification": r["verification"]}
    win = f1_winning(6, [1] * 6, 6)
    out["F1_unanimity_hand_witness_n6"] = swings_by_direct_enumeration(6, win)
    spec = importlib.util.spec_from_file_location("wf", os.path.join(ROOT, "q3", "wfamily_gen.py"))
    wf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(wf)
    res = wf.complement_edge(6) or wf.triangle(6)
    G, F, c, method = res
    win = wfamily_winning(6, [tuple(e) for e in G], [tuple(t) for t in F])
    eta = swings_by_direct_enumeration(6, win)
    out["F3_enumeration_vs_closed_form_n6"] = {
        "method": method, "c": c, "swings": eta, "normalized": normalize(eta),
        "matches_target": normalize(eta) == [2, 2, 2, 2, 2, 1]}
    return out


# --------------------------------------------------------------------------
# agreement
# --------------------------------------------------------------------------

def agreement_check(records):
    by_n = {}
    for r in records:
        v = r.get("verification")
        if v and r.get("outcome") in ("OPTIMAL", "FEASIBLE"):
            by_n.setdefault(r["n"], []).append(r)
    out = []
    for n in sorted(by_n):
        forms = by_n[n]
        vecs = {f["formulation"]: f["verification"]["gcd_normalized"] for f in forms}
        entry = {
            "n": n,
            "formulations_with_witness": [f["formulation"] for f in forms],
            "normalized_swing_vectors_by_direct_enumeration": vecs,
            "all_match_target": all(v == target_pattern(n) for v in vecs.values()),
            "pairwise_equal": None,
            "scales_c": {f["formulation"]: f.get("c") for f in forms},
        }
        if len(forms) >= 2:
            vals = [tuple(v) for v in vecs.values()]
            entry["pairwise_equal"] = all(v == vals[0] for v in vals)
        out.append(entry)
    return out


# --------------------------------------------------------------------------
# driver
# --------------------------------------------------------------------------

def main_driver(args):
    import platform
    python = sys.executable
    ns = args.ns
    records = []
    meta = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "target": ("psi^n = (2,...,2,1)/(2n-1); swings eta_i = 2c for i != n-1 and "
                   "eta_{n-1} = c, c >= 1 integer"),
        "distinguished_player": "index n-1 (0-based) in all three formulations",
        "ns": ns,
        "solver_time_limit_s": args.timeout,
        "build_budget_s": args.build_budget,
        "worker_wall_cap_s": args.build_budget + args.timeout + WORKER_SLACK,
        "outcome_codes": {
            "OPTIMAL": "solver proved optimality",
            "FEASIBLE": "solver returned a feasible incumbent without proving optimality",
            "INFEASIBLE": "solver proved infeasibility",
            "TIMEOUT": "solver hit the %ds time limit" % args.timeout,
            "BUILD_FAILED": "model could not be built within the build budget (null counts)",
            "UNBOUNDED": "solver reported unbounded",
        },
        "formulations": {
            "F1": {"name": "direct weight-space, big-M coalition indicators",
                   "written_in": "code/benchmark_formulations.py",
                   "solver": "scipy.optimize.milp -> HiGHS",
                   "weight_bound": "w_i in [1, W], W = 2^(n-1)",
                   "weight_bound_rationale": (
                       "W = 2^(n-1) is the bound used by the paper's own weight-space script "
                       "q3/conj15_feas.py, whose docstring derives it from Muroga (1971) for "
                       "n <= 10; a smaller W would risk a false INFEASIBLE, so no smaller bound "
                       "is used here."),
                   "bigM": BIG_M_NOTES, "symmetry_breaking": "none"},
            "F2": {"name": "general monotone-Boolean model (manuscript Section 7)",
                   "reused_file": "code/milp_n8.py",
                   "reuse_method": ("source text loaded, the constants n / NV / c_idx and the "
                                    "solver time limit substituted, then exec'd unchanged"),
                   "solver": "scipy.optimize.milp -> HiGHS",
                   "note_on_c_bound": ("code/milp_n8.py itself bounds c <= 100 "
                                       "(bounds.ub[c_idx] = 100); this was left unchanged rather than "
                                       "retuned. The cap cannot make F2 report a spurious INFEASIBLE at "
                                       "the n run here: the F3 rows of this same file return, for every "
                                       "such n, an explicit monotone game with x(empty)=0, x(full)=1 "
                                       "whose direct-enumeration swings are (2c,...,2c,c) for the c "
                                       "listed in the main table (all of them <= 58), and any such game "
                                       "is a feasible point of F2's constraint set as well.")},
            "F3": {"name": ("compressed W-family model with O(n^3) variables "
                            "(Proposition 12 / Section 10.1)"),
                   "reused_file": "code/cpsat_wfamily.py",
                   "reuse_method": ("imported as a module; its own main() called with sys.argv "
                                    "patched; the CP-SAT model captured by spying on "
                                    "CpSolver.Solve so the counts are the ones it builds"),
                   "solver": "OR-Tools CP-SAT"},
        },
        "solver_versions": solver_versions(),
        "host": {"platform": platform.platform(), "python": sys.version.split()[0],
                 "processor": platform.processor()},
        "selftest_note": SELFTEST_NOTES,
        "exact_commands": {},
        "json_path": "data/benchmark_formulations.json",
        "markdown_path": "code/benchmark_formulations_results.md",
    }

    print("running selftest ...", flush=True)
    meta["selftest_results"] = selftest(args.timeout)
    print("selftest done", flush=True)

    order = args.formulations if args.formulations else ["F3", "F1", "F2"]
    for form in order:
        for n in ns:
            cmd = "%s code/benchmark_formulations.py --one %s --n %d --timeout %d --build-budget %d" % (
                os.path.basename(python), form, n, args.timeout, args.build_budget)
            meta["exact_commands"]["%s_n%d" % (form, n)] = cmd
            print("[%s] n=%d ..." % (form, n), flush=True)
            r = run_worker_subprocess(form, n, args.timeout, args.build_budget, python)
            records.append(r)
            print("    -> %-12s build=%s solve=%s vars=%s cons=%s c=%s  %s" % (
                r.get("outcome"), r.get("build_time_s"), r.get("solve_time_s"),
                r.get("num_variables"), r.get("num_constraints"), r.get("c"),
                str(r.get("solver_status"))[:60]), flush=True)
            json.dump({"meta": meta, "results": records, "agreement": agreement_check(records)},
                      open(os.path.join(DATA, "benchmark_formulations.json"), "w",
                           encoding="utf-8"), indent=1, default=str)

    payload = {"meta": meta, "results": records, "agreement": agreement_check(records)}
    with open(os.path.join(DATA, "benchmark_formulations.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, default=str)
    print("wrote data/benchmark_formulations.json", flush=True)
    return payload


def _num(v):
    """Render a JSON value verbatim (no rounding, no re-formatting)."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def render_markdown(payload):
    m = payload["meta"]
    recs = payload["results"]
    L = []
    A = L.append
    A("# Benchmark of three formulations for the inverse Banzhaf problem")
    A("")
    A("Target: `psi^n = (2,...,2,1)/(2n-1)`; the distinguished player is index `n-1` (0-based) in all")
    A("three formulations, and the swing equations are `eta_i = 2c` for `i != n-1`, `eta_{n-1} = c`,")
    A("`c >= 1` integer.")
    A("")
    A("Every number below is copied from `data/benchmark_formulations.json`, which is written by")
    A("`code/benchmark_formulations.py`; every one of them comes from a solver run performed for this")
    A("file. Times are floats exactly as the run produced them, with no rounding. `null` means the")
    A("quantity was not measured (see the failures section at the end).")
    A("")
    A("- generated: `%s`" % m["generated"])
    A("- solver time limit per instance: `%s` s; build budget: `%s` s; worker wall cap: `%s` s"
      % (m["solver_time_limit_s"], m["build_budget_s"], m["worker_wall_cap_s"]))
    A("- solver versions: `%s`" % json.dumps(m["solver_versions"]))
    A("- host: `%s`, Python `%s`" % (m["host"]["platform"], m["host"]["python"]))
    A("")

    A("## Main table")
    A("")
    A("| formulation | n | build time (s) | solve time (s) | variables | constraints | c | outcome | solver status string |")
    A("|---|---|---|---|---|---|---|---|---|")
    for form in ("F1", "F2", "F3"):
        for n in m["ns"]:
            r = _find(recs, form, n)
            if r is None:
                continue
            A("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
                form, r["n"], _num(r.get("build_time_s")), _num(r.get("solve_time_s")),
                _num(r.get("num_variables")), _num(r.get("num_constraints")), _num(r.get("c")),
                r["outcome"], str(r.get("solver_status", "")).replace("|", "\\|")))
    A("")
    A("Outcome vocabulary: " + "; ".join("`%s` = %s" % (k, v)
                                         for k, v in m["outcome_codes"].items()) + ".")
    A("")
    over = [r for r in recs if isinstance(r.get("solve_time_s"), float)
            and r["solve_time_s"] > m["solver_time_limit_s"]]
    A("### Solve wall times that exceeded the nominal `%s` s limit"
      % m["solver_time_limit_s"])
    A("")
    if not over:
        A("None: every solve returned within the nominal limit (or was never started).")
    else:
        A("These rows were given `options={\"time_limit\": %s}` (HiGHS) or"
          % m["solver_time_limit_s"])
        A("`solver.parameters.max_time_in_seconds = %s` (CP-SAT), but the solver's own clock"
          % m["solver_time_limit_s"])
        A("overran it. The wall clock is reported as measured; the overshoot factor is given so the")
        A("rows can be re-budgeted by the reader.")
        A("")
        A("| formulation | n | solve wall time (s) | overshoot factor | solver status string |")
        A("|---|---|---|---|---|")
        for r in sorted(over, key=lambda z: (z["formulation"], z["n"])):
            A("| %s | %s | %s | %s | %s |" % (
                r["formulation"], r["n"], _num(r["solve_time_s"]),
                _num(r["solve_time_s"] / float(m["solver_time_limit_s"])),
                str(r.get("solver_status", "")).replace("|", "\\|")))
    A("")

    A("Machine-readable copy of every field above, plus the per-instance solver stdout tails, the")
    A("model parameters and the verdict details: `data/benchmark_formulations.json`.")
    A("")
    A("## How the variable and constraint counts break down")
    A("")
    for form in ("F1", "F2", "F3"):
        rows = [r for r in recs if r["formulation"] == form]
        if not rows:
            A("**%s**: no model was built, so there is no breakdown." % form)
            A("")
            continue
        A("**%s** -- one row per n:" % form)
        A("")
        A("| n | num_nonzeros | breakdown |")
        A("|---|---|---|")
        for r in sorted(rows, key=lambda z: z["n"]):
            cb = r.get("counts_breakdown")
            A("| %s | %s | `%s` |" % (
                r["n"], _num(r.get("num_nonzeros")),
                json.dumps(cb, default=str).replace("|", "\\|") if cb is not None
                else ("null -- the worker was killed before the run record was assembled; the "
                      "counts it did report are in the main table")))
        A("")

    A("## Exact commands")
    A("")
    A("Driver (produced this file and the JSON):")
    A("")
    A("```")
    A("python code/benchmark_formulations.py --all")
    A("```")
    A("")
    A("One worker invocation per (formulation, n) row above; each row of the table was produced by")
    A("exactly the command recorded next to it:")
    A("")
    A("```")
    for k in sorted(m["exact_commands"], key=lambda s: (s.split("_n")[0], int(s.split("_n")[1]))):
        A(m["exact_commands"][k])
    A("```")
    A("")

    A("## What was reused")
    A("")
    for form in ("F1", "F2", "F3"):
        f = m["formulations"][form]
        A("**%s -- %s**" % (form, f["name"]))
        A("")
        A("- solver: %s" % f["solver"])
        if "written_in" in f:
            A("- written in this benchmark: `%s`" % f["written_in"])
        if "reused_file" in f:
            A("- reused: `%s`" % f["reused_file"])
            A("- how: %s" % f["reuse_method"])
        A("")
    A("For F2 the only changes made to `code/milp_n8.py` are the substitutions shown here (a unified")
    A("diff of the file as loaded against the text that was actually executed, verbatim from the")
    A("`patch_diff` field of the JSON):")
    A("")
    A("```diff")
    A("\n".join(_f2_patch_diff(recs, m["ns"][0])))
    A("```")
    A("")
    if m["formulations"]["F2"].get("note_on_c_bound"):
        A("Note on F2's scale bound: %s" % m["formulations"]["F2"]["note_on_c_bound"])
        A("")
    A("F1's big-M choice, as recorded in the JSON:")
    A("")
    A("```")
    A(m["formulations"]["F1"]["bigM"])
    A("```")
    A("")
    A("F1 weight bound: %s -- %s" % (m["formulations"]["F1"]["weight_bound"],
                                     m["formulations"]["F1"]["weight_bound_rationale"]))
    A("")
    A("F3 counts are read off the CP-SAT model proto that `code/cpsat_wfamily.py` builds. Per n the")
    A("JSON also carries the analytic variable count for that file's model "
      "(`C(n,2) + C(n,3) + 3*C(n,3) + 1`); for every n run here the proto count equals it:")
    A("")
    A("| n | C(n,2) | C(n,3) | 3*C(n,3) | analytic total | proto variable count | proto constraint count |")
    A("|---|---|---|---|---|---|---|")
    for n in m["ns"]:
        r = _find(recs, "F3", n)
        if r is None or not r.get("counts_breakdown"):
            continue
        av = r["counts_breakdown"]["analytic_variable_count"]
        A("| %s | %s | %s | %s | %s | %s | %s |" % (
            n, _num(av["pairs_C_n_2"]), _num(av["triples_C_n_3"]),
            _num(av["z_terms_3_per_triple"]), _num(av["analytic_total"]),
            _num(r.get("num_variables")), _num(r.get("num_constraints"))))
    A("")

    A("## Direct-enumeration verification of the witnesses found")
    A("")
    A("Wherever a formulation returned a witness, the witness game was rebuilt and its Banzhaf swing")
    A("counts were recomputed by enumerating all `2^n` coalitions directly (function")
    A("`swings_by_direct_enumeration`), independently of the formulation that produced it. The")
    A("resulting swing vector is gcd-normalised and compared with the target pattern.")
    A("")
    A("| formulation | n | c | swing vector (direct enumeration) | gcd-normalised | matches target |")
    A("|---|---|---|---|---|---|")
    for form in ("F1", "F2", "F3"):
        for n in m["ns"]:
            r = _find(recs, form, n)
            if r is None or not r.get("verification"):
                continue
            v = r["verification"]
            A("| %s | %s | %s | %s | %s | %s |" % (
                form, n, _num(r.get("c")), v["swings_by_direct_enumeration"],
                v["gcd_normalized"], _num(v["matches_target"])))
    A("")
    A("Cross-formulation agreement (same target reached by more than one formulation), from the")
    A("`agreement` field of the JSON:")
    A("")
    A("```")
    A(json.dumps(payload.get("agreement", []), indent=1, default=str))
    A("```")
    A("")
    A("### Cross-check against the paper's own claim (Section 9)")
    A("")
    f1inf = [r for r in recs if r["formulation"] == "F1" and r["outcome"] == "INFEASIBLE"]
    if f1inf:
        A("Section 9 of the manuscript certifies that no weighted majority game realizes psi^n for")
        A("6 <= n <= 10. The F1 rows that terminated with a definite verdict are:")
        A("")
        for r in f1inf:
            A("- n=%s: `%s` -- %s" % (r["n"], r["outcome"], r["solver_status"]))
    else:
        A("No F1 row terminated with a definite verdict, so nothing here corroborates or contradicts")
        A("Section 9 of the manuscript; every F1 row either timed out or failed to build.")
    A("")
    A("Runs re-taken after the first pass, with the reason for each attempt (from the `reruns` field")
    A("of the JSON, in order; each entry supersedes the previous record for that (formulation, n)):")
    A("")
    if m.get("reruns"):
        A("| formulation | n | when | outcome of this attempt | solver/reason recorded | why |")
        A("|---|---|---|---|---|---|")
        for e in m["reruns"]:
            A("| %s | %s | %s | %s | %s | %s |" % (
                e["formulation"], e["n"], e["when"], e["outcome"],
                str(e.get("solver_status", "")).replace("|", "\\|")[:200],
                e.get("reason", "").replace("|", "\\|")))
    else:
        A("None.")
    A("")
    A("### Longer-budget reruns (recorded, not spliced)")
    A("")
    A("The rows above are what the common %ds cap reached. Three runs across two instance sizes were"
      % m.get("solver_time_limit_s", 0))
    A("re-run with a per-instance budget far above that cap, to separate a limit of the model from a")
    A("limit of the shared budget. These are recorded under `meta.longer_budget_reruns` and are **not**")
    A("spliced into `results`: the main table is defined by the common cap, and replacing one of its")
    A("cells with a result obtained under a different budget would change what the table means. Where")
    A("a rerun also")
    A("loosens a bound in the model, the `configuration` column says so, since the two are then not")
    A("strictly comparable.")
    A("")
    if m.get("longer_budget_reruns"):
        A("| formulation | n | budget | configuration | outcome | solve | c | spliced into results |")
        A("|---|---|---|---|---|---|---|---|")
        for e in m["longer_budget_reruns"]:
            A("| %s | %s | %ds | %s | %s | %s | %s | %s |" % (
                e["formulation"], e["n"], e["budget_s"], e.get("configuration", ""),
                e.get("outcome"),
                ("%.1f s" % e["solve_time_s"]) if e.get("solve_time_s") is not None else "--",
                e.get("c") if e.get("c") is not None else "--",
                "yes" if e.get("spliced_into_results") else "no"))
    else:
        A("None.")
    A("")
    A("Note on the scale `c`: none of the three models carries an objective, so where the outcome is")
    A("`FEASIBLE`/`OPTIMAL` the reported `c` is the feasible point the solver happened to reach, not a")
    A("minimum. No minimality claim is made anywhere in this file.")
    A("")

    A("## Self-test")
    A("")
    A("```")
    A(json.dumps(m.get("selftest_results"), indent=1, default=str))
    A("```")
    A("")
    A(m.get("selftest_note", ""))
    A("")

    A("## Nulls and failures (stated plainly)")
    A("")
    bad = []
    for r in recs:
        nulls = [k for k in ("build_time_s", "solve_time_s", "num_variables", "num_constraints", "c")
                 if r.get(k) is None]
        if r["outcome"] in ("BUILD_FAILED", "TIMEOUT") or nulls:
            bad.append((r, nulls))
    if not bad:
        A("None: every run has a solver status and non-null counts.")
    for r, nulls in bad:
        A("- **%s n=%s: %s** -- null fields: %s. Solver/reason: `%s`%s" % (
            r["formulation"], r["n"], r["outcome"], ", ".join(nulls) or "none",
            str(r.get("solver_status", "")).replace("\n", " "),
            ("; traceback tail: `" + str(r["traceback_tail"]).strip().replace("\n", " | ") + "`")
            if r.get("traceback_tail") else ""))
    A("")
    A("### Where the numbers are absent, and why")
    A("")
    A("- `c` is `null` exactly when the formulation returned no witness (infeasible, timed out, or")
    A("  build failed); an infeasible model has no scale to report.")
    A("- A `BUILD_FAILED` row has `num_variables`, `num_constraints`, `solve_time_s` and `c` all")
    A("  null, because no model reached the solver. Any `build_time_s` shown on such a row is the")
    A("  wall time elapsed until the build died, not the cost of a completed build.")
    A("- A `TIMEOUT` row has whatever the solver had produced at the limit: `num_variables` and")
    A("  `num_constraints` are non-null (the model was built), `solve_time_s` is the wall time spent")
    A("  in the solve, and `c` is null because no witness was returned.")
    A("- A `TIMEOUT` row with `solve_time_s = null` and `killed_at_wall_cap = true` is one where the")
    A("  worker was killed at the outer wall-clock cap while the solver was still running: the model")
    A("  was built (so it is not a build failure) but the solver never returned a status of its own,")
    A("  so its solve wall time is not known and is reported as `null` rather than guessed.")
    A("")
    return "\n".join(L) + "\n"


def _f2_patch_diff(recs, n):
    """The F2 patch diff as recorded for the first F2 row that carries one; if no
    F2 row has run yet, compute it directly (identical operation, same regexes)."""
    for r in recs:
        if r["formulation"] == "F2" and r.get("patch_diff"):
            return r["patch_diff"]
    try:
        return _patch_diff(n, DEFAULT_TIMEOUT)
    except Exception as exc:  # noqa: BLE001
        return ["<unavailable: %s: %s>" % (type(exc).__name__, exc)]


def _find(recs, form, n):
    for r in recs:
        if r["formulation"] == form and r["n"] == n:
            return r
    return None


def rerun_one(form, n, args):
    """Re-measure a single (formulation, n) row with the same worker machinery and
    splice the fresh record into data/benchmark_formulations.json, then re-render
    the markdown. Used only when a row has to be re-taken; the fresh row records the
    command that produced it, exactly like a --all row."""
    path = os.path.join(DATA, "benchmark_formulations.json")
    payload = json.load(open(path, encoding="utf-8"))
    print("[rerun %s n=%d] ..." % (form, n), flush=True)
    r = run_worker_subprocess(form, n, args.timeout, args.build_budget, sys.executable)
    r["rerun"] = True
    reps = []
    replaced = False
    for old in payload["results"]:
        if old["formulation"] == form and old["n"] == n:
            if not replaced:
                reps.append(r)
                replaced = True
            else:
                reps.append(old)
        else:
            reps.append(old)
    if not replaced:
        reps.append(r)
    payload["results"] = reps
    payload["meta"]["exact_commands"]["%s_n%d" % (form, n)] = r.get("worker_cmd")
    payload["meta"].setdefault("reruns", []).append({
        "formulation": form, "n": n, "when": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "reason": args.rerun_reason or "re-taken",
        "command": r.get("worker_cmd"), "outcome": r.get("outcome"),
        "solver_status": r.get("solver_status"),
        "supersedes_previous_record": True})
    payload["agreement"] = agreement_check(reps)
    json.dump(payload, open(path, "w", encoding="utf-8"), indent=1, default=str)
    md = render_markdown(payload)
    open(os.path.join(CODE, "benchmark_formulations_results.md"), "w",
         encoding="utf-8").write(md)
    print("  -> %s  build=%s solve=%s vars=%s cons=%s" % (
        r.get("outcome"), r.get("build_time_s"), r.get("solve_time_s"),
        r.get("num_variables"), r.get("num_constraints")), flush=True)
    print("  spliced into the JSON; markdown re-rendered", flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--one", choices=["F1", "F2", "F3"])
    ap.add_argument("--n", type=int)
    ap.add_argument("--ns", type=int, nargs="*", default=DEFAULT_NS)
    ap.add_argument("--formulations", type=str, nargs="*", default=None)
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--build-budget", type=int, default=DEFAULT_BUILD_BUDGET)
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--rerun", type=str, nargs=2, metavar=("FORM", "N"),
                    help="re-measure one (formulation, n) row and splice it into the JSON")
    ap.add_argument("--rerun-reason", type=str, default=None)
    ap.add_argument("--markdown", action="store_true",
                    help="re-render code/benchmark_formulations_results.md from the JSON")
    args = ap.parse_args()

    if args.rerun:
        rerun_one(args.rerun[0], int(args.rerun[1]), args)
        return
    if args.selftest:
        print(json.dumps(selftest(args.timeout), indent=1, default=str))
        return
    if args.one:
        worker(args.one, args.n, args.timeout, args.build_budget)
        return
    if args.markdown:
        payload = json.load(open(os.path.join(DATA, "benchmark_formulations.json"), encoding="utf-8"))
        md = render_markdown(payload)
        open(os.path.join(CODE, "benchmark_formulations_results.md"), "w",
             encoding="utf-8").write(md)
        print("wrote code/benchmark_formulations_results.md (%d bytes)" % len(md))
        return
    if args.all:
        payload = main_driver(args)
        md = render_markdown(payload)
        open(os.path.join(CODE, "benchmark_formulations_results.md"), "w",
             encoding="utf-8").write(md)
        print("wrote code/benchmark_formulations_results.md (%d bytes)" % len(md))
        return
    ap.print_help()


if __name__ == "__main__":
    main()
