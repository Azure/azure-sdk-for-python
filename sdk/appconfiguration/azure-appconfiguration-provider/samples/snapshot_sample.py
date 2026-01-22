# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

from azure.appconfiguration.provider import load, SettingSelector
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    ConfigurationSettingsFilter,
    ConfigurationSnapshot,
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
)
from sample_utilities import get_authority, get_credential, get_client_modifications
import os
import uuid

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# Step 1: Create a snapshot
# First, we'll create some configuration settings and then create a snapshot containing them
client = AzureAppConfigurationClient(endpoint, credential)


# Create sample configuration settings (these will be included in the snapshot)
sample_settings = [
    ConfigurationSetting(key="app/settings/message", value="Hello from snapshot!"),
    ConfigurationSetting(key="app/settings/fontSize", value="14"),
    ConfigurationSetting(key="app/settings/backgroundColor", value="#FFFFFF"),
]

# Create a feature flag (also included in the snapshot)
sample_feature_flag = FeatureFlagConfigurationSetting(
    feature_id="Beta",
    enabled=True,
    description="Beta feature flag from snapshot sample",
)

# Override settings with "prod" label (used in mixed selects, not in snapshot)
override_settings = [
    ConfigurationSetting(key="override.message", value="Production override!", label="prod"),
    ConfigurationSetting(key="override.fontSize", value="16", label="prod"),
]

print("Creating sample configuration settings...")
for setting in sample_settings:
    # client.set_configuration_setting(setting)
    print(f"  Created: {setting.key} = {setting.value}")

# Create the feature flag
client.set_configuration_setting(sample_feature_flag)
print(f"  Created feature flag: {sample_feature_flag.feature_id} = {sample_feature_flag.enabled}")

for setting in override_settings:
    # client.set_configuration_setting(setting)
    print(f"  Created: {setting.key} = {setting.value} (label: {setting.label})")

# Generate a unique snapshot name
snapshot_name = f"sample-snapshot-{uuid.uuid4().hex[:8]}"

# Create snapshot with filters for app settings and feature flags (retention_period=3600 seconds = 1 hour)
snapshot_filters = [
    ConfigurationSettingsFilter(key="app/*"),
    ConfigurationSettingsFilter(key=".appconfig.featureflag/*"),
]

try:
    created_snapshot = client.begin_create_snapshot(
        name=snapshot_name, filters=snapshot_filters, retention_period=3600
    ).result()
    print(f"Created snapshot: {created_snapshot.name} with status: {created_snapshot.status}")
except Exception as e:
    print(f"Error creating snapshot: {e}")
    print("Make sure you have configuration settings with keys starting with 'app/' in your store.")
    raise

# Step 2: Loading configuration settings from the snapshot
snapshot_selects = [SettingSelector(snapshot_name=snapshot_name)]
config = load(endpoint=endpoint, credential=credential, selects=snapshot_selects, **kwargs)

print("Configuration settings from snapshot:")
for key, value in config.items():
    print(f"{key}: {value}")

# Step 3: Combine snapshot with regular selectors (later selectors take precedence)
mixed_selects = [
    SettingSelector(snapshot_name=snapshot_name),  # Load all settings from snapshot
    SettingSelector(key_filter="override.*", label_filter="prod"),  # Also load specific override settings
]
config_mixed = load(endpoint=endpoint, credential=credential, selects=mixed_selects, **kwargs)

print("\nMixed configuration (snapshot + filtered settings):")
for key, value in config_mixed.items():
    print(f"{key}: {value}")

# Step 4: Load feature flags from the snapshot (requires feature_flag_enabled=True)
feature_flag_selects = [SettingSelector(snapshot_name=snapshot_name)]
config_with_flags = load(
    endpoint=endpoint,
    credential=credential,
    selects=feature_flag_selects,
    feature_flag_enabled=True,
    **kwargs,
)

print(f"\nFeature flags loaded: {'feature_management' in config_with_flags}")
if "feature_management" in config_with_flags:
    feature_flags = config_with_flags["feature_management"].get("feature_flags", [])
    for flag in feature_flags:
        print(f"  {flag['id']}: enabled={flag['enabled']}")
