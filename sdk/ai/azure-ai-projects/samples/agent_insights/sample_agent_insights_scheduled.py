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

    The service supports one monitor per agent. To make this sample safe to run
    more than once, it deletes any existing monitor for `FOUNDRY_AGENT_NAME`
    before it creates a monitor.

    The sample disables and deletes the scheduled monitor during cleanup. If
    enabling the monitor starts a run, cleanup cancels that run instead of
    waiting for analysis to finish. Deleting a monitor also deletes its runs,
    insights, and state. Use a test agent that does not have Agent Insights data
    that you need to keep.

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

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentInsightMonitorCreate, AgentInsightMonitorUpdate
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
        existing_monitors = list(monitor_operations.list(agent_name=agent_name))
        for existing_monitor in existing_monitors:
            _delete_monitor(monitor_operations, existing_monitor.id, "Existing")

        monitor = None
        try:
            monitor = monitor_operations.create(
                AgentInsightMonitorCreate(
                    agent_name=agent_name,
                    model_deployment_name=model_deployment_name,
                    enabled=False,
                )
            )
            print(f"Created disabled monitor `{monitor.id}` for agent `{monitor.agent_name}`.")

            # Set the analysis frequency and enable recurring runs in one update.
            monitor_operations.update(
                monitor.id,
                AgentInsightMonitorUpdate(
                    enabled=True,
                    run_interval_hours=ANALYSIS_INTERVAL_HOURS,
                    model_deployment_name=model_deployment_name,
                ),
            )

            scheduled_monitor = monitor_operations.get(monitor.id)
            next_run = scheduled_monitor.next_scheduled_run_at
            if next_run is None:
                raise RuntimeError("The enabled monitor did not return its next scheduled run time.")
            print(f"Scheduled monitor enabled: {scheduled_monitor.enabled}")
            print(f"Run interval hours: {scheduled_monitor.run_interval_hours}")
            print(f"Next scheduled run: {next_run}")
        finally:
            if monitor is not None:
                _delete_monitor(monitor_operations, monitor.id, "Scheduled")


def _delete_monitor(operations: BetaAgentInsightMonitorsOperations, monitor_id: str, label: str) -> None:
    # Disabling stops future scheduling, but a run may already have started.
    try:
        operations.update(monitor_id, AgentInsightMonitorUpdate(enabled=False))
    except ResourceNotFoundError:
        print(f"{label} monitor `{monitor_id}` was already deleted.")
        return

    cancellation_requested: set[str] = set()
    active_statuses = {"queued", "in_progress"}
    for attempt in range(30):
        active_runs = [
            run
            for run in operations.list_runs(monitor_id, limit=20)
            if str(getattr(run.status, "value", run.status)).lower() in active_statuses
        ]
        for run in active_runs:
            if run.id in cancellation_requested:
                continue
            try:
                operations.cancel_run(monitor_id, run.id)
            except ResourceExistsError:
                current_run = operations.get_run(monitor_id, run.id)
                if str(getattr(current_run.status, "value", current_run.status)).lower() in active_statuses:
                    raise
            cancellation_requested.add(run.id)
            print(f"Requested cancellation of run `{run.id}`.")

        if not active_runs:
            try:
                operations.delete(monitor_id)
                print(f"Deleted {label.lower()} monitor `{monitor_id}`.")
                return
            except ResourceNotFoundError:
                print(f"{label} monitor `{monitor_id}` was already deleted.")
                return
            except ResourceExistsError:
                # A previously dispatched run can appear after the list request.
                print(f"Monitor `{monitor_id}` still has an active run; retrying cleanup.")

        if attempt < 29:
            time.sleep(2)
    raise TimeoutError(f"Monitor `{monitor_id}` could not be deleted after stopping its scheduled runs.")


if __name__ == "__main__":
    main()
