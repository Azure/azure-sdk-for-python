# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Cold-start regression coverage for the SDK-owned Responses startup path."""
from __future__ import annotations

import http.client
import json
import os
import socket
import subprocess
import sys
import time


# Best-of-three matches the hosted measurement method. The budgets are broad
# cross-platform regression guards, not hosted-container performance targets.
_RUN_COUNT = 3
_SDK_IMPORT_BUDGET_SECONDS = 3.0
_HOST_CONSTRUCTION_BUDGET_SECONDS = 2.0
_PROCESS_TO_READINESS_BUDGET_SECONDS = 2.5
_READINESS_TIMEOUT_SECONDS = 15.0

_COLD_START_SCRIPT = """
import json
import os
import time

sdk_import_started = time.perf_counter()
from azure.ai.agentserver.responses import ResponsesAgentServerHost
sdk_import_seconds = time.perf_counter() - sdk_import_started

host_construction_started = time.perf_counter()
app = ResponsesAgentServerHost()
host_construction_seconds = time.perf_counter() - host_construction_started

print(
    json.dumps(
        {
            "sdk_import_seconds": sdk_import_seconds,
            "host_construction_seconds": host_construction_seconds,
        }
    ),
    flush=True,
)
app.run(host="127.0.0.1", port=int(os.environ["PORT"]))
"""


def _unused_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _wait_for_readiness(process: subprocess.Popen[str], port: int) -> None:
    deadline = time.perf_counter() + _READINESS_TIMEOUT_SECONDS
    last_error: Exception | None = None

    while time.perf_counter() < deadline:
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr is not None else ""
            raise AssertionError(
                f"cold-start subprocess exited with {process.returncode}: {stderr}"
            )
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=0.25)
        try:
            connection.request("GET", "/readiness")
            if connection.getresponse().status == 200:
                return
        except OSError as exc:
            last_error = exc
        finally:
            connection.close()
        time.sleep(0.01)

    raise AssertionError(
        f"/readiness did not respond within {_READINESS_TIMEOUT_SECONDS}s: {last_error!r}"
    )


def _measure_cold_start() -> dict[str, float]:
    port = _unused_local_port()
    env = os.environ.copy()
    env["PORT"] = str(port)
    env["PYTHONUNBUFFERED"] = "1"
    for name in (
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "FOUNDRY_HOSTING_ENVIRONMENT",
        "OTEL_EXPORTER_OTLP_ENDPOINT",
        "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
        "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
        "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
    ):
        env.pop(name, None)

    started = time.perf_counter()
    process = subprocess.Popen(  # pylint: disable=consider-using-with
        [sys.executable, "-c", _COLD_START_SCRIPT],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_for_readiness(process, port)
        process_to_readiness_seconds = time.perf_counter() - started
        assert process.stdout is not None
        child_metrics = json.loads(process.stdout.readline())
        return {
            "sdk_import_seconds": float(child_metrics["sdk_import_seconds"]),
            "host_construction_seconds": float(
                child_metrics["host_construction_seconds"]
            ),
            "process_to_readiness_seconds": process_to_readiness_seconds,
        }
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


def test_sdk_cold_start_budgets() -> None:
    """A minimal Responses host becomes ready within cold-start budgets."""
    runs = [_measure_cold_start() for _ in range(_RUN_COUNT)]
    best = {metric: min(run[metric] for run in runs) for metric in runs[0]}

    print(f"best-of-{_RUN_COUNT} Responses cold-start metrics: {best}")

    assert best["sdk_import_seconds"] < _SDK_IMPORT_BUDGET_SECONDS, best
    assert best["host_construction_seconds"] < _HOST_CONSTRUCTION_BUDGET_SECONDS, best
    assert (
        best["process_to_readiness_seconds"] < _PROCESS_TO_READINESS_BUDGET_SECONDS
    ), best
