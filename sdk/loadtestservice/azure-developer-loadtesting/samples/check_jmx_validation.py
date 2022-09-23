# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: check_jmx_validation.py

DESCRIPTION:
    This sample shows how to check if a jmx file upload is validated
    success or not.

USAGE:
    python check_jmx_validation.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
"""
from azure.developer.loadtesting import LoadTestingClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer-loadtesting/README.md
from azure.identity import DefaultAzureCredential

# importing os and dotenv for managing and loading environment variables
import os
from dotenv import load_dotenv

# for various
import time

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-new-sdk-test-id"

# checking if jmx file is validated
start_time = time.time()

TIMEOUT = 6000
REFRESH_TIME = 10


while time.time() - start_time < TIMEOUT:
    result = client.load_test_administration.get_load_test(
        TEST_ID
    )

    # checking if the file was validated successfully
    if result["inputArtifacts"]["testScriptUrl"]["validationStatus"] == "VALIDATION_SUCCESS":
        break

    time.sleep(REFRESH_TIME)

if time.time() - start_time < TIMEOUT:
    print("Validation was successful")

else:
    print("System TimedOut")