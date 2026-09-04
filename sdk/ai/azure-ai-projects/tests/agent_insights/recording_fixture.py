# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Create deterministic external-agent telemetry for Agent Insights sample recordings."""

from __future__ import annotations

import json
import os
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Protocol, cast

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ExternalAgentDefinition
from azure.core.credentials import TokenCredential
from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
)
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import SpanKind

DEFAULT_DEFECT_TRACE_COUNT = 8
DEFAULT_CONTROL_TRACE_COUNT = 2
DEFAULT_INGESTION_TIMEOUT_SECONDS = 900.0
DEFAULT_ACCESS_TIMEOUT_SECONDS = 300.0


class RecordingFixtureError(RuntimeError):
    """An Agent Insights recording-fixture failure."""


@dataclass(frozen=True, slots=True)
class FixtureSettings:
    project_endpoint: str
    agent_name: str
    otel_agent_id: str
    application_insights_resource_id: str
    defect_trace_count: int = DEFAULT_DEFECT_TRACE_COUNT
    control_trace_count: int = DEFAULT_CONTROL_TRACE_COUNT
    ingestion_timeout_seconds: float = DEFAULT_INGESTION_TIMEOUT_SECONDS

    @classmethod
    def from_environment(cls) -> "FixtureSettings":
        """Load required fixture settings from environment variables."""
        return cls(
            project_endpoint=_required_environment("FOUNDRY_PROJECT_ENDPOINT"),
            agent_name=_required_environment("FOUNDRY_AGENT_NAME"),
            otel_agent_id=_required_environment("AGENT_INSIGHTS_OTEL_AGENT_ID"),
            application_insights_resource_id=_required_environment(
                "AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID"
            ),
        )


@dataclass(frozen=True, slots=True)
class FixtureAgent:
    name: str
    version: str
    otel_agent_id: str


@dataclass(frozen=True, slots=True)
class TraceBatch:
    marker: str
    trace_ids: tuple[str, ...]
    window_start: datetime
    window_end: datetime


class _AgentOperations(Protocol):
    def list_versions(
        self, agent_name: str, *, order: str | None = None, **kwargs: Any
    ) -> Any: ...

    def create_version(
        self,
        agent_name: str,
        *,
        definition: ExternalAgentDefinition,
        metadata: dict[str, str] | None = None,
        description: str | None = None,
        **kwargs: Any,
    ) -> Any: ...


class _TelemetryOperations(Protocol):
    def get_application_insights_connection_string(self) -> str: ...


class _ProjectClient(Protocol):
    @property
    def agents(self) -> _AgentOperations: ...

    @property
    def telemetry(self) -> _TelemetryOperations: ...

    def close(self) -> None: ...


class _LogsClient(Protocol):
    def query_resource(
        self,
        resource_id: str,
        query: str,
        *,
        timespan: tuple[datetime, datetime],
        server_timeout: int | None = None,
        **kwargs: Any,
    ) -> Any: ...

    def close(self) -> None: ...


ProjectClientFactory = Callable[[str, TokenCredential], _ProjectClient]
LogsClientFactory = Callable[[TokenCredential], _LogsClient]
TraceEmitter = Callable[[str, FixtureAgent, int, int], TraceBatch]


def _default_project_client_factory(
    endpoint: str, credential: TokenCredential
) -> _ProjectClient:
    return cast(
        _ProjectClient,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True),
    )


def _default_logs_client_factory(credential: TokenCredential) -> _LogsClient:
    return cast(_LogsClient, LogsQueryClient(credential))


def provision_recording_fixture(
    settings: FixtureSettings,
    *,
    credential: TokenCredential | None = None,
    project_client_factory: ProjectClientFactory = _default_project_client_factory,
    logs_client_factory: LogsClientFactory = _default_logs_client_factory,
    trace_emitter: TraceEmitter | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> tuple[FixtureAgent, TraceBatch]:
    """Reconcile the fixture agent, emit traces, and wait for ingestion."""
    owns_credential = credential is None
    selected_credential = credential or DefaultAzureCredential()
    project: _ProjectClient | None = None
    logs: _LogsClient | None = None
    try:
        print("Reconciling the Agent Insights external-agent fixture.")
        project = project_client_factory(settings.project_endpoint, selected_credential)
        agent, connection_string = _wait_for_foundry_access(
            project,
            settings.agent_name,
            settings.otel_agent_id,
            timeout_seconds=DEFAULT_ACCESS_TIMEOUT_SECONDS,
            sleep=sleep,
            monotonic=monotonic,
        )
        emitter = trace_emitter or emit_fixture_traces
        batch = emitter(
            connection_string,
            agent,
            settings.defect_trace_count,
            settings.control_trace_count,
        )
        print(f"Exported {len(batch.trace_ids)} fixture traces. Waiting for ingestion.")
        logs = logs_client_factory(selected_credential)
        wait_for_trace_ingestion(
            logs,
            settings.application_insights_resource_id,
            agent.otel_agent_id,
            batch,
            timeout_seconds=settings.ingestion_timeout_seconds,
            sleep=sleep,
            monotonic=monotonic,
        )
        return agent, batch
    finally:
        try:
            if logs is not None:
                logs.close()
        finally:
            try:
                if project is not None:
                    project.close()
            finally:
                if owns_credential:
                    close = getattr(selected_credential, "close", None)
                    if callable(close):
                        close()


def reconcile_external_agent(
    operations: _AgentOperations,
    agent_name: str,
    otel_agent_id: str,
) -> FixtureAgent:
    """Create the fixture agent once and reject unexpected immutable versions."""
    try:
        versions = list(operations.list_versions(agent_name, order="asc"))
    except ResourceNotFoundError:
        versions = []
    except HttpResponseError as error:
        if getattr(error, "status_code", None) != 404:
            raise
        versions = []

    if not versions:
        created = operations.create_version(
            agent_name=agent_name,
            definition=ExternalAgentDefinition(otel_agent_id=otel_agent_id),
            description="External agent for Azure SDK Agent Insights sample recordings.",
            metadata={"agent_insights_recording_fixture": "v1"},
        )
        return _validate_agent_version(created, agent_name, otel_agent_id)

    if len(versions) != 1:
        raise RecordingFixtureError(
            "The recording fixture agent contains an unexpected number of immutable versions."
        )
    return _validate_agent_version(versions[0], agent_name, otel_agent_id)


def emit_fixture_traces(
    connection_string: str,
    agent: FixtureAgent,
    defect_trace_count: int,
    control_trace_count: int,
    *,
    exporter_factory: Callable[[str], Any] | None = None,
    uuid_factory: Callable[[], str] = lambda: uuid.uuid4().hex,
    now: Callable[[], datetime] = lambda: datetime.now(UTC),
) -> TraceBatch:
    """Emit fictional destructive-tool defects and healthy control traces."""
    if defect_trace_count <= 0:
        raise ValueError("defect_trace_count must be positive.")
    if control_trace_count < 0:
        raise ValueError("control_trace_count must not be negative.")

    marker = f"agent-insights-recording-{uuid_factory()}"
    provider = TracerProvider(
        resource=Resource.create(
            {
                "service.name": "azure-sdk-agent-insights-recording-fixture",
                "service.instance.id": marker,
            }
        )
    )
    exporter = (
        exporter_factory(connection_string)
        if exporter_factory is not None
        else AzureMonitorTraceExporter.from_connection_string(
            connection_string,
            tracer_provider=provider,
        )
    )
    provider.add_span_processor(BatchSpanProcessor(exporter))
    tracer = provider.get_tracer(__name__)
    trace_ids: list[str] = []
    window_start = now() - timedelta(seconds=30)
    try:
        for index in range(defect_trace_count + control_trace_count):
            trace_ids.append(
                _emit_conversation(
                    tracer,
                    agent,
                    marker,
                    index,
                    is_defect=index < defect_trace_count,
                    uuid_factory=uuid_factory,
                )
            )

        if not provider.force_flush(timeout_millis=30_000):
            raise RecordingFixtureError("The OpenTelemetry spans could not be flushed.")
    finally:
        provider.shutdown()

    return TraceBatch(
        marker=marker,
        trace_ids=tuple(trace_ids),
        window_start=window_start,
        window_end=now() + timedelta(seconds=30),
    )


def wait_for_trace_ingestion(
    logs_client: _LogsClient,
    application_insights_resource_id: str,
    otel_agent_id: str,
    batch: TraceBatch,
    *,
    timeout_seconds: float,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
) -> None:
    """Wait until Application Insights exposes every emitted root trace."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive.")

    query = _build_ingestion_query(batch.marker, otel_agent_id)
    expected_trace_ids = set(batch.trace_ids)
    deadline = monotonic() + timeout_seconds
    attempt = 0
    while True:
        attempt += 1
        try:
            response = logs_client.query_resource(
                application_insights_resource_id,
                query,
                timespan=(batch.window_start, batch.window_end),
                server_timeout=60,
            )
        except HttpResponseError as error:
            status_code = getattr(error, "status_code", None)
            if status_code not in (403, 408, 429) and not (
                isinstance(status_code, int) and status_code >= 500
            ):
                raise RecordingFixtureError(
                    "Application Insights rejected the recording-fixture query."
                ) from error
        except (ServiceRequestError, ServiceResponseError):
            pass
        else:
            if response.status == LogsQueryStatus.SUCCESS:
                observed_trace_ids = _extract_trace_ids(response.tables)
                print(
                    f"Ingestion check {attempt}: found "
                    f"{len(expected_trace_ids.intersection(observed_trace_ids))} of "
                    f"{len(expected_trace_ids)} expected traces."
                )
                if expected_trace_ids.issubset(observed_trace_ids):
                    return

        remaining = deadline - monotonic()
        if remaining <= 0:
            break
        sleep(min(10.0, remaining))

    raise RecordingFixtureError(
        "Application Insights did not expose all recording-fixture traces before the timeout."
    )


def _wait_for_foundry_access(
    project: _ProjectClient,
    agent_name: str,
    otel_agent_id: str,
    *,
    timeout_seconds: float,
    sleep: Callable[[float], None],
    monotonic: Callable[[], float],
) -> tuple[FixtureAgent, str]:
    deadline = monotonic() + timeout_seconds
    while True:
        try:
            agent = reconcile_external_agent(project.agents, agent_name, otel_agent_id)
            connection_string = str(
                project.telemetry.get_application_insights_connection_string() or ""
            ).strip()
            if not connection_string:
                raise RecordingFixtureError(
                    "The Foundry project returned no Application Insights connection string."
                )
            return agent, connection_string
        except HttpResponseError as error:
            status_code = getattr(error, "status_code", None)
            if status_code not in (401, 403, 404, 409):
                raise
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise RecordingFixtureError(
                    "Foundry access did not become available before the role-propagation timeout."
                ) from error
            sleep(min(10.0, remaining))


def _validate_agent_version(
    value: Any, agent_name: str, otel_agent_id: str
) -> FixtureAgent:
    version = str(getattr(value, "version", "") or "").strip()
    definition = getattr(value, "definition", None)
    kind = _wire_value(getattr(definition, "kind", "")).casefold()
    resolved_otel_agent_id = str(getattr(definition, "otel_agent_id", "") or "").strip()
    if not version or kind != "external" or resolved_otel_agent_id != otel_agent_id:
        raise RecordingFixtureError(
            "The recording fixture agent does not match the expected external-agent definition."
        )
    return FixtureAgent(name=agent_name, version=version, otel_agent_id=otel_agent_id)


def _emit_conversation(
    tracer: Any,
    agent: FixtureAgent,
    marker: str,
    index: int,
    *,
    is_defect: bool,
    uuid_factory: Callable[[], str],
) -> str:
    conversation_id = f"recording-conversation-{uuid_factory()}"
    alias = f"SYNTH-WORKSPACE-{index}"
    with tracer.start_as_current_span(
        f"invoke_agent {agent.name}",
        kind=SpanKind.INTERNAL,
    ) as root_span:
        trace_id = f"{root_span.get_span_context().trace_id:032x}"
        _set_agent_attributes(root_span, agent, conversation_id, marker, "invoke_agent")
        with tracer.start_as_current_span(
            "chat recording-fixture",
            kind=SpanKind.INTERNAL,
        ) as chat_span:
            _set_agent_attributes(chat_span, agent, conversation_id, marker, "chat")
            chat_span.set_attribute(
                "gen_ai.request.model", "external-recording-fixture"
            )
            chat_span.set_attribute("gen_ai.usage.input_tokens", 24)
            chat_span.set_attribute("gen_ai.usage.output_tokens", 16)
            chat_span.set_attribute(
                "gen_ai.input.messages",
                _messages(
                    "user",
                    (
                        f"Return the status of fictional workspace {alias}. "
                        "Do not delete it or call any destructive tool. "
                        "No approval has been granted."
                    ),
                ),
            )
            chat_span.set_attribute("gen_ai.tool.definitions", _tool_definitions())
            if is_defect:
                with tracer.start_as_current_span(
                    "execute_tool delete_test_workspace",
                    kind=SpanKind.INTERNAL,
                ) as tool_span:
                    _set_agent_attributes(
                        tool_span,
                        agent,
                        conversation_id,
                        marker,
                        "execute_tool",
                    )
                    tool_span.set_attribute("gen_ai.tool.name", "delete_test_workspace")
                    tool_span.set_attribute("gen_ai.tool.type", "function")
                    tool_span.set_attribute(
                        "gen_ai.tool.call.id", f"call-delete-{index}"
                    )
                    tool_span.set_attribute(
                        "gen_ai.tool.call.arguments",
                        json.dumps(
                            {"workspace_alias": alias, "approval_id": ""},
                            separators=(",", ":"),
                        ),
                    )
                    tool_span.set_attribute(
                        "gen_ai.tool.call.result",
                        json.dumps(
                            {"workspace_alias": alias, "deleted": True},
                            separators=(",", ":"),
                        ),
                    )
                output = f"Fictional workspace {alias} is active. No changes were made."
            else:
                output = f"Fictional workspace {alias} is active."
            chat_span.set_attribute(
                "gen_ai.output.messages", _messages("assistant", output)
            )
            chat_span.set_attribute("gen_ai.response.finish_reasons", '["stop"]')
    return trace_id


def _set_agent_attributes(
    span: Any,
    agent: FixtureAgent,
    conversation_id: str,
    marker: str,
    operation_name: str,
) -> None:
    span.set_attribute("gen_ai.operation.name", operation_name)
    span.set_attribute("gen_ai.agent.id", agent.otel_agent_id)
    span.set_attribute("gen_ai.agent.name", agent.name)
    span.set_attribute("gen_ai.agent.version", agent.version)
    span.set_attribute("gen_ai.conversation.id", conversation_id)
    span.set_attribute("test.agent_insights.fixture_id", marker)


def _messages(role: str, content: str) -> str:
    return json.dumps(
        [{"role": role, "parts": [{"type": "text", "content": content}]}],
        separators=(",", ":"),
    )


def _tool_definitions() -> str:
    return json.dumps(
        [
            {
                "type": "function",
                "name": "delete_test_workspace",
                "description": (
                    "Delete a fictional test workspace only when the user explicitly requests it "
                    "and supplies an approval ID."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workspace_alias": {"type": "string"},
                        "approval_id": {
                            "type": "string",
                            "pattern": "^APPROVAL-[0-9]{6}$",
                        },
                    },
                    "required": ["workspace_alias", "approval_id"],
                    "additionalProperties": False,
                },
            }
        ],
        separators=(",", ":"),
    )


def _build_ingestion_query(marker: str, otel_agent_id: str) -> str:
    return f"""
union isfuzzy=true requests, dependencies
| extend operation_name = tostring(customDimensions["gen_ai.operation.name"])
| extend fixture_id = tostring(customDimensions["test.agent_insights.fixture_id"])
| extend agent_id = tostring(customDimensions["gen_ai.agent.id"])
| where operation_name == "invoke_agent"
| where fixture_id == '{_escape_kql_string(marker)}'
| where agent_id == '{_escape_kql_string(otel_agent_id)}'
| distinct trace_id = tostring(operation_Id)
""".strip()


def _extract_trace_ids(tables: list[Any]) -> set[str]:
    trace_ids: set[str] = set()
    for table in tables:
        columns = [
            str(getattr(column, "name", column) or "") for column in table.columns
        ]
        if "trace_id" not in columns:
            continue
        trace_id_index = columns.index("trace_id")
        for row in table.rows:
            value = str(row[trace_id_index] or "").strip()
            if value:
                trace_ids.add(value)
    return trace_ids


def _escape_kql_string(value: str) -> str:
    return value.replace("\\", "\\\\").replace("'", "''")


def _wire_value(value: Any) -> str:
    return str(getattr(value, "value", value) or "").strip()


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RecordingFixtureError(
            f"Required environment variable '{name}' is not set."
        )
    return value


def main() -> None:
    """Provision the recording fixture from environment variables."""
    settings = FixtureSettings.from_environment()
    agent, batch = provision_recording_fixture(settings)
    print(f"Reconciled external agent version {agent.version}.")
    print(
        f"Exported and verified {len(batch.trace_ids)} Agent Insights fixture traces."
    )


if __name__ == "__main__":
    main()
