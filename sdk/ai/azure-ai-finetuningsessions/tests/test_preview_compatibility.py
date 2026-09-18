# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Compatibility of the regenerated SDK with existing preview callers."""

import asyncio
import json
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline import PipelineContext, PipelineRequest
from azure.core.rest import HttpRequest

from azure.ai.finetuningsessions import FineTuningSession, FineTuningSessionClient, aio
from azure.ai.finetuningsessions.models import FoundryFeaturesOptInKeys
from azure.ai.finetuningsessions.models import _models as raw
from test_generated_contract import _AsyncTransport, _CREATE_BODY, _CREATED

PREVIEW = FoundryFeaturesOptInKeys.FINETUNING_SESSIONS_V1_PREVIEW


def test_sync_create_accepts_legacy_body_keyword(client, transport):
    transport._response_body = json.dumps(_CREATED).encode()
    result = client.sessions.create(body=_CREATE_BODY, foundry_features=PREVIEW, api_version="v1")
    assert result.session_id == _CREATED["session_id"]
    assert json.loads(transport.requests[0].content) == _CREATE_BODY


def test_sync_per_call_api_version_is_not_shared_or_forwarded(client, transport, monkeypatch):
    original_send = transport.send

    def strict_send(request, **kwargs):
        assert "api_version" not in kwargs
        return original_send(request, **kwargs)

    monkeypatch.setattr(transport, "send", strict_send)
    transport._response_body = b'{"session_id":"session_test"}'
    client.sessions.heartbeat("session_test", foundry_features=PREVIEW, api_version="override")
    client.sessions.heartbeat("session_test", foundry_features=PREVIEW)
    assert [parse_qs(urlsplit(request.url).query)["api-version"] for request in transport.requests] == [
        ["override"],
        ["v1"],
    ]
    assert client._config.api_version == "v1"


def test_sync_poll_accepts_legacy_operation_id_keyword(client, transport):
    transport._response_body = b'{"status":"completed","result":{}}'
    result = client.operations.get(
        session_id="session_test", operation_id="request_test", foundry_features=PREVIEW, api_version="v1"
    )
    assert isinstance(result, raw.CompletedRequest)
    assert "/session_test/request/request_test?" in transport.requests[0].url


def test_conflicting_body_keywords_fail_before_send(client, transport):
    with pytest.raises(TypeError, match="either 'body' or 'session'"):
        client.sessions.create(session=_CREATE_BODY, body=_CREATE_BODY, foundry_features=PREVIEW)
    assert not transport.requests


@pytest.mark.asyncio
async def test_async_legacy_keywords_preserve_concurrent_api_versions():
    class StrictTransport(_AsyncTransport):
        async def send(self, request, **kwargs):
            assert "api_version" not in kwargs
            await asyncio.sleep(0)
            return await super().send(request, **kwargs)

    transport = StrictTransport(_CREATED, {"status": "completed", "result": {}}, {}, {}, {})
    async with aio.FineTuningSessionClient("https://fake", AzureKeyCredential("key"), transport=transport) as client:
        created = await client.sessions.create(body=_CREATE_BODY, foundry_features=PREVIEW, api_version="v1")
        result = await client.operations.get(
            session_id=created.session_id, operation_id="request_test", foundry_features=PREVIEW, api_version="v1"
        )
        assert isinstance(result, raw.CompletedRequest)
        await asyncio.gather(
            client.sessions.heartbeat("session_test", foundry_features=PREVIEW, api_version="first"),
            client.sessions.heartbeat("session_test", foundry_features=PREVIEW, api_version="second"),
        )
        await client.sessions.heartbeat("session_test", foundry_features=PREVIEW)
        assert client._config.api_version == "v1"
    assert [parse_qs(urlsplit(r.url).query)["api-version"] for r in transport.requests[-3:]] == [
        ["first"],
        ["second"],
        ["v1"],
    ]


@pytest.mark.parametrize("asynchronous", [False, True])
def test_omitted_lora_configuration_stays_omitted(monkeypatch, asynchronous):
    from test_create_session_id_normalization import _AsyncRecordingClient, _RecordingClient
    from azure.ai.finetuningsessions.aio import _patch as async_patch

    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda self: None)
    monkeypatch.setattr(async_patch, "_start_heartbeat", lambda *args, **kwargs: None)
    if asynchronous:
        client = _AsyncRecordingClient("session_test")
        asyncio.run(async_patch.create_session(client, base_model="model_test"))
    else:
        client = _RecordingClient("session_test")
        FineTuningSession.create(client, base_model="model_test")
    assert "lora_config" not in json.loads(client.requests[0].content)


def test_error_models_remain_importable():
    from azure.ai.finetuningsessions.models import ApiError, ApiErrorResponse

    error = ApiError(code="invalid_request", message="Invalid input", additional_info={"field": "data"})
    response = ApiErrorResponse(error=error)
    assert response.error.code == "invalid_request"
    assert response.as_dict()["error"]["additionalInfo"] == {"field": "data"}


@pytest.mark.parametrize("legacy", [False, True])
def test_sync_route_selection_applies_to_generated_and_convenience_requests(legacy, monkeypatch):
    from test_legacy_polling import _SequenceTransport

    monkeypatch.setattr(FineTuningSession, "_start_heartbeat", lambda self: None)
    transport = _SequenceTransport(_CREATED, {"status": "completed", "result": {}}, {"session_id": "session_test"}, {})
    endpoint = "https://fake/api/projects/project_test"
    with FineTuningSessionClient(
        endpoint, AzureKeyCredential("key"), transport=transport, use_legacy_routes=legacy
    ) as client:
        session = FineTuningSession.create(client, base_model="model_test")
        session.heartbeat()
        session.close()
    prefix = "/fine_tuning/sessions" if legacy else "/fine_tuning_sessions"
    assert [request.method for request in transport.requests] == ["POST", "GET", "POST", "POST"]
    assert all(request.url.startswith(endpoint + prefix) for request in transport.requests)
    assert all("use_legacy_routes" not in options for options in transport.options)
    assert all(request.headers["api-key"] == "key" for request in transport.requests)


@pytest.mark.asyncio
@pytest.mark.parametrize("legacy", [False, True])
async def test_async_route_selection_applies_to_convenience_and_begin_polling(legacy, monkeypatch):
    from test_legacy_polling import _AsyncSequenceTransport
    from azure.ai.finetuningsessions.aio import _patch as async_patch

    monkeypatch.setattr(async_patch, "_start_heartbeat", lambda *args, **kwargs: None)
    transport = _AsyncSequenceTransport(
        _CREATED, {"status": "completed", "result": {}},
        {"request_id": "request_unload", "session_id": "raw_id"}, {"status": "completed", "result": {}},
    )
    endpoint = "https://fake/api/projects/project_test"
    async with aio.FineTuningSessionClient(
        endpoint, AzureKeyCredential("key"), transport=transport, use_legacy_routes=legacy
    ) as client:
        await client.create_session(base_model="model_test")
        poller = await client.sessions.begin_unload("raw_id", api_version="v1", polling_interval=0)
        assert (await poller.result()).operation_id == "request_unload"
    prefix = "/fine_tuning/sessions" if legacy else "/fine_tuning_sessions"
    assert [request.method for request in transport.requests] == ["POST", "GET", "POST", "GET"]
    assert all(request.url.startswith(endpoint + prefix) for request in transport.requests)
    assert all("use_legacy_routes" not in options for options in transport.options)


@pytest.mark.parametrize(
    "url",
    [
        "https://other.example/api/projects/p/fine_tuning_sessions/id",
        "https://fake/api/projects/other/fine_tuning_sessions/id",
        "https://fake/api/projects/p/fine_tuning_sessions_extra/id",
        "https://fake/api/projects/p/sessions?next=/fine_tuning_sessions/id",
        "https://fake/api/projects/p/fine_tuning/sessions/id",
    ],
)
def test_legacy_route_policy_does_not_rewrite_unrelated_requests(url):
    from azure.ai.finetuningsessions._client_options import _LegacySessionRoutePolicy

    policy = _LegacySessionRoutePolicy("https://fake/api/projects/p")
    request = PipelineRequest(HttpRequest("GET", url), PipelineContext(None))
    policy.on_request(request)
    assert request.http_request.url == url
