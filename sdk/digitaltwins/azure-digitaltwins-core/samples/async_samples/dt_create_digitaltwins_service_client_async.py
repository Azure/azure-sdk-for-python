# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
Simple example of how to:
    - create a DigitalTwins Service Client using the DigitalTwinsClient constructor

    Preconditions:
    - Environment variables have to be set
"""

import os
import asyncio

from azure.identity.aio import DefaultAzureCredential
from azure.digitaltwins.core.aio import DigitalTwinsClient

async def create_digitaltwins_service_client():
    # DefaultAzureCredential supports different authentication mechanisms and determines
    # the appropriate credential type based of the environment it is executing in.
    # It attempts to use multiple credential types in an order until it finds a working credential.

    # - AZURE_URL: The tenant ID in Azure Active Directory
    url = os.getenv("AZURE_URL")

    # DefaultAzureCredential expects the following three environment variables:
    # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
    # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
    # - AZURE_CLIENT_SECRET: The client secret for the registered application
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)

    print(service_client)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_digitaltwins_service_client())
