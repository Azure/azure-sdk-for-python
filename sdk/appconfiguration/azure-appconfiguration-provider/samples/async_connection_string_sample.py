# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import asyncio
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector
from sample_utilities import get_client_modifications
import os


async def main():
    kwargs = get_client_modifications()
    connection_string = os.environ.get("APPCONFIGURATION_CONNECTION_STRING")

    # Connecting to Azure App Configuration using connection string
    config = await load(connection_string=connection_string, **kwargs)

    print(config["message"])
    print(config["my_json"]["key"])

    # Connecting to Azure App Configuration using connection string and trimmed key prefixes
    trimmed = {"test."}
    config = await load(connection_string=connection_string, trim_prefixes=trimmed, **kwargs)

    print(config["message"])

    # Connection to Azure App Configuration using SettingSelector
    selects = {SettingSelector(key_filter="message*")}
    config = await load(connection_string=connection_string, selects=selects, **kwargs)

    print("message found: " + str("message" in config))
    print("test.message found: " + str("test.message" in config))


if __name__ == "__main__":
    asyncio.run(main())
