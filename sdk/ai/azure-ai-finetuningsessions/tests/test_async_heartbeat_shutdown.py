# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Deterministic heartbeat shutdown ordering for async session lifecycle calls."""

import asyncio
import logging
from typing import Any
from urllib.parse import urlsplit

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline.transport import AsyncHttpResponse, AsyncHttpTransport
from azure.core.utils import case_insensitive_dict

from azure.ai.finetuningsessions.aio import FineTuningSessionClient
from azure.ai.finetuningsessions.aio import _patch as aio_patch


class _Response:
    status_code = 200

    def raise_for_status(self) -> None:
        pass


class _HeartbeatClient:
    def __init__(self) -> None:
        self.entered = asyncio.Event()
        self.cleanup_started = asyncio.Event()
        self.release_cleanup = asyncio.Event()
        self.cleanup_finished = asyncio.Event()
        self.events: list[str] = []
        self.lifecycle_requests: list[Any] = []

    async def send_request(self, request: Any) -> _Response:
        if urlsplit(request.url).path.endswith("/heartbeat"):
            self.events.append("heartbeat")
            self.entered.set()
            try:
                await asyncio.Future()
            finally:
                self.events.append("cleanup_started")
                self.cleanup_started.set()
                # A second cancellation would interrupt this transport cleanup.
                await self.release_cleanup.wait()
                self.events.append("cleanup_finished")
                self.cleanup_finished.set()
        else:
            self.events.append("lifecycle")
            self.lifecycle_requests.append(request)
        return _Response()


async def _wait(event: asyncio.Event) -> None:
    # The timeout is a deadlock guard, not a timing-based ordering assertion.
    await asyncio.wait_for(event.wait(), timeout=5)


@pytest.fixture
async def active_heartbeat():
    client = _HeartbeatClient()
    aio_patch._ensure_async_state(client)
    client._session_resource_ids["session_test"] = "model_test"
    aio_patch._start_heartbeat(client, "model_test", interval_sec=0)
    task = client._heartbeat_tasks["session_test"]
    try:
        await _wait(client.entered)
        yield client, task
    finally:
        client.release_cleanup.set()
        if not client.cleanup_started.is_set():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.parametrize("operation", ["close_session", "delete_session"])
@pytest.mark.parametrize("session_id", ["session_test", "model_test", "test"])
async def test_lifecycle_waits_for_inflight_heartbeat_cleanup(active_heartbeat, operation, session_id) -> None:
    client, heartbeat = active_heartbeat
    lifecycle = asyncio.create_task(getattr(aio_patch, operation)(client, session_id))
    try:
        await _wait(client.cleanup_started)
        assert not heartbeat.done()
        assert not lifecycle.done()
        assert client.lifecycle_requests == []
        assert client._heartbeat_tasks["session_test"] is heartbeat

        client.release_cleanup.set()
        await asyncio.wait_for(lifecycle, timeout=5)

        assert heartbeat.done()
        assert client.cleanup_finished.is_set()
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
        assert client.events == ["heartbeat", "cleanup_started", "cleanup_finished", "lifecycle"]
        [request] = client.lifecycle_requests
        suffix = "/complete" if operation == "close_session" else ""
        assert request.method == ("POST" if operation == "close_session" else "DELETE")
        assert urlsplit(request.url).path == "{endpoint}" + f"/fine_tuning/sessions/model_test{suffix}"
    finally:
        client.release_cleanup.set()
        await asyncio.gather(lifecycle, return_exceptions=True)


@pytest.mark.parametrize(
    "operations",
    [
        ("close_session", "delete_session"),
        ("delete_session", "close_session"),
        ("close_session", "close_session"),
        ("delete_session", "delete_session"),
    ],
)
async def test_concurrent_lifecycles_share_one_heartbeat_shutdown(active_heartbeat, operations) -> None:
    client, heartbeat = active_heartbeat
    first = asyncio.create_task(getattr(aio_patch, operations[0])(client, "model_test"))
    second = None
    second_entered = asyncio.Event()

    async def run_second() -> None:
        second_entered.set()
        await getattr(aio_patch, operations[1])(client, "session_test")

    try:
        await _wait(client.cleanup_started)
        second = asyncio.create_task(run_second())
        await _wait(second_entered)
        assert not first.done() and not second.done()
        assert not heartbeat.done()
        assert client.lifecycle_requests == []
        assert len(client._heartbeat_shutdowns) == 1

        client.release_cleanup.set()
        await asyncio.wait_for(asyncio.gather(first, second), timeout=5)
        assert heartbeat.done() and client.cleanup_finished.is_set()
        assert client.events == ["heartbeat", "cleanup_started", "cleanup_finished", "lifecycle", "lifecycle"]
        for operation, request in zip(operations, client.lifecycle_requests):
            suffix = "/complete" if operation == "close_session" else ""
            assert urlsplit(request.url).path == "{endpoint}" + f"/fine_tuning/sessions/model_test{suffix}"
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
    finally:
        client.release_cleanup.set()
        await asyncio.gather(first, *([second] if second is not None else []), return_exceptions=True)


@pytest.mark.parametrize("operation", ["close_session", "delete_session"])
async def test_caller_cancellation_propagates_without_interrupting_heartbeat_cleanup(
    active_heartbeat, operation
) -> None:
    client, heartbeat = active_heartbeat
    lifecycle = asyncio.create_task(getattr(aio_patch, operation)(client, "session_test"))
    try:
        await _wait(client.cleanup_started)
        lifecycle.cancel()
        with pytest.raises(asyncio.CancelledError):
            await lifecycle

        assert client.lifecycle_requests == []
        assert not heartbeat.done()
        assert client._heartbeat_tasks["session_test"] is heartbeat
        shutdown = client._heartbeat_shutdowns["session_test"]
        assert not shutdown.cancelled()

        client.release_cleanup.set()
        await asyncio.wait_for(asyncio.shield(shutdown), timeout=5)
        assert heartbeat.done() and client.cleanup_finished.is_set()
        assert client.lifecycle_requests == []
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
    finally:
        client.release_cleanup.set()
        await asyncio.gather(lifecycle, return_exceptions=True)


async def test_cancelling_one_waiter_does_not_release_another(active_heartbeat) -> None:
    client, heartbeat = active_heartbeat
    first = asyncio.create_task(aio_patch.close_session(client, "session_test"))
    second = None
    second_entered = asyncio.Event()

    async def run_second() -> None:
        second_entered.set()
        await aio_patch.delete_session(client, "session_test")

    try:
        await _wait(client.cleanup_started)
        second = asyncio.create_task(run_second())
        await _wait(second_entered)
        first.cancel()
        with pytest.raises(asyncio.CancelledError):
            await first
        assert not second.done() and not heartbeat.done()
        assert client.lifecycle_requests == []

        client.release_cleanup.set()
        await asyncio.wait_for(second, timeout=5)
        assert heartbeat.done() and client.cleanup_finished.is_set()
        assert len(client.lifecycle_requests) == 1
        assert client.lifecycle_requests[0].method == "DELETE"
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
    finally:
        client.release_cleanup.set()
        await asyncio.gather(first, *([second] if second is not None else []), return_exceptions=True)


@pytest.mark.parametrize("operation", ["close_session", "delete_session"])
async def test_lifecycle_without_heartbeat_is_a_noop_shutdown(operation) -> None:
    client = _HeartbeatClient()
    await getattr(aio_patch, operation)(client, "session_test")
    assert len(client.lifecycle_requests) == 1
    assert client._heartbeat_tasks == {}
    assert client._heartbeat_shutdowns == {}


@pytest.mark.parametrize("state", ["not_started", "sleeping", "finished", "cancelled", "failed"])
async def test_stop_handles_each_heartbeat_task_state(state, caplog) -> None:
    client = _HeartbeatClient()
    aio_patch._ensure_async_state(client)
    entered = asyncio.Event()

    async def heartbeat() -> None:
        entered.set()
        if state in {"not_started", "sleeping"}:
            await asyncio.Future()
        elif state == "cancelled":
            raise asyncio.CancelledError()
        elif state == "failed":
            raise RuntimeError("heartbeat failed unexpectedly")

    task = asyncio.create_task(heartbeat())
    client._heartbeat_tasks["session_test"] = task
    try:
        if state == "sleeping":
            await _wait(entered)
        elif state != "not_started":
            # Wait for completion without consuming the exception: shutdown must retrieve it.
            await asyncio.wait({task})
        await aio_patch._stop_heartbeat(client, "model_test")
        assert task.done()
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
        if state == "failed":
            assert "heartbeat failed unexpectedly" in caplog.text
        # A repeated stop, including a bare ID, is harmless.
        await aio_patch._stop_heartbeat(client, "test")
    finally:
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)


@pytest.mark.skipif(not hasattr(asyncio, "eager_task_factory"), reason="Eager tasks require Python 3.12+")
async def test_eagerly_completed_shutdown_leaves_no_stale_registry_entry() -> None:
    client = _HeartbeatClient()
    aio_patch._ensure_async_state(client)
    loop = asyncio.get_running_loop()
    old_factory = loop.get_task_factory()

    async def finished_heartbeat() -> None:
        pass

    try:
        loop.set_task_factory(asyncio.eager_task_factory)
        task = asyncio.create_task(finished_heartbeat())
        assert task.done()
        client._heartbeat_tasks["session_test"] = task
        await aio_patch._stop_heartbeat(client, "session_test")
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
    finally:
        loop.set_task_factory(old_factory)


async def test_shutdown_does_not_stop_other_sessions(active_heartbeat) -> None:
    client, heartbeat = active_heartbeat
    other = asyncio.create_task(asyncio.Event().wait())
    client._heartbeat_tasks["session_other"] = other
    lifecycle = asyncio.create_task(aio_patch.close_session(client, "session_test"))
    try:
        await _wait(client.cleanup_started)
        client.release_cleanup.set()
        await asyncio.wait_for(lifecycle, timeout=5)
        assert heartbeat.done()
        assert not other.done()
        assert client._heartbeat_tasks == {"session_other": other}
    finally:
        client.release_cleanup.set()
        other.cancel()
        await asyncio.gather(lifecycle, other, return_exceptions=True)


class _TransportResponse(AsyncHttpResponse):
    def __init__(self, request) -> None:
        super().__init__(request, None)
        self.status_code = 200
        self.headers = case_insensitive_dict({"Content-Type": "application/json"})
        self.content_type = "application/json"
        self.reason = "OK"

    def body(self):
        return b"{}"


class _HeartbeatTransport(AsyncHttpTransport):
    def __init__(self) -> None:
        self.requests = []
        self.received = asyncio.Queue()
        self.closed = False
        self.release_response = asyncio.Event()
        self.release_response.set()
        self.status_code = 200
        self.error = None

    async def send(self, request, **kwargs):
        self.requests.append(request)
        self.received.put_nowait(request)
        await self.release_response.wait()
        if self.error is not None:
            raise self.error
        response = _TransportResponse(request)
        response.status_code = self.status_code
        return response

    async def open(self):
        pass

    async def close(self):
        self.closed = True

    async def __aexit__(self, *args):
        await self.close()


@pytest.fixture
def heartbeat_waits():
    return asyncio.Queue()


@pytest.fixture
def heartbeat_ticks(monkeypatch, heartbeat_waits):
    ticks = asyncio.Queue()

    async def sleep(interval):
        assert interval == 30.0
        heartbeat_waits.put_nowait(None)
        await ticks.get()

    monkeypatch.setattr(aio_patch.asyncio, "sleep", sleep)
    return ticks


@pytest.mark.parametrize(
    ("session_id", "resource_id"),
    [("session_test", "session_test"), ("model_test", "model_test"), ("test", "model_test")],
)
@pytest.mark.parametrize("shutdown", ["close", "context_exit", "close_session"])
async def test_attach_sends_heartbeat_and_shutdown_stops_it(
    heartbeat_ticks, session_id, resource_id, shutdown, caplog
) -> None:
    caplog.set_level(logging.INFO, logger=aio_patch.__name__)
    transport = _HeartbeatTransport()
    client = FineTuningSessionClient("https://unit.invalid", AzureKeyCredential("test-key"), transport=transport)
    try:
        await client.__aenter__()
        assert await client.attach_session(session_id) is None
        heartbeat = client._heartbeat_tasks["session_test"]
        await client.attach_session(session_id)
        await client.attach_session("session_test")
        assert client._heartbeat_tasks == {"session_test": heartbeat}
        assert not heartbeat.done()
        assert transport.requests == []
        assert "first HTTP success" not in caplog.text

        heartbeat_ticks.put_nowait(None)
        request = await asyncio.wait_for(transport.received.get(), timeout=5)
        assert request.method == "POST"
        assert urlsplit(request.url).path == f"/fine_tuning/sessions/{resource_id}/heartbeat"
        assert not heartbeat.done()

        if shutdown == "context_exit":
            await client.__aexit__(None, None, None)
        else:
            await getattr(client, shutdown)(*([session_id] if shutdown == "close_session" else []))
        assert heartbeat.done()
        assert client._heartbeat_tasks == {}
        assert client._heartbeat_shutdowns == {}
        heartbeat_ticks.put_nowait(None)
        # Draining the task proves no subsequent timer tick can send another heartbeat.
        await asyncio.gather(heartbeat, return_exceptions=True)
        expected_paths = [f"/fine_tuning/sessions/{resource_id}/heartbeat"]
        if shutdown == "close_session":
            expected_paths.append(f"/fine_tuning/sessions/{resource_id}/complete")
        else:
            assert transport.closed
        assert [urlsplit(req.url).path for req in transport.requests] == expected_paths
        assert all(req.method == "POST" for req in transport.requests)
        messages = [
            record.getMessage()
            for record in caplog.records
            if record.name == aio_patch.__name__ and "[heartbeat]" in record.getMessage()
        ]
        assert messages == [
            "[heartbeat] task registered; not HTTP confirmation. "
            f"SessionId=session_test ResourceSessionId={resource_id} interval=30s",
            "[heartbeat] first HTTP success. " f"SessionId=session_test ResourceSessionId={resource_id} status=200",
            "[heartbeat] task stopped. SessionId=session_test",
        ]
    finally:
        await client.close()


@pytest.mark.parametrize("failure", [401, 500, ServiceRequestError("sensitive-transport-details")])
async def test_heartbeat_first_http_success_is_once_and_only_after_completion(
    heartbeat_ticks, heartbeat_waits, caplog, failure
) -> None:
    caplog.set_level(logging.INFO, logger=aio_patch.__name__)
    transport = _HeartbeatTransport()
    transport.release_response.clear()
    if isinstance(failure, int):
        transport.status_code = failure
    else:
        transport.error = failure
    async with FineTuningSessionClient(
        "https://unit.invalid",
        AzureKeyCredential("test-key"),
        transport=transport,
        retry_total=0,
    ) as client:
        await client.attach_session("model_test")
        await asyncio.wait_for(heartbeat_waits.get(), timeout=5)
        heartbeat_ticks.put_nowait(None)
        await asyncio.wait_for(transport.received.get(), timeout=5)
        assert "first HTTP success" not in caplog.text
        transport.release_response.set()
        await asyncio.wait_for(heartbeat_waits.get(), timeout=5)
        assert "first HTTP success" not in caplog.text
        warnings = [r for r in caplog.records if r.name == aio_patch.__name__ and r.levelno == logging.WARNING]
        assert len(warnings) == 1
        assert "SessionId=session_test" in warnings[0].getMessage()
        assert "sensitive-transport-details" not in caplog.text

        transport.error = None
        transport.status_code = 200
        transport.release_response.clear()
        heartbeat_ticks.put_nowait(None)
        await asyncio.wait_for(transport.received.get(), timeout=5)
        assert "first HTTP success" not in caplog.text
        transport.release_response.set()
        await asyncio.wait_for(heartbeat_waits.get(), timeout=5)
        assert caplog.text.count("first HTTP success") == 1
        await client.attach_session("model_test")
        heartbeat_ticks.put_nowait(None)
        await asyncio.wait_for(transport.received.get(), timeout=5)
        await asyncio.wait_for(heartbeat_waits.get(), timeout=5)
        assert caplog.text.count("first HTTP success") == 1
        assert caplog.text.count("task registered;") == 1
        assert not client._heartbeat_tasks["session_test"].done()
        assert len(transport.requests) == 3
        assert all(urlsplit(r.url).path.endswith("/model_test/heartbeat") for r in transport.requests)
    assert caplog.text.count("task stopped.") == 1
    assert client._heartbeat_tasks == {}


async def test_close_before_heartbeat_http_completion_never_confirms(heartbeat_ticks, heartbeat_waits, caplog) -> None:
    caplog.set_level(logging.INFO, logger=aio_patch.__name__)
    transport = _HeartbeatTransport()
    transport.release_response.clear()
    client = FineTuningSessionClient("https://unit.invalid", AzureKeyCredential("test-key"), transport=transport)
    try:
        await client.attach_session("session_test")
        await asyncio.wait_for(heartbeat_waits.get(), timeout=5)
        task = client._heartbeat_tasks["session_test"]
        heartbeat_ticks.put_nowait(None)
        await asyncio.wait_for(transport.received.get(), timeout=5)
        await client.close()
        heartbeat_ticks.put_nowait(None)
        transport.release_response.set()
        await asyncio.gather(task, return_exceptions=True)
        assert task.done() and transport.closed
        assert client._heartbeat_tasks == client._heartbeat_shutdowns == {}
        assert len(transport.requests) == 1
        assert "first HTTP success" not in caplog.text
        assert caplog.text.count("task stopped.") == 1
    finally:
        await client.close()


async def test_attach_reuses_created_heartbeat_and_preserves_other_client(heartbeat_ticks) -> None:
    first_transport, second_transport = _HeartbeatTransport(), _HeartbeatTransport()
    async with (
        FineTuningSessionClient(
            "https://unit.invalid", AzureKeyCredential("test-key"), transport=first_transport
        ) as first,
        FineTuningSessionClient(
            "https://unit.invalid", AzureKeyCredential("test-key"), transport=second_transport
        ) as second,
    ):
        aio_patch._ensure_async_state(first)
        first._session_resource_ids["session_test"] = "model_test"
        aio_patch._start_heartbeat(first, "session_test")
        created_heartbeat = first._heartbeat_tasks["session_test"]
        await first.attach_session("session_test")
        assert first._heartbeat_tasks["session_test"] is created_heartbeat
        assert first._session_resource_ids["session_test"] == "model_test"
        await second.attach_session("session_test")
        second_heartbeat = second._heartbeat_tasks["session_test"]

        await first.close()
        assert created_heartbeat.done()
        assert first._heartbeat_tasks == {}
        assert not second_heartbeat.done()
        heartbeat_ticks.put_nowait(None)
        request = await asyncio.wait_for(second_transport.received.get(), timeout=5)
        assert urlsplit(request.url).path == "/fine_tuning/sessions/session_test/heartbeat"
        assert first_transport.requests == []
    assert second_heartbeat.done()
    assert second._heartbeat_tasks == {}
