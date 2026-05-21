# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from sample_utilities import get_authority, get_audience, get_credential, get_client_modifications
from azure.appconfiguration.provider import load, SettingSelector

endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
authority = get_authority(endpoint)
audience = get_audience(authority)
credential = get_credential(authority)
kwargs = get_client_modifications()

# [START key_vault_reference]
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using Entra ID and Resolving Key Vault References
selects = [SettingSelector(key_filter="*", label_filter="prod")]

config = load(endpoint=endpoint, credential=credential, keyvault_credential=credential, selects=selects, **kwargs)
# [END key_vault_reference]

print(config["secret"])

# [START key_vault_reference_secret_resolver]
from azure.appconfiguration.provider import load


def secret_resolver(uri):
    return "From Secret Resolver"


config = load(endpoint=endpoint, credential=credential, secret_resolver=secret_resolver, **kwargs)
# [END key_vault_reference_secret_resolver]

print(config["secret"])

# [START key_vault_reference_secret_refresh_interval]
from azure.appconfiguration.provider import load

# Refresh Key Vault secrets every 120 seconds
config = load(
    endpoint=endpoint,
    credential=credential,
    keyvault_credential=credential,
    secret_refresh_interval=120,
    **kwargs,
)
# [END key_vault_reference_secret_refresh_interval]

print(config["secret"])
