# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# cspell:ignore capsys

from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.trace import get_tracer_provider

from agent_insights.sample_test_helpers import assert_agent_insights_output

from azure.ai.projects.models import (
    AgentInsight,
    AgentInsightRun,
    AgentInsightRunResult,
    AgentInsightStatus,
)
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations
from azure.core.exceptions import ResourceExistsError
from azure.monitor.query import LogsQueryStatus


@pytest.fixture(autouse=True)
def _sample_import_path(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).parents[2] / "samples" / "agent_insights"))


@pytest.fixture(name="scheduled_sample")
def _scheduled_sample(monkeypatch):
    path = Path(__file__).parents[2] / "samples" / "agent_insights" / "sample_agent_insights_scheduled.py"
    sample = runpy.run_path(str(path))
    monkeypatch.setattr(sample["cleanup"].__globals__["time"], "sleep", MagicMock())
    return sample


@pytest.fixture(name="on_demand_sample")
def _on_demand_sample():
    path = Path(__file__).parents[2] / "samples" / "agent_insights" / "sample_agent_insights_on_demand.py"
    return runpy.run_path(str(path))


@pytest.fixture(name="cleanup_sample")
def _cleanup_sample(scheduled_sample):
    return scheduled_sample["cleanup"].__globals__


@pytest.mark.parametrize("name_prefix", ["a" * 31, "my_agent", "-agent"])
def test_invalid_agent_prefix_fails_before_creation(on_demand_sample, name_prefix):
    project = MagicMock()
    with pytest.raises(ValueError, match="FOUNDRY_AGENT_NAME must be 1-30 characters"):
        on_demand_sample["create_agent"](project, name_prefix)
    project.agents.create_version.assert_not_called()


def test_longest_agent_prefix_fits_service_limit(on_demand_sample):
    project = MagicMock()
    on_demand_sample["create_agent"](project, "a" * 30)
    creation = project.agents.create_version.call_args.kwargs
    assert len(creation["agent_name"]) == 63
    assert creation["agent_name"].startswith("a" * 30 + "-")
    assert creation["definition"].otel_agent_id == creation["agent_name"]


def test_cleanup_cancels_active_run(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.side_effect = [
        [AgentInsightRun({"id": "run-test", "status": "queued"})],
        [AgentInsightRun({"id": "run-test", "status": "cancelled"})],
    ]

    cleanup_sample["delete_monitor"](operations, "monitor-test")

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
        cleanup_sample["delete_monitor"](operations, "monitor-test")

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

    cleanup_sample["delete_monitor"](operations, "monitor-test")

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

    cleanup_sample["delete_monitor"](operations, "monitor-test")

    operations.cancel_run.assert_called_once_with("monitor-test", "run-test")
    operations.get_run.assert_not_called()
    operations.delete.assert_called_once_with("monitor-test")


def test_cleanup_repeated_delete_conflict_is_bounded(cleanup_sample):
    operations = MagicMock(spec=BetaAgentInsightMonitorsOperations)
    operations.list_runs.return_value = []
    error = ResourceExistsError("Monitor still has an active run")
    operations.delete.side_effect = error

    with pytest.raises(ResourceExistsError) as exc_info:
        cleanup_sample["delete_monitor"](operations, "monitor-test")

    assert exc_info.value is error
    assert operations.list_runs.call_count == operations.delete.call_count == 12
    assert cleanup_sample["time"].sleep.call_args_list == [call(10)] * 11


@pytest.fixture(name="on_demand_main")
def _on_demand_main(on_demand_sample, monkeypatch):
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
    project = client.return_value.__enter__.return_value
    project.beta.agent_insight_monitors = operations
    project.agents.create_version.return_value = SimpleNamespace(name="test-agent", version="1")
    monkeypatch.setitem(main.__globals__, "AIProjectClient", client)
    monkeypatch.setitem(main.__globals__, "DefaultAzureCredential", MagicMock())
    monkeypatch.setitem(main.__globals__, "load_dotenv", MagicMock())
    monkeypatch.setitem(main.__globals__, "LogsQueryClient", MagicMock())
    monkeypatch.setitem(main.__globals__, "seed_traces", MagicMock(return_value=(10, 10, 10, 8)))
    monkeypatch.setitem(main.__globals__, "wait_for_ingestion", MagicMock())
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.test")
    monkeypatch.setenv("APP_INSIGHTS_RESOURCE_ID", "test-application-insights")
    monkeypatch.setenv("FOUNDRY_MODEL_NAME", "test-model")
    monkeypatch.delenv("FOUNDRY_AGENT_NAME", raising=False)
    return main, operations


@pytest.mark.parametrize("polling_error", [RuntimeError("Polling failed"), KeyboardInterrupt()])
def test_on_demand_cleans_up_after_polling_error(on_demand_main, polling_error, capsys):
    main, operations = on_demand_main
    operations.begin_create_run.return_value.result.side_effect = polling_error
    with pytest.raises(type(polling_error)) as exc_info:
        main()

    assert exc_info.value is polling_error
    operations.list.assert_not_called()
    operations.cancel_run.assert_not_called()
    operations.delete.assert_called_once_with("new-monitor")
    assert operations.update.call_args.args[1].enabled is False
    operations.list_runs.assert_called_once()
    project = main.__globals__["AIProjectClient"].return_value.__enter__.return_value
    project.agents.delete.assert_called_once_with("test-agent", force=True)
    assert "Deleted monitor" in capsys.readouterr().out


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


def test_on_demand_reports_no_insights(on_demand_main, capsys):
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
    project = main.__globals__["AIProjectClient"].return_value.__enter__.return_value
    project.agents.delete.assert_called_once_with("test-agent", force=True)


@pytest.mark.parametrize("configuration_error", [RuntimeError("Schedule configuration failed"), KeyboardInterrupt()])
def test_scheduled_sample_cleans_up_after_configuration_error(
    scheduled_sample, on_demand_main, monkeypatch, configuration_error
):
    main = scheduled_sample["main"]
    configured_main, operations = on_demand_main
    for name in (
        "AIProjectClient",
        "DefaultAzureCredential",
        "load_dotenv",
        "LogsQueryClient",
        "seed_traces",
        "wait_for_ingestion",
    ):
        monkeypatch.setitem(main.__globals__, name, configured_main.__globals__[name])
    operations.update.side_effect = configuration_error
    cleanup = MagicMock()
    monkeypatch.setitem(main.__globals__["cleanup"].__globals__, "delete_monitor", cleanup)
    project = main.__globals__["AIProjectClient"].return_value.__enter__.return_value
    project.attach_mock(cleanup, "cleanup_monitor")

    with pytest.raises(type(configuration_error)) as exc_info:
        main()
    assert exc_info.value is configuration_error

    cleanup.assert_called_once_with(operations, "new-monitor", scheduled=True)
    operations.list.assert_not_called()
    assert operations.create.call_args.args[0].enabled is False
    assert operations.update.call_args.args[1].run_interval_hours == 6
    assert operations.update.call_args.args[1].enabled is True
    project.agents.delete.assert_called_once_with("test-agent", force=True)
    assert project.mock_calls.index(
        call.cleanup_monitor(operations, "new-monitor", scheduled=True)
    ) < project.mock_calls.index(call.agents.delete("test-agent", force=True))


def test_scheduled_creation_failure_leaves_existing_monitor(scheduled_sample, monkeypatch, on_demand_main):
    main = scheduled_sample["main"]
    configured_main, operations = on_demand_main
    for name in (
        "AIProjectClient",
        "DefaultAzureCredential",
        "load_dotenv",
        "LogsQueryClient",
        "seed_traces",
        "wait_for_ingestion",
    ):
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
    project = main.__globals__["AIProjectClient"].return_value.__enter__.return_value
    project.agents.delete.assert_called_once_with("test-agent", force=True)


@pytest.mark.parametrize("sample_fixture", ["on_demand_sample", "scheduled_sample"])
@pytest.mark.parametrize("name_prefix", [None, "", "custom-agent"])
def test_partial_setup_cleans_up_only_owned_agent(request, sample_fixture, name_prefix, on_demand_main, monkeypatch):
    main = request.getfixturevalue(sample_fixture)["main"]
    configured_main, operations = on_demand_main
    for name in (
        "AIProjectClient",
        "DefaultAzureCredential",
        "load_dotenv",
        "LogsQueryClient",
        "seed_traces",
        "wait_for_ingestion",
    ):
        monkeypatch.setitem(main.__globals__, name, configured_main.__globals__[name])
    project = main.__globals__["AIProjectClient"].return_value.__enter__.return_value
    if name_prefix is not None:
        monkeypatch.setenv("FOUNDRY_AGENT_NAME", name_prefix)
    error = RuntimeError("Trace export failed")
    main.__globals__["seed_traces"].side_effect = error

    with pytest.raises(RuntimeError, match="Trace export failed"):
        main()

    creation = project.agents.create_version.call_args.kwargs
    assert creation["agent_name"].startswith(f"{name_prefix or 'agent-insights-sample'}-")
    assert creation["definition"].otel_agent_id == creation["agent_name"]
    assert main.__globals__["AIProjectClient"].call_args.kwargs["allow_preview"] is True
    project.agents.delete.assert_called_once_with("test-agent", force=True)
    operations.create.assert_not_called()
    operations.delete.assert_not_called()

    project.agents.reset_mock()
    project.agents.create_version.side_effect = ResourceExistsError("Agent creation failed")
    with pytest.raises(ResourceExistsError):
        main()
    project.agents.delete.assert_not_called()
    project.agents.list.assert_not_called()


def test_monitor_cleanup_failure_keeps_agent(on_demand_main, capsys):
    main, operations = on_demand_main
    operations.update.side_effect = RuntimeError("Cleanup failed")
    with pytest.raises(RuntimeError, match="Cleanup failed"):
        main()
    project = main.__globals__["AIProjectClient"].return_value.__enter__.return_value
    project.agents.delete.assert_not_called()
    assert "Cleaning up monitor `new-monitor`" in capsys.readouterr().out


@pytest.mark.parametrize("sample_fixture", ["on_demand_sample", "scheduled_sample"])
def test_fictional_trace_shape_and_complete_ingestion(request, sample_fixture, monkeypatch):
    sample = request.getfixturevalue(sample_fixture)
    seed = sample["seed_traces"]
    exporter = InMemorySpanExporter()
    factory = MagicMock()
    factory.from_connection_string.return_value = exporter
    monkeypatch.setitem(seed.__globals__, "AzureMonitorTraceExporter", factory)
    project = MagicMock()
    project.telemetry.get_application_insights_connection_string.return_value = "unused"
    global_provider = get_tracer_provider()

    counts = seed(project, SimpleNamespace(name="unique-agent", version="1"))

    spans = exporter.get_finished_spans()
    operations = [span.attributes["gen_ai.operation.name"] for span in spans]
    assert counts == (10, 10, 10, 8)
    assert [operations.count(name) for name in ("invoke_agent", "chat", "execute_tool")] == list(counts[1:])
    assert len({span.context.trace_id for span in spans}) == counts[0]
    assert len({span.context.span_id for span in spans}) == sum(counts[1:])
    assert all(span.attributes["gen_ai.agent.id"] == "unique-agent" for span in spans)
    assert get_tracer_provider() is global_provider
    tools = [span for span in spans if span.attributes["gen_ai.operation.name"] == "execute_tool"]
    assert all('"deleted":true' in span.attributes["gen_ai.tool.call.result"] for span in tools)
    controls = [span for span in spans if "cannot verify" in span.attributes.get("gen_ai.output.messages", "")]
    assert len(controls) == 2
    assert all("is active" not in span.attributes["gen_ai.output.messages"] for span in controls)
    parents = {span.context.span_id: span for span in spans}
    assert all(parents[span.parent.span_id].attributes["gen_ai.operation.name"] == "chat" for span in tools)

    logs = MagicMock()
    logs.query_resource.side_effect = [
        SimpleNamespace(status=LogsQueryStatus.SUCCESS, tables=[SimpleNamespace(rows=[row])])
        for row in [(10, 10, 0, 0), (10, 10, 10, 0), counts]
    ]
    monkeypatch.setattr(sample["wait_for_ingestion"].__globals__["time"], "sleep", MagicMock())
    sample["wait_for_ingestion"](logs, "resource-id", "unique-agent", counts)
    assert logs.query_resource.call_count == 3
    query = logs.query_resource.call_args.args[1]
    assert "unique-agent" in query and "| distinct trace_id" in query and 'operation == "execute_tool"' in query


def test_ingestion_timeout_and_query_failure(on_demand_sample, monkeypatch):
    wait = on_demand_sample["wait_for_ingestion"]
    logs = MagicMock()
    logs.query_resource.return_value = SimpleNamespace(
        status=LogsQueryStatus.SUCCESS, tables=[SimpleNamespace(rows=[(10, 10, 10, 0)])]
    )
    monkeypatch.setattr(wait.__globals__["time"], "monotonic", MagicMock(side_effect=[0, 1]))
    with pytest.raises(TimeoutError, match="did not expose all spans"):
        wait(logs, "resource-id", "unique-agent", (10, 10, 10, 8), timeout_seconds=1)

    monkeypatch.setattr(wait.__globals__["time"], "monotonic", MagicMock(return_value=0))
    logs.query_resource.side_effect = PermissionError("Query access denied")
    with pytest.raises(PermissionError, match="Query access denied"):
        wait(logs, "resource-id", "unique-agent", (10, 10, 10, 8))
