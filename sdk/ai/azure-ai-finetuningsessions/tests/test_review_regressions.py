# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Regression evidence for SDK PR 47495; no network or GPU work."""

import asyncio
import logging
from types import SimpleNamespace
from typing import get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.credentials import AzureKeyCredential, TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest

from azure.ai.finetuningsessions import FineTuningSession, FineTuningSessionClient
from azure.ai.finetuningsessions import _patch as sync
from azure.ai.finetuningsessions import _exceptions as errors
from azure.ai.finetuningsessions.aio import _patch as aio
from azure.ai.finetuningsessions.models import LoRAConfig


class Response:
    def __init__(self, status=200, body=None, headers=None):
        self.status_code = status
        self._body = {} if body is None else body
        self.headers = headers or {}
        self.reason = "fixture"
        self.content_type = "application/json"

    def json(self):
        return self._body

    def text(self):
        return "fixture"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HttpResponseError(response=self)


class Clock:
    def __init__(self):
        self.now = 0.0
        self.waits = []

    def monotonic(self):
        return self.now

    def sleep(self, delay):
        assert 0 <= delay < float("inf")
        self.waits.append(delay)
        self.now += delay

    async def asleep(self, delay):
        self.sleep(delay)


@pytest.fixture
def clock(monkeypatch):
    value = Clock()
    # Replace module aliases, not time.monotonic globally (asyncio uses it).
    time = SimpleNamespace(monotonic=value.monotonic, sleep=value.sleep)
    monkeypatch.setattr(sync, "_time", time)
    monkeypatch.setattr(aio, "_time", time)
    monkeypatch.setattr(aio.asyncio, "sleep", value.asleep)
    monkeypatch.setattr(sync.FineTuningSession, "_start_heartbeat", lambda *_: None)
    monkeypatch.setattr(aio, "_start_heartbeat", lambda *_: None)
    return value


@pytest.mark.parametrize("value", ["later", {}, [], "nan", "inf", -1])
def test_bad_503_retry_hint_preserves_typed_error(value):
    error = errors._classify_http_error(503, {"detail": {"reason": "engine_busy", "retry_after_sec": value}})
    assert isinstance(error, errors.NoCapacityError)
    assert error.retry_after_sec is None


def test_metadata_413_is_not_reported_as_batch_size():
    assert errors._classify_http_error(413, {"detail": {"field": "user_metadata", "message": "too large"}}) is None
    assert isinstance(
        errors._classify_http_error(413, {"detail": {"field": "forward_input.data", "message": "too large"}}),
        errors.BatchTooLargeError,
    )


def test_custom_policies_and_single_pipeline():
    with FineTuningSessionClient("https://unit.invalid", AzureKeyCredential("fixture"), policies=[]) as client:
        assert client.sessions._client is client._client
        assert client._session_client is client._client


def test_auth_annotations_resolve():
    hint = get_type_hints(FineTuningSessionClient.__init__)["credential"]
    assert set(hint.__args__) == {TokenCredential, AzureKeyCredential}
    get_type_hints(aio.FineTuningSessionClient.__init__)


def test_empty_batch_rejected_before_chunking():
    with pytest.raises(ValueError, match="empty"):
        sync._chunk_data([])


@pytest.mark.parametrize(
    "method",
    ["forward", "forward_backward", "forward_post", "forward_backward_post", "forward_async", "forward_backward_async"],
)
async def test_empty_async_batch_does_not_submit(method):
    client = SimpleNamespace(send_request=AsyncMock())
    with pytest.raises(ValueError, match="empty"):
        await getattr(aio, method)(client, "session_test", [])
    client.send_request.assert_not_called()


@pytest.mark.parametrize("method", ["forward", "forward_post"])
async def test_forward_uses_offloop_chunker(monkeypatch, method):
    chunker = AsyncMock(side_effect=ValueError("off-loop marker"))
    monkeypatch.setattr(aio, "_chunk_data_async", chunker)
    with pytest.raises(ValueError, match="off-loop marker"):
        await getattr(aio, method)(SimpleNamespace(), "session_test", [object()])
    chunker.assert_awaited_once()


def test_sampler_ids_required_before_post(monkeypatch):
    session = object.__new__(FineTuningSession)
    session.session_id = "session_test"
    session._post_and_poll = MagicMock()
    with pytest.raises(ValueError, match="path.*sampling_session_seq_id"):
        session.save_weights_for_sampler(7)
    session._post_and_poll.assert_not_called()
    session.save_weights_for_sampler(7, sampling_session_seq_id=0)
    assert session._post_and_poll.call_args.kwargs["extra_result_fields"] == {"checkpoint_id": "ss0_seq7"}


@pytest.mark.parametrize("status", [301, 302, 307, 308])
def test_sync_delete_rejects_unhandled_redirect(status):
    session = object.__new__(FineTuningSession)
    session._resource_session_id = "session_test"
    session._stop_heartbeat = lambda: None
    session._client = SimpleNamespace(send_request=lambda _: Response(status))
    with pytest.raises(HttpResponseError):
        session.delete()


@pytest.mark.parametrize("status", [301, 302, 307, 308])
async def test_async_delete_preserves_mapping_on_redirect(monkeypatch, status):
    client = SimpleNamespace(send_request=AsyncMock(return_value=Response(status)))
    aio._ensure_async_state(client)
    client._session_resource_ids["session_test"] = "model_test"
    monkeypatch.setattr(aio, "_stop_heartbeat", AsyncMock())
    with pytest.raises(HttpResponseError):
        await aio.delete_session(client, "session_test")
    assert client._session_resource_ids["session_test"] == "model_test"


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_create_unknown_status_is_immediate_protocol_error(clock, asynchronous):
    responses = iter(
        [Response(body={"session_id": "session_test", "request_id": "r"}), Response(body={"status": "unexpected"})]
    )
    client = SimpleNamespace(send_request=lambda _: next(responses))
    if asynchronous:
        client.send_request = AsyncMock(side_effect=lambda _: next(responses))
    with pytest.raises(RuntimeError, match="Unexpected.*status"):
        if asynchronous:
            await aio.create_session(client, base_model="m", lora_config=LoRAConfig(rank=16))
        else:
            FineTuningSession.create(client, base_model="m", lora_config=LoRAConfig(rank=16))
    assert clock.waits == []


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_create_waits_are_deadline_bounded(clock, asynchronous):
    calls = []

    def send(request):
        calls.append(request)
        return (
            Response(body={"session_id": "session_test", "request_id": "r"})
            if request.method == "POST"
            else Response(503, headers={"Retry-After": "7200"})
        )

    client = SimpleNamespace(send_request=AsyncMock(side_effect=send) if asynchronous else send)
    with pytest.raises(RuntimeError, match="Timed out"):
        if asynchronous:
            await aio.create_session(client, base_model="m", lora_config=LoRAConfig(rank=16), timeout_sec=3)
        else:
            FineTuningSession.create(client, base_model="m", lora_config=LoRAConfig(rank=16), timeout_sec=3)
    assert clock.now <= 3
    assert max(clock.waits) <= 3


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_create_404_grace_does_not_resubmit(clock, asynchronous):
    responses = iter(
        [
            Response(body={"session_id": "session_test", "request_id": "r"}),
            Response(404),
            Response(body={"status": "completed", "result": {}}),
        ]
    )
    calls = []

    def send(request):
        calls.append(request.method)
        return next(responses)

    client = SimpleNamespace(send_request=AsyncMock(side_effect=send) if asynchronous else send)
    if asynchronous:
        assert await aio.create_session(client, base_model="m", lora_config=LoRAConfig(rank=16)) == "session_test"
    else:
        assert (
            FineTuningSession.create(client, base_model="m", lora_config=LoRAConfig(rank=16)).session_id
            == "session_test"
        )
    assert calls == ["POST", "GET", "GET"]
    assert clock.waits


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_create_default_logs_do_not_contain_payload(clock, caplog, asynchronous):
    marker = "private-customer-payload"
    responses = iter(
        [
            Response(body={"session_id": "session_test", "request_id": "r", "user_metadata": {"secret": marker}}),
            Response(body={"status": "completed", "result": {"secret": marker}}),
        ]
    )
    client = SimpleNamespace(
        send_request=AsyncMock(side_effect=lambda _: next(responses)) if asynchronous else lambda _: next(responses)
    )
    with caplog.at_level(logging.INFO):
        if asynchronous:
            await aio.create_session(client, base_model="m", lora_config=LoRAConfig(rank=16))
        else:
            FineTuningSession.create(client, base_model="m", lora_config=LoRAConfig(rank=16))
    assert marker not in caplog.text


def test_error_budget_clamps_retry_sleep(clock):
    budget = sync._ErrorBudget.for_polling(3, op_type="forward", request_id="r")
    budget.consume("HTTP 503")
    assert budget.clamp_delay(7200) == 3
    clock.sleep(3)
    with pytest.raises(TimeoutError):
        budget.consume("HTTP 503")


async def test_async_client_close_drains_heartbeat():
    client = aio.FineTuningSessionClient("https://unit.invalid", AzureKeyCredential("fixture"))
    aio._ensure_async_state(client)
    entered, cleaned = asyncio.Event(), asyncio.Event()

    async def heartbeat():
        entered.set()
        try:
            await asyncio.Future()
        finally:
            cleaned.set()

    task = asyncio.create_task(heartbeat())
    client._heartbeat_tasks["session_test"] = task
    await entered.wait()
    try:
        await client.close()
        assert task.done() and cleaned.is_set()
        assert client._heartbeat_tasks == {}
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


def test_direct_context_policy_scopes_headers_and_preserves_overrides(monkeypatch):
    from azure.ai.finetuningsessions._client_options import _DirectContextPolicy

    monkeypatch.setenv("X_COGNITIVE_SUBSCRIPTION_ID", "environment-sub")
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_ID", "environment-resource")
    policy = _DirectContextPolicy("https://unit.invalid/api/projects/p")
    request = PipelineRequest(
        HttpRequest(
            "GET",
            "https://unit.invalid/api/projects/p/fine_tuning/sessions/s",
            headers={"apim-subscription-id": "caller-sub"},
        ),
        PipelineContext(None),
    )
    policy.on_request(request)
    assert request.http_request.headers["apim-subscription-id"] == "caller-sub"
    assert request.http_request.headers["azure-resource-id"] == "environment-resource"
    request.http_request.url = "https://other.invalid/redirect"
    policy.on_request(request)
    assert "azure-resource-id" not in request.http_request.headers
    assert request.http_request.headers["apim-subscription-id"] == "caller-sub"


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_raw_heartbeat_sends_direct_context(monkeypatch, asynchronous):
    from azure.core.pipeline.transport import AsyncHttpTransport, HttpTransport

    monkeypatch.setenv("X_COGNITIVE_SUBSCRIPTION_ID", "environment-sub")
    monkeypatch.setenv("LOOM_AZURE_RESOURCE_ID", "environment-resource")
    seen = []

    class StopAtTransport(Exception):
        pass

    def capture(request):
        seen.append(dict(request.headers))
        raise StopAtTransport()

    class SyncTransport(HttpTransport):
        def send(self, request, **kwargs):
            capture(request)

        def open(self):
            pass

        def close(self):
            pass

        def __exit__(self, *args):
            pass

    class AsyncTransport(AsyncHttpTransport):
        async def send(self, request, **kwargs):
            capture(request)

        async def open(self):
            pass

        async def close(self):
            pass

        async def __aexit__(self, *args):
            pass

    client_type = aio.FineTuningSessionClient if asynchronous else FineTuningSessionClient
    client = client_type(
        "https://unit.invalid/api/projects/p",
        AzureKeyCredential("fixture"),
        transport=AsyncTransport() if asynchronous else SyncTransport(),
        retry_total=0,
    )
    try:
        with pytest.raises(StopAtTransport):
            result = client.sessions.heartbeat(
                "s", foundry_features=sync._PREVIEW, api_version="v1", headers={"apim-subscription-id": "caller-sub"}
            )
            if asynchronous:
                await result
        assert seen[0]["apim-subscription-id"] == "caller-sub"
        assert seen[0]["azure-resource-id"] == "environment-resource"
    finally:
        if asynchronous:
            await client.close()
        else:
            client.close()


def test_sync_lifecycle_does_not_drop_live_heartbeat_reference():
    import threading

    session = object.__new__(FineTuningSession)
    session._heartbeat_stop = threading.Event()
    worker = MagicMock()
    worker.is_alive.return_value = True
    session._heartbeat_thread = worker
    session._client = SimpleNamespace(send_request=MagicMock())
    with pytest.raises(RuntimeError, match="Heartbeat is still running"):
        session.delete()
    assert session._heartbeat_thread is worker
    session._client.send_request.assert_not_called()


async def test_completed_wave_returns_task_interface():
    from azure.ai.finetuningsessions.models import OperationResult

    value = OperationResult({"type": "forward_backward"})
    task = await aio._completed_result_task(value, "regression-wave")
    assert isinstance(task, asyncio.Task)
    assert task.done() and task.get_name() == "regression-wave"
    assert task.get_coro() is not None
    assert await task is value


@pytest.mark.parametrize(
    "value",
    [
        {"data": "YmFk", "format": "jpeg", "expected_tokens": 1},
        {"data": "/9j/dmFsaWQ=", "format": "jpeg", "expected_tokens": 0},
    ],
)
def test_image_mapping_uses_image_validation(value):
    from azure.ai.finetuningsessions.models import ModelInput

    with pytest.raises(ValueError):
        ModelInput(chunks=[{"type": "image", **value}])


def test_multimodal_constructor_and_annotation():
    import ast
    import inspect
    from typing import get_args, get_origin, get_type_hints
    from azure.ai.finetuningsessions import models
    from azure.ai.finetuningsessions.models import ImageChunk, InputChunk, ModelInput, ModelInputChunk

    image = ImageChunk(data=b"\xff\xd8\xffvalid", format="jpeg", expected_tokens=1)
    value = ModelInput(chunks=[ModelInputChunk(tokens=[1]), image])
    assert value.as_dict()["chunks"][1]["type"] == "image"
    annotation = get_type_hints(ModelInput, localns={"_models": models})["chunks"]
    assert get_origin(annotation) is list
    (element,) = get_args(annotation)
    # Python 3.10 retains forward strings in some built-in generics.
    if isinstance(element, str):
        assert element == "_models.InputChunk"
        element = models.InputChunk
    assert element is InputChunk
    assert issubclass(ImageChunk, InputChunk)
    assert issubclass(ModelInputChunk, InputChunk)
    assert value.as_dict()["chunks"][0] == {"type": "text", "tokens": [1]}
    # Python 3.9/3.10 do not retain typing.overload definitions at runtime.
    # Inspect the shipped source on every supported version, rather than
    # skipping the overload contract or requiring Python 3.11's get_overloads.
    definition = ast.parse(inspect.getsource(ModelInput)).body[0]
    overloads = [
        method
        for method in definition.body
        if isinstance(method, ast.FunctionDef)
        and method.name == "__init__"
        and any(isinstance(decorator, ast.Name) and decorator.id == "overload" for decorator in method.decorator_list)
    ]
    assert len(overloads) == 2
