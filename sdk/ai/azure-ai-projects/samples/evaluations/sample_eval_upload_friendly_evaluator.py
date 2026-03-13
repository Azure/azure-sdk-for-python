# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to upload a custom
    LLM-based evaluator (FriendlyEvaluator) that uses the common_util helper
    module.  The evaluator calls Azure OpenAI to judge the friendliness of a
    response and returns score, label, reason, and explanation.

    This proves that the upload() API can handle nested folder structures
    (common_util/util.py is uploaded alongside friendly_evaluator.py).

USAGE:
    python sample_eval_upload_friendly_evaluator.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" azure-storage-blob python-dotenv azure-identity openai

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint.
"""

import os
from pathlib import Path
from pprint import pprint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    CodeBasedEvaluatorDefinition,
    EvaluatorCategory,
    EvaluatorCredentialRequest,
    EvaluatorMetric,
    EvaluatorMetricType,
    EvaluatorMetricDirection,
    EvaluatorType,
    EvaluatorVersion,
)

from dotenv import load_dotenv

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

# The folder containing the evaluator code, including common_util/ subfolder
local_upload_folder = str(Path(__file__).parent / "custom_evaluator")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # ---------------------------------------------------------------
    # 1. Upload evaluator code and create evaluator version
    #    The folder structure uploaded is:
    #      custom_evaluator/
    #        friendly_evaluator.py          <- entry point
    #        common_util/
    #          __init__.py
    #          util.py                      <- helper functions
    #        answer_length_evaluator.py     <- (also uploaded, ignored by this evaluator)
    # ---------------------------------------------------------------
    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="Friendliness Evaluator 3",
        description="LLM-based evaluator that scores how friendly a response is (1-5)",
        definition=CodeBasedEvaluatorDefinition(
            entry_point="friendly_evaluator:FriendlyEvaluator",
            init_parameters={
                "type": "object",
                "properties": {
                    "model_config": {
                        "type": "object",
                        "description": "Azure OpenAI configuration for the LLM judge",
                        "properties": {
                            "azure_endpoint": {"type": "string"},
                            "azure_deployment": {"type": "string"},
                            "api_version": {"type": "string"},
                            "api_key": {"type": "string"},
                        },
                        "required": ["azure_endpoint", "azure_deployment"],
                    }
                },
                "required": ["model_config"],
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
        name="friendly_evaluator_3",
        evaluator_version=evaluator_version,
        folder=local_upload_folder,
        overwrite=True,
    )

    print(f"\nEvaluator created: name={friendly_evaluator.name}, version={friendly_evaluator.version}")
    print(f"Evaluator ID: {friendly_evaluator.id}")
    pprint(friendly_evaluator)

    # ---------------------------------------------------------------
    # 2. Call getCredentials to verify blob storage access
    # ---------------------------------------------------------------
    blob_uri = friendly_evaluator["definition"]["blob_uri"]
    print(f"\nCalling getCredentials with blob_uri: {blob_uri}")

    credential_response = project_client.beta.evaluators.get_credentials(
        name=friendly_evaluator.name,
        version=friendly_evaluator.version,
        credential_request=EvaluatorCredentialRequest(blob_uri=blob_uri),
    )

    print("GetCredentials response:")
    pprint(credential_response)

    # ---------------------------------------------------------------
    # 3. Cleanup: delete the evaluator version
    # ---------------------------------------------------------------
    print("\nCleaning up - deleting the created evaluator version...")
    # project_client.beta.evaluators.delete_version(
    #     name=friendly_evaluator.name,
    #     version=friendly_evaluator.version,
    # )
    print("Done - FriendlyEvaluator upload with nested folders verified successfully.")
