# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Shared fixtures and factory functions for invocations tests."""
import asyncio
from collections import deque
import faulthandler
import gc
import json
import os
import sys
import threading
import time
from typing import Any
from unittest.mock import patch
from xml.sax.saxutils import escape, quoteattr

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver.invocations import InvocationAgentServerHost


_CI_HANG_DIAGNOSTICS = os.environ.get("TF_BUILD", "").lower() == "true"
_CI_WINDOWS_VOICE_REPEATS = _CI_HANG_DIAGNOSTICS and os.environ.get("AGENT_OS") == "Windows_NT"
_TEST_TIMEOUT_SECONDS = 60.0
_SESSION_TIMEOUT_SECONDS = 300.0
_CI_VOICE_REPEAT_COUNT = 100
_CI_VOICE_REPEAT_TESTS = frozenset(
    {
        (
            "test_voice_adversarial_limits.py",
            "test_session_retention_outlives_connection_for_resistant_customer_task",
        ),
        (
            "test_voice_adversarial_limits.py",
            "test_global_customer_task_bytes_are_shared_across_event_loops",
        ),
        (
            "test_voice_host.py",
            "test_session_start_callback_failure_releases_session_retention",
        ),
        (
            "test_voice_host.py",
            "test_session_retention_admission_failure_rejects_before_callback",
        ),
        (
            "test_voice_host.py",
            "test_cancellation_resistant_signal_does_not_block_teardown",
        ),
        (
            "test_voice_host.py",
            "test_session_end_runs_despite_a_blocked_prior_callback",
        ),
        (
            "test_voice_host.py",
            "test_cancellation_resistant_task_is_tracked_until_done",
        ),
        (
            "test_voice_host.py",
            "test_resistant_task_limit_closes_without_additional_work",
        ),
        (
            "test_voice_host.py",
            "test_cancel_pending_retains_active_owner_until_bridge_outcome",
        ),
        (
            "test_voice_host.py",
            "test_cancel_pending_active_owner_is_released_by_connection_terminal",
        ),
    }
)
_watchdog_lock = threading.Lock()
_session_watchdog: threading.Timer | None = None
_active_test = "pytest collection/startup"
_active_phase = "startup"
_active_checkpoint = "none"
_activity_history: deque[str] = deque(maxlen=100)


def _record_activity(kind: str, value: str) -> None:
    global _active_test, _active_phase, _active_checkpoint  # pylint: disable=global-statement
    with _watchdog_lock:
        if kind == "test":
            _active_test = value
        elif kind == "phase":
            _active_phase = value
        elif kind == "checkpoint":
            _active_checkpoint = value
        _activity_history.append(
            f"{time.monotonic():.6f} thread={threading.current_thread().name!r} "
            f"thread_id={threading.get_ident()} {kind}={value}"
        )


def _write_stderr(text: str) -> None:
    """Write directly to stderr so a hard process exit cannot discard text buffers."""
    try:
        descriptor = sys.stderr.fileno()
        pending = memoryview(text.encode("utf-8", errors="backslashreplace"))
        while pending:
            written = os.write(descriptor, pending[:16384])
            pending = pending[written:]
    except (AttributeError, OSError, ValueError):
        print(text, file=sys.stderr, end="", flush=True)


def _write_hang_artifacts(scope: str) -> tuple[str, str]:
    """Persist a raw dump and valid JUnit error before the watchdog exits."""
    with _watchdog_lock:
        active_test = _active_test
        active_phase = _active_phase
        active_checkpoint = _active_checkpoint
        activity_history = tuple(_activity_history)

    diagnostic_directory = os.environ.get("VOICE_CI_DIAGNOSTIC_DIR", os.path.dirname(__file__))
    os.makedirs(diagnostic_directory, exist_ok=True)
    artifact_stem = f"test-hang-diagnostics-{os.getpid()}"
    raw_path = os.path.join(diagnostic_directory, f"{artifact_stem}.txt")
    junit_path = os.path.join(diagnostic_directory, f"{artifact_stem}.xml")

    with open(raw_path, "w", encoding="utf-8", buffering=1) as diagnostic:
        diagnostic.write(
            f"VOICE_CI_HANG_DIAGNOSTIC timeout={scope} active_test={active_test} "
            f"phase={active_phase} checkpoint={active_checkpoint}\n"
        )
        diagnostic.write("VOICE_CI_HANG_DIAGNOSTIC recent activity:\n")
        for activity in activity_history:
            diagnostic.write(f"  {activity}\n")
        diagnostic.write("VOICE_CI_HANG_DIAGNOSTIC all thread stacks:\n")
        diagnostic.flush()
        faulthandler.dump_traceback(file=diagnostic, all_threads=True)
        diagnostic.write("VOICE_CI_HANG_DIAGNOSTIC pending asyncio tasks:\n")
        for candidate in gc.get_objects():
            if not isinstance(candidate, asyncio.Task) or candidate.done():
                continue
            try:
                diagnostic.write(f"task={candidate!r} loop={candidate.get_loop()!r}\n")
                candidate.print_stack(file=diagnostic)
            except BaseException as exc:  # pylint: disable=broad-exception-caught
                diagnostic.write(f"task dump failed for {candidate!r}: {exc!r}\n")
        diagnostic.flush()
        os.fsync(diagnostic.fileno())

    with open(raw_path, "r", encoding="utf-8") as diagnostic:
        diagnostic_text = diagnostic.read()
    junit = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<testsuite name="voice-ci-hang" tests="1" failures="0" errors="1">\n'
        f'  <testcase classname="voice-ci-hang" name={quoteattr(active_test)}>\n'
        f'    <error type="TimeoutError" message={quoteattr(scope)}>'
        f"{escape(diagnostic_text)}</error>\n"
        "  </testcase>\n"
        "</testsuite>\n"
    )
    with open(junit_path, "w", encoding="utf-8") as junit_artifact:
        junit_artifact.write(junit)
        junit_artifact.flush()
        os.fsync(junit_artifact.fileno())
    return diagnostic_text, junit_path


def _dump_hang_diagnostics(scope: str) -> None:
    """Dump process state and terminate so dispatch_checks prints buffered output."""
    try:
        diagnostic_text, junit_path = _write_hang_artifacts(scope)
        _write_stderr(f"\n{diagnostic_text}VOICE_CI_HANG_DIAGNOSTIC junit_artifact={junit_path}\n")
    except BaseException as exc:  # pylint: disable=broad-exception-caught
        _write_stderr(f"VOICE_CI_HANG_DIAGNOSTIC dump failed: {exc!r}\n")
        try:
            faulthandler.dump_traceback(file=sys.stderr, all_threads=True)
        except BaseException:  # pylint: disable=broad-exception-caught
            pass
    finally:
        sys.stdout.flush()
        sys.stderr.flush()
        # dispatch_checks buffers concurrent child output until the child exits.
        # A hard exit makes the diagnostic visible instead of losing it at the
        # three-hour parent-job cancellation boundary.
        os._exit(124)  # pylint: disable=protected-access


def _start_watchdog(seconds: float, scope: str) -> threading.Timer:
    watchdog = threading.Timer(seconds, _dump_hang_diagnostics, args=(scope,))
    watchdog.daemon = True
    watchdog.start()
    return watchdog


def pytest_configure(config):
    config.addinivalue_line("markers", "tracing_e2e: end-to-end tracing tests against live Application Insights")
    config.addinivalue_line("markers", "slow: tests that send large payloads or otherwise take noticeable time in CI")
    config.addinivalue_line(
        "markers", "live: tests that require live external services (Azure OpenAI, github-copilot-sdk, etc.)"
    )
    if _CI_HANG_DIAGNOSTICS:
        global _session_watchdog  # pylint: disable=global-statement
        faulthandler.enable(file=sys.stderr, all_threads=True)
        _session_watchdog = _start_watchdog(_SESSION_TIMEOUT_SECONDS, "pytest session")


def pytest_generate_tests(metafunc):
    """Repeat hang-prone Voice tests in CI to amplify scheduling races."""
    if not _CI_WINDOWS_VOICE_REPEATS or "_voice_ci_repeat" not in metafunc.fixturenames:
        return
    test_key = (metafunc.definition.path.name, metafunc.function.__name__)
    if test_key not in _CI_VOICE_REPEAT_TESTS:
        return
    repeats = [pytest.param(index, id=f"ci-repeat-{index:03d}") for index in range(1, _CI_VOICE_REPEAT_COUNT + 1)]
    metafunc.parametrize("_voice_ci_repeat", repeats, indirect=True)


@pytest.fixture(autouse=True)
def _voice_ci_repeat(request):
    """Provide the CI-only repeat parameter without changing test signatures."""
    return getattr(request, "param", None)


@pytest.fixture
def voice_ci_checkpoint():
    """Record the last operation reached by a hang-prone Voice test."""

    def _checkpoint(value: str) -> None:
        if not _CI_HANG_DIAGNOSTICS:
            return
        _record_activity("checkpoint", value)
        print(f"VOICE_CI_CHECKPOINT {value}", flush=True)

    return _checkpoint


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    if _CI_HANG_DIAGNOSTICS:
        _record_activity("phase", f"setup: {item.nodeid}")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_call(item):
    if _CI_HANG_DIAGNOSTICS:
        _record_activity("phase", f"call: {item.nodeid}")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_teardown(item):
    if _CI_HANG_DIAGNOSTICS:
        _record_activity("phase", f"teardown: {item.nodeid}")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):  # pylint: disable=unused-argument
    """Identify and bound every test, including its setup and teardown phases."""
    if not _CI_HANG_DIAGNOSTICS:
        yield
        return

    _record_activity("test", item.nodeid)
    _record_activity("checkpoint", "test protocol entered")
    print(f"VOICE_CI_TEST_START {item.nodeid}", flush=True)
    watchdog = _start_watchdog(_TEST_TIMEOUT_SECONDS, f"test protocol: {item.nodeid}")
    try:
        yield
    finally:
        watchdog.cancel()
        print(f"VOICE_CI_TEST_END {item.nodeid}", flush=True)


def pytest_sessionfinish(session, exitstatus):  # pylint: disable=unused-argument
    """Keep a watchdog alive through pytest and interpreter shutdown."""
    if not _CI_HANG_DIAGNOSTICS:
        return

    global _active_test  # pylint: disable=global-statement
    with _watchdog_lock:
        _active_test = f"pytest session shutdown (exitstatus={exitstatus})"
    if _session_watchdog is not None:
        _session_watchdog.cancel()
    print(f"VOICE_CI_SESSION_FINISH exitstatus={exitstatus}", flush=True)
    _start_watchdog(_TEST_TIMEOUT_SECONDS, "pytest/interpreter shutdown")


@pytest.fixture(autouse=True)
def _prevent_distro_setup(request):
    """Prevent microsoft-opentelemetry distro from contaminating global OTel
    state during tests.  Without this, CI environments that have the distro
    installed and APPLICATIONINSIGHTS_CONNECTION_STRING set would trigger
    ``use_microsoft_opentelemetry()`` on the first server construction,
    installing a global TracerProvider that breaks later traceparent-
    propagation tests.

    A function-scoped fixture must inspect the current test marker. The global
    ``-m`` expression can select tracing and ordinary tests in one run; a
    session-scoped decision would then either disable the live exporter or
    contaminate unrelated tests with global provider state."""
    if request.node.get_closest_marker("tracing_e2e") is not None:
        yield
    else:
        with patch("azure.ai.agentserver.core._tracing._setup_distro_export", create=True):
            yield


# ---------------------------------------------------------------------------
# E2E tracing fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def appinsights_connection_string():
    """Return APPLICATIONINSIGHTS_CONNECTION_STRING or skip the test."""
    cs = os.environ.get("APPLICATIONINSIGHTS_CONNECTION_STRING")
    if not cs:
        pytest.skip("APPLICATIONINSIGHTS_CONNECTION_STRING not set")
    return cs


@pytest.fixture()
def appinsights_resource_id():
    """Return the App Insights resource ID provisioned by test-resources.bicep."""
    rid = os.environ.get("APPLICATIONINSIGHTS_RESOURCE_ID")
    if not rid:
        pytest.skip("APPLICATIONINSIGHTS_RESOURCE_ID not set")
    return rid


@pytest.fixture()
def logs_query_client():
    """Create a ``LogsQueryClient`` for querying Application Insights.

    In CI the pipeline runs inside ``AzurePowerShell@5`` — use
    ``AzurePowerShellCredential`` directly to get a token from the correct
    tenant.  Locally fall back to ``DefaultAzureCredential``.
    """
    from azure.monitor.query import LogsQueryClient

    if os.environ.get("AZURESUBSCRIPTION_TENANT_ID"):
        from azure.identity import AzurePowerShellCredential

        credential = AzurePowerShellCredential(
            tenant_id=os.environ["AZURESUBSCRIPTION_TENANT_ID"],
        )
    else:
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
    return LogsQueryClient(credential)


# ---------------------------------------------------------------------------
# Sample OpenAPI spec used by several tests
# ---------------------------------------------------------------------------

SAMPLE_OPENAPI_SPEC: dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {"title": "Echo Agent", "version": "1.0.0"},
    "paths": {
        "/invocations": {
            "post": {
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["message"],
                                "properties": {
                                    "message": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "OK",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "reply": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
}


# ---------------------------------------------------------------------------
# Factory functions
# ---------------------------------------------------------------------------


def _make_echo_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose invoke handler echoes the request body."""
    kwargs.setdefault("configure_observability", None)
    app = InvocationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return app


def _make_streaming_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose invoke handler returns 3 JSON chunks."""
    kwargs.setdefault("configure_observability", None)
    app = InvocationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(request: Request) -> StreamingResponse:
        async def generate():
            for i in range(3):
                yield json.dumps({"chunk": i}) + "\n"

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    return app


def _make_async_storage_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost with get/cancel handlers and in-memory store."""
    kwargs.setdefault("configure_observability", None)
    app = InvocationAgentServerHost(**kwargs)
    store: dict[str, Any] = {}

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        inv_id = request.state.invocation_id
        body = await request.body()
        store[inv_id] = body
        return Response(content=body, media_type="application/octet-stream")

    @app.get_invocation_handler
    async def get_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id not in store:
            return JSONResponse(
                {"error": {"code": "not_found", "message": "Not found"}},
                status_code=404,
            )
        return Response(content=store[inv_id], media_type="application/octet-stream")

    @app.cancel_invocation_handler
    async def cancel_handler(request: Request) -> Response:
        inv_id = request.path_params["invocation_id"]
        if inv_id not in store:
            return JSONResponse(
                {"error": {"code": "not_found", "message": "Not found"}},
                status_code=404,
            )
        del store[inv_id]
        return JSONResponse({"status": "cancelled"})

    return app


def _make_validated_agent() -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost with OpenAPI spec."""
    app = InvocationAgentServerHost(openapi_spec=SAMPLE_OPENAPI_SPEC, configure_observability=None)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        data = await request.json()
        return JSONResponse({"reply": f"echo: {data['message']}"})

    return app


def _make_failing_agent(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose handler raises ValueError."""
    kwargs.setdefault("configure_observability", None)
    app = InvocationAgentServerHost(**kwargs)

    @app.invoke_handler
    async def handle(request: Request) -> Response:
        raise ValueError("something went wrong")

    return app


# ---------------------------------------------------------------------------
# WebSocket factory functions and helpers
# ---------------------------------------------------------------------------


def _make_echo_ws_app(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose ws handler echoes text frames."""
    from starlette.websockets import WebSocket

    app = InvocationAgentServerHost(**kwargs)

    @app.ws_handler
    async def echo(websocket: WebSocket) -> None:
        async for message in websocket.iter_text():
            await websocket.send_text(message)

    return app


def _make_failing_ws_app(**kwargs: Any) -> InvocationAgentServerHost:
    """Create an InvocationAgentServerHost whose ws handler raises after one frame."""
    from starlette.websockets import WebSocket

    app = InvocationAgentServerHost(**kwargs)

    @app.ws_handler
    async def boom(websocket: WebSocket) -> None:
        await websocket.receive_text()
        raise ValueError("boom")

    return app


def _records_with_ws_extras(records):
    """Filter log records that carry the close-event ``ws.*`` extras."""
    return [
        r
        for r in records
        if hasattr(r, "azure.ai.agentserver.invocations_ws.session_id")
        and hasattr(r, "azure.ai.agentserver.invocations_ws.close_code")
    ]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def echo_client():
    app = _make_echo_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def streaming_client():
    app = _make_streaming_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def async_storage_server():
    return _make_async_storage_agent()


@pytest.fixture()
def async_storage_client(async_storage_server):
    transport = ASGITransport(app=async_storage_server)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def validated_client():
    app = _make_validated_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def no_spec_client():
    app = _make_echo_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.fixture()
def failing_client():
    app = _make_failing_agent()
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")
