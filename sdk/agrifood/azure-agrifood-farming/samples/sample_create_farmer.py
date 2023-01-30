import os
from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from dotenv import load_dotenv
import random


def create_farmer():
    farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']

    credential = DefaultAzureCredential()
    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    farmer_id = f"contoso-farmer-{random.randint(0,1000)}"

    # Create or update a farmer within FarmBeats.
    farmer = client.farmers.create_or_update(
        farmer_id=farmer_id,
        farmer={
            "name": "contoso farmersdk",
            "status": "created from SDK",
            "description": "created from SDK"
        }
    )
    print(farmer)

if __name__ == "__main__":

    load_dotenv()

    create_farmer()