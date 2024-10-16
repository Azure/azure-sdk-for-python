# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: hello_world_sample.py

DESCRIPTION:
    This sample demos how to add/update/retrieve/delete configuration settings synchronously.

USAGE: python hello_world_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
from azure.appconfiguration import ConfigurationSetting


def main():
    # [START create_app_config_client]
    import os
    from azure.appconfiguration import AzureAppConfigurationClient

    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    # Create app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)
    # [END create_app_config_client]

    print("Add new configuration setting")
    # [START create_config_setting]
    config_setting = ConfigurationSetting(
        key="MyKey", label="MyLabel", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    added_config_setting = client.add_configuration_setting(config_setting)
    # [END create_config_setting]
    print("New configuration setting:")
    print(added_config_setting)
    print("")

    print("Set configuration setting")
    # [START set_config_setting]
    added_config_setting.value = "new value"
    added_config_setting.content_type = "new content type"
    updated_config_setting = client.set_configuration_setting(added_config_setting)
    # [END set_config_setting]
    print(updated_config_setting)
    print("")

    print("Get configuration setting")
    # [START get_config_setting]
    fetched_config_setting = client.get_configuration_setting(key="MyKey", label="MyLabel")
    # [END get_config_setting]
    print("Fetched configuration setting:")
    print(fetched_config_setting)
    print("")

    print("Delete configuration setting")
    # [START delete_config_setting]
    client.delete_configuration_setting(key="MyKey", label="MyLabel")
    # [END delete_config_setting]


if __name__ == "__main__":
    main()
