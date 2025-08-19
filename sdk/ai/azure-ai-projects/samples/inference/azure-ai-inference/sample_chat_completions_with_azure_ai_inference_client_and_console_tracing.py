# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AI Foundry Project endpoint, this sample demonstrates how to get an authenticated
    ChatCompletionsClient from the azure.ai.inference package and perform one chat completion
    operation. It also shows how to turn on local console tracing.
    For more information on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_chat_completions_with_azure_ai_inference_client_and_console_tracing.py

    Before running the sample:

    pip install azure-ai-inference azure-identity opentelemetry.sdk

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
    3) AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED - Optional. Set to `true` to trace the content of chat
       messages, which may contain personal data. False by default.
"""

import os
from azure.core.settings import settings
from urllib.parse import urlparse
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.tracing import AIInferenceInstrumentor
from azure.ai.inference.models import UserMessage
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter

settings.tracing_implementation = "opentelemetry"

span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
scenario = os.path.basename(__file__)

AIInferenceInstrumentor().instrument()

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with tracer.start_as_current_span(scenario):

    with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

        # Project endpoint has the form:   https://your-ai-services-account-name.services.ai.azure.com/api/projects/your-project-name
        # Inference endpoint has the form: https://your-ai-services-account-name.services.ai.azure.com/models
        # Strip the "/api/projects/your-project-name" part and replace with "/models":
        inference_endpoint = f"https://{urlparse(endpoint).netloc}/models"

        with ChatCompletionsClient(
            endpoint=inference_endpoint,
            credential=credential,
            credential_scopes=["https://ai.azure.com/.default"],
        ) as client:

            response = client.complete(
                model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
            )

            print(response.choices[0].message.content)
