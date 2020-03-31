import os
from azure.identity import DefaultAzureCredential, KnownAuthorities

class KeyVaultBase:
    credential_type = DefaultAzureCredential
    host_alias_map = {
        'AzureChinaCloud': KnownAuthorities.AZURE_CHINA,
        'AzureGermanCloud': KnownAuthorities.AZURE_GERMANY,
        'AzureUSGovernment': KnownAuthorities.AZURE_GOVERNMENT,
        'AzureCloud': KnownAuthorities.AZURE_PUBLIC_CLOUD,
    }

    # Instantiate a default credential based on the credential_type
    def get_default_credential(self, authority_host_alias=None):
        alias = authority_host_alias or os.environ.get("AZURE_CLOUD")
        authority_host = self.host_alias_map.get(alias, KnownAuthorities.AZURE_PUBLIC_CLOUD)
        return self.credential_type(authority=authority_host)
