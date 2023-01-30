from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
import random


async def create_farmer():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()
    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    farmer_id = f"contoso-farmer-{random.randint(0,1000)}"

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

    await client.close()
    await credential.close()

if __name__ == "__main__":
    load_dotenv()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(create_farmer())