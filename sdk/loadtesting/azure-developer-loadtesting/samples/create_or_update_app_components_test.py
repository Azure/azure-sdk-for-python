# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: create_or_update_app_components_test.py

DESCRIPTION:
    This sample shows how to create or update app component for an existing test.

USAGE:
    python create_or_update_app_components_test.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  RESOURCE_ID - resource id of resource that will be added as the app component
    5)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
"""
from azure.developer.loadtesting import LoadTestAdministrationClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtesting/azure-developer-loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv


load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
RESOURCE_ID = os.environ["RESOURCE_ID"]

# Build a client through AAD and resource endpoint
client = LoadTestAdministrationClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"

result = client.create_or_update_app_components(
    TEST_ID,
    {
        "components": {
            RESOURCE_ID: {
                "resourceId": RESOURCE_ID,
                "resourceName": "App-Service-Sample-Demo",
                "resourceType": "Microsoft.Web/sites",
                "kind": "web",
            }
        },
    },
)

print(result)
