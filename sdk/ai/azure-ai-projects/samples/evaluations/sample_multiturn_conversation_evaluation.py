# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to create and run a
    multi-turn conversation evaluation using the synchronous `openai.evals.*`
    methods. Multi-turn evaluations assess complete conversations—including
    tool-calling exchanges—using conversation-level metrics such as customer
    satisfaction, task completion, coherence, and groundedness.

    This sample uses a JSONL dataset where each row contains a ``messages``
    array (and optional ``tool_definitions``). It shows how to:
      - Define a ``custom`` data source config with the conversation schema.
      - Select conversation-level evaluators with ``{{item.messages}}`` mapping.
      - Upload conversation data, create an evaluation, and run it.
      - Poll for completion and print results.

USAGE:
    python sample_multiturn_conversation_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) FOUNDRY_MODEL_NAME - Required. The name of the model deployment to use for AI-assisted evaluators.
"""

import os
import time
from pprint import pprint
from dotenv import load_dotenv
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileID,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import TestingCriterionAzureAIEvaluator

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

# Path to the multi-turn conversation data file
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
data_file = os.path.join(data_folder, "sample_data_multiturn_conversations.jsonl")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # Define the data source config for multi-turn conversations.
    # The item_schema declares the "messages" array and optional "tool_definitions".
    # Set include_sample_schema to False since conversation evaluators use
    # {{item.messages}} mapping rather than per-turn sample fields.
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "messages": {"type": "array"},
                "tool_definitions": {"type": "array"},
            },
            "required": ["messages"],
        },
        include_sample_schema=False,
    )

    # Define conversation-level evaluators.
    # All evaluators map to {{item.messages}} to assess the full conversation.
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="customer_satisfaction",
            evaluator_name="builtin.customer_satisfaction",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"messages": "{{item.messages}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="task_completion",
            evaluator_name="builtin.task_completion",
            initialization_parameters={"deployment_name": model_deployment_name},
            data_mapping={"messages": "{{item.messages}}"},
        ),
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="conversation_coherence",
            evaluator_name="builtin.coherence",
            initialization_parameters={"deployment_name": model_deployment_name},
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

    print("Creating multi-turn conversation evaluation")
    eval_object = client.evals.create(
        name="Multi-turn Conversation Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id})")

    # Upload the conversation dataset
    try:
        data_id = project_client.datasets.upload_file(
            name="multiturn-conversation-data",
            version="1",
            file_path=data_file,
        ).id
        print(f"Dataset uploaded (id: {data_id})")
    except Exception:
        # Dataset already exists — use the existing URI
        account = endpoint.split("/")[2].split(".")[0]
        project = endpoint.rstrip("/").split("/")[-1]
        data_id = f"azureai://accounts/{account}/projects/{project}/data/multiturn-conversation-data/versions/1"
        print(f"Using existing dataset (id: {data_id})")

    # Create a run with evaluation_level set to "conversation"
    # so evaluators score each conversation as a whole.
    eval_run = client.evals.runs.create(
        eval_id=eval_object.id,
        name="multiturn-conversation-run",
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileID(
                type="file_id",
                id=data_id,
            ),
        ),
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
