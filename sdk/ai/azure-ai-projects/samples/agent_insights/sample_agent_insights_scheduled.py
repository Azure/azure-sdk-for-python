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
    more than once, it reuses an existing monitor for `FOUNDRY_AGENT_NAME`.

    The sample leaves the monitor enabled so that scheduled analysis can run.
    Delete or disable the monitor when you no longer need scheduled analysis.
    Deleting a monitor also deletes its runs, insights, and state.

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

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentInsightMonitorCreate, AgentInsightMonitorUpdate


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
        if existing_monitors:
            monitor_id = existing_monitors[0].id
            print(f"Using existing monitor `{monitor_id}` for agent `{agent_name}`.")
        else:
            created_monitor = monitor_operations.create(
                AgentInsightMonitorCreate(
                    agent_name=agent_name,
                    model_deployment_name=model_deployment_name,
                    enabled=False,
                )
            )
            monitor_id = created_monitor.id
            print(f"Created disabled monitor `{monitor_id}` for agent `{created_monitor.agent_name}`.")

        # Set the analysis frequency and enable recurring runs in one update.
        monitor_operations.update(
            monitor_id,
            AgentInsightMonitorUpdate(
                enabled=True,
                run_interval_hours=ANALYSIS_INTERVAL_HOURS,
                model_deployment_name=model_deployment_name,
            ),
        )

        scheduled_monitor = monitor_operations.get(monitor_id)
        print(f"Scheduled monitor enabled: {scheduled_monitor.enabled}")
        print(f"Run interval hours: {scheduled_monitor.run_interval_hours}")
        print(f"Next scheduled run: {scheduled_monitor.next_scheduled_run_at}")
        print("The scheduled monitor remains enabled.")


if __name__ == "__main__":
    main()
