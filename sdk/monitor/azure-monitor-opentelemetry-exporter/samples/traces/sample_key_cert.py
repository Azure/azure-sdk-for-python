"""
Examples to show usage of the azure-core-tracing-opentelemetry
with the KeyVault Certificate SDK and exporting to Azure monitor backend.
This example traces calls for creating a certificate using the 
KeyVault Certificate SDK. The telemetry will be collected automatically
and sent to Application Insights via the AzureMonitorTraceExporter
"""

import os

# Declare OpenTelemetry as enabled tracing plugin for Azure SDKs
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan

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

# Example with KeyVault Certificate SDKs
from azure.identity import ClientSecretCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy

tenant_id = "<tenant-id>"
client_id = "<client-id>"
client_secret = "<client-secret>"

credential = ClientSecretCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    client_secret=client_secret
)

vault_url = "https://my-key-vault.vault.azure.net/"

certificate_client = CertificateClient(vault_url=vault_url, credential=credential)

with tracer.start_as_current_span(name="KeyVaultCertificate"):
    create_certificate_poller = certificate_client.begin_create_certificate(
        certificate_name="cert-name", policy=CertificatePolicy.get_default()
    )
    print(create_certificate_poller.result())
