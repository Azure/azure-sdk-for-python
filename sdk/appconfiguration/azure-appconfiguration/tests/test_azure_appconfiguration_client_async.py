# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from uuid import uuid4
import pytest
from consts import (
    APPCONFIGURATION_CONNECTION_STRING,
)
from azure.appconfiguration import (
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.appconfiguration.aio import AzureAppConfigurationClient


class TestAppConfigurationClientUnitTest:
    def test_type_error(self):
        with pytest.raises(TypeError):
            _ = FeatureFlagConfigurationSetting("blah", value="blah")
        with pytest.raises(TypeError):
            _ = SecretReferenceConfigurationSetting("blah", value="blah")  # pylint: disable=no-value-for-parameter

    @pytest.mark.asyncio
    async def test_mock_policies(self):
        from azure.core.pipeline.transport import HttpResponse, AsyncHttpTransport
        from azure.core.pipeline import PipelineRequest, PipelineResponse

        class MockTransport(AsyncHttpTransport):
            def __init__(self):
                self.auth_headers = []

            async def __aexit__(self, exc_type, exc_val, exc_tb):
                pass

            async def close(self):
                pass

            async def open(self):
                pass

            async def send(self, request: PipelineRequest, **kwargs) -> PipelineResponse:
                assert request.headers["Authorization"] != self.auth_headers
                self.auth_headers.append(request.headers["Authorization"])
                response = HttpResponse(request, None)
                response.status_code = 429
                return response

        @staticmethod
        def new_method(request):
            request.http_request.headers["Authorization"] = str(uuid4())

        from azure.appconfiguration._azure_appconfiguration_requests import AppConfigRequestsCredentialsPolicy

        # Store the method to restore later
        temp = AppConfigRequestsCredentialsPolicy._signed_request
        AppConfigRequestsCredentialsPolicy._signed_request = new_method

        client = AzureAppConfigurationClient.from_connection_string(
            APPCONFIGURATION_CONNECTION_STRING, transport=MockTransport()
        )
        client.list_configuration_settings()

        # Reset the actual method
        AppConfigRequestsCredentialsPolicy._signed_request = temp

    @pytest.mark.asyncio
    async def test_from_connection_string(self):
        connection_string = "Endpoint=https://fake_app_config.azconfig-test.io;" "Id=fake-id;" "Secret=fakesecret="
        client = AzureAppConfigurationClient.from_connection_string(connection_string)
        assert client._impl._config.endpoint == "https://fake_app_config.azconfig-test.io"
        await client.close()

    def test_from_connection_string_invalid(self):
        with pytest.raises(ValueError):
            AzureAppConfigurationClient.from_connection_string("invalid_connection_string")
        with pytest.raises(ValueError):
            AzureAppConfigurationClient.from_connection_string("Endpoint=;Id=;Secret=")
        with pytest.raises(ValueError):
            AzureAppConfigurationClient.from_connection_string("Endpoint=https://fake.io;Id=abc")

    @pytest.mark.asyncio
    async def test_from_connection_string_mock_policies(self):
        from unittest.mock import patch, MagicMock

        connection_string = "Endpoint=https://fake_app_config.azconfig-test.io;" "Id=fake-id;" "Secret=fakesecret="
        with patch(
            "azure.appconfiguration.aio._azure_appconfiguration_client_async.AppConfigRequestsCredentialsPolicy"
        ) as mock_policy_cls:
            mock_policy = MagicMock()
            mock_policy_cls.return_value = mock_policy
            client = AzureAppConfigurationClient.from_connection_string(connection_string)
            mock_policy_cls.assert_called_once()
            args, _ = mock_policy_cls.call_args
            # Verify the credential, endpoint, and id_credential are passed correctly
            assert args[1] == "https://fake_app_config.azconfig-test.io"
            assert args[2] == "fake-id"
            await client.close()
