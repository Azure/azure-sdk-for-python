# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Post-run integrity gate for the latency matrix.

Each window's row is written to Cosmos with a best-effort upsert that is only
logged on failure, so under pressure a window's data can silently vanish. A
vanished bad window would make the run look healthier than it was. This script
catches that with two checks at the end of a run:

  1. Row-continuity -- each row records ``window_seconds`` (how long it covers) and
     ``elapsed_seconds`` (seconds since post-warmup start). In a healthy run the
     jump in elapsed_seconds between two rows equals the later row's
     window_seconds; a larger jump means a window was dropped.

  2. Reporter-warning scan -- grep the per-cell logs for the reporter's own
     "upsert failed" warnings. Zero hits means nothing was dropped at the source.

Exit code is non-zero if either check finds a problem, so a caller can treat it
as a hard gate.

USAGE:
  source ./perf_env.sh            # exports RESULTS_COSMOS_* (incl. the key)
  python3 perf_validate.py [--run-id YYYYMMDD-HHMMSS] [--log-dir logs/latency-...]
      --run-id   which run to check; default = the most recent matching run.
      --log-dir  per-cell logs to scan for reporter warnings; optional.
"""

import argparse
import glob
import os
import re
import sys

try:
    from azure.cosmos import CosmosClient
except ImportError:
    print("ERROR: azure-cosmos is required (pip install azure-cosmos).", file=sys.stderr)
    sys.exit(2)


# A continuity hole only counts if the elapsed jump exceeds the row's own
# window by more than this slack, so normal jitter (a flush a few seconds late,
# a merged/short final window) never trips a false alarm. One full report
# interval of slack means "we tolerate timing wobble but not a whole lost row".
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


def check_quality(container, prefix: str, run_id: str):
    """Every cell must have real work (count > 0) and near-zero errors, and every
    operation must have both backends present, before any latency number is
    believed. This runs first: a "fast" p50 means nothing if the cell did nothing.

    We do not require core and rust to have equal counts. They run the same
    duration closed-loop, so the faster backend completes more ops; equal counts
    would be the wrong test. We just need both sides to do real, low-error work.
    """
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.operation, c.config_backend, c.count, c.errors "
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
    for r in rows:
        wid = r["workload_id"]
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
    all_ok = True
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

    # Every operation must have been measured on BOTH backends, or the matrix
    # produced a one-sided comparison no one should read as rust-vs-core.
    for op in sorted(backends_by_op):
        present = backends_by_op[op]
        if not {"core-python", "rust"}.issubset(present):
            all_ok = False
            lines.append(
                f"  [BAD] op={op}: missing a backend (have {sorted(present)}); "
                "comparison is one-sided"
            )
    return all_ok, lines


def check_continuity(container, prefix: str, run_id: str, report_interval_s: float):
    """Return (ok, lines) for the row-continuity check across all cells in `run_id`."""
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.elapsed_seconds, c.window_seconds, c.count, "
            "c.errors, c.operation, c.config_backend FROM c "
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
    for r in rows:
        cells.setdefault(r["workload_id"], []).append(r)

    tol = _gap_tolerance_s(report_interval_s)
    all_ok = True
    for wid in sorted(cells):
        recs = sorted(cells[wid], key=lambda x: x.get("elapsed_seconds", 0.0))
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
    """Return (ok, lines) for the reporter-warning scan over the per-cell logs.

    The scan proves a negative -- that no cell dropped a results write -- so it is
    only worth anything if the logs were actually read. Absent evidence is not the
    same as clean evidence: with no ``--log-dir``, a directory that isn't there, no
    ``.log`` files in it, or a file that won't open, the gate has checked nothing
    and must say so rather than report the run clean.

    In strict mode (the default) each of those is a failure. Pass ``strict=False``
    (``--allow-missing-logs``) to score a run whose logs were genuinely not kept,
    which downgrades them to warnings.
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
    pat = re.compile(r"PerfReporter (?:upsert failed|error upsert failed)")
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


def check_backend_execution(container, prefix: str, run_id: str):
    """Prove every cell ran on the engine its label claims, from counters in the
    rows rather than COSMOS_BACKEND.

    Each row carries, beside the declared ``config_backend``:
      * ``runtime_backend``    -- the class of the backend object the client built.
      * ``rust_execute_calls`` -- ops the Rust path handled this window.
      * ``binding_calls``      -- ops the Rust binding counted (-1 when unknown).

    Rules per cell (workload_id):
      * "rust": must have run on Rust. Require binding_calls > 0 and
        rust_execute_calls > 0, and binding_calls must cover essentially all
        operations (a small slack for the wave open at the final flush). If
        binding_calls is unknown (-1), fall back to rust_execute_calls > 0.
      * "core-python": must not have touched Rust. Both counts must be 0
        (binding_calls == -1 is also fine).
    """
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.config_backend, c.runtime_backend, "
            "c.rust_execute_calls, c.binding_calls, c.count, c.errors "
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
    for r in rows:
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
            },
        )
        a["count"] += int(r.get("count", 0) or 0)
        a["execute"] += int(r.get("rust_execute_calls", 0) or 0)
        b = r.get("binding_calls", -1)
        b = int(b if b is not None else -1)
        if b >= 0:
            a["binding"] += b
            a["binding_known"] = True
        a["runtime"] = r.get("runtime_backend", a["runtime"])

    lines = []
    all_ok = True
    # Slack: the closed-loop wave still in flight at the final flush can leave a
    # few ops uncounted on one side; tolerate a small fraction so a healthy run
    # never trips, while a wholesale mismatch (mislabeled engine) still fails.
    for wid in sorted(agg):
        a = agg[wid]
        label = (a["backend"] or "").strip().lower()
        if label == "rust":
            if a["binding_known"]:
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
            )
            flag = "OK " if cell_ok else "BAD"
            lines.append(
                f"  [{flag}] {wid}: backend=rust runtime={a['runtime']} "
                f"count={a['count']} {proof_name}={proof} "
                f"rust_execute_calls={a['execute']}"
            )
            if not cell_ok:
                lines.append(
                    "        -> labeled rust but the Rust path did not cover the "
                    "work; this row may actually be core-python."
                )
        else:
            cell_ok = a["execute"] == 0 and a["binding"] == 0
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
        "--prefix",
        default="lat-",
        help="workload_id prefix identifying the run. Used to find the latest "
        "run id and to label the report.",
    )
    args = ap.parse_args()

    report_interval_s = float(os.environ.get("PERF_REPORT_INTERVAL", "300") or "300")
    container = _connect()

    run_id = args.run_id or _latest_run_id(container, args.prefix)
    if not run_id:
        print(f"ERROR: no {args.prefix}* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    print(f"=== integrity gate (prefix {args.prefix}, run id {run_id}) ===")
    print("-- 0. work-done: count > 0, near-zero errors, both backends present --")
    qual_ok, qual_lines = check_quality(container, args.prefix, run_id)
    print("\n".join(qual_lines))
    print("-- 1. row-continuity (no dropped windows) --")
    cont_ok, cont_lines = check_continuity(container, args.prefix, run_id, report_interval_s)
    print("\n".join(cont_lines))
    print("-- 2. reporter dropped-write warnings --")
    warn_ok, warn_lines = check_warnings(args.log_dir, strict=not args.allow_missing_logs)
    print("\n".join(warn_lines))
    print("-- 3. backend check: each row ran on the engine it claims --")
    prov_ok, prov_lines = check_backend_execution(container, args.prefix, run_id)
    print("\n".join(prov_lines))

    ok = qual_ok and cont_ok and warn_ok and prov_ok
    print(f"=== integrity gate: {'PASS' if ok else 'FAIL'} ===")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
