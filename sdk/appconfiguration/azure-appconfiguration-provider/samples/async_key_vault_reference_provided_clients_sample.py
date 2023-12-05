# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector
import os
from sample_utilities import get_authority, get_credential, get_client_modifications


async def main():
    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    key_vault_uri = os.environ.get("KEYVAULT_URL")
    authority = get_authority(endpoint)
    credential = get_credential(authority, is_async=True)
    kwargs = get_client_modifications()

    # Connection to Azure App Configuration using AAD with Provided Client
    client_configs = {key_vault_uri: {"credential": credential}}
    selects = {SettingSelector(key_filter="*", label_filter="prod")}
    config = await load(
        endpoint=endpoint, credential=credential, selects=selects, keyvault_client_configs=client_configs, **kwargs
    )

    print(config["secret"])

    await credential.close()
    await config.close()


if __name__ == "__main__":
    asyncio.run(main())
