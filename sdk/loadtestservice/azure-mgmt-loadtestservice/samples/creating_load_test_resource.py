# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: creating_load_test_resource.py

DESCRIPTION:
    This sample shows how to create Azure LoadTest Resource from mgmt API.

USAGE:
    python creating_load_test_resource.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  SUBSCRIPTION_ID - subscription id in which you want to create resource
    5)  RESOURCE_GROUP - resource group name in which you want to create resource
"""

# importing the main loadtestservice management api
from azure.mgmt.loadtestservice import LoadTestClient
from azure.mgmt.loadtestservice.models import LoadTestResource

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

SUBSCRIPTION_ID = os.environ["SUBSCRIPTION_ID"]
RESOURCE_GROUP = os.environ["RESOURCE_GROUP"]

# setting up management client
mgmt_client = LoadTestClient(
    credential=DefaultAzureCredential(),
    subscription_id=SUBSCRIPTION_ID
)

# creating a new loadtest resource
result = mgmt_client.load_tests.create_or_update(
    resource_group_name=RESOURCE_GROUP,
    load_test_name="new-loadtest-python-sdk",
    load_test_resource=LoadTestResource(
        location="eastus",
        description="New LoadTest Resource created via Python SDK"
    )
)

# getting dataplane url from loadtest
print(result.data_plane_uri)
