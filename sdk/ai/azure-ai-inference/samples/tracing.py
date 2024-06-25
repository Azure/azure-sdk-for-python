# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

import dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
from azure.core.credentials import AzureKeyCredential
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import StreamingChatCompletions
settings.tracing_implementation = OpenTelemetrySpan

dotenv.load_dotenv()

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)

client = ChatCompletionsClient(
    endpoint=f"{os.environ['AZURE_OPENAI_ENDPOINT']}/openai/deployments/gpt-4",
    credential=AzureKeyCredential(os.environ["AZURE_OPENAI_API_KEY"]),
    headers={"api-key": os.environ["AZURE_OPENAI_API_KEY"]},
    api_version=os.environ["OPENAI_API_VERSION"]
)
response = client.complete(
    messages=[{"role": "user", "content": "hello world!"}],
    stream=True,
)
assert isinstance(response, StreamingChatCompletions)
for result in response:
    print(result)
