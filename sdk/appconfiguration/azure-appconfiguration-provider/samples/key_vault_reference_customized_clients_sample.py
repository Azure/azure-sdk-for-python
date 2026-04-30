# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from sample_utilities import get_authority, get_credential, get_client_modifications
from azure.appconfiguration.provider import load, SettingSelector

endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
key_vault_uri = os.environ["KEYVAULT_URL"]
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# [START key_vault_reference_customized_clients]
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using Entra ID with Provided Client
client_configs = {key_vault_uri: {"credential": credential}}
selects = [SettingSelector(key_filter="*", label_filter="prod")]
config = load(
    endpoint=endpoint,
    credential=credential,
    keyvault_client_configs=client_configs,
    selects=selects,
    **kwargs,
)
# [END key_vault_reference_customized_clients]

print(config["secret"])
