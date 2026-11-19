# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: send_request_sample_async.py

DESCRIPTION:
    This sample demonstrates how to make custom HTTP requests through a client pipeline asynchronously.

USAGE:
    python send_request_sample_async.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT_STRING: Endpoint URL used to access the Azure App Configuration.
"""

import os
import asyncio
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.core.rest import HttpRequest
from azure.identity.aio import DefaultAzureCredential


async def main():
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    credential = DefaultAzureCredential()
    async with AzureAppConfigurationClient(endpoint, credential) as client:
        request = HttpRequest(
            method="GET",
            url="/kv?api-version=2023-10-01",
        )
        response = await client.send_request(request)
        print(response.status_code)
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
