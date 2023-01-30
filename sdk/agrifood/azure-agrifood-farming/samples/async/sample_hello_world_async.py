# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_hello_world_async.py

DESCRIPTION:
    This sample demonstrates the most basic operation that can be 
    performed - creation of a Farmer. Use this to understand how to 
    create the client object, how to authenticate it, and make sure 
    your client is set up correctly to call into your FarmBeats endpoint.

USAGE:
    ```python sample_hello_world_async.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from azure.agrifood.farming.models import Farmer
import os
import asyncio
from dotenv import load_dotenv
import random


async def sample_hello_world_async():

    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    farmer_id = f"contoso-farmer-{random.randint(0,1000)}"
    farmer_name = "Contoso"
    farmer_description = "Contoso is hard working."

    print("Creating farmer, or updating if farmer already exists...", end=" ", flush=True)
    farmer = await client.farmers.create_or_update(
        farmer_id=farmer_id,
        farmer={
            "name": farmer_name,
            "description": farmer_description,
            "status": "Sample Status",
            "properties": {
                "foo": "bar",
                "numeric one": 1,
                1: "numeric key"
            }
        }
    )
    print("Done")
    
    print("Here are the details of the farmer:")
    print("\tID:", farmer["id"])
    print("\tName:", farmer["name"])
    print("\tDescription:", farmer["description"])
    print("\tCreated timestamp:", farmer["createdDateTime"])
    print("\tLast modified timestamp:", farmer["modifiedDateTime"])

    await client.close()
    await credential.close()


if __name__ == "__main__":

    load_dotenv()
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(sample_hello_world_async())
