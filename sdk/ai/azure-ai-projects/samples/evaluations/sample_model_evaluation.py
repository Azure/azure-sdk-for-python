# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create and run an evaluation for an Azure AI model
    using the synchronous AIProjectClient.

    The OpenAI compatible Evals calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_model_evaluation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from pprint import pprint
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from openai.types.eval_create_params import DataSourceConfigCustom

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        include_sample_schema=True,
    )
    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "violence_detection",
            "evaluator_name": "builtin.violence",
            "data_mapping": {"query": "{{item.query}}", "response": "{{item.response}}"},
        }
    ]
    eval_object = openai_client.evals.create(
        name="Agent Evaluation",
        data_source_config=data_source_config,  # type: ignore
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    model = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]
    data_source = {
        "type": "azure_ai_target_completions",
        "source": {
            "type": "file_content",
            "content": [
                {"item": {"query": "What is the capital of France?"}},
                {"item": {"query": "How do I reverse a string in Python?"}},
            ],
        },
        "input_messages": {
            "type": "template",
            "template": [
                {"type": "message", "role": "user", "content": {"type": "input_text", "text": "{{item.query}}"}}
            ],
        },
        "target": {
            "type": "azure_ai_model",
            "model": model,
            "sampling_params": {  # Note: model sampling parameters are optional and can differ per model
                "top_p": 1.0,
                "max_completion_tokens": 2048,
            },
        },
    }

    agent_eval_run = openai_client.evals.runs.create(
        eval_id=eval_object.id, name=f"Evaluation Run for Model {model}", data_source=data_source  # type: ignore
    )
    print(f"Evaluation run created (id: {agent_eval_run.id})")

    while agent_eval_run.status not in ["completed", "failed"]:
        agent_eval_run = openai_client.evals.runs.retrieve(run_id=agent_eval_run.id, eval_id=eval_object.id)
        print(f"Waiting for eval run to complete... current status: {agent_eval_run.status}")
        time.sleep(5)

    if agent_eval_run.status == "completed":
        print("\n✓ Evaluation run completed successfully!")
        print(f"Result Counts: {agent_eval_run.result_counts}")

        output_items = list(
            openai_client.evals.runs.output_items.list(run_id=agent_eval_run.id, eval_id=eval_object.id)
        )
        print(f"\nOUTPUT ITEMS (Total: {len(output_items)})")
        print(f"{'-'*60}")
        pprint(output_items)
        print(f"{'-'*60}")
    else:
        print("\n✗ Evaluation run failed.")

    openai_client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
