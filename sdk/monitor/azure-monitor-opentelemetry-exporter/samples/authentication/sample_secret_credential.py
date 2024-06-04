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
from azure.identity import ClientSecretCredential
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter


credential = ClientSecretCredential(
    tenant_id="<tenant_id",
    client_id="<client_id>",
    client_secret="<client_secret>",
)
exporter = AzureMonitorTraceExporter.from_connection_string(
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"],
    credential=credential
)

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_processor = BatchSpanProcessor(exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

with tracer.start_as_current_span("hello with aad client secret"):
    print("Hello, World!")
