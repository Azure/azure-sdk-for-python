# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import uuid
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient

# Scenario example of how to:
# - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# - create digital twin based on a model
# - get digital twin
# - update digital twin using JSON patch
# - delete digital twin
#
# Preconditions:
# - Environment variables have to be set
# - DigitalTwins enabled device must exist on the ADT hub
#
# For the purpose of this example we will create temporary digital twin using random Ids.
# We have to make sure these Ids are unique within the DT instance so we use generated UUIDs.
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

    # Create model first from sample dtdl
    with open(r"dtdl\models\building.json") as f:
        dtdl_model_building = json.load(f)
    new_model_list = []
    new_model_list.append(dtdl_model_building)
    model = service_client.create_models(new_model_list)
    print('Created Model:')
    print(model)

    # Create digital twin based on the created model
    digital_twin_id = 'digitalTwin-' + str(uuid.uuid4())
    with open(r"dtdl\digital_twins_\buildingTwin.json") as f:
        dtdl_digital_twins_building_twin = json.load(f)

    created_twin = service_client.upsert_digital_twin(digital_twin_id, dtdl_digital_twins_building_twin)
    print('Created Digital Twin:')
    print(created_twin)

    # Get digital twin
    get_twin = service_client.get_digital_twin(digital_twin_id)
    print('Get Digital Twin:')
    print(get_twin)

    # Update digital twin
    twin_patch = {
        "AverageTemperature": 42
    }
    updated_twin = service_client.update_digital_twin(digital_twin_id, twin_patch)
    print('Updated Digital Twin:')
    print(updated_twin)

    # Delete digital twin
    service_client.delete_digital_twin(digital_twin_id)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
