# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
from azure.digitaltwins.core import DigitalTwinsClient

# Scenario example of how to:
# - create a DigitalTwins Service Client using the DigitalTwinsClient constructor
# - create two models, one model and one component model
# - get created models by modelIds one by one
# - list all models by listing them using the paginated API
# - decomission the created models
# - delete the created models
#
# Preconditions:
# - Environment variables have to be set
# - DigitalTwins enabled device must exist on the ADT hub
#
# For the purpose of this example we will create temporary model and a temporay component model using random Ids.
# We have to make sure these model Ids are unique within the DT instance so we use generated UUIDs.
try:
    model_id = 'dtmi:samples:examplemodel;1'
    component_id = 'dtmi:samples:examplecomponent;1'

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
        },
        {
            "@type": "Telemetry",
            "name": "ComponentTelemetry1",
            "schema": "integer"
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
            "schema": "string"
        },
        {
            "@type": "Component",
            "name": "Component1",
            "schema": component_id
        },
        {
            "@type": "Telemetry",
            "name": "Telemetry1",
            "schema": "integer"
        }
        ]
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

    # Get created models
    get_component_model = service_client.get_model(component_id)
    print('Get Component Models:')
    print(get_component_model)

    get_model = service_client.get_model(model_id)
    print('Get Model:')
    print(get_model)

    # List all models
    listed_models = service_client.list_models()
    for model in listed_models:
        print(model)

    # Decomission models
    service_client.decommission_model(model_id)
    service_client.decommission_model(component_id)

    # Delete models
    service_client.delete_model(model_id)
    service_client.delete_model(component_id)

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
