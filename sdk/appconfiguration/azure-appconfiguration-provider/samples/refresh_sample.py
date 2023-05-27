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

def my_callback():
    print("Refreshed!")

def my_callback_on_fail():
    print("Refresh failed!")

# Connecting to Azure App Configuration using connection string
refresh_options = AzureAppConfigurationRefreshOptions()
refresh_options.refresh_interval = 1
refresh_options.register(key_filter="message", refresh_all=True)
refresh_options.callback = my_callback
refresh_options.callback_on_fail = my_callback_on_fail
config = load(connection_string=connection_string, refresh_options=refresh_options)

print(config["message"])
print(config["my_json"]["key"])

# Updating the configuration setting
configuration_setting.value = "Hello World Updated!"

client.set_configuration_setting(configuration_setting=configuration_setting)

# Waiting for the refresh interval to pass
time.sleep(2)

# Refreshing the configuration setting
config.refresh()

# Printing the updated value
print(config["message"])
print(config["my_json"]["key"])

# Waiting for the refresh interval to pass
time.sleep(2)

# Refreshing the configuration setting with no changes
config.refresh()

# Printing the updated value
print(config["message"])
print(config["my_json"]["key"])
