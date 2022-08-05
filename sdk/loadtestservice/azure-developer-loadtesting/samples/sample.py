# coding=utf-8
# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
# --------------------------------------------------------------------------
import logging
import os

from azure.developer.loadtesting import LoadTestingClient
from azure.identity import DefaultAzureCredential
import time

# can be installed using pip install azure-mgmt-loadtestservice
from azure.mgmt.loadtestservice import LoadTestClient
from azure.mgmt.loadtestservice.models import LoadTestResource

# using python dotenv library to load environment variables from a .env file
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, SUBSCRIPTION_ID, RESOURCE_GROUP

load_dotenv()

TEST_ID = "some-test-id"  # ID to be assigned to a test
FILE_ID = "some-file-id"  # ID to be assigned to file uploaded
TEST_RUN_ID = "some-testrun-id"  # ID to be assigned to a test run
APP_COMPONENT = "some-appcomponent-id"  # ID of the APP Component
DISPLAY_NAME = "my-loadtest"  # display name
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["RESOURCE_GROUP"]

# setting up management client
mgmt_client = LoadTestClient(
    credential=DefaultAzureCredential(),
    subscription_id=SUBSCRIPTION_ID,
)

# creating a new loadtest resource and getting its endpoint
endpoint = "https://" + mgmt_client.load_tests.create_or_update(
    resource_group_name=RESOURCE_GROUP,
    load_test_name="my-loadtesting-service",
    load_test_resource=LoadTestResource(
        location="eastus",
        description="my-loadtest",
    )
).data_plane_uri

print(f'Created loadtest resource with endpoint: {endpoint}')

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(), endpoint=endpoint)

result = client.load_test_administration.create_or_update_test(
    TEST_ID,
    {
        "description": "",
        "displayName": DISPLAY_NAME,
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

# uploading .jmx file to a test
result = client.load_test_administration.upload_test_file(TEST_ID, FILE_ID, open("sample.jmx", "rb"))
print(result)

# creating app component
result = client.load_test_administration.create_or_update_app_components(
    APP_COMPONENT,
    {
        "testId": TEST_ID,
        "value": {
            f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                "resourceId": f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                "resourceName": "App-Service-Sample-Demo",
                "resourceType": "Microsoft.Web/sites",
             }
        },
    },
)
print(result)

# Creating the test run
result = client.load_test_runs.create_or_update_test(
    TEST_RUN_ID,
    {
        "testId": TEST_ID,
        "displayName": DISPLAY_NAME,
    },
)
print(result)

# Checking the test run status and printing metrics
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

# deleting the test run
client.load_test_runs.delete_test_run(TEST_RUN_ID)

# deleting the test
client.load_test_administration.delete_load_test(TEST_ID)
