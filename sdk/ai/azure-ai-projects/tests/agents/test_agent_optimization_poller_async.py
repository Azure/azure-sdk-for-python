# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for async agent optimization pollers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.projects.aio.operations._patch_agents_async import BetaAgentsOperations
from azure.ai.projects.models import AsyncAgentOptimizationLROPoller


@pytest.mark.asyncio
async def test_begin_create_optimization_job_exposes_job_id_async():
    """The async create operation exposes its job ID without SDK polling."""
    operation = BetaAgentsOperations.__new__(BetaAgentsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "optimization-job-async"}
    initial_response.http_response.read = AsyncMock()
    operation._create_optimization_job_initial = AsyncMock(
        return_value=initial_response
    )  # pylint: disable=protected-access

    poller = await operation.begin_create_optimization_job(job={}, polling=False)

    assert isinstance(poller, AsyncAgentOptimizationLROPoller)
    assert poller.details["job_id"] == "optimization-job-async"
