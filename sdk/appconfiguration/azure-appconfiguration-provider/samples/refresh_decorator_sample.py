# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import load, AzureAppConfigurationRefreshOptions
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    ConfigurationSetting,
)
import os
import time

connection_string = os.environ.get("AZURE_APPCONFIG_CONNECTION_STRING")

# Setting up a configuration setting with a known value
client = AzureAppConfigurationClient.from_connection_string(connection_string)

configuration_setting = ConfigurationSetting(key="message", value="Hello World!")

client.set_configuration_setting(configuration_setting=configuration_setting)

# Connecting to Azure App Configuration using connection string
refresh_options = AzureAppConfigurationRefreshOptions()
refresh_options.refresh_interval = 1
refresh_options.register(key_filter="message")
config = load(connection_string=connection_string, refresh_options=refresh_options)


@config.refresh_configuration_settings
def print_configurations(config):
    time.sleep(2)
    print(config["message"])
    print(config["my_json"]["key"])


print_configurations(config)

# Updating the configuration setting
configuration_setting.value = "Hello World Updated!"

client.set_configuration_setting(configuration_setting=configuration_setting)

print_configurations(config)
