"""G8: every number in the Section 10.4 benchmark tables must match the raw JSON.

The benchmark of Section 10.4 is the manuscript's answer to the objection that the
computational methodology "is not sufficiently benchmarked against existing
approaches", so its table is load-bearing evidence and is checked the same way the
c-values and the closed forms are.

Reads `manuscript.md` and `data/benchmark_formulations.json`; deterministic, offline,
exit code 0 = consistent.  The check is deliberately strict about *identity*: each
cell must name the outcome the JSON records for that (formulation, n), and any
runtime printed must equal the JSON value rounded to the manuscript's own precision.

Why this is not redundant with reading the table: the outcome vocabulary of the JSON
(`OPTIMAL`, `TIMEOUT`, `BUILD_FAILED`) is not the vocabulary of the manuscript
(`witness`, `no verdict`), so a rename in the JSON would silently change what the
table claims.  The mapping is asserted here rather than assumed.
"""
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANUSCRIPT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "manuscript.md"
# (an explicit path is accepted so that the self-test can run the same checker over a
#  deliberately corrupted copy; the gate always calls it with no argument)
DATA = ROOT / "data" / "benchmark_formulations.json"

# JSON outcome -> the phrase the manuscript may use for it
OUTCOME_PHRASE = {
    "OPTIMAL": "witness",
    "FEASIBLE": "witness",
    "INFEASIBLE": "infeasible",
    "TIMEOUT": "no verdict",
    "BUILD_FAILED": "build failed",
}

# formulations whose columns the outcome table carries, in order
COLS = ["F1", "F2", "F3"]
SIZE_NS = [6, 10, 14, 18, 20]


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def section(text, heading, nxt):
    i = text.index(heading)
    j = text.index(nxt, i)
    return text[i:j]


def parse_pipe_rows(block):
    rows = []
    for line in block.splitlines():
        line = norm(line)
        if not line.startswith("|"):
            continue
        cells = [norm(c) for c in line.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in cells):
            continue  # separator
        rows.append(cells)
    return rows


def num_in(cell):
    """The first decimal number in a cell, as a float, or None."""
    m = re.search(r"(\d+(?:\.\d+)?)", cell)
    return float(m.group(1)) if m else None


def agrees(cell, truth):
    """True when the number printed in `cell` is `truth` rounded to the precision
    actually printed there.  This is the honest rule for a reported measurement: the
    manuscript may print 43.5 s for 43.4669 s, or 0.06 s for 0.0621 s, and both are
    faithful; printing 43.4 would not be."""
    printed = num_in(cell)
    if printed is None:
        return False
    decimals = len(re.search(r"(\d+)\.(\d+)", cell).group(2)) if re.search(r"(\d+)\.(\d+)", cell) else 0
    return abs(printed - round(truth, decimals)) < 1e-9


def main():
    fails = []
    notes = []

    md = io.open(MANUSCRIPT, encoding="utf-8").read()
    js = json.load(io.open(DATA, encoding="utf-8"))
    rows = {(r["formulation"], r["n"]): r for r in js["results"]}

    sec = section(md, "### 10.4 Benchmark", "### 10.5 ")

    # ---- the two tables in the section -------------------------------------
    blocks = sec.split("Model sizes,")
    if len(blocks) != 2:
        print("[FAIL] could not split the section into the outcome table and the size table")
        return 1
    outcome_rows = parse_pipe_rows(blocks[0])
    size_rows = parse_pipe_rows(blocks[1])
    if not outcome_rows or not size_rows:
        print("[FAIL] one of the two tables did not parse")
        return 1

    # ---- outcome + runtime table -------------------------------------------
    checked = 0
    for cells in outcome_rows[1:]:  # skip the header row
        if len(cells) != 1 + len(COLS):
            fails.append("outcome row has %d cells, expected %d: %r" % (len(cells), 1 + len(COLS), cells))
            continue
        n = int(cells[0])
        for k, f in enumerate(COLS):
            cell = cells[1 + k]
            rec = rows.get((f, n))
            if rec is None:
                fails.append("no JSON record for %s at n = %d" % (f, n))
                continue
            want = OUTCOME_PHRASE[rec["outcome"]]
            if want not in cell:
                fails.append("%s n=%d: manuscript says %r, JSON outcome %s wants %r"
                             % (f, n, cell, rec["outcome"], want))
                continue
            # A cell that prints a time must print a time the JSON supports; a cell
            # that prints none is checked against the manuscript's stated policy,
            # which is to give a time exactly when a verdict was reached.
            got = num_in(cell)
            if got is not None:
                if rec["solve_time_s"] is None:
                    fails.append("%s n=%d: manuscript prints a time (%r) but the JSON records none"
                                 % (f, n, cell))
                elif not agrees(cell, rec["solve_time_s"]):
                    fails.append("%s n=%d: cell prints %r, JSON is %.4f"
                                 % (f, n, cell, rec["solve_time_s"]))
            elif rec["outcome"] in ("OPTIMAL", "FEASIBLE", "INFEASIBLE"):
                fails.append("%s n=%d: a verdict was reached (%s, %.2f s) but the cell prints no time: %r"
                             % (f, n, rec["outcome"], rec["solve_time_s"] or 0.0, cell))
            checked += 1

    # ---- model-size table ---------------------------------------------------
    size_checked = 0
    by_form = {}
    for cells in size_rows[1:]:
        if cells[0] not in ("F1", "F2", "F3"):
            continue
        by_form[cells[0]] = cells[1:]
    for f in COLS:
        if f not in by_form:
            fails.append("size table has no row for %s" % f)
            continue
        vals = by_form[f]
        if len(vals) != len(SIZE_NS):
            fails.append("size row %s has %d entries, expected %d" % (f, len(vals), len(SIZE_NS)))
            continue
        for k, n in enumerate(SIZE_NS):
            rec = rows.get((f, n))
            if rec is None:
                fails.append("no JSON record for %s at n = %d" % (f, n))
                continue
            want = rec["num_variables"]
            got = num_in(vals[k])
            if want is None:
                # the manuscript uses an em dash placeholder; it must not print a number
                if got is not None:
                    fails.append("size %s n=%d prints %r but the JSON has no size" % (f, n, vals[k]))
            elif got is None or int(round(got)) != int(want):
                fails.append("size %s n=%d: table has %r, JSON has %s" % (f, n, vals[k], want))
            size_checked += 1

    # ---- a few prose figures that carry the table's message ------------------
    prose = [
        ("at most 2.6 s", "F2 n=10 solve time 2.63 s rounds to 2.6"),
        ("0.03 s at n = 6", "F3 n=6 solve time 0.0312 s rounds to 0.03"),
        ("2.14 s at n = 20", "F3 n=20 solve time 2.1427 s rounds to 2.14"),
        ("96 variables at n = 6", "F3 n=6 has 96 variables"),
        ("4,751 at n = 20", "F3 n=20 has 4751 variables"),
        ("262,145-variable model built at n = 18", "F2 n=18 has 262145 variables"),
    ]
    for needle, why in prose:
        if needle not in sec:
            fails.append("prose figure missing from Section 10.4: %r (%s)" % (needle, why))
        else:
            notes.append(why)

    # cross-check the commas by hand: 4,751 and 262,145 must equal the JSON ints
    for text_form, key in (("4,751", ("F3", 20)), ("262,145", ("F2", 18))):
        if text_form.replace(",", "") != str(rows[key]["num_variables"]):
            fails.append("%s does not equal the JSON value for %s" % (text_form, key))

    # ---- the longer-budget reruns quoted in the closing paragraph -------------
    # The table's frontier is a property of the shared cap, and the paragraph that says
    # so quotes three runs taken with a per-instance budget.  Those runs do not live in
    # `results` (they are not rows of the table), so they are guarded separately: each
    # quoted time is derived from `meta.longer_budget_reruns` rather than written here, so
    # that a re-measurement cannot leave the prose behind.
    lbr = {(e.get("configuration_key"), e.get("n")): e
           for e in (js["meta"].get("longer_budget_reruns") or [])}
    # (which copy of the model, n, decimals the manuscript prints)
    for key, n, dp in [("milp_verify", 11, 1), ("benchmark", 12, 0), ("milp_verify", 12, 0)]:
        e = lbr.get((key, n))
        if e is None:
            fails.append("meta.longer_budget_reruns has no entry for the %s copy at n=%d" % (key, n))
            continue
        if e.get("solve_time_s") is None:
            fails.append("the %s copy at n=%d records no solve time" % (key, n))
            continue
        if e.get("configuration_key") == "benchmark" and rows.get(("F2", n)) is None:
            fails.append("the benchmark's own configuration at n=%d has no row in results" % n)
        printed = "%.*f" % (dp, e["solve_time_s"])
        if printed not in sec:
            fails.append("Section 10.4 does not quote the %s copy at n=%d as %s s (JSON: %.4f)"
                         % (key, n, printed, e["solve_time_s"]))
        else:
            notes.append("longer-budget rerun: %s copy, n=%d, quoted as %s s" % (key, n, printed))

    # the paragraph's own claim, that the two bounds reached the same scale
    n12 = [lbr.get(("benchmark", 12)), lbr.get(("milp_verify", 12))]
    if all(e is not None for e in n12):
        if n12[0].get("c") != n12[1].get("c"):
            fails.append("the two n=12 configurations reached different scales (%s and %s), so the "
                         "paragraph's 'same scale' claim is false"
                         % (n12[0].get("c"), n12[1].get("c")))
        elif "c = %d" % n12[0]["c"] not in sec:
            fails.append("Section 10.4 does not quote the shared scale c = %d reached at n = 12"
                         % n12[0]["c"])
        else:
            notes.append("the two n=12 configurations agree on the scale c = %d, as quoted"
                         % n12[0]["c"])

    print("[INFO] outcome/runtime cells checked: %d" % checked)
    print("[INFO] size cells checked: %d" % size_checked)
    print("[INFO] prose figures confirmed: %d" % len(notes))
    if fails:
        for f in fails:
            print("[FAIL] %s" % f)
        print("BENCHMARK MANUSCRIPT CHECK: FAIL (%d)" % len(fails))
        return 1
    print("BENCHMARK MANUSCRIPT CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
