# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import asyncio
import argparse

from azure.identity import ManagedIdentityCredential
from azure.identity.aio import ManagedIdentityCredential as AsyncManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient


def run_sync(identity_type="system"):
    """Run synchronous authentication using the specified identity type.

    :param str identity_type: The type of managed identity to use ("system" or "user")
    """
    if identity_type == "user" and os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID"):
        credential = ManagedIdentityCredential(client_id=os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID"))
        storage_name = os.environ.get("IDENTITY_STORAGE_NAME_USER_ASSIGNED", os.environ.get("IDENTITY_STORAGE_NAME"))
    else:
        # Default to system-assigned identity
        credential = ManagedIdentityCredential()
        storage_name = os.environ.get("IDENTITY_STORAGE_NAME")

    if not storage_name:
        print("Storage account name not found in environment variables")
        return False

    client = BlobServiceClient(
        account_url=f"https://{storage_name}.blob.core.windows.net",
        credential=credential,
    )

    containers = client.list_containers()
    for container in containers:
        print(container["name"])

    print(f"Successfully acquired token with ManagedIdentityCredential (identity_type={identity_type})")
    return True


async def run_async(identity_type="system"):
    """Run asynchronous authentication using the specified identity type.

    :param str identity_type: The type of managed identity to use ("system" or "user")
    """
    if identity_type == "user" and os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID"):
        credential = AsyncManagedIdentityCredential(
            client_id=os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID")
        )
        storage_name = os.environ.get("IDENTITY_STORAGE_NAME_USER_ASSIGNED", os.environ.get("IDENTITY_STORAGE_NAME"))
    else:
        # Default to system-assigned identity
        credential = AsyncManagedIdentityCredential()
        storage_name = os.environ.get("IDENTITY_STORAGE_NAME")

    if not storage_name:
        print("Storage account name not found in environment variables")
        return False

    client = AsyncBlobServiceClient(
        account_url=f"https://{storage_name}.blob.core.windows.net",
        credential=credential,
    )

    async for container in client.list_containers():
        print(container["name"])

    await client.close()
    await credential.close()

    print(f"Successfully acquired token with async ManagedIdentityCredential (identity_type={identity_type})")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test managed identity authentication in AKS")
    parser.add_argument(
        "--identity-type",
        choices=["system", "user", "both"],
        default="both",
        help="Type of managed identity to use (system, user, or both)",
    )
    args = parser.parse_args()

    success = True

    if args.identity_type in ["system", "both"]:
        print("Testing with system-assigned managed identity:")
        if not run_sync("system"):
            success = False

    if args.identity_type in ["user", "both"] and os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID"):
        print("\nTesting with user-assigned managed identity:")
        if not run_sync("user"):
            success = False

    if args.identity_type in ["system", "both"]:
        print("\nTesting with async system-assigned managed identity:")
        if not asyncio.run(run_async("system")):
            success = False

    if args.identity_type in ["user", "both"] and os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID"):
        print("\nTesting with async user-assigned managed identity:")
        if not asyncio.run(run_async("user")):
            success = False

    if success:
        print("\nPassed!")
    else:
        print("\nFailed!")
        exit(1)
