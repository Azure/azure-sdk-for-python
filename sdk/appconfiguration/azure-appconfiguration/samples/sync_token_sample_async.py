# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sync_token_sample_async.py

DESCRIPTION:
    This sample demos how to update sync_token for an AzureAppConfigurationClient asynchronously.

USAGE: python sync_token_sample_async.py

    Set the environment variables with your own values before running the sample:
    1) APPCONFIGURATION_CONNECTION_STRING: Connection String used to access the Azure App Configuration.
"""
import asyncio
import os
from azure.appconfiguration.aio import AzureAppConfigurationClient


async def handle_event_grid_notifications(event_grid_events):
    CONNECTION_STRING = os.environ["APPCONFIGURATION_CONNECTION_STRING"]

    all_keys = []

    async with AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING) as client:
        for event_grid_event in event_grid_events:
            if event_grid_event["eventType"] == "Microsoft.KeyValueModified":
                sync_token = event_grid_event["data"]["syncToken"]
                await client.update_sync_token(sync_token)

                new_key = await client.get_configuration_setting(
                    key=event_grid_event["data"]["key"], label=event_grid_event["data"]["label"]
                )

                all_keys.append(new_key)


if __name__ == "__main__":
    asyncio.run(handle_event_grid_notifications([]))
