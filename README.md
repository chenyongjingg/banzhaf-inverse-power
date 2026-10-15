# Inverse Banzhaf power: datasets, models, and run logs

Data-and-code companion to two papers on prescribing the Penrose–Banzhaf power of simple games.
Neither manuscript is distributed here (see **What is not here**).

**The two papers.**

- *Closed-form games for prescribed Banzhaf power: congruence conditions and a unified W-family* —
  Yongjin Chen, Ziying Xue, Yukai Zhuo, Songze Zhu (corresponding).
- *Certified obstructions to prescribed Banzhaf power in weighted majority games* —
  Yongjin Chen, Ziying Xue, Songze Zhu (corresponding).

All four authors are at the People's Public Security University of China, Beijing 100038, China: Yongjin Chen
and Songze Zhu, School of Public Security Management; Ziying Xue, School of Investigation; Yukai Zhuo,
School of Information Network Security. Corresponding author: 20196846@ppsuc.edu.cn

Below, *the closed-form paper* and *the obstructions paper* refer to these two, in that order.

This repository holds the machine-readable datasets and every script that reproduces a numerical claim
in them. It is self-contained and deterministic: no step requires network access.

## Layout

| Path | Contents |
|---|---|
| `graphical_abstract.pdf` / `.png` / `.py` | Graphical abstract and the script that draws it |
| `source_manifest.json` | The 18 sources consulted for this project (E001–E018), each with a verification record. A project-level evidence list, not the bibliography of either paper, which is compiled separately |
| `code/` | 87 Python scripts — constructions, MILP/CP-SAT models, verification, the formulation benchmark |
| `q3/` | Weighted-infeasibility experiments (§3 of the obstructions paper) and their server run logs |
| `q3/recheck/` | Raw logs of an independent re-run of the small-scale certificates on a second machine, including the runs that went wrong and the corrections that superseded them |
| `data/` | Result datasets (see below) |
| `scripts/` | The script that reproduces the EU Council case study, and its captured output |

## Reproducing the claims

Every numerical claim in the two papers is checked against `data/appendix-data-n80.json`, the
authoritative dataset covering n = 6..80 whose swing vectors were re-verified by direct enumeration.

- **Closed-form constructions (W-family), the closed-form paper.** `python code/reproduce_all.py`
  prints the swing vectors β(v_{G_n}) ∝ (2,…,2,1); every c-value that paper tabulates is stored in and
  cross-checked against `data/appendix-data-n80.json`.
- **Theorem 2 (the target family ψⁿ(a,b)), the closed-form paper.** `python
  code/general_target_family.py --nmax 18 --amax 4` builds each realizing graph by Havel–Hakimi and
  confirms the swing vector by enumerating all 2ⁿ coalitions. The script asserts the exhaustive-search
  bound before searching, so negative entries in its coverage table are complete for n ≤ 120 rather
  than artifacts of a truncated loop.
- **Weighted infeasibility (ψⁿ is not realizable by a weighted majority game, n = 6..10), §3 of the
  obstructions paper.** `python q3/conj15_feas.py` (n ≤ 8) and `python q3/conj15_feas2.py` (n = 9, 10;
  the enhanced model with (M′) mirror constraints). The weight bound W = 2^(n−1) makes INFEASIBLE
  conclusive. Run scripts and server logs are in `q3/`. The small-scale certificates were also re-run
  independently on a second machine; the unedited logs, the two instrument errors those runs exposed,
  and the runs that superseded them are in `q3/recheck/`.
- **Formulation benchmark, §4.4 of the obstructions paper.** `python code/benchmark_formulations.py`
  runs the three formulations (direct weight-space, general monotone, compressed W-family) on n = 6..20
  under one 300 s solver limit and writes `data/benchmark_formulations.json`. The witness check is
  independent of the formulations: each solution is rebuilt and its swings recounted by enumerating all
  2ⁿ coalitions.
- **EU Council case study (EEC-6/9/10/12, EU-15), §6 of the obstructions paper.**
  `python scripts/case_study_eu.py` reproduces every number there; captured output in
  `scripts/case_study_eu_output.txt`.

## Verification scripts

| Script | Purpose |
|---|---|
| `code/reproduce_all.py` | the appendix chain check: for every n = 6..80, the shipped data satisfy Pairs(F) ⊆ G and deg_G(i) + r_i = D with the special player c/2 above it, whereupon (U) returns c·(2,…,2,1) |
| `code/general_target_family.py` | Theorem 2: builds each realizing graph by Havel–Hakimi and confirms the swing vector by enumerating all 2ⁿ coalitions |
| `scripts/case_study_eu.py` | reproduces every EU Council case-study number |

These are offline and exit non-zero on any mismatch. Two further checkers, which cross-read the
earlier draft's own prose and tables, were removed with that draft (see **What is not here**); the
claim-to-script mapping above is the part that does not depend on any manuscript text.

## Data files

| File | Role |
|---|---|
| `data/appendix-data-n80.json` | **Authoritative**: an explicit realizing graph and a scale c for every n = 6..80, each re-verified against ψⁿ and the monotonicity condition Pairs(F) ⊆ G (`code/reproduce_all.py`). Minimality of c is certified for n = 6..10 only; for larger n it is an upper bound, and minimality is an open problem (open problem 1 in §9 of the closed-form paper) |
| `data/appendix-data.json` | Earlier-generation dataset, superseded by the n80 file |
| `data/appendix-solutions.md` | Human-readable appendix of realizing constructions |
| `data/benchmark_formulations.json` | Every field of the three-formulation benchmark (§4.4 of the obstructions paper) |

## Dependencies

Python 3 (the standard library is enough for `reproduce_all.py`), `ortools` for the CP-SAT
obstruction and W-family models, and `scipy`/HiGHS for some MILP scripts.

## What is not here

**The manuscripts.** Neither paper's text is distributed here. The repository carries the datasets,
models, and run logs behind the numerical claims, not the claims as written.

**The pre-split draft.** Earlier revisions of this repository shipped a single combined manuscript
(`manuscript.md` / `.tex` / `.pdf`), together with the tooling that existed only to build it
(`mathfix.lua` and six one-shot editing scripts under `code/`) and the two checkers that read it
(`scripts/verify_appendix_manuscript.py`, `scripts/verify_benchmark_manuscript.py`). That draft was
written before the work was divided into the two papers above, and it is superseded: it predates the
current presentation and still carries at least one number that was afterwards corrected — it reports
`3.85×` for the EU Council power spread, where `1.67×` (EEC-6) is the true lower endpoint of the
certified range. Those files were removed from the tree in September 2026; **they remain in the
repository's earlier commits**, so anything reached through the history should be read as historical
and not as the current version of the work. The datasets, models, and run logs that back the
numerical claims are unchanged and remain here.
