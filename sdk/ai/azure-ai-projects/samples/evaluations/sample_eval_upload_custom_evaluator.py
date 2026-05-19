# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to:
      1. Upload a local folder containing custom evaluator Python code and
         register it as a code-based evaluator version using `evaluators.upload()`.
      2. Create an evaluation (eval) that references the uploaded evaluator.
      3. Run the evaluation with inline data and poll for results.

USAGE:
    python sample_eval_upload_custom_evaluator.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" azure-storage-blob python-dotenv azure-identity openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) FOUNDRY_MODEL_NAME - Optional. The name of the model deployment to use for evaluation.
"""

import os
import time
import random
import string
from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from openai.types.evals.create_eval_jsonl_run_data_source_param import (
    CreateEvalJSONLRunDataSourceParam,
    SourceFileContent,
    SourceFileContentContent,
)
from openai.types.eval_create_params import DataSourceConfigCustom
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeBasedEvaluatorDefinition,
    EvaluatorCategory,
    EvaluatorMetric,
    EvaluatorMetricType,
    EvaluatorMetricDirection,
    EvaluatorType,
    EvaluatorVersion,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model_deployment_name = os.environ.get("FOUNDRY_MODEL_NAME")

# The folder containing the AnswerLength evaluator code, relative to this sample file.
local_upload_folder = str(Path(__file__).parent / "custom_evaluators" / "answer_length_evaluator")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # ---------------------------------------------------------------
    # 1. Upload evaluator code and create evaluator version
    #    upload() internally calls startPendingUpload to get a SAS URI,
    #    uploads the folder contents to blob storage, then creates the
    #    evaluator version with the blob URI.
    # ---------------------------------------------------------------
    suffix = "".join(random.choices(string.ascii_lowercase, k=5))
    evaluator_name = f"answer_length_evaluator_{suffix}"
    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="Answer Length Evaluator",
        description="Custom evaluator to calculate length of content",
        definition=CodeBasedEvaluatorDefinition(
            entry_point="answer_length_evaluator:AnswerLengthEvaluator",
            init_parameters={
                "type": "object",
                "properties": {"config": {"type": "string"}, "threshold": {"type": "number"}},
                "required": ["config", "threshold"],
            },
            data_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                },
                "required": ["query", "response"],
            },
            metrics={
                "result": EvaluatorMetric(
                    type=EvaluatorMetricType.ORDINAL,
                    desirable_direction=EvaluatorMetricDirection.INCREASE,
                    min_value=1,
                    max_value=5,
                )
            },
        ),
    )

    print("Uploading custom evaluator code and creating evaluator version...")
    code_evaluator = project_client.beta.evaluators.upload(
        name=evaluator_name,
        evaluator_version=evaluator_version,
        folder=local_upload_folder,
    )

    print(f"Evaluator created: name={code_evaluator.name}, version={code_evaluator.version}")
    print(f"Evaluator ID: {code_evaluator.id}")
    pprint(code_evaluator)

    # ---------------------------------------------------------------
    # 2. Create an evaluation referencing the uploaded evaluator
    # ---------------------------------------------------------------
    data_source_config = DataSourceConfigCustom(
        {
            "type": "custom",
            "item_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                },
                "required": ["query", "response"],
            },
            "include_sample_schema": True,
        }
    )

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": evaluator_name,
            "evaluator_name": evaluator_name,
            "initialization_parameters": {
                "config": "example config value",
                "threshold": 3,
            },
        }
    ]

    print("\nCreating evaluation...")
    eval_object = client.evals.create(
        name=f"Answer Length Evaluation - {suffix}",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # ---------------------------------------------------------------
    # 3. Run the evaluation with inline data
    # ---------------------------------------------------------------
    print("\nCreating evaluation run with inline data...")
    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"Answer Length Eval Run - {suffix}",
        metadata={"team": "eval-exp", "scenario": "answer-length-v1"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
                    SourceFileContentContent(
                        item={
                            "query": "What is the capital of France?",
                            "response": "Paris",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "Explain quantum computing",
                            "response": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information in fundamentally different ways than classical computers.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "What is AI?",
                            "response": "AI stands for Artificial Intelligence. It is a branch of computer science that aims to create intelligent machines that can perform tasks that typically require human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "Say hello",
                            "response": "Hi!",
                        }
                    ),
                ],
            ),
        ),
    )

    print(f"Evaluation run created (id: {eval_run_object.id})")
    pprint(eval_run_object)

    # ---------------------------------------------------------------
    # 4. Poll for evaluation run completion
    # ---------------------------------------------------------------
    while True:
        run = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        if run.status in ("completed", "failed"):
            print(f"\nEvaluation run finished with status: {run.status}")
            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            pprint(output_items)
            print(f"\nEvaluation run Report URL: {run.report_url}")
            break
        time.sleep(5)
        print("Waiting for evaluation run to complete...")

    # ---------------------------------------------------------------
    # 5. Cleanup (uncomment to delete)
    # ---------------------------------------------------------------
    # print("\nCleaning up...")
    # project_client.beta.evaluators.delete_version(
    #     name=code_evaluator.name,
    #     version=code_evaluator.version,
    # )
    # client.evals.delete(eval_id=eval_object.id)
    # print("Cleanup done.")
    print("\nDone - upload, eval creation, and eval run verified successfully.")
