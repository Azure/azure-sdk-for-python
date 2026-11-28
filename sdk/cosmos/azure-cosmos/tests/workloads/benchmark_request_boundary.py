# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Called by the ignored release-mode Rust test measure_request_boundary.

No clients, accounts, network, driver lookups, retries, diagnostics or response
conversion. Query extraction measures the common fields/body used by the
one-shot entry point, not retained-cursor planning or execution.
"""

from __future__ import annotations

import gc
import hashlib
import json
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from azure.cosmos._backend._binding_conversions import build_binding_request_from_page
from azure.cosmos._backend.contracts import PreparedPageRequest
from azure.cosmos._helpers._document import serialize_document
from azure.cosmos._helpers._request_item import (
    build_create_item_request,
    build_read_item_request,
)


def cases():
    link = "dbs/bank/colls/accounts"

    def read(options):
        return build_read_item_request(
            container_link=link,
            item_id="account-1",
            partition_key_value="customer-1",
            container_rid=None,
            request_options=options,
        )

    def create(size):
        body = {"id": "account-1", "customer": "customer-1", "data": "x" * size}

        def prepare():
            return build_create_item_request(
                container_link=link,
                document=serialize_document(body, operation="create_item"),
                partition_key_value="customer-1",
                container_rid=None,
                request_options={},
            )

        return prepare

    def query(count):
        parameters = ({"name": "@values", "value": list(range(count))},)
        query_text = "SELECT * FROM c WHERE ARRAY_CONTAINS(@values, c.number)"
        page = PreparedPageRequest(
            op="query_items",
            container_link=link,
            query=query_text,
            parameters=parameters,
            query_body=json.dumps(
                {"query": query_text, "parameters": parameters},
                separators=(",", ":"),
            ).encode(),
            max_item_count=100,
            continuation="opaque-page-token",
        )
        return lambda: build_binding_request_from_page(page)

    return [
        ("read_minimal", lambda: read({}), "read"),
        (
            "read_headers",
            lambda: read(
                {
                    "initialHeaders": {f"x-benchmark-{n}": str(n) for n in range(8)},
                    "sessionToken": "0:-1#10",
                }
            ),
            "read",
        ),
        ("create_1k", create(1024), "create"),
        ("create_64k", create(65536), "create"),
        ("query_page_10_values", query(10), "query"),
        ("query_page_1000_values", query(1000), "query"),
    ]


def sample(function, iterations):
    start = time.perf_counter_ns()
    for _ in range(iterations):
        function()
    return (time.perf_counter_ns() - start) / iterations / 1000


def run(extract_read, extract_create, extract_query, executable):
    output = Path(os.environ["COSMOS_BOUNDARY_BENCHMARK_OUTPUT"])
    iterations = int(os.environ.get("COSMOS_BOUNDARY_BENCHMARK_ITERATIONS", "5000"))
    rounds = int(os.environ.get("COSMOS_BOUNDARY_BENCHMARK_ROUNDS", "9"))
    warmup = int(os.environ.get("COSMOS_BOUNDARY_BENCHMARK_WARMUP", "500"))
    if min(iterations, rounds, warmup) <= 0:
        raise ValueError("iterations, rounds and warmup must be positive")
    native = {"read": extract_read, "create": extract_create, "query": extract_query}
    functions = {}
    for name, prepare, kind in cases():
        prepared = prepare()
        extract = native[kind]
        extract(prepared)  # Fail before recording timings if real extraction fails.
        functions[f"{name}/prepare"] = prepare
        functions[f"{name}/extract"] = lambda p=prepared, e=extract: e(p)
        functions[f"{name}/combined"] = lambda p=prepare, e=extract: e(p())

    for function in functions.values():
        for _ in range(warmup):
            function()
    samples = {name: [] for name in functions}
    rng = random.Random(0)
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(rounds):
            names = list(functions)
            rng.shuffle(names)
            for name in names:
                samples[name].append(sample(functions[name], iterations))
    finally:
        if gc_was_enabled:
            gc.enable()

    package = Path(__file__).resolve().parents[2]
    sources = [
        *sorted((package / "azure" / "cosmos").rglob("*.py")),
        *sorted((package / "azure_cosmos_rust" / "src").rglob("*.rs")),
        package / "Cargo.lock",
        Path(__file__).resolve(),
    ]
    source_hashes = {
        str(path.relative_to(package)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sources
    }
    result = {
        "schema_version": 1,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "profile": "cargo test --release; test-only extraction functions",
        "rustc": subprocess.check_output(["rustc", "--version"], text=True).strip(),
        "commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=package, text=True
        ).strip(),
        "working_tree": subprocess.check_output(
            ["git", "status", "--short"], cwd=package, text=True
        ),
        "native_executable_sha256": hashlib.sha256(Path(executable).read_bytes()).hexdigest(),
        "source_hashes": source_hashes,
        "iterations": iterations,
        "rounds": rounds,
        "warmup": warmup,
        "gc_during_measurement": False,
        "unit": "microseconds_per_operation",
        "exclusions": [
            "public API validation before the item builder",
            "initial query serialization and pager construction",
            "retained-cursor-specific extraction and planning",
            "driver lookup and operation construction",
            "network, diagnostics, response conversion",
        ],
        "results": {
            name: {"samples": values, "median": statistics.median(values)}
            for name, values in samples.items()
        },
    }
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for name, values in result["results"].items():
        print(f"{name:42} {values['median']:9.3f} us", flush=True)
    print(f"Saved: {output}", flush=True)
