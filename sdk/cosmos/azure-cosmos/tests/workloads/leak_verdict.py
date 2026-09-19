# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Classify observed RSS traces using tail slopes and adjacent-sample steps.

Group samples by backend/operation, fit the final time window, and compare
ordinary least-squares intervals and median pairwise slopes with configured
thresholds. The final window need not be a plateau; serial dependence and
sampling affect inference. Labels describe the observed run, not proof of
a leak's cause or bounded memory in longer runs.

Backend names and declared driver-commit labels are checked separately.
They do not attest execution or the extension's actual build provenance.
A successful exit is not equivalent to every trace being leak-free.

Run leak_verdict.py with --stamp and --prefix after configuring the results
account.
"""

import argparse
import math
import os
import sys

import perf_driver_commit_gate as _driver_gate
from perf_results import EXPECTED_RUNTIME, summary_rows

try:
    from azure.cosmos import CosmosClient
except ImportError:
    print("ERROR: azure-cosmos is required (pip install azure-cosmos).", file=sys.stderr)
    sys.exit(2)

# Heuristic recent-slope thresholds (MB/h), not measured allocator-noise bounds
# or proof of a leak. Classification depends on the sampled time window.
FLAT_MAX = 2.0
LEAK_MIN = 5.0
WARMUP_S = 600          # drop the first 10 min (warmup) before fitting anything.
TAIL_S = 3600           # final time window; it need not be a plateau.
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
    """Fit ordinary least squares to (elapsed seconds, RSS MB) samples.

    Return slope/hour, r2, slope standard error/hour, nominal 95% interval
    half-width/hour, and sample count. With fewer than three samples or no time
    spread, only the count is populated. No residual independence check is made.
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
    """Return the median of nonvertical pairwise slopes in MB/hour.

    Step changes remain in the input and can influence this statistic.
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
    """Fit samples within tail_seconds of the final sample.

    This is a time-window selection, not plateau detection. Return slope,
    interval, median pairwise slope, r2, and count when available.
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
    """Count adjacent RSS increases greater than or equal to step_mb.

    Return their count, maximum, and sum. Sampling alone cannot distinguish
    a sudden allocation from accumulated growth between samples.
    """
    steps = [pts[i][1] - pts[i - 1][1] for i in range(1, len(pts))]
    big = [d for d in steps if d >= step_mb]
    return len(big), (max(big) if big else 0.0), sum(big)


def verdict(tail, n_steps):
    """Shape- and CI-aware verdict from the final-plateau fit and step count.

    Uses the 95% confidence interval rather than the point estimate alone.
    ``PLATEAUED``/``STAIRCASE`` require the interval's upper bound to sit below
    ``FLAT_MAX``; ``GROWING`` requires its lower bound to sit above
    ``LEAK_MIN``. An interval spanning the gap between those two thresholds is
    not conclusive either way, so it reports ``WATCH``.
    """
    if tail is None or tail.get("slope") is None:
        return "INCONCLUSIVE"
    slope = tail["slope"]
    hi = tail["hi"] if tail["hi"] is not None else slope
    lo = tail["lo"] if tail["lo"] is not None else slope
    if hi <= FLAT_MAX:
        # Below the configured slope threshold; this does not prove bounded RSS.
        return "PLATEAUED" if n_steps <= 1 else "STAIRCASE"
    if lo >= LEAK_MIN:
        return "GROWING"            # CI entirely above the leak threshold.
    return "WATCH"                  # neither classification threshold was met.


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
# to. A row that does not match -- or is None/blank -- fails the backend match check.
_EXPECTED_RUNTIME = EXPECTED_RUNTIME


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
    _driver_gate.add_cli_flag(ap)
    args = ap.parse_args()

    container = _connect()
    stamp = args.stamp or _latest_stamp(container, args.prefix)
    if not stamp:
        print(f"ERROR: no rows found for prefix '{args.prefix}'.", file=sys.stderr)
        sys.exit(2)
    print(f"=== Leak verdict for stamp {stamp} (prefix '{args.prefix}') ===")

    rows = list(
        container.query_items(
            "SELECT * "
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

    # ---- backend match check (enforced) ----
    grp = {}                                  # (config_backend, op) -> [(elapsed, rss)]
    labels = {}                               # (config_backend, op) -> {runtime_backend: count}
    processes = {}
    for r in summary_rows(rows):
        bk = r.get("config_backend")
        op = r.get("operation")
        key = (bk, op)
        if op not in ("ReadItem", "CreateItem", "UpsertItem", "ReplaceItem", "DeleteItem", "PatchItem"):
            continue
        processes.setdefault(key, set()).add(r.get("process_id") or r["workload_id"])
        if len(processes[key]) > 1:
            raise ValueError(f"RSS trends require one process per operation/backend, got {key}")
        memory = r.get("memory_bytes")
        if isinstance(memory, bool) or not isinstance(memory, (int, float)) or not math.isfinite(memory) or memory <= 0:
            raise ValueError(f"Missing or invalid RSS measurement for {r['workload_id']}")
        grp.setdefault(key, []).append((r.get("elapsed_seconds"), r.get("memory_bytes")))
        labels.setdefault(key, {})
        rb = r.get("runtime_backend")
        labels[key][rb] = labels[key].get(rb, 0) + 1

    print("\n### GATE: backend purity per (config_backend, op) ###")
    gate_fail = not bool(grp)
    for (bk, op), seen in sorted(labels.items()):
        expected = _EXPECTED_RUNTIME.get(bk)
        bad = expected is None or any(rb not in expected for rb in seen)
        if bad:
            gate_fail = True
            exp = "/".join(sorted(expected)) if expected else "??"
            print(f"  FAIL {bk:11s} {op:11s} runtime_backend={seen} (expected all '{exp}')")
    if not gate_fail:
        print("  OK -- every row's runtime_backend matches its config_backend label.")
    print("GATE:", "FAIL" if gate_fail else "PASS",
          "(None/blank/mismatched runtime_backend rows mean the backend is unconfirmed)")

    # ---- Rust driver commit check (enforced; scoped to Rust rows) ----
    commit_ok, commit_lines = _driver_gate.evaluate(rows, strict=_driver_gate.strict_from(args))
    print()
    for _l in commit_lines:
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
                gate_fail = True
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

    sys.exit(1 if (gate_fail or not commit_ok) else 0)


if __name__ == "__main__":
    main()
