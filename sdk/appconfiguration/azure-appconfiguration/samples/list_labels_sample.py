# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_labels_sample.py

DESCRIPTION:
    This sample demos how to list labels synchronously.

USAGE: python list_labels_sample.py

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
        key="MyKey1", label="my label1", content_type="my content type", tags={"my tag1": "my tag1 value"}
    )
    config_setting2 = ConfigurationSetting(
        key="MyKey2", label="my label2", content_type="my content type", tags={"my tag2": "my tag2 value"}
    )
    client.set_configuration_setting(config_setting1)
    client.set_configuration_setting(config_setting2)

    # [START list_labels]
    print("List all labels in resource")
    config_settings = client.list_labels()
    for config_setting in config_settings:
        print(config_setting)

    print("List labels by exact match")
    config_settings = client.list_labels(name="my label1")
    for config_setting in config_settings:
        print(config_setting)

    print("List labels by wildcard")
    config_settings = client.list_labels(name="my label*")
    for config_setting in config_settings:
        print(config_setting)
    # [END list_labels]

    client.delete_configuration_setting(key="MyKey1", label="my label1")
    client.delete_configuration_setting(key="MyKey2", label="my label2")


if __name__ == "__main__":
    main()
