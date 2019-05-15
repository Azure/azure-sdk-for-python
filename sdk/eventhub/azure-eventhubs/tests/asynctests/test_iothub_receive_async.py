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
    messages += len(batch)
    return messages


async def get_partitions(iot_connection_str):
    try:
        client = EventHubClientAsync.from_iothub_connection_string(iot_connection_str, debug=True)
        client.add_async_receiver("$default", "0", prefetch=1000, operation='/messages/events')
        await client.run_async()
        partitions = await client.get_eventhub_info_async()
        return partitions["partition_ids"]
    finally:
        await client.stop_async()


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_iothub_receive_multiple_async(iot_connection_str):
    partitions = await get_partitions(iot_connection_str)
    client = EventHubClientAsync.from_iothub_connection_string(iot_connection_str, debug=True)
    try:
        receivers = []
        for p in partitions:
            receivers.append(client.add_async_receiver("$default", p, prefetch=10, operation='/messages/events'))
        await client.run_async()
        outputs = await asyncio.gather(*[pump(r) for r in receivers])

        assert isinstance(outputs[0], int) and outputs[0] <= 10
        assert isinstance(outputs[1], int) and outputs[1] <= 10
    finally:
        await client.stop_async()
