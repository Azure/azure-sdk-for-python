# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for telemetry flushing and generator reseeding around memory snapshots."""

import asyncio
import logging
import os
import random
import sys
import threading
import time
import types

import httpx
import pytest

from azure.ai.agentserver.core import AgentServerHost, AgentSessionContext
from azure.ai.agentserver.core import _base, _restore_entropy, _tracing

_BEFORE = "/_agent/before-snapshot"
_AFTER = "/_agent/after-restore"


def _payload(session_id: str = "session-1", restore_id: str = "restore-1") -> dict[str, object]:
    return {"session_context": {"session_id": session_id, "restore_id": restore_id, "session_env_overrides": {}}}


def _client(host: AgentServerHost) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.ASGITransport(app=host), base_url="http://testserver")


@pytest.fixture(autouse=True)
def preserve_process_state():
    """After-restore hydrates os.environ and reseeds the global random generator."""
    environment = dict(os.environ)
    state = random.getstate()
    yield
    random.setstate(state)
    os.environ.clear()
    os.environ.update(environment)


class _RecordingProvider:
    def __init__(
        self,
        name: str,
        calls: list[str],
        *,
        result: object = True,
        error: Exception | None = None,
        delay_s: float = 0.0,
    ) -> None:
        self.name = name
        self.calls = calls
        self.result = result
        self.error = error
        self.delay_s = delay_s

    def force_flush(self, timeout_millis: int = 30000) -> object:
        del timeout_millis
        if self.delay_s:
            time.sleep(self.delay_s)
        self.calls.append(self.name)
        if self.error is not None:
            raise self.error
        return self.result


class _CallListHandler(logging.Handler):
    def __init__(self, calls: list[str]) -> None:
        super().__init__()
        self.calls = calls

    def emit(self, record: logging.LogRecord) -> None:
        if "before memory snapshot" in record.getMessage():
            self.calls.append(f"log:{record.levelname}")


@pytest.fixture()
def flush_calls(monkeypatch: pytest.MonkeyPatch):
    """Replace the global providers with recording fakes and record flush summary logs."""
    calls: list[str] = []
    providers = {
        "traces": _RecordingProvider("traces", calls),
        "metrics": _RecordingProvider("metrics", calls),
        "logs": _RecordingProvider("logs", calls),
    }
    monkeypatch.setattr(
        _tracing,
        "_get_snapshot_flush_providers",
        lambda: ([("traces", providers["traces"]), ("metrics", providers["metrics"])], providers["logs"]),
    )
    handler = _CallListHandler(calls)
    tracing_logger = logging.getLogger("azure.ai.agentserver")
    tracing_logger.addHandler(handler)
    monkeypatch.setattr(tracing_logger, "level", logging.INFO)
    monkeypatch.setattr(tracing_logger, "disabled", False)
    yield calls, providers
    tracing_logger.removeHandler(handler)


# ---------------------------------------------------------------- before-snapshot flush


@pytest.mark.asyncio
async def test_before_snapshot_flushes_after_app_hook_with_logs_last(flush_calls) -> None:
    calls, _ = flush_calls
    host = AgentServerHost()

    @host.before_snapshot_handler
    async def _release() -> None:
        calls.append("app")

    async with _client(host) as client:
        response = await client.post(_BEFORE, json={})

    assert response.status_code == 200
    assert calls == ["app", "traces", "metrics", "log:INFO", "logs"]


@pytest.mark.asyncio
async def test_before_snapshot_does_not_flush_when_hook_fails_or_cycle_already_completed(flush_calls) -> None:
    calls, _ = flush_calls
    failing_host = AgentServerHost()

    @failing_host.before_snapshot_handler
    async def _fail() -> None:
        raise RuntimeError("release failed")

    async with _client(failing_host) as client:
        assert (await client.post(_BEFORE, json={})).status_code == 500
    assert calls == []

    host = AgentServerHost()
    async with _client(host) as client:
        assert (await client.post(_BEFORE, json={})).status_code == 200
        assert (await client.post(_BEFORE, json={})).status_code == 200
    assert calls.count("traces") == 1


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("provider_name", "kwargs"),
    [
        ("traces", {"error": RuntimeError("exporter down")}),
        ("metrics", {"result": False}),
        ("logs", {"error": RuntimeError("exporter down")}),
    ],
)
async def test_before_snapshot_flush_failures_are_fail_open(flush_calls, provider_name: str, kwargs: dict) -> None:
    calls, providers = flush_calls
    providers[provider_name].__dict__.update(kwargs)
    host = AgentServerHost()

    async with _client(host) as client:
        first = await client.post(_BEFORE, json={})
        second = await client.post(_BEFORE, json={})

    assert first.status_code == 200
    assert second.status_code == 200
    assert [call for call in calls if not call.startswith("log:")] == ["traces", "metrics", "logs"]
    assert "log:WARNING" in calls


@pytest.mark.asyncio
async def test_before_snapshot_flush_wait_is_bounded(flush_calls, monkeypatch: pytest.MonkeyPatch) -> None:
    calls, providers = flush_calls
    providers["traces"].delay_s = 1.0
    monkeypatch.setattr(_tracing, "_SNAPSHOT_FLUSH_TIMEOUT_SECONDS", 0.1)
    host = AgentServerHost()

    async with _client(host) as client:
        started = time.monotonic()
        response = await client.post(_BEFORE, json={})
        elapsed = time.monotonic() - started

    assert response.status_code == 200
    assert elapsed < 0.9
    assert "log:WARNING" in calls


@pytest.mark.asyncio
async def test_flush_defers_cancellation_until_the_flush_finishes(flush_calls) -> None:
    calls, providers = flush_calls
    release = threading.Event()
    started = threading.Event()

    def _blocking_flush(timeout_millis: int = 30000) -> bool:
        del timeout_millis
        started.set()
        release.wait(5)
        calls.append("traces")
        return True

    providers["traces"].force_flush = _blocking_flush
    task = asyncio.ensure_future(_tracing.flush_providers_before_snapshot())
    await asyncio.get_running_loop().run_in_executor(None, started.wait, 5)
    task.cancel()
    await asyncio.sleep(0.05)
    assert not task.done()
    release.set()

    with pytest.raises(asyncio.CancelledError):
        await task
    assert [call for call in calls if not call.startswith("log:")] == ["traces", "metrics", "logs"]


@pytest.mark.asyncio
async def test_before_snapshot_cycle_is_complete_even_if_flush_is_cancelled(monkeypatch: pytest.MonkeyPatch) -> None:
    hook_calls = 0

    async def _cancelled_flush(timeout_seconds: float | None = None) -> None:
        del timeout_seconds
        raise asyncio.CancelledError

    monkeypatch.setattr(_tracing, "flush_providers_before_snapshot", _cancelled_flush)
    host = AgentServerHost()

    @host.before_snapshot_handler
    async def _release() -> None:
        nonlocal hook_calls
        hook_calls += 1

    async with _client(host) as client:
        with pytest.raises(asyncio.CancelledError):
            await client.post(_BEFORE, json={})
        monkeypatch.undo()
        assert (await client.post(_BEFORE, json={})).status_code == 200

    assert hook_calls == 1


@pytest.mark.asyncio
async def test_each_capture_after_a_restore_flushes_again(flush_calls) -> None:
    calls, _ = flush_calls
    host = AgentServerHost()

    async with _client(host) as client:
        assert (await client.post(_BEFORE, json={})).status_code == 200
        assert (await client.post(_AFTER, json=_payload())).status_code == 200
        assert (await client.post(_BEFORE, json={})).status_code == 200

    assert calls.count("logs") == 2


def test_flush_exports_the_summary_with_a_real_batch_log_processor(monkeypatch: pytest.MonkeyPatch) -> None:
    from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
    from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, InMemoryLogRecordExporter

    exporter = InMemoryLogRecordExporter()
    provider = LoggerProvider()
    provider.add_log_record_processor(BatchLogRecordProcessor(exporter, schedule_delay_millis=60_000))
    handler = LoggingHandler(logger_provider=provider)
    tracing_logger = logging.getLogger("azure.ai.agentserver")
    tracing_logger.addHandler(handler)
    monkeypatch.setattr(tracing_logger, "level", logging.INFO)
    monkeypatch.setattr(_tracing, "_get_snapshot_flush_providers", lambda: ([], provider))
    try:
        tracing_logger.warning("buffered before capture")
        _tracing._flush_providers_for_snapshot(1000)  # pylint: disable=protected-access
    finally:
        tracing_logger.removeHandler(handler)
        provider.shutdown()

    exported = [record.log_record.body for record in exporter.get_finished_logs()]
    assert "buffered before capture" in exported
    assert any("Telemetry flush before memory snapshot" in str(body) for body in exported)


# ---------------------------------------------------------------- after-restore reseed


@pytest.mark.asyncio
async def test_restored_clones_draw_different_python_random_values() -> None:
    cloned_state = random.getstate()
    draws: list[float] = []

    for restore_id in ("restore-a", "restore-b"):
        random.setstate(cloned_state)
        host = AgentServerHost()

        @host.after_restore_handler
        async def _record(_context: AgentSessionContext) -> None:
            draws.append(random.random())

        async with _client(host) as client:
            assert (await client.post(_AFTER, json=_payload(restore_id=restore_id))).status_code == 200

    random.setstate(cloned_state)
    copied_draw = random.random()
    assert draws[0] != draws[1]
    assert copied_draw not in draws


@pytest.mark.asyncio
async def test_reseed_runs_before_protocol_and_application_restore_hooks() -> None:
    observed: dict[str, object] = {}

    class _ProtocolHost(AgentServerHost):
        async def _after_restore(self, context: AgentSessionContext) -> None:
            observed["protocol"] = random.getstate()
            await super()._after_restore(context)

    host = _ProtocolHost()

    @host.after_restore_handler
    async def _record(_context: AgentSessionContext) -> None:
        observed["app"] = random.getstate()

    pre_restore_state = random.getstate()
    async with _client(host) as client:
        assert (await client.post(_AFTER, json=_payload())).status_code == 200

    assert observed["protocol"] != pre_restore_state
    assert observed["app"] == observed["protocol"]


@pytest.mark.asyncio
async def test_openssl_entropy_is_added_on_every_after_restore_call(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def _count() -> list[str]:
        nonlocal calls
        calls += 1
        return []

    monkeypatch.setattr(_base, "add_openssl_entropy", _count)
    host = AgentServerHost()

    async with _client(host) as client:
        assert (
            await client.post(_AFTER, content=b"{", headers={"content-type": "application/json"})
        ).status_code == 400
        assert (await client.post(_AFTER, json=_payload())).status_code == 200
        assert (await client.post(_AFTER, json=_payload())).status_code == 200
        assert (await client.post(_AFTER, json=_payload(session_id="other"))).status_code == 409

    assert calls == 4


@pytest.mark.asyncio
async def test_python_generators_reseed_once_per_restore_and_again_on_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    reseeds = 0
    failures_left = 1

    def _count() -> list[str]:
        nonlocal reseeds
        reseeds += 1
        return []

    monkeypatch.setattr(_base, "reseed_python_generators", _count)
    host = AgentServerHost()

    @host.after_restore_handler
    async def _flaky(_context: AgentSessionContext) -> None:
        nonlocal failures_left
        if failures_left:
            failures_left -= 1
            raise RuntimeError("dependency not ready")

    async with _client(host) as client:
        assert (await client.post(_AFTER, json=_payload())).status_code == 500
        assert reseeds == 1
        assert (await client.post(_AFTER, json=_payload())).status_code == 200
        assert reseeds == 2
        assert (await client.post(_AFTER, json=_payload())).status_code == 200
        assert reseeds == 2


# ---------------------------------------------------------------- generator gating


def test_numpy_is_reseeded_only_when_numpy_random_is_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "numpy.random", raising=False)
    assert _restore_entropy.reseed_python_generators() == ["random"]
    assert "numpy.random" not in sys.modules

    seeds: list[object] = []
    monkeypatch.setitem(sys.modules, "numpy.random", types.SimpleNamespace(seed=seeds.append))
    assert _restore_entropy.reseed_python_generators() == ["random", "numpy.random"]
    assert len(seeds) == 1
    assert len(seeds[0]) == 8
    assert all(0 <= value < 2**32 for value in seeds[0])


def test_real_numpy_legacy_global_generator_is_reseeded() -> None:
    numpy_random = pytest.importorskip("numpy.random")
    numpy_random.seed(1234)
    copied = numpy_random.random()
    numpy_random.seed(1234)

    assert "numpy.random" in _restore_entropy.reseed_python_generators()
    assert numpy_random.random() != copied


def test_cryptography_is_not_imported_when_its_native_module_is_not_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delitem(sys.modules, "cryptography.hazmat.bindings._rust", raising=False)
    monkeypatch.delitem(sys.modules, "cryptography.hazmat.bindings.openssl.binding", raising=False)

    assert _restore_entropy.add_openssl_entropy() == ["ssl"]
    assert "cryptography.hazmat.bindings.openssl.binding" not in sys.modules


def test_cryptography_binding_errors_do_not_fail_the_restore(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def _fail_import(_name: str) -> object:
        raise RuntimeError("legacy provider unavailable")

    monkeypatch.setitem(sys.modules, "cryptography.hazmat.bindings._rust", types.ModuleType("_rust"))
    monkeypatch.delitem(sys.modules, "cryptography.hazmat.bindings.openssl.binding", raising=False)
    monkeypatch.setattr(_restore_entropy.importlib, "import_module", _fail_import)

    with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
        assert _restore_entropy.add_openssl_entropy() == ["ssl"]
    assert "cryptography OpenSSL" in caplog.text


def test_real_cryptography_openssl_receives_entropy() -> None:
    ec = pytest.importorskip("cryptography.hazmat.primitives.asymmetric.ec")
    ec.generate_private_key(ec.SECP256R1())

    assert _restore_entropy.add_openssl_entropy() == ["ssl", "cryptography"]
