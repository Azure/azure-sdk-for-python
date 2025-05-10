#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Initialize the Online Experimentation Client
"""

import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient


def initialize_client():
    # Create a client with your Online Experimentation workspace endpoint and credentials
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())
    print(f"Client initialized with endpoint: {endpoint}")
    return client


def initialize_client_with_api_version():
    # Create a client with a specific API version
    endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
    client = OnlineExperimentationClient(endpoint, DefaultAzureCredential(), api_version="2025-05-31-preview")

    return client


if __name__ == "__main__":
    initialize_client()
    initialize_client_with_api_version()
