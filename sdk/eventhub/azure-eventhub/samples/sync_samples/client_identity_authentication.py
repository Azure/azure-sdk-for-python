#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using credentials defined by azure.identity library.

EnvironmentCredential is capable of authenticating as a service principal using a client secret or a certificate, or as
a user with a username and password. Configuration is attempted in this order, using these environment variables:

Service principal with secret:
  - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
  - **AZURE_CLIENT_ID**: the service principal's client ID
  - **AZURE_CLIENT_SECRET**: one of the service principal's client secrets

Service principal with certificate:
  - **AZURE_TENANT_ID**: ID of the service principal's tenant. Also called its 'directory' ID.
  - **AZURE_CLIENT_ID**: the service principal's client ID
  - **AZURE_CLIENT_CERTIFICATE_PATH**: path to a PEM-encoded certificate file including the private key. The
    certificate must not be password-protected.

User with username and password:
  - **AZURE_CLIENT_ID**: the application's client ID
  - **AZURE_USERNAME**: a username (usually an email address)
  - **AZURE_PASSWORD**: that user's password
  - **AZURE_TENANT_ID**: (optional) ID of the service principal's tenant. Also called its 'directory' ID.
    If not provided, defaults to the 'organizations' tenant, which supports only Azure Active Directory work or
    school accounts.

Please refer to azure.identity library for detailed information.

This sample also shows the process of utilizing a different credential object, in this case, DefaultAzureCredential,
both to demonstrate the ease of adjusting authentication, and to surface another method for doing so.
"""

import os
from azure.eventhub import EventData, EventHubProducerClient
from azure.identity import EnvironmentCredential


fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
eventhub_name = os.environ['EVENT_HUB_NAME']

credential = EnvironmentCredential()

# Note: One has other options to specify the credential.  For instance, DefaultAzureCredential.
# Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
# For example user to be logged in can be specified by the environment variable AZURE_USERNAME, consumed via the ManagedIdentityCredential
# Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
# The docs above specify all mechanisms which the defaultCredential internally support.
#
# credential = DefaultAzureCredential()

producer = EventHubProducerClient(fully_qualified_namespace=fully_qualified_namespace,
                                  eventhub_name=eventhub_name,
                                  credential=credential)

with producer:
    event_data_batch = producer.create_batch()
    while True:
        try:
            event_data_batch.add(EventData('Message inside EventBatchData'))
        except ValueError:
            # EventDataBatch object reaches max_size.
            # New EventDataBatch object can be created here to send more data.
            break
    producer.send_batch(event_data_batch)

print('Finished sending.')
