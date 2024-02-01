# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import azure.functions as func
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient

EXPECTED_VARIABLES = (
    "IDENTITY_USER_DEFINED_IDENTITY_CLIENT_ID",
    "IDENTITY_STORAGE_NAME_1",
    "IDENTITY_STORAGE_NAME_2",
    "MSI_ENDPOINT",
)


def main(req: func.HttpRequest) -> func.HttpResponse:
    # capture interesting environment variables for debugging
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

        return func.HttpResponse("Successfully acquired tokens with ManagedIdentityCredential")
    except Exception as ex:
        return func.HttpResponse(f"Test Failed: {repr(ex)}\n\n{system_success_message}\n\n{env}", status_code=500)
