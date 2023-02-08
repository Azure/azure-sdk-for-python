import os
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from dotenv import load_dotenv
import random


def create_party():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()
    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    party_id = f"contoso-party-{random.randint(0,1000)}"

    # Create or update a party within FarmBeats.
    party = client.parties.create_or_update(
        party_id=party_id,
        party={
            "name": "contoso party sdk",
            "status": "created from SDK",
            "description": "created from SDK"
        }
    )
    print(party)

if __name__ == "__main__":

    load_dotenv()

    create_party()