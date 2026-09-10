# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore capsys

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest
from azure.ai.projects.models import (
    AgentInsight,
    AgentInsightRun,
    AgentInsightRunResult,
    AgentInsightStatus,
)
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations
from azure.core.exceptions import ResourceExistsError

from agent_insights.sample_test_helpers import assert_agent_insights_output


@pytest.fixture
def scheduled_sample(monkeypatch):
    path = Path(__file__).parents[2] / "samples" / "agent_insights" / "sample_agent_insights_scheduled.py"
    sample = runpy.run_path(str(path))
    monkeypatch.setattr(sample["time"], "sleep", MagicMock())
    return sample


@pytest.fixture
def on_demand_sample():
    path = Path(__file__).parents[2] / "samples" / "agent_insights" / "sample_agent_insights_on_demand.py"
    return runpy.run_path(str(path))


@pytest.fixture
def cleanup_sample(scheduled_sample):
    return scheduled_sample


def test_cleanup_cancels_active_run(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [AgentInsightRun({"id": "run-test", "status": "queued"})],
        [AgentInsightRun({"id": "run-test", "status": "cancelled"})],
    ]

    cleanup_sample["_delete_monitor"](operations, "monitor-test")

    assert operations.update.call_args.args[1].enabled is False
    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.delete.assert_called_once_with("monitor-test")
    cleanup_sample["time"].sleep.assert_called_once_with(10)
    assert [method[0] for method in operations.method_calls] == [
        "update",
        "list_runs",
        "cancel_run",
        "list_runs",
        "delete",
    ]


def test_cleanup_has_bounded_wait(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="in_progress")]

    with pytest.raises(TimeoutError, match="could not be deleted"):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    assert operations.list_runs.call_count == 12
    assert operations.cancel_run.call_args_list == [call("monitor-test", "run-test")] * 12
    operations.delete.assert_not_called()
    assert cleanup_sample["time"].sleep.call_args_list == [call(10)] * 11


def test_cleanup_handles_run_dispatch_during_delete(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [],
        [SimpleNamespace(id="run-test", status="queued")],
        [SimpleNamespace(id="run-test", status="cancelled")],
    ]
    operations.delete.side_effect = [ResourceExistsError(), None]

    cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    assert operations.delete.call_count == 2


def test_cleanup_handles_run_finishing_during_cancel(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    terminal_run = AgentInsightRun({"id": "run-test", "status": "succeeded"})
    operations.list_runs.side_effect = [
        [AgentInsightRun({"id": "run-test", "status": "queued"})],
        [terminal_run],
    ]
    operations.cancel_run.side_effect = ResourceExistsError()

    cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.get_run.assert_not_called()
    operations.delete.assert_called_once_with("monitor-test")


def test_cleanup_repeated_delete_conflict_is_bounded(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = []
    error = ResourceExistsError("Monitor still has an active run")
    operations.delete.side_effect = error

    with pytest.raises(ResourceExistsError) as exc_info:
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    assert exc_info.value is error
    assert operations.list_runs.call_count == operations.delete.call_count == 12
    assert cleanup_sample["time"].sleep.call_args_list == [call(10)] * 11


@pytest.fixture
def on_demand_main(on_demand_sample, monkeypatch):
    main = on_demand_sample["main"]
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list.return_value = [SimpleNamespace(id="old-monitor")]
    operations.create.return_value = SimpleNamespace(
        id="new-monitor", agent_name="test-agent", enabled=False, run_interval_hours=6
    )
    operations.begin_create_run.return_value.details = {"run_id": "new-run"}
    operations.begin_create_run.return_value.result.return_value = AgentInsightRunResult(
        traces_in_window=10,
        traces_analyzed=10,
        insights_created=1,
        insights_updated=0,
        insights_reopened=0,
        token_usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 15},
    )
    operations.get_run.return_value = AgentInsightRun(status="succeeded")
    operations.list_runs.return_value = [SimpleNamespace(id="new-run", status="succeeded")]
    insight = {
        "id": "insight-test",
        "title": "Require approval",
        "severity": "high",
        "status": "active",
        "trace_count": 8,
        "details": {"recommended_actions": {"proposed_fix": {"kind": "prose", "text": "Check approval first."}}},
    }
    operations.list_insights.return_value = [AgentInsight(insight)]
    operations.update_insight.return_value = AgentInsight({**insight, "status": "resolved"})
    client = MagicMock()
    client.return_value.__enter__.return_value.beta.agent_insight_monitors = operations
    monkeypatch.setitem(main.__globals__, "AIProjectClient", client)
    monkeypatch.setitem(main.__globals__, "DefaultAzureCredential", MagicMock())
    monkeypatch.setitem(main.__globals__, "load_dotenv", MagicMock())
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-agent")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")
    return main, operations


@pytest.mark.parametrize("polling_error", [RuntimeError("Polling failed"), KeyboardInterrupt()])
def test_on_demand_leaves_monitor_after_polling_error(on_demand_main, polling_error, capsys):
    main, operations = on_demand_main
    operations.begin_create_run.return_value.result.side_effect = polling_error
    with pytest.raises(type(polling_error)) as exc_info:
        main()

    assert exc_info.value is polling_error
    operations.list.assert_not_called()
    operations.cancel_run.assert_not_called()
    operations.delete.assert_not_called()
    operations.update.assert_not_called()
    operations.list_runs.assert_not_called()
    assert "Deleted monitor" not in capsys.readouterr().out


def test_on_demand_accepts_future_severity(on_demand_main, capsys):
    main, operations = on_demand_main
    operations.list_insights.return_value[0].severity = "future-severity"

    main()

    operations.delete.assert_called_once_with("new-monitor")
    operations.list.assert_not_called()
    output = capsys.readouterr().out.splitlines()
    assert_agent_insights_output("sample_agent_insights_on_demand.py", output)
    assert any("severity=future-severity," in line for line in output)
    operations.update_insight.assert_called_once()
    assert operations.update_insight.call_args.args[:2] == ("new-monitor", "insight-test")
    assert operations.update_insight.call_args.args[2].status == "resolved"


def test_on_demand_allows_no_insights_for_customer_data(on_demand_main, capsys):
    main, operations = on_demand_main
    operations.list_insights.return_value = []

    main()

    operations.update_insight.assert_not_called()
    assert "No insights were available to resolve." in capsys.readouterr().out


def test_on_demand_allows_insight_without_optional_details(on_demand_main, capsys):
    main, operations = on_demand_main
    operations.list_insights.return_value[0].details = None

    main()

    output = capsys.readouterr().out
    assert "Insight `insight-test`:" in output
    assert "Recommended action:" not in output
    assert f"Insight status after update: {AgentInsightStatus.RESOLVED}" in output


def test_on_demand_reports_creation_failure(on_demand_main):
    main, operations = on_demand_main
    error = ResourceExistsError("Existing monitor")
    operations.create.side_effect = error

    with pytest.raises(ResourceExistsError) as exc_info:
        main()

    assert exc_info.value is error
    operations.list.assert_not_called()
    operations.delete.assert_not_called()
    operations.update.assert_not_called()
    operations.cancel_run.assert_not_called()
    operations.begin_create_run.assert_not_called()


@pytest.mark.parametrize("configuration_error", [RuntimeError("Schedule configuration failed"), KeyboardInterrupt()])
def test_scheduled_sample_cleans_up_after_configuration_error(scheduled_sample, monkeypatch, configuration_error):
    main = scheduled_sample["main"]
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list.return_value = [SimpleNamespace(id="old-monitor")]
    operations.create.return_value = SimpleNamespace(id="new-monitor", agent_name="test-agent")
    operations.update.side_effect = configuration_error
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

    with pytest.raises(type(configuration_error)) as exc_info:
        main()
    assert exc_info.value is configuration_error

    cleanup.assert_called_once_with(operations, "new-monitor")
    operations.list.assert_not_called()
    assert operations.create.call_args.args[0].enabled is False
    assert operations.update.call_args.args[1].run_interval_hours == 6
    assert operations.update.call_args.args[1].enabled is True


def test_scheduled_creation_failure_leaves_existing_monitor(scheduled_sample, monkeypatch, on_demand_main):
    main = scheduled_sample["main"]
    configured_main, operations = on_demand_main
    for name in ("AIProjectClient", "DefaultAzureCredential", "load_dotenv"):
        monkeypatch.setitem(main.__globals__, name, configured_main.__globals__[name])
    error = ResourceExistsError("Existing monitor")
    operations.create.side_effect = error

    with pytest.raises(ResourceExistsError) as exc_info:
        main()

    assert exc_info.value is error
    operations.list.assert_not_called()
    operations.update.assert_not_called()
    operations.list_runs.assert_not_called()
    operations.cancel_run.assert_not_called()
    operations.delete.assert_not_called()
