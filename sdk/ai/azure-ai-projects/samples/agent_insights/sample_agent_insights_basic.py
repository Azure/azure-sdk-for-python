# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create, retrieve, list, and delete an
    Agent Insights monitor using the synchronous AIProjectClient.

    Agent Insights is a preview feature. In the Python SDK, you access these
    operations through `project_client.beta.agent_insight_monitors`.

    The service supports one monitor per agent. To make this sample safe to run
    more than once, it deletes any existing monitor for `FOUNDRY_AGENT_NAME`
    before it creates a monitor. It also deletes the new monitor during cleanup.

    Deleting a monitor also deletes its runs, insights, and state. Use a test
    agent that does not have Agent Insights data that you need to keep.

USAGE:
    python sample_agent_insights_basic.py

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

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentInsightMonitorCreate


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

        existing_monitors = list(monitor_operations.list(agent_name=agent_name))
        for existing_monitor in existing_monitors:
            try:
                monitor_operations.delete(existing_monitor.id)
                print(f"Deleted existing monitor `{existing_monitor.id}` for agent `{agent_name}`.")
            except ResourceNotFoundError:
                print(f"Existing monitor `{existing_monitor.id}` was already deleted.")

        monitor = None
        try:
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

            retrieved_monitor = monitor_operations.get(monitor.id)
            print(
                f"Retrieved monitor `{retrieved_monitor.id}` using model "
                f"`{retrieved_monitor.model_deployment_name}`."
            )

            monitors = list(monitor_operations.list(agent_name=agent_name))
            print(f"Found {len(monitors)} monitor(s) for agent `{agent_name}`.")
        finally:
            if monitor is not None:
                try:
                    monitor_operations.delete(monitor.id)
                    print(f"Deleted monitor `{monitor.id}`.")
                except ResourceNotFoundError:
                    print(f"Monitor `{monitor.id}` was already deleted.")


if __name__ == "__main__":
    main()
