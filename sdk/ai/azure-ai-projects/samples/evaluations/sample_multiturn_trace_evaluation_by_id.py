# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to evaluate multi-turn
    conversations captured as agent traces in Application Insights, using specific
    conversation IDs or trace IDs to select which conversations to evaluate.

    This is Scenario 2 of multi-turn evaluations: you provide known conversation
    or trace identifiers, and the service reconstructs the messages from App Insights
    traces, then runs conversation-level evaluators against them.

    Two modes are supported:
      - conversation_id_source: Provide Foundry conversation IDs.
      - trace_id_source: Provide W3C trace IDs (operation_Id from App Insights).

USAGE:
    python sample_multiturn_trace_evaluation_by_id.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME - Required. The model deployment name for AI-assisted evaluators.
    3) FOUNDRY_CONVERSATION_IDS - Required (for conversation_id mode). Comma-separated
       Foundry conversation IDs to evaluate.
       Example: "conv_abc123,conv_def456,conv_ghi789"
    4) FOUNDRY_TRACE_IDS - Optional (for trace_id mode). Comma-separated W3C trace IDs.
       If set, overrides conversation IDs.
"""

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

# Choose one: conversation IDs or trace IDs
conversation_ids_str = os.environ.get("FOUNDRY_CONVERSATION_IDS", "")
trace_ids_str = os.environ.get("FOUNDRY_TRACE_IDS", "")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # Eval group for trace-based evaluations uses azure_ai_source with scenario "traces"
    data_source_config = {
        "type": "azure_ai_source",
        "scenario": "traces",
    }

    # Conversation-level evaluators for trace data
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
        name="Multi-turn Trace Evaluation (by ID)",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id})")

    # Build the data source based on which IDs are provided
    if trace_ids_str:
        # Trace ID mode — provide W3C trace IDs (operation_Id from App Insights)
        trace_ids = [tid.strip() for tid in trace_ids_str.split(",") if tid.strip()]
        print(f"Using {len(trace_ids)} trace IDs")
        data_source = {
            "type": "azure_ai_trace_data_source_preview",
            "trace_source": {
                "type": "trace_id_source",
                "trace_ids": trace_ids,
            },
        }
    else:
        # Conversation ID mode — provide Foundry conversation IDs
        conversation_ids = [cid.strip() for cid in conversation_ids_str.split(",") if cid.strip()]
        if not conversation_ids:
            raise ValueError(
                "Set FOUNDRY_CONVERSATION_IDS or FOUNDRY_TRACE_IDS. "
                "These are IDs from prior agent interactions captured in App Insights."
            )
        print(f"Using {len(conversation_ids)} conversation IDs")
        data_source = {
            "type": "azure_ai_trace_data_source_preview",
            "trace_source": {
                "type": "conversation_id_source",
                "conversation_ids": conversation_ids,
            },
        }

    # Create run with evaluation_level = "conversation"
    eval_run = client.evals.runs.create(
        eval_id=eval_object.id,
        name="multiturn-trace-by-id-run",
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
