# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: hero.py

DESCRIPTION:
    This sample contain hero/champion scenarios for loadtestservice.

USAGE:
    python check_jmx_validation.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
    5) SUBSCRIPTION_ID - Subscription Id
"""
import sys

from azure.developer.loadtesting import LoadTestingClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer
# -loadtesting/README.md
from azure.identity import DefaultAzureCredential

# importing os and dotenv for managing and loading environment variables
import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(authority="https://login.windows-ppe.net"), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-hero-test-id"
TEST_RUN_ID = "my-hero-test-run-id"
FILE_NAME = "my-hero-jmx-file.jmx"

# creating a loadtest
try:
    result = client.load_test_administration.create_or_update_test(
        TEST_ID,
        {
            "description": "",
            "displayName": "My New Load Test",
            "loadTestConfig": {
                "engineInstances": 1,
                "splitAllCSVs": False,
            },
            "passFailCriteria": {
                "passFailMetrics": {

                }
            },
            "secrets": {

            },
            "environmentVariables": {

            },
        }
    )
    print("Created a loadtest with id: {} and response: {}".format(TEST_ID, result))

except Exception as e:
    print("Error occurred while creating a loadtest: {}".format(e))


# adding JMX file to loadtest
try:
    result = client.load_test_administration.upload_test_file(
        TEST_ID, FILE_NAME, open("sample.jmx", "rb")
    )
    print("Uploaded JMX file to loadtest with id: {} and response: {}".format(TEST_ID, result))

except Exception as e:
    print("Error occurred while uploading JMX file to loadtest: {}".format(e))


# check for JMX file validation status
try:
    result = client.load_test_administration.begin_get_test_script_validation_status(
        TEST_ID
    )
    print("JMX file validation status {}".format(result))

except Exception as e:
    print("Error occurred while checking JMX file validation status: {}".format(e))


# attaching App Component to loadtest
try:
    result = client.load_test_administration.create_or_update_app_components(
        "my-app-component-id",
        {
            "testId": TEST_ID,
            "value": {
                f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers/Microsoft.Web"
                f"/sites/App-Service-Sample-Demo": {
                    "resourceId": f"/subscriptions/{SUBSCRIPTION_ID}/resourceGroups/App-Service-Sample-Demo-rg/providers"
                                  f"/Microsoft.Web/sites/App-Service-Sample-Demo",
                    "resourceName": "App-Service-Sample-Demo",
                    "resourceType": "Microsoft.Web/sites",
                }
            },
        },
    )

    print("Attached App Component to loadtest with response: {}".format(result))

except Exception as e:
    print("Error occurred while attaching App Component to loadtest: {}".format(e))


# start running the loadtest
try:
    result = client.load_test_run.create_or_update_test_run(
        TEST_RUN_ID,
        {
            "testId": TEST_ID,
            "displayName": "My New Load Test Run",
        },
    )
    print("Started running the loadtest with id: {} and response: {}".format(TEST_RUN_ID, result))

except Exception as e:
    print("Error occurred while starting the loadtest: {}".format(e))


# waiting for loadtest to complete
try:
    result = client.load_test_run.begin_test_run_status(
        TEST_RUN_ID,
        timeout=600,
        refresh_time=10
    )
    print("Loadtest status: {}".format(result))

    from azure.developer.loadtesting import TestRunStatus

    if result == TestRunStatus.CheckTimeout:
        # stop the loadtest
        try:
            result = client.load_test_run.stop_test_run(TEST_RUN_ID)
            print("Stopped the loadtest with id: {} and response: {}".format(TEST_RUN_ID, result))
        except Exception as e:
            print("Error occurred while stopping the loadtest: {}".format(e))

    if not result == TestRunStatus.Done:
        sys.exit(1)

except Exception as e:
    print("Error occurred while checking loadtest status: {}".format(e))


# get metrics for a test run
try:
    metric_namespaces = client.load_test_run.list_metric_namespaces(TEST_RUN_ID)
    print("Metric namespaces: {}".format(metric_namespaces))

except Exception as e:
    print("Error occurred while getting metric namespaces: {}".format(e))


# get metrics for a test run
try:
    metric_definations = client.load_test_run.list_metric_definitions(TEST_RUN_ID, metric_namespace=metric_namespaces["value"][0]["name"])
    print("Metric definations: {}".format(metric_definations))

except Exception as e:
    print("Error occurred while getting metric definations: {}".format(e))


# fetch metrics for a test run using metric defination and namespace
try:
    test_run_response = client.load_test_run.get_test_run(TEST_RUN_ID)

    metrics = client.load_test_run.list_metrics(
        TEST_RUN_ID,
        metricname=metric_definations["value"][0]["name"],
        metric_namespace=metric_namespaces["value"][0]["name"],
        timespan=test_run_response["startDateTime"]+"/"+test_run_response["endDateTime"]
    )
    print("Metrics: {}".format(metrics))

except Exception as e:
    print("Error occurred while fetching metrics: {}".format(e))

# deleting test run
try:
    result = client.load_test_run.delete_test_run(TEST_RUN_ID)
    print("Deleted test run with id: {} and response: {}".format(TEST_RUN_ID, result))

except Exception as e:
    print("Error occurred while deleting test run: {}".format(e))


# deleting loadtest
try:
    result = client.load_test_administration.delete_test(TEST_ID)
    print("Deleted loadtest with id: {} and response: {}".format(TEST_ID, result))

except:
    print("Error occurred while deleting loadtest: {}".format(e))
