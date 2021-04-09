# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import AzureAuthorityHosts, DefaultAzureCredential


class KeyVaultBase:
    credential_type = DefaultAzureCredential
    host_alias_map = {
        "AzureChinaCloud": (AzureAuthorityHosts.AZURE_CHINA, "2016-10-01"),
        "AzureGermanCloud": (AzureAuthorityHosts.AZURE_GERMANY, "2016-10-01"),
        "AzureUSGovernment": (AzureAuthorityHosts.AZURE_GOVERNMENT, "2016-10-01"),
        "AzureCloud": (AzureAuthorityHosts.AZURE_PUBLIC_CLOUD, "7.1"),
    }

    def get_client_args(self, authority_host_alias=None):
        alias = authority_host_alias or os.environ.get("AZURE_CLOUD", "AzureCloud")
        authority_host, api_version = self.host_alias_map[alias]
        credential = self.credential_type(authority=authority_host)
        return {"api_version": api_version, "credential": credential, "vault_url": os.environ["AZURE_PROJECT_URL"]}
