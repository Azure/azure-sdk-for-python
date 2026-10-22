# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_authentication_async.py

DESCRIPTION:
    This sample demonstrates how to authenticate the LogsIngestionClient.

    Note: This sample requires the azure-identity library.

USAGE:
    python sample_authentication_async.py
"""

import asyncio


async def authenticate_public_cloud():
    # [START create_client_public_cloud_async]
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.ingestion.aio import LogsIngestionClient

    credential = DefaultAzureCredential()
    endpoint = "https://example.ingest.monitor.azure.com"
    client = LogsIngestionClient(endpoint, credential)
    # [END create_client_public_cloud_async]


async def authenticate_sovereign_cloud():
    # [START create_client_sovereign_cloud_async]
    from azure.identity import AzureAuthorityHosts
    from azure.identity.aio import DefaultAzureCredential
    from azure.monitor.ingestion.aio import LogsIngestionClient

    credential = DefaultAzureCredential(authority=AzureAuthorityHosts.AZURE_GOVERNMENT)
    endpoint = "https://example.ingest.monitor.azure.us"
    client = LogsIngestionClient(endpoint, credential, credential_scopes=["https://monitor.azure.us/.default"])
    # [END create_client_sovereign_cloud_async]


async def main():
    await authenticate_public_cloud()
    await authenticate_sovereign_cloud()


if __name__ == "__main__":
    asyncio.run(main())
