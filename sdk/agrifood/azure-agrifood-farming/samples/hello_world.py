# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Dict
from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from azure.agrifood.farming.models import Farmer
import asyncio
import platform
import os


async def main(client: FarmBeatsClient, config: Dict):

    print("Creating farmer, or updating if farmer already exists...", end=" ", flush=True)
    farmer = await client.farmers.create_or_update(
        farmer_id=config['farmer_id'],
        farmer=Farmer(
            name=config['farmer_name'],
            description=config['farmer_description']
        )
    )
    print("Done")
    print("Here are the details of the farmer:")
    print(f"ID: {farmer.id}")
    print(f"Name: {farmer.name}")
    print(f"Description: {farmer.description}")
    print(f"Created timestamp: {farmer.created_date_time}")
    print(f"Last modified timestamp: {farmer.modified_date_time}")


if __name__ == "__main__":

    # config contains any data that might be used while running the sample.
    config = {
        'farmer_id': "contoso-farmer",
        'farmer_name': "Contoso",
        'farmer_description': "Contoso is hard working."
    }

    try:
        farmbeats_endpoint = os.environ.get('FARMBEATS_ENDPOINT')
    except KeyError:
        farmbeats_endpoint = None

    if farmbeats_endpoint is None:
        raise SystemExit("Please set the 'FARMBEATS_ENDPOINT' env variable to your FarmBeats endpoint.")


    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    # Using the default Proactor policy on windows 
    # causes an exception at the end of the script.
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run the main function and dispose objects safely.
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(main(client, config))
    event_loop.run_until_complete(client.close())
    event_loop.run_until_complete(credential.close())

