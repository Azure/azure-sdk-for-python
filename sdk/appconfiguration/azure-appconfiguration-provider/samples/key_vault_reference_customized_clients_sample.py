# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import (
    load,
    AzureAppConfigurationKeyVaultOptions,
    SettingSelector
)
import os
from sample_utilities import get_authority, get_credential

endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
key_vault_uri = os.environ.get("AZURE_KEYVAULT_URI")
authority = get_authority(endpoint)
credential = get_credential(authority)

# Connection to Azure App Configuration using AAD with Provided Client
client_configs = {key_vault_uri: {'credential': credential}}
selects = {SettingSelector(key_filter="*", label_filter="prod")}
key_vault_options = AzureAppConfigurationKeyVaultOptions(client_configs=client_configs)
config = load(endpoint=endpoint, credential=credential, key_vault_options=key_vault_options, selects=selects)

print(config["secret"])
