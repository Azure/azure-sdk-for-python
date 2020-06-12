# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.identity import ManagedIdentityCredential

try:
    from azure.keyvault.secrets import SecretClient
except ImportError:
    # prevent pytest discovery failing before it can skip the test
    pass


def test_managed_identity_live(live_managed_identity_config):
    credential = ManagedIdentityCredential(client_id=live_managed_identity_config["client_id"])

    # do something with Key Vault to verify the credential can get a valid token
    client = SecretClient(live_managed_identity_config["vault_url"], credential, logging_enable=True)
    for _ in client.list_properties_of_secrets():
        pass
