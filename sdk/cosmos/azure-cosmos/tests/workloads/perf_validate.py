# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Post-run checks for workload quality, continuity, logs, and backend counters.

Check success/error totals and required backend labels per observed operation;
compare elapsed/window times; scan available cell logs for upsert warnings;
and check backend labels against the recorded counters. A failed check makes
the exit status nonzero. Overrides can permit weaker log/counter evidence.

Expected-workload lists catch absent cells; process completion records reconcile
persisted summary totals. Continuity and warning checks alone cannot establish
completeness. Backend counters do not attribute each service operation to an engine.

Run perf_validate.py with --run-id, --prefix, and --log-dir to select the
result rows and cell logs. Results-account configuration is required.
"""

import argparse
import math
import glob
import os
import re
import sys
from perf_results import EXPECTED_RUNTIME, summary_rows, window_key

try:
    from azure.cosmos import CosmosClient
except ImportError:
    print("ERROR: azure-cosmos is required (pip install azure-cosmos).", file=sys.stderr)
    sys.exit(2)


# Allow the larger of 60 seconds and half a report interval when checking gaps.
# This timing tolerance can hide smaller gaps and does not rule out false alarms.
def _gap_tolerance_s(report_interval_s: float) -> float:
    return max(60.0, 0.5 * report_interval_s)


def _run_id_of(workload_id: str) -> str:
    # workload_id = lat-{op}-{backend}-r{r}-{YYYYMMDD-HHMMSS}. The backend can
    # itself contain a dash (core-python), so the run id is always the LAST two
    # dash-separated fields joined -- never positional from the front.
    parts = workload_id.split("-")
    if len(parts) < 2:
        return ""
    return parts[-2] + "-" + parts[-1]


def _connect():
    uri = os.environ.get("RESULTS_COSMOS_URI")
    key = os.environ.get("RESULTS_COSMOS_KEY")
    db = os.environ.get("RESULTS_COSMOS_DATABASE", "perfdb")
    cont = os.environ.get("RESULTS_COSMOS_CONTAINER", "perfresults-v2")
    if not uri or not key:
        print(
            "ERROR: RESULTS_COSMOS_URI / RESULTS_COSMOS_KEY not set. "
            "`source ./perf_env.sh` (after exporting the key) first.",
            file=sys.stderr,
        )
        sys.exit(2)
    return CosmosClient(uri, key).get_database_client(db).get_container_client(cont)


def _latest_run_id(container, prefix: str) -> str:
    ids = list(
        container.query_items(
            "SELECT VALUE c.workload_id FROM c WHERE STARTSWITH(c.workload_id, @p)",
            parameters=[{"name": "@p", "value": prefix}],
            enable_cross_partition_query=True,
        )
    )
    run_ids = {_run_id_of(i) for i in ids if i}
    run_ids.discard("")
    if not run_ids:
        return ""
    # YYYYMMDD-HHMMSS sorts correctly as a plain string.
    return max(run_ids)


# A latency row is only trustworthy if the cell actually did work. An empty or
# nearly-empty cell, or one whose ops mostly errored, can still report tidy-
# looking percentiles (a count=0 window leaves the latency fields at 0.0). We
# refuse to trust any cell whose error fraction exceeds this -- 1% of ops.
_MAX_ERROR_FRACTION = 0.01


def check_quality(container, prefix: str, run_id: str, required_backends):
    """Every cell must have real work (count > 0) and near-zero errors, and every
    operation must have all requested backends present, before any latency number
    is believed. This runs first: a "fast" p50 means nothing if the cell did nothing.

    We do not require backends to have equal counts. We just need every requested
    side to do real, low-error work.
    """
    rows = list(
        container.query_items(
            "SELECT * "
            "FROM c WHERE STARTSWITH(c.workload_id, @prefix) AND ENDSWITH(c.workload_id, @run_id)",
            parameters=[
                {"name": "@prefix", "value": prefix},
                {"name": "@run_id", "value": run_id},
            ],
            enable_cross_partition_query=True,
        )
    )
    if not rows:
        return False, [f"  (no result rows found for run id {run_id})"]

    # Aggregate per cell (workload_id), and remember which op/backend it is.
    agg = {}
    for r in summary_rows(rows):
        wid = (r["workload_id"], r["operation"])
        a = agg.setdefault(
            wid,
            {
                "op": r.get("operation", "?"),
                "backend": r.get("config_backend", "?"),
                "count": 0,
                "errors": 0,
            },
        )
        a["count"] += int(r.get("count", 0) or 0)
        a["errors"] += int(r.get("errors", 0) or 0)

    lines = []
    all_ok = bool(agg)
    backends_by_op = {}
    for wid in sorted(agg):
        a = agg[wid]
        backends_by_op.setdefault(a["op"], set()).add(a["backend"])
        total = a["count"] + a["errors"]
        err_frac = (a["errors"] / total) if total else 1.0
        cell_ok = a["count"] > 0 and err_frac <= _MAX_ERROR_FRACTION
        all_ok = all_ok and cell_ok
        flag = "OK " if cell_ok else "BAD"
        lines.append(
            f"  [{flag}] {wid}: count={a['count']} errors={a['errors']} "
            f"err_frac={err_frac*100:.2f}%"
        )

    required = set(required_backends)
    # Every operation must have been measured on every backend the caller asked
    # for. The default remains the two-sided Rust-vs-core comparison, while an
    # explicitly selected Rust-only baseline is still a valid path proof.
    for op in sorted(backends_by_op):
        present = backends_by_op[op]
        missing = required - present
        if missing:
            all_ok = False
            lines.append(
                f"  [BAD] op={op}: missing required backend(s) {sorted(missing)} "
                f"(have {sorted(present)})"
            )
    return all_ok, lines


def check_continuity(container, prefix: str, run_id: str, report_interval_s: float):
    """Return (ok, lines) for the row-continuity check across all cells in `run_id`."""
    rows = list(
        container.query_items(
            "SELECT * FROM c "
            "WHERE STARTSWITH(c.workload_id, @prefix) AND ENDSWITH(c.workload_id, @run_id)",
            parameters=[
                {"name": "@prefix", "value": prefix},
                {"name": "@run_id", "value": run_id},
            ],
            enable_cross_partition_query=True,
        )
    )
    lines = []
    if not rows:
        return False, [f"  (no result rows found for run id {run_id})"]

    # One results row may carry several operations? No -- one row per op per
    # window, all sharing a workload_id (which is per op+backend already). Group
    # strictly by workload_id so each timeline is a single process.
    cells = {}
    for r in summary_rows(rows):
        cells.setdefault((r["workload_id"], r.get("process_id")), {})[window_key(r)] = r

    tol = _gap_tolerance_s(report_interval_s)
    all_ok = bool(cells)
    for wid in sorted(cells):
        recs = sorted(cells[wid].values(), key=lambda x: x.get("elapsed_seconds", 0.0))
        sum_window = sum(float(x.get("window_seconds", 0.0)) for x in recs)
        max_elapsed = max(float(x.get("elapsed_seconds", 0.0)) for x in recs)
        holes = []
        prev = None
        for x in recs:
            el = float(x.get("elapsed_seconds", 0.0))
            wl = float(x.get("window_seconds", 0.0))
            if prev is not None:
                jump = el - prev
                # A healthy jump equals THIS row's window. A bigger jump means
                # one or more windows between prev and here were never written.
                if jump - wl > tol:
                    missing = round((jump - wl) / max(report_interval_s, 1.0), 1)
                    holes.append(
                        f"        hole at elapsed {prev:.0f}s -> {el:.0f}s "
                        f"(~{missing} window(s) missing)"
                    )
            prev = el
        coverage_gap = max_elapsed - sum_window
        cell_ok = not holes and coverage_gap <= tol
        all_ok = all_ok and cell_ok
        flag = "OK " if cell_ok else "BAD"
        lines.append(
            f"  [{flag}] {wid}: rows={len(recs)} "
            f"covered={sum_window:.0f}s span={max_elapsed:.0f}s "
            f"gap={coverage_gap:.0f}s"
        )
        lines.extend(holes)
    return all_ok, lines


def check_warnings(log_dir: str, strict: bool = True):
    """Scan available .log files for the two reporter-upsert warning patterns.

    Missing log arguments, directories, or files fail in strict mode and may be
    allowed otherwise. Unreadable files fail even when strict=False.
    A clean scan does not prove that all expected logs or result writes exist.
    """
    def _missing(reason: str):
        """Report absent evidence: a failure in strict mode, a note otherwise."""
        label = "BAD" if strict else "OK "
        suffix = "" if strict else " (allowed: --allow-missing-logs)"
        return not strict, [f"  [{label}] no log evidence: {reason}{suffix}"]

    if not log_dir:
        return _missing("no --log-dir given")
    if not os.path.isdir(log_dir):
        return _missing(f"log dir not found: {log_dir}")
    pat = re.compile(r"PerfReporter.*(?:failed|incomplete|still alive)|Invalid request-(?:charge|duration) measurement")
    lines = []
    total = 0
    unreadable = 0
    scanned = 0
    for path in sorted(glob.glob(os.path.join(log_dir, "*.log"))):
        n = 0
        try:
            with open(path, "r", errors="replace") as fh:
                for ln in fh:
                    if pat.search(ln):
                        n += 1
        except OSError as e:
            unreadable += 1
            lines.append(f"  [BAD] could not read {path}: {e}")
            continue
        scanned += 1
        if n:
            total += n
            lines.append(f"  [BAD] {os.path.basename(path)}: {n} dropped-write warning(s)")
    if scanned == 0 and unreadable == 0:
        return _missing(f"no *.log files in {log_dir}")
    if total == 0 and unreadable == 0:
        lines.insert(
            0,
            f"  [OK ] no PerfReporter dropped-write warnings in {scanned} cell log(s)",
        )
        return True, lines
    summary = f"  [BAD] {total} dropped-write warning(s) across {scanned} cell log(s)"
    if unreadable:
        summary += f"; {unreadable} log(s) unreadable"
    lines.insert(0, summary)
    return False, lines


def check_backend_execution(container, prefix: str, run_id: str, allow_unknown_binding: bool = False):
    """Check per-workload aggregates against configured backend/counter rules.

    Runtime names identify objects, Python counts measure normal execute
    returns, and native counts measure instrumented binding entries.
    Unknown native counts are accepted only with allow_unknown_binding.
    Process-wide deltas, timing slack, and aggregation limit attribution;
    a passing cell does not prove each row or operation ran entirely in Rust.
    """
    rows = list(
        container.query_items(
            "SELECT * "
            "FROM c WHERE STARTSWITH(c.workload_id, @prefix) AND ENDSWITH(c.workload_id, @run_id)",
            parameters=[
                {"name": "@prefix", "value": prefix},
                {"name": "@run_id", "value": run_id},
            ],
            enable_cross_partition_query=True,
        )
    )
    if not rows:
        return False, [f"  (no result rows found for run id {run_id})"]

    agg = {}
    for r in summary_rows(rows):
        wid = r["workload_id"]
        a = agg.setdefault(
            wid,
            {
                "backend": r.get("config_backend", "?"),
                "runtime": r.get("runtime_backend", "?"),
                "count": 0,
                "execute": 0,
                "binding": 0,
                "binding_known": False,
                "binding_unknown": False,
                "runtimes": set(),
                "labels": set(),
                "windows": set(),
            },
        )
        a["count"] += int(r.get("count", 0) or 0)
        a["runtimes"].add(r.get("runtime_backend"))
        a["labels"].add(r.get("config_backend"))
        if window_key(r) in a["windows"]:
            continue
        a["windows"].add(window_key(r))
        a["execute"] += int(r.get("rust_execute_calls", 0) or 0)
        b = r.get("binding_calls", -1)
        b = int(b if b is not None else -1)
        if b >= 0:
            a["binding"] += b
            a["binding_known"] = True
        else:
            a["binding_unknown"] = True
        a["runtime"] = r.get("runtime_backend", a["runtime"])

    lines = []
    all_ok = bool(agg)
    # Slack: the closed-loop wave still in flight at the final flush can leave a
    # few ops uncounted on one side; tolerate a small fraction so a healthy run
    # never trips, while a wholesale mismatch (mislabeled engine) still fails.
    for wid in sorted(agg):
        a = agg[wid]
        label = (a["backend"] or "").strip().lower()
        if label == "rust":
            # binding_calls is incremented inside the compiled extension, so it
            # is the only counter whose movement is evidence that compiled code
            # ran. rust_execute_calls is incremented by a Python-side wrapper
            # around the backend object's execute, so it proves a backend object
            # existed and returned responses -- weaker, and taken on the Python
            # side of the boundary rather than beyond it. (The run cannot start
            # with COSMOS_BACKEND=Rust and no extension at all: workload.py
            # refuses on the backend mismatch check before any row is written.
            # The difference here is where the count is taken, not whether the
            # extension loaded.) A row with no binding_calls therefore cannot
            # carry the document's proof, so it fails unless the caller
            # explicitly opts into the weaker evidence.
            known = a["binding_known"] and not a["binding_unknown"]
            if known:
                proof = a["binding"]
                proof_name = "binding_calls"
            else:
                proof = a["execute"]
                proof_name = "rust_execute_calls(binding unknown)"
            min_expected = int(a["count"] * 0.99)
            cell_ok = (
                proof > 0
                and a["execute"] > 0
                and proof >= min_expected
                and (known or allow_unknown_binding)
                and a["runtimes"] <= EXPECTED_RUNTIME["rust"]
                and a["labels"] == {"rust"}
            )
            flag = "OK " if cell_ok else "BAD"
            lines.append(
                f"  [{flag}] {wid}: backend=rust runtime={a['runtime']} "
                f"count={a['count']} {proof_name}={proof} "
                f"rust_execute_calls={a['execute']}"
            )
            if not cell_ok:
                if not a["binding_known"] and not allow_unknown_binding:
                    lines.append(
                        "        -> no binding_calls counter on any row, so nothing "
                        "proves compiled code ran; rust_execute_calls is counted on "
                        "the Python side of the boundary. Re-run with a harness that "
                        "records binding_calls, or pass --allow-unknown-binding to "
                        "score this run on the weaker evidence."
                    )
                else:
                    lines.append(
                        "        -> labeled rust but the Rust path did not cover the "
                        "work; this row may actually be core-python."
                    )
        else:
            cell_ok = (
                label == "core-python" and a["labels"] == {"core-python"}
                and a["runtimes"] <= EXPECTED_RUNTIME["core-python"]
                and a["execute"] == 0 and a["binding"] == 0
            )
            flag = "OK " if cell_ok else "BAD"
            lines.append(
                f"  [{flag}] {wid}: backend=core-python runtime={a['runtime']} "
                f"rust_execute_calls={a['execute']} binding_calls={a['binding']}"
            )
            if not cell_ok:
                lines.append(
                    "        -> labeled core-python but Rust activity was counted; "
                    "run is cross-contaminated."
                )
        all_ok = all_ok and cell_ok
    return all_ok, lines


def check_completion(container, prefix, run_id, expected_workloads=None):
    """Require every process's durable completion record and all its summaries."""
    rows = list(container.query_items(
        "SELECT * FROM c WHERE STARTSWITH(c.workload_id, @prefix) AND ENDSWITH(c.workload_id, @run_id)",
        parameters=[{"name": "@prefix", "value": prefix}, {"name": "@run_id", "value": run_id}],
        enable_cross_partition_query=True,
    ))
    measurements = list(summary_rows(rows))
    completed = [r for r in rows if r.get("record_type") == "completion"]
    observed = {r["workload_id"] for r in measurements}
    lines = []
    ok = bool(measurements) and bool(completed)
    expected = set(expected_workloads or [])
    if expected and observed != expected:
        ok = False
        lines.append(f"  [BAD] missing cells={sorted(expected-observed)} unexpected cells={sorted(observed-expected)}")
    grouped = {}
    for row in measurements:
        grouped.setdefault((row["workload_id"], row.get("process_id")), []).append(row)
    if len(grouped) != len(observed):
        ok = False
        lines.append("  [BAD] workload ID reused by multiple processes")
    done = {}
    for row in completed:
        key = (row["workload_id"], row.get("process_id"))
        if key in done:
            raise ValueError("Duplicate process completion records")
        done[key] = row
    if grouped.keys() != done.keys():
        ok = False
        lines.append("  [BAD] process measurements and completion records do not match")
    for key, summaries in grouped.items():
        record = done.get(key, {})
        windows = {r.get("window_index") for r in summaries}
        valid = (
            isinstance(key[1], str) and bool(key[1])
            and record.get("summary_count") == len(summaries)
            and record.get("total_count") == sum(r["count"] for r in summaries)
            and record.get("total_errors") == sum(r["errors"] for r in summaries)
            and windows == set(range(1, record.get("window_count", 0) + 1))
        )
        ok = ok and valid
        lines.append(f"  [{'OK ' if valid else 'BAD'}] {key[0]} process={key[1]} complete summaries={len(summaries)}")
    if not measurements:
        lines.append("  [BAD] no measurement rows")
    return ok, lines


def main():
    ap = argparse.ArgumentParser(description="Post-run integrity gate for the perf drill.")
    ap.add_argument("--run-id", default=None, help="run id YYYYMMDD-HHMMSSmmm (default: latest)")
    ap.add_argument("--stamp", dest="run_id", help=argparse.SUPPRESS)
    ap.add_argument("--log-dir", default=None, help="per-cell log dir to scan for reporter warnings")
    ap.add_argument(
        "--allow-missing-logs",
        action="store_true",
        default=os.environ.get("PERF_ALLOW_MISSING_LOGS", "") not in ("", "0", "false"),
        help="downgrade absent log evidence from a failure to a warning, for "
        "scoring a run whose per-cell logs were not kept",
    )
    ap.add_argument(
        "--allow-unknown-binding",
        action="store_true",
        default=os.environ.get("PERF_ALLOW_UNKNOWN_BINDING", "") not in ("", "0", "false"),
        help="accept rust-labelled rows that carry no binding_calls counter, "
        "scoring them on rust_execute_calls instead. Weaker evidence: that "
        "counter is incremented on the Python side of the boundary, not "
        "inside the compiled extension.",
    )
    ap.add_argument(
        "--prefix",
        default="lat-",
        help="workload_id prefix identifying the run. Used to find the latest "
        "run id and to label the report.",
    )
    ap.add_argument(
        "--required-backends",
        default="core-python,rust",
        help="comma-separated backends every operation must contain "
        "(default core-python,rust)",
    )
    ap.add_argument("--expected-workloads", help="File listing every planned workload ID, one per line")
    ap.add_argument("--allow-incomplete-history", action="store_true",
                    help="Inspect historical data without process completion records; not a completeness pass")
    args = ap.parse_args()
    required_backends = [
        backend.strip()
        for backend in args.required_backends.split(",")
        if backend.strip()
    ]
    if not required_backends or not set(required_backends) <= EXPECTED_RUNTIME.keys():
        ap.error("--required-backends must name core-python and/or rust")

    try:
        report_interval_s = float(os.environ.get("PERF_REPORT_INTERVAL", "300"))
    except ValueError:
        ap.error("PERF_REPORT_INTERVAL must be numeric")
    if not math.isfinite(report_interval_s) or report_interval_s <= 0:
        ap.error("PERF_REPORT_INTERVAL must be finite and positive")
    container = _connect()

    run_id = args.run_id or _latest_run_id(container, args.prefix)
    if not run_id:
        print(f"ERROR: no {args.prefix}* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    print(f"=== integrity gate (prefix {args.prefix}, run id {run_id}) ===")
    print(
        "-- 0. work-done: count > 0, near-zero errors, "
        f"required backends present ({','.join(required_backends)}) --"
    )
    qual_ok, qual_lines = check_quality(
        container, args.prefix, run_id, required_backends
    )
    print("\n".join(qual_lines))
    print("-- 1. row-continuity (no dropped windows) --")
    cont_ok, cont_lines = check_continuity(container, args.prefix, run_id, report_interval_s)
    print("\n".join(cont_lines))
    print("-- 2. reporter dropped-write warnings --")
    warn_ok, warn_lines = check_warnings(args.log_dir, strict=not args.allow_missing_logs)
    print("\n".join(warn_lines))
    print("-- 3. backend labels and available execution evidence --")
    prov_ok, prov_lines = check_backend_execution(
        container, args.prefix, run_id, allow_unknown_binding=args.allow_unknown_binding
    )
    print("\n".join(prov_lines))

    expected = None
    if args.expected_workloads:
        with open(args.expected_workloads, encoding="utf-8") as handle:
            expected = [line.strip() for line in handle if line.strip()]
        if not expected:
            ap.error("--expected-workloads must not be empty")
    complete_ok, complete_lines = check_completion(container, args.prefix, run_id, expected)
    print("-- 4. process completion and complete result windows --")
    print("\n".join(complete_lines))
    if args.allow_incomplete_history:
        print("  WARNING: completeness is unverified (--allow-incomplete-history)")
    ok = qual_ok and cont_ok and warn_ok and prov_ok and (complete_ok or args.allow_incomplete_history)
    print(f"=== integrity gate: {'PASS' if ok else 'FAIL'} ===")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
