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
from azure.identity import DefaultAzureCredential
import os

endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
credential = DefaultAzureCredential()

# Connection to Azure App Configuration using AAD and Resolving Key Vault References
key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
selects = {SettingSelector("*", "prod")}

config = AzureAppConfigurationProvider.load(
    endpoint=endpoint, credential=credential, key_vault_options=key_vault_options, selects=selects)

print(config["secret"])
