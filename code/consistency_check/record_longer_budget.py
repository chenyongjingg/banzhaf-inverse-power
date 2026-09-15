"""Collect the longer-budget reruns into the benchmark JSON, without touching the table.

Section 10.4 states its frontier under one common 300 s cap, and the table records what
that cap reached.  Three measurements were then taken with a per-instance budget far
above the cap, to find out whether a "no verdict" row says something about the model or
only about the shared cap:

    n = 11  the discovery copy of the model, c <= 100000   25.9 s   c = 14
    n = 12  the discovery copy of the model, c <= 100000  270.3 s   c = 20
    n = 12  the benchmark's own F2 configuration, c <= 100  918.9 s   c = 20

The third is why the configuration is recorded per entry: the same model with a tighter
bound on `c` reached the same feasible point (`c = 20`) at a very different time, so a
row is only meaningful together with the bound it was run under.

Those reruns must NOT be spliced into `results`: a row of the Section 10.4 table means
"what the common 300 s cap reached", and replacing it with a 3600 s result would change
the definition the table is read under.  So they are recorded here, under
`meta.longer_budget_reruns`, with `spliced_into_results: false` on every entry, and the
companion markdown renders them in their own subsection.

This script parses the two logs rather than re-running anything, so it is cheap and
idempotent: run it again after a new measurement and the block is rebuilt from the logs.

    python code/consistency_check/record_longer_budget.py [--check]

`--check` reports whether the recorded numbers still match the logs and exits non-zero if
not, without writing.  It compares content, not filesystem metadata: the `when` field of a
Section 7 entry is derived from that log's mtime, so it is excluded from the comparison --
otherwise unpacking the archive, which rewrites mtimes, would report STALE on a package
whose numbers all still match.  See the note in `main` for the measurement.
"""
import json
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODE = HERE.parent
ROOT = CODE.parent
sys.path.insert(0, str(CODE))

JSON_PATH = ROOT / "data" / "benchmark_formulations.json"
MD_PATH = CODE / "benchmark_formulations_results.md"
F2_LOG = HERE / "f2_config_rerun.log"
SEC7_LOG = HERE / "sec7_rerun.log"

# the benchmark's own vocabulary, so the block can be read next to `results`
OUTCOME_BY_STATUS = {"OPTIMAL": "OPTIMAL", "FEASIBLE": "FEASIBLE"}


def parse_f2_log(text):
    """The benchmark-configuration rerun log: a header, then one JSON object, then a wall line."""
    out = {}
    for m in re.finditer(r"^=== n=(\d+) budget=(\d+)s at ([0-9T:-]+) ===$(.*?)^--- wall ([0-9.]+)s ---$",
                         text, re.S | re.M):
        n, budget, when, body, wall = int(m.group(1)), int(m.group(2)), m.group(3), m.group(4), float(m.group(5))
        j = json.loads(body[body.index("{"):body.rindex("}") + 1])
        out[(n, "benchmark")] = {
            "formulation": "F2",
            "n": n,
            "configuration": ("the benchmark's own F2 configuration, reused from code/milp_n8.py, "
                              "which bounds c <= 100"),
            "configuration_key": "benchmark",
            "command": "python code/consistency_check/rerun_f2_config.py %d %d" % (n, budget),
            "budget_s": budget,
            "outcome": j.get("outcome"),
            "solve_time_s": j.get("solve_time_s"),
            "wall_time_s": j.get("wall_time_s") if j.get("wall_time_s") is not None else wall,
            "c": j.get("c"),
            "solver_status": j.get("solver_status"),
            "when": when,
            "spliced_into_results": False,
            "source_log": str(F2_LOG.relative_to(ROOT)).replace("\\", "/"),
        }
    return out


def parse_sec7_log(text):
    """The longer-budget rerun of the Section 7 instances (code/milp_verify.py)."""
    out = {}
    for m in re.finditer(r"^=== n=(\d+) ===\n(.*?)(?=^=== |\Z)", text, re.S | re.M):
        n, body = int(m.group(1)), m.group(2)
        sm = re.search(r"status=(\d+) msg=(.*?) time=([0-9.]+)s", body)
        cm = re.search(r"^\s+c=(\d+)$", body, re.M)
        if not sm:
            continue
        msg, secs = sm.group(2).strip(), float(sm.group(3))
        status = int(sm.group(1))
        if status != 0:
            outcome = "TIMEOUT"
        elif "Optimal" in msg:
            outcome = "OPTIMAL"
        elif "Feasible" in msg:
            outcome = "FEASIBLE"
        else:
            outcome = "UNKNOWN"
        out[(n, "milp_verify")] = {
            "formulation": "F2",
            "n": n,
            "configuration": ("the discovery copy of the general monotone model of code/milp_verify.py, "
                              "which bounds c <= 100000 rather than c <= 100"),
            "configuration_key": "milp_verify",
            "command": "python code/milp_verify.py %d 3600" % n,
            "budget_s": 3600,
            "outcome": outcome,
            "solve_time_s": secs,
            "wall_time_s": None,
            "c": int(cm.group(1)) if cm else None,
            "solver_status": msg,
            "when": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(
                SEC7_LOG.stat().st_mtime)) if SEC7_LOG.exists() else None,
            "spliced_into_results": False,
            "source_log": str(SEC7_LOG.relative_to(ROOT)).replace("\\", "/"),
        }
    return out


def collect():
    entries = {}
    if F2_LOG.exists():
        entries.update(parse_f2_log(F2_LOG.read_text(encoding="utf-8", errors="replace")))
    if SEC7_LOG.exists():
        entries.update(parse_sec7_log(SEC7_LOG.read_text(encoding="utf-8", errors="replace")))
    return [entries[k] for k in sorted(entries, key=lambda t: (t[0], t[1]))]


def main():
    check = "--check" in sys.argv
    entries = collect()
    if not entries:
        print("[FAIL] no longer-budget rerun found in either log")
        return 1
    payload = json.load(open(JSON_PATH, encoding="utf-8"))

    # The recorded block must never disagree with `results` about whether a row was
    # replaced: this block exists precisely because it does not replace anything.  Only a
    # rerun of the benchmark's own configuration has a row to stay clear of; the
    # discovery copy was also run at sizes the benchmark never visited (n = 11).
    rows = {(r["formulation"], r["n"]): r for r in payload["results"]}
    for e in entries:
        r = rows.get((e["formulation"], e["n"]))
        if r is None and e.get("configuration_key") == "benchmark":
            print("[FAIL] the benchmark's own configuration at %s n=%d has no row in results"
                  % (e["formulation"], e["n"]))
            return 1
        if e["spliced_into_results"]:
            print("[FAIL] an entry claims to be spliced; this block holds non-spliced reruns")
            return 1
        if e["budget_s"] <= payload["meta"]["solver_time_limit_s"]:
            print("[FAIL] %s n=%d budget %ds does not exceed the common cap %ds"
                  % (e["formulation"], e["n"], e["budget_s"], payload["meta"]["solver_time_limit_s"]))
            return 1

    if check:
        # `when` on a Section 7 entry is derived from the LOG FILE'S MTIME (see
        # parse_sec7_log).  An mtime is filesystem metadata, not content: unpacking the
        # shipped archive rewrites it, so a comparison that includes it reports STALE on a
        # fresh extraction while every number still matches.  Measured on the shipped
        # package: with the log and the JSON byte-identical to the tree's, a copy's
        # mtime alone turned MATCHES THE LOGS into STALE, and restoring only the mtime --
        # content untouched -- turned it back.  The field is still recorded, because it is
        # useful provenance, but --check compares substance.
        #
        # Only the Section 7 entries are exempt.  An F2 entry's `when` is parsed out of
        # the log's own text ("=== n=.. budget=..s at <ISO> ==="), so it is content and is
        # still compared.
        def comparable(e):
            e = dict(e)
            if e.get("configuration_key") == "milp_verify":
                e.pop("when", None)
            return e

        same = ([comparable(x) for x in payload["meta"].get("longer_budget_reruns", [])]
                == [comparable(x) for x in entries])
        print("LONGER-BUDGET RECORD: %s" % ("MATCHES THE LOGS" if same else "STALE"))
        return 0 if same else 1

    payload["meta"]["longer_budget_reruns"] = entries
    json.dump(payload, open(JSON_PATH, "w", encoding="utf-8"), indent=1, default=str)

    import benchmark_formulations as bf
    MD_PATH.write_text(bf.render_markdown(payload), encoding="utf-8")

    for e in entries:
        print("  %s n=%-3d budget %ds  %-9s solve=%-8s c=%s"
              % (e["formulation"], e["n"], e["budget_s"], e["outcome"],
                 ("%.1f s" % e["solve_time_s"]) if e["solve_time_s"] else "-", e["c"]))
    print("recorded %d longer-budget rerun(s) in meta.longer_budget_reruns; results untouched"
          % len(entries))
    print("re-rendered %s" % MD_PATH.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
