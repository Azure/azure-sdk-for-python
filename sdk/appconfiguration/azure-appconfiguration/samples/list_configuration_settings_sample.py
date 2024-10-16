# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_configuration_settings_sample.py

DESCRIPTION:
    This sample demos how to list configuration settings with optional filters synchronously.

USAGE: python list_configuration_settings_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting


def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    # Create an app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    config_setting1 = ConfigurationSetting(
        key="MyKey1", value="my value1", content_type="my content type", tags={"my tag1": "my tag1 value"}
    )
    config_setting2 = ConfigurationSetting(
        key="MyKey2", value="my value2", content_type="my content type", tags={"my tag2": "my tag2 value"}
    )
    client.set_configuration_setting(config_setting1)
    client.set_configuration_setting(config_setting2)

    print("List configuration settings")
    # [START list_configuration_settings]
    config_settings = client.list_configuration_settings(key_filter="MyKey*", tags_filter=["my tag1=my tag1 value"])
    for config_setting in config_settings:
        print(config_setting)
    # [END list_configuration_settings]

    client.delete_configuration_setting(key="MyKey1")
    client.delete_configuration_setting(key="MyKey2")


if __name__ == "__main__":
    main()
