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
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from consts import (
    KEY,
    LABEL,
    TEST_VALUE,
    TEST_CONTENT_TYPE,
)


class AppConfigTestCase(AzureRecordedTestCase):
    def create_aad_client(self, appconfiguration_endpoint_string):
        cred = self.get_credential(AzureAppConfigurationClient)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred)

    def create_client(self, appconfiguration_connection_string):
        return AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)

    def create_config_setting(self):
        return ConfigurationSetting(
            key=KEY,
            label=LABEL,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )

    def create_config_setting_no_label(self):
        return ConfigurationSetting(
            key=KEY,
            label=None,
            value=TEST_VALUE,
            content_type=TEST_CONTENT_TYPE,
            tags={"tag1": "tag1", "tag2": "tag2"},
        )

    def add_for_test(self, client, config_setting):
        key = config_setting.key
        label = config_setting.label
        exist = bool(list(client.list_configuration_settings(key_filter=key, label_filter=label)))
        if exist:
            client.delete_configuration_setting(key=config_setting.key, label=config_setting.label)
        return client.add_configuration_setting(config_setting)

    def set_up(self, appconfiguration_string, is_aad=False):
        if is_aad:
            self.client = self.create_aad_client(appconfiguration_string)
        else:
            self.client = self.create_client(appconfiguration_string)
        self.add_for_test(self.client, self.create_config_setting())
        self.add_for_test(self.client, self.create_config_setting_no_label())

    def tear_down(self):
        if self.client is not None:
            config_settings = self.client.list_configuration_settings()
            for config_setting in config_settings:
                self.client.delete_configuration_setting(key=config_setting.key, label=config_setting.label)
        else:
            raise ValueError("Client is None!")

    def _order_dict(self, d):
        from collections import OrderedDict

        new = OrderedDict()
        for k, v in d.items():
            new[k] = str(v)
        return new

    def _assert_same_keys(self, key1, key2):
        assert type(key1) == type(key2)
        assert key1.key == key2.key
        assert key1.label == key2.label
        assert key1.content_type == key2.content_type
        assert key1.tags == key2.tags
        assert key1.etag != key2.etag
        if isinstance(key1, FeatureFlagConfigurationSetting):
            assert key1.enabled == key2.enabled
            assert len(key1.filters) == len(key2.filters)
        elif isinstance(key1, SecretReferenceConfigurationSetting):
            assert key1.secret_id == key2.secret_id
        else:
            assert key1.value == key2.value
