# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.appconfiguration.provider import load, WatchKey
from azure.appconfiguration import (  # type:ignore
    AzureAppConfigurationClient,
    ConfigurationSetting,
)
from sample_utilities import get_client_modifications
import os
import time

kwargs = get_client_modifications()
connection_string = os.environ.get("APPCONFIGURATION_CONNECTION_STRING")

# Setting up a configuration setting with a known value
client = AzureAppConfigurationClient.from_connection_string(connection_string)

configuration_setting = ConfigurationSetting(key="message", value="Hello World!")

client.set_configuration_setting(configuration_setting=configuration_setting)


def my_callback_on_fail(error):
    print("Refresh failed!")


# Connecting to Azure App Configuration using connection string, and refreshing when the configuration setting message changes
config = load(
    connection_string=connection_string,
    refresh_on=[WatchKey("message")],
    refresh_interval=1,
    on_refresh_error=my_callback_on_fail,
    **kwargs,
)

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
