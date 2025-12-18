# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------


import os
from datetime import datetime, timedelta, timezone
from azure.identity import DefaultAzureCredential
from azure.mgmt.mysqlflexibleservers import MySQLManagementClient
from azure.mgmt.mysqlflexibleservers.models import Configuration
from azure.mgmt.resource.resources import ResourceManagementClient

from dotenv import load_dotenv

import sys
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", stream=sys.stdout
)


def main():

    credential = DefaultAzureCredential()

    # Get subscription ID from environment variable or use a default value
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "ffffffff-ffff-ffff-ffff-ffffffffffff")

    # Set your resource details
    resource_group_name = "TestGroup"
    # Generate a unique server name (must be globally unique)
    server_name = "mysqlserver-2025-12-18-00"
    location = "southeastasia"

    # Step 1: Create Resource Group (if it doesn't exist)
    resource_client = ResourceManagementClient(
        credential=credential,
        subscription_id=subscription_id,
    )

    # Check if resource group exists
    try:
        resource_client.resource_groups.get(resource_group_name)
        print(f"Resource group '{resource_group_name}' already exists.")
    except Exception:
        print(f"Creating resource group '{resource_group_name}'...")
        resource_client.resource_groups.create_or_update(
            resource_group_name=resource_group_name, parameters={"location": location}
        )
        print(f"Resource group '{resource_group_name}' created successfully.")

    # Step 2: Create MySQL Flexible Server (if it doesn't exist)
    mysql_client = MySQLManagementClient(
        credential=credential,
        subscription_id=subscription_id,
    )

    server_parameters = {
        "location": location,
        "properties": {
            "administratorLogin": "cloudsa",
            "administratorLoginPassword": "P@ssw0rd1234!",
            "availabilityZone": "1",
            "createMode": "Default",
            "storage": {"storageSizeGB": 100, "iops": 600, "autoGrow": "Enabled"},
            "backup": {"backupRetentionDays": 7, "geoRedundantBackup": "Disabled"},
            "version": "8.0.21",
        },
        "sku": {"name": "Standard_D2ds_v4", "tier": "GeneralPurpose"},
    }

    poller = mysql_client.servers.begin_create(
        resource_group_name=resource_group_name,
        server_name=server_name,
        parameters=server_parameters,
        logging_enable=True,
    )

    server_result = poller.result()
    print(f"MySQL flexible server '{server_name}' created successfully.")

    # assert the result to check whether parameter of result is same as input
    assert server_result.name == server_name
    assert server_result.sku.name == "Standard_D2ds_v4"
    assert server_result.properties.version == "8.0.21"
    assert server_result.properties.storage.storage_size_gb == 100
    assert server_result.properties.storage.iops == 600


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from a .env file if present
    main()
