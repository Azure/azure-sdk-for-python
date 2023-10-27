# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: hello_world_advanced_async_sample.py

DESCRIPTION:
    This sample demos more advanced scenarios including add/set with label/list operations for app configuration

USAGE: python hello_world_advanced_async_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import asyncio
import os
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.aio import AzureAppConfigurationClient
from util import print_configuration_setting


async def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    # Create app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    print("Add new configuration setting")
    config_setting = ConfigurationSetting(
        key="MyKey", label="MyLabel", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    added_config_setting = await client.add_configuration_setting(config_setting)
    print("New configuration setting:")
    print_configuration_setting(added_config_setting)
    print("")

    print("Set configuration setting")
    added_config_setting.value = "new value"
    added_config_setting.content_type = "new content type"
    updated_config_setting = await client.set_configuration_setting(added_config_setting)
    print_configuration_setting(updated_config_setting)
    print("")

    print("List configuration settings")
    # [START list_config_setting]
    config_settings = client.list_configuration_settings(label_filter="MyLabel")
    async for item in config_settings:
        print_configuration_setting(item)
    # [END list_config_setting]

    print("Delete configuration setting")
    await client.delete_configuration_setting(
        key="MyKey",
        label="MyLabel",
    )


if __name__ == "__main__":
    asyncio.run(main())
