# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from typing import Dict
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Farmer
from pathlib import Path
import os

def main(client: FarmBeatsClient, config: Dict):

    farmer_id = config['farmer_id']
    farm_id = config['farm_id']
    attachment_on_farmer_id= config['attachment_on_farmer_id']
    attachment_on_farm_id=config['attachment_on_farm_id']
    attachment_on_farmer_file_path=config['attachment_on_farmer_file_path']
    attachment_on_farm_file_path=config['attachment_on_farm_file_path']

    if not (os.path.isfile(attachment_on_farmer_file_path) and 
            os.path.isfile(attachment_on_farm_file_path)):
        raise SystemExit("Please provide the paths to the files " +
            "in the config keys 'attachment_on_farmer_file_path' " +
            "and 'attachment_on_farm_file_path'"
        )

    # Ensure farmer exists, create if necessary.
    print(f"Create/updating farmer with id {farmer_id}...", end=" ", flush=True)
    client.farmers.create_or_update(
        farmer_id=farmer_id,
        farmer=Farmer()
    )
    print("Done!")

    # Ensure farm exists, create if necessary.
    print(f"Create/updating farm with id {farm_id}...", end=" ", flush=True)
    client.farms.create_or_update(
        farmer_id=farmer_id,
        farm_id=farm_id,
        farm=Farmer()
    )
    print("Done!")

    # Create attachment on farmer
    try:
        print(f"Checking if attachment with id {attachment_on_farmer_id} already exists "
            f"on farmer with id {farmer_id}...", end=" ", flush=True)
        client.attachments.get(
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

        client.attachments.create_or_update(
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
        client.attachments.get(
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

        client.attachments.create_or_update(
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

    print("Downloading attachments one at a time. Please refer to the" +
        "async sample to learn more about concurrent downloads."
    )

    for attachment in farmer_attachments:

        downloaded_attachment = client.attachments.download(
            farmer_id=farmer_id,
            attachment_id=attachment_on_farmer_id
        )
        out_path = \
            "./data/attachments/" + \
            f"{attachment.resource_type}/{attachment.resource_id}" + \
            f"/{attachment.id}/{attachment.original_file_name}"

        # Make sure the dirs to the output path exists
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"Saving attachment id {attachment.id} to {out_path}")
        with open(
                out_path,
                'wb'
                ) as out_file:
            for bits in downloaded_attachment:
                out_file.write(bits)
        

    print("All files downloaded into directory 'data/attachments/'")

    

if __name__ == "__main__":

    # config contains any data that might be used while running the sample.
    config = {
        'farmer_id': "contoso-farmer",
        'farm_id': "contoso-farm",
        'farmer_description': "Contoso is hard working.",
        'attachment_on_farmer_id': "contoso-farmer-attachment-1",
        'attachment_on_farm_id': "contoso-farm-attachment-1",
        'attachment_on_farmer_file_path': "./README.md",
        'attachment_on_farm_file_path': "./README.md",
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

    # Run the main function and dispose objects safely.
    main(client, config)