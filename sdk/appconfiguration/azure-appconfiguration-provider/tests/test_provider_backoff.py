# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import load, SettingSelector
from devtools_testutils import AzureRecordedTestCase, recorded_by_proxy
from preparers import app_config_decorator


class TestAppConfigurationProvider(AzureRecordedTestCase):
    def build_provider(
        self,
        connection_string,
        trim_prefixes=[],
        selects={SettingSelector(key_filter="*", label_filter="\0")},
        **kwargs
    ):
        return load(connection_string=connection_string, trim_prefixes=trim_prefixes, selects=selects, **kwargs)


"""     # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff(self, appconfiguration_connection_string):
        client = self.build_provider(appconfiguration_connection_string)
        min_backoff = 30000
        assert min_backoff == client._configuration_refresh.calculate_backoff()

        attempts = 2
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << attempts))

        attempts = 3
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << attempts))

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_max_attempts(self, appconfiguration_connection_string):
        client = self.build_provider(appconfiguration_connection_string)
        min_backoff = 3000

        # When attempts is > 30 then it acts as if it was 30
        attempts = 30
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << attempts))

        attempts = 31
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << 30))

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_invalid_attempts(self, appconfiguration_connection_string):
        client = self.build_provider(appconfiguration_connection_string)
        min_backoff = 30000 # 30 Seconds in milliseconds

        # When attempts is < 1 then it acts as if it was 1
        attempts = 0
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff == min_backoff

        attempts = -1
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff == min_backoff

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_missmatch_settings(self, appconfiguration_connection_string):
        min_backoff = 1000
        max_backoff = 100
        microsecond = 1000 # 1 Second in milliseconds
        client = self.build_provider(
            appconfiguration_connection_string, min_backoff=min_backoff, max_backoff=max_backoff
        )

        # When attempts is < 1 then it acts as if it was 1
        attempts = 0
        client._configuration_refresh.attempts = attempts
        backoff = client._configuration_refresh.calculate_backoff()
        assert backoff == (min_backoff * microsecond)
 """
