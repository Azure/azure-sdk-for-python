# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Offline wire contracts for generated operations, independent of convenience polling."""

import json
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.transport import AsyncHttpResponse, AsyncHttpTransport

from azure.ai import finetuning_sessions as sdk
from azure.ai.finetuning_sessions import aio
from azure.ai.finetuning_sessions._utils.model_base import SdkJSONEncoder, _deserialize
from azure.ai.finetuning_sessions._version import VERSION
from azure.ai.finetuning_sessions.models import FoundryFeaturesOptInKeys, _models as raw
from azure.ai.finetuning_sessions.operations import _operations as builders
from conftest import FakeCredential, FakeTransport

_PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW
_ROOT = "/fine_tuning_sessions"
_SESSION = {"session_id": "session_test"}
_JSON = {"enabled": True, "nested": {"values": [1, 0.5, None, False]}}
_CREATE_BODY = {"type": "training", "base_model": "model_test", "lora_config": {"rank": 16}, "user_metadata": _JSON}
_CREATED = {**_CREATE_BODY, "session_id": "raw_id", "request_id": "request_test", "status": "queued"}
_POLL_CASES = [
    pytest.param({"status": "pending", "phase": None}, raw.PendingRequest, id="pending"),
    pytest.param({"status": "completed", "result": {"metrics": _JSON}}, raw.CompletedRequest, id="completed"),
    pytest.param(
        dict(
            status="failed",
            error="unavailable",
            should_retry=True,
            retry_after_sec=1.5,
            error_code="capacity",
            debug_ref="debug_test",
        ),
        raw.FailedRequest,
        id="failed",
    ),
]


def _json_value(value: Any) -> Any:
    return json.loads(json.dumps(value, cls=SdkJSONEncoder))


def _assert_request(request: Any, method: str, url: str, **query: Any) -> None:
    assert request.method == method
    assert request.url.partition("?")[0] == url
    assert "/fine_tuning/sessions" not in request.url
    assert parse_qs(urlsplit(request.url).query) == {"api-version": ["v1"], **{k: [str(v)] for k, v in query.items()}}
    assert request.headers["Foundry-Features"] == "FineTuningSessions=V1Preview"
    assert request.headers["Accept"] == "application/json"


def _assert_surface(module: Any, client: Any) -> None:
    assert type(client) is module.FineTuningSessionClient
    assert {name for name in module.__all__ if name.endswith("Client")} == {"FineTuningSessionClient"}
    assert not hasattr(module, "ProjectsClient")
    assert {name for name in vars(client) if not name.startswith("_")} == {
        "sessions",
        "training",
        "checkpoints",
        "sampling",
        "operations",
    }


def _assert_user_agent(request: Any) -> None:
    assert f"azsdk-python-ai-finetuningsessions/{VERSION}" in request.headers["User-Agent"]
    assert "ai-finetuning-sessions/" not in request.headers["User-Agent"]


def _assert_poll(result: Any, payload: dict, model: type) -> None:
    assert type(result) is model
    assert isinstance(result, raw.RequestStatus) and not isinstance(result, raw.OperationResult)
    assert result.status == payload["status"]
    assert result.as_dict() == payload
    for name, value in payload.items():
        assert getattr(result, name) == value  # Exercise typed fields, not just unknown mapping entries.


@pytest.mark.parametrize(
    "operation, method, suffix, identifiers",
    [
        ("sessions_create", "POST", "", {}),
        ("sessions_list", "GET", "", {}),
        ("sessions_get", "GET", "/session_test", _SESSION),
        ("sessions_delete", "DELETE", "/session_test", _SESSION),
        ("sessions_unload", "POST", "/session_test/complete", _SESSION),
        ("sessions_heartbeat", "POST", "/session_test/heartbeat", _SESSION),
        ("training_forward_backward", "POST", "/session_test/forward_backward", _SESSION),
        ("training_forward", "POST", "/session_test/forward", _SESSION),
        ("training_optimizer_step", "POST", "/session_test/optim_step", _SESSION),
        ("checkpoints_save", "POST", "/session_test/checkpoint", _SESSION),
        ("checkpoints_save_sampler_weights", "POST", "/session_test/checkpoint_sample", _SESSION),
        ("checkpoints_list", "GET", "/session_test/checkpoints", _SESSION),
        (
            "checkpoints_get",
            "GET",
            "/session_test/checkpoints/checkpoint_test",
            {**_SESSION, "checkpoint_id": "checkpoint_test"},
        ),
        ("sampling_sample", "POST", "/session_test/sample", {**_SESSION, "checkpoint_id": "checkpoint_test"}),
        (
            "operations_get",
            "GET",
            "/session_test/request/request_test",
            {**_SESSION, "request_id_parameter": "request_test"},
        ),
    ],
)
def test_all_generated_request_builders(operation: str, method: str, suffix: str, identifiers: dict) -> None:
    # Builders need only path/query identifiers and the preview opt-in, not body fields.
    request = getattr(builders, f"build_{operation}_request")(foundry_features=_PREVIEW, **identifiers)
    query = {"checkpoint_id": "checkpoint_test"} if operation == "sampling_sample" else {}
    _assert_request(request, method, _ROOT + suffix, **query)


@pytest.mark.parametrize("with_options", [False, True])
def test_sync_raw_create_200_without_operation_location(client, transport: FakeTransport, with_options: bool) -> None:
    _assert_surface(sdk, client)
    transport._response_body = json.dumps(_CREATED).encode()
    body = raw.CreateSessionRequest(
        type="training", base_model="model_test", lora_config=raw.LoRAConfig(rank=16), user_metadata=_JSON
    )
    expected = dict(_CREATE_BODY)
    if with_options:
        body.training_type = "DeveloperTier"
        body.from_checkpoint = raw.FromCheckpoint(source_session_id="session_source", checkpoint_id="checkpoint_test")
        expected["training_type"] = "DeveloperTier"
        expected["from_checkpoint"] = {"source_session_id": "session_source", "checkpoint_id": "checkpoint_test"}
    responses = []
    result = client.sessions.create(body, foundry_features=_PREVIEW, raw_response_hook=responses.append)
    assert type(result) is raw.CreateSessionResponse
    assert isinstance(result.session_id, str) and result.session_id == "raw_id"
    assert result.request_id == "request_test" and result.lora_config.rank == 16
    assert result.user_metadata["enabled"] is True and result.as_dict() == _CREATED
    assert responses[0].http_response.status_code == 200
    assert "operation-location" not in {key.lower() for key in responses[0].http_response.headers}
    [request] = transport.requests  # No automatic LRO polling or ID normalization.
    _assert_request(request, "POST", "https://fake" + _ROOT)
    _assert_user_agent(request)
    assert request.headers["Content-Type"] == "application/json"
    assert request.headers["Authorization"] == "Bearer fake_token" and "api-key" not in request.headers
    assert json.loads(request.content) == expected


@pytest.mark.parametrize("payload, model", _POLL_CASES)
def test_sync_poll_retains_raw_discriminator_and_failure_hints(
    client, transport: FakeTransport, payload, model
) -> None:
    transport._response_body = json.dumps(payload).encode()
    result = client.operations.get("session_test", "request_test", foundry_features=_PREVIEW)
    _assert_poll(result, payload, model)
    [request] = transport.requests
    _assert_request(request, "GET", "https://fake" + _ROOT + "/session_test/request/request_test")


def test_sync_lists_preserve_page_cursor_and_checkpoint_envelopes(client, transport: FakeTransport) -> None:
    timestamp = "2026-09-17T12:00:00Z"
    instant = datetime(2026, 9, 17, 12, tzinfo=timezone.utc)
    summary = {
        "session_id": "session_a",
        "base_model": "model_test",
        "status": "running",
        "is_lora": True,
        "lora_rank": 16,
        "corrupted": False,
        "last_request_time": timestamp,
    }
    payload = {
        "data": [summary, {**summary, "session_id": "session_b"}],
        "cursor": {"offset": 5, "limit": 2, "total_count": 9},
    }
    transport._response_body = json.dumps(payload).encode()
    page = client.sessions.list(offset=5, limit=2, foundry_features=_PREVIEW)
    assert type(page) is raw.SessionList and page.as_dict() == payload
    assert page.cursor.as_dict() == payload["cursor"]
    assert [item.session_id for item in page.data] == ["session_a", "session_b"]
    assert page.data[0].last_request_time == instant
    assert len(transport.requests) == 1  # The caller controls offsets; no opaque iterator.
    _assert_request(transport.requests[0], "GET", "https://fake" + _ROOT, offset=5, limit=2)

    payload = {
        "checkpoints": [
            {"checkpoint_id": "train", "checkpoint_type": "training", "time": timestamp},
            {"checkpoint_id": "sample", "checkpoint_type": "sampler", "time": timestamp},
        ]
    }
    transport._response_body = json.dumps(payload).encode()
    checkpoints = client.checkpoints.list("session_test", foundry_features=_PREVIEW)
    assert type(checkpoints) is raw.CheckpointList and checkpoints.as_dict() == payload
    assert [item.checkpoint_id for item in checkpoints.checkpoints] == ["train", "sample"]
    assert all(item.time == instant for item in checkpoints.checkpoints)
    assert len(transport.requests) == 2
    _assert_request(transport.requests[1], "GET", "https://fake" + _ROOT + "/session_test/checkpoints")


def test_raw_image_mixed_input_and_lora_flags_round_trip() -> None:
    image = raw.ImageChunk(data=b"\xff\xd8\xffjpeg", format="jpeg", expected_tokens=12)
    model_input = raw.ModelInput(chunks=[raw.ModelInputChunk(tokens=[1, 2]), image, raw.ModelInputChunk(tokens=[3])])
    wire = _json_value(model_input)
    assert wire == {
        "chunks": [
            {"tokens": [1, 2]},
            {"type": "image", "data": "/9j/anBlZw==", "format": "jpeg", "expected_tokens": 12},
            {"tokens": [3]},
        ]
    }
    assert _deserialize(raw.ImageChunk, wire["chunks"][1]).data == b"\xff\xd8\xffjpeg"
    assert _json_value(_deserialize(raw.ModelInput, wire)) == wire
    lora = raw.LoRAConfig(rank=16, freeze_vision_tower=False, freeze_multi_modal_projector=True)
    wire = _json_value(lora)
    assert wire == {"rank": 16, "freeze_vision_tower": False, "freeze_multi_modal_projector": True}
    restored = _deserialize(raw.LoRAConfig, wire)
    assert restored.freeze_vision_tower is False and restored.freeze_multi_modal_projector is True
    assert _json_value(restored) == wire


def test_generated_sample_output_preserves_nulls_and_numeric_types() -> None:
    payload = {
        "type": "sample",
        "operation_id": "request_test",
        "status": "succeeded",
        "sequences": [{"tokens": [42], "text": None, "logprobs": None}],
        "metrics": _JSON,
        "prompt_logprobs": [None, -0.5],
        "topk_prompt_logprobs": [None, [[42, -0.5], [43.0, -1.0]]],
    }
    result = _deserialize(raw.OperationResult, payload)
    assert type(result) is raw.SampleOperationResult
    assert result.prompt_logprobs == [None, -0.5] and result.topk_prompt_logprobs[0] is None
    pairs = result.topk_prompt_logprobs[1]  # unknown[][] must not coerce IDs or log-probabilities.
    assert pairs == [[42, -0.5], [43.0, -1.0]]
    assert type(pairs[0][0]) is int and type(pairs[1][0]) is float and type(pairs[0][1]) is float
    assert result.sequences[0].tokens == [42]
    assert result.sequences[0].text is None and result.sequences[0].logprobs is None
    assert result.metrics["enabled"] is True
    assert result.metrics == _JSON and _json_value(result) == payload


@pytest.mark.parametrize("total_loss", [None, 0.0, 0.75])
def test_generated_forward_output_optional_loss_and_json_metrics(total_loss: Any) -> None:
    payload = {
        "type": "forward_backward",
        "operation_id": "request_test",
        "status": "succeeded",
        "loss_fn_outputs": [{"logprobs": [None, -0.5]}],
        "metrics": _JSON,
    }
    if total_loss is not None:
        payload["total_loss"] = total_loss
    result = _deserialize(raw.OperationResult, payload)
    assert type(result) is raw.ForwardBackwardOperationResult
    assert result.total_loss == total_loss and ("total_loss" in result) == (total_loss is not None)
    assert result.loss_fn_outputs == payload["loss_fn_outputs"]
    assert result.metrics["enabled"] is True
    assert result.metrics == _JSON and _json_value(result) == payload


class _AsyncResponse(AsyncHttpResponse):
    """Buffered async response: JSON/text stay synchronous, lifecycle methods are async."""

    def __init__(self, request: Any, payload: dict) -> None:
        super().__init__(request, None)
        self.status_code, self.reason = 200, "OK"
        self.headers = {"content-type": "application/json"}
        self.content_type = "application/json"
        self._body = json.dumps(payload).encode()

    def body(self) -> bytes:
        return self._body

    def json(self) -> Any:
        return json.loads(self._body)

    async def read(self) -> bytes:
        return self._body

    async def close(self) -> None:
        pass


class _AsyncTransport(AsyncHttpTransport):
    def __init__(self, *payloads: dict) -> None:
        self.requests: list = []
        self._payloads = iter(payloads)

    async def send(self, request: Any, **kwargs: Any) -> _AsyncResponse:
        self.requests.append(request)
        return _AsyncResponse(request, next(self._payloads))

    async def open(self) -> None:
        pass

    async def close(self) -> None:
        pass

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def sleep(self, duration: float) -> None:
        pytest.fail("Raw operations must not sleep or retry these HTTP 200 responses")


class _AsyncCredential:
    async def get_token(self, *scopes: str, **kwargs: Any) -> Any:
        return FakeCredential().get_token(*scopes, **kwargs)


@pytest.mark.asyncio
@pytest.mark.parametrize("use_key", [False, True], ids=["token", "key"])
@pytest.mark.parametrize("payload, model", _POLL_CASES)
async def test_async_raw_create_and_poll_through_authenticated_pipeline(use_key, payload, model) -> None:
    transport = _AsyncTransport(_CREATED, payload)
    credential = AzureKeyCredential("offline-key") if use_key else _AsyncCredential()
    endpoint = "https://fake/api/projects/project_test"
    async with aio.FineTuningSessionClient(endpoint, credential, transport=transport, retry_total=0) as client:
        _assert_surface(aio, client)
        created = await client.sessions.create(raw.CreateSessionRequest(_CREATE_BODY), foundry_features=_PREVIEW)
        assert type(created) is raw.CreateSessionResponse and created.as_dict() == _CREATED
        assert created.session_id == "raw_id" and created.request_id == "request_test"
        assert len(transport.requests) == 1
        result = await client.operations.get(created.session_id, created.request_id, foundry_features=_PREVIEW)
        _assert_poll(result, payload, model)
    create_request, poll_request = transport.requests
    _assert_request(create_request, "POST", endpoint + _ROOT)
    assert create_request.headers["Content-Type"] == "application/json"
    assert json.loads(create_request.content) == _CREATE_BODY
    _assert_request(poll_request, "GET", endpoint + _ROOT + "/raw_id/request/request_test")
    for request in transport.requests:
        _assert_user_agent(request)
        if use_key:
            assert request.headers["api-key"] == "offline-key" and "Authorization" not in request.headers
        else:
            assert request.headers["Authorization"] == "Bearer fake_token" and "api-key" not in request.headers
