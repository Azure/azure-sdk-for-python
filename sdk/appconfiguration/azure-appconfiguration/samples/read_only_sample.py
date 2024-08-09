# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: read_only_sample.py

DESCRIPTION:
    This sample demos how to set and clear read-only for configuration settings synchronously.

USAGE: python read_only_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting


def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    # Create an app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    print("Set new configuration setting")
    config_setting = ConfigurationSetting(
        key="MyKey", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    updated_config_setting = client.set_configuration_setting(config_setting)
    print("New configuration setting:")
    print(updated_config_setting)
    print("")

    print("Read only configuration setting:")
    # [START set_read_only]
    read_only_config_setting = client.set_read_only(updated_config_setting)
    # [END set_read_only]
    print(read_only_config_setting)
    print("")

    print("Clear read only configuration setting:")
    # [START clear_read_only]
    read_write_config_setting = client.set_read_only(updated_config_setting, False)
    # [END clear_read_only]
    print(read_write_config_setting)
    print("")

    print("Delete configuration setting")
    client.delete_configuration_setting(key="MyKey")


if __name__ == "__main__":
    main()
