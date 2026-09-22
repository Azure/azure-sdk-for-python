# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
import asyncio
from azure.appconfiguration.provider import SettingSelector


async def main():
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]

    # [START create_provider_entra_id_async]
    from azure.appconfiguration.provider.aio import load

    # Connecting to Azure App Configuration using Entra ID
    config = await load(endpoint=endpoint, credential=credential)
    print(config["message"])

    await credential.close()
    await config.close()
    # [END create_provider_entra_id_async]

    # [START trim_prefixes_entra_id_async]
    # Connecting to Azure App Configuration using Entra ID and trim key prefixes
    trimmed = ["test."]
    config = await load(endpoint=endpoint, credential=credential, trim_prefixes=trimmed)
    # [END trim_prefixes_entra_id_async]

    print(config["message"])

    await credential.close()
    await config.close()

    # Connection to Azure App Configuration using SettingSelector
    selects = [SettingSelector(key_filter="message*")]
    config = await load(endpoint=endpoint, credential=credential, selects=selects)

    print("message found: " + str("message" in config))
    print("test.message found: " + str("test.message" in config))

    await credential.close()
    await config.close()


if __name__ == "__main__":
    asyncio.run(main())
