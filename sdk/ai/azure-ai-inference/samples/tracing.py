# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the storage SDK and exporting to Azure monitor backend.
This example traces calls for creating a container using storage SDK.
The telemetry will be collected automatically and sent to Application
Insights via the AzureMonitorTraceExporter
"""
# mypy: disable-error-code="attr-defined"
import os
import dotenv
# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
dotenv.load_dotenv()
settings.tracing_implementation = OpenTelemetrySpan

# Regular open telemetry usage from here, see https://github.com/open-telemetry/opentelemetry-python
# for details
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# azure monitor trace exporter to send telemetry to appinsights
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
span_processor = BatchSpanProcessor(
    AzureMonitorTraceExporter.from_connection_string(
        os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    )
)
trace.get_tracer_provider().add_span_processor(span_processor)


from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential


client = ChatCompletionsClient(
    endpoint=f"{os.environ['AZURE_OPENAI_ENDPOINT']}/openai/deployments/gpt-4",
    credential=AzureKeyCredential(os.environ["AZURE_OPENAI_API_KEY"]),
    headers={"api-key": os.environ["AZURE_OPENAI_API_KEY"]},
    api_version=os.environ["OPENAI_API_VERSION"]
)
response = client.complete(
    messages=[{"role": "user", "content": "hello world!"}]
)
print(response)
