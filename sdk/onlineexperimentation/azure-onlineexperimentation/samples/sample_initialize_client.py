#!/usr/bin/env python

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Initialize the Online Experimentation Client
"""

# [START initialize_client]
import os
from azure.identity import DefaultAzureCredential
from azure.onlineexperimentation import OnlineExperimentationClient

# Create a client with your Online Experimentation workspace endpoint and credentials
endpoint = os.environ["AZURE_ONLINEEXPERIMENTATION_ENDPOINT"]
client = OnlineExperimentationClient(endpoint, DefaultAzureCredential())
print(f"Client initialized with endpoint: {endpoint}")
# [END initialize_client]
