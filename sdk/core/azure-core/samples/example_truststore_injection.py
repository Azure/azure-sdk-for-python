# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Example: Using truststore with Azure SDK for Python (Sync and Async)

This sample demonstrates how to use the `truststore` library to leverage
operating system certificate stores when working with Azure SDK for Python,
including both synchronous (requests) and asynchronous (aiohttp)
HTTP clients.

Requirements:
    pip install truststore azure-identity azure-storage-blob aiohttp
"""

import ssl
import asyncio
import truststore

# Inject truststore BEFORE importing Azure SDK libraries
truststore.inject_into_ssl()

# Synchronous imports
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

# Asynchronous imports
from azure.identity.aio import DefaultAzureCredential as AsyncDefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


# =============================================================================
# Synchronous Example
# =============================================================================

def sync_blob_storage_example():
    """Synchronous Azure Blob Storage with system certificates."""
    
    account_url = "https://<your-storage-account>.blob.core.windows.net"
    
    credential = DefaultAzureCredential()
    blob_service_client = BlobServiceClient(
        account_url=account_url,
        credential=credential
    )
    
    print("=== Sync Blob Storage ===")
    for container in blob_service_client.list_containers():
        print(f"Container: {container['name']}")
    
    blob_service_client.close()
    credential.close()


# =============================================================================
# Asynchronous Example (uses aiohttp underneath)
# =============================================================================

async def async_blob_storage_example():
    """Asynchronous Azure Blob Storage with system certificates (aiohttp)."""
    
    account_url = "https://<your-storage-account>.blob.core.windows.net"
    
    # Async credential and client - aiohttp will use the injected truststore
    credential = AsyncDefaultAzureCredential()
    blob_service_client = AsyncBlobServiceClient(
        account_url=account_url,
        credential=credential
    )
    
    print("=== Async Blob Storage ===")
    async for container in blob_service_client.list_containers():
        print(f"Container: {container['name']}")
    
    # Always close async clients
    await blob_service_client.close()
    await credential.close()


async def main():
    # Run async example
    await async_blob_storage_example()

if __name__ == "__main__":
    sync_blob_storage_example()
    asyncio.run(main())
    truststore.extract_from_ssl()
