#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import time
import asyncio
import pytest

from azure.eventhub import (
    EventData,
    EventPosition,
    EventHubError)
from azure.eventhub.aio import EventHubClient


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_long_interval_async(connstr_receivers, sleep):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, network_tracing=False)
    sender = client.create_producer()
    try:
        await sender.send(EventData(b"A single event"))
        for _ in range(1):
            if sleep:
                await asyncio.sleep(300)
            else:
                sender._handler._connection._conn.destroy()
            await sender.send(EventData(b"A single event"))
    finally:
        await sender.close()

    received = []
    for r in receivers:
        if not sleep:  # if sender sleeps, the receivers will be disconnected. destroy connection to simulate
            r._handler._connection._conn.destroy()
        received.extend(r.receive(timeout=5))
    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"
