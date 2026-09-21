# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_put_key_value_with_send_request.py

DESCRIPTION:
    This sample creates or updates an App Configuration key-value and the feature flag named
    "Alpha" by using AppConfigurationManagementClient.send_request.

USAGE:
    python sample_put_key_value_with_send_request.py

    Set these environment variables before running the sample:
    1) AZURE_SUBSCRIPTION_ID
    2) RESOURCE_GROUP_NAME
    3) APPCONFIGURATION_STORE_NAME
"""

import json

from azure.core.rest import HttpRequest
from azure.identity import DefaultAzureCredential
from azure.mgmt.appconfiguration import AppConfigurationManagementClient


AZURE_ARM_ENDPOINT = "https://centraluseuap.management.azure.com"


def main() -> None:
    subscription_id = "160a734f-944d-4dd1-a36a-ebf7acd0958a"
    resource_group_name = "mametcal"
    config_store_name = "rp-test-fc"

    credential = DefaultAzureCredential()
    with AppConfigurationManagementClient(
        credential,
        subscription_id,
        base_url=AZURE_ARM_ENDPOINT,
    ) as client:
        request = HttpRequest(
            method="PUT",
            url=(
                f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
                "/providers/Microsoft.AppConfiguration/configurationStores/"
                f"{config_store_name}/keyValues/ExampleKey9"
            ),
            params={"api-version": "2024-06-01"},
            headers={"Content-Type": "application/json"},
            json={"properties": {"value": "ExampleValue"}},
        )
        response = client.send_request(request)
        if response.status_code >= 400:
            print(f"Request URL: {response.request.url}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response.text()}")
        response.raise_for_status()

        key_value = response.json()
        print(key_value)

        request = HttpRequest(
            method="PUT",
            url=(
                f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}"
                "/providers/Microsoft.AppConfiguration/configurationStores/"
                f"{config_store_name}/featureFlags/Alpha9"
            ),
            params={"api-version": "2026-09-01-preview"},
            headers={"Content-Type": "application/json"},
            json={
                "properties": {
                    "description": "Enables a personalized checkout experience during business hours.",
                    "enabled": True,
                    "conditions": {
                        "requirementType": "All",
                        "filters": [
                            {
                                "name": "Microsoft.TimeWindow",
                                "parameters": {
                                    "Start": "Wed, 9 Sep 2026 09:00:00 GMT",
                                    "End": "Wed, 9 Sep 2026 17:00:00 GMT",
                                    "Recurrence": json.dumps(
                                        {
                                            "Pattern": {
                                                "Type": "Weekly",
                                                "Interval": 1,
                                                "DaysOfWeek": [
                                                    "Monday",
                                                    "Tuesday",
                                                    "Wednesday",
                                                    "Thursday",
                                                    "Friday",
                                                ],
                                                "FirstDayOfWeek": "Monday",
                                            },
                                            "Range": {"Type": "NoEnd"},
                                        }
                                    ),
                                },
                            },
                            {
                                "name": "Microsoft.Targeting",
                                "parameters": {
                                    "Audience": json.dumps(
                                        {
                                            "DefaultRolloutPercentage": 20,
                                            "Users": [
                                                "alice@example.com",
                                                "bob@example.com",
                                            ],
                                            "Groups": [
                                                {
                                                    "Name": "beta-testers",
                                                    "RolloutPercentage": 100,
                                                },
                                                {
                                                    "Name": "early-adopters",
                                                    "RolloutPercentage": 50,
                                                },
                                            ],
                                            "Exclusion": {
                                                "Users": ["contractor@example.com"],
                                                "Groups": ["internal-audit"],
                                            },
                                        }
                                    )
                                },
                            },
                        ],
                    },
                    "variants": [
                        {
                            "name": "Control",
                            "value": json.dumps(
                                {
                                    "layout": "classic",
                                    "showRecommendations": False,
                                }
                            ),
                            "contentType": "application/json",
                            "statusOverride": "Disabled",
                        },
                        {
                            "name": "Personalized",
                            "value": json.dumps(
                                {
                                    "layout": "personalized",
                                    "showRecommendations": True,
                                    "recommendationCount": 5,
                                }
                            ),
                            "contentType": "application/json",
                            "statusOverride": "Enabled",
                        },
                        {
                            "name": "Experimental",
                            "value": json.dumps(
                                {
                                    "layout": "personalized",
                                    "showRecommendations": True,
                                    "recommendationCount": 10,
                                }
                            ),
                            "contentType": "application/json",
                            "statusOverride": "Enabled",
                        },
                    ],
                    "allocation": {
                        "defaultWhenDisabled": "Control",
                        "defaultWhenEnabled": "Personalized",
                        "user": [
                            {
                                "variant": "Experimental",
                                "users": ["alice@example.com"],
                            }
                        ],
                        "group": [
                            {
                                "variant": "Experimental",
                                "groups": ["beta-testers"],
                            }
                        ],
                        "percentile": [
                            {"variant": "Personalized", "from": 0, "to": 80},
                            {"variant": "Experimental", "from": 80, "to": 100},
                        ],
                        "seed": "personalized-checkout-rollout",
                    },
                    "telemetry": {
                        "enabled": True,
                        "metadata": {
                            "Owner": "checkout-team",
                            "Ticket": "CHECKOUT-2048",
                        },
                    },
                    "tags": {
                        "owner": "checkout-team",
                        "environment": "development",
                    },
                }
            },
        )
        response = client.send_request(request)
        if response.status_code >= 400:
            print(f"Request URL: {response.request.url}")
            print(f"Response headers: {dict(response.headers)}")
            print(f"Response body: {response.text()}")
        response.raise_for_status()

        feature_flag = response.json()
        print(feature_flag)


if __name__ == "__main__":
    main()
