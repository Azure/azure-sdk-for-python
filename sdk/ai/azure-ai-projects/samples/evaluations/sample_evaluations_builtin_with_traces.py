# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to run Azure AI Evaluations
    against agent traces collected in Azure Application Insights. The sample fetches
    trace IDs for a given agent and time range, creates an evaluation group configured
    for trace analysis, and monitors the evaluation run until it completes.

USAGE:
    python sample_evaluations_builtin_with_traces.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity azure-monitor-query python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) APPINSIGHTS_RESOURCE_ID - Required. The Azure Application Insights resource ID that stores agent traces.
       It has the form: /subscriptions/<subscription_id>/resourceGroups/<rg_name>/providers/Microsoft.Insights/components/<resource_name>.
    3) AGENT_ID - Required. The agent identifier emitted by the Azure tracing integration, used to filter traces.
    4) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The Azure OpenAI deployment name to use with the built-in evaluators.
    5) TRACE_LOOKBACK_HOURS - Optional. Number of hours to look back when querying traces and in the evaluation run.
       Defaults to 1.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.ai.projects import AIProjectClient

from pprint import pprint

load_dotenv()


endpoint = os.environ[
    "AZURE_AI_PROJECT_ENDPOINT"
]
appinsights_resource_id = os.environ[
    "APPINSIGHTS_RESOURCE_ID"
]  # Sample : /subscriptions/<subscription_id>/resourceGroups/<rg_name>/providers/Microsoft.Insights/components/<resource_name>
agent_id = os.environ["AGENT_ID"]
model_deployment_name = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
trace_query_hours = int(os.environ.get("TRACE_LOOKBACK_HOURS", "1"))


def _build_evaluator_config(name: str, evaluator_name: str) -> Dict[str, Any]:
    """Create a standard Azure AI evaluator configuration block for trace evaluations."""
    return {
        "type": "azure_ai_evaluator",
        "name": name,
        "evaluator_name": evaluator_name,
        "data_mapping": {
            "query": "{{query}}",
            "response": "{{response}}",
            "tool_definitions": "{{tool_definitions}}",
        },
        "initialization_parameters": {
            "deployment_name": model_deployment_name,
        },
    }


def get_trace_ids(
    appinsight_resource_id: str, tracked_agent_id: str, start_time: datetime, end_time: datetime
) -> List[str]:
    """
    Query Application Insights for trace IDs (operation_Id) based on agent ID and time range.

    Args:
        appinsight_resource_id: The resource ID of the Application Insights instance.
        tracked_agent_id: The agent ID to filter by.
        start_time: Start time for the query.
        end_time: End time for the query.

    Returns:
        List of distinct operation IDs (trace IDs).
    """
    query = f"""
dependencies
| where timestamp between (datetime({start_time.isoformat()}) .. datetime({end_time.isoformat()}))
| extend agent_id = tostring(customDimensions["gen_ai.agent.id"])
| where agent_id == "{tracked_agent_id}"
| distinct operation_Id
"""

    try:
        with DefaultAzureCredential() as credential:
            client = LogsQueryClient(credential)
            response = client.query_resource(
                appinsight_resource_id,
                query=query,
                timespan=None,  # Time range is specified in the query itself.
            )
    except Exception as exc:  # pylint: disable=broad-except
        print(f"Error executing query: {exc}")
        return []

    if response.status == LogsQueryStatus.SUCCESS:
        trace_ids: List[str] = []
        for table in response.tables:
            for row in table.rows:
                trace_ids.append(row[0])
        return trace_ids

    print(f"Query failed with status: {response.status}")
    if response.partial_error:
        print(f"Partial error: {response.partial_error}")
    return []


def main() -> None:
    end_time = datetime.now(tz=timezone.utc)
    start_time = end_time - timedelta(hours=trace_query_hours)

    print("Querying Application Insights for trace identifiers...")
    print(f"Agent ID: {agent_id}")
    print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")

    trace_ids = get_trace_ids(appinsights_resource_id, agent_id, start_time, end_time)

    if not trace_ids:
        print("No trace IDs found for the provided agent and time window.")
        return

    print(f"\nFound {len(trace_ids)} trace IDs:")
    for trace_id in trace_ids:
        print(f"  - {trace_id}")

    with DefaultAzureCredential() as credential:
        with AIProjectClient(
            endpoint=endpoint,
            credential=credential
        ) as project_client:
            client = project_client.get_openai_client()
            data_source_config = {
                "type": "azure_ai_source",
                "scenario": "traces",
            }

            testing_criteria = [
                _build_evaluator_config(
                    name="intent_resolution",
                    evaluator_name="builtin.intent_resolution",
                ),
                _build_evaluator_config(
                    name="task_adherence",
                    evaluator_name="builtin.task_adherence",
                ),
            ]

            print("\nCreating Eval Group")
            eval_object = client.evals.create(
                name="agent_trace_eval_group",
                data_source_config=data_source_config, # type: ignore
                testing_criteria=testing_criteria, # type: ignore
            )
            print("Eval Group created")

            print("\nGet Eval Group by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Eval Group Response:")
            pprint(eval_object_response)

            print("\nCreating Eval Run with trace IDs")
            run_name = f"agent_trace_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            data_source={
                "type": "azure_ai_traces",
                "trace_ids": trace_ids,
                "lookback_hours": trace_query_hours,
            }
            eval_run_object = client.evals.runs.create(
                eval_id=eval_object.id,
                name=run_name,
                metadata={
                    "agent_id": agent_id,
                    "start_time": start_time.isoformat(),
                    "end_time": end_time.isoformat(),
                },
                data_source=data_source # type: ignore
            )
            print("Eval Run created")
            pprint(eval_run_object)

            print("\nMonitoring Eval Run status...")
            while True:
                run = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
                print(f"Status: {run.status}")

                if run.status in {"completed", "failed", "canceled"}:
                    print("\nEval Run finished!")
                    print("Final Eval Run Response:")
                    pprint(run)
                    break

                time.sleep(5)
                print("Waiting for eval run to complete...")

            client.evals.delete(eval_id=eval_object.id)
            print("Evaluation deleted")


if __name__ == "__main__":
    main()
