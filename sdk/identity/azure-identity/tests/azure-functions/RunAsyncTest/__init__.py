# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

import azure.functions as func
from azure.identity.aio import ManagedIdentityCredential
from azure.keyvault.secrets.aio import SecretClient

EXPECTED_VARIABLES = (
    "AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID",
    "AZURE_IDENTITY_TEST_VAULT_URL",
    "MSI_ENDPOINT",
    "MSI_SECRET",
)


async def main(req: func.HttpRequest) -> func.HttpResponse:
    # capture interesting environment variables for debugging
    env = "\n".join(f"{var}: {os.environ.get(var)}" for var in EXPECTED_VARIABLES)

    try:
        credential = ManagedIdentityCredential(
            client_id=os.environ.get("AZURE_IDENTITY_TEST_MANAGED_IDENTITY_CLIENT_ID")
        )

        # do something with Key Vault to verify the credential can get a valid token
        client = SecretClient(os.environ["AZURE_IDENTITY_TEST_VAULT_URL"], credential, logging_enable=True)
        secret = await client.set_secret("managed-identity-test-secret", "value")
        await client.delete_secret(secret.name)

        return func.HttpResponse("test passed")
    except Exception as ex:
        return func.HttpResponse("test failed: " + repr(ex) + "\n" * 3 + env)
