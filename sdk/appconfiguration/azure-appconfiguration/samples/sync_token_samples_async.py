# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sync_token_async_samples.py
DESCRIPTION:
    This sample demos update_sync_token for the AzureAppConfigurationClient
USAGE: python sync_token_async_samples.py
"""
import asyncio
from typing import Any, Dict, List
from azure.appconfiguration.aio import AzureAppConfigurationClient
from util import get_connection_string


async def handle_event_grid_notifications(event_grid_events: List[Dict[str, Any]]) -> None:
    CONNECTION_STRING = get_connection_string()

    all_keys = []

    async with AzureAppConfigurationClient.from_connection_string(CONNECTION_STRING) as client:
        for event_grid_event in event_grid_events:
            if event_grid_event["eventType"] == "Microsoft.KeyValueModified":
                sync_token = event_grid_event["data"]["syncToken"]
                client.update_sync_token(sync_token)

                new_key = await client.get_configuration_setting(
                    key=event_grid_event["data"]["key"], label=event_grid_event["data"]["label"]
                )

                all_keys.append(new_key)


if __name__ == "__main__":
    asyncio.run(handle_event_grid_notifications([]))
