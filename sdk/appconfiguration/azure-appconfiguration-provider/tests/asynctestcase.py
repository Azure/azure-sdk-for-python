# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase
from azure.appconfiguration.aio import AzureAppConfigurationClient
from testcase import get_configs
from azure.appconfiguration.provider.aio import load
from azure.appconfiguration.provider import AzureAppConfigurationKeyVaultOptions


class AppConfigTestCase(AzureRecordedTestCase):
    async def create_client(self, **kwargs):
        credential = self.get_credential(AzureAppConfigurationClient, is_async=True)
        client = None

        if "connection_string" in kwargs:
            client = AzureAppConfigurationClient.from_connection_string(kwargs["connection_string"])
        else:
            client = AzureAppConfigurationClient(kwargs["endpoint"], credential)

        await setup_configs(client, kwargs.get("keyvault_secret_url"), kwargs.get("keyvault_secret_url2"))
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

        return await load(**kwargs)

    @staticmethod
    def create_sdk_client(appconfiguration_connection_string):
        return AzureAppConfigurationClient.from_connection_string(
            appconfiguration_connection_string, user_agent="SDK/Integration"
        )

    def create_aad_sdk_client(self, appconfiguration_endpoint_string):
        cred = self.get_credential(AzureAppConfigurationClient, is_async=True)
        return AzureAppConfigurationClient(appconfiguration_endpoint_string, cred, user_agent="SDK/Integration")


async def setup_configs(client, keyvault_secret_url, keyvault_secret_url2):
    async with client:
        for config in get_configs(keyvault_secret_url, keyvault_secret_url2):
            await client.set_configuration_setting(config)


async def cleanup_test_resources_async(
    client,
    settings=None,
    snapshot_names=None,
):
    """
    Clean up test resources from Azure App Configuration (async version).

    :param client: The async AzureAppConfigurationClient to use for cleanup.
    :param settings: List of ConfigurationSetting objects to delete.
    :param snapshot_names: List of snapshot names to archive.
    """
    # Archive snapshots
    if snapshot_names:
        for snapshot_name in snapshot_names:
            try:
                await client.archive_snapshot(snapshot_name)
            except Exception:
                pass

    # Delete configuration settings and feature flags
    if settings:
        for setting in settings:
            try:
                await client.delete_configuration_setting(key=setting.key, label=setting.label)
            except Exception:
                pass


async def set_test_settings_async(client, settings):
    """
    Set multiple configuration settings in Azure App Configuration (async version).

    :param client: The async AzureAppConfigurationClient to use.
    :param settings: List of ConfigurationSetting or FeatureFlagConfigurationSetting objects to set.
    """
    for setting in settings:
        await client.set_configuration_setting(setting)


async def create_snapshot_async(client, snapshot_name, key_filters, composition_type=None, retention_period=3600):
    """
    Create a snapshot in Azure App Configuration and verify it was created successfully (async version).

    :param client: The async AzureAppConfigurationClient to use.
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

    snapshot_poller = await client.begin_create_snapshot(
        name=snapshot_name,
        filters=filters,
        composition_type=composition_type,
        retention_period=retention_period,
    )
    snapshot = await snapshot_poller.result()

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
