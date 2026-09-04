# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Unit tests for Agent Insights run poller configuration."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from azure.ai.projects.aio.operations._patch_agent_insights_async import (
    BetaAgentInsightMonitorsOperations as AsyncBetaAgentInsightMonitorsOperations,
)
from azure.ai.projects.operations._patch_agent_insights import (
    BetaAgentInsightMonitorsOperations,
)


def test_begin_create_run_uses_operation_location_as_final_state() -> None:
    """The sync poller returns the completed operation response without a final Location GET."""
    operation = BetaAgentInsightMonitorsOperations.__new__(
        BetaAgentInsightMonitorsOperations
    )
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
    initial_response.http_response.json.return_value = {"id": "run-sync"}
    operation._create_run_initial = MagicMock(  # pylint: disable=protected-access
        return_value=initial_response
    )

    polling_method = MagicMock()
    polling_method.finished.return_value = True
    with patch(
        "azure.ai.projects.operations._patch_agent_insights.LROBasePolling",
        return_value=polling_method,
    ) as polling_type:
        poller = operation.begin_create_run("monitor-sync", run={})

    assert poller.details["run_id"] == "run-sync"
    assert polling_type.call_args.kwargs["lro_options"] == {
        "final-state-via": "operation-location"
    }


@pytest.mark.asyncio
async def test_begin_create_run_uses_operation_location_as_final_state_async() -> None:
    """The async poller returns the operation response without a final Location GET."""
    operation = AsyncBetaAgentInsightMonitorsOperations.__new__(
        AsyncBetaAgentInsightMonitorsOperations
    )
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
    initial_response.http_response.json.return_value = {"id": "run-async"}
    initial_response.http_response.read = AsyncMock()
    operation._create_run_initial = AsyncMock(  # pylint: disable=protected-access
        return_value=initial_response
    )

    polling_method = MagicMock()
    with patch(
        "azure.ai.projects.aio.operations._patch_agent_insights_async.AsyncLROBasePolling",
        return_value=polling_method,
    ) as polling_type:
        poller = await operation.begin_create_run("monitor-async", run={})

    assert poller.details["run_id"] == "run-async"
    assert polling_type.call_args.kwargs["lro_options"] == {
        "final-state-via": "operation-location"
    }
