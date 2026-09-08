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
from azure.core.rest import HttpRequest, HttpResponse

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


def _run_response(status: str, *, initial: bool = False) -> PipelineResponse:
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
    response = MagicMock(spec=HttpResponse)
    response.request = request
    response.status_code = 202 if initial else 200
    response.headers = (
        {
            "operation-location": "https://example.test/operations/run-test",
            "location": "/runs/run-test",
        }
        if initial
        else {}
    )
    response.content = json.dumps(payload).encode()
    response.text.return_value = json.dumps(payload)
    response.json.return_value = payload
    return PipelineResponse(request, response, PipelineContext(None))


def _operation_for_status(terminal_status: str, *, is_async: bool = False):
    operation_type = AsyncBetaAgentInsightMonitorsOperations if is_async else BetaAgentInsightMonitorsOperations
    operation = operation_type.__new__(operation_type)
    operation._client = MagicMock()
    operation._config = MagicMock(polling_interval=0)
    operation._serialize = MagicMock()
    operation._serialize.url.return_value = "https://example.test"
    operation._deserialize = MagicMock()
    initial = _run_response("queued", initial=True)
    responses = [_run_response("in_progress"), _run_response(terminal_status)]
    if is_async:
        initial.http_response.read = AsyncMock()
        operation._create_run_initial = AsyncMock(return_value=initial)
        operation._client.send_request = AsyncMock(side_effect=responses)
        operation._client._pipeline._transport.sleep = AsyncMock()
    else:
        operation._create_run_initial = MagicMock(return_value=initial)
        operation._client.send_request = MagicMock(side_effect=responses)
    return operation


@pytest.mark.parametrize("terminal_status", ["succeeded", "failed", "cancelled", "canceled"])
def test_run_poller_stops_at_terminal_status(terminal_status: str) -> None:
    operation = _operation_for_status(terminal_status)
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
async def test_async_run_poller_stops_at_terminal_status(terminal_status: str) -> None:
    operation = _operation_for_status(terminal_status, is_async=True)
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
