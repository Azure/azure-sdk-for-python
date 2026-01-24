# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: hello_world_sample_entra_id_and_bleu.py

DESCRIPTION:
    This sample demos how to add/update/retrieve/delete configuration settings synchronously using Entra ID
    authentication with Azure Bleu (French Sovereign Cloud).

USAGE: python hello_world_sample_entra_id_and_bleu.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT: Endpoint URL for the Azure App Configuration store in Bleu cloud
       (e.g., https://<your-store-name>.azconfig.sovcloud-api.fr)
    2) AZURE_TENANT_ID: Your Azure tenant ID
    3) AZURE_CLIENT_ID: Your application (client) ID
    4) AZURE_CLIENT_SECRET: Your application client secret
    
    For Azure Bleu (French Sovereign Cloud):
    - Use audience: ["https://appconfig.sovcloud-api.fr/"]
    
    DefaultAzureCredential will attempt multiple authentication methods:
    - Environment variables (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    - Managed Identity
    - Azure CLI (if configured for Bleu cloud)
    - Visual Studio Code
    - Azure PowerShell
    - Interactive browser
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential
from azure.appconfiguration import ConfigurationSetting


def main():
    # [START create_app_config_client_entra_id]
    ENDPOINT = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]

    # Create app config client with Entra ID authentication
    credential = DefaultAzureCredential()
    client = AzureAppConfigurationClient(
        base_url=ENDPOINT, credential=credential, audience="https://appconfig.sovcloud-api.fr/"
    )
    # [END create_app_config_client_entra_id]

    print("Add new configuration setting")
    # [START create_config_setting]
    config_setting = ConfigurationSetting(
        key="MyKey", label="MyLabel", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    added_config_setting = client.set_configuration_setting(config_setting)
    # [END create_config_setting]
    print("New configuration setting:")
    print(added_config_setting)
    print("")

    print("Set configuration setting")
    # [START set_config_setting]
    added_config_setting.value = "new value"
    added_config_setting.content_type = "new content type"
    updated_config_setting = client.set_configuration_setting(added_config_setting)
    # [END set_config_setting]
    print(updated_config_setting)
    print("")

    print("Get configuration setting")
    # [START get_config_setting]
    fetched_config_setting = client.get_configuration_setting(key="MyKey", label="MyLabel")
    # [END get_config_setting]
    print("Fetched configuration setting:")
    print(fetched_config_setting)
    print("")

    print("Delete configuration setting")
    # [START delete_config_setting]
    client.delete_configuration_setting(key="MyKey", label="MyLabel")
    # [END delete_config_setting]


if __name__ == "__main__":
    main()
