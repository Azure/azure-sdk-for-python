# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: delete_load_test.py

DESCRIPTION:
    This sample shows how to delete a load test

USAGE:
    python delete_load_test.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
"""
# main library import
from azure.developer.loadtesting import LoadTestAdministrationClient

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

TEST_ID = "my-sdk-test-id"

# Build a client through AAD and resource endpoint
client = LoadTestAdministrationClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

client.delete_test(TEST_ID)
