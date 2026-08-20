# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""
FILE: enhanced_feature_flag_sample.py
DESCRIPTION:
    This sample demonstrates loading feature flags that were created using the dedicated enhanced feature flag
    endpoint (via ``FeatureFlagClient``/``FeatureFlag``), as opposed to the key-value
    based feature flags stored as configuration settings. The provider loads both kinds of feature
    flags side by side into the same ``feature_management.feature_flags`` list, so no additional
    ``load()`` options are required to opt in.
USAGE: python enhanced_feature_flag_sample.py
    Set the environment variable APPCONFIGURATION_ENDPOINT_STRING with your App Configuration
    connection endpoint before running the sample.
"""
import os
from sample_utilities import get_authority, get_credential, get_client_modifications
from azure.appconfiguration import FeatureFlag, FeatureFlagClient  # type:ignore
from azure.appconfiguration.provider import load, SettingSelector

endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# Creating a feature flag using the dedicated enhanced feature flag endpoint. This is a separate resource
# type from the key-value based feature flags, and is managed via FeatureFlagClient instead of
# AzureAppConfigurationClient.
feature_flag_client = FeatureFlagClient(endpoint, credential, **kwargs)
feature_flag_client.set_feature_flag(FeatureFlag(name="EnhancedFeatureBeta", enabled=True))

try:
    # [START enhanced_feature_flag_loading]
    from azure.appconfiguration.provider import load

    # Feature flags loaded from the enhanced feature flag endpoint are merged into the same
    # feature_management.feature_flags list as key-value based feature flags.
    config = load(endpoint=endpoint, credential=credential, feature_flag_enabled=True, **kwargs)
    feature_flags = config["feature_management"]["feature_flags"]
    enhanced_flag_beta = next(flag for flag in feature_flags if flag.get("id") == "EnhancedFeatureBeta")
    print(enhanced_flag_beta["enabled"])
    # [END enhanced_feature_flag_loading]

    # [START enhanced_feature_flag_selector]
    from azure.appconfiguration.provider import load, SettingSelector

    # The same SettingSelector used to filter key-value based feature flags also filters enhanced feature
    # flags, by name/label/tags.
    config = load(
        endpoint=endpoint,
        credential=credential,
        feature_flag_enabled=True,
        feature_flag_selectors=[SettingSelector(key_filter="Enhanced*")],
        **kwargs,
    )
    feature_flags = config["feature_management"]["feature_flags"]
    enhanced_flag_beta = next(flag for flag in feature_flags if flag.get("id") == "EnhancedFeatureBeta")
    print(enhanced_flag_beta["enabled"])
    # [END enhanced_feature_flag_selector]

    # [START enhanced_feature_flag_selector_with_feature_flag_selector]
    from azure.appconfiguration.provider import load, FeatureFlagSelector

    # FeatureFlagSelector is the dedicated selector type for filtering enhanced feature flags.
    config = load(
        endpoint=endpoint,
        credential=credential,
        feature_flag_enabled=True,
        feature_flag_selectors=[FeatureFlagSelector(name_filter="Enhanced*")],
        **kwargs,
    )
    feature_flags = config["feature_management"]["feature_flags"]
    enhanced_flag_beta = next(flag for flag in feature_flags if flag.get("id") == "EnhancedFeatureBeta")
    print(enhanced_flag_beta["enabled"])
    # [END enhanced_feature_flag_selector_with_feature_flag_selector]
finally:
    # Cleaning up the enhanced feature flag created for this sample.
    feature_flag_client.delete_feature_flag("EnhancedFeatureBeta")
    feature_flag_client.close()
