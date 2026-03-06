# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import sys

from opentelemetry import trace
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.core.credentials import AzureKeyCredential

from azure.monitor.opentelemetry import configure_azure_monitor

# Set up exporting to Azure Monitor
configure_azure_monitor()

# Example with Azure AI Inference SDK

try:
    endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
    key = os.environ["AZURE_AI_CHAT_KEY"]
except KeyError:
    print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
    print("Set them before running this sample.")
    sys.exit()

is_content_tracing_enabled = os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"]
if not is_content_tracing_enabled:
    print(
        "Content tracing is disabled. Set 'AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED' to 'true' to record prompts and completions."  # pylint: disable=line-too-long
    )

tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span(name="MyApplication"):
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key), model="gpt-4o-mini")

    # Call will be traced
    response = client.complete(
        messages=[
            UserMessage(content="Tell me a joke"),
        ]
    )

    print(response.choices[0].message.content)
