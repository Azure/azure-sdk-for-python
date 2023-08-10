# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import SettingSelector
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator
from testcase import AppConfigTestCase


class TestAppConfigurationProvider(AppConfigTestCase):
    # method: provider_creation
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_creation(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        client = self.create_client(
            appconfiguration_connection_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        )
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )

    # method: provider_trim_prefixes
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_trim_prefixes(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        trimmed = {"test."}
        client = self.create_client(
            appconfiguration_connection_string,
            trim_prefixes=trimmed,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["trimmed"] == "key"
        assert "test.trimmed" not in client
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_selectors(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        selects = {SettingSelector(key_filter="message*", label_filter="dev")}
        client = self.create_client(
            appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )
        assert client["message"] == "test"
        assert "test.trimmed" not in client
        assert "FeatureManagementFeatureFlags" not in client
