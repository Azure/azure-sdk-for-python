# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Automated scaling verdict for the throughput sweep.

Reading a knee off a chart by eye is subjective and unreproducible. This script
turns the sweep rows into an explicit verdict per (op, backend):

  1. Pooled throughput per concurrency point: SUM(count)/SUM(window_seconds) over
     post-warmup windows, never the max or last of a single window.

  2. Automated knee. Walking the concurrency ladder, the first level whose
     throughput gain over the previous level falls below KNEE_GAIN (default 5%) is
     the plateau, the single-process saturation point. If throughput is still
     climbing at the top of the ladder we report NO PLATEAU REACHED.

  3. Saturation flags. A point is only a trustworthy ceiling if it is not error- or
     CPU-bound: we flag err% > MAX_ERR_PCT or system CPU > MAX_SYS_CPU so host
     saturation is not mistaken for the SDK's limit.

  4. Crossover. Per op, the rust-vs-core throughput ratio across shared concurrency
     levels (geomean and range).

  5. Backend match check (enforced, exits non-zero). Every point's runtime_backend must
     match its config_backend label, so a "rust" point that fell back to
     core-python is never reported as a rust ceiling. Empty reporting windows
     (count 0/None, e.g. cold-start or idle intervals) carry no engine label and
     are ignored; a point with no non-empty window at all fails the gate.

USAGE:
  source ./perf_env.sh                        # exports RESULTS_COSMOS_* (incl. key)
  python3 scale_verdict.py [--stamp YYYYMMDD-HHMMSS] [--prefix sweep-] \
      [--warmup 600] [--knee-gain 0.05]

EXIT CODE:
  0 = backend match check passed (the scaling verdict is trustworthy).
  1 = backend match check failed (a point's runtime_backend did not match its label).
  2 = configuration error (env vars not set, no rows for the stamp).
"""

import argparse
import math
import os
import sys

import perf_driver_commit_gate as _driver_gate

try:
    from azure.cosmos import CosmosClient
except ImportError:
    print("ERROR: azure-cosmos is required (pip install azure-cosmos).", file=sys.stderr)
    sys.exit(2)

WARMUP_S = 600          # harness default: drop the first 10 min of each point.
KNEE_GAIN = 0.05        # <5% throughput gain over the previous level => plateau.
MAX_ERR_PCT = 0.5       # a point above this error fraction is not a clean ceiling.
MAX_SYS_CPU = 85.0      # system CPU above this means host-bound, not SDK-bound.

# runtime_backend (live class) each config_backend label must resolve to.
_EXPECTED_RUNTIME = {"core-python": {"core-python"}, "rust": {"AsyncRustBackend"}}


def geomean(xs):
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else 0.0


def parse_wid(wid):
    """sweep-<op>-<backend>-c<N>-<stampdate>-<stamptime> -> (op, backend, conc)."""
    body = wid[len("sweep-"):]
    fields = body.split("-")
    core = fields[:-2]                       # strip the 2-field stamp
    cidx = max(i for i, f in enumerate(core) if f.startswith("c") and f[1:].isdigit())
    op = core[0]
    conc = int(core[cidx][1:])
    backend = "-".join(core[1:cidx])
    return op, backend, conc


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


def _stamp_of(workload_id: str) -> str:
    parts = (workload_id or "").rsplit("-", 2)
    return parts[-2] + "-" + parts[-1] if len(parts) >= 2 else ""


def _latest_stamp(container, prefix: str) -> str:
    ids = list(
        container.query_items(
            "SELECT VALUE c.workload_id FROM c WHERE STARTSWITH(c.workload_id, @p)",
            parameters=[{"name": "@p", "value": prefix}],
            enable_cross_partition_query=True,
        )
    )
    stamps = {_stamp_of(i) for i in ids if i}
    stamps.discard("")
    return max(stamps) if stamps else ""


def main():
    ap = argparse.ArgumentParser(description="Automated scaling verdict.")
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--prefix", default="sweep-", help="workload_id prefix (default 'sweep-')")
    ap.add_argument("--warmup", type=float, default=WARMUP_S, help="warmup seconds to drop")
    ap.add_argument("--knee-gain", type=float, default=KNEE_GAIN,
                    help="fractional throughput gain below which a level is a plateau")
    _driver_gate.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_stamp(container, args.prefix)
    if not stamp:
        print(f"ERROR: no rows found for prefix '{args.prefix}'.", file=sys.stderr)
        sys.exit(2)
    print(f"=== Scaling verdict for stamp {stamp} (prefix '{args.prefix}') ===")
    print(f"    warmup-drop={args.warmup:.0f}s  knee-gain<{args.knee_gain*100:.0f}%  "
          f"err-flag>{MAX_ERR_PCT}%  syscpu-flag>{MAX_SYS_CPU:.0f}%")

    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.config_backend, c.operation, c.runtime_backend, "
            "c.elapsed_seconds, c.window_seconds, c.count, c.errors, "
            "c.ru_sum, c.ru_count, c.system_cpu_percent, c.p99_ms, c.driver_commit "
            "FROM c WHERE STARTSWITH(c.workload_id, @p) AND ENDSWITH(c.workload_id, @s)",
            parameters=[
                {"name": "@p", "value": args.prefix},
                {"name": "@s", "value": stamp},
            ],
            enable_cross_partition_query=True,
        )
    )
    if not rows:
        print(f"ERROR: no result rows for stamp {stamp}.", file=sys.stderr)
        sys.exit(2)

    # Group post-warmup windows per (op, backend, concurrency).
    cells = {}
    labels = {}
    for r in rows:
        wid = r.get("workload_id") or ""
        try:
            op, bk, conc = parse_wid(wid)
        except (ValueError, IndexError):
            continue
        key = (op, bk, conc)
        cells.setdefault(key, []).append(r)
        labels.setdefault(key, {})
        # Only rows that actually executed operations carry a meaningful engine
        # label. Empty reporting windows (count 0/None) -- e.g. cold-start or idle
        # intervals -- legitimately record runtime_backend=None; counting them here
        # would falsely trip the purity gate even though no work ran on a wrong
        # engine. Attribute the label only when the window did real work.
        if r.get("count"):
            rb = r.get("runtime_backend")
            labels[key][rb] = labels[key].get(rb, 0) + 1

    # ---- backend match check (enforced) ----
    print("\n### GATE: backend purity per (op, backend, concurrency) ###")
    gate_fail = False
    for key in sorted(labels):
        op, bk, conc = key
        expected = _EXPECTED_RUNTIME.get(bk)
        seen = labels[key]
        if not seen:
            # No non-empty window ran for this point: there is no engine evidence
            # to trust, which is itself a failure (a ceiling with no real data).
            gate_fail = True
            print(f"  FAIL {op} {bk} c{conc}: no non-empty windows -- no runtime_backend evidence")
            continue
        if expected is None or any(rb not in expected for rb in seen):
            gate_fail = True
            exp = "/".join(sorted(expected)) if expected else "??"
            print(f"  FAIL {op} {bk} c{conc}: runtime_backend={seen} (expected all '{exp}')")
    if not gate_fail:
        print("  OK -- every point's runtime_backend matches its config_backend label.")

    # ---- Rust driver commit check (enforced; scoped to rust rows) ----
    commit_ok, commit_lines = _driver_gate.evaluate(rows, strict=_driver_gate.strict_from(args))
    print()
    for _l in commit_lines:
        print(_l)

    # Reduce each cell to a pooled point.
    points = {}
    for key, rs in cells.items():
        post = [r for r in rs if (r.get("elapsed_seconds") or 0) > args.warmup]
        if not post:
            continue
        cnt = sum(r.get("count") or 0 for r in post)
        wsec = sum(r.get("window_seconds") or 0 for r in post)
        err = sum(r.get("errors") or 0 for r in post)
        ru = sum(r.get("ru_sum") or 0 for r in post)
        ruc = sum(r.get("ru_count") or 0 for r in post)
        if wsec <= 0:
            continue
        points[key] = {
            "n": len(post),
            "thr": cnt / wsec,
            "rups": ru / wsec if wsec else 0.0,
            "ru_op": (ru / ruc) if ruc else 0.0,
            "err_pct": 100.0 * err / (cnt + err) if (cnt + err) else 0.0,
            "syscpu": max((r.get("system_cpu_percent") or 0) for r in post),
            "p99": max((r.get("p99_ms") or 0) for r in post),
        }

    ops = sorted({k[0] for k in points})
    for op in ops:
        backends = sorted({k[1] for k in points if k[0] == op})
        print(f"\n### {op} ###")
        print(f"{'backend':11s} {'conc':>5s} {'pts':>4s} {'ops/s':>9s} {'RU/s':>9s} "
              f"{'RU/op':>6s} {'err%':>6s} {'sys%':>5s} {'p99ms':>7s}  note")
        for bk in backends:
            ladder = sorted([k[2] for k in points if k[0] == op and k[1] == bk])
            prev = None
            knee_conc = None
            for conc in ladder:
                p = points[(op, bk, conc)]
                note = []
                if prev is not None and prev > 0:
                    gain = (p["thr"] - prev) / prev
                    if gain < args.knee_gain and knee_conc is None:
                        knee_conc = conc
                        note.append("<- plateau (knee)")
                prev = p["thr"]
                if p["err_pct"] > MAX_ERR_PCT:
                    note.append("ERR")
                if p["syscpu"] > MAX_SYS_CPU:
                    note.append("CPU")
                print(f"{bk:11s} {conc:>5d} {p['n']:>4d} {p['thr']:>9.0f} {p['rups']:>9.0f} "
                      f"{p['ru_op']:>6.1f} {p['err_pct']:>6.2f} {p['syscpu']:>5.0f} "
                      f"{p['p99']:>7.1f}  {' '.join(note)}")
            # verdict line for this backend
            if ladder:
                peak = max(ladder, key=lambda c: points[(op, bk, c)]["thr"])
                pk = points[(op, bk, peak)]
                if knee_conc is not None:
                    kp = points[(op, bk, knee_conc)]
                    print(f"    -> {bk}: saturates at concurrency {knee_conc} "
                          f"(~{kp['thr']:,.0f} ops/s, {kp['rups']:,.0f} RU/s); "
                          f"peak ~{pk['thr']:,.0f} ops/s at c{peak}.")
                else:
                    print(f"    -> {bk}: NO PLATEAU REACHED -- still gaining >"
                          f"{args.knee_gain*100:.0f}% at top of ladder (c{peak}, "
                          f"~{pk['thr']:,.0f} ops/s). Extend the ladder to find the ceiling.")
        # crossover: rust vs core across shared levels
        if "rust" in backends and "core-python" in backends:
            common = sorted({k[2] for k in points if k[0] == op and k[1] == "rust"}
                            & {k[2] for k in points if k[0] == op and k[1] == "core-python"})
            sp = []
            for conc in common:
                ct = points[(op, "core-python", conc)]["thr"]
                if ct > 0:
                    sp.append(points[(op, "rust", conc)]["thr"] / ct)
            if sp:
                print(f"    -> rust/core throughput: geomean {geomean(sp):.2f}x "
                      f"(range {min(sp):.2f}-{max(sp):.2f}x) across {len(sp)} shared level(s).")

    overall_fail = gate_fail or not commit_ok
    print("\n### GATE:", "FAIL" if overall_fail else "PASS",
          "(backend purity + rust driver commit) ###")
    sys.exit(1 if overall_fail else 0)


if __name__ == "__main__":
    main()
