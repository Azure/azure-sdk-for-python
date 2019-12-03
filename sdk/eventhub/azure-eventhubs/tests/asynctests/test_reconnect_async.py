#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import time
import asyncio
import pytest

from azure import eventhub
from azure.eventhub import (
    EventHubClientAsync,
    EventData,
    Offset,
    EventHubError)


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_long_interval_async(short_idle_connstr_receivers):
    connection_str, receivers = short_idle_connstr_receivers
    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        await asyncio.sleep(12)
        for _ in range(2):
            await sender.send(EventData(b"A single event"))
    finally:
        await client.stop_async()

    received = []
    for r in receivers:
       received.extend(r.receive(timeout=1))

    assert len(received) == 0

    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        await sender.send(EventData(b"A single event"))
        for _ in range(2):
            await sender.send(EventData(b"A single event"))
    finally:
        await client.stop_async()

    received = []
    for r in receivers:
       received.extend(r.receive(timeout=1))

    assert len(received) == 3
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
@pytest.mark.asyncio
async def test_send_with_prior_events_long_interval_async(short_idle_connstr_receivers):
    connection_str, receivers = short_idle_connstr_receivers
    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    sender = client.add_async_sender('0')
    sender_1 = client.add_async_sender('1')
    try:
        await client.run_async()
        await sender.send(EventData(b"A single event"))
        await sender_1.send(EventData(b"A single event"))
    finally:
        await client.stop_async()

    received = []
    for r in receivers:
       received.extend(r.receive(timeout=1))

    assert len(received) == 2

    await asyncio.sleep(12)

    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    sender = client.add_async_sender()
    try:
        await client.run_async()
        for _ in range(2):
            await sender.send(EventData(b"A single event"))
    finally:
        await client.stop_async()

    for r in receivers:
       received.extend(r.receive(timeout=5, max_reconnect_retries=1)) # setting max retries > 0 is important so that it tries reconnecting more than never.

    assert len(received) == 4


def pump(receiver):
    messages = []
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
    client = EventHubClientAsync.from_connection_string(connection_str, debug=True)
    sender = client.add_async_sender()
    try:
        await client.run_async()
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
        await client.stop_async()
    
    received = []
    for r in receivers:
       received.extend(pump(r))
    assert len(received) == 5
    assert list(received[0].body)[0] == b"A single event"


# def test_send_with_forced_link_detach(connstr_receivers):
#     connection_str, receivers = connstr_receivers
#     client = EventHubClient.from_connection_string(connection_str, debug=True)
#     sender = client.add_sender()
#     size = 20 * 1024
#     try:
#         client.run()
#         for i in range(1000):
#             sender.transfer(EventData([b"A"*size, b"B"*size, b"C"*size, b"D"*size, b"A"*size, b"B"*size, b"C"*size, b"D"*size, b"A"*size, b"B"*size, b"C"*size, b"D"*size]))
#         sender.wait()
#     finally:
#         client.stop()

#     received = []
#     for r in receivers:
#         received.extend(r.receive(timeout=10))
