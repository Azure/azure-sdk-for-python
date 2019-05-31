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
async def test_send_with_long_interval_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.create_sender()
    try:
        await sender.send(EventData(b"A single event"))
        for _ in range(1):
            #await asyncio.sleep(300)
            sender._handler._connection._conn.destroy()
            await sender.send(EventData(b"A single event"))
    finally:
        await sender.close()

    received = []
    for r in receivers:
        r._handler._connection._conn.destroy()
        received.extend(r.receive(timeout=1))
    assert len(received) == 2
    assert list(received[0].body)[0] == b"A single event"


def pump(receiver):
    messages = []
    with receiver:
        batch = receiver.receive(timeout=1)
        messages.extend(batch)
        while batch:
            batch = receiver.receive(timeout=1)
            messages.extend(batch)
    return messages


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_forced_conn_close_async(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.create_sender()
    try:
        await sender.send(EventData(b"A single event"))
        sender._handler._message_sender.destroy()
        await asyncio.sleep(300)
        await sender.send(EventData(b"A single event"))
        await sender.send(EventData(b"A single event"))
        sender._handler._message_sender.destroy()
        await asyncio.sleep(300)
        await sender.send(EventData(b"A single event"))
        await sender.send(EventData(b"A single event"))
    finally:
        await sender.close()
    
    received = []
    for r in receivers:
       received.extend(pump(r))
    assert len(received) == 5
    assert list(received[0].body)[0] == b"A single event"
