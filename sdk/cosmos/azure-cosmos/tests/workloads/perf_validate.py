# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Post-run integrity gate for the latency matrix (methodology red-flag #2).

WHY THIS EXISTS (plain English):
  Every reporting window's row is written to Cosmos with a best-effort upsert
  that, on failure, is ONLY logged -- there is no retry and no backfill
  (perf_reporter.py upsert_item try/except). Under pressure a write can fail,
  and that window's data silently vanishes. A vanished BAD window (a latency
  spike, an error burst) would make the run look healthier than it was.

  This makes that failure impossible to MISS instead of impossible to HAPPEN,
  by enforcing the two cheap checks at the end of every run:

    1. Row-continuity -- each row stamps `window_seconds` (how long it covers)
       and `elapsed_seconds` (seconds since post-warmup start). For a healthy
       run the rows tile the timeline with no holes: the jump in elapsed_seconds
       between two consecutive rows equals the later row's window_seconds. A
       larger jump means a window in between was dropped -> we point at the hole.

    2. Reporter-warning scan -- grep the per-cell workload logs for the
       reporter's own "PerfReporter upsert failed" / "error upsert failed"
       warnings. Zero hits means nothing was dropped at the source.

  Exit code is non-zero if EITHER check finds a problem, so a caller (the matrix
  driver, the hourly monitor, CI) can treat it as a hard gate, not a footnote.

USAGE:
  source ./perf_env.sh            # exports RESULTS_COSMOS_* (incl. the key)
  python3 perf_validate.py [--stamp YYYYMMDD-HHMMSS] [--log-dir logs/latency-...]
      --stamp    which run to check; default = the most recent lat-* stamp
                 found in the results container.
      --log-dir  per-cell logs to scan for reporter warnings; optional but
                 recommended (the continuity check alone cannot see a drop that
                 happened to land on a window the run never reached).
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


def _stamp_of(workload_id: str) -> str:
    # workload_id = lat-{op}-{backend}-r{r}-{YYYYMMDD-HHMMSS}. The backend can
    # itself contain a dash (core-python), so the stamp is always the LAST two
    # dash-separated fields joined -- never positional from the front.
    parts = workload_id.split("-")
    if len(parts) < 2:
        return ""
    return parts[-2] + "-" + parts[-1]


def _connect():
    uri = os.environ.get("RESULTS_COSMOS_URI")
    key = os.environ.get("RESULTS_COSMOS_KEY")
    db = os.environ.get("RESULTS_COSMOS_DATABASE", "perfdb")
    cont = os.environ.get("RESULTS_COSMOS_CONTAINER", "perfresults")
    if not uri or not key:
        print(
            "ERROR: RESULTS_COSMOS_URI / RESULTS_COSMOS_KEY not set. "
            "`source ./perf_env.sh` (after exporting the key) first.",
            file=sys.stderr,
        )
        sys.exit(2)
    return CosmosClient(uri, key).get_database_client(db).get_container_client(cont)


def _latest_stamp(container) -> str:
    ids = list(
        container.query_items(
            "SELECT VALUE c.workload_id FROM c WHERE STARTSWITH(c.workload_id, 'lat-')",
            enable_cross_partition_query=True,
        )
    )
    stamps = {_stamp_of(i) for i in ids if i}
    stamps.discard("")
    if not stamps:
        return ""
    # YYYYMMDD-HHMMSS sorts correctly as a plain string.
    return max(stamps)


# A latency row is only trustworthy if the cell actually did work. An empty or
# nearly-empty cell, or one whose ops mostly errored, can still report tidy-
# looking percentiles (a count=0 window leaves the latency fields at 0.0). We
# refuse to trust any cell whose error fraction exceeds this -- 1% of ops.
_MAX_ERROR_FRACTION = 0.01


def check_quality(container, stamp: str):
    """Flag #4 gate: every cell must have real work (count > 0) and near-zero
    errors, and every operation must have BOTH backends present, BEFORE any
    latency number is believed. This is intentionally the first check -- a
    "fast" p50 means nothing if it came from a cell that did nothing.

    NOTE: we do NOT require core and rust to have EQUAL counts. They run the
    same duration closed-loop, so the faster backend legitimately completes more
    ops; equal counts would be the wrong test. Parity here means "both sides did
    substantial, low-error work on the same operation", not "identical totals".
    """
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.operation, c.config_backend, c.count, c.errors "
            "FROM c WHERE ENDSWITH(c.workload_id, @stamp)",
            parameters=[{"name": "@stamp", "value": stamp}],
            enable_cross_partition_query=True,
        )
    )
    if not rows:
        return False, [f"  (no result rows found for stamp {stamp})"]

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


def check_continuity(container, stamp: str, report_interval_s: float):
    """Return (ok, lines) for the row-continuity check across all cells in `stamp`."""
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.elapsed_seconds, c.window_seconds, c.count, "
            "c.errors, c.operation, c.config_backend FROM c "
            "WHERE ENDSWITH(c.workload_id, @stamp)",
            parameters=[{"name": "@stamp", "value": stamp}],
            enable_cross_partition_query=True,
        )
    )
    lines = []
    if not rows:
        return False, [f"  (no result rows found for stamp {stamp})"]

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


def check_warnings(log_dir: str):
    """Return (ok, lines) for the reporter-warning scan over the per-cell logs."""
    if not log_dir:
        return True, ["  (skipped: no --log-dir given)"]
    if not os.path.isdir(log_dir):
        return True, [f"  (skipped: log dir not found: {log_dir})"]
    pat = re.compile(r"PerfReporter (?:upsert failed|error upsert failed)")
    lines = []
    total = 0
    for path in sorted(glob.glob(os.path.join(log_dir, "*.log"))):
        n = 0
        try:
            with open(path, "r", errors="replace") as fh:
                for ln in fh:
                    if pat.search(ln):
                        n += 1
        except OSError as e:
            lines.append(f"  (could not read {path}: {e})")
            continue
        if n:
            total += n
            lines.append(f"  [BAD] {os.path.basename(path)}: {n} dropped-write warning(s)")
    if total == 0:
        lines.insert(0, "  [OK ] no PerfReporter dropped-write warnings in any cell log")
        return True, lines
    lines.insert(0, f"  [BAD] {total} dropped-write warning(s) across cell logs")
    return False, lines


def main():
    ap = argparse.ArgumentParser(description="Post-run integrity gate for the latency matrix.")
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--log-dir", default=None, help="per-cell log dir to scan for reporter warnings")
    args = ap.parse_args()

    report_interval_s = float(os.environ.get("PERF_REPORT_INTERVAL", "300") or "300")
    container = _connect()

    stamp = args.stamp or _latest_stamp(container)
    if not stamp:
        print("ERROR: no lat-* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    print(f"=== Phase A integrity gate (stamp {stamp}) ===")
    print("-- 0. work-done: count > 0, near-zero errors, both backends present --")
    qual_ok, qual_lines = check_quality(container, stamp)
    print("\n".join(qual_lines))
    print("-- 1. row-continuity (no dropped windows) --")
    cont_ok, cont_lines = check_continuity(container, stamp, report_interval_s)
    print("\n".join(cont_lines))
    print("-- 2. reporter dropped-write warnings --")
    warn_ok, warn_lines = check_warnings(args.log_dir)
    print("\n".join(warn_lines))

    ok = qual_ok and cont_ok and warn_ok
    print(f"=== integrity gate: {'PASS' if ok else 'FAIL'} ===")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
