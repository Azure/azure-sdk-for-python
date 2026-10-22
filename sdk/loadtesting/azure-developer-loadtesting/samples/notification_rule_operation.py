# pylint: disable=line-too-long,useless-suppression
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: notification_rule_operations.py

DESCRIPTION:
    This sample shows how to create, get, list, and delete a notification rule
    for load tests.

USAGE:
    python notification_rule_operations.py

    Set the environment variables with your own values before running the sample:
    1)  AZURE_CLIENT_ID - client id
    2)  AZURE_CLIENT_SECRET - client secret
    3)  AZURE_TENANT_ID - tenant id for your Azure
    4)  LOADTESTSERVICE_ENDPOINT - Data Plane endpoint for Loadtestservice
    5)  ACTION_GROUP_ID - Resource ID of the Azure Monitor action group for notifications
"""
from azure.developer.loadtesting import LoadTestAdministrationClient
from azure.identity import DefaultAzureCredential

import os
from dotenv import load_dotenv

load_dotenv()
LOADTESTSERVICE_ENDPOINT = os.environ["LOADTESTSERVICE_ENDPOINT"]
ACTION_GROUP_ID = os.environ["ACTION_GROUP_ID"]

# Build a client through AAD and resource endpoint
client = LoadTestAdministrationClient(credential=DefaultAzureCredential(), endpoint=LOADTESTSERVICE_ENDPOINT)

TEST_ID = "my-sdk-test-id"
NOTIFICATION_RULE_ID = "my-sdk-notification-rule-id"

# Create or update a notification rule
print("Creating notification rule...")
notification_rule = client.create_or_update_notification_rule(
    NOTIFICATION_RULE_ID,
    {
        "displayName": "My Test Run Notification Rule",
        "scope": "Tests",
        "testIds": [TEST_ID],
        "actionGroupIds": [ACTION_GROUP_ID],
        "eventFilters": {
            "testRunEnded": {
                "kind": "TestRunEnded",
                "condition": {
                    "testRunStatuses": ["DONE", "FAILED"],
                    "testRunResults": ["PASSED", "FAILED"],
                },
            },
        },
    },
)
print(f"Notification rule created: {notification_rule}")

# Get a notification rule
print("\nGetting notification rule...")
notification_rule = client.get_notification_rule(NOTIFICATION_RULE_ID)
print(f"Notification rule retrieved: {notification_rule}")

# List all notification rules
print("\nListing all notification rules...")
notification_rules = client.list_notification_rules()
for nr in notification_rules:
    print(f"  - Notification Rule ID: {nr['notificationRuleId']}, Display Name: {nr['displayName']}")

# Delete a notification rule
print("\nDeleting notification rule...")
client.delete_notification_rule(NOTIFICATION_RULE_ID)
print("Notification rule deleted successfully")