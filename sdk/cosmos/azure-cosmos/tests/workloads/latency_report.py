# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Low-load latency report: pooled percentiles per operation.

Reads the low-load probe rows (concurrency 1, one client, no proxy) and prints a
latency table per operation and backend. At one request in flight each number is a
single round trip, not a throughput figure.

Percentiles are pooled correctly. A per-window scalar percentile cannot be
averaged across windows, so each row also stores the full histogram for its window
(``hist_b64``). This script merges those histograms per cell and reads the
percentile off the merged result, so the printed values are exact for the whole
run. When a row has no ``hist_b64`` (an older run) the script says so per cell and
falls back to a count-weighted average, which understates the tail.

USAGE:
  source ./perf_env.sh                 # exports RESULTS_COSMOS_* (incl. the key)
  python3 latency_report.py [--run-id YYYYMMDD-HHMMSS] [--prefix baseline-]
      --run-id  which run to read; default = the most recent matching run.
      --prefix  workload_id prefix identifying the run (default baseline-).
"""

import argparse
import os
import sys

import perf_provenance_gate as _prov

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
    parts = workload_id.split("-")
    if len(parts) < 5:
        return None, None, ""
    run_id = parts[-2] + "-" + parts[-1]
    op = parts[1]
    backend = "-".join(parts[2:-2])
    return op, backend, run_id


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
            "SELECT c.workload_id, c.count, c.errors, c.throttled_429, "
            "c.window_seconds, c.hist_b64, c.mean_ru, c.p99_9_ms, c.driver_commit, "
            "c.config_arrival_rate, c.config_concurrency, c.config_proxy_enabled, "
            "c.attempt_calls, c.retry_calls "
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
    for r in rows:
        op, backend, _ = _split_wid(r["workload_id"])
        if op is None:
            continue
        key = (op, backend)
        if backend and "rust" in backend.lower():
            prov_rust += 1
            _dc = str(r.get("driver_commit") or "").strip()
            if _dc:
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
                "proxy_values": set(),
                "attempt_calls": 0,
                "retry_calls": 0,
            }
        c = int(r.get("count", 0) or 0)
        a["count"] += c
        a["errors"] += int(r.get("errors", 0) or 0)
        a["throttled_429"] += int(r.get("throttled_429", 0) or 0)
        a["arrival_rates"].add(float(r.get("config_arrival_rate", 0.0) or 0.0))
        a["concurrencies"].add(int(r.get("config_concurrency", 0) or 0))
        a["proxy_values"].add(bool(r.get("config_proxy_enabled", False)))
        a["attempt_calls"] += int(r.get("attempt_calls", 0) or 0)
        a["retry_calls"] += int(r.get("retry_calls", 0) or 0)
        a["window_s"] += float(r.get("window_seconds", 0.0) or 0.0)
        mr = float(r.get("mean_ru", 0.0) or 0.0)
        if mr:
            a["ru_weighted"] += mr * c
            a["ru_count"] += c
        hb = r.get("hist_b64")
        if hb:
            a["hist"].decode_and_add(hb)
        else:
            a["no_hist_windows"] += 1
            a["scalar_p999_weighted"] += float(r.get("p99_9_ms", 0.0) or 0.0) * c
    return agg, (sorted(prov_commits), prov_missing, prov_rust)


def _pctile_ms(a, q):
    """Pooled percentile in ms from the merged histogram (values are in µs)."""
    if a["count"] <= 0:
        return float("nan")
    return a["hist"].get_value_at_percentile(q) / 1000.0


def _mean_ms(a):
    """Pooled arithmetic mean in ms from the merged histogram."""
    if a["count"] <= 0:
        return float("nan")
    return a["hist"].get_mean_value() / 1000.0


def _fmt_cell(op, backend, a):
    rps = a["count"] / a["window_s"] if a["window_s"] else 0.0
    ru = a["ru_weighted"] / a["ru_count"] if a["ru_count"] else 0.0
    exact = a["no_hist_windows"] == 0
    note = "" if exact else f"  [!] {a['no_hist_windows']} window(s) lacked hist_b64 (approx)"
    return (
        f"  {op:8s} {backend:11s} count={a['count']:>9d} err={a['errors']:>4d} "
        f"429={a['throttled_429']:>4d} retries={a['retry_calls']:>4d} rps={rps:>8.1f} "
        f"mean={_mean_ms(a):>6.2f} p50={_pctile_ms(a,50):>6.2f} "
        f"p90={_pctile_ms(a,90):>6.2f} "
        f"p99={_pctile_ms(a,99):>6.2f} p99.9={_pctile_ms(a,99.9):>7.2f} "
        f"RU/op={ru:>6.2f}{note}"
    )


def main():
    ap = argparse.ArgumentParser(
        description="Low-load latency report (pooled percentiles)."
    )
    ap.add_argument("--run-id", default=None, help="run id YYYYMMDD-HHMMSSmmm (default: latest)")
    ap.add_argument("--stamp", dest="run_id", help=argparse.SUPPRESS)
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
    _prov.add_cli_flag(ap)
    args = ap.parse_args()

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
    print("    Fixed-rate arrivals, 1 client, no proxy; latency is end-to-end from scheduled arrival.")
    print("    Percentiles are POOLED across windows from merged HdrHistograms (exact).")
    print()

    for backend in backends:
        print(f"-- backend: {backend} --")
        for op in _OP_ORDER:
            a = agg.get((op, backend))
            if a:
                print(_fmt_cell(op, backend, a))
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

    # ---- Rust driver provenance gate (enforced; scoped to rust rows) ----
    commits, missing, rust_rows = prov_info
    prov_ok, prov_lines = _prov.decide(
        commits, missing, rust_rows, strict=_prov.strict_from(args)
    )
    print()
    for _l in prov_lines:
        print(_l)
    print("\n### GATE:", "FAIL" if not prov_ok else "PASS", "(rust driver provenance) ###")

    latency_ok = True
    if args.point_read_gate:
        checks = []
        read = agg.get(("read", "rust"))
        if read is None:
            checks.append((False, "Rust read row exists"))
        else:
            achieved_rps = read["count"] / read["window_s"] if read["window_s"] else 0.0
            checks.extend([
                (read["count"] > 0, f"successful reads > 0 ({read['count']})"),
                (read["errors"] == 0, f"errors = 0 ({read['errors']})"),
                (
                    read["throttled_429"] == 0,
                    f"terminal 429 responses = 0 ({read['throttled_429']})",
                ),
                (
                    read["retry_calls"] == 0,
                    f"driver retries = 0 ({read['retry_calls']})",
                ),
                (
                    read["no_hist_windows"] == 0,
                    f"all windows have histograms (missing={read['no_hist_windows']})",
                ),
                (
                    read["arrival_rates"] == {args.expected_rps},
                    f"configured arrival rate = {args.expected_rps:g} "
                    f"({sorted(read['arrival_rates'])})",
                ),
                (
                    read["proxy_values"] == {False},
                    f"proxy disabled ({sorted(read['proxy_values'])})",
                ),
                (
                    abs(achieved_rps - args.expected_rps) <= args.expected_rps * 0.05,
                    f"achieved rate within 5% of {args.expected_rps:g} "
                    f"({achieved_rps:.1f})",
                ),
                (
                    _pctile_ms(read, 99) < args.max_p99_ms,
                    f"Rust p99 < {args.max_p99_ms:g} ms "
                    f"({_pctile_ms(read, 99):.2f} ms)",
                ),
            ])
        latency_ok = all(ok for ok, _ in checks)
        print("\n### POINT-READ GATE ###")
        for ok, message in checks:
            print(f"  [{'PASS' if ok else 'FAIL'}] {message}")
        print("### POINT-READ GATE:", "PASS" if latency_ok else "FAIL", "###")

    sys.exit(0 if prov_ok and latency_ok else 1)


if __name__ == "__main__":
    main()
