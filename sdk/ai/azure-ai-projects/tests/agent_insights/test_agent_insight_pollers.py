# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unit tests for Agent Insights run poller configuration and terminal states."""

import asyncio
import io
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import requests
from urllib3.response import HTTPResponse
from azure.core.credentials import AccessToken
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.pipeline.transport import AioHttpTransport, RequestsTransport
from azure.core.rest import HttpRequest

from azure.ai.projects import AIProjectClient
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient
from azure.ai.projects.aio.operations._patch_agent_insights_async import (
    BetaAgentInsightMonitorsOperations as AsyncBetaAgentInsightMonitorsOperations,
)
from azure.ai.projects.operations._patch_agent_insights import (
    BetaAgentInsightMonitorsOperations,
)


class _RunResponse:
    """A buffered, picklable response for both supported Core token formats."""

    def __init__(self, request, status_code, headers, payload):
        self.request = request
        self.status_code = status_code
        self.headers = headers
        self.content = json.dumps(payload).encode()
        self.reason = "Test response"

    def text(self):
        return self.content.decode()

    def json(self):
        return json.loads(self.content)


class _SyncRunResponse(_RunResponse):
    def read(self):
        return self.content


class _AsyncRunResponse(_RunResponse):
    async def read(self):
        return self.content


def _run_response(
    status: str, *, initial: bool = False, initial_status_code: int = 201, is_async: bool = False
) -> PipelineResponse:
    request = HttpRequest(
        "POST" if initial else "GET",
        "https://example.test/runs/run-test",
        headers={"x-ms-client-request-id": "request-test"},
    )
    payload: dict[str, Any] = {"id": "run-test", "status": status}
    if status == "succeeded":
        payload["result"] = {
            "traces_in_window": 10,
            "traces_analyzed": 10,
            "insights_created": 1,
            "insights_updated": 0,
            "insights_reopened": 0,
            "token_usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
        }
    headers = (
        {
            "operation-location": "https://example.test/operations/run-test",
            "location": "https://example.test/runs/run-test",
        }
        if initial
        else {}
    )
    response_type = _AsyncRunResponse if is_async else _SyncRunResponse
    response = response_type(request, initial_status_code if initial else 200, headers, payload)
    return PipelineResponse(request, response, PipelineContext(None))


def _operation_for_status(terminal_status: str, *, is_async: bool = False, initial_status_code: int = 201):
    operation_type = AsyncBetaAgentInsightMonitorsOperations if is_async else BetaAgentInsightMonitorsOperations
    operation = operation_type.__new__(operation_type)
    operation._client = MagicMock()
    operation._config = MagicMock(polling_interval=0)
    operation._serialize = MagicMock()
    operation._serialize.url.return_value = "https://example.test"
    operation._deserialize = MagicMock()
    initial = _run_response("queued", initial=True, initial_status_code=initial_status_code, is_async=is_async)
    responses = [_run_response("in_progress"), _run_response(terminal_status)]
    if terminal_status == "succeeded":
        responses.append(_run_response("succeeded"))
    if is_async:
        operation._create_run_initial = AsyncMock(return_value=initial)
        operation._client.send_request = AsyncMock(side_effect=responses)
        operation._client._pipeline._transport.sleep = AsyncMock()
    else:
        operation._create_run_initial = MagicMock(return_value=initial)
        operation._client.send_request = MagicMock(side_effect=responses)
    return operation


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("custom_headers", [False, True])
async def test_run_poller_sends_headers_on_every_request(is_async: bool, custom_headers: bool) -> None:
    headers = {"foundry-features": "custom-preview", "x-custom-header": "custom-value"} if custom_headers else {}
    original_headers = headers.copy()
    responses = []
    for index, status in enumerate(["queued", "in_progress", "succeeded", "succeeded"]):
        response = _run_response(status, initial=index == 0).http_response
        response.headers["content-type"] = "application/json"
        response.headers["location"] = "https://example.test/runs/run-test"
        if is_async:
            raw_response = MagicMock(status=response.status_code, headers=response.headers, reason="OK")
            raw_response.read = AsyncMock(return_value=response.content)
        else:
            raw_response = requests.Response()
            raw_response.status_code = response.status_code
            raw_response.headers.update(response.headers)
            raw_response.raw = HTTPResponse(body=io.BytesIO(response.content), preload_content=False)
            raw_response._content = response.content
            raw_response._content_consumed = True
        responses.append(raw_response)

    session = MagicMock()
    credential = MagicMock(spec=["get_token"])
    token = AccessToken("test-token", 4102444800)
    if is_async:
        session.request = AsyncMock(side_effect=responses)
        credential.get_token = AsyncMock(return_value=token)
        async with AsyncAIProjectClient(
            endpoint="https://example.test",
            credential=credential,
            transport=AioHttpTransport(session=session, session_owner=False),
        ) as client:
            poller = await client.beta.agent_insight_monitors.begin_create_run(
                "monitor-test", run={}, polling_interval=0, headers=headers
            )
            result = await asyncio.wait_for(poller.result(), timeout=5)
    else:
        session.request.side_effect = responses
        credential.get_token.return_value = token
        with AIProjectClient(
            endpoint="https://example.test", credential=credential, transport=RequestsTransport(session=session)
        ) as client:
            poller = client.beta.agent_insight_monitors.begin_create_run(
                "monitor-test", run={}, polling_interval=0, headers=headers
            )
            result = poller.result(timeout=5)

    assert result.traces_analyzed == 10
    calls = session.request.call_args_list
    assert [call.args[0] if call.args else call.kwargs["method"] for call in calls] == ["POST", "GET", "GET", "GET"]
    final_url = calls[-1].args[1] if len(calls[-1].args) > 1 else calls[-1].kwargs["url"]
    assert final_url == "https://example.test/runs/run-test"
    for call in calls:
        sent_headers = {key.lower(): value for key, value in call.kwargs["headers"].items()}
        assert sent_headers["foundry-features"] == ("custom-preview" if custom_headers else "AgentInsights=V1Preview")
        if custom_headers:
            assert sent_headers["x-custom-header"] == "custom-value"
    if custom_headers:
        assert headers == original_headers


@pytest.mark.parametrize("initial_status_code", [201, 202])
def test_run_poller_stops_after_cancellation(initial_status_code: int) -> None:
    operation = _operation_for_status("cancelled", initial_status_code=initial_status_code)
    poller = operation.begin_create_run("monitor-test", run={})
    with pytest.raises(HttpResponseError):
        poller.result(timeout=5)
    assert poller.done()
    assert poller.status() == "cancelled"
    assert operation._client.send_request.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("initial_status_code", [201, 202])
async def test_async_run_poller_stops_after_cancellation(initial_status_code: int) -> None:
    operation = _operation_for_status("cancelled", is_async=True, initial_status_code=initial_status_code)
    poller = await operation.begin_create_run("monitor-test", run={})
    with pytest.raises(HttpResponseError):
        await asyncio.wait_for(poller.result(), timeout=5)
    assert poller.polling_method().finished()
    assert poller.status() == "cancelled"
    assert operation._client.send_request.call_count == 2


@pytest.mark.parametrize("is_async", [False, True])
def test_begin_create_run_preserves_custom_polling_method(is_async):
    operation = _operation_for_status("succeeded", is_async=is_async)
    polling_method = MagicMock()
    polling_method.finished.return_value = True
    if is_async:
        poller = asyncio.run(operation.begin_create_run("monitor-test", run={}, polling=polling_method))
    else:
        poller = operation.begin_create_run("monitor-test", run={}, polling=polling_method)
    assert poller.polling_method() is polling_method
    polling_method.initialize.assert_called_once()
    operation._client.send_request.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
async def test_begin_create_run_resumes_without_creating_another_run(is_async):
    original_operation = _operation_for_status("succeeded", is_async=is_async)
    if is_async:
        original = await original_operation.begin_create_run("monitor-test", run={})
        await asyncio.wait_for(original.result(), timeout=5)
    else:
        original = original_operation.begin_create_run("monitor-test", run={})
        original.result(timeout=5)

    operation = _operation_for_status("succeeded", is_async=is_async)
    kwargs = {"run": {}, "continuation_token": original.continuation_token()}
    if is_async:
        poller = await operation.begin_create_run("monitor-test", **kwargs)
        result = await asyncio.wait_for(poller.result(), timeout=5)
    else:
        poller = operation.begin_create_run("monitor-test", **kwargs)
        result = poller.result(timeout=5)
    operation._create_run_initial.assert_not_called()
    assert result.traces_analyzed == 10
    assert operation._client.send_request.call_count == 3
