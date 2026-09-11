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

    This sample registers a temporary external agent and emits fictional traces;
    it does not execute tools or call a model to produce those traces. It waits
    for ingestion, then deletes its monitor and agent in finally. Ingested
    telemetry remains in Application Insights under its normal retention policy.

    Use an existing project, connected Application Insights resource, and suitable
    analysis-model deployment. Your identity needs agent/monitor management and
    telemetry query access. The project identity needs model and trace-content access.
    Protected trace content also requires Privileged Monitoring Data Reader on
    the connected Application Insights resource for the project identity.

USAGE:
    python sample_agent_insights_scheduled.py

    Before running the sample:

    pip install "azure-ai-projects>=2.7.0" azure-identity python-dotenv azure-monitor-opentelemetry azure-monitor-query opentelemetry-sdk

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Your Microsoft Foundry project endpoint.
    2) APP_INSIGHTS_RESOURCE_ID - The connected Application Insights resource ID.
    3) FOUNDRY_MODEL_NAME - The model deployment name for trace analysis.
    4) FOUNDRY_AGENT_NAME - Optional agent name prefix. Defaults to
       "agent-insights-sample" when unset or empty. A unique suffix is added
       on each run so existing agents and retained traces are not reused.
"""

import os

from dotenv import load_dotenv
from agent_insights_util import cleanup, create_agent, seed_traces, wait_for_ingestion

from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentInsightMonitorCreate, AgentInsightMonitorUpdate


ANALYSIS_INTERVAL_HOURS = 6


def main() -> None:
    load_dotenv()

    endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
    app_insights_resource_id = os.environ["APP_INSIGHTS_RESOURCE_ID"]
    model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
    agent_name = os.environ.get("FOUNDRY_AGENT_NAME") or "agent-insights-sample"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
        LogsQueryClient(credential) as logs_client,
    ):
        monitor_operations = project_client.beta.agent_insight_monitors

        agent = None
        monitor = None
        try:
            agent = create_agent(project_client, agent_name)
            print(f"Created external agent `{agent.name}` (version={agent.version}).")
            expected_counts = seed_traces(project_client, agent)
            wait_for_ingestion(logs_client, app_insights_resource_id, agent.name, expected_counts)

            monitor = monitor_operations.create(
                AgentInsightMonitorCreate(
                    agent_name=agent.name,
                    model_deployment_name=model_deployment_name,
                    enabled=False,
                )
            )
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
            cleanup(project_client, agent, monitor.id if monitor is not None else None, scheduled=True)


if __name__ == "__main__":
    main()
