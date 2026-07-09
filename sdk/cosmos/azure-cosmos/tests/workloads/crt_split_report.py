# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Client-vs-server latency split report: which layer owns a latency tail.

A point operation's client-side latency (wall clock at the caller) is network +
transport + the Python-to-Rust binding + the time the service spends processing
the request (server time). When one backend has a higher tail than another for the
same operation and account, this report shows which layer owns the extra time. The
service reports its own processing time in the ``x-ms-request-duration-ms``
response header, which both backends surface, so:

    client_tail - server_tail = everything outside the service
                                (network + transport + binding)

If the Rust create tail is high in client time but its server time matches
core-python's, the extra time is client-side, not the service. If the server tail
is also high, it is service variance and hits both backends. This script pools the
client histogram (``hist_b64``) and the server histogram (``server_hist_b64``) per
window across the run and prints both tails side by side.

USAGE:
  source ./perf_env.sh                 # exports RESULTS_COSMOS_* (incl. the key)
  python3 crt_split_report.py [--stamp YYYYMMDD-HHMMSS] [--prefix crepro-]
      --stamp   which run to read; default = the most recent <prefix> stamp.
      --prefix  workload_id prefix identifying the run (default crepro-).
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

try:
    from perf_stats import _MIN_VALUE_US as MIN_US, _MAX_VALUE_US as MAX_US
except Exception:  # pragma: no cover - perf_stats import is best-effort
    MIN_US, MAX_US = 1, 60_000_000

_OP_ORDER = ["read", "create", "upsert", "replace", "delete", "patch"]


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


def _split_wid(workload_id: str):
    """Return (op, backend, stamp) from ``<prefix><op>-<backend>-<YYYYMMDD-HHMMSS>``.

    The backend can itself contain a dash (``core-python``), so the stamp is the
    LAST two dash fields and the backend is everything between the op and stamp.
    """
    parts = workload_id.split("-")
    if len(parts) < 5:
        return None, None, ""
    stamp = parts[-2] + "-" + parts[-1]
    op = parts[1]
    backend = "-".join(parts[2:-2])
    return op, backend, stamp


def _latest_stamp(container, prefix: str) -> str:
    ids = list(
        container.query_items(
            "SELECT VALUE c.workload_id FROM c WHERE STARTSWITH(c.workload_id, @p)",
            parameters=[{"name": "@p", "value": prefix}],
            enable_cross_partition_query=True,
        )
    )
    stamps = {_split_wid(i)[2] for i in ids if i}
    stamps.discard("")
    return max(stamps) if stamps else ""


def _aggregate(container, prefix: str, stamp: str):
    """Merge every window of each (op, backend) cell into pooled client + server
    histograms. ``no_server_windows`` counts windows with no server_hist_b64 (an
    older run or a response with no x-ms-request-duration-ms header).

    Scoped by BOTH prefix (STARTSWITH) and stamp (ENDSWITH): filtering on the stamp
    alone would mix rows from any other run that shares the same-second stamp under
    a different prefix.
    """
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.count, c.errors, c.window_seconds, "
            "c.hist_b64, c.server_hist_b64, c.server_count, c.driver_commit "
            "FROM c WHERE STARTSWITH(c.workload_id, @prefix) "
            "AND ENDSWITH(c.workload_id, @stamp)",
            parameters=[
                {"name": "@prefix", "value": prefix},
                {"name": "@stamp", "value": stamp},
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
                "server_count": 0,
                "window_s": 0.0,
                "client": HdrHistogram(MIN_US, MAX_US, 3),
                "server": HdrHistogram(MIN_US, MAX_US, 3),
                "no_client_windows": 0,
                "no_server_windows": 0,
            }
        a["count"] += int(r.get("count", 0) or 0)
        a["errors"] += int(r.get("errors", 0) or 0)
        a["server_count"] += int(r.get("server_count", 0) or 0)
        a["window_s"] += float(r.get("window_seconds", 0.0) or 0.0)
        cb = r.get("hist_b64")
        if cb:
            a["client"].decode_and_add(cb)
        else:
            a["no_client_windows"] += 1
        sb = r.get("server_hist_b64")
        if sb:
            a["server"].decode_and_add(sb)
        else:
            a["no_server_windows"] += 1
    return agg, (sorted(prov_commits), prov_missing, prov_rust)


def _c(a, q):
    return a["client"].get_value_at_percentile(q) / 1000.0 if a["count"] else float("nan")


def _s(a, q):
    return (
        a["server"].get_value_at_percentile(q) / 1000.0
        if a["server_count"]
        else float("nan")
    )


def main():
    ap = argparse.ArgumentParser(description="Client-vs-server latency split report.")
    ap.add_argument("--stamp", default=None, help="run stamp (default: latest)")
    ap.add_argument("--prefix", default="crepro-", help="workload_id prefix (default crepro-)")
    _prov.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_stamp(container, args.prefix)
    if not stamp:
        print(f"ERROR: no {args.prefix}* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    agg, prov_info = _aggregate(container, args.prefix, stamp)
    if not agg:
        print(f"ERROR: no result rows found for stamp {stamp}.", file=sys.stderr)
        sys.exit(2)

    print(f"=== Client-vs-server latency split (prefix {args.prefix}, stamp {stamp}) ===")
    print("    CLIENT = wall clock at caller; SERVER = x-ms-request-duration-ms.")
    print("    gap = CLIENT - SERVER = network + transport + binding bridge (client-side).")
    print()
    backends = sorted({b for (_, b) in agg})
    for backend in backends:
        print(f"-- backend: {backend} --")
        print(
            f"  {'op':8s} {'count':>8s} {'srvN':>8s} "
            f"{'cli_p50':>8s} {'srv_p50':>8s} {'gap50':>7s} "
            f"{'cli_p99':>8s} {'srv_p99':>8s} {'gap99':>7s} "
            f"{'cli_999':>8s} {'srv_999':>8s} {'gap999':>7s}"
        )
        for op in _OP_ORDER:
            a = agg.get((op, backend))
            if not a:
                continue
            note = ""
            if a["no_server_windows"] and a["server_count"] == 0:
                note = "  [!] no server header (old harness / header absent)"
            print(
                f"  {op:8s} {a['count']:>8d} {a['server_count']:>8d} "
                f"{_c(a,50):>8.2f} {_s(a,50):>8.2f} {_c(a,50)-_s(a,50):>7.2f} "
                f"{_c(a,99):>8.2f} {_s(a,99):>8.2f} {_c(a,99)-_s(a,99):>7.2f} "
                f"{_c(a,99.9):>8.2f} {_s(a,99.9):>8.2f} {_c(a,99.9)-_s(a,99.9):>7.2f}"
                f"{note}"
            )
        print()

    # Head-to-head: for each op, is the Rust CLIENT tail excess (over its own
    # server time) larger than core-python's? That isolates a client-side tail.
    if "core-python" in backends and "rust" in backends:
        print("-- rust vs core-python: client-side excess = cli_999 - srv_999 --")
        print(f"  {'op':8s} {'py_excess':>10s} {'ru_excess':>10s} {'ru-py':>8s}")
        for op in _OP_ORDER:
            py = agg.get((op, "core-python"))
            ru = agg.get((op, "rust"))
            if not (py and ru):
                continue
            pe = _c(py, 99.9) - _s(py, 99.9)
            re = _c(ru, 99.9) - _s(ru, 99.9)
            print(f"  {op:8s} {pe:>10.2f} {re:>10.2f} {re-pe:>8.2f}")

    # ---- Rust driver provenance gate (enforced; scoped to rust rows) ----
    commits, missing, rust_rows = prov_info
    prov_ok, prov_lines = _prov.decide(
        commits, missing, rust_rows, strict=_prov.strict_from(args)
    )
    print()
    for _l in prov_lines:
        print(_l)
    print("\n### GATE:", "FAIL" if not prov_ok else "PASS", "(rust driver provenance) ###")
    sys.exit(0 if prov_ok else 1)


if __name__ == "__main__":
    main()
