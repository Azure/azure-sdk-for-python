# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: create_or_update_test_profile.py

DESCRIPTION:
    This sample shows how to create or update a test profile

USAGE:
    python create_or_update_test_profile.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
    5)  LOADTESTSERVICE_TARGET_RESOURCE_ID - ResourceID of a Flex Consumptions Function
"""
from azure.developer.loadtesting import LoadTestAdministrationClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtesting/azure-developer-loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
TARGET_RESOURCE_ID = os.environ["LOADTESTSERVICE_TARGET_RESOURCE_ID"]

# Build a client through AAD and resource endpoint
client = LoadTestAdministrationClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"

# ID to be assigned to test profile
TEST_PROFILE_ID = "my-sdk-test-profile-id"


result = client.create_or_update_test_profile(
    TEST_PROFILE_ID,
    {
        "description": "",
        "displayName": "My New Test Profile",
        "testId": TEST_ID,
        "targetResourceId": TARGET_RESOURCE_ID,
        "targetResourceConfigurations": {
            "kind": "FunctionsFlexConsumption",
            "configurations": {
                "config1": {
                    "instanceMemoryMB": 2048,
                    "httpConcurrency": 20,
                },
                "config2": {
                    "instanceMemoryMB": 4096,
                    "httpConcurrency": 100,
                }
            }
        }
    },
)

print(result)
