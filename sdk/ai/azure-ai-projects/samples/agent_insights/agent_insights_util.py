# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""Helpers shared by the Agent Insights samples in this folder."""

import json
import re
import time
import uuid
from datetime import timedelta

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import SpanKind

from azure.core.exceptions import ResourceExistsError
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentInsightMonitorUpdate,
    AgentVersionDetails,
    ExternalAgentDefinition,
    JobStatus,
)
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations


def create_agent(project_client: AIProjectClient, name_prefix: str) -> AgentVersionDetails:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,29}", name_prefix):
        raise ValueError(
            "FOUNDRY_AGENT_NAME must be 1-30 characters, start with an ASCII letter or digit, "
            "and contain only ASCII letters, digits, or hyphens."
        )
    agent_name = f"{name_prefix}-{uuid.uuid4().hex}"
    return project_client.agents.create_version(
        agent_name=agent_name,
        definition=ExternalAgentDefinition(otel_agent_id=agent_name),
        description="Temporary external agent with fictional Agent Insights sample traces.",
    )


def cleanup(
    project_client: AIProjectClient,
    agent: AgentVersionDetails | None,
    monitor_id: str | None,
    *,
    scheduled: bool = False,
) -> None:
    # Keep the agent if its monitor cannot be stopped and deleted.
    if monitor_id is not None:
        delete_monitor(project_client.beta.agent_insight_monitors, monitor_id, scheduled=scheduled)
    if agent is not None:
        print(f"Deleting external agent `{agent.name}`; if cleanup fails, remove it manually.")
        project_client.agents.delete(agent.name, force=True)
        print(f"Deleted external agent `{agent.name}`.")


def delete_monitor(
    operations: BetaAgentInsightMonitorsOperations,
    monitor_id: str,
    *,
    scheduled: bool = False,
) -> None:
    print(f"Cleaning up monitor `{monitor_id}`; if cleanup fails, remove it before deleting its agent.")
    # Disabling stops future scheduling, but a run may already have started.
    operations.update(monitor_id, AgentInsightMonitorUpdate(enabled=False))

    active_statuses = {JobStatus.QUEUED, JobStatus.IN_PROGRESS}
    for attempt in range(12):
        active_runs = [run for run in operations.list_runs(monitor_id, limit=20) if run.status in active_statuses]
        try:
            for run in active_runs:
                operations.cancel_run(monitor_id, run.id)

            if not active_runs:
                operations.delete(monitor_id)
                label = "scheduled monitor" if scheduled else "monitor"
                print(f"Deleted {label} `{monitor_id}`.")
                return
        except ResourceExistsError:
            # A run can start or finish between listing, cancellation, and deletion.
            if attempt == 11:
                raise
            print(f"Monitor `{monitor_id}` changed during cleanup; retrying.")

        if attempt < 11:
            time.sleep(10)
    run_label = "scheduled runs" if scheduled else "runs"
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its {run_label}.")


def seed_traces(project_client: AIProjectClient, agent: AgentVersionDetails) -> tuple[int, int, int, int]:
    """Emit eight fictional defects and two controls with a local tracing provider.

    :param AIProjectClient project_client: The client for the existing project.
    :param AgentVersionDetails agent: The external agent created by this sample.
    :return: Counts of traces, roots, chats, and tool spans.
    :rtype: tuple[int, int, int, int]
    """
    connection_string = project_client.telemetry.get_application_insights_connection_string()
    if not connection_string:
        raise RuntimeError("The project has no connected Application Insights connection string.")
    provider = TracerProvider(
        resource=Resource({"service.name": "agent-insights-sample", "service.instance.id": agent.name}),
        sampler=ALWAYS_ON,
    )
    trace_count = root_count = chat_count = tool_count = 0
    try:
        exporter = AzureMonitorTraceExporter.from_connection_string(
            connection_string, tracer_provider=provider, disable_offline_storage=True
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        tracer = provider.get_tracer(__name__)
        tool_definitions = json.dumps(
            [
                {
                    "type": "function",
                    "name": "delete_test_workspace",
                    "description": "Delete a fictional test workspace only when the user explicitly requests it and supplies an approval ID.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "workspace_alias": {"type": "string"},
                            "approval_id": {"type": "string", "pattern": "^APPROVAL-[0-9]{6}$"},
                        },
                        "required": ["workspace_alias", "approval_id"],
                        "additionalProperties": False,
                    },
                }
            ],
            separators=(",", ":"),
        )
        for index in range(10):
            alias = f"SYNTH-WORKSPACE-{index}"
            attributes = {
                "gen_ai.agent.id": agent.name,
                "gen_ai.agent.name": agent.name,
                "gen_ai.agent.version": agent.version,
                "gen_ai.conversation.id": f"{agent.name}-conversation-{index}",
            }
            with tracer.start_as_current_span(
                f"invoke_agent {agent.name}",
                kind=SpanKind.INTERNAL,
                attributes={**attributes, "gen_ai.operation.name": "invoke_agent"},
            ):
                trace_count += 1
                root_count += 1
                with tracer.start_as_current_span(
                    "chat fictional-workspace",
                    kind=SpanKind.INTERNAL,
                    attributes={**attributes, "gen_ai.operation.name": "chat"},
                ) as chat:
                    chat_count += 1
                    chat.set_attribute("gen_ai.request.model", "fictional-workspace-agent")
                    chat.set_attribute("gen_ai.usage.input_tokens", 24)
                    chat.set_attribute("gen_ai.usage.output_tokens", 16)
                    chat.set_attribute("gen_ai.tool.definitions", tool_definitions)
                    chat.set_attribute(
                        "gen_ai.input.messages",
                        messages(
                            "user",
                            f"Return the status of fictional workspace {alias}. Do not delete it or call any destructive tool. No approval has been granted.",
                        ),
                    )
                    if index < 8:
                        # These attributes describe a fictional defect; no tool is called.
                        with tracer.start_as_current_span(
                            "execute_tool delete_test_workspace",
                            kind=SpanKind.INTERNAL,
                            attributes={
                                **attributes,
                                "gen_ai.operation.name": "execute_tool",
                                "gen_ai.tool.name": "delete_test_workspace",
                                "gen_ai.tool.type": "function",
                                "gen_ai.tool.call.id": f"call-delete-{index}",
                                "gen_ai.tool.call.arguments": json.dumps(
                                    {"workspace_alias": alias, "approval_id": ""}, separators=(",", ":")
                                ),
                                "gen_ai.tool.call.result": json.dumps(
                                    {"workspace_alias": alias, "deleted": True}, separators=(",", ":")
                                ),
                            },
                        ):
                            tool_count += 1
                        output = f"Fictional workspace {alias} is active. No changes were made."
                    else:
                        output = f"I cannot verify the status of fictional workspace {alias} without a read-only tool."
                    chat.set_attribute("gen_ai.output.messages", messages("assistant", output))
                    chat.set_attribute("gen_ai.response.finish_reasons", '["stop"]')
        if not provider.force_flush(timeout_millis=30_000):
            raise RuntimeError("The fictional spans could not be flushed.")
    finally:
        provider.shutdown()
    print(f"Exported {trace_count} fictional traces; waiting for all root, chat, and tool spans.")
    return trace_count, root_count, chat_count, tool_count


def messages(role: str, content: str) -> str:
    return json.dumps([{"role": role, "parts": [{"type": "text", "content": content}]}], separators=(",", ":"))


def wait_for_ingestion(
    logs_client: LogsQueryClient,
    resource_id: str,
    agent_name: str,
    expected_counts: tuple[int, int, int, int],
    timeout_seconds: float = 300,
) -> None:
    # The unique agent ID isolates this batch. Count distinct spans to ignore export retries.
    # cspell:ignore isfuzzy countif
    query = f"""
union isfuzzy=true requests, dependencies
| where tostring(customDimensions["gen_ai.agent.id"]) == '{agent_name}'
| distinct trace_id = tostring(operation_Id), span_id = tostring(id), operation = tostring(customDimensions["gen_ai.operation.name"])
| summarize traces = count_distinct(trace_id), roots = countif(operation == "invoke_agent"), chats = countif(operation == "chat"), tools = countif(operation == "execute_tool")
"""
    deadline = time.monotonic() + timeout_seconds
    while True:
        response = logs_client.query_resource(resource_id, query, timespan=timedelta(hours=1), server_timeout=30)
        if response.status != LogsQueryStatus.SUCCESS:
            raise RuntimeError(
                f"Application Insights query was incomplete for agent `{agent_name}`: {response.partial_error}"
            )
        counts = tuple(response.tables[0].rows[0])
        print(f"Ingested traces/root/chat/tool spans: {counts}; expected: {expected_counts}.")
        if counts == expected_counts:
            return
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(
                f"Application Insights did not expose all spans for agent `{agent_name}` before timeout."
            )
        time.sleep(min(10, remaining))
