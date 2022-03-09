#!/usr/bin/env python

# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
An example to show authentication using credentials defined by azure.identity library asynchronously.

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
"""

import os
import asyncio
from azure.servicebus import ServiceBusMessage
from azure.servicebus.aio import ServiceBusClient
from azure.identity.aio import EnvironmentCredential


FULLY_QUALIFIED_NAMESPACE = os.environ['SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE']
QUEUE_NAME = os.environ["SERVICE_BUS_QUEUE_NAME"]


async def run():
    credential = EnvironmentCredential()
    # Note: One has other options to specify the credential.  For instance, DefaultAzureCredential.
    # Default Azure Credentials attempt a chained set of authentication methods, per documentation here: https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/identity/azure-identity
    # For example user to be logged in can be specified by the environment variable AZURE_USERNAME, consumed via the ManagedIdentityCredential
    # Alternately, one can specify the AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET to use the EnvironmentCredentialClass.
    # The docs above specify all mechanisms which the defaultCredential internally support.
    # credential = DefaultAzureCredential()

    servicebus_client = ServiceBusClient(FULLY_QUALIFIED_NAMESPACE, credential)
    async with servicebus_client:
        sender = servicebus_client.get_queue_sender(queue_name=QUEUE_NAME)
        async with sender:
            await sender.send_messages(ServiceBusMessage('Single Message'))

    await credential.close()

asyncio.run(run())

print("Send message is done.")
