# Benchmark of three formulations for the inverse Banzhaf problem

Target: `psi^n = (2,...,2,1)/(2n-1)`; the distinguished player is index `n-1` (0-based) in all
three formulations, and the swing equations are `eta_i = 2c` for `i != n-1`, `eta_{n-1} = c`,
`c >= 1` integer.

Every number below is copied from `data/benchmark_formulations.json`, which is written by
`code/benchmark_formulations.py`; every one of them comes from a solver run performed for this
file. Times are floats exactly as the run produced them, with no rounding. `null` means the
quantity was not measured (see the failures section at the end).

- generated: `2026-09-13T23:17:27`
- solver time limit per instance: `300` s; build budget: `300` s; worker wall cap: `690` s
- solver versions: `{"python": "3.14.4", "ortools": "9.15.6755", "scipy": "1.17.1", "highs": "1.12.0", "highs_via": "scipy.optimize.milp"}`
- host: `Windows-11-10.0.26200-SP0`, Python `3.14.4`

## Main table

| formulation | n | build time (s) | solve time (s) | variables | constraints | c | outcome | solver status string |
|---|---|---|---|---|---|---|---|---|
| F1 | 6 | 0.0011061999830417335 | 43.466873799974564 | 71 | 131 | null | INFEASIBLE | The problem is infeasible. (HiGHS Status 8: model_status is Infeasible; primal_status is None) |
| F1 | 7 | 0.0012426000321283937 | 300.0183593999827 | 136 | 260 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 8 | 0.0021995999850332737 | 300.0296534000081 | 265 | 517 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 9 | 0.0019503000075928867 | 300.0285994000151 | 522 | 1030 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 10 | 0.0026962999836541712 | 300.02976810000837 | 1035 | 2055 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 12 | 0.009375699970405549 | 302.9020290999906 | 4109 | 8201 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 14 | 0.03925370000069961 | 306.05223390000174 | 16399 | 32779 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 16 | 0.13684590003686026 | 300.62682080001105 | 65553 | 131085 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 18 | 0.8600140000344254 | 305.3845195999602 | 262163 | 524303 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 20 | 4.303116799972486 | null | 1048597 | 2097169 | null | TIMEOUT | worker killed at the 690s wall-clock cap while the solver was still running; the model was built (so this is not a build failure) but the solver returned no status of its own |
| F2 | 6 | 0.00405069999396801 | 0.062146599986590445 | 65 | 201 | 4 | OPTIMAL | Optimization terminated successfully. (HiGHS Status 7: Optimal) |
| F2 | 7 | 0.0035516000352799892 | 0.11754569999175146 | 129 | 458 | 10 | OPTIMAL | Optimization terminated successfully. (HiGHS Status 7: Optimal) |
| F2 | 8 | 0.005524000036530197 | 1.4067077000509016 | 257 | 1035 | 8 | OPTIMAL | Optimization terminated successfully. (HiGHS Status 7: Optimal) |
| F2 | 9 | 0.009722899994812906 | 0.7464620999526232 | 513 | 2316 | 6 | OPTIMAL | Optimization terminated successfully. (HiGHS Status 7: Optimal) |
| F2 | 10 | 0.019313500029966235 | 2.6287662999820895 | 1025 | 5133 | 10 | OPTIMAL | Optimization terminated successfully. (HiGHS Status 7: Optimal) |
| F2 | 12 | 0.08305779995862395 | 655.4418238999788 | 4097 | 24591 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F2 | 14 | 0.4103655999642797 | 300.1784757000278 | 16385 | 114705 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F2 | 16 | 1.965991600009147 | 407.94920339999953 | 65537 | 524307 | null | TIMEOUT | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F2 | 18 | 8.834927499992773 | null | 262145 | 2359317 | null | TIMEOUT | worker killed at the 690s wall-clock cap while the solver was still running; the model was built (so this is not a build failure) but the solver returned no status of its own |
| F2 | 20 | 318.7313907999778 | null | null | null | null | BUILD_FAILED | MemoryError while building |
| F3 | 6 | 0.00403740000911057 | 0.03119840001454577 | 96 | 246 | 4 | OPTIMAL | OPTIMAL |
| F3 | 7 | 0.006349200033582747 | 0.052731000003404915 | 162 | 427 | 6 | OPTIMAL | OPTIMAL |
| F3 | 8 | 0.009315400035120547 | 0.06507690000580624 | 253 | 680 | 8 | OPTIMAL | OPTIMAL |
| F3 | 9 | 0.012853499967604876 | 0.06753360002767295 | 373 | 1017 | 6 | OPTIMAL | OPTIMAL |
| F3 | 10 | 0.01950100000249222 | 0.4297573000076227 | 526 | 1450 | 10 | OPTIMAL | OPTIMAL |
| F3 | 12 | 0.03632249997463077 | 0.2859417999861762 | 947 | 2652 | 24 | OPTIMAL | OPTIMAL |
| F3 | 14 | 0.06125679996330291 | 0.5133408000110649 | 1548 | 4382 | 16 | OPTIMAL | OPTIMAL |
| F3 | 16 | 0.09609780000755563 | 0.7295754000078887 | 2361 | 6736 | 12 | OPTIMAL | OPTIMAL |
| F3 | 18 | 0.1359830999863334 | 1.2925072999787517 | 3418 | 9810 | 28 | OPTIMAL | OPTIMAL |
| F3 | 20 | 0.1944132999633439 | 2.1426802999922074 | 4751 | 13700 | 58 | OPTIMAL | OPTIMAL |

Outcome vocabulary: `OPTIMAL` = solver proved optimality; `FEASIBLE` = solver returned a feasible incumbent without proving optimality; `INFEASIBLE` = solver proved infeasibility; `TIMEOUT` = solver hit the 300s time limit; `BUILD_FAILED` = model could not be built within the build budget (null counts); `UNBOUNDED` = solver reported unbounded.

### Solve wall times that exceeded the nominal `300` s limit

These rows were given `options={"time_limit": 300}` (HiGHS) or
`solver.parameters.max_time_in_seconds = 300` (CP-SAT), but the solver's own clock
overran it. The wall clock is reported as measured; the overshoot factor is given so the
rows can be re-budgeted by the reader.

| formulation | n | solve wall time (s) | overshoot factor | solver status string |
|---|---|---|---|---|
| F1 | 7 | 300.0183593999827 | 1.0000611979999425 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 8 | 300.0296534000081 | 1.0000988446666936 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 9 | 300.0285994000151 | 1.0000953313333836 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 10 | 300.02976810000837 | 1.000099227000028 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 12 | 302.9020290999906 | 1.0096734303333021 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 14 | 306.05223390000174 | 1.0201741130000057 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 16 | 300.62682080001105 | 1.0020894026667035 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F1 | 18 | 305.3845195999602 | 1.0179483986665339 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F2 | 12 | 655.4418238999788 | 2.184806079666596 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F2 | 14 | 300.1784757000278 | 1.0005949190000927 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |
| F2 | 16 | 407.94920339999953 | 1.3598306779999985 | Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None) |

Machine-readable copy of every field above, plus the per-instance solver stdout tails, the
model parameters and the verdict details: `data/benchmark_formulations.json`.

## How the variable and constraint counts break down

**F1** -- one row per n:

| n | num_nonzeros | breakdown |
|---|---|---|
| 6 | 1005 | `{"num_variables": 71, "num_constraints": 131, "num_nonzeros": 1005, "variable_breakdown": {"weights": 6, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 62, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 62, "bigM_lower": 62, "swing_equations": 6, "grand_coalition_wins": 1}}` |
| 7 | 2283 | `{"num_variables": 136, "num_constraints": 260, "num_nonzeros": 2283, "variable_breakdown": {"weights": 7, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 126, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 126, "bigM_lower": 126, "swing_equations": 7, "grand_coalition_wins": 1}}` |
| 8 | 5097 | `{"num_variables": 265, "num_constraints": 517, "num_nonzeros": 5097, "variable_breakdown": {"weights": 8, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 254, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 254, "bigM_lower": 254, "swing_equations": 8, "grand_coalition_wins": 1}}` |
| 9 | 11239 | `{"num_variables": 522, "num_constraints": 1030, "num_nonzeros": 11239, "variable_breakdown": {"weights": 9, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 510, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 510, "bigM_lower": 510, "swing_equations": 9, "grand_coalition_wins": 1}}` |
| 10 | 24549 | `{"num_variables": 1035, "num_constraints": 2055, "num_nonzeros": 24549, "variable_breakdown": {"weights": 10, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 1022, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 1022, "bigM_lower": 1022, "swing_equations": 10, "grand_coalition_wins": 1}}` |
| 12 | 114657 | `{"num_variables": 4109, "num_constraints": 8201, "num_nonzeros": 114657, "variable_breakdown": {"weights": 12, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 4094, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 4094, "bigM_lower": 4094, "swing_equations": 12, "grand_coalition_wins": 1}}` |
| 14 | 524253 | `{"num_variables": 16399, "num_constraints": 32779, "num_nonzeros": 524253, "variable_breakdown": {"weights": 14, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 16382, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 16382, "bigM_lower": 16382, "swing_equations": 14, "grand_coalition_wins": 1}}` |
| 16 | 2359257 | `{"num_variables": 65553, "num_constraints": 131085, "num_nonzeros": 2359257, "variable_breakdown": {"weights": 16, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 65534, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 65534, "bigM_lower": 65534, "swing_equations": 16, "grand_coalition_wins": 1}}` |
| 18 | 10485717 | `{"num_variables": 262163, "num_constraints": 524303, "num_nonzeros": 10485717, "variable_breakdown": {"weights": 18, "quota": 1, "scale_c": 1, "coalition_binaries_y_S": 262142, "fixed_y_empty": 0, "fixed_y_full": 1}, "constraint_breakdown": {"bigM_upper": 262142, "bigM_lower": 262142, "swing_equations": 18, "grand_coalition_wins": 1}}` |
| 20 | null | `null -- the worker was killed before the run record was assembled; the counts it did report are in the main table` |

**F2** -- one row per n:

| n | num_nonzeros | breakdown |
|---|---|---|
| 6 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 64, "scale_c": 1, "monotonicity_rows": 192, "swing_rows": 6, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 7 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 128, "scale_c": 1, "monotonicity_rows": 448, "swing_rows": 7, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 8 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 256, "scale_c": 1, "monotonicity_rows": 1024, "swing_rows": 8, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 9 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 512, "scale_c": 1, "monotonicity_rows": 2304, "swing_rows": 9, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 10 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 1024, "scale_c": 1, "monotonicity_rows": 5120, "swing_rows": 10, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 12 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 4096, "scale_c": 1, "monotonicity_rows": 24576, "swing_rows": 12, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 14 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 16384, "scale_c": 1, "monotonicity_rows": 114688, "swing_rows": 14, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 16 | null | `{"note": "counts are exactly what code/milp_n8.py constructs (NV, len(lb))", "coalition_variables": 65536, "scale_c": 1, "monotonicity_rows": 524288, "swing_rows": 16, "fixed_x_empty": 1, "fixed_x_full": 1}` |
| 18 | null | `null -- the worker was killed before the run record was assembled; the counts it did report are in the main table` |
| 20 | null | `null -- the worker was killed before the run record was assembled; the counts it did report are in the main table` |

**F3** -- one row per n:

| n | num_nonzeros | breakdown |
|---|---|---|
| 6 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 15, "triples_C_n_3": 20, "z_terms_3_per_triple": 60, "scale_c": 1, "analytic_total": 96}}` |
| 7 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 21, "triples_C_n_3": 35, "z_terms_3_per_triple": 105, "scale_c": 1, "analytic_total": 162}}` |
| 8 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 28, "triples_C_n_3": 56, "z_terms_3_per_triple": 168, "scale_c": 1, "analytic_total": 253}}` |
| 9 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 36, "triples_C_n_3": 84, "z_terms_3_per_triple": 252, "scale_c": 1, "analytic_total": 373}}` |
| 10 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 45, "triples_C_n_3": 120, "z_terms_3_per_triple": 360, "scale_c": 1, "analytic_total": 526}}` |
| 12 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 66, "triples_C_n_3": 220, "z_terms_3_per_triple": 660, "scale_c": 1, "analytic_total": 947}}` |
| 14 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 91, "triples_C_n_3": 364, "z_terms_3_per_triple": 1092, "scale_c": 1, "analytic_total": 1548}}` |
| 16 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 120, "triples_C_n_3": 560, "z_terms_3_per_triple": 1680, "scale_c": 1, "analytic_total": 2361}}` |
| 18 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 153, "triples_C_n_3": 816, "z_terms_3_per_triple": 2448, "scale_c": 1, "analytic_total": 3418}}` |
| 20 | null | `{"note": "counts are read off the CP-SAT model proto built by code/cpsat_wfamily.py itself: len(proto.variables) and len(proto.constraints). CP-SAT may split one source-level row into several proto constraints, so the constraint count is the proto count, not a count of source lines.", "analytic_variable_count": {"pairs_C_n_2": 190, "triples_C_n_3": 1140, "z_terms_3_per_triple": 3420, "scale_c": 1, "analytic_total": 4751}}` |

## Exact commands

Driver (produced this file and the JSON):

```
python code/benchmark_formulations.py --all
```

One worker invocation per (formulation, n) row above; each row of the table was produced by
exactly the command recorded next to it:

```
python.exe code/benchmark_formulations.py --one F1 --n 6 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 7 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 8 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 9 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 10 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 12 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 14 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 16 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F1 --n 18 --timeout 300 --build-budget 300
C:\Python314\python.exe code\benchmark_formulations.py --one F1 --n 20 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 6 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 7 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 8 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 9 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 10 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 12 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 14 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 16 --timeout 300 --build-budget 300
C:\Python314\python.exe code\benchmark_formulations.py --one F2 --n 18 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F2 --n 20 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 6 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 7 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 8 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 9 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 10 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 12 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 14 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 16 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 18 --timeout 300 --build-budget 300
python.exe code/benchmark_formulations.py --one F3 --n 20 --timeout 300 --build-budget 300
```

## What was reused

**F1 -- direct weight-space, big-M coalition indicators**

- solver: scipy.optimize.milp -> HiGHS
- written in this benchmark: `code/benchmark_formulations.py`

**F2 -- general monotone-Boolean model (manuscript Section 7)**

- solver: scipy.optimize.milp -> HiGHS
- reused: `code/milp_n8.py`
- how: source text loaded, the constants n / NV / c_idx and the solver time limit substituted, then exec'd unchanged

**F3 -- compressed W-family model with O(n^3) variables (Proposition 12 / Section 10.1)**

- solver: OR-Tools CP-SAT
- reused: `code/cpsat_wfamily.py`
- how: imported as a module; its own main() called with sys.argv patched; the CP-SAT model captured by spying on CpSolver.Solve so the counts are the ones it builds

For F2 the only changes made to `code/milp_n8.py` are the substitutions shown here (a unified
diff of the file as loaded against the text that was actually executed, verbatim from the
`patch_diff` field of the JSON):

```diff
--- code/milp_n8.py
+++ code/milp_n8.py (patched for n=6)
@@ -7,6 +7,5 @@
 
-n = 8
-NV = 257
-c_idx = 256
-
+n = 6
+NV = (1 << n) + 1
+c_idx = (1 << n)
 I = []   # row indices
@@ -26,3 +25,3 @@
 add_constraint({0: 1}, 0, 0)
-add_constraint({255: 1}, 1, 1)
+add_constraint({(1 << n) - 1: 1}, 1, 1)
 
```

Note on F2's scale bound: code/milp_n8.py itself bounds c <= 100 (bounds.ub[c_idx] = 100); this was left unchanged. The manuscript's own constructions give c <= 24 for every n <= 20 considered here, so this cap cannot turn a feasible instance into an infeasible one at these n.

F1's big-M choice, as recorded in the JSON:

```
F1 big-M constants actually used. The equivalence y_S = 1 iff sum_{i in S} w_i >= q is encoded by two rows per nonempty proper coalition S. (U) 'y = 0 => sum <= q - 1':  sum_{i in S} w_i - q - (W*|S|) * y_S <= -1, i.e. the big-M is exactly the prescribed W*|S|; it is valid because sum_{i in S} w_i <= W*|S| for every feasible point, so the row cannot cut off a winning coalition. (L) 'y = 1 => sum >= q':  sum_{i in S} w_i - q - (n*W - |S|) * y_S >= -(n*W - |S|), with the constant big-M n*W - |S| = max(q - sum_{i in S} w_i) over the box 1 <= w_i <= W, 1 <= q <= n*W; this is the tight value for that direction. Both multipliers are constants (not variable-dependent), so both rows are linear. y_empty is fixed to 0 and y_full to 1, so neither gets a variable; one extra row sum_i w_i - q >= 0 forces the grand coalition to win.
```

F1 weight bound: w_i in [1, W], W = 2^(n-1) -- W = 2^(n-1) is the bound used by the paper's own weight-space script q3/conj15_feas.py, whose docstring states it is conclusive; a smaller W would risk a false INFEASIBLE, so no smaller bound is used here.

F3 counts are read off the CP-SAT model proto that `code/cpsat_wfamily.py` builds. Per n the
JSON also carries the analytic variable count for that file's model (`C(n,2) + C(n,3) + 3*C(n,3) + 1`); for every n run here the proto count equals it:

| n | C(n,2) | C(n,3) | 3*C(n,3) | analytic total | proto variable count | proto constraint count |
|---|---|---|---|---|---|---|
| 6 | 15 | 20 | 60 | 96 | 96 | 246 |
| 7 | 21 | 35 | 105 | 162 | 162 | 427 |
| 8 | 28 | 56 | 168 | 253 | 253 | 680 |
| 9 | 36 | 84 | 252 | 373 | 373 | 1017 |
| 10 | 45 | 120 | 360 | 526 | 526 | 1450 |
| 12 | 66 | 220 | 660 | 947 | 947 | 2652 |
| 14 | 91 | 364 | 1092 | 1548 | 1548 | 4382 |
| 16 | 120 | 560 | 1680 | 2361 | 2361 | 6736 |
| 18 | 153 | 816 | 2448 | 3418 | 3418 | 9810 |
| 20 | 190 | 1140 | 3420 | 4751 | 4751 | 13700 |

## Direct-enumeration verification of the witnesses found

Wherever a formulation returned a witness, the witness game was rebuilt and its Banzhaf swing
counts were recomputed by enumerating all `2^n` coalitions directly (function
`swings_by_direct_enumeration`), independently of the formulation that produced it. The
resulting swing vector is gcd-normalised and compared with the target pattern.

| formulation | n | c | swing vector (direct enumeration) | gcd-normalised | matches target |
|---|---|---|---|---|---|
| F2 | 6 | 4 | [8, 8, 8, 8, 8, 4] | [2, 2, 2, 2, 2, 1] | true |
| F2 | 7 | 10 | [20, 20, 20, 20, 20, 20, 10] | [2, 2, 2, 2, 2, 2, 1] | true |
| F2 | 8 | 8 | [16, 16, 16, 16, 16, 16, 16, 8] | [2, 2, 2, 2, 2, 2, 2, 1] | true |
| F2 | 9 | 6 | [12, 12, 12, 12, 12, 12, 12, 12, 6] | [2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F2 | 10 | 10 | [20, 20, 20, 20, 20, 20, 20, 20, 20, 10] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 6 | 4 | [8, 8, 8, 8, 8, 4] | [2, 2, 2, 2, 2, 1] | true |
| F3 | 7 | 6 | [12, 12, 12, 12, 12, 12, 6] | [2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 8 | 8 | [16, 16, 16, 16, 16, 16, 16, 8] | [2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 9 | 6 | [12, 12, 12, 12, 12, 12, 12, 12, 6] | [2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 10 | 10 | [20, 20, 20, 20, 20, 20, 20, 20, 20, 10] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 12 | 24 | [48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 24] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 14 | 16 | [32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 16] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 16 | 12 | [24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 12] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 18 | 28 | [56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 56, 28] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |
| F3 | 20 | 58 | [116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 58] | [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1] | true |

Cross-formulation agreement (same target reached by more than one formulation), from the
`agreement` field of the JSON:

```
[
 {
  "n": 6,
  "formulations_with_witness": [
   "F3",
   "F2"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    1
   ],
   "F2": [
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": true,
  "scales_c": {
   "F3": 4,
   "F2": 4
  }
 },
 {
  "n": 7,
  "formulations_with_witness": [
   "F3",
   "F2"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ],
   "F2": [
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": true,
  "scales_c": {
   "F3": 6,
   "F2": 10
  }
 },
 {
  "n": 8,
  "formulations_with_witness": [
   "F3",
   "F2"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ],
   "F2": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": true,
  "scales_c": {
   "F3": 8,
   "F2": 8
  }
 },
 {
  "n": 9,
  "formulations_with_witness": [
   "F3",
   "F2"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ],
   "F2": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": true,
  "scales_c": {
   "F3": 6,
   "F2": 6
  }
 },
 {
  "n": 10,
  "formulations_with_witness": [
   "F3",
   "F2"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ],
   "F2": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": true,
  "scales_c": {
   "F3": 10,
   "F2": 10
  }
 },
 {
  "n": 12,
  "formulations_with_witness": [
   "F3"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": null,
  "scales_c": {
   "F3": 24
  }
 },
 {
  "n": 14,
  "formulations_with_witness": [
   "F3"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": null,
  "scales_c": {
   "F3": 16
  }
 },
 {
  "n": 16,
  "formulations_with_witness": [
   "F3"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": null,
  "scales_c": {
   "F3": 12
  }
 },
 {
  "n": 18,
  "formulations_with_witness": [
   "F3"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": null,
  "scales_c": {
   "F3": 28
  }
 },
 {
  "n": 20,
  "formulations_with_witness": [
   "F3"
  ],
  "normalized_swing_vectors_by_direct_enumeration": {
   "F3": [
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    2,
    1
   ]
  },
  "all_match_target": true,
  "pairwise_equal": null,
  "scales_c": {
   "F3": 58
  }
 }
]
```

### Cross-check against the paper's own claim (Section 9)

Section 9 of the manuscript certifies that no weighted majority game realizes psi^n for
6 <= n <= 10. The F1 rows that terminated with a definite verdict are:

- n=6: `INFEASIBLE` -- The problem is infeasible. (HiGHS Status 8: model_status is Infeasible; primal_status is None)

Runs re-taken after the first pass, with the reason for each attempt (from the `reruns` field
of the JSON, in order; each entry supersedes the previous record for that (formulation, n)):

| formulation | n | when | outcome of this attempt | solver/reason recorded | why |
|---|---|---|---|---|---|
| F1 | 20 | 2026-09-14T00:54:17 | BUILD_FAILED |  | wall-clock cap killed the worker during the solve, and the build record was not flushed before the fix; re-taken with the build record flushed first |
| F2 | 18 | 2026-09-14T00:54:28 | BUILD_FAILED |  | wall-clock cap killed the worker during the solve, and the build record was not flushed before the fix; re-taken with the build record flushed first |
| F1 | 20 | 2026-09-14T01:13:03 | TIMEOUT | worker killed at the 690s wall-clock cap while the solver was still running; the model was built (so this is not a build failure) but the solver returned no status of its own | the previous F1 n=20 record was a wall-clock-cap kill during the solve with the build record not yet flushed (fixed); re-taken |
| F2 | 18 | 2026-09-14T01:24:34 | TIMEOUT | worker killed at the 690s wall-clock cap while the solver was still running; the model was built (so this is not a build failure) but the solver returned no status of its own | the previous F2 n=18 record was a wall-clock-cap kill during the solve with the build record not yet flushed (fixed); re-taken |

### Longer-budget reruns (recorded, not spliced)

The rows above are what the common 300s cap reached. Three runs across two instance sizes were
re-run with a per-instance budget far above that cap, to separate a limit of the model from a
limit of the shared budget. These are recorded under `meta.longer_budget_reruns` and are **not**
spliced into `results`: the main table is defined by the common cap, and replacing one of its
cells with a result obtained under a different budget would change what the table means. Where
a rerun also
loosens a bound in the model, the `configuration` column says so, since the two are then not
strictly comparable.

| formulation | n | budget | configuration | outcome | solve | c | spliced into results |
|---|---|---|---|---|---|---|---|
| F2 | 11 | 3600s | the discovery copy of the general monotone model of code/milp_verify.py, which bounds c <= 100000 rather than c <= 100 | OPTIMAL | 25.9 s | 14 | no |
| F2 | 12 | 3600s | the benchmark's own F2 configuration, reused from code/milp_n8.py, which bounds c <= 100 | OPTIMAL | 918.9 s | 20 | no |
| F2 | 12 | 3600s | the discovery copy of the general monotone model of code/milp_verify.py, which bounds c <= 100000 rather than c <= 100 | OPTIMAL | 270.3 s | 20 | no |

Note on the scale `c`: none of the three models carries an objective, so where the outcome is
`FEASIBLE`/`OPTIMAL` the reported `c` is the feasible point the solver happened to reach, not a
minimum. No minimality claim is made anywhere in this file.

## Self-test

```
{
 "F1_unanimity_n6": {
  "outcome": "OPTIMAL",
  "solver_status": "Optimization terminated successfully. (HiGHS Status 7: Optimal)",
  "num_variables": 71,
  "num_constraints": 131,
  "c": 1,
  "verification": {
   "swings_by_direct_enumeration": [
    1,
    1,
    1,
    1,
    1,
    1
   ],
   "gcd_normalized": [
    1,
    1,
    1,
    1,
    1,
    1
   ],
   "target_pattern": [
    1,
    1,
    1,
    1,
    1,
    1
   ],
   "matches_target": true,
   "n_coalitions_enumerated": 64,
   "witness": {
    "w": [
     32,
     1,
     32,
     32,
     32,
     32
    ],
    "q": 161,
    "c": 1
   }
  }
 },
 "F1_unanimity_n8": {
  "outcome": "OPTIMAL",
  "solver_status": "Optimization terminated successfully. (HiGHS Status 7: Optimal)",
  "num_variables": 265,
  "num_constraints": 517,
  "c": 1,
  "verification": {
   "swings_by_direct_enumeration": [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1
   ],
   "gcd_normalized": [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1
   ],
   "target_pattern": [
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1
   ],
   "matches_target": true,
   "n_coalitions_enumerated": 256,
   "witness": {
    "w": [
     1,
     1,
     1,
     1,
     1,
     1,
     1,
     1
    ],
    "q": 1,
    "c": 1
   }
  }
 },
 "F1_unanimity_hand_witness_n6": [
  1,
  1,
  1,
  1,
  1,
  1
 ],
 "F3_enumeration_vs_closed_form_n6": {
  "method": "complement-edge",
  "c": 4,
  "swings": [
   8,
   8,
   8,
   8,
   8,
   4
  ],
  "normalized": [
   2,
   2,
   2,
   2,
   2,
   1
  ],
  "matches_target": true
 }
}
```

The same encoders are run against a target that IS realizable by a weighted majority game: the unanimity vector (1,...,1), realized by w = (1,...,1), q = n. A FEASIBLE verdict there shows the encoding is able to find realizable targets, so a non-FEASIBLE verdict on psi^n is not an artefact of a broken model.

## Nulls and failures (stated plainly)

- **F1 n=6: INFEASIBLE** -- null fields: c. Solver/reason: `The problem is infeasible. (HiGHS Status 8: model_status is Infeasible; primal_status is None)`
- **F1 n=7: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=8: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=9: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=10: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=12: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=14: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=16: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=18: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F1 n=20: TIMEOUT** -- null fields: solve_time_s, c. Solver/reason: `worker killed at the 690s wall-clock cap while the solver was still running; the model was built (so this is not a build failure) but the solver returned no status of its own`
- **F2 n=12: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F2 n=14: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F2 n=16: TIMEOUT** -- null fields: c. Solver/reason: `Time limit reached. (HiGHS Status 13: model_status is Time limit reached; primal_status is None)`
- **F2 n=18: TIMEOUT** -- null fields: solve_time_s, c. Solver/reason: `worker killed at the 690s wall-clock cap while the solver was still running; the model was built (so this is not a build failure) but the solver returned no status of its own`
- **F2 n=20: BUILD_FAILED** -- null fields: solve_time_s, num_variables, num_constraints, c. Solver/reason: `MemoryError while building`

### Where the numbers are absent, and why

- `c` is `null` exactly when the formulation returned no witness (infeasible, timed out, or
  build failed); an infeasible model has no scale to report.
- A `BUILD_FAILED` row has `num_variables`, `num_constraints`, `solve_time_s` and `c` all
  null, because no model reached the solver. Any `build_time_s` shown on such a row is the
  wall time elapsed until the build died, not the cost of a completed build.
- A `TIMEOUT` row has whatever the solver had produced at the limit: `num_variables` and
  `num_constraints` are non-null (the model was built), `solve_time_s` is the wall time spent
  in the solve, and `c` is null because no witness was returned.
- A `TIMEOUT` row with `solve_time_s = null` and `killed_at_wall_cap = true` is one where the
  worker was killed at the outer wall-clock cap while the solver was still running: the model
  was built (so it is not a build failure) but the solver never returned a status of its own,
  so its solve wall time is not known and is reported as `null` rather than guessed.

