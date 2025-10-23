# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from azure.appconfiguration.provider import SettingSelector, AzureAppConfigurationKeyVaultOptions
from devtools_testutils.aio import recorded_by_proxy_async
from async_preparers import app_config_decorator_async
from testcase import has_feature_flag
from asynctestcase import AppConfigTestCase
from test_constants import FEATURE_MANAGEMENT_KEY
from unittest.mock import MagicMock, patch
from azure.appconfiguration.provider.aio._azureappconfigurationproviderasync import (
    _buildprovider,
)


class TestAppConfigurationProvider(AppConfigTestCase):
    # method: provider_creation
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_creation(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
        ) as client:
            assert client["message"] == "hi"
            assert client["my_json"]["key"] == "value"
            assert ".appconfig.featureflag/Alpha" not in client
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "Alpha")

    # method: provider_trim_prefixes
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_trim_prefixes(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        trimmed = {"test."}
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            trim_prefixes=trimmed,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
        ) as client:
            assert client["message"] == "hi"
            assert client["my_json"]["key"] == "value"
            assert client["trimmed"] == "key"
            assert "test.trimmed" not in client
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "Alpha")

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_selectors(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        selects = {SettingSelector(key_filter="message*", label_filter="dev")}
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert client["message"] == "test"
            assert "test.trimmed" not in client
            assert FEATURE_MANAGEMENT_KEY not in client

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_key_vault_reference(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert client["secret"] == "Very secret value"

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_secret_resolver(self, appconfiguration_connection_string):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        async with await self.create_client(
            connection_string=appconfiguration_connection_string, selects=selects, secret_resolver=secret_resolver
        ) as client:
            assert client["secret"] == "Resolver Value"

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_key_vault_reference_options(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        key_vault_options = AzureAppConfigurationKeyVaultOptions()
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            key_vault_options=key_vault_options,
        ) as client:
            assert client["secret"] == "Very secret value"

    # method: provider_selectors
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_secret_resolver_options(self, appconfiguration_connection_string):
        selects = {SettingSelector(key_filter="*", label_filter="prod")}
        key_vault_options = AzureAppConfigurationKeyVaultOptions(secret_resolver=secret_resolver)
        async with await self.create_client(
            connection_string=appconfiguration_connection_string, selects=selects, key_vault_options=key_vault_options
        ) as client:
            assert client["secret"] == "Resolver Value"

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_process_key_value_content_type(self, appconfiguration_connection_string):
        with patch(
            "azure.appconfiguration.provider.aio._azureappconfigurationproviderasync.ConfigurationClientManager"
        ) as MockClientManager:
            # Mock the client manager and its methods
            mock_client_manager = MockClientManager.return_value
            mock_client_manager.load_configuration_settings.return_value = [
                {"key": "test_key", "value": '{"key": "value"}', "content_type": "application/json"}
            ]

            # Create the provider with the mocked client manager
            provider = await _buildprovider("=mock_connection_string;;", None, None)
            provider._replica_client_manager = mock_client_manager

            # Call the method to process key-value pairs
            processed_value = await provider._process_key_value(
                MagicMock(content_type="application/json", value='{"key": "value"}')
            )

            # Assert the processed value is as expected
            assert processed_value == {"key": "value"}
            assert provider._tracing_context.uses_ai_configuration == False
            assert provider._tracing_context.uses_aicc_configuration == False

            mock_client_manager.load_configuration_settings.return_value = [
                {
                    "key": "test_key",
                    "value": '{"key": "value"}',
                    "content_type": "https://azconfig.io/mime-profiles/ai/",
                }
            ]
            processed_value = await provider._process_key_value(
                MagicMock(
                    content_type='application/json; profile="https://azconfig.io/mime-profiles/ai/"',
                    value='{"key": "value"}',
                )
            )

            assert processed_value == {"key": "value"}
            assert provider._tracing_context.uses_ai_configuration == True
            assert provider._tracing_context.uses_aicc_configuration == False

            mock_client_manager.load_configuration_settings.return_value = [
                {
                    "key": "test_key",
                    "value": '{"key": "value"}',
                    "content_type": 'application/json; profile="https://azconfig.io/mime-profiles/ai/chat-completion"',
                }
            ]
            processed_value = await provider._process_key_value(
                MagicMock(
                    content_type='application/json; profile="https://azconfig.io/mime-profiles/ai/chat-completion"',
                    value='{"key": "value"}',
                )
            )

            assert processed_value == {"key": "value"}
            assert provider._tracing_context.uses_ai_configuration == True
            assert provider._tracing_context.uses_aicc_configuration == True

    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_provider_tag_filters(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        selects = {SettingSelector(key_filter="*", tag_filters=["a=b"])}
        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            selects=selects,
            feature_flag_enabled=True,
            feature_flag_selectors={SettingSelector(key_filter="*", tag_filters=["a=b"])},
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
        ) as client:
            assert "tagged_config" in client
            assert FEATURE_MANAGEMENT_KEY in client
            assert has_feature_flag(client, "TaggedFeatureFlag")
            assert "message" not in client

    # method: load
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_configuration_mapper(self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url):
        async def test_mapper(setting):
            if setting.key == "message":
                setting.value = "mapped"

        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            configuration_mapper=test_mapper,
        ) as client:
            assert client["message"] == "mapped"
            assert client["refresh_message"] == "original value"

    # method: load
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_configuration_mapper_with_trimming(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        async def test_mapper(setting):
            if setting.key == "message":
                setting.value = "mapped"

        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            configuration_mapper=test_mapper,
            trim_prefixes=["refresh_"],
        ) as client:
            # Because our processing happens after mapping and refresh_message is alphabetically after message the override
            # value isn't used, as the mapped value is overridden by the first value.
            assert client["message"] == "original value"
            assert "refresh_message" not in client

    # method: load
    @app_config_decorator_async
    @recorded_by_proxy_async
    async def test_configuration_mapper_with_feature_flags(
        self, appconfiguration_connection_string, appconfiguration_keyvault_secret_url
    ):
        async def test_mapper(setting):
            if setting.key == ".appconfig.featureflag/Alpha":
                setting.content_type = "application/json"

        async with await self.create_client(
            connection_string=appconfiguration_connection_string,
            keyvault_secret_url=appconfiguration_keyvault_secret_url,
            feature_flag_enabled=True,
            configuration_mapper=test_mapper,
            trim_prefixes=[".appconfig.featureflag/"],
        ) as client:
            # Feature Flags aren't modified by configuration mappers
            assert "Alpha" not in client
            assert client["feature_management"]["feature_flags"][0]["id"] == "Alpha"


async def secret_resolver(secret_id):
    return "Resolver Value"
