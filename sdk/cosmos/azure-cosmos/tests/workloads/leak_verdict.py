# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Automated leak verdict for the leak sweep.

Judging a memory trace by eye is unreliable: a trace that steps up and then
plateaus looks flat, while a whole-run regression over the same trace reports a
fake slope because it spans the step. This script produces a reproducible verdict
per (config_backend, operation):

  1. Provenance gate (enforced, exits non-zero). Every row for a backend must
     carry the matching runtime_backend ('core-python' or 'AsyncRustBackend'). A
     blank or mismatched value means the engine is unproven, so the run fails.

  2. Shape-aware slope. The traces are staircases, so the leak signal is the slope
     of the final plateau (the last hour), not the whole run. We fit OLS over the
     tail and report the slope with its standard error and 95% confidence interval,
     plus a Theil-Sen robust slope as a cross-check.

  3. Step detection. We count discrete RSS jumps. A run that ends flat but stepped
     repeatedly is reported STAIRCASE, not "bounded", because one plateau cannot
     prove the next would not be higher.

  4. Rust vs core. Print final RSS and the tail slope for both engines side by
     side per operation.

USAGE:
  source ./perf_env.sh                      # exports RESULTS_COSMOS_* (incl. key)
  python3 leak_verdict.py [--stamp YYYYMMDD-HHMMSS] [--prefix leak-]
      --stamp   which run to judge; default = the most recent leak-* stamp.
      --prefix  workload_id prefix for the leak sweep (default 'leak-').

EXIT CODE:
  0 = provenance gate passed (verdicts are trustworthy).
  1 = provenance gate failed (blank/mismatched runtime_backend rows).
  2 = configuration error (env vars not set, no rows for the stamp).
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

# Recent-slope thresholds (MB/h) for the verdict. A point-op write loop sampled
# on 5-min windows: a tail slope whose 95% CI sits below ~2 MB/h is flat within
# allocator noise; a CI entirely above ~5 MB/h is genuine ongoing growth.
FLAT_MAX = 2.0
LEAK_MIN = 5.0
WARMUP_S = 600          # drop the first 10 min (warmup) before fitting anything.
TAIL_S = 3600           # the "final plateau" window the leak slope is measured on.
STEP_MB = 10.0          # an adjacent-window RSS jump this large counts as a step.

# Two-sided 95% t critical values by degrees of freedom (n-2). Embedded so we
# need no scipy; falls back to the normal approx (1.96) for df > 30.
_T95 = {1: 12.71, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
        8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160,
        14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093,
        20: 2.086, 21: 2.080, 22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060,
        26: 2.056, 27: 2.052, 28: 2.048, 29: 2.045, 30: 2.042}


def t_critical(df):
    """Two-sided 95% t multiplier for the given degrees of freedom."""
    if df <= 0:
        return None
    return _T95.get(df, 1.96)


def regress(pts):
    """OLS fit for [(elapsed_s, rss_MB)].

    Returns (slope_MB_per_h, r2, se_MB_per_h, ci95_halfwidth_MB_per_h, n).
    The standard error and CI are what let us call a near-zero slope
    *statistically* flat instead of merely small. Tuple of Nones if n < 3 or x
    has no spread.
    """
    if len(pts) < 3:
        return None, None, None, None, len(pts)
    xs = [e for e, _ in pts]
    ys = [m for _, m in pts]
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return None, None, None, None, n
    b = sxy / sxx                       # MB per second
    a = my - b * mx
    syy = sum((y - my) ** 2 for y in ys)
    r2 = (sxy * sxy) / (sxx * syy) if syy > 0 else 1.0
    sse = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    df = n - 2
    se_b = (sse / df / sxx) ** 0.5 if df > 0 else None      # MB per second
    tc = t_critical(df)
    half = (se_b * tc * 3600.0) if (se_b is not None and tc is not None) else None
    return b * 3600.0, r2, (se_b * 3600.0 if se_b is not None else None), half, n


def theil_sen(pts):
    """Robust slope (MB/h): the median of all pairwise slopes.

    Resistant to the discrete allocator *steps* in the trace, so it answers
    'ignoring the step jumps, is the floor drifting up?'.
    """
    if len(pts) < 3:
        return None
    slopes = []
    for i in range(len(pts)):
        xi, yi = pts[i]
        for j in range(i + 1, len(pts)):
            xj, yj = pts[j]
            if xj != xi:
                slopes.append((yj - yi) / (xj - xi))
    if not slopes:
        return None
    slopes.sort()
    m = len(slopes)
    med = slopes[m // 2] if m % 2 else 0.5 * (slopes[m // 2 - 1] + slopes[m // 2])
    return med * 3600.0


def settled_tail(pts, tail_seconds=TAIL_S):
    """OLS fit over only the final `tail_seconds` of the series.

    A whole-run regression spans a step and shows a misleading trend; the
    'is it growing now' signal is the slope of the final plateau. Returns a
    dict with slope, se, ci half-width, ci_lo/ci_hi, theil-sen, r2, n.
    """
    if not pts:
        return None
    t_end = pts[-1][0]
    tail = [p for p in pts if p[0] >= t_end - tail_seconds]
    slope, r2, se, half, n = regress(tail)
    if slope is None:
        return {"slope": None, "se": None, "half": None, "lo": None,
                "hi": None, "theil": theil_sen(tail), "r2": r2, "n": n}
    return {"slope": slope, "se": se, "half": half,
            "lo": slope - half if half is not None else None,
            "hi": slope + half if half is not None else None,
            "theil": theil_sen(tail), "r2": r2, "n": n}


def detect_steps(pts, step_mb=STEP_MB):
    """Count abrupt jumps: adjacent-window RSS deltas exceeding step_mb.

    Returns (n_steps, largest_step_mb, total_step_mb). A staircase shows a few
    large steps; smooth growth shows none (it is spread across many windows).
    """
    steps = [pts[i][1] - pts[i - 1][1] for i in range(1, len(pts))]
    big = [d for d in steps if d >= step_mb]
    return len(big), (max(big) if big else 0.0), sum(big)


def verdict(tail, n_steps):
    """Shape- and CI-aware verdict from the final-plateau fit and step count.

    Uses the 95% CI, not just the point estimate: 'flat' requires the slope CI
    upper bound below the leak threshold; 'growing' requires the CI lower bound
    above the flat threshold; anything straddling is WATCH.
    """
    if tail is None or tail.get("slope") is None:
        return "INCONCLUSIVE"
    slope = tail["slope"]
    hi = tail["hi"] if tail["hi"] is not None else slope
    lo = tail["lo"] if tail["lo"] is not None else slope
    if hi <= FLAT_MAX:
        # Confidently flat right now. But repeated large steps mean the next
        # plateau could be higher -- one run ending flat cannot prove bounded.
        return "PLATEAUED" if n_steps <= 1 else "STAIRCASE"
    if lo >= LEAK_MIN:
        return "GROWING"            # CI entirely above the leak threshold.
    return "WATCH"                  # CI straddles -- not yet conclusive.


def _glyph_or_fallback(glyph: str, fallback: str) -> str:
    """Return a display glyph only when stdout encoding can represent it."""
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        glyph.encode(enc)
    except UnicodeEncodeError:
        return fallback
    return glyph


_SPARK = _glyph_or_fallback("\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588", "..::--==")
# Keep this ASCII so output is stable across mixed Windows terminal encodings.
_PLUS_MINUS = "+/-"


def spark(ys):
    if not ys:
        return ""
    lo, hi = min(ys), max(ys)
    if hi == lo:
        return _SPARK[0] * len(ys)
    return "".join(_SPARK[min(len(_SPARK) - 1,
                    int((y - lo) / (hi - lo) * (len(_SPARK) - 1)))] for y in ys)


# runtime_backend (the live class) that each config_backend label must resolve
# to. A row that does not match -- or is None/blank -- fails the provenance gate.
_EXPECTED_RUNTIME = {"core-python": {"core-python"}, "rust": {"AsyncRustBackend"}}


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
    ap = argparse.ArgumentParser(description="Automated leak verdict.")
    ap.add_argument("--stamp", default=None, help="run stamp YYYYMMDD-HHMMSS (default: latest)")
    ap.add_argument("--prefix", default="leak-", help="workload_id prefix (default 'leak-')")
    _prov.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_stamp(container, args.prefix)
    if not stamp:
        print(f"ERROR: no rows found for prefix '{args.prefix}'.", file=sys.stderr)
        sys.exit(2)
    print(f"=== Leak verdict for stamp {stamp} (prefix '{args.prefix}') ===")

    rows = list(
        container.query_items(
            "SELECT c.config_backend, c.operation, c.runtime_backend, "
            "c.elapsed_seconds, c.memory_bytes, c.driver_commit "
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

    # ---- provenance gate (enforced) ----
    grp = {}                                  # (config_backend, op) -> [(elapsed, rss)]
    labels = {}                               # (config_backend, op) -> {runtime_backend: count}
    err_docs = {}                             # (config_backend, op) -> count of error documents
    for r in rows:
        bk = r.get("config_backend")
        op = r.get("operation")
        key = (bk, op)
        # Error documents are a separate doc type: perf_reporter writes them with an
        # error_message and none of the measurement fields -- no memory_bytes,
        # elapsed_seconds, or runtime_backend. They must stay out of the provenance
        # gate, or their missing runtime_backend reads as a None "mismatch" and fails
        # a clean run. Tally them instead, so a real error surge is still visible.
        if r.get("memory_bytes") is None:
            err_docs[key] = err_docs.get(key, 0) + 1
            continue
        grp.setdefault(key, []).append((r.get("elapsed_seconds"), r.get("memory_bytes")))
        labels.setdefault(key, {})
        rb = r.get("runtime_backend")
        labels[key][rb] = labels[key].get(rb, 0) + 1

    print("\n### GATE: backend purity per (config_backend, op) ###")
    gate_fail = False
    for (bk, op), seen in sorted(labels.items()):
        expected = _EXPECTED_RUNTIME.get(bk)
        bad = expected is None or any(rb not in expected for rb in seen)
        if bad:
            gate_fail = True
            exp = "/".join(sorted(expected)) if expected else "??"
            print(f"  FAIL {bk:11s} {op:11s} runtime_backend={seen} (expected all '{exp}')")
    if not gate_fail:
        print("  OK -- every row's runtime_backend matches its config_backend label.")
    if err_docs:
        total_err = sum(err_docs.values())
        print(f"  NOTE: {total_err} error document(s) excluded from the gate/trend "
              f"(separate doc type, no measurement fields):")
        for (bk, op), n in sorted(err_docs.items()):
            print(f"    {bk:11s} {op:11s} error_docs={n}")
    print("GATE:", "FAIL" if gate_fail else "PASS",
          "(None/blank/mismatched runtime_backend rows indicate provenance not proven)")

    # ---- Rust driver provenance gate (enforced; scoped to rust rows) ----
    prov_ok, prov_lines = _prov.evaluate(rows, strict=_prov.strict_from(args))
    print()
    for _l in prov_lines:
        print(_l)

    backends = sorted({k[0] for k in grp})
    ops = sorted({k[1] for k in grp})

    for bk in backends:
        print(f"\n### {bk} ###")
        print(f"{'op':11s} {'pts':>4s} {'first':>6s} {'last':>6s} {'grow':>6s} "
              f"{'steps':>5s} {f'tailSlope{_PLUS_MINUS}95%CI(MB/h)':>22s} {'theil':>7s} "
              f"{'verdict':>11s}  trajectory")
        for op in ops:
            pts = sorted([(e, m / 1e6) for e, m in grp.get((bk, op), [])
                          if e is not None and m and e > WARMUP_S], key=lambda x: x[0])
            if len(pts) < 3:
                print(f"{op:11s} {len(pts):4d}  (insufficient post-warmup points)")
                continue
            first_rss, rss_now = pts[0][1], pts[-1][1]
            tail = settled_tail(pts, TAIL_S)
            n_steps, _max_step, _ = detect_steps(pts, STEP_MB)
            ys = [m for _, m in pts]
            step = max(1, len(ys) // 24)
            v = verdict(tail, n_steps)
            if tail and tail.get("slope") is not None:
                hw = tail["half"]
                ci = (f"{tail['slope']:+.2f}{_PLUS_MINUS}{hw:.2f}" if hw is not None
                      else f"{tail['slope']:+.2f}{_PLUS_MINUS}n/a")
                th = f"{tail['theil']:+.2f}" if tail.get("theil") is not None else "n/a"
            else:
                ci, th = "n/a", "n/a"
            print(f"{op:11s} {len(pts):4d} {first_rss:6.0f} {rss_now:6.0f} "
                  f"{rss_now-first_rss:+6.0f} {n_steps:5d} {ci:>22s} {th:>7s} "
                  f"{v:>11s}  {ys[0]:.0f}{spark(ys[::step])}{ys[-1]:.0f}")

    if 'rust' in backends and 'core-python' in backends:
        print(f"\n### RUST vs CORE (final RSS + recent slope {_PLUS_MINUS}95% CI) ###")
        print(f"{'op':11s} {'rustRSS':>8s} {'coreRSS':>8s} {'rustRecent':>18s} "
              f"{'coreRecent':>18s}")
        for op in ops:
            def series(bk):
                return sorted([(e, m / 1e6) for e, m in grp.get((bk, op), [])
                               if e is not None and m and e > WARMUP_S], key=lambda x: x[0])
            rp, cp = series('rust'), series('core-python')
            rr = settled_tail(rp, TAIL_S) if len(rp) >= 3 else None
            cr = settled_tail(cp, TAIL_S) if len(cp) >= 3 else None
            rrss = rp[-1][1] if rp else float('nan')
            crss = cp[-1][1] if cp else float('nan')

            def fmt(d):
                if d and d.get("slope") is not None and d.get("half") is not None:
                    return f"{d['slope']:+.2f}{_PLUS_MINUS}{d['half']:.2f}"
                return "n/a"
            print(f"{op:11s} {rrss:8.0f} {crss:8.0f} {fmt(rr):>18s} {fmt(cr):>18s}")

    sys.exit(1 if (gate_fail or not prov_ok) else 0)


if __name__ == "__main__":
    main()
