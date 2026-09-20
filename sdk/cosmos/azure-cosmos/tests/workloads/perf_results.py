# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Shared rules for reading measurement rows, not error/completion documents."""

import math
import re

EXPECTED_RUNTIME = {
    "core-python": {"LegacyBackend", "AsyncLegacyBackend"},
    # Old class labels remain valid in historical measurement artifacts.
    "rust": {"RustBinding", "AsyncRustBinding", "RustBackend", "AsyncRustBackend"},
}
OPERATIONS = {
    "read": "ReadItem", "create": "CreateItem", "upsert": "UpsertItem",
    "replace": "ReplaceItem", "delete": "DeleteItem", "patch": "PatchItem",
    "query": "QueryItems",
}
TIMING_COMPONENTS = ("delay_before_call", "sdk_call", "total")


def fixed_rate_timing(row, outcome):
    """Return a validated timing group, or None when the evidence is absent."""
    group = row.get("fixed_rate_timings", {}).get(outcome)
    if group is None:
        return None
    expected = row["count"] if outcome == "success" else row["errors"]
    for name in TIMING_COMPONENTS:
        series = group.get(name)
        if (not isinstance(series, dict) or type(series.get("count")) is not int
                or series["count"] != expected):
            raise ValueError(f"Incomplete {outcome} {name} timing population")
        overflow = series.get("overflow_count")
        maximum = series.get("max_observed_ms")
        if (type(overflow) is not int or not 0 <= overflow <= expected
                or isinstance(maximum, bool) or not isinstance(maximum, (int, float))
                or not math.isfinite(maximum) or maximum < 0
                or (maximum > 60_000) != (overflow > 0)):
            raise ValueError(f"Invalid {outcome} {name} timing bounds")
    return group


def fixed_rate_schedule_totals(summaries, completion):
    """Validate final per-client schedules against completed calls in one process."""
    schedules = completion.get("fixed_rate_schedules") if completion else None
    if not schedules:
        return None
    count_fields = ("scheduled_count", "launched_count", "not_launched_count", "limit_wait_count")
    totals = {field: 0 for field in count_fields}
    totals["limit_wait_ms"] = 0.0
    ids = set()
    for schedule in schedules:
        identifier = schedule.get("schedule_id")
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise ValueError("Missing or duplicate fixed-rate schedule ID")
        ids.add(identifier)
        for field in (*count_fields, "max_inflight", "peak_inflight"):
            value = schedule.get(field)
            if type(value) is not int or value < 0:
                raise ValueError(f"Invalid schedule {field}")
        for field in ("rate", "limit_wait_ms", "scheduling_seconds"):
            value = schedule.get(field)
            if (isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value) or value < 0):
                raise ValueError(f"Invalid schedule {field}")
        if (schedule["rate"] <= 0 or schedule["max_inflight"] <= 0
                or schedule["peak_inflight"] > schedule["max_inflight"]
                or schedule["scheduled_count"] != schedule["launched_count"] + schedule["not_launched_count"]
                or schedule["limit_wait_count"] > schedule["launched_count"] + 1):
            raise ValueError("Inconsistent fixed-rate schedule counts")
        for row in summaries:
            if (row.get("config_arrival_rate") != schedule["rate"]
                    or row.get("config_max_inflight") != schedule["max_inflight"]):
                raise ValueError("Schedule disagrees with recorded workload configuration")
        for field in count_fields:
            totals[field] += schedule[field]
        totals["limit_wait_ms"] += schedule["limit_wait_ms"]
    if any(row.get("config_num_clients") != len(schedules) for row in summaries):
        raise ValueError("Missing or unexpected client schedules")
    if totals["launched_count"] != sum(row["count"] + row["errors"] for row in summaries):
        raise ValueError("Launched calls disagree with persisted successes and failures")
    return totals


def summary_rows(rows):
    for row in rows:
        if row.get("record_type") in ("error", "completion") or "count" not in row:
            continue
        for field in ("count", "errors", "window_seconds", "elapsed_seconds"):
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {field} in measurement {row.get('id', row.get('workload_id'))}")
        if row["window_seconds"] <= 0:
            raise ValueError("Measurement window must be positive")
        if any(int(row[field]) != row[field] for field in ("count", "errors")):
            raise ValueError("Measurement counts must be integers")
        yield row


def split_workload_id(workload_id, prefix=None):
    body = workload_id[len(prefix):] if prefix and workload_id.startswith(prefix) else workload_id.partition("-")[2]
    match = re.fullmatch(r"([a-z]+)-(.+)-(\d{8}-\d{6,9})", body)
    if not match:
        raise ValueError(f"Malformed workload_id: {workload_id!r}")
    op, backend, stamp = match.groups()
    # Matrix repeats are independent cells, but aggregate under the actual backend.
    backend = re.sub(r"-r\d+$", "", backend)
    return op, backend, stamp


def window_key(row):
    if row.get("window_id"):
        return row["window_id"]
    if row.get("elapsed_seconds") is None:
        raise ValueError("Cannot identify the process window; elapsed_seconds is missing")
    return (row["workload_id"], row.get("process_id"), row["elapsed_seconds"])


def add_histogram(target, encoded, expected_count):
    """Return False for missing samples; reject malformed or inconsistent payloads."""
    if not encoded:
        return expected_count == 0
    from hdrh.histogram import HdrHistogram

    decoded = HdrHistogram.decode(encoded)
    if decoded.total_count != expected_count:
        raise ValueError(f"Histogram has {decoded.total_count} samples, expected {expected_count}")
    target.add(decoded)
    return True


def post_warmup(row, seconds):
    # A window straddling warmup still contains warmup calls; drop the whole window.
    return row["elapsed_seconds"] - row["window_seconds"] >= seconds - 0.001
