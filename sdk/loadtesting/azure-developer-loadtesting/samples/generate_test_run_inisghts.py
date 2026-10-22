# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: generate_test_run_insights.py

DESCRIPTION:
    This sample shows how to generate and fetch actionable insights for a completed test run.

USAGE:
    python generate_test_run_insights.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
    5)  LOADTESTSERVICE_COMPLETED_TEST_RUN_ID - The ID of a completed test run for which we need to generate insights
"""
from azure.developer.loadtesting import LoadTestRunClient
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
COMPLETED_TEST_RUN_ID = os.environ["LOADTESTSERVICE_COMPLETED_TEST_RUN_ID"]

client = LoadTestRunClient(
    credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT
)

# Generate test run insights
print(f"Generating insights for test run '{COMPLETED_TEST_RUN_ID}'...")
poller = client.begin_generate_test_run_insights(COMPLETED_TEST_RUN_ID)

# Wait for the operation to complete
result = poller.result()
print(f"Insights generation completed: {result}")
print(f"Operation status: {poller.status()}")

# Fetch the latest insights
print(f"\nFetching latest insights for test run '{COMPLETED_TEST_RUN_ID}'...")
insights = client.get_latest_test_run_insights(COMPLETED_TEST_RUN_ID)
print(f"Latest insights: {insights}")