# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import os
import sys
import traceback
import uuid

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.cosmos import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account in fabric environment and database and container created.
#    https://learn.microsoft.com/en-us/fabric/database/cosmos-db/overview
# 2. Python packages (preview + identity) and login:
#    pip install "azure-cosmos==4.14.0b3" azure-identity
#    az login
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to authenticate and use your database account using AAD credentials with Fabric.
# Read more about operations allowed for this authorization method: https://aka.ms/cosmos-native-rbac
# ----------------------------------------------------------------------------------------------------------
# Note:
# This sample assumes the database and container already exist.
# It writes one item (PK path assumed to be "/pk") and reads it back.
# ----------------------------------------------------------------------------------------------------------
HOST = config.settings["host"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]
PARTITION_KEY = PartitionKey(path="/pk")

def get_test_item(num: int) -> dict:
    return {
        "id": f"Item_{num}",
        "pk": "partition1",
        "name": "Item 1",
        "description": "This is item 1",
        "runId": str(uuid.uuid4())
    }


def run_sample():
    # if you want to override scope for AAD authentication.
    #os.environ["AZURE_COSMOS_AAD_SCOPE_OVERRIDE"] = "https://cosmos.azure.com/.default"

    # AAD auth works with az login
    aad_credentials = InteractiveBrowserCredential()

    # Use your credentials to authenticate your client.
    aad_client = CosmosClient(HOST, aad_credentials)

    # Do R/W data operations with your authorized AAD client.
    db = aad_client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)

    # Create item
    item = get_test_item(0)
    container.create_item(item)
    print("Created item:", item["id"])

    # Read item
    read_doc = container.read_item(item=item["id"], partition_key=item["pk"])
    print("Point read:\n" + json.dumps(read_doc, indent=2))


def main():
    try:
        run_sample()
    except exceptions.CosmosHttpResponseError as e:
        print(f"CosmosHttpResponseError: {getattr(e, 'status_code', None)} - {e}")
        resp = getattr(e, "response", None)
        if resp is not None and getattr(resp, "headers", None) is not None:
            try:
                print("Response headers:\n" + json.dumps(dict(resp.headers), indent=2))
            except Exception:
                pass
        traceback.print_exc()
        raise
    except Exception as ex:
        print(f"Exception: {ex}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()