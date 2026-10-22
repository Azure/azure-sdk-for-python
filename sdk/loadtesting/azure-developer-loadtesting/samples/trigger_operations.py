# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: trigger_operations.py

DESCRIPTION:
    This sample shows how to create, get, list, and delete a scheduled trigger
    for load tests.

USAGE:
    python trigger_operations.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
"""
from azure.developer.loadtesting import LoadTestAdministrationClient
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]

# Build a client through AAD and resource endpoint
client = LoadTestAdministrationClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"
TRIGGER_ID = "my-sdk-trigger-id"

# Create or update a trigger
print("Creating trigger...")
trigger = client.create_or_update_trigger(
    TRIGGER_ID,
    {
        "displayName": "My Daily Trigger",
        "description": "Trigger to run load tests daily",
        "kind": "ScheduleTestsTrigger",
        "testIds": [TEST_ID],
        "recurrence": {
            "frequency": "Daily",
            "interval": 1,
        },
        "startDateTime": "2026-04-01T08:00:00.000Z",
    },
)
print(f"Trigger created: {trigger}")

# Get a trigger
print("\nGetting trigger...")
trigger = client.get_trigger(TRIGGER_ID)
print(f"Trigger retrieved: {trigger}")

# List all triggers
print("\nListing all triggers...")
triggers = client.list_triggers()
for t in triggers:
    print(f"  - Trigger ID: {t['triggerId']}, Display Name: {t['displayName']}")

# Delete a trigger
print("\nDeleting trigger...")
client.delete_trigger(TRIGGER_ID)
print("Trigger deleted successfully")