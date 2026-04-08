"""Timing instrumentation for the async query path.

Adds lightweight perf_counter-based timing to key stages of the per-request flow.
Accumulates totals and prints a summary at the end.

Usage: import this module before running the benchmark. Call print_timing_summary() when done.
"""
import time
import threading
from collections import defaultdict

_timings = defaultdict(lambda: [0.0, 0])  # {label: [total_seconds, count]}
_lock = threading.Lock()


def record(label, elapsed):
    with _lock:
        entry = _timings[label]
        entry[0] += elapsed
        entry[1] += 1


def print_timing_summary():
    print("\n" + "=" * 90)
    print("  SDK PER-REQUEST TIMING BREAKDOWN")
    print("=" * 90)
    print(f"{'Stage':<45} {'Total(ms)':>12} {'Count':>10} {'Avg(μs)':>12}")
    print("-" * 90)

    sorted_items = sorted(_timings.items(), key=lambda x: -x[1][0])
    for label, (total, count) in sorted_items:
        avg_us = (total / count * 1_000_000) if count > 0 else 0
        print(f"{label:<45} {total*1000:>12.1f} {count:>10,} {avg_us:>12.1f}")
    print("=" * 90)
