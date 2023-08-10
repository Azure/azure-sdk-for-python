# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os

from azure.keyvault.administration import KeyVaultSetting, KeyVaultSettingType

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

# Instantiate an access control client that will be used to call the service.
# Here we use the DefaultAzureCredential, but any azure-identity credential can be used.
# [START create_a_settings_client]
from azure.identity import DefaultAzureCredential
from azure.keyvault.administration import KeyVaultSettingsClient

MANAGED_HSM_URL = os.environ["MANAGED_HSM_URL"]
credential = DefaultAzureCredential()
client = KeyVaultSettingsClient(vault_url=MANAGED_HSM_URL, credential=credential)
# [END create_a_settings_client]

# First, let's fetch the settings that apply to our Managed HSM
# Each setting has a name, value, and type (for example, KeyVaultSettingType.BOOLEAN)
print("\n.. List Key Vault settings")
settings = client.list_settings()
boolean_setting = None
for setting in settings:
    if setting.setting_type == KeyVaultSettingType.BOOLEAN:
        boolean_setting = setting
    print(f"{setting.name}: {setting.value} (type: {setting.setting_type})")

# Now, let's flip the value of a boolean setting
# The `value` property is a string, but you can get the value of a boolean setting as a bool with `getboolean`
print(f"\n.. Update value of {boolean_setting.name}")
opposite_value = KeyVaultSetting(name=boolean_setting.name, value=not setting.getboolean())
updated_setting = client.update_setting(opposite_value)
print(f"{boolean_setting.name} updated successfully.")
print(f"Old value: {boolean_setting.value}. New value: {updated_setting.value}")

# Finally, let's restore the setting's old value
print(f"\n.. Restore original value of {boolean_setting.name}")
client.update_setting(boolean_setting)
print(f"{boolean_setting.name} updated successfully.")
