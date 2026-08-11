# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Scale-out report: how far throughput scales past one process.

The single-process sweep (scale_verdict.py) finds each engine's per-process
ceiling and knee concurrency C*. This script runs N copies of the workload at C*
and sums their achieved req/s into a per-N throughput curve.

  1. Per-process throughput = SUM(count)/SUM(window_seconds) over that process's
     post-warmup windows, never a single window's max or last. Each of the N
     processes writes its own rows (unique workload_id ...-pI-...), pooled per
     point rather than averaged.

  2. Point throughput at N = sum of the N processes' throughputs. They run
     concurrently over the same wall-clock window, so the sum is the account's
     achieved aggregate req/s at that fan-out.

  3. Scaling efficiency = thr(N) / (N * thr(1)). 1.0 is perfect linear scaling;
     below 1.0 the account or host is bottlenecking. Achieved RU/s, terminal
     error %, and system CPU are printed so a plateau can be attributed to the RU
     ceiling, host CPU, or the SDK. A per-window 429 counter is not used because
     the Rust driver retries throttles internally; achieved RU/s vs provisioned is
     the ceiling signal instead.

  4. Repeatability. Reruns of the same point (...-rR-...) are pooled and their
     spread (min..max) printed.

  5. Backend match check (enforced, exits non-zero). Every row's runtime_backend must
     match its config_backend label, and the azure-sdk-for-rust driver commit is
     printed; a mixed-build curve is called out, not silently pooled.

USAGE:
  source ./perf_env.sh                        # exports RESULTS_COSMOS_* (incl. key)
  python3 scaleout_report.py [--stamp YYYYMMDD-HHMMSS] [--prefix scaleout-] \
      [--warmup 600]

EXIT CODE:
  0 = backend match check passed (the scale-out curve is trustworthy).
  1 = backend match check failed (a row's runtime_backend did not match its label).
  2 = configuration error (env vars not set, no rows for the stamp).
"""

import argparse
import os
import sys

import perf_driver_commit_gate as _driver_gate

try:
    from azure.cosmos import CosmosClient
except ImportError:
    print("ERROR: azure-cosmos is required (pip install azure-cosmos).", file=sys.stderr)
    sys.exit(2)

WARMUP_S = 600          # drop the first 10 min of each process so warmup never counts.
MAX_ERR_PCT = 0.5       # a point above this error fraction is not a clean data point.
MAX_SYS_CPU = 85.0      # system CPU above this means host-bound, not account-bound.

# runtime_backend (live class) each config_backend label must resolve to.
_EXPECTED_RUNTIME = {"core-python": {"core-python"}, "rust": {"AsyncRustBackend"}}


def parse_wid(wid, prefix="scaleout-"):
    """scaleout-<op>-<backend>-c<C>-N<N>-r<R>-p<i>-<stampdate>-<stamptime>
    -> (op, backend, conc, nprocs, rep, pidx). backend may contain dashes."""
    body = wid[len(prefix):]
    core = body.split("-")[:-2]             # strip the 2-field stamp
    c_tok, n_tok, r_tok, p_tok = core[-4], core[-3], core[-2], core[-1]
    if not (c_tok.startswith("c") and n_tok.startswith("N")
            and r_tok.startswith("r") and p_tok.startswith("p")):
        raise ValueError(f"unexpected scale-out workload_id shape: {wid}")
    conc = int(c_tok[1:])
    nprocs = int(n_tok[1:])
    rep = int(r_tok[1:])
    pidx = int(p_tok[1:])
    op = core[0]
    backend = "-".join(core[1:-4])
    return op, backend, conc, nprocs, rep, pidx


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


def _latest_stamp(container, prefix):
    wids = list(
        container.query_items(
            "SELECT VALUE c.workload_id FROM c WHERE STARTSWITH(c.workload_id, @p)",
            parameters=[{"name": "@p", "value": prefix}],
            enable_cross_partition_query=True,
        )
    )
    stamps = set()
    for w in wids:
        parts = (w or "").split("-")
        if len(parts) >= 2:
            stamps.add("-".join(parts[-2:]))
    return max(stamps) if stamps else None


def main():
    ap = argparse.ArgumentParser(description="Scale-out report.")
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--prefix", default="scaleout-", help="workload_id prefix (default scaleout-)")
    ap.add_argument("--warmup", type=float, default=WARMUP_S,
                    help=f"drop windows with elapsed_seconds <= this (default {WARMUP_S:.0f})")
    _driver_gate.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_stamp(container, args.prefix)
    if not stamp:
        print(f"ERROR: no rows found for prefix '{args.prefix}'.", file=sys.stderr)
        sys.exit(2)
    print(f"=== Scale-out report for stamp {stamp} (prefix '{args.prefix}') ===")
    print(f"    warmup-drop<={args.warmup:.0f}s  err-flag>{MAX_ERR_PCT}%  syscpu-flag>{MAX_SYS_CPU:.0f}%")

    rows = list(
        container.query_items(
            "SELECT c.workload_id, c.config_backend, c.operation, c.runtime_backend, "
            "c.elapsed_seconds, c.window_seconds, c.count, c.errors, "
            "c.ru_sum, c.ru_count, c.system_cpu_percent, c.driver_commit "
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

    # (op, bk, N, rep, pidx) -> pooled per-process post-warmup measurement.
    procs = {}
    labels = {}                               # (op, bk) -> {runtime_backend: count}
    for r in rows:
        wid = r.get("workload_id") or ""
        try:
            op, bk, conc, nprocs, rep, pidx = parse_wid(wid, args.prefix)
        except (ValueError, IndexError):
            continue
        # Only rows that actually did work carry a meaningful engine label; empty
        # windows legitimately record runtime_backend=None and must not trip the gate.
        if r.get("count"):
            labels.setdefault((op, bk), {})
            rb = r.get("runtime_backend")
            labels[(op, bk)][rb] = labels[(op, bk)].get(rb, 0) + 1
        if (r.get("elapsed_seconds") or 0) <= args.warmup:
            continue
        d = procs.setdefault((op, bk, nprocs, rep, pidx),
                             {"cnt": 0, "wsec": 0.0, "err": 0, "ru": 0.0,
                              "ruc": 0, "syscpu": 0.0})
        d["cnt"] += r.get("count") or 0
        d["wsec"] += r.get("window_seconds") or 0.0
        d["err"] += r.get("errors") or 0
        d["ru"] += r.get("ru_sum") or 0.0
        d["ruc"] += r.get("ru_count") or 0
        d["syscpu"] = max(d["syscpu"], r.get("system_cpu_percent") or 0)

    # ---- backend match check (enforced) ----
    print("\n### GATE: backend purity per (op, backend) ###")
    gate_fail = False
    for (op, bk), seen in sorted(labels.items()):
        expected = _EXPECTED_RUNTIME.get(bk)
        if expected is None or any(rb not in expected for rb in seen):
            gate_fail = True
            exp = "/".join(sorted(expected)) if expected else "??"
            print(f"  FAIL {op} {bk}: runtime_backend={seen} (expected all '{exp}')")
    if not gate_fail:
        print("  OK -- every row's runtime_backend matches its config_backend label.")

    # ---- Rust driver commit check (enforced; scoped to rust rows) ----
    commit_ok, commit_lines = _driver_gate.evaluate(rows, strict=_driver_gate.strict_from(args))
    print()
    for _l in commit_lines:
        print(_l)

    # Point throughput per (op, bk, N, rep) = SUM of the N processes' throughputs.
    point = {}
    for (op, bk, nprocs, rep, pidx), d in procs.items():
        if d["wsec"] <= 0:
            continue
        p = point.setdefault((op, bk, nprocs, rep),
                             {"thr": 0.0, "rups": 0.0, "cnt": 0, "err": 0,
                              "ru": 0.0, "ruc": 0, "syscpu": 0.0, "nseen": 0})
        p["thr"] += d["cnt"] / d["wsec"]
        p["rups"] += d["ru"] / d["wsec"]
        p["cnt"] += d["cnt"]
        p["err"] += d["err"]
        p["ru"] += d["ru"]
        p["ruc"] += d["ruc"]
        p["syscpu"] = max(p["syscpu"], d["syscpu"])
        p["nseen"] += 1

    ops = sorted({k[0] for k in point})
    for op in ops:
        backends = sorted({k[1] for k in point if k[0] == op})
        print(f"\n### {op} ###")
        print(f"{'backend':11s} {'N':>4s} {'procs':>5s} {'reps':>4s} {'ops/s':>10s} "
              f"{'RU/s':>10s} {'RU/op':>6s} {'per-proc':>9s} {'eff':>5s} {'err%':>6s} "
              f"{'sys%':>5s}  note")
        for bk in backends:
            # Pool reps per N.
            ns = sorted({k[2] for k in point if k[0] == op and k[1] == bk})
            pooled = {}
            for n in ns:
                reps = [point[(op, bk, n, rp)] for (o2, b2, n2, rp) in point
                        if o2 == op and b2 == bk and n2 == n]
                thrs = [p["thr"] for p in reps]
                pooled[n] = {
                    "thr": sum(thrs) / len(thrs),
                    "thr_min": min(thrs),
                    "thr_max": max(thrs),
                    "rups": sum(p["rups"] for p in reps) / len(reps),
                    "ru_op": (sum(p["ru"] for p in reps) / sum(p["ruc"] for p in reps))
                             if sum(p["ruc"] for p in reps) else 0.0,
                    "err_pct": (100.0 * sum(p["err"] for p in reps)
                                / max(1, sum(p["cnt"] + p["err"] for p in reps))),
                    "syscpu": max(p["syscpu"] for p in reps),
                    "reps": len(reps),
                    "procs": max(p["nseen"] for p in reps),
                    "expected_procs": n,
                }
            base = pooled.get(1, {}).get("thr")
            for n in ns:
                pl = pooled[n]
                eff = (pl["thr"] / (n * base)) if base else 0.0
                note = []
                if pl["procs"] != pl["expected_procs"]:
                    note.append(f"ONLY {pl['procs']}/{pl['expected_procs']} PROCS")
                if pl["err_pct"] > MAX_ERR_PCT:
                    note.append("ERR")
                if pl["syscpu"] > MAX_SYS_CPU:
                    note.append("CPU")
                spread = ""
                if pl["reps"] > 1:
                    spread = f" [{pl['thr_min']:,.0f}-{pl['thr_max']:,.0f}]"
                print(f"{bk:11s} {n:>4d} {pl['procs']:>5d} {pl['reps']:>4d} "
                      f"{pl['thr']:>10,.0f} {pl['rups']:>10,.0f} {pl['ru_op']:>6.1f} "
                      f"{pl['thr']/max(1,pl['procs']):>9,.0f} {eff:>5.2f} {pl['err_pct']:>6.2f} "
                      f"{pl['syscpu']:>5.0f}  {' '.join(note)}{spread}")
            if ns:
                topn = max(ns)
                tp = pooled[topn]
                if base:
                    print(f"    -> {bk}: {tp['thr']:,.0f} ops/s at N={topn} "
                          f"(x{tp['thr']/base:,.1f} the single-process {base:,.0f} ops/s; "
                          f"efficiency {tp['thr']/(topn*base):.2f}).")

    overall_fail = gate_fail or not commit_ok
    print("\n### GATE:", "FAIL" if overall_fail else "PASS",
          "(backend purity + rust driver commit) ###")
    sys.exit(1 if overall_fail else 0)


if __name__ == "__main__":
    main()
