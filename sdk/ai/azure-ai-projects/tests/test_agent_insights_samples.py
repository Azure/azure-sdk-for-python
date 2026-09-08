# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


@pytest.fixture
def scheduled_sample(monkeypatch):
    path = Path(__file__).parents[1] / "samples" / "agent_insights" / "sample_agent_insights_scheduled.py"
    sample = runpy.run_path(str(path))
    monkeypatch.setattr(sample["time"], "sleep", MagicMock())
    return sample


def test_scheduled_cleanup_cancels_active_run(scheduled_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [SimpleNamespace(id="run-test", status="in_progress")],
        [SimpleNamespace(id="run-test", status="cancelled")],
    ]

    scheduled_sample["_delete_monitor"](operations, "monitor-test", "Scheduled")

    assert operations.update.call_args.args[1].enabled is False
    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.delete.assert_called_once_with("monitor-test")
    scheduled_sample["time"].sleep.assert_called_once_with(2)


def test_scheduled_cleanup_does_not_cancel_completed_run(scheduled_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="succeeded")]

    scheduled_sample["_delete_monitor"](operations, "monitor-test", "Scheduled")

    operations.cancel_run.assert_not_called()
    operations.delete.assert_called_once_with("monitor-test")
    scheduled_sample["time"].sleep.assert_not_called()


def test_scheduled_cleanup_handles_already_deleted_monitor(scheduled_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.update.side_effect = ResourceNotFoundError()

    scheduled_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.list_runs.assert_not_called()
    operations.delete.assert_not_called()


def test_scheduled_cleanup_has_bounded_wait(scheduled_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="in_progress")]

    with pytest.raises(TimeoutError, match="could not be deleted"):
        scheduled_sample["_delete_monitor"](operations, "monitor-test", "Scheduled")

    assert operations.list_runs.call_count == 30
    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.delete.assert_not_called()


def test_scheduled_cleanup_handles_run_dispatch_during_delete(scheduled_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [],
        [SimpleNamespace(id="run-test", status="queued")],
        [SimpleNamespace(id="run-test", status="cancelled")],
    ]
    operations.delete.side_effect = [ResourceExistsError(), None]

    scheduled_sample["_delete_monitor"](operations, "monitor-test", "Scheduled")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    assert operations.delete.call_count == 2


def test_scheduled_sample_cleans_up_after_configuration_error(scheduled_sample, monkeypatch):
    main = scheduled_sample["main"]
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list.return_value = [SimpleNamespace(id="old-monitor")]
    operations.create.return_value = SimpleNamespace(id="new-monitor", agent_name="test-agent")
    operations.update.side_effect = RuntimeError("Schedule configuration failed")
    client = MagicMock()
    client.return_value.__enter__.return_value.beta.agent_insight_monitors = operations
    cleanup = MagicMock()
    monkeypatch.setitem(main.__globals__, "AIProjectClient", client)
    monkeypatch.setitem(main.__globals__, "DefaultAzureCredential", MagicMock())
    monkeypatch.setitem(main.__globals__, "load_dotenv", MagicMock())
    monkeypatch.setitem(main.__globals__, "_delete_monitor", cleanup)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-agent")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")

    with pytest.raises(RuntimeError, match="Schedule configuration failed"):
        main()

    assert cleanup.call_args_list == [
        call(operations, "old-monitor", "Existing"),
        call(operations, "new-monitor", "Scheduled"),
    ]
    assert operations.create.call_args.args[0].enabled is False
    assert operations.update.call_args.args[1].run_interval_hours == 6
    assert operations.update.call_args.args[1].enabled is True
