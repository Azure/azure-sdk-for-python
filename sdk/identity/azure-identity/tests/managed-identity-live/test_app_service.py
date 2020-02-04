# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import pytest

from azure.core import PipelineClient
from azure.core.pipeline.policies import ContentDecodePolicy, HttpLoggingPolicy, RedirectPolicy, RetryPolicy
from azure.identity import ManagedIdentityCredential


@pytest.mark.appservice
def test_app_service_live(app_service):
    credential = ManagedIdentityCredential()
    token = credential.get_token("https://vault.azure.net")

    # Validate the token by sending a request to the Key Vault. The request is manual because azure-keyvault-secrets
    # can't authenticate in Cloud Shell; the MSI endpoint there doesn't support AADv2 scopes.
    policies = [ContentDecodePolicy(), RedirectPolicy(), RetryPolicy(), HttpLoggingPolicy()]
    client = PipelineClient(app_service["vault_url"], policies=policies)
    list_secrets = client.get(
        "secrets", headers={"Authorization": "Bearer " + token.token}, params={"api-version": "7.0"}
    )
    with client:
        client._pipeline.run(list_secrets)
