# Remove this if un-needed, I use it to ensure I always run against the local SDK
import sys
sys.path.append(r"C:\Users\my-user\azure-sdk-for-python\sdk\cosmos\azure-cosmos")

import asyncio
import uuid
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncClient

# Replace with your Cosmos DB details
COSMOS_URI = ""
COSMOS_KEY = ""

def connection_things():
    client = CosmosClient(COSMOS_URI, COSMOS_KEY, preferred_locations=['West US 2', "West US"])
    db = client.create_database_if_not_exists("db-id")
    container = db.create_container_if_not_exists("container-id", PartitionKey("/pk"))
    container.upsert_item({"id": "simon", "pk": "simon"})
    container.read_item('simon', 'simon')

async def connection_things_async():
    async with AsyncClient(COSMOS_URI, COSMOS_KEY, preferred_locations=['West US 2', "West US"]) as client:
        db = await client.create_database_if_not_exists("db-id")
        container = await db.create_container_if_not_exists("container-id", PartitionKey("/pk"))
        await container.upsert_item({"id": "simon", "pk": "simon"})
        await container.read_item('simon', 'simon')

if __name__ == "__main__":
    # Use the one you want for sync vs. async
    connection_things()
    # asyncio.run(connection_things_async())