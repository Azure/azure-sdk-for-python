from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from datetime import datetime
import os
from dotenv import load_dotenv
import asyncio
import random


async def create_party():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()
    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    party_id = f"contoso-party-{random.randint(0,1000)}"

    # Create or update a party within FarmBeats.
    party = await client.parties.create_or_update(
        party_id=party_id,
        party={
            "name": "contoso party",
            "status": "created from SDK",
            "description": "created from SDK"
        }
    )
    print(party)

    await client.close()
    await credential.close()

if __name__ == "__main__":
    load_dotenv()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(create_party())