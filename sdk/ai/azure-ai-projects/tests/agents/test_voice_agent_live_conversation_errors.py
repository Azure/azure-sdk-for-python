# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline HTTP error coverage for Live conversation operations."""

import json
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict


def _operation(asynchronous, status, code):
    request = HttpRequest("GET", "https://example.test")
    payload = {"error": {"code": code, "message": "Offline test error."}}
    response = MagicMock()
    response.request = request
    response.status_code = status
    response.reason = "Not Found" if status == 404 else "Conflict"
    response.headers = case_insensitive_dict({"Content-Type": "application/json"})
    if code == "recording_not_ready":
        response.headers["Retry-After"] = "5"
    response.text.return_value = json.dumps(payload)
    response.json.return_value = payload
    response.content = json.dumps(payload).encode()
    response.read = (
        AsyncMock(return_value=response.content) if asynchronous else MagicMock(return_value=response.content)
    )

    pipeline_response = PipelineResponse(request, response, PipelineContext(None))
    client = MagicMock()
    client.format_url.side_effect = lambda url, **kwargs: url.format(**kwargs)
    client._pipeline.run = (
        AsyncMock(return_value=pipeline_response) if asynchronous else MagicMock(return_value=pipeline_response)
    )
    serializer = MagicMock()
    serializer.url.side_effect = lambda name, value, data_type, **kwargs: value
    config = SimpleNamespace(endpoint="https://example.test", api_version="v1")
    namespace = "azure.ai.projects.aio.operations" if asynchronous else "azure.ai.projects.operations"
    operation_type = getattr(import_module(namespace), "BetaVoiceAgentsLiveConversationsOperations")
    return operation_type(client, config, serializer, MagicMock()), client, response


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
@pytest.mark.parametrize(
    "method,item,suffix,status,code,error_type",
    [
        pytest.param("get", False, "", 404, "not_found", ResourceNotFoundError, id="get-missing"),
        pytest.param("get_item", True, "/items/item", 404, "not_found", ResourceNotFoundError, id="item-missing"),
        pytest.param("get_audio", False, "/audio", 404, "not_found", ResourceNotFoundError, id="audio-missing"),
        pytest.param(
            "get_audio_item",
            True,
            "/items/item/audio",
            404,
            "not_found",
            ResourceNotFoundError,
            id="item-audio-missing",
        ),
        pytest.param(
            "download_audio", False, "/audio/content", 404, "not_found", ResourceNotFoundError, id="download-missing"
        ),
        pytest.param(
            "download_audio_item",
            True,
            "/items/item/audio/content",
            404,
            "not_found",
            ResourceNotFoundError,
            id="item-download-missing",
        ),
        pytest.param(
            "get_audio", False, "/audio", 409, "recording_not_ready", ResourceExistsError, id="audio-not-ready"
        ),
        pytest.param(
            "get_audio", False, "/audio", 409, "recording_unavailable", ResourceExistsError, id="audio-unavailable"
        ),
        pytest.param(
            "download_audio",
            False,
            "/audio/content",
            409,
            "recording_not_ready",
            ResourceExistsError,
            id="download-not-ready",
        ),
        pytest.param(
            "download_audio",
            False,
            "/audio/content",
            409,
            "recording_unavailable",
            ResourceExistsError,
            id="download-unavailable",
        ),
        pytest.param(
            "download_audio_item",
            True,
            "/items/item/audio/content",
            409,
            "conflict",
            ResourceExistsError,
            id="item-download-conflict",
        ),
    ],
)
async def test_live_conversation_error_responses(asynchronous, method, item, suffix, status, code, error_type):
    operation, client, response = _operation(asynchronous, status, code)
    args = ("agent", "conversation", "item") if item else ("agent", "conversation")

    with pytest.raises(error_type) as error:
        result = getattr(operation, method)(*args)
        if asynchronous:
            result = await result
            if method.startswith("download"):
                async for _ in result:
                    pass
        elif method.startswith("download"):
            list(result)

    assert error.value.status_code == status
    assert error.value.error.code == code
    if code == "recording_not_ready":
        assert error.value.response.headers["Retry-After"] == "5"
    call = client._pipeline.run.call_args
    request = call.args[0]
    assert request.method == "GET"
    assert (
        urlsplit(request.url).path == f"/agents/agent/endpoint/protocols/voice/live/conversations/conversation{suffix}"
    )
    assert parse_qs(urlsplit(request.url).query) == {"api-version": ["v1"]}
    assert call.kwargs["stream"] is method.startswith("download")
    if method.startswith("download"):
        if asynchronous:
            response.read.assert_awaited_once()
        else:
            response.read.assert_called_once()
