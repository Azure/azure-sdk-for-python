# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""
FILE: async_enhanced_feature_flag_sample.py
DESCRIPTION:
    This sample demonstrates loading feature flags that were created using the dedicated enhanced feature flag
    endpoint (via ``FeatureFlagClient``/``FeatureFlag``), as opposed to the key-value
    based feature flags stored as configuration settings. The provider loads both kinds of feature
    flags side by side into the same ``feature_management.feature_flags`` list, so no additional
    ``load()`` options are required to opt in. This is the async version of enhanced_feature_flag_sample.py.
USAGE: python async_enhanced_feature_flag_sample.py
    Set the environment variable APPCONFIGURATION_ENDPOINT_STRING with your App Configuration
    connection endpoint before running the sample.
"""
import os
import asyncio
from sample_utilities import get_authority, get_credential, get_client_modifications
from azure.appconfiguration.aio import FeatureFlagClient
from azure.appconfiguration import FeatureFlag
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import SettingSelector


async def main():
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
    authority = get_authority(endpoint)
    credential = get_credential(authority, is_async=True)
    kwargs = get_client_modifications()

    # Creating a feature flag using the dedicated enhanced feature flag endpoint. This is a separate
    # resource type from the key-value based feature flags, and is managed via FeatureFlagClient
    # instead of AzureAppConfigurationClient.
    feature_flag_client = FeatureFlagClient(endpoint, credential, **kwargs)
    await feature_flag_client.set_feature_flag(FeatureFlag(name="EnhancedFeatureBeta", enabled=True))

    try:
        # [START enhanced_feature_flag_loading_async]
        from azure.appconfiguration.provider.aio import load

        # Feature flags loaded from the enhanced feature flag endpoint are merged into the same
        # feature_management.feature_flags list as key-value based feature flags.
        config = await load(endpoint=endpoint, credential=credential, feature_flag_enabled=True, **kwargs)
        feature_flags = config["feature_management"]["feature_flags"]
        enhanced_flag_beta = next(flag for flag in feature_flags if flag.get("id") == "EnhancedFeatureBeta")
        print(enhanced_flag_beta["enabled"])

        await config.close()
        # [END enhanced_feature_flag_loading_async]

        # [START enhanced_feature_flag_selector_async]
        from azure.appconfiguration.provider.aio import load
        from azure.appconfiguration.provider import SettingSelector

        # The same SettingSelector used to filter key-value based feature flags also filters enhanced feature
        # flags, by name/label/tags.
        config = await load(
            endpoint=endpoint,
            credential=credential,
            feature_flag_enabled=True,
            feature_flag_selectors=[SettingSelector(key_filter="Enhanced*")],
            **kwargs,
        )
        feature_flags = config["feature_management"]["feature_flags"]
        enhanced_flag_beta = next(flag for flag in feature_flags if flag.get("id") == "EnhancedFeatureBeta")
        print(enhanced_flag_beta["enabled"])

        await config.close()
        # [END enhanced_feature_flag_selector_async]

        # [START enhanced_feature_flag_selector_with_feature_flag_selector_async]
        from azure.appconfiguration.provider.aio import load
        from azure.appconfiguration.provider import FeatureFlagSelector

        # FeatureFlagSelector is the dedicated selector type for filtering enhanced feature flags.
        config = await load(
            endpoint=endpoint,
            credential=credential,
            feature_flag_enabled=True,
            feature_flag_selectors=[FeatureFlagSelector(name_filter="Enhanced*")],
            **kwargs,
        )
        feature_flags = config["feature_management"]["feature_flags"]
        enhanced_flag_beta = next(flag for flag in feature_flags if flag.get("id") == "EnhancedFeatureBeta")
        print(enhanced_flag_beta["enabled"])

        await config.close()
        # [END enhanced_feature_flag_selector_with_feature_flag_selector_async]
    finally:
        # Cleaning up the enhanced feature flag created for this sample.
        await feature_flag_client.delete_feature_flag("EnhancedFeatureBeta")
        await feature_flag_client.close()
        await credential.close()


if __name__ == "__main__":
    asyncio.run(main())
