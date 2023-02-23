# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import os

from azure.keyvault.administration import SettingType
from azure.keyvault.administration.aio import KeyVaultSettingsClient
from azure.identity.aio import DefaultAzureCredential

# ----------------------------------------------------------------------------------------------------------
# Prerequisites:
# 1. A managed HSM (https://docs.microsoft.com/azure/key-vault/managed-hsm/quick-create-cli)
#
# 2. azure-keyvault-administration and azure-identity libraries (pip install these)
#
# 3. Set environment variable MANAGED_HSM_URL with the URL of your managed HSM
#    
# 4. Set up your environment to use azure-identity's DefaultAzureCredential. For more information about how to configure
#    the DefaultAzureCredential, refer to https://aka.ms/azsdk/python/identity/docs#azure.identity.DefaultAzureCredential
#
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Key Vault setting management operations for Managed HSM
#
# 1. List all settings (list_settings)
#
# 2. Update a setting (update_setting)
# ----------------------------------------------------------------------------------------------------------

from dotenv import load_dotenv
load_dotenv()

async def run_sample():
    MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]

    # Instantiate an access control client that will be used to call the service.
    # Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
    credential = DefaultAzureCredential()
    client = KeyVaultSettingsClient(vault_url=MANAGED_HSM_URL, credential=credential)

    # First, let's fetch the settings that apply to our Managed HSM
    # Each setting has a name, value, and type (for example, SettingType.BOOLEAN)
    print("\n.. List Key Vault settings")
    settings = await client.list_settings()
    boolean_setting = None
    async for setting in settings:
        if setting.type == SettingType.BOOLEAN:
            boolean_setting = setting
        print(f"{setting.name}: {setting.value} (type: {setting.type})")

    # Now, let's flip the value of a boolean setting
    # KeyVaultSettingsClient.update_setting accepts booleans and strings, so we can send True or "True", for example
    print(f"\n.. Update value of {boolean_setting.name}")
    opposite_value = not boolean_setting.value
    updated_setting = await client.update_setting(boolean_setting.name, opposite_value)
    print(f"{boolean_setting.name} updated successfully.")
    print(f"Old value: {boolean_setting.value}. New value: {updated_setting.value}")

    # Finally, let's restore the setting's old value
    print(f"\n.. Restore original value of {boolean_setting.name}")
    await client.update_setting(boolean_setting.name, boolean_setting.value)
    print(f"{boolean_setting.name} updated successfully.")


if __name__ == "__main__":
    asyncio.run(run_sample())
