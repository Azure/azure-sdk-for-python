# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest
from azure.ai.projects.models import AgentInsight, AgentInsightMonitor, AgentInsightRunResult
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations
from azure.core.exceptions import HttpResponseError, ResourceExistsError, ResourceNotFoundError


@pytest.fixture
def scheduled_sample(monkeypatch):
    path = Path(__file__).parents[1] / "samples" / "agent_insights" / "sample_agent_insights_scheduled.py"
    sample = runpy.run_path(str(path))
    monkeypatch.setattr(sample["time"], "sleep", MagicMock())
    return sample


@pytest.fixture
def on_demand_sample(monkeypatch):
    path = Path(__file__).parents[1] / "samples" / "agent_insights" / "sample_agent_insights_on_demand.py"
    sample = runpy.run_path(str(path))
    monkeypatch.setattr(sample["time"], "sleep", MagicMock())
    return sample


@pytest.fixture(params=["scheduled_sample", "on_demand_sample"])
def cleanup_sample(request):
    return request.getfixturevalue(request.param)


def test_cleanup_cancels_active_run(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [SimpleNamespace(id="run-test", status="in_progress")],
        [SimpleNamespace(id="run-test", status="cancelled")],
    ]

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    assert operations.update.call_args.args[1].enabled is False
    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.delete.assert_called_once_with("monitor-test")
    cleanup_sample["time"].sleep.assert_called_once_with(2)


def test_cleanup_does_not_cancel_completed_run(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="succeeded")]

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.cancel_run.assert_not_called()
    operations.delete.assert_called_once_with("monitor-test")
    cleanup_sample["time"].sleep.assert_not_called()


def test_cleanup_handles_already_deleted_monitor(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.update.side_effect = ResourceNotFoundError()

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.list_runs.assert_not_called()
    operations.delete.assert_not_called()


def test_cleanup_has_bounded_wait(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="in_progress")]

    with pytest.raises(TimeoutError, match="could not be deleted"):
        cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    assert operations.list_runs.call_count == 30
    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.delete.assert_not_called()
    assert cleanup_sample["time"].sleep.call_args_list == [call(2)] * 29


def test_cleanup_handles_run_dispatch_during_delete(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [],
        [SimpleNamespace(id="run-test", status="queued")],
        [SimpleNamespace(id="run-test", status="cancelled")],
    ]
    operations.delete.side_effect = [ResourceExistsError(), None]

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    assert operations.delete.call_count == 2


@pytest.mark.parametrize("status", ["succeeded", "failed", "cancelled"])
def test_cleanup_handles_run_finishing_during_cancel(cleanup_sample, status):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    terminal_run = SimpleNamespace(id="run-test", status=SimpleNamespace(value=status))
    operations.list_runs.side_effect = [
        [SimpleNamespace(id="run-test", status=SimpleNamespace(value="queued"))],
        [terminal_run],
    ]
    operations.cancel_run.side_effect = ResourceExistsError()
    operations.get_run.return_value = terminal_run

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.get_run.assert_called_once_with("monitor-test", "run-test")
    operations.delete.assert_called_once_with("monitor-test")


def test_cleanup_raises_cancel_conflict_for_active_run(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    active_run = SimpleNamespace(id="run-test", status="in_progress")
    operations.list_runs.return_value = [active_run]
    operations.cancel_run.side_effect = ResourceExistsError()
    operations.get_run.return_value = active_run

    with pytest.raises(ResourceExistsError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.delete.assert_not_called()


def test_cleanup_handles_monitor_deleted_during_delete(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = []
    operations.delete.side_effect = ResourceNotFoundError()

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.delete.assert_called_once_with("monitor-test")
    cleanup_sample["time"].sleep.assert_not_called()


def test_cleanup_does_not_hide_delete_error(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = []
    operations.delete.side_effect = HttpResponseError("Delete failed")

    with pytest.raises(HttpResponseError, match="Delete failed"):
        cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")


def test_cleanup_confirms_monitor_disappeared_during_list(cleanup_sample, capsys):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = ResourceNotFoundError()
    operations.get.side_effect = ResourceNotFoundError()

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    operations.get.assert_called_once_with("monitor-test")
    operations.delete.assert_not_called()
    assert "was already deleted." in capsys.readouterr().out


def test_cleanup_does_not_hide_missing_list_endpoint(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = ResourceNotFoundError()
    operations.get.return_value = SimpleNamespace(id="monitor-test")

    with pytest.raises(ResourceNotFoundError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")
    operations.delete.assert_not_called()


@pytest.mark.parametrize("stage", ["cancel", "get_run"])
def test_cleanup_relists_when_run_disappears(cleanup_sample, stage):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [[SimpleNamespace(id="run-test", status="in_progress")], []]
    operations.cancel_run.side_effect = ResourceNotFoundError() if stage == "cancel" else ResourceExistsError()
    operations.get_run.side_effect = ResourceNotFoundError()

    cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")

    assert operations.list_runs.call_count == 2
    operations.delete.assert_called_once_with("monitor-test")


def test_cleanup_does_not_report_success_when_cancel_endpoint_is_missing(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = [SimpleNamespace(id="run-test", status="in_progress")]
    operations.cancel_run.side_effect = ResourceNotFoundError()

    with pytest.raises(TimeoutError):
        cleanup_sample["_delete_monitor"](operations, "monitor-test", "Existing")
    operations.delete.assert_not_called()


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
    operations.get_run.return_value = SimpleNamespace(status="succeeded")
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
    operations.get_insight.side_effect = [
        AgentInsight(insight),
        AgentInsight({**insight, "status": "resolved"}),
        AgentInsight(insight),
    ]
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
def test_on_demand_cleans_up_active_runs_after_polling_error(on_demand_main, polling_error, capsys):
    main, operations = on_demand_main
    operations.begin_create_run.return_value.result.side_effect = polling_error
    operations.list_runs.side_effect = [
        [SimpleNamespace(id="old-run", status="queued")],
        [SimpleNamespace(id="old-run", status="cancelled")],
        [SimpleNamespace(id="new-run", status="in_progress")],
        [SimpleNamespace(id="new-run", status="in_progress")],
        [SimpleNamespace(id="new-run", status="cancelled")],
    ]

    with pytest.raises(type(polling_error)) as exc_info:
        main()

    assert exc_info.value is polling_error
    assert operations.cancel_run.call_args_list == [
        call("old-monitor", "old-run"),
        call("new-monitor", "new-run"),
    ]
    assert operations.delete.call_args_list == [call("old-monitor"), call("new-monitor")]
    assert [args.args[0] for args in operations.update.call_args_list] == ["old-monitor", "new-monitor"]
    assert all(args.args[1].enabled is False for args in operations.update.call_args_list)
    assert operations.method_calls.index(call.delete("old-monitor")) < next(
        index for index, method_call in enumerate(operations.method_calls) if method_call[0] == "create"
    )
    assert "Deleted monitor `new-monitor`." in capsys.readouterr().out.splitlines()


def test_on_demand_cleanup_after_success(on_demand_main, capsys):
    main, operations = on_demand_main

    main()

    operations.cancel_run.assert_not_called()
    assert operations.delete.call_args_list == [call("old-monitor"), call("new-monitor")]
    output = capsys.readouterr().out.splitlines()
    assert "Deleted monitor `new-monitor`." in output
    assert "Traces analyzed: 10" in output
    assert "Insight status after update: resolved" in output
    assert "Insight status after reopening: active" in output
    assert "Recommended action: Check approval first." in output
    assert [args.args[2].status for args in operations.update_insight.call_args_list] == ["resolved", "active"]
    assert all(args.args[:2] == ("new-monitor", "insight-test") for args in operations.update_insight.call_args_list)


def test_on_demand_allows_no_insights_for_customer_data(on_demand_main, capsys):
    main, operations = on_demand_main
    operations.list_insights.return_value = []

    main()

    operations.update_insight.assert_not_called()
    assert "No insights were available to demonstrate lifecycle updates." in capsys.readouterr().out


@pytest.mark.parametrize("cleanup_stage", ["before", "after"])
def test_on_demand_cleanup_timeout_is_reported(on_demand_main, cleanup_stage, capsys):
    main, operations = on_demand_main
    polling_error = RuntimeError("Polling failed")
    operations.begin_create_run.return_value.result.side_effect = polling_error
    active_runs = [SimpleNamespace(id="run-test", status="in_progress")]
    operations.list_runs.side_effect = ([[]] if cleanup_stage == "after" else []) + [active_runs] * 30

    with pytest.raises(TimeoutError, match="could not be deleted") as exc_info:
        main()

    if cleanup_stage == "before":
        operations.create.assert_not_called()
        operations.delete.assert_not_called()
    else:
        assert exc_info.value.__context__ is polling_error
        operations.delete.assert_called_once_with("old-monitor")
    assert "Deleted monitor `new-monitor`." not in capsys.readouterr().out


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


@pytest.mark.parametrize("next_run", [1_789_000_000, None])
def test_scheduled_sample_reads_timestamp_and_cleans_up(scheduled_sample, monkeypatch, capsys, next_run):
    main = scheduled_sample["main"]
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list.return_value = []
    operations.create.return_value = SimpleNamespace(id="new-monitor", agent_name="test-agent")
    operations.get.return_value = AgentInsightMonitor(
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

    if next_run is None:
        with pytest.raises(RuntimeError, match="next scheduled run"):
            main()
    else:
        main()
    output = capsys.readouterr().out
    if next_run is not None:
        assert f"Next scheduled run: {operations.get.return_value.next_scheduled_run_at.isoformat()}" in output
        assert "Scheduled monitor enabled: True" in output
    assert "Deleted scheduled monitor `new-monitor`." in output
    operations.cancel_run.assert_called_once_with("new-monitor", "scheduled-run")
    operations.delete.assert_called_once_with("new-monitor")
    assert [args.args[1].enabled for args in operations.update.call_args_list] == [True, False]
