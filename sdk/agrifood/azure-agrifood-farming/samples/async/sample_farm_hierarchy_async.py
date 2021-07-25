# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_farm_hierarchy_async.py

DESCRIPTION:
    This sample demonstrates
    - Creation of Farmer
    - Creation of Farm
    - Creation of Field
    - Creation of Boundary with a multipolygon GeoJSON

USAGE:
    ```python sample_farm_hierarchy_async.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from azure.agrifood.farming.models import Farmer, Farm, Field, Boundary, MultiPolygon
import os
import asyncio
from dotenv import load_dotenv


async def sample_farm_hierarchy_async():

    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    farmer_id = "contoso-farmer"
    farmer_name = "contoso-farmer-name"
    farmer_description = "contoso-farmer-description"
    farm_id = "contoso-farm"
    farm_name = "contoso-farm-name"
    farm_description = "contoso-farm-description"
    field_id = "contoso-field"
    field_name = "contoso-field-name"
    field_description = "contoso-field-description"
    boundary_id = "contoso-boundary"
    boundary_name = "contoso-boundary-name"
    boundary_description = "contoso-boundary-description"
    multi_polygon = MultiPolygon(
        coordinates=[
            [
                [
                    [-94.05807495, 44.75916947],
                    [-94.05802487, 44.7592142],
                    [-94.05798752, 44.75921875],
                    [-94.05692697, 44.75883808],
                    [-94.05697525, 44.75861334],
                    [-94.05542493, 44.75844192],
                    [-94.05537128, 44.75891045],
                    [-94.05443251, 44.75884951],
                    [-94.05086517, 44.75856001],
                    [-94.05093491, 44.75533736],
                    [-94.05389607, 44.75516594],
                    [-94.05421793, 44.75520023],
                    [-94.05447543, 44.75534879],
                    [-94.05746988, 44.75751702],
                    [-94.05795157, 44.75824385],
                    [-94.05805349, 44.75863619],
                    [-94.05807495, 44.75916947]
                ]
            ],
            [
                [
                    [-94.05802667, 44.75929136],
                    [-94.05793598, 44.7607673],
                    [-94.05693233, 44.76072738],
                    [-94.05694842, 44.76008746],
                    [-94.05727246, 44.75988264],
                    [-94.05752903, 44.75946416],
                    [-94.05760288, 44.75923042],
                    [-94.05802667, 44.75929136]
                ]
            ]
        ]
    )

    # Step 1: Create a farmer.
    print(
        f"Creating or updating farmer with Id {farmer_id}...", end=" ", flush=True)
    farmer = await client.farmers.create_or_update(
        farmer_id=farmer_id,
        farmer=Farmer(
            name=farmer_name,
            description=farmer_description
        )
    )
    print("Done")

    print("Details of farmer:")
    print("\tID:", farmer.id)
    print("\tName:", farmer.name)
    print("\tDescription:", farmer.description)

    # Step 2: Create a farm.
    print(
        f"Creating or updating farm with Id {farm_id}...", end=" ", flush=True)
    farm = await client.farms.create_or_update(
        farmer_id=farmer_id,
        farm_id= farm_id,
        farm=Farm(
            name=farm_name,
            description=farm_description
        )
    )
    print("Done")

    print("Details of farm:")
    print("\tID:", farm.id)
    print("\tName:", farm.name)
    print("\tFarmer Name:", farm.farmer_id)
    print("\tDescription:", farm.description)

    # Step 3: Create a field.
    print(
        f"Creating or updating field with Id {field_id}...", end=" ", flush=True)
    field = await client.fields.create_or_update(
        farmer_id=farmer_id,
        field_id= field_id,
        field=Field(
            name=field_name,
            farm_id=farm_id,
            description=field_description
        )
    )
    print("Done")

    print("Details of field:")
    print("\tID:", field.id)
    print("\tName:", field.name)
    print("\tFarmer Name:", field.farmer_id)
    print("\tFarm Name:", field.farm_id)
    print("\tName:", field.name)
    print("\tDescription:", field.description)

    # Step 4: Create a boundary.
    try:
        print(
            f"Trying to fetch boundary with id {boundary_id}...", end=" ", flush=True)
        boundary = await client.boundaries.get(
            farmer_id=farmer_id,
            boundary_id=boundary_id
        )
        print("Boundary already exists.")
    except ResourceNotFoundError:
        print(
            f"Doesn't exist. Creating boundary...", end=" ", flush=True)
        boundary = await client.boundaries.create_or_update(
            farmer_id=farmer_id,
            boundary_id=boundary_id,
            boundary=Boundary(
                name=boundary_name,
                geometry=multi_polygon,
                description=boundary_description
            )
        )
        print("Done")

    print("Details of boundary:")
    print("\tID:", boundary.id)
    print("\tName:", boundary.name)
    print("\tDescription:", boundary.description)

    await client.close()
    await credential.close()


if __name__ == "__main__":

    load_dotenv()

    asyncio.get_event_loop().run_until_complete(sample_farm_hierarchy_async())
