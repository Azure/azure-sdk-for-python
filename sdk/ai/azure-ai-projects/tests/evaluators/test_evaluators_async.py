# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for async evaluator generation pollers."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.ai.projects.aio.operations._patch_evaluators_async import BetaEvaluatorsOperations
from azure.ai.projects.models import AsyncEvaluatorGenerationLROPoller


@pytest.mark.asyncio
async def test_begin_create_generation_job_exposes_job_id_async():
    """The async create operation exposes its job ID without SDK polling."""
    operation = BetaEvaluatorsOperations.__new__(BetaEvaluatorsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(polling_interval=0)  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = "https://example.test"  # pylint: disable=protected-access
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "evaluator-job-async"}
    initial_response.http_response.read = AsyncMock()
    operation._create_generation_job_initial = AsyncMock(  # pylint: disable=protected-access
        return_value=initial_response
    )

    poller = await operation.begin_create_generation_job(job={}, polling=False)

    assert isinstance(poller, AsyncEvaluatorGenerationLROPoller)
    assert poller.details["job_id"] == "evaluator-job-async"
