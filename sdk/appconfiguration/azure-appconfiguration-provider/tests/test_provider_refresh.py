# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
from azure.appconfiguration.provider import load, SettingSelector, AzureAppConfigurationRefreshOptions
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from azure.appconfiguration import AzureAppConfigurationClient
from preparers import app_config_decorator_aad


class TestAppConfigurationProvider(AzureRecordedTestCase):
    def build_provider_aad(
        self, endpoint, trim_prefixes=[], selects={SettingSelector(key_filter="*", label_filter="\0")}, refresh_key="message"
    ):
        refresh_options = AzureAppConfigurationRefreshOptions()
        refresh_options.refresh_interval = 1
        refresh_options.register(key_filter=refresh_key, refresh_all=True)
        refresh_options.callback = self.my_callback
        refresh_options.callback_on_fail = self.my_callback_on_fail
        cred = self.get_credential(AzureAppConfigurationClient)
        return load(credential=cred, endpoint=endpoint, trim_prefixes=trim_prefixes, selects=selects, refresh_options=refresh_options)

    # method: refresh
    @recorded_by_proxy
    @app_config_decorator_aad
    def test_refresh(self, appconfiguration_endpoint_string):
        client = self.build_provider_aad(appconfiguration_endpoint_string, refresh_key="refresh_message")
        assert client["refresh_message"] == "original value"
        assert client["my_json"]["key"] == "value"
        assert (
            client["FeatureManagementFeatureFlags"]["Alpha"]
            == '{"enabled": false, "conditions": {"client_filters": []}}'
        )
        setting = client._client.get_configuration_setting(key="refresh_message")
        setting.value = "updated value"
        client._client.set_configuration_setting(setting)
        
        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "updated value"

        setting.value = "original value"
        client._client.set_configuration_setting(setting)
        
        # Waiting for the refresh interval to pass
        time.sleep(2)

        client.refresh()
        assert client["refresh_message"] == "original value"
    
    def my_callback(self):
        assert True

    def my_callback_on_fail(self):
        assert False
