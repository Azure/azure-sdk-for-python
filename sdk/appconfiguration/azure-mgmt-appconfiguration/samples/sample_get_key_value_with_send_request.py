# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_get_key_value_with_send_request.py

DESCRIPTION:
    This sample creates or updates the App Configuration feature flag named "Alpha" by using
    AppConfigurationManagementClient.send_request.

USAGE:
    python sample_get_key_value_with_send_request.py

    Set these environment variables before running the sample:
    1) AZURE_SUBSCRIPTION_ID
    2) RESOURCE_GROUP_NAME
    3) APPCONFIGURATION_STORE_NAME
"""

from azure.core.rest import HttpRequest
from azure.identity import DefaultAzureCredential
from azure.mgmt.appconfiguration import AppConfigurationManagementClient


AZURE_ARM_ENDPOINT = "https://centraluseuap.management.azure.com"


def main() -> None:
    subscription_id = "160a734f-944d-4dd1-a36a-ebf7acd0958a"
    resource_group_name = "mametcal"
    config_store_name = "mgmt-wus2"

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
                f"{config_store_name}/featureFlags/Alpha"
            ),
            params={"api-version": "2026-09-01-preview"},
            headers={"Content-Type": "application/json"},
            json={"properties": {"enabled": True}},
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
