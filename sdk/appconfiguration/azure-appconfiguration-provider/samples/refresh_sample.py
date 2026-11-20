# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import time
from sample_utilities import get_authority, get_credential, get_client_modifications
from azure.appconfiguration import (  # type:ignore
    AzureAppConfigurationClient,
    ConfigurationSetting,
)
from azure.appconfiguration.provider import load, WatchKey

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# Setting up a configuration setting with a known value
client = AzureAppConfigurationClient(endpoint, credential)

configuration_setting = ConfigurationSetting(key="message", value="Hello World!")

client.set_configuration_setting(configuration_setting=configuration_setting)


def my_callback_on_fail(_):
    print("Refresh failed!")


# Setting the sentinel key that will be watched for changes. Whenever any monitored configuration is
# updated, the sentinel key should also be updated to signal that a refresh is needed.
sentinel_setting = ConfigurationSetting(key="Sentinel", value="1")
client.set_configuration_setting(configuration_setting=sentinel_setting)

# [START refresh_provider]
import os
from azure.appconfiguration.provider import load, WatchKey

config = load(
    endpoint=endpoint,
    credential=credential,
    refresh_on=[WatchKey("Sentinel")],
    refresh_interval=30,
    **kwargs,
)
# [END refresh_provider]

# Reload with test-specific configuration

print(config["message"])
print(config["my_json"]["key"])

# [START refresh_call]
config.refresh()
# [END refresh_call]

# Updating the configuration setting
configuration_setting.value = "Hello World Updated!"

client.set_configuration_setting(configuration_setting=configuration_setting)

# Updating the sentinel key so that the watched key change is detected on the next refresh
sentinel_setting.value = "2"
client.set_configuration_setting(configuration_setting=sentinel_setting)

# Waiting for the refresh interval to pass
time.sleep(35)

# Refreshing the configuration setting
config.refresh()

# Printing the updated value
print(config["message"])
print(config["my_json"]["key"])

# Waiting for the refresh interval to pass
time.sleep(35)

# Refreshing the configuration setting with no changes
config.refresh()

# Printing the updated value
print(config["message"])
print(config["my_json"]["key"])
