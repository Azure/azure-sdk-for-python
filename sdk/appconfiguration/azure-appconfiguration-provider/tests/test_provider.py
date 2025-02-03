# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import SettingSelector, AzureAppConfigurationKeyVaultOptions
from devtools_testutils import recorded_by_proxy
from preparers import app_config_decorator
from testcase import AppConfigTestCase, has_feature_flag
import datetime
from unittest.mock import patch
from test_constants import FEATURE_MANAGEMENT_KEY

from azure.appconfiguration.provider._azureappconfigurationproviderbase import delay_failure


def sleep(seconds):
    assert isinstance(seconds, float)


class TestAppConfigurationProvider(AppConfigTestCase):
    # method: provider_creation
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_creation(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        client = self.create_client(
            appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
        )
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")

    # method: provider_trim_prefixes
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_trim_prefixes(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        trimmed = {"test."}
        client = self.create_client(
            appconfiguration_connection_string,
            trim_prefixes=trimmed,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
        )
        assert client["message"] == "hi"
        assert client["my_json"]["key"] == "value"
        assert client["trimmed"] == "key"
        assert "test.trimmed" not in client
        assert FEATURE_MANAGEMENT_KEY in client
        assert has_feature_flag(client, "Alpha")

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
        assert FEATURE_MANAGEMENT_KEY not in client

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_key_vault_reference(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        client = self.create_client(
            appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        )
        assert client["secret"] == "Very secret value"

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_secret_resolver(self, appconfiguration_connection_string):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        client = self.create_client(
            appconfiguration_connection_string, selects=selects, secret_resolver=secret_resolver
        )
        assert client["secret"] == "Reslover Value"

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_key_vault_reference_options(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        key_vault_options = AzureAppConfigurationKeyVaultOptions()
        client = self.create_client(
            appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            key_vault_options=key_vault_options,
        )
        assert client["secret"] == "Very secret value"

    # method: provider_selectors
    @recorded_by_proxy
    @app_config_decorator
    def test_provider_secret_resolver_options(self, appconfiguration_connection_string):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        key_vault_options = AzureAppConfigurationKeyVaultOptions(secret_resolver=secret_resolver)
        client = self.create_client(
            appconfiguration_connection_string, selects=selects, key_vault_options=key_vault_options
        )
        assert client["secret"] == "Reslover Value"

    # method: delay_failure
    @patch("time.sleep", side_effect=sleep)
    def test_delay_failure(self, mock_sleep, **kwargs):
        start_time = datetime.datetime.now()
        delay_failure(start_time)
        assert mock_sleep.call_count == 1

        mock_sleep.reset_mock()
        start_time = datetime.datetime.now() - datetime.timedelta(seconds=10)
        delay_failure(start_time)
        mock_sleep.assert_not_called()


def secret_resolver(secret_id):
    return "Reslover Value"
