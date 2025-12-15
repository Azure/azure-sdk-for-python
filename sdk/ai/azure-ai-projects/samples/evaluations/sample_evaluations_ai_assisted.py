# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list evaluation and and eval runs.

USAGE:
    python sample_evaluations_ai_assisted.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
    3) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    4) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    5) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
"""

import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DatasetVersion,
)

import time
from pprint import pprint
from openai.types.evals.create_eval_jsonl_run_data_source_param import CreateEvalJSONLRunDataSourceParam, SourceFileID
from openai.types.eval_create_params import DataSourceConfigCustom
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")
dataset_name = os.environ.get("DATASET_NAME", "")
dataset_version = os.environ.get("DATASET_VERSION", "1")

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
data_file = os.path.join(data_folder, "sample_data_evaluation.jsonl")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):

    print("Upload a single file and create a new Dataset to reference the file.")
    dataset: DatasetVersion = project_client.datasets.upload_file(
        name=dataset_name or f"eval-data-{datetime.utcnow().strftime('%Y-%m-%d_%H%M%S_UTC')}",
        version=dataset_version,
        file_path=data_file,
    )
    pprint(dataset)

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

    print("Creating evaluation")
    eval_object = client.evals.create(
        name="ai assisted evaluators test",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    print("Get Evaluation by Id")
    eval_object_response = client.evals.retrieve(eval_object.id)
    print("Evaluation Response:")
    pprint(eval_object_response)

    print("Creating evaluation run")
    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name="dataset",
        metadata={"team": "eval-exp", "scenario": "notifications-v1"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            source=SourceFileID(id=dataset.id or "", type="file_id"), type="jsonl"
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

    project_client.datasets.delete(name=dataset.name, version=dataset.version)
    print("Dataset deleted")

    client.evals.delete(eval_id=eval_object.id)
    print("Evaluation deleted")
