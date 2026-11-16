# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for agent optimization pollers."""

import asyncio
import json
from pathlib import Path
import runpy
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.exceptions import HttpResponseError
from azure.core.pipeline import PipelineContext, PipelineResponse
from azure.core.rest import HttpRequest

from azure.ai.projects.models import AgentOptimizationLROPoller
from azure.ai.projects.aio.operations._patch_agents_async import AgentsOperations as AsyncAgentsOperations
from azure.ai.projects.operations._patch_agents import AgentsOperations


class _JobResponse:
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


class _SyncJobResponse(_JobResponse):
    def read(self):
        return self.content


class _AsyncJobResponse(_JobResponse):
    async def read(self):
        return self.content


def _job_response(status: str, *, initial: bool = False, is_async: bool = False) -> PipelineResponse:
    request = HttpRequest(
        "POST" if initial else "GET",
        "https://example.test/agent_optimization_jobs/optimization-job",
        headers={"x-ms-client-request-id": "request-test"},
    )
    payload: dict[str, Any] = {"id": "optimization-job", "status": status}
    headers = (
        {
            "operation-location": "https://example.test/agent_optimization_jobs/optimization-job?api-version=v1",
            "location": "https://example.test/agent_optimization_jobs/optimization-job?api-version=v1",
        }
        if initial
        else {}
    )
    response_type = _AsyncJobResponse if is_async else _SyncJobResponse
    response = response_type(request, 201 if initial else 200, headers, payload)
    return PipelineResponse(request, response, PipelineContext(None))


def _operation_for_cancellation(*, is_async: bool = False):
    operation_type = AsyncAgentsOperations if is_async else AgentsOperations
    operation = operation_type.__new__(operation_type)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access
    initial = _job_response("queued", initial=True, is_async=is_async)
    responses = [
        _job_response("in_progress", is_async=is_async),
        _job_response("cancelled", is_async=is_async),
    ]
    if is_async:
        operation._create_optimization_job_initial = AsyncMock(return_value=initial)  # pylint: disable=protected-access
        operation._client.send_request = AsyncMock(side_effect=responses)  # pylint: disable=protected-access
        operation._client._pipeline._transport.sleep = AsyncMock()  # pylint: disable=protected-access
    else:
        operation._create_optimization_job_initial = MagicMock(return_value=initial)  # pylint: disable=protected-access
        operation._client.send_request = MagicMock(side_effect=responses)  # pylint: disable=protected-access
    return operation


def test_begin_create_optimization_job_exposes_job_id():
    """The sync create operation exposes its job ID without SDK polling."""
    operation = AgentsOperations.__new__(AgentsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "optimization-job-sync"}
    operation._create_optimization_job_initial = MagicMock(
        return_value=initial_response
    )  # pylint: disable=protected-access

    poller = operation.begin_create_optimization_job(job={}, polling=False)

    assert isinstance(poller, AgentOptimizationLROPoller)
    assert poller.details["job_id"] == "optimization-job-sync"


def test_optimization_poller_stops_after_cancellation():
    operation = _operation_for_cancellation()

    poller = operation.begin_create_optimization_job(job={})

    with pytest.raises(HttpResponseError):
        poller.result(timeout=5)
    assert poller.done()
    assert poller.status() == "cancelled"
    assert operation._client.send_request.call_count == 2  # pylint: disable=protected-access


@pytest.mark.parametrize("is_async", [False, True])
def test_app_polling_sample_stops_after_skipped_job(is_async, monkeypatch):
    namespace = "azure.ai.projects.aio" if is_async else "azure.ai.projects"
    identity_namespace = "azure.identity.aio" if is_async else "azure.identity"
    client = AsyncMock() if is_async else MagicMock()
    credential = AsyncMock() if is_async else MagicMock()
    context_method = "__aenter__" if is_async else "__enter__"
    operations = getattr(client, context_method).return_value.agents
    operations.begin_create_optimization_job.return_value.details = {"job_id": "skipped-job"}
    operations.get_optimization_job.return_value = MagicMock(id="skipped-job", status="skipped", warnings=None)
    monkeypatch.setattr(f"{namespace}.AIProjectClient", MagicMock(return_value=client))
    monkeypatch.setattr(f"{identity_namespace}.DefaultAzureCredential", MagicMock(return_value=credential))
    monkeypatch.setattr("dotenv.load_dotenv", MagicMock())
    for name, value in {
        "FOUNDRY_PROJECT_ENDPOINT": "https://example.test",
        "FOUNDRY_AGENT_NAME": "test-agent",
        "EVALUATOR_NAME": "test-evaluator",
        "EVAL_MODEL": "test-model",
        "POLL_INTERVAL_SECONDS": "0",
    }.items():
        monkeypatch.setenv(name, value)
    suffix = "_async" if is_async else ""
    sample = Path(__file__).parents[2] / "samples" / "agents" / "optimization"
    sample /= f"sample_optimization_job_advanced_app_polling{suffix}.py"
    with pytest.raises(RuntimeError, match="was skipped"):
        runpy.run_path(str(sample), run_name="__main__")
    operations.get_optimization_job.assert_called_once_with(job_id="skipped-job")


@pytest.mark.asyncio
async def test_async_optimization_poller_stops_after_cancellation():
    operation = _operation_for_cancellation(is_async=True)

    poller = await operation.begin_create_optimization_job(job={})

    with pytest.raises(HttpResponseError):
        await asyncio.wait_for(poller.result(), timeout=5)
    assert poller.polling_method().finished()
    assert poller.status() == "cancelled"
    assert operation._client.send_request.call_count == 2  # pylint: disable=protected-access
