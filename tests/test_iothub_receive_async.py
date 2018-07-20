#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import asyncio
import pytest
import time

from azure import eventhub
from azure.eventhub import EventData, Offset, EventHubError, EventHubClientAsync


async def pump(receiver, sleep=None):
    messages = 0
    if sleep:
        await asyncio.sleep(sleep)
    batch = await receiver.receive(timeout=1)
    while batch:
        messages += len(batch)
        batch = await receiver.receive(timeout=1)
    return messages


@pytest.mark.asyncio
async def test_iothub_receive_multiple_async(iot_connection_str):
    client = EventHubClientAsync.from_iothub_connection_string(iot_connection_str, debug=True)
    try:
        receivers = []
        for i in range(2):
            receivers.append(client.add_async_receiver("$default", "0", prefetch=1000, operation='/messages/events'))
        await client.run_async()
        partitions = await client.get_eventhub_info_async()
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)

        assert isinstance(outputs[0], int) and outputs[0] == 0
        assert isinstance(outputs[1], int) and outputs[1] == 0
    finally:
        await client.stop_async()


@pytest.mark.asyncio
async def test_iothub_receive_detach_async(iot_connection_str):
    client = EventHubClientAsync.from_iothub_connection_string(iot_connection_str, debug=True)
    receivers = []
    for i in range(2):
        receivers.append(client.add_async_receiver("$default", str(i), prefetch=1000, operation='/messages/events'))
    await client.run_async()
    try:
        outputs = await asyncio.gather(
            pump(receivers[0]),
            pump(receivers[1]),
            return_exceptions=True)

        assert isinstance(outputs[0], int) and outputs[0] == 0
        assert isinstance(outputs[1], EventHubError)
    finally:
        await client.stop_async()