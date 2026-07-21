# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""End-to-end OTLP protocol tests using in-process loopback receivers."""

import os
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
from threading import Lock, Thread

import grpc
import pytest
from opentelemetry.proto.collector.logs.v1 import (
    logs_service_pb2,
    logs_service_pb2_grpc,
)
from opentelemetry.proto.collector.metrics.v1 import (
    metrics_service_pb2,
    metrics_service_pb2_grpc,
)
from opentelemetry.proto.collector.trace.v1 import (
    trace_service_pb2,
    trace_service_pb2_grpc,
)

_SIGNALS = {"traces", "metrics", "logs"}
_PACKAGE_ROOT = Path(__file__).resolve().parents[1]
_OTLP_ENV_VARS = (
    "APPLICATIONINSIGHTS_CONNECTION_STRING",
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "OTEL_EXPORTER_OTLP_PROTOCOL",
    "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
    "OTEL_EXPORTER_OTLP_TRACES_PROTOCOL",
    "OTEL_EXPORTER_OTLP_METRICS_ENDPOINT",
    "OTEL_EXPORTER_OTLP_METRICS_PROTOCOL",
    "OTEL_EXPORTER_OTLP_LOGS_ENDPOINT",
    "OTEL_EXPORTER_OTLP_LOGS_PROTOCOL",
)

_EMIT_ALL_SIGNALS = """
from azure.ai.agentserver.core import configure_observability
from opentelemetry import metrics, trace
from opentelemetry._logs import LogRecord, SeverityNumber, get_logger_provider

configure_observability()

with trace.get_tracer("agentserver.otlp.test").start_as_current_span("otlp-test-span"):
    pass

metrics.get_meter("agentserver.otlp.test").create_counter("otlp.test").add(1)

get_logger_provider().get_logger("agentserver.otlp.test").emit(
    LogRecord(
        severity_text="INFO",
        severity_number=SeverityNumber.INFO,
        body="otlp-test-log",
    )
)

trace.get_tracer_provider().force_flush()
metrics.get_meter_provider().force_flush()
get_logger_provider().force_flush()
"""


class _SignalReceiver:
    def __init__(self) -> None:
        self._signals: set[str] = set()
        self._lock = Lock()

    @property
    def signals(self) -> set[str]:
        with self._lock:
            return set(self._signals)

    @property
    def endpoint(self) -> str:
        raise NotImplementedError

    def record(self, signal: str) -> None:
        with self._lock:
            self._signals.add(signal)

    def __enter__(self) -> "_SignalReceiver":
        raise NotImplementedError

    def __exit__(self, *_args: object) -> None:
        raise NotImplementedError


class _HttpOtlpReceiver(_SignalReceiver):
    def __init__(self) -> None:
        super().__init__()
        receiver = self
        services = {
            "/v1/traces": (
                "traces",
                trace_service_pb2.ExportTraceServiceRequest,
                trace_service_pb2.ExportTraceServiceResponse,
            ),
            "/v1/metrics": (
                "metrics",
                metrics_service_pb2.ExportMetricsServiceRequest,
                metrics_service_pb2.ExportMetricsServiceResponse,
            ),
            "/v1/logs": (
                "logs",
                logs_service_pb2.ExportLogsServiceRequest,
                logs_service_pb2.ExportLogsServiceResponse,
            ),
        }

        class Handler(BaseHTTPRequestHandler):
            protocol_version = "HTTP/1.1"

            def do_POST(self) -> None:  # pylint: disable=invalid-name
                service = services.get(self.path)
                if service is None:
                    self.send_error(404)
                    return

                signal, request_type, response_type = service
                body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                request_type.FromString(body)
                receiver.record(signal)

                response = response_type().SerializeToString()
                self.send_response(200)
                self.send_header("Content-Type", "application/x-protobuf")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

            def log_message(  # pylint: disable=redefined-builtin
                self, format: str, *args: object
            ) -> None:
                del format, args

        self._server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self._thread = Thread(target=self._server.serve_forever, daemon=True)

    @property
    def endpoint(self) -> str:
        return f"http://127.0.0.1:{self._server.server_port}"

    def __enter__(self) -> "_HttpOtlpReceiver":
        self._thread.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join(timeout=5)


class _GrpcOtlpReceiver(_SignalReceiver):
    def __init__(self) -> None:
        super().__init__()
        receiver = self

        class TraceService(trace_service_pb2_grpc.TraceServiceServicer):
            def Export(
                self, request, context
            ):  # pylint: disable=invalid-name,unused-argument
                receiver.record("traces")
                return trace_service_pb2.ExportTraceServiceResponse()

        class MetricsService(metrics_service_pb2_grpc.MetricsServiceServicer):
            def Export(
                self, request, context
            ):  # pylint: disable=invalid-name,unused-argument
                receiver.record("metrics")
                return metrics_service_pb2.ExportMetricsServiceResponse()

        class LogsService(logs_service_pb2_grpc.LogsServiceServicer):
            def Export(
                self, request, context
            ):  # pylint: disable=invalid-name,unused-argument
                receiver.record("logs")
                return logs_service_pb2.ExportLogsServiceResponse()

        self._server = grpc.server(ThreadPoolExecutor(max_workers=3))
        trace_service_pb2_grpc.add_TraceServiceServicer_to_server(
            TraceService(), self._server
        )
        metrics_service_pb2_grpc.add_MetricsServiceServicer_to_server(
            MetricsService(), self._server
        )
        logs_service_pb2_grpc.add_LogsServiceServicer_to_server(
            LogsService(), self._server
        )
        self._port = self._server.add_insecure_port("127.0.0.1:0")

    @property
    def endpoint(self) -> str:
        return f"http://127.0.0.1:{self._port}"

    def __enter__(self) -> "_GrpcOtlpReceiver":
        self._server.start()
        return self

    def __exit__(self, *_args: object) -> None:
        self._server.stop(grace=0).wait(timeout=5)


@pytest.mark.parametrize(
    ("protocol", "receiver_type"),
    [
        pytest.param("http/protobuf", _HttpOtlpReceiver, id="http-protobuf"),
        pytest.param("grpc", _GrpcOtlpReceiver, id="grpc"),
    ],
)
def test_otlp_protocol_exports_all_signals(
    protocol: str,
    receiver_type: type[_SignalReceiver],
) -> None:
    """Agent Server must honor the configured OTLP protocol for every signal."""
    with receiver_type() as receiver:
        env = os.environ.copy()
        for variable in _OTLP_ENV_VARS:
            env.pop(variable, None)
        env.update(
            {
                "OTEL_EXPORTER_OTLP_ENDPOINT": receiver.endpoint,
                "OTEL_EXPORTER_OTLP_PROTOCOL": protocol,
                "OTEL_EXPORTER_OTLP_TIMEOUT": "1",
            }
        )

        result = subprocess.run(
            [sys.executable, "-c", _EMIT_ALL_SIGNALS],
            cwd=_PACKAGE_ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    assert result.returncode == 0, result.stderr
    assert receiver.signals == _SIGNALS, (
        f"{protocol} receiver got {sorted(receiver.signals)} instead of "
        f"{sorted(_SIGNALS)}.\nsubprocess stderr:\n{result.stderr}"
    )
    if protocol == "grpc":
        assert "otlp-test-span" not in result.stdout
        assert "otlp-test-log" not in result.stdout
