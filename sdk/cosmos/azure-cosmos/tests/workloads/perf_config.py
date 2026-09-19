# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Performance reporting configuration from environment variables."""

import os
import subprocess
import uuid


def _get_git_sha() -> str:
    """Get the current git commit SHA, or 'unknown' if unavailable."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
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
    """Read the current short HEAD of the configured or sibling Rust checkout.

    This does not inspect the loaded extension's build provenance or uncommitted
    changes. get_perf_config may override the field using PERF_DRIVER_COMMIT.
    Return 'unknown' if the Git lookup fails.
    """
    driver_dir = os.environ.get("AZURE_SDK_FOR_RUST_DIR")
    if not driver_dir:
        # perf_config.py lives in sdk/cosmos/azure-cosmos/tests/workloads; five
        # levels up is the azure-sdk-for-python repo root, and the driver clone
        # sits next to it as a sibling directory.
        here = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(here, "..", "..", "..", "..", ".."))
        driver_dir = os.path.join(os.path.dirname(repo_root), "azure-sdk-for-rust")
    try:
        result = subprocess.run(
            ["git", "-C", driver_dir, "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _safe_int_env(name: str, default: int) -> int:
    """Read an integer from an environment variable with a fallback default."""
    return _safe_int(os.environ.get(name, str(default)), default)


def _safe_int(value: object, default: int) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def get_perf_config() -> dict:
    """Build performance reporter configuration from environment variables."""
    return {
        "enabled": os.environ.get("PERF_ENABLED", "true").lower() == "true",
        "results_endpoint": os.environ.get("RESULTS_COSMOS_URI", ""),
        "results_database": os.environ.get("RESULTS_COSMOS_DATABASE", "perfdb"),
        "results_container": os.environ.get("RESULTS_COSMOS_CONTAINER", "perfresults-v2"),
        "report_interval": _safe_int(
            os.environ.get("PERF_REPORT_INTERVAL", "300"), 300
        ),
        "workload_id": os.environ.get("PERF_WORKLOAD_ID", str(uuid.uuid4())),
        "commit_sha": os.environ.get("PERF_COMMIT_SHA", _get_git_sha()),
        # Declared driver provenance: an override or the checkout's current HEAD,
        # not a revision extracted from the loaded extension.
        "driver_commit": os.environ.get("PERF_DRIVER_COMMIT", _get_driver_sha()),
    }
