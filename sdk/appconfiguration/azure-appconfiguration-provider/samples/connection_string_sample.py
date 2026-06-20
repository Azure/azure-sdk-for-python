# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from sample_utilities import get_client_modifications
from azure.appconfiguration.provider import load, SettingSelector

kwargs = get_client_modifications()
connection_string = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

# [START create_provider_connection_string]
import os
from azure.appconfiguration.provider import load

connection_string = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

# Connecting to Azure App Configuration using connection string
config = load(connection_string=connection_string, **kwargs)
# [END create_provider_connection_string]

print(config["message"])
print(config["my_json"]["key"])

# [START trim_prefixes_connection_string]
from azure.appconfiguration.provider import load

# Connecting to Azure App Configuration using connection string and trimmed key prefixes
trimmed = ["test."]
config = load(connection_string=connection_string, trim_prefixes=trimmed, **kwargs)
# [END trim_prefixes_connection_string]

print(config["message"])

# [START setting_selector_connection_string]
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using SettingSelector
selects = [SettingSelector(key_filter="message*")]
config = load(connection_string=connection_string, selects=selects, **kwargs)
# [END setting_selector_connection_string]

print("message found: " + str("message" in config))
print("test.message found: " + str("test.message" in config))
