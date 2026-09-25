# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Report pooled success-latency histograms by operation and backend.

Intended for low-load, single-client probes; one timed SDK call can include
multiple requests or retries, so its duration is not one wire round trip.

Merge available window histograms rather than averaging their percentiles.
Results retain histogram quantization and the workload's range clamping.
Missing histograms make pooled percentiles unavailable; omitted failures are
not reconstructed from scalar percentiles.

Select baseline results with --profiling-session-id and --prefix after
configuring the results container. --run-id also accepts separate capture identifiers.
"""

import argparse
import math
import os
import sys

import perf_driver_commit_gate as _driver_gate
from perf_results import (
    OPERATIONS, TIMING_COMPONENTS, add_histogram, split_workload_id, summary_rows,
    fixed_rate_timing, fixed_rate_schedule_totals,
)

try:
    from azure.cosmos import CosmosClient
except ImportError:
    print("ERROR: azure-cosmos is required (pip install azure-cosmos).", file=sys.stderr)
    sys.exit(2)

try:
    from hdrh.histogram import HdrHistogram
except ImportError:
    print(
        "ERROR: hdrhistogram is required to merge per-window histograms "
        "(pip install hdrhistogram; import name: hdrh).",
        file=sys.stderr,
    )
    sys.exit(2)

# Use the same histogram range as perf_stats.py (1 us floor, 60 s ceiling, 3
# significant digits) so a merged histogram matches the ones the workload
# encoded. Import the constants when available; fall back to the literals.
try:
    from perf_stats import _MIN_VALUE_US as MIN_US, _MAX_VALUE_US as MAX_US
except Exception:  # pragma: no cover - perf_stats import is best-effort
    MIN_US, MAX_US = 1, 60_000_000

# Point operations in the order we report them (read first, then the writes).
_OP_ORDER = ["read", "create", "upsert", "replace", "delete", "patch"]


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


def _split_wid(workload_id: str):
    """Return (op, backend, run_id) from ``prefix-<op>-<backend>-<run-id>``.

    The backend itself can contain a dash (``core-python``), so the run id is the
    LAST two dash fields and the backend is everything between the op and run id —
    never taken positionally from a fixed index.
    """
    try:
        return split_workload_id(workload_id)
    except ValueError:
        return None, None, ""


def _latest_run_id(container, prefix: str) -> str:
    ids = list(
        container.query_items(
            "SELECT VALUE c.workload_id FROM c WHERE STARTSWITH(c.workload_id, @p)",
            parameters=[{"name": "@p", "value": prefix}],
            enable_cross_partition_query=True,
        )
    )
    run_ids = {_split_wid(i)[2] for i in ids if i}
    run_ids.discard("")
    return max(run_ids) if run_ids else ""


def _new_timing_fields():
    return {
        "duration_kinds": set(),
        "latency_overflow_count": 0,
        "latency_overflow_unknown": False,
        "missing_timing_windows": 0,
        "timings": {
            outcome: {name: {"hist": HdrHistogram(MIN_US, MAX_US, 3),
                             "overflow_count": 0, "max_observed_ms": 0.0}
                      for name in TIMING_COMPONENTS}
            for outcome in ("success", "failure")
        },
        "schedule": None,
    }


def _add_timing_row(cell, row):
    count = int(row["count"])
    fixed_rate = float(row.get("config_arrival_rate", 0) or 0) > 0 and row.get("config_use_sync") is False
    kind = "total" if fixed_rate else "sdk_call"
    if row.get("duration_kind", kind) != kind:
        raise ValueError("Duration kind disagrees with workload configuration")
    cell["duration_kinds"].add(kind)
    if len(cell["duration_kinds"]) > 1:
        raise ValueError("Cannot combine total duration and SDK-call duration in one cell")
    overflow = row.get("latency_overflow_count")
    if overflow is not None and (type(overflow) is not int or not 0 <= overflow <= count):
        raise ValueError("Invalid latency overflow count")
    if overflow is None:
        cell["latency_overflow_unknown"] = True
    else:
        cell["latency_overflow_count"] += overflow
    if fixed_rate:
        for outcome, expected in (("success", count), ("failure", int(row["errors"]))):
            group = fixed_rate_timing(row, outcome)
            if expected and group is None:
                cell["missing_timing_windows"] += 1
                continue
            if group is not None:
                for name in TIMING_COMPONENTS:
                    target, source = cell["timings"][outcome][name], group[name]
                    if not add_histogram(target["hist"], source.get("hist_b64"), expected):
                        raise ValueError(f"Missing {outcome} {name} histogram")
                    target["overflow_count"] += source["overflow_count"]
                    target["max_observed_ms"] = max(target["max_observed_ms"], source["max_observed_ms"])


def _attach_schedule(cell, measurements, rows):
    """Attach process-wide schedule totals once, never once per mixed-operation row."""
    if cell["duration_kinds"] != {"total"}:
        return
    process_rows = {}
    for row in measurements:
        process_rows.setdefault((row["workload_id"], row.get("process_id")), []).append(row)
    totals = None
    for (wid, pid), selected in process_rows.items():
        completed = [r for r in rows if r.get("record_type") == "completion"
                     and r.get("workload_id") == wid and r.get("process_id") == pid]
        if len(completed) > 1:
            raise ValueError("Duplicate fixed-rate completion record")
        schedule = fixed_rate_schedule_totals(selected, completed[0] if completed else None)
        if schedule is None:
            totals = None
            break
        if totals is None:
            totals = {field: 0 for field in schedule}
        for field, value in schedule.items():
            totals[field] += value
    cell["schedule"] = totals


def _aggregate(container, prefix: str, run_id: str):
    """Merge all windows of each (op, backend) cell into one pooled histogram.

    Returns a dict keyed (op, backend) -> stats. ``hist`` is the merged
    HdrHistogram; ``no_hist_windows`` counts windows that had no hist_b64 (older
    runs), which is what makes exact pooling impossible for that cell.

    The query is scoped by BOTH the prefix (STARTSWITH) and the run id (ENDSWITH):
    filtering on the run id alone would mix rows from another workload that happened
    to start in the same millisecond under a different prefix.
    """
    rows = list(
        container.query_items(
            "SELECT * "
            "FROM c WHERE STARTSWITH(c.workload_id, @prefix) "
            "AND ENDSWITH(c.workload_id, @stamp)",
            parameters=[
                {"name": "@prefix", "value": prefix},
                {"name": "@stamp", "value": run_id},
            ],
            enable_cross_partition_query=True,
        )
    )
    agg = {}
    prov_commits, prov_missing, prov_rust = set(), 0, 0
    measurements = list(summary_rows(rows))
    for r in measurements:
        op, backend, _ = split_workload_id(r["workload_id"], prefix)
        if r.get("operation") != OPERATIONS.get(op):
            continue
        key = (op, backend)
        if backend and "rust" in backend.lower():
            prov_rust += 1
            _dc = str(r.get("driver_commit") or "").strip()
            if _driver_gate.is_stamped_commit(_dc):
                prov_commits.add(_dc)
            else:
                prov_missing += 1
        a = agg.get(key)
        if a is None:
            a = agg[key] = {
                "count": 0,
                "errors": 0,
                "throttled_429": 0,
                "window_s": 0.0,
                "ru_weighted": 0.0,
                "ru_count": 0,
                "hist": HdrHistogram(MIN_US, MAX_US, 3),
                "no_hist_windows": 0,
                "scalar_p999_weighted": 0.0,  # count-weighted fallback only
                "arrival_rates": set(),
                "concurrencies": set(),
                "client_counts": set(),
                "sync_values": set(),
                "proxy_values": set(),
                "attempt_calls": 0,
                "retry_calls": 0,
                **_new_timing_fields(),
            }
        c = int(r.get("count", 0) or 0)
        a["count"] += c
        a["errors"] += int(r.get("errors", 0) or 0)
        for field in ("throttled_429", "attempt_calls", "retry_calls"):
            value = r.get(field)
            if value is None or value < 0 or a[field] is None:
                a[field] = None
            else:
                a[field] += int(value)
        a["arrival_rates"].add(float(r.get("config_arrival_rate", 0.0) or 0.0))
        _add_timing_row(a, r)
        a["concurrencies"].add(int(r.get("config_concurrency", 0) or 0))
        # -1 / None mean the field was absent, i.e. an older harness wrote the
        # row. That is distinct from a recorded value and must not read as one.
        _nc = r.get("config_num_clients")
        a["client_counts"].add(int(_nc) if _nc is not None else -1)
        _us = r.get("config_use_sync")
        a["sync_values"].add(bool(_us) if _us is not None else None)
        a["proxy_values"].add(r.get("config_proxy_enabled"))
        a["window_s"] += float(r.get("window_seconds", 0.0) or 0.0)
        a["ru_weighted"] += float(r.get("ru_sum", 0.0) or 0.0)
        a["ru_count"] += int(r.get("ru_count", 0) or 0)
        hb = r.get("hist_b64")
        if not add_histogram(a["hist"], hb, c):
            a["no_hist_windows"] += 1
            a["scalar_p999_weighted"] += float(r.get("p99_9_ms", 0.0) or 0.0) * c
    for (op, backend), cell in agg.items():
        selected = [r for r in measurements if split_workload_id(r["workload_id"], prefix)[:2] == (op, backend)]
        _attach_schedule(cell, selected, rows)
    return agg, (sorted(prov_commits), prov_missing, prov_rust)


def _pctile_ms(a, q):
    """Pooled percentile in ms from the merged histogram (values are in µs)."""
    if a["count"] <= 0 or a["no_hist_windows"] or a["latency_overflow_count"]:
        return float("nan")
    return a["hist"].get_value_at_percentile(q) / 1000.0


def _mean_ms(a):
    """Pooled arithmetic mean in ms from the merged histogram."""
    if a["count"] <= 0 or a["no_hist_windows"] or a["latency_overflow_count"]:
        return float("nan")
    return a["hist"].get_mean_value() / 1000.0


def _fmt_cell(op, backend, a):
    rps = a["count"] / a["window_s"] if a["window_s"] else 0.0
    ru = a["ru_weighted"] / a["ru_count"] if a["ru_count"] else float("nan")
    non_initial = str(a["retry_calls"]) if "rust" in backend.lower() else "n/a"
    exact = a["no_hist_windows"] == 0
    note = "" if exact else f"  [!] {a['no_hist_windows']} window(s) lacked hist_b64; pooled latency unavailable"
    if a["latency_overflow_unknown"]:
        note += " [!] histogram overflow evidence unavailable"
    if a["latency_overflow_count"]:
        note += f" [!] {a['latency_overflow_count']} durations exceeded histogram range; pooled latency unavailable"
    return (
        f"  {op:8s} {backend:11s} count={a['count']:>9d} err={a['errors']:>4d} "
        f"terminal_429={str(a['throttled_429']):>4s} recorded_non_initial={non_initial:>4s} rps={rps:>8.1f} "
        f"mean={_mean_ms(a):>6.2f} p50={_pctile_ms(a,50):>6.2f} "
        f"p90={_pctile_ms(a,90):>6.2f} "
        f"p99={_pctile_ms(a,99):>6.2f} p99.9={_pctile_ms(a,99.9):>7.2f} "
        f"RU/sample={ru:>6.2f} ru_samples={a['ru_count']} "
        f"duration={next(iter(a['duration_kinds'])).replace('_', '-')}{note}"
    )


def _print_fixed_rate_details(a, *, include_schedule=True):
    if a["duration_kinds"] != {"total"}:
        return
    if a["missing_timing_windows"]:
        print("    [!] Separate timing measurements incomplete; component percentiles unavailable.")
    else:
        for outcome in ("success", "failure"):
            for name in TIMING_COMPONENTS:
                series = a["timings"][outcome][name]
                hist = series["hist"]
                p99 = (hist.get_value_at_percentile(99) / 1000
                       if hist.total_count and not series["overflow_count"] else float("nan"))
                label = {"delay_before_call": "delay before SDK call", "sdk_call": "SDK-call duration",
                         "total": "total duration"}[name]
                print(f"    {outcome} {label}: samples={hist.total_count} p99={p99:.3f} ms "
                      f"max_observed={series['max_observed_ms']:.3f} ms "
                      f"overflow={series['overflow_count']}")
    if not include_schedule:
        return
    schedule = a["schedule"]
    if schedule is None:
        print("    [!] Final scheduling/backlog evidence unavailable.")
    else:
        print(f"    scheduled={schedule['scheduled_count']} launched={schedule['launched_count']} "
              f"not_launched={schedule['not_launched_count']} "
              f"limit_waits={schedule['limit_wait_count']} limit_wait_ms={schedule['limit_wait_ms']:.3f}")


def main():
    ap = argparse.ArgumentParser(
        description="Low-load latency report (pooled percentiles)."
    )
    selection = ap.add_mutually_exclusive_group()
    selection.add_argument("--profiling-session-id", dest="run_id",
                           help="profiling session identifier used as the baseline workload ID suffix")
    selection.add_argument("--run-id", help="workload ID suffix, including separate capture identifiers (default: latest)")
    selection.add_argument("--stamp", dest="run_id", help=argparse.SUPPRESS)
    ap.add_argument("--prefix", default="baseline-", help="workload_id prefix (default baseline-)")
    ap.add_argument(
        "--point-read-gate",
        action="store_true",
        help="enforce the low-load Rust point-read gate",
    )
    ap.add_argument(
        "--expected-rps",
        type=float,
        default=250.0,
        help="required configured and achieved read rate for --point-read-gate (default 250)",
    )
    ap.add_argument(
        "--max-p99-ms",
        type=float,
        default=10.0,
        help="exclusive Rust p99 ceiling for --point-read-gate (default 10)",
    )
    ap.add_argument(
        "--gate-backends",
        default="core-python,rust",
        help="comma-separated backends the --point-read-gate shape checks apply "
        "to (default core-python,rust). Narrow it only when the run "
        "deliberately exercised one engine, e.g. BASELINE_BACKENDS=rust.",
    )
    _driver_gate.add_cli_flag(ap)
    ap.add_argument("--workload-health", action="store_true",
                    help="require successful, error-free samples and known zero recorded Rust non-initial request counts")
    args = ap.parse_args()
    args.gate_backends = [b.strip() for b in args.gate_backends.split(",") if b.strip()]
    if not args.gate_backends or not set(args.gate_backends) <= {"core-python", "rust"}:
        ap.error("--gate-backends must name core-python and/or rust")
    if any(not math.isfinite(value) or value <= 0 for value in (args.expected_rps, args.max_p99_ms)):
        ap.error("Rate and latency threshold must be finite and positive")

    container = _connect()
    run_id = args.run_id or _latest_run_id(container, args.prefix)
    if not run_id:
        print(f"ERROR: no {args.prefix}* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    agg, prov_info = _aggregate(container, args.prefix, run_id)
    if not agg:
        print(f"ERROR: no result rows found for run id {run_id}.", file=sys.stderr)
        sys.exit(2)

    backends = sorted({b for (_, b) in agg})
    print(f"=== Low-load latency baseline (prefix {args.prefix}, run id {run_id}) ===")
    print("    Fixed-rate: total duration from scheduled start. Send-and-wait: SDK-call duration.")
    print("    Percentiles merge recorded success histograms; missing samples remain unavailable.")
    print()

    for backend in backends:
        print(f"-- backend: {backend} --")
        for op in _OP_ORDER:
            a = agg.get((op, backend))
            if a:
                print(_fmt_cell(op, backend, a))
                _print_fixed_rate_details(a)
        print()

    # Side-by-side mean/p50/p99/p99.9 when both engines are present, so a reader can
    # see per-request cost head to head. At conc=1 the engines are expected to be
    # close (latency is network-bound); a large gap on one op is worth a look.
    if "core-python" in backends and "rust" in backends:
        print("-- core-python vs rust (pooled ms; deltas = python - rust) --")
        print(
            f"  {'op':8s} {'mean_py':>7s} {'mean_ru':>7s} {'dmean':>6s} "
            f"{'p50_py':>7s} {'p50_ru':>7s} {'d50':>6s} "
            f"{'p99_py':>7s} {'p99_ru':>7s} {'p999_py':>8s} {'p999_ru':>8s}"
        )
        for op in _OP_ORDER:
            py = agg.get((op, "core-python"))
            ru = agg.get((op, "rust"))
            if not (py and ru):
                continue
            dmean = _mean_ms(py) - _mean_ms(ru)
            d50 = _pctile_ms(py, 50) - _pctile_ms(ru, 50)
            print(
                f"  {op:8s} {_mean_ms(py):>7.2f} {_mean_ms(ru):>7.2f} {dmean:>6.2f} "
                f"{_pctile_ms(py,50):>7.2f} {_pctile_ms(ru,50):>7.2f} "
                f"{d50:>6.2f} {_pctile_ms(py,99):>7.2f} {_pctile_ms(ru,99):>7.2f} "
                f"{_pctile_ms(py,99.9):>8.2f} {_pctile_ms(ru,99.9):>8.2f}"
            )

    # ---- Rust driver commit check (enforced; scoped to Rust rows) ----
    commits, missing, rust_rows = prov_info
    commit_ok, commit_lines = _driver_gate.decide(
        commits, missing, rust_rows, strict=_driver_gate.strict_from(args)
    )
    print()
    for _l in commit_lines:
        print(_l)
    print("\n### GATE:", "FAIL" if not commit_ok else "PASS", "(rust driver commit) ###")

    latency_ok = True
    if args.workload_health:
        latency_ok = all(
            a["count"] > 0 and a["errors"] == 0 and a["no_hist_windows"] == 0
            and a["throttled_429"] == 0
            and ("rust" not in backend or a["retry_calls"] == 0)
            and a["latency_overflow_count"] == 0
            and not a["latency_overflow_unknown"]
            for (_, backend), a in agg.items()
        )
        print("### WORKLOAD HEALTH:", "PASS" if latency_ok else "FAIL", "###")
    if args.point_read_gate:
        checks = []
        notes = []
        # The document's clean-baseline requirements are about the RUN, not one
        # engine: a core-Python row full of errors, 429s or retries is not a
        # comparable baseline even if the Rust row is spotless. So the shape
        # checks run per backend, and only the p99 threshold is Rust-specific.
        for backend in args.gate_backends:
            row = agg.get(("read", backend))
            if row is None:
                checks.append((False, f"{backend} read row exists"))
                continue
            achieved = row["count"] / row["window_s"] if row["window_s"] else 0.0
            checks.extend([
                (row["count"] > 0, f"{backend}: successful reads > 0 ({row['count']})"),
                (row["errors"] == 0, f"{backend}: errors = 0 ({row['errors']})"),
                (row["latency_overflow_count"] == 0 and not row["latency_overflow_unknown"],
                 f"{backend}: no clipped successful durations ({row['latency_overflow_count']})"),
                (row["missing_timing_windows"] == 0,
                 f"{backend}: separate timing measurements complete"),
                (row["schedule"] is not None,
                 f"{backend}: final scheduling/backlog evidence present"),
                (row["schedule"] is not None and row["schedule"]["limit_wait_count"] == 0,
                 f"{backend}: in-flight limit did not block launches"),
                (row["schedule"] is not None and row["schedule"]["not_launched_count"] == 0,
                 f"{backend}: no scheduled work left unlaunched at shutdown"),
                (
                    row["throttled_429"] == 0,
                    f"{backend}: terminal 429 responses = 0 ({row['throttled_429']})",
                ),
                (
                    row["no_hist_windows"] == 0,
                    f"{backend}: all windows have histograms "
                    f"(missing={row['no_hist_windows']})",
                ),
                (
                    row["arrival_rates"] == {args.expected_rps},
                    f"{backend}: configured arrival rate = {args.expected_rps:g} "
                    f"({sorted(row['arrival_rates'])})",
                ),
                (
                    row["proxy_values"] == {False},
                    f"{backend}: proxy disabled ({sorted(row['proxy_values'])})",
                ),
                (
                    row["concurrencies"] == {1},
                    f"{backend}: concurrency = 1 ({sorted(row['concurrencies'])})",
                ),
                (
                    row["client_counts"] == {1},
                    f"{backend}: client count = 1 "
                    f"({sorted(row['client_counts'])}; -1 means not recorded)",
                ),
                # config_arrival_rate is copied from the environment whether or
                # not anything paced the run. The sync client ignores it and
                # runs a send-and-wait, so this is the check that makes the
                # recorded rate mean what the report says it means.
                (
                    row["sync_values"] == {False},
                    f"{backend}: async fixed-rate client, so the arrival rate was "
                    f"actually scheduled (config_use_sync="
                    f"{[str(v) for v in row['sync_values']]})",
                ),
                (
                    abs(achieved - args.expected_rps) <= args.expected_rps * 0.05,
                    f"{backend}: achieved rate within 5% of {args.expected_rps:g} "
                    f"({achieved:.1f})",
                ),
            ])
            # retry_calls is read from the Rust binding's own counter, so a
            # core-Python row reports 0 whether or not core Python retried.
            # Gating on it there would manufacture a passing check out of an
            # uninstrumented backend, so the check is scoped to Rust and the
            # gap is printed rather than hidden.
            if "rust" in backend.lower():
                checks.append(
                    (
                        row["retry_calls"] == 0,
                        f"{backend}: recorded non-initial requests = 0 ({row['retry_calls']})",
                    )
                )
                notes.append(
                    f"  [note] {backend}: retry_calls counts retained non-initial records only; "
                    "zero does not prove that no retry occurred"
                )
            else:
                notes.append(
                    f"  [n/a] {backend}: driver retries not instrumented "
                    "(retry_calls comes from the Rust binding only), so this "
                    "row's retry behaviour is unverified"
                )
        read = agg.get(("read", "rust"))
        if read is not None:
            checks.append(
                (
                    _pctile_ms(read, 99) < args.max_p99_ms,
                    f"rust: p99 < {args.max_p99_ms:g} ms "
                    f"({_pctile_ms(read, 99):.2f} ms)",
                )
            )
        latency_ok = latency_ok and all(ok for ok, _ in checks)
        print("\n### POINT-READ GATE ###")
        for ok, message in checks:
            print(f"  [{'PASS' if ok else 'FAIL'}] {message}")
        for message in notes:
            print(message)
        print("### POINT-READ GATE:", "PASS" if latency_ok else "FAIL", "###")

    sys.exit(0 if commit_ok and latency_ok else 1)


if __name__ == "__main__":
    main()
