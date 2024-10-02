# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""
An example to show an application using Opentelemetry tracing api and sdk with a Azure Managed Identity
Credential. Credentials are used for Azure Active Directory/EntraId Authentication. 
"""
# You will need to install azure-identity
from azure.identity import ManagedIdentityCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace


credential = ManagedIdentityCredential(client_id="<client_id>")
configure_azure_monitor(
    credential=credential,
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("hello with aad managed identity"):
    print("Hello, World!")

input()
