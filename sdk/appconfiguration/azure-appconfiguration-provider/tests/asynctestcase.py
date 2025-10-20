# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.appconfiguration.aio import AzureAppConfigurationClient
from testcase import get_configs
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import AzureAppConfigurationKeyVaultOptions


class AppConfigTestCase(AzureRecordedTestCase):
    async def create_client(self, **kwargs):
        credential = self.get_credential(AzureAppConfigurationClient, is_async=True)
        client = None

        if "connection_string" in kwargs:
            client = AzureAppConfigurationClient.from_connection_string(kwargs["connection_string"])
        else:
            client = AzureAppConfigurationClient(kwargs["endpoint"], credential)

        await setup_configs(client, kwargs.get("keyvault_secret_url"), kwargs.get("keyvault_secret_url2"))
        kwargs["user_agent"] = "SDK/Integration"

        if "endpoint" in kwargs:
            kwargs["credential"] = credential

        if "secret_resolver" not in kwargs and kwargs.get("keyvault_secret_url") and "key_vault_options" not in kwargs:
            kwargs["keyvault_credential"] = credential

        if "key_vault_options" in kwargs:
            key_vault_options = kwargs.pop("key_vault_options")
            if not key_vault_options.secret_resolver:
                key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
            kwargs["key_vault_options"] = key_vault_options

        return await load(**kwargs)

    @staticmethod
    def create_sdk_client(appconfiguration_connection_string):
        return AzureAppConfigurationClient.from_connection_string(
            appconfiguration_connection_string, user_agent="SDK/Integration"
        )

    def create_aad_sdk_client(self, appconfiguration_endpoint_string):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred, user_agent="SDK/Integration")


async def setup_configs(client, keyvault_secret_url, keyvault_secret_url2):
    async with client:
        for config in get_configs(keyvault_secret_url, keyvault_secret_url2):
            await client.set_configuration_setting(config)
