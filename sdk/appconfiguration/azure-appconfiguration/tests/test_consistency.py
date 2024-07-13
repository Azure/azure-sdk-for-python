# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration import (
    FeatureFlagConfigurationSetting,
    FILTER_PERCENTAGE,
)
from testcase import AppConfigTestCase
from preparers import app_config_decorator
from devtools_testutils import recorded_by_proxy, set_custom_default_matcher
import json
import pytest


class TestAppConfigurationConsistency(AppConfigTestCase):
    @app_config_decorator
    @recorded_by_proxy
    def test_update_json_by_value(self, appconfiguration_connection_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_connection_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key, enabled=True, filters=[{"name": FILTER_PERCENTAGE, "parameters": {"Value": 10, "User": "user1"}}]
        )
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = json.dumps(
            {
                "conditions": {
                    "client_filters": [
                        {
                            "name": "Microsoft.Targeting",
                            "parameters": {
                                "name": "Microsoft.Targeting",
                                "parameters": {"Audience": {"DefaultRolloutPercentage": 50, "Groups": [], "Users": []}},
                            },
                        }
                    ]
                },
                "description": "",
                "enabled": False,
                "id": key,
            }
        )

        set_flag = client.set_configuration_setting(set_flag)
        assert isinstance(set_flag, FeatureFlagConfigurationSetting)
        assert set_flag.enabled == False
        assert set_flag.key.endswith(key)

        client.delete_configuration_setting(set_flag)

    @app_config_decorator
    @recorded_by_proxy
    def test_feature_flag_invalid_json(self, appconfiguration_connection_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_connection_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        set_flag = client.set_configuration_setting(feature_flag)

        with pytest.raises(TypeError):
            set_flag.value = []
            client.set_configuration_setting(set_flag)

        client.delete_configuration_setting(feature_flag)

    @app_config_decorator
    @recorded_by_proxy
    def test_feature_flag_invalid_json_string(self, appconfiguration_connection_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_connection_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = "hello world"
        received = client.set_configuration_setting(set_flag)

        assert isinstance(received, FeatureFlagConfigurationSetting)
        client.delete_configuration_setting(set_flag)

    @app_config_decorator
    @recorded_by_proxy
    def test_feature_flag_invalid_json_access_properties(self, appconfiguration_connection_string):
        # response header <x-ms-content-sha256> and <x-ms-date> are missing in python38.
        set_custom_default_matcher(compare_bodies=False, excluded_headers="x-ms-content-sha256,x-ms-date")
        client = self.create_client(appconfiguration_connection_string)
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = "hello world"
        assert set_flag.enabled == False
        assert set_flag.filters == None
        client.delete_configuration_setting(feature_flag)


class TestAppConfigurationConsistencyUnitTest(AppConfigTestCase):
    def test_feature_flag_set_value(self):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key, enabled=True, filters=[{"name": FILTER_PERCENTAGE, "parameters": {"Value": 10, "User": "user1"}}]
        )
        feature_flag.value = json.dumps({"conditions": {"client_filters": []}, "enabled": False})

        assert feature_flag.enabled == False

    def test_feature_flag_set_enabled(self):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key, enabled=True, filters=[{"name": FILTER_PERCENTAGE, "parameters": {"Value": 10, "User": "user1"}}]
        )
        feature_flag.enabled = False

        temp = json.loads(feature_flag.value)
        assert temp["enabled"] == False

    def test_feature_flag_prefix(self):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, enabled=True)
        assert feature_flag.key.startswith(".appconfig.featureflag/")

    def test_feature_flag_different_key_and_id(self):
        key = f'.appconfig.featureflag/{self.get_resource_name("key")}'
        feature_id = self.get_resource_name("id")
        feature_flag = FeatureFlagConfigurationSetting(feature_id, enabled=True, key=key)

        assert feature_flag.feature_id == feature_id
        assert feature_flag.key == key
