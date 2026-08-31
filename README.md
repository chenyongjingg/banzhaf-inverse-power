# Inverse Banzhaf Power by Exact Computation

Reproducible code and data for

> **Prescribed Banzhaf Power by Exact Computation: Closed-Form Realizations and Certified Weighted Obstructions**

Yongjin Chen, Shi Jin, and Songze Zhu — School of Public Security Management, People's Public Security University of China.

*Manuscript under review at Computers & Operations Research.*

## What this is

The inverse (Banzhaf) power index problem asks: given a desired distribution of voting power, does a voting rule realize it, and can one be constructed — or certified not to exist? This repository holds the exact, fully reproducible computation behind the paper's two-sided answer.

- **Constructive side.** A single parametric family of simple games (the W-family) with an exact closed-form swing formula yields explicit realizing games for every n ≥ 6, resolving Kurz's Conjecture 16.
- **Obstruction side.** A sharpened swap/block rigidity condition drives a CP-SAT certification that no *weighted majority* game realizes the egalitarian benchmark ψⁿ = (2,…,2,1)/(2n−1) for 6 ≤ n ≤ 10, at a conclusive weight bound.
- **Case study.** The methodology is applied to the historical weighted Council of the European Union (EEC-6/9/10/12, EU-15).

Every numerical claim in the manuscript is reproduced by a script in this repository against the machine-readable dataset `data/appendix-data-n80.json` (the authoritative, swing-re-verified dataset covering n = 6..80).

## Repository layout

| Path | Contents |
|---|---|
| `manuscript.pdf` / `manuscript.md` / `manuscript.tex` | The manuscript (PDF, Markdown source, LaTeX) |
| `mathfix.lua` | Pandoc Lua filter used to typeset the math (Unicode → LaTeX) |
| `source_manifest.json` | The 13 references (E001–E013), all existence-verified |
| `code/` | 88 experiment scripts (constructions, MILP/CP-SAT, verification) |
| `q3/` | Weighted-infeasibility experiments (§9) |
| `data/` | Machine-readable result datasets (see below) |
| `scripts/` | `case_study_eu.py`, `verify_appendix_manuscript.py`, `renumber_propcor.py` |
| `graphical_abstract.*` | Graphical abstract (PDF + PNG + generator script) |

## Reproducing the claims

- **§3–5 closed-form constructions (W-family).** `python code/reproduce_all.py` prints the swing
  vectors β(v_{G_n}) ∝ (2,…,2,1) for the representative constructions; every c-value in §10.1 /
  Proposition 12 / §7 tables is stored in and cross-checked against `data/appendix-data-n80.json`.
- **§9 weighted infeasibility (ψⁿ not realizable by a weighted majority game, n = 6..10).**
  `python q3/conj15_feas.py` (n ≤ 8), `python q3/conj15_feas2.py` (n = 9, 10; enhanced model with
  (M′) mirror constraints). Weight bound W = 2^(n−1) makes INFEASIBLE conclusive. Run scripts
  `q3/run_n8_cont.sh`, `q3/run_n9_enh.sh`, `q3/run_n10_enh.sh`.
- **§10.2 runtimes.** Tables report measured solver runtimes; the corresponding scripts are in
  `code/` (e.g. `cpsat_wfamily.py`, `milp_*.py`) and `q3/` for the obstruction models.
- **§12 EU Council case study (EEC-6/9/10/12, EU-15).** `python scripts/case_study_eu.py`
  reproduces every §12 number.
- **Consistency audit.** `python scripts/verify_appendix_manuscript.py` cross-checks every c-value
  claimed in the manuscript (tables and narrative) against `data/appendix-data-n80.json`.
  Deterministic, offline, exit code 0 = all consistent.

## Rebuilding the manuscript PDF

```
pandoc manuscript.md --lua-filter mathfix.lua -s \
  --pdf-engine=xelatex -V mainfont="Latin Modern Roman" -o manuscript.tex
xelatex manuscript.tex
```

(The title and author block live in `manuscript.md` as raw LaTeX.) The committed PDF compiles with
0 errors, 0 Overfull h-boxes, and 0 missing-character warnings.

## Data files

| File | Role |
|---|---|
| `data/appendix-data-n80.json` | **Authoritative** dataset: minimal c and an explicit realizing graph for every n = 6..80, re-verified by direct swing enumeration |
| `data/appendix-data.json` | Earlier-generation dataset (superseded by n80) |
| `data/appendix-solutions.md` | Human-readable appendix of realizing constructions |

## Dependencies

Python 3 (stdlib only for `reproduce_all.py` / `verify_appendix_manuscript.py`), `ortools`
(CP-SAT for the obstruction and W-family MILP), `scipy`/HiGHS (some MILP scripts), and
pandoc + xelatex (LaTeX rebuild). All scripts are self-contained and deterministic.
