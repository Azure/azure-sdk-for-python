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

from azure.developer.loadtestservice import LoadTestClient
from azure.identity import DefaultAzureCredential
from azure.core.exceptions import HttpResponseError
import time

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, LOADTESTSERVICE_ENDPOINT

# using python dotenv library to load environment variables from a .env file
from dotenv import load_dotenv

load_dotenv()

try:
    endpoint = os.environ["LOADTESTSERVICE_ENDPOINT"]
except KeyError:
    LOG.error("Missing environment variable 'LOADTESTSERVICE_ENDPOINT' - please set if before running the example")
    exit()
# Build a client through AAD
client = LoadTestClient(credential=DefaultAzureCredential(), endpoint=endpoint)


TEST_ID = "a011890b-0201-004d-010d-1200d888bb11"  # ID to be assigned to a test
FILE_ID = "a012b234-1230-ab00-0040-ab12c4501111"  # ID to be assigned to file uploaded
TEST_RUN_ID = "08673e89-3285-46a1-9c6b-7e5ecba39111"  # ID to be assigned to a test run
APP_COMPONENT = "01730263-6671-4216-b283-8b28ed953111"  # ID of the APP Component
DISPLAY_NAME = "example_application"  # display name

# creating load test
try:
    result = client.test.create_or_update_test(
        TEST_ID,
        {
            "resourceId": "/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/yashika-rg/providers/Microsoft.LoadTestService/loadtests/loadtestsdk",
            "description": "",
            "displayName": DISPLAY_NAME,
            "loadTestConfig": {
                "engineSize": "m",
                "engineInstances": 1,
                "splitAllCSVs": False,
            },
            "secrets": {},
            "environmentVariables": {},
            "passFailCriteria": {"passFailMetrics": {}},
            "keyvaultReferenceIdentityType": "SystemAssigned",
            "keyvaultReferenceIdentityId": None,
        },
    )
    print(result)
except HttpResponseError as e:
    print("Failed to process the request: {}".format(e.response.json()))
# uploading .jmx file to a test
try:
    # opening .jmx file
    body = {}
    body["file"] = open("sample.jmx", "rb")

    result = client.test.upload_test_file(TEST_ID, FILE_ID, body)
    print(result)
except HttpResponseError as e:
    print("Failed to send JSON message: {}".format(e.response.json()))
# creating app component
try:
    result = client.app_component.create_or_update_app_components(
        APP_COMPONENT,
        {
            "name": "app_component",
            "testId": TEST_ID,
            "value": {
                "/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo": {
                    "resourceId": "/subscriptions/7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web/sites/App-Service-Sample-Demo",
                    "resourceName": "App-Service-Sample-Demo",
                    "resourceType": "Microsoft.Web/sites",
                    "subscriptionId": "7c71b563-0dc0-4bc0-bcf6-06f8f0516c7a",
                }
            },
        },
    )
    print(result)
except HttpResponseError as e:
    print("Failed to send JSON message: {}".format(e.response.json()))
# Creating the test run
try:
    result = client.test_run.create_and_update_test(
        TEST_RUN_ID,
        {
            "testId": TEST_ID,
            "displayName": DISPLAY_NAME,
            "requestSamplers": [],
            "errors": [],
            "percentiles": ["90"],
            "groupByInterval": "5s",
        },
    )
    print(result)
except HttpResponseError as e:
    print("Failed to send JSON message: {}".format(e.response.json()))
# Checking the test run status and printing metrics
try:
    start_time = time.time()

    TIMEOUT = 6000
    REFRESH_RATE = 10

    while time.time() - start_time < TIMEOUT:
        result = client.test_run.get_test_run(TEST_RUN_ID)
        if result["status"] == "DONE" or result["status"] == "CANCELLED" or result["status"] == "FAILED":
            break
        else:
            time.sleep(REFRESH_RATE)
    print(result)
except HttpResponseError as e:
    print("Failed to send JSON message: {}".format(e.response.json()))
