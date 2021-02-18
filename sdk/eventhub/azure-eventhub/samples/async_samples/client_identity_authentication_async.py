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
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from azure.identity.aio import EnvironmentCredential


fully_qualified_namespace = os.environ['EVENT_HUB_HOSTNAME']
eventhub_name = os.environ['EVENT_HUB_NAME']


async def run():
    credential = EnvironmentCredential()
    async with credential:
        producer = EventHubProducerClient(fully_qualified_namespace=fully_qualified_namespace,
                                          eventhub_name=eventhub_name,
                                          credential=credential)

        async with producer:
            event_data_batch = await producer.create_batch()
            while True:
                try:
                    event_data_batch.add(EventData('Message inside EventBatchData'))
                except ValueError:
                    # EventDataBatch object reaches max_size.
                    # New EventDataBatch object can be created here to send more data.
                    break
            await producer.send_batch(event_data_batch)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
print('Finished sending.')
