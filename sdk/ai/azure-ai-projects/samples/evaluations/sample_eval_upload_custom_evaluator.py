# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to upload a local
    folder containing custom evaluator Python code and register it as a
    code-based evaluator version using the `evaluators.upload()` method.
    It then calls getCredentials to verify access to the uploaded blob storage.

USAGE:
    python sample_eval_upload_custom_evaluator.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" azure-storage-blob python-dotenv azure-identity

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - Required. The Azure AI Project endpoint, as found in the overview page of your
       Microsoft Foundry project. It has the form: https://<account_name>.services.ai.azure.com/api/projects/<project_name>.
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

# The folder containing the AnswerLength evaluator code, relative to this sample file.
local_upload_folder = str(Path(__file__).parent / "custom_evaluators" / "answer_length_evaluator")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    # ---------------------------------------------------------------
    # 1. Upload evaluator code and create evaluator version
    #    upload() internally calls startPendingUpload to get a SAS URI,
    #    uploads the folder contents to blob storage, then creates the
    #    evaluator version with the blob URI.
    # ---------------------------------------------------------------
    evaluator_version = EvaluatorVersion(
        evaluator_type=EvaluatorType.CUSTOM,
        categories=[EvaluatorCategory.QUALITY],
        display_name="Answer Length Evaluator",
        description="Custom evaluator to calculate length of content",
        definition=CodeBasedEvaluatorDefinition(
            entry_point="answer_length_evaluator:AnswerLengthEvaluator",
            init_parameters={
                "type": "object",
                "properties": {"model_config": {"type": "string"}},
                "required": ["model_config"],
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
                "score": EvaluatorMetric(
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
        name="answer_length_evaluator",
        evaluator_version=evaluator_version,
        folder=local_upload_folder,
        overwrite=True,
    )

    print(f"Evaluator created: name={code_evaluator.name}, version={code_evaluator.version}")
    print(f"Evaluator ID: {code_evaluator.id}")
    pprint(code_evaluator)

    # ---------------------------------------------------------------
    # 2. Call getCredentials to verify access to the uploaded blob
    # ---------------------------------------------------------------
    blob_uri = code_evaluator["definition"]["blob_uri"]
    print(f"\nCalling getCredentials with blob_uri: {blob_uri}")

    credential_response = project_client.beta.evaluators.get_credentials(
        name=code_evaluator.name,
        version=code_evaluator.version,
        credential_request=EvaluatorCredentialRequest(blob_uri=blob_uri),
    )

    print("GetCredentials response:")
    pprint(credential_response)

    # ---------------------------------------------------------------
    # 3. Cleanup: delete the evaluator version
    # ---------------------------------------------------------------
    print("\nCleaning up - deleting the created evaluator version...")
    # project_client.beta.evaluators.delete_version(
    #     name=code_evaluator.name,
    #     version=code_evaluator.version,
    # )
    print("Done - upload and getCredentials verified successfully.")
