# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: snapshot_samples.py

DESCRIPTION:
    This sample demos CRUD operations for app configuration setting snapshot.

USAGE: python snapshot_samples.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from util import print_configuration_setting, print_snapshot
from uuid import uuid4


def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]
    config_setting1 = ConfigurationSetting(key="my_key1", label="my_label1")
    config_setting2 = ConfigurationSetting(key="my_key2", label="my_label2")
    snapshot_name = str(uuid4())
    with AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING) as client:
        client.add_configuration_setting(config_setting1)
        client.add_configuration_setting(config_setting2)

        # [START create_snapshot]
        from azure.appconfiguration import ConfigurationSettingsFilter

        filters = [ConfigurationSettingsFilter(key="my_key1", label="my_label1")]
        response = client.begin_create_snapshot(name=snapshot_name, filters=filters)
        created_snapshot = response.result()
        print_snapshot(created_snapshot)
        # [END create_snapshot]
        print("")

        # [START get_snapshot]
        received_snapshot = client.get_snapshot(name=snapshot_name)
        # [END get_snapshot]

        # [START archive_snapshot]
        archived_snapshot = client.archive_snapshot(name=snapshot_name)
        print_snapshot(archived_snapshot)
        # [END archive_snapshot]
        print("")

        # [START recover_snapshot]
        recovered_snapshot = client.recover_snapshot(name=snapshot_name)
        print_snapshot(recovered_snapshot)
        # [END recover_snapshot]
        print("")

        # [START list_snapshots]
        for snapshot in client.list_snapshots():
            print_snapshot(snapshot)
        # [END list_snapshots]
        print("")

        # [START list_configuration_settings_for_snapshot]
        for config_setting in client.list_configuration_settings(snapshot_name=snapshot_name):
            print_configuration_setting(config_setting)
        # [END list_configuration_settings_for_snapshot]

        client.delete_configuration_setting(key=config_setting1.key, label=config_setting1.label)
        client.delete_configuration_setting(key=config_setting2.key, label=config_setting2.label)


if __name__ == "__main__":
    main()
