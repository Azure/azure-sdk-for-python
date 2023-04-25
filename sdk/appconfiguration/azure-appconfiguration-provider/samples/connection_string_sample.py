# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import (
    load,
    SettingSelector,
    AzureAppConfigurationRefreshOptions,
)
import os

connection_string = os.environ.get("AZURE_APPCONFIG_CONNECTION_STRING")

refresh_options = AzureAppConfigurationRefreshOptions()
refresh_options.register(key_filter="message", refresh_all=True)

# Connecting to Azure App Configuration using connection string
config = load(connection_string=connection_string, refresh_options=refresh_options)

print(config["message"])
print(config["my_json"]["key"])

breakpoint()

config.refresh()

print(config["message"])
