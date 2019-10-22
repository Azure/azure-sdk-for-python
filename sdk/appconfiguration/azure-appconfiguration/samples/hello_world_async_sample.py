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

import os
import sys
import asyncio
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.aio import AzureAppConfigurationClient

async def main():
    try:
        CONNECTION_STRING = os.environ['AZURE_APPCONFIG_CONNECTION_STRING']

    except KeyError:
        print("AZURE_APPCONFIG_CONNECTION_STRING must be set.")
        sys.exit(1)

    # Create app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    print("Set new configration setting")
    config_setting = ConfigurationSetting(
        key="MyKey",
        value="my value",
        content_type="my content type",
        tags={"my tag": "my tag value"}
    )
    returned_config_setting = await client.set_configuration_setting(config_setting)
    print("New configration setting:")
    print(returned_config_setting)
    print("")

    print("Get configuration setting")
    fetched_config_setting = await client.get_configuration_setting(
        key="MyKey"
    )
    print("Fetched configration setting:")
    print(fetched_config_setting)
    print("")

    print("Delete configuration setting")
    await client.delete_configuration_setting(
        key="MyKey"
    )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
