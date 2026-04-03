# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to:
      1. Upload a custom LLM-based evaluator (FriendlyEvaluator) with nested
         folder structure (common_util/) using `evaluators.upload()`.
      2. Create an evaluation (eval) that references the uploaded evaluator.
      3. Run the evaluation with inline data and poll for results.

    The FriendlyEvaluator calls Azure OpenAI to judge the friendliness of a
    response and returns score, label, reason, and explanation.

USAGE:
    python sample_eval_upload_friendly_evaluator.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" azure-storage-blob python-dotenv azure-identity openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint.
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
openai_api_key = os.environ["OPENAI_API_KEY"]
openai_model = os.environ.get("OPENAI_MODEL", "gpt-4.1")

# The folder containing the FriendlyEvaluator code, including common_util/ subfolder
local_upload_folder = str(Path(__file__).parent / "custom_evaluators" / "friendly_evaluator")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # ---------------------------------------------------------------
    # 1. Upload evaluator code and create evaluator version
    #    The folder structure uploaded is:
    #      friendly_evaluator/
    #        friendly_evaluator.py          <- entry point
    #        common_util/
    #          __init__.py
    #          util.py                      <- helper functions
    # ---------------------------------------------------------------
    suffix = "".join(random.choices(string.ascii_lowercase, k=5))
    evaluator_name = f"friendly_evaluator_{suffix}"

    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="Friendliness Evaluator",
        description="LLM-based evaluator that scores how friendly a response is (1-5)",
        definition=CodeBasedEvaluatorDefinition(
            entry_point="friendly_evaluator:FriendlyEvaluator",
            init_parameters={
                "type": "object",
                "properties": {
                    "api_key": {
                        "type": "string",
                        "description": "OpenAI API key for the LLM judge",
                    },
                    "model": {
                        "type": "string",
                        "description": "Model name to use for evaluation (e.g. gpt-4.1)",
                    },
                    "threshold": {"type": "number"},
                },
                "required": ["api_key", "model", "threshold"],
            },
            data_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The original user query"},
                    "response": {"type": "string", "description": "The response to evaluate for friendliness"},
                },
                "required": ["query", "response"],
            },
            metrics={
                "score": EvaluatorMetric(
                    type=EvaluatorMetricType.ORDINAL,
                    desirable_direction=EvaluatorMetricDirection.INCREASE,
                    min_value=1,
                    max_value=5,
                )
            },
        ),
    )

    print("Uploading FriendlyEvaluator (with nested common_util folder)...")
    friendly_evaluator = project_client.beta.evaluators.upload(
        name=evaluator_name,
        evaluator_version=evaluator_version,
        folder=local_upload_folder,
    )

    print(f"\nEvaluator created: name={friendly_evaluator.name}, version={friendly_evaluator.version}")
    print(f"Evaluator ID: {friendly_evaluator.id}")
    pprint(friendly_evaluator)

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
                 "api_key": openai_api_key,
                 "model": openai_model,
                 "threshold": 3,
            },
        }
    ]

    print("\nCreating evaluation...")
    eval_object = client.evals.create(
        name=f"Friendliness Evaluation - {suffix}",
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
        name=f"Friendliness Eval Run - {suffix}",
        metadata={"team": "eval-exp", "scenario": "friendliness-v1"},
        data_source=CreateEvalJSONLRunDataSourceParam(
            type="jsonl",
            source=SourceFileContent(
                type="file_content",
                content=[
                    SourceFileContentContent(
                        item={
                            "query": "How do I reset my password?",
                            "response": "Go to settings and click reset. That's it.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "I'm having trouble with my account",
                            "response": "I'm really sorry to hear you're having trouble! I'd love to help you get this sorted out. Could you tell me a bit more about what's happening so I can assist you better?",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "Can you help me?",
                            "response": "Read the docs.",
                        }
                    ),
                    SourceFileContentContent(
                        item={
                            "query": "What's the weather like today?",
                            "response": "Great question! While I'm not a weather service, I'd be happy to suggest some wonderful weather apps that can give you accurate forecasts. Would you like some recommendations? 😊",
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
    #     name=friendly_evaluator.name,
    #     version=friendly_evaluator.version,
    # )
    # client.evals.delete(eval_id=eval_object.id)
    # print("Cleanup done.")
    print("\nDone - FriendlyEvaluator upload, eval creation, and eval run verified successfully.")
