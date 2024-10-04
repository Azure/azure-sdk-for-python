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
from azure.appconfiguration.provider import SettingSelector, AzureAppConfigurationKeyVaultOptions
from test_constants import FEATURE_MANAGEMENT_KEY, FEATURE_FLAG_KEY


class AppConfigTestCase(AzureRecordedTestCase):
    async def create_aad_client(
        self,
        appconfiguration_endpoint_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
        keyvault_secret_url=None,
        refresh_on=None,
        refresh_interval=30,
        secret_resolver=None,
        key_vault_options=None,
        on_refresh_success=None,
        feature_flag_enabled=False,
        feature_flag_refresh_enabled=False,
    ):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)

        if not secret_resolver and keyvault_secret_url:
            keyvault_cred = cred
        else:
            keyvault_cred = None

        client = AzureAppConfigurationClient(appconfiguration_endpoint_string, cred)
        await setup_configs(client, keyvault_secret_url)

        if not secret_resolver and keyvault_secret_url and not key_vault_options:
            keyvault_cred = cred
            return await load(
                credential=cred,
                endpoint=appconfiguration_endpoint_string,
                trim_prefixes=trim_prefixes,
                selects=selects,
                refresh_on=refresh_on,
                refresh_interval=refresh_interval,
                user_agent="SDK/Integration",
                keyvault_credential=keyvault_cred,
                on_refresh_success=on_refresh_success,
                feature_flag_enabled=feature_flag_enabled,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        if key_vault_options:
            if not key_vault_options.secret_resolver:
                key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=cred)
            return await load(
                credential=cred,
                endpoint=appconfiguration_endpoint_string,
                trim_prefixes=trim_prefixes,
                selects=selects,
                refresh_on=refresh_on,
                refresh_interval=refresh_interval,
                user_agent="SDK/Integration",
                key_vault_options=key_vault_options,
                on_refresh_success=on_refresh_success,
                feature_flag_enabled=feature_flag_enabled,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        return await load(
            credential=cred,
            endpoint=appconfiguration_endpoint_string,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_on=refresh_on,
            refresh_interval=refresh_interval,
            user_agent="SDK/Integration",
            secret_resolver=secret_resolver,
            on_refresh_success=on_refresh_success,
            feature_flag_enabled=feature_flag_enabled,
            feature_flag_refresh_enabled=feature_flag_refresh_enabled,
        )

    async def create_client(
        self,
        appconfiguration_connection_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
        keyvault_secret_url=None,
        refresh_on=None,
        refresh_interval=30,
        secret_resolver=None,
        key_vault_options=None,
        on_refresh_success=None,
        feature_flag_enabled=False,
        feature_flag_refresh_enabled=False,
    ):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        await setup_configs(client, keyvault_secret_url)

        if not secret_resolver and keyvault_secret_url and not key_vault_options:
            return await load(
                connection_string=appconfiguration_connection_string,
                trim_prefixes=trim_prefixes,
                selects=selects,
                refresh_on=refresh_on,
                refresh_interval=refresh_interval,
                user_agent="SDK/Integration",
                keyvault_credential=self.get_credential(AzureAppConfigurationClient, is_async=True),
                on_refresh_success=on_refresh_success,
                feature_flag_enabled=feature_flag_enabled,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        if key_vault_options:
            if not key_vault_options.secret_resolver:
                key_vault_options = AzureAppConfigurationKeyVaultOptions(
                    credential=self.get_credential(AzureAppConfigurationClient, is_async=True)
                )
            return await load(
                connection_string=appconfiguration_connection_string,
                trim_prefixes=trim_prefixes,
                selects=selects,
                refresh_on=refresh_on,
                refresh_interval=refresh_interval,
                user_agent="SDK/Integration",
                key_vault_options=key_vault_options,
                on_refresh_success=on_refresh_success,
                feature_flag_enabled=feature_flag_enabled,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        return await load(
            connection_string=appconfiguration_connection_string,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_on=refresh_on,
            refresh_interval=refresh_interval,
            user_agent="SDK/Integration",
            secret_resolver=secret_resolver,
            on_refresh_success=on_refresh_success,
            feature_flag_enabled=feature_flag_enabled,
            feature_flag_refresh_enabled=feature_flag_refresh_enabled,
        )

    @staticmethod
    def create_sdk_client(appconfiguration_connection_string):
        return AzureAppConfigurationClient.from_connection_string(
            appconfiguration_connection_string, user_agent="SDK/Integration"
        )

    def create_aad_sdk_client(self, appconfiguration_endpoint_string):
        cred = self.get_credential(AzureAppConfigurationClient)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred, user_agent="SDK/Integration")


async def setup_configs(client, keyvault_secret_url):
    async with client:
        for config in get_configs(keyvault_secret_url):
            await client.set_configuration_setting(config)


def has_feature_flag(client, feature_id, enabled=False):
    for feature_flag in client[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY]:
        if feature_flag["id"] == feature_id:
            return feature_flag["enabled"] == enabled
    return False
