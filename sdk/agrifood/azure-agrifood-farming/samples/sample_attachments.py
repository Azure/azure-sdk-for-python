# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_attachments.py

DESCRIPTION:
    This sample demonstrates FarmBeats' capability of storing arbitrary files 
    in context to the various farm hierarchy objects. 
    We first attach some files onto a party and a farm, and then download all 
    existing attachments for the party onto a local directory.

USAGE:
    ```python sample_attachments.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`: The tenant ID of your active directory application.
    - `AZURE_CLIENT_ID`: The client ID of your active directory application.
    - `AZURE_CLIENT_SECRET`: The client secret of your active directory application.
    - `FARMBEATS_ENDPOINT`: The FarmBeats endpoint that you want to run these samples on.
"""


from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from pathlib import Path
import os
from dotenv import load_dotenv
import random
import pathlib


def sample_attachments():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()

    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    party_id = f"contoso-party-{random.randint(0,1000)}"
    farm_id = "contoso-farm"
    attachment_on_party_id = "contoso-party-attachment-1"
    attachment_on_farm_id = "contoso-farm-attachment-1"
    file_path = str(pathlib.Path(pathlib.Path(__file__).parent.resolve(), "test.txt"))
    attachment_on_party_file_path = file_path
    attachment_on_farm_file_path = file_path

    if not (os.path.isfile(attachment_on_party_file_path) and 
            os.path.isfile(attachment_on_farm_file_path)):
        raise SystemExit(
            "Please provide the paths to the files you want to upload."
        )

    # Ensure party exists, create if necessary.
    print(f"Create/updating party with id {party_id}...", end=" ", flush=True)
    client.parties.create_or_update(
        party_id=party_id,
        party={
            "name": "Contoso Party",
            "description": "Contoso Party.",
            "status": "Contoso Status",
            "properties": {
                "foo": "bar",
                "numeric one": 1,
                1: "numeric key"
            }
        }
    )
    print("Done!")

    # Ensure farm exists, create if necessary.
    print(f"Create/updating farm with id {farm_id}...", end=" ", flush=True)
    client.farms.create_or_update(
        party_id=party_id,
        farm_id=farm_id,
        farm={
            "name": "Contoso Farm",
            "description": "Contoso Farm.",
            "status": "Contoso Status"
        }
    )
    print("Done!")

    # Create attachment on party
    try:
        print(f"Checking if attachment with id {attachment_on_party_id} already exists "
            f"on party with id {party_id}...", end=" ", flush=True)
        client.attachments.get(
            party_id=party_id,
            attachment_id=attachment_on_party_id
        )
        print("Attachment already exists. Not updating file.")

    except ResourceNotFoundError:
        print("Attachment doesn't exist")
        print("Creating attachment...", end=" ", flush=True)

        # Open file with buffering set to 0, to get a IO object.
        file_to_attach_on_party = open(
            attachment_on_party_file_path,
            "rb")

        attachment = {
            "resourceId": party_id,
            "resourceType": "Party",
            "name": "a"
        }

        client.attachments.create_or_update(
            party_id=party_id,
            attachment_id=attachment_on_party_id,
            attachment=attachment,
            file=file_to_attach_on_party)

        print("Done!")
        
    # Create attachment with farm
    try:
        # Open file with buffering set to 0, to get a IO object.
        file_to_attach_on_farm = open(
            attachment_on_farm_file_path,
            "rb")

        attachment = {
            "resourceId": farm_id,
            "resourceType": "Farm",
            "name": "attachment name"
        }

        client.attachments.create_or_update(
            party_id=party_id,
            attachment_id=attachment_on_farm_id,
            attachment=attachment,
            file=file_to_attach_on_farm)

        print("Done!")
        
        print(f"Checking if attachment with id {attachment_on_farm_id} already exists " + 
            f"on farm with id {farm_id}...", end=" ", flush=True)
        client.attachments.get(
            party_id=party_id,
            attachment_id=attachment_on_farm_id
        )
        print("Attachment already exists. Not updating file.")

    except ResourceNotFoundError:
        print("Attachment doesn't exist")
        print("Creating attachment...", end=" ", flush=True)

        # Open file with buffering set to 0, to get a IO object.
        file_to_attach_on_farm = open(
            attachment_on_farm_file_path,
            "rb")

        attachment = {
            "resourceId": farm_id,
            "resourceType": "Farm",
            "name": "attachment name"
        }

        client.attachments.create_or_update(
            party_id=party_id,
            attachment_id=attachment_on_farm_id,
            attachment=attachment,
            file=file_to_attach_on_farm)

        print("Done!")


    print("Getting a list of all attachments " +
        f"on the party with id {party_id}...", end=" ", flush=True)
    party_attachments = client.attachments.list_by_party_id(
        party_id=party_id,
    )
    print("Done!")

    for attachment in party_attachments:

        downloaded_attachment = client.attachments.download(
            party_id=party_id,
            attachment_id=attachment_on_party_id
        )
        out_path = Path(
            "./data/attachments/" +
            f"{attachment['resourceType']}/{attachment['resourceId']}" +
            f"/{attachment['id']}/{attachment['originalFileName']}"
        )

        # Make sure the dirs to the output path exists
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)

        print(f"Saving attachment id {attachment['id']} to {out_path.resolve()}")
        with open(
                out_path,
                'wb'
                ) as out_file:
            for bits in downloaded_attachment:
                out_file.write(bits)
        

    print("Done!")

    
if __name__ == "__main__":

    load_dotenv()

    sample_attachments()
