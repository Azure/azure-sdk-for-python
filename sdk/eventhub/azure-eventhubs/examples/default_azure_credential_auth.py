#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using default azure credentials
"""

import os
from azure.eventhub import EventHubClient
from azure.eventhub import EventData
from azure.identity import DefaultAzureCredential, ManagedIdentityCredential 


HOSTNAME = os.environ['EVENT_HUB_HOSTNAME']  # <mynamespace>.servicebus.windows.net
EVENT_HUB = os.environ['EVENT_HUB_NAME']

# Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/identity/azure-identity
# For example user to be logged in can be specified by the environment variable AZURE_USERNAME, consumed via the ManagedIdentityCredential
# Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
# The docs above specify all mechanisms which the defaultCredential internally support.

credential = DefaultAzureCredential()
client = EventHubClient(host=HOSTNAME,
                        event_hub_path=EVENT_HUB,
                        credential=credential)

producer = client.create_producer(partition_id='0')
with producer:
    event = EventData(body='A single message')
    producer.send(event)
