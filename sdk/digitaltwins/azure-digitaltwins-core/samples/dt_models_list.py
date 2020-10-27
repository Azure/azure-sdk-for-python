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
# - list all models using the paginated API
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

    # List models
    # from the samples: dtmi:samples:Room1, dtmi:samples:Wifi1, dtmi:samples:Floor1, dtmi:samples:Building1
    dependecies_for = ["<MODEL_ID>"]
    models = service_client.list_models(dependecies_for)
    for model in models:
        print(model + '\n')

except HttpResponseError as e:
    print("\nThis sample has caught an error. {0}".format(e.message))
