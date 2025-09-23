#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Initialize the Online Experimentation Async Client
"""

# [START initialize_async_client]
import os
from azure.identity.aio import DefaultAzureCredential
from azure.onlineexperimentation.aio import OnlineExperimentationClient

# Create a client with your Online Experimentation workspace endpoint and credentials
endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())
print(f"Client initialized with endpoint: {endpoint}")
# [END initialize_async_client]
