# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import (
    load_provider,
    SettingSelector
)
import os
from sample_utilities import get_authority, get_audience, get_credential

endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
authority = get_authority(endpoint)
audience = get_audience(authority)
credential = get_credential(authority)

# Connecting to Azure App Configuration using AAD
config = load_provider(endpoint=endpoint, credential=credential)

print(config["message"])

# Connecting to Azure App Configuration using AAD and trimmed key prefixes
trimmed = {"test."}
config = load_provider(endpoint=endpoint, credential=credential, trimmed_key_prefixes=trimmed)

print(config["message"])

# Connection to Azure App Configuration using SettingSelector
selects = {SettingSelector("message*", "\0")}
config = load_provider(endpoint=endpoint, credential=credential, selects=selects)

print("message found: " + str("message" in config))
print("test.message found: " + str("test.message" in config))
