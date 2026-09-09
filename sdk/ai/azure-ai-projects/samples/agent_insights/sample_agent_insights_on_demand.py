# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an Agent Insights monitor, run
    on-demand trace analysis, inspect run statistics, list generated insights,
    resolve an insight, and delete the monitor using the
    synchronous AIProjectClient.

    Agent Insights is a preview feature. In the Python SDK, you access these
    operations through `project_client.beta.agent_insight_monitors`.

    Use a disposable test agent. The service allows one monitor per agent, so
    this sample deletes its existing monitor before starting and its new monitor
    when finished. Deletion also removes the monitor's runs, insights, and state.

    The project must have a connected Application Insights resource, and the
    project's managed identity must have permission to query it. The selected
    agent must have ingested traces from the last three hours. For an external
    agent, the emitted OpenTelemetry agent ID must match its registered ID.
    This sample does not create traces. Without recent traces that show an
    issue, there may be no insights to resolve.
    Tracing setup:
    https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side?tabs=python

    Run only one Agent Insights sample at a time for a given test agent.

USAGE:
    python sample_agent_insights_on_demand.py

    Before running the sample:

    pip install "azure-ai-projects>=2.7.0" python-dotenv

    Version 2.7.0 contains the required run-poller fixes. Until it is published,
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

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentInsightMonitorCreate,
    AgentInsightMonitorUpdate,
    AgentInsightRunCreate,
    AgentInsightStatus,
    AgentInsightUpdate,
    JobStatus,
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
        for existing_monitor in monitor_operations.list(agent_name=agent_name):
            _delete_monitor(monitor_operations, existing_monitor.id, "Existing")

        # Keep scheduling disabled because this sample starts one explicit run.
        monitor = monitor_operations.create(
            AgentInsightMonitorCreate(
                agent_name=agent_name,
                model_deployment_name=model_deployment_name,
                enabled=False,
            )
        )
        try:
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
            _delete_monitor(monitor_operations, monitor.id)


def _delete_monitor(operations: BetaAgentInsightMonitorsOperations, monitor_id: str, label: str = "") -> None:
    monitor_label = f"{label} monitor" if label else "Monitor"
    # Disabling stops future scheduling, but a run may already have started.
    operations.update(monitor_id, AgentInsightMonitorUpdate(enabled=False))

    active_statuses = {JobStatus.QUEUED, JobStatus.IN_PROGRESS}
    for attempt in range(30):
        active_runs = [run for run in operations.list_runs(monitor_id, limit=20) if run.status in active_statuses]
        try:
            for run in active_runs:
                operations.cancel_run(monitor_id, run.id)

            if not active_runs:
                operations.delete(monitor_id)
                print(f"Deleted {monitor_label.lower()} `{monitor_id}`.")
                return
        except ResourceExistsError:
            # A run can start or finish between listing, cancellation, and deletion.
            if attempt == 29:
                raise
            print(f"Monitor `{monitor_id}` changed during cleanup; retrying.")

        if attempt < 29:
            time.sleep(2)
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its active runs.")


if __name__ == "__main__":
    main()
