# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import (
    load_provider,
    SettingSelector
)
from devtools_testutils import (
    AzureRecordedTestCase, 
    recorded_by_proxy
)
from preparers import app_config_decorator

class TestAppConfigurationProvider(AzureRecordedTestCase):

    def build_provider(self, connection_string, trim_prefixes=[], selects={SettingSelector("*", "\0")}):
        return load_provider(connection_string=connection_string, trim_prefixes=trim_prefixes, selects=selects)

    # method: provider_creation
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_creation(self, appconfiguration_connection_string):
        client = self.build_provider(appconfiguration_connection_string)
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["FeatureManagementFeatureFlags"]["Alpha"] == '{\"enabled\": false, \"conditions\": {\"client_filters\": []}}'

    # method: provider_trim_prefixes
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_trim_prefixes(self, appconfiguration_connection_string):
        trimmed = {"test."}
        client = self.build_provider(appconfiguration_connection_string, trim_prefixes=trimmed)
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["trimmed"] == "key"
        assert "test.trimmed" not in client
        assert client["FeatureManagementFeatureFlags"]["Alpha"] == '{\"enabled\": false, \"conditions\": {\"client_filters\": []}}'

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_selectors(self, appconfiguration_connection_string):
        selects = {SettingSelector(key_filter="message*",label_filter="dev")}
        client = self.build_provider(appconfiguration_connection_string, selects=selects)
        assert client["message"] == "test"
        assert "test.trimmed" not in client
        assert "FeatureManagementFeatureFlags" not in client
