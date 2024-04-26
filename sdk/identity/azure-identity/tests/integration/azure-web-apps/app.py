# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from azure.identity.aio import ManagedIdentityCredential as AsyncManagedIdentityCredential
from azure.storage.blob.aio import BlobServiceClient as AsyncBlobServiceClient
from flask import Flask


app = Flask(__name__)

EXPECTED_VARIABLES = (
    "IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID",
    "IDENTITY_STORAGE_NAME_1",
    "IDENTITY_STORAGE_NAME_2",
    "MSI_ENDPOINT",
)


@app.route("/")
def index():
    return "OK", 200


@app.route("/sync", methods=["GET"])
def sync_route():

    env = "\n".join(f"{var}: {os.environ.get(var)}" for var in EXPECTED_VARIABLES)
    system_success_message = ""
    try:
        credential_system_assigned = ManagedIdentityCredential()
        credential_user_assigned = ManagedIdentityCredential(
            client_id=os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID")
        )

        client = BlobServiceClient(
            account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_1']}.blob.core.windows.net",
            credential=credential_system_assigned,
        )
        client2 = BlobServiceClient(
            account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_2']}.blob.core.windows.net",
            credential=credential_user_assigned,
        )

        containers = client.list_containers()
        for container in containers:
            print(container["name"])

        system_success_message = "Successfully acquired token with system-assigned ManagedIdentityCredential"

        containers = client2.list_containers()
        for container in containers:
            print(container["name"])

        return f"Successfully acquired tokens with ManagedIdentityCredential", 200

    except Exception as ex:
        return f"Test Failed: {repr(ex)}\n\n{system_success_message}\n\n{env}", 500


@app.route("/async", methods=["GET"])
async def async_route():

    env = "\n".join(f"{var}: {os.environ.get(var)}" for var in EXPECTED_VARIABLES)
    system_success_message = ""
    try:
        credential_system_assigned = AsyncManagedIdentityCredential()
        credential_user_assigned = AsyncManagedIdentityCredential(
            client_id=os.environ.get("IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID")
        )

        client = AsyncBlobServiceClient(
            account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_1']}.blob.core.windows.net",
            credential=credential_system_assigned,
        )
        client2 = AsyncBlobServiceClient(
            account_url=f"https://{os.environ['IDENTITY_STORAGE_NAME_2']}.blob.core.windows.net",
            credential=credential_user_assigned,
        )
        async for container in client.list_containers():
            print(container["name"])

        system_success_message = "Successfully acquired token with system-assigned ManagedIdentityCredential"
        async for container in client2.list_containers():
            print(container["name"])

        await client.close()
        await client2.close()
        await credential_system_assigned.close()
        await credential_user_assigned.close()

        return f"Successfully acquired tokens with async ManagedIdentityCredential", 200
    except Exception as ex:
        return f"Test Failed: {repr(ex)}\n\n{system_success_message}\n\n{env}", 500


if __name__ == "__main__":
    app.run()
