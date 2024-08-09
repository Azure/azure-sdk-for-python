# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: snapshot_sample.py

DESCRIPTION:
    This sample demos how to create/retrieve/archive/recover/list configuration settings snapshot and list configuration settings of a snapshot synchronously.

USAGE: python snapshot_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
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
        # [END create_snapshot]
        print(created_snapshot)
        print("")

        # [START get_snapshot]
        received_snapshot = client.get_snapshot(name=snapshot_name)
        # [END get_snapshot]
        print(received_snapshot)
        print("")

        # [START archive_snapshot]
        archived_snapshot = client.archive_snapshot(name=snapshot_name)
        # [END archive_snapshot]
        print(archived_snapshot)
        print("")

        # [START recover_snapshot]
        recovered_snapshot = client.recover_snapshot(name=snapshot_name)
        # [END recover_snapshot]
        print(recovered_snapshot)
        print("")

        # [START list_snapshots]
        for snapshot in client.list_snapshots():
            print(snapshot)
        # [END list_snapshots]
        print("")

        # [START list_configuration_settings_for_snapshot]
        for config_setting in client.list_configuration_settings(snapshot_name=snapshot_name):
            print(config_setting)
        # [END list_configuration_settings_for_snapshot]

        client.delete_configuration_setting(key=config_setting1.key, label=config_setting1.label)
        client.delete_configuration_setting(key=config_setting2.key, label=config_setting2.label)


if __name__ == "__main__":
    main()
