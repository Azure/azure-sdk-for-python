# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to evaluate multi-turn
    agent conversations by filtering traces from Application Insights using an
    agent name/version or agent ID, with optional smart filtering.

    This is Scenario 3 of multi-turn evaluations: instead of providing specific
    conversation or trace IDs, you specify an agent identity and a time window.
    The service samples traces from App Insights matching that agent and evaluates
    the reconstructed conversations.

    Three agent filter forms are supported:
      - agent_name + agent_version: Specify the agent by name and version separately.
      - agent_id: Specify the agent as a single "name:version" string.
      - smart_filtering: Use filter_strategy="smart_filtering" to bias trace
        selection toward more interesting conversations.

USAGE:
    python sample_multiturn_trace_evaluation_agent_filter.py
    python sample_multiturn_trace_evaluation_agent_filter.py --agent-id "my-agent:1"
    python sample_multiturn_trace_evaluation_agent_filter.py --smart-filter

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - Required. The model deployment name for AI-assisted evaluators.
    3) FOUNDRY_AGENT_NAME - Required. The name of the agent whose traces to evaluate.
    4) FOUNDRY_AGENT_VERSION - Optional. The agent version. If not set, latest is used.
"""

import argparse
import os
import time
from pprint import pprint
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ["FOUNDRY_AGENT_NAME"]
agent_version = os.environ.get("FOUNDRY_AGENT_VERSION", "")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate agent traces using agent filter.")
    parser.add_argument("--agent-id", default=None, help='Agent ID in "name:version" format')
    parser.add_argument("--smart-filter", action="store_true", help="Use smart_filtering strategy")
    parser.add_argument("--max-traces", type=int, default=5, help="Max traces to evaluate (default: 5)")
    parser.add_argument("--lookback-hours", type=int, default=24, help="Hours to look back (default: 24)")
    args = parser.parse_args()

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as client,
    ):
        # Eval group for trace-based evaluations
        data_source_config = {
            "type": "azure_ai_source",
            "scenario": "traces",
        }

        testing_criteria = [
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="customer_satisfaction",
                evaluator_name="builtin.customer_satisfaction",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="task_completion",
                evaluator_name="builtin.task_completion",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="conversation_coherence",
                evaluator_name="builtin.coherence",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
            TestingCriterionAzureAIEvaluator(
                type="azure_ai_evaluator",
                name="groundedness",
                evaluator_name="builtin.groundedness",
                initialization_parameters={"model": model_deployment_name},
                data_mapping={"messages": "{{item.messages}}"},
            ),
        ]

        print("Creating trace-based evaluation group")
        eval_object = client.evals.create(
            name="Multi-turn Trace Evaluation (Agent Filter)",
            data_source_config=data_source_config,  # type: ignore
            testing_criteria=testing_criteria,
        )
        print(f"Evaluation created (id: {eval_object.id})")

        # Compute time window in unix seconds
        # Pad end_time by +600s (10 min) to avoid ingestion-delay edge exclusion
        now_unix = int(time.time())
        end_time = now_unix + 600
        start_time = now_unix - (args.lookback_hours * 3600)

        # Build trace_source based on mode
        trace_source: dict = {
            "type": "agent_filter",
            "start_time": start_time,
            "end_time": end_time,
            "max_traces": args.max_traces,
        }

        if args.agent_id:
            # agent_id form: single "name:version" string
            trace_source["agent_id"] = args.agent_id
            print(f"Using agent_id filter: {args.agent_id}")
        else:
            # agent_name + agent_version form
            trace_source["agent_name"] = agent_name
            if agent_version:
                trace_source["agent_version"] = agent_version
            print(f"Using agent filter: {agent_name} v{agent_version or '(latest)'}")

        if args.smart_filter:
            trace_source["filter_strategy"] = "smart_filtering"
            print("Filter strategy: smart_filtering")

        data_source = {
            "type": "azure_ai_trace_data_source_preview",
            "trace_source": trace_source,
        }

        eval_run = client.evals.runs.create(
            eval_id=eval_object.id,
            name="multiturn-agent-filter-run",
            data_source=data_source,  # type: ignore
            extra_body={"evaluation_level": "conversation"},
        )
        print(f"Evaluation run created (id: {eval_run.id})")

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run.id, eval_id=eval_object.id)
            if run.status in ("completed", "failed"):
                break
            print(f"Waiting for eval run to complete... current status: {run.status}")
            time.sleep(5)

        if run.status == "completed":
            print("\n✓ Evaluation run completed successfully!")
            print(f"Result Counts: {run.result_counts}")

            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
            print(f"{'-'*60}")
            pprint(output_items)
            print(f"{'-'*60}")

            print(f"\nEval Run Report URL: {run.report_url}")
        else:
            print(f"\n✗ Evaluation run failed: {run.error}")

        client.evals.delete(eval_id=eval_object.id)
        print("Evaluation deleted")


if __name__ == "__main__":
    main()
