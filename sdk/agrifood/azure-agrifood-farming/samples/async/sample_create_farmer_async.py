from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio


async def create_farmer():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()
    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    farmer_id = "contoso-farmer"

    # Create or update a farmer within FarmBeats.
    farmer = await client.farmers.create_or_update(
        farmer_id=farmer_id,
        farmer={
            "name": "contoso farmer",
            "status": "created from SDK",
            "description": "created from SDK"
        }
    )
    print(farmer)

if __name__ == "__main__":

    load_dotenv()

    asyncio.get_event_loop().run_until_complete(create_farmer())