# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def print_configuration_setting(config_setting):
    if not config_setting:
        return
    print("key: " + config_setting.key)
    if config_setting.label:
        print("label: " + config_setting.label)
    if config_setting.value:
        print("value: " + config_setting.value)
    if config_setting.read_only:
        print("read_only: True")
    else:
        print("read_only: False")
    if config_setting.etag:
        print("etag: " + config_setting.etag)
