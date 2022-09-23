# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: create_or_update_test.py

DESCRIPTION:
    This sample shows how to create or update a load test

USAGE:
    python create_or_update_test.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
"""
from azure.developer.loadtesting import LoadTestingClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer-loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

# ID to be assigned to test
TEST_ID = "my-new-sdk-test-id"

result = client.load_test_administration.create_or_update_test(
    TEST_ID,
    {
        "description": "",
        "displayName": "My New Load Test",
        "loadTestConfig": {
            "engineInstances": 1,
            "splitAllCSVs": False,
        },
        "secrets": {},
        "environmentVariables": {},
        "passFailCriteria": {"passFailMetrics": {}}
    },
)

print(result)
