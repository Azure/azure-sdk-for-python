# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AI Foundry Project endpoint, this sample demonstrates how to get an authenticated
    ChatCompletionsClient from the azure.ai.inference package and perform one chat completion
    operation. It also shows how to turn on local console tracing using the helper functions
    in file azure_ai_inference_telemetry_helper.py.
    For more information on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_and_console_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.

ALTERNATIVE USAGE:
    If you want to export telemetry to OTLP endpoint (such as Aspire dashboard
    https://learn.microsoft.com/dotnet/aspire/fundamentals/dashboard/standalone?tabs=bash)
    instead of to the console, also install:

    pip install opentelemetry-exporter-otlp-proto-grpc

    And also define:
    3) OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
import sys
from urllib.parse import urlparse
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure_ai_inference_telemetry_helper import azure_ai_inference_telemetry_helper

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

# Enables telemetry collection with OpenTelemetry for Azure AI Inference client (azure-ai-inference).
# or, if you have local OTLP endpoint running, change it to
# azure_ai_inference_telemetry_helper(destination="http://localhost:4317")
azure_ai_inference_telemetry_helper(destination=sys.stdout)

# Project endpoint has the form:   https://<your-ai-services-account-name>.services.ai.azure.com/api/projects/<your-project-name>
# Inference endpoint has the form: https://<your-ai-services-account-name>.services.ai.azure.com/models
# Strip the "/api/projects/<your-project-name>" part and replace with "/models":
inference_endpoint = f"https://{urlparse(endpoint).netloc}/models"

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with ChatCompletionsClient(
        endpoint=inference_endpoint,
        credential=credential,
        credential_scopes=["https://ai.azure.com/.default"],
    ) as client:

        response = client.complete(
            model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
        )

        print(response.choices[0].message.content)
