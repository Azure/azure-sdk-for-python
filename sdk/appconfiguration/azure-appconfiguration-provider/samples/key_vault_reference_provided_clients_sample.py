# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import (
    AzureAppConfigurationProvider,
    AzureAppConfigurationKeyVaultOptions,
    SettingSelector
)
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import os

endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
key_vault_uri = os.environ.get("AZURE_KEYVAULT_URI")
credential = DefaultAzureCredential()

# Connection to Azure App Configuration using AAD with Provided Client
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)
selects = {SettingSelector("*", "prod")}
key_vault_options = AzureAppConfigurationKeyVaultOptions(secret_clients=[
                                                         secret_client])
config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=credential, key_vault_options=key_vault_options, selects=selects)

print(config["secret"])
