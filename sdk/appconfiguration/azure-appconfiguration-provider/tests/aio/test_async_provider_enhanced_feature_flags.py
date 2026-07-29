# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
Tests for loading feature flags from the dedicated enhanced feature flag endpoint
(``FeatureFlagClient``/``FeatureFlag``), as opposed to the key-value based
``FeatureFlagConfigurationSetting`` stored via ``AzureAppConfigurationClient`` (async version).
"""
import functools
from devtools_testutils import EnvironmentVariableLoader
from devtools_testutils.aio import recorded_by_proxy_async
from testcase import has_feature_flag, get_feature_flag
from asynctestcase import AppConfigTestCase
from test_constants import APPCONFIGURATION_ENDPOINT_STRING, FEATURE_MANAGEMENT_KEY
from azure.appconfiguration import FeatureFlag, FeatureFlagConfigurationSetting
from azure.appconfiguration.provider import SettingSelector
from azure.appconfiguration.provider._constants import NULL_CHAR

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    appconfiguration_endpoint_string=APPCONFIGURATION_ENDPOINT_STRING,
)


class TestAppConfigurationProviderEnhancedFeatureFlags(AppConfigTestCase):
    """Tests for the provider loading feature flags from the dedicated enhanced feature flag endpoint (async)."""

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_load_enhanced_feature_flag(self, appconfiguration_endpoint_string):
        """A feature flag created via the enhanced feature flag endpoint should be loaded by the provider."""
        feature_flag_client = self.create_enhanced_feature_flag_client(appconfiguration_endpoint_string)
        feature_flag = FeatureFlag(name="ResourceOnlyFeature", enabled=True)
        await feature_flag_client.set_feature_flag(feature_flag)

        try:
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                selects=[],
                feature_flag_enabled=True,
                feature_flag_selectors=[SettingSelector(key_filter="ResourceOnlyFeature")],
            ) as client:
                assert FEATURE_MANAGEMENT_KEY in client
                assert has_feature_flag(client, "ResourceOnlyFeature", enabled=True)
        finally:
            await feature_flag_client.delete_feature_flag("ResourceOnlyFeature")
            await feature_flag_client.close()

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_load_enhanced_feature_flag_disabled(self, appconfiguration_endpoint_string):
        """A disabled enhanced feature flag should be loaded with enabled set to False."""
        feature_flag_client = self.create_enhanced_feature_flag_client(appconfiguration_endpoint_string)
        feature_flag = FeatureFlag(name="ResourceDisabledFeature", enabled=False)
        await feature_flag_client.set_feature_flag(feature_flag)

        try:
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                selects=[],
                feature_flag_enabled=True,
                feature_flag_selectors=[SettingSelector(key_filter="ResourceDisabledFeature")],
            ) as client:
                assert has_feature_flag(client, "ResourceDisabledFeature", enabled=False)
        finally:
            await feature_flag_client.delete_feature_flag("ResourceDisabledFeature")
            await feature_flag_client.close()

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_load_enhanced_feature_flag_with_label(self, appconfiguration_endpoint_string):
        """An enhanced feature flag with a label should be loaded when the label filter matches."""
        feature_flag_client = self.create_enhanced_feature_flag_client(appconfiguration_endpoint_string)
        feature_flag = FeatureFlag(name="ResourceLabeledFeature", enabled=True, label="test_label")
        await feature_flag_client.set_feature_flag(feature_flag)

        try:
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                selects=[],
                feature_flag_enabled=True,
                feature_flag_selectors=[
                    SettingSelector(key_filter="ResourceLabeledFeature", label_filter="test_label")
                ],
            ) as client:
                assert has_feature_flag(client, "ResourceLabeledFeature", enabled=True)
        finally:
            await feature_flag_client.delete_feature_flag("ResourceLabeledFeature", label="test_label")
            await feature_flag_client.close()

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_enhanced_feature_flag_selector_filters_by_name(self, appconfiguration_endpoint_string):
        """The feature_flag_selectors key_filter should scope which enhanced feature flags are loaded."""
        feature_flag_client = self.create_enhanced_feature_flag_client(appconfiguration_endpoint_string)
        included_flag = FeatureFlag(name="IncludedResourceFeature", enabled=True)
        excluded_flag = FeatureFlag(name="ExcludedResourceFeature", enabled=True)
        await feature_flag_client.set_feature_flag(included_flag)
        await feature_flag_client.set_feature_flag(excluded_flag)

        try:
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                selects=[],
                feature_flag_enabled=True,
                feature_flag_selectors=[SettingSelector(key_filter="Included*")],
            ) as client:
                assert has_feature_flag(client, "IncludedResourceFeature", enabled=True)
                assert not has_feature_flag(client, "ExcludedResourceFeature")
        finally:
            await feature_flag_client.delete_feature_flag("IncludedResourceFeature")
            await feature_flag_client.delete_feature_flag("ExcludedResourceFeature")
            await feature_flag_client.close()

    # method: load
    @AppConfigProviderPreparer()
    @recorded_by_proxy_async
    async def test_enhanced_feature_flag_overrides_key_value(self, appconfiguration_endpoint_string):
        """An enhanced feature flag should take precedence over a key-value based feature flag with the
        same identifier when both are loaded."""
        appconfig_client = self.create_appconfig_client(appconfiguration_endpoint_string)
        feature_flag_client = self.create_enhanced_feature_flag_client(appconfiguration_endpoint_string)

        kv_feature_flag = FeatureFlagConfigurationSetting(feature_id="OverlapFeature", enabled=False, label=NULL_CHAR)
        await appconfig_client.set_configuration_setting(kv_feature_flag)
        enhanced_feature_flag_obj = FeatureFlag(name="OverlapFeature", enabled=True)
        await feature_flag_client.set_feature_flag(enhanced_feature_flag_obj)

        try:
            async with await self.create_client(
                endpoint=appconfiguration_endpoint_string,
                selects=[],
                feature_flag_enabled=True,
                feature_flag_selectors=[SettingSelector(key_filter="OverlapFeature")],
            ) as client:
                # The enhanced feature flag (enabled=True) should win over the key-value based one
                # (enabled=False) since they share the same identifier.
                assert has_feature_flag(client, "OverlapFeature", enabled=True)
                feature_flag = get_feature_flag(client, "OverlapFeature")
                assert feature_flag is not None
                assert "id" in feature_flag
        finally:
            await appconfig_client.delete_configuration_setting(key=kv_feature_flag.key, label=kv_feature_flag.label)
            await feature_flag_client.delete_feature_flag("OverlapFeature")
            await appconfig_client.close()
            await feature_flag_client.close()
