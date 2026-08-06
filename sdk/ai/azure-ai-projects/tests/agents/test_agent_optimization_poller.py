# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for sync agent optimization pollers."""

from unittest.mock import MagicMock

from azure.ai.projects.models import AgentOptimizationLROPoller
from azure.ai.projects.operations._patch_agents import BetaAgentsOperations


def test_begin_create_optimization_job_exposes_job_id():
    """The sync create operation exposes its job ID without SDK polling."""
    operation = BetaAgentsOperations.__new__(BetaAgentsOperations)
    operation._client = MagicMock()  # pylint: disable=protected-access
    operation._config = MagicMock(
        polling_interval=0
    )  # pylint: disable=protected-access
    operation._serialize = MagicMock()  # pylint: disable=protected-access
    operation._serialize.url.return_value = (
        "https://example.test"  # pylint: disable=protected-access
    )
    operation._deserialize = MagicMock()  # pylint: disable=protected-access

    initial_response = MagicMock()
    initial_response.http_response.json.return_value = {"id": "optimization-job-sync"}
    operation._create_optimization_job_initial = MagicMock(
        return_value=initial_response
    )  # pylint: disable=protected-access

    poller = operation.begin_create_optimization_job(job={}, polling=False)

    assert isinstance(poller, AgentOptimizationLROPoller)
    assert poller.details["job_id"] == "optimization-job-sync"
