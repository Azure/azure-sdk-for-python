# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Read an existing order asynchronously using an account-key connection string.

Set AZURE_COSMOS_CONNECTION_STRING to AccountEndpoint=...;AccountKey=...;.
The sales database and orders container must already contain order-42 with
partition key value customer-17. This sample does not create resources.
"""

import asyncio
import os

from azure.cosmos.aio import CosmosClient


async def main():
    # [START client_from_connection_string]
    async with CosmosClient.from_connection_string(
        os.environ["AZURE_COSMOS_CONNECTION_STRING"],
        consistency_level="Session",
    ) as client:
        orders = client.get_database_client("sales").get_container_client("orders")
        order = await orders.read_item("order-42", partition_key="customer-17")
        print("Order ID:", order["id"])
    # [END client_from_connection_string]


if __name__ == "__main__":
    asyncio.run(main())
