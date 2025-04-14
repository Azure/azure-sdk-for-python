# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: begin_test_profile_run.py

DESCRIPTION:
    This sample shows how to start a test profile run.

USAGE:
    python begin_test_profile_run.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
"""
from azure.developer.loadtesting import LoadTestRunClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer
# -loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

TEST_PROFILE_RUN_ID = "my-sdk-test-profile-run-id"
TEST_PROFILE_ID = "my-sdk-test-profile-id"

# Build a client through AAD and resource endpoint
client = LoadTestRunClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

testProfileRunPoller = client.begin_test_profile_run(
    TEST_PROFILE_RUN_ID,
    {
        "testProfileId": TEST_PROFILE_ID,
        "displayName": "My Test Profile Run Run",
    },
)

# waiting for test run status to be completed with timeout = 3600 seconds
result = testProfileRunPoller.result(3600)

print(result["status"])
print(result)
print(result["recommendations"])
