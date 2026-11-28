# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Performance reporting configuration from environment variables."""

import os
import subprocess
import uuid
from pathlib import Path


def _get_git_sha() -> str:
    """Get the current git commit SHA, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _get_driver_sha() -> str:
    """Read the loaded extension's declared driver revision, not sibling HEAD."""
    try:
        from azure.cosmos import _rust
    except ImportError:
        return "unknown"
    return getattr(_rust, "__rust_driver_commit__", "unknown")


def _safe_int_env(name: str, default: int) -> int:
    """Read an integer from an environment variable with a fallback default."""
    return _safe_int(os.environ.get(name, str(default)), default)


def _safe_int(value: object, default: int) -> int:
    return int(value)


def get_perf_config() -> dict:
    """Build performance reporter configuration from environment variables."""
    interval = _safe_int_env("PERF_REPORT_INTERVAL", 300)
    if interval <= 0:
        raise ValueError("PERF_REPORT_INTERVAL must be positive")
    enabled = os.environ.get("PERF_ENABLED", "true").lower()
    if enabled not in ("true", "false"):
        raise ValueError("PERF_ENABLED must be true or false")
    actual = _get_driver_sha()
    declared = os.environ.get("PERF_DRIVER_COMMIT", actual)
    if actual != "unknown" and declared != actual:
        raise ValueError("PERF_DRIVER_COMMIT disagrees with the loaded extension")
    return {
        "enabled": enabled == "true",
        "results_endpoint": os.environ.get("RESULTS_COSMOS_URI", ""),
        "results_database": os.environ.get("RESULTS_COSMOS_DATABASE", "perfdb"),
        "results_container": os.environ.get("RESULTS_COSMOS_CONTAINER", "perfresults-v2"),
        "report_interval": interval,
        "workload_id": os.environ.get("PERF_WORKLOAD_ID", str(uuid.uuid4())),
        "commit_sha": os.environ.get("PERF_COMMIT_SHA", _get_git_sha()),
        # Embedded build label; the session manifest also fingerprints the binary.
        "driver_commit": actual,
    }
