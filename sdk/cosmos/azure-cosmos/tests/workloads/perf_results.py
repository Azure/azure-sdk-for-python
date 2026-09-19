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
