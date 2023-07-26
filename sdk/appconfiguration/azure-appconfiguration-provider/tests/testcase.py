# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    ConfigurationSetting,
    FeatureFlagConfigurationSetting
)

from azure.appconfiguration.provider import SettingSelector, load

class AppConfigTestCase(AzureRecordedTestCase):

    def create_aad_client(self, appconfiguration_endpoint_string, trim_prefixes=[], selects={SettingSelector(key_filter="*", label_filter="\0")}):
        cred = self.get_credential(AzureAppConfigurationClient)
        client = load(credential=cred, endpoint=appconfiguration_endpoint_string, trim_prefixes=trim_prefixes, selects=selects)
        setup_configs(client._client)
        return client

    def create_client(self, appconfiguration_connection_string, trim_prefixes=[], selects={SettingSelector(key_filter="*", label_filter="\0")}):
        client = load(connection_string=appconfiguration_connection_string, trim_prefixes=trim_prefixes, selects=selects)
        setup_configs(client._client)
        return client

def setup_configs(client):
        client.set_configuration_setting(create_config_setting("message", "\0", "hi"))
        client.set_configuration_setting(create_config_setting("message", "dev", "test"))
        client.set_configuration_setting(create_config_setting("my_json", "\0", "{\"key\": \"value\"}", "application/json"))
        client.set_configuration_setting(create_config_setting("test.trimmed", "\0", "key"))
        client.set_configuration_setting(create_config_setting(".appconfig.featureflag/Alpha", "\0", "{	\"id\": \"Alpha\", \"description\": \"\", \"enabled\": false, \"conditions\": {	\"client_filters\": []	}}", "application/vnd.microsoft.appconfig.ff+json;charset=utf-8"))

def create_config_setting(key, label, value, content_type="text/plain"):
    return ConfigurationSetting(
        key=key,
        label=label,
        value=value,
        content_type=content_type,
    )

def create_feature_flag_config_setting(key, label, enabled):
    return FeatureFlagConfigurationSetting(
        feature_id=key,
        label=label,
        enabled=enabled,
    )
