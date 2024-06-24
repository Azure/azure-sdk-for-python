# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import unittest
import pytest
from unittest.mock import Mock
from azure.appconfiguration.provider import WatchKey
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator_aad
from testcase import AppConfigTestCase, has_feature_flag
from test_constants import FEATURE_MANAGEMENT_KEY


class TestAppConfigurationProvider(AppConfigTestCase, unittest.TestCase):
    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_aad_client(
            appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_on=[WatchKey("refresh_message")],
            refresh_interval=1,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
            feature_flag_refresh_enabled=True,
        )
        assert client["refresh_message"] == "original value"
        assert client["my_json"]["key"] == "value"
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")

        setting = client._client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        feature_flag = client._client.get_configuration_setting(key=".appconfig.featureflag/Alpha")
        feature_flag.enabled = True
        client._client.set_configuration_setting(setting)
        client._client.set_configuration_setting(feature_flag)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "updated value"
        assert has_feature_flag(client, "Alpha", True)
        assert mock_callback.call_count == 1

        setting.value = "original value"
        feature_flag.enabled = False
        client._client.set_configuration_setting(setting)
        client._client.set_configuration_setting(feature_flag)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert has_feature_flag(client, "Alpha", False)
        assert mock_callback.call_count == 2

        setting.value = "updated value 2"
        feature_flag.enabled = True
        client._client.set_configuration_setting(setting)
        client._client.set_configuration_setting(feature_flag)

        # Not waiting for the refresh interval to pass
        client.refresh()
        assert client["refresh_message"] == "original value"
        assert has_feature_flag(client, "Alpha", False)
        assert mock_callback.call_count == 2

        setting.value = "original value"
        client._client.set_configuration_setting(setting)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert mock_callback.call_count == 2

    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_empty_refresh(self, appconfiguration_endpoint_string, appconfiguration_keyvault_secret_url):
        mock_callback = Mock()
        client = self.create_aad_client(
            appconfiguration_endpoint_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            on_refresh_success=mock_callback,
            feature_flag_enabled=True,
        )
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert client["my_json"]["key"] == "value"
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")

        setting = client._client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        client._client.set_configuration_setting(setting)
        static_setting = client._client.get_configuration_setting(key="non_refreshed_message")
        static_setting.value = "updated static"
        client._client.set_configuration_setting(static_setting)

        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
        assert client["non_refreshed_message"] == "Static"
        assert mock_callback.call_count == 0

        setting.value = "original value"
        client._client.set_configuration_setting(setting)
        static_setting.value = "Static"
        client._client.set_configuration_setting(static_setting)
