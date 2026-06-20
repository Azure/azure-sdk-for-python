# pylint: disable=line-too-long,useless-suppression
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

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
import time
from pprint import pprint
from typing import Union
from dotenv import load_dotenv
from openai.types.evals.create_eval_completions_run_data_source_param import SourceFileContent, SourceFileContentContent
from openai.types.eval_create_params import DataSourceConfigCustom
from openai.types.evals.run_create_response import RunCreateResponse
from openai.types.evals.run_retrieve_response import RunRetrieveResponse
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAIModelTargetParam,
    TestingCriterionAzureAIEvaluator,
    ModelSamplingConfigParam,
    TargetCompletionEvalRunDataSource,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
        include_sample_schema=True,
    )
    # Notes: for data_mapping:
    # {{sample.output_text}} is the string output of the provide model target for the given input in {{item.query}}
    testing_criteria = [
        TestingCriterionAzureAIEvaluator(
            type="azure_ai_evaluator",
            name="violence_detection",
            evaluator_name="builtin.violence",
            data_mapping={"query": "{{item.query}}", "response": "{{sample.output_text}}"},
        )
    ]
    eval_object = openai_client.evals.create(
        name="Model Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    model = os.environ["FOUNDRY_MODEL_NAME"]
    data_source = TargetCompletionEvalRunDataSource(
        type="azure_ai_target_completions",
        source=SourceFileContent(
            type="file_content",
            content=[
                SourceFileContentContent(item={"query": "What is the capital of France?"}),
                SourceFileContentContent(item={"query": "How do I reverse a string in Python?"}),
            ],
        ),
        input_messages={
            "type": "template",  # type: ignore
            "template": [
                {"type": "message", "role": "user", "content": {"type": "input_text", "text": "{{item.query}}"}}
            ],
        },
        target=AzureAIModelTargetParam(
            type="azure_ai_model",
            model=model,
            sampling_params=ModelSamplingConfigParam(  # Note: model sampling parameters are optional and can differ per model
                top_p=1.0,
                max_completion_tokens=2048,
            ),
        ),
    )

    agent_eval_run: Union[RunCreateResponse, RunRetrieveResponse] = openai_client.evals.runs.create(
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
