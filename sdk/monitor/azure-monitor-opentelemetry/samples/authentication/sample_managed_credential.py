# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

"""
An example to show an application using Opentelemetry tracing api and sdk with a Azure Managed Identity
Credential. Credentials are used for Azure Active Directory/EntraId Authentication. 
"""
from opentelemetry import trace

# You will need to install azure-identity
from azure.identity import ManagedIdentityCredential
from azure.monitor.opentelemetry import configure_azure_monitor

credential = ManagedIdentityCredential(client_id="<client_id>")
configure_azure_monitor(
    credential=credential,
)

tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("hello with aad managed identity"):
    print("Hello, World!")

input()
