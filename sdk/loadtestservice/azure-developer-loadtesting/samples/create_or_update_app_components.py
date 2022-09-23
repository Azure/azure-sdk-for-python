# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: create_or_update_test.py

DESCRIPTION:
    This sample shows how to create or update app component

USAGE:
    python create_or_update_app_components.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  SUBSCRIPTION_ID - in which resource to connect is/are present
"""
from azure.developer.loadtesting import LoadTestingClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer-loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv


load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-new-sdk-test-id"
APP_COMPONENT = "my-new-app-component"

result = client.load_test_administration.create_or_update_app_components(
    APP_COMPONENT,
    {
        "testId": TEST_ID,
        "value": {
            f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web"
            f"/sites/App-Service-Sample-Demo": {
                "resourceId": f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers"
                              f"/Microsoft.Web/sites/App-Service-Sample-Demo",
                "resourceName": "App-Service-Sample-Demo",
                "resourceType": "Microsoft.Web/sites",
             }
        },
    },
)

print(result)
