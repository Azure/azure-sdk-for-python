# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from os import environ

from opentelemetry import trace
from azure.monitor.opentelemetry import configure_azure_monitor
from azure.storage.blob import BlobServiceClient

# Set up exporting to Azure Monitor
configure_azure_monitor()

# Example with Storage SDKs


tracer = trace.get_tracer(__name__)
with tracer.start_as_current_span(name="MyApplication"):
    client = BlobServiceClient.from_connection_string(environ["AZURE_STORAGE_ACCOUNT_CONNECTION_STRING"])
    client.create_container("mycontainer")  # Call will be traced
