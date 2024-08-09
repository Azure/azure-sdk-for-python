# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: list_revision_sample.py

DESCRIPTION:
    This sample demos how to get configuration setting revision history synchronously.

USAGE: python list_revision_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting


def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    # Create an app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    config_setting = ConfigurationSetting(
        key="MyKey", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    returned_config_setting = client.set_configuration_setting(config_setting)

    returned_config_setting.value = "new value"
    returned_config_setting.content_type = "new content type"
    client.set_configuration_setting(config_setting)

    # [START list_revisions]
    items = client.list_revisions(key_filter="MyKey", tags_filter=["my tag=my tag value"])
    for item in items:
        print(item)
    # [END list_revisions]

    client.delete_configuration_setting(key="MyKey")


if __name__ == "__main__":
    main()
