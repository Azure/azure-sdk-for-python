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
from azure.appconfiguration import AzureAppConfigurationClient
from preparers import app_config_decorator_aad

class TestAppConfigurationProvider(AzureRecordedTestCase):

    def build_provider_aad(self, endpoint, trimmed_key_prefixes=[], selects={SettingSelector("*", "\0")}):
        cred = self.get_credential(AzureAppConfigurationClient)
        return load_provider(credential=cred, endpoint=endpoint, trimmed_key_prefixes=trimmed_key_prefixes, selects=selects)

    # method: provider_creation_aad
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_provider_creation_aad(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad(appconfiguration_endpoint_string)
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["FeatureManagementFeatureFlags"]["Alpha"] == '{\"enabled\": false, \"conditions\": {\"client_filters\": []}}'

    # method: provider_trimmed_key_prefixes
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_provider_trimmed_key_prefixes(self, appconfiguration_endpoint_string):
        trimmed = {"test."}
        client = self.build_provider_aad(appconfiguration_endpoint_string, trimmed_key_prefixes=trimmed)
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["trimmed"] == "key"
        assert "test.trimmed" not in client
        assert client["FeatureManagementFeatureFlags"]["Alpha"] == '{\"enabled\": false, \"conditions\": {\"client_filters\": []}}'

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_provider_selectors(self, appconfiguration_endpoint_string):
        selects = {SettingSelector("message*", "dev")}
        client = self.build_provider_aad(appconfiguration_endpoint_string, selects=selects)
        assert client["message"] == "test"
        assert "test.trimmed" not in client
        assert "FeatureManagementFeatureFlags" not in client
