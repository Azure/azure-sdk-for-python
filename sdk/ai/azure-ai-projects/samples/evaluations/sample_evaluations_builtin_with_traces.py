# pylint: disable=line-too-long,useless-suppression,docstring-missing-param,docstring-missing-return,docstring-missing-rtype,unused-argument
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to run Azure AI Evaluations
    against agent traces collected in Azure Application Insights.

    Supports three modes:
      - Default mode (no flags): Queries Application Insights client-side for trace IDs
        using the AGENT_ID environment variable, then passes them to the eval service.
      - Agent ID mode (--agent-id): Passes the agent ID directly to the eval service,
        which resolves traces server-side from Application Insights.
      - Trace ID mode (--trace-ids): Passes explicit trace IDs to the eval service.

USAGE:
    python sample_evaluations_builtin_with_traces.py
    python sample_evaluations_builtin_with_traces.py --agent-id "my-agent:1"
    python sample_evaluations_builtin_with_traces.py --trace-ids abc123 def456
    python sample_evaluations_builtin_with_traces.py --agent-id "my-agent:1" --lookback-hours 48 --max-traces 20
    python sample_evaluations_builtin_with_traces.py --no-cleanup

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv azure-monitor-query

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) APPINSIGHTS_RESOURCE_ID - Required (for default mode). The Azure Application Insights resource ID that stores
       agent traces. Not needed when using --agent-id or --trace-ids.
       It has the form: /subscriptions/<subscription_id>/resourceGroups/<rg_name>/providers/Microsoft.Insights/components/<resource_name>.
    3) AGENT_ID - Required. The agent identifier emitted by the Azure tracing integration, used to filter traces.
    4) FOUNDRY_MODEL_NAME - Required. The Azure OpenAI deployment name to use with the built-in evaluators.
    5) TRACE_LOOKBACK_HOURS - Optional. Number of hours to look back when querying traces and in the evaluation run.
       Defaults to 1.
"""

import argparse
import os
import time
from datetime import datetime, timedelta, timezone
from pprint import pprint
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.monitor.query import LogsQueryClient, LogsQueryStatus
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    TestingCriterionAzureAIEvaluator,
)

load_dotenv()


endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
appinsights_resource_id = os.environ[
    "APPINSIGHTS_RESOURCE_ID"
]  # Sample : /subscriptions/<subscription_id>/resourceGroups/<rg_name>/providers/Microsoft.Insights/components/<resource_name>
agent_id = os.environ["AGENT_ID"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
default_lookback_hours = int(os.environ.get("TRACE_LOOKBACK_HOURS", "1"))


def _build_evaluator_config(name: str, evaluator_name: str) -> TestingCriterionAzureAIEvaluator:
    """Create a standard Azure AI evaluator configuration block for trace evaluations."""
    return TestingCriterionAzureAIEvaluator(
        type="azure_ai_evaluator",
        name=name,
        evaluator_name=evaluator_name,
        data_mapping={
            "query": "{{sample.query}}",
            "response": "{{sample.response}}",
            "tool_definitions": "{{sample.tool_definitions}}",
        },
        initialization_parameters={
            "deployment_name": model_deployment_name,
        },
    )


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
    query = """
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


def main() -> None:  # pylint: disable=too-many-statements
    parser = argparse.ArgumentParser(description="Run Azure AI trace evaluations against agent traces.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--agent-id", default=None, help="Agent ID for server-side trace resolution")
    mode.add_argument("--trace-ids", nargs="+", default=None, help="Explicit trace IDs to evaluate")
    parser.add_argument("--lookback-hours", type=int, default=None, help="Lookback window in hours")
    parser.add_argument("--max-traces", type=int, default=50, help="Max traces in agent-id mode (default: 50)")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep eval group after run")
    args = parser.parse_args()

    lookback_hours = args.lookback_hours or default_lookback_hours
    trace_ids: Optional[List[str]] = None
    agent_id_for_server: Optional[str] = None
    metadata: Dict[str, str] = {}

    if args.agent_id:
        agent_id_for_server = args.agent_id
        print("Mode: Server-side agent ID resolution")
        print(f"Agent ID: {args.agent_id}")
        print(f"Lookback: {lookback_hours}h, Max traces: {args.max_traces}")
        metadata["agent_id"] = args.agent_id

    elif args.trace_ids:
        trace_ids = list(args.trace_ids)
        print(f"Mode: Explicit trace IDs ({len(trace_ids)} provided)")

    else:
        end_time = datetime.now(tz=timezone.utc)
        start_time = end_time - timedelta(hours=lookback_hours)

        print("Querying Application Insights for trace identifiers...")
        print(f"Agent ID: {agent_id}")
        print(f"Time range: {start_time.isoformat()} to {end_time.isoformat()}")

        trace_ids = get_trace_ids(appinsights_resource_id, agent_id, start_time, end_time)

        if not trace_ids:
            print("No trace IDs found for the provided agent and time window.")
            return

        print(f"\nFound {len(trace_ids)} trace IDs:")
        for tid in trace_ids:
            print(f"  - {tid}")

        metadata["agent_id"] = agent_id
        metadata["start_time"] = start_time.isoformat()
        metadata["end_time"] = end_time.isoformat()

    with DefaultAzureCredential() as credential:
        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:
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

            print("\nCreating evaluation")
            eval_object = client.evals.create(
                name="agent_trace_eval_group",
                data_source_config=data_source_config,  # type: ignore
                testing_criteria=testing_criteria,  # type: ignore
            )
            print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

            print("\nGet Evaluation by Id")
            eval_object_response = client.evals.retrieve(eval_object.id)
            print("Evaluation Response:")
            pprint(eval_object_response)

            # Build data source based on mode
            if agent_id_for_server:
                data_source: Dict[str, Any] = {
                    "type": "azure_ai_traces",
                    "agent_id": agent_id_for_server,
                    "lookback_hours": lookback_hours,
                    "max_traces": args.max_traces,
                }
            else:
                assert trace_ids is not None
                data_source = {
                    "type": "azure_ai_traces",
                    "trace_ids": trace_ids,
                    "lookback_hours": lookback_hours,
                }

            print("\nCreating Eval Run")
            run_name = f"agent_trace_eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            eval_run_object = client.evals.runs.create(
                eval_id=eval_object.id,
                name=run_name,
                metadata=metadata if metadata else None,
                data_source=data_source,  # type: ignore
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

            if not args.no_cleanup:
                client.evals.delete(eval_id=eval_object.id)
                print("Evaluation deleted")
            else:
                print(f"Skipping cleanup (--no-cleanup). Eval ID: {eval_object.id}")


if __name__ == "__main__":
    main()
