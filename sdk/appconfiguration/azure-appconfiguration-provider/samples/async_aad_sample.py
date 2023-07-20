# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import sys
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector
import os
from sample_utilities import get_authority, get_audience, get_credential
from azure.core.exceptions import ClientAuthenticationError


async def main():
    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    authority = get_authority(endpoint)
    credential = get_credential(authority, is_async=True)

    # Connecting to Azure App Configuration using AAD
    try:
        config = await load(endpoint=endpoint, credential=credential)
    except ClientAuthenticationError:
        print("Unauthorized")
    print(config.get("message"))

    # Connecting to Azure App Configuration using AAD and trim key prefixes
    trimmed = {"test."}
    try:
        config = await load(endpoint=endpoint, credential=credential, trim_prefixes=trimmed)
    except ClientAuthenticationError:
        print("Unauthorized")

    print(config.get("message"))

    # Connection to Azure App Configuration using SettingSelector
    selects = {SettingSelector(key_filter="message*")}
    try:
        config = await load(endpoint=endpoint, credential=credential, selects=selects)
    except ClientAuthenticationError:
        print("Unauthorized")

    print("message found: " + str("message" in config))
    print("test.message found: " + str("test.message" in config))

    await credential.close()
    await config.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
