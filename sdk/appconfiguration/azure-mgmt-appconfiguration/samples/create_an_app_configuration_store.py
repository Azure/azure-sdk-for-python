# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os

from azure.identity import EnvironmentCredential
from azure.mgmt.appconfiguration import AppConfigurationManagementClient
from azure.mgmt.resource import ResourceManagementClient


def main():

    SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID", None)
    GROUP_NAME = "testgroupx"
    CONFIG_STORE_NAME = "configstorexyz"

    # Create client
    appconfig_client = AppConfigurationManagementClient(
        credential=EnvironmentCredential(),
        subscription_id=SUBSCRIPTION_ID
    )
    resource_client = ResourceManagementClient(
        credential=EnvironmentCredential(),
        subscription_id=SUBSCRIPTION_ID
    )

    # Create resource group
    resource_client.resource_groups.create_or_update(
        GROUP_NAME,
        {"location": "eastus"}
    )

    # Create appconfiguration store
    appconfig_store = appconfig_client.configuration_stores.begin_create(
        GROUP_NAME,
        CONFIG_STORE_NAME,
        {
          "location": "eastus",
          "sku": {
            "name": "Standard"
          }
        }
    ).result()
    print("Create appconfigruation store:\n{}".format(appconfig_store))

    # Get appconfiguration store
    appconfig_store = appconfig_client.configuration_stores.get(
        GROUP_NAME,
        CONFIG_STORE_NAME
    )
    print("Get appconfigruation store:\n{}".format(appconfig_store))

    # Update appconfiguration store
    appconfig_store = appconfig_client.configuration_stores.begin_update(
        GROUP_NAME,
        CONFIG_STORE_NAME,
        {
          "tags": {
            "category": "Marketing"
          },
          "sku": {
            "name": "Standard"
          }
        }
    ).result()
    print("Update appconfigruation store:\n{}".format(appconfig_store))

    # Delete appconfiguration store
    appconfig_client.configuration_stores.begin_delete(
        GROUP_NAME,
        CONFIG_STORE_NAME
    ).result()
    print("Delete appconfiguration store")

    # Delete Group
    resource_client.resource_groups.begin_delete(
        GROUP_NAME
    ).result()

if __name__ == "__main__":
    main()
