# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import asyncio

from azure.identity import ManagedIdentityCredential
from azure.identity.aio import ManagedIdentityCredential as AsyncManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


def run_sync():
    credential = ManagedIdentityCredential()

    client = BlobServiceClient(
        account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME']}.blob.core.windows.net",
        credential=credential,
    )

    containers = client.list_containers()
    for container in containers:
        print(container["name"])

    print(f"Successfully acquired token with ManagedIdentityCredential")


async def run_async():
    credential = AsyncManagedIdentityCredential()

    client = AsyncBlobServiceClient(
        account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME']}.blob.core.windows.net",
        credential=credential,
    )

    async for container in client.list_containers():
        print(container["name"])

    await client.close()
    await credential.close()

    print("Successfully acquired token with async ManagedIdentityCredential")


if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())

    print("Passed!")
