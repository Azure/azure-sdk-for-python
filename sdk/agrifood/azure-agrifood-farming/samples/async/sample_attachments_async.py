# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_attachments_async.py

DESCRIPTION:
    This sample demonstrates FarmBeats' capabaility of storing arbitrary files 
    in context to the various farm hierarchy objects. 
    We first attach some files onto a farmer and a farm, and then download all 
    existing attachments for the farmer onto a local directory.

USAGE:
    ```python sample_attachments_async.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`
    - `AZURE_CLIENT_ID`
    - `AZURE_CLIENT_SECRET`
    - `FARMBEATS_ENDPOINT`
"""

from typing import Dict
from azure.core.exceptions import ResourceNotFoundError
from azure.identity.aio import DefaultAzureCredential
from azure.agrifood.farming.aio import FarmBeatsClient
from azure.agrifood.farming.models import Farmer
from pathlib import Path
import asyncio
import os
from dotenv import load_dotenv


async def sample_attachments_async():

    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']
    auth_authority = os.environ.get('AZURE_AUTHORITY')
    auth_scope = os.environ.get('FARMBEATS_SCOPE')

    credential = DefaultAzureCredential(
        authority=auth_authority
    )

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential,
        credential_scopes=[auth_scope]
    )

    farmer_id = "contoso-farmer"
    farm_id = "contoso-farm"
    attachment_on_farmer_id = "contoso-farmer-attachment-1"
    attachment_on_farm_id = "contoso-farm-attachment-1"
    attachment_on_farmer_file_path = "../test.txt"
    attachment_on_farm_file_path = "../test.txt"


    if not (os.path.isfile(attachment_on_farmer_file_path) and 
            os.path.isfile(attachment_on_farm_file_path)):
        raise SystemExit(
            "Please provide the paths to the files you want to upload."
    )

    # Ensure farmer exists, create if necessary.
    print(f"Create/updating farmer with id {farmer_id}...", end=" ", flush=True)
    await client.farmers.create_or_update(
        farmer_id=farmer_id,
        farmer=Farmer()
    )
    print("Done!")

    # Ensure farm exists, create if necessary.
    print(f"Create/updating farm with id {farm_id}...", end=" ", flush=True)
    await client.farms.create_or_update(
        farmer_id=farmer_id,
        farm_id=farm_id,
        farm=Farmer()
    )
    print("Done!")

    # Create attachment on farmer
    try:
        print(f"Checking if attachment with id {attachment_on_farmer_id} already exists "
            f"on farmer with id {farmer_id}...", end=" ", flush=True)
        await client.attachments.get(
            farmer_id=farmer_id,
            attachment_id=attachment_on_farmer_id
        )
        print("Attachment already exists. Not updating file.")

    except ResourceNotFoundError:
        print("Attachment doesn't exist")
        print("Creating attachment...", end=" ", flush=True)

        # Open file with buffering set to 0, to get a IO object.
        file_to_attach_on_farmer = open(
            attachment_on_farmer_file_path,
            "rb",
            buffering=0)

        await client.attachments.create_or_update(
            farmer_id=farmer_id,
            attachment_id=attachment_on_farmer_id,
            resource_id= farmer_id,
            resource_type="Farmer",
            file=file_to_attach_on_farmer)

        print("Done!")
        
    # Create attachment with farm
    try:
        print(f"Checking if attachment with id {attachment_on_farm_id} already exists " + 
            f"on farm with id {farm_id}...", end=" ", flush=True)
        await client.attachments.get(
            farmer_id=farmer_id,
            attachment_id=attachment_on_farm_id
        )
        print("Attachment already exists. Not updating file.")

    except ResourceNotFoundError:
        print("Attachment doesn't exist")
        print("Creating attachment...", end=" ", flush=True)

        # Open file with buffering set to 0, to get a IO object.
        file_to_attach_on_farm = open(
            attachment_on_farm_file_path,
            "rb",
            buffering=0)

        await client.attachments.create_or_update(
            farmer_id=farmer_id,
            attachment_id=attachment_on_farm_id,
            resource_id= farm_id,
            resource_type="Farm",
            file=file_to_attach_on_farm)

        print("Done!")
    
    print("Proceeding to download all attachments on the farmer. " +
        "Press enter to continue...")
    input()


    print("Getting a list of all attachments " +
        f"on the farmer with id {farmer_id}...", end=" ", flush=True)
    farmer_attachments = client.attachments.list_by_farmer_id(
        farmer_id=farmer_id,
    )
    print("Done!")

    # Using a semaphore to limit the number of concurrent downloads.
    semaphore =  asyncio.Semaphore(2)
    

    print("Downloading attachments with a maximum concurrency "+
        "of two downloads at a time...")

    # Setting up a async function (a coroutine) to download each attachment
    async def download(attachment, semaphore):
        async with semaphore:
            downloaded_attachment = await client.attachments.download(
                farmer_id=farmer_id,
                attachment_id=attachment_on_farmer_id
            )
            out_path = Path(
                "../data/attachments/" +
                f"{attachment.resource_type}/{attachment.resource_id}" +
                f"/{attachment.id}/{attachment.original_file_name}"
            )

            # Make sure the dirs to the output path exists
            out_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"Saving attachment id {attachment.id} to {out_path.resolve()}")
            with open(
                    out_path,
                    'wb'
                    ) as out_file:
                async for bits in downloaded_attachment:
                        out_file.write(bits)

    await asyncio.gather(
        *[download(attachment, semaphore) async for attachment in farmer_attachments]
    )
        
    print("Done!")

    await client.close()
    await credential.close()


if __name__ == "__main__":

    load_dotenv()

    asyncio.get_event_loop().run_until_complete(sample_attachments_async())
