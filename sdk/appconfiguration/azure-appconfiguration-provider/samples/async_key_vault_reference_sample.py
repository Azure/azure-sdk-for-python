# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
import sys
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector, AzureAppConfigurationKeyVaultOptions
import os
from sample_utilities import get_authority, get_audience, get_credential
from azure.core.exceptions import ClientAuthenticationError


async def main():
    endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
    authority = get_authority(endpoint)
    audience = get_audience(authority)
    credential = get_credential(authority, is_async=True)

    # Connection to Azure App Configuration using AAD and Resolving Key Vault References
    key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
    selects = {SettingSelector(key_filter="*", label_filter="prod")}

    try:
        config = await load(
            endpoint=endpoint, credential=credential, key_vault_options=key_vault_options, selects=selects
        )
    except ClientAuthenticationError:
        print("Unauthorized")

    print(config.get("secret"))

    await credential.close()
    await config.close()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
