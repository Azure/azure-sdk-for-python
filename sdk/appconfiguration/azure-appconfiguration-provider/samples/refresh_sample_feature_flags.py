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
    FeatureFlagConfigurationSetting,
)
from azure.appconfiguration.provider import load, WatchKey

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# Setting up a configuration setting with a known value
client = AzureAppConfigurationClient(endpoint, credential)

configuration_setting = ConfigurationSetting(key="message", value="Hello World!")
json_setting = ConfigurationSetting(key="my_json", value='{"key": "value"}', content_type="application/json")
feature_flag_setting = FeatureFlagConfigurationSetting("Beta", enabled=True)

client.set_configuration_setting(configuration_setting=configuration_setting)
client.set_configuration_setting(configuration_setting=json_setting)
client.set_configuration_setting(configuration_setting=feature_flag_setting)


def get_feature_flag(config, flag_id):
    for flag in config["feature_management"]["feature_flags"]:
        if flag["id"] == flag_id:
            return flag
    raise KeyError(flag_id)


def my_callback_on_fail(_):
    print("Refresh failed!")


# [START refresh_feature_flags]
import os
from azure.appconfiguration.provider import load, WatchKey

config = load(
    endpoint=endpoint,
    credential=credential,
    refresh_on=[WatchKey("message")],
    refresh_on_feature_flags=True,
    refresh_interval=30,
    feature_flag_enabled=True,
    feature_flag_refresh_enabled=True,
    **kwargs,
)
# [END refresh_feature_flags]

# Reload with test-specific configuration

print(config["message"])
print(config["my_json"]["key"])
print(get_feature_flag(config, "Beta"))

# Updating the configuration setting
feature_flag_setting.enabled = False

client.set_configuration_setting(configuration_setting=feature_flag_setting)

# Waiting for the refresh interval to pass
time.sleep(35)

# Refreshing the configuration setting
config.refresh()

# Printing the updated value
print(config["message"])
print(config["my_json"]["key"])
print(get_feature_flag(config, "Beta"))

# Waiting for the refresh interval to pass
time.sleep(35)

# Refreshing the configuration setting with no changes
config.refresh()

# Printing the updated value
print(config["message"])
print(config["my_json"]["key"])
print(get_feature_flag(config, "Beta"))
