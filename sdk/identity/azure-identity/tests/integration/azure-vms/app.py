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
    credential_user_assigned = ManagedIdentityCredential(
        client_id=os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID")
    )

    client = BlobServiceClient(
        account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_1']}.blob.core.windows.net",
        credential=credential,
    )

    client2 = BlobServiceClient(
        account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_2']}.blob.core.windows.net",
        credential=credential_user_assigned,
    )

    for container in client.list_containers():
        print(container["name"])

    print(f"Successfully acquired token with system-assigned ManagedIdentityCredential")

    for container in client2.list_containers():
        print(container["name"])

    print(f"Successfully acquired token with user-assigned ManagedIdentityCredential")


async def run_async():
    credential = AsyncManagedIdentityCredential()
    credential_user_assigned = AsyncManagedIdentityCredential(
        client_id=os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID")
    )

    client = AsyncBlobServiceClient(
        account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_1']}.blob.core.windows.net",
        credential=credential,
    )
    client2 = AsyncBlobServiceClient(
        account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_2']}.blob.core.windows.net",
        credential=credential_user_assigned,
    )

    async for container in client.list_containers():
        print(container["name"])

    print(f"Successfully acquired token with system-assigned async ManagedIdentityCredential")

    async for container in client2.list_containers():
        print(container["name"])

    print(f"Successfully acquired token with user-assigned async ManagedIdentityCredential")

    await client.close()
    await credential.close()
    await client2.close()
    await credential_user_assigned.close()


if __name__ == "__main__":
    run_sync()
    asyncio.run(run_async())

    print("Passed!")
