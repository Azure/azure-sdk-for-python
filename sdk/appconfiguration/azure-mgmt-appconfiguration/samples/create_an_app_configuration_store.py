# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.mgmt.appconfiguration import AppConfigurationManagementClient
from azure.mgmt.resource import ResourceManagementClient

from _prepare import (
    client_credential,
    SUBSCRIPTION_ID
)

def main():

    GROUP_NAME = "testgroupx"
    CONFIG_STORE_NAME = "configstorex"

    # Create client
    appconfig_client = AppConfigurationManagementClient(
        credential=client_credential,
        subscription_id=SUBSCRIPTION_ID
    )
    resource_client = ResourceManagementClient(
        credential=client_credential,
        subscription_id=SUBSCRIPTION_ID
    )

    # Create resource group
    resource_client.resource_groups.create_or_update(
        GROUP_NAME,
        {"location": "eastus"}
    )

    # Create appconfiguration store
    config_store = appconfig_client.configuration_stores.begin_create(
        GROUP_NAME,
        CONFIG_STORE_NAME,
        {
          "location": "westus",
          "sku": {
            "name": "Standard"  # Free can not use private endpoint
          }
        }
    ).result()

    # Get appconfiguration store connection string
    keys = appconfig_client.configuration_stores.list_keys(
        GROUP_NAME,
        CONFIG_STORE_NAME
    )
    keys = list(keys)
    connection_string = keys[0].connection_string
    print("connection_str: {}".format(connection_string))

    # Delete appconfiguration store
    appconfig_client.configuration_stores.begin_delete(
        GROUP_NAME,
        CONFIG_STORE_NAME
    ).result()

    # Delete Group
    resource_client.resource_groups.begin_delete(
        GROUP_NAME
    ).result()

if __name__ == "__main__":
    main()
