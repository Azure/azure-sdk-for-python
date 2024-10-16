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
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    authority = get_authority(endpoint)
    credential = get_credential(authority, is_async=True)
    kwargs = get_client_modifications()

    # Connection to Azure App Configuration using AAD and Resolving Key Vault References
    selects = [SettingSelector(key_filter="*", label_filter="prod")]

    config = await load(
        endpoint=endpoint, credential=credential, keyvault_credential=credential, selects=selects, **kwargs
    )

    print(config["secret"])

    await credential.close()
    await config.close()


if __name__ == "__main__":
    asyncio.run(main())
