# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest
from azure.appconfiguration.aio import AzureAppConfigurationClient
from azure.appconfiguration._audience_error_handling_policy import AudienceErrorHandlingPolicy
from asynctestcase import AsyncAppConfigTestCase
from async_preparers import app_config_aad_decorator_async
from devtools_testutils.aio import recorded_by_proxy_async
from consts import KEY, LABEL


class TestAudienceErrorHandlingLiveAsync(AsyncAppConfigTestCase):
    """Async live and recorded tests for audience error handling with the Azure App Configuration client."""

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_client_has_audience_policy_with_no_audience(self, appconfiguration_endpoint_string):
        """Test that async client created without audience has policy with has_audience=False."""
        # Create client without audience
        client = self.create_aad_client(appconfiguration_endpoint_string)

        # Check that audience error handling policy is in the pipeline
        policies = client._impl._client._pipeline._impl_policies
        audience_policy = None
        for policy in policies:
            # Policies are wrapped in _SansIOHTTPPolicyRunner, so we need to access the underlying policy
            underlying_policy = getattr(policy, "_policy", policy)
            if isinstance(underlying_policy, AudienceErrorHandlingPolicy):
                audience_policy = underlying_policy
                break

        assert audience_policy is not None, "AudienceErrorHandlingPolicy should be in pipeline"
        assert audience_policy.has_audience is False, "has_audience should be False when no audience provided"

        await client.close()

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_client_has_audience_policy_with_audience(self, appconfiguration_endpoint_string):
        """Test that async client created with audience has policy with has_audience=True."""
        # Create client with audience
        client = self.create_aad_client(appconfiguration_endpoint_string, audience="https://azconfig.io")

        # Check that audience error handling policy is in the pipeline
        policies = client._impl._client._pipeline._impl_policies
        audience_policy = None
        for policy in policies:
            # Policies are wrapped in _SansIOHTTPPolicyRunner, so we need to access the underlying policy
            underlying_policy = getattr(policy, "_policy", policy)
            if isinstance(underlying_policy, AudienceErrorHandlingPolicy):
                audience_policy = underlying_policy
                break

        assert audience_policy is not None, "AudienceErrorHandlingPolicy should be in pipeline"
        assert audience_policy.has_audience is True, "has_audience should be True when audience provided"

        await client.close()

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_successful_operation_with_correct_audience(self, appconfiguration_endpoint_string):
        """Test that async operations succeed when correct audience is provided."""
        client = self.create_aad_client(appconfiguration_endpoint_string, audience="https://azconfig.io")

        # Should be able to perform operations successfully
        kv = self.create_config_setting()
        await self.add_for_test(client, kv)

        # Get the configuration setting
        result = await client.get_configuration_setting(key=kv.key, label=kv.label)
        assert result.key == kv.key
        assert result.value == kv.value

        # Clean up
        await client.delete_configuration_setting(key=kv.key, label=kv.label)
        await client.close()

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_successful_operation_without_audience(self, appconfiguration_endpoint_string):
        """Test that async operations succeed when no audience is provided."""
        # Create client without specifying audience
        client = self.create_aad_client(appconfiguration_endpoint_string)

        # Should be able to perform operations successfully
        kv = self.create_config_setting()
        await self.add_for_test(client, kv)

        # Get the configuration setting
        result = await client.get_configuration_setting(key=kv.key, label=kv.label)
        assert result.key == kv.key
        assert result.value == kv.value

        # Clean up
        await client.delete_configuration_setting(key=kv.key, label=kv.label)
        await client.close()

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_context_manager_with_correct_audience(self, appconfiguration_endpoint_string):
        """Test that async context manager works properly with correct audience."""
        async with self.create_aad_client(appconfiguration_endpoint_string, audience="https://azconfig.io") as client:
            kv = self.create_config_setting()
            await self.add_for_test(client, kv)
            result = await client.get_configuration_setting(key=kv.key, label=kv.label)
            assert result.key == kv.key
            await client.delete_configuration_setting(key=kv.key, label=kv.label)

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_multiple_operations_with_aad_auth(self, appconfiguration_endpoint_string):
        """Test multiple async operations with AAD authentication."""
        client = self.create_aad_client(appconfiguration_endpoint_string, audience="https://azconfig.io")

        # Test multiple operations
        kv1 = self.create_config_setting()
        await self.add_for_test(client, kv1)

        # Get operation
        result1 = await client.get_configuration_setting(key=kv1.key, label=kv1.label)
        assert result1.key == kv1.key

        # Set operation
        kv1.value = "updated_value"
        result2 = await client.set_configuration_setting(kv1)
        assert result2.value == "updated_value"

        # List operation
        items = []
        async for item in client.list_configuration_settings(key_filter=kv1.key, label_filter=kv1.label):
            items.append(item)
        assert len(items) >= 1

        # Clean up
        await client.delete_configuration_setting(key=kv1.key, label=kv1.label)
        await client.close()

    @app_config_aad_decorator_async
    @recorded_by_proxy_async
    async def test_async_list_revisions_with_aad_auth(self, appconfiguration_endpoint_string):
        """Test list revisions with async AAD authentication."""
        client = self.create_aad_client(appconfiguration_endpoint_string, audience="https://azconfig.io")

        # Create and modify a configuration setting to create revisions
        kv = self.create_config_setting()
        await self.add_for_test(client, kv)

        # Update to create a revision
        kv.value = "updated_value"
        await client.set_configuration_setting(kv)

        # List revisions
        revisions = []
        async for revision in client.list_revisions(key_filter=kv.key, label_filter=kv.label):
            revisions.append(revision)
        assert len(revisions) >= 2

        # Clean up
        await client.delete_configuration_setting(key=kv.key, label=kv.label)
        await client.close()
