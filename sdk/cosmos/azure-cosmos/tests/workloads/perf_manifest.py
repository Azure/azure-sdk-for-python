# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Write an escaped, non-secret run manifest; fail if required build evidence is missing."""

import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from datetime import datetime, timezone

from perf_build_details import PACKAGE_ROOT, driver_commit, extension_details, source_digest


def write_manifest(directory, stamp, phase):
    def git(*args):
        return subprocess.check_output(["git", "-C", str(PACKAGE_ROOT), *args], text=True).strip()

    build = {
        "git_commit": git("rev-parse", "HEAD"),
        "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "git_dirty": bool(git("status", "--porcelain", "--untracked-files=normal")),
        "source_sha256": source_digest(),
        "rust_driver_commit": driver_commit(),
        "rust_driver_dirty": False,
        "driver_source": "Cargo resolved locked Git dependency, not the sibling checkout",
        "python": platform.python_version(),
        "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        **extension_details(),
    }
    def fields(names):
        return {key: os.environ.get(env, "") for key, env in names.items()}

    record = {
        "phase": phase, "stamp": stamp,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "build": build,
        "host": {"hostname": platform.node(), "kernel": platform.platform(), "nproc": os.cpu_count()},
        "account": fields({
            "uri": "COSMOS_URI", "database": "COSMOS_DATABASE", "container": "COSMOS_CONTAINER",
            "throughput_ru": "COSMOS_THROUGHPUT", "preferred_locations": "COSMOS_PREFERRED_LOCATIONS",
            "partition_key": "COSMOS_PARTITION_KEY", "max_item_index": "COSMOS_MAX_ITEM_INDEX",
            "client_excluded_locations": "COSMOS_CLIENT_EXCLUDED_LOCATIONS",
            "request_excluded_locations": "COSMOS_REQUEST_EXCLUDED_LOCATIONS",
        }),
        "load": fields({
            "num_clients": "WORKLOAD_NUM_CLIENTS", "concurrent_requests": "COSMOS_CONCURRENT_REQUESTS",
            "request_timeout_s": "COSMOS_REQUEST_TIMEOUT", "arrival_rate": "WORKLOAD_ARRIVAL_RATE",
            "max_inflight": "WORKLOAD_MAX_INFLIGHT", "operations": "WORKLOAD_OPERATIONS",
            "use_proxy": "WORKLOAD_USE_PROXY", "use_sync": "WORKLOAD_USE_SYNC",
            "gc_freeze": "WORKLOAD_GC_FREEZE", "loop_lag_monitor": "WORKLOAD_LOOP_LAG_MONITOR",
            "workload_mix": "WORKLOAD_MIX", "doc_profile": "WORKLOAD_DOC_PROFILE",
            "log_level": "COSMOS_LOG_LEVEL", "diagnostics_logging": "COSMOS_ENABLE_DIAGNOSTICS_LOGGING",
            "report_interval_s": "PERF_REPORT_INTERVAL",
        }),
        "results_sink": fields({
            "uri": "RESULTS_COSMOS_URI", "database": "RESULTS_COSMOS_DATABASE",
            "container": "RESULTS_COSMOS_CONTAINER",
        }),
    }
    # Capture stamps can differ from their parent profiling session identifier.
    if os.environ.get("PROFILING_SESSION_ID"):
        record["profiling_session_id"] = os.environ["PROFILING_SESSION_ID"]
    path = Path(directory) / f"manifest-{stamp}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"run manifest written: {path}")


if __name__ == "__main__":
    write_manifest(*sys.argv[1:])
