# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_revision_sample.py
DESCRIPTION:
    This sample demos list revision operations for app configuration
USAGE: python list_revision_sample.py
"""

from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting
from util import print_configuration_setting, get_connection_string

def main():
    CONNECTION_STRING = get_connection_string()

    # Create app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    config_setting = ConfigurationSetting(
        key="MyKey",
        value="my value",
        content_type="my content type",
        tags={"my tag": "my tag value"}
    )
    returned_config_setting = client.set_configuration_setting(config_setting)

    returned_config_setting.value = "new value"
    returned_config_setting.content_type = "new content type"
    client.set_configuration_setting(config_setting)

    items = client.list_revisions(key_filter="MyKey")
    for item in items:
        print_configuration_setting(item)
        print("")

    client.delete_configuration_setting(
        key="MyKey",
    )

if __name__ == "__main__":
    main()
