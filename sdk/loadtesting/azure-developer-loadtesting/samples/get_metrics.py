# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: get_metrics.py

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
from azure.developer.loadtesting import LoadTestRunClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer
# -loadtesting/README.md
from azure.identity import DefaultAzureCredential

# importing os and dotenv for managing and loading environment variables
import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

# Build a client through AAD and resource endpoint
client = LoadTestRunClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"
TEST_RUN_ID = "my-sdk-test-run-id"

test_run_response = client.get_test_run(TEST_RUN_ID)

# get a list of metric namespaces for a given test run
metric_namespaces = client.get_metric_namespaces(TEST_RUN_ID)
print(metric_namespaces)

# get a list of metric definitions for a given test run and metric namespace
metric_definitions = client.get_metric_definitions(TEST_RUN_ID, metric_namespace=metric_namespaces["value"][0]["name"])
print(metric_definitions)

# fetch metrics for a test run using metric definition and namespace
metrics = client.list_metrics(
    TEST_RUN_ID,
    metric_name=metric_definitions["value"][0]["name"],
    metric_namespace=metric_namespaces["value"][0]["name"],
    time_interval=test_run_response["startDateTime"] + "/" + test_run_response["endDateTime"],
)

for page in metrics.by_page():
    for data in page:
        print(data)
