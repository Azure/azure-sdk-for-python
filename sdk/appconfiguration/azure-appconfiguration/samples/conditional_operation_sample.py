# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: conditional_operation_sample.py

DESCRIPTION:
    This sample demos how to conditional set/get/delete configuration settings synchronously.

USAGE: python conditional_operation_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import os
from azure.core import MatchConditions
from azure.core.exceptions import ResourceModifiedError
from azure.appconfiguration import AzureAppConfigurationClient, ConfigurationSetting


def main():
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    # Create an app config client
    client = AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING)

    # Unconditional set
    config_setting = ConfigurationSetting(
        key="MyKey", value="my value", content_type="my content type", tags={"my tag": "my tag value"}
    )
    client.set_configuration_setting(config_setting)

    # Unconditional get
    first_get = client.get_configuration_setting(key="MyKey")
    if first_get is None:
        return print("Error, unconditional set failed.")
    print(first_get)

    # Conditional get, expect to return None because it is not modified
    second_get = client.get_configuration_setting(
        key="MyKey", etag=first_get.etag, match_condition=MatchConditions.IfModified
    )
    print(second_get)

    # Conditional set
    first_get.value = "new value"
    client.set_configuration_setting(configuration_setting=first_get, match_condition=MatchConditions.IfNotModified)

    # Conditional set, expect to see error because it is modified
    try:
        client.set_configuration_setting(configuration_setting=first_get, match_condition=MatchConditions.IfNotModified)
    except ResourceModifiedError:
        pass

    client.delete_configuration_setting(key="MyKey")


if __name__ == "__main__":
    main()
