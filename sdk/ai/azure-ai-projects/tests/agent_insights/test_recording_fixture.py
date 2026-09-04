# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

import pytest
from azure.ai.projects.models import ExternalAgentDefinition
from azure.core.exceptions import HttpResponseError
from azure.monitor.query import LogsQueryStatus
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from recording_fixture import (
    FixtureAgent,
    RecordingFixtureError,
    TraceBatch,
    _build_ingestion_query,
    emit_fixture_traces,
    reconcile_external_agent,
    wait_for_trace_ingestion,
)


class _AgentOperations:
    def __init__(self, versions: list[Any] | None = None) -> None:
        self.versions = versions or []
        self.created: list[dict[str, Any]] = []

    def list_versions(self, agent_name: str, *, order: str | None = None, **kwargs: Any) -> list[Any]:
        del agent_name, kwargs
        assert order == "asc"
        return self.versions

    def create_version(
        self,
        agent_name: str,
        *,
        definition: ExternalAgentDefinition,
        metadata: dict[str, str] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> Any:
        del kwargs
        self.created.append(
            {
                "agent_name": agent_name,
                "definition": definition,
                "metadata": metadata,
                "description": description,
            }
        )
        created = SimpleNamespace(
            version="1",
            definition=SimpleNamespace(kind="external", otel_agent_id=definition.otel_agent_id),
        )
        self.versions.append(created)
        return created


def _batch() -> TraceBatch:
    return TraceBatch(
        marker="fixture-marker",
        trace_ids=("trace-1", "trace-2"),
        window_start=datetime(2026, 9, 1, 1, tzinfo=timezone.utc),
        window_end=datetime(2026, 9, 1, 2, tzinfo=timezone.utc),
    )


def test_reconcile_external_agent_creates_missing_version() -> None:
    operations = _AgentOperations()

    agent = reconcile_external_agent(operations, "fixture-agent", "fixture-otel")

    assert agent == FixtureAgent("fixture-agent", "1", "fixture-otel")
    assert operations.created[0]["metadata"] == {"agent_insights_recording_fixture": "v1"}
    assert operations.created[0]["definition"].otel_agent_id == "fixture-otel"


def test_reconcile_external_agent_reuses_matching_version() -> None:
    existing = SimpleNamespace(
        version="7",
        definition=SimpleNamespace(kind="external", otel_agent_id="fixture-otel"),
    )
    operations = _AgentOperations([existing])

    agent = reconcile_external_agent(operations, "fixture-agent", "fixture-otel")

    assert agent == FixtureAgent("fixture-agent", "7", "fixture-otel")
    assert not operations.created


@pytest.mark.parametrize(
    "versions",
    [
        [
            SimpleNamespace(
                version="1",
                definition=SimpleNamespace(kind="external", otel_agent_id="unexpected-otel"),
            )
        ],
        [
            SimpleNamespace(
                version="1",
                definition=SimpleNamespace(kind="external", otel_agent_id="fixture-otel"),
            ),
            SimpleNamespace(
                version="2",
                definition=SimpleNamespace(kind="external", otel_agent_id="fixture-otel"),
            ),
        ],
    ],
)
def test_reconcile_external_agent_rejects_drift(versions: list[Any]) -> None:
    with pytest.raises(RecordingFixtureError):
        reconcile_external_agent(_AgentOperations(versions), "fixture-agent", "fixture-otel")


def test_emit_fixture_traces_builds_defects_and_controls() -> None:
    exporter = InMemorySpanExporter()
    values = iter(
        [
            "marker",
            "conversation-1",
            "conversation-2",
            "conversation-3",
        ]
    )
    fixed_time = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)

    batch = emit_fixture_traces(
        "unused-connection-string",
        FixtureAgent("fixture-agent", "1", "fixture-otel"),
        defect_trace_count=2,
        control_trace_count=1,
        exporter_factory=lambda _connection_string: exporter,
        uuid_factory=lambda: next(values),
        now=lambda: fixed_time,
    )

    spans = exporter.get_finished_spans()
    operations = [span.attributes["gen_ai.operation.name"] for span in spans]
    assert operations.count("invoke_agent") == 3
    assert operations.count("chat") == 3
    assert operations.count("execute_tool") == 2
    assert len(batch.trace_ids) == 3
    assert len(set(batch.trace_ids)) == 3
    assert batch.marker == "agent-insights-recording-marker"
    assert all(span.attributes["gen_ai.agent.id"] == "fixture-otel" for span in spans)

    tool_results = [
        span.attributes["gen_ai.tool.call.result"]
        for span in spans
        if span.attributes["gen_ai.operation.name"] == "execute_tool"
    ]
    assert all('"deleted":true' in result for result in tool_results)


def test_wait_for_trace_ingestion_retries_until_all_traces_are_visible() -> None:
    class LogsClient:
        def __init__(self) -> None:
            self.calls = 0

        def query_resource(self, *_args: Any, **_kwargs: Any) -> Any:
            self.calls += 1
            rows = [["trace-1"]] if self.calls == 1 else [["trace-1"], ["trace-2"]]
            table = SimpleNamespace(columns=["trace_id"], rows=rows)
            return SimpleNamespace(status=LogsQueryStatus.SUCCESS, tables=[table])

        def close(self) -> None:
            pass

    client = LogsClient()
    wait_for_trace_ingestion(
        client,
        "application-insights-resource",
        "fixture-otel",
        _batch(),
        timeout_seconds=1,
        sleep=lambda _seconds: None,
    )

    assert client.calls == 2


def test_wait_for_trace_ingestion_retries_role_propagation_failure() -> None:
    class LogsClient:
        def __init__(self) -> None:
            self.calls = 0

        def query_resource(self, *_args: Any, **_kwargs: Any) -> Any:
            self.calls += 1
            if self.calls == 1:
                error = HttpResponseError(message="Forbidden")
                error.status_code = 403
                raise error
            table = SimpleNamespace(columns=["trace_id"], rows=[["trace-1"], ["trace-2"]])
            return SimpleNamespace(status=LogsQueryStatus.SUCCESS, tables=[table])

        def close(self) -> None:
            pass

    client = LogsClient()
    wait_for_trace_ingestion(
        client,
        "application-insights-resource",
        "fixture-otel",
        _batch(),
        timeout_seconds=1,
        sleep=lambda _seconds: None,
    )

    assert client.calls == 2


def test_wait_for_trace_ingestion_fails_after_timeout() -> None:
    class LogsClient:
        def query_resource(self, *_args: Any, **_kwargs: Any) -> Any:
            table = SimpleNamespace(columns=[SimpleNamespace(name="trace_id")], rows=[])
            return SimpleNamespace(status=LogsQueryStatus.SUCCESS, tables=[table])

        def close(self) -> None:
            pass

    times = iter([0.0, 0.0, 1.0])
    with pytest.raises(RecordingFixtureError, match="did not expose"):
        wait_for_trace_ingestion(
            LogsClient(),
            "application-insights-resource",
            "fixture-otel",
            _batch(),
            timeout_seconds=0.5,
            sleep=lambda _seconds: None,
            monotonic=lambda: next(times),
        )


def test_ingestion_query_escapes_values() -> None:
    query = _build_ingestion_query("marker'\\value", "agent'\\value")

    assert "marker''\\\\value" in query
    assert "agent''\\\\value" in query
