# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.core import MatchConditions
from azure.core.exceptions import HttpResponseError
from devtools_testutils import AzureTestCase, PowerShellPreparer
from azure.core.exceptions import (
    ResourceModifiedError,
    ResourceNotFoundError,
    ResourceExistsError,
    AzureError,
)
from azure.appconfiguration import (
    ResourceReadOnlyError,
    AzureAppConfigurationClient,
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
    PERCENTAGE,
    TARGETING,
    TIME_WINDOW,
)
from azure.identity import DefaultAzureCredential

from consts import (
    KEY,
    LABEL,
    TEST_VALUE,
    TEST_CONTENT_TYPE,
    LABEL_RESERVED_CHARS,
    PAGE_SIZE,
    KEY_UUID,
)
from wrapper import app_config_decorator

from uuid import uuid4
import pytest


class AppConfigurationClientTest(AzureTestCase):


    def _assert_same_keys(self, key1, key2):
        assert type(key1) == type(key2)
        try:
            assert key1.key == key2.key
        except AttributeError:
            assert key1.feature_id == key2.feature_id
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

    @app_config_decorator
    def test_update_json_by_value(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key,
            True,
            filters=[
                {
                    "name": PERCENTAGE,
                    "parameters": {
                        "Value": 10,
                        "User": "user1"
                    }
                }
            ]
        )
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = {
            'conditions': {
                'client_filters': [
                    {
                        'name': 'Microsoft.Targeting',
                        'parameters': {
                            'name': 'Microsoft.Targeting',
                            'parameters': {
                                'Audience': {
                                    'DefaultRolloutPercentage': 50,
                                    'Groups': [],
                                    'Users': []
                                }
                            }
                        }
                    }
                ]
            },
            'description': '',
            'enabled': False,
            'id': key,
        }

        set_flag = client.set_configuration_setting(set_flag)
        assert isinstance(set_flag, FeatureFlagConfigurationSetting)
        assert set_flag.enabled == False
        assert set_flag.feature_id.endswith(key)

    @app_config_decorator
    def test_feature_flag_invalid_json(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = []
        received = client.set_configuration_setting(set_flag)

        assert not isinstance(received, FeatureFlagConfigurationSetting)

    @app_config_decorator
    def test_feature_flag_invalid_json_string(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = "hello world"
        received = client.set_configuration_setting(set_flag)

        assert not isinstance(received, FeatureFlagConfigurationSetting)

    @app_config_decorator
    def test_feature_flag_invalid_json_access_properties(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, True)
        set_flag = client.set_configuration_setting(feature_flag)

        set_flag.value = "hello world"
        with pytest.raises(ValueError):
            a = set_flag.enabled
        with pytest.raises(ValueError):
            b = set_flag.filters

    @app_config_decorator
    def test_feature_flag_set_value(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key,
            True,
            filters=[
                {
                    "name": PERCENTAGE,
                    "parameters": {
                        "Value": 10,
                        "User": "user1"
                    }
                }
            ]
        )
        feature_flag.value = {
            "conditions": {
                "client_filters": []
            },
            "enabled": False
        }

        assert feature_flag.value["enabled"] == False

    @app_config_decorator
    def test_feature_flag_set_enabled(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(
            key,
            True,
            filters=[
                {
                    "name": PERCENTAGE,
                    "parameters": {
                        "Value": 10,
                        "User": "user1"
                    }
                }
            ]
        )
        feature_flag.enabled = False

        assert feature_flag.value["enabled"] == False

    @app_config_decorator
    def test_feature_flag_prefix(self, client):
        key = self.get_resource_name("key")
        feature_flag = FeatureFlagConfigurationSetting(key, True)
        assert feature_flag.feature_id.startswith(".appconfig.featureflag/")
