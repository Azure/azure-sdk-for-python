# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Mixed (blended) workload report: per-operation and blended pooled percentiles.

A single-operation run measures one operation type in isolation. Real applications
send a mix (mostly reads, some creates/upserts, a few replaces/patches). A blended
run (WORKLOAD_MIX) issues that mix from one process, so a run can be gated on one
blended p99 instead of the fastest operation's p99.

This script prints two things:
  1. a per-operation table (each op's pooled p50/p90/p99/p99.9), and
  2. a blended distribution that pools every operation together, the headline SLA
     number for the mix.

Pooling: each row stores ``hist_b64``, the full histogram for that window.
Percentiles cannot be averaged across windows, so this script merges the
histograms -- per operation for the per-op table, and across all operations of a
backend for the blended distribution -- and the printed values are exact for the
whole run. Grouping is by the row's ``operation`` field (the op actually run), not
the workload_id: a blended run shares one workload_id
(``mixed-blend-<backend>-<stamp>``), so the operation must come from the row.

USAGE:
  source ./perf_env.sh
  python3 mixed_report.py [--stamp YYYYMMDD-HHMMSS] [--prefix mixed-]
"""

import argparse
import sys

import perf_provenance_gate as _prov
from phase0_report import (
    HdrHistogram,
    MAX_US,
    MIN_US,
    _connect,
    _latest_stamp,
    _split_wid,
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
    }


def _add_row(cell, r, c):
    cell["count"] += c
    cell["errors"] += int(r.get("errors", 0) or 0)
    cell["throttled_429"] += int(r.get("throttled_429", 0) or 0)
    cell["window_s"] += float(r.get("window_seconds", 0.0) or 0.0)
    mr = float(r.get("mean_ru", 0.0) or 0.0)
    if mr:
        cell["ru_weighted"] += mr * c
        cell["ru_count"] += c
    hb = r.get("hist_b64")
    if hb:
        cell["hist"].decode_and_add(hb)
    else:
        cell["no_hist_windows"] += 1


def _aggregate(container, prefix, stamp):
    """Return per_op[(backend, op)] and blended[backend], both pooled histograms.

    Scoped by BOTH prefix (STARTSWITH) and stamp (ENDSWITH) so no other run that
    happened to land on the same-second stamp under a different prefix leaks in.
    """
    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.operation, c.count, c.errors, c.throttled_429, "
            "c.window_seconds, c.hist_b64, c.mean_ru, c.driver_commit "
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
    for r in rows:
        # backend comes from the workload_id; the real operation comes from the row.
        _wop, backend, _ = _split_wid(r["workload_id"])
        op = _canon_op(r.get("operation"))
        if not backend or not op:
            continue
        c = int(r.get("count", 0) or 0)
        if backend and "rust" in backend.lower():
            prov_rust += 1
            _dc = str(r.get("driver_commit") or "").strip()
            if _dc:
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
    return per_op, blended, (sorted(prov_commits), prov_missing, prov_rust)


def _pctile_ms(cell, q):
    if cell["count"] <= 0:
        return float("nan")
    return cell["hist"].get_value_at_percentile(q) / 1000.0


def _fmt(label, cell):
    rps = cell["count"] / cell["window_s"] if cell["window_s"] else 0.0
    ru = cell["ru_weighted"] / cell["ru_count"] if cell["ru_count"] else 0.0
    note = "" if cell["no_hist_windows"] == 0 else (
        f"  [!] {cell['no_hist_windows']} window(s) lacked hist_b64 (approx)"
    )
    return (
        f"  {label:16s} count={cell['count']:>10d} err={cell['errors']:>5d} "
        f"429={cell['throttled_429']:>5d} rps={rps:>8.1f} "
        f"p50={_pctile_ms(cell,50):>6.2f} p90={_pctile_ms(cell,90):>6.2f} "
        f"p99={_pctile_ms(cell,99):>6.2f} p99.9={_pctile_ms(cell,99.9):>7.2f} "
        f"RU/op={ru:>6.2f}{note}"
    )


def main():
    ap = argparse.ArgumentParser(
        description="Mixed/blended workload report (per-op + blended pooled percentiles)."
    )
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--prefix", default="mixed-", help="workload_id prefix (default mixed-)")
    _prov.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_stamp(container, args.prefix)
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
    print("    across windows from merged HdrHistograms (exact).")
    print()

    for backend in backends:
        print(f"-- backend: {backend} --")
        for op in _OP_ORDER:
            cell = per_op.get((backend, op))
            if cell:
                print(_fmt(op, cell))
        # The blended line is the headline SLA number for the mix.
        print(_fmt("BLENDED (all)", blended[backend]))
        print()

    if "core-python" in backends and "rust" in backends:
        py, ru = blended["core-python"], blended["rust"]
        print("-- blended p99 head to head (the SLA number for the mix) --")
        print(
            f"  core-python p99={_pctile_ms(py,99):.2f}ms p99.9={_pctile_ms(py,99.9):.2f}ms  |  "
            f"rust p99={_pctile_ms(ru,99):.2f}ms p99.9={_pctile_ms(ru,99.9):.2f}ms"
        )
        print()

    commits, missing, rust_rows = prov_info
    prov_ok, prov_lines = _prov.decide(
        commits, missing, rust_rows, strict=_prov.strict_from(args)
    )
    for _l in prov_lines:
        print(_l)
    print("\n### GATE:", "FAIL" if not prov_ok else "PASS", "(rust driver provenance) ###")
    sys.exit(0 if prov_ok else 1)


if __name__ == "__main__":
    main()
