# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Report per-operation and blended percentiles from available success histograms.

Merge window histograms within each backend, grouping operations by the
row's operation field. Blended percentiles describe the observed sample mix,
not every operation's tail or an automatically satisfied application SLA.

Pooling preserves histogram quantization and workload range clamping; it
cannot recover missing windows, failed-call durations, or unrecorded samples.

Run mixed_report.py with --stamp and --prefix after configuring the results
account.
"""

import argparse
import sys

import perf_driver_commit_gate as _driver_gate
from perf_results import add_histogram, split_workload_id, summary_rows, window_key
from latency_report import (
    HdrHistogram,
    MAX_US,
    MIN_US,
    _connect,
    _latest_run_id,
    _split_wid,
    _new_timing_fields,
    _add_timing_row,
    _attach_schedule,
    _print_fixed_rate_details,
)

_OP_ORDER = ["read", "create", "upsert", "replace", "delete", "patch"]

# The stored ``operation`` field uses the SDK call label (e.g. "ReadItem",
# "UpsertItem", "QueryItems"), not the short op name. Normalize to the short name
# so per-op grouping lines up with _OP_ORDER. Anything unrecognized is lowercased
# with a trailing "item"/"items" stripped, so a new op still maps sensibly.
_CANON = {
    "readitem": "read",
    "createitem": "create",
    "upsertitem": "upsert",
    "replaceitem": "replace",
    "deleteitem": "delete",
    "patchitem": "patch",
    "queryitems": "query",
}


def _canon_op(raw):
    k = str(raw or "").strip().lower()
    if k in _CANON:
        return _CANON[k]
    for suffix in ("items", "item"):
        if k.endswith(suffix):
            return k[: -len(suffix)]
    return k


def _new_cell():
    return {
        "count": 0,
        "errors": 0,
        "throttled_429": 0,
        "window_s": 0.0,
        "ru_weighted": 0.0,
        "ru_count": 0,
        "hist": HdrHistogram(MIN_US, MAX_US, 3),
        "no_hist_windows": 0,
        "windows": {},
        **_new_timing_fields(),
    }


def _add_row(cell, r, c):
    _add_timing_row(cell, r)
    cell["count"] += c
    cell["errors"] += int(r.get("errors", 0) or 0)
    throttled = r.get("throttled_429")
    if throttled is None or throttled < 0 or cell["throttled_429"] is None:
        cell["throttled_429"] = None
    else:
        cell["throttled_429"] += int(throttled)
    key = window_key(r)
    duration = r["window_seconds"]
    if key not in cell["windows"]:
        cell["window_s"] += duration
        cell["windows"][key] = duration
    elif cell["windows"][key] != duration:
        raise ValueError("Conflicting durations for one process window")
    cell["ru_weighted"] += r.get("ru_sum", 0.0) or 0.0
    cell["ru_count"] += r.get("ru_count", 0) or 0
    hb = r.get("hist_b64")
    if not add_histogram(cell["hist"], hb, c):
        cell["no_hist_windows"] += 1


def _aggregate(container, prefix, stamp):
    """Return per_op[(backend, op)] and blended[backend], both pooled histograms.

    Scoped by BOTH prefix (STARTSWITH) and stamp (ENDSWITH) so no other run that
    happened to land on the same-second stamp under a different prefix leaks in.
    """
    rows = list(
        container.query_items(
            "SELECT * "
            "FROM c WHERE STARTSWITH(c.workload_id, @prefix) "
            "AND ENDSWITH(c.workload_id, @stamp)",
            parameters=[
                {"name": "@prefix", "value": prefix},
                {"name": "@stamp", "value": stamp},
            ],
            enable_cross_partition_query=True,
        )
    )
    per_op, blended = {}, {}
    prov_commits, prov_missing, prov_rust = set(), 0, 0
    measurements = list(summary_rows(rows))
    for r in measurements:
        # backend comes from the workload_id; the real operation comes from the row.
        _wop, backend, _ = split_workload_id(r["workload_id"], prefix)
        op = _canon_op(r.get("operation"))
        if not backend or op not in _OP_ORDER:
            continue
        c = int(r.get("count", 0) or 0)
        if backend and "rust" in backend.lower():
            prov_rust += 1
            _dc = str(r.get("driver_commit") or "").strip()
            if _driver_gate.is_stamped_commit(_dc):
                prov_commits.add(_dc)
            else:
                prov_missing += 1
        cell = per_op.get((backend, op))
        if cell is None:
            cell = per_op[(backend, op)] = _new_cell()
        _add_row(cell, r, c)
        bcell = blended.get(backend)
        if bcell is None:
            bcell = blended[backend] = _new_cell()
        _add_row(bcell, r, c)
    for backend, cell in blended.items():
        selected = [r for r in measurements if split_workload_id(r["workload_id"], prefix)[1] == backend]
        _attach_schedule(cell, selected, rows)
    return per_op, blended, (sorted(prov_commits), prov_missing, prov_rust)


def _pctile_ms(cell, q):
    if cell["count"] <= 0 or cell["no_hist_windows"] or cell["latency_overflow_count"]:
        return float("nan")
    return cell["hist"].get_value_at_percentile(q) / 1000.0


def _fmt(label, cell):
    rps = cell["count"] / cell["window_s"] if cell["window_s"] else 0.0
    ru = cell["ru_weighted"] / cell["ru_count"] if cell["ru_count"] else float("nan")
    note = "" if cell["no_hist_windows"] == 0 else (
        f"  [!] {cell['no_hist_windows']} window(s) lacked hist_b64; pooled latency unavailable"
    )
    if cell["latency_overflow_unknown"]:
        note += " [!] histogram overflow evidence unavailable"
    if cell["latency_overflow_count"]:
        note += " [!] durations exceeded histogram range; pooled latency unavailable"
    return (
        f"  {label:16s} count={cell['count']:>10d} err={cell['errors']:>5d} "
        f"429={str(cell['throttled_429']):>5s} rps={rps:>8.1f} "
        f"p50={_pctile_ms(cell,50):>6.2f} p90={_pctile_ms(cell,90):>6.2f} "
        f"p99={_pctile_ms(cell,99):>6.2f} p99.9={_pctile_ms(cell,99.9):>7.2f} "
        f"RU/op={ru:>6.2f} duration={next(iter(cell['duration_kinds'])).replace('_', '-')}{note}"
    )


def main():
    ap = argparse.ArgumentParser(
        description="Mixed/blended workload report (per-op + blended pooled percentiles)."
    )
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--prefix", default="mixed-", help="workload_id prefix (default mixed-)")
    _driver_gate.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_run_id(container, args.prefix)
    if not stamp:
        print(f"ERROR: no {args.prefix}* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    per_op, blended, prov_info = _aggregate(container, args.prefix, stamp)
    if not blended:
        print(f"ERROR: no result rows found for stamp {stamp}.", file=sys.stderr)
        sys.exit(2)

    backends = sorted(blended)
    print(f"=== Mixed/blended workload (prefix {args.prefix}, stamp {stamp}) ===")
    print("    One process issues a weighted BLEND of ops; percentiles are POOLED")
    print("    across complete success histograms, with one denominator per process window.")
    print()

    for backend in backends:
        print(f"-- backend: {backend} --")
        for op in _OP_ORDER:
            cell = per_op.get((backend, op))
            if cell:
                print(_fmt(op, cell))
                _print_fixed_rate_details(cell, include_schedule=False)
        # Retain per-operation results: the blend can hide an infrequent slow operation.
        print(_fmt("BLENDED (all)", blended[backend]))
        _print_fixed_rate_details(blended[backend])
        print()

    if "core-python" in backends and "rust" in backends:
        py, ru = blended["core-python"], blended["rust"]
        print("-- blended p99 head to head (observed successful-operation mix) --")
        print(
            f"  core-python p99={_pctile_ms(py,99):.2f}ms p99.9={_pctile_ms(py,99.9):.2f}ms  |  "
            f"rust p99={_pctile_ms(ru,99):.2f}ms p99.9={_pctile_ms(ru,99.9):.2f}ms"
        )
        print()

    commits, missing, rust_rows = prov_info
    commit_ok, commit_lines = _driver_gate.decide(
        commits, missing, rust_rows, strict=_driver_gate.strict_from(args)
    )
    for _l in commit_lines:
        print(_l)
    print("\n### GATE:", "FAIL" if not commit_ok else "PASS", "(rust driver commit) ###")
    measurements_ok = all(c["count"] > 0 and not c["no_hist_windows"]
                          and not c["latency_overflow_count"] for c in blended.values())
    sys.exit(0 if commit_ok and measurements_ok else 1)


if __name__ == "__main__":
    main()
