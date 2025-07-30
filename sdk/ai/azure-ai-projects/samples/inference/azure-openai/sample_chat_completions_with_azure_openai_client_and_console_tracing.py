# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated
    AzureOpenAI client from the openai package, and perform one chat completion operation.
    The client is already instrumented with console OpenTelemetry tracing.
    For more information, see: https://learn.microsoft.com/azure/ai-foundry/how-to/develop/trace-application

USAGE:
    python sample_chat_completions_with_azure_openai_client_and_console_tracing.py

    Before running the sample:

    pip install azure-ai-projects openai httpx opentelemetry-sdk opentelemetry-instrumentation-openai-v2

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Foundry project.

    Update the Azure OpenAI api-version as needed (see `api_version=` below). Values can be found here:
    https://learn.microsoft.com/azure/ai-foundry/openai/reference#api-specs

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
from azure.core.settings import settings
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from opentelemetry import trace
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace import TracerProvider

settings.tracing_implementation = "opentelemetry"

span_exporter = ConsoleSpanExporter()
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(span_exporter))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)
scenario = os.path.basename(__file__)

OpenAIInstrumentor().instrument()

endpoint = os.environ["PROJECT_ENDPOINT"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

with tracer.start_as_current_span(scenario):

    with DefaultAzureCredential(exclude_interactive_browser_credential=False) as credential:

        with AIProjectClient(endpoint=endpoint, credential=credential) as project_client:

            with project_client.get_openai_client(api_version="2024-10-21") as client:

                response = client.chat.completions.create(
                    model=model_deployment_name,
                    messages=[
                        {
                            "role": "user",
                            "content": "How many feet are in a mile?",
                        },
                    ],
                )

                print(response.choices[0].message.content)
