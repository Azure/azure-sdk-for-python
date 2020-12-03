# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import uuid
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient

# Scenario example of how to:
# - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# - create model, component and twin
# - create digital twin based on the model
# - update component
# - get component
# - delete twin
# - decomission and delete model, component
#
# Preconditions:
# - Environment variables have to be set
# - DigitalTwins enabled device must exist on the ADT hub
#
# For the purpose of this example we will create temporary digital twin using random Ids.
# We have to make sure these model Ids are unique within the DT instance so we use generated UUIDs.
try:
    model_id = 'dtmi:samples:componentlifecyclemodel;1'
    component_id = 'dtmi:samples:componentlifecycle;1'
    digital_twin_id = 'digitalTwin-' + str(uuid.uuid4())

    temporary_component = {
        "@id": component_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "Component1",
        "contents": [
        {
            "@type": "Property",
            "name": "ComponentProp1",
            "schema": "string"
        }
        ]
    }

    temporary_model = {
        "@id": model_id,
        "@type": "Interface",
        "@context": "dtmi:dtdl:context;2",
        "displayName": "TempModel",
        "contents": [
        {
            "@type": "Property",
            "name": "Prop1",
            "schema": "double"
        },
        {
            "@type": "Component",
            "name": "Component1",
            "schema": component_id
        }
        ]
    }

    temporary_twin = {
        "$metadata": {
            "$model": model_id
        },
        "$dtId": digital_twin_id,
        "Prop1": 42,
        "Component1": {
            "$metadata": {},
        "ComponentProp1": "value1"
        }
    }

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

    # Create models
    new_models = [temporary_component, temporary_model]
    models = service_client.create_models(new_models)
    print('Created Models:')
    print(models)

    # Create digital twin
    created_twin = service_client.upsert_digital_twin(digital_twin_id, temporary_twin)
    print('Created Digital Twin:')
    print(created_twin)

    # Update component
    component_name = "Component1"
    patch = [
        {
            "op": "replace",
            "path": "/ComponentProp1",
            "value": "value2"
        }
    ]
    service_client.update_component(digital_twin_id, component_name, patch)

    # Get component
    get_component = service_client.get_component(digital_twin_id, component_name)
    print('Get Component:')
    print(get_component)

    # Delete digital twin
    service_client.delete_digital_twin(digital_twin_id)

    # Decomission models
    service_client.decommission_model(model_id)
    service_client.decommission_model(component_id)

    # Delete models
    service_client.delete_model(model_id)
    service_client.delete_model(component_id)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
