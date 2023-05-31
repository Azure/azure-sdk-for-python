# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: read_only_async_sample.py
DESCRIPTION:
    This sample demos set_read_only operations for app configuration
USAGE: python read_only_async_sample.py
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
        key="MyKey", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    returned_config_setting = await client.set_configuration_setting(config_setting)
    print("New configuration setting:")
    print_configuration_setting(returned_config_setting)
    print("")

    print("Read only configuration setting:")
    read_only_config_setting = await client.set_read_only(returned_config_setting)
    print_configuration_setting(read_only_config_setting)
    print("")

    print("Clear read only configuration setting:")
    read_write_config_setting = await client.set_read_only(returned_config_setting, False)
    print_configuration_setting(read_write_config_setting)
    print("")

    print("Delete configuration setting")
    await client.delete_configuration_setting(
        key="MyKey",
    )


if __name__ == "__main__":
    asyncio.run(main())
