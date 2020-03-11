# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: hello_world_async_sample.py
DESCRIPTION:
    This sample demos set/get/delete operations for app configuration
USAGE: python hello_world_async_sample.py
"""

import asyncio
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.aio import AzureAppConfigurationClient
from util import print_configuration_setting, get_connection_string

async def main():
    CONNECTION_STRING = get_connection_string()

    # Create app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    print("Set new configuration setting")
    config_setting = ConfigurationSetting(
        key="MyKey",
        value="my value",
        content_type="my content type",
        tags={"my tag": "my tag value"}
    )
    returned_config_setting = await client.set_configuration_setting(config_setting)
    print("New configuration setting:")
    print_configuration_setting(returned_config_setting)
    print("")

    print("Get configuration setting")
    fetched_config_setting = await client.get_configuration_setting(
        key="MyKey"
    )
    print("Fetched configuration setting:")
    print_configuration_setting(fetched_config_setting)
    print("")

    print("Delete configuration setting")
    await client.delete_configuration_setting(
        key="MyKey"
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
