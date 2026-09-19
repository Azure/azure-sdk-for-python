# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Report early timed SDK calls in fresh processes, not total startup latency.

Client construction, asynchronous entry and the workload's initial sleep precede
these timers. Lazy setup may still occur during the calls. Each process has its
own workload ID; repeated cold snapshots are deduplicated by process identity.
Failed-call runs cannot establish the first call from successful durations alone.
The launcher uses concurrency one so completion order also describes call order.

USAGE:
  source ./perf_env.sh
  python3 coldstart_report.py [--stamp YYYYMMDD-HHMMSS] [--prefix cold-]
"""

import argparse
import math
import sys

import perf_driver_commit_gate as _driver_gate
from latency_report import _connect, _latest_run_id, _split_wid
from perf_results import OPERATIONS, split_workload_id, summary_rows

_OP_ORDER = ["read", "create", "upsert", "replace", "delete", "patch"]


def _pct(sorted_vals, q):
    """Nearest-rank percentile of a small sorted list (ms)."""
    if not sorted_vals:
        return float("nan")
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    idx = math.ceil((q / 100.0) * len(sorted_vals)) - 1
    idx = max(0, min(idx, len(sorted_vals) - 1))
    return sorted_vals[idx]


def _aggregate(container, prefix, stamp):
    """Return per_cell[(backend, op)] with first-call samples + warm-up curves.

    Scoped by BOTH prefix (STARTSWITH) and stamp (ENDSWITH) so a same-second stamp
    under another prefix cannot leak in.
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
    cells = {}
    total_rows = 0
    no_first_rows = 0
    prov_commits, prov_missing, prov_rust = set(), 0, 0
    seen = {}
    for r in summary_rows(rows):
        total_rows += 1
        op, backend, _ = split_workload_id(r["workload_id"], prefix)
        if r.get("operation") != OPERATIONS.get(op):
            continue
        if "rust" in backend.lower():
            prov_rust += 1
            _dc = str(r.get("driver_commit") or "").strip()
            if _driver_gate.is_stamped_commit(_dc):
                prov_commits.add(_dc)
            else:
                prov_missing += 1
        first = r.get("cold_first_ms")
        if not r.get("process_id"):
            raise ValueError("Cold samples require process_id; historical rows cannot establish one sample per process")
        key = (backend, op, r["process_id"])
        if r["errors"]:
            raise ValueError("Cold workload had failures; first success is not the first call")
        if first is None:
            no_first_rows += 1
            continue  # a row with no cold sample (e.g. an all-errors flush)
        if key in seen:
            if seen[key]["cold_first_ms"] != first:
                raise ValueError("Conflicting first-call samples for one process")
            if len(r.get("cold_first_n_ms") or []) > len(seen[key].get("cold_first_n_ms") or []):
                seen[key] = r
            continue
        seen[key] = r
    for (backend, op, _process), r in seen.items():
        cell = cells.get((backend, op))
        if cell is None:
            cell = cells[(backend, op)] = {"firsts": [], "curves": []}
        cell["firsts"].append(float(r["cold_first_ms"]))
        curve = r.get("cold_first_n_ms") or []
        if curve:
            cell["curves"].append([float(v) for v in curve])
    return (
        cells,
        (sorted(prov_commits), prov_missing, prov_rust),
        (total_rows, no_first_rows),
    )


def _warmup_curve(curves, max_points=10):
    """Element-wise mean across processes: position i = mean latency of call #i+1."""
    if not curves:
        return []
    n = min(max_points, max(len(c) for c in curves))
    out = []
    for i in range(n):
        vals = [c[i] for c in curves if len(c) > i]
        if vals:
            out.append(sum(vals) / len(vals))
    return out


def _fmt_cell(op, cell):
    firsts = sorted(cell["firsts"])
    curve = _warmup_curve(cell["curves"])
    curve_txt = " ".join(f"{v:.2f}" for v in curve)
    return (
        f"  {op:8s} procs={len(firsts):>4d}  "
        f"first-call p50={_pct(firsts,50):>7.2f} p90={_pct(firsts,90):>7.2f} "
        f"p99={_pct(firsts,99):>7.2f} max={firsts[-1]:>7.2f}\n"
        f"           warm-up (call #1..#{len(curve)} mean ms): {curve_txt}"
    )


def main():
    ap = argparse.ArgumentParser(
        description="Cold-start report: first-call latency + warm-up curve per op/backend."
    )
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--prefix", default="cold-", help="workload_id prefix (default cold-)")
    _driver_gate.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_run_id(container, args.prefix)
    if not stamp:
        print(f"ERROR: no {args.prefix}* runs found in the results container.", file=sys.stderr)
        sys.exit(2)

    cells, prov_info, sample_info = _aggregate(container, args.prefix, stamp)
    if not cells:
        print(
            f"ERROR: no cold-start rows (with cold_first_ms) found for stamp {stamp}.",
            file=sys.stderr,
        )
        sys.exit(2)

    backends = sorted({b for (b, _) in cells})
    print(f"=== Cold-start report (prefix {args.prefix}, stamp {stamp}) ===")
    print("    Each process = one first-call sample; percentiles pool across processes.")
    print("    Warm-up curve = element-wise mean of the earliest calls (settle point).")
    total_rows, no_first_rows = sample_info
    print(f"    rows seen={total_rows} rows_without_cold_sample={no_first_rows}")
    print()

    for backend in backends:
        print(f"-- backend: {backend} --")
        for op in _OP_ORDER:
            cell = cells.get((backend, op))
            if cell and cell["firsts"]:
                print(_fmt_cell(op, cell))
        print()

    if "core-python" in backends and "rust" in backends:
        print("-- first timed SDK-call p50 head to head (excludes client startup) --")
        for op in _OP_ORDER:
            py = cells.get(("core-python", op))
            ru = cells.get(("rust", op))
            if not (py and ru and py["firsts"] and ru["firsts"]):
                continue
            print(
                f"  {op:8s} core-python={_pct(sorted(py['firsts']),50):>7.2f}ms  "
                f"rust={_pct(sorted(ru['firsts']),50):>7.2f}ms"
            )
        print()

    commits, missing, rust_rows = prov_info
    commit_ok, commit_lines = _driver_gate.decide(
        commits, missing, rust_rows, strict=_driver_gate.strict_from(args)
    )
    for _l in commit_lines:
        print(_l)
    print("\n### GATE:", "FAIL" if not commit_ok else "PASS", "(rust driver commit) ###")
    sys.exit(0 if commit_ok else 1)


if __name__ == "__main__":
    main()
