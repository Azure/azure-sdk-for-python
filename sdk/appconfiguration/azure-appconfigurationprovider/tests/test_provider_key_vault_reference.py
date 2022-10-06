# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfigurationprovider import (
    AzureAppConfigurationProvider,
    SettingSelector,
    AzureAppConfigurationKeyVaultOptions
)
from azure.keyvault.secrets import SecretClient
from devtools_testutils import (
    AzureRecordedTestCase, 
    recorded_by_proxy
)
from azure.appconfiguration import AzureAppConfigurationClient
from preparers import app_config_decorator_aad

class TestAppConfigurationProvider(AzureRecordedTestCase):

    def build_provider_aad(self, endpoint, key_vault_options):
        cred = self.get_credential(AzureAppConfigurationClient)
        return AzureAppConfigurationProvider.load(endpoint=endpoint,credential=cred, selects=[SettingSelector("*", "prod")], key_vault_options=key_vault_options)

    # method: provider_with_key_vault
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_provider_with_key_vault(self, appconfiguration_endpoint_string):
        key_vault_cred = self.get_credential(SecretClient)
        key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=key_vault_cred)
        client = self.build_provider_aad(appconfiguration_endpoint_string, key_vault_options=key_vault_options)
        assert client["secret"] == "my-secret"