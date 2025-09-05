# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_delete_trained_model_async.py
DESCRIPTION:
    This sample demonstrates how to delete a **trained model** from a Text Authoring project (async).
USAGE:
    python sample_delete_trained_model_async.py
REQUIRED ENV VARS (for AAD / DefaultAzureCredential):
    AZURE_TEXT_ENDPOINT
    AZURE_CLIENT_ID
    AZURE_TENANT_ID
    AZURE_CLIENT_SECRET
NOTE:
    If you want to use AzureKeyCredential instead, set:
      - AZURE_TEXT_ENDPOINT
      - AZURE_TEXT_KEY
OPTIONAL ENV VARS:
    PROJECT_NAME         # defaults to "<project-name>"
    TRAINED_MODEL_LABEL  # defaults to "<trained-model-label>"
"""

# [START text_authoring_delete_trained_model_async]
import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.language.text.authoring.aio import TextAuthoringClient


async def sample_delete_trained_model_async():
    # settings
    endpoint = os.environ["AZURE_TEXT_ENDPOINT"]
    project_name = os.environ.get("PROJECT_NAME", "<project-name>")
    trained_model_label = os.environ.get("TRAINED_MODEL_LABEL", "<trained-model-label>")

    # create a client with AAD
    credential = DefaultAzureCredential()
    async with TextAuthoringClient(endpoint, credential=credential) as client:
        # project-scoped client
        project_client = client.get_project_client(project_name)

        # capture raw HTTP status via pipeline hook
        captured = {}

        def capture_response(pipeline_response):
            captured["status_code"] = pipeline_response.http_response.status_code

        # delete trained model (async call)
        await project_client.trained_model.delete_trained_model(
            trained_model_label,
            raw_response_hook=capture_response,
        )

        # Print response status (204 expected on success)
        status = captured.get("status_code")
        print("=== Delete Trained Model (Async) ===")
        print(f"Project: {project_name}")
        print(f"Trained Model Label: {trained_model_label}")
        print(f"HTTP Status: {status}")  # 204 No Content on success

# [END text_authoring_delete_trained_model_async]


async def main():
    await sample_delete_trained_model_async()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
