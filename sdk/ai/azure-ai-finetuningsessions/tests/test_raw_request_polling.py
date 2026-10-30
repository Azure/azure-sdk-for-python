# pylint: disable=too-many-lines
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Exercise raw begin operations through real public clients and offline transports."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import base64
import hashlib
from io import BytesIO
import json
import math
import os
from pathlib import Path
import threading
from typing import Any
from urllib.parse import parse_qs, quote, urlencode, urlsplit

import pytest
from azure.core.credentials import AccessToken, AzureKeyCredential
from azure.core.exceptions import (
    ClientAuthenticationError,
    DecodeError,
    HttpResponseError,
    ResourceExistsError,
    ResourceNotFoundError,
    ResourceNotModifiedError,
    ServiceRequestError,
)
from azure.core.pipeline.policies import AsyncRetryPolicy, RetryPolicy
from azure.core.pipeline.transport import AsyncHttpResponse, AsyncHttpTransport, HttpResponse, HttpTransport
from azure.core.polling import AsyncNoPolling, AsyncPollingMethod, NoPolling, PollingMethod
from azure.core.polling.async_base_polling import AsyncLROBasePolling
from azure.core.polling.base_polling import LROBasePolling
from azure.core.utils import case_insensitive_dict

from azure.ai.finetuningsessions import FineTuningSessionClient, _exceptions, _operation_compat
from azure.ai.finetuningsessions.aio import FineTuningSessionClient as AsyncFineTuningSessionClient
from azure.ai.finetuningsessions.models import TextOnlySampleOperationResult

ENDPOINT = "https://unit.invalid/api/projects/p"
COMMON = {"api_version": "v1", "foundry_features": "FineTuningSessions=V1Preview"}
RESULT = {"type": "optim_step", "operation_id": "request_test", "status": "succeeded", "step_count": 2}
DOWNLOAD_URL = ENDPOINT + "/fine_tuning_sessions/session_test/checkpoints/checkpoint_test/download?api-version=v1"


def download_file(file_id: str = "a" * 64, *, api_version: str = "v1", **changes: Any) -> dict[str, Any]:
    """Realistic private metadata matching the current preparation API."""
    return {
        "file_id": file_id,
        "filename": "nested/weights.bin",
        "size_bytes": 123,
        "etag": '"file-v1"',
        "download_url": f"download/files/{file_id}?" + urlencode({"api-version": api_version}),
        **changes,
    }


@dataclass
class Reply:
    """One HTTP reply, including deliberately malformed JSON when payload is bytes."""

    payload: Any
    status: int = 200
    headers: dict[str, str] = field(default_factory=dict)


class ResponseBuffer:
    """Share response buffering between the sync and async transport ABCs."""

    def initialize(self, reply: Reply) -> None:
        self.status_code = reply.status
        self.reason = "fixture"
        self.headers = case_insensitive_dict({"content-type": "application/json", **reply.headers})
        self.content_type = "application/json"
        self._body = reply.payload if isinstance(reply.payload, bytes) else json.dumps(reply.payload).encode("utf-8")
        self.is_closed = False
        self.is_stream_consumed = False

    @property
    def content(self) -> bytes:
        return self._body

    def body(self) -> bytes:
        return self._body

    def text(self, encoding: str | None = None) -> str:
        return self._body.decode(encoding or "utf-8")

    def json(self) -> Any:
        return json.loads(self._body)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise HttpResponseError(response=self)


class SyncResponse(ResponseBuffer, HttpResponse):
    """Buffered offline synchronous HTTP response."""

    def __init__(self, request: Any, reply: Reply) -> None:
        HttpResponse.__init__(self, request, None)
        self.initialize(reply)

    def read(self) -> bytes:
        self.is_stream_consumed = True
        return self._body

    def close(self) -> None:
        self.is_closed = True

    def iter_bytes(self, **_: Any):
        yield self._body

    def iter_raw(self, **_: Any):
        yield self._body

    def stream_download(self, pipeline: Any, **kwargs: Any):
        return self.iter_bytes(**kwargs)


class AsyncResponse(ResponseBuffer, AsyncHttpResponse):
    """Buffered offline asynchronous HTTP response."""

    def __init__(self, request: Any, reply: Reply) -> None:
        AsyncHttpResponse.__init__(self, request, None)
        self.initialize(reply)

    async def read(self) -> bytes:
        self.is_stream_consumed = True
        return self._body

    async def close(self) -> None:
        self.is_closed = True

    async def iter_bytes(self, **_: Any):
        yield self._body

    async def iter_raw(self, **_: Any):
        yield self._body

    def stream_download(self, pipeline: Any, **kwargs: Any):
        return self.iter_bytes(**kwargs)


class Script:
    """Record actual pipeline requests; never open a socket or sleep."""

    def __init__(self, *replies: Reply) -> None:
        self.replies = deque(replies)
        self.requests: list[dict[str, Any]] = []
        self.delays: list[float] = []

    def receive(self, request: Any, options: dict[str, Any]) -> Reply:
        content = request.content
        if hasattr(content, "read"):
            content = content.read()
        self.requests.append(
            {
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
                "options": dict(options),
                "body": json.loads(content) if content else None,
            }
        )
        assert self.replies, f"Unscripted request: {request.method} {request.url}"
        return self.replies.popleft()

    def sleep(self, duration: float) -> None:
        assert math.isfinite(duration) and duration >= 0
        self.delays.append(duration)


class SyncTransport(HttpTransport):
    """Run the real sync pipeline against a deterministic reply script."""

    def __init__(self, script: Script) -> None:
        self.script = script

    def send(self, request: Any, **kwargs: Any) -> SyncResponse:
        return SyncResponse(request, self.script.receive(request, kwargs))

    def open(self) -> None:
        pass

    def close(self) -> None:
        pass

    def __exit__(self, *args: Any) -> None:
        self.close()

    def sleep(self, duration: float) -> None:
        self.script.sleep(duration)


class AsyncTransport(AsyncHttpTransport):
    """Run the real async pipeline against a deterministic reply script."""

    def __init__(self, script: Script) -> None:
        self.script = script

    async def send(self, request: Any, **kwargs: Any) -> AsyncResponse:
        return AsyncResponse(request, self.script.receive(request, kwargs))

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def sleep(self, duration: float) -> None:
        self.script.sleep(duration)


def client_for(script: Script, asynchronous: bool, **kwargs: Any) -> Any:
    """Construct a public client, preserving generated groups and real policies."""
    client_type = AsyncFineTuningSessionClient if asynchronous else FineTuningSessionClient
    transport = AsyncTransport(script) if asynchronous else SyncTransport(script)
    options = {"polling_interval": 0, "retry_total": 0, **kwargs}
    endpoint = options.pop("endpoint", ENDPOINT)
    credential = options.pop("credential", AzureKeyCredential("fixture-key"))
    return client_type(endpoint, credential, transport=transport, **options)


async def begin(client: Any, asynchronous: bool, **kwargs: Any) -> Any:
    """Submit a raw training request without using convenience polling helpers."""
    session_id = kwargs.pop("session_id", "session_test")
    body = kwargs.pop("body", {})
    result = client.training.begin_optim_step(session_id, body, **COMMON, **kwargs)
    return await result if asynchronous else result


async def result_of(poller: Any, asynchronous: bool) -> Any:
    """Wait through Azure Core's public sync or async poller API."""
    return await poller.result() if asynchronous else poller.result(timeout=5)


async def close_client(client: Any, asynchronous: bool) -> None:
    """Close clients even when protocol validation raises."""
    if asynchronous:
        await client.close()
    else:
        client.close()


def test_public_source_import() -> None:
    """Source and installed-wheel runs must load the complete reviewed runtime."""
    imported = Path(_operation_compat.__file__).resolve()
    explicit_root = os.environ.get("FINETUNING_TEST_PACKAGE_ROOT")
    if explicit_root is not None:
        assert imported == Path(explicit_root).resolve() / "azure/ai/finetuningsessions/_operation_compat.py"
    source = Path(__file__).resolve().parents[1] / "azure/ai/finetuningsessions"

    def inventory(directory):
        return {
            file.relative_to(directory)
            .as_posix(): hashlib.sha256(file.read_bytes().replace(b"\r\n", b"\n"))
            .hexdigest()
            for file in directory.rglob("*")
            if file.is_file() and "__pycache__" not in file.parts
        }

    expected = inventory(source)
    assert len(expected) == 32
    assert {
        "_text_only.py",
        "models/_text_only.py",
        "_checkpoint_download.py",
        "_scalar_serialization.py",
    } <= expected.keys()
    assert inventory(imported.parent) == expected


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_raw_sampling_poller_preserves_public_choices(asynchronous: bool) -> None:
    """Raw JSON bodies use the same routes and expose choices, not token sequences."""
    public = {
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": "hello", "tool_calls": []},
                "sample_ref": "opaque-do-not-decode",
                "finish_reason": "stop",
            }
        ]
    }
    script = Script(
        Reply({"request_id": "request_test", "status": "pending"}),
        Reply({"status": "completed", "result": public}),
    )
    client = client_for(script, asynchronous)
    try:
        poller = client.sampling.begin_sample(
            "session_test",
            {
                "text_only_input": {"messages": [{"role": "user", "content": "hello"}]},
                "sampling_params": {"max_tokens": 8},
            },
            params={"checkpoint_id": "sampler_test"},
            **COMMON,
        )
        if asynchronous:
            poller = await poller
        value = await result_of(poller, asynchronous)
        assert isinstance(value, TextOnlySampleOperationResult)
        assert value.choices[0].sample_ref == "opaque-do-not-decode"
        assert value.as_dict() == public
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("keyword_inputs", [False, True], ids=["positional", "keyword"])
@pytest.mark.parametrize("token_credential", [False, True], ids=["key", "token"])
async def test_download_weights_validates_and_polls_without_writing_files(
    asynchronous, keyword_inputs, token_credential, tmp_path
):
    scopes_requested = []

    class Credential:
        def get_token(self, *scopes, **kwargs):
            scopes_requested.append(scopes)
            return AccessToken("fixture-token", 2**31)

    class AsyncCredential(Credential):
        async def get_token(self, *scopes, **kwargs):
            return super().get_token(*scopes, **kwargs)

    credential = (
        (AsyncCredential() if asynchronous else Credential()) if token_credential else AzureKeyCredential("fixture-key")
    )
    script = Script(
        Reply({"status": "Pending"}, status=202, headers={"Retry-After": "30"}),
        Reply({"status": "Pending"}, status=202, headers={"Retry-After": "1000"}),
        Reply({"status": "Pending"}, status=202),
        Reply({"status": "Succeeded", "files": [download_file(api_version="test-preview")]}),
    )
    (tmp_path / "unrelated.txt").write_text("keep")
    client = client_for(script, asynchronous, credential=credential, api_version="test-preview", polling_interval=7)
    try:
        result = (
            client.checkpoints.download_weights(
                session_id="session_test", checkpoint_id="checkpoint_test", output_path=tmp_path
            )
            if keyword_inputs
            else client.checkpoints.download_weights("session_test", "checkpoint_test", str(tmp_path))
        )
        if asynchronous:
            result = await result
        assert result is None
        assert len(script.requests) == 4
        for request in script.requests:
            assert request["method"] == "POST"
            assert request["url"] == DOWNLOAD_URL.replace("api-version=v1", "api-version=test-preview")
            assert request["headers"]["Foundry-Features"] == COMMON["foundry_features"]
            if token_credential:
                assert request["headers"]["Authorization"] == "Bearer fixture-token"
                assert "api-key" not in request["headers"]
            else:
                assert request["headers"]["api-key"] == "fixture-key"
                assert "Authorization" not in request["headers"]
            assert request["body"] is None
        assert scopes_requested == ([("https://ai.azure.com/.default",)] if token_credential else [])
        assert script.delays == [30, 60, 7]
        assert not script.replies
        assert [path.name for path in tmp_path.iterdir()] == ["unrelated.txt"]
        assert (tmp_path / "unrelated.txt").read_text() == "keep"
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "reply,error_type",
    [
        (Reply({}, status=401), ClientAuthenticationError),
        (Reply({"detail": {"type": "checkpoint_download_disabled"}}, status=403), HttpResponseError),
        (Reply({}, status=404), ResourceNotFoundError),
        (Reply({"detail": "Checkpoint registration is pending. Try again later."}, status=409), ResourceExistsError),
        (Reply({}, status=500), HttpResponseError),
        (Reply({}, status=503), HttpResponseError),
        (Reply({}, status=307, headers={"Location": "https://other.invalid/config"}), HttpResponseError),
        (Reply(b"{"), DecodeError),
        (Reply({"status": "Failed"}), _exceptions.FineTuningSessionsError),
        (Reply({}), _exceptions.MalformedResponseError),
        (Reply({"status": "Pending"}), _exceptions.MalformedResponseError),
        (Reply({"status": "Succeeded"}), _exceptions.MalformedResponseError),
        (Reply({"status": "Succeeded"}, status=202), _exceptions.MalformedResponseError),
    ],
)
async def test_download_server_errors_are_explicit_without_retry_redirect_or_transfer(
    asynchronous, reply, error_type, tmp_path
):
    script = Script(Reply({"status": "Pending"}, status=202, headers={"Retry-After": "2"}), reply)
    client = client_for(script, asynchronous, retry_total=5, retry_status=5)
    try:
        with pytest.raises(error_type):
            result = client.checkpoints.download_weights("session_test", "checkpoint_test", tmp_path)
            if asynchronous:
                await result
        assert len(script.requests) == 2
        assert all(request["url"] == DOWNLOAD_URL for request in script.requests)
        assert script.delays == [2]
        assert list(tmp_path.iterdir()) == []
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_download_transport_failure_is_not_retried(asynchronous, monkeypatch, tmp_path):
    script = Script(Reply({"status": "Pending"}, status=202, headers={"Retry-After": "2"}), Reply({}))
    receive = script.receive

    def fail(request, options):
        reply = receive(request, options)
        if len(script.requests) == 2:
            raise ServiceRequestError("offline preparation transport failure")
        return reply

    monkeypatch.setattr(script, "receive", fail)
    client = client_for(script, asynchronous, retry_total=5)
    try:
        with pytest.raises(ServiceRequestError, match="offline preparation transport failure"):
            result = client.checkpoints.download_weights("session_test", "checkpoint_test", tmp_path)
            if asynchronous:
                await result
        assert len(script.requests) == 2
        assert script.delays == [2]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "session_id,expected_session_id,checkpoint_id,endpoint",
    [
        ("session_abc", "session_abc", "step-100", ENDPOINT),
        ("model_abc", "session_abc", "step-100", ENDPOINT),
        ("abc", "session_abc", "step-100", ENDPOINT),
        ("session_abc_dz", "session_abc_dz", "step-100", ENDPOINT),
        ("session_a %#", "session_a %#", "step %#-100", ENDPOINT),
        (
            "session_abc",
            "session_abc",
            "step-100",
            "https://unit.invalid/subscriptions/arm-sub/resourceGroups/rg/providers/"
            "Microsoft.CognitiveServices/accounts/account",
        ),
        (
            "session_abc",
            "session_abc",
            "step-100",
            "https://unit.invalid/loom/v1.0/subscriptions/arm-sub/resourceGroups/rg/providers/"
            "Microsoft.MachineLearningServices/workspaces/account@project@AML",
        ),
    ],
)
async def test_download_normalizes_http_ids_but_preserves_local_path(
    asynchronous, session_id, expected_session_id, checkpoint_id, endpoint, tmp_path, monkeypatch
):
    monkeypatch.setenv("X_COGNITIVE_SUBSCRIPTION_ID", "fixture-sub")
    if session_id != expected_session_id:
        other = tmp_path / expected_session_id / checkpoint_id
        other.mkdir(parents=True)
        (other / "weights.bin").write_bytes(b"keep")
    before = list(tmp_path.rglob("*"))
    script = Script(Reply({"status": "Succeeded", "files": [download_file()]}))
    client = client_for(script, asynchronous, endpoint=endpoint)
    try:
        result = client.checkpoints.download_weights(session_id, checkpoint_id, tmp_path)
        if asynchronous:
            result = await result
        assert result is None
        assert len(script.requests) == 1
        request = script.requests[0]
        assert request["method"] == "POST"
        assert request["url"] == (
            endpoint
            + "/fine_tuning_sessions/"
            + quote(expected_session_id, safe="")
            + "/checkpoints/"
            + quote(checkpoint_id, safe="")
            + "/download?api-version=v1"
        )
        assert request["body"] is None
        assert request["headers"]["apim-subscription-id"] == "fixture-sub"
        assert not script.delays
        assert list(tmp_path.rglob("*")) == before
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_download_rejects_nonempty_verbatim_checkpoint_before_http(asynchronous, tmp_path):
    checkpoint = tmp_path / "model_legacy" / "final"
    checkpoint.mkdir(parents=True)
    (checkpoint / "weights.bin").write_bytes(b"keep")
    script = Script()
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(ValueError, match="Checkpoint directory must be empty"):
            result = client.checkpoints.download_weights("model_legacy", "final", tmp_path)
            if asynchronous:
                await result
        assert not script.requests
        assert (checkpoint / "weights.bin").read_bytes() == b"keep"
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "session_id,checkpoint_id,interval",
    [("session_", "c", 0), ("model_", "c", 0), ("session_s", "c", math.inf)],
)
async def test_download_invalid_request_options_do_not_send_requests(
    asynchronous, session_id, checkpoint_id, interval, tmp_path
):
    script = Script()
    client = client_for(script, asynchronous, polling_interval=interval)
    try:
        with pytest.raises(ValueError):
            result = client.checkpoints.download_weights(session_id, checkpoint_id, tmp_path)
            if asynchronous:
                await result
        assert not script.requests
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_http200_acceptance_is_not_completion(asynchronous: bool) -> None:
    script = Script(
        Reply({"request_id": "request_test", "status": "pending"}),
        Reply({"status": "pending"}),
        Reply({"status": "completed", "result": RESULT}),
    )
    client = client_for(script, asynchronous)
    try:
        poller = await begin(client, asynchronous)
        value = await result_of(poller, asynchronous)
        assert value.as_dict() == RESULT
        assert [request["method"] for request in script.requests] == ["POST", "GET", "GET"]
        assert not script.replies
        assert poller.done()
    finally:
        await close_client(client, asynchronous)


OPERATIONS = [
    ("sessions", "begin_create", "", "created"),
    ("sessions", "begin_unload", "/complete", "pending"),
    ("training", "begin_forward_backward", "/forward_backward", "pending"),
    ("training", "begin_optim_step", "/optim_step", "pending"),
    ("checkpoints", "begin_save", "/checkpoint", "pending"),
    ("checkpoints", "begin_save_sampler_weights", "/checkpoint_sample", "pending"),
    ("sampling", "begin_sample", "/sample", "pending"),
]


@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize("group,method,path,status", OPERATIONS)
async def test_all_raw_begin_routes_and_pending_states(asynchronous, group, method, path, status):
    session_id, request_id = "session a/%?#é", "request a/%?#é"
    accepted = {"request_id": request_id, "status": status}
    if method in ("begin_create", "begin_forward_backward"):
        accepted["session_id"] = session_id
    script = Script(
        Reply(accepted),
        Reply({"status": "pending", "result": RESULT}),
        Reply({"status": "queued"}),
        Reply({"status": "running"}),
        Reply({"status": "completed", "result": RESULT, "request_id": request_id, "session_id": session_id}),
    )
    client = client_for(script, asynchronous)
    try:
        args = [] if method == "begin_create" else [session_id]
        if method != "begin_unload":
            args.append({"fixture": "unchanged"})
        poller = getattr(getattr(client, group), method)(*args, **COMMON)
        if asynchronous:
            poller = await poller
        assert isinstance(poller.polling_method(), AsyncPollingMethod if asynchronous else PollingMethod)
        assert (await result_of(poller, asynchronous)).as_dict() == RESULT
        assert poller.status() == "Succeeded"
        base = ENDPOINT + "/fine_tuning_sessions"
        post_base = ENDPOINT + "/fine_tuning/sessions" if method == "begin_sample" else base
        expected_post = post_base if method == "begin_create" else post_base + "/" + quote(session_id, safe="") + path
        assert script.requests[0]["url"] == expected_post + "?api-version=v1"
        assert script.requests[0]["body"] == (None if method == "begin_unload" else {"fixture": "unchanged"})
        expected_poll = base + "/" + quote(session_id, safe="") + "/request/" + quote(request_id, safe="")
        assert all(item["url"] == expected_poll + "?api-version=v1" for item in script.requests[1:])
        assert [item["method"] for item in script.requests] == ["POST", "GET", "GET", "GET", "GET"]
        assert not script.replies
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("shape", ["dict", "bytes", "io"])
async def test_final_cls_and_caller_pipeline_options(asynchronous, shape):
    callback_calls, hooks = [], []

    def callback(response, value, headers):
        callback_calls.append((response.http_request.method, response.http_response.status_code, headers))
        return {"custom": value.as_dict()}

    script = Script(
        Reply({"request_id": "request_test"}, headers={"Operation-Location": "https://evil.invalid/initial"}),
        Reply({"status": "completed", "result": RESULT}, headers={"Operation-Location": "https://evil.invalid/final"}),
    )
    client = client_for(script, asynchronous)
    body = {"adam_params": {"learning_rate": 0.001}}
    if shape != "dict":
        body = json.dumps(body).encode()
        if shape == "io":
            body = BytesIO(body)
    try:
        poller = await begin(
            client,
            asynchronous,
            body=body,
            cls=callback,
            headers={"x-fixture": "header", "Content-Type": "application/json"},
            params={"extra": "a b", "api-version": "not-used"},
            connection_timeout=12,
            raw_response_hook=lambda response: hooks.append(response.http_request.method),
        )
        assert await result_of(poller, asynchronous) == {"custom": RESULT}
        assert callback_calls == [("GET", 200, {"Operation-Location": "https://evil.invalid/final"})]
        assert hooks == ["POST", "GET"]
        for request in script.requests:
            assert request["headers"]["x-fixture"] == "header"
            assert request["headers"]["Foundry-Features"] == COMMON["foundry_features"]
            assert request["options"]["connection_timeout"] == 12
            assert parse_qs(urlsplit(request["url"]).query) == {"extra": ["a b"], "api-version": ["v1"]}
        assert script.requests[0]["body"] == {"adam_params": {"learning_rate": 0.001}}
        assert script.requests[1]["body"] is None
        assert "Content-Length" not in script.requests[1]["headers"]
    finally:
        await close_client(client, asynchronous)


HTTP_ERRORS = [
    (400, {"error": {"code": "bad", "message": "fixture"}}, HttpResponseError),
    (401, {}, ClientAuthenticationError),
    (404, {}, ResourceNotFoundError),
    (409, {"error": {"code": "Conflict", "message": "already exists"}}, ResourceExistsError),
    (304, {}, ResourceNotModifiedError),
    (
        413,
        {"detail": {"field": "data", "message": "Batch size (20) exceeds the maximum allowed (10)"}},
        _exceptions.BatchTooLargeError,
    ),
    (
        422,
        {"detail": {"error_code": "invalid_request", "message": "invalid datum"}},
        _exceptions.RequestValidationError,
    ),
    (429, {"detail": {"retry_after_sec": "nan"}}, _exceptions.RateLimitedError),
    (409, {"detail": {"reason": "engine_dead", "message": "engine died"}}, _exceptions.TrainingEngineError),
    (500, {"error_code": "worker_crashed", "message": "engine died"}, _exceptions.TrainingEngineError),
    (503, {"detail": {"reason": "engine_busy", "retry_after_sec": "inf"}}, _exceptions.NoCapacityError),
    (418, ["not-an-object"], HttpResponseError),
    (404, b"not-json", ResourceNotFoundError),
    (202, {"request_id": "request_test", "status": "pending"}, HttpResponseError),
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("stage", ["submit", "poll"])
@pytest.mark.parametrize("status,payload,error_type", HTTP_ERRORS)
async def test_http_error_mapping(asynchronous, stage, status, payload, error_type):
    replies = [] if stage == "submit" else [Reply({"request_id": "request_test"})]
    script = Script(*replies, Reply(payload, status=status))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(error_type) as caught:
            await result_of(await begin(client, asynchronous), asynchronous)
        assert type(caught.value) is error_type
        assert caught.value.status_code == status
        assert caught.value.response is not None
        assert [item["method"] for item in script.requests] == (["POST"] if stage == "submit" else ["POST", "GET"])
    finally:
        await close_client(client, asynchronous)


class CallerError(HttpResponseError):
    """Caller-selected error_map exception."""


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("stage", ["submit", "poll", "failed"])
async def test_error_map_overrides_typed_errors(asynchronous, stage):
    replies = [] if stage == "submit" else [Reply({"request_id": "request_test"})]
    status = 200 if stage == "failed" else 409
    payload = (
        {"status": "failed", "error": "engine died", "error_code": "engine_dead"}
        if stage == "failed"
        else {"detail": {"reason": "engine_dead"}}
    )
    script = Script(*replies, Reply(payload, status=status))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(CallerError):
            await result_of(await begin(client, asynchronous, error_map={status: CallerError}), asynchronous)
        assert all("error_map" not in item["options"] for item in script.requests)
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_error_map_none_disables_default_mapping(asynchronous):
    script = Script(Reply({"request_id": "request_test"}), Reply({"reason": "engine_dead"}, status=409))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(HttpResponseError) as caught:
            await result_of(await begin(client, asynchronous, error_map={409: None}), asynchronous)
        assert type(caught.value) is HttpResponseError
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_error_map_applies_even_to_non_json_poll_error(asynchronous):
    script = Script(Reply({"request_id": "request_test"}), Reply(b"not-json", status=503))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(CallerError):
            await result_of(await begin(client, asynchronous, error_map={503: CallerError}), asynchronous)
    finally:
        await close_client(client, asynchronous)


FAILED_ERRORS = [
    ({"error_code": "worker_crashed"}, _exceptions.TrainingEngineError),
    (
        {"error_code": "engine_dead", "should_retry": True, "retry_after_sec": 1},
        _exceptions.TrainingEngineError,
    ),
    ({"error_code": "engine_oom"}, _exceptions.BatchTooLargeError),
    ({"error_code": "invalid_request"}, _exceptions.RequestValidationError),
    ({"error_code": "anything", "should_retry": True, "retry_after_sec": "inf"}, _exceptions.RequestRetryableError),
    (
        {"error_code": "operation_completed_result_unavailable", "should_retry": True},
        _exceptions.OperationResultUnavailableError,
    ),
    ({"error_code": "operation_failed_result_unavailable"}, _exceptions.OperationResultUnavailableError),
    ({"error_code": "unknown"}, HttpResponseError),
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("failure,error_type", FAILED_ERRORS)
async def test_failed_envelopes_never_resubmit(asynchronous, failure, error_type):
    script = Script(
        Reply({"request_id": "request_test"}),
        Reply({"status": "failed", "error": "fixture failure", "debug_ref": "support", **failure}),
    )
    client = client_for(script, asynchronous)
    try:
        poller = await begin(client, asynchronous)
        for _ in range(2):
            with pytest.raises(error_type) as caught:
                await result_of(poller, asynchronous)
            assert type(caught.value) is error_type
        assert poller.status() == "Failed"
        assert caught.value.response.status_code == 200
        assert [item["method"] for item in script.requests] == ["POST", "GET"]
        if isinstance(caught.value, _exceptions.RequestRetryableError):
            assert caught.value.retry_after_sec is None
        if isinstance(caught.value, _exceptions.TrainingEngineError):
            assert caught.value.session_id == "session_test"
            assert "continual fine-tuning (CFT)" in str(caught.value)
            assert "completed training checkpoint" in str(caught.value)
        if isinstance(caught.value, _exceptions.OperationResultUnavailableError):
            assert caught.value.operation_completed == (
                failure["error_code"] == "operation_completed_result_unavailable"
            )
    finally:
        await close_client(client, asynchronous)


BAD_ACCEPTANCE = [
    None,
    [],
    "text",
    b"not-json",
    {},
    {"request_id": ""},
    {"request_id": 123},
    {"request_id": []},
    {"request_id": ".."},
    {"request_id": "r\n"},
    {"request_id": " "},
    {"request_id": "x" * 1025},
    {"request_id": "r", "session_id": "different"},
    {"request_id": "r", "session_id": None},
    {"request_id": "r", "status": "succeeded"},
    {"request_id": "r", "status": []},
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("payload", BAD_ACCEPTANCE)
async def test_malformed_acceptance_is_rejected(asynchronous, payload):
    script = Script(Reply(payload))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(HttpResponseError, match="acceptance|JSON object"):
            await begin(client, asynchronous)
        assert [item["method"] for item in script.requests] == ["POST"]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("payload", [{"request_id": "r"}, {"request_id": "r", "session_id": 12}])
async def test_create_requires_returned_session_id(asynchronous, payload):
    script = Script(Reply(payload))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(HttpResponseError, match="session_id"):
            poller = client.sessions.begin_create({}, **COMMON)
            if asynchronous:
                await poller
    finally:
        await close_client(client, asynchronous)


BAD_ENVELOPES = [
    (None, "JSON object"),
    ([], "JSON object"),
    (b"not-json", "JSON object"),
    ({}, "Unexpected.*status"),
    ({"status": "succeeded", "result": RESULT}, "Unexpected.*status"),
    ({"status": []}, "Unexpected.*status"),
    ({"status": "mystery"}, "Unexpected.*status"),
    ({"status": "completed"}, "result must be an object"),
    ({"status": "completed", "result": None}, "result must be an object"),
    ({"status": "completed", "result": []}, "result must be an object"),
    ({"status": "failed", "error": {}}, "error must be a string"),
    ({"status": "pending", "request_id": "different"}, "request_id"),
    ({"status": "completed", "result": RESULT, "session_id": "different"}, "session_id"),
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("payload,match", BAD_ENVELOPES)
async def test_bad_poll_envelope_is_never_completion(asynchronous, payload, match):
    script = Script(Reply({"request_id": "request_test"}), Reply(payload))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(HttpResponseError, match=match):
            await result_of(await begin(client, asynchronous), asynchronous)
        assert [item["method"] for item in script.requests] == ["POST", "GET"]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_actual_engine_result_without_discriminator_is_preserved(asynchronous):
    raw = {"metrics": {"skyrl.ai/grad_norm": 0.25}, "step": 3}
    script = Script(Reply({"request_id": "request_test"}), Reply({"status": "completed", "result": raw}))
    client = client_for(script, asynchronous)
    try:
        assert (await result_of(await begin(client, asynchronous), asynchronous)).as_dict() == raw
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("mode", ["false", "no_polling", "azure_base"])
async def test_explicit_polling_strategy_owns_http200(asynchronous, mode):
    script = Script(Reply({"result": RESULT}))  # No request/session locator is needed by these strategies.
    client = client_for(script, asynchronous)
    strategy = False
    if mode == "no_polling":
        strategy = AsyncNoPolling() if asynchronous else NoPolling()
    elif mode == "azure_base":
        strategy = AsyncLROBasePolling(timeout=0) if asynchronous else LROBasePolling(timeout=0)
    try:
        poller = await begin(client, asynchronous, polling=strategy)
        assert (await result_of(poller, asynchronous)).as_dict() == RESULT
        if mode != "false":
            assert poller.polling_method() is strategy
        assert [item["method"] for item in script.requests] == ["POST"]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_custom_continuation_token_remains_caller_owned(asynchronous):
    saved = []

    class CustomPolling(NoPolling):
        def initialize(self, client, initial_response, deserialization_callback):
            assert initial_response.http_response.status_code == 200
            saved.append(initial_response)
            super().initialize(client, initial_response, deserialization_callback)

        def get_continuation_token(self):
            return "caller-owned-token"

        @classmethod
        def from_continuation_token(cls, continuation_token, **kwargs):
            assert continuation_token == "caller-owned-token"
            return kwargs["client"], saved[0], kwargs["deserialization_callback"]

    class AsyncCustomPolling(CustomPolling, AsyncNoPolling):
        async def run(self):
            pass

    script = Script(Reply({"result": RESULT}))
    client = client_for(script, asynchronous)
    strategy = AsyncCustomPolling() if asynchronous else CustomPolling()
    try:
        original = await begin(client, asynchronous, polling=strategy)
        resumed = await begin(client, asynchronous, polling=strategy, continuation_token=original.continuation_token())
        assert (await result_of(resumed, asynchronous)).as_dict() == RESULT
        assert len(saved) == 2
        assert [item["method"] for item in script.requests] == ["POST"]
    finally:
        await close_client(client, asynchronous)


def locator_token(**changes):
    """Build a documented test locator without using SDK token decoder internals."""
    state = {
        "kind": "azure.ai.finetuningsessions.request",
        "version": 1,
        "endpoint": ENDPOINT,
        "operation": "build_training_optim_step_request",
        "api_version": "v1",
        "session_id": "session_test",
        "request_id": "request_test",
        **changes,
    }
    return base64.urlsafe_b64encode(json.dumps(state).encode()).decode()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("create", [False, True])
async def test_continuation_resumes_get_without_second_post(asynchronous, create):
    accepted = {"request_id": "request_test", "session_id": "session_test"}
    script = Script(Reply(accepted), Reply({"status": "pending"}), Reply({"error": "offline"}, status=418))
    client = client_for(script, asynchronous)
    try:
        if create:
            poller = client.sessions.begin_create({}, **COMMON, headers={"x-private": "secret"})
            if asynchronous:
                poller = await poller
        else:
            poller = await begin(client, asynchronous, headers={"x-private": "secret"})
        with pytest.raises(HttpResponseError) as caught:
            await result_of(poller, asynchronous)
        token = poller.continuation_token()
        assert caught.value.continuation_token == token
        state = json.loads(base64.urlsafe_b64decode(token))
        assert set(state) == {"kind", "version", "endpoint", "operation", "api_version", "session_id", "request_id"}
        assert "secret" not in json.dumps(state) and "fixture-key" not in json.dumps(state)
    finally:
        await close_client(client, asynchronous)
    # Rehydrate with the opposite client mode to prove tokens carry no transport objects.
    resumed_script = Script(Reply({"status": "running"}), Reply({"status": "completed", "result": RESULT}))
    resumed_client = client_for(resumed_script, not asynchronous)
    try:
        if create:
            resumed = resumed_client.sessions.begin_create(object(), **COMMON, continuation_token=token)
            if not asynchronous:
                resumed = await resumed
        else:
            resumed = await begin(resumed_client, not asynchronous, body=object(), continuation_token=token)
        assert (await result_of(resumed, not asynchronous)).as_dict() == RESULT
        assert [item["method"] for item in script.requests] == ["POST", "GET", "GET"]
        assert [item["method"] for item in resumed_script.requests] == ["GET", "GET"]
        assert all(
            "/fine_tuning_sessions/session_test/request/request_test?" in item["url"]
            for item in resumed_script.requests
        )
    finally:
        await close_client(resumed_client, not asynchronous)


INVALID_TOKENS = [
    "",
    "not-a-token",
    base64.b64encode(b"\x80\x04}.").decode(),
    base64.b64encode(b"[]").decode(),
    base64.b64encode(b"{}").decode(),
    locator_token(version=True),
    locator_token(version=1.0),
    locator_token(version=2),
    locator_token(endpoint="https://evil.invalid"),
    locator_token(endpoint=ENDPOINT + "/other"),
    locator_token(endpoint=ENDPOINT.replace("https:", "http:")),
    locator_token(endpoint="https://user:password@unit.invalid/api/projects/p"),
    locator_token(endpoint=ENDPOINT + "?key=secret"),
    locator_token(session_id="different"),
    locator_token(request_id=""),
    locator_token(request_id=".."),
    locator_token(request_id="bad\r\n"),
    locator_token(request_id=[]),
    locator_token(api_version="v2"),
    locator_token(operation="build_sessions_create_request"),
    locator_token(poll_url="https://evil.invalid"),
    "A" * 65537,
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("token", INVALID_TOKENS, ids=[f"invalid-{i}" for i in range(len(INVALID_TOKENS))])
async def test_invalid_continuation_is_rejected_before_http(asynchronous, token):
    script = Script()
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(ValueError):
            await begin(client, asynchronous, continuation_token=token)
        assert not script.requests
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_token_request_id_is_encoded_not_interpreted_as_url(asynchronous):
    request_id = "https://evil.invalid/?secret=x#fragment"
    script = Script(Reply({"status": "completed", "result": RESULT}))
    client = client_for(script, asynchronous)
    try:
        poller = await begin(client, asynchronous, continuation_token=locator_token(request_id=request_id))
        await result_of(poller, asynchronous)
        assert script.requests[0]["url"] == (
            ENDPOINT + "/fine_tuning_sessions/session_test/request/" + quote(request_id, safe="") + "?api-version=v1"
        )
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_default_polling_ignores_server_urls_and_disallows_redirects(asynchronous):
    headers = {"Operation-Location": "https://evil.invalid/op", "Location": "https://evil.invalid/result"}
    script = Script(Reply({"request_id": "request_test"}, headers=headers), Reply({}, status=307, headers=headers))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(HttpResponseError):
            await result_of(await begin(client, asynchronous, permit_redirects=True), asynchronous)
        assert [item["method"] for item in script.requests] == ["POST", "GET"]
        assert all(urlsplit(item["url"]).hostname == "unit.invalid" for item in script.requests)
    finally:
        await close_client(client, asynchronous)


HINTS = [
    ({"Retry-After": "2.5"}, None, 2.5),
    ({"Retry-After": "9999999999999"}, None, 60.0),
    ({"Retry-After": "nan"}, None, 3.0),
    ({"Retry-After": "inf"}, None, 3.0),
    ({"Retry-After": "-1"}, None, 3.0),
    ({"Retry-After": "later"}, None, 3.0),
    ({"Retry-After": "0"}, None, 0.0),
    ({"retry-after-ms": "1250"}, None, 1.25),
    ({"x-ms-retry-after-ms": "250"}, None, 0.25),
    ({"Retry-After": "Wed, 01 Jan 2100 00:00:00 GMT"}, None, 60.0),
    ({}, 2.0, 2.0),
    ({}, 10**400, 3.0),
    ({}, "Infinity", 3.0),
    ({}, [], 3.0),
    ({}, -2, 3.0),
    ({}, True, 3.0),
    ({}, 9000000, 60.0),
]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("headers,hint,expected", HINTS)
async def test_retry_hints_are_finite_and_bounded(asynchronous, headers, hint, expected):
    script = Script(
        Reply({"request_id": "request_test"}),
        Reply({"status": "pending", "retry_after_sec": hint}, headers=headers),
        Reply({"status": "completed", "result": RESULT}),
    )
    client = client_for(script, asynchronous)
    try:
        await result_of(await begin(client, asynchronous, polling_interval=3), asynchronous)
        assert script.delays == [expected]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("interval", [float("nan"), float("inf"), -1, True, {}, "later"])
async def test_invalid_polling_interval_fails_before_submission(asynchronous, interval):
    script = Script()
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(ValueError, match="polling_interval"):
            await begin(client, asynchronous, polling_interval=interval)
        assert not script.requests
    finally:
        await close_client(client, asynchronous)


def test_sync_result_timeout_cannot_deserialize_acceptance_or_pending():
    entered, release = threading.Event(), threading.Event()

    class PausedScript(Script):
        def sleep(self, duration):
            super().sleep(duration)
            entered.set()
            assert release.wait(5), "Test did not release the pending poller"

    script = PausedScript(
        Reply({"request_id": "request_test", "result": {"premature": True}}),
        Reply({"status": "pending", "result": {"premature": True}}),
        Reply({"status": "completed", "result": RESULT}),
    )
    client = client_for(script, False)
    poller = None
    try:
        poller = client.training.begin_optim_step("session_test", {}, **COMMON)
        assert entered.wait(5)
        assert not poller.done()
        assert poller.status() == "InProgress"
        assert poller.result(timeout=0) is None
    finally:
        release.set()
        if poller is not None:
            poller.wait(5)
        client.close()
    assert poller.result().as_dict() == RESULT


async def test_async_before_wait_is_not_complete_and_has_no_resource():
    script = Script(Reply({"request_id": "request_test"}), Reply({"status": "completed", "result": {}}))
    client = client_for(script, True)
    try:
        poller = await begin(client, True)
        assert not poller.done()
        assert poller.status() == "InProgress"
        assert poller.polling_method().resource() is None
        assert [item["method"] for item in script.requests] == ["POST"]
        assert (await poller.result()).as_dict() == {}
        assert poller.status() == "Succeeded"
    finally:
        await close_client(client, True)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_explicit_azure_base_poller_retains_real_http200_protocol(asynchronous):
    location = ENDPOINT + "/caller-owned-status"
    script = Script(
        Reply({"status": "InProgress"}, headers={"Operation-Location": location}),
        Reply({"status": "Succeeded", "result": RESULT}),
    )
    client = client_for(script, asynchronous)
    strategy = AsyncLROBasePolling(timeout=0) if asynchronous else LROBasePolling(timeout=0)
    try:
        poller = await begin(client, asynchronous, polling=strategy)
        assert (await result_of(poller, asynchronous)).as_dict() == RESULT
        assert script.requests[1]["url"] == location
        assert poller.polling_method() is strategy
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_queued_creation_polls_request_and_preserves_raw_session_id(asynchronous):
    script = Script(
        Reply({"request_id": "r", "session_id": "model_test", "status": "queued"}),
        Reply({"status": "completed", "result": {"session_id": "session_test"}}),
    )
    client = client_for(script, asynchronous)
    try:
        poller = client.sessions.begin_create({}, **COMMON)
        if asynchronous:
            poller = await poller
        assert (await result_of(poller, asynchronous)).as_dict() == {"session_id": "session_test"}
        assert script.requests[1]["url"] == ENDPOINT + "/fine_tuning_sessions/model_test/request/r?api-version=v1"
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_completed_post_still_requires_verified_request_get(asynchronous):
    script = Script(
        Reply({"request_id": "request_test", "status": "completed", "result": {"premature": True}}),
        Reply({"status": "completed", "result": RESULT}),
    )
    client = client_for(script, asynchronous)
    try:
        assert (await result_of(await begin(client, asynchronous), asynchronous)).as_dict() == RESULT
        assert [item["method"] for item in script.requests] == ["POST", "GET"]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_failed_poll_http_error_is_repeated_without_new_get(asynchronous):
    script = Script(Reply({"request_id": "request_test"}), Reply({"detail": "gone"}, status=404))
    client = client_for(script, asynchronous)
    try:
        poller = await begin(client, asynchronous)
        for _ in range(2):
            with pytest.raises(ResourceNotFoundError):
                await result_of(poller, asynchronous)
        assert poller.status() == "Failed"
        assert [item["method"] for item in script.requests] == ["POST", "GET"]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("stage", ["submit", "poll"])
@pytest.mark.parametrize("hint", ["inf", "nan", "999999999999999", "invalid"])
async def test_default_strategy_cannot_replay_post_or_sleep_in_core_retry(asynchronous, stage, hint):
    replies = [] if stage == "submit" else [Reply({"request_id": "request_test"})]
    script = Script(*replies, Reply({"detail": "unavailable"}, status=503, headers={"Retry-After": hint}))
    # Exercise real RetryPolicy configuration, not the tests' usual retry_total=0.
    client = client_for(script, asynchronous, retry_total=3)
    try:
        with pytest.raises(_exceptions.ContentionError):
            await result_of(await begin(client, asynchronous, retry_total=5), asynchronous)
        assert [item["method"] for item in script.requests] == (["POST"] if stage == "submit" else ["POST", "GET"])
        assert script.delays == []
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_default_post_does_not_follow_mutation_redirect(asynchronous):
    script = Script(Reply({}, status=307, headers={"Location": ENDPOINT + "/replay"}))
    client = client_for(script, asynchronous)
    try:
        with pytest.raises(HttpResponseError):
            await result_of(await begin(client, asynchronous, permit_redirects=True), asynchronous)
        assert [item["method"] for item in script.requests] == ["POST"]
    finally:
        await close_client(client, asynchronous)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_explicit_no_polling_keeps_caller_pipeline_retry_settings(asynchronous):
    script = Script(Reply({"detail": "unavailable"}, status=503), Reply({"result": RESULT}))
    # Mutation retries now require an explicitly caller-owned retry policy,
    # independently of choosing a custom or disabled polling strategy.
    retry_policy = (AsyncRetryPolicy if asynchronous else RetryPolicy)(retry_total=1)
    client = client_for(script, asynchronous, retry_total=1, retry_policy=retry_policy)
    try:
        poller = await begin(client, asynchronous, polling=False)
        assert (await result_of(poller, asynchronous)).as_dict() == RESULT
        assert [item["method"] for item in script.requests] == ["POST", "POST"]
    finally:
        await close_client(client, asynchronous)
