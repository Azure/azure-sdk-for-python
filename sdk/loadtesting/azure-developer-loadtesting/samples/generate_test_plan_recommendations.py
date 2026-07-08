# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: generate_test_plan_recommendations.py

DESCRIPTION:
    This sample shows how to generate test plan recommendations for an existing load test with browser recording.

USAGE:
    python generate_test_plan_recommendations.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
    5)  LOADTESTSERVICE_TEST_ID - The ID of the load test for which to generate recommendations, it should have browser recording file before generating recommendations.
"""
from azure.developer.loadtesting import LoadTestAdministrationClient
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
TEST_ID = os.environ["LOADTESTSERVICE_TEST_ID"]

client = LoadTestAdministrationClient(
    credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT
)

# Generate test plan recommendations
print("Generating test plan recommendations...")
poller = client.begin_generate_test_plan_recommendations(TEST_ID)

# Wait for the operation to complete
result = poller.result()
print(f"Test plan recommendations generated: {result}")
print(f"Operation status: {poller.status()}")
