# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated
    ChatCompletionsClient from the azure.ai.inference package and perform one chat completion
    operation.
    The client is instrumented to upload OpenTelemetry traces to Azure Monitor. View the uploaded traces
    in the "Tracing" tab in your Azure AI Foundry project page.
    For more information on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_and_azure_monitor_tracing.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-inference azure-identity azure-monitor-opentelemetry

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The AI model deployment name, as found in your AI Foundry project.
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
from urllib.parse import urlparse
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

scenario = os.path.basename(__file__)
tracer = trace.get_tracer(__name__)

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

    with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

        connection_string = project_client.telemetry.get_application_insights_connection_string()
        configure_azure_monitor(connection_string=connection_string)

    # Project endpoint has the form:   https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name
    # Inference endpoint has the form: https://your-ai-services-account-name.services.ai.azure.com/models
    # Strip the "/api/projects/your-project-name" part and replace with "/models":
    inference_endpoint = f"https://{urlparse(endpoint).netloc}/models"

    with tracer.start_as_current_span(scenario):

        with ChatCompletionsClient(
            endpoint=inference_endpoint,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"],
        ) as client:

            response = client.complete(
                model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
            )

            print(response.choices[0].message.content)
