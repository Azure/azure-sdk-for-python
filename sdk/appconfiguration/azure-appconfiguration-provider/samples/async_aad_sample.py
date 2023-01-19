# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
from azure.appconfiguration.provider.aio import load_provider
from azure.appconfiguration.provider import SettingSelector
from azure.identity.aio import DefaultAzureCredential
import os

async def main():
    endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
    credential = DefaultAzureCredential()

    # Connecting to Azure App Configuration using AAD
    config = await load_provider(endpoint=endpoint, credential=credential)
    print(config["message"])

    await credential.close()
    await config.close()

if __name__ == "__main__":
    asyncio.run(main())
