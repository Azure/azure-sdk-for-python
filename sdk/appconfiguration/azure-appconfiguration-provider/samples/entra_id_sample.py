# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from sample_utilities import get_authority, get_credential, get_client_modifications
from azure.appconfiguration.provider import load, SettingSelector

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# [START create_provider_aad]
import os
from azure.appconfiguration.provider import load
from azure.identity import DefaultAzureCredential

endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
credential = DefaultAzureCredential()

# Connecting to Azure App Configuration using Entra ID
config = load(endpoint=endpoint, credential=credential)
# [END create_provider_aad]

print(config["message"])

# [START trim_prefixes_aad]
from azure.appconfiguration.provider import load

# Connecting to Azure App Configuration using Entra ID and trim key prefixes
trimmed = ["test."]
config = load(endpoint=endpoint, credential=credential, trim_prefixes=trimmed, **kwargs)
# [END trim_prefixes_aad]

print(config["message"])

# [START setting_selector_aad]
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using SettingSelector
selects = [SettingSelector(key_filter="message*")]
config = load(
    endpoint=endpoint,
    credential=credential,
    selects=selects,
    feature_flag_enabled=True,
    feature_flag_selectors=None,
    **kwargs
)
# [END setting_selector_aad]

print("message found: " + str("message" in config))
print("test.message found: " + str("test.message" in config))
print("feature_flag_enabled found: " + str(config.get("feature_management")))
