# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create a scheduled Agent Insights monitor
    using the synchronous AIProjectClient. The monitor is enabled with a
    six-hour run interval, and the sample retrieves the next scheduled run time.
    It does not wait for a scheduled run or fetch the run's results.

    Agent Insights is a preview feature. In the Python SDK, you access these
    operations through `project_client.beta.agent_insight_monitors`.

    Use a disposable test agent. The service allows one monitor per agent, so
    this sample deletes its existing monitor before starting. At the end, it
    disables scheduling, cancels active runs, and deletes the new monitor.
    Deletion also removes the monitor's runs, insights, and state.

    The project must have a connected Application Insights resource, and its
    managed identity must have permission to query the agent's traces. This
    sample configures scheduling; it does not create traces.
    Tracing setup:
    https://learn.microsoft.com/azure/foundry/observability/how-to/trace-agent-client-side?tabs=python

    Run only one Agent Insights sample at a time for a given test agent.

USAGE:
    python sample_agent_insights_scheduled.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found on the Overview
       page of your Microsoft Foundry project.
    2) FOUNDRY_AGENT_NAME - The name of an existing test agent to monitor.
    3) FOUNDRY_MODEL_NAME - The deployment name of the AI model that Agent Insights
       uses to analyze traces.
"""

import os
import time

from dotenv import load_dotenv

from azure.core.exceptions import ResourceExistsError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentInsightMonitorCreate, AgentInsightMonitorUpdate, JobStatus
from azure.ai.projects.operations import BetaAgentInsightMonitorsOperations


ANALYSIS_INTERVAL_HOURS = 6


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

        monitor = monitor_operations.create(
            AgentInsightMonitorCreate(
                agent_name=agent_name,
                model_deployment_name=model_deployment_name,
                enabled=False,
            )
        )
        try:
            print(f"Created disabled monitor `{monitor.id}` for agent `{monitor.agent_name}`.")

            # Set the analysis frequency and enable recurring runs in one update.
            scheduled_monitor = monitor_operations.update(
                monitor.id,
                AgentInsightMonitorUpdate(
                    enabled=True,
                    run_interval_hours=ANALYSIS_INTERVAL_HOURS,
                ),
            )

            print(f"Scheduled monitor enabled: {scheduled_monitor.enabled}")
            print(f"Run interval hours: {scheduled_monitor.run_interval_hours}")
            print(f"Next scheduled run: {scheduled_monitor.next_scheduled_run_at}")
        finally:
            _delete_monitor(monitor_operations, monitor.id, "Scheduled")


def _delete_monitor(operations: BetaAgentInsightMonitorsOperations, monitor_id: str, label: str) -> None:
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
                print(f"Deleted {label.lower()} monitor `{monitor_id}`.")
                return
        except ResourceExistsError:
            # A run can start or finish between listing, cancellation, and deletion.
            if attempt == 29:
                raise
            print(f"Monitor `{monitor_id}` changed during cleanup; retrying.")

        if attempt < 29:
            time.sleep(2)
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its scheduled runs.")


if __name__ == "__main__":
    main()
