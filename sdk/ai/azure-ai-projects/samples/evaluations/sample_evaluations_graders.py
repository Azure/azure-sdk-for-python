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
    python sample_evaluations_graders.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity python-dotenv

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
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()

endpoint = os.environ[
    "AZURE_AI_PROJECT_ENDPOINT"
]

model_deployment_name = os.environ.get("AZURE_AI_MODEL_DEPLOYMENT_NAME", "")
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
                    "query": {"type": "string"},
                    "response": {"type": "string"},
                    "context": {"type": "string"},
                    "ground_truth": {"type": "string"},
                },
                "required": [],
            },
            "include_sample_schema": True,
        }

        testing_criteria = [
            {
                "type": "label_model",
                "model": "{{aoai_deployment_and_model}}",
                "input": [
                    {
                        "role": "developer",
                        "content": "Classify the sentiment of the following statement as one of 'positive', 'neutral', or 'negative'",
                    },
                    {"role": "user", "content": "Statement: {{item.query}}"},
                ],
                "passing_labels": ["positive", "neutral"],
                "labels": ["positive", "neutral", "negative"],
                "name": "label_grader",
            },
            {
                "type": "text_similarity",
                "input": "{{item.ground_truth}}",
                "evaluation_metric": "bleu",
                "reference": "{{item.response}}",
                "pass_threshold": 1,
                "name": "text_check_grader",
            },
            {
                "type": "string_check",
                "input": "{{item.ground_truth}}",
                "reference": "{{item.ground_truth}}",
                "operation": "eq",
                "name": "string_check_grader",
            },
            {
                "type": "score_model",
                "name": "score",
                "model": "{{aoai_deployment_and_model}}",
                "input": [
                    {
                        "role": "system",
                        "content": 'Evaluate the degree of similarity between the given output and the ground truth on a scale from 1 to 5, using a chain of thought to ensure step-by-step reasoning before reaching the conclusion.\n\nConsider the following criteria:\n\n- 5: Highly similar - The output and ground truth are nearly identical, with only minor, insignificant differences.\n- 4: Somewhat similar - The output is largely similar to the ground truth but has few noticeable differences.\n- 3: Moderately similar - There are some evident differences, but the core essence is captured in the output.\n- 2: Slightly similar - The output only captures a few elements of the ground truth and contains several differences.\n- 1: Not similar - The output is significantly different from the ground truth, with few or no matching elements.\n\n# Steps\n\n1. Identify and list the key elements present in both the output and the ground truth.\n2. Compare these key elements to evaluate their similarities and differences, considering both content and structure.\n3. Analyze the semantic meaning conveyed by both the output and the ground truth, noting any significant deviations.\n4. Based on these comparisons, categorize the level of similarity according to the defined criteria above.\n5. Write out the reasoning for why a particular score is chosen, to ensure transparency and correctness.\n6. Assign a similarity score based on the defined criteria above.\n\n# Output Format\n\nProvide the final similarity score as an integer (1, 2, 3, 4, or 5).\n\n# Examples\n\n**Example 1:**\n\n- Output: "The cat sat on the mat."\n- Ground Truth: "The feline is sitting on the rug."\n- Reasoning: Both sentences describe a cat sitting on a surface, but they use different wording. The structure is slightly different, but the core meaning is preserved. There are noticeable differences, but the overall meaning is conveyed well.\n- Similarity Score: 3\n\n**Example 2:**\n\n- Output: "The quick brown fox jumps over the lazy dog."\n- Ground Truth: "A fast brown animal leaps over a sleeping canine."\n- Reasoning: The meaning of both sentences is very similar, with only minor differences in wording. The structure and intent are well preserved.\n- Similarity Score: 4\n\n# Notes\n\n- Always aim to provide a fair and balanced assessment.\n- Consider both syntactic and semantic differences in your evaluation.\n- Consistency in scoring similar pairs is crucial for accurate measurement.',
                    },
                    {"role": "user", "content": "Output: {{item.response}}}}\nGround Truth: {{item.ground_truth}}"},
                ],
                "image_tag": "2025-05-08",
                "pass_threshold": 0.5,
            },
        ]

        print("Creating evaluation")
        eval_object = client.evals.create(
            name="OpenAI graders test",
            data_source_config=data_source_config, # type: ignore
            testing_criteria=testing_criteria, # type: ignore
        )
        print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

        print("Get evaluation by Id")
        eval_object_response = client.evals.retrieve(eval_object.id)
        print("Evaluation Response:")
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
        print(f"Eval Run created (id: {eval_run_object.id}, name: {eval_run_object.name})")
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

        project_client.datasets.delete(name=dataset.name, version=dataset.version)
        print("Dataset deleted")

        client.evals.delete(eval_id=eval_object.id)
        print("Evaluation deleted")