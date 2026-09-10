# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample uses the synchronous AIProjectClient to configure an Agent
    Insights monitor with a six-hour run interval and read the next scheduled
    run time. It does not wait for scheduled analysis.

    Agent Insights is a preview feature. In the Python SDK, you access these
    operations through `project_client.beta.agent_insight_monitors`.

    The agent must not already have a monitor.

    The project must have a connected Application Insights resource, and the
    project's managed identity must have permission to query it.

USAGE:
    python sample_agent_insights_scheduled.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.1" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Your Microsoft Foundry project endpoint.
    2) FOUNDRY_AGENT_NAME - The name of an existing agent to monitor.
    3) FOUNDRY_MODEL_NAME - The model deployment name for trace analysis.
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
            # Enabling schedules the first occurrence for now, so a run may already be active.
            _delete_monitor(monitor_operations, monitor.id)


def _delete_monitor(operations: BetaAgentInsightMonitorsOperations, monitor_id: str) -> None:
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
                print(f"Deleted scheduled monitor `{monitor_id}`.")
                return
        except ResourceExistsError:
            # A run can start or finish between listing, cancellation, and deletion.
            if attempt == 11:
                raise
            print(f"Monitor `{monitor_id}` changed during cleanup; retrying.")

        if attempt < 11:
            time.sleep(10)
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its scheduled runs.")


if __name__ == "__main__":
    main()
