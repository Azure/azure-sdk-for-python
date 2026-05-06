# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import os
from sample_utilities import get_authority, get_credential, get_client_modifications
from azure.appconfiguration.provider import load, SettingSelector

endpoint = os.environ.get("APPCONFIGURATION_ENDPOINT_STRING")
authority = get_authority(endpoint)
credential = get_credential(authority)
kwargs = get_client_modifications()

# [START create_provider_entra_id]
import os
from azure.appconfiguration.provider import load
from azure.identity import DefaultAzureCredential

endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]
credential = DefaultAzureCredential()

# Connecting to Azure App Configuration using Entra ID
config = load(endpoint=endpoint, credential=credential)
# [END create_provider_entra_id]

print(config["message"])

# [START trim_prefixes_entra_id]
from azure.appconfiguration.provider import load

# Connecting to Azure App Configuration using Entra ID and trim key prefixes
trimmed = ["test."]
config = load(endpoint=endpoint, credential=credential, trim_prefixes=trimmed, **kwargs)
# [END trim_prefixes_entra_id]

print(config["message"])

# [START setting_selector_entra_id]
from azure.appconfiguration.provider import load, SettingSelector

# Connection to Azure App Configuration using SettingSelector
selects = [SettingSelector(key_filter="message*")]
config = load(
    endpoint=endpoint,
    credential=credential,
    selects=selects,
    feature_flag_enabled=True,
    feature_flag_selectors=None,
    **kwargs,
)
# [END setting_selector_entra_id]

print("message found: " + str("message" in config))
print("test.message found: " + str("test.message" in config))
print("feature_flag_enabled found: " + str(config.get("feature_management")))

# [START tag_filters]
from azure.appconfiguration.provider import load, SettingSelector

# Filtering by tags
selects = [SettingSelector(key_filter="*", tag_filters=["env=prod"])]
config = load(endpoint=endpoint, credential=credential, selects=selects, **kwargs)
# [END tag_filters]

# [START geo_replication_disable_discovery]
from azure.appconfiguration.provider import load

# Disabling replica discovery
config = load(endpoint=endpoint, credential=credential, replica_discovery_enabled=False, **kwargs)
# [END geo_replication_disable_discovery]

# [START geo_replication_load_balancing]
from azure.appconfiguration.provider import load

# Enabling load balancing across replicas
config = load(endpoint=endpoint, credential=credential, load_balancing_enabled=True, **kwargs)
# [END geo_replication_load_balancing]

# [START feature_flag_loading]
from azure.appconfiguration.provider import load

config = load(endpoint=endpoint, credential=credential, feature_flag_enabled=True, **kwargs)
feature_flags = config["feature_management"]["feature_flags"]
alpha = next(flag for flag in feature_flags if flag["id"] == "Alpha")
print(alpha["enabled"])
# [END feature_flag_loading]

# [START feature_flag_selector]
from azure.appconfiguration.provider import load, SettingSelector

config = load(
    endpoint=endpoint,
    credential=credential,
    feature_flag_enabled=True,
    feature_flag_selectors=[SettingSelector(key_filter="*", label_filter="dev")],
    **kwargs,
)
feature_flags = config["feature_management"]["feature_flags"]
alpha = next(flag for flag in feature_flags if flag["id"] == "Alpha")
print(alpha["enabled"])
# [END feature_flag_selector]

# [START json_content_type]
from azure.appconfiguration.provider import load

# Settings with JSON content type are automatically deserialized
config = load(endpoint=endpoint, credential=credential, **kwargs)
app_config = config["app/config"]  # Returns a dict if the value is JSON
print(app_config["timeout"])
# [END json_content_type]

# [START configuration_mapper]
from azure.appconfiguration.provider import load


def my_mapper(setting):
    # Transform the setting as needed
    setting.value = setting.value.strip()


config = load(endpoint=endpoint, credential=credential, configuration_mapper=my_mapper, **kwargs)
# [END configuration_mapper]

# [START startup_timeout]
from azure.appconfiguration.provider import load

config = load(endpoint=endpoint, credential=credential, startup_timeout=200, **kwargs)
# [END startup_timeout]
