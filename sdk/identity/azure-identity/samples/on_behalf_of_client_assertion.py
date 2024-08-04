# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
FILE: on_behalf_of_client_assertion.py
DESCRIPTION:
    This sample demonstrates the use of OnBehalfOfCredential to authenticate the Key Vault SecretClient using a managed
    identity as the client assertion. More information about the On-Behalf-Of flow can be found here:
    https://learn.microsoft.com/entra/identity-platform/v2-oauth2-on-behalf-of-flow.
USAGE:
    python on_behalf_of_client_assertion.py

**Note** - This sample requires the `azure-keyvault-secrets` package.
"""
# [START obo_client_assertion]
from azure.identity import OnBehalfOfCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient


# Replace the following variables with your own values.
tenant_id = "<tenant_id>"
client_id = "<client_id>"
user_assertion = "<user_assertion>"

managed_identity_credential = ManagedIdentityCredential()


def get_managed_identity_token() -> str:
    # This function should return an access token obtained from a managed identity.
    access_token = managed_identity_credential.get_token("api://AzureADTokenExchange")
    return access_token.token


credential = OnBehalfOfCredential(
    tenant_id=tenant_id,
    client_id=client_id,
    user_assertion=user_assertion,
    client_assertion_func=get_managed_identity_token,
)

client = SecretClient(vault_url="https://<your-key-vault-name>.vault.azure.net/", credential=credential)
# [END obo_client_assertion]
