# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

"""
FILE: sample_hello_world.py

DESCRIPTION:
    This sample demonstrates the most basic operation that can be 
    performed - creation of a Farmer. Use this to understand how to 
    create the client object, how to authenticate it, and make sure 
    your client is set up correctly to call into your FarmBeats endpoint.

USAGE:
    ```python sample_hello_world.py```

    Set the environment variables with your own values before running the sample:
    - `AZURE_TENANT_ID`
    - `AZURE_CLIENT_ID`
    - `AZURE_CLIENT_SECRET`
    - `FARMBEATS_ENDPOINT`
"""

from azure.identity import DefaultAzureCredential
from azure.agrifood.farming import FarmBeatsClient
from azure.agrifood.farming.models import Farmer
import os


class HelloWorldSample:

    @staticmethod
    def run(client):

        farmer_id = "contoso-farmer"
        farmer_name = "Contoso"
        farmer_description = "Contoso is hard working."

        print("Creating farmer, or updating if farmer already exists...", end=" ", flush=True)
        farmer = client.farmers.create_or_update(
            farmer_id=farmer_id,
            farmer=Farmer(
                name=farmer_name,
                description=farmer_description
            )
        )
        print("Done")
        
        print("Here are the details of the farmer:")
        print(f"ID: {farmer.id}")
        print(f"Name: {farmer.name}")
        print(f"Description: {farmer.description}")
        print(f"Created timestamp: {farmer.created_date_time}")
        print(f"Last modified timestamp: {farmer.modified_date_time}")


def main():

    # Create client
    try:
        farmbeats_endpoint = os.environ['FARMBEATS_ENDPOINT']
    except KeyError:
        raise SystemExit("Please set the 'FARMBEATS_ENDPOINT' env variable to your FarmBeats endpoint.")

    # Initialize credentials
    credential = DefaultAzureCredential()

    # Init client
    client = FarmBeatsClient(
        endpoint=farmbeats_endpoint,
        credential=credential
    )

    # Run the samples
    HelloWorldSample.run(client)


if __name__ == "__main__":
    
    main()

