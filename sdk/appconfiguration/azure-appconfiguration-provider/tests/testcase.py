# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from test_constants import FEATURE_MANAGEMENT_KEY, FEATURE_FLAG_KEY
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    ConfigurationSetting,
    FeatureFlagConfigurationSetting,
    SecretReferenceConfigurationSetting,
)
from azure.appconfiguration.provider import load, AzureAppConfigurationKeyVaultOptions
from azure.appconfiguration.provider._constants import NULL_CHAR


class AppConfigTestCase(AzureRecordedTestCase):
    def create_client(self, **kwargs):
        credential = self.get_credential(AzureAppConfigurationClient)

        client = None

        if "connection_string" in kwargs:
            client = AzureAppConfigurationClient.from_connection_string(kwargs["connection_string"])
        else:
            client = AzureAppConfigurationClient(kwargs["endpoint"], credential)

        setup_configs(client, kwargs.get("keyvault_secret_url"), kwargs.get("keyvault_secret_url2"))
        kwargs["user_agent"] = "SDK/Integration"

        if "endpoint" in kwargs:
            kwargs["credential"] = credential

        if "secret_resolver" not in kwargs and kwargs.get("keyvault_secret_url") and "key_vault_options" not in kwargs:
            kwargs["keyvault_credential"] = credential

        if "key_vault_options" in kwargs:
            key_vault_options = kwargs.pop("key_vault_options")
            if not key_vault_options.secret_resolver:
                key_vault_options = AzureAppConfigurationKeyVaultOptions(credential=credential)
            kwargs["key_vault_options"] = key_vault_options

        return load(**kwargs)

    @staticmethod
    def create_sdk_client(appconfiguration_connection_string):
        return AzureAppConfigurationClient.from_connection_string(
            appconfiguration_connection_string, user_agent="SDK/Integration"
        )

    def create_aad_sdk_client(self, appconfiguration_endpoint_string):
        cred = self.get_credential(AzureAppConfigurationClient)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred, user_agent="SDK/Integration")


def setup_configs(client, keyvault_secret_url, keyvault_secret_url2):
    for config in get_configs(keyvault_secret_url, keyvault_secret_url2):
        client.set_configuration_setting(config)


def get_configs(keyvault_secret_url, keyvault_secret_url2):
    configs = []
    configs.append(create_config_setting("message", NULL_CHAR, "hi"))
    configs.append(create_config_setting("message", "dev", "test"))
    configs.append(create_config_setting("my_json", NULL_CHAR, '{"key": "value"}', "application/json"))
    configs.append(create_config_setting("test.trimmed", NULL_CHAR, "key"))
    configs.append(create_config_setting("refresh_message", NULL_CHAR, "original value"))
    configs.append(create_config_setting("non_refreshed_message", NULL_CHAR, "Static"))
    configs.append(create_config_setting("tagged_config", NULL_CHAR, None, tags={"a": "b"}))
    configs.append(create_config_setting("two_tagged", NULL_CHAR, None, tags={"a": "b", "second": "tag"}))
    configs.append(create_config_setting("only_second_tag", NULL_CHAR, None, tags={"second": "tag"}))
    configs.append(
        create_config_setting(
            "complex_tag", NULL_CHAR, None, tags={"Special:Tag": "Value:With:Colons", "Tag@With@At": "Value@With@At"}
        )
    )
    configs.append(
        create_config_setting(
            ".appconfig.featureflag/Alpha",
            NULL_CHAR,
            '{	"id": "Alpha", "description": "", "enabled": false, "conditions": {	"client_filters": []	}}',
            "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
        )
    )
    configs.append(
        create_config_setting(
            ".appconfig.featureflag/TaggedFeatureFlag",
            NULL_CHAR,
            '{	"id": "TaggedFeatureFlag", "description": "", "enabled": false, "conditions": {	"client_filters": []	}}',
            "application/vnd.microsoft.appconfig.ff+json;charset=utf-8",
            tags={"a": "b"},
        )
    )
    # Configuration with multiple tags
    configs.append(create_config_setting("multi_tagged", NULL_CHAR, "multi tagged value", tags={"a": "b", "c": "d"}))
    # Configuration with tag that has special characters
    configs.append(create_config_setting("special_chars", NULL_CHAR, "special", tags={"special@tag": "special:value"}))
    # Configuration with no tags
    configs.append(create_config_setting("no_tags", NULL_CHAR, "no tags"))
    # Configuration with tag that has no value
    configs.append(create_config_setting("tag_no_value", NULL_CHAR, "no value", tags={"a": ""}))
    # Configuration with different tag
    configs.append(create_config_setting("different_tag", NULL_CHAR, "different", tags={"different": "tag"}))
    # Configuration with null tag
    configs.append(create_config_setting("null_tag", NULL_CHAR, "null tag", tags={"tag": None}))
    if keyvault_secret_url:
        configs.append(
            create_secret_config_setting(
                "secret",
                "prod",
                keyvault_secret_url,
            )
        )
    if keyvault_secret_url2:
        configs.append(
            create_secret_config_setting(
                "secret2",
                "prod",
                keyvault_secret_url2,
            )
        )
    return configs


def create_config_setting(key, label, value, content_type="text/plain", tags=None):
    return ConfigurationSetting(key=key, label=label, value=value, content_type=content_type, tags=tags)


def create_secret_config_setting(key, label, value):
    return SecretReferenceConfigurationSetting(
        key=key,
        label=label,
        secret_id=value,
    )


def create_feature_flag_config_setting(key, label, enabled, tags=None):
    return FeatureFlagConfigurationSetting(feature_id=key, label=label, enabled=enabled, tags=tags)


def cleanup_test_resources(
    client,
    settings=None,
    snapshot_names=None,
):
    """
    Clean up test resources from Azure App Configuration.

    :param client: The AzureAppConfigurationClient to use for cleanup.
    :param settings: List of ConfigurationSetting objects to delete.
    :param snapshot_names: List of snapshot names to archive.
    """
    # Archive snapshots
    if snapshot_names:
        for snapshot_name in snapshot_names:
            try:
                client.archive_snapshot(snapshot_name)
            except Exception:
                pass

    # Delete configuration settings and feature flags
    if settings:
        for setting in settings:
            try:
                client.delete_configuration_setting(key=setting.key, label=setting.label)
            except Exception:
                pass


def set_test_settings(client, settings):
    """
    Set multiple configuration settings in Azure App Configuration.

    :param client: The AzureAppConfigurationClient to use.
    :param settings: List of ConfigurationSetting or FeatureFlagConfigurationSetting objects to set.
    """
    for setting in settings:
        client.set_configuration_setting(setting)


def create_snapshot(client, snapshot_name, key_filters, composition_type=None, retention_period=3600):
    """
    Create a snapshot in Azure App Configuration and verify it was created successfully.

    :param client: The AzureAppConfigurationClient to use.
    :param snapshot_name: The name of the snapshot to create.
    :param key_filters: List of key filter strings to define what settings to include.
    :param composition_type: The composition type for the snapshot (default: SnapshotComposition.KEY).
    :param retention_period: The retention period in seconds (default: 3600, minimum valid value).
    :return: The created snapshot.
    """
    from azure.appconfiguration import SnapshotComposition, ConfigurationSettingsFilter, SnapshotStatus
    from devtools_testutils import is_live

    if composition_type is None:
        composition_type = SnapshotComposition.KEY

    # Convert key filter strings to ConfigurationSettingsFilter objects
    filters = [ConfigurationSettingsFilter(key=key_filter) for key_filter in key_filters]

    snapshot = client.begin_create_snapshot(
        name=snapshot_name,
        filters=filters,
        composition_type=composition_type,
        retention_period=retention_period,
    ).result()

    # Verify snapshot was created successfully
    assert snapshot.status == SnapshotStatus.READY, f"Snapshot status is {snapshot.status}, expected READY"
    assert (
        snapshot.composition_type == composition_type
    ), f"Snapshot composition_type is {snapshot.composition_type}, expected {composition_type}"

    # Verify snapshot name (sanitized in playback mode)
    if is_live():
        assert snapshot.name == snapshot_name, f"Snapshot name is {snapshot.name}, expected {snapshot_name}"
    else:
        assert snapshot.name == "Sanitized", f"Snapshot name is {snapshot.name}, expected 'Sanitized' in playback"

    return snapshot


def get_feature_flag(client, feature_id):
    for feature_flag in client[FEATURE_MANAGEMENT_KEY][FEATURE_FLAG_KEY]:
        if feature_flag["id"] == feature_id:
            return feature_flag
    return None


def has_feature_flag(client, feature_id, enabled=False):
    feature_flag = get_feature_flag(client, feature_id)
    if feature_flag:
        return feature_flag["enabled"] == enabled
    return False
