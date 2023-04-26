# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_farm_hierarchy_complete_async.py

DESCRIPTION:
    This sample demonstrates creation of the complete farm hierarchy
    - Creation of Party
    - Creation of Farm
    - Creation of Field
    - Creation of Crop and Crop Variety
    - Creation of Season and SeasonalField
    - Creation of Boundary with a multipolygon GeoJSON

USAGE:
    ```python sample_farm_hierarchy_complete_async.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
import os
import asyncio
from dotenv import load_dotenv
import random


async def sample_farm_hierarchy_complete_async():

    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    party_id = f"contoso-party-{random.randint(0,1000)}"
    party_name = "contoso-party-name"
    party_description = "contoso-party-description"
    farm_id = "contoso-farm"
    farm_name = "contoso-farm-name"
    farm_description = "contoso-farm-description"
    field_id = "contoso-field"
    field_name = "contoso-field-name"
    field_description = "contoso-field-description"
    boundary_id = "contoso-boundary"
    boundary_name = "contoso-boundary-name"
    boundary_description = "contoso-boundary-description"
    crop_id = "contoso-crop"
    crop_name = "contoso-crop-name"
    crop_description = "contoso-crop-description"
    crop_product_id = "contoso-crop-product"
    crop_product_name = "contoso-crop_product-name"
    crop_product_description = "contoso-crop-product-description"
    season_id = "contoso-season"
    season_name = "contoso-season-name"
    season_description = "contoso-season-description"
    seasonal_field_id = "contoso-seasonal_field"
    seasonal_field_name = "contoso-seasonal_field-name"
    seasonal_field_description = "contoso-seasonal_field-description"
    year = "2021"
    start_date_time = "2021-01-01T20:08:10.137Z"
    end_date_time = "2021-06-06T20:08:10.137Z"
    multi_polygon = {
        "type": "MultiPolygon",
        "coordinates": [
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
    }

    # Step 1: Create a party.
    print(
        f"Creating or updating party with Id {party_id}...", end=" ", flush=True)
    party = await client.parties.create_or_update(
        party_id=party_id,
        party={
            "name": party_name,
            "description": party_description
        }
    )
    print("Done")

    print("Details of party:")
    print("\tID:", party["id"])
    print("\tName:", party["name"])
    print("\tDescription:", party["description"])

    # Step 2: Create a farm.
    print(
        f"Creating or updating farm with Id {farm_id}...", end=" ", flush=True)
    farm = await client.farms.create_or_update(
        party_id=party_id,
        farm_id=farm_id,
        farm={
            "name": farm_name,
            "description": farm_description
        }
    )
    print("Done")

    print("Details of farm:")
    print("\tID:", farm["id"])
    print("\tName:", farm["name"])
    print("\tParty Id:", farm["partyId"])
    print("\tDescription:", farm["description"])

    # Step 3: Create a field.
    print(
        f"Creating or updating field with Id {field_id}...", end=" ", flush=True)
    field = await client.fields.create_or_update(
        party_id=party_id,
        field_id=field_id,
        field={
            "name": field_name,
            "farmId": farm_id,
            "description": field_description
        }
    )
    print("Done")

    print("Details of field:")
    print("\tID:", field["id"])
    print("\tName:", field["name"])
    print("\tParty Id:", field["partyId"])
    print("\tFarm Id:", field["farmId"])
    print("\tName:", field["name"])
    print("\tDescription:", field["description"])

    # Step 4: Create a crop.
    print(
        f"Creating or updating crop with Id {crop_id}...", end=" ", flush=True)
    crop = await client.crops.create_or_update(
        crop_id=crop_id,
        crop={
            "name": crop_name,
            "description": crop_description
        }
    )
    print("Done")

    print("Details of crop:")
    print("\tID:", crop["id"])
    print("\tName:", crop["name"])
    print("\tDescription:", crop["description"])

    # Step 5: Create a crop product.
    print(
        f"Creating or updating crop product with Id {crop_product_id}...", end=" ", flush=True)
    crop_product = await client.crop_products.create_or_update(
        crop_product_id=crop_product_id,
        crop_product={
            "name": crop_product_name,
            "description": crop_product_description
        }
    )
    print("Done")

    print("Details of crop product:")
    print("\tID:", crop_product["id"])
    print("\tName:", crop_product["name"])
    print("\tDescription:", crop_product["description"])

    # Step 6: Create a season.
    print(
        f"Creating or updating season with Id {season_id}...", end=" ", flush=True)
    season = await client.seasons.create_or_update(
        season_id=season_id,
        season={
            "name": season_name,
            "year": year,
            "startDateTime": start_date_time,
            "endDateTime": end_date_time,
            "description": season_description
        }
    )
    print("Done")

    print("Details of season:")
    print("\tID:", season["id"])
    print("\tName:", season["name"])
    print("\tDescription:", season["description"])
    print("\tYear:", season["year"])
    print("\tStart Date Time:", season["startDateTime"])
    print("\tEnd Date Time:", season["endDateTime"])

    # Step 7: Create a seasonal field.
    print(
        f"Creating or updating seasonal field with Id {seasonal_field_id}...", end=" ", flush=True)
    seasonal_field = await client.seasonal_fields.create_or_update(
        party_id=party_id,
        seasonal_field_id=seasonal_field_id,
        seasonal_field={
            "name": seasonal_field_name,
            "farmId": farm_id,
            "fieldId": field_id,
            "seasonId": season_id,
            "cropId": crop_id,
            "cropProductIds": [crop_product_id],
            "description": seasonal_field_description
        }
    )
    print("Done")

    print("Details of seasonal field:")
    print("\tID:", seasonal_field["id"])
    print("\tName:", seasonal_field["name"])
    print("\tParty Name:", seasonal_field["partyId"])
    print("\tFarm Name:", seasonal_field["farmId"])
    print("\tCrop Name:", seasonal_field["cropId"])
    print("\tSeason Name:", seasonal_field["seasonId"])
    print("\tField Name:", seasonal_field["fieldId"])
    print("\tCrop Variety Name:", seasonal_field["cropProductIds"])
    print("\tName:", seasonal_field["name"])
    print("\tDescription:", seasonal_field["description"])

    # Step 8: Create a boundary.
    try:
        print(
            f"Trying to fetch boundary with id {boundary_id}...", end=" ", flush=True)
        boundary = await client.boundaries.get(
            party_id=party_id,
            boundary_id=boundary_id
        )
        print("Boundary already exists.")
    except ResourceNotFoundError:
        print(
            f"Doesn't exist. Creating boundary...", end=" ", flush=True)
        boundary = await client.boundaries.create_or_update(
            party_id=party_id,
            boundary_id=boundary_id,
            boundary={
                "name": boundary_name,
                "geometry": multi_polygon,
                "parentId": seasonal_field_id,
                "parentType": "SeasonalField",
                "description": boundary_description
            }
        )
        print("Done")

    print("\tDetails of boundary:")
    print("\tID:", boundary["id"])
    print("\tName:", boundary["name"])
    print("\tDescription:", boundary["description"])
    print("\tParentId:", boundary["parentId"])

    await client.close()
    await credential.close()


if __name__ == "__main__":

    load_dotenv()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.run(sample_farm_hierarchy_complete_async())
