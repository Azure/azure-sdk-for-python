# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and eval runs
    with AI-assisted evaluators (Similarity, ROUGE, METEOR, GLEU, F1, BLEU).

USAGE:
    python sample_evaluations_ai_assisted.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
"""

import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import time
from pprint import pprint
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from dotenv import load_dotenv


load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):

    data_source_config = DataSourceConfigCustom(
        {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "response": {"type": "string"},
                    "ground_truth": {"type": "string"},
                },
                "required": [],
            },
            "include_sample_schema": False,
        }
    )

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "Similarity",
            "evaluator_name": "builtin.similarity",
            "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
            "initialization_parameters": {"deployment_name": f"{model_deployment_name}", "threshold": 3},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "ROUGEScore",
            "evaluator_name": "builtin.rouge_score",
            "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
            "initialization_parameters": {
                "rouge_type": "rouge1",
                "f1_score_threshold": 0.5,
                "precision_threshold": 0.5,
                "recall_threshold": 0.5,
            },
        },
        {
            "type": "azure_ai_evaluator",
            "name": "METEORScore",
            "evaluator_name": "builtin.meteor_score",
            "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
            "initialization_parameters": {"threshold": 0.5},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "GLEUScore",
            "evaluator_name": "builtin.gleu_score",
            "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
            "initialization_parameters": {"threshold": 0.5},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "F1Score",
            "evaluator_name": "builtin.f1_score",
            "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
            "initialization_parameters": {"threshold": 0.5},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "BLEUScore",
            "evaluator_name": "builtin.bleu_score",
            "data_mapping": {"response": "{{item.response}}", "ground_truth": "{{item.ground_truth}}"},
            "initialization_parameters": {"threshold": 0.5},
        },
    ]

    print("Creating evaluation with AI-assisted evaluators")
    eval_object = client.evals.create(
        name="AI assisted evaluators test",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    print("Get Evaluation by Id")
    eval_object_response = client.evals.retrieve(eval_object.id)
    print("Evaluation Response:")
    pprint(eval_object_response)

    print("Creating evaluation run with inline data")
    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name="inline_data_ai_assisted_run",
        metadata={"team": "eval-exp", "scenario": "ai-assisted-inline-v1"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
                    SourceFileContentContent(
                        item={
                            "response": "The capital of France is Paris, which is also known as the City of Light.",
                            "ground_truth": "Paris is the capital of France.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "response": "Python is a high-level programming language known for its simplicity and readability.",
                            "ground_truth": "Python is a popular programming language that is easy to learn.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "response": "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
                            "ground_truth": "Machine learning allows computers to learn from data without being explicitly programmed.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "response": "The sun rises in the east and sets in the west due to Earth's rotation.",
                            "ground_truth": "The sun appears to rise in the east and set in the west because of Earth's rotation.",
                        }
                    ),
                ],
            ),
        ),
    )
    print(f"Eval Run created")
    pprint(eval_run_object)

    print("Get Evaluation Run by Id")
    eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
    print("Evaluation Run Response:")
    pprint(eval_run_response)

    while True:
        run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
        if run.status == "completed" or run.status == "failed":
            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            pprint(output_items)
            print(f"Eval Run Report URL: {run.report_url}")
            break

        time.sleep(5)
        print("Waiting for evaluation run to complete...")

    client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
