# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def print_configuration_setting(config_setting):
    if not config_setting:
        return
    print(f"key: {config_setting.key}")
    print(f"label: {config_setting.label}")
    print(f"value: {config_setting.value}")
    print(f"read_only: {config_setting.read_only}")
    print(f"etag: {config_setting.etag}")


def print_snapshot(snapshot):
    if not snapshot:
        return
    print(f"name: {snapshot.name}")
    print(f"status: {snapshot.status}")
    print("filers: ")
    for config_setting_filter in snapshot.filters:
        print(f"key: {config_setting_filter.key} label: {config_setting_filter.label}")
    print(f"composition_type: {snapshot.composition_type}")
    print(f"created: {snapshot.created}")
    print(f"expires: {snapshot.expires}")
    print(f"retention_period: {snapshot.retention_period}")
    print(f"size: {snapshot.size}")
    print(f"items_count: {snapshot.items_count}")
    print(f"tags: {snapshot.tags}")
    print(f"etag: {snapshot.etag}")
