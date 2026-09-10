# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from azure.monitor.query import LogsQueryStatus
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from recording_fixture import (
    FixtureAgent,
    RecordingFixtureError,
    TraceBatch,
    emit_fixture_traces,
    wait_for_trace_ingestion,
)


def test_recording_resources_are_not_auto_discovered() -> None:
    resources = Path(__file__).parent / "resources"
    assert (resources / "recording-resources.bicep").is_file()
    assert (resources / "validate-recording-model.ps1").is_file()
    assert not list(resources.rglob("test-resources.bicep"))
    assert not list(resources.rglob("test-resources.json"))
    assert not list(resources.rglob("test-resources-post.ps1"))


def _batch() -> TraceBatch:
    return TraceBatch(
        marker="fixture-marker",
        trace_ids=("trace-1", "trace-2"),
        span_ids=("root-1", "chat-1", "tool-1", "root-2", "chat-2"),
        window_start=datetime(2026, 9, 1, 1, tzinfo=timezone.utc),
        window_end=datetime(2026, 9, 1, 2, tzinfo=timezone.utc),
    )


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
    assert set(batch.span_ids) == {f"{span.context.span_id:016x}" for span in spans}
    assert len(batch.span_ids) == 8
    assert batch.marker == "agent-insights-recording-marker"
    assert all(span.attributes["gen_ai.agent.id"] == "fixture-otel" for span in spans)

    tool_results = [
        span.attributes["gen_ai.tool.call.result"]
        for span in spans
        if span.attributes["gen_ai.operation.name"] == "execute_tool"
    ]
    assert all('"deleted":true' in result for result in tool_results)
    control_chat = next(
        span
        for span in spans
        if span.attributes["gen_ai.operation.name"] == "chat"
        and span.attributes["gen_ai.conversation.id"] == "recording-conversation-conversation-3"
    )
    assert "cannot verify" in control_chat.attributes["gen_ai.output.messages"]
    assert "is active" not in control_chat.attributes["gen_ai.output.messages"]


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


def test_wait_for_trace_ingestion_waits_for_chat_and_tool_spans() -> None:
    responses = [
        [["trace-1", "root-1"], ["trace-2", "root-2"]],
        [["trace-1", "root-1"], ["trace-2", "root-2"], ["trace-1", "chat-1"], ["trace-2", "chat-2"]],
        [
            ["trace-1", "root-1"],
            ["trace-2", "root-2"],
            ["trace-1", "chat-1"],
            ["trace-2", "chat-2"],
            ["trace-1", "tool-1"],
        ],
    ]

    class LogsClient:
        def __init__(self):
            self.calls = 0

        def query_resource(self, *_args, **_kwargs):
            rows = responses[self.calls]
            self.calls += 1
            table = SimpleNamespace(columns=["trace_id", "span_id"], rows=rows)
            return SimpleNamespace(status=LogsQueryStatus.SUCCESS, tables=[table])

    client = LogsClient()
    wait_for_trace_ingestion(
        client,
        "application-insights-resource",
        "fixture-otel",
        _batch(),
        timeout_seconds=1,
        sleep=lambda _seconds: None,
    )
    assert client.calls == 3
