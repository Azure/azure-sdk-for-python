# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient

# Simple example of how to:
# - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# - get relationship
#
# Preconditions:
# - Environment variables have to be set
# - DigitalTwins enabled device must exist on the ADT hub
try:
    # DefaultAzureCredential supports different authentication mechanisms and determines
    # the appropriate credential type based of the environment it is executing in.
    # It attempts to use multiple credential types in an order until it finds a working credential.

    # - AZURE_URL: The tenant ID in Azure Active Directory
    url = os.getenv("AZURE_URL")

    # DefaultAzureCredential expects the following three environment variables:
    # - AZURE_TENANT_ID: The tenant ID in Azure Active Directory
    # - AZURE_CLIENT_ID: The application (client) ID registered in the AAD tenant
    # - AZURE_CLIENT_SECRET: The client secret for the registered application
    credential = DefaultAzureCredential()
    service_client = DigitalTwinsClient(url, credential)

    # Get incoming relationship
    # from the samples: BuildingTwin, FloorTwin, HVACTwin, RoomTwin
    digital_twin_id = "<DIGITAL_TWIN_ID>"
    # from the samples: BuildingHasFloor, BuildingIsEquippedWithHVAC, HVACCoolsFloor, FloorContainsRoom
    relationship_id = "<RELATIONSHIP_ID>"
    relationship = service_client.get_relationship(digital_twin_id, relationship_id)
    print('Relationship:')
    print(relationship)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
