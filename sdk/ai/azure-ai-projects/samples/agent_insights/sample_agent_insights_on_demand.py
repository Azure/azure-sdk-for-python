# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an Agent Insights monitor, run
    on-demand trace analysis, inspect run statistics, list generated insights,
    update an insight's lifecycle status, and delete the monitor using the
    synchronous AIProjectClient.

    Agent Insights is a preview feature. In the Python SDK, you access these
    operations through `project_client.beta.agent_insight_monitors`.

    The service supports one monitor per agent. To make this sample safe to run
    more than once, it deletes any existing monitor for `FOUNDRY_AGENT_NAME`
    before it creates a monitor. It also deletes the new monitor during cleanup.

    Cleanup disables scheduling and cancels active runs before deleting a
    monitor. It waits for cancellation for up to 30 checks, two seconds apart,
    and raises an error if the monitor still cannot be deleted.

    Deleting a monitor also deletes its runs, insights, and state. Use a test
    agent that does not have Agent Insights data that you need to keep.

    The project must have a connected Application Insights resource, and the
    project's managed identity must have permission to query it. The selected
    agent must have ingested traces from the last three hours. For an external
    agent, the emitted OpenTelemetry agent ID must match its registered ID.
    This sample does not create traces. Without recent traces that show an
    issue, there may be no insights to resolve and reopen.
    Tracing setup:
    https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side?tabs=python

    Run only one Agent Insights sample at a time for a given test agent.

USAGE:
    python sample_agent_insights_on_demand.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.1" python-dotenv

    Version 2.6.1 contains the required run-poller fixes. Until it is published,
    install this package from the repository root instead:

    pip install -e sdk/ai/azure-ai-projects python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found on the Overview
       page of your Microsoft Foundry project.
    2) FOUNDRY_AGENT_NAME - The name of an existing test agent to monitor.
    3) FOUNDRY_MODEL_NAME - The deployment name of the AI model that Agent Insights
       uses to analyze traces.
"""

import os
import time
import uuid

from dotenv import load_dotenv

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentInsightMonitorCreate,
    AgentInsightMonitorUpdate,
    AgentInsightRunCreate,
    AgentInsightStatus,
    AgentInsightUpdate,
)
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations


def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    agent_name = os.environ["FOUNDRY_AGENT_NAME"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    ):
        monitor_operations = project_client.beta.agent_insight_monitors

        # Agent Insights supports only one monitor for each agent.
        existing_monitors = list(monitor_operations.list(agent_name=agent_name))
        for existing_monitor in existing_monitors:
            _delete_monitor(monitor_operations, existing_monitor.id, "Existing")

        monitor = None
        try:
            # Keep scheduling disabled because this sample starts one explicit run.
            monitor = monitor_operations.create(
                AgentInsightMonitorCreate(
                    agent_name=agent_name,
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
            run_status = getattr(completed_run.status, "value", completed_run.status)
            print(f"Run status: {run_status}")
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
                severity = getattr(insight.severity, "value", insight.severity)
                status = getattr(insight.status, "value", insight.status)
                proposed_fix = insight.details.recommended_actions.proposed_fix if insight.details is not None else None
                fix_kind = (
                    getattr(proposed_fix.kind, "value", proposed_fix.kind)
                    if proposed_fix is not None
                    else "not returned"
                )
                print(
                    f"Insight `{insight.id}`: title=`{insight.title}`, severity={severity}, "
                    f"status={status}, traces={insight.trace_count}, fix kind={fix_kind}."
                )
                if proposed_fix is not None:
                    print(f"Recommended action: {proposed_fix.text}")

            if insights:
                selected_insight = monitor_operations.get_insight(
                    monitor.id,
                    insights[0].id,
                    include_details=True,
                )
                selected_status = getattr(selected_insight.status, "value", selected_insight.status)
                print(f"Retrieved insight `{selected_insight.id}` with status {selected_status}.")

                # Status changes track review decisions; they do not apply the proposed fix.
                monitor_operations.update_insight(
                    monitor.id,
                    selected_insight.id,
                    AgentInsightUpdate(status=AgentInsightStatus.RESOLVED),
                )
                resolved_insight = monitor_operations.get_insight(
                    monitor.id,
                    selected_insight.id,
                )
                resolved_status = getattr(resolved_insight.status, "value", resolved_insight.status)
                print(f"Insight status after update: {resolved_status}")

                monitor_operations.update_insight(
                    monitor.id,
                    selected_insight.id,
                    AgentInsightUpdate(status=AgentInsightStatus.ACTIVE),
                )
                reopened_insight = monitor_operations.get_insight(
                    monitor.id,
                    selected_insight.id,
                )
                reopened_status = getattr(reopened_insight.status, "value", reopened_insight.status)
                print(f"Insight status after reopening: {reopened_status}")
            else:
                print("No insights were available to demonstrate lifecycle updates.")
        finally:
            if monitor is not None:
                _delete_monitor(monitor_operations, monitor.id)


def _delete_monitor(operations: BetaAgentInsightMonitorsOperations, monitor_id: str, label: str = "") -> None:
    monitor_label = f"{label} monitor" if label else "Monitor"
    # Disabling stops future scheduling, but a run may already have started.
    try:
        operations.update(monitor_id, AgentInsightMonitorUpdate(enabled=False))
    except ResourceNotFoundError:
        print(f"{monitor_label} `{monitor_id}` was already deleted.")
        return

    cancellation_requested: set[str] = set()
    active_statuses = {"queued", "in_progress"}
    for attempt in range(30):
        try:
            active_runs = [
                run
                for run in operations.list_runs(monitor_id, limit=20)
                if str(getattr(run.status, "value", run.status)).lower() in active_statuses
            ]
        except ResourceNotFoundError:
            # Confirm the monitor disappeared, rather than hiding a missing run endpoint.
            try:
                operations.get(monitor_id)
            except ResourceNotFoundError:
                print(f"{monitor_label} `{monitor_id}` was already deleted.")
                return
            raise
        for run in active_runs:
            if run.id in cancellation_requested:
                continue
            try:
                operations.cancel_run(monitor_id, run.id)
            except ResourceNotFoundError:
                # Re-list before deciding whether the run or monitor has disappeared.
                continue
            except ResourceExistsError:
                try:
                    current_run = operations.get_run(monitor_id, run.id)
                except ResourceNotFoundError:
                    continue
                if str(getattr(current_run.status, "value", current_run.status)).lower() in active_statuses:
                    raise
            cancellation_requested.add(run.id)
            print(f"Requested cancellation of run `{run.id}`.")

        if not active_runs:
            try:
                operations.delete(monitor_id)
                print(f"Deleted {monitor_label.lower()} `{monitor_id}`.")
                return
            except ResourceNotFoundError:
                print(f"{monitor_label} `{monitor_id}` was already deleted.")
                return
            except ResourceExistsError:
                # A previously dispatched run can appear after the list request.
                print(f"Monitor `{monitor_id}` still has an active run; retrying cleanup.")

        if attempt < 29:
            time.sleep(2)
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its active runs.")


if __name__ == "__main__":
    main()
