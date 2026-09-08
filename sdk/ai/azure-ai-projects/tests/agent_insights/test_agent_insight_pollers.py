# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unit tests for Agent Insights run poller configuration and terminal states."""

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.rest import HttpRequest

from azure.ai.projects.aio.operations._patch_agent_insights_async import (
    BetaAgentInsightMonitorsOperations as AsyncBetaAgentInsightMonitorsOperations,
)
from azure.ai.projects.operations._patch_agent_insights import (
    BetaAgentInsightMonitorsOperations,
)


def test_begin_create_run_uses_operation_location_as_final_state() -> None:
    """The sync poller returns the completed operation response without a final Location GET."""
    operation = BetaAgentInsightMonitorsOperations.__new__(BetaAgentInsightMonitorsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "run-sync"}
    operation._create_run_initial = MagicMock(return_value=initial_response)  # pylint: disable=protected-access

    polling_method = MagicMock()
    polling_method.finished.return_value = True
    with patch(
        "azure.ai.projects.operations._patch_agent_insights._AgentInsightPolling",
        return_value=polling_method,
    ) as polling_type:
        poller = operation.begin_create_run("monitor-sync", run={})

    assert poller.details["run_id"] == "run-sync"
    assert polling_type.call_args.kwargs["lro_options"] == {"final-state-via": "operation-location"}


@pytest.mark.asyncio
async def test_begin_create_run_uses_operation_location_as_final_state_async() -> None:
    """The async poller returns the operation response without a final Location GET."""
    operation = AsyncBetaAgentInsightMonitorsOperations.__new__(AsyncBetaAgentInsightMonitorsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "run-async"}
    initial_response.http_response.read = AsyncMock()
    operation._create_run_initial = AsyncMock(return_value=initial_response)  # pylint: disable=protected-access

    polling_method = MagicMock()
    with patch(
        "azure.ai.projects.aio.operations._patch_agent_insights_async._AsyncAgentInsightPolling",
        return_value=polling_method,
    ) as polling_type:
        poller = await operation.begin_create_run("monitor-async", run={})

    assert poller.details["run_id"] == "run-async"
    assert polling_type.call_args.kwargs["lro_options"] == {"final-state-via": "operation-location"}


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
            "location": "/runs/run-test",
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
    if is_async:
        operation._create_run_initial = AsyncMock(return_value=initial)
        operation._client.send_request = AsyncMock(side_effect=responses)
        operation._client._pipeline._transport.sleep = AsyncMock()
    else:
        operation._create_run_initial = MagicMock(return_value=initial)
        operation._client.send_request = MagicMock(side_effect=responses)
    return operation


@pytest.mark.parametrize("terminal_status", ["succeeded", "failed", "cancelled", "canceled"])
@pytest.mark.parametrize("initial_status_code", [201, 202])
def test_run_poller_stops_at_terminal_status(terminal_status: str, initial_status_code: int) -> None:
    operation = _operation_for_status(terminal_status, initial_status_code=initial_status_code)
    poller = operation.begin_create_run("monitor-test", run={})
    if terminal_status == "succeeded":
        assert poller.result(timeout=5).traces_analyzed == 10
    else:
        with pytest.raises(HttpResponseError):
            poller.result(timeout=5)
    assert poller.done()
    assert poller.status() == ("cancelled" if terminal_status == "canceled" else terminal_status)
    assert operation._client.send_request.call_count == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal_status", ["succeeded", "failed", "cancelled", "canceled"])
@pytest.mark.parametrize("initial_status_code", [201, 202])
async def test_async_run_poller_stops_at_terminal_status(terminal_status: str, initial_status_code: int) -> None:
    operation = _operation_for_status(terminal_status, is_async=True, initial_status_code=initial_status_code)
    poller = await operation.begin_create_run("monitor-test", run={})
    if terminal_status == "succeeded":
        result = await asyncio.wait_for(poller.result(), timeout=5)
        assert result.traces_analyzed == 10
    else:
        with pytest.raises(HttpResponseError):
            await asyncio.wait_for(poller.result(), timeout=5)
    assert poller.polling_method().finished()
    assert poller.status() == ("cancelled" if terminal_status == "canceled" else terminal_status)
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
    assert poller.details == {"run_id": "run-test"}
    assert result.traces_analyzed == 10
    assert operation._client.send_request.call_count == 2
