#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Initialize the Online Experimentation Client
"""

# [START initialize_async_client]
import os
from azure.identity.aio import DefaultAzureCredential
from azure.onlineexperimentation.aio import OnlineExperimentationClient

def initialize_async_client():
    # Create a client with your Online Experimentation workspace endpoint and credentials
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())
    print(f"Client initialized with endpoint: {endpoint}")
    return client
# [END initialize_async_client]

def initialize_client_with_api_version():
    # Create a client with a specific API version
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential(), api_version="2025-05-31-preview")

    return client


if __name__ == "__main__":
    initialize_async_client()
    initialize_client_with_api_version()
