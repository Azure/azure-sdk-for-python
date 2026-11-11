# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for shared polling customizations."""

import pytest
from azure.core.polling.base_polling import LROBasePolling
from azure.core.polling.async_base_polling import AsyncLROBasePolling

from azure.ai.projects._utils.polling import AIProjectsLROBasePolling, AsyncAIProjectsLROBasePolling
from azure.ai.projects.operations import (
    _patch_agent_insights,
    _patch_agents,
    _patch_datasets,
    _patch_evaluators,
)
from azure.ai.projects.aio.operations import (
    _patch_agent_insights_async,
    _patch_agents_async,
    _patch_datasets_async,
    _patch_evaluators_async,
)
from azure.ai.projects.models._patch import (
    _AsyncUpdateMemoriesLROPollingMethod,
    _UpdateMemoriesLROPollingMethod,
)


@pytest.mark.parametrize(
    "polling_type",
    [
        AIProjectsLROBasePolling,
        AsyncAIProjectsLROBasePolling,
    ],
)
@pytest.mark.parametrize(
    "status, expected",
    [
        ("cancelled", "canceled"),
        ("Cancelled", "canceled"),
        ("completed", "completed"),
    ],
)
def test_polling_status_normalization(polling_type, status, expected):
    """Azure AI Projects pollers expose the normalized cancellation spelling."""
    polling = polling_type.__new__(polling_type)
    polling._operation = object()  # pylint: disable=protected-access
    polling._status = status  # pylint: disable=protected-access

    assert polling.status() == expected


@pytest.mark.parametrize("polling_type", [LROBasePolling, AsyncLROBasePolling])
def test_azure_core_polling_status_is_unchanged(polling_type):
    """Importing Azure AI Projects does not alter Azure Core polling behavior."""
    polling = polling_type.__new__(polling_type)
    polling._operation = object()  # pylint: disable=protected-access
    polling._status = "cancelled"  # pylint: disable=protected-access

    assert polling.status() == "cancelled"


@pytest.mark.parametrize(
    "operation_module",
    [_patch_agent_insights, _patch_agents, _patch_datasets, _patch_evaluators],
)
def test_sync_projects_operation_modules_use_local_polling(operation_module):
    assert operation_module.AIProjectsLROBasePolling is AIProjectsLROBasePolling


@pytest.mark.parametrize(
    "operation_module",
    [_patch_agent_insights_async, _patch_agents_async, _patch_datasets_async, _patch_evaluators_async],
)
def test_async_projects_operation_modules_use_local_polling(operation_module):
    assert operation_module.AsyncAIProjectsLROBasePolling is AsyncAIProjectsLROBasePolling


def test_memory_polling_uses_local_polling():
    assert issubclass(_UpdateMemoriesLROPollingMethod, AIProjectsLROBasePolling)
    assert issubclass(_AsyncUpdateMemoriesLROPollingMethod, AsyncAIProjectsLROBasePolling)
