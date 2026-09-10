# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample uses the synchronous AIProjectClient to create an Agent Insights
    monitor, analyze traces from the last three hours on demand, read run results,
    and resolve one insight.

    Agent Insights is a preview feature. In the Python SDK, you access these
    operations through `project_client.beta.agent_insight_monitors`.

    This sample registers a temporary external agent and emits fictional traces;
    it does not execute tools or call a model to produce those traces. It waits
    for ingestion, then deletes its monitor and agent in finally. Ingested
    telemetry remains in Application Insights under its normal retention policy.

    Use an existing project, connected Application Insights resource, and suitable
    analysis-model deployment. Your identity needs agent/monitor management and
    telemetry query access. The project identity needs model and trace-content access.

USAGE:
    python sample_agent_insights_on_demand.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.1" azure-identity python-dotenv azure-monitor-opentelemetry azure-monitor-query opentelemetry-sdk

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Your Microsoft Foundry project endpoint.
    2) AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID - The connected Application Insights resource ID.
    3) FOUNDRY_MODEL_NAME - The model deployment name for trace analysis.
"""

import json
import os
import time
import uuid
from datetime import timedelta

from dotenv import load_dotenv
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON
from opentelemetry.trace import SpanKind

from azure.identity import DefaultAzureCredential
from azure.core.exceptions import ResourceExistsError
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentInsightMonitorCreate,
    AgentInsightMonitorUpdate,
    AgentInsightRunCreate,
    AgentInsightStatus,
    AgentInsightUpdate,
    AgentVersionDetails,
    ExternalAgentDefinition,
    JobStatus,
)
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations


def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    application_insights_resource_id = os.environ["AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        LogsQueryClient(credential) as logs_client,
    ):
        monitor_operations = project_client.beta.agent_insight_monitors
        agent = None
        monitor = None
        try:
            agent = _create_agent(project_client)
            print(f"Created external agent `{agent.name}` (version={agent.version}).")
            expected_counts = _seed_traces(project_client, agent)
            _wait_for_ingestion(logs_client, application_insights_resource_id, agent.name, expected_counts)

            # Keep scheduling disabled because this sample starts one explicit run.
            monitor = monitor_operations.create(
                AgentInsightMonitorCreate(
                    agent_name=agent.name,
                    model_deployment_name=model_deployment_name,
                    enabled=False,
                )
            )
            print(
                f"Created monitor `{monitor.id}` for agent `{monitor.agent_name}` "
                f"(enabled={monitor.enabled}, run interval={monitor.run_interval_hours} hours)."
            )

            poller = monitor_operations.begin_create_run(
                monitor.id,
                AgentInsightRunCreate(lookback_hours=3),
                operation_id=str(uuid.uuid4()),
            )
            run_id = poller.details["run_id"]
            print(f"Started on-demand run `{run_id}`.")

            run_result = poller.result()
            completed_run = monitor_operations.get_run(monitor.id, run_id)
            print(f"Run status: {completed_run.status}")
            print(f"Traces in window: {run_result.traces_in_window}")
            print(f"Traces analyzed: {run_result.traces_analyzed}")
            print(f"Insights created: {run_result.insights_created}")
            print(f"Insights updated: {run_result.insights_updated}")
            print(f"Insights reopened: {run_result.insights_reopened}")
            print(
                "Token usage: "
                f"input={run_result.token_usage.input_tokens}, "
                f"output={run_result.token_usage.output_tokens}, "
                f"total={run_result.token_usage.total_tokens}"
            )

            runs = list(monitor_operations.list_runs(monitor.id, limit=5))
            print(f"Listed runs: {len(runs)}")

            insights = list(monitor_operations.list_insights(monitor.id, include_details=True))
            print(f"Listed insights: {len(insights)}")
            for insight in insights:
                print(
                    f"Insight `{insight.id}`: title=`{insight.title}`, severity={insight.severity}, "
                    f"status={insight.status}, traces={insight.trace_count}."
                )
                if insight.details:
                    print(f"Recommended action: {insight.details.recommended_actions.proposed_fix.text}")

            if insights:
                # Status changes track review decisions; they do not apply the proposed fix.
                resolved_insight = monitor_operations.update_insight(
                    monitor.id,
                    insights[0].id,
                    AgentInsightUpdate(status=AgentInsightStatus.RESOLVED),
                )
                print(f"Insight status after update: {resolved_insight.status}")
            else:
                print("No insights were available to resolve.")
        finally:
            _cleanup(project_client, agent, monitor.id if monitor is not None else None)


def _create_agent(project_client: AIProjectClient) -> AgentVersionDetails:
    agent_name = f"agent-insights-sample-{uuid.uuid4().hex}"
    return project_client.agents.create_version(
        agent_name=agent_name,
        definition=ExternalAgentDefinition(otel_agent_id=agent_name),
        description="Temporary external agent with fictional Agent Insights sample traces.",
    )


def _cleanup(project_client: AIProjectClient, agent: AgentVersionDetails | None, monitor_id: str | None) -> None:
    # Keep the agent if its monitor cannot be stopped and deleted.
    if monitor_id is not None:
        _delete_monitor(project_client.beta.agent_insight_monitors, monitor_id)
    if agent is not None:
        print(f"Deleting external agent `{agent.name}`; if cleanup fails, remove it manually.")
        project_client.agents.delete(agent.name, force=True)
        print(f"Deleted external agent `{agent.name}`.")


def _seed_traces(project_client: AIProjectClient, agent: AgentVersionDetails) -> tuple[int, int, int, int]:
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
                        _messages(
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
                    chat.set_attribute("gen_ai.output.messages", _messages("assistant", output))
                    chat.set_attribute("gen_ai.response.finish_reasons", '["stop"]')
        if not provider.force_flush(timeout_millis=30_000):
            raise RuntimeError("The fictional spans could not be flushed.")
    finally:
        provider.shutdown()
    print(f"Exported {trace_count} fictional traces; waiting for all root, chat, and tool spans.")
    return trace_count, root_count, chat_count, tool_count


def _messages(role: str, content: str) -> str:
    return json.dumps([{"role": role, "parts": [{"type": "text", "content": content}]}], separators=(",", ":"))


def _wait_for_ingestion(
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


def _delete_monitor(operations: BetaAgentInsightMonitorsOperations, monitor_id: str) -> None:
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
                print(f"Deleted monitor `{monitor_id}`.")
                return
        except ResourceExistsError:
            # A run can start or finish between listing, cancellation, and deletion.
            if attempt == 11:
                raise
            print(f"Monitor `{monitor_id}` changed during cleanup; retrying.")

        if attempt < 11:
            time.sleep(10)
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its runs.")


if __name__ == "__main__":
    main()
