# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_custom_span_processor.py

DESCRIPTION:
    This sample demonstrates how to make a custom batch span processor for OpenTelemetry.
    Here, we override the `on_end` method of `BatchSpanProcessor` to filter out specific span names
    and spans containing specific URLs.

    Note: The `azure-storage-blob` package is required. If using the OpenTelemetry exporter for
    Azure Monitor, you must also install the `azure-monitor-opentelemetry-exporter` package.

USAGE:
    python sample_custom_span_processor.py

    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string for your storage account
"""

import os
import re

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.storage.blob import BlobServiceClient
from opentelemetry import trace
from opentelemetry.sdk.trace import ReadableSpan, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


settings.tracing_implementation = "opentelemetry"

# In the below example, we use a simple console exporter, uncomment these lines to use
# the OpenTelemetry exporter for Azure Monitor.
# Example of a trace exporter for Azure Monitor, but you can use anything OpenTelemetry supports.

# from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
# exporter = AzureMonitorTraceExporter(
#     connection_string="the connection string used for your Application Insights resource"
# )


# This is a custom span processor that inherits from BatchSpanProcessor.
# We override the `on_end` method to filter out spans with specific names and URLs, preventing them
# from being exported.
class CustomSpanProcessor(BatchSpanProcessor):

    EXCLUDED_SPAN_NAMES = [".*list_containers.*"]
    EXCLUDED_SPAN_URLS = [".*blob\.core\.windows\.net/\?comp=list.*"]

    def on_end(self, span: ReadableSpan) -> None:
        for regex in self.EXCLUDED_SPAN_NAMES:
            if re.match(regex, span.name):
                return
        if span.attributes:
            if "url.full" in span.attributes:
                for regex in self.EXCLUDED_SPAN_URLS:
                    if isinstance(span.attributes["url.full"], str) and re.match(regex, span.attributes["url.full"]):
                        return
            # Check for the older attribute name as well.
            if "http.url" in span.attributes:
                for regex in self.EXCLUDED_SPAN_URLS:
                    if isinstance(span.attributes["http.url"], str) and re.match(regex, span.attributes["http.url"]):
                        return
        super().on_end(span)


tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Simple console exporter.
exporter = ConsoleSpanExporter()

# Add the custom span processor to the tracer provider.
tracer_provider.add_span_processor(CustomSpanProcessor(exporter))

connection_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
with tracer.start_as_current_span(name="MyApplication"):
    client = BlobServiceClient.from_connection_string(connection_string)

    # The custom span processor will filter out spans produced from the `list_containers` operation.
    containers = client.list_containers()
    print(f"There are {len(list(containers))} containers in the account.")

    # Spans from the following operation will still be exported.
    client.get_service_properties()
