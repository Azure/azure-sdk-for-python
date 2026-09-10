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
    AgentInsightMonitor,
    AgentInsightRun,
    AgentInsightRunResult,
    AgentInsightStatus,
    JobStatus,
)
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError

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


@pytest.mark.parametrize("status", ["queued", "in_progress", JobStatus.QUEUED, JobStatus.IN_PROGRESS])
def test_cleanup_cancels_active_run(cleanup_sample, status):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [AgentInsightRun({"id": "run-test", "status": status})],
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


def test_cleanup_does_not_cancel_completed_run(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="succeeded")]

    cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.cancel_run.assert_not_called()
    operations.delete.assert_called_once_with("monitor-test")
    cleanup_sample["time"].sleep.assert_not_called()


def test_cleanup_reports_already_deleted_monitor(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.update.side_effect = ResourceNotFoundError()

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.list_runs.assert_not_called()
    operations.delete.assert_not_called()


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


@pytest.mark.parametrize(
    "status", ["succeeded", "failed", "cancelled", JobStatus.SUCCEEDED, JobStatus.FAILED, JobStatus.CANCELLED]
)
def test_cleanup_handles_run_finishing_during_cancel(cleanup_sample, status):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    terminal_run = AgentInsightRun({"id": "run-test", "status": status})
    operations.list_runs.side_effect = [
        [AgentInsightRun({"id": "run-test", "status": JobStatus.QUEUED})],
        [terminal_run],
    ]
    operations.cancel_run.side_effect = ResourceExistsError()

    cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.get_run.assert_not_called()
    operations.delete.assert_called_once_with("monitor-test")


def test_cleanup_repeated_cancel_conflict_is_bounded(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    active_run = SimpleNamespace(id="run-test", status="in_progress")
    operations.list_runs.return_value = [active_run]
    error = ResourceExistsError("Cancellation conflict")
    operations.cancel_run.side_effect = error

    with pytest.raises(ResourceExistsError) as exc_info:
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    assert exc_info.value is error
    assert operations.cancel_run.call_count == 12
    assert cleanup_sample["time"].sleep.call_args_list == [call(10)] * 11
    operations.delete.assert_not_called()


def test_cleanup_reports_monitor_deleted_during_delete(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = []
    operations.delete.side_effect = ResourceNotFoundError()

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.delete.assert_called_once_with("monitor-test")
    cleanup_sample["time"].sleep.assert_not_called()


@pytest.mark.parametrize("stage", ["update", "list_runs", "cancel_run", "delete"])
def test_cleanup_does_not_hide_service_error(cleanup_sample, stage):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = (
        [SimpleNamespace(id="run-test", status="queued")] if stage == "cancel_run" else []
    )
    error = HttpResponseError("Service failed")
    getattr(operations, stage).side_effect = error

    with pytest.raises(HttpResponseError, match="Service failed") as exc_info:
        cleanup_sample["_delete_monitor"](operations, "monitor-test")
    assert exc_info.value is error
    cleanup_sample["time"].sleep.assert_not_called()


def test_cleanup_reports_monitor_disappeared_during_list(cleanup_sample, capsys):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = ResourceNotFoundError()
    operations.get.side_effect = ResourceNotFoundError()

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.get.assert_not_called()
    operations.delete.assert_not_called()
    assert "deleted" not in capsys.readouterr().out


def test_cleanup_does_not_hide_missing_list_endpoint(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = ResourceNotFoundError()
    operations.get.return_value = SimpleNamespace(id="monitor-test")

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")
    operations.delete.assert_not_called()


def test_cleanup_reports_run_disappearing(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [[SimpleNamespace(id="run-test", status="in_progress")], []]
    operations.cancel_run.side_effect = ResourceNotFoundError()

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    operations.list_runs.assert_called_once_with("monitor-test", limit=20)
    operations.delete.assert_not_called()


def test_cleanup_does_not_report_success_when_cancel_endpoint_is_missing(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="in_progress")]
    operations.cancel_run.side_effect = ResourceNotFoundError()

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test")
    operations.delete.assert_not_called()
    cleanup_sample["time"].sleep.assert_not_called()


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


@pytest.mark.parametrize("stage", ["update", "list_runs"])
def test_cleanup_does_not_retry_unrelated_conflicts(cleanup_sample, stage):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    error = ResourceExistsError("Unexpected conflict")
    getattr(operations, stage).side_effect = error

    with pytest.raises(ResourceExistsError) as exc_info:
        cleanup_sample["_delete_monitor"](operations, "monitor-test")

    assert exc_info.value is error
    operations.delete.assert_not_called()
    cleanup_sample["time"].sleep.assert_not_called()


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
    operations.list_runs.side_effect = lambda _monitor_id, *, limit: (
        [SimpleNamespace(id="new-run", status="succeeded")] if limit == 5 else []
    )
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


@pytest.mark.parametrize("severity", ["high", "future-severity"])
def test_on_demand_cleanup_after_success(on_demand_main, capsys, severity):
    main, operations = on_demand_main
    operations.list_insights.return_value[0].severity = severity

    main()

    operations.cancel_run.assert_not_called()
    operations.delete.assert_called_once_with("new-monitor")
    operations.list.assert_not_called()
    operations.update.assert_not_called()
    assert operations.create.call_args.args[0].enabled is False
    assert operations.begin_create_run.call_args.args[1].lookback_hours == 3
    operations.begin_create_run.return_value.result.assert_called_once_with()
    assert [method[0] for method in operations.method_calls] == [
        "create",
        "begin_create_run",
        "get_run",
        "list_runs",
        "list_insights",
        "update_insight",
        "delete",
    ]
    output = capsys.readouterr().out.splitlines()
    assert_agent_insights_output("sample_agent_insights_on_demand.py", output)
    assert "Deleted monitor `new-monitor`." in output
    assert "Traces analyzed: 10" in output
    assert f"Run status: {JobStatus.SUCCEEDED}" in output
    displayed_severity = operations.list_insights.return_value[0].severity
    assert any(f"severity={displayed_severity}, status={AgentInsightStatus.ACTIVE}," in line for line in output)
    assert f"Insight status after update: {AgentInsightStatus.RESOLVED}" in output
    assert "Recommended action: Check approval first." in output
    operations.get_insight.assert_not_called()
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


@pytest.mark.parametrize(
    "error", [HttpResponseError("Monitor creation failed"), ResourceExistsError("Existing monitor")]
)
def test_on_demand_reports_creation_failure(on_demand_main, error):
    main, operations = on_demand_main
    operations.create.side_effect = error

    with pytest.raises(HttpResponseError) as exc_info:
        main()

    assert exc_info.value is error
    operations.list.assert_not_called()
    operations.delete.assert_not_called()
    operations.update.assert_not_called()
    operations.cancel_run.assert_not_called()
    operations.begin_create_run.assert_not_called()


def test_on_demand_reports_deletion_error(on_demand_main):
    main, operations = on_demand_main
    cleanup_error = HttpResponseError("Cleanup failed")
    operations.delete.side_effect = cleanup_error

    with pytest.raises(HttpResponseError) as exc_info:
        main()

    assert exc_info.value is cleanup_error
    operations.delete.assert_called_once_with("new-monitor")


def test_cleanup_error_is_not_hidden_by_callers_exception(on_demand_main):
    main, operations = on_demand_main
    operations.delete.side_effect = HttpResponseError("Cleanup failed")

    try:
        raise ValueError("Caller is handling an unrelated error")
    except ValueError:
        with pytest.raises(HttpResponseError, match="Cleanup failed"):
            main()


@pytest.mark.parametrize("stage", ["begin_create_run", "get_run", "list_runs", "list_insights", "update_insight"])
def test_on_demand_leaves_monitor_after_service_error(on_demand_main, stage, capsys):
    main, operations = on_demand_main
    error = HttpResponseError("Service failed")
    getattr(operations, stage).side_effect = error

    with pytest.raises(HttpResponseError) as exc_info:
        main()

    assert exc_info.value is error
    operations.delete.assert_not_called()
    operations.update.assert_not_called()
    operations.cancel_run.assert_not_called()
    assert "Deleted monitor `new-monitor`." not in capsys.readouterr().out


@pytest.mark.parametrize("configuration_error", [RuntimeError("Schedule configuration failed"), KeyboardInterrupt()])
@pytest.mark.parametrize("cleanup_error", [None, ResourceNotFoundError("Cleanup failed")])
def test_scheduled_sample_cleans_up_after_configuration_error(
    scheduled_sample, monkeypatch, cleanup_error, configuration_error
):
    main = scheduled_sample["main"]
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list.return_value = [SimpleNamespace(id="old-monitor")]
    operations.create.return_value = SimpleNamespace(id="new-monitor", agent_name="test-agent")
    operations.update.side_effect = configuration_error
    client = MagicMock()
    client.return_value.__enter__.return_value.beta.agent_insight_monitors = operations
    cleanup = MagicMock(side_effect=cleanup_error)
    monkeypatch.setitem(main.__globals__, "AIProjectClient", client)
    monkeypatch.setitem(main.__globals__, "DefaultAzureCredential", MagicMock())
    monkeypatch.setitem(main.__globals__, "load_dotenv", MagicMock())
    monkeypatch.setitem(main.__globals__, "_delete_monitor", cleanup)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-agent")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")

    expected_error = cleanup_error if cleanup_error is not None else operations.update.side_effect
    with pytest.raises(type(expected_error)) as exc_info:
        main()
    assert exc_info.value is expected_error
    if cleanup_error is not None:
        assert exc_info.value.__context__ is operations.update.side_effect

    cleanup.assert_called_once_with(operations, "new-monitor")
    operations.list.assert_not_called()
    assert operations.create.call_args.args[0].enabled is False
    assert operations.update.call_args.args[1].run_interval_hours == 6
    assert operations.update.call_args.args[1].enabled is True


@pytest.mark.parametrize(
    "error", [HttpResponseError("Monitor creation failed"), ResourceExistsError("Existing monitor")]
)
def test_scheduled_creation_failure_leaves_existing_monitor(scheduled_sample, monkeypatch, on_demand_main, error):
    main = scheduled_sample["main"]
    configured_main, operations = on_demand_main
    for name in ("AIProjectClient", "DefaultAzureCredential", "load_dotenv"):
        monkeypatch.setitem(main.__globals__, name, configured_main.__globals__[name])
    operations.create.side_effect = error

    with pytest.raises(HttpResponseError) as exc_info:
        main()

    assert exc_info.value is error
    operations.list.assert_not_called()
    operations.update.assert_not_called()
    operations.list_runs.assert_not_called()
    operations.cancel_run.assert_not_called()
    operations.delete.assert_not_called()


@pytest.mark.parametrize("next_run", [1_789_000_000, None])
def test_scheduled_sample_reads_timestamp_and_cleans_up(scheduled_sample, monkeypatch, capsys, next_run):
    main = scheduled_sample["main"]
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list.return_value = []
    operations.create.return_value = SimpleNamespace(id="new-monitor", agent_name="test-agent")
    operations.update.return_value = AgentInsightMonitor(
        {"id": "new-monitor", "enabled": True, "run_interval_hours": 6, "next_scheduled_run_at": next_run}
    )
    operations.list_runs.side_effect = [
        [SimpleNamespace(id="scheduled-run", status="queued")],
        [SimpleNamespace(id="scheduled-run", status="cancelled")],
    ]
    client = MagicMock()
    client.return_value.__enter__.return_value.beta.agent_insight_monitors = operations
    monkeypatch.setitem(main.__globals__, "AIProjectClient", client)
    monkeypatch.setitem(main.__globals__, "DefaultAzureCredential", MagicMock())
    monkeypatch.setitem(main.__globals__, "load_dotenv", MagicMock())
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("FOUNDRY_AGENT_NAME", "test-agent")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")

    main()
    output = capsys.readouterr().out
    assert f"Next scheduled run: {operations.update.return_value.next_scheduled_run_at}" in output
    assert "Scheduled monitor enabled: True" in output
    operations.get.assert_not_called()
    assert "Deleted scheduled monitor `new-monitor`." in output
    operations.cancel_run.assert_called_once_with("new-monitor", "scheduled-run")
    operations.delete.assert_called_once_with("new-monitor")
    operations.list.assert_not_called()
    scheduled_sample["time"].sleep.assert_called_once_with(10)
    assert [args.args[1].enabled for args in operations.update.call_args_list] == [True, False]
