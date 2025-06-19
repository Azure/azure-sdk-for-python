# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting, FeatureFlagConfigurationSetting
from azure.appconfiguration.provider import SettingSelector, load, AzureAppConfigurationKeyVaultOptions
from azure.appconfiguration.provider._constants import NULL_CHAR
from test_constants import FEATURE_MANAGEMENT_KEY, FEATURE_FLAG_KEY


class AppConfigTestCase(AzureRecordedTestCase):
    def create_aad_client(
        self,
        appconfiguration_endpoint_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter=NULL_CHAR)},
        keyvault_secret_url=None,
        refresh_on=None,
        refresh_interval=30,
        secret_resolver=None,
        key_vault_options=None,
        on_refresh_success=None,
        feature_flag_enabled=False,
        feature_flag_selectors=[SettingSelector(key_filter="*", label_filter=NULL_CHAR)],
        feature_flag_refresh_enabled=False,
    ):
        cred = self.get_credential(AzureAppConfigurationClient)
        client = AzureAppConfigurationClient(appconfiguration_endpoint_string, cred)
        setup_configs(client, keyvault_secret_url)

        if not secret_resolver and keyvault_secret_url and not key_vault_options:
            keyvault_cred = cred
            return load(
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
                feature_flag_selectors=feature_flag_selectors,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        if key_vault_options:
            if not key_vault_options.secret_resolver:
                key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=cred)
            return load(
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
                feature_flag_selectors=feature_flag_selectors,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        return load(
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
            feature_flag_selectors=feature_flag_selectors,
            feature_flag_refresh_enabled=feature_flag_refresh_enabled,
        )

    def create_client(
        self,
        appconfiguration_connection_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter=NULL_CHAR)},
        keyvault_secret_url=None,
        refresh_on=None,
        refresh_interval=30,
        secret_resolver=None,
        key_vault_options=None,
        on_refresh_success=None,
        feature_flag_enabled=False,
        feature_flag_selectors=[SettingSelector(key_filter="*", label_filter=NULL_CHAR)],
        feature_flag_refresh_enabled=False,
    ):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        setup_configs(client, keyvault_secret_url)

        if not secret_resolver and keyvault_secret_url and not key_vault_options:
            return load(
                connection_string=appconfiguration_connection_string,
                trim_prefixes=trim_prefixes,
                selects=selects,
                refresh_on=refresh_on,
                refresh_interval=refresh_interval,
                user_agent="SDK/Integration",
                keyvault_credential=self.get_credential(AzureAppConfigurationClient),
                on_refresh_success=on_refresh_success,
                feature_flag_enabled=feature_flag_enabled,
                feature_flag_selectors=feature_flag_selectors,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        if key_vault_options:
            if not key_vault_options.secret_resolver:
                key_vault_options = AzureAppConfigurationKeyVaultOptions(
                    credential=self.get_credential(AzureAppConfigurationClient)
                )
            return load(
                connection_string=appconfiguration_connection_string,
                trim_prefixes=trim_prefixes,
                selects=selects,
                refresh_on=refresh_on,
                refresh_interval=refresh_interval,
                user_agent="SDK/Integration",
                key_vault_options=key_vault_options,
                on_refresh_success=on_refresh_success,
                feature_flag_enabled=feature_flag_enabled,
                feature_flag_selectors=feature_flag_selectors,
                feature_flag_refresh_enabled=feature_flag_refresh_enabled,
            )
        return load(
            connection_string=appconfiguration_connection_string,
            trim_prefixes=trim_prefixes,
            selects=selects,
            refresh_on=refresh_on,
            refresh_interval=refresh_interval,
            user_agent="SDK/Integration",
            secret_resolver=secret_resolver,
            on_refresh_success=on_refresh_success,
            feature_flag_enabled=feature_flag_enabled,
            feature_flag_selectors=feature_flag_selectors,
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


def setup_configs(client, keyvault_secret_url):
    for config in get_configs(keyvault_secret_url):
        client.set_configuration_setting(config)


def get_configs(keyvault_secret_url):
    configs = []
    configs.append(create_config_setting("message", NULL_CHAR, "hi"))
    configs.append(create_config_setting("message", "dev", "test"))
    configs.append(create_config_setting("my_json", NULL_CHAR, '{"key": "value"}', "application/json"))
    configs.append(create_config_setting("test.trimmed", NULL_CHAR, "key"))
    configs.append(create_config_setting("refresh_message", NULL_CHAR, "original value"))
    configs.append(create_config_setting("non_refreshed_message", NULL_CHAR, "Static"))
    configs.append(create_config_setting("tagged_config", NULL_CHAR, None, tags={"a": "b"}))
    configs.append(create_config_setting("two_tagged", NULL_CHAR, None, tags={"a": "b", "second": "tag"}))
    configs.append(create_config_setting("only_second_tag", NULL_CHAR, None, tags={"second": "tag"}))
    configs.append(
        create_config_setting(
            "complex_tag", NULL_CHAR, None, tags={"Special:Tag": "Value:With:Colons", "Tag@With@At": "Value@With@At"}
        )
    )
    configs.append(
        create_config_setting(
            ".appconfig.featureflag/Alpha",
            NULL_CHAR,
            '{	"id": "Alpha", "description": "", "enabled": false, "conditions": {	"client_filters": []	}}',
            "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
        )
    )
    configs.append(
        create_config_setting(
            ".appconfig.featureflag/TaggedFeatureFlag",
            NULL_CHAR,
            '{	"id": "TaggedFeatureFlag", "description": "", "enabled": false, "conditions": {	"client_filters": []	}}',
            "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
            tags={"a": "b"},
        )
    )
    # Configuration with multiple tags
    configs.append(create_config_setting("multi_tagged", NULL_CHAR, "multi tagged value", tags={"a": "b", "c": "d"}))
    # Configuration with tag that has special characters
    configs.append(create_config_setting("special_chars", NULL_CHAR, "special", tags={"special@tag": "special:value"}))
    # Configuration with no tags
    configs.append(create_config_setting("no_tags", NULL_CHAR, "no tags"))
    # Configuration with tag that has no value
    configs.append(create_config_setting("tag_no_value", NULL_CHAR, "no value", tags={"a": ""}))
    # Configuration with different tag
    configs.append(create_config_setting("different_tag", NULL_CHAR, "different", tags={"different": "tag"}))
    # Configuration with null tag
    configs.append(create_config_setting("null_tag", NULL_CHAR, "null tag", tags={"tag": None}))
    if keyvault_secret_url:
        configs.append(
            create_config_setting(
                "secret",
                "prod",
                '{"uri":"' + keyvault_secret_url + '"}',
                "application/vnd.microsoft.appconfig.keyvaultref+json;charset=utf-8",
            )
        )
    return configs


def create_config_setting(key, label, value, content_type="text/plain", tags=None):
    return ConfigurationSetting(key=key, label=label, value=value, content_type=content_type, tags=tags)


def create_feature_flag_config_setting(key, label, enabled, tags=None):
    return FeatureFlagConfigurationSetting(feature_id=key, label=label, enabled=enabled, tags=tags)


def get_feature_flag(client, feature_id):
    for feature_flag in client[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY]:
        if feature_flag["id"] == feature_id:
            return feature_flag
    return None


def has_feature_flag(client, feature_id, enabled=False):
    feature_flag = get_feature_flag(client, feature_id)
    if feature_flag:
        return feature_flag["enabled"] == enabled
    return False
