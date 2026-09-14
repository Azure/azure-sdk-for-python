# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sync_token_sample.py

DESCRIPTION:
    This sample demos how to update sync_token for an AzureAppConfigurationClient synchronously.


USAGE: python sync_token_sample.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_ENDPOINT_STRING: Endpoint URL used to access the Azure App Configuration.
"""

import os
from azure.appconfiguration import AzureAppConfigurationClient
from azure.identity import DefaultAzureCredential


def handle_event_grid_notifications(event_grid_events):
    endpoint = os.environ["APPCONFIGURATION_ENDPOINT_STRING"]

    all_keys = []

    with AzureAppConfigurationClient(endpoint, DefaultAzureCredential()) as client:
        for event_grid_event in event_grid_events:
            if event_grid_event["eventType"] == "Microsoft.KeyValueModified":
                sync_token = event_grid_event["data"]["syncToken"]
                client.update_sync_token(sync_token)

                new_key = client.get_configuration_setting(
                    key=event_grid_event["data"]["key"], label=event_grid_event["data"]["label"]
                )

                all_keys.append(new_key)


if __name__ == "__main__":
    handle_event_grid_notifications([])
