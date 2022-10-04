# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_test_run_metrics.py

DESCRIPTION:
    This sample shows how to get test run metrics

USAGE:
    python get_test_run_metrics.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
"""
from azure.developer.loadtesting import LoadTestingClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer
# -loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

import time

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

TEST_RUN_ID = "my-new-load-test-run"
TEST_ID = "my-new-sdk-test-id"

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

# checking the test run stats and printing metrics
start_time = time.time()

TIMEOUT = 6000
REFRESH_TIME = 10

# pooling the test run status to get results
while time.time() - start_time < TIMEOUT:
    result = client.load_test_runs.get_test_run(TEST_RUN_ID)
    if result["status"] == "DONE" or result["status"] == "CANCELLED" or result["status"] == "FAILED":
        # getting the test run metrics filters
        client_metrics_filters = client.load_test_runs.get_test_run_client_metrics_filters(
            TEST_RUN_ID
        )

        # getting the test run metrics
        result_metrics = client.load_test_runs.get_test_run_client_metrics(
            TEST_RUN_ID,
            {
                "requestSamplers": ["GET"],
                "startTime": client_metrics_filters['timeRange']['startTime'],
                "endTime": client_metrics_filters['timeRange']['endTime']
            }
        )

        print(result_metrics)
        break

    else:
        time.sleep(REFRESH_TIME)
