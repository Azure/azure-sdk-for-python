# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: read_only_sample.py
DESCRIPTION:
    This sample demos set_read_only/clear_read_only operations for app configuration
USAGE: python read_only_sample.py
"""

import os
import sys
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting

def main():
    try:
        CONNECTION_STRING = os.environ['AZURE_APPCONFIG_CONNECTION_STRING']

    except KeyError:
        print("AZURE_APPCONFIG_CONNECTION_STRING must be set.")
        sys.exit(1)

    # Create app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    print("Set new configration setting")
    config_setting = ConfigurationSetting(
        key="MyKey",
        value="my value",
        content_type="my content type",
        tags={"my tag": "my tag value"}
    )
    returned_config_setting = client.set_configuration_setting(config_setting)
    print("New configration setting:")
    print(returned_config_setting)
    print("")

    print("Read only configration setting:")
    read_only_config_setting = client.set_read_only(
        returned_config_setting
    )
    print(read_only_config_setting)
    print("")

    print("Clear read only configration setting:")
    read_only_config_setting = client.clear_read_only(
        returned_config_setting
    )
    print(read_only_config_setting)
    print("")

    print("Delete configuration setting")
    client.delete_configuration_setting(
        key="MyKey",
    )

if __name__ == "__main__":
    main()
