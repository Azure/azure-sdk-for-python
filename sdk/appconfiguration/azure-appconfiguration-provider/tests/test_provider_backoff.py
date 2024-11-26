# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator
from testcase import AppConfigTestCase


class TestAppConfigurationProvider(AppConfigTestCase):
    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        client = self.create_client(
            appconfiguration_connection_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        )
        min_backoff = 30000
        assert min_backoff == client._refresh_timer._calculate_backoff()

        attempts = 2
        client._refresh_timer.attempts = attempts
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << attempts))

        attempts = 3
        client._refresh_timer.attempts = attempts
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << attempts))

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_max_attempts(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        client = self.create_client(
            appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )
        min_backoff = 3000

        # When attempts is > 30 then it acts as if it was 30
        attempts = 30
        client._refresh_timer.attempts = attempts
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << attempts))

        attempts = 31
        client._refresh_timer.attempts = attempts
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff >= min_backoff and backoff <= (min_backoff * (1 << 30))

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_bounds(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        client = self.create_client(
            appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=1,
        )

        assert client._refresh_timer._min_backoff == 1
        assert client._refresh_timer._max_backoff == 1

        client = self.create_client(
            appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=45,
        )

        assert client._refresh_timer._min_backoff == 30
        assert client._refresh_timer._max_backoff == 45

        client = self.create_client(
            appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            refresh_interval=700,
        )

        assert client._refresh_timer._min_backoff == 30
        assert client._refresh_timer._max_backoff == 600

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_invalid_attempts(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        client = self.create_client(
            appconfiguration_connection_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        )
        min_backoff = 30000  # 30 Seconds in milliseconds

        # When attempts is < 1 then it acts as if it was 1
        attempts = 0
        client._refresh_timer.attempts = attempts
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff == min_backoff

        attempts = -1
        client._refresh_timer.attempts = attempts
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff == min_backoff

    # method: _calculate_backoff
    @recorded_by_proxy
    @app_config_decorator
    def test_backoff_missmatch_settings(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        min_backoff = 30000
        client = self.create_client(
            appconfiguration_connection_string, keyvault_secret_url=appconfiguration_keyvault_secret_url
        )

        # When attempts is < 1 then it acts as if it was 1
        client._refresh_timer.attempts = 0
        backoff = client._refresh_timer._calculate_backoff()
        assert backoff == min_backoff
