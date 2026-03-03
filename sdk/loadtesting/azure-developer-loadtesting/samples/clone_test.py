# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: clone_test.py

DESCRIPTION:
    This sample shows how to clone an existing load test.

USAGE:
    python clone_test.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
    5)  SOURCE_TEST_ID - The ID of the existing load test to be cloned
"""
from azure.developer.loadtesting import LoadTestAdministrationClient
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

client = LoadTestAdministrationClient(
    credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT
)

SOURCE_TEST_ID = os.environ["SOURCE_TEST_ID"]
NEW_TEST_ID = "my-cloned-test-id"

# Clone the test
print(f"Cloning test '{SOURCE_TEST_ID}' to '{NEW_TEST_ID}'...")
poller = client.begin_clone_test(
    SOURCE_TEST_ID,
    new_test_id=NEW_TEST_ID,
    display_name="My Cloned Load Test",
    description="This is a cloned load test",
)

# Wait for the operation to complete
result = poller.result()
print(f"Test cloned successfully: {result}")
print(f"Operation status: {poller.status()}")

# Get the cloned test to verify
cloned_test = client.get_test(NEW_TEST_ID)
print("\nCloned test details:")
print(f"  Test ID: {cloned_test['testId']}")
print(f"  Display Name: {cloned_test['displayName']}")
print(f"  Description: {cloned_test.get('description', 'N/A')}")
