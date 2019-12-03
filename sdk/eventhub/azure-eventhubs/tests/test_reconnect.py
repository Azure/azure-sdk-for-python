#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import time
import pytest

from azure import eventhub
from azure.eventhub import (
    EventData,
    Offset,
    EventHubError,
    EventHubClient)


@pytest.mark.liveTest
def test_send_with_long_interval_sync(short_idle_connstr_receivers):
    connection_str, receivers = short_idle_connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender()
    try:
        client.run()
        sender.send(EventData(b"A single event"))
        for _ in range(2):
            time.sleep(6)
            sender.send(EventData(b"A single event"))
    finally:
        client.stop()

    received = []
    for r in receivers:
        received.extend(r.receive(timeout=2))

    assert len(received) == 0

    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender()
    client.run()
    sender.send(EventData(b"A single event"))
    client.stop()

    for r in receivers:
        received.extend(r.receive(timeout=2))

    # We expect only 1 because the receiver, having not read prior to timing out, won't have ANY 
    # concept of an internal checkpoint to resume from.
    assert len(received) == 1
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
def test_send_with_prior_messages_long_interval_sync(short_idle_connstr_receivers):
    connection_str, receivers = short_idle_connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    # If you don't define a partition, the pre-and-post-reconnect sendings could come from different partitions, 
    # and thus the checkpoint would go to latest on second read and miss messages.
    sender = client.add_sender('0') 
    sender_1 = client.add_sender('1') 
    try:
        client.run()
        sender.send(EventData(b"A single event"))
        sender_1.send(EventData(b"A single event"))
    finally:
        client.stop()
    received = []
    for r in receivers:
        received.extend(r.receive(timeout=1))

    assert len(received) == 2
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender()
    client.run()
    for _ in range(2):
        time.sleep(6)
        sender.send(EventData(b"A single event"))
    client.stop()
    for r in receivers:
        received.extend(r.receive(timeout=5, max_reconnect_retries=1)) #setting max retries > 0 is important so that it tries reconnecting more than never.

    assert len(received) == 4
    assert list(received[0].body)[0] == b"A single event"


@pytest.mark.liveTest
def test_send_with_forced_conn_close_sync(connstr_receivers):
    connection_str, receivers = connstr_receivers
    client = EventHubClient.from_connection_string(connection_str, debug=True)
    sender = client.add_sender()
    try:
        client.run()
        sender.send(EventData(b"A single event"))
        sender._handler._message_sender.destroy()
        time.sleep(300)
        sender.send(EventData(b"A single event"))
        sender.send(EventData(b"A single event"))
        sender._handler._message_sender.destroy()
        time.sleep(300)
        sender.send(EventData(b"A single event"))
        sender.send(EventData(b"A single event"))
    finally:
        client.stop()
    
    received = []
    for r in receivers:
       received.extend(r.receive(timeout=1))
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
