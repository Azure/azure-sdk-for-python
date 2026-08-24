# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import unittest
from unittest.mock import AsyncMock, Mock

from azure.appconfiguration.provider.aio._azureappconfigurationproviderasync import AzureAppConfigurationProvider
from azure.appconfiguration.provider._azureappconfigurationproviderbase import AzureAppConfigurationProviderBase


def _make_provider() -> AzureAppConfigurationProvider:
    """
    Builds an AzureAppConfigurationProvider (async) instance for unit testing ``_attempt_refresh`` without
    creating any real network clients. ``AzureAppConfigurationProviderBase.__init__`` is invoked directly (it
    does not create any network resources), and the subclass-specific attributes normally set up by
    ``AzureAppConfigurationProvider.__init__`` (which does create real clients) are stubbed out instead.
    """
    provider = AzureAppConfigurationProvider.__new__(AzureAppConfigurationProvider)
    AzureAppConfigurationProviderBase.__init__(
        provider,
        endpoint="https://test.azconfig.io",
        feature_flag_enabled=True,
        feature_flag_refresh_enabled=True,
        refresh_enabled=False,
    )
    provider._secret_provider = Mock(uses_key_vault=False)
    provider._on_refresh_success = None
    provider._on_refresh_error = None
    provider._configuration_mapper = None
    provider._replica_client_manager = Mock()
    # Force the feature flag refresh timer to be due immediately.
    provider._feature_flag_refresh_timer._next_refresh_time = 0
    return provider


def _make_client(kv_changed: bool, enhanced_changed: bool) -> Mock:
    client = Mock()
    client.endpoint = "https://test.azconfig.io"
    client.check_feature_flag_page_etags = AsyncMock(return_value=kv_changed)
    client.check_enhanced_feature_flag_etags = AsyncMock(return_value=enhanced_changed)
    client.load_feature_flags = AsyncMock(return_value=([], [["kv_etag"]]))
    client.load_enhanced_feature_flags = AsyncMock(return_value=([], [["enhanced_etag"]]))
    return client


class TestAsyncAttemptRefreshReloadsBothFeatureFlagSources(unittest.IsolatedAsyncioTestCase):
    """Test that the async ``_attempt_refresh`` always reloads and re-merges both the key-value based feature
    flags and the enhanced feature flags together whenever either source's change-detection indicates a change,
    so the merged result is always internally consistent. Mirrors the sync test suite in
    ``test_provider_feature_flag_refresh_unit.py``."""

    async def test_only_kv_changed_reloads_both(self):
        provider = _make_provider()
        provider._feature_flag_page_etags = [["old_kv_etag"]]
        provider._enhanced_feature_flag_etags = [["old_enhanced_etag"]]

        client = _make_client(kv_changed=True, enhanced_changed=False)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        client.load_feature_flags.assert_called_once()
        client.load_enhanced_feature_flags.assert_called_once()

    async def test_only_enhanced_changed_reloads_both(self):
        provider = _make_provider()
        provider._feature_flag_page_etags = [["old_kv_etag"]]
        provider._enhanced_feature_flag_etags = [["old_enhanced_etag"]]

        client = _make_client(kv_changed=False, enhanced_changed=True)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        client.load_feature_flags.assert_called_once()
        client.load_enhanced_feature_flags.assert_called_once()

    async def test_neither_changed_reloads_neither(self):
        provider = _make_provider()
        provider._feature_flag_page_etags = [["old_kv_etag"]]
        provider._enhanced_feature_flag_etags = [["old_enhanced_etag"]]

        client = _make_client(kv_changed=False, enhanced_changed=False)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        client.load_feature_flags.assert_not_called()
        client.load_enhanced_feature_flags.assert_not_called()

    async def test_both_changed_reloads_both(self):
        provider = _make_provider()
        provider._feature_flag_page_etags = [["old_kv_etag"]]
        provider._enhanced_feature_flag_etags = [["old_enhanced_etag"]]

        client = _make_client(kv_changed=True, enhanced_changed=True)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        client.load_feature_flags.assert_called_once()
        client.load_enhanced_feature_flags.assert_called_once()

    async def test_no_previous_etag_state_reloads_both_without_checking(self):
        """When there is no previous etag state at all (first refresh attempt), both sources should be loaded
        without needing to call the etag-check methods."""
        provider = _make_provider()
        provider._feature_flag_page_etags = []
        provider._enhanced_feature_flag_etags = []

        client = _make_client(kv_changed=False, enhanced_changed=False)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        client.load_feature_flags.assert_called_once()
        client.load_enhanced_feature_flags.assert_called_once()

    async def test_reload_updates_etag_state_for_both_sources(self):
        provider = _make_provider()
        provider._feature_flag_page_etags = [["old_kv_etag"]]
        provider._enhanced_feature_flag_etags = [["old_enhanced_etag"]]

        client = _make_client(kv_changed=True, enhanced_changed=False)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        self.assertEqual(provider._feature_flag_page_etags, [["kv_etag"]])
        self.assertEqual(provider._enhanced_feature_flag_etags, [["enhanced_etag"]])

    async def test_on_refresh_success_called_when_feature_flags_refresh_to_empty_list(self):
        """Regression test: even when a feature flag refresh occurs but yields an empty list (a falsy but
        non-None value), ``_on_refresh_success`` must still be invoked because a refresh was in fact attempted
        and completed successfully."""
        provider = _make_provider()
        provider._feature_flag_page_etags = [["old_kv_etag"]]
        provider._enhanced_feature_flag_etags = [["old_enhanced_etag"]]
        on_refresh_success = Mock()
        provider._on_refresh_success = on_refresh_success

        # Both loads return an empty list, which is falsy but not None.
        client = _make_client(kv_changed=True, enhanced_changed=False)

        await provider._attempt_refresh(client, replica_count=0, is_failover_request=False)

        on_refresh_success.assert_called_once()


if __name__ == "__main__":
    unittest.main()
