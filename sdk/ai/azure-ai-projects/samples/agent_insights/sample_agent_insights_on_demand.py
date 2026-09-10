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

    The agent must not already have a monitor.

    The project must have a connected Application Insights resource, and the
    project's managed identity must have permission to query it.

USAGE:
    python sample_agent_insights_on_demand.py

    Before running the sample:

    pip install "azure-ai-projects>=2.6.1" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Your Microsoft Foundry project endpoint.
    2) FOUNDRY_AGENT_NAME - The name of an existing agent to monitor.
    3) FOUNDRY_MODEL_NAME - The model deployment name for trace analysis.
"""

import os
import uuid

from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentInsightMonitorCreate,
    AgentInsightRunCreate,
    AgentInsightStatus,
    AgentInsightUpdate,
)


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

        monitor_operations.delete(monitor.id)
        print(f"Deleted monitor `{monitor.id}`.")


if __name__ == "__main__":
    main()
