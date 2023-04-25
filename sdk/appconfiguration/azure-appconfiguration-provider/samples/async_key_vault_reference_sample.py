# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import asyncio
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector, AzureAppConfigurationKeyVaultOptions
import os
from sample_utilities import get_authority, get_audience, get_credential

async def main():
    endpoint = os.environ.get("AZURE_APPCONFIG_ENDPOINT")
    authority = get_authority(endpoint)
    audience = get_audience(authority)
    credential = get_credential(authority, is_async=True)

    # Connection to Azure App Configuration using AAD and Resolving Key Vault References
    key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
    selects = {SettingSelector(key_filter="*", label_filter="prod")}

    config = await load(endpoint=endpoint, credential=credential, key_vault_options=key_vault_options, selects=selects)

    print(config["secret"])

    await credential.close()
    await config.close()

if __name__ == "__main__":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
