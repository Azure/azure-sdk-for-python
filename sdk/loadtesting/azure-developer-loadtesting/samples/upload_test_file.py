# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: upload_test_file.py

DESCRIPTION:
    This sample shows how to upload a file to your loadtest
USAGE:
    python upload_test_file.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice

    Please ensure that correct jmx file and path is used
"""
from azure.developer.loadtesting import LoadTestAdministrationClient

# for details refer: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/loadtestservice/azure-developer
# -loadtesting/README.md
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

client = LoadTestAdministrationClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"
FILE_NAME = "my-file-id.jmx"

# uploading .jmx file to a test
resultPoller = client.begin_upload_test_file(TEST_ID, FILE_NAME, open("sample.jmx", "rb"))
fileUploadResponse = resultPoller.get_initial_response()
print(fileUploadResponse)

# getting result of LRO poller with timeout of 600 secs
validationResponse = resultPoller.result(600)
print(validationResponse)
