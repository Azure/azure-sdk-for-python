# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import load, SettingSelector
import os
from sample_utilities import get_authority, get_credential, get_client_modifications

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# Connecting to Azure App Configuration using AAD
config = load(endpoint=endpoint, credential=credential, **kwargs)

print(config["message"])

# Connecting to Azure App Configuration using AAD and trim key prefixes
trimmed = ["test."]
config = load(endpoint=endpoint, credential=credential, trim_prefixes=trimmed, **kwargs)

print(config["message"])

# Connection to Azure App Configuration using SettingSelector
selects = [SettingSelector(key_filter="message*")]
config = load(endpoint=endpoint, credential=credential, selects=selects, **kwargs)

print("message found: " + str("message" in config))
print("test.message found: " + str("test.message" in config))
