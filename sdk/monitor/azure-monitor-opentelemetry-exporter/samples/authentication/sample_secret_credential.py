# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry tracing api and sdk with a Azure Client Secret
Credential. Credentials are used for Azure Active Directory Authentication. Custom dependencies are
tracked via spans and telemetry is exported to application insights with the AzureMonitorTraceExporter.
"""
# mypy: disable-error-code="attr-defined"
import os

# You will need to install azure-identity
# from azure.identity import ClientSecretCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter


# credential = ClientSecretCredential(
#     tenant_id="<tenant_id",
#     client_id="<client_id>",
#     client_secret="<client_secret>",
# )
cs = "InstrumentationKey=c99f03df-e0fe-c30b-9f1f-a24bdb74506e;EndpointSuffix=applicationinsights.azure.cn;IngestionEndpoint=https://chinanorth3-0.in.applicationinsights.azure.cn/;AADAudience=https://monitor.azure.cn/;ApplicationId=49209aa7-c691-403d-8e9c-e841702580a1"
exporter = AzureMonitorTraceExporter.from_connection_string(
    cs,
)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello with aad client secret"):
    print("Hello, World!")

input()