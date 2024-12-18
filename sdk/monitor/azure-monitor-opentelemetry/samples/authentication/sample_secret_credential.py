# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry tracing api and sdk with a Azure Client Secret
Credential. Credentials are used for Azure Active Directory/EntraId Authentication.
"""
# You will need to install azure-identity
from azure.identity import ClientSecretCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace

credential = ClientSecretCredential(
    tenant_id="<tenant_id",
    client_id="<client_id>",
    client_secret="<client_secret>",
)
configure_azure_monitor(
    credential=credential,
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("hello with aad client secret"):
    print("Hello, World!")

input()
