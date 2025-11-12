# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to use the synchronous
    `openai.evals.*` methods to create, get and list eval group and and eval runs.

USAGE:
    python sample_evaluations_ai_assisted.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
    2) CONNECTION_NAME - Required. The name of the connection of type Azure Storage Account, to use for the dataset upload.
    3) MODEL_ENDPOINT - Required. The Azure OpenAI endpoint associated with your Foundry project.
       It can be found in the Foundry overview page. It has the form https://<account_name>.openai.azure.com.
    4) MODEL_API_KEY - Required. The API key for the model endpoint. Can be found under "key" in the model details page
       (click "Models + endpoints" and select your model to get to the model details page).
    5) AZURE_AI_MODEL_DEPLOYMENT_NAME - Required. The name of the model deployment to use for evaluation.
    6) DATASET_NAME - Optional. The name of the Dataset to create and use in this sample.
    7) DATASET_VERSION - Optional. The version of the Dataset to create and use in this sample.
    8) DATA_FOLDER - Optional. The folder path where the data files for upload are located.
"""

import os

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    DatasetVersion,
)
import json
import time
from pprint import pprint
from openai.types.evals.create_eval_jsonl_run_data_source_param import CreateEvalJSONLRunDataSourceParam, SourceFileID
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

endpoint = os.environ[
    "AZURE_AI_PROJECT_ENDPOINT"
]  # Sample : https://<account_name>.services.ai.azure.com/api/projects/<project_name>

connection_name = os.environ.get("CONNECTION_NAME", "")
model_endpoint = os.environ.get("MODEL_ENDPOINT", "")  # Sample: https://<account_name>.openai.azure.com.
model_api_key = os.environ.get("MODEL_API_KEY", "")
model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")  # Sample : gpt-4o-mini
dataset_name = os.environ.get("DATASET_NAME", "")
dataset_version = os.environ.get("DATASET_VERSION", "1")

# Construct the paths to the data folder and data file used in this sample
script_dir = os.path.dirname(os.path.abspath(__file__))
data_folder = os.environ.get("DATA_FOLDER", os.path.join(script_dir, "data_folder"))
data_file = os.path.join(data_folder, "sample_data_evaluation.jsonl")

with DefaultAzureCredential() as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        print("Upload a single file and create a new Dataset to reference the file.")
        dataset: DatasetVersion = project_client.datasets.upload_file(
            name=dataset_name or f"eval-data-{datetime.utcnow().strftime('%Y-%m-%d_%H%M%S_UTC')}",
            version=dataset_version,
            file_path=data_file,
        )
        pprint(dataset)

        print("Creating an OpenAI client from the AI Project client")

        client = project_client.get_openai_client()

        data_source_config = {
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

        print("Creating Eval Group")
        eval_object = client.evals.create(
            name="ai assisted evaluators test",
            data_source_config=data_source_config, # type: ignore
            testing_criteria=testing_criteria, # type: ignore
        )
        print(f"Eval Group created")

        print("Get Eval Group by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Eval Run Response:")
        pprint(eval_object_response)

        print("Creating Eval Run")
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

        print("Get Eval Run by Id")
        eval_run_response = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        print("Eval Run Response:")
        pprint(eval_run_response)

        while True:
            run = client.evals.runs.retrieve(run_id=eval_run_response.id, eval_id=eval_object.id)
            if run.status == "completed" or run.status == "failed":
                output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
                pprint(output_items)
                print(f"Eval Run Report URL: {run.report_url}")

                break
            time.sleep(5)
            print("Waiting for eval run to complete...")
