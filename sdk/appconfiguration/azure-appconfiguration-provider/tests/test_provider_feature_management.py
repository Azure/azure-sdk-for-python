# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader, recorded_by_proxy
from testcase import AppConfigTestCase, setup_configs, has_feature_flag, get_feature_flag
from test_constants import APPCONFIGURATION_CONNECTION_STRING, FEATURE_MANAGEMENT_KEY
from azure.appconfiguration import AzureAppConfigurationClient
from azure.appconfiguration.provider import SettingSelector, load

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_connection_string=APPCONFIGURATION_CONNECTION_STRING,
)


class TestAppConfigurationProviderFeatureManagement(AppConfigTestCase):
    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_load_only_feature_flags(self, appconfiguration_connection_string):
        client = self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=[],
            feature_flag_enabled=True,
        )
        assert len(client.keys()) == 1
        assert FEATURE_MANAGEMENT_KEY in client
        alpha = get_feature_flag(client, "Alpha")
        assert alpha
        assert "telemetry" in alpha
        assert "enabled" not in alpha.get("telemetry")

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy
    def test_select_feature_flags(self, appconfiguration_connection_string):
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)
        setup_configs(client, None, None)

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
