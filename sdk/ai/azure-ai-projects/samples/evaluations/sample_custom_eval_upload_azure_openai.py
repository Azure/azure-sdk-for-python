# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to:
      1. Upload the AzureFriendlyEvaluator code (which uses AzureOpenAI)
         using ``evaluators.upload()``.
      2. Create an evaluation (eval) that references the uploaded evaluator,
         passing only ``deployment_name`` — the service automatically resolves
         this into a ``model_config`` dict and injects it into the evaluator's
         ``__init__``.
      3. Run the evaluation with inline data and poll for results.

PREREQUISITE:
    To enable evaluations, please assign project managed identity with the following steps:
    1) Open https://portal.azure.com
    2) Search for the AI Foundry project from search bar
    3) Choose "Access control (IAM)" -> "Add"
    4) In "Add role assignment", search for "Azure AI User"
    5) Choose "User, group, or service principal" or "Managed Identity", add your AI Foundry project managed identity

USAGE:
    python sample_custom_eval_upload_azure_openai.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-storage-blob python-dotenv azure-identity openai

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint.
    2) FOUNDRY_MODEL_NAME       - Required. The model deployment name in the project.
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
model_deployment_name = os.environ["FOUNDRY_MODEL_NAME"]

# The folder containing the AzureFriendlyEvaluator code
evaluator_folder = str(Path(__file__).parent / "custom_evaluators" / "azure_friendly_evaluator")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as client,
):
    # ---------------------------------------------------------------
    # 1. Upload evaluator code and create evaluator version
    # ---------------------------------------------------------------
    suffix = "".join(random.choices(string.ascii_lowercase, k=5))
    evaluator_name = f"azure_friendly_evaluator_{suffix}"

    print(f"=== Step 1: Upload evaluator as '{evaluator_name}' ===\n")

    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="Azure Friendly Evaluator",
        description="Azure-OpenAI-based evaluator that scores how friendly a response is (1-5)",
        definition=CodeBasedEvaluatorDefinition(
            entry_point="azure_friendly_evaluator:AzureFriendlyEvaluator",
            init_parameters={
                "type": "object",
                "properties": {
                    "model_config": {
                        "type": "object",
                        "description": "Azure OpenAI model configuration (injected by service from deployment_name)",
                    },
                    "threshold": {"type": "number"},
                },
                "required": ["model_config", "threshold"],
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

    azure_friendly_evaluator = project_client.beta.evaluators.upload(
        name=evaluator_name,
        evaluator_version=evaluator_version,
        folder=evaluator_folder,
    )

    print(f"Evaluator created: name={azure_friendly_evaluator.name}, version={azure_friendly_evaluator.version}")
    print(f"Evaluator ID: {azure_friendly_evaluator.id}")
    pprint(azure_friendly_evaluator)

    # ---------------------------------------------------------------
    # 2. Create an evaluation referencing the uploaded evaluator
    #    Only deployment_name is passed — the service resolves it
    #    into a full model_config dict for the evaluator's __init__.
    # ---------------------------------------------------------------
    print(f"\n=== Step 2: Create evaluation ===\n")

    data_source_config = DataSourceConfigCustom(
        type="custom",
        item_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "response": {"type": "string"},
            },
            "required": ["query", "response"],
        },
        include_sample_schema=True,
    )

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": evaluator_name,
            "evaluator_name": evaluator_name,
            "initialization_parameters": {
                "deployment_name": model_deployment_name,
                "threshold": 3,
            },
        }
    ]

    eval_object = client.evals.create(
        name=f"Azure Friendly Evaluation - {suffix}",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,  # type: ignore
    )
    print(f"Evaluation created (id: {eval_object.id}, name: {eval_object.name})")

    # ---------------------------------------------------------------
    # 3. Run the evaluation with inline data
    # ---------------------------------------------------------------
    print(f"\n=== Step 3: Create evaluation run ===\n")

    eval_run_object = client.evals.runs.create(
        eval_id=eval_object.id,
        name=f"Azure Friendly Eval Run - {suffix}",
        metadata={"team": "eval-exp", "scenario": "azure-friendliness-v1"},
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
    print("\n=== Step 4: Polling for results ===\n")

    while True:
        run = client.evals.runs.retrieve(run_id=eval_run_object.id, eval_id=eval_object.id)
        if run.status in ("completed", "failed"):
            print(f"Evaluation run finished with status: {run.status}")
            output_items = list(client.evals.runs.output_items.list(run_id=run.id, eval_id=eval_object.id))
            pprint(output_items)
            print(f"\nEvaluation run Report URL: {run.report_url}")
            break
        time.sleep(5)
        print("Waiting for evaluation run to complete...")

    print("\nDone - AzureFriendlyEvaluator upload, eval creation, and eval run verified successfully.")
    print(f"Evaluator '{azure_friendly_evaluator.name}' (version {azure_friendly_evaluator.version}) retained.")
    print(f"Evaluation '{eval_object.name}' (id: {eval_object.id}) retained.")
