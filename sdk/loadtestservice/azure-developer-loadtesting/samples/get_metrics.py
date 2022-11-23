# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_metics.py

DESCRIPTION:
    This sample shows how to get metrics for a test run

USAGE:
    python get_metrics.py

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

# importing os and dotenv for managing and loading environment variables
import os
from dotenv import load_dotenv

# for various
import time

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(authority="https://login.windows-ppe.net"), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"
TEST_RUN_ID = "my-new-load-test-run"

print(client.load_test_run.begin_test_run_status(TEST_RUN_ID))

test_run_response = client.load_test_run.get_test_run(TEST_RUN_ID)

# get metrics for a test run
metric_namespaces = client.load_test_run.list_metric_namespaces(TEST_RUN_ID)
print(metric_namespaces)

# get metrics for a test run
metric_definations = client.load_test_run.list_metric_definitions(TEST_RUN_ID, metric_namespace=metric_namespaces["value"][0]["name"])
print(metric_definations)

# fetch metrics for a test run using metric defination and namespace
metrics = client.load_test_run.list_metrics(
    TEST_RUN_ID,
    metricname=metric_definations["value"][0]["name"],
    metric_namespace=metric_namespaces["value"][0]["name"],
    timespan=test_run_response["startDateTime"]+"/"+test_run_response["endDateTime"]
)
print(metrics)

