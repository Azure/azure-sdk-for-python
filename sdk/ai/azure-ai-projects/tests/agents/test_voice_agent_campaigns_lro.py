# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cspell:ignore Acancel
"""Deterministic sync/async tests for campaign LRO completion and resumption."""

import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from urllib.parse import parse_qs, urlsplit

import pytest
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.polling import AsyncLROPoller, AsyncPollingMethod, PollingMethod
from azure.core.rest import HttpRequest
from azure.core.utils import case_insensitive_dict

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.aio.operations import BetaVoiceAgentsCampaignsOperations as AsyncCampaignsOperations
from azure.ai.projects.models import TelephonyCampaign
from azure.ai.projects.operations import BetaVoiceAgentsCampaignsOperations as CampaignsOperations
from azure.ai.projects.operations._patch import _OperationMethodHeaderProxy
from azure.ai.projects._utils.campaign_polling import _configure_campaign_polling

pytestmark = pytest.mark.asyncio

_ENDPOINT = "https://example.test/api/projects/project"
_CAMPAIGN_PATH = "/api/projects/project/agents/voice-agent/telephony_campaigns/campaign"
_CAMPAIGN_URL = f"https://example.test{_CAMPAIGN_PATH}?api-version=v1&tag=one&tag=two"
_MONITOR_URL = "https://example.test/monitors/original-operation?api-version=v1"
_OPERATION_ID = "original-operation"
_METHODS = ("begin_create", "begin_cancel", "begin_delete")
_FEATURES = "VoiceAgents=V1Preview"


class _CampaignResponse:
    def __init__(self, request, status_code, headers, payload):
        self.request = request
        self.status_code = status_code
        self.headers = case_insensitive_dict(headers)
        self.content = json.dumps(payload).encode() if payload is not None else b""
        self.reason = "Test response"

    def text(self):
        return self.content.decode()

    def json(self):
        return json.loads(self.content)


class _SyncCampaignResponse(_CampaignResponse):
    def read(self):
        return self.content


class _AsyncCampaignResponse(_CampaignResponse):
    async def read(self):
        return self.content


def _campaign_payload():
    return {
        "name": "campaign",
        "connection_name": "connection",
        "source": {"type": "phone_number", "value": "+15555550100"},
        "status": "completed",
        "operation_id": "later-operation",
    }


def _response(asynchronous, method, url, status_code, payload, headers=None):
    request = HttpRequest(method, url, headers={"x-ms-client-request-id": "request-id"})
    response_type = _AsyncCampaignResponse if asynchronous else _SyncCampaignResponse
    response = response_type(request, status_code, headers or {}, payload)
    return PipelineResponse(request, response, PipelineContext(None))


def _operation(
    asynchronous,
    method,
    *,
    states=("in_progress", "succeeded"),
    operation_id=_OPERATION_ID,
    initial_status=None,
    final_status=200,
    initial_url=None,
):
    operation_type = AsyncCampaignsOperations if asynchronous else CampaignsOperations
    operation = operation_type.__new__(operation_type)
    operation._client = MagicMock()
    operation._config = SimpleNamespace(polling_interval=0, endpoint=_ENDPOINT)
    operation._serialize = MagicMock()
    operation._serialize.url.side_effect = lambda name, value, data_type, **kwargs: value
    operation._deserialize = MagicMock(side_effect=lambda data_type, value: value)
    operation._client.format_url.side_effect = lambda url, **kwargs: url.format(**kwargs)

    verb = {"begin_create": "PUT", "begin_cancel": "POST", "begin_delete": "DELETE"}[method]
    url = initial_url or _CAMPAIGN_URL
    if method == "begin_cancel":
        url = url.replace("?", ":cancel?", 1)
    headers = {"Operation-Location": _MONITOR_URL, "Retry-After": "0"}
    if operation_id is not None:
        headers["operation-id"] = operation_id
    payload = _campaign_payload() if method == "begin_create" else {"id": _OPERATION_ID, "status": "queued"}
    if initial_status in (200, 204):
        headers = {}
    if initial_status == 204:
        payload = None
    initial = _response(
        asynchronous,
        verb,
        url,
        initial_status or (201 if method == "begin_create" else 202),
        payload,
        headers,
    )
    initial_method = AsyncMock(return_value=initial) if asynchronous else MagicMock(return_value=initial)
    setattr(operation, f"_{method.removeprefix('begin_')}_initial", initial_method)
    responses = [
        _response(
            asynchronous,
            "GET",
            _MONITOR_URL,
            200,
            {"id": _OPERATION_ID, "status": state, "kind": method.removeprefix("begin_")},
        )
        for state in states
    ]
    if method != "begin_delete":
        payload = (
            _campaign_payload()
            if final_status == 200
            else {"error": {"code": "campaign_operation_mismatch", "message": "Campaign was replaced."}}
        )
        responses.append(_response(asynchronous, "GET", _CAMPAIGN_URL, final_status, payload))
    operation._client.send_request = (
        AsyncMock(side_effect=responses) if asynchronous else MagicMock(side_effect=responses)
    )
    if asynchronous:
        operation._client._pipeline._transport.sleep = AsyncMock()
    return _OperationMethodHeaderProxy(operation, _FEATURES), operation, initial, initial_method


async def _begin(operation, method, **kwargs):
    arguments = {"agent_name": "voice-agent", "campaign_name": "campaign"}
    if method == "begin_create":
        arguments["campaign"] = {}
    else:
        arguments.update(etag='"etag"', match_condition=MatchConditions.IfNotModified)
    arguments.update(kwargs)
    result = getattr(operation, method)(**arguments)
    return await result if inspect.isawaitable(result) else result


async def _result(poller):
    if isinstance(poller, AsyncLROPoller):
        return await asyncio.wait_for(poller.result(), timeout=5)
    return poller.result(timeout=5)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", _METHODS)
async def test_campaign_lro_completion(asynchronous, method):
    operation, raw, _, initial_method = _operation(asynchronous, method)

    poller = await _begin(operation, method)
    result = await _result(poller)

    calls = raw._client.send_request.call_args_list
    assert initial_method.call_args.kwargs["headers"]["Foundry-Features"] == _FEATURES
    assert [call.args[0].url for call in calls[:2]] == [_MONITOR_URL, _MONITOR_URL]
    assert all(call.args[0].method == "GET" for call in calls)
    assert all(call.kwargs["headers"]["Foundry-Features"] == _FEATURES for call in calls)
    if method == "begin_delete":
        assert result is None
        assert len(calls) == 2
    else:
        assert isinstance(result, TelephonyCampaign)
        assert result.name == "campaign"
        assert result.operation_id == "later-operation"
        assert len(calls) == 3
        final_url = urlsplit(calls[-1].args[0].url)
        assert final_url.path == _CAMPAIGN_PATH
        assert parse_qs(final_url.query) == {
            "api-version": ["v1"],
            "tag": ["one", "two"],
            "operation_id": [_OPERATION_ID],
        }


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", _METHODS)
@pytest.mark.parametrize("status", ["cancelled", "Cancelled", "canceled", "failed"])
async def test_campaign_lro_terminal_failure(asynchronous, method, status):
    operation, raw, _, _ = _operation(asynchronous, method, states=(status,))

    poller = await _begin(operation, method)

    with pytest.raises(HttpResponseError):
        await _result(poller)
    assert poller.polling_method().finished()
    assert raw._client.send_request.call_count == 1
    assert poller.status().lower() == ("canceled" if status.lower() == "cancelled" else status)


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", ("begin_create", "begin_cancel"))
async def test_campaign_lro_requires_original_operation_id(asynchronous, method):
    operation, raw, _, _ = _operation(asynchronous, method, states=("succeeded",), operation_id=None)

    poller = await _begin(operation, method)

    with pytest.raises(HttpResponseError, match="Operation-Id"):
        await _result(poller)
    assert raw._client.send_request.call_count == 1


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", ("begin_create", "begin_cancel"))
@pytest.mark.parametrize("status", [404, 409])
async def test_campaign_lro_surfaces_final_get_errors(asynchronous, method, status):
    operation, raw, _, _ = _operation(asynchronous, method, states=("succeeded",), final_status=status)

    poller = await _begin(operation, method)

    with pytest.raises(HttpResponseError) as error:
        await _result(poller)
    assert error.value.status_code == status
    assert raw._client.send_request.call_count == 2


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", _METHODS)
async def test_campaign_lro_polling_can_be_disabled(asynchronous, method):
    operation, raw, _, _ = _operation(asynchronous, method)

    poller = await _begin(operation, method, polling=False)

    assert poller.polling_method().finished()
    raw._client.send_request.assert_not_called()
    assert poller.polling_method().__class__.__name__ == ("AsyncNoPolling" if asynchronous else "NoPolling")


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", _METHODS)
async def test_campaign_lro_preserves_custom_polling(asynchronous, method):
    operation, raw, _, _ = _operation(asynchronous, method)
    polling = MagicMock(spec=AsyncPollingMethod if asynchronous else PollingMethod)
    polling.finished.return_value = True
    polling.resource = MagicMock(return_value="custom-result")

    poller = await _begin(operation, method, polling=polling)

    assert poller.polling_method() is polling
    assert await _result(poller) == "custom-result"
    raw._client.send_request.assert_not_called()


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", _METHODS)
async def test_campaign_lro_preserves_request_options_and_callback(asynchronous, method):
    operation, raw, _, initial_method = _operation(asynchronous, method)
    callback = MagicMock(return_value="callback-result")

    poller = await _begin(
        operation,
        method,
        cls=callback,
        polling_interval=7,
        connection_timeout=11,
        headers={"X-Test": "custom"},
    )

    assert await _result(poller) == "callback-result"
    assert poller.polling_method()._timeout == 7
    assert initial_method.call_args.kwargs["connection_timeout"] == 11
    assert initial_method.call_args.kwargs["headers"]["X-Test"] == "custom"
    for call in raw._client.send_request.call_args_list:
        assert call.kwargs["connection_timeout"] == 11
        assert call.kwargs["headers"]["X-Test"] == "custom"
        assert call.kwargs["headers"]["Foundry-Features"] == _FEATURES
        assert "cls" not in call.kwargs
    callback.assert_called_once()
    assert (
        callback.call_args.args[1] is None
        if method == "begin_delete"
        else isinstance(callback.call_args.args[1], TelephonyCampaign)
    )


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method", _METHODS)
async def test_campaign_lro_resumes_original_operation(asynchronous, method):
    operation, raw, initial, initial_method = _operation(asynchronous, method)
    options = {}
    _configure_campaign_polling(options, 0, {"endpoint": _ENDPOINT}, is_async=asynchronous)
    polling = options["polling"]
    polling.initialize(raw._client, initial, lambda response: None)
    token = polling.get_continuation_token()

    poller = await _begin(
        operation,
        method,
        agent_name="different-agent",
        campaign_name="different-campaign",
        continuation_token=token,
    )
    result = await _result(poller)

    initial_method.assert_not_called()
    calls = raw._client.send_request.call_args_list
    assert calls[0].args[0].url == _MONITOR_URL
    if method == "begin_delete":
        assert result is None
        assert len(calls) == 2
    else:
        assert isinstance(result, TelephonyCampaign)
        final_url = urlsplit(calls[-1].args[0].url)
        assert final_url.path == _CAMPAIGN_PATH
        assert parse_qs(final_url.query)["operation_id"] == [_OPERATION_ID]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("method,status", [("begin_create", 200), ("begin_delete", 204)])
async def test_campaign_lro_immediate_completion(asynchronous, method, status):
    operation, raw, _, _ = _operation(asynchronous, method, initial_status=status)

    poller = await _begin(operation, method)
    result = await _result(poller)

    raw._client.send_request.assert_not_called()
    assert result is None if method == "begin_delete" else isinstance(result, TelephonyCampaign)


@pytest.mark.parametrize("asynchronous", [False, True])
async def test_campaign_lro_keeps_encoded_names_and_overrides_stale_guard(asynchronous):
    url = f"https://example.test{_CAMPAIGN_PATH}%3Acancel?api-version=v1&operation_id=stale"
    operation, raw, _, _ = _operation(asynchronous, "begin_cancel", initial_url=url)

    poller = await _begin(operation, "begin_cancel")
    await _result(poller)

    final_url = urlsplit(raw._client.send_request.call_args_list[-1].args[0].url)
    assert final_url.path == f"{_CAMPAIGN_PATH}%3Acancel"
    assert parse_qs(final_url.query)["operation_id"] == [_OPERATION_ID]


@pytest.mark.parametrize("asynchronous", [False, True])
@pytest.mark.parametrize("allow_preview", [False, True])
async def test_campaign_operations_are_wired_to_public_clients(asynchronous, allow_preview):
    client_type = AsyncAIProjectClient if asynchronous else AIProjectClient
    client = client_type(endpoint=_ENDPOINT, credential=MagicMock(), allow_preview=allow_preview)
    try:
        campaigns = client.beta.voice_agents.campaigns._operation
        assert isinstance(campaigns, AsyncCampaignsOperations if asynchronous else CampaignsOperations)
    finally:
        result = client.close()
        if inspect.isawaitable(result):
            await result
