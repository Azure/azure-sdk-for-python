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

    Please ensure that correct jmx file and path is used
"""
# main library import
from azure.developer.loadtesting import LoadTestingClient

# for managing authentication and authorization can be installed from pypi, follow:
# https://pypi.org/project/azure-identity/ using DefaultAzureCredentials, read more at:
# https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential?view=azure-python
from azure.identity import DefaultAzureCredential

# importing os and dotenv for managing and loading environment variables
import os
from dotenv import load_dotenv

# Set the values of the client ID, tenant ID, and client secret of the AAD application as environment variables:
# AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, SUBSCRIPTION_ID, RESOURCE_GROUP

# loading dotenv file
load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

# Build a client through AAD and resource endpoint
client = LoadTestingClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-new-sdk-test-id"
FILE_ID = "my-file-id"

# uploading .jmx file to a test
result = client.load_test_administration.upload_test_file(TEST_ID, FILE_ID, open("sample.jmx", "rb"))

print(result)
