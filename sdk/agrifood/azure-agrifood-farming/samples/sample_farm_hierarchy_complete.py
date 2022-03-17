# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_farm_hierarchy_complete.py

DESCRIPTION:
    This sample demonstrates creation of the complete farm hierarchy
    - Creation of Farmer
    - Creation of Farm
    - Creation of Field
    - Creation of Crop and Crop Variety
    - Creation of Season and SeasonalField
    - Creation of Boundary with a multipolygon GeoJSON

USAGE:
    ```python sample_farm_hierarchy_complete.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Farmer, Farm, Field, Boundary, Crop, CropVariety, Season, SeasonalField, MultiPolygon
import os
from dotenv import load_dotenv


def sample_farm_hierarchy_complete():

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
    crop_id = "contoso-crop"
    crop_name = "contoso-crop-name"
    crop_description = "contoso-crop-description"
    crop_variety_id = "contoso-crop-variety"
    crop_variety_name = "contoso-crop_variety-name"
    crop_variety_description = "contoso-crop-variety-description"
    season_id = "contoso-season"
    season_name = "contoso-season-name"
    season_description = "contoso-season-description"
    seasonal_field_id = "contoso-seasonal_field"
    seasonal_field_name = "contoso-seasonal_field-name"
    seasonal_field_description = "contoso-seasonal_field-description"
    year = "2021"
    start_date_time = "2021-01-01T20:08:10.137Z"
    end_date_time = "2021-06-06T20:08:10.137Z"
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
    farmer = client.farmers.create_or_update(
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
    farm = client.farms.create_or_update(
        farmer_id=farmer_id,
        farm_id=farm_id,
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
    field = client.fields.create_or_update(
        farmer_id=farmer_id,
        field_id=field_id,
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

    # Step 4: Create a crop.
    print(
        f"Creating or updating crop with Id {crop_id}...", end=" ", flush=True)
    crop = client.crops.create_or_update(
        crop_id=crop_id,
        crop=Crop(
            name=crop_name,
            description=crop_description
        )
    )
    print("Done")

    print("Details of crop:")
    print("\tID:", crop.id)
    print("\tName:", crop.name)
    print("\tDescription:", crop.description)

    # Step 5: Create a crop variety.
    print(
        f"Creating or updating crop variety with Id {crop_variety_id}...", end=" ", flush=True)
    crop_variety = client.crop_varieties.create_or_update(
        crop_id=crop_id,
        crop_variety_id=crop_variety_id,
        crop_variety=CropVariety(
            name=crop_variety_name,
            description=crop_variety_description
        )
    )
    print("Done")

    print("Details of crop variety:")
    print("\tID:", crop_variety.id)
    print("\tCrop ID:", crop_variety.crop_id)
    print("\tName:", crop_variety.name)
    print("\tDescription:", crop_variety.description)

    # Step 6: Create a season.
    print(
        f"Creating or updating season with Id {season_id}...", end=" ", flush=True)
    season = client.seasons.create_or_update(
        season_id=season_id,
        season=Season(
            name=season_name,
            year=year,
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            description=season_description
        )
    )
    print("Done")

    print("Details of season:")
    print("\tID:", season.id)
    print("\tName:", season.name)
    print("\tDescription:", season.description)
    print("\tYear:", season.year)
    print("\tStart Date Time:", season.start_date_time)
    print("\tEnd Date Time:", season.end_date_time)

    # Step 7: Create a seasonal field.
    print(
        f"Creating or updating seasonal field with Id {seasonal_field_id}...", end=" ", flush=True)
    seasonal_field = client.seasonal_fields.create_or_update(
        farmer_id=farmer_id,
        seasonal_field_id=seasonal_field_id,
        seasonal_field=SeasonalField(
            name=seasonal_field_name,
            farm_id=farm_id,
            field_id=field_id,
            season_id=season_id,
            crop_id=crop_id,
            crop_variety_ids=[crop_variety_id],
            description=seasonal_field_description
        )
    )
    print("Done")

    print("Details of seasonal field:")
    print("\tID:", seasonal_field.id)
    print("\tName:", seasonal_field.name)
    print("\tFarmer Name:", seasonal_field.farmer_id)
    print("\tFarm Name:", seasonal_field.farm_id)
    print("\tCrop Name:", seasonal_field.crop_id)
    print("\tSeason Name:", seasonal_field.season_id)
    print("\tField Name:", seasonal_field.field_id)
    print("\tCrop Variety Name:", seasonal_field.crop_variety_ids)
    print("\tName:", seasonal_field.name)
    print("\tDescription:", seasonal_field.description)

    # Step 8: Create a boundary.
    try:
        print(
            f"Trying to fetch boundary with id {boundary_id}...", end=" ", flush=True)
        boundary = client.boundaries.get(
            farmer_id=farmer_id,
            boundary_id=boundary_id
        )
        print("Boundary already exists.")
    except ResourceNotFoundError:
        print(
            f"Doesn't exist. Creating boundary...", end=" ", flush=True)
        boundary = client.boundaries.create_or_update(
            farmer_id=farmer_id,
            boundary_id=boundary_id,
            boundary=Boundary(
                name=boundary_name,
                geometry=multi_polygon,
                parent_id=seasonal_field_id,
                description=boundary_description
            )
        )
        print("Done")

    print("\tDetails of boundary:")
    print("\tID:", boundary.id)
    print("\tName:", boundary.name)
    print("\tDescription:", boundary.description)
    print("\tParentId:", boundary.parent_id)


if __name__ == "__main__":

    load_dotenv()

    sample_farm_hierarchy_complete()
