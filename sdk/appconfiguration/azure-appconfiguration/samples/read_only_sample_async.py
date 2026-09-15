# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: read_only_sample_async.py

DESCRIPTION:
    This sample demos how to set and clear read-only for configuration settings asynchronously.

USAGE: python read_only_sample_async.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT_STRING: Endpoint URL used to access the Azure App Configuration.
"""

import asyncio
import os
from azure.appconfiguration import ConfigurationSetting
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.identity.aio import DefaultAzureCredential


async def main():
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    credential = DefaultAzureCredential()

    # Create an app config client
    client = AzureAppConfigurationClient(endpoint, credential)

    print("Set new configuration setting")
    config_setting = ConfigurationSetting(
        key="MyKey", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    updated_config_setting = await client.set_configuration_setting(config_setting)
    print("New configuration setting:")
    print(updated_config_setting)
    print("")

    print("Read only configuration setting:")
    read_only_config_setting = await client.set_read_only(updated_config_setting)
    print(read_only_config_setting)
    print("")

    print("Clear read only configuration setting:")
    read_write_config_setting = await client.set_read_only(updated_config_setting, False)
    print(read_write_config_setting)
    print("")

    print("Delete configuration setting")
    await client.delete_configuration_setting(key="MyKey")
    await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
