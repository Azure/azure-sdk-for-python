# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import SettingSelector, load
from azure.appconfiguration import AzureAppConfigurationClient
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator
from testcase import AppConfigTestCase, setup_configs, has_feature_flag, get_feature_flag
from test_constants import FEATURE_MANAGEMENT_KEY


class TestAppConfigurationProviderFeatureManagement(AppConfigTestCase):
    # method: load
    @recorded_by_proxy
    @app_config_decorator
    def test_load_only_feature_flags(self, appconfiguration_connection_string):
        client = self.create_client(
            appconfiguration_connection_string,
            selects=[],
            feature_flag_enabled=True,
        )
        assert len(client.keys()) == 1
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")
        assert "telemetry" not in get_feature_flag(client, "Alpha")

    # method: load
    @recorded_by_proxy
    @app_config_decorator
    def test_select_feature_flags(self, appconfiguration_connection_string):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        setup_configs(client, None)

        client = load(
            connection_string=appconfiguration_connection_string,
            selects=[],
            feature_flag_enabled=True,
            feature_flag_selectors=[SettingSelector(key_filter="B*")],
            user_agent="SDK/Integration",
        )
        assert len(client.keys()) == 1
        assert FEATURE_MANAGEMENT_KEY in client
        assert not has_feature_flag(client, "Alpha")
