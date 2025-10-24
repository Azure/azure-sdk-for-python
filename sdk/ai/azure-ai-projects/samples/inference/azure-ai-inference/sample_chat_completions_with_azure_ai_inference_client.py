# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AI Foundry Project endpoint, this sample demonstrates how to get an authenticated
    ChatCompletionsClient from the azure.ai.inference package and perform one chat completion
    operation. For more information on the azure.ai.inference package see
    https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.
"""

import os
from dotenv import load_dotenv
from urllib.parse import urlparse
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]
model_deployment_name = os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"]

# Project endpoint has the form:   https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name
# Inference endpoint has the form: https://your-ai-services-account-name.services.ai.azure.com/models
# Strip the "/api/projects/your-project-name" part and replace with "/models":
inference_endpoint = f"https://{urlparse(endpoint).netloc}/models"

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with ChatCompletionsClient(
        endpoint=inference_endpoint,
        credential=credential,
        credential_scopes=["https://ai.azure.com/.default"],
    ) as client:

        response = client.complete(
            model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]  # type: ignore[arg-type]
        )

        print(response.choices[0].message.content)
